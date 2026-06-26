#!/usr/bin/env python3
"""Rank topics by cross-lingual value-shift divergence.

For each topic that has both mixed-language and same-English condition runs,
computes the difference in Agent B's private probe shift.  A large difference
means language condition (mixed vs same-English) changes how much B's values
shift — i.e., the topic is sensitive to cross-lingual dialogue framing.

Usage:
    python3 code/analyze_topic_divergence.py
    python3 code/analyze_topic_divergence.py --runs-dir runs/bivad-local-lm
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs" / "bivad-local-lm"
DEFAULT_OUT_DIR = REPO_ROOT / "code" / "bivad-evidence-audit"

VALUE_KEYS = [
    "achievement", "benevolence", "conformity", "power",
    "security", "self_direction", "tradition", "universalism",
]

# Conditions needed for cross-lingual comparison
SCAN_CONDITIONS = {"mixed-language", "same-English"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs-dir", default=str(RUNS_DIR))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def euclidean(v1: dict[str, float], v2: dict[str, float]) -> float:
    return math.sqrt(sum((v1.get(k, 0.0) - v2.get(k, 0.0)) ** 2 for k in VALUE_KEYS))


def get_agent_shift(probes: list[dict], agent_id: str) -> float | None:
    agent_probes = [p for p in probes if p.get("agent_id") == agent_id]
    if len(agent_probes) < 2:
        return None
    agent_probes.sort(key=lambda x: x.get("turn", 0))
    initial = agent_probes[0].get("values") or {}
    final = agent_probes[-1].get("values") or {}
    if not initial or not final:
        return None
    return euclidean(initial, final)


def get_private_public_gap(probes: list[dict], readouts: list[dict], agent_id: str) -> float | None:
    agent_probes = [p for p in probes if p.get("agent_id") == agent_id]
    if not agent_probes:
        return None
    agent_probes.sort(key=lambda x: x.get("turn", 0))
    final_private = agent_probes[-1].get("values") or {}

    agent_readouts = [r for r in readouts if r.get("agent_id") == agent_id]
    if not agent_readouts:
        return None
    agent_readouts.sort(key=lambda x: x.get("turn", 0))
    final_public = agent_readouts[-1].get("values") or {}

    if not final_private or not final_public:
        return None
    return euclidean(final_private, final_public)


def is_synthetic(artifact: dict) -> bool:
    if artifact.get("synthetic"):
        return True
    run_id = str(artifact.get("run_id", ""))
    return any(k in run_id for k in ("dry-run", "preflight", "synthetic", "fixture"))


def load_artifacts(runs_dir: Path) -> list[dict]:
    artifacts = []
    for path in sorted(runs_dir.glob("*.json")):
        if "manifest" in path.stem:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if is_synthetic(data):
            continue
        if data.get("artifact_type") != "local_lm_bivad_pilot":
            continue
        data["_path"] = str(path)
        artifacts.append(data)
    return artifacts


def get_target_language(artifact: dict) -> str:
    """Extract B's language (the non-English target) from the agents list."""
    agents = artifact.get("agents") or []
    for agent in agents:
        lang = agent.get("language", "")
        if lang and lang != "English":
            return lang
    return "unknown"


