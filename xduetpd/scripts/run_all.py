#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from cell_policy import jv_skip_active, runnable_cells, write_skip_report

ROOT = Path(__file__).resolve().parents[1]
S1_JV_REQUIRED_PHASES = {"core", "h5", "culture"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    args = parser.parse_args()
    guard_phase(args.phase)
    completed = completed_cells()
    runnable, skipped = runnable_cells(args.phase)
    write_skip_report(args.phase, skipped)
    selected = [data["cell_id"] for data in runnable if data["cell_id"] not in completed]
    for cell_id in selected:
        subprocess.run(["make", "run", f"CELL={cell_id}"], cwd=ROOT, check=True)
    print(
        json.dumps(
            {
                "phase": args.phase,
                "ran": selected,
                "skipped_completed": len(completed),
                "skipped_unavailable": skipped,
            },
            sort_keys=True,
        )
    )
    return 0


def guard_phase(phase: str) -> None:
    if phase not in S1_JV_REQUIRED_PHASES:
        return
    if jv_skip_active():
        return
    if s1_has_jv():
        return
    raise SystemExit(
        f"phase {phase} requires S1 JV variants; run M1 JV translation/adjudication first"
    )


def s1_has_jv() -> bool:
    path = ROOT / "data" / "s1" / "items.jsonl"
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row: dict[str, Any] = json.loads(line)
            return "JV" in (row.get("variants") or {})
    return False


def completed_cells() -> set[str]:
    path = ROOT / "results" / "manifest.json"
    out = set()
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") == "cell_result" and row.get("status") == "done":
                out.add(row["cell_id"])
    return out


if __name__ == "__main__":
    raise SystemExit(main())
