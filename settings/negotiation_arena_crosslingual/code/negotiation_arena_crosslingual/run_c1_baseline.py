#!/usr/bin/env python3
"""Run the first Qwen/local C1 ID baseline episode, or record the exact gate."""

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


def pending_review_units(review: dict[str, Any]) -> list[str]:
    return [
        f"{item.get('context', '')}/{item.get('unit_id', '')}"
        for item in review.get("units", [])
        if item.get("reviewer_status") != "approved"
    ]


def translation_review_complete(review: dict[str, Any]) -> bool:
    reviewer = review.get("reviewer", {})
    return (
        review.get("status") == "human_review_complete"
        and reviewer.get("completed") is True
        and bool(reviewer.get("name"))
        and bool(reviewer.get("reviewed_at"))
        and not pending_review_units(review)
    )


def selected_benchmark_provider() -> str:
    override = os.environ.get("NEGOTIATION_BENCHMARK_PROVIDER")
    if override:
        return override
    if benchmark_openai_allowed(load_benchmark_model_config()):
        return "openai_benchmark"
    return "local_qwen"


def write_translation_blocked_artifact(review: dict[str, Any]) -> Path:
    pending = pending_review_units(review)
    benchmark_config = load_benchmark_model_config() or {}
    provider_after_gate = selected_benchmark_provider()
    if provider_after_gate == "openai_benchmark":
        provider_model_after_gate = benchmark_config.get("default_model", "gpt-4.1-mini")
        provider_scope_after_gate = "OpenAI benchmark override evidence; not Qwen3-1.7B evidence"
    else:
        provider_model_after_gate = "Qwen3-1.7B"
        provider_scope_after_gate = "Qwen/local model run"
    payload = {
        "checked_at": utc_now(),
        "status": "BLOCKED",
        "blocker": "pending_human_translation_review",
        "failed_command": FAILED_COMMAND,
        "condition": "C1",
        "game_id": "buy_sell",
        "language_pair": "EN-ID",
        "planned_model": "Qwen3-1.7B",
        "active_benchmark_provider_after_gate": provider_after_gate,
        "active_benchmark_model_after_gate": provider_model_after_gate,
        "active_benchmark_evidence_scope_after_gate": provider_scope_after_gate,
        "openai_key_read": False,
        "message": "C1 ID baseline is gated until a bilingual human approves every EN-ID prompt unit.",
        "review_status": review.get("status"),
        "reviewer_completed": review.get("reviewer", {}).get("completed"),
        "pending_units": pending,
        "pending_unit_count": len(pending),
        "source_translation_file": review.get("source_translation_file"),
        "review_file": "config/translation_review.json",
        "review_packet": "docs/id_translation_review.md",
        "next_action": (
            "Have a bilingual reviewer fill config/translation_review.json with reviewer.completed=true, "
            "reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit. "
            "Then run python3 scripts/validate_translation_review.py and rerun bash scripts/run_c1_baseline.sh."
        ),
        "evidence_scope": "No C1 empirical evidence produced; this is a gate artifact only.",
    }
    return write_json(BLOCKED_ARTIFACT, payload)


def main() -> int:
    plan = load_c1_plan()
    episodes = plan.get("episodes", [])
    if len(episodes) != 1:
        raise RuntimeError("config/c1_baseline_plan.json must contain exactly one first C1 baseline episode")

    review = load_json("config/translation_review.json")
    if not translation_review_complete(review):
        artifact = write_translation_blocked_artifact(review)
        append_event(
            "baseline",
            "BLOCKED",
            f"C1 ID baseline blocked on pending human translation review; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={FAILED_COMMAND}; next_command={FAILED_COMMAND}",
        )
        print(json.dumps({"blocked": str(artifact)}, indent=2))
        return 2

    episode_config = episodes[0]
    episode_plan = baseline_episode_plan(episode_config)
    provider = selected_benchmark_provider()

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=FAILED_COMMAND)
    except SystemExit as exc:
        append_event(
            "baseline",
            "BLOCKED",
            f"C1 ID baseline blocked on benchmark provider {provider}; failed_command={FAILED_COMMAND}",
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
