#!/usr/bin/env python3
"""Run the first C1 ID output-channel baseline episode, or record the exact gate."""

from __future__ import annotations

import copy
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))

from run_c0_smoke import (  # noqa: E402
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


FAILED_COMMAND = "bash scripts/run_c1_baseline.sh"
BLOCKED_ARTIFACT = "artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json"


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def load_c1_plan() -> dict[str, Any]:
    return load_json("config/c1_baseline_plan.json")


def baseline_episode_plan(episode: dict[str, Any]) -> dict[str, Any]:
    return {
        "episode": {
            "episode_id": episode["episode_id"],
            "condition": episode["condition"],
            "game_id": episode["game_id"],
            "language_pair": episode["language_pair"],
            "role_languages": copy.deepcopy(episode["role_languages"]),
            "model": episode["model"],
            "turn_limit": episode["turn_limit"],
            "seed": episode["seed"],
        },
        "expected_artifacts": {
            "transcript": episode["transcript"],
            "metrics": episode["metrics"],
        },
    }


def selected_benchmark_provider() -> str:
    override = os.environ.get("NEGOTIATION_BENCHMARK_PROVIDER")
    if override:
        return override
    if benchmark_openai_allowed(load_benchmark_model_config()):
        return "openai_benchmark"
    return "local_qwen"


def main() -> int:
    plan = load_c1_plan()
    episodes = plan.get("episodes", [])
    if len(episodes) != 1:
        raise RuntimeError("config/c1_baseline_plan.json must contain exactly one first C1 baseline episode")

    episode_config = episodes[0]
    episode_plan = baseline_episode_plan(episode_config)
    provider = selected_benchmark_provider()

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=FAILED_COMMAND)
    except SystemExit as exc:
        benchmark_config = load_benchmark_model_config() or {}
        artifact = write_json(
            BLOCKED_ARTIFACT,
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "benchmark_provider_unavailable",
                "failed_command": FAILED_COMMAND,
                "condition": "C1",
                "game_id": "buy_sell",
                "language_pair": "EN-ID",
                "role_languages": episode_config.get("role_languages", {}),
                "active_benchmark_provider": provider,
                "active_benchmark_model": benchmark_config.get("default_model", episode_config.get("model")),
                "active_benchmark_evidence_scope": (
                    "OpenAI benchmark override evidence; not Qwen3-1.7B evidence"
                    if provider == "openai_benchmark"
                    else "Qwen/local model run"
                ),
                "channel_gate_status": "ready",
                "channel_gate_artifact": "artifacts/results/language_channel_validation.json",
                "provider_probe_artifact": "artifacts/results/benchmark_model_probe.json"
                if provider == "openai_benchmark"
                else "artifacts/results/model_endpoint_probe.json",
                "message": "C1 ID output-channel baseline is ready but the selected benchmark provider probe failed.",
                "next_action": f"Fix the selected benchmark provider, then rerun {FAILED_COMMAND}.",
                "evidence_scope": "No C1 empirical evidence produced; this is a provider blocker artifact only.",
            },
        )
        append_event(
            "baseline",
            "BLOCKED",
            f"C1 ID baseline blocked on benchmark provider {provider}; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={FAILED_COMMAND}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(episode_plan, provider, model_metadata)
    except Exception as exc:
        artifact = write_json(
            "artifacts/results/baseline_c1_buy_sell_id_seed001.error.json",
            {
                "checked_at": utc_now(),
                "status": "ERROR",
                "failed_command": FAILED_COMMAND,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
            },
        )
        append_event("baseline", "ERROR", f"C1 ID baseline episode failed; artifact={artifact.relative_to(ROOT)}")
        raise

    artifacts = episode_plan["expected_artifacts"]
    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "baseline",
        "OK",
        f"C1 ID baseline buy_sell episode completed; transcript={transcript_path.relative_to(ROOT)}; "
        f"metrics={metrics_path.relative_to(ROOT)}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
