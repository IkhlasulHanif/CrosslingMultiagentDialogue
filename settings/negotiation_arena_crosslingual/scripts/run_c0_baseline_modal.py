#!/usr/bin/env python3
"""Run the first C0 baseline episode on Modal with Qwen3-1.7B.

This is a bounded Modal job, not a persistent service. It copies the setting
source into a GPU container, runs one upstream BuySellGame episode with a
Transformers-loaded Qwen model, then writes the returned transcript/metrics back
to this setting's artifact directory.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

import modal


ROOT = Path(__file__).resolve().parents[1]
REMOTE_ROOT = Path("/root/negotiation_arena_setting")
MODEL_ID = "Qwen/Qwen3-1.7B"


app = modal.App("negotiation-arena-c0-qwen-baseline")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "accelerate>=0.33.0",
        "sentencepiece>=0.2.0",
        "torch>=2.4.0",
        "transformers>=4.51.0",
    )
    .add_local_dir(ROOT / "scripts", REMOTE_ROOT / "scripts", copy=True)
    .add_local_dir(ROOT / "config", REMOTE_ROOT / "config", copy=True)
    .add_local_dir(ROOT / "external" / "NegotiationArena", REMOTE_ROOT / "external" / "NegotiationArena", copy=True)
)


def _write_json(relative_path: str, payload: dict[str, Any]) -> Path:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _append_event(kind: str, status: str, message: str) -> None:
    sys.path.insert(0, str(ROOT.parent / "_benchmark_common"))
    from benchmark_harness import append_event

    append_event(ROOT, kind, message, status)


def _load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def _artifact_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@app.function(gpu="L4", image=image, timeout=1800)
def run_modal_baseline() -> dict[str, Any]:
    os.chdir(REMOTE_ROOT)
    sys.path.insert(0, str(REMOTE_ROOT / "scripts"))
    sys.path.insert(0, str(REMOTE_ROOT / "external" / "NegotiationArena"))

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    import run_c0_baseline
    import run_c0_smoke

    class ModalQwenChat:
        _tokenizer = None
        _model = None

        def __init__(self) -> None:
            if ModalQwenChat._tokenizer is None or ModalQwenChat._model is None:
                ModalQwenChat._tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
                ModalQwenChat._model = AutoModelForCausalLM.from_pretrained(
                    MODEL_ID,
                    torch_dtype="auto",
                    device_map="auto",
                    trust_remote_code=True,
                )

        def complete(self, messages: list[dict[str, str]], **_overrides: Any) -> str:
            tokenizer = ModalQwenChat._tokenizer
            model = ModalQwenChat._model
            if tokenizer is None or model is None:
                raise RuntimeError("Qwen model was not initialized")
            try:
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
            except TypeError:
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
            with torch.inference_mode():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.2,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                )
            new_tokens = generated[:, inputs.input_ids.shape[-1] :]
            text = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
            if "</think>" in text:
                text = text.split("</think>", 1)[1].strip()
            return text

    chat_singleton: ModalQwenChat | None = None

    def make_modal_chat_client(_provider: str) -> tuple[ModalQwenChat, dict[str, Any]]:
        nonlocal chat_singleton
        if chat_singleton is None:
            chat_singleton = ModalQwenChat()
        return chat_singleton, {
            "provider": "modal_qwen",
            "model": MODEL_ID,
            "endpoint": "modal://bounded-transformers-job",
            "evidence_scope": "Qwen3-1.7B Modal baseline",
        }

    run_c0_smoke.make_chat_client = make_modal_chat_client

    baseline = run_c0_baseline.load_baseline_plan()
    episode = baseline["episodes"][0]
    episode_plan = run_c0_baseline.baseline_episode_plan(episode)
    model_metadata = {
        "provider": "modal_qwen",
        "model": MODEL_ID,
        "endpoint": "modal://bounded-transformers-job",
        "evidence_scope": "Qwen3-1.7B Modal baseline",
    }
    result = run_c0_smoke.run_episode(episode_plan, "modal_qwen", model_metadata)
    transcript_path = run_c0_smoke.write_json(episode["transcript"], result)
    metrics_path = run_c0_smoke.write_metrics(result, episode["metrics"])
    return {
        "status": "OK",
        "transcript_path": episode["transcript"],
        "metrics_path": episode["metrics"],
        "transcript": _artifact_payload(transcript_path),
        "metrics": _artifact_payload(metrics_path),
    }


@app.local_entrypoint()
def main() -> None:
    try:
        payload = run_modal_baseline.remote()
    except Exception as exc:
        artifact = _write_json(
            "artifacts/results/baseline_c0_buy_sell_en_seed001.modal_error.json",
            {
                "status": "ERROR",
                "provider": "modal_qwen",
                "model": MODEL_ID,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "failed_command": "modal run scripts/run_c0_baseline_modal.py",
            },
        )
        _append_event("baseline", "ERROR", f"Modal C0 baseline failed; artifact={artifact.relative_to(ROOT)}")
        raise

    transcript = _write_json(payload["transcript_path"], payload["transcript"])
    metrics = _write_json(payload["metrics_path"], payload["metrics"])
    marker = _write_json(
        "artifacts/results/baseline_c0_buy_sell_en_seed001.modal_run.json",
        {
            "status": "OK",
            "provider": "modal_qwen",
            "model": MODEL_ID,
            "transcript": payload["transcript_path"],
            "metrics": payload["metrics_path"],
        },
    )
    _append_event(
        "baseline",
        "OK",
        f"Modal Qwen C0 baseline completed; transcript={transcript.relative_to(ROOT)}; "
        f"metrics={metrics.relative_to(ROOT)}; marker={marker.relative_to(ROOT)}",
    )
    print(json.dumps({"transcript": str(transcript), "metrics": str(metrics), "marker": str(marker)}, indent=2))
