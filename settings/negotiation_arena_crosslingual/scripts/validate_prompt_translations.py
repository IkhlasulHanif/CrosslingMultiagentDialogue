#!/usr/bin/env python3
"""Validate setting-local EN-ID prompt/rule translations."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def validate_unit(unit: dict[str, Any], context: str) -> list[str]:
    errors: list[str] = []
    unit_id = unit.get("id", "<missing-id>")
    en = unit.get("en")
    id_translation = unit.get("id_translation")
    if not isinstance(en, str) or not en.strip():
        errors.append(f"{context}/{unit_id} has empty en text")
    if not isinstance(id_translation, str) or not id_translation.strip():
        errors.append(f"{context}/{unit_id} has empty id_translation text")
    if isinstance(en, str) and isinstance(id_translation, str):
        en_placeholders = placeholders(en)
        id_placeholders = placeholders(id_translation)
        if en_placeholders != id_placeholders:
            errors.append(
                f"{context}/{unit_id} placeholder mismatch: "
                f"en={sorted(en_placeholders)} id={sorted(id_placeholders)}"
            )
    return errors


def main() -> int:
    benchmark = load_json("config/benchmark.json")
    games_config = load_json("config/games.json")
    translations = load_json("config/prompt_translations.json")

    if translations.get("language_pair") != "EN-ID":
        return fail("prompt translations must target EN-ID")
    if translations.get("status") != "translated_pending_human_check":
        return fail("translation status must remain translated_pending_human_check")

    human_check = translations.get("human_check", {})
    if human_check.get("completed") is not False or human_check.get("required") is not True:
        return fail("human_check must be required=true and completed=false")

    selected_game_ids = {game.get("id") for game in games_config.get("selected_games", [])}
    translation_game_ids = {game.get("game_id") for game in translations.get("games", [])}
    if selected_game_ids != translation_game_ids:
        return fail(
            "translated games must match selected games: "
            f"selected={sorted(selected_game_ids)} translated={sorted(translation_game_ids)}"
        )

    required_conditions = set(benchmark.get("conditions", []))
    global_unit_ids = {unit.get("id") for unit in translations.get("global_prompt_units", [])}
    expected_policy_ids = {
        "C0": "language_policy_c0_en",
        "C1": "language_policy_c1_id",
        "C2": "language_policy_c2_forced_mixed",
        "C3": "language_policy_c3_free_choice",
    }
    missing_policies = [
        policy_id
        for condition, policy_id in expected_policy_ids.items()
        if condition in required_conditions and policy_id not in global_unit_ids
    ]
    if missing_policies:
        return fail("missing condition language policy units: " + ", ".join(missing_policies))

    errors: list[str] = []
    for unit in translations.get("global_prompt_units", []):
        errors.extend(validate_unit(unit, "global"))

    for game in translations.get("games", []):
        game_id = game.get("game_id", "<missing-game-id>")
        units = game.get("prompt_units", [])
        kinds = {unit.get("kind") for unit in units}
        for required_kind in {"public_rules", "private_prompt", "offer_format"}:
            if required_kind not in kinds:
                errors.append(f"{game_id} is missing {required_kind}")
        for unit in units:
            errors.extend(validate_unit(unit, game_id))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "OK: EN-ID prompt/rule translations cover selected games, C0-C3 language "
        "policies, and preserve placeholders; human check remains pending."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
