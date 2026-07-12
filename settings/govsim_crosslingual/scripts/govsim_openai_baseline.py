#!/usr/bin/env python3
"""Run GovSim fishery baselines with the configured OpenAI benchmark override.

These artifacts are OpenAI benchmark evidence only. They must not be reported as
Qwen3-1.7B evidence. Language is treated as the interaction-output channel:
GovSim rules/private state stay in English while model replies are constrained
to the assigned output language.
"""

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
RUN_STORAGE_ROOT = RESULT_DIR / "govsim_openai_baseline_runs"

sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from govsim_openai_smoke import append_event, read_api_key, run_episode, stamp, utc_now, write_json  # noqa: E402
from endpoint_probe import probe_endpoint  # noqa: E402
from local_model_adapter import LocalModelError, VLLMChatAdapter  # noqa: E402
from translation_pack import (  # noqa: E402
    TranslationPackNotReady,
    render_human_review_manifest,
    render_human_review_packet,
    require_complete_translation_pack,
)


def load_benchmark_config() -> dict[str, Any]:
    path = ROOT / "config" / "benchmark_model.json"
    if not path.exists():
        raise RuntimeError("missing config/benchmark_model.json")
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("provider") != "openai":
        raise RuntimeError("config/benchmark_model.json does not allow provider=openai")
    policy = config.get("policy") or {}
    if policy.get("benchmark_execution_may_use_openai_key") is not True:
        raise RuntimeError("config/benchmark_model.json policy does not allow OpenAI benchmark execution")
    return config


def baseline_condition_language() -> tuple[str, str]:
    condition = os.environ.get("GOVSIM_CONDITION", "C0").strip().upper()
    language = os.environ.get("GOVSIM_LANGUAGE", "EN").strip().upper()
    pair = os.environ.get("GOVSIM_LANGUAGE_PAIR", "EN-ID").strip().upper()
    pair_languages = tuple(part.strip() for part in pair.split("-"))
    if condition not in {"C0", "C1"} or language not in {"EN", "ID", "ZH"}:
        raise RuntimeError(
            "unsupported baseline; use GOVSIM_CONDITION=C0 or C1 with GOVSIM_LANGUAGE=EN, ID, or ZH"
        )
    if len(pair_languages) != 2 or language not in pair_languages:
        raise RuntimeError(f"GOVSIM_LANGUAGE={language} is not in GOVSIM_LANGUAGE_PAIR={pair}")
    return condition, language


