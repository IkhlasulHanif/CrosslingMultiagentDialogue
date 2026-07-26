from __future__ import annotations

import json
from pathlib import Path

from runner.schema import validate_summary_row, validate_turn_row

ROOT = Path(__file__).resolve().parents[1]


def test_turn_schema_accepts_contract_shape():
    row = {
        "run_id": "r",
        "cell_id": "m0_smoke",
        "seed": 1,
        "dialogue_id": "d",
        "turn": 0,
        "role": "T",
        "lang": "EN",
        "persona": "none",
        "reasoning_mode": "native",
        "direction": "misleading",
        "appeal_type": None,
        "utterance": "I choose the best answer.\nANSWER: A",
        "think_trace": None,
        "committed_letter": "A",
        "answer_text": "I choose the best answer.",
        "probe": {
            "p1": "A",
            "p2": {"A": 1.0, "B": 0.0, "C": 0.0, "D": 0.0},
            "p3": None,
            "p4": 80.0,
            "probe_mode": "parsed",
        },
        "gold": "A",
        "advocated": "B",
        "coherence": {"langid": 1.0, "parsed": True, "refusal": False},
        "model": "gpt-4o-mini",
        "timestamp": "2026-07-26T00:00:00+00:00",
    }
    validate_turn_row(row)


def test_summary_schema_accepts_contract_shape():
    row = {
        "run_id": "r",
        "cell_id": "m0_smoke",
        "seed": 1,
        "dialogue_id": "d",
        "phase": "m0",
        "target_lang": "EN",
        "persuader_lang": "EN",
        "direction": "misleading",
        "persona": "none",
        "reasoning_mode": "native",
        "model_T": "gpt-4o-mini",
        "model_P": "gpt-4o-mini",
        "stimulus_id": "s",
        "gold": "A",
        "advocated": "B",
        "initial": "A",
        "final": "B",
        "ftw": True,
        "ftr": False,
        "tof": 3,
        "nof": 1,
        "final_is_gold": False,
        "capitulation_persistence": True,
        "excluded": False,
        "exclusion_reason": None,
        "refusal_turns": 0,
        "incoherent_turns": 0,
        "appeal_delta_p_gold": {"logic_true": -0.25},
        "timestamp": "2026-07-26T00:00:00+00:00",
    }
    validate_summary_row(row)


def test_m0_output_schema_if_present():
    turn_path = ROOT / "results" / "jsonl" / "m0_smoke.jsonl"
    if turn_path.exists():
        for line in turn_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                validate_turn_row(json.loads(line))
    summary_path = ROOT / "results" / "summaries" / "m0_smoke.jsonl"
    if summary_path.exists():
        for line in summary_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                validate_summary_row(json.loads(line))
