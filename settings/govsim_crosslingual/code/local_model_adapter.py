#!/usr/bin/env python3
"""Local Qwen/vLLM chat adapter for the GovSim setting.

The adapter targets an OpenAI-compatible local endpoint such as vLLM's
`/v1/chat/completions`, but it does not read or require OpenAI credentials.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from http.client import RemoteDisconnected
from dataclasses import dataclass
from typing import Any, Iterable


DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
DEFAULT_MODEL = "Qwen3-1.7B"
THINK_RE = re.compile(r"<think>(.*?)</think>", flags=re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str

    def as_payload(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ModelResponse:
    model: str
    visible_text: str
    thinking: list[str]
    raw_text: str
    finish_reason: str | None
    usage: dict[str, Any]


class LocalModelError(RuntimeError):
    """Raised when the local model endpoint cannot return a usable response."""


def strip_think_blocks(text: str) -> tuple[str, list[str]]:
    """Return visible text plus any stripped Qwen `<think>...</think>` blocks."""

    thinking = [match.group(1).strip() for match in THINK_RE.finditer(text)]
    visible = THINK_RE.sub("", text)
    visible = re.sub(r"\n{3,}", "\n\n", visible).strip()
    return visible, thinking


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in {None, "text"}:
                value = item.get("text", "")
                if isinstance(value, str):
                    parts.append(value)
        return "\n".join(parts)
    return "" if content is None else str(content)


class VLLMChatAdapter:
    """Small OpenAI-compatible adapter for local or explicitly configured Qwen."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_s: float = 120.0,
        api_key: str | None = None,
        opener: Any | None = None,
        max_retries: int = 0,
        retry_sleep_s: float = 1.0,
        completion_token_param: str = "max_tokens",
    ) -> None:
        if completion_token_param not in {"max_tokens", "max_completion_tokens"}:
            raise ValueError(
                "completion_token_param must be 'max_tokens' or 'max_completion_tokens'"
            )
        self.base_url = (base_url or os.environ.get("GOVSIM_MODEL_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("GOVSIM_MODEL_NAME") or DEFAULT_MODEL
        self.timeout_s = timeout_s
        self.api_key = api_key
        self._opener = opener or urllib.request.build_opener()
        self.max_retries = max(0, max_retries)
        self.retry_sleep_s = max(0.0, retry_sleep_s)
        self.completion_token_param = completion_token_param

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def complete(
        self,
        messages: Iterable[ChatMessage | dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 512,
        extra: dict[str, Any] | None = None,
    ) -> ModelResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [self._message_payload(message) for message in messages],
            "temperature": temperature,
            self.completion_token_param: max_tokens,
        }
        if extra:
            payload.update(extra)

        request = urllib.request.Request(
            self.chat_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )

        body = self._open_with_retries(request)

        return self._parse_response(body)

    def _open_with_retries(self, request: urllib.request.Request) -> str:
        last_exc: BaseException | None = None
        attempts = self.max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                with self._opener.open(request, timeout=self.timeout_s) as response:
                    return response.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise LocalModelError(f"Local model HTTP {exc.code}: {detail}") from exc
            except urllib.error.URLError as exc:
                last_exc = exc
                if not _is_transient_error(exc.reason) or attempt >= attempts:
                    raise LocalModelError(f"Local model endpoint unavailable at {self.chat_url}: {exc.reason}") from exc
            except (RemoteDisconnected, TimeoutError) as exc:
                last_exc = exc
                if attempt >= attempts:
                    raise LocalModelError(
                        f"Local model endpoint unavailable at {self.chat_url}: {exc}"
                    ) from exc

            if self.retry_sleep_s:
                time.sleep(self.retry_sleep_s)

        raise LocalModelError(f"Local model endpoint unavailable at {self.chat_url}: {last_exc}")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @staticmethod
    def _message_payload(message: ChatMessage | dict[str, str]) -> dict[str, str]:
        if isinstance(message, ChatMessage):
            return message.as_payload()
        return {"role": message["role"], "content": message["content"]}

    def _parse_response(self, body: str) -> ModelResponse:
        try:
            data = json.loads(body)
            choice = data["choices"][0]
            raw_text = _content_to_text(choice.get("message", {}).get("content"))
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise LocalModelError(f"Malformed local model response: {body[:500]}") from exc

        visible, thinking = strip_think_blocks(raw_text)
        return ModelResponse(
            model=str(data.get("model") or self.model),
            visible_text=visible,
            thinking=thinking,
            raw_text=raw_text,
            finish_reason=choice.get("finish_reason"),
            usage=data.get("usage") or {},
        )


def adapter_from_env() -> VLLMChatAdapter:
    """Construct the default adapter from GovSim-specific environment vars."""

    return VLLMChatAdapter()


def _is_transient_error(reason: Any) -> bool:
    if isinstance(reason, (TimeoutError, RemoteDisconnected)):
        return True
    text = str(reason).lower()
    transient_markers = (
        "temporarily unavailable",
        "timed out",
        "timeout",
        "remote end closed connection",
        "connection reset",
        "connection aborted",
    )
    return any(marker in text for marker in transient_markers)
