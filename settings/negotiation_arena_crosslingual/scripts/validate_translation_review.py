#!/usr/bin/env python3
"""Validate the EN-ID human translation review queue."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_UNIT_STATUSES = {"pending", "approved", "revise"}


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def translation_units(translations: dict[str, Any]) -> dict[tuple[str, str], str]:
    units: dict[tuple[str, str], str] = {}
    for unit in translations.get("global_prompt_units", []):
        units[("global", unit.get("id", ""))] = unit.get("kind", "")
    for game in translations.get("games", []):
        context = game.get("game_id", "")
        for unit in game.get("prompt_units", []):
            units[(context, unit.get("id", ""))] = unit.get("kind", "")
    return units


def main() -> int:
    translations = load_json("config/prompt_translations.json")
    review = load_json("config/translation_review.json")

    if review.get("schema_version") != 1:
        return fail("translation_review.json schema_version must be 1")
    if review.get("language_pair") != translations.get("language_pair"):
        return fail("review language_pair must match prompt_translations.json")
    if review.get("source_translation_file") != "config/prompt_translations.json":
        return fail("review source_translation_file must be config/prompt_translations.json")

    expected = translation_units(translations)
    seen: dict[tuple[str, str], str] = {}
    errors: list[str] = []

    for index, item in enumerate(review.get("units", []), start=1):
        key = (item.get("context", ""), item.get("unit_id", ""))
        kind = item.get("kind", "")
        status = item.get("reviewer_status", "")
        if key in seen:
            errors.append(f"duplicate review unit at row {index}: {key[0]}/{key[1]}")
        seen[key] = kind
        if key not in expected:
            errors.append(f"review unit not found in translations: {key[0]}/{key[1]}")
        elif expected[key] != kind:
            errors.append(
                f"kind mismatch for {key[0]}/{key[1]}: review={kind} translations={expected[key]}"
            )
        if status not in ALLOWED_UNIT_STATUSES:
            errors.append(
                f"invalid reviewer_status for {key[0]}/{key[1]}: {status!r}; "
                "use pending, approved, or revise"
            )

    missing = set(expected) - set(seen)
    extra = set(seen) - set(expected)
    if missing:
        errors.append("review queue missing translation units: " + ", ".join(f"{c}/{u}" for c, u in sorted(missing)))
    if extra:
        errors.append("review queue has extra units: " + ", ".join(f"{c}/{u}" for c, u in sorted(extra)))

    reviewer = review.get("reviewer", {})
    completed = reviewer.get("completed")
    unit_statuses = [item.get("reviewer_status") for item in review.get("units", [])]
    if completed is True:
        if not reviewer.get("name") or not reviewer.get("reviewed_at"):
            errors.append("completed review requires reviewer.name and reviewer.reviewed_at")
        if any(status != "approved" for status in unit_statuses):
            errors.append("completed review requires every unit reviewer_status to be approved")
        if review.get("status") != "human_review_complete":
            errors.append("completed review requires status=human_review_complete")
    elif completed is False:
        if review.get("status") != "pending_human_review":
            errors.append("incomplete review requires status=pending_human_review")
    else:
        errors.append("reviewer.completed must be true or false")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if completed:
        print("OK: EN-ID translation human review is complete and all units are approved.")
    else:
        print("OK: EN-ID translation review queue is aligned with prompt translations; human review remains pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
