#!/usr/bin/env python3
"""No-network checks for synchronizing GovSim license reports."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from update_license_report import sync_report  # noqa: E402


class UpdateLicenseReportTest(unittest.TestCase):
    def test_blocked_report_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            status = sync_report(root, Path("artifacts/logs/source_license_status.json"), Path("licenses.md"))
            data = json.loads((root / "artifacts/logs/source_license_status.json").read_text(encoding="utf-8"))
            markdown = (root / "licenses.md").read_text(encoding="utf-8")

        self.assertEqual(status, "BLOCKED")
        self.assertEqual(data["status"], "BLOCKED")
        self.assertIn("Status: blocked pending GovSim source/license material.", markdown)
        self.assertIn("missing manifest config/govsim_source.json", markdown)
        self.assertIn("No local file fingerprints are available.", markdown)

    def test_ready_for_review_report_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "vendor" / "govsim"
            source.mkdir(parents=True)
            (source / "LICENSE").write_text("Example license text\n", encoding="utf-8")
            (source / "prompts").mkdir()
            (source / "prompts" / "fishery_rules.md").write_text("Fishery rules\n", encoding="utf-8")
            (root / "config").mkdir()
            (root / "config" / "govsim_source.json").write_text(
                json.dumps(
                    {
                        "upstream_url": "https://github.com/research-lab/govsim",
                        "upstream_license_url": "https://github.com/research-lab/govsim/blob/main/LICENSE",
                        "upstream_license_spdx_id": "MIT",
                        "paper_url": "https://arxiv.org/abs/2404.16698",
                        "upstream_evidence_note": "Repository page reports MIT license.",
                        "source_path": "vendor/govsim",
                        "license_files": ["LICENSE"],
                        "source_prompt_files": ["prompts/fishery_rules.md"],
                        "substrate": "fishery",
                        "fishery_substrate_allowed": True,
                    }
                ),
                encoding="utf-8",
            )

            status = sync_report(root, Path("status.json"), Path("licenses.md"))
            data = json.loads((root / "status.json").read_text(encoding="utf-8"))
            markdown = (root / "licenses.md").read_text(encoding="utf-8")

        self.assertEqual(status, "READY_FOR_REVIEW")
        self.assertEqual(data["missing"], [])
        self.assertEqual(data["license_file_metadata"][0]["bytes"], len("Example license text\n"))
        self.assertEqual(len(data["license_file_metadata"][0]["sha256"]), 64)
        self.assertIn("Status: local source/license evidence recorded.", markdown)
        self.assertIn("`vendor/govsim/LICENSE`", markdown)
        self.assertIn("| Upstream license SPDX | `MIT` |", markdown)
        self.assertIn("Repository page reports MIT license.", markdown)
        self.assertIn("`vendor/govsim/prompts/fishery_rules.md`", markdown)
        self.assertIn("## License File Fingerprints", markdown)
        self.assertIn("## Source Prompt / Rule File Fingerprints", markdown)


if __name__ == "__main__":
    unittest.main(verbosity=2)
