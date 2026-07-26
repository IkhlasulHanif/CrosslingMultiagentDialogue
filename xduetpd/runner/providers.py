from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .constants import LETTERS


@dataclass
class ModelReply:
    text: str
    top_logprobs: dict[str, float] | None = None
    cost_usd: float = 0.0


class Provider:
    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_logprobs: bool = False,
        seed: int | None = None,
    ) -> ModelReply:
        raise NotImplementedError


class MockProvider(Provider):
    """Deterministic model for schema smoke tests only."""

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_logprobs: bool = False,
        seed: int | None = None,
    ) -> ModelReply:
        text = "\n".join(message["content"] for message in messages)
        rng = random.Random(seed)
        if "option letter only" in text.lower():
            letter = _extract_marker(text, "CURRENT_ANSWER") or _extract_marker(text, "GOLD") or "A"
            if temperature >= 1.0 and rng.random() < 0.25:
                letter = rng.choice(list(LETTERS))
            return ModelReply(letter, _mock_logprobs(letter) if top_logprobs else None)
        if "number from 0 to 100" in text.lower():
            return ModelReply(str(72 + rng.randint(-4, 4)))
        if "Your goal: convince them" in text:
            advocated = _extract_marker(text, "ADVOCATED") or _extract_advocated(text) or "B"
            return ModelReply(
                "The evidence points more strongly to option "
                f"{advocated}. A careful reading supports that answer."
            )
        gold = _extract_marker(text, "GOLD") or "A"
        advocated = _extract_marker(text, "ADVOCATED") or "B"
        turn = _extract_marker(text, "TURN")
        direction = _extract_marker(text, "DIRECTION") or "misleading"
        committed = gold
        if direction == "misleading" and turn and turn.isdigit() and int(turn) >= 3:
            committed = advocated
        body = "I will answer based on the options and the strongest available clue."
        if committed != gold:
            body = "I am persuaded by the latest argument and will update my answer."
        return ModelReply(f"{body}\nANSWER: {committed}")


class OpenAIHTTPProvider(Provider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com").rstrip("/")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for XDUETPD_PROVIDER=openai")

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_logprobs: bool = False,
        seed: int | None = None,
    ) -> ModelReply:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if seed is not None:
            payload["seed"] = seed
        if top_logprobs:
            payload["logprobs"] = True
            payload["top_logprobs"] = 20
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI HTTP {exc.code}: {body}") from exc
        choice = data["choices"][0]
        content = choice["message"].get("content") or ""
        logprobs = _parse_letter_top_logprobs(choice.get("logprobs")) if top_logprobs else None
        usage = data.get("usage") or {}
        cost = float(usage.get("total_tokens", 0)) * 0.0
        _ = started
        return ModelReply(content, logprobs, cost)


def build_provider(name: str | None = None) -> Provider:
    provider = (name or os.environ.get("XDUETPD_PROVIDER") or "mock").lower()
    if provider == "mock":
        return MockProvider()
    if provider == "openai":
        return OpenAIHTTPProvider()
    raise ValueError(f"unsupported provider for this goals.md: {provider}")


def _extract_marker(text: str, marker: str) -> str | None:
    prefix = marker + ":"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _extract_advocated(text: str) -> str | None:
    marker = "answer is "
    idx = text.find(marker)
    if idx == -1:
        return None
    letter = text[idx + len(marker) : idx + len(marker) + 1].upper()
    return letter if letter in LETTERS else None


def _mock_logprobs(letter: str) -> dict[str, float]:
    return {candidate: (-0.05 if candidate == letter else -4.0) for candidate in LETTERS}


def _parse_letter_top_logprobs(raw: Any) -> dict[str, float] | None:
    if not raw:
        return None
    try:
        token_logprobs = raw["content"][0]["top_logprobs"]
    except (KeyError, IndexError, TypeError):
        return None
    out = {letter: -1000.0 for letter in LETTERS}
    for item in token_logprobs:
        token = str(item.get("token", "")).strip().upper()
        if token in out:
            out[token] = float(item.get("logprob", -1000.0))
    if all(value == -1000.0 for value in out.values()):
        return None
    return out
