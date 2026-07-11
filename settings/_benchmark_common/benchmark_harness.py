#!/usr/bin/env python3
"""Small per-benchmark harness/status/implementation loop.

This gives every benchmark setting the same control surface and one readable
report:

  ./harness.sh status
  ./harness.sh check
  ./harness.sh note "human note"
  ./harness.sh error "token quota exhausted"
  ./harness.sh run-smoke
  ./harness.sh once
  ./harness.sh loop
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def append_event(root: Path, kind: str, message: str, status: str = "NOTE") -> None:
    events = root / "plan" / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": utc_now(),
        "kind": kind,
        "status": status,
        "message": message,
    }
    with events.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_events(root: Path, limit: int = 8) -> list[dict[str, Any]]:
    path = root / "plan" / "events.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"ts": "unknown", "kind": "parse_error", "status": "WARN", "message": line})
    return rows[-limit:]


def count_files(path: Path, patterns: list[str]) -> int:
    if not path.exists():
        return 0
    total = 0
    for pattern in patterns:
        total += sum(1 for _ in path.rglob(pattern))
    return total


def read_text(path: Path, fallback: str = "") -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8", errors="replace")


def first_unchecked_goal(goals: Path) -> str:
    if not goals.exists():
        return "Missing goals.md"
    for line in goals.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            return stripped[5:].strip()
    return "No unchecked checklist item found"


def current_answer(root: Path) -> str:
    findings = root / "reports" / "findings.md"
    if findings.exists() and findings.stat().st_size > 0:
        text = findings.read_text(encoding="utf-8", errors="replace").strip()
        return "\n".join(text.splitlines()[:12])
    return (
        "No empirical answer yet. This setting is scaffolded for benchmark "
        "adaptation and smoke testing."
    )


def render_status(root: Path) -> str:
    config = load_json(root / "config" / "benchmark.json")
    benchmark_model = load_json(root / "config" / "benchmark_model.json")
    events = read_events(root)
    artifacts = root / "artifacts"
    logs = artifacts / "logs"
    results = artifacts / "results"
    transcripts = artifacts / "transcripts"

    name = config.get("name", root.name)
    bench_id = config.get("id", "unknown")
    bucket = config.get("bucket", "unknown")
    model = config.get("default_model", "Qwen3-1.7B")
    active_model = model
    model_note = "default research plan"
    if benchmark_model.get("provider"):
        active_model = f"{benchmark_model.get('provider')} / {benchmark_model.get('default_model', 'unspecified')}"
        model_note = benchmark_model.get("purpose", "explicit benchmark model override")
    priority = config.get("priority", "unknown")
    phase = config.get("phase", "setup")
    question = config.get(
        "headline_question",
        "Does language contact change outcomes or whose framing dominates?",
    )
    acceptance = config.get("acceptance", "not specified")
    next_step = first_unchecked_goal(root / "goals.md").rstrip(".")

    last_error = next((e for e in reversed(events) if e.get("status") in {"ERROR", "BLOCKED"}), None)
    event_lines = []
    for event in events:
        event_lines.append(
            f"- `{event.get('ts', 'unknown')}` {event.get('status', 'NOTE')}: "
            f"{event.get('message', '')}"
        )
    if not event_lines:
        event_lines.append("- No run events logged yet.")

    blocker = "None logged."
    if last_error:
        blocker = f"{last_error.get('status')}: {last_error.get('message')}"

    metrics = config.get("primary_metrics", [])
    metric_text = ", ".join(metrics) if metrics else "not specified"
    conditions = ", ".join(config.get("conditions", ["C0", "C1", "C2", "C3"]))
    pairs = ", ".join(config.get("language_pairs", ["EN-ID"]))

    return f"""# {bench_id} {name} Status

This is the concise file to read first for this benchmark.

## Current Answer

{current_answer(root)}

Next useful work: **{next_step}**.

## Question

{question}

## State

| Field | Value |
|---|---|
| Setting | `{root.name}` |
| Benchmark | `{bench_id}` / {name} |
| Bucket | {bucket} |
| Priority | {priority} |
| Phase | {phase} |
| Default model | `{model}` |
| Active benchmark model | `{active_model}` |
| Model note | {model_note} |
| Language pairs | {pairs} |
| Conditions | {conditions} |
| Primary metrics | {metric_text} |
| Acceptance gate | {acceptance} |

