#!/usr/bin/env python3
"""No-network checks for GovSim process language metrics."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from process_metrics import message_metrics, summarize_records  # noqa: E402


class ProcessMetricsTest(unittest.TestCase):
    def test_message_metrics_detects_code_switch_and_off_pair_text(self) -> None:
        metrics = message_metrics(
            {
                "event_type": "model_message",
                "round_index": 1,
                "agent_id": "agent_2",
                "language": "ID",
                "visible_text": "Kita should harvest ikan مرحبا",
            }
        )

        self.assertEqual(metrics["language_token_counts"]["ID"], 2)
        self.assertEqual(metrics["language_token_counts"]["EN"], 2)
        self.assertTrue(metrics["code_switch"])
        self.assertEqual(metrics["code_switch_points"], 2)
        self.assertEqual(metrics["off_pair_scripts"]["AR"], 1)
        self.assertIsNone(metrics["dominant_language"])
        self.assertFalse(metrics["channel_compliant"])

    def test_zh_is_pair_language_when_configured(self) -> None:
        metrics = message_metrics(
            {
                "event_type": "model_message",
                "round_index": 1,
                "agent_id": "agent_3",
                "language": "ZH",
                "visible_text": "我们应该合作捕鱼，保护鱼和资源",
            },
            pair_languages=("EN", "ZH"),
        )

        self.assertGreater(metrics["language_token_counts"]["ZH"], 0)
        self.assertEqual(metrics["off_pair_token_count"], 0)
        self.assertTrue(metrics["channel_compliant"])

    def test_hebrew_script_counts_as_off_pair_text(self) -> None:
        metrics = message_metrics(
            {
                "event_type": "model_message",
                "round_index": 0,
                "agent_id": "framework",
                "language": "ID",
                "visible_text": "kita jaga stok ikan untuk כולם",
            }
        )

        self.assertEqual(metrics["off_pair_scripts"]["HE"], 1)
        self.assertEqual(metrics["off_pair_token_count"], 1)
        self.assertTrue(metrics["channel_compliant"])

    def test_summary_reports_language_share_and_convergence_delta(self) -> None:
        records = [
            {
                "event_type": "model_message",
                "round_index": 0,
                "agent_id": "agent_a",
                "language": "EN",
                "visible_text": "we should harvest fish and protect stock",
            },
            {
                "event_type": "model_message",
                "round_index": 0,
                "agent_id": "agent_b",
                "language": "ID",
                "visible_text": "kita harus panen ikan dan jaga stok",
            },
            {
                "event_type": "model_message",
                "round_index": 1,
                "agent_id": "agent_a",
                "language": "EN",
                "visible_text": "kita should ikan harvest",
            },
            {
                "event_type": "model_message",
                "round_index": 1,
                "agent_id": "agent_b",
                "language": "ID",
                "visible_text": "kita should ikan harvest",
            },
        ]

        summary = summarize_records(records)

        self.assertEqual(summary["message_count"], 4)
        self.assertGreater(summary["language_share"]["EN"], 0.0)
        self.assertGreater(summary["language_share"]["ID"], 0.0)
        self.assertEqual(summary["code_switch_message_count"], 2)
        self.assertEqual(summary["convergence"]["agents_compared"], ["agent_a", "agent_b"])
        self.assertGreater(summary["convergence"]["convergence_delta"], 0.0)

    def test_cli_writes_summary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript = Path(tmpdir) / "sample.jsonl"
            out = Path(tmpdir) / "summary.json"
            transcript.write_text(
                json.dumps(
                    {
                        "event_type": "model_message",
                        "round_index": 0,
                        "agent_id": "agent_a",
                        "visible_text": "we harvest fish",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [sys.executable, str(ROOT / "code" / "process_metrics.py"), str(transcript), "--out", str(out)],
                check=True,
                cwd=ROOT,
            )

            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], "govsim-process-metrics-v2")
            self.assertEqual(data["message_count"], 1)
            self.assertEqual(data["source_path"], str(transcript))


if __name__ == "__main__":
    unittest.main(verbosity=2)
