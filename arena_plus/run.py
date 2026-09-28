"""Run / smoke / score / cost CLI (GOALS §8).

  python -m arena_plus.run run   RUN [--n N]   play games for configs/runs/RUN.toml (resumes; smoke = --n 5)
  python -m arena_plus.run score RUN           score games, write summary.json + gate verdict
  python -m arena_plus.run cost                token + USD meter from logs/api_calls.jsonl
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import threading
import time
import tomllib
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from arena_plus import k2, ratelimit
from arena_plus.engine import play, ITERATIONS
from arena_plus.metrics import score_game, summarize

REPO = k2.REPO
DAILY_TOKEN_CAP = 10_000_000      # IFM per-key daily cap (docs.ifm.ai, Limits)
_lock = threading.Lock()


def cfg_path(run):
    return REPO / "configs" / "runs" / f"{run}.toml"


def load_cfg(run):
    return tomllib.loads(cfg_path(run).read_text())


def git(*args, cwd=REPO):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout.strip()


def config_hash(run, cfg):
    # workers is operational only (throughput), so it is excluded from the hash
    h = hashlib.sha256("\n".join(l for l in cfg_path(run).read_text().splitlines() if not l.startswith("workers")).encode())
    for f in ["engine.py", "protocol.py", "k2.py", "i18n.py"] + [f"variants/{v}.py" for v in cfg["variants"]] + ["variants/_checks.py"]:
        h.update((REPO / "arena_plus" / f).read_bytes())
    return h.hexdigest()[:16]


def write_manifest(run, cfg, n_games):
    d = REPO / "runs" / run
    d.mkdir(parents=True, exist_ok=True)
    man = dict(run=run, step=cfg.get("step"), variants=cfg["variants"], langs=cfg.get("langs"), config_hash=config_hash(run, cfg),
               model=k2.os.environ["IFM_MODEL"], base_url=k2.os.environ["IFM_BASE_URL"], sampling=k2.SAMPLING,
               iterations=ITERATIONS, upstream="vendor/NegotiationArena",
               upstream_commit=git("rev-parse", "HEAD", cwd=REPO / "vendor" / "NegotiationArena"),
               n_games=n_games, n_planned=cfg["n"], seeds=[cfg.get("seed_start", 1), cfg.get("seed_start", 1) + cfg["n"] - 1],
               git_sha=git("rev-parse", "HEAD"), git_dirty=bool(git("status", "--porcelain", "--", "arena_plus", "configs")),
               updated=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    (d / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    return man


def tokens_today():
    if not k2.LOG.exists():
        return 0
    day = dt.datetime.now(dt.timezone.utc).date()
    tot = 0
    for line in k2.LOG.read_text().splitlines():
        r = json.loads(line)
        if dt.datetime.fromtimestamp(r["ts"], dt.timezone.utc).date() == day:
            tot += r["prompt_tokens"] + r["completion_tokens"]
    return tot


def done_seeds(run):
    f = REPO / "runs" / run / "games.jsonl"
    if not f.exists():
        return set()
    return {json.loads(l)["seed"] for l in f.read_text().splitlines() if l.strip()}


def transcript_md(g):
    lines = [f"# {g['game_id']}", "", f"variants: {g['variants']}  ", f"params: `{json.dumps(g['params'], ensure_ascii=False)}`  ",
             f"end: **{g['end']}**, price: **{g['price']}**, turns: {g['n_turns']}", ""]
    for s in ("seller", "buyer"):
        lines += [f"## system prompt ({s})", "", "```", g["system_prompts"][s], "```", ""]
    for t in g["turns"]:
        lines += [f"## turn {t['turn']} · {t['seat']} · {t['status']} · finish={t['finish_reason']}"]
        for i, a in enumerate(t.get("attempts", [])):
            lines += [f"*discarded attempt {i + 1}: {a['status']}*", ""]
        lines += ["", "<details><summary>reasoning</summary>", "", "```", t.get("reasoning") or "", "```", "</details>", "",
                  "```", t["content"], "```", ""]
    return "\n".join(lines)


def run_games(run, n=None):
    cfg = load_cfg(run)
    n = n or cfg["n"]
    start = cfg.get("seed_start", 1)
    seeds = [s for s in range(start, start + n) if s not in done_seeds(run)]
    out_dir = REPO / "runs" / run
    (out_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    write_manifest(run, cfg, len(done_seeds(run)))
    print(f"[run] {run}: {len(seeds)} games to play (workers={cfg.get('workers', 8)})", flush=True)

    def one(seed):
        ratelimit.wait_for_quota()
        g = play(run, seed, cfg["variants"], cfg.get("langs"))
        with _lock:
            with (out_dir / "games.jsonl").open("a") as f:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
            (out_dir / "transcripts" / f"{g['game_id']}.md").write_text(transcript_md(g))
        return g

    fails = 0
    with ThreadPoolExecutor(cfg.get("workers", 8)) as ex:
        futs = {ex.submit(one, s): s for s in seeds}
        for fut in as_completed(futs):
            try:
                g = fut.result()
                print(f"[game] {g['game_id']} end={g['end']} price={g['price']} turns={g['n_turns']}", flush=True)
            except k2.BudgetExceeded:
                print("[budget] BudgetExceeded — stopping", flush=True); ex.shutdown(cancel_futures=True); raise
            except Exception as e:
                fails += 1
                print(f"[fail] seed={futs[fut]} {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
    man = write_manifest(run, cfg, len(done_seeds(run)))
    print(f"[run] {run}: {man['n_games']}/{n} games, {fails} failed this pass", flush=True)
    return fails


def load_games(run):
    f = REPO / "runs" / run / "games.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines() if l.strip()]


def score_run(run):
    games = sorted(load_games(run), key=lambda g: g["seed"])
    rows = [score_game(g) for g in games]
    d = REPO / "runs" / run
    with (d / "scores.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sm = summarize(rows)
    usage = run_usage(run)
    sm.update(usage)
    (d / "summary.json").write_text(json.dumps(sm, indent=2) + "\n")
    v = "PASS" if sm["gate"]["passed"] else "FAIL"
    print(f"[score] {run}: n={sm['n']} cap-collapse={sm['cap_collapse']} IQR={sm['iqr']} correct={sm['correct_rate']} "
          f"leak={sm['leak_rate']} trunc={sm['truncated_turn_rate']:.3f} -> {v} {sm['gate']['reasons']}")
    return sm


def run_usage(run):
    rows = [json.loads(l) for l in k2.LOG.read_text().splitlines()] if k2.LOG.exists() else []
    rows = [r for r in rows if r["run"] == run and r["game_id"].startswith(run + "-")]
    games = {r["game_id"] for r in rows}
    pt, ct = sum(r["prompt_tokens"] for r in rows), sum(r["completion_tokens"] for r in rows)
    return dict(api_calls=len(rows), prompt_tokens=pt, completion_tokens=ct,
                tokens_per_game=(pt + ct) / len(games) if games else None,
                tokens_per_call=(pt + ct) / len(rows) if rows else None,
                length_finish_rate=(sum(r["finish_reason"] == "length" for r in rows) / len(rows)) if rows else None,
                usd=pt / 1e6 * k2.USD_PER_M_IN + ct / 1e6 * k2.USD_PER_M_OUT)


def cost():
    rows = [json.loads(l) for l in k2.LOG.read_text().splitlines()] if k2.LOG.exists() else []
    by = {}
    for r in rows:
        b = by.setdefault(r["run"], [0, 0, 0, set()])
        b[0] += 1; b[1] += r["prompt_tokens"]; b[2] += r["completion_tokens"]; b[3].add(r["game_id"])
    print(f"{'run':28} {'calls':>7} {'games':>6} {'prompt':>12} {'completion':>12} {'tok/game':>9}")
    for k, (c, p, o, g) in by.items():
        print(f"{k:28} {c:7d} {len(g):6d} {p:12,d} {o:12,d} {(p + o) / len(g):9,.0f}")
    print(f"spent ${k2.spent_usd():.2f} of ${k2.BUDGET_USD} (IFM preview has no published price: see DEVIATIONS.md)")
    print(f"tokens today (UTC): {tokens_today():,}; rolling 24 h: {ratelimit.tokens_last_24h():,} / {DAILY_TOKEN_CAP:,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "score", "cost", "manifest"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--n", type=int)
    a = ap.parse_args()
    if a.cmd == "run":
        sys.exit(1 if run_games(a.run, a.n) else 0)
    elif a.cmd == "score":
        score_run(a.run)
    elif a.cmd == "manifest":
        write_manifest(a.run, load_cfg(a.run), len(done_seeds(a.run)))
    else:
        cost()
