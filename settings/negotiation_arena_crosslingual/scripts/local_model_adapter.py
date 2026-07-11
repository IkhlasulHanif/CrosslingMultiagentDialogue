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


ROOT = Path(__file__).resolve().parents[1]
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

    @property
    def endpoint(self) -> str:
        base = self.base_url.rstrip("/") + "/"
        path = self.chat_completions_path.lstrip("/")
        return urljoin(base, path)


def load_adapter_config(path: Path = CONFIG_PATH, environ: dict[str, str] | None = None) -> LocalModelConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    env = os.environ if environ is None else environ
    overrides = raw.get("env_overrides", {})

    base_url = env.get(overrides.get("base_url", ""), raw.get("base_url", "http://127.0.0.1:8000"))
    model = env.get(overrides.get("model", ""), raw.get("model", "Qwen3-1.7B"))
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
        provider=str(raw.get("provider", "local_vllm")),
        model=str(model),
        base_url=str(base_url),
        chat_completions_path=str(raw.get("chat_completions_path", "/v1/chat/completions")),
        timeout_seconds=timeout_seconds,
        generation_defaults=dict(defaults),
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
        print(LocalQwenChat(config).complete(messages, max_tokens=8))
    if not (args.show_config or args.dry_run or args.live_probe):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
