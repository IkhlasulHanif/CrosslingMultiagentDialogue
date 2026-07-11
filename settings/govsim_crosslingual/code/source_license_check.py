#!/usr/bin/env python3
"""Check whether GovSim source and license evidence exists in this setting."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "govsim-source-license-check-v2"
MANIFEST_PATH = Path("config/govsim_source.json")
SOURCE_CANDIDATES = (
    Path("vendor/govsim"),
    Path("external/govsim"),
    Path("source/govsim"),
    Path("govsim"),
)
LICENSE_NAMES = {
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "COPYING",
    "COPYING.md",
    "NOTICE",
    "NOTICE.md",
}


@dataclass
class CheckResult:
    status: str
    message: str
    root: str
    manifest_path: str
    upstream_url: str | None = None
    upstream_license_url: str | None = None
    upstream_license_spdx_id: str | None = None
    paper_url: str | None = None
    upstream_evidence_note: str | None = None
    source_path: str | None = None
    license_files: list[str] = field(default_factory=list)
    source_prompt_files: list[str] = field(default_factory=list)
    license_file_metadata: list[dict[str, Any]] = field(default_factory=list)
    source_prompt_file_metadata: list[dict[str, Any]] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    substrate: str | None = None
    fishery_substrate_allowed: bool | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "message": self.message,
            "root": self.root,
            "manifest_path": self.manifest_path,
            "upstream_url": self.upstream_url,
            "upstream_license_url": self.upstream_license_url,
            "upstream_license_spdx_id": self.upstream_license_spdx_id,
            "paper_url": self.paper_url,
            "upstream_evidence_note": self.upstream_evidence_note,
            "source_path": self.source_path,
            "license_files": self.license_files,
            "source_prompt_files": self.source_prompt_files,
            "license_file_metadata": self.license_file_metadata,
            "source_prompt_file_metadata": self.source_prompt_file_metadata,
            "missing": self.missing,
            "warnings": self.warnings,
            "substrate": self.substrate,
            "fishery_substrate_allowed": self.fishery_substrate_allowed,
        }


def _read_manifest(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / MANIFEST_PATH
    if not path.exists():
        return {}, [f"missing manifest {MANIFEST_PATH}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"manifest is invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return {}, ["manifest must be a JSON object"]
    return data, []


def _inside_root(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _resolve_source_path(root: Path, manifest: dict[str, Any], warnings: list[str]) -> Path | None:
    raw_source_path = manifest.get("source_path")
    if isinstance(raw_source_path, str) and raw_source_path.strip():
        source_path = root / raw_source_path
        if not _inside_root(root, source_path):
            warnings.append(f"source_path points outside this setting: {raw_source_path}")
            return None
        return source_path

    for candidate in SOURCE_CANDIDATES:
        path = root / candidate
        if path.is_dir():
            return path
    return None


def _manifest_license_paths(root: Path, source_path: Path, manifest: dict[str, Any], warnings: list[str]) -> list[Path]:
    raw_license_files = manifest.get("license_files")
    if raw_license_files is None:
        return []
    if not isinstance(raw_license_files, list):
        warnings.append("license_files must be a list of paths relative to source_path")
        return []

    paths: list[Path] = []
    for item in raw_license_files:
        if not isinstance(item, str) or not item.strip():
            warnings.append("license_files contains a non-string or empty path")
            continue
        candidate = source_path / item
        if not _inside_root(root, candidate):
            warnings.append(f"license file path points outside this setting: {item}")
            continue
        paths.append(candidate)
    return paths


def _manifest_source_prompt_paths(root: Path, source_path: Path, manifest: dict[str, Any], warnings: list[str]) -> list[Path]:
    raw_source_prompt_files = manifest.get("source_prompt_files")
    if raw_source_prompt_files is None:
        return []
    if not isinstance(raw_source_prompt_files, list):
        warnings.append("source_prompt_files must be a list of paths relative to source_path")
        return []

    paths: list[Path] = []
    for item in raw_source_prompt_files:
        if not isinstance(item, str) or not item.strip():
            warnings.append("source_prompt_files contains a non-string or empty path")
            continue
        candidate = source_path / item
        if not _inside_root(root, candidate):
            warnings.append(f"source prompt file path points outside this setting: {item}")
            continue
        paths.append(candidate)
    return paths


def _discover_license_files(source_path: Path) -> list[Path]:
    found: list[Path] = []
    for name in LICENSE_NAMES:
        candidate = source_path / name
        if candidate.is_file():
            found.append(candidate)
    return sorted(found)


def _existing_nonempty_files(paths: list[Path]) -> list[Path]:
    existing: list[Path] = []
    for path in paths:
        if path.is_file() and path.stat().st_size > 0:
            existing.append(path)
    return existing


def _file_metadata(paths: list[Path]) -> list[dict[str, Any]]:
    metadata: list[dict[str, Any]] = []
    for path in paths:
        content = path.read_bytes()
        metadata.append(
            {
                "path": str(path),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return metadata


def _is_placeholder_upstream_url(value: str | None) -> bool:
    if value is None:
        return True
    stripped = value.strip()
    if not stripped:
        return True

    parsed = urlparse(stripped)
    host = parsed.netloc.lower()
    lowered = stripped.lower()
    if parsed.scheme not in {"http", "https", "ssh", "git"}:
        return True
    if host in {"example.com", "example.org", "example.net"}:
        return True
    return any(token in lowered for token in ("replace-with", "placeholder", "todo", "tbd"))


def _optional_string_manifest_value(manifest: dict[str, Any], key: str, warnings: list[str]) -> str | None:
    value = manifest.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        warnings.append(f"{key} must be a string")
        return None
    stripped = value.strip()
    return stripped or None


def check_source_license(root: Path) -> CheckResult:
    root = root.resolve()
    manifest, warnings = _read_manifest(root)
    upstream_url = manifest.get("upstream_url")
    if upstream_url is not None and not isinstance(upstream_url, str):
        warnings.append("upstream_url must be a string")
        upstream_url = None
    upstream_license_url = _optional_string_manifest_value(manifest, "upstream_license_url", warnings)
    upstream_license_spdx_id = _optional_string_manifest_value(manifest, "upstream_license_spdx_id", warnings)
    paper_url = _optional_string_manifest_value(manifest, "paper_url", warnings)
    upstream_evidence_note = _optional_string_manifest_value(manifest, "upstream_evidence_note", warnings)

    source_path = _resolve_source_path(root, manifest, warnings)
    license_files: list[Path] = []
    source_prompt_files: list[Path] = []
    if source_path is not None:
        license_files = _existing_nonempty_files(
            _manifest_license_paths(root, source_path, manifest, warnings)
            or _discover_license_files(source_path)
        )
        source_prompt_files = _existing_nonempty_files(
            _manifest_source_prompt_paths(root, source_path, manifest, warnings)
        )

    substrate = manifest.get("substrate")
    if substrate is not None and not isinstance(substrate, str):
        warnings.append("substrate must be a string")
        substrate = None

    fishery_allowed = manifest.get("fishery_substrate_allowed")
    if fishery_allowed is not None and not isinstance(fishery_allowed, bool):
        warnings.append("fishery_substrate_allowed must be true, false, or null")
        fishery_allowed = None

    missing: list[str] = []
    if not isinstance(upstream_url, str) or _is_placeholder_upstream_url(upstream_url):
        missing.append("non-placeholder authoritative upstream_url")
    if source_path is None or not source_path.is_dir():
        missing.append("GovSim source checkout inside this setting")
    if not license_files:
        missing.append("non-empty license file under the GovSim source checkout")
    if not source_prompt_files:
        missing.append("non-empty fishery source prompt/rule/resource files listed in source_prompt_files")
    if substrate != "fishery":
        missing.append("manifest substrate set to fishery")
    if fishery_allowed is not True:
        missing.append("human confirmation that fishery_substrate_allowed is true")

    status = "READY_FOR_REVIEW" if not missing else "BLOCKED"
    message = (
        "GovSim source/license evidence is present and ready for human review."
        if status == "READY_FOR_REVIEW"
        else "GovSim license verification remains blocked by missing source/license evidence."
    )
    return CheckResult(
        status=status,
        message=message,
        root=str(root),
        manifest_path=str(root / MANIFEST_PATH),
        upstream_url=upstream_url.strip() if isinstance(upstream_url, str) and upstream_url.strip() else None,
        upstream_license_url=upstream_license_url,
        upstream_license_spdx_id=upstream_license_spdx_id,
        paper_url=paper_url,
        upstream_evidence_note=upstream_evidence_note,
        source_path=str(source_path) if source_path is not None else None,
        license_files=[str(path) for path in license_files],
        source_prompt_files=[str(path) for path in source_prompt_files],
        license_file_metadata=_file_metadata(license_files),
        source_prompt_file_metadata=_file_metadata(source_prompt_files),
        missing=missing,
        warnings=warnings,
        substrate=substrate,
        fishery_substrate_allowed=fishery_allowed,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Setting root to inspect.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    result = check_source_license(args.root)
    data = result.as_dict()
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result.status == "READY_FOR_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
