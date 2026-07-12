#!/usr/bin/env python3
"""No-network checks for the GovSim local model adapter."""

from __future__ import annotations

import json
from http.client import RemoteDisconnected
import sys
import unittest
from pathlib import Path
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from local_model_adapter import ChatMessage, VLLMChatAdapter, strip_think_blocks  # noqa: E402


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class FakeOpener:
    def __init__(self, response_payload: dict) -> None:
        self.response_payload = response_payload
        self.last_request: Request | None = None
        self.last_timeout: float | None = None

    def open(self, request: Request, timeout: float) -> FakeResponse:
        self.last_request = request
        self.last_timeout = timeout
        return FakeResponse(self.response_payload)


class FlakyOpener:
    def __init__(self, response_payload: dict) -> None:
        self.response_payload = response_payload
        self.calls = 0

    def open(self, request: Request, timeout: float) -> FakeResponse:
        self.calls += 1
        if self.calls == 1:
            raise RemoteDisconnected("Remote end closed connection without response")
        return FakeResponse(self.response_payload)


class LocalModelAdapterTest(unittest.TestCase):
    def test_strip_think_blocks(self) -> None:
        visible, thinking = strip_think_blocks("A\n<think>hidden note</think>\nB")
        self.assertEqual(visible, "A\n\nB")
        self.assertEqual(thinking, ["hidden note"])

    def test_complete_posts_openai_compatible_payload(self) -> None:
        opener = FakeOpener(
            {
                "model": "Qwen3-1.7B",
                "choices": [
                    {
                        "message": {
                            "content": "<think>choose small harvest</think>\nHarvest: 2"
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            }
        )
        adapter = VLLMChatAdapter(
            base_url="http://localhost:8000/v1",
            model="Qwen3-1.7B",
            timeout_s=3,
            opener=opener,
        )

        result = adapter.complete(
            [
                ChatMessage("system", "You are a fishery agent."),
                {"role": "user", "content": "Choose harvest."},
            ],
            temperature=0.0,
            max_tokens=32,
        )

        self.assertEqual(result.visible_text, "Harvest: 2")
        self.assertEqual(result.thinking, ["choose small harvest"])
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(opener.last_timeout, 3)
        self.assertIsNotNone(opener.last_request)
        assert opener.last_request is not None
        self.assertEqual(opener.last_request.full_url, "http://localhost:8000/v1/chat/completions")
        payload = json.loads(opener.last_request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "Qwen3-1.7B")
        self.assertEqual(payload["messages"][1]["content"], "Choose harvest.")
        self.assertEqual(payload["max_tokens"], 32)

    def test_complete_retries_transient_remote_disconnect(self) -> None:
        opener = FlakyOpener(
            {
                "model": "gpt-5.4-mini-2026-03-17",
                "choices": [{"message": {"content": "Answer: 10"}, "finish_reason": "stop"}],
                "usage": {},
            }
        )
        adapter = VLLMChatAdapter(
            base_url="https://api.openai.com/v1",
            model="gpt-5.4-mini-2026-03-17",
            opener=opener,
            max_retries=1,
            retry_sleep_s=0,
        )

        result = adapter.complete([{"role": "user", "content": "Choose harvest."}])

        self.assertEqual(result.visible_text, "Answer: 10")
        self.assertEqual(opener.calls, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
