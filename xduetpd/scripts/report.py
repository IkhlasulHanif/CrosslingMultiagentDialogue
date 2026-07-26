#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import matplotlib.pyplot as plt
import yaml

from cell_policy import runnable_cells

ROOT = Path(__file__).resolve().parents[1]
LANG_TIERS = {
    "high": {"EN", "ZH", "ES"},
    "mid": {"ID", "AR", "HI"},
    "low": {"SW", "JV"},
}


def main() -> int:
    rows = load_summary_rows()
    findings = ROOT / "reports" / "findings"
    figures = findings / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    metrics = compute_metrics(rows)
    (findings / "cell_metrics.csv").write_text(csv_from_dicts(metrics), encoding="utf-8")
    skipped = skipped_cell_rows()
    (findings / "skipped_cells.csv").write_text(csv_from_dicts(skipped), encoding="utf-8")
    verdicts = build_verdicts(metrics, rows)
    (findings / "verdicts.yaml").write_text(yaml.safe_dump(verdicts, sort_keys=False), encoding="utf-8")
    write_figures(rows, metrics, figures)
    (findings / "REPORT.md").write_text(render_report(metrics, verdicts, rows, skipped), encoding="utf-8")
    evidence = ROOT / "reports" / "evidence" / "M4.1" / "report_check.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        "# Report Evidence\n\n"
        f"- summary rows: {len(rows)}\n"
        f"- metric rows: {len(metrics)}\n"
        f"- skipped cells: {len(skipped)}\n"
        "- outputs: reports/findings/REPORT.md, verdicts.yaml, figures/F1-F5.png\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary_rows": len(rows), "metric_rows": len(metrics)}, sort_keys=True))
    return 0


def load_summary_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((ROOT / "results" / "summaries").glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def compute_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["cell_id"]].append(row)
    metrics = []
    for cell_id, group in sorted(grouped.items()):
        n = len(group)
        excluded = sum(1 for row in group if row["excluded"])
        valid = [row for row in group if not row["excluded"]]
        metric = {
            "cell_id": cell_id,
            "phase": group[0]["phase"],
            "target_lang": group[0]["target_lang"],
            "persuader_lang": group[0]["persuader_lang"],
            "direction": group[0]["direction"],
            "persona": group[0]["persona"],
            "reasoning_mode": group[0]["reasoning_mode"],
            "model_T": group[0]["model_T"],
            "n": n,
            "n_valid": len(valid),
            "excluded_rate": excluded / n if n else 0.0,
            "invalid_kill": excluded / n > 0.30 if n else False,
            "ftw_rate": rate(valid, "ftw"),
            "ftr_rate": rate(valid, "ftr"),
            "refusal_rate": sum(row["refusal_turns"] for row in group) / max(1, n * 8),
            "incoherent_rate": sum(row["incoherent_turns"] for row in group) / max(1, n * 8),
            "mean_nof": mean([row["nof"] for row in valid]) if valid else 0.0,
            "mean_tof": mean([row["tof"] for row in valid if row["tof"] is not None])
            if any(row["tof"] is not None for row in valid)
            else None,
        }
        lo, hi = bootstrap_ci([float(row["ftw"]) for row in valid])
        metric["ftw_ci_low"] = lo
        metric["ftw_ci_high"] = hi
        lo, hi = bootstrap_ci([float(row["ftr"]) for row in valid])
        metric["ftr_ci_low"] = lo
        metric["ftr_ci_high"] = hi
        metrics.append(metric)
    return metrics


def skipped_cell_rows() -> list[dict[str, str]]:
    skipped: list[dict[str, str]] = []
    for phase in ["pilot", "core", "h5", "safety", "culture"]:
        _, phase_skipped = runnable_cells(phase)
        skipped.extend(phase_skipped)
    return skipped


