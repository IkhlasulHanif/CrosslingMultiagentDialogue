#!/usr/bin/env python3
"""Run the first Qwen/local C0 baseline episode, or record the exact blocker."""

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

from local_model_adapter import load_adapter_config  # noqa: E402
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


FAILED_COMMAND = "bash scripts/run_c0_baseline.sh"
OPENAI_FAILED_COMMAND = "bash scripts/run_c0_openai_baseline.sh"


def load_baseline_plan() -> dict[str, Any]:
    return json.loads((ROOT / "config" / "baseline_plan.json").read_text(encoding="utf-8"))


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
    return "local_qwen"


def provider_artifacts(artifacts: dict[str, str], provider: str) -> dict[str, str]:
    if provider != "openai_benchmark":
        return artifacts
    return {
        "transcript": artifacts["transcript"].replace(".json", ".openai_benchmark.json"),
        "metrics": artifacts["metrics"].replace(".metrics.json", ".openai_benchmark.metrics.json"),
    }


def command_for_provider(provider: str) -> str:
    return OPENAI_FAILED_COMMAND if provider == "openai_benchmark" else FAILED_COMMAND


def write_blocked_artifact(reason: str, error: str | None = None) -> Path:
    config = load_adapter_config()
    probe_path = ROOT / "artifacts" / "results" / "model_endpoint_probe.json"
    probe_error = None
    if probe_path.exists():
        try:
            probe_error = json.loads(probe_path.read_text(encoding="utf-8")).get("error")
        except json.JSONDecodeError:
            probe_error = None
    payload: dict[str, Any] = {
        "checked_at": utc_now(),
        "status": "BLOCKED",
        "blocker": reason,
        "failed_command": FAILED_COMMAND,
        "provider": config.provider,
        "model": config.model,
        "endpoint": config.endpoint,
        "message": "C0 baseline requires a usable local Qwen provider.",
        "next_action": (
            "For local_transformers, ensure Qwen/Qwen3-1.7B is present in the local Hugging Face cache "
            "with torch/transformers installed. For local_vllm, start Qwen3-1.7B behind the configured "
            "OpenAI-compatible endpoint or set LOCAL_QWEN_BASE_URL/LOCAL_QWEN_MODEL. Then rerun "
            "bash scripts/run_c0_baseline.sh."
        ),
        "openai_smoke_override_used": False,
        "related_probe": "artifacts/results/model_endpoint_probe.json",
    }
    if probe_error or error:
        payload["error"] = probe_error or error
    return write_json("artifacts/results/baseline_c0_buy_sell_en_seed001.blocked.json", payload)


def main() -> int:
    plan = load_baseline_plan()
    episodes = plan.get("episodes", [])
    if len(episodes) != 1:
        raise RuntimeError("config/baseline_plan.json must contain exactly one first C0 baseline episode")
    episode_config = episodes[0]
    episode_plan = baseline_episode_plan(episode_config)

    provider = selected_benchmark_provider()
    failed_command = command_for_provider(provider)
    if provider == "openai_benchmark" and not benchmark_openai_allowed(load_benchmark_model_config()):
        artifact = write_json(
            "artifacts/results/baseline_c0_buy_sell_en_seed001.openai_benchmark.blocked.json",
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "openai_benchmark_override_not_allowed",
                "failed_command": failed_command,
                "message": "OpenAI benchmark provider was requested but config/benchmark_model.json does not allow it.",
                "next_command": "Use local Qwen with bash scripts/run_c0_baseline.sh or update config/benchmark_model.json explicitly.",
            },
        )
        append_event(
            "baseline",
            "BLOCKED",
            f"C0 OpenAI benchmark baseline blocked by config; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={failed_command}",
        )
        return 2
    episode_plan["expected_artifacts"] = provider_artifacts(episode_plan["expected_artifacts"], provider)

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=failed_command)
    except SystemExit as exc:
        if provider == "openai_benchmark":
            append_event(
                "baseline",
                "BLOCKED",
                f"C0 OpenAI benchmark baseline blocked on provider probe; failed_command={failed_command}",
            )
            return int(exc.code) if isinstance(exc.code, int) else 2
        artifact = write_blocked_artifact("local_qwen_endpoint_unreachable", str(exc))
        append_event(
            "baseline",
            "BLOCKED",
            f"C0 baseline blocked on local Qwen endpoint; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={failed_command}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(episode_plan, provider, model_metadata)
    except Exception as exc:
        artifact = write_json(
            "artifacts/results/baseline_c0_buy_sell_en_seed001.error.json",
            {
                "checked_at": utc_now(),
                "status": "ERROR",
                "failed_command": failed_command,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
            },
        )
        append_event("baseline", "ERROR", f"C0 baseline episode failed; artifact={artifact.relative_to(ROOT)}")
        raise

    artifacts = episode_plan["expected_artifacts"]
    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "baseline",
        "OK",
        f"C0 baseline buy_sell episode completed; transcript={transcript_path.relative_to(ROOT)}; "
        f"metrics={metrics_path.relative_to(ROOT)}; provider={provider}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
