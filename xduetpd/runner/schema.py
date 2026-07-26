from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from jsonschema import Draft202012Validator

from .constants import DIRECTIONS, LANGUAGES, LETTERS, PERSONAS, REASONING_MODES


PROBE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["p1", "p2", "p3", "p4", "probe_mode"],
    "properties": {
        "p1": {"anyOf": [{"enum": list(LETTERS)}, {"type": "null"}]},
        "p2": {
            "anyOf": [
                {
                    "type": "object",
                    "required": list(LETTERS),
                    "properties": {letter: {"type": "number"} for letter in LETTERS},
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "p3": {
            "anyOf": [
                {
                    "type": "object",
                    "required": list(LETTERS),
                    "properties": {letter: {"type": "number"} for letter in LETTERS},
                    "additionalProperties": False,
                },
                {"type": "null"},
            ]
        },
        "p4": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        "probe_mode": {"enum": ["parsed", "judged", "missing"]},
    },
    "additionalProperties": False,
}

TURN_ROW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "run_id",
        "cell_id",
        "seed",
        "dialogue_id",
        "turn",
        "role",
        "lang",
        "persona",
        "reasoning_mode",
        "direction",
        "appeal_type",
        "utterance",
        "think_trace",
        "committed_letter",
        "answer_text",
        "probe",
        "gold",
        "advocated",
        "coherence",
        "model",
        "timestamp",
    ],
    "properties": {
        "run_id": {"type": "string", "minLength": 1},
        "cell_id": {"type": "string", "minLength": 1},
        "seed": {"type": "integer"},
        "dialogue_id": {"type": "string", "minLength": 1},
        "turn": {"anyOf": [{"type": "integer"}, {"enum": ["final"]}]},
        "role": {"enum": ["T"]},
        "lang": {"enum": list(LANGUAGES)},
        "persona": {"enum": list(PERSONAS)},
        "reasoning_mode": {"enum": list(REASONING_MODES)},
        "direction": {"enum": list(DIRECTIONS)},
        "appeal_type": {
            "anyOf": [
                {
                    "enum": [
                        "credibility",
                        "logic_true",
                        "logic_fabricated",
                        "emotion",
                        "social_proof",
                        "authority",
                    ]
                },
                {"type": "null"},
            ]
        },
        "utterance": {"type": "string"},
        "think_trace": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "committed_letter": {"anyOf": [{"enum": list(LETTERS)}, {"type": "null"}]},
        "answer_text": {"type": "string"},
        "probe": PROBE_SCHEMA,
        "gold": {"enum": list(LETTERS)},
        "advocated": {"enum": list(LETTERS)},
        "coherence": {
            "type": "object",
            "required": ["langid", "parsed", "refusal"],
            "properties": {
                "langid": {"type": "number"},
                "parsed": {"type": "boolean"},
                "refusal": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
        "model": {"type": "string", "minLength": 1},
        "timestamp": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}

SUMMARY_ROW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "run_id",
        "cell_id",
        "seed",
        "dialogue_id",
        "phase",
        "target_lang",
        "persuader_lang",
        "direction",
        "persona",
        "reasoning_mode",
        "model_T",
        "model_P",
        "stimulus_id",
        "gold",
        "advocated",
        "initial",
        "final",
        "ftw",
        "ftr",
        "tof",
        "nof",
        "final_is_gold",
        "capitulation_persistence",
        "excluded",
        "exclusion_reason",
        "refusal_turns",
        "incoherent_turns",
        "appeal_delta_p_gold",
        "timestamp",
    ],
    "properties": {
        "run_id": {"type": "string"},
        "cell_id": {"type": "string"},
        "seed": {"type": "integer"},
        "dialogue_id": {"type": "string"},
        "phase": {"type": "string"},
        "target_lang": {"enum": list(LANGUAGES)},
        "persuader_lang": {"enum": list(LANGUAGES)},
        "direction": {"enum": list(DIRECTIONS)},
        "persona": {"enum": list(PERSONAS)},
        "reasoning_mode": {"enum": list(REASONING_MODES)},
        "model_T": {"type": "string"},
        "model_P": {"type": "string"},
        "stimulus_id": {"type": "string"},
        "gold": {"enum": list(LETTERS)},
        "advocated": {"enum": list(LETTERS)},
        "initial": {"anyOf": [{"enum": list(LETTERS)}, {"type": "null"}]},
        "final": {"anyOf": [{"enum": list(LETTERS)}, {"type": "null"}]},
        "ftw": {"type": "boolean"},
        "ftr": {"type": "boolean"},
        "tof": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
        "nof": {"type": "integer"},
        "final_is_gold": {"type": "boolean"},
        "capitulation_persistence": {"type": "boolean"},
        "excluded": {"type": "boolean"},
        "exclusion_reason": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "refusal_turns": {"type": "integer"},
        "incoherent_turns": {"type": "integer"},
        "appeal_delta_p_gold": {"type": "object"},
        "timestamp": {"type": "string"},
    },
    "additionalProperties": False,
}


TURN_VALIDATOR = Draft202012Validator(TURN_ROW_SCHEMA)
SUMMARY_VALIDATOR = Draft202012Validator(SUMMARY_ROW_SCHEMA)


@dataclass(frozen=True)
class Probe:
    p1: str | None
    p2: dict[str, float] | None
    p3: dict[str, float] | None
    p4: float | None
    probe_mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_turn_row(row: dict[str, Any]) -> None:
    errors = sorted(TURN_VALIDATOR.iter_errors(row), key=lambda err: err.path)
    if errors:
        message = "; ".join(f"{list(err.path)}: {err.message}" for err in errors)
        raise ValueError(f"turn row schema violation: {message}")


def validate_summary_row(row: dict[str, Any]) -> None:
    errors = sorted(SUMMARY_VALIDATOR.iter_errors(row), key=lambda err: err.path)
    if errors:
        message = "; ".join(f"{list(err.path)}: {err.message}" for err in errors)
        raise ValueError(f"summary row schema violation: {message}")


def loads_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows
