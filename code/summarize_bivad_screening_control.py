#!/usr/bin/env python3
"""Summarize rejected low-disagreement controls against retained BiVaD runs.

The script is API-free. It does not infer missing model results; it only
collects screening records, audit metrics, readout completeness, and short
transcript snippets from existing artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from audit_bivad_evidence import audit_artifact, discover_json_files, load_json


VALUE_KEYS = [
    "achievement",
    "benevolence",
    "conformity",
    "power",
    "security",
    "self_direction",
    "tradition",
    "universalism",
]


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


def euclidean(v1: dict[str, Any], v2: dict[str, Any]) -> float | None:
    if not all(k in v1 and k in v2 for k in VALUE_KEYS):
        return None
    return round(math.sqrt(sum((float(v1[k]) - float(v2[k])) ** 2 for k in VALUE_KEYS)), 6)


def l1_distance(v1: dict[str, Any], v2: dict[str, Any]) -> float | None:
    if not all(k in v1 and k in v2 for k in VALUE_KEYS):
        return None
    return round(sum(abs(float(v1[k]) - float(v2[k])) for k in VALUE_KEYS), 6)


def private_shift_summary(data: dict[str, Any]) -> dict[str, Any]:
    probes = data.get("private_probes") if isinstance(data.get("private_probes"), list) else []
    by_agent: dict[str, list[dict[str, Any]]] = {}
    for item in probes:
        if not isinstance(item, dict) or not item.get("complete"):
            continue
        values = item.get("values")
        if item.get("agent_id") and isinstance(values, dict):
            by_agent.setdefault(str(item["agent_id"]), []).append(item)

    summary: dict[str, Any] = {}
    for agent_id, items in sorted(by_agent.items()):
        ordered = sorted(items, key=lambda item: item.get("turn", 0))
        if len(ordered) < 2:
            continue
        initial = ordered[0]
        final = ordered[-1]
        shift = euclidean(initial["values"], final["values"])
        summary[agent_id] = {
            "initial_turn": initial.get("turn"),
            "final_turn": final.get("turn"),
            "initial_values": initial["values"],
            "final_values": final["values"],
            "shift": shift,
        }
    return summary


def private_agent_distances(shift_summary: dict[str, Any]) -> dict[str, Any]:
    a = shift_summary.get("A")
    b = shift_summary.get("B")
    if not a or not b:
        return {}
    return {
        "initial_l1": l1_distance(a["initial_values"], b["initial_values"]),
        "initial_l2": euclidean(a["initial_values"], b["initial_values"]),
        "final_l1": l1_distance(a["final_values"], b["final_values"]),
        "final_l2": euclidean(a["final_values"], b["final_values"]),
    }


def final_observer_summary(data: dict[str, Any]) -> dict[str, Any]:
    readouts = data.get("observer_readouts") if isinstance(data.get("observer_readouts"), list) else []
    summary: dict[str, Any] = {}
    for item in readouts:
        if not isinstance(item, dict) or not item.get("complete"):
            continue
        values = item.get("values")
        if item.get("agent_id") and isinstance(values, dict):
            summary[str(item["agent_id"])] = {
                "turn": item.get("turn"),
                "values": values,
            }
    return summary


def transcript_signature(data: dict[str, Any]) -> list[str]:
    transcript = data.get("transcript") if isinstance(data.get("transcript"), list) else []
    return [
        " ".join(str(turn.get("text") or "").split()).lower()
        for turn in transcript
        if isinstance(turn, dict)
    ]


def identical_prefix_turns(control_data: dict[str, Any], comparator_data: dict[str, Any]) -> int:
    total = 0
    for left, right in zip(transcript_signature(control_data), transcript_signature(comparator_data)):
        if left == right:
            total += 1
            continue
        break
    return total


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
    shifts = private_shift_summary(data)
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
        "private_shift_summary": shifts,
        "private_agent_distances": private_agent_distances(shifts),
        "final_observer_summary": final_observer_summary(data),
        "transcript_snippets": snippets,
    }


def is_complete_readout(row: dict[str, Any]) -> bool:
    counts = row["readout_completeness"]
    return counts["private_complete_flags"].startswith("4/") and counts["observer_complete_flags"].startswith("2/")


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
    if report["historical_exclusions"]:
        lines.append("## Historical Exclusions")
        lines.append("")
        for exclusion in report["historical_exclusions"]:
            lines.append(f"- `{exclusion['run_id']}`: {exclusion['reason']}")
        lines.append("")
    if report["findings"]:
        lines.append("## Findings")
        lines.append("")
        for finding in report["findings"]:
            lines.append(f"- {finding}")
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
                f"- Identical transcript prefix turns: `{pair['identical_prefix_turns']}`",
                "",
                "### Private Probe Shifts",
                "",
                f"- Control A/B private distances: `{json.dumps(control['private_agent_distances'], sort_keys=True)}`",
                f"- Comparator A/B private distances: `{json.dumps(comparator['private_agent_distances'], sort_keys=True)}`",
                f"- Control: `{json.dumps(control['private_shift_summary'], sort_keys=True)}`",
                f"- Comparator: `{json.dumps(comparator['private_shift_summary'], sort_keys=True)}`",
                "",
                "### Final Observer Readouts",
                "",
                f"- Control: `{json.dumps(control['final_observer_summary'], sort_keys=True)}`",
                f"- Comparator: `{json.dumps(comparator['final_observer_summary'], sort_keys=True)}`",
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
    historical_exclusions = []
    for control in rejected_controls:
        if not is_complete_readout(control):
            historical_exclusions.append(
                {
                    "run_id": control["run_id"],
                    "path": control["path"],
                    "reason": f"incomplete readouts {control['readout_completeness']}",
                }
            )
            continue
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
        comparator_path = Path(comparator["path"])
        control_data = load_json(Path(control["path"])) or {}
        comparator_data = load_json(comparator_path) or {}
        comparisons.append(
            {
                "control": control,
                "retained_comparator": comparator,
                "match_score": score,
                "match_basis": basis,
                "identical_prefix_turns": identical_prefix_turns(control_data, comparator_data),
            }
        )

    blockers = []
    if not rejected_controls:
        blockers.append("no rejected low-disagreement-control artifact found")
    if not retained:
        blockers.append("no retained real comparator artifact found")
    if rejected_controls and retained and not comparisons:
        blockers.append("could not pair rejected controls with retained comparators")
    complete_comparisons = [
        pair for pair in comparisons
        if is_complete_readout(pair["control"]) and is_complete_readout(pair["retained_comparator"])
    ]
    if rejected_controls and not complete_comparisons:
        blockers.append("no low-disagreement control with complete private and observer readouts could be paired")
    if comparisons:
        if any(
            pair["control"]["semantic_debate_depth"].get("semantic_depth_rate") is None
            for pair in comparisons
        ):
            blockers.append("low-disagreement control has too few response turns for semantic depth scoring")

    findings = []
    for pair in complete_comparisons:
        control = pair["control"]
        comparator = pair["retained_comparator"]
        control_shifts = {
            agent: item.get("shift")
            for agent, item in control["private_shift_summary"].items()
        }
        comparator_shifts = {
            agent: item.get("shift")
            for agent, item in comparator["private_shift_summary"].items()
        }
        findings.append(
            "Complete low-disagreement control is now available: "
            f"`{control['run_id']}` vs retained `{comparator['run_id']}`. "
            f"Private shifts are control {control_shifts} vs retained {comparator_shifts}; "
            f"A/B initial private L1 distances are control={control['private_agent_distances'].get('initial_l1')} "
            f"vs retained={comparator['private_agent_distances'].get('initial_l1')}; "
            f"identical transcript prefix turns={pair['identical_prefix_turns']}."
        )
        if control["final_observer_summary"] == comparator["final_observer_summary"]:
            findings.append(
                "Final observer readouts are identical for the complete control pair, "
                "so the observer readout still appears dominated by topic semantics rather than initial disagreement."
            )

    report = {
        "rejected_control_count": len(rejected_controls),
        "retained_comparator_count": len(retained),
        "rejected_controls": rejected_controls,
        "comparisons": comparisons,
        "blockers": blockers,
        "historical_exclusions": historical_exclusions,
        "findings": findings,
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
