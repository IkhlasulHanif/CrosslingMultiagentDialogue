#!/usr/bin/env python3
"""No-network checks for GovSim translation pack validation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from translation_pack import (  # noqa: E402
    SCHEMA_VERSION,
    TranslationPackNotReady,
    check_translation_pack,
    render_human_review_packet,
    require_complete_translation_pack,
)


class TranslationPackTest(unittest.TestCase):
    def test_setting_draft_pack_is_source_covered_but_not_human_checked(self) -> None:
        result = check_translation_pack(ROOT)

        self.assertEqual(result.status, "DRAFT")
        self.assertEqual(result.missing, [])
        self.assertEqual(result.language_pair, "EN-ID")
        self.assertTrue(result.source_coverage_complete)
        self.assertFalse(result.human_checked)
        self.assertIn("instruction", result.categories)
        self.assertIn("resource", result.categories)
        self.assertIn("rule", result.categories)
        self.assertGreaterEqual(result.entry_count, 12)
        self.assertEqual(result.mechanical_qa["status"], "PASS")
        self.assertEqual(result.mechanical_qa["issue_count"], 0)

    def test_missing_required_category_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pack = root / "pack.json"
            pack.write_text(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "language_pair": "EN-ID",
                        "source_coverage_complete": False,
                        "entries": [
                            {
                                "id": "only.instruction",
                                "category": "instruction",
                                "en": "Choose a harvest.",
                                "id_text": "Pilih jumlah panen.",
                                "human_checked": False,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = check_translation_pack(root, pack)

        self.assertEqual(result.status, "INVALID")
        self.assertIn("at least one resource entry", result.missing)
        self.assertIn("at least one rule entry", result.missing)

    def test_placeholder_and_number_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pack = root / "pack.json"
            entries = [
                {
                    "id": "instruction.bad",
                    "category": "instruction",
                    "en": "Choose between 0 and {num_tons_lake} tons. Answer:",
                    "id_text": "Pilih antara 0 dan 100 ton.",
                    "human_checked": True,
                },
                {
                    "id": "resource.ok",
                    "category": "resource",
                    "en": "There are 100 tons.",
                    "id_text": "Ada 100 ton.",
                    "human_checked": True,
                },
                {
                    "id": "rule.ok",
                    "category": "rule",
                    "en": "Fish double.",
                    "id_text": "Ikan menjadi dua kali lipat.",
                    "human_checked": True,
                },
            ]
            pack.write_text(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "language_pair": "EN-ID",
                        "source_coverage_complete": True,
                        "entries": entries,
                    }
                ),
                encoding="utf-8",
            )

            result = check_translation_pack(root, pack)

        self.assertEqual(result.status, "INVALID")
        self.assertEqual(result.mechanical_qa["status"], "FAIL")
        self.assertIn("instruction.bad: missing placeholders in id_text: {num_tons_lake}", result.missing)
        self.assertIn("instruction.bad: extra numeric tokens in id_text: 100", result.missing)
        self.assertIn("instruction.bad: answer label instruction is not preserved as Answer: or Jawaban:", result.missing)

    def test_complete_pack_requires_source_coverage_and_human_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pack = root / "pack.json"
            entries = [
                {
                    "id": f"{category}.one",
                    "category": category,
                    "en": f"{category} text",
                    "id_text": f"teks {category}",
                    "human_checked": True,
                }
                for category in ("instruction", "resource", "rule")
            ]
            pack.write_text(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "language_pair": "EN-ID",
                        "source_coverage_complete": True,
                        "entries": entries,
                    }
                ),
                encoding="utf-8",
            )

            result = check_translation_pack(root, pack)

        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(result.missing, [])
        self.assertTrue(result.human_checked)

    def test_review_packet_contains_human_gate_and_placeholders(self) -> None:
        packet = render_human_review_packet(ROOT)

        self.assertIn("# GovSim EN-ID Translation Human Review Packet", packet)
        self.assertIn("All entries human checked: `False`", packet)
        self.assertIn("`fishery.task.choose_harvest`", packet)
        self.assertIn("{num_tons_lake}", packet)
        self.assertIn("Review decision: [ ] accept  [ ] edit required", packet)

    def test_indonesian_run_gate_blocks_draft_pack(self) -> None:
        with self.assertRaises(TranslationPackNotReady) as raised:
            require_complete_translation_pack(ROOT, "ID")

        self.assertEqual(raised.exception.check.status, "DRAFT")
        self.assertFalse(raised.exception.check.human_checked)

    def test_english_run_does_not_require_translation_pack(self) -> None:
        self.assertIsNone(require_complete_translation_pack(ROOT, "EN"))

    def test_indonesian_run_gate_accepts_complete_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pack = root / "pack.json"
            entries = [
                {
                    "id": f"{category}.one",
                    "category": category,
                    "en": f"{category} text",
                    "id_text": f"teks {category}",
                    "human_checked": True,
                }
                for category in ("instruction", "resource", "rule")
            ]
            pack.write_text(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "language_pair": "EN-ID",
                        "source_coverage_complete": True,
                        "entries": entries,
                    }
                ),
                encoding="utf-8",
            )

            result = require_complete_translation_pack(root, "ID", pack)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, "COMPLETE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
