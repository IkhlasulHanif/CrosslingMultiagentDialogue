#!/usr/bin/env python3
"""Run one pairwise buy/sell channel condition from pairwise_channel_plan.json."""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))

from run_c0_smoke import (  # noqa: E402
    OpenAIExternalRequestNeeded,
    append_event,
    benchmark_openai_allowed,
    load_benchmark_model_config,
    run_endpoint_probe,
    run_episode,
    upstream_commit,
    utc_now,
    write_json,
    write_metrics,
)


def load_pairwise_plan() -> dict[str, Any]:
    return json.loads((ROOT / "config" / "pairwise_channel_plan.json").read_text(encoding="utf-8"))


def slug(value: str) -> str:
    return value.lower().replace("-", "_").replace("/", "_")


def selected_provider(explicit: str | None) -> str:
    if explicit:
        return explicit
    override = os.environ.get("NEGOTIATION_BENCHMARK_PROVIDER")
    if override:
        return override
    if benchmark_openai_allowed(load_benchmark_model_config()):
        return "openai_benchmark"
    return "local_qwen"


def rows_for_pair(plan: dict[str, Any], pair: str) -> list[dict[str, Any]]:
    normalized = pair.upper()
    for entry in plan.get("active_pairs", []):
        if str(entry.get("pair", "")).upper() == normalized:
            rows = entry.get("conditions", [])
            if isinstance(rows, list):
                return rows
    raise ValueError(f"pair {pair!r} is not in config/pairwise_channel_plan.json")


def select_row(rows: list[dict[str, Any]], condition: str, counterbalance: str | None) -> dict[str, Any]:
    normalized_condition = condition.upper()
    matches = [row for row in rows if str(row.get("condition", "")).upper() == normalized_condition]
    if normalized_condition == "C2":
        if not counterbalance:
            raise ValueError("C2 requires --counterbalance buyer_lx_seller_ly or buyer_ly_seller_lx")
        matches = [row for row in matches if row.get("counterbalance_id") == counterbalance]
    elif counterbalance:
        raise ValueError("--counterbalance is only valid for C2")

    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one row for condition={condition!r} counterbalance={counterbalance!r}; "
            f"found {len(matches)}"
        )
    return matches[0]


def episode_id(pair: str, row: dict[str, Any], seed: int) -> str:
    condition = str(row["condition"]).lower()
    counterbalance = row.get("counterbalance_id")
    suffix = f"_{slug(str(counterbalance))}" if counterbalance else ""
    return f"pair_{slug(pair)}_{condition}{suffix}_buy_sell_seed{seed:03d}"


def build_plan(pair: str, row: dict[str, Any], seed: int, turn_limit: int, model: str) -> dict[str, Any]:
    eid = episode_id(pair, row, seed)
    episode = {
        "episode_id": eid,
        "condition": row["condition"],
        "game_id": "buy_sell",
        "language_pair": pair.upper(),
        "role_languages": row["role_languages"],
        "model": model,
        "turn_limit": turn_limit,
        "seed": seed,
    }
    return {
        "episode": episode,
        "expected_artifacts": {
            "transcript": f"artifacts/transcripts/{eid}.json",
            "metrics": f"artifacts/results/{eid}.metrics.json",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", required=True, choices=["EN-ID", "EN-ZH", "ZH-ID"])
    parser.add_argument("--condition", required=True, choices=["C0", "C1", "C2", "C3"])
    parser.add_argument("--counterbalance", choices=["buyer_lx_seller_ly", "buyer_ly_seller_lx"])
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--turn-limit", type=int, default=8)
    parser.add_argument("--provider", choices=["local_qwen", "openai_benchmark", "openai_benchmark_shell_bridge"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    benchmark_config = load_benchmark_model_config() or {}
    model = os.environ.get(
        str(benchmark_config.get("env_model", "OPENAI_BENCHMARK_MODEL")),
        str(benchmark_config.get("default_model", "gpt-5.4-mini-2026-03-17")),
    )
    plan_config = load_pairwise_plan()
    row = select_row(rows_for_pair(plan_config, args.pair), args.condition, args.counterbalance)
    plan = build_plan(args.pair, row, args.seed, args.turn_limit, model)

    if args.dry_run:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0

    provider = selected_provider(args.provider)
    failed_command = (
        "python3 scripts/run_pairwise_buy_sell.py "
        f"--pair {args.pair} --condition {args.condition}"
        + (f" --counterbalance {args.counterbalance}" if args.counterbalance else "")
    )

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=failed_command)
    except SystemExit as exc:
        artifact = write_json(
            f"artifacts/results/{plan['episode']['episode_id']}.blocked.json",
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "benchmark_provider_unavailable",
                "failed_command": failed_command,
                "active_benchmark_provider": provider,
                "active_benchmark_model": model,
                "episode": plan["episode"],
                "provider_probe_artifact": "artifacts/results/benchmark_model_probe.json",
                "message": "Pairwise buy/sell episode is ready but the selected provider failed.",
                "evidence_scope": "No empirical evidence produced by this attempt.",
            },
        )
        append_event(
            "pairwise_buy_sell",
            "BLOCKED",
            f"{plan['episode']['episode_id']} blocked on provider {provider}; artifact={artifact.relative_to(ROOT)}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(plan, provider, model_metadata)
    except OpenAIExternalRequestNeeded as exc:
        append_event(
            "pairwise_buy_sell",
            "RUNNING",
            f"{plan['episode']['episode_id']} shell bridge request ready; request={exc.request_path.relative_to(ROOT)}",
        )
        return 75
    except Exception as exc:
        artifact = write_json(
            f"artifacts/results/{plan['episode']['episode_id']}.error.json",
            {
                "checked_at": utc_now(),
                "status": "ERROR",
                "failed_command": failed_command,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
                "episode": plan["episode"],
            },
        )
        append_event(
            "pairwise_buy_sell",
            "ERROR",
            f"{plan['episode']['episode_id']} failed; artifact={artifact.relative_to(ROOT)}",
        )
        raise

    artifacts = plan["expected_artifacts"]
    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "pairwise_buy_sell",
        "OK",
        f"{plan['episode']['episode_id']} completed; transcript={transcript_path.relative_to(ROOT)}; "
        f"metrics={metrics_path.relative_to(ROOT)}; provider={provider}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
