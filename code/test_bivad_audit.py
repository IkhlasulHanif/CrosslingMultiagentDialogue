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


def test_dry_run_manifest_does_not_count_as_result() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        runs = tmp_path / "runs"
        audit_out = tmp_path / "audit"
        run_command(
            [
                sys.executable,
                "code/run_bivad_pilot.py",
                "--out-dir",
                str(runs),
                "--conditions",
                "mixed-language",
            ]
        )
        run_command(
            [
                sys.executable,
                "code/audit_bivad_evidence.py",
                str(runs),
                "--out-dir",
                str(audit_out),
            ]
        )
        report = json.loads((audit_out / "audit.json").read_text(encoding="utf-8"))

    summary = report["summary"]
    assert summary["artifact_count"] == 1
    assert summary["synthetic_artifact_count"] == 1
    assert summary["real_artifact_count"] == 0
    assert summary["executed_results_present"] is False


def test_local_torch_schema_checks_do_not_count_as_results() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        runs = tmp_path / "local-torch"
        audit_out = tmp_path / "audit"
        run_command(
            [
                sys.executable,
                "code/run_bivad_local_torch.py",
                "--out-dir",
                str(runs),
                "--include-low-disagreement-control",
            ]
        )
        run_command(
            [
                sys.executable,
                "code/audit_bivad_evidence.py",
                str(runs),
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
    assert summary["screening"]["retained"] == 5
    assert summary["screening"]["rejected"] == 1

    paired = report["paired_condition_audit"]
    assert paired["complete_paired_sets"] == []
    ready_groups = [
        item
        for item in paired["incomplete_paired_sets"]
        if item["ready_for_cross_lingual_outcome_comparison"]
    ]
    assert len(ready_groups) == 1
    assert ready_groups[0]["ready_with_real_artifacts"] is False


def test_validation_rejects_synthetic_schema_checks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        runs = tmp_path / "local-torch"
        validation_out = tmp_path / "validation"
        run_command(
            [
                sys.executable,
                "code/run_bivad_local_torch.py",
                "--out-dir",
                str(runs),
                "--include-low-disagreement-control",
            ]
        )
        completed = subprocess.run(
            [
                sys.executable,
                "code/validate_bivad_artifacts.py",
                str(runs),
                "--out-dir",
                str(validation_out),
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        report = json.loads((validation_out / "validation.json").read_text(encoding="utf-8"))

    assert completed.returncode == 1
    assert report["summary"]["artifact_count"] == 6
    assert report["summary"]["citable_candidate_count"] == 0
    assert "no artifacts pass the citable empirical candidate gate" in report["summary"]["global_blockers"]
    assert all(
        "artifact is synthetic, non-empirical, dry-run, or placeholder" in item["blockers"]
        for item in report["artifacts"]
    )


def main() -> int:
    test_synthetic_fixtures_do_not_count_as_results()
    test_dry_run_manifest_does_not_count_as_result()
    test_local_torch_schema_checks_do_not_count_as_results()
    test_validation_rejects_synthetic_schema_checks()
    print("bivad audit regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
