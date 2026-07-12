#!/usr/bin/env python3
"""No-network checks for pairwise channel-run wrapper coverage."""

from __future__ import annotations

import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PairwiseChannelPlanTest(unittest.TestCase):
    def test_ladder_pair_openai_wrappers_are_pinned(self) -> None:
        expected = {
            "scripts/run_openai_en_zh_c0_baseline.sh": (
                "GOVSIM_LANGUAGE_PAIR=EN-ZH",
                "GOVSIM_CONDITION=C0",
                "GOVSIM_LANGUAGE=EN",
            ),
            "scripts/run_openai_en_zh_c1_baseline.sh": (
                "GOVSIM_LANGUAGE_PAIR=EN-ZH",
                "GOVSIM_CONDITION=C1",
                "GOVSIM_LANGUAGE=ZH",
            ),
            "scripts/run_openai_zh_id_c0_baseline.sh": (
                "GOVSIM_LANGUAGE_PAIR=ZH-ID",
                "GOVSIM_CONDITION=C0",
                "GOVSIM_LANGUAGE=ZH",
            ),
            "scripts/run_openai_zh_id_c1_baseline.sh": (
                "GOVSIM_LANGUAGE_PAIR=ZH-ID",
                "GOVSIM_CONDITION=C1",
                "GOVSIM_LANGUAGE=ID",
            ),
            "scripts/run_openai_en_id_c3_free_choice.sh": (
                "GOVSIM_LANGUAGE_PAIR=EN-ID",
                "scripts/govsim_openai_c3.py",
            ),
        }
        for rel_path, snippets in expected.items():
            path = ROOT / rel_path
            self.assertTrue(path.exists(), rel_path)
            self.assertTrue(os.access(path, os.X_OK), rel_path)
            text = path.read_text(encoding="utf-8")
            if rel_path.endswith("_c3_free_choice.sh"):
                self.assertIn("scripts/govsim_openai_c3.py", text)
            else:
                self.assertIn("scripts/govsim_openai_baseline.py", text)
            for snippet in snippets:
                self.assertIn(snippet, text)

    def test_plan_lists_active_ladder_commands(self) -> None:
        plan = (ROOT / "plan" / "channel_run_plan.md").read_text(encoding="utf-8")
        for command in (
            "./scripts/run_openai_en_zh_c0_baseline.sh",
            "./scripts/run_openai_en_zh_c1_baseline.sh",
            "./scripts/run_openai_zh_id_c0_baseline.sh",
            "./scripts/run_openai_zh_id_c1_baseline.sh",
            "./scripts/run_openai_en_id_c3_free_choice.sh",
        ):
            self.assertIn(command, plan)


if __name__ == "__main__":
    unittest.main(verbosity=2)
