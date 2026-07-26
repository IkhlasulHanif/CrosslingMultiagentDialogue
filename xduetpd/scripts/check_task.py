#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from cell_policy import runnable_cells


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    args = parser.parse_args()
    checks: dict[str, Callable[[], list[str]]] = {
        "M0.1": check_m0_1,
        "M1.1": check_m1_1,
        "M2.1": check_m2_1,
        "M2.3": lambda: check_phase_complete("pilot"),
        "M3.1": lambda: check_phase_complete("core"),
        "M3.2": lambda: check_phase_complete("h5"),
        "M3.3": lambda: check_phase_complete("safety"),
        "M3.4": lambda: check_phase_complete("culture"),
        "M4.1": check_m4_1,
        "M5.1": check_m5_1,
    }
    if args.task_id not in checks:
        raise SystemExit(f"unknown task id: {args.task_id}")
    evidence = ROOT / "reports" / "evidence" / args.task_id
    evidence.mkdir(parents=True, exist_ok=True)
    failures = checks[args.task_id]()
    output = evidence / "check_output.txt"
    if failures:
        output.write_text("FAIL\n" + "\n".join(f"- {failure}" for failure in failures) + "\n", encoding="utf-8")
        print(output.read_text(encoding="utf-8"))
        return 1
    output.write_text("PASS\n", encoding="utf-8")
    print(output.read_text(encoding="utf-8"))
    return 0


def check_m0_1() -> list[str]:
    failures = require_paths(
        [
            "STATE.yaml",
            "Makefile",
            "configs/appeals.yaml",
            "configs/cells/m0_smoke.yaml",
            "results/manifest.json",
        ]
    )
    failures.extend(validate_jsonl_file(ROOT / "results" / "jsonl" / "m0_smoke.jsonl", kind="turn"))
    failures.extend(validate_jsonl_file(ROOT / "results" / "summaries" / "m0_smoke.jsonl", kind="summary"))
    if not list((ROOT / "inspect").glob("m0_smoke_*.md")):
        failures.append("missing inspect/m0_smoke_*.md transcript")
    proc = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_schema.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (ROOT / "reports" / "evidence" / "M0.1" / "pytest_output.txt").write_text(proc.stdout, encoding="utf-8")
    if proc.returncode != 0:
        failures.append("pytest tests/test_schema.py failed")
    return failures


def check_m1_1() -> list[str]:
    failures = require_paths(["reports/evidence/M1.1/ingest_report.md", "data/s1/jv_review.csv"])
    report = ROOT / "reports" / "evidence" / "M1.1" / "ingest_report.md"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        if "- status: pass" not in text:
            failures.append("ingest report is not a strict pass")
    return failures


def check_m2_1() -> list[str]:
    failures = require_paths(["configs/cells_index.json"])
    index_path = ROOT / "configs" / "cells_index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        expected = {"m0": 1, "pilot": 12, "core": 144, "h5": 50, "safety": 8, "culture": 16}
        if index.get("by_phase") != expected:
            failures.append(f"unexpected by_phase counts: {index.get('by_phase')}")
        for cell_id in index.get("cells", []):
            if not (ROOT / "configs" / "cells" / f"{cell_id}.yaml").exists():
                failures.append(f"missing cell config {cell_id}")
    return failures


def check_phase_complete(phase: str) -> list[str]:
    failures: list[str] = []
    planned = planned_cells(phase)
    completed = completed_cells()
    missing = [cell_id for cell_id in planned if cell_id not in completed]
    if missing:
        failures.append(f"{phase} missing completed cells: {missing[:20]} count={len(missing)}")
    return failures


def check_m4_1() -> list[str]:
    failures = require_done(["M1.1", "M2.1", "M2.3", "M3.1", "M3.2", "M3.3", "M3.4"])
    if failures:
        return failures
    failures = require_paths(
        [
            "reports/findings/REPORT.md",
            "reports/findings/verdicts.yaml",
            "reports/findings/figures/F1.png",
            "reports/findings/figures/F2.png",
            "reports/findings/figures/F3.png",
            "reports/findings/figures/F4.png",
            "reports/findings/figures/F5.png",
        ]
    )
    verdicts_path = ROOT / "reports" / "findings" / "verdicts.yaml"
    if verdicts_path.exists():
        verdicts = yaml.safe_load(verdicts_path.read_text(encoding="utf-8")) or {}
        for hyp in ["H1", "H2", "H3", "H4", "H5", "H7"]:
            if hyp not in verdicts:
                failures.append(f"missing verdict {hyp}")
            elif verdicts[hyp].get("verdict") not in {"supported", "refuted", "null", "invalid"}:
                failures.append(f"invalid verdict enum for {hyp}")
    report = ROOT / "reports" / "findings" / "REPORT.md"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        for marker in ["A. Data Health", "B. Per-Hypothesis", "C. Interpretation", "D. Null", "E. Figures", "F. Release"]:
            if marker not in text:
                failures.append(f"REPORT.md missing section marker {marker}")
    return failures


def check_m5_1() -> list[str]:
    failures = []
    if not (ROOT / "reports" / "approvals" / "m5.md").exists():
        failures.append("M5 requires explicit reports/approvals/m5.md before Spyfall fork work")
    return failures


def require_paths(rel_paths: list[str]) -> list[str]:
    return [f"missing {rel}" for rel in rel_paths if not (ROOT / rel).exists()]


def require_done(task_ids: list[str]) -> list[str]:
    state_path = ROOT / "STATE.yaml"
    if not state_path.exists():
        return ["STATE.yaml missing"]
    rows = yaml.safe_load(state_path.read_text(encoding="utf-8")) or []
    statuses = {row["id"]: row.get("status") for row in rows}
    return [
        f"{task_id} must be done before this check"
        for task_id in task_ids
        if statuses.get(task_id) != "done"
    ]


def validate_jsonl_file(path: Path, kind: str) -> list[str]:
    failures: list[str] = []
    if not path.exists():
        return [f"missing {path.relative_to(ROOT)}"]
    if kind == "turn":
        from runner.schema import validate_turn_row as validate
    else:
        from runner.schema import validate_summary_row as validate
    with path.open("r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    if not rows:
        failures.append(f"{path.relative_to(ROOT)} has no rows")
    for idx, row in enumerate(rows, start=1):
        try:
            validate(row)
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)}:{idx}: {exc}")
    return failures


def planned_cells(phase: str) -> list[str]:
    runnable, skipped = runnable_cells(phase)
    skip_report = ROOT / "reports" / "evidence" / "run" / f"skipped_{phase}.md"
    if skipped and not skip_report.exists():
        failures_text = "\n".join(f"- {row['cell_id']}: {row['reason']}" for row in skipped)
        skip_report.parent.mkdir(parents=True, exist_ok=True)
        skip_report.write_text(
            f"# Skipped Cells: {phase}\n\n- skipped: {len(skipped)}\n\n{failures_text}\n",
            encoding="utf-8",
        )
    return [data["cell_id"] for data in runnable]


def completed_cells() -> set[str]:
    path = ROOT / "results" / "manifest.json"
    out = set()
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("type") == "cell_result" and row.get("status") == "done":
                out.add(row["cell_id"])
    return out


if __name__ == "__main__":
    raise SystemExit(main())
