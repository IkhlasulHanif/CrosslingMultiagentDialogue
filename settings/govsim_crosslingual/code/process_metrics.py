#!/usr/bin/env python3
"""Process-layer language metrics for GovSim transcript JSONL files."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PAIR_LANGUAGES = ("EN", "ID")
TOKEN_RE = re.compile(
    r"[\u0600-\u06ff]+|[\u0750-\u077f]+|[\u08a0-\u08ff]+|"
    r"[\u4e00-\u9fff]+|[A-Za-z]+(?:['-][A-Za-z]+)?|\d+"
)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")

EN_LEXICON = {
    "a",
    "about",
    "after",
    "agent",
    "all",
    "and",
    "avoid",
    "because",
    "before",
    "can",
    "catch",
    "cooperate",
    "fish",
    "for",
    "from",
    "harvest",
    "if",
    "in",
    "is",
    "keep",
    "less",
    "limit",
    "more",
    "need",
    "of",
    "our",
    "protect",
    "reduce",
    "resource",
    "round",
    "safe",
    "should",
    "stock",
    "survive",
    "take",
    "the",
    "this",
    "to",
    "we",
    "welfare",
    "will",
    "with",
}

ID_LEXICON = {
    "agar",
    "agen",
    "ambil",
    "aman",
    "dan",
    "dari",
    "dengan",
    "di",
    "harus",
    "ikan",
    "ini",
    "jaga",
    "jangan",
    "karena",
    "kecil",
    "kita",
    "lebih",
    "mari",
    "membatasi",
    "mengurangi",
    "panen",
    "perlu",
    "putaran",
    "saling",
    "sedikit",
    "sebelum",
    "semua",
    "setelah",
    "stok",
    "sumber",
    "supaya",
    "tahan",
    "untuk",
    "yang",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def classify_token(token: str) -> str:
    """Classify a token as EN, ID, OFF_PAIR:* or UNKNOWN.

    The classifier is intentionally lightweight and deterministic. It is good
    enough for smoke-gate process metrics, not a replacement for manual
    translation review or a trained language-ID model.
    """

    if CJK_RE.search(token):
        return "OFF_PAIR:ZH"
    if ARABIC_RE.search(token):
        return "OFF_PAIR:AR"
    lowered = token.lower()
    if not lowered.isalpha():
        return "UNKNOWN"

    is_en = lowered in EN_LEXICON
    is_id = lowered in ID_LEXICON
    if is_en and not is_id:
        return "EN"
    if is_id and not is_en:
        return "ID"
    return "UNKNOWN"


def message_metrics(record: dict[str, Any], pair_languages: tuple[str, str] = PAIR_LANGUAGES) -> dict[str, Any]:
    text = str(record.get("visible_text") or "")
    tokens = tokenize(text)
    labels = [classify_token(token) for token in tokens]
    pair_counts = Counter(label for label in labels if label in pair_languages)
    off_pair_counts = Counter(label.split(":", 1)[1] for label in labels if label.startswith("OFF_PAIR:"))
    unknown_count = sum(1 for label in labels if label == "UNKNOWN")
    pair_label_sequence = [label for label in labels if label in pair_languages]
    switch_points = sum(
        1 for left, right in zip(pair_label_sequence, pair_label_sequence[1:]) if left != right
    )
    pair_total = sum(pair_counts.values())
    shares = {
        language: (pair_counts[language] / pair_total if pair_total else 0.0)
        for language in pair_languages
    }
    dominant_language = None
    if pair_total:
        dominant_language = max(pair_languages, key=lambda language: pair_counts[language])
        tied = [language for language in pair_languages if pair_counts[language] == pair_counts[dominant_language]]
        if len(tied) > 1:
            dominant_language = None

    declared_language = record.get("language")
    declared_mismatch = (
        declared_language in pair_languages
        and dominant_language is not None
        and declared_language != dominant_language
    )

    return {
        "agent_id": record.get("agent_id"),
        "round_index": record.get("round_index"),
        "token_count": len(tokens),
        "classified_pair_token_count": pair_total,
        "unknown_token_count": unknown_count,
        "language_token_counts": dict(pair_counts),
        "language_share": shares,
        "dominant_language": dominant_language,
        "declared_language": declared_language,
        "declared_language_mismatch": bool(declared_mismatch),
        "off_pair_token_count": sum(off_pair_counts.values()),
        "off_pair_scripts": dict(off_pair_counts),
        "code_switch_points": switch_points,
        "code_switch": len(set(pair_label_sequence)) > 1,
    }


def _mean_pairwise_l1(vectors: list[dict[str, float]], pair_languages: tuple[str, str]) -> float | None:
    if len(vectors) < 2:
        return None
    distances: list[float] = []
    for index, left in enumerate(vectors):
        for right in vectors[index + 1 :]:
            distances.append(sum(abs(left.get(language, 0.0) - right.get(language, 0.0)) for language in pair_languages))
    return sum(distances) / len(distances)


def _agent_vectors_for_rounds(
    messages: list[dict[str, Any]],
    rounds: set[int],
    pair_languages: tuple[str, str],
) -> dict[str, dict[str, float]]:
    counts_by_agent: dict[str, Counter[str]] = defaultdict(Counter)
    for message in messages:
        round_index = message.get("round_index")
        agent_id = message.get("agent_id")
        if not isinstance(round_index, int) or round_index not in rounds or not agent_id:
            continue
        counts_by_agent[str(agent_id)].update(message["language_token_counts"])

    vectors: dict[str, dict[str, float]] = {}
    for agent_id, counts in counts_by_agent.items():
        total = sum(counts[language] for language in pair_languages)
        if total:
            vectors[agent_id] = {language: counts[language] / total for language in pair_languages}
    return vectors


def convergence_metrics(
    messages: list[dict[str, Any]],
    pair_languages: tuple[str, str] = PAIR_LANGUAGES,
) -> dict[str, Any]:
    rounds = sorted({message.get("round_index") for message in messages if isinstance(message.get("round_index"), int)})
    if len(rounds) < 2:
        return {
            "rounds_observed": rounds,
            "first_half_mean_pairwise_l1": None,
            "second_half_mean_pairwise_l1": None,
            "convergence_delta": None,
            "agents_compared": [],
        }

    split = max(1, len(rounds) // 2)
    first_rounds = set(rounds[:split])
    second_rounds = set(rounds[split:])
    first_vectors = _agent_vectors_for_rounds(messages, first_rounds, pair_languages)
    second_vectors = _agent_vectors_for_rounds(messages, second_rounds, pair_languages)
    shared_agents = sorted(set(first_vectors) & set(second_vectors))
    first_distance = _mean_pairwise_l1([first_vectors[agent] for agent in shared_agents], pair_languages)
    second_distance = _mean_pairwise_l1([second_vectors[agent] for agent in shared_agents], pair_languages)
    delta = None
    if first_distance is not None and second_distance is not None:
        delta = first_distance - second_distance

    return {
        "rounds_observed": rounds,
        "first_half_rounds": sorted(first_rounds),
        "second_half_rounds": sorted(second_rounds),
        "first_half_mean_pairwise_l1": first_distance,
        "second_half_mean_pairwise_l1": second_distance,
        "convergence_delta": delta,
        "agents_compared": shared_agents,
    }


def summarize_records(
    records: Iterable[dict[str, Any]],
    pair_languages: tuple[str, str] = PAIR_LANGUAGES,
) -> dict[str, Any]:
    model_records = [
        record
        for record in records
        if record.get("event_type") in {None, "model_message"} and "visible_text" in record
    ]
    messages = [message_metrics(record, pair_languages) for record in model_records]
    language_counts: Counter[str] = Counter()
    off_pair_scripts: Counter[str] = Counter()
    total_tokens = 0
    classified_pair_tokens = 0
    unknown_tokens = 0
    code_switch_points = 0
    declared_mismatches = 0

    for message in messages:
        total_tokens += message["token_count"]
        classified_pair_tokens += message["classified_pair_token_count"]
        unknown_tokens += message["unknown_token_count"]
        code_switch_points += message["code_switch_points"]
        declared_mismatches += int(message["declared_language_mismatch"])
        language_counts.update(message["language_token_counts"])
        off_pair_scripts.update(message["off_pair_scripts"])

    language_share = {
        language: (language_counts[language] / classified_pair_tokens if classified_pair_tokens else 0.0)
        for language in pair_languages
    }
    off_pair_token_count = sum(off_pair_scripts.values())
    round_shares = _round_language_shares(messages, pair_languages)

    return {
        "schema_version": "govsim-process-metrics-v1",
        "message_count": len(messages),
        "token_count": total_tokens,
        "classified_pair_token_count": classified_pair_tokens,
        "unknown_token_count": unknown_tokens,
        "language_token_counts": dict(language_counts),
        "language_share": language_share,
        "code_switch_message_count": sum(1 for message in messages if message["code_switch"]),
        "code_switch_message_rate": (
            sum(1 for message in messages if message["code_switch"]) / len(messages) if messages else 0.0
        ),
        "code_switch_points": code_switch_points,
        "code_switch_points_per_100_pair_tokens": (
            100.0 * code_switch_points / classified_pair_tokens if classified_pair_tokens else 0.0
        ),
        "off_pair_token_count": off_pair_token_count,
        "off_pair_rate": off_pair_token_count / total_tokens if total_tokens else 0.0,
        "off_pair_scripts": dict(off_pair_scripts),
        "declared_language_mismatch_count": declared_mismatches,
        "declared_language_mismatch_rate": declared_mismatches / len(messages) if messages else 0.0,
        "per_round_language_share": round_shares,
        "convergence": convergence_metrics(messages, pair_languages),
    }


def _round_language_shares(
    messages: list[dict[str, Any]],
    pair_languages: tuple[str, str],
) -> list[dict[str, Any]]:
    counts_by_round: dict[int, Counter[str]] = defaultdict(Counter)
    for message in messages:
        round_index = message.get("round_index")
        if isinstance(round_index, int):
            counts_by_round[round_index].update(message["language_token_counts"])

    rows: list[dict[str, Any]] = []
    for round_index in sorted(counts_by_round):
        counts = counts_by_round[round_index]
        total = sum(counts[language] for language in pair_languages)
        rows.append(
            {
                "round_index": round_index,
                "classified_pair_token_count": total,
                "language_share": {
                    language: (counts[language] / total if total else 0.0)
                    for language in pair_languages
                },
            }
        )
    return rows


def summarize_transcript(path: Path, pair_languages: tuple[str, str] = PAIR_LANGUAGES) -> dict[str, Any]:
    summary = summarize_records(read_jsonl(path), pair_languages)
    summary["source_path"] = str(path)
    return summary


def _json_default(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    raise TypeError(f"Cannot JSON encode {type(value).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize GovSim process language metrics.")
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    summary = summarize_transcript(args.transcript)
    text = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True, default=_json_default)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
