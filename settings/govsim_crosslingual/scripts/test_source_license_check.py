#!/usr/bin/env python3
"""No-network checks for GovSim source/license evidence detection."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from source_license_check import check_source_license  # noqa: E402


class SourceLicenseCheckTest(unittest.TestCase):
    def test_missing_manifest_and_source_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_source_license(Path(tmpdir))

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("non-placeholder authoritative upstream_url", result.missing)
        self.assertIn("GovSim source checkout inside this setting", result.missing)
        self.assertIn("missing manifest config/govsim_source.json", result.warnings)

    def test_source_license_manifest_is_ready_for_review(self) -> None:
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

            result = check_source_license(root)

        self.assertEqual(result.status, "READY_FOR_REVIEW")
        self.assertEqual(result.upstream_license_spdx_id, "MIT")
        self.assertEqual(result.paper_url, "https://arxiv.org/abs/2404.16698")
        self.assertIn("MIT license", result.upstream_evidence_note or "")
        self.assertEqual(result.missing, [])
        self.assertEqual(len(result.license_files), 1)
        self.assertEqual(len(result.source_prompt_files), 1)
        self.assertEqual(result.license_file_metadata[0]["bytes"], len("Example license text\n"))
        self.assertEqual(len(result.license_file_metadata[0]["sha256"]), 64)
        self.assertEqual(result.source_prompt_file_metadata[0]["bytes"], len("Fishery rules\n"))

    def test_placeholder_upstream_url_is_blocked_even_with_files(self) -> None:
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
                        "upstream_url": "https://example.org/replace-with-authoritative-govsim-url",
                        "source_path": "vendor/govsim",
                        "license_files": ["LICENSE"],
                        "source_prompt_files": ["prompts/fishery_rules.md"],
                        "substrate": "fishery",
                        "fishery_substrate_allowed": True,
                    }
                ),
                encoding="utf-8",
            )

            result = check_source_license(root)

        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("non-placeholder authoritative upstream_url", result.missing)
        self.assertEqual(len(result.license_file_metadata), 1)

    def test_source_path_outside_setting_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "config").mkdir()
            (root / "config" / "govsim_source.json").write_text(
                json.dumps(
                    {
                        "upstream_url": "https://example.org/govsim",
                        "source_path": "../govsim",
                        "substrate": "fishery",
                        "fishery_substrate_allowed": True,
                    }
                ),
                encoding="utf-8",
            )

            result = check_source_license(root)

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("outside this setting" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
