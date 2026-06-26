#!/usr/bin/env python3
"""Summarize no-dialogue measurement-drift baselines from BiVaD artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs" / "bivad-local-lm"
OUT_DIR = REPO_ROOT / "code" / "bivad-evidence-audit"

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

TOPIC_ORDER = [
    "public release of dual-use policy datasets",
    "universal basic income as a social safety net",
    "religious exemptions from anti-discrimination law",
    "government surveillance for national security",
    "mandatory content moderation on social media platforms",
]


def euclidean(v1: dict[str, float], v2: dict[str, float]) -> float:
    return math.sqrt(sum((v1.get(k, 0.0) - v2.get(k, 0.0)) ** 2 for k in VALUE_KEYS))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def topic_sort_key(topic: str) -> tuple[int, str]:
    try:
        return (TOPIC_ORDER.index(topic), topic)
    except ValueError:
        return (len(TOPIC_ORDER), topic)


def private_shift_by_agent(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    probes = artifact.get("private_probes") or []
    by_agent: dict[str, list[dict[str, Any]]] = {}
    for probe in probes:
        agent = probe.get("agent_id")
        values = probe.get("values")
        if agent and isinstance(values, dict):
            by_agent.setdefault(agent, []).append(probe)

    shifts: dict[str, dict[str, Any]] = {}
    for agent, agent_probes in by_agent.items():
        if len(agent_probes) < 2:
            continue
        initial = agent_probes[0]["values"]
        final = agent_probes[-1]["values"]
        shifts[agent] = {
            "initial_values": initial,
            "final_values": final,
            "shift": round(euclidean(initial, final), 6),
        }
    return shifts


def final_private_public_gap(artifact: dict[str, Any]) -> dict[str, float]:
    probes = artifact.get("private_probes") or []
    readouts = artifact.get("observer_readouts") or []

    private: dict[str, dict[str, float]] = {}
    for probe in probes:
        agent = probe.get("agent_id")
        values = probe.get("values")
        if agent and isinstance(values, dict):
            private[agent] = values

    public: dict[str, dict[str, float]] = {}
    for readout in readouts:
        agent = readout.get("agent_id")
        values = readout.get("values")
        if agent and isinstance(values, dict):
            public[agent] = values

    return {
        agent: round(euclidean(private[agent], public[agent]), 6)
        for agent in sorted(set(private) & set(public))
    }


def load_debate_b_shift_ranges(comparison_dir: Path) -> dict[str, dict[str, float]]:
    ranges: dict[str, dict[str, float]] = {}
    for path in sorted(comparison_dir.glob("five_condition_comparison*.json")):
        data = load_json(path)
        rows = data.get("rows") or []
        if not rows:
            continue
        topics = {row.get("topic") for row in rows if row.get("condition") != "no-dialogue"}
        if len(topics) != 1:
            continue
        topic = next(iter(topics))
        b_shifts = [
            row.get("agent_shifts", {}).get("B", {}).get("shift")
            for row in rows
            if row.get("condition") != "no-dialogue"
        ]
        b_shifts = [float(x) for x in b_shifts if isinstance(x, (int, float))]
        if b_shifts and topic:
            ranges[topic] = {
                "debate_min_b_shift": round(min(b_shifts), 6),
                "debate_max_b_shift": round(max(b_shifts), 6),
            }
    return ranges


def discover_latest_no_dialogue(runs_dir: Path) -> dict[str, Path]:
    by_topic: dict[str, Path] = {}
    for path in sorted(runs_dir.glob("*.json")):
        if "no-dialogue" not in path.name or "manifest" in path.name:
            continue
        artifact = load_json(path)
        if artifact.get("condition") != "no-dialogue" or artifact.get("synthetic"):
            continue
        topic = artifact.get("topic")
        if not topic:
            continue
        previous = by_topic.get(topic)
        if previous is None or path.stem > previous.stem:
            by_topic[topic] = path
    return by_topic


def build_summary(runs_dir: Path, out_dir: Path) -> dict[str, Any]:
    debate_ranges = load_debate_b_shift_ranges(out_dir)
    latest = discover_latest_no_dialogue(runs_dir)
    rows: list[dict[str, Any]] = []

    for topic, path in sorted(latest.items(), key=lambda item: topic_sort_key(item[0])):
        artifact = load_json(path)
        shifts = private_shift_by_agent(artifact)
        gaps = final_private_public_gap(artifact)
        row = {
            "run_id": artifact.get("run_id", path.stem),
            "path": str(path),
            "topic": topic,
            "seed": artifact.get("seed"),
            "model": str(artifact.get("model", "unknown")).rsplit("/", 1)[-1],
            "a_no_dialogue_shift": shifts.get("A", {}).get("shift"),
            "b_no_dialogue_shift": shifts.get("B", {}).get("shift"),
            "a_private_public_gap": gaps.get("A"),
            "b_private_public_gap": gaps.get("B"),
            "debate_min_b_shift": debate_ranges.get(topic, {}).get("debate_min_b_shift"),
            "debate_max_b_shift": debate_ranges.get(topic, {}).get("debate_max_b_shift"),
        }
        b_shift = row["b_no_dialogue_shift"]
        debate_min = row["debate_min_b_shift"]
        row["debate_exceeds_no_dialogue_b"] = (
            bool(debate_min > b_shift) if isinstance(b_shift, (int, float)) and isinstance(debate_min, (int, float)) else None
        )
        rows.append(row)

    return {
        "generated_by": "summarize_no_dialogue.py",
        "note": (
            "No-dialogue artifacts skip debate turns and repeat the private probe after an elapsed-time framing. "
            "Debate ranges are B private-probe shift ranges from topic-specific five-condition comparison files."
        ),
        "topic_count": len(rows),
        "all_debate_min_exceeds_no_dialogue_b": all(
            row["debate_exceeds_no_dialogue_b"] for row in rows if row["debate_exceeds_no_dialogue_b"] is not None
        ),
        "rows": rows,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# No-Dialogue Baseline Summary",
        "",
        summary["note"],
        "",
        f"Topics: `{summary['topic_count']}`",
        "",
        "| topic | run_id | A no-dialogue | B no-dialogue | debate min B | debate max B | A gap | B gap |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {row['topic']} | {row['run_id']} | {row['a_no_dialogue_shift']} | "
            f"{row['b_no_dialogue_shift']} | {row['debate_min_b_shift']} | "
            f"{row['debate_max_b_shift']} | {row['a_private_public_gap']} | {row['b_private_public_gap']} |"
        )
    lines.append("")
    lines.append(
        f"All available debate minima exceed B no-dialogue drift: "
        f"`{summary['all_debate_min_exceeds_no_dialogue_b']}`."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default=str(RUNS_DIR))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(runs_dir, out_dir)
    out_json = out_dir / "no_dialogue_summary.json"
    out_md = out_dir / "no_dialogue_summary.md"
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    write_markdown(summary, out_md)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
