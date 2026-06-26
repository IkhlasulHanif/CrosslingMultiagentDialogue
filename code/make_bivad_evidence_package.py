#!/usr/bin/env python3
"""Build a compact BiVaD evidence package from validated artifacts.

This script does not run models and does not fill missing results. It reads the
current audit and validation outputs, selects artifacts that already pass the
citation gate, and writes a small JSON/Markdown package with metrics, short
transcript spans, recovered probe/readout values, and explicit blockers.
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from typing import Any

from audit_bivad_evidence import VALUE_KEYS, recover_readout_values, vector_distance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-json",
        default="code/bivad-evidence-audit/audit.json",
        help="Audit JSON produced by audit_bivad_evidence.py.",
    )
    parser.add_argument(
        "--validation-json",
        default="code/bivad-evidence-audit/validation.json",
        help="Validation JSON produced by validate_bivad_artifacts.py.",
    )
    parser.add_argument(
        "--out-dir",
        default="code/bivad-evidence-audit",
        help="Directory for evidence_package.json and evidence_package.md.",
    )
    parser.add_argument(
        "--snippet-chars",
        type=int,
        default=260,
        help="Maximum characters per transcript/probe excerpt.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def truncate(text: Any, limit: int) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)].rstrip() + "..."


def validated_rows(validation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in validation.get("artifacts") or []:
        if isinstance(row, dict) and row.get("citable_candidate"):
            rows[str(row.get("run_id"))] = row
    return rows


def artifact_audits(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("run_id")): row
        for row in audit.get("artifacts") or []
        if isinstance(row, dict)
    }


def transcript_span(transcript: list[dict[str, Any]], snippet_chars: int) -> list[dict[str, Any]]:
    if not transcript:
        return []
    selected: list[dict[str, Any]] = []
    for turn in transcript:
        if not isinstance(turn, dict):
            continue
        has_marker = any(
            str(turn.get("text", "")).lower().find(marker) >= 0
            for marker in ("strongest", "poin kuat", "counterargument", "belum berubah", "has not changed")
        )
        if has_marker or int(turn.get("turn", 0) or 0) in (1, len(transcript)):
            selected.append(
                {
                    "turn": turn.get("turn"),
                    "speaker": turn.get("speaker"),
                    "language": turn.get("language"),
                    "text_excerpt": truncate(turn.get("text", ""), snippet_chars),
                }
            )
        if len(selected) >= 3:
            break
    return selected


def readout_summary(items: Any, snippet_chars: int) -> list[dict[str, Any]]:
    rows = []
    if not isinstance(items, list):
        return rows
    for item in items:
        if not isinstance(item, dict):
            continue
        values, trace = recover_readout_values(item)
        rows.append(
            {
                "agent_id": item.get("agent_id"),
                "turn": item.get("turn"),
                "complete_after_recovery": all(key in values for key in VALUE_KEYS),
                "values": {key: values.get(key) for key in VALUE_KEYS if key in values},
                "recovery_event_count": len(trace),
                "raw_text_excerpt": truncate(item.get("raw_text", ""), snippet_chars),
            }
        )
    return rows


def shift_rows(private_rows: list[dict[str, Any]], observer_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    private_by_agent_turn = {
        (str(row["agent_id"]), int(row["turn"])): row["values"]
        for row in private_rows
        if row.get("agent_id") and row.get("turn") is not None and row.get("values")
    }
    observer_by_agent_turn = {
        (str(row["agent_id"]), int(row["turn"])): row["values"]
        for row in observer_rows
        if row.get("agent_id") and row.get("turn") is not None and row.get("values")
    }
    agents = sorted({agent for agent, _turn in private_by_agent_turn})
    rows = []
    for agent in agents:
        turns = sorted(turn for row_agent, turn in private_by_agent_turn if row_agent == agent)
        if not turns:
            continue
        start_turn = turns[0]
        end_turn = turns[-1]
        private_shift = None
        if start_turn != end_turn:
            private_shift = vector_distance(
                private_by_agent_turn[(agent, start_turn)],
                private_by_agent_turn[(agent, end_turn)],
            )
        public_private_gap = None
        if (agent, end_turn) in observer_by_agent_turn:
            public_private_gap = vector_distance(
                private_by_agent_turn[(agent, end_turn)],
                observer_by_agent_turn[(agent, end_turn)],
            )
        rows.append(
            {
                "agent_id": agent,
                "private_start_turn": start_turn,
                "private_end_turn": end_turn,
                "private_shift_distance": private_shift,
                "final_private_public_distance": public_private_gap,
            }
        )
    return rows


def build_package(args: argparse.Namespace) -> dict[str, Any]:
    audit = load_json(Path(args.audit_json))
    validation = load_json(Path(args.validation_json))
    citable = validated_rows(validation)
    audits_by_run = artifact_audits(audit)
    artifacts = []
    for run_id, validation_row in sorted(citable.items()):
        path = Path(str(validation_row["path"]))
        data = load_json(path)
        audit_row = audits_by_run.get(run_id, {})
        private = readout_summary(data.get("private_probes"), args.snippet_chars)
        observer = readout_summary(data.get("observer_readouts"), args.snippet_chars)
        artifacts.append(
            {
                "run_id": run_id,
                "condition": data.get("condition"),
                "path": str(path),
                "model": data.get("model"),
                "seed": data.get("seed"),
                "topic": data.get("topic"),
                "screening": data.get("screening"),
                "metrics": {
                    "transcript_turns": len(data.get("transcript") or []),
                    "debate_quality_adequate_rate": (audit_row.get("debate_quality") or {}).get("adequate_rate"),
                    "language_declared_compliance_rate": (
                        audit_row.get("language_compliance") or {}
                    ).get("declared_compliance_rate"),
                    "private_readouts_complete_after_recovery": (
                        (audit_row.get("readout_normalization") or {}).get("private_probes") or {}
                    ).get("complete_after_recovery"),
                    "observer_readouts_complete_after_recovery": (
                        (audit_row.get("readout_normalization") or {}).get("observer_readouts") or {}
                    ).get("complete_after_recovery"),
                    "flagged_private_public_gaps": len(
                        ((audit_row.get("private_public_divergence") or {}).get("flagged_private_public_gaps") or [])
                    ),
                },
                "transcript_snippets": transcript_span(data.get("transcript") or [], args.snippet_chars),
                "private_probe_outputs": private,
                "observer_readout_outputs": observer,
                "shift_summary": shift_rows(private, observer),
                "readout_recovery_note": (
                    "Values are reported only after the existing audited recovery path accepts numeric 1-7 "
                    "values emitted by the model under unambiguous aliases."
                ),
            }
        )

    failed_conditions = []
    for row in validation.get("artifacts") or []:
        if not isinstance(row, dict) or row.get("citable_candidate"):
            continue
        run_id = str(row.get("run_id", ""))
        if run_id.startswith("20260626T173227Z-") and row.get("condition") in {
            "same-target-language",
            "translated-relay",
        }:
            failed_conditions.append(
                {
                    "run_id": run_id,
                    "condition": row.get("condition"),
                    "blockers": row.get("blockers") or [],
                    "path": row.get("path"),
                }
            )

    included_conditions = sorted({str(item["condition"]) for item in artifacts})
    five_conditions_required = {"mixed-language", "same-English", "same-target-language", "swapped-language", "translated-relay"}
    five_cond_ready = five_conditions_required <= set(included_conditions)
    paired_audit = validation.get("paired_condition_audit") or {}
    ready_sets = [s for s in (paired_audit.get("complete_paired_sets") or []) if s.get("ready_with_real_artifacts")]

    failed_assumptions = []
    if not five_cond_ready:
        failed_assumptions.append("This is not a complete five-condition comparison.")
    if failed_conditions:
        blocked_ids = [c["run_id"] for c in failed_conditions]
        failed_assumptions.append(f"Some paired artifacts are not citable (blocked): {', '.join(blocked_ids)}.")
    if not ready_sets:
        failed_assumptions.append("No complete real paired set found for cross-lingual outcome comparison.")
    failed_assumptions.extend([
        "Language compliance remains declaration-based plus heuristic warnings, not publication-grade language ID.",
        "Readout values rely on audited recovery from model-emitted aliases; raw parse failures are not silently repaired.",
    ])

    return {
        "summary": {
            "source_audit_json": str(Path(args.audit_json)),
            "source_validation_json": str(Path(args.validation_json)),
            "citable_candidate_count": len(artifacts),
            "included_conditions": included_conditions,
            "five_condition_comparison_ready": five_cond_ready,
            "complete_real_paired_sets": len(ready_sets),
            "failed_assumptions": failed_assumptions,
        },
        "artifacts": artifacts,
        "excluded_latest_paired_conditions": failed_conditions,
    }


def render_markdown(package: dict[str, Any]) -> str:
    summary = package["summary"]
    lines = [
        "# BiVaD Compact Evidence Package",
        "",
        f"Citable candidates included: `{summary['citable_candidate_count']}`",
        "",
        f"Conditions included: `{', '.join(summary['included_conditions']) or 'none'}`",
        "",
        "## Guardrails",
        "",
    ]
    for item in summary["failed_assumptions"]:
        lines.append(f"- {item}")
    lines.append("")
    if not package["artifacts"]:
        lines.extend(
            [
                "No citable candidates were available from the validation report.",
                "",
                "Smallest next action: produce at least one non-synthetic artifact that passes "
                "`code/validate_bivad_artifacts.py`.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(["## Metrics", ""])
    lines.append(
        "| run_id | condition | seed | debate_quality | language_compliance | private_readouts | observer_readouts | private_public_gaps |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in package["artifacts"]:
        metrics = item["metrics"]
        lines.append(
            "| {run_id} | {condition} | {seed} | {dq} | {lang} | {private} | {observer} | {gaps} |".format(
                run_id=item["run_id"],
                condition=item["condition"],
                seed=item["seed"],
                dq=metrics["debate_quality_adequate_rate"],
                lang=metrics["language_declared_compliance_rate"],
                private=metrics["private_readouts_complete_after_recovery"],
                observer=metrics["observer_readouts_complete_after_recovery"],
                gaps=metrics["flagged_private_public_gaps"],
            )
        )
    lines.append("")

    for item in package["artifacts"]:
        lines.extend(
            [
                f"## `{item['run_id']}`",
                "",
                f"- Condition: `{item['condition']}`",
                f"- Topic: `{item['topic']}`",
                f"- Artifact: `{item['path']}`",
                f"- Screening retained: `{(item.get('screening') or {}).get('retained')}`; "
                f"value distance: `{(item.get('screening') or {}).get('value_distance')}`",
                "",
                "### Transcript Snippets",
                "",
            ]
        )
        for snippet in item["transcript_snippets"]:
            lines.append(
                f"- Turn `{snippet['turn']}` `{snippet['speaker']}`/{snippet['language']}: "
                f"{snippet['text_excerpt']}"
            )
        lines.extend(["", "### Shift And Divergence", ""])
        for row in item["shift_summary"]:
            lines.append(
                "- Agent `{agent}` private shift `{shift}` from turn `{start}` to `{end}`; "
                "final private-public distance `{gap}`.".format(
                    agent=row["agent_id"],
                    shift=row["private_shift_distance"],
                    start=row["private_start_turn"],
                    end=row["private_end_turn"],
                    gap=row["final_private_public_distance"],
                )
            )
        lines.extend(["", "### Probe/Readout Excerpts", ""])
        for probe in item["private_probe_outputs"][:2]:
            values = json.dumps(probe["values"], sort_keys=True)
            lines.append(
                f"- Private `{probe['agent_id']}` turn `{probe['turn']}` complete "
                f"`{probe['complete_after_recovery']}` values `{values}`."
            )
        for readout in item["observer_readout_outputs"][:2]:
            values = json.dumps(readout["values"], sort_keys=True)
            lines.append(
                f"- Observer `{readout['agent_id']}` turn `{readout['turn']}` complete "
                f"`{readout['complete_after_recovery']}` values `{values}`."
            )
        lines.append("")

    lines.extend(["## Excluded Latest Paired Conditions", ""])
    for item in package["excluded_latest_paired_conditions"]:
        wrapped = textwrap.fill("; ".join(item["blockers"]), width=100)
        lines.append(f"- `{item['run_id']}` `{item['condition']}`: {wrapped}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    package = build_package(args)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evidence_package.json").write_text(
        json.dumps(package, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "evidence_package.md").write_text(render_markdown(package), encoding="utf-8")
    print(f"Wrote {out_dir / 'evidence_package.json'}")
    print(f"Wrote {out_dir / 'evidence_package.md'}")
    if package["summary"]["citable_candidate_count"] == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