## Blockers / Errors

{blocker}

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

{chr(10).join(event_lines)}

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | {count_files(transcripts, ["*.json", "*.jsonl"])} |
| Result summaries | {count_files(results, ["*.md", "*.json", "*.jsonl", "*.csv"])} |
| Logs | {count_files(logs, ["*.txt", "*.log"])} |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
"""


def write_status(root: Path) -> None:
    report = root / "reports" / "status.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_status(root), encoding="utf-8")
    print(report)


def check(root: Path) -> int:
    required = [
        root / "goals.md",
        root / "config" / "benchmark.json",
        root / "harness.sh",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        append_event(root, "check", "Missing required files: " + ", ".join(missing), "ERROR")
        write_status(root)
        return 1
    append_event(root, "check", "Harness scaffold check passed", "OK")
    write_status(root)
    return 0


def run_smoke(root: Path) -> int:
    script = root / "scripts" / "run_smoke.sh"
    if not script.exists():
        append_event(root, "smoke", "No scripts/run_smoke.sh is wired for this benchmark yet", "BLOCKED")
        write_status(root)
        return 2
    proc = subprocess.run(["bash", str(script)], cwd=root)
    status = "OK" if proc.returncode == 0 else "ERROR"
    append_event(root, "smoke", f"scripts/run_smoke.sh exited {proc.returncode}", status)
    write_status(root)
    return proc.returncode


def maybe_run_smoke_after_codex(root: Path) -> int | None:
    script = root / "scripts" / "run_smoke.sh"
    if not script.exists():
        append_event(root, "smoke", "No scripts/run_smoke.sh exists after Codex pass", "BLOCKED")
        write_status(root)
        return None
    append_event(root, "smoke", "Parent harness starting post-Codex smoke/experiment attempt", "RUNNING")
    return run_smoke(root)


def git_output(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def repo_root_for(root: Path) -> Path | None:
    proc = git_output(["rev-parse", "--show-toplevel"], root)
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip())


def rel_to_repo(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def maybe_commit_and_push(root: Path, reason: str) -> None:
    """Best-effort parent checkpoint after a validated milestone.

    The child Codex agent is still expected to commit/push its own work. This
    parent-side fallback is intentionally scoped to the active setting and the
    shared harness files so it does not sweep unrelated worktree changes.
    """
    if shutil.which("git") is None:
        append_event(root, "git", "git not found; skipped commit/push checkpoint", "BLOCKED")
        return

    repo_root = repo_root_for(root)
    if repo_root is None:
        append_event(root, "git", "No git repository found; skipped commit/push checkpoint", "BLOCKED")
        return

    try:
        setting_path = rel_to_repo(repo_root, root)
    except ValueError as exc:
        append_event(root, "git", f"Setting is outside repo; skipped commit/push checkpoint: {exc}", "BLOCKED")
        return

    candidate_paths = [
        setting_path,
        "settings/_benchmark_common/benchmark_harness.py",
        "settings/_benchmark_common/protocol.md",
        "settings/_benchmark_common/README.md",
        "settings/README.md",
        "settings/benchmark_status.md",
        "run_setting.sh",
    ]
    existing_paths = [p for p in candidate_paths if (repo_root / p).exists()]
    excluded_checkout_paths = [
        f"{setting_path}/external",
        f"{setting_path}/vendor",
        f"{setting_path}/code/vendor",
        f"{setting_path}/.venv",
    ]
    pathspecs = [
        *existing_paths,
        *[f":(exclude){p}" for p in excluded_checkout_paths if (repo_root / p).exists()],
    ]

    status_before = git_output(["status", "--porcelain", "--", *pathspecs], repo_root)
    if status_before.returncode != 0:
        append_event(root, "git", f"Could not inspect scoped git status: {status_before.stdout.strip()}", "BLOCKED")
        return
    if not status_before.stdout.strip():
        return

    append_event(
        root,
        "git",
        f"Attempting scoped commit/push after {reason}; if no later git blocker appears, check git log/remote for success",
        "RUNNING",
    )
    add_proc = git_output(["add", "--", *pathspecs], repo_root)
    if add_proc.returncode != 0:
        append_event(root, "git", f"git add failed during checkpoint: {add_proc.stdout.strip()}", "BLOCKED")
        return

    staged = git_output(["diff", "--cached", "--name-only", "--", *pathspecs], repo_root)
    if staged.returncode != 0:
        append_event(root, "git", f"Could not inspect staged files: {staged.stdout.strip()}", "BLOCKED")
        return
    staged_files = [line for line in staged.stdout.splitlines() if line.strip()]
    if not staged_files:
        return

    config = load_json(root / "config" / "benchmark.json")
    label = config.get("benchmark") or config.get("name") or root.name
    message = f"{label} checkpoint after {reason}"
    commit_proc = git_output(["commit", "-m", message, "--", *pathspecs], repo_root)
    if commit_proc.returncode != 0:
        output = commit_proc.stdout.strip()
        if "nothing to commit" in output.lower():
            append_event(root, "git", f"No staged changes to commit after {reason}", "OK")
        else:
            append_event(root, "git", f"git commit failed during checkpoint: {output}", "BLOCKED")
        return

    push_proc = git_output(["push"], repo_root)
    if push_proc.returncode != 0:
        append_event(root, "git", f"git push failed during checkpoint: {push_proc.stdout.strip()}", "BLOCKED")
        return


def build_codex_prompt(root: Path) -> str:
    config = load_json(root / "config" / "benchmark.json")
    smoke_model = load_json(root / "config" / "smoke_model.json")
    benchmark_model = load_json(root / "config" / "benchmark_model.json")
    protocol = read_text(root.parent / "_benchmark_common" / "protocol.md")
    goals = read_text(root / "goals.md")
    status = render_status(root)
    events = read_text(root / "plan" / "events.jsonl")
    readme = read_text(root / "README.md")

    return f"""You are the implementation agent for one benchmark setting.

