#!/usr/bin/env python3
"""Run one C0 GovSim fishery episode through the local Qwen/vLLM adapter.

This is the narrowest executable Qwen baseline command. It uses the same
upstream GovSim fishery environment and prompt text as the OpenAI bring-up
smoke, but it never reads OpenAI credentials and only targets the configured
OpenAI-compatible local/Modal Qwen endpoint.
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
RUN_STORAGE_ROOT = RESULT_DIR / "govsim_qwen_c0_baseline_runs"

sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from govsim_openai_smoke import append_event, run_episode, stamp, utc_now, write_json  # noqa: E402
from local_model_adapter import LocalModelError, VLLMChatAdapter  # noqa: E402


def adapter_from_qwen_env() -> VLLMChatAdapter:
    timeout_s = float(os.environ.get("GOVSIM_MODEL_TIMEOUT_S", "120"))
    api_key = os.environ.get("GOVSIM_MODEL_API_KEY") or None
    return VLLMChatAdapter(timeout_s=timeout_s, api_key=api_key)


def blocked_result(exc: BaseException, adapter: VLLMChatAdapter) -> dict[str, Any]:
    next_command = (
        "GOVSIM_MODEL_BASE_URL=http://127.0.0.1:8000/v1 "
        "GOVSIM_MODEL_NAME=Qwen3-1.7B ./scripts/run_qwen_c0_baseline.sh"
    )
    return {
        "schema_version": "govsim-c0-qwen-baseline-v1",
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": False,
        "evidence_scope": "blocked Qwen3 C0 baseline; no matrix evidence",
        "condition": "C0",
        "language": "EN",
        "model_provider": "local-vllm-compatible",
        "model": adapter.model,
        "base_url": adapter.base_url,
        "chat_url": adapter.chat_url,
        "blockers": [f"{type(exc).__name__}: {exc}"],
        "traceback_tail": traceback.format_exc()[-4000:],
        "next_command_once_unblocked": next_command,
    }


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = f"govsim_c0_qwen_baseline_{stamp()}"
    result_path = RESULT_DIR / f"{run_id}.json"
    adapter = adapter_from_qwen_env()

    try:
        result = run_episode(
            adapter,
            adapter.model,
            run_id,
            provider="local-vllm-compatible",
            evidence_scope="Qwen3 C0 baseline candidate; valid only if model endpoint is Qwen3-1.7B or configured Qwen",
            condition="C0",
            language="EN",
            schema_version="govsim-c0-qwen-baseline-v1",
            episode_id="c0-qwen-baseline-0001",
            run_storage_root=RUN_STORAGE_ROOT,
        )
        result["base_url"] = adapter.base_url
        result["chat_url"] = adapter.chat_url
        write_json(result_path, result)
        append_event(
            "baseline",
            "OK",
            f"GovSim C0 Qwen baseline produced transcript/result artifact={result_path.relative_to(ROOT)} transcript={result['transcript_path']}",
        )
        print(result_path.relative_to(ROOT))
        return 0
    except (LocalModelError, Exception) as exc:
        result = blocked_result(exc, adapter)
        write_json(result_path, result)
        append_event(
            "baseline",
            "BLOCKED",
            f"GovSim C0 Qwen baseline blocked at {adapter.chat_url}: {type(exc).__name__}: {exc}; artifact={result_path.relative_to(ROOT)}",
        )
        print(result_path.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
