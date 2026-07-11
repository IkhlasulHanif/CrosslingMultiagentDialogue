#!/usr/bin/env python3
"""Validate the planned first C0 smoke episode contract.

This validator checks only the setting-local smoke plan. It does not execute a
benchmark episode and must not be treated as benchmark evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    benchmark = load_json("config/benchmark.json")
    games = load_json("config/games.json")
    model_adapter = load_json("config/model_adapter.json")
    plan = load_json("config/smoke_plan.json")
    smoke_model_path = ROOT / "config" / "smoke_model.json"
    smoke_model = json.loads(smoke_model_path.read_text(encoding="utf-8")) if smoke_model_path.exists() else {}

    episode = plan.get("episode", {})
    if plan.get("schema_version") != 1:
        return fail("config/smoke_plan.json schema_version must be 1")
    if plan.get("status") != "planned_gated_on_bringup_and_model_endpoint":
        return fail("smoke plan must remain gated until source bring-up and one allowed local Qwen provider pass")

    if episode.get("condition") != "C0":
        return fail("first smoke episode must be C0")
    if episode.get("game_id") != "buy_sell":
        return fail("first smoke episode must use buy_sell for the narrowest price-negotiation check")
    if episode.get("model") != benchmark.get("default_model"):
        return fail("smoke model must match the benchmark default model")
    if model_adapter.get("model") != benchmark.get("default_model"):
        return fail("model adapter must remain aligned with the benchmark default model")
    if model_adapter.get("provider") not in {"local_vllm", "local_transformers", "modal_qwen"}:
        return fail("model adapter provider must stay on local/Modal Qwen, not OpenAI")

    selected_game_ids = [game.get("id") for game in games.get("selected_games", []) if game.get("include")]
    if episode.get("game_id") not in selected_game_ids:
        return fail("smoke game_id is not included in config/games.json")

    role_languages = episode.get("role_languages", {})
    if role_languages != {"buyer": "EN", "seller": "EN"}:
        return fail("C0 smoke must assign both buy_sell roles to EN")

    schema = plan.get("minimum_episode_schema", {})
    required_keys = set(schema.get("required_top_level_keys", []))
    missing_required = {
        "episode_id",
        "condition",
        "game_id",
        "role_languages",
        "messages",
        "deal",
        "final_terms",
        "payoffs",
    } - required_keys
    if missing_required:
        return fail("smoke schema omits required keys: " + ", ".join(sorted(missing_required)))
    if schema.get("allowed_message_languages") != ["EN"]:
        return fail("C0 smoke must allow only EN message metadata")
    if "OFFER" not in schema.get("required_structured_actions", []):
        return fail("C0 smoke must require at least one parseable OFFER")

    preconditions = {item.get("id"): item for item in plan.get("preconditions", [])}
    for required in [
        "upstream_checkout",
        "local_qwen_provider",
        "structured_offer_parser",
        "process_metrics",
    ]:
        item = preconditions.get(required)
        if not item or item.get("required") is not True or not item.get("check"):
            return fail(f"smoke precondition is incomplete: {required}")

    override = preconditions.get("openai_smoke_override")
    if override:
        policy = smoke_model.get("policy", {}) if isinstance(smoke_model, dict) else {}
        allowed = (
            smoke_model.get("provider") == "openai"
            and policy.get("benchmark_smoke_may_use_openai_key") is True
            and policy.get("codex_auth_uses_openai_key") is False
        )
        if not allowed:
            return fail("openai_smoke_override precondition exists but config/smoke_model.json does not allow it")
        if override.get("required") is not False:
            return fail("openai_smoke_override must remain optional and smoke-only")

    artifacts = plan.get("expected_artifacts", {})
    transcript = artifacts.get("transcript", "")
    metrics = artifacts.get("metrics", "")
    if not transcript.startswith("artifacts/transcripts/") or not transcript.endswith(".json"):
        return fail("smoke transcript artifact must be a JSON file under artifacts/transcripts")
    if not metrics.startswith("artifacts/results/") or not metrics.endswith(".metrics.json"):
        return fail("smoke metrics artifact must be a .metrics.json file under artifacts/results")

    print(
        "OK: C0 smoke plan is narrow, EN-monolingual, selected-game aligned, "
        "Qwen-default, and ready to run after source bring-up plus an allowed local Qwen probe succeeds."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
