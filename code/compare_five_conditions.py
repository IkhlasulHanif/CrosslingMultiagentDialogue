#!/usr/bin/env python3
"""Build a five-condition cross-lingual outcome comparison table.

Reads citable BiVaD run artifacts, extracts initial and final private probe
values for each agent, computes Euclidean shift distances in 8-dimensional
Schwartz value space, and writes a comparison table. By default, the newest
citable artifact per condition is retained so the table is a five-condition
comparison rather than a full validation dump.

Usage:
    python3 code/compare_five_conditions.py
    python3 code/compare_five_conditions.py --out-dir code/bivad-evidence-audit
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs" / "bivad-local-lm"
DEFAULT_OUT_DIR = REPO_ROOT / "code" / "bivad-evidence-audit"

VALUE_KEYS = [
    "achievement", "benevolence", "conformity", "power",
    "security", "self_direction", "tradition", "universalism",
]

CONDITION_ORDER = [
    "same-English",
    "mixed-language",
    "swapped-language",
    "same-target-language",
    "translated-relay",
]


def euclidean(v1: dict[str, float], v2: dict[str, float]) -> float:
    return math.sqrt(sum((v1.get(k, 0.0) - v2.get(k, 0.0)) ** 2 for k in VALUE_KEYS))


def short_model(model_str: str) -> str:
    if "/" in model_str:
        return model_str.rsplit("/", 1)[-1]
    if len(model_str) > 40:
        return "..." + model_str[-37:]
    return model_str


def truncate(text: str, limit: int = 260) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def transcript_examples(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    """Return compact first/final transcript examples for human inspection."""
    turns = artifact.get("transcript") or []
    examples: list[dict[str, Any]] = []
    for turn in turns[:1] + turns[-1:]:
        text = turn.get("text") or turn.get("content") or ""
        examples.append({
            "turn": turn.get("turn"),
            "agent_id": turn.get("agent_id"),
            "language": turn.get("language"),
            "text_excerpt": truncate(text),
        })
    return examples


def extract_shifts(artifact: dict[str, Any]) -> dict[str, dict[str, Any]] | None:
    """Return per-agent shift info from private probes, or None if insufficient data."""
    probes = artifact.get("private_probes") or []
    by_agent: dict[str, list[dict]] = {}
    for p in probes:
        agent = p.get("agent_id")
        vals = p.get("values")
        if agent and isinstance(vals, dict) and len(vals) >= len(VALUE_KEYS) - 1:
            by_agent.setdefault(agent, []).append(p)

    result: dict[str, dict[str, Any]] = {}
    for agent_id, agent_probes in by_agent.items():
        sorted_probes = sorted(agent_probes, key=lambda x: x.get("turn", 0))
        if len(sorted_probes) < 2:
            continue
        initial = sorted_probes[0]["values"]
        final = sorted_probes[-1]["values"]
        shift = euclidean(initial, final)
        result[agent_id] = {
            "initial_values": initial,
            "initial_turn": sorted_probes[0].get("turn", 0),
            "final_values": final,
            "final_turn": sorted_probes[-1].get("turn"),
            "shift": round(shift, 6),
        }
    return result or None


def extract_private_public_gap(artifact: dict[str, Any]) -> dict[str, float]:
    """Return final private-public Euclidean distance per agent."""
    probes = artifact.get("private_probes") or []
    readouts = artifact.get("observer_readouts") or []

    final_private: dict[str, dict[str, float]] = {}
    for p in probes:
        agent = p.get("agent_id")
        if agent:
            final_private[agent] = p["values"]

    final_public: dict[str, dict[str, float]] = {}
    for ob in readouts:
        agent = ob.get("agent_id")
        if agent:
            final_public[agent] = ob.get("values") or {}

    gaps: dict[str, float] = {}
    for agent in set(final_private) & set(final_public):
        gaps[agent] = round(euclidean(final_private[agent], final_public[agent]), 6)
    return gaps


def load_citable_run_ids(validation_path: Path) -> set[str]:
    """Return the run_ids of citable candidates from validation.json."""
    if not validation_path.exists():
        return set()
    v = json.loads(validation_path.read_text())
    return {
        a["run_id"]
        for a in v.get("artifacts", [])
        if a.get("citable_candidate") and a.get("run_id")
    }


def load_evidence_package(out_dir: Path) -> dict[str, dict]:
    """Load shift_summary and observer readout values from evidence_package.json keyed by run_id."""
    ep_path = out_dir / "evidence_package.json"
    if not ep_path.exists():
        return {}
    ep = json.loads(ep_path.read_text())
    index: dict[str, dict] = {}
    for item in ep.get("artifacts", []):
        run_id = item.get("run_id")
        if run_id:
            index[run_id] = item
    return index


def evidence_transcript_examples(ep_entry: dict[str, Any]) -> list[dict[str, Any]]:
    snippets = ep_entry.get("transcript_snippets") or []
    examples: list[dict[str, Any]] = []
    for item in snippets[:1] + snippets[-1:]:
        text = item.get("text") or item.get("text_excerpt") or item.get("excerpt") or ""
        examples.append({
            "turn": item.get("turn"),
            "agent_id": item.get("agent_id"),
            "language": item.get("language"),
            "text_excerpt": truncate(text),
        })
    return examples


def discover_artifacts(runs_dir: Path, citable_ids: set[str]) -> list[Path]:
    """Yield artifact paths for citable run IDs only."""
    paths = []
    for p in sorted(runs_dir.glob("*.json")):
        stem = p.stem
        if stem in citable_ids:
            paths.append(p)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default=str(RUNS_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument(
        "--include-all-citable",
        action="store_true",
        help="Include every citable artifact instead of keeping the newest row per condition.",
    )
    return parser.parse_args()


def newest_per_condition(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        cond = row["condition"]
        previous = selected.get(cond)
        if previous is None or str(row["run_id"]) > str(previous["run_id"]):
            selected[cond] = row
    return list(selected.values())


def strict_same_model_sets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, str, str], set[str]] = {}
    for row in rows:
        key = (row.get("seed"), row.get("topic", "unknown"), row.get("model", "unknown"))
        by_key.setdefault(key, set()).add(row["condition"])
    full = set(CONDITION_ORDER)
    return [
        {"seed": key[0], "topic": key[1], "model": key[2], "conditions": sorted(conds)}
        for key, conds in by_key.items()
        if full.issubset(conds)
    ]


def build_outcome_comparisons(rows: list[dict[str, Any]]) -> list[str]:
    by_cond = {row["condition"]: row for row in rows}
    notes: list[str] = []

    same_en = by_cond.get("same-English")
    mixed = by_cond.get("mixed-language")
    if same_en and mixed:
        a_same = same_en["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_same = same_en["agent_shifts"].get("B", {}).get("shift", 0.0)
        a_mixed = mixed["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_mixed = mixed["agent_shifts"].get("B", {}).get("shift", 0.0)
        b_direction = "more" if b_same > b_mixed else "less" if b_same < b_mixed else "the same amount"
        notes.append(
            "same-English vs mixed-language: A shift is unchanged "
            f"({a_same} vs {a_mixed}), while B shifts {b_direction} in same-English "
            f"than in mixed-language ({b_same} vs {b_mixed})."
        )

    same_target = by_cond.get("same-target-language")
    relay = by_cond.get("translated-relay")
    if same_target and relay:
        a_target = same_target["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_target = same_target["agent_shifts"].get("B", {}).get("shift", 0.0)
        a_relay = relay["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_relay = relay["agent_shifts"].get("B", {}).get("shift", 0.0)
        notes.append(
            "same-target-language vs translated-relay on the Modal Qwen2.5 pair: "
            f"A shifts less under relay ({a_target} vs {a_relay}), while B shifts more "
            f"({b_target} vs {b_relay})."
        )

    swapped = by_cond.get("swapped-language")
    if mixed and swapped:
        a_mixed = mixed["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_mixed = mixed["agent_shifts"].get("B", {}).get("shift", 0.0)
        a_swapped = swapped["agent_shifts"].get("A", {}).get("shift", 0.0)
        b_swapped = swapped["agent_shifts"].get("B", {}).get("shift", 0.0)
        notes.append(
            "mixed-language vs swapped-language: private shifts are similar under the two "
            f"production-language assignments (mixed A={a_mixed}, B={b_mixed}; "
            f"swapped A={a_swapped}, B={b_swapped})."
        )
    return notes


def main() -> None:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    validation_path = out_dir / "validation.json"
    citable_ids = load_citable_run_ids(validation_path)
    ep_index = load_evidence_package(out_dir)

    artifact_paths = discover_artifacts(runs_dir, citable_ids)
    # Also include run_ids from evidence_package that may not exist as raw files
    ep_only_ids = set(ep_index) - {p.stem for p in artifact_paths}
    if not artifact_paths and not ep_only_ids:
        print("No citable artifacts found — run validate_bivad_artifacts.py first.")
        return

    rows: list[dict[str, Any]] = []

    def process_ep_entry(run_id: str, ep_entry: dict) -> dict | None:
        """Build a row from an evidence_package entry using shift_summary."""
        shift_summary = ep_entry.get("shift_summary") or []
        if not shift_summary:
            return None
        shifts: dict[str, dict[str, Any]] = {}
        gaps: dict[str, float] = {}
        for s in shift_summary:
            agent_id = s.get("agent_id")
            if not agent_id:
                continue
            # Recover initial/final values from private_probe_outputs
            pp_outputs = ep_entry.get("private_probe_outputs") or []
            initial_vals = next(
                (p["values"] for p in pp_outputs
                 if p.get("agent_id") == agent_id and p.get("turn") == s.get("private_start_turn", 0)),
                None,
            )
            final_vals = next(
                (p["values"] for p in pp_outputs
                 if p.get("agent_id") == agent_id and p.get("turn") == s.get("private_end_turn")),
                None,
            )
            shifts[agent_id] = {
                "initial_values": initial_vals,
                "initial_turn": s.get("private_start_turn", 0),
                "final_values": final_vals,
                "final_turn": s.get("private_end_turn"),
                "shift": s.get("private_shift_distance", 0.0),
            }
            gap = s.get("final_private_public_distance")
            if gap is not None:
                gaps[agent_id] = gap
        if not shifts:
            return None
        combined_shift = round(sum(v["shift"] for v in shifts.values()), 6)
        model_str = ep_entry.get("model", "unknown")
        return {
            "run_id": run_id,
            "condition": ep_entry.get("condition", "unknown"),
            "seed": ep_entry.get("seed"),
            "model": short_model(str(model_str)),
            "backend": "local (text-recovered)",
            "topic": ep_entry.get("topic", "unknown"),
            "agent_shifts": shifts,
            "private_public_gaps": gaps,
            "combined_shift": combined_shift,
            "transcript_examples": evidence_transcript_examples(ep_entry),
        }

    for path in artifact_paths:
        run_id = path.stem
        try:
            artifact = json.loads(path.read_text())
        except Exception as e:
            print(f"  skip {path.name}: {e}")
            continue

        condition = artifact.get("condition", "unknown")
        seed = artifact.get("seed")
        run_id_from_artifact = artifact.get("run_id", run_id)
        model = short_model(str(artifact.get("model", "unknown")))
        backend = artifact.get("backend", "local")
        topic = artifact.get("topic", "unknown")

        shifts = extract_shifts(artifact)
        if not shifts:
            # Fall back to evidence_package recovered values
            ep_entry = ep_index.get(run_id)
            if ep_entry:
                row = process_ep_entry(run_id, ep_entry)
                if row:
                    rows.append(row)
                    continue
            print(f"  skip {path.name}: insufficient probe data (no ep fallback)")
            continue

        gaps = extract_private_public_gap(artifact)
        combined_shift = round(sum(v["shift"] for v in shifts.values()), 6)

        rows.append({
            "run_id": run_id_from_artifact,
            "condition": condition,
            "seed": seed,
            "model": model,
            "backend": backend,
            "topic": topic,
            "agent_shifts": shifts,
            "private_public_gaps": gaps,
            "combined_shift": combined_shift,
            "transcript_examples": transcript_examples(artifact),
        })

    if not args.include_all_citable:
        rows = newest_per_condition(rows)

    def sort_key(row: dict) -> tuple:
        try:
            order = CONDITION_ORDER.index(row["condition"])
        except ValueError:
            order = len(CONDITION_ORDER)
        return (order, row["run_id"])

    rows.sort(key=sort_key)

    # Build pattern notes
    pattern_notes: list[str] = []
    by_cond: dict[str, list[dict]] = {}
    for row in rows:
        by_cond.setdefault(row["condition"], []).append(row)

    # Observation: which agent shifts more per condition
    for cond in CONDITION_ORDER:
        for row in by_cond.get(cond, []):
            shifts = row["agent_shifts"]
            a_shift = shifts.get("A", {}).get("shift", 0.0)
            b_shift = shifts.get("B", {}).get("shift", 0.0)
            model = row["model"]
            if abs(a_shift - b_shift) > 1.0:
                dominant = "A" if a_shift > b_shift else "B"
                pattern_notes.append(
                    f"{cond} ({model}): agent {dominant} shifts more "
                    f"(A={a_shift}, B={b_shift})"
                )

    same_model_sets = strict_same_model_sets(rows)
    outcome_comparisons = build_outcome_comparisons(rows)
    limitation_notes = []
    if not same_model_sets:
        limitation_notes.append(
            "No strict five-condition set has the same model, topic, and seed. "
            "The first three rows are Qwen3-1.7B recovered artifacts; same-target-language "
            "and translated-relay are Modal Qwen2.5-7B-Instruct artifacts. Treat the table "
            "as a cross-condition audit, not a publication-grade same-model causal comparison."
        )

    result = {
        "generated_by": "compare_five_conditions.py",
        "conditions_represented": sorted({r["condition"] for r in rows}),
        "artifact_count": len(rows),
        "selection": "newest citable artifact per condition" if not args.include_all_citable else "all citable artifacts",
        "note": (
            "Euclidean shift = L2 distance in 8-dimensional Schwartz value space "
            "between initial (turn 0) and final private probes. "
            "private_public_gaps are L2 distances between final private probe and "
            "final observer readout for each agent."
        ),
        "strict_same_model_five_condition_sets": same_model_sets,
        "limitations": limitation_notes,
        "pattern_observations": pattern_notes,
        "outcome_comparisons": outcome_comparisons,
        "rows": rows,
    }

    out_json = out_dir / "five_condition_comparison.json"
    out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {out_json}")

    # Markdown table
    lines = ["# Five-Condition Cross-Lingual Outcome Comparison", ""]
    lines.append(result["note"])
    lines.append("")
    lines.append(f"Selection: {result['selection']}.")
    if limitation_notes:
        lines.append("")
        lines.append("## Limitations")
        lines.append("")
        for note in limitation_notes:
            lines.append(f"- {note}")
    lines.append("")
    lines.append(
        "| run_id | condition | seed | model | A shift | B shift | combined | "
        "A priv-pub gap | B priv-pub gap |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        a_shift = row["agent_shifts"].get("A", {}).get("shift", "—")
        b_shift = row["agent_shifts"].get("B", {}).get("shift", "—")
        a_gap = row["private_public_gaps"].get("A", "—")
        b_gap = row["private_public_gaps"].get("B", "—")
        lines.append(
            f"| {row['run_id']} | {row['condition']} | {row['seed']} "
            f"| {row['model']} | {a_shift} | {b_shift} | {row['combined_shift']} "
            f"| {a_gap} | {b_gap} |"
        )
    lines.append("")

    if pattern_notes:
        lines.append("## Pattern Observations")
        lines.append("")
        for note in pattern_notes:
            lines.append(f"- {note}")
        lines.append("")

    if outcome_comparisons:
        lines.append("## Outcome Comparisons")
        lines.append("")
        for note in outcome_comparisons:
            lines.append(f"- {note}")
        lines.append("")

    lines.append("## Per-Condition Detail")
    lines.append("")
    for cond in CONDITION_ORDER:
        cond_rows = by_cond.get(cond, [])
        if not cond_rows:
            continue
        lines.append(f"### {cond}")
        for row in cond_rows:
            lines.append(f"- `{row['run_id']}` ({row['model']}, {row['backend']})")
            lines.append(f"  - Topic: {row['topic']}")
            for agent_id in sorted(row["agent_shifts"]):
                s = row["agent_shifts"][agent_id]
                gap = row["private_public_gaps"].get(agent_id, "—")
                lines.append(
                    f"  - Agent {agent_id}: initial {s['initial_values']} "
                    f"→ final {s['final_values']} | shift={s['shift']} | priv-pub gap={gap}"
                )
            examples = row.get("transcript_examples") or []
            if examples:
                lines.append("  - Transcript spans:")
                for ex in examples:
                    lines.append(
                        f"    - turn {ex.get('turn')} {ex.get('language')}: "
                        f"{ex.get('text_excerpt')}"
                    )
        lines.append("")

    out_md = out_dir / "five_condition_comparison.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")

    print(f"\nConditions represented: {result['conditions_represented']}")
    print(f"Artifacts: {len(rows)}")
    if pattern_notes:
        print("Key observations:")
        for note in pattern_notes:
            print(f"  {note}")


if __name__ == "__main__":
    main()