You are running inside this setting directory:
{root}

Do not work in sibling benchmark settings. Do not edit the old
settings/crosslingual_debate loop unless this setting's goals explicitly require
shared code. Keep all benchmark-specific code, logs, artifacts, docs, and plans
inside this setting folder.

Do not use an OpenAI API key for Codex. Codex is already authenticated by the
CLI/session. The OpenAI key, when configured below, is only for benchmark
agents/judges called by setting-local scripts.

Benchmark model override:
- Default research design used local Qwen/vLLM or Modal Qwen.
- If `config/benchmark_model.json` exists and sets `"provider": "openai"`, the
  human has explicitly changed this benchmark setting's execution plan: use
  OpenAI for benchmark agent/judge calls when that unblocks smoke, C0/C1, or
  later matrix runs.
- Read the key only inside benchmark runner scripts from the configured
  `api_key_file_candidates` or `OPENAI_API_KEY`. Do not print secrets.
- Label artifacts and reports as OpenAI benchmark evidence, not Qwen3 evidence.
- This override does not remove design gates such as counterbalancing,
  translation review, or G2 notes; if you intentionally proceed around a gate,
  record the deviation in `plan/deviations.md`.

Smoke model override:
- If `config/smoke_model.json` exists and sets `"provider": "openai"`, the
  human has explicitly allowed OpenAI for this benchmark's initial smoke tests.
- That OpenAI key is for benchmark smoke scripts only, not Codex auth. Prefer
  reading it from the setting config's `api_key_file_candidates` or from
  `OPENAI_API_KEY` inside the smoke runner, and do not print the key.
- OpenAI smoke results are runner bring-up evidence only. Do not report them as
  Qwen3-1.7B research-matrix evidence unless goals.md is later updated.

Meaning of this harness:
- This is not a documentation-only or scaffold-only loop.
- Your pass should move the benchmark toward real execution: resolve source,
  install, data, license, or model-endpoint blockers from the paper/GitHub when
  possible; implement the minimum runner/adapter needed; then run the next
  allowed smoke, C0 baseline, or source/data check.
