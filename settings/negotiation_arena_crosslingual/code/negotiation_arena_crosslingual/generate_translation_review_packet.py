#!/usr/bin/env python3
"""Generate the human-facing EN-ID translation review packet."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = "docs/id_translation_review.md"
ARTIFACT_PATH = "artifacts/results/translation_review_packet.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


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


def review_status_by_unit(review: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    statuses: dict[tuple[str, str], dict[str, Any]] = {}
    for unit in review.get("units", []):
        statuses[(unit.get("context", ""), unit.get("unit_id", ""))] = unit
    return statuses


def iter_translation_units(translations: dict[str, Any]) -> list[dict[str, str]]:
    units: list[dict[str, str]] = []
    for unit in translations.get("global_prompt_units", []):
        units.append(
            {
                "context": "global",
                "unit_id": unit.get("id", ""),
                "kind": unit.get("kind", ""),
                "en": unit.get("en", ""),
                "id_translation": unit.get("id_translation", ""),
            }
        )
    for game in translations.get("games", []):
        context = game.get("game_id", "")
        for unit in game.get("prompt_units", []):
            units.append(
                {
                    "context": context,
                    "unit_id": unit.get("id", ""),
                    "kind": unit.get("kind", ""),
                    "en": unit.get("en", ""),
                    "id_translation": unit.get("id_translation", ""),
                }
            )
    return units


def markdown_escape_table(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_packet(translations: dict[str, Any], review: dict[str, Any], generated_at: str) -> tuple[str, list[str]]:
    statuses = review_status_by_unit(review)
    units = iter_translation_units(translations)
    pending_units = [
        f"{unit['context']}/{unit['unit_id']}"
        for unit in units
        if statuses.get((unit["context"], unit["unit_id"]), {}).get("reviewer_status") != "approved"
    ]

    reviewer = review.get("reviewer", {})
    lines = [
        "# EN-ID Translation Human Review",
        "",
        f"Status: {review.get('status', 'unknown')}.",
        "",
        "This file is generated from `config/prompt_translations.json` and "
        "`config/translation_review.json`. The machine-readable review state is "
        "`config/translation_review.json`.",
        "",
        "Do not mark `Human-check ID translation` complete in `goals.md` until:",
        "",
        "- `config/translation_review.json` has `reviewer.completed: true`.",
        "- Reviewer name and review date are filled.",
        '- Every unit has `reviewer_status: "approved"`.',
        "- `python3 scripts/validate_translation_review.py` passes.",
        "",
        "Reviewer metadata:",
        "",
        f"- Completed: `{reviewer.get('completed')}`",
        f"- Name: `{reviewer.get('name', '')}`",
        f"- Reviewed at: `{reviewer.get('reviewed_at', '')}`",
        f"- Notes: `{reviewer.get('notes', '')}`",
        "",
        "Review criteria:",
        "",
    ]
    for criterion in review.get("review_criteria", []):
        lines.append(f"- {criterion}")

    lines.extend(
        [
            "",
            "## Review Queue",
            "",
            "| Context | Unit | Kind | Status | Notes |",
            "|---|---|---|---|---|",
        ]
    )
    for unit in units:
        status_record = statuses.get((unit["context"], unit["unit_id"]), {})
        status = status_record.get("reviewer_status", "missing")
        notes = markdown_escape_table(status_record.get("reviewer_notes", ""))
        lines.append(
            "| "
            f"{markdown_escape_table(unit['context'])} | "
            f"{markdown_escape_table(unit['unit_id'])} | "
            f"{markdown_escape_table(unit['kind'])} | "
            f"{markdown_escape_table(status)} | "
            f"{notes} |"
        )

    lines.extend(["", "## Side-By-Side Units", ""])
    for unit in units:
        status_record = statuses.get((unit["context"], unit["unit_id"]), {})
        lines.extend(
            [
                f"### {unit['context']}/{unit['unit_id']}",
                "",
                f"Kind: {unit['kind']}",
                "",
                f"Review status: {status_record.get('reviewer_status', 'missing')}",
                "",
                f"Reviewer notes: {status_record.get('reviewer_notes', '')}",
                "",
                f"EN: {unit['en']}",
                "",
                f"ID: {unit['id_translation']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Next Command",
            "",
            "After a bilingual reviewer approves every unit in "
            "`config/translation_review.json`, run:",
            "",
            "```bash",
            "python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh",
            "```",
            "",
        ]
    )
    return "\n".join(lines), pending_units


def main() -> int:
    generated_at = utc_now()
    translations = load_json("config/prompt_translations.json")
    review = load_json("config/translation_review.json")
    packet, pending_units = render_packet(translations, review, generated_at)

    packet_path = ROOT / PACKET_PATH
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(packet, encoding="utf-8")

    artifact = write_json(
        ARTIFACT_PATH,
        {
            "generated_at": generated_at,
            "status": "BLOCKED" if pending_units else "OK",
            "packet": PACKET_PATH,
            "source_translation_file": "config/prompt_translations.json",
            "review_file": "config/translation_review.json",
            "unit_count": len(iter_translation_units(translations)),
            "pending_unit_count": len(pending_units),
            "pending_units": pending_units,
            "next_command": (
                "python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh"
            ),
            "evidence_scope": "Human-review packet only; no C1 empirical evidence produced.",
        },
    )
    append_event(
        "translation_review",
        "BLOCKED" if pending_units else "OK",
        f"Generated EN-ID translation review packet; packet={PACKET_PATH}; "
        f"artifact={artifact.relative_to(ROOT)}; pending_units={len(pending_units)}",
    )
    print(
        json.dumps(
            {
                "packet": str(packet_path),
                "artifact": str(artifact),
                "status": "BLOCKED" if pending_units else "OK",
                "pending_unit_count": len(pending_units),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
