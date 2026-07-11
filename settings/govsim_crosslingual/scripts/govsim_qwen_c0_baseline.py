#!/usr/bin/env python3
"""Run one GovSim fishery baseline episode through the local Qwen/vLLM adapter.

This is the narrowest executable Qwen baseline command. It uses the same
upstream GovSim fishery environment as the OpenAI bring-up smoke, but it never
reads OpenAI credentials and only targets the configured OpenAI-compatible
local/Modal Qwen endpoint.
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
RUN_STORAGE_ROOT = RESULT_DIR / "govsim_qwen_baseline_runs"

sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from govsim_openai_smoke import append_event, run_episode, stamp, utc_now, write_json  # noqa: E402
from local_model_adapter import LocalModelError, VLLMChatAdapter  # noqa: E402
from translation_pack import TranslationPackNotReady, require_complete_translation_pack  # noqa: E402


def adapter_from_qwen_env() -> VLLMChatAdapter:
    timeout_s = float(os.environ.get("GOVSIM_MODEL_TIMEOUT_S", "120"))
    api_key = os.environ.get("GOVSIM_MODEL_API_KEY") or None
    return VLLMChatAdapter(timeout_s=timeout_s, api_key=api_key)


def baseline_condition_language() -> tuple[str, str]:
    condition = os.environ.get("GOVSIM_CONDITION", "C0").strip().upper()
    language = os.environ.get("GOVSIM_LANGUAGE", "EN").strip().upper()
    if (condition, language) not in {("C0", "EN"), ("C1", "ID")}:
        raise RuntimeError(
            "unsupported baseline pair; use GOVSIM_CONDITION=C0 GOVSIM_LANGUAGE=EN "
            "or GOVSIM_CONDITION=C1 GOVSIM_LANGUAGE=ID"
        )
    return condition, language


def blocked_result(exc: BaseException, adapter: VLLMChatAdapter, condition: str, language: str) -> dict[str, Any]:
    script_name = "run_qwen_c1_baseline.sh" if condition == "C1" else "run_qwen_c0_baseline.sh"
    next_command = (
        "GOVSIM_MODEL_BASE_URL=http://127.0.0.1:8000/v1 "
        f"GOVSIM_MODEL_NAME=Qwen3-1.7B ./scripts/{script_name}"
    )
    schema_suffix = condition.lower()
    blocked_stage = "translation_review_gate" if isinstance(exc, TranslationPackNotReady) else "model_or_runner"
    result = {
        "schema_version": f"govsim-{schema_suffix}-qwen-baseline-v1",
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": False,
        "evidence_scope": f"blocked Qwen3 {condition} baseline; no matrix evidence",
        "condition": condition,
        "language": language,
        "blocked_stage": blocked_stage,
        "model_call_attempted": not isinstance(exc, TranslationPackNotReady),
        "model_provider": "local-vllm-compatible",
        "model": adapter.model,
        "base_url": adapter.base_url,
        "chat_url": adapter.chat_url,
        "blockers": [f"{type(exc).__name__}: {exc}"],
        "traceback_tail": traceback.format_exc()[-4000:],
        "next_command_once_unblocked": next_command,
    }
    if isinstance(exc, TranslationPackNotReady):
        result.update(
            {
                "evidence_scope": f"blocked {condition} baseline before model call; no matrix evidence",
                "translation_gate": exc.check.as_dict(),
                "human_review_packet": "artifacts/logs/translation_human_review_packet.md",
                "next_unblock_command": (
                    "python3 code/translation_pack.py --root . "
                    "--out artifacts/logs/translation_status.json "
                    "--review-out artifacts/logs/translation_human_review_packet.md --strict"
                ),
            }
        )
    return result


def blocked_event_message(
    exc: BaseException,
    adapter: VLLMChatAdapter,
    condition: str,
    artifact_path: Path,
) -> str:
    artifact = artifact_path.relative_to(ROOT)
    if isinstance(exc, TranslationPackNotReady):
        return (
            f"GovSim {condition} Qwen baseline blocked before model call by translation gate: "
            f"{type(exc).__name__}: {exc}; artifact={artifact}"
        )
    return (
        f"GovSim {condition} Qwen baseline blocked at {adapter.chat_url}: "
        f"{type(exc).__name__}: {exc}; artifact={artifact}"
    )


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    condition, language = baseline_condition_language()
    schema_suffix = condition.lower()
    run_id = f"govsim_{schema_suffix}_qwen_baseline_{stamp()}"
    result_path = RESULT_DIR / f"{run_id}.json"
    adapter = adapter_from_qwen_env()

    try:
        require_complete_translation_pack(ROOT, language)
        result = run_episode(
            adapter,
            adapter.model,
            run_id,
            provider="local-vllm-compatible",
            evidence_scope=f"Qwen3 {condition} baseline candidate; valid only if model endpoint is Qwen3-1.7B or configured Qwen",
            condition=condition,
            language=language,
            schema_version=f"govsim-{schema_suffix}-qwen-baseline-v1",
            episode_id=f"{schema_suffix}-qwen-baseline-0001",
            run_storage_root=RUN_STORAGE_ROOT,
        )
        result["base_url"] = adapter.base_url
        result["chat_url"] = adapter.chat_url
        write_json(result_path, result)
        append_event(
            "baseline",
            "OK",
            f"GovSim {condition} Qwen baseline produced transcript/result artifact={result_path.relative_to(ROOT)} transcript={result['transcript_path']}",
        )
        print(result_path.relative_to(ROOT))
        return 0
    except (LocalModelError, Exception) as exc:
        result = blocked_result(exc, adapter, condition, language)
        write_json(result_path, result)
        append_event("baseline", "BLOCKED", blocked_event_message(exc, adapter, condition, result_path))
        print(result_path.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