- If a benchmark cannot run yet, the pass must leave a concrete command and
  artifact showing exactly what source/data/dependency/model endpoint is still
  missing. Do not keep adding generic scaffolding around the same blocker.

Source-resolution requirement:
- When the blocker is a missing repo, package, dataset, branch, license, or
  benchmark entry point, inspect the paper/repo from the canonical source. Use
  `git ls-remote`, `git clone --depth 1`, `git fetch`, `curl -L`, package
  metadata, README, LICENSE, pyproject, requirements, and source tree searches.
- Prefer setting-local checkouts under `vendor/`, `external/`, `code/vendor/`,
  or `data/source/`. Record exact URL, branch/commit, license evidence, and
  artifact path in `reports/findings.md` and `plan/events.jsonl`.
- If the paper says experiments live on a branch or separate data path, use that
  branch/path; do not keep probing the wrong default branch.
- If Python urllib fails due DNS or certificates, try `curl -L` before declaring
  the source unreachable.
- If dependencies are missing but the source is present, create or document a
  setting-local `.venv` / offline install path. Never install globally.

Experiment-running requirement:
- After source resolution or code edits, run the next real command available:
  `./harness.sh run-smoke`, `scripts/run_smoke.sh`, a C0 smoke script, or a
  newly implemented C0 baseline command.
- A dry-run/preflight is acceptable only when the real run is blocked by a
  named missing dependency, missing benchmark model endpoint/API quota, license
  gate, or human translation gate. If `config/benchmark_model.json` allows
  OpenAI, implement and run the OpenAI-backed command instead of stopping on a
  missing local/Modal Qwen endpoint. Log any blocker with the exact failed
  command.
- Do not claim empirical results from synthetic fixtures, validators, or
  preflights. They are contract checks only.

Version-control requirement:
- Once in a while, after a meaningful validated increment, commit and push your
  benchmark-setting changes to `origin` so progress is not trapped locally.
- If your pass finishes with a successful smoke/baseline, a resolved source/data
  blocker, or a working runner, attempt a commit and push before exiting the
  pass. Do this even if the parent harness may also try a scoped checkpoint.
- Do not commit/push after every tiny edit. A good push boundary is: source/data
  blocker resolved, smoke runner implemented, smoke/baseline artifact produced,
  or several related validators/docs/code changes completed together.
- Before committing, inspect `git status --short`. Stage only files relevant to
  this benchmark setting and shared harness/protocol files you intentionally
  changed. Do not stage unrelated user changes from sibling settings.
- Use a concise commit message naming the benchmark, for example
  `B5 wire NegotiationArena smoke source resolution`.
- If push fails due auth/network or the worktree contains unrelated ambiguous
  changes, log that in `plan/events.jsonl` and continue; do not block the
  experiment loop solely on push failure.

Your job in this pass:
1. Read goals.md, config/benchmark.json, reports/status.md, and plan/events.jsonl.
2. Pick the first unchecked or blocked task that can unlock a real run fastest.
3. Resolve source/data/install blockers from canonical paper/GitHub sources
   before writing more scaffolding.
4. Implement concrete code/docs/config needed for the next smoke or baseline run.
5. Run the narrowest real smoke/baseline command that is allowed by gates.
6. If you hit a blocker such as missing repo, missing dependency, quota, token
   limit, DNS, or unclear human decision, write it to plan/events.jsonl as JSONL
   and keep the setting usable.
7. Update goals.md checkboxes only when there is real evidence on disk.
8. Keep reports/findings.md concise and human-readable. It should say the current
   empirical story, any errors, and open questions. If no data has run, say that.
9. Do not fabricate results. Null or blocked state is acceptable.
10. Prefer small, verifiable increments over broad rewrites.
11. Commit and push periodically at meaningful validated milestones, following
    the version-control requirement above.
12. If this pass produced a successful smoke/baseline or unblocked executable
    runner, make one final scoped commit/push attempt before exiting; if it
    fails, record the push blocker in plan/events.jsonl.

At the end of the pass, the benchmark should have one of these:
- a new transcript/result artifact from a smoke/baseline run, or
- a source/data/license/dependency artifact proving why the real run cannot
  proceed yet, with the exact next command to run once unblocked.

