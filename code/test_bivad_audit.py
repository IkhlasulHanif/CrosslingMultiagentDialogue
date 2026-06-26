#!/usr/bin/env python3
"""Regression checks for the BiVaD audit harness."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(args: list[str]) -> None:
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def test_synthetic_fixtures_do_not_count_as_results() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fixtures = tmp_path / "fixtures"
        audit_out = tmp_path / "audit"
        run_command(
            [
                sys.executable,
                "code/make_bivad_audit_fixtures.py",
                "--out-dir",
                str(fixtures),
            ]
        )
        run_command(
            [
                sys.executable,
                "code/audit_bivad_evidence.py",
                str(fixtures),
                "--out-dir",
                str(audit_out),
            ]
        )
        report = json.loads((audit_out / "audit.json").read_text(encoding="utf-8"))

    summary = report["summary"]
    assert summary["artifact_count"] == 6
    assert summary["synthetic_artifact_count"] == 6
    assert summary["real_artifact_count"] == 0
    assert summary["executed_results_present"] is False

    paired = report["paired_condition_audit"]
    assert paired["complete_paired_sets"] == []
    fixture_groups = [
        item
        for item in paired["incomplete_paired_sets"]
        if item["ready_for_cross_lingual_outcome_comparison"]
    ]
    assert len(fixture_groups) == 1
    assert fixture_groups[0]["synthetic_artifacts"] == 5
    assert fixture_groups[0]["ready_with_real_artifacts"] is False


def main() -> int:
    test_synthetic_fixtures_do_not_count_as_results()
    print("bivad audit regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
