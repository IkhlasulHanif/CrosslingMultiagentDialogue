#!/usr/bin/env python3
"""Structured offer parser for the B5 NegotiationArena setting."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]

ACTION_RE = re.compile(r"^\s*(OFFER|ACCEPT|REJECT)\s*:\s*(.*)\s*$", re.IGNORECASE)
PRICE_RE = re.compile(r"\b(?:price|harga)\s*[:=]\s*\$?\s*(-?\d+(?:\.\d+)?)\b", re.IGNORECASE)
RESOURCE_ROLE_RE = re.compile(
    r"\b(agent_[ab])\s*(?:gets|mendapat|receives|=|:)\s*(.+?)(?=(?:;\s*agent_[ab]\b)|$)",
    re.IGNORECASE,
)
PAIR_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)\s*[:=]\s*(-?\d+(?:\.\d+)?)")
COUNT_NAME_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s+([A-Za-z_][A-Za-z0-9_-]*)")


@dataclass(frozen=True)
class ParseResult:
    game_id: str
    action: str | None
    terms: dict[str, Any]
    ok: bool
    raw_line: str | None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _number(value: str) -> int | float:
    parsed = float(value)
    if parsed.is_integer():
        return int(parsed)
    return parsed


def _structured_line(text: str) -> tuple[str, str, str] | None:
    for line in text.splitlines():
        match = ACTION_RE.match(line)
        if match:
            return match.group(1).upper(), match.group(2).strip(), line.strip()
    return None


def _parse_allocation(text: str) -> dict[str, int | float]:
    cleaned = text.strip().strip(".")
    if cleaned.startswith("{") and cleaned.endswith("}"):
        cleaned = cleaned[1:-1]

    values: dict[str, int | float] = {}
    for key, value in PAIR_RE.findall(cleaned):
        values[key] = _number(value)

    if values:
        return values

    for value, key in COUNT_NAME_RE.findall(cleaned):
        values[key] = _number(value)
    return values


def parse_buy_sell(text: str) -> ParseResult:
    line = _structured_line(text)
    if line is None:
        return ParseResult("buy_sell", None, {}, False, None, "missing OFFER/ACCEPT/REJECT line")

    action, payload, raw_line = line
    if action == "REJECT":
        return ParseResult("buy_sell", action, {}, True, raw_line)

    price = PRICE_RE.search(payload)
    if not price:
        return ParseResult("buy_sell", action, {}, False, raw_line, "missing price=... term")

    return ParseResult("buy_sell", action, {"price": _number(price.group(1))}, True, raw_line)


def parse_resource_exchange(text: str) -> ParseResult:
    line = _structured_line(text)
    if line is None:
        return ParseResult(
            "resource_exchange",
            None,
            {},
            False,
            None,
            "missing OFFER/ACCEPT/REJECT line",
        )

    action, payload, raw_line = line
    if action == "REJECT":
        return ParseResult("resource_exchange", action, {}, True, raw_line)

    role_allocations: dict[str, dict[str, int | float]] = {}
    for role, allocation_text in RESOURCE_ROLE_RE.findall(payload):
        role_allocations[role.lower()] = _parse_allocation(allocation_text)

    missing = [role for role in ("agent_a", "agent_b") if role not in role_allocations]
    if missing:
        return ParseResult(
            "resource_exchange",
            action,
            {},
            False,
            raw_line,
            "missing allocation for " + ", ".join(missing),
        )

    empty = [role for role, allocation in role_allocations.items() if not allocation]
    if empty:
        return ParseResult(
            "resource_exchange",
            action,
            role_allocations,
            False,
            raw_line,
            "empty allocation for " + ", ".join(sorted(empty)),
        )

    return ParseResult("resource_exchange", action, role_allocations, True, raw_line)


def parse_offer(game_id: str, text: str) -> ParseResult:
    if game_id == "buy_sell":
        return parse_buy_sell(text)
    if game_id == "resource_exchange":
        return parse_resource_exchange(text)
    return ParseResult(game_id, None, {}, False, None, f"unsupported game_id: {game_id}")


def offer_parse_rate(results: Iterable[ParseResult]) -> float:
    rows = list(results)
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.ok) / len(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("game_id", choices=["buy_sell", "resource_exchange"])
    parser.add_argument("text", nargs="?", help="message text; stdin is used when omitted")
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    result = parse_offer(args.game_id, text)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
