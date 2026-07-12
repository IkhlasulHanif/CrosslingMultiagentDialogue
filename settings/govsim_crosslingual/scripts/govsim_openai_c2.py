#!/usr/bin/env python3
"""Run GovSim EN-ID mixed-channel C2 contact episodes with OpenAI override."""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
SCRIPT_DIR = ROOT / "scripts"
RESULT_DIR = ROOT / "artifacts" / "results"
RUN_STORAGE_ROOT = RESULT_DIR / "govsim_openai_c2_runs"

sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from endpoint_probe import probe_endpoint  # noqa: E402
from govsim_openai_baseline import MissingOpenAIKey, load_benchmark_config  # noqa: E402
from govsim_openai_smoke import append_event, read_api_key, run_episode, stamp, utc_now, write_json  # noqa: E402
from local_model_adapter import LocalModelError, VLLMChatAdapter  # noqa: E402


NAMES = ["persona_0", "persona_1", "persona_2", "persona_3", "persona_4"]


def assignment_for(pair: str, counterbalance: str) -> dict[str, str]:
    languages = tuple(part.strip().upper() for part in pair.split("-"))
    if len(languages) != 2:
        raise RuntimeError(f"expected two-language pair, got {pair!r}")
    left, right = languages
    if counterbalance == "A":
        assigned = [left, left, right, right, right]
    elif counterbalance == "B":
        assigned = [left, left, left, right, right]
    else:
        raise RuntimeError("GOVSIM_COUNTERBALANCE must be A or B")
    return dict(zip(NAMES, assigned))


def blocked_result(
    exc: BaseException,
    *,
    run_id: str,
    pair: str,
    counterbalance: str,
    agent_languages: dict[str, str],
    model_name: str | None,
    key_source: str | None,
    endpoint_probe_path: Path | None,
    endpoint_probe_result: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "govsim-c2-openai-contact-v1",
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": False,
        "evidence_scope": "blocked OpenAI benchmark override C2 contact; no Qwen3 evidence",
        "condition": "C2",
        "language_pair": pair,
        "counterbalance": counterbalance,
        "agent_output_languages": agent_languages,
        "model_provider": "openai",
        "model": model_name,
        "api_key_source": key_source,
        "blockers": [f"{type(exc).__name__}: {exc}"],
        "traceback_tail": traceback.format_exc()[-4000:],
        "next_command_once_unblocked": f"./scripts/run_openai_en_id_c2_counterbalance_{counterbalance.lower()}.sh",
    }
    if endpoint_probe_path is not None:
        result["endpoint_probe_path"] = str(endpoint_probe_path.relative_to(ROOT))
    if endpoint_probe_result is not None:
        result["endpoint_probe"] = {
            "schema_version": endpoint_probe_result.get("schema_version"),
            "models_url": endpoint_probe_result.get("models_url"),
            "endpoint_reachable": endpoint_probe_result.get("endpoint_reachable"),
            "blockers": endpoint_probe_result.get("blockers", []),
        }
    return result


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    pair = os.environ.get("GOVSIM_LANGUAGE_PAIR", "EN-ID").strip().upper()
    counterbalance = os.environ.get("GOVSIM_COUNTERBALANCE", "A").strip().upper()
    agent_languages = assignment_for(pair, counterbalance)
    run_id = f"govsim_c2_openai_{pair.lower().replace('-', '_')}_{counterbalance.lower()}_{stamp()}"
    result_path = RESULT_DIR / f"{run_id}.json"
    model_name: str | None = None
    key_source: str | None = None

    try:
        config = load_benchmark_config()
        api_key, key_source = read_api_key(config)
        if not api_key:
            raise MissingOpenAIKey("missing OpenAI benchmark API key from env or configured key files")
        model_name = os.environ.get(config.get("env_model") or "OPENAI_BENCHMARK_MODEL") or config.get("default_model")
        adapter = VLLMChatAdapter(
            base_url="https://api.openai.com/v1",
            model=model_name,
            api_key=api_key,
            timeout_s=120.0,
            max_retries=2,
            retry_sleep_s=2.0,
            completion_token_param="max_completion_tokens",
        )
        result = run_episode(
            adapter,
            model_name,
            run_id,
            provider="openai",
            evidence_scope=(
                "OpenAI benchmark override C2 forced mixed-channel contact; "
                "not Qwen3-1.7B research-matrix evidence"
            ),
            condition="C2",
            language=pair.split("-")[0],
            language_pair=pair,
            agent_languages=agent_languages,
            schema_version="govsim-c2-openai-contact-v1",
            episode_id=f"c2-openai-{pair.lower()}-{counterbalance.lower()}-0001",
            run_storage_root=RUN_STORAGE_ROOT,
        )
        result["api_key_source"] = key_source
        result["benchmark_model_config"] = "config/benchmark_model.json"
        result["openai_override_label"] = "OpenAI benchmark evidence, not Qwen3 evidence"
        result["counterbalance"] = counterbalance
        write_json(result_path, result)
        append_event(
            "contact",
            "OK",
            f"GovSim C2 OpenAI {pair} counterbalance {counterbalance} produced artifact={result_path.relative_to(ROOT)} transcript={result['transcript_path']}",
        )
        print(result_path.relative_to(ROOT))
        return 0
    except (LocalModelError, Exception) as exc:
        endpoint_probe_result = None
        endpoint_probe_path = None
        if not isinstance(exc, MissingOpenAIKey) and model_name:
            config = load_benchmark_config()
            api_key, key_source = read_api_key(config)
            endpoint_probe_result, endpoint_probe_path = probe_endpoint(
                ROOT,
                base_url="https://api.openai.com/v1",
                model=model_name,
                timeout_s=float(os.environ.get("GOVSIM_ENDPOINT_PROBE_TIMEOUT_S", "5")),
                api_key=api_key,
                schema_version="govsim-openai-endpoint-probe-v1",
                model_provider="openai",
                blocker_label="OpenAI benchmark endpoint",
                artifact_prefix="openai_endpoint_probe",
                next_command_once_unblocked=f"./scripts/run_openai_en_id_c2_counterbalance_{counterbalance.lower()}.sh",
            )
        result = blocked_result(
            exc,
            run_id=run_id,
            pair=pair,
            counterbalance=counterbalance,
            agent_languages=agent_languages,
            model_name=model_name,
            key_source=key_source,
            endpoint_probe_path=endpoint_probe_path,
            endpoint_probe_result=endpoint_probe_result,
        )
        write_json(result_path, result)
        append_event(
            "contact",
            "BLOCKED",
            f"GovSim C2 OpenAI {pair} counterbalance {counterbalance} blocked: {type(exc).__name__}: {exc}; artifact={result_path.relative_to(ROOT)}",
        )
        print(result_path.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
