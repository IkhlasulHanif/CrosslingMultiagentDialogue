#!/usr/bin/env python3
"""Validate structured offer parsing for selected NegotiationArena games."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))

from offer_parser import offer_parse_rate, parse_offer  # noqa: E402


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    fixtures = [
        (
            "buy_sell",
            "I can open here.\nOFFER: price=42.",
            True,
            "OFFER",
            {"price": 42},
        ),
        (
            "buy_sell",
            "ACCEPT: harga: $37.5",
            True,
            "ACCEPT",
            {"price": 37.5},
        ),
        (
            "buy_sell",
            "REJECT: outside option is better.",
            True,
            "REJECT",
            {},
        ),
        (
            "resource_exchange",
            "OFFER: agent_a gets wood=2, food=1; agent_b gets wood=1, food=3.",
            True,
            "OFFER",
            {"agent_a": {"wood": 2, "food": 1}, "agent_b": {"wood": 1, "food": 3}},
        ),
        (
            "resource_exchange",
            "ACCEPT: agent_a mendapat {wood: 2, food: 1}; agent_b mendapat {wood: 1, food: 3}",
            True,
            "ACCEPT",
            {"agent_a": {"wood": 2, "food": 1}, "agent_b": {"wood": 1, "food": 3}},
        ),
        (
            "resource_exchange",
            "No structured line here.",
            False,
            None,
            {},
        ),
    ]

    results = []
    for index, (game_id, text, expected_ok, expected_action, expected_terms) in enumerate(fixtures, start=1):
        result = parse_offer(game_id, text)
        results.append(result)
        if result.ok is not expected_ok:
            return fail(f"fixture {index} ok mismatch: got {result.ok}, expected {expected_ok}")
        if result.action != expected_action:
            return fail(f"fixture {index} action mismatch: got {result.action}, expected {expected_action}")
        if result.terms != expected_terms:
            return fail(f"fixture {index} terms mismatch: got {result.terms}, expected {expected_terms}")
        if not result.ok and not result.error:
            return fail(f"fixture {index} failed without an error message")

    rate = offer_parse_rate(results)
    expected_rate = 5 / 6
    if abs(rate - expected_rate) > 1e-12:
        return fail(f"offer_parse_rate mismatch: got {rate}, expected {expected_rate}")

    print(
        "OK: structured offer parser handles buy_sell price offers, "
        "resource_exchange allocations, accepts/rejects, ID/EN verbs, and explicit parse failures."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
