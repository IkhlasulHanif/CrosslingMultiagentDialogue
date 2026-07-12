#!/usr/bin/env python3
"""Validate process metrics for first-offer anchoring and payoff asymmetry."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))

from process_metrics import (  # noqa: E402
    episode_pairwise_payoff_asymmetry,
    episode_payoff_asymmetry,
    first_offer_anchoring,
    pairwise_payoff_asymmetry,
    payoff_asymmetry,
)


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    buy_sell = first_offer_anchoring(
        "buy_sell",
        [
            {"role": "buyer", "language": "EN", "text": "OFFER: price=40"},
            {"role": "seller", "language": "ID", "text": "ACCEPT: harga=45"},
        ],
        {"final_price": 45},
    )
    if not buy_sell["has_first_offer"]:
        return fail("buy_sell first offer was not detected")
    if buy_sell["first_offer"]["role"] != "buyer" or buy_sell["first_offer"]["language"] != "EN":
        return fail("buy_sell first-offer role/language metadata was not preserved")
    if buy_sell["anchoring"].get("signed_delta") != 5:
        return fail(f"buy_sell signed anchor delta mismatch: {buy_sell['anchoring']}")

    resource_exchange = first_offer_anchoring(
        "resource_exchange",
        [
            {
                "speaker": "agent_a",
                "lang": "ID",
                "message": "OFFER: agent_a mendapat wood=2, food=1; agent_b mendapat wood=1, food=3.",
            },
            {
                "speaker": "agent_b",
                "lang": "EN",
                "message": "REJECT: I want a different split.",
            },
        ],
        {
            "final_terms": {
                "agent_a": {"wood": 1, "food": 2},
                "agent_b": {"wood": 2, "food": 2},
            }
        },
    )
    if not resource_exchange["has_first_offer"]:
        return fail("resource_exchange first offer was not detected")
    if resource_exchange["first_offer"]["language"] != "ID":
        return fail("resource_exchange language metadata was not normalized")
    if resource_exchange["anchoring"].get("l1_distance") != 4:
        return fail(f"resource_exchange L1 anchor distance mismatch: {resource_exchange['anchoring']}")

    missing = first_offer_anchoring(
        "buy_sell",
        [{"role": "seller", "language": "EN", "text": "REJECT: no deal."}],
        {"price": 10},
    )
    if missing["has_first_offer"] or missing["anchoring"].get("reason") != "missing_first_offer":
        return fail("missing-first-offer case did not report a clean null state")

    buy_sell_asymmetry = payoff_asymmetry(
        "buy_sell",
        {"buyer": 70, "seller": 55},
        {"buyer": "EN", "seller": "ID"},
    )
    if not buy_sell_asymmetry["available"]:
        return fail(f"buy_sell payoff asymmetry unexpectedly unavailable: {buy_sell_asymmetry}")
    if buy_sell_asymmetry["value"] != 15:
        return fail(f"buy_sell payoff asymmetry mismatch: {buy_sell_asymmetry}")
    if buy_sell_asymmetry["en_role"] != "buyer" or buy_sell_asymmetry["id_role"] != "seller":
        return fail(f"buy_sell payoff asymmetry role attribution mismatch: {buy_sell_asymmetry}")

    counterbalanced = payoff_asymmetry(
        "buy_sell",
        {"buyer": 70, "seller": 55},
        {"buyer": "ID", "seller": "EN"},
    )
    if counterbalanced.get("value") != -15:
        return fail(f"counterbalanced payoff asymmetry mismatch: {counterbalanced}")

    resource_asymmetry = episode_payoff_asymmetry(
        "resource_exchange",
        {
            "payoffs": {"agent_a": {"payoff": 8}, "agent_b": {"payoff": 13}},
            "role_languages": {"agent_a": "ID", "agent_b": "EN"},
        },
    )
    if not resource_asymmetry["available"] or resource_asymmetry["value"] != 5:
        return fail(f"resource_exchange payoff asymmetry mismatch: {resource_asymmetry}")

    zh_id_asymmetry = pairwise_payoff_asymmetry(
        "buy_sell",
        {"buyer": 80, "seller": 30},
        {"buyer": "ZH", "seller": "ID"},
        "ZH-ID",
    )
    if not zh_id_asymmetry["available"] or zh_id_asymmetry["value"] != 50:
        return fail(f"ZH-ID pairwise payoff asymmetry mismatch: {zh_id_asymmetry}")

    en_zh_counterbalanced = episode_pairwise_payoff_asymmetry(
        "buy_sell",
        {
            "language_pair": "EN-ZH",
            "payoffs": {"buyer": 25, "seller": 40},
            "role_languages": {"buyer": "ZH", "seller": "EN"},
        },
    )
    if not en_zh_counterbalanced["available"] or en_zh_counterbalanced["value"] != 15:
        return fail(f"EN-ZH pairwise payoff asymmetry mismatch: {en_zh_counterbalanced}")

    inferred_languages = episode_payoff_asymmetry(
        "resource_exchange",
        {"agent_a_payoff": 2, "agent_b_payoff": 9},
        [
            {"speaker": "agent_a", "lang": "EN", "message": "OFFER: agent_a gets wood=1; agent_b gets wood=2"},
            {"speaker": "agent_b", "lang": "ID", "message": "REJECT: no"},
        ],
    )
    if not inferred_languages["available"] or inferred_languages["value"] != -7:
        return fail(f"message-language payoff asymmetry inference mismatch: {inferred_languages}")

    monolingual = payoff_asymmetry(
        "buy_sell",
        {"buyer": 70, "seller": 55},
        {"buyer": "EN", "seller": "EN"},
    )
    if monolingual["available"] or monolingual.get("reason") != "missing_unique_en_id_roles":
        return fail(f"monolingual null state mismatch: {monolingual}")

    missing_payoff = payoff_asymmetry(
        "resource_exchange",
        {"agent_a": 4},
        {"agent_a": "EN", "agent_b": "ID"},
    )
    if missing_payoff["available"] or missing_payoff.get("reason") != "missing_payoff":
        return fail(f"missing-payoff null state mismatch: {missing_payoff}")

    print(
        "OK: first-offer anchoring tracks proposer role/language, buy_sell price delta, "
        "resource_exchange allocation distance, EN-ID and pairwise payoff asymmetry, and null states."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