Shared protocol:
{protocol}

Setting README:
{readme}

Benchmark config:
{json.dumps(config, indent=2, ensure_ascii=False)}

Smoke model config:
{json.dumps(smoke_model, indent=2, ensure_ascii=False)}

Benchmark model config:
{json.dumps(benchmark_model, indent=2, ensure_ascii=False)}

Current goals.md:
{goals}

Current status:
{status}

Recent events:
{events[-6000:]}
"""


def codex_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_FILE",
        "OPENAI_ORG_ID",
        "OPENAI_PROJECT_ID",
    ]:
        env.pop(key, None)
    return env


def run_codex_once(root: Path) -> int:
    if shutil.which("codex") is None:
        append_event(root, "codex", "codex CLI not found on PATH", "BLOCKED")
        write_status(root)
        return 127

    logs = root / "artifacts" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f"codex_once_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    prompt = build_codex_prompt(root)
    cmd = ["codex", "--cd", str(root), "exec", "--color", "never", prompt]
    if os.environ.get("CODEX_BYPASS_APPROVALS_AND_SANDBOX") == "1":
        cmd = [
            "codex",
            "--dangerously-bypass-approvals-and-sandbox",
            "--cd",
            str(root),
            "exec",
            "--color",
            "never",
            prompt,
        ]

    append_event(root, "codex", f"Starting Codex implementation pass; log={log.name}", "RUNNING")
    write_status(root)
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=root, env=codex_env(), stdout=fh, stderr=subprocess.STDOUT)

    status = "OK" if proc.returncode == 0 else "ERROR"
    append_event(root, "codex", f"Codex implementation pass exited {proc.returncode}; log={log.name}", status)
    if proc.returncode == 0:
        smoke_code = maybe_run_smoke_after_codex(root)
        if smoke_code is not None:
            append_event(root, "smoke", f"Post-Codex smoke/experiment attempt exited {smoke_code}", "OK" if smoke_code == 0 else "BLOCKED")
            if smoke_code == 0:
                maybe_commit_and_push(root, "successful post-Codex smoke")
    write_status(root)
    return proc.returncode


def loop(root: Path, sleep_seconds: int, max_iters: int) -> int:
    append_event(
        root,
        "loop",
        f"Starting Codex implementation loop sleep={sleep_seconds}s max_iters={max_iters or 'infinite'}",
        "RUNNING",
    )
    write_status(root)
    iteration = 0
    while max_iters <= 0 or iteration < max_iters:
        iteration += 1
        code = run_codex_once(root)
        if code != 0:
            append_event(root, "loop", f"Codex pass failed with {code}; sleeping before retry", "ERROR")
        else:
            append_event(root, "loop", f"Codex pass {iteration} completed", "OK")
        write_status(root)
        if max_iters > 0 and iteration >= max_iters:
            break
        time.sleep(sleep_seconds)
    append_event(root, "loop", "Loop exited", "OK")
    write_status(root)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("run-smoke")
    sub.add_parser("once")
    loop_parser = sub.add_parser("loop")
    loop_parser.add_argument("--sleep", type=int, default=900)
    loop_parser.add_argument("--max-iters", type=int, default=0)
    note_parser = sub.add_parser("note")
    note_parser.add_argument("message")
    error_parser = sub.add_parser("error")
    error_parser.add_argument("message")
    args = parser.parse_args()

    root = args.root.resolve()
    for path in ["artifacts/logs", "artifacts/results", "artifacts/transcripts", "plan", "reports"]:
        (root / path).mkdir(parents=True, exist_ok=True)

    cmd = args.cmd or "status"
    if cmd == "status":
        write_status(root)
        return 0
    if cmd == "check":
        return check(root)
    if cmd == "note":
        append_event(root, "note", args.message, "NOTE")
        write_status(root)
        return 0
    if cmd == "error":
        append_event(root, "error", args.message, "ERROR")
        write_status(root)
        return 0
    if cmd == "run-smoke":
        return run_smoke(root)
    if cmd == "once":
        return run_codex_once(root)
    if cmd == "loop":
        return loop(root, args.sleep, args.max_iters)
    parser.error(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
