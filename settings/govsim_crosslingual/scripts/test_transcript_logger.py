#!/usr/bin/env python3
"""No-network checks for GovSim transcript logging."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from local_model_adapter import ModelResponse  # noqa: E402
from transcript_logger import TranscriptContext, TranscriptWriter, read_transcript  # noqa: E402


class TranscriptLoggerTest(unittest.TestCase):
    def test_log_text_strips_thinking_from_visible_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TranscriptWriter.for_run(
                Path(tmpdir),
                TranscriptContext(
                    run_id="smoke/c0 seed 1",
                    condition="C0",
                    episode_id="episode-001",
                    seed=1,
                ),
            )

            record = writer.log_text(
                round_index=0,
                phase="harvest",
                agent_id="agent_0",
                role="assistant",
                raw_text="<think>private calculation</think>\nHarvest: 2",
                language="EN",
            )

            self.assertEqual(record["visible_text"], "Harvest: 2")
            self.assertEqual(record["thinking"], ["private calculation"])
            self.assertNotIn("<think>", record["visible_text"])
            self.assertIn("raw_text_sha256", record)
            self.assertIn("event_hash", record)
            self.assertEqual(writer.path.name, "smoke_c0_seed_1.jsonl")

            rows = read_transcript(writer.path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["condition"], "C0")
            self.assertEqual(rows[0]["episode_id"], "episode-001")

    def test_log_model_response_preserves_adapter_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TranscriptWriter.for_run(
                Path(tmpdir),
                TranscriptContext(run_id="c2-balanced", condition="C2", language_pair="EN-ID"),
            )
            response = ModelResponse(
                model="Qwen3-1.7B",
                visible_text="Panen: 1",
                thinking=["hidden ID reasoning"],
                raw_text="<think>hidden ID reasoning</think>\nPanen: 1",
                finish_reason="stop",
                usage={"prompt_tokens": 12, "completion_tokens": 8},
            )

            record = writer.log_model_response(
                round_index=3,
                phase="harvest",
                agent_id="agent_4",
                role="assistant",
                response=response,
                language="ID",
                prompt_messages=[{"role": "user", "content": "Pilih panen."}],
            )

            self.assertEqual(record["visible_text"], "Panen: 1")
            self.assertEqual(record["thinking"], ["hidden ID reasoning"])
            self.assertEqual(record["model"], "Qwen3-1.7B")
            self.assertEqual(record["finish_reason"], "stop")
            self.assertEqual(record["usage"]["completion_tokens"], 8)
            self.assertEqual(record["prompt_messages"][0]["content"], "Pilih panen.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
