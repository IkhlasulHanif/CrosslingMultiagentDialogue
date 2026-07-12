#!/usr/bin/env python3
"""Validate output-channel templates and heuristic compliance metrics."""

from __future__ import annotations

import sys
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))

from language_channels import channel_compliance, classify_text_language, output_channel_instruction  # noqa: E402


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    for language in ("EN", "ID", "ZH"):
        text = output_channel_instruction(language, "C1")
        if language not in text:
            return fail(f"{language} assigned-only template did not name the language code")
        free_choice = output_channel_instruction(language, "C3", "EN-ID")
        if "may" not in free_choice.lower():
            return fail(f"{language} C3 template did not expose free-choice wording")

    examples = {
        "EN": "I can offer a price of 55 ZUP for this item.",
        "ID": "Saya menawarkan harga 55 ZUP untuk barang ini.",
        "ZH": "我出价55 ZUP购买这个物品。",
    }
    for expected, text in examples.items():
        detected = classify_text_language(text)
        if detected != expected:
            return fail(f"language classifier mismatch for {expected}: {detected}")

    metrics = channel_compliance(
        [
            {"role": "buyer", "upstream_public": {"message": "Saya menawarkan harga 55 ZUP untuk barang ini."}},
            {"role": "seller", "upstream_public": {"message": "Saya menerima tawaran ini."}},
            {"role": "buyer", "upstream_public": {"message": "I accept this deal."}},
            {"role": "seller", "upstream_public": {"message": "我同意这个价格。"}},
        ],
        {"buyer": "ID", "seller": "ID"},
        "EN-ID",
    )
    if metrics["message_count"] != 4:
        return fail("channel compliance did not inspect every message")
    if metrics["assigned_compliance_rate"] != 0.5:
        return fail(f"unexpected ID compliance rate: {metrics['assigned_compliance_rate']}")
    if metrics["off_pair_rate"] != 0.25:
        return fail(f"unexpected off-pair rate: {metrics['off_pair_rate']}")
    if metrics["zh_share"] != 0.25 or metrics["id_share"] != 0.5 or metrics["en_share"] != 0.25:
        return fail(f"unexpected language shares: {metrics}")

    artifact = ROOT / "artifacts" / "results" / "language_channel_validation.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        json.dumps(
            {
                "checked_at": utc_now(),
                "status": "OK",
                "validated_templates": ["EN", "ID", "ZH"],
                "validated_metrics": [
                    "assigned_compliance_rate",
                    "en_share",
                    "id_share",
                    "zh_share",
                    "code_switch_rate",
                    "off_pair_rate",
                ],
                "sample_channel_compliance": metrics,
                "evidence_scope": "validator only; no benchmark episode was run by this command",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print("OK: output-channel templates and EN/ID/ZH compliance metrics validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