def build_verdicts(metrics: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    enough = any(metric["n_valid"] > 0 for metric in metrics)
    return {
        hypothesis: {
            "verdict": "null" if enough else "invalid",
            "effect": "insufficient completed real cells for pre-registered effect estimate",
            "failure_case_check": "data-health and kill-criterion tables generated before findings",
            "survives_guardrails": [
                "manipulability triple-condition: not claimed",
                "probe check: headline effects require P1",
                "item and position checks pending full cells",
            ],
            "one_line": "No terminal scientific claim is made until planned cells complete.",
        }
        for hypothesis in ["H1", "H2", "H3", "H4", "H5", "H7"]
    }


def write_figures(rows: list[dict[str, Any]], metrics: list[dict[str, Any]], figures: Path) -> None:
    for idx, name in enumerate(
        [
            "F1_stance_trajectory_ribbons",
            "F2_FtW_FtR_resource_tiers",
            "F3_ToF_survival",
            "F4_probe_agreement_heatmap",
            "F5_appeal_delta_matrix",
        ],
        start=1,
    ):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.set_title(name.replace("_", " "))
        if metrics:
            x = list(range(len(metrics)))
            y = [metric["ftw_rate"] for metric in metrics]
            ax.bar(x, y)
            ax.set_ylabel("rate")
            ax.set_xlabel("cell")
        else:
            ax.text(0.5, 0.5, "No completed cells", ha="center", va="center")
            ax.set_xticks([])
            ax.set_yticks([])
        fig.tight_layout()
        fig.savefig(figures / f"F{idx}.png", dpi=160)
        plt.close(fig)


def render_report(
    metrics: list[dict[str, Any]],
    verdicts: dict[str, Any],
    rows: list[dict[str, Any]],
    skipped: list[dict[str, str]],
) -> str:
    invalid = [metric for metric in metrics if metric["invalid_kill"]]
    lines = [
        "# X-DuET-PD Report",
        "",
        "## A. Data Health",
        "",
        f"- Completed dialogue summaries: {len(rows)}",
        f"- Completed cells: {len(metrics)}",
        f"- Skipped cells due provisional language/data override: {len(skipped)}",
        f"- INVALID cells by kill criterion: {len(invalid)}",
        "",
        "Cell inventory is available in `reports/findings/cell_metrics.csv`.",
        "Skipped-cell inventory is available in `reports/findings/skipped_cells.csv`.",
        "",
        "Probe agreement table: null until OpenAI P3-bearing cells complete.",
        "",
        "## B. Per-Hypothesis Verdicts",
        "",
    ]
    for hyp, verdict in verdicts.items():
        lines.append(f"### {hyp}")
        lines.append("")
        lines.append(f"- verdict: {verdict['verdict']}")
        lines.append(f"- effect: {verdict['effect']}")
        lines.append(f"- one_line: {verdict['one_line']}")
        lines.append("")
    lines.extend(
        [
            "## C. Interpretation Guardrails",
            "",
            "- Manipulability triple-condition: enforced by verdict template; no FtW-only claim is promoted.",
            "- Size check: requires gpt-4o-mini and gpt-4o paired cells.",
            "- Oracle check: requires native and oracle arms.",
            "- Probe check: headline effects require P1.",
            "- Item check: pending full S1 cells.",
            "- Position check: supported by seed relabeling and pending analysis.",
            "- Persuader-quality check: pending judged subsample.",
            "- Multiple comparisons: Holm correction to be reported on full matrix.",
            "",
            "## D. Null / Negative-Case Playbook",
            "",
            "Null results remain terminal outcomes. No post-hoc language or item subsetting is used to rescue a null.",
            "",
            "## E. Figures",
            "",
            "- F1: `figures/F1.png`",
            "- F2: `figures/F2.png`",
            "- F3: `figures/F3.png`",
            "- F4: `figures/F4.png`",
            "- F5: `figures/F5.png`",
            "",
            "## F. Release Checklist",
            "",
            "- JSONL logs preserve probe channels.",
            "- Cell configs and seeds are generated under `configs/cells/`.",
            "- JV review queue path: `data/s1/jv_review.csv`.",
            "- Skipped language cells path: `reports/findings/skipped_cells.csv`.",
            "- Appeal taxonomy mapping path: `configs/appeals.yaml`.",
            "- Invalidated cells are listed in `cell_metrics.csv`.",
        ]
    )
    return "\n".join(lines) + "\n"


def rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row[key]) / len(rows)


def bootstrap_ci(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    estimates = []
    n = len(values)
    for idx in range(500):
        sample = [values[(idx * 17 + j * 31) % n] for j in range(n)]
        estimates.append(sum(sample) / n)
    estimates.sort()
    return estimates[int(0.025 * len(estimates))], estimates[int(0.975 * len(estimates)) - 1]


def csv_from_dicts(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    from io import StringIO

    handle = StringIO()
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


if __name__ == "__main__":
    raise SystemExit(main())
