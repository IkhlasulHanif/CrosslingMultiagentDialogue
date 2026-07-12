#!/usr/bin/env python3
"""Output-channel instructions and transcript compliance metrics."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = ("EN", "ID", "ZH")
OFF_PAIR = "OFF_PAIR"
UNKNOWN = "UNKNOWN"

EN_MARKERS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "buyer",
    "can",
    "counter",
    "deal",
    "for",
    "from",
    "i",
    "is",
    "item",
    "my",
    "of",
    "offer",
    "price",
    "seller",
    "the",
    "this",
    "to",
    "trade",
    "will",
    "with",
    "you",
}
ID_MARKERS = {
    "agar",
    "akan",
    "anda",
    "barang",
    "beli",
    "dengan",
    "harga",
    "ini",
    "jual",
    "kami",
    "karena",
    "kesepakatan",
    "mari",
    "menawarkan",
    "menerima",
    "menolak",
    "pada",
    "pembeli",
    "penjual",
    "saya",
    "sepakat",
    "tawaran",
    "untuk",
    "yang",
}


def load_channel_config() -> dict[str, Any]:
    return json.loads((ROOT / "config" / "language_channels.json").read_text(encoding="utf-8"))


def normalize_language(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text or None


def output_channel_instruction(language: str, condition: str | None = None, pair: str | None = None) -> str:
    config = load_channel_config()
    templates = config.get("output_channel_templates", {})
    normalized_language = normalize_language(language)
    if normalized_language not in templates:
        raise KeyError(f"Missing output-channel template for {language!r}")

    condition_key = "assigned_only"
    if condition and condition.upper() == "C3":
        condition_key = "free_choice"

    language_templates = templates[normalized_language]
    text = language_templates.get(condition_key) or language_templates.get("assigned_only")
    if not isinstance(text, str) or not text.strip():
        raise KeyError(f"Missing {condition_key} output-channel template for {language!r}")
    return text.format(language=normalized_language, pair=pair or "")


def visible_negotiation_text(message: Any) -> str:
    if isinstance(message, dict):
        public = message.get("upstream_public")
        if isinstance(public, dict) and isinstance(public.get("message"), str):
            return public["message"].strip()
        for key in ("visible_text", "message", "utterance", "content", "text"):
            value = message.get(key)
            if isinstance(value, str):
                return _strip_protocol_text(value)
    if isinstance(message, str):
        return _strip_protocol_text(message)
    return ""


def _strip_protocol_text(text: str) -> str:
    text = re.split(r"\n\s*RAW_UPSTREAM_RESPONSE\s*:", text, maxsplit=1, flags=re.IGNORECASE)[0]
    lines = [line for line in text.splitlines() if not re.match(r"^\s*(OFFER|ACCEPT|REJECT)\s*:", line, re.I)]
    return "\n".join(lines).strip()


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+", text.lower())


def language_scores(text: str) -> dict[str, int]:
    zh_chars = re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text)
    words = _word_tokens(text)
    en_score = sum(1 for word in words if word in EN_MARKERS)
    id_score = sum(1 for word in words if word in ID_MARKERS)

    ascii_words = [word for word in words if word not in {"zup", "x", "xml", "offer", "accept", "reject"}]
    if ascii_words and en_score == 0 and id_score == 0:
        en_score = max(en_score, 1)

    return {"EN": en_score, "ID": id_score, "ZH": len(zh_chars)}


def classify_text_language(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return UNKNOWN

    scores = language_scores(stripped)
    nonzero = {language: score for language, score in scores.items() if score > 0}
    if not nonzero:
        return UNKNOWN
    top_score = max(nonzero.values())
    top_languages = [language for language, score in nonzero.items() if score == top_score]
    if len(top_languages) != 1:
        return "MIXED"
    top_language = top_languages[0]
    other_score = sum(score for language, score in nonzero.items() if language != top_language)
    if other_score > 0 and other_score / max(1, top_score + other_score) >= 0.25:
        return "MIXED"
    return top_language


def _pair_languages(pair: str | None, role_languages: dict[str, Any]) -> set[str]:
    if pair and "-" in pair:
        return {part.strip().upper() for part in pair.split("-") if part.strip()}
    return {language for language in (normalize_language(value) for value in role_languages.values()) if language}


def channel_compliance(
    messages: Iterable[Any],
    role_languages: dict[str, Any],
    language_pair: str | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts = {language: 0 for language in LANGUAGES}
    counts.update({"MIXED": 0, UNKNOWN: 0})
    compliant = 0
    code_switch = 0
    off_pair = 0
    pair_languages = _pair_languages(language_pair, role_languages)

    for index, message in enumerate(messages):
        role = str(message.get("role")) if isinstance(message, dict) and message.get("role") is not None else None
        assigned = normalize_language(role_languages.get(role)) if role else None
        visible_text = visible_negotiation_text(message)
        detected = classify_text_language(visible_text)
        in_pair = detected in pair_languages if detected in LANGUAGES else detected in {"MIXED", UNKNOWN}
        is_mixed = detected == "MIXED"
        is_off_pair = detected in LANGUAGES and detected not in pair_languages
        is_compliant = bool(assigned and detected == assigned)

        counts[detected if detected in counts else UNKNOWN] += 1
        compliant += 1 if is_compliant else 0
        code_switch += 1 if is_mixed else 0
        off_pair += 1 if is_off_pair else 0
        rows.append(
            {
                "turn_index": message.get("turn_index") if isinstance(message, dict) else index,
                "role": role,
                "assigned_language": assigned,
                "detected_language": detected,
                "compliant": is_compliant,
                "in_pair": in_pair,
                "code_switch": is_mixed,
                "off_pair": is_off_pair,
                "scores": language_scores(visible_text),
                "visible_text_preview": visible_text[:200],
            }
        )

    total = len(rows)
    shares = {key.lower() + "_share": (value / total if total else None) for key, value in counts.items()}
    return {
        "available": total > 0,
        "method": "heuristic_visible_message_language_v1",
        "language_pair": language_pair,
        "pair_languages": sorted(pair_languages),
        "message_count": total,
        "assigned_compliance_rate": compliant / total if total else None,
        "code_switch_rate": code_switch / total if total else None,
        "off_pair_rate": off_pair / total if total else None,
        "off_pair_share": off_pair / total if total else None,
        **shares,
        "rows": rows,
    }
