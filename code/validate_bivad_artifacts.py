#!/usr/bin/env python3
"""Validate BiVaD artifacts before treating them as empirical evidence.

This is a stricter gate than the audit package. The audit summarizes whatever
artifacts exist; this validator answers whether those artifacts are citable
empirical candidates for the paper draft.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from audit_bivad_evidence import (
    VALUE_KEYS,
    audit_artifact,
    discover_json_files,
    load_json,
    paired_condition_audit,
)


REQUIRED_CONDITIONS = {
    "mixed-language",
    "same-English",
    "same-target-language",
    "swapped-language",
    "translated-relay",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", help="JSON files or directories containing BiVaD artifacts.")
    parser.add_argument("--glob", default="*.json", help="Glob used when an input is a directory.")
    parser.add_argument(
        "--out-dir",
        default="code/bivad-evidence-audit",
        help="Directory for validation JSON and Markdown outputs.",
    )
    parser.add_argument("--min-debate-quality", type=float, default=0.67)
    parser.add_argument("--divergence-threshold", type=float, default=0.5)
    return parser.parse_args()


def value_readout_complete(items: Any) -> bool:
    if not isinstance(items, list) or not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            return False
        values = item.get("values")
        if not isinstance(values, dict):
            return False
        if not all(isinstance(values.get(key), (int, float)) for key in VALUE_KEYS):
            return False
    return True


def transcript_complete(transcript: Any) -> bool:
    if not isinstance(transcript, list) or not transcript:
        return False
    for index, turn in enumerate(transcript, start=1):
        if not isinstance(turn, dict):
            return False
        if not str(turn.get("speaker", "")).strip():
            return False
        if not str(turn.get("language", "")).strip():
            return False
        if not str(turn.get("text", "")).strip():
            return False
        try:
            int(turn.get("turn", index))
        except (TypeError, ValueError):
            return False
    return True


def artifact_blockers(data: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if audit["synthetic"] or data.get("non_empirical"):
        blockers.append("artifact is synthetic, non-empirical, dry-run, or placeholder")
    if str(data.get("artifact_type", "")).endswith("_manifest"):
        blockers.append("artifact is a run manifest, not an executed transcript")
    if not data.get("run_id"):
        blockers.append("missing run_id")
    if not data.get("created_at"):
        blockers.append("missing created_at")
    if not data.get("model"):
        blockers.append("missing model or backend identifier")
    if not data.get("seed") and data.get("seed") != 0:
        blockers.append("missing paired-run seed")
    if not transcript_complete(data.get("transcript")):
        blockers.append("missing or incomplete transcript turns")
    screening = data.get("screening")
    if not isinstance(screening, dict):
        blockers.append("missing initial-disagreement screening record")
    elif not screening.get("retained", False):
        blockers.append("screening rejected this candidate")
    if not value_readout_complete(data.get("private_probes")):
        blockers.append("missing complete private probe value readouts")
    if not value_readout_complete(data.get("observer_readouts")):
        blockers.append("missing complete observer readout values")

    debate_quality = audit["debate_quality"]
    if debate_quality["audited_response_turns"] == 0:
        blockers.append("no response turns with opponent context for debate-quality audit")
    elif debate_quality["adequate_rate"] is None or debate_quality["adequate_rate"] < 1.0:
        blockers.append("at least one response turn fails debate-quality audit")

    compliance = audit["language_compliance"]
    if compliance["declared_compliance_rate"] is None:
        blockers.append("no language compliance audit available")
    elif compliance["declared_compliance_rate"] < 1.0:
        blockers.append("declared language compliance below 100%")
    if compliance["copied_opponent_language_events"]:
        blockers.append("opponent-language copying events detected")
    return blockers


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# BiVaD Artifact Validation",
        "",
        f"Artifacts checked: `{summary['artifact_count']}`",
        "",
        f"Citable empirical candidates: `{summary['citable_candidate_count']}`",
        "",
        f"Complete real paired sets: `{summary['complete_real_paired_sets']}`",
        "",
    ]
    if summary["global_blockers"]:
        lines.append("## Global Blockers")
        lines.append("")
        for blocker in summary["global_blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    if not report["artifacts"]:
        lines.append("No artifacts were available for validation.")
        lines.append("")
    for artifact in report["artifacts"]:
        lines.extend(
            [
                f"### `{artifact['run_id']}`",
                "",
                f"- Path: `{artifact['path']}`",
                f"- Condition: `{artifact['condition']}`",
                f"- Citable candidate: `{artifact['citable_candidate']}`",
                f"- Blockers: `{'; '.join(artifact['blockers']) if artifact['blockers'] else 'none'}`",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    files = [
        path
        for path in discover_json_files(args.inputs, args.glob)
        if not path.is_relative_to(out_dir)
    ]
    audit_args = SimpleNamespace(
        min_debate_quality=args.min_debate_quality,
        divergence_threshold=args.divergence_threshold,
    )
    rows = []
    audits = []
    for path in files:
        data = load_json(path)
        if data is None:
            continue
        artifact_audit = audit_artifact(path, data, audit_args)
        audit = artifact_audit.__dict__
        audits.append(artifact_audit)
        blockers = artifact_blockers(data, audit)
        rows.append(
            {
                "path": str(path),
                "run_id": audit["run_id"],
                "condition": audit["condition"],
                "topic": audit["topic"],
                "seed": audit["seed"],
                "agent_prior_hash": audit["agent_prior_hash"],
                "synthetic": audit["synthetic"],
                "citable_candidate": not blockers,
                "blockers": blockers,
            }
        )

    paired = paired_condition_audit(audits)
    citable_count = sum(1 for row in rows if row["citable_candidate"])
    global_blockers = []
    if not rows:
        global_blockers.append("no JSON artifacts found")
    if citable_count == 0:
        global_blockers.append("no artifacts pass the citable empirical candidate gate")
    if not paired["complete_paired_sets"]:
        global_blockers.append(
            "no complete real paired set covers mixed, same-English, same-target-language, swapped, and translated-relay conditions"
        )
    available_conditions = {row["condition"] for row in rows}
    missing_conditions = sorted(REQUIRED_CONDITIONS - available_conditions)
    if missing_conditions:
        global_blockers.append(f"missing condition artifacts: {', '.join(missing_conditions)}")

    report = {
        "summary": {
            "artifact_count": len(rows),
            "citable_candidate_count": citable_count,
            "complete_real_paired_sets": len(paired["complete_paired_sets"]),
            "global_blockers": global_blockers,
        },
        "artifacts": rows,
        "paired_condition_audit": paired,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "validation.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_dir / 'validation.json'}")
    print(f"Wrote {out_dir / 'validation.md'}")
    if global_blockers:
        print("Validation found blockers; see validation.md.")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