def blocked_result(
    exc: BaseException,
    condition: str,
    language: str,
    *,
    model_name: str | None,
    key_source: str | None,
    endpoint_probe_path: Path | None = None,
    endpoint_probe_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    schema_suffix = condition.lower()
    blocked_stage = "translation_review_gate" if isinstance(exc, TranslationPackNotReady) else "model_or_runner"
    model_call_attempted = not isinstance(exc, TranslationPackNotReady) and not isinstance(exc, MissingOpenAIKey)
    result: dict[str, Any] = {
        "schema_version": f"govsim-{schema_suffix}-openai-baseline-v1",
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": False,
        "evidence_scope": f"blocked OpenAI benchmark override {condition} baseline; no Qwen3 evidence",
        "condition": condition,
        "language": language,
        "blocked_stage": blocked_stage,
        "model_call_attempted": model_call_attempted,
        "model_provider": "openai",
        "model": model_name,
        "api_key_source": key_source,
        "blockers": [f"{type(exc).__name__}: {exc}"],
        "traceback_tail": traceback.format_exc()[-4000:],
        "next_command_once_unblocked": f"./scripts/run_openai_{schema_suffix}_baseline.sh",
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
    if isinstance(exc, TranslationPackNotReady):
        result.update(
            {
                "evidence_scope": f"blocked OpenAI benchmark override {condition} baseline before model call; no matrix evidence",
                "translation_gate": exc.check.as_dict(),
                "human_review_packet": "artifacts/logs/translation_human_review_packet.md",
                "human_review_manifest": "artifacts/logs/translation_human_review_manifest.json",
                "next_unblock_command": (
                    "python3 code/translation_pack.py --root . "
                    "--out artifacts/logs/translation_status.json "
                    "--review-out artifacts/logs/translation_human_review_packet.md "
                    "--review-manifest-out artifacts/logs/translation_human_review_manifest.json --strict"
                ),
            }
        )
    return result


def blocked_event_message(
    exc: BaseException,
    condition: str,
    artifact_path: Path,
    *,
    endpoint_probe_path: Path | None = None,
) -> str:
    artifact = artifact_path.relative_to(ROOT)
    schema_suffix = condition.lower()
    next_command = f"./scripts/run_openai_{schema_suffix}_baseline.sh"
    if isinstance(exc, TranslationPackNotReady):
        return (
            f"GovSim {condition} OpenAI baseline blocked before model call by translation gate: "
            f"{type(exc).__name__}: {exc}; artifact={artifact}; "
            "review_manifest=artifacts/logs/translation_human_review_manifest.json; "
            f"next={next_command}"
        )
    message = (
        f"GovSim {condition} OpenAI baseline blocked: {type(exc).__name__}: {exc}; "
        f"artifact={artifact}; next={next_command}"
    )
    if endpoint_probe_path is not None:
        message += f"; endpoint_probe={endpoint_probe_path.relative_to(ROOT)}"
    return message


class MissingOpenAIKey(RuntimeError):
    """Raised when the configured benchmark API key is not available."""


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    condition, language = baseline_condition_language()
    schema_suffix = condition.lower()
    run_id = f"govsim_{schema_suffix}_openai_baseline_{stamp()}"
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
                f"OpenAI benchmark override {condition} baseline; "
                "not Qwen3-1.7B research-matrix evidence"
            ),
            condition=condition,
            language=language,
            language_pair=os.environ.get("GOVSIM_LANGUAGE_PAIR", "EN-ID").strip().upper(),
            schema_version=f"govsim-{schema_suffix}-openai-baseline-v1",
            episode_id=f"{schema_suffix}-openai-baseline-0001",
            run_storage_root=RUN_STORAGE_ROOT,
        )
        result["api_key_source"] = key_source
        result["benchmark_model_config"] = "config/benchmark_model.json"
        result["openai_override_label"] = "OpenAI benchmark evidence, not Qwen3 evidence"
        write_json(result_path, result)
        append_event(
            "baseline",
            "OK",
            f"GovSim {condition} OpenAI baseline produced transcript/result artifact={result_path.relative_to(ROOT)} transcript={result['transcript_path']}",
        )
        print(result_path.relative_to(ROOT))
        return 0
    except (LocalModelError, Exception) as exc:
        endpoint_probe_result = None
        endpoint_probe_path = None
        if isinstance(exc, TranslationPackNotReady):
            review_packet_path = ROOT / "artifacts" / "logs" / "translation_human_review_packet.md"
            review_manifest_path = ROOT / "artifacts" / "logs" / "translation_human_review_manifest.json"
            review_packet_path.parent.mkdir(parents=True, exist_ok=True)
            review_packet_path.write_text(render_human_review_packet(ROOT), encoding="utf-8")
            review_manifest = render_human_review_manifest(ROOT)
            review_manifest_path.write_text(
                json.dumps(review_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if not isinstance(exc, (TranslationPackNotReady, MissingOpenAIKey)) and model_name:
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
                next_command_once_unblocked=f"./scripts/run_openai_{schema_suffix}_baseline.sh",
            )
        result = blocked_result(
            exc,
            condition,
            language,
            model_name=model_name,
            key_source=key_source,
            endpoint_probe_path=endpoint_probe_path,
            endpoint_probe_result=endpoint_probe_result,
        )
        write_json(result_path, result)
        append_event(
            "baseline",
            "BLOCKED",
            blocked_event_message(
                exc,
                condition,
                result_path,
                endpoint_probe_path=endpoint_probe_path,
            ),
        )
        print(result_path.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
