#!/usr/bin/env python3
"""Process-layer metrics for the B5 NegotiationArena setting."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from offer_parser import ParseResult, parse_offer  # noqa: E402


TEXT_KEYS = ("text", "message", "content", "utterance", "response", "raw")
ROLE_KEYS = ("role", "speaker", "agent", "player")
LANGUAGE_KEYS = ("language", "lang")
PAYOFF_KEYS = ("payoff", "score", "utility")
GAME_ROLES = {
    "buy_sell": ("buyer", "seller"),
    "resource_exchange": ("agent_a", "agent_b"),
}


def _message_value(message: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        value = message.get(key)
        if value is not None:
            return value
    return None


def message_text(message: Any) -> str | None:
    if isinstance(message, str):
        return message
    if not isinstance(message, dict):
        return None

    value = _message_value(message, TEXT_KEYS)
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts) if parts else None
    return None


def message_role(message: Any) -> str | None:
    if not isinstance(message, dict):
        return None
    value = _message_value(message, ROLE_KEYS)
    return str(value) if value is not None else None


def message_language(message: Any) -> str | None:
    if not isinstance(message, dict):
        return None
    value = _message_value(message, LANGUAGE_KEYS)
    return str(value).upper() if value is not None else None


def normalize_language(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip().upper()


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
        return int(parsed) if parsed.is_integer() else parsed
    return None


def _nested_mapping_value(payload: dict[str, Any], keys: Iterable[str]) -> dict[str, Any] | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return None


def _role_value(mapping: dict[str, Any], role: str, keys: Iterable[str]) -> Any:
    value = mapping.get(role)
    if isinstance(value, dict):
        nested = _message_value(value, keys)
        if nested is not None:
            return nested
    return value


def extract_role_payoffs(game_id: str, payload: dict[str, Any]) -> dict[str, int | float]:
    roles = GAME_ROLES.get(game_id, ())
    payoffs: dict[str, int | float] = {}

    nested = _nested_mapping_value(payload, ("payoffs", "scores", "utilities"))
    for role in roles:
        value = None
        if nested is not None:
            value = _role_value(nested, role, PAYOFF_KEYS)
        if value is None:
            value = payload.get(f"{role}_payoff", payload.get(f"{role}_score"))
        number = _number(value)
        if number is not None:
            payoffs[role] = number
    return payoffs


def extract_role_languages(
    game_id: str,
    payload: dict[str, Any],
    messages: Iterable[Any] | None = None,
) -> dict[str, str]:
    roles = GAME_ROLES.get(game_id, ())
    role_languages: dict[str, str] = {}

    nested = _nested_mapping_value(payload, ("role_languages", "languages", "language_by_role"))
    if nested is not None:
        for role in roles:
            language = normalize_language(_role_value(nested, role, LANGUAGE_KEYS))
            if language:
                role_languages[role] = language

    agents = _nested_mapping_value(payload, ("agents", "players"))
    if agents is not None:
        for role in roles:
            if role in role_languages:
                continue
            language = normalize_language(_role_value(agents, role, LANGUAGE_KEYS))
            if language:
                role_languages[role] = language

    if messages is not None:
        for message in messages:
            role = message_role(message)
            language = message_language(message)
            if role in roles and language and role not in role_languages:
                role_languages[role] = language

    return role_languages


def payoff_asymmetry(
    game_id: str,
    payoffs: dict[str, Any],
    role_languages: dict[str, Any],
) -> dict[str, Any]:
    roles = GAME_ROLES.get(game_id)
    if roles is None:
        return {"available": False, "reason": f"unsupported_game_id:{game_id}"}

    normalized_payoffs: dict[str, int | float] = {}
    normalized_languages: dict[str, str] = {}
    for role in roles:
        payoff = _number(payoffs.get(role))
        if payoff is not None:
            normalized_payoffs[role] = payoff
        language = normalize_language(role_languages.get(role))
        if language:
            normalized_languages[role] = language

    missing_payoff = [role for role in roles if role not in normalized_payoffs]
    if missing_payoff:
        return {
            "available": False,
            "reason": "missing_payoff",
            "missing_roles": missing_payoff,
            "payoffs": normalized_payoffs,
            "role_languages": normalized_languages,
        }

    language_roles = {"EN": [], "ID": []}
    for role, language in normalized_languages.items():
        if language in language_roles:
            language_roles[language].append(role)

    if len(language_roles["EN"]) != 1 or len(language_roles["ID"]) != 1:
        return {
            "available": False,
            "reason": "missing_unique_en_id_roles",
            "payoffs": normalized_payoffs,
            "role_languages": normalized_languages,
        }

    en_role = language_roles["EN"][0]
    id_role = language_roles["ID"][0]
    en_payoff = normalized_payoffs[en_role]
    id_payoff = normalized_payoffs[id_role]
    return {
        "available": True,
        "metric": "EN_agent_payoff_minus_ID_agent_payoff",
        "value": en_payoff - id_payoff,
        "en_role": en_role,
        "id_role": id_role,
        "en_payoff": en_payoff,
        "id_payoff": id_payoff,
        "payoffs": normalized_payoffs,
        "role_languages": normalized_languages,
    }


def episode_payoff_asymmetry(game_id: str, payload: dict[str, Any], messages: Iterable[Any] | None = None) -> dict[str, Any]:
    return payoff_asymmetry(
        game_id,
        extract_role_payoffs(game_id, payload),
        extract_role_languages(game_id, payload, messages),
    )


def normalize_final_terms(game_id: str, payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None

    terms = payload.get("final_terms")
    if isinstance(terms, dict):
        payload = terms

    if game_id == "buy_sell":
        price = _number(payload.get("price", payload.get("final_price")))
        return {"price": price} if price is not None else None

    if game_id == "resource_exchange":
        normalized: dict[str, dict[str, int | float]] = {}
        for role in ("agent_a", "agent_b"):
            allocation = payload.get(role)
            if not isinstance(allocation, dict):
                return None
            normalized[role] = {}
            for item, value in allocation.items():
                number = _number(value)
                if number is None:
                    return None
                normalized[role][str(item)] = number
        return normalized

    return None


def _allocation_l1(first_terms: dict[str, Any], final_terms: dict[str, Any]) -> int | float:
    distance: int | float = 0
    roles = set(first_terms) | set(final_terms)
    for role in roles:
        first_allocation = first_terms.get(role, {})
        final_allocation = final_terms.get(role, {})
        if not isinstance(first_allocation, dict) or not isinstance(final_allocation, dict):
            continue
        items = set(first_allocation) | set(final_allocation)
        for item in items:
            first_value = _number(first_allocation.get(item)) or 0
            final_value = _number(final_allocation.get(item)) or 0
            distance += abs(final_value - first_value)
    return distance


def anchoring_delta(game_id: str, first_terms: dict[str, Any], final_terms: dict[str, Any] | None) -> dict[str, Any]:
    if final_terms is None:
        return {
            "available": False,
            "reason": "missing_final_terms",
        }

    if game_id == "buy_sell":
        first_price = _number(first_terms.get("price"))
        final_price = _number(final_terms.get("price"))
        if first_price is None or final_price is None:
            return {"available": False, "reason": "missing_price"}
        return {
            "available": True,
            "metric": "final_price_minus_first_offer_price",
            "signed_delta": final_price - first_price,
            "absolute_delta": abs(final_price - first_price),
        }

    if game_id == "resource_exchange":
        return {
            "available": True,
            "metric": "final_allocation_l1_distance_from_first_offer",
            "l1_distance": _allocation_l1(first_terms, final_terms),
        }

    return {"available": False, "reason": f"unsupported_game_id:{game_id}"}


def parsed_message_row(index: int, message: Any, result: ParseResult) -> dict[str, Any]:
    return {
        "turn_index": index,
        "role": message_role(message),
        "language": message_language(message),
        "action": result.action,
        "ok": result.ok,
        "terms": result.terms,
        "raw_line": result.raw_line,
        "error": result.error,
    }


def first_offer_anchoring(
    game_id: str,
    messages: Iterable[Any],
    final_terms_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    message_rows = list(messages)
    parsed_rows: list[dict[str, Any]] = []
    first_offer: dict[str, Any] | None = None

    for index, message in enumerate(message_rows):
        text = message_text(message)
        if text is None:
            continue
        result = parse_offer(game_id, text)
        row = parsed_message_row(index, message, result)
        parsed_rows.append(row)
        if first_offer is None and result.ok and result.action == "OFFER":
            first_offer = row

    final_terms = normalize_final_terms(game_id, final_terms_payload)
    output: dict[str, Any] = {
        "game_id": game_id,
        "message_count": len(message_rows),
        "parsed_message_count": len(parsed_rows),
        "has_first_offer": first_offer is not None,
        "first_offer": first_offer,
        "final_terms": final_terms,
        "anchoring": {"available": False, "reason": "missing_first_offer"},
    }

    if first_offer is not None:
        output["anchoring"] = anchoring_delta(game_id, first_offer["terms"], final_terms)

    return output


def _load_json_or_jsonl(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith("{") or stripped.startswith("["):
        return json.loads(stripped)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _episode_parts(payload: Any) -> tuple[str | None, list[Any], dict[str, Any] | None, dict[str, Any]]:
    if isinstance(payload, list):
        return None, payload, None, {}
    if not isinstance(payload, dict):
        return None, [], None, {}

    messages = (
        payload.get("messages")
        or payload.get("turns")
        or payload.get("transcript")
        or payload.get("events")
        or []
    )
    if not isinstance(messages, list):
        messages = []

    final_payload = {
        key: payload[key]
        for key in ("final_terms", "final_price", "price", "agent_a", "agent_b")
        if key in payload
    }
    return payload.get("game_id"), messages, final_payload or None, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path, help="JSON or JSONL transcript/episode file")
    parser.add_argument("--game-id", choices=["buy_sell", "resource_exchange"])
    parser.add_argument("--final-terms", help="JSON object overriding final terms from episode")
    args = parser.parse_args()

    payload = _load_json_or_jsonl(args.episode)
    episode_game_id, messages, episode_final_terms, episode_payload = _episode_parts(payload)
    game_id = args.game_id or episode_game_id
    if game_id is None:
        print("ERROR: game id is required via --game-id or episode.game_id", file=sys.stderr)
        return 1

    final_terms = episode_final_terms
    if args.final_terms:
        final_terms = json.loads(args.final_terms)

    result = first_offer_anchoring(game_id, messages, final_terms)
    result["payoff_asymmetry"] = episode_payoff_asymmetry(game_id, episode_payload, messages)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
