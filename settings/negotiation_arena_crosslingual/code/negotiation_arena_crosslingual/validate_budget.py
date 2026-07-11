#!/usr/bin/env python3
"""Validate that the setting has a pre-full-matrix budget plan."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUDGET = ROOT / "budget.md"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not BUDGET.exists():
        return fail("budget.md is missing")

    text = BUDGET.read_text(encoding="utf-8")
    normalized_text = re.sub(r"\s+", " ", text)
    required_phrases = [
        "local `Qwen3-1.7B`",
        "`Qwen3-8B`",
        "OpenAI API calls: not allowed",
        "`EN-ID`",
        "`resource_exchange` and `buy_sell`",
        "`C0`, `C1`, `C2`, and `C3`",
        "C0 deal rate is at least 50 percent",
        "offer-parse rate is at least 90 percent",
        "Do not run more than the 1-episode smoke",
        "Do not run more than the 40-episode C0/C1 pilot",
        "Total EN-ID",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in normalized_text]
    if missing:
        return fail("budget.md is missing required budget details: " + "; ".join(missing))

    required_sections = [
        "## Scope",
        "## Run Gates",
        "## Episode Budget",
        "## Resource Budget",
        "## Artifact Budget",
        "## Stop Rules",
    ]
    missing_sections = [section for section in required_sections if section not in text]
    if missing_sections:
        return fail("budget.md is missing sections: " + ", ".join(missing_sections))

    total_match = re.search(r"\|\s*Total EN-ID\s*\|\s*(\d+)\s*\|", text)
    if not total_match:
        return fail("budget.md must include a Total EN-ID row with an episode count")
    if int(total_match.group(1)) != 300:
        return fail("Total EN-ID episode budget must be 300 for the gated full matrix")

    print("OK: budget.md defines gated model, episode, artifact, and stop-rule budgets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
