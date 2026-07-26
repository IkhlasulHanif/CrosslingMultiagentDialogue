from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
JV_SKIP_OVERRIDE = ROOT / "reports" / "evidence" / "M1.1" / "jv_skip_override.md"


def jv_skip_active() -> bool:
    value = os.environ.get("XDUETPD_SKIP_JV", "").lower()
    return value in {"1", "true", "yes"} or JV_SKIP_OVERRIDE.exists()


def effective_target_lang(config: dict[str, Any]) -> str:
    return "EN" if config.get("persona") == "en_persona" else str(config["target_lang"])


def cell_skip_reason(config: dict[str, Any]) -> str | None:
    target_lang = str(config["target_lang"])
    persuader_lang = str(config.get("persuader_lang", target_lang))
    effective_lang = effective_target_lang(config)
    if jv_skip_active() and "JV" in {target_lang, persuader_lang, effective_lang}:
        return "JV skipped by provisional human override"

    stimulus_set = str(config.get("stimulus_set", "s1"))
    available = stimulus_langs(stimulus_set)
    if available and effective_lang not in available:
        return f"{stimulus_set} lacks complete {effective_lang} stimulus variants"
    return None


def runnable_cells(phase: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    runnable: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for config in load_cell_configs(phase):
        reason = cell_skip_reason(config)
        if reason:
            skipped.append({"cell_id": config["cell_id"], "phase": phase, "reason": reason})
        else:
            runnable.append(config)
    return runnable, skipped


def load_cell_configs(phase: str | None = None) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []
    for path in sorted((ROOT / "configs" / "cells").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if phase is None or data.get("phase") == phase:
            configs.append(data)
    return configs


def write_skip_report(phase: str, skipped: list[dict[str, str]]) -> None:
    report = ROOT / "reports" / "evidence" / "run" / f"skipped_{phase}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Skipped Cells: {phase}", "", f"- skipped: {len(skipped)}", ""]
    for row in skipped:
        lines.append(f"- {row['cell_id']}: {row['reason']}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


@lru_cache(maxsize=None)
def stimulus_langs(stimulus_set: str) -> frozenset[str]:
    path = stimulus_path(stimulus_set)
    if not path.exists():
        return frozenset()
    counts: dict[str, int] = {}
    rows = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows += 1
            data = json.loads(line)
            variants = data.get("variants") or {}
            langs = set(variants) if variants else {"EN"}
            for lang in langs:
                counts[lang] = counts.get(lang, 0) + 1
    return frozenset(lang for lang, count in counts.items() if rows and count == rows)


def stimulus_path(stimulus_set: str) -> Path:
    if "/" in stimulus_set:
        return ROOT / "data" / f"{stimulus_set}.jsonl"
    return ROOT / "data" / stimulus_set / "items.jsonl"
