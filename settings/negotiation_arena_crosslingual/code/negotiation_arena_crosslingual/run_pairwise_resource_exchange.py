#!/usr/bin/env python3
"""Run one pairwise resource-exchange channel condition."""

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

from run_c0_resource_exchange_baseline import run_episode  # noqa: E402
from run_c0_smoke import (  # noqa: E402
    OpenAIExternalRequestNeeded,
    append_event,
    benchmark_openai_allowed,
    load_benchmark_model_config,
    run_endpoint_probe,
    upstream_commit,
    utc_now,
    write_json,
    write_metrics,
)
from run_pairwise_buy_sell import load_pairwise_plan, rows_for_pair, select_row, slug  # noqa: E402


def selected_provider(explicit: str | None) -> str:
    if explicit:
        return explicit
    override = os.environ.get("NEGOTIATION_BENCHMARK_PROVIDER")
    if override:
        return override
    if benchmark_openai_allowed(load_benchmark_model_config()):
        return "openai_benchmark"
    return "local_qwen"


def resource_role_languages(row: dict[str, Any]) -> dict[str, str]:
    role_languages = row.get("role_languages", {})
    if not isinstance(role_languages, dict):
        raise ValueError("selected pairwise plan row is missing role_languages")
    buyer_language = role_languages.get("buyer")
    seller_language = role_languages.get("seller")
    if not buyer_language or not seller_language:
        raise ValueError("selected pairwise plan row must define buyer and seller languages")
    return {"agent_a": str(buyer_language), "agent_b": str(seller_language)}


def episode_id(pair: str, row: dict[str, Any], seed: int) -> str:
    condition = str(row["condition"]).lower()
    counterbalance = row.get("counterbalance_id")
    suffix = f"_{slug(str(counterbalance))}" if counterbalance else ""
    return f"pair_{slug(pair)}_{condition}{suffix}_resource_exchange_seed{seed:03d}"


def build_plan(pair: str, row: dict[str, Any], seed: int, turn_limit: int, model: str) -> dict[str, Any]:
    eid = episode_id(pair, row, seed)
    episode = {
        "episode_id": eid,
        "condition": row["condition"],
        "game_id": "resource_exchange",
        "language_pair": pair.upper(),
        "role_languages": resource_role_languages(row),
        "pairwise_plan_role_languages": row.get("role_languages", {}),
        "role_mapping": {"buyer": "agent_a", "seller": "agent_b"},
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


def failed_command(args: argparse.Namespace) -> str:
    command = (
        "python3 scripts/run_pairwise_resource_exchange.py "
        f"--pair {args.pair} --condition {args.condition}"
    )
    if args.counterbalance:
        command += f" --counterbalance {args.counterbalance}"
    command += f" --seed {args.seed}"
    return command


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", required=True, choices=["EN-ID", "EN-ZH", "ZH-ID"])
    parser.add_argument("--condition", required=True, choices=["C0", "C1", "C2", "C3"])
    parser.add_argument("--counterbalance", choices=["buyer_lx_seller_ly", "buyer_ly_seller_lx"])
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--turn-limit", type=int, default=6)
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
    command = failed_command(args)

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=command)
    except SystemExit as exc:
        artifact = write_json(
            f"artifacts/results/{plan['episode']['episode_id']}.blocked.json",
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "benchmark_provider_unavailable",
                "failed_command": command,
                "active_benchmark_provider": provider,
                "active_benchmark_model": model,
                "episode": plan["episode"],
                "provider_probe_artifact": "artifacts/results/benchmark_model_probe.json",
                "message": "Pairwise resource_exchange episode is ready but the selected provider failed.",
                "evidence_scope": "No empirical evidence produced by this attempt.",
            },
        )
        append_event(
            "pairwise_resource_exchange",
            "BLOCKED",
            f"{plan['episode']['episode_id']} blocked on provider {provider}; artifact={artifact.relative_to(ROOT)}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(plan, provider, model_metadata)
    except OpenAIExternalRequestNeeded as exc:
        append_event(
            "pairwise_resource_exchange",
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
                "failed_command": command,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
                "episode": plan["episode"],
            },
        )
        append_event(
            "pairwise_resource_exchange",
            "ERROR",
            f"{plan['episode']['episode_id']} failed; artifact={artifact.relative_to(ROOT)}",
        )
        raise

    artifacts = plan["expected_artifacts"]
    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "pairwise_resource_exchange",
        "OK",
        f"{plan['episode']['episode_id']} completed; transcript={transcript_path.relative_to(ROOT)}; "
        f"metrics={metrics_path.relative_to(ROOT)}; provider={provider}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