def run_time(artifact: dict) -> datetime | None:
    """Parse the timestamp prefix from run_id, e.g. 20260626T210916Z-..."""
    run_id = str(artifact.get("run_id") or "")
    if len(run_id) < 16:
        return None
    try:
        return datetime.strptime(run_id[:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def run_time_distance(a: dict, b: dict) -> float:
    a_time = run_time(a)
    b_time = run_time(b)
    if a_time is None or b_time is None:
        return float("inf")
    return abs((a_time - b_time).total_seconds())


def main() -> None:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    artifacts = load_artifacts(runs_dir)
    print(f"Loaded {len(artifacts)} non-synthetic BiVaD artifacts from {runs_dir}")

    # Strategy:
    # - For mixed-language runs: group by (topic, seed, target_language), where
    #   target_language is B's non-English production language.
    # - For same-English runs: there is no target language in the artifact. When
    #   multiple language-pair replications share a topic/seed, pair each mixed
    #   run with the closest same-English control by run timestamp.
    mixed_by_lang: dict[tuple[str, Any, str], dict] = {}  # (topic, seed, lang) → artifact
    same_en_by_ts: dict[tuple[str, Any], list[dict]] = {}  # (topic, seed) → artifacts

    for artifact in artifacts:
        topic = artifact.get("topic", "unknown")
        seed = artifact.get("seed")
        condition = artifact.get("condition", "unknown")
        ts_key = (topic, seed)
        run_id = artifact.get("run_id", "")

        if condition == "mixed-language":
            target_lang = get_target_language(artifact)
            if target_lang == "unknown":
                continue
            key = (topic, seed, target_lang)
            existing = mixed_by_lang.get(key)
            if existing is None or run_id > existing.get("run_id", ""):
                mixed_by_lang[key] = artifact

        elif condition == "same-English":
            same_en_by_ts.setdefault(ts_key, []).append(artifact)

    # Build groups: for each mixed-language run, pair with the nearest same-English
    # baseline for the same topic/seed. This preserves separate Indonesian and
    # Spanish replications of the same topic/seed.
    by_group: dict[tuple[str, Any, str], dict[str, dict]] = {}
    for (topic, seed, target_lang), mixed_art in mixed_by_lang.items():
        ts_key = (topic, seed)
        key = (topic, seed, target_lang)
        if key not in by_group:
            by_group[key] = {}
        by_group[key]["mixed-language"] = mixed_art
        same_en_candidates = same_en_by_ts.get(ts_key) or []
        if same_en_candidates:
            same_en = min(
                same_en_candidates,
                key=lambda candidate: (
                    run_time_distance(mixed_art, candidate),
                    str(candidate.get("run_id") or ""),
                ),
            )
            by_group[key]["same-English"] = same_en

    # For each group that has both mixed-language and same-English, compute divergence
    topic_results: list[dict[str, Any]] = []
    for (topic, seed, target_language), conditions_map in sorted(by_group.items()):
        if not SCAN_CONDITIONS.issubset(conditions_map.keys()):
            available = sorted(conditions_map.keys())
            print(f"  skip ({topic!r}, seed={seed}, lang={target_language!r}): missing conditions (have {available})")
            continue

        mixed = conditions_map["mixed-language"]
        same_en = conditions_map["same-English"]

        mixed_probes = mixed.get("private_probes") or []
        same_probes = same_en.get("private_probes") or []
        mixed_readouts = mixed.get("observer_readouts") or []
        same_readouts = same_en.get("observer_readouts") or []

        mixed_b_shift = get_agent_shift(mixed_probes, "B")
        same_b_shift = get_agent_shift(same_probes, "B")
        mixed_a_shift = get_agent_shift(mixed_probes, "A")
        same_a_shift = get_agent_shift(same_probes, "A")

        if mixed_b_shift is None or same_b_shift is None:
            print(f"  skip ({topic!r}, seed={seed}, lang={target_language!r}): missing B probe data")
            continue

        b_divergence = abs(mixed_b_shift - same_b_shift)
        a_divergence = abs((mixed_a_shift or 0.0) - (same_a_shift or 0.0))

        mixed_b_gap = get_private_public_gap(mixed_probes, mixed_readouts, "B")
        same_b_gap = get_private_public_gap(same_probes, same_readouts, "B")
        mixed_a_gap = get_private_public_gap(mixed_probes, mixed_readouts, "A")
        same_a_gap = get_private_public_gap(same_probes, same_readouts, "A")

        topic_results.append({
            "topic": topic,
            "seed": seed,
            "target_language": target_language,
            "model": mixed.get("model", "unknown"),
            "b_shift_mixed": round(mixed_b_shift, 4),
            "b_shift_same_en": round(same_b_shift, 4),
            "b_divergence": round(b_divergence, 4),
            "a_shift_mixed": round(mixed_a_shift or 0.0, 4),
            "a_shift_same_en": round(same_a_shift or 0.0, 4),
            "a_divergence": round(a_divergence, 4),
            "b_gap_mixed": round(mixed_b_gap, 4) if mixed_b_gap is not None else None,
            "b_gap_same_en": round(same_b_gap, 4) if same_b_gap is not None else None,
            "a_gap_mixed": round(mixed_a_gap, 4) if mixed_a_gap is not None else None,
            "a_gap_same_en": round(same_a_gap, 4) if same_a_gap is not None else None,
            "mixed_run_id": mixed.get("run_id"),
            "same_en_run_id": same_en.get("run_id"),
        })

    # Rank by B divergence descending
    topic_results.sort(key=lambda r: -r["b_divergence"])

    report = {
        "artifact_type": "topic_divergence_scan",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metric": (
            "b_divergence = |B_private_shift(mixed-language) - B_private_shift(same-English)|. "
            "High divergence: language condition changes how much B's private values shift. "
            "Shift = L2 distance in 8D Schwartz space between initial and final private probe."
        ),
        "note": (
            "Topics are ranked by B divergence. A divergence ranks the same way but is "
            "expected to be small since A is always English-speaking across both conditions."
        ),
        "total_topic_seed_pairs": len(topic_results),
        "topics": topic_results,
    }

    out_json = out_dir / "topic_divergence_scan.json"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_json}")

    # Markdown report
    lines = [
        "# Topic Divergence Scan: Cross-Lingual Value-Shift Ranking",
        "",
        f"Created: `{report['created_at']}`",
        "",
        f"**Metric**: `b_divergence` = |B shift(mixed-language) − B shift(same-English)|",
        "",
        "High divergence: the topic is sensitive to whether B operates in its non-English language vs English.",
        "",
        "| rank | topic | seed | lang | B shift(mixed) | B shift(same-EN) | B divergence | A divergence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rank, r in enumerate(topic_results, 1):
        short_topic = r["topic"][:44] + "…" if len(r["topic"]) > 45 else r["topic"]
        lines.append(
            f"| {rank} | {short_topic} | {r['seed']} | {r.get('target_language', '?')} | "
            f"{r['b_shift_mixed']} | {r['b_shift_same_en']} | "
            f"**{r['b_divergence']}** | {r['a_divergence']} |"
        )

    lines.extend(["", "## Detail per Topic", ""])
    for r in topic_results:
        lines.append(f"### {r['topic']} (seed={r['seed']}, lang={r.get('target_language', '?')})")
        lines.append(f"- Model: `{r['model']}`  Seed: {r['seed']}  Target language: {r.get('target_language', '?')}")
        lines.append(f"- B shift mixed-language: {r['b_shift_mixed']}")
        lines.append(f"- B shift same-English: {r['b_shift_same_en']}")
        lines.append(f"- **B divergence**: {r['b_divergence']}")
        lines.append(f"- A shift mixed-language: {r['a_shift_mixed']} | same-English: {r['a_shift_same_en']}")
        if r.get("b_gap_mixed") is not None:
            lines.append(f"- B priv-pub gap mixed: {r['b_gap_mixed']} | same-EN: {r['b_gap_same_en']}")
        if r.get("a_gap_mixed") is not None:
            lines.append(f"- A priv-pub gap mixed: {r['a_gap_mixed']} | same-EN: {r['a_gap_same_en']}")
        lines.append(f"- mixed run_id: `{r['mixed_run_id']}`")
        lines.append(f"- same-EN run_id: `{r['same_en_run_id']}`")
        lines.append("")

    out_md = out_dir / "topic_divergence_scan.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")

    print(f"\nTopics ranked by B cross-lingual divergence:")
    for rank, r in enumerate(topic_results, 1):
        print(f"  {rank}. [{r['b_divergence']:.3f}] {r['topic']} (seed={r['seed']}, lang={r.get('target_language', '?')})")


if __name__ == "__main__":
    main()
