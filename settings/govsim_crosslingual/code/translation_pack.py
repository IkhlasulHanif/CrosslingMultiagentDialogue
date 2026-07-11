#!/usr/bin/env python3
"""Validate EN-ID translation packs for the GovSim setting."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "govsim-translation-pack-v1"
DEFAULT_PACK_PATH = Path("config/translations/en_id_fishery_draft.json")
REQUIRED_CATEGORIES = {"rule", "instruction", "resource"}


@dataclass
class TranslationCheck:
    status: str
    message: str
    pack_path: str
    language_pair: str | None = None
    entry_count: int = 0
    categories: list[str] = field(default_factory=list)
    source_coverage_complete: bool | None = None
    human_checked: bool | None = None
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "message": self.message,
            "pack_path": self.pack_path,
            "language_pair": self.language_pair,
            "entry_count": self.entry_count,
            "categories": self.categories,
            "source_coverage_complete": self.source_coverage_complete,
            "human_checked": self.human_checked,
            "missing": self.missing,
            "warnings": self.warnings,
        }


def _read_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"missing translation pack {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"translation pack is invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return {}, ["translation pack must be a JSON object"]
    return data, []


def _entry_text(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    return value.strip() if isinstance(value, str) else ""


def check_translation_pack(root: Path, pack_path: Path = DEFAULT_PACK_PATH) -> TranslationCheck:
    root = root.resolve()
    path = (root / pack_path).resolve() if not pack_path.is_absolute() else pack_path.resolve()
    data, warnings = _read_json(path)

    missing: list[str] = []
    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        missing.append(f"schema_version set to {SCHEMA_VERSION}")

    language_pair = data.get("language_pair")
    if language_pair != "EN-ID":
        missing.append("language_pair set to EN-ID")
        language_pair = language_pair if isinstance(language_pair, str) else None

    source_coverage_complete = data.get("source_coverage_complete")
    if not isinstance(source_coverage_complete, bool):
        missing.append("source_coverage_complete is boolean")
        source_coverage_complete = None

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        missing.append("non-empty entries list")
        entries = []

    ids: set[str] = set()
    categories: set[str] = set()
    human_flags: list[bool] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            missing.append(f"entry {index} is a JSON object")
            continue

        entry_id = _entry_text(entry, "id")
        if not entry_id:
            missing.append(f"entry {index} has non-empty id")
        elif entry_id in ids:
            missing.append(f"duplicate entry id {entry_id}")
        ids.add(entry_id)

        category = _entry_text(entry, "category")
        if not category:
            missing.append(f"entry {entry_id or index} has non-empty category")
        else:
            categories.add(category)

        if not _entry_text(entry, "en"):
            missing.append(f"entry {entry_id or index} has non-empty en text")
        if not _entry_text(entry, "id_text"):
            missing.append(f"entry {entry_id or index} has non-empty id_text translation")

        human_checked = entry.get("human_checked")
        if not isinstance(human_checked, bool):
            missing.append(f"entry {entry_id or index} has boolean human_checked")
        else:
            human_flags.append(human_checked)

    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    for category in missing_categories:
        missing.append(f"at least one {category} entry")

    all_human_checked = bool(human_flags) and all(human_flags)
    if all_human_checked and source_coverage_complete is not True:
        warnings.append("human_checked entries do not imply complete upstream source coverage")

    if missing:
        status = "INVALID"
        message = "Translation pack is structurally invalid."
    elif source_coverage_complete is True and all_human_checked:
        status = "COMPLETE"
        message = "Translation pack covers source prompts and is human checked."
    elif source_coverage_complete is True:
        status = "DRAFT"
        message = "Translation pack covers source prompts but is pending human review."
    else:
        status = "DRAFT"
        message = "Translation pack is structurally valid but pending upstream source coverage and human review."

    return TranslationCheck(
        status=status,
        message=message,
        pack_path=str(path),
        language_pair=language_pair if isinstance(language_pair, str) else None,
        entry_count=len(entries),
        categories=sorted(categories),
        source_coverage_complete=source_coverage_complete if isinstance(source_coverage_complete, bool) else None,
        human_checked=all_human_checked,
        missing=missing,
        warnings=warnings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Setting root to inspect.")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH, help="Translation pack path.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero unless the pack is complete.")
    args = parser.parse_args()

    result = check_translation_pack(args.root, args.pack)
    text = json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        out_path = args.root / args.out if not args.out.is_absolute() else args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    if result.status == "INVALID":
        return 2
    if args.strict and result.status != "COMPLETE":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
