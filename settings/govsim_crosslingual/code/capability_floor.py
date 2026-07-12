#!/usr/bin/env python3
"""Capability-floor checks for GovSim baseline result artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


THRESHOLD = 0.90


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_result(root: Path, condition: str, language: str, pair: str) -> Path:
    candidates: list[tuple[str, Path]] = []
    for path in sorted((root / "artifacts" / "results").glob(f"govsim_{condition.lower()}_openai_baseline_*.json")):
        data = read_json(path)
        if not data.get("empirical_episode_ran"):
            continue
        if str(data.get("condition", "")).upper() != condition:
            continue
        if str(data.get("language", "")).upper() != language:
            continue
        artifact_pair = data.get("language_pair")
        if artifact_pair is not None and str(artifact_pair).upper() != pair:
            continue
        candidates.append((str(data.get("timestamp_utc") or path.name), path))
    if not candidates:
        raise RuntimeError(f"no empirical {condition}/{language} OpenAI baseline result found for {pair}")
    return sorted(candidates)[-1][1]


def condition_row(root: Path, result_path: Path, condition: str, language: str, pair: str) -> dict[str, Any]:
    result = read_json(result_path)
    process_path = root / str(result["process_metrics_path"])
    process = read_json(process_path)
    parseable_rate = float(result.get("parseable_harvest_rate") or 0.0)
    compliance_rate = process.get("channel_compliant_message_rate")
    compliance_ok = compliance_rate is not None and float(compliance_rate) >= THRESHOLD
    parseable_ok = parseable_rate >= THRESHOLD
    return {
        "condition": condition,
        "language": language,
        "language_pair": result.get("language_pair") or pair,
        "result_path": str(result_path.relative_to(root)),
        "transcript_path": result.get("transcript_path"),
        "process_metrics_path": str(process_path.relative_to(root)),
        "empirical_episode_ran": bool(result.get("empirical_episode_ran")),
        "parseable_harvest_rate": parseable_rate,
        "parseable_harvest_count": result.get("parseable_harvest_count"),
        "harvest_prompt_count": result.get("harvest_prompt_count"),
        "channel_compliant_message_rate": compliance_rate,
        "off_pair_token_count": process.get("off_pair_token_count"),
        "off_pair_scripts": process.get("off_pair_scripts", {}),
        "survival_time": result.get("survival_time"),
        "total_welfare": result.get("total_welfare"),
        "gini": result.get("gini"),
        "passed": bool(result.get("empirical_episode_ran")) and parseable_ok and compliance_ok,
    }


def build_report(
    root: Path,
    *,
    pair: str,
    c0_result: Path | None,
    c1_result: Path | None,
) -> dict[str, Any]:
    pair = pair.upper()
    left, right = pair.split("-")
    c0_path = c0_result or latest_result(root, "C0", left, pair)
    c1_path = c1_result or latest_result(root, "C1", right, pair)
    rows = [
        condition_row(root, c0_path, "C0", left, pair),
        condition_row(root, c1_path, "C1", right, pair),
    ]
    passed = all(row["passed"] for row in rows)
    return {
        "schema_version": "govsim-g2-capability-floor-v1",
        "timestamp_utc": utc_now(),
        "benchmark": "GovSim",
        "substrate": "fishery",
        "model_provider": "openai",
        "evidence_scope": "OpenAI benchmark capability-floor evidence, not Qwen3 evidence",
        "language_pair": pair,
        "thresholds": {
            "parseable_harvest_rate": THRESHOLD,
            "channel_compliant_message_rate": THRESHOLD,
        },
        "conditions": rows,
        "passed": passed,
        "next_command_if_passed": "./scripts/run_openai_en_id_c2_counterbalance_a.sh",
        "notes": [
            "Rules/private state stayed in English; language is the visible output channel.",
            "A nonzero off_pair_token_count is reported as process evidence even if the compliance threshold passes.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check GovSim C0/C1 capability floor.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--pair", default="EN-ID")
    parser.add_argument("--c0-result", type=Path)
    parser.add_argument("--c1-result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(
        root,
        pair=args.pair,
        c0_result=(root / args.c0_result if args.c0_result else None),
        c1_result=(root / args.c1_result if args.c1_result else None),
    )
    out = args.out or root / "artifacts" / "logs" / f"g2_{args.pair.lower().replace('-', '_')}_capability_floor.json"
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out.relative_to(root))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
