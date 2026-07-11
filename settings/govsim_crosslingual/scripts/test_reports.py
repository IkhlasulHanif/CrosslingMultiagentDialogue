#!/usr/bin/env python3
"""No-network checks for human-readable report consistency."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class ReportConsistencyTest(unittest.TestCase):
    def test_status_excerpt_is_self_contained(self) -> None:
        findings = (ROOT / "reports" / "findings.md").read_text(encoding="utf-8").strip()
        status = (ROOT / "reports" / "status.md").read_text(encoding="utf-8")
        excerpt = "\n".join(findings.splitlines()[:12])

        self.assertIn("One C0 OpenAI smoke episode has run.", excerpt)
        self.assertIn("not Qwen3-1.7B research-matrix evidence", excerpt)
        self.assertIn("Current blockers:", findings)
        self.assertNotIn("It currently reports\n", excerpt)
        self.assertIn("Qwen3-1.7B", status)
        self.assertNotIn("It currently reports\n\nNext useful work", status)

    def test_report_matches_current_gate_artifacts(self) -> None:
        license_status = _read_json(ROOT / "artifacts" / "logs" / "source_license_status.json")
        translation_status = _read_json(ROOT / "artifacts" / "logs" / "translation_status.json")
        findings = (ROOT / "reports" / "findings.md").read_text(encoding="utf-8")

        self.assertEqual(license_status["status"], "READY_FOR_REVIEW")
        self.assertEqual(translation_status["status"], "DRAFT")
        self.assertTrue(translation_status["source_coverage_complete"])
        self.assertIn("`READY_FOR_REVIEW`", findings)
        self.assertIn("`DRAFT`", findings)
        self.assertIn("One C0 OpenAI smoke episode has run.", findings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
