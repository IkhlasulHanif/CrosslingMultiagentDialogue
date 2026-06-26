#!/usr/bin/env python3
"""Summarize rejected low-disagreement controls against retained BiVaD runs.

The script is API-free. It does not infer missing model results; it only
collects screening records, audit metrics, readout completeness, and short
transcript snippets from existing artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from audit_bivad_evidence import audit_artifact, discover_json_files, load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="*", help="JSON files or directories containing BiVaD artifacts.")
    parser.add_argument("--glob", default="*.json", help="Glob used when an input is a directory.")
    parser.add_argument(
        "--out-dir",
        default="code/bivad-evidence-audit",
        help="Directory for screening-control summary outputs.",
    )
    parser.add_argument("--min-debate-quality", type=float, default=0.67)
    parser.add_argument("--divergence-threshold", type=float, default=0.5)
    parser.add_argument("--snippet-chars", type=int, default=420)
    return parser.parse_args()


def short_text(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def readout_counts(data: dict[str, Any]) -> dict[str, str]:
    private = data.get("private_probes") if isinstance(data.get("private_probes"), list) else []
    observer = data.get("observer_readouts") if isinstance(data.get("observer_readouts"), list) else []
    return {
        "private_complete_flags": f"{sum(1 for item in private if item.get('complete'))}/{len(private)}",
        "observer_complete_flags": f"{sum(1 for item in observer if item.get('complete'))}/{len(observer)}",
    }


def artifact_row(path: Path, data: dict[str, Any], audit: dict[str, Any], snippet_chars: int) -> dict[str, Any]:
    transcript = data.get("transcript") if isinstance(data.get("transcript"), list) else []
    snippets = [
        {
            "turn": turn.get("turn"),
            "speaker": turn.get("speaker"),
            "language": turn.get("language"),
            "text": short_text(turn.get("text"), snippet_chars),
        }
        for turn in transcript[:4]
        if isinstance(turn, dict)
    ]
    return {
        "path": str(path),
        "run_id": audit["run_id"],
        "condition": audit["condition"],
        "model": data.get("model"),
        "seed": audit["seed"],
        "screening": audit["screening"],
        "debate_quality": audit["debate_quality"],
        "semantic_debate_depth": audit["semantic_debate_depth"],
        "language_compliance": audit["language_compliance"],
        "readout_completeness": readout_counts(data),
        "transcript_snippets": snippets,
    }


def retained_match_score(control: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, str]:
    score = 0.0
    reasons = []
    if control.get("model") == candidate.get("model"):
        score += 4
        reasons.append("same model")
    if control.get("topic") == candidate.get("topic"):
        score += 3
        reasons.append("same topic")
    if control.get("seed") == candidate.get("seed"):
        score += 2
        reasons.append("same seed")
    if candidate.get("condition") == "same-English":
        score += 1
        reasons.append("same-English retained baseline")
    adequate_rate = candidate["debate_quality"].get("adequate_rate")
    if isinstance(adequate_rate, (int, float)):
        score += adequate_rate * 2
        reasons.append(f"debate adequate rate {adequate_rate}")
    private_flags = candidate["readout_completeness"]["private_complete_flags"]
    observer_flags = candidate["readout_completeness"]["observer_complete_flags"]
    if private_flags.startswith("4/") and observer_flags.startswith("2/"):
        score += 1
        reasons.append("complete readouts")
    depth_rate = candidate["semantic_debate_depth"].get("semantic_depth_rate")
    if isinstance(depth_rate, (int, float)):
        score += depth_rate * 2
        reasons.append(f"semantic depth rate {depth_rate}")
    return score, ", ".join(reasons) or "fallback retained artifact"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BiVaD Screening Control Summary",
        "",
        f"Rejected controls: `{report['rejected_control_count']}`",
        "",
        f"Retained comparators: `{report['retained_comparator_count']}`",
        "",
    ]
    if report["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for blocker in report["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    for pair in report["comparisons"]:
        control = pair["control"]
        comparator = pair["retained_comparator"]
        lines.extend(
            [
                f"## `{control['run_id']}` vs `{comparator['run_id']}`",
                "",
                f"- Match basis: `{pair['match_basis']}`",
                f"- Control screening: `{json.dumps(control['screening'], sort_keys=True)}`",
                f"- Comparator screening: `{json.dumps(comparator['screening'], sort_keys=True)}`",
                f"- Control debate adequate rate: `{control['debate_quality']['adequate_rate']}` over `{control['debate_quality']['audited_response_turns']}` response turn(s)",
                f"- Comparator debate adequate rate: `{comparator['debate_quality']['adequate_rate']}` over `{comparator['debate_quality']['audited_response_turns']}` response turn(s)",
                f"- Control semantic depth rate: `{control['semantic_debate_depth']['semantic_depth_rate']}`; on-topic rate: `{control['semantic_debate_depth']['on_topic_rate']}`",
                f"- Comparator semantic depth rate: `{comparator['semantic_debate_depth']['semantic_depth_rate']}`; on-topic rate: `{comparator['semantic_debate_depth']['on_topic_rate']}`",
                f"- Control readout completeness flags: `{control['readout_completeness']}`",
                f"- Comparator readout completeness flags: `{comparator['readout_completeness']}`",
                "",
                "### Control Transcript Snippets",
                "",
            ]
        )
        for snippet in control["transcript_snippets"]:
            lines.append(
                f"- Turn {snippet['turn']} {snippet['speaker']} [{snippet['language']}]: {snippet['text']}"
            )
        lines.extend(["", "### Comparator Transcript Snippets", ""])
        for snippet in comparator["transcript_snippets"]:
            lines.append(
                f"- Turn {snippet['turn']} {snippet['speaker']} [{snippet['language']}]: {snippet['text']}"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_args = SimpleNamespace(
        min_debate_quality=args.min_debate_quality,
        divergence_threshold=args.divergence_threshold,
    )

    rejected_controls = []
    retained = []
    for path in discover_json_files(args.inputs or ["runs"], args.glob):
        if path.is_relative_to(out_dir.resolve()):
            continue
        data = load_json(path)
        if data is None:
            continue
        audit = audit_artifact(path, data, audit_args).__dict__
        screening = audit["screening"]
        if not screening:
            continue
        row = artifact_row(path, data, audit, args.snippet_chars)
        row["topic"] = audit["topic"]
        if audit["condition"] == "low-disagreement-control" and not screening.get("retained", False):
            rejected_controls.append(row)
        elif screening.get("retained", False) and not audit["synthetic"] and audit["condition"] != "unknown":
            retained.append(row)

    comparisons = []
    for control in rejected_controls:
        if not retained:
            break
        scored = sorted(
            (
                retained_match_score(control, candidate)[0],
                str(candidate.get("run_id") or ""),
                retained_match_score(control, candidate)[1],
                candidate,
            )
            for candidate in retained
        )
        score, _run_id, basis, comparator = scored[-1]
        comparisons.append(
            {
                "control": control,
                "retained_comparator": comparator,
                "match_score": score,
                "match_basis": basis,
            }
        )

    blockers = []
    if not rejected_controls:
        blockers.append("no rejected low-disagreement-control artifact found")
    if not retained:
        blockers.append("no retained real comparator artifact found")
    if rejected_controls and retained and not comparisons:
        blockers.append("could not pair rejected controls with retained comparators")
    if comparisons:
        if any(
            pair["control"]["readout_completeness"]["private_complete_flags"].startswith("0/")
            or pair["control"]["readout_completeness"]["observer_complete_flags"].startswith("0/")
            for pair in comparisons
        ):
            blockers.append("low-disagreement control still lacks reliable private/observer readouts")
        if any(
            pair["control"]["semantic_debate_depth"].get("semantic_depth_rate") is None
            for pair in comparisons
        ):
            blockers.append("low-disagreement control has too few response turns for semantic depth scoring")

    report = {
        "rejected_control_count": len(rejected_controls),
        "retained_comparator_count": len(retained),
        "rejected_controls": rejected_controls,
        "comparisons": comparisons,
        "blockers": blockers,
        "note": "This is a descriptive control summary from existing local artifacts, not a new experiment result.",
    }
    json_path = out_dir / "screening_control_summary.json"
    md_path = out_dir / "screening_control_summary.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if blockers:
        print("Screening-control summary has blockers.")
        return 1
    print("Screening-control summary completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
