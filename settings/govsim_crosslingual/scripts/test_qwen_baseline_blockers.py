#!/usr/bin/env python3
"""No-network checks for GovSim Qwen baseline blocker artifacts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "scripts"))

from govsim_qwen_c0_baseline import blocked_event_message, blocked_result  # noqa: E402
from local_model_adapter import LocalModelError, VLLMChatAdapter  # noqa: E402
from translation_pack import TranslationPackNotReady, check_translation_pack  # noqa: E402


class QwenBaselineBlockerTest(unittest.TestCase):
    def test_translation_gate_blocker_is_before_model_call(self) -> None:
        adapter = VLLMChatAdapter(base_url="http://127.0.0.1:8000/v1", model="Qwen3-1.7B")
        exc = TranslationPackNotReady(check_translation_pack(ROOT))
        artifact_path = ROOT / "artifacts" / "results" / "example.json"

        result = blocked_result(exc, adapter, "C1", "ID")
        message = blocked_event_message(exc, adapter, "C1", artifact_path)

        self.assertEqual(result["blocked_stage"], "translation_review_gate")
        self.assertFalse(result["model_call_attempted"])
        self.assertIn("translation_gate", result)
        self.assertIn("blocked before model call by translation gate", message)
        self.assertNotIn("blocked at http://127.0.0.1:8000", message)

    def test_endpoint_blocker_records_model_call_attempt(self) -> None:
        adapter = VLLMChatAdapter(base_url="http://127.0.0.1:8000/v1", model="Qwen3-1.7B")
        exc = LocalModelError("Local model endpoint unavailable")
        artifact_path = ROOT / "artifacts" / "results" / "example.json"

        result = blocked_result(exc, adapter, "C0", "EN")
        message = blocked_event_message(exc, adapter, "C0", artifact_path)

        self.assertEqual(result["blocked_stage"], "model_or_runner")
        self.assertTrue(result["model_call_attempted"])
        self.assertIn("blocked at http://127.0.0.1:8000/v1/chat/completions", message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
