#!/usr/bin/env python3
"""Summarize mechanistic language-steering probe artifacts.

This is an artifact-level validation gate for the checklist item that requires
language conditioning without prompt-level language instructions. It does not
run models; it inspects saved steering probes and reports whether any generated
row plausibly satisfies the minimum target-language validation criteria.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = (
    "runs/language-steering",
    "runs/language-steering-activation",
    "runs/language-steering-caa",
    "runs/archived/language-steering-activation",
    "runs/archived/language-steering-caa",
)

TARGET_STOPWORD_MIN = 3
MIN_WORDS = 18

DEGENERATION_MARKERS = (
    " {",
    " }",
    "\\[",
    "<F>",
    "<url>",
    ".pdf",
    "http://",
    "https://",
    "statement A.",
    "Group. B.",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        nargs="*",
        default=list(DEFAULT_INPUTS),
        help="Artifact files or directories containing steering JSON files.",
    )
    parser.add_argument("--out-dir", default="code/bivad-evidence-audit")
    parser.add_argument("--target-stopword-min", type=int, default=TARGET_STOPWORD_MIN)
    parser.add_argument("--min-words", type=int, default=MIN_WORDS)
    return parser.parse_args()


def iter_json_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_file() and path.suffix == ".json":
            paths.append(path)
        elif path.is_dir():
            paths.extend(sorted(path.glob("*.json")))
    return sorted(dict.fromkeys(paths))


def token_repetition_rate(text: str) -> float:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", text.lower())
    if not words:
        return 1.0
    counts = Counter(words)
    return max(counts.values()) / len(words)


def has_repeated_short_pattern(text: str) -> bool:
    lowered = text.lower()
    patterns = re.findall(r"\b([a-z]{1,4})\b(?:[\s.]+\\?\b\1\b){3,}", lowered)
    return bool(patterns)


def classify_generation(row: dict[str, Any], *, target_stopword_min: int, min_words: int) -> dict[str, Any]:
    steered = str(row.get("steered") or "")
    heuristic = row.get("steered_language_heuristic") or {}
    stopword_hits = int(heuristic.get("stopword_hit_count") or 0)
    words = re.findall(r"\S+", steered)
    repetition_rate = token_repetition_rate(steered)
    markers = [marker for marker in DEGENERATION_MARKERS if marker in steered]
    markup_or_symbol_ratio = sum(
        1 for ch in steered if ch in "<>{}[]\\|`#$*_=~"
    ) / max(len(steered), 1)
    degenerate = (
        len(words) < min_words
        or repetition_rate >= 0.18
        or has_repeated_short_pattern(steered)
        or bool(markers)
        or markup_or_symbol_ratio >= 0.08
    )
    target_language_candidate = stopword_hits >= target_stopword_min
    passes = target_language_candidate and not degenerate
    blockers: list[str] = []
    if not target_language_candidate:
        blockers.append(
            f"target-language evidence below threshold "
            f"({stopword_hits} < {target_stopword_min} stopword hits)"
        )
    if degenerate:
        blockers.append(
            "degenerate or too-short output "
            f"(words={len(words)}, max_token_repetition={repetition_rate:.3f})"
        )
    return {
        "target_lang": row.get("target_lang"),
            "alpha": row.get("alpha"),
        "prompt": row.get("prompt"),
        "stopword_hit_count": stopword_hits,
        "stopword_hits": heuristic.get("stopword_hits") or [],
        "word_count": len(words),
        "max_token_repetition": round(repetition_rate, 4),
        "markup_or_symbol_ratio": round(markup_or_symbol_ratio, 4),
        "degeneration_markers": markers,
        "target_language_candidate": target_language_candidate,
        "degenerate": degenerate,
        "passes_minimum_validation": passes,
        "blockers": blockers,
        "steered_excerpt": steered[:240].replace("\n", " "),
    }


def method_family(report: dict[str, Any]) -> str:
    artifact_type = str(report.get("artifact_type") or "")
    if "caa" in artifact_type:
        return "caa_instruction_contrast"
    if "activation" in artifact_type:
        return "flores_activation_steering"
    if "probability" in artifact_type or "language_probability" in artifact_type:
        return "flores_logit_bias"
    return artifact_type or "unknown"


def summarize_artifact(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    rows = report.get("generations") or []
    classified = [
        classify_generation(
            row,
            target_stopword_min=args.target_stopword_min,
            min_words=args.min_words,
        )
        for row in rows
    ]
    passed = [row for row in classified if row["passes_minimum_validation"]]
    best_by_target: dict[str, dict[str, Any]] = {}
    for row in classified:
        target = str(row.get("target_lang") or "unknown")
        current = best_by_target.get(target)
        if current is None:
            best_by_target[target] = row
            continue
        row_key = (row["stopword_hit_count"], -int(row["degenerate"]), row["word_count"])
        current_key = (
            current["stopword_hit_count"],
            -int(current["degenerate"]),
            current["word_count"],
        )
        if row_key > current_key:
            best_by_target[target] = row

    return {
        "path": str(path),
        "artifact_type": report.get("artifact_type"),
        "method_family": method_family(report),
        "model": report.get("model"),
        "device": report.get("device"),
        "created_at": report.get("created_at"),
        "source_lang": report.get("source_lang"),
        "targets": report.get("targets") or [],
        "alpha_values": report.get("alpha_values") or [],
        "generation_count": len(classified),
        "validated_generation_count": len(passed),
        "passes_minimum_validation": bool(passed),
        "best_by_target": best_by_target,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines: list[str] = [
        "# Language Steering Summary",
        "",
        f"- Artifacts inspected: {report['summary']['artifact_count']}",
        f"- Generations inspected: {report['summary']['generation_count']}",
        f"- Validated fluent target-language generations: {report['summary']['validated_generation_count']}",
        f"- Overall status: {report['summary']['status']}",
        "",
        "Validation rule: a row must have at least "
        f"{report['config']['target_stopword_min']} target-language stopword hits, "
        f"at least {report['config']['min_words']} whitespace tokens, and no simple degeneration flags.",
        "",
        "## Method Summary",
        "",
        "| Method | Artifacts | Generations | Validated |",
        "|---|---:|---:|---:|",
    ]
    for method, stats in sorted(report["by_method"].items()):
        lines.append(
            f"| {method} | {stats['artifact_count']} | "
            f"{stats['generation_count']} | {stats['validated_generation_count']} |"
        )
    lines.extend(["", "## Best Rows By Artifact", ""])
    for artifact in report["artifacts"]:
        lines.append(
            f"### `{artifact['path']}`"
        )
        lines.append(
            f"- Method: {artifact['method_family']}; model: {artifact.get('model')}; "
            f"validated rows: {artifact['validated_generation_count']}/{artifact['generation_count']}"
        )
        for target, row in sorted(artifact["best_by_target"].items()):
            status = "PASS" if row["passes_minimum_validation"] else "FAIL"
            blockers = "; ".join(row["blockers"]) or "none"
            lines.append(
                f"- {target}: {status}; hits={row['stopword_hit_count']}; "
                f"words={row['word_count']}; rep={row['max_token_repetition']}; "
                f"blockers={blockers}"
            )
            lines.append(f"  - Excerpt: {row['steered_excerpt']}")
        lines.append("")
    lines.extend(["## Conclusion", "", report["summary"]["conclusion"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    artifacts = [summarize_artifact(path, args) for path in iter_json_paths(args.inputs)]
    by_method: dict[str, dict[str, int]] = defaultdict(lambda: {
        "artifact_count": 0,
        "generation_count": 0,
        "validated_generation_count": 0,
    })
    for artifact in artifacts:
        stats = by_method[artifact["method_family"]]
        stats["artifact_count"] += 1
        stats["generation_count"] += artifact["generation_count"]
        stats["validated_generation_count"] += artifact["validated_generation_count"]

    generation_count = sum(item["generation_count"] for item in artifacts)
    validated_count = sum(item["validated_generation_count"] for item in artifacts)
    status = "blocked_negative_result" if validated_count == 0 else "has_candidate_successes"
    conclusion = (
        "No saved mechanistic steering generation satisfies the minimum validation gate. "
        "The current evidence supports treating instruction-free language steering as "
        "empirically blocked for the tested Qwen2.5-1.5B-Instruct settings; the smallest "
        "next action is a new Modal run with a base non-instruction-tuned model or a "
        "larger chat-template-direction intervention."
        if validated_count == 0
        else "At least one saved generation passes the heuristic gate; inspect those rows manually before using them as evidence."
    )
    report = {
        "artifact_type": "language_steering_summary",
        "config": {
            "target_stopword_min": args.target_stopword_min,
            "min_words": args.min_words,
            "inputs": args.inputs,
        },
        "summary": {
            "artifact_count": len(artifacts),
            "generation_count": generation_count,
            "validated_generation_count": validated_count,
            "status": status,
            "conclusion": conclusion,
        },
        "by_method": dict(by_method),
        "artifacts": artifacts,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "language_steering_summary.json"
    md_path = out_dir / "language_steering_summary.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    write_markdown(report, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 1 if validated_count == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
