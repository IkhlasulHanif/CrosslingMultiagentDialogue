#!/usr/bin/env python3
"""Rank language-steered generations for possible opinion divergence seeds.

This is an artifact scanner, not a model runner. It consumes JSON from
saved steering probes and flags prompts where baseline and steered generations
move in different heuristic stance directions. These are candidate seeds for
manual inspection or later BiVaD runs; the script does not instruct a stance and
does not fabricate agent priors.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUPPORT_TERMS = (
    "should release",
    "public access",
    "open",
    "transparency",
    "accountability",
    "civic",
    "release",
    "share",
    "akses publik",
    "terbuka",
    "transparansi",
    "akuntabilitas",
    "acceso publico",
    "acceso público",
    "abierto",
    "transparencia",
)

CAUTION_TERMS = (
    "restrict",
    "restriction",
    "risk",
    "misuse",
    "harm",
    "safeguard",
    "control",
    "security",
    "withhold",
    "limit",
    "risiko",
    "penyalahgunaan",
    "bahaya",
    "pengaman",
    "keamanan",
    "membatasi",
    "riesgo",
    "mal uso",
    "daño",
    "salvaguarda",
    "seguridad",
    "limitar",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Steering JSON artifacts or directories.")
    parser.add_argument("--glob", default="*.json")
    parser.add_argument("--out", default="code/bivad-evidence-audit/divergence_scan.json")
    parser.add_argument("--min-score-delta", type=float, default=1.0)
    return parser.parse_args()


def discover(inputs: list[str], glob_pattern: str) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            paths.extend(path.rglob(glob_pattern))
        elif path.is_file():
            paths.append(path)
    return sorted({path.resolve() for path in paths})


def term_count(text: str, terms: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if re.search(rf"\b{re.escape(term)}\b", lowered))


def stance_score(text: str) -> dict[str, Any]:
    support = term_count(text, SUPPORT_TERMS)
    caution = term_count(text, CAUTION_TERMS)
    score = support - caution
    if score > 0:
        label = "access_leaning"
    elif score < 0:
        label = "caution_leaning"
    else:
        label = "undetermined"
    return {"support_terms": support, "caution_terms": caution, "score": score, "label": label}


def scan_artifact(path: Path, min_score_delta: float) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = []
    for item in data.get("generations", []):
        if not isinstance(item, dict):
            continue
        baseline = str(item.get("baseline", ""))
        steered = str(item.get("steered", ""))
        baseline_score = stance_score(baseline)
        steered_score = stance_score(steered)
        delta = float(steered_score["score"] - baseline_score["score"])
        candidate = (
            abs(delta) >= min_score_delta
            and baseline_score["label"] != "undetermined"
            and steered_score["label"] != "undetermined"
            and baseline_score["label"] != steered_score["label"]
        )
        rows.append(
            {
                "path": str(path),
                "model": data.get("model"),
                "target_lang": item.get("target_lang"),
                "prompt": item.get("prompt"),
                "baseline_stance": baseline_score,
                "steered_stance": steered_score,
                "score_delta": delta,
                "candidate_divergence_seed": candidate,
                "baseline_excerpt": baseline[:500],
                "steered_excerpt": steered[:500],
            }
        )
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Language-Steered Divergence Scan",
        "",
        f"Created at: `{report['created_at']}`",
        "",
        f"Rows scanned: `{report['summary']['row_count']}`",
        "",
        f"Candidate divergence seeds: `{report['summary']['candidate_count']}`",
        "",
    ]
    for row in report["ranked_rows"][:20]:
        lines.extend(
            [
                f"## `{row['target_lang']}` delta `{row['score_delta']}`",
                "",
                f"- Candidate: `{row['candidate_divergence_seed']}`",
                f"- Prompt: {row['prompt']}",
                f"- Baseline stance: `{row['baseline_stance']['label']}`",
                f"- Steered stance: `{row['steered_stance']['label']}`",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    for path in discover(args.inputs, args.glob):
        rows.extend(scan_artifact(path, args.min_score_delta))
    rows.sort(key=lambda row: (not row["candidate_divergence_seed"], -abs(row["score_delta"])))
    report = {
        "artifact_type": "language_steering_divergence_scan",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "row_count": len(rows),
            "candidate_count": sum(1 for row in rows if row["candidate_divergence_seed"]),
            "min_score_delta": args.min_score_delta,
        },
        "ranked_rows": rows,
        "note": "Heuristic ranking for follow-up only; not a substitute for manual or judge validation.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    out.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Wrote {out.with_suffix('.md')}")
    return 0 if report["summary"]["candidate_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
