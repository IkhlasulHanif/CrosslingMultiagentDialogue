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
    run_endpoint_probe,
    run_episode,
    upstream_commit,
    utc_now,
    write_json,
    write_metrics,
)


FAILED_COMMAND = "bash scripts/run_c0_baseline.sh"


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

    provider = "local_qwen"
    try:
        model_metadata = run_endpoint_probe(provider)
    except SystemExit as exc:
        artifact = write_blocked_artifact("local_qwen_endpoint_unreachable", str(exc))
        append_event(
            "baseline",
            "BLOCKED",
            f"C0 baseline blocked on local Qwen endpoint; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={FAILED_COMMAND}",
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
                "failed_command": FAILED_COMMAND,
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
        f"metrics={metrics_path.relative_to(ROOT)}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
