#!/usr/bin/env python3
"""Validate EN-ID translation packs for the GovSim setting."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "govsim-translation-pack-v1"
DEFAULT_PACK_PATH = Path("config/translations/en_id_fishery_draft.json")
REQUIRED_CATEGORIES = {"rule", "instruction", "resource"}
PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
NUMBER_RE = re.compile(r"(?<![\w.-])-?\d+(?:\.\d+)?(?![\w.-])")


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
    mechanical_qa: dict[str, Any] = field(default_factory=dict)

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
            "mechanical_qa": self.mechanical_qa,
        }


class TranslationPackNotReady(RuntimeError):
    """Raised when a benchmark run requires reviewed translations."""

    def __init__(self, check: TranslationCheck) -> None:
        self.check = check
        super().__init__(
            "ID translation pack is not ready for benchmark use: "
            f"status={check.status}, source_coverage_complete={check.source_coverage_complete}, "
            f"human_checked={check.human_checked}, pack={check.pack_path}"
        )


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


def _tokens(pattern: re.Pattern[str], text: str) -> Counter[str]:
    return Counter(pattern.findall(text))


def _counter_delta(left: Counter[str], right: Counter[str]) -> list[str]:
    delta: list[str] = []
    for token, count in sorted((left - right).items()):
        delta.extend([token] * count)
    return delta


def _entry_mechanical_qa(entry: dict[str, Any]) -> dict[str, Any]:
    entry_id = _entry_text(entry, "id") or "<missing-id>"
    en = _entry_text(entry, "en")
    id_text = _entry_text(entry, "id_text")
    en_placeholders = _tokens(PLACEHOLDER_RE, en)
    id_placeholders = _tokens(PLACEHOLDER_RE, id_text)
    en_numbers = _tokens(NUMBER_RE, en)
    id_numbers = _tokens(NUMBER_RE, id_text)
    issues: list[str] = []

    missing_placeholders = _counter_delta(en_placeholders, id_placeholders)
    extra_placeholders = _counter_delta(id_placeholders, en_placeholders)
    if missing_placeholders:
        issues.append(f"{entry_id}: missing placeholders in id_text: {', '.join(missing_placeholders)}")
    if extra_placeholders:
        issues.append(f"{entry_id}: extra placeholders in id_text: {', '.join(extra_placeholders)}")

    missing_numbers = _counter_delta(en_numbers, id_numbers)
    extra_numbers = _counter_delta(id_numbers, en_numbers)
    if missing_numbers:
        issues.append(f"{entry_id}: missing numeric tokens in id_text: {', '.join(missing_numbers)}")
    if extra_numbers:
        issues.append(f"{entry_id}: extra numeric tokens in id_text: {', '.join(extra_numbers)}")

    if "Answer:" in en and not any(label in id_text for label in ("Answer:", "Jawaban:")):
        issues.append(f"{entry_id}: answer label instruction is not preserved as Answer: or Jawaban:")

    return {
        "entry_id": entry_id,
        "placeholder_count": sum(en_placeholders.values()),
        "numeric_token_count": sum(en_numbers.values()),
        "issues": issues,
    }


def _mechanical_qa(entries: list[Any], root: Path) -> dict[str, Any]:
    checked_entries = 0
    issue_list: list[str] = []
    missing_source_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        checked_entries += 1
        qa = _entry_mechanical_qa(entry)
        issue_list.extend(qa["issues"])

        source = _entry_text(entry, "source")
        source_path_text = source.split(":", 1)[0]
        if source_path_text and not (root / source_path_text).exists():
            missing_source_paths.append(source_path_text)

    return {
        "status": "PASS" if not issue_list else "FAIL",
        "checked_entries": checked_entries,
        "issue_count": len(issue_list),
        "issues": issue_list,
        "missing_source_paths": sorted(set(missing_source_paths)),
    }


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

    mechanical_qa = _mechanical_qa(entries, root)
    missing.extend(mechanical_qa["issues"])
    for source_path in mechanical_qa["missing_source_paths"]:
        warnings.append(f"entry source path is not present locally: {source_path}")

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
        mechanical_qa=mechanical_qa,
    )


def require_complete_translation_pack(
    root: Path,
    language: str,
    pack_path: Path = DEFAULT_PACK_PATH,
) -> TranslationCheck | None:
    """Require reviewed translations for Indonesian benchmark prompts.

    English prompts come directly from upstream GovSim and do not use this pack.
    Indonesian C1/C2/C3 runs must not proceed while the pack is still draft.
    """

    if language.strip().upper() != "ID":
        return None
    check = check_translation_pack(root, pack_path)
    if check.status != "COMPLETE":
        raise TranslationPackNotReady(check)
    return check


def render_human_review_packet(root: Path, pack_path: Path = DEFAULT_PACK_PATH) -> str:
    """Render a human-facing EN-ID translation review packet."""

    root = root.resolve()
    path = (root / pack_path).resolve() if not pack_path.is_absolute() else pack_path.resolve()
    data, warnings = _read_json(path)
    check = check_translation_pack(root, pack_path)
    entries = data.get("entries")
    if not isinstance(entries, list):
        entries = []

    lines = [
        "# GovSim EN-ID Translation Human Review Packet",
        "",
        "This packet is for human review of the active GovSim fishery translation pack.",
        "Do not mark `goals.md` human-check complete until every active entry is reviewed and the JSON pack has `human_checked: true` for each accepted entry.",
        "",
        "## Review Status",
        "",
        f"- Pack: `{path.relative_to(root) if path.is_relative_to(root) else path}`",
        f"- Status: `{check.status}`",
        f"- Language pair: `{check.language_pair}`",
        f"- Entries: {check.entry_count}",
        f"- Source coverage complete: `{check.source_coverage_complete}`",
        f"- All entries human checked: `{check.human_checked}`",
        f"- Mechanical QA: `{check.mechanical_qa.get('status')}` ({check.mechanical_qa.get('issue_count')} issue(s))",
        "",
        "## Reviewer Instructions",
        "",
        "For each entry, compare the English source text with the Indonesian translation.",
        "Check that quantities, constraints, role labels, answer-format requirements, and placeholders such as `{num_tons_lake}` are preserved exactly.",
        "If an entry is acceptable, set its `human_checked` field to `true` in the JSON pack.",
        "If an entry needs changes, edit `id_text`, keep the same placeholders, then set `human_checked` to `true` after review.",
        "",
        "## Entries",
        "",
    ]
    if check.missing:
        lines.extend(["## Structural Issues", ""])
        lines.extend(f"- {item}" for item in check.missing)
        lines.append("")
    if warnings or check.warnings:
        lines.extend(["## Warnings", ""])
        for item in [*warnings, *check.warnings]:
            lines.append(f"- {item}")
        lines.append("")
    if check.mechanical_qa.get("issues"):
        lines.extend(["## Mechanical QA Issues", ""])
        lines.extend(f"- {item}" for item in check.mechanical_qa["issues"])
        lines.append("")

    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            lines.extend([f"### {index}. Invalid Entry", "", "Entry is not a JSON object.", ""])
            continue
        entry_id = _entry_text(entry, "id") or f"entry_{index}"
        category = _entry_text(entry, "category") or "unknown"
        source = _entry_text(entry, "source") or "unknown"
        human_checked = entry.get("human_checked")
        lines.extend(
            [
                f"### {index}. `{entry_id}`",
                "",
                f"- Category: `{category}`",
                f"- Source: `{source}`",
                f"- Human checked: `{human_checked}`",
                "",
                "**EN**",
                "",
                "```text",
                _entry_text(entry, "en"),
                "```",
                "",
                "**ID**",
                "",
                "```text",
                _entry_text(entry, "id_text"),
                "```",
                "",
                "- Review decision: [ ] accept  [ ] edit required",
                "- Reviewer note:",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_human_review_manifest(root: Path, pack_path: Path = DEFAULT_PACK_PATH) -> dict[str, Any]:
    """Render machine-readable evidence for the translation human-review gate."""

    root = root.resolve()
    path = (root / pack_path).resolve() if not pack_path.is_absolute() else pack_path.resolve()
    data, warnings = _read_json(path)
    check = check_translation_pack(root, pack_path)
    entries = data.get("entries")
    if not isinstance(entries, list):
        entries = []

    unchecked_entry_ids: list[str] = []
    checked_entry_ids: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            unchecked_entry_ids.append(f"<invalid-entry-{index}>")
            continue
        entry_id = _entry_text(entry, "id") or f"<missing-id-{index}>"
        if entry.get("human_checked") is True:
            checked_entry_ids.append(entry_id)
        else:
            unchecked_entry_ids.append(entry_id)

    pack_bytes = path.read_bytes() if path.exists() else b""
    packet_text = render_human_review_packet(root, pack_path)
    packet_sha256 = hashlib.sha256(packet_text.encode("utf-8")).hexdigest()

    return {
        "schema_version": "govsim-translation-review-manifest-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pack_path": str(path.relative_to(root) if path.is_relative_to(root) else path),
        "pack_sha256": hashlib.sha256(pack_bytes).hexdigest(),
        "review_packet_path": "artifacts/logs/translation_human_review_packet.md",
        "review_packet_sha256": packet_sha256,
        "status": check.status,
        "language_pair": check.language_pair,
        "entry_count": check.entry_count,
        "checked_entry_count": len(checked_entry_ids),
        "unchecked_entry_count": len(unchecked_entry_ids),
        "checked_entry_ids": checked_entry_ids,
        "unchecked_entry_ids": unchecked_entry_ids,
        "source_coverage_complete": check.source_coverage_complete,
        "all_entries_human_checked": check.human_checked,
        "mechanical_qa": check.mechanical_qa,
        "missing": check.missing,
        "warnings": [*warnings, *check.warnings],
        "next_unblock_command": (
            "python3 code/translation_pack.py --root . "
            "--out artifacts/logs/translation_status.json "
            "--review-out artifacts/logs/translation_human_review_packet.md "
            "--review-manifest-out artifacts/logs/translation_human_review_manifest.json --strict"
        ),
        "review_rule": (
            "C1/C2/C3 Indonesian runs remain blocked until every active entry has "
            "human_checked=true after human review and strict validation returns 0."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Setting root to inspect.")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH, help="Translation pack path.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--review-out", type=Path, help="Optional Markdown human review packet path.")
    parser.add_argument("--review-manifest-out", type=Path, help="Optional JSON human review manifest path.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero unless the pack is complete.")
    args = parser.parse_args()

    result = check_translation_pack(args.root, args.pack)
    text = json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        out_path = args.root / args.out if not args.out.is_absolute() else args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
    if args.review_out:
        review_path = args.root / args.review_out if not args.review_out.is_absolute() else args.review_out
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(render_human_review_packet(args.root, args.pack), encoding="utf-8")
    if args.review_manifest_out:
        manifest_path = (
            args.root / args.review_manifest_out if not args.review_manifest_out.is_absolute() else args.review_manifest_out
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = render_human_review_manifest(args.root, args.pack)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(text)
    if result.status == "INVALID":
        return 2
    if args.strict and result.status != "COMPLETE":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
