"""CASEBOOK.md helper.

  python -m arena_plus.casebook pick RUN             print the 3 most extreme games (lowest s, highest s, third pick)
  python -m arena_plus.casebook add RUN notes.json   append them to CASEBOOK.md; notes.json = {game_id: "2-line note"}

Third pick: a wrong right-or-wrong outcome if the run has any, else the longest game.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def games(run):
    d = REPO / "runs" / run
    g = {json.loads(l)["game_id"]: json.loads(l) for l in (d / "games.jsonl").read_text().splitlines() if l.strip()}
    s = [json.loads(l) for l in (d / "scores.jsonl").read_text().splitlines() if l.strip()]
    return g, s


def pick(run):
    g, rows = games(run)
    rows = [r for r in rows if not r["void"]]
    with_s = sorted([r for r in rows if r["s"] is not None], key=lambda r: (r["s"], r["seed"]))
    chosen, why = [], {}
    if with_s:
        chosen.append(with_s[0]); why[with_s[0]["game_id"]] = f"lowest s = {with_s[0]['s']:.2f}"
        top = with_s[-1]
        if top["game_id"] not in why:
            chosen.append(top); why[top["game_id"]] = f"highest s = {top['s']:.2f}"
    wrong = [r for r in rows if r.get("correct") is False and r["game_id"] not in why]
    rest = sorted([r for r in rows if r["game_id"] not in why], key=lambda r: (-r["n_turns"], r["seed"]))
    third = wrong[0] if wrong else (rest[0] if rest else None)
    if third:
        chosen.append(third); why[third["game_id"]] = "wrong action for private info" if wrong else f"longest game ({third['n_turns']} turns)"
    return [(g[r["game_id"]], r, why[r["game_id"]]) for r in chosen[:3]]


def exchange(game):
    out = []
    for t in game["turns"]:
        if t.get("parsed"):
            p = t["parsed"]
            tr = "" if p["trade"] is None else f" [{json.dumps(p['trade']['BLUE'], ensure_ascii=False)}]"
            out.append(f"> **T{t['turn']} {t['seat']}** {p['answer']}{tr}: {p['message']}")
    return "\n>\n".join(out)


def main():
    cmd, run = sys.argv[1], sys.argv[2]
    picks = pick(run)
    if cmd == "pick":
        for game, r, why in picks:
            print(f"=== {game['game_id']} ({why}) params={game['params']} end={game['end']} price={game['price']} correct={r.get('correct')}")
            print(exchange(game)); print()
        return
    notes = json.loads(Path(sys.argv[3]).read_text())
    cb = REPO / "CASEBOOK.md"
    text = cb.read_text() if cb.exists() else "# CASEBOOK\n\nThe 3 most extreme transcripts per step (visible exchange only; full transcripts in `runs/<run>/transcripts/`).\n"
    text += f"\n## {run}\n"
    for game, r, why in picks:
        s = "n/a" if r["s"] is None else f"{r['s']:.2f}"
        text += (f"\n### {game['game_id']} — {why}\n\nparams `{json.dumps(game['params'], ensure_ascii=False)}` · end **{game['end']}** · "
                 f"price **{game['price']}** · s {s} · correct {r.get('correct')}\n\n{exchange(game)}\n\n**Note.** {notes[game['game_id']]}\n")
    cb.write_text(text)
    print(f"added {len(picks)} entries for {run}")


if __name__ == "__main__":
    main()
