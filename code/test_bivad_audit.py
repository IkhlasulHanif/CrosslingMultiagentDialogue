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


def test_local_lm_dry_run_manifest_does_not_count_as_result() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        runs = tmp_path / "runs"
        audit_out = tmp_path / "audit"
        run_command(
            [
                sys.executable,
                "code/run_bivad_local_lm.py",
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


def test_local_lm_preflight_does_not_count_as_result() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        preflight_out = tmp_path / "preflight"
        audit_out = tmp_path / "audit"
        completed = subprocess.run(
            [
                sys.executable,
                "code/preflight_bivad_local_lm.py",
                "--search-root",
                str(tmp_path / "missing-model-root"),
                "--out-dir",
                str(preflight_out),
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        run_command(
            [
                sys.executable,
                "code/audit_bivad_evidence.py",
                str(preflight_out),
                "--out-dir",
                str(audit_out),
            ]
        )
        report = json.loads((audit_out / "audit.json").read_text(encoding="utf-8"))

    assert completed.returncode in (0, 1)
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


def test_readout_key_normalization_recovers_unambiguous_aliases() -> None:
    from audit_bivad_evidence import VALUE_KEYS, recover_readout_values

    item = {
        "agent_id": "A",
        "turn": 4,
        "values": {"Universalism": 5, "security ": "4", "Conformation": 3},
        "raw_text": (
            '{"Benevolence ":5,"%self_direction%":4,!tradition! : 3,'
            '#achievement#: 2,&power& : 1,"evidence":"raw model text"}'
        ),
    }
    values, trace = recover_readout_values(item)

    assert all(key in values for key in VALUE_KEYS)
    assert values["universalism"] == 5
    assert values["security"] == 4
    assert values["conformity"] == 3
    assert values["benevolence"] == 5
    assert values["self_direction"] == 4
    assert values["tradition"] == 3
    assert values["achievement"] == 2
    assert values["power"] == 1
    assert any(event.get("source") == "raw_text" for event in trace)


def test_evidence_package_includes_only_validated_candidates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        runs = tmp_path / "runs"
        audit_out = tmp_path / "audit"
        package_out = tmp_path / "package"
        run_command(
            [
                sys.executable,
                "code/make_bivad_audit_fixtures.py",
                "--out-dir",
                str(runs),
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
        completed = subprocess.run(
            [
                sys.executable,
                "code/validate_bivad_artifacts.py",
                str(runs),
                "--out-dir",
                str(audit_out),
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        package_completed = subprocess.run(
            [
                sys.executable,
                "code/make_bivad_evidence_package.py",
                "--audit-json",
                str(audit_out / "audit.json"),
                "--validation-json",
                str(audit_out / "validation.json"),
                "--out-dir",
                str(package_out),
            ],
            cwd=REPO_ROOT,
            check=False,
        )
        package = json.loads((package_out / "evidence_package.json").read_text(encoding="utf-8"))

    assert completed.returncode == 1
    assert package_completed.returncode == 1
    assert package["summary"]["citable_candidate_count"] == 0
    assert package["artifacts"] == []
    assert "This is not a complete five-condition comparison." in package["summary"]["failed_assumptions"]


def main() -> int:
    test_synthetic_fixtures_do_not_count_as_results()
    test_dry_run_manifest_does_not_count_as_result()
    test_local_lm_dry_run_manifest_does_not_count_as_result()
    test_local_lm_preflight_does_not_count_as_result()
    test_local_torch_schema_checks_do_not_count_as_results()
    test_validation_rejects_synthetic_schema_checks()
    test_readout_key_normalization_recovers_unambiguous_aliases()
    test_evidence_package_includes_only_validated_candidates()
    print("bivad audit regression checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
