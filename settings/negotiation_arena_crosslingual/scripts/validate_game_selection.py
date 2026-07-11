#!/usr/bin/env python3
"""Validate the setting-local NegotiationArena game selection config."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    benchmark = load_json("config/benchmark.json")
    upstream = load_json("config/upstream.json")
    games = load_json("config/games.json")

    selected = games.get("selected_games", [])
    skipped = games.get("skipped_games", [])
    selected_ids = [item.get("id") for item in selected]
    skipped_ids = [item.get("id") for item in skipped]

    if selected_ids != upstream.get("selected_games"):
        return fail(
            "config/games.json selected_games must match config/upstream.json selected_games"
        )

    if "ultimatum" not in skipped_ids or "ultimatum" not in upstream.get("skipped_games", []):
        return fail("ultimatum must remain explicitly skipped in both game config files")

    if selected_ids != ["resource_exchange", "buy_sell"]:
        return fail("selected games must be resource_exchange followed by buy_sell")

    benchmark_conditions = set(benchmark.get("conditions", []))
    if benchmark_conditions != {"C0", "C1", "C2", "C3"}:
        return fail("benchmark conditions must be exactly C0, C1, C2, C3")

    for game in selected:
        if not game.get("include"):
            return fail(f"selected game {game.get('id')} is not marked include=true")
        if set(game.get("conditions", [])) != benchmark_conditions:
            return fail(f"selected game {game.get('id')} does not cover all benchmark conditions")
        required_outputs = set(game.get("required_outputs", []))
        if "deal" not in required_outputs or "first_offer" not in required_outputs:
            return fail(f"selected game {game.get('id')} is missing deal or first_offer output")
        mapping = game.get("upstream_mapping", {})
        if mapping.get("status") != "pending_local_checkout":
            return fail(f"selected game {game.get('id')} should remain pending until bring-up succeeds")

    required_metrics = set(games.get("metrics_required_by_selection", []))
    primary_metrics = set(benchmark.get("primary_metrics", []))
    missing_primary = primary_metrics - required_metrics
    if missing_primary:
        return fail("game selection omits primary metrics: " + ", ".join(sorted(missing_primary)))
    if "first_offer_anchoring" not in required_metrics:
        return fail("game selection must require first_offer_anchoring")

    pair = games.get("counterbalancing", {}).get("core_pair")
    if pair != "EN-ID":
        return fail("core counterbalancing pair must be EN-ID")

    assignments = games.get("counterbalancing", {}).get("c2_role_language_assignments", [])
    assignment_pairs = {
        (item.get("role_a_language"), item.get("role_b_language")) for item in assignments
    }
    if assignment_pairs != {("EN", "ID"), ("ID", "EN")}:
        return fail("C2 role-language assignments must counterbalance EN/ID and ID/EN")

    print(
        "OK: selected NegotiationArena games are resource_exchange and buy_sell; "
        "ultimatum is skipped; C0-C3 and EN-ID counterbalancing are configured."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
