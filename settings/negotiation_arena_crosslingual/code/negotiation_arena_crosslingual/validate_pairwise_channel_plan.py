#!/usr/bin/env python3
"""Validate the active pairwise output-channel run plan."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "artifacts" / "results" / "pairwise_channel_plan_validation.json"
PLAN_PATH = ROOT / "config" / "pairwise_channel_plan.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_event(kind: str, status: str, message: str) -> None:
    path = ROOT / "plan" / "events.jsonl"
    record = {"ts": utc_now(), "kind": kind, "status": status, "message": message}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def role_languages(row: dict[str, Any]) -> dict[str, str]:
    value = row.get("role_languages")
    if not isinstance(value, dict):
        raise ValueError(f"{row.get('condition')} row is missing role_languages")
    buyer = str(value.get("buyer", "")).strip().upper()
    seller = str(value.get("seller", "")).strip().upper()
    if not buyer or not seller:
        raise ValueError(f"{row.get('condition')} row has incomplete role_languages")
    return {"buyer": buyer, "seller": seller}


def main() -> int:
    benchmark = load_json("config/benchmark.json")
    channels = load_json("config/language_channels.json")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    benchmark_pairs = list(benchmark.get("language_pairs", []))
    channel_pairs = list(channels.get("active_pairs", []))
    plan_pairs = [entry.get("pair") for entry in plan.get("active_pairs", [])]
    if plan_pairs != benchmark_pairs:
        return fail(f"pairwise plan order {plan_pairs} does not match benchmark language_pairs {benchmark_pairs}")
    if plan_pairs != channel_pairs:
        return fail(f"pairwise plan order {plan_pairs} does not match language_channels active_pairs {channel_pairs}")

    active_languages = set(channels.get("active_languages", []))
    required_conditions = {"C0", "C1", "C2", "C3"}
    c2_ids = {"buyer_lx_seller_ly", "buyer_ly_seller_lx"}
    summary: list[dict[str, Any]] = []

    for entry in plan.get("active_pairs", []):
        pair = str(entry.get("pair", ""))
        lx = str(entry.get("lx", "")).upper()
        ly = str(entry.get("ly", "")).upper()
        pair_languages = pair.split("-")
        if pair_languages != [lx, ly]:
            return fail(f"{pair} lx/ly fields do not match pair order")
        if not {lx, ly}.issubset(active_languages):
            return fail(f"{pair} uses languages outside active language set {sorted(active_languages)}")

        rows = entry.get("conditions", [])
        condition_set = {row.get("condition") for row in rows}
        if condition_set != required_conditions:
            return fail(f"{pair} condition coverage is {sorted(condition_set)}, expected {sorted(required_conditions)}")

        c0_rows = [row for row in rows if row.get("condition") == "C0"]
        c1_rows = [row for row in rows if row.get("condition") == "C1"]
        c2_rows = [row for row in rows if row.get("condition") == "C2"]
        c3_rows = [row for row in rows if row.get("condition") == "C3"]
        if len(c0_rows) != 1 or len(c1_rows) != 1 or len(c2_rows) != 2 or len(c3_rows) != 1:
            return fail(f"{pair} must have 1 C0, 1 C1, 2 C2 counterbalances, and 1 C3 row")

        if set(role_languages(c0_rows[0]).values()) != {lx}:
            return fail(f"{pair} C0 must assign both roles to Lx={lx}")
        if set(role_languages(c1_rows[0]).values()) != {ly}:
            return fail(f"{pair} C1 must assign both roles to Ly={ly}")

        seen_c2_ids = {str(row.get("counterbalance_id", "")) for row in c2_rows}
        if seen_c2_ids != c2_ids:
            return fail(f"{pair} C2 counterbalances {seen_c2_ids} do not match {c2_ids}")
        c2_assignments = {tuple(role_languages(row)[role] for role in ("buyer", "seller")) for row in c2_rows}
        if c2_assignments != {(lx, ly), (ly, lx)}:
            return fail(f"{pair} C2 role assignments {c2_assignments} do not counterbalance lx/ly")

        c3_allowed = [str(language).upper() for language in c3_rows[0].get("allowed_languages", [])]
        if c3_allowed != [lx, ly]:
            return fail(f"{pair} C3 allowed_languages {c3_allowed} must follow pair order {[lx, ly]}")
        if set(role_languages(c3_rows[0]).values()) != {pair}:
            return fail(f"{pair} C3 role_languages must mark both roles as bilingual {pair}")

        summary.append(
            {
                "pair": pair,
                "conditions": ["C0", "C1", "C2", "C2", "C3"],
                "c2_counterbalances": sorted(seen_c2_ids),
            }
        )

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(
        json.dumps(
            {
                "checked_at": utc_now(),
                "status": "OK",
                "plan": str(PLAN_PATH.relative_to(ROOT)),
                "validated_pairs": summary,
                "next_executable_command": plan.get("next_executable_command"),
                "evidence_scope": "validator only; no benchmark episode was run by this command",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    append_event(
        "pairwise_plan",
        "OK",
        f"Pairwise EN-ID, EN-ZH, and ZH-ID channel-run plan validated; artifact={ARTIFACT.relative_to(ROOT)}",
    )
    print("OK: pairwise EN-ID, EN-ZH, and ZH-ID channel-run plan validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
