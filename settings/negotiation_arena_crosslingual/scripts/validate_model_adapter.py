#!/usr/bin/env python3
"""Validate the setting-local local-model adapter without requiring a server."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from local_model_adapter import build_payload, extract_text, load_adapter_config  # noqa: E402


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def main() -> int:
    config_file = load_json("config/model_adapter.json")
    benchmark = load_json("config/benchmark.json")
    config = load_adapter_config()

    if config.provider not in {"local_vllm", "local_transformers"}:
        return fail("model adapter provider must remain local_vllm or local_transformers")
    if config.model != benchmark.get("default_model"):
        return fail("model adapter model must match benchmark default_model")
    if config.provider == "local_vllm" and not config.endpoint.endswith("/v1/chat/completions"):
        return fail("model adapter endpoint must target /v1/chat/completions")
    if config.provider == "local_transformers":
        if config.transformers_model_id != "Qwen/Qwen3-1.7B":
            return fail("local_transformers must target Qwen/Qwen3-1.7B")
        if not config.local_files_only:
            return fail("local_transformers must use local_files_only=true")
        if not config.endpoint.startswith("hf-cache://"):
            return fail("local_transformers endpoint evidence must use hf-cache://")

    forbidden_envs = {"OPENAI_API_KEY", "OPENAI_API_KEY_FILE", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID"}
    override_values = set(config_file.get("env_overrides", {}).values())
    forbidden_used = forbidden_envs & override_values
    if forbidden_used:
        return fail("model adapter must not use OpenAI API-key environment variables")

    payload = build_payload(
        [
            {"role": "system", "content": "You are a negotiation agent."},
            {"role": "user", "content": "Make one structured offer."},
        ],
        config,
        max_tokens=16,
    )
    if payload.get("model") != config.model:
        return fail("payload does not preserve configured model")
    if payload.get("max_tokens") != 16:
        return fail("payload overrides are not applied")
    if payload.get("temperature") != config.generation_defaults.get("temperature"):
        return fail("payload does not include generation defaults")

    text = extract_text({"choices": [{"message": {"content": "OK"}}]})
    if text != "OK":
        return fail("response extraction failed")

    print(
        "OK: local Qwen adapter config, dry payload construction, "
        "and response extraction validated without live endpoint."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
