#!/usr/bin/env python3
"""Small local Qwen/vLLM chat adapter for this benchmark setting."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "model_adapter.json"


class LocalModelError(RuntimeError):
    """Raised when the local model endpoint cannot satisfy a request."""


@dataclass(frozen=True)
class LocalModelConfig:
    provider: str
    model: str
    base_url: str
    chat_completions_path: str
    timeout_seconds: float
    generation_defaults: dict[str, Any]
    transformers_model_id: str
    local_files_only: bool

    @property
    def endpoint(self) -> str:
        if self.provider == "local_transformers":
            return f"hf-cache://{self.transformers_model_id}"
        base = self.base_url.rstrip("/") + "/"
        path = self.chat_completions_path.lstrip("/")
        return urljoin(base, path)


def load_adapter_config(path: Path = CONFIG_PATH, environ: dict[str, str] | None = None) -> LocalModelConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    env = os.environ if environ is None else environ
    overrides = raw.get("env_overrides", {})

    provider = env.get(overrides.get("provider", ""), raw.get("provider", "local_vllm"))
    base_url = env.get(overrides.get("base_url", ""), raw.get("base_url", "http://127.0.0.1:8000"))
    model = env.get(overrides.get("model", ""), raw.get("model", "Qwen3-1.7B"))
    transformers_model_id = env.get(
        overrides.get("transformers_model_id", ""),
        raw.get("transformers_model_id", "Qwen/Qwen3-1.7B"),
    )
    timeout_value = env.get(
        overrides.get("timeout_seconds", ""),
        str(raw.get("timeout_seconds", 120)),
    )
    try:
        timeout_seconds = float(timeout_value)
    except ValueError as exc:
        raise LocalModelError(f"invalid timeout_seconds value: {timeout_value!r}") from exc

    defaults = raw.get("generation_defaults", {})
    if not isinstance(defaults, dict):
        raise LocalModelError("generation_defaults must be an object")

    return LocalModelConfig(
        provider=str(provider),
        model=str(model),
        base_url=str(base_url),
        chat_completions_path=str(raw.get("chat_completions_path", "/v1/chat/completions")),
        timeout_seconds=timeout_seconds,
        generation_defaults=dict(defaults),
        transformers_model_id=str(transformers_model_id),
        local_files_only=bool(raw.get("local_files_only", True)),
    )


def build_payload(
    messages: list[dict[str, str]],
    config: LocalModelConfig,
    **overrides: Any,
) -> dict[str, Any]:
    if not messages:
        raise LocalModelError("messages must not be empty")
    for index, message in enumerate(messages):
        role = message.get("role")
        content = message.get("content")
        if role not in {"system", "user", "assistant"}:
            raise LocalModelError(f"message {index} has invalid role: {role!r}")
        if not isinstance(content, str) or not content:
            raise LocalModelError(f"message {index} has empty content")

    payload: dict[str, Any] = {
        "model": config.model,
        "messages": messages,
    }
    payload.update(config.generation_defaults)
    payload.update({key: value for key, value in overrides.items() if value is not None})
    return payload


def extract_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LocalModelError("model response has no choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise LocalModelError("model response choice is not an object")
    message = first.get("message")
    if not isinstance(message, dict):
        raise LocalModelError("model response choice has no message object")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise LocalModelError("model response message content is empty")
    return content


class LocalQwenChat:
    def __init__(self, config: LocalModelConfig | None = None) -> None:
        self.config = config or load_adapter_config()

    def complete(self, messages: list[dict[str, str]], **overrides: Any) -> str:
        payload = build_payload(messages, self.config, **overrides)
        request = urllib.request.Request(
            self.config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise LocalModelError(f"local model endpoint request failed: {exc}") from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LocalModelError("local model endpoint returned non-JSON response") from exc
        return extract_text(parsed)


class LocalTransformersQwenChat:
    _tokenizer: Any = None
    _model: Any = None
    _loaded_model_id: str | None = None

    def __init__(self, config: LocalModelConfig | None = None) -> None:
        self.config = config or load_adapter_config()

    def _load(self) -> tuple[Any, Any]:
        if (
            LocalTransformersQwenChat._tokenizer is not None
            and LocalTransformersQwenChat._model is not None
            and LocalTransformersQwenChat._loaded_model_id == self.config.transformers_model_id
        ):
            return LocalTransformersQwenChat._tokenizer, LocalTransformersQwenChat._model

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except Exception as exc:  # pragma: no cover - environment-specific dependency probe
            raise LocalModelError(f"local Transformers Qwen dependencies are unavailable: {exc}") from exc

        try:
            tokenizer = AutoTokenizer.from_pretrained(
                self.config.transformers_model_id,
                local_files_only=self.config.local_files_only,
                trust_remote_code=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                self.config.transformers_model_id,
                local_files_only=self.config.local_files_only,
                dtype="auto",
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception as exc:
            raise LocalModelError(
                f"local Transformers Qwen load failed for {self.config.transformers_model_id}: {exc}"
            ) from exc

        LocalTransformersQwenChat._tokenizer = tokenizer
        LocalTransformersQwenChat._model = model
        LocalTransformersQwenChat._loaded_model_id = self.config.transformers_model_id
        return tokenizer, model

    def complete(self, messages: list[dict[str, str]], **overrides: Any) -> str:
        build_payload(messages, self.config, **overrides)
        tokenizer, model = self._load()
        try:
            import torch
        except Exception as exc:  # pragma: no cover - already covered by _load in normal use
            raise LocalModelError(f"torch is unavailable after model load: {exc}") from exc

        try:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
        defaults = dict(self.config.generation_defaults)
        defaults.update({key: value for key, value in overrides.items() if value is not None})
        max_new_tokens = int(defaults.get("max_tokens", defaults.get("max_new_tokens", 512)))
        temperature = float(defaults.get("temperature", 0.2))
        top_p = float(defaults.get("top_p", 0.9))
        generation_args: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": tokenizer.eos_token_id,
        }
        if temperature > 0:
            generation_args["temperature"] = temperature
            generation_args["top_p"] = top_p

        with torch.inference_mode():
            generated = model.generate(**inputs, **generation_args)
        new_tokens = generated[:, inputs.input_ids.shape[-1] :]
        text = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
        if "</think>" in text:
            text = text.split("</think>", 1)[1].strip()
        if not text:
            raise LocalModelError("local Transformers Qwen returned empty text")
        return text


def make_local_chat(config: LocalModelConfig | None = None) -> Any:
    resolved = config or load_adapter_config()
    if resolved.provider == "local_transformers":
        return LocalTransformersQwenChat(resolved)
    if resolved.provider == "local_vllm":
        return LocalQwenChat(resolved)
    raise LocalModelError(f"unsupported local Qwen provider: {resolved.provider}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-config", action="store_true", help="print resolved adapter config")
    parser.add_argument("--dry-run", action="store_true", help="print a sample request payload without network")
    parser.add_argument("--live-probe", action="store_true", help="send a tiny request to the configured endpoint")
    args = parser.parse_args()

    config = load_adapter_config()
    messages = [
        {"role": "system", "content": "You are a concise negotiation test agent."},
        {"role": "user", "content": "Reply with OK."},
    ]

    if args.show_config:
        print(
            json.dumps(
                {
                    "provider": config.provider,
                    "model": config.model,
                    "endpoint": config.endpoint,
                    "timeout_seconds": config.timeout_seconds,
                    "generation_defaults": config.generation_defaults,
                },
                indent=2,
            )
        )
    if args.dry_run:
        print(json.dumps(build_payload(messages, config, max_tokens=8), indent=2))
    if args.live_probe:
        print(make_local_chat(config).complete(messages, max_tokens=8))
    if not (args.show_config or args.dry_run or args.live_probe):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
