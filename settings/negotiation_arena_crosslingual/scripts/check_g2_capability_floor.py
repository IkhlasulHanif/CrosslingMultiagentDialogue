#!/usr/bin/env python3
"""Summarize the G2 capability floor from real baseline artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_c0_smoke import append_event, utc_now, write_json  # noqa: E402


ARTIFACT = "artifacts/results/g2_capability_floor.json"
FAILED_COMMAND = "python3 scripts/check_g2_capability_floor.py"
MIN_DEAL_RATE = 0.5
MIN_OFFER_PARSE_RATE = 0.9

C0_METRICS = [
    "artifacts/results/baseline_c0_buy_sell_en_seed001.metrics.json",
    "artifacts/results/baseline_c0_resource_exchange_en_seed001.metrics.json",
]
C1_METRICS = [
    "artifacts/results/baseline_c1_buy_sell_id_seed001.metrics.json",
]


def load_json(relative_path: str) -> dict[str, Any] | None:
    path = ROOT / relative_path
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def metric_row(relative_path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative_path,
        "game_id": payload.get("game_id"),
        "deal_rate": payload.get("deal_rate"),
        "offer_parse_rate": payload.get("offer_parse_rate"),
        "turns_to_deal": payload.get("turns_to_deal"),
    }


def numeric(values: list[Any]) -> list[float]:
    rows: list[float] = []
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            rows.append(float(value))
    return rows


def summarize(paths: list[str]) -> dict[str, Any]:
    present: list[dict[str, Any]] = []
    missing: list[str] = []
    for relative_path in paths:
        payload = load_json(relative_path)
        if payload is None:
            missing.append(relative_path)
            continue
        present.append(metric_row(relative_path, payload))

    deal_rates = numeric([row.get("deal_rate") for row in present])
    parse_rates = numeric([row.get("offer_parse_rate") for row in present])
    deal_rate_mean = sum(deal_rates) / len(deal_rates) if deal_rates else None
    offer_parse_rate_mean = sum(parse_rates) / len(parse_rates) if parse_rates else None

    enough = bool(present) and not missing
    passed = (
        enough
        and deal_rate_mean is not None
        and offer_parse_rate_mean is not None
        and deal_rate_mean >= MIN_DEAL_RATE
        and offer_parse_rate_mean >= MIN_OFFER_PARSE_RATE
    )
    return {
        "present_count": len(present),
        "missing": missing,
        "episodes": present,
        "deal_rate_mean": deal_rate_mean,
        "offer_parse_rate_mean": offer_parse_rate_mean,
        "thresholds": {
            "min_deal_rate": MIN_DEAL_RATE,
            "min_offer_parse_rate": MIN_OFFER_PARSE_RATE,
        },
        "passed": passed,
    }


def translation_review_gate() -> dict[str, Any]:
    review = load_json("config/translation_review.json") or {}
    pending = [
        f"{item.get('context', '')}/{item.get('unit_id', '')}"
        for item in review.get("units", [])
        if item.get("reviewer_status") != "approved"
    ]
    return {
        "status": review.get("status"),
        "reviewer_completed": review.get("reviewer", {}).get("completed"),
        "pending_unit_count": len(pending),
        "pending_units": pending,
        "review_file": "config/translation_review.json",
        "review_packet": "docs/id_translation_review.md",
    }


def main() -> int:
    c0 = summarize(C0_METRICS)
    c1 = summarize(C1_METRICS)
    review = translation_review_gate()

    if not c0["passed"]:
        status = "BLOCKED"
        blocker = "c0_capability_floor_not_met_or_missing"
        next_command = "bash scripts/run_c0_baseline.sh && bash scripts/run_c0_resource_exchange_baseline.sh"
        message = "G2 cannot pass because required C0 Qwen baseline evidence is missing or below floor."
        exit_code = 2
    elif not c1["passed"]:
        status = "BLOCKED"
        blocker = "c1_id_baseline_missing_pending_human_translation_review"
        next_command = "bash scripts/run_c1_baseline.sh"
        message = (
            "C0 floor passes on existing Qwen baseline artifacts, but G2 remains blocked until "
            "human-approved ID translations allow the C1 ID baseline to run."
        )
        exit_code = 2
    else:
        status = "OK"
        blocker = None
        next_command = "prepare C2/C3 role-language counterbalanced runs"
        message = "G2 capability floor passes for available C0 and C1 baseline artifacts."
        exit_code = 0

    payload = {
        "checked_at": utc_now(),
        "status": status,
        "blocker": blocker,
        "failed_command": FAILED_COMMAND if status != "OK" else None,
        "criteria": (
            "Before C2/C3, both monolingual baselines must meet deal_rate >= 0.5 "
            "and offer_parse_rate >= 0.9."
        ),
        "c0_en_summary": c0,
        "c1_id_summary": c1,
        "translation_review_gate": review,
        "message": message,
        "next_command": next_command,
        "evidence_scope": "Gate summary only; uses existing real Qwen baseline metric artifacts.",
    }
    artifact = write_json(ARTIFACT, payload)
    append_event(
        "gate",
        status,
        f"G2 capability floor check {status.lower()}; artifact={artifact.relative_to(ROOT)}; "
        f"next_command={next_command}",
    )
    print(json.dumps({"artifact": str(artifact), "status": status, "blocker": blocker}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
