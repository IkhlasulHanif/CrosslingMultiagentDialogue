#!/usr/bin/env python3
"""Validate the EN-ID human translation review queue."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_UNIT_STATUSES = {"pending", "approved", "revise"}
ARTIFACT = "artifacts/results/translation_review_validation.json"
COMMAND = "python3 scripts/validate_translation_review.py"
NEXT_COMMAND = "bash scripts/run_c1_baseline.sh"


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(relative_path: str, payload: dict[str, Any]) -> Path:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_event(kind: str, status: str, message: str) -> None:
    path = ROOT / "plan" / "events.jsonl"
    record = {"ts": utc_now(), "kind": kind, "status": status, "message": message}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def translation_units(translations: dict[str, Any]) -> dict[tuple[str, str], str]:
    units: dict[tuple[str, str], str] = {}
    for unit in translations.get("global_prompt_units", []):
        units[("global", unit.get("id", ""))] = unit.get("kind", "")
    for game in translations.get("games", []):
        context = game.get("game_id", "")
        for unit in game.get("prompt_units", []):
            units[(context, unit.get("id", ""))] = unit.get("kind", "")
    return units


def pending_review_units(review: dict[str, Any]) -> list[str]:
    return [
        f"{item.get('context', '')}/{item.get('unit_id', '')}"
        for item in review.get("units", [])
        if item.get("reviewer_status") != "approved"
    ]


def write_validation_artifact(review: dict[str, Any], errors: list[str], completed: bool) -> Path:
    pending = pending_review_units(review)
    if errors:
        status = "ERROR"
        blocker = "invalid_translation_review_file"
        message = "EN-ID translation review file is invalid and must be fixed before C1 can run."
        next_command = COMMAND
    elif completed:
        status = "OK"
        blocker = None
        message = "EN-ID translation human review is complete; C1 ID baseline is allowed to run."
        next_command = NEXT_COMMAND
    else:
        status = "BLOCKED"
        blocker = "pending_human_translation_review"
        message = "EN-ID translation review queue is aligned, but human approval is still pending."
        next_command = (
            "Fill config/translation_review.json with reviewer.completed=true, reviewer.name, "
            "reviewer.reviewed_at, and reviewer_status=approved for every unit; then run "
            f"{COMMAND} && {NEXT_COMMAND}."
        )

    payload = {
        "checked_at": utc_now(),
        "status": status,
        "blocker": blocker,
        "command": COMMAND,
        "next_command": next_command,
        "review_status": review.get("status"),
        "reviewer_completed": review.get("reviewer", {}).get("completed"),
        "pending_unit_count": len(pending),
        "pending_units": pending,
        "review_file": "config/translation_review.json",
        "review_packet": "docs/id_translation_review.md",
        "source_translation_file": review.get("source_translation_file"),
        "errors": errors,
        "message": message,
        "evidence_scope": "Translation gate artifact only; no C1 empirical evidence produced.",
    }
    artifact = write_json(ARTIFACT, payload)
    append_event(
        "translation_review",
        status,
        f"Translation review validation {status.lower()}; artifact={artifact.relative_to(ROOT)}; "
        f"pending_units={len(pending)}; next_command={next_command}",
    )
    return artifact


def main() -> int:
    translations = load_json("config/prompt_translations.json")
    review = load_json("config/translation_review.json")
    errors: list[str] = []

    if review.get("schema_version") != 1:
        errors.append("translation_review.json schema_version must be 1")
    if review.get("language_pair") != translations.get("language_pair"):
        errors.append("review language_pair must match prompt_translations.json")
    if review.get("source_translation_file") != "config/prompt_translations.json":
        errors.append("review source_translation_file must be config/prompt_translations.json")

    expected = translation_units(translations)
    seen: dict[tuple[str, str], str] = {}

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
        artifact = write_validation_artifact(review, errors, False)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(json.dumps({"artifact": str(artifact), "status": "ERROR"}, indent=2))
        return 1

    artifact = write_validation_artifact(review, errors, bool(completed))
    if completed:
        print("OK: EN-ID translation human review is complete and all units are approved.")
    else:
        print("OK: EN-ID translation review queue is aligned with prompt translations; human review remains pending.")
    print(json.dumps({"artifact": str(artifact), "status": "OK" if completed else "BLOCKED"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
