#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ["EN", "ID", "ZH", "ES", "AR", "HI", "SW", "JV"]


def main() -> int:
    evidence = ROOT / "reports" / "evidence" / "M1.1"
    evidence.mkdir(parents=True, exist_ok=True)
    report = evidence / "ingest_report.md"
    strict = os.environ.get("XDUETPD_STRICT_INGEST", "1") == "1"
    use_sample = os.environ.get("XDUETPD_SAMPLE_INGEST", "0") == "1"
    findings: list[str] = []
    status = "pass"
    if use_sample:
        copy_sample_sets()
        findings.append("sample ingest enabled; this is scaffold evidence only")
        status = "sample"
    else:
        ok, details = ingest_real()
        findings.extend(details)
        if not ok:
            status = "blocked" if strict else "sample"
            if not strict:
                copy_sample_sets()
    write_jv_review()
    acceptance = run_acceptance_checks()
    if not acceptance["ok"]:
        status = "blocked" if strict else status
    report.write_text(render_report(status, findings, acceptance), encoding="utf-8")
    print(json.dumps({"status": status, "acceptance": acceptance}, sort_keys=True))
    return 1 if status == "blocked" else 0


def ingest_real() -> tuple[bool, list[str]]:
    details: list[str] = []
    try:
        from datasets import load_dataset
    except Exception as exc:
        return False, [f"datasets import failed: {exc}"]
    details.append("datasets import available")
    ok = True
    try:
        _ = load_dataset("CohereForAI/Global-MMLU", split="test", streaming=True)
        details.append("Global-MMLU streaming handle opened")
    except Exception as exc:
        ok = False
        details.append(f"Global-MMLU ingest not completed: {exc}")
    try:
        _ = load_dataset("DAMO-NLP-SG/MultiJail", split="train", streaming=True)
        details.append("MultiJail streaming handle opened")
    except Exception as exc:
        ok = False
        details.append(f"MultiJail ingest not completed: {exc}")
    try:
        _ = load_dataset("Anthropic/llm_global_opinions", split="train", streaming=True)
        details.append("GlobalOpinionQA streaming handle opened")
    except Exception as exc:
        ok = False
        details.append(f"GlobalOpinionQA ingest not completed: {exc}")
    return ok, details


def copy_sample_sets() -> None:
    mapping = {
        "s1_smoke.jsonl": ROOT / "data" / "s1" / "items.jsonl",
        "s2_smoke.jsonl": ROOT / "data" / "s2" / "items.jsonl",
        "s3_smoke.jsonl": ROOT / "data" / "s3" / "items.jsonl",
    }
    for src_name, dst in mapping.items():
        src = ROOT / "data" / "sample" / src_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def write_jv_review() -> None:
    path = ROOT / "data" / "s1" / "jv_review.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "item_id",
                "source_lang",
                "mt_engine_1",
                "mt_engine_2",
                "backtranslation_1",
                "backtranslation_2",
                "chrf_engine_pair",
                "chrf_vs_source",
                "flagged",
                "adjudicated",
                "adjudicator",
                "notes",
            ],
        )
        writer.writeheader()


def run_acceptance_checks() -> dict[str, Any]:
    path = ROOT / "data" / "s1" / "items.jsonl"
    failures: list[str] = []
    count = 0
    if not path.exists():
        return {"ok": False, "failures": ["missing data/s1/items.jsonl"], "items": 0}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            count += 1
            item = json.loads(line)
            variants = item.get("variants") or {}
            missing = [lang for lang in LANGUAGES if lang not in variants]
            if missing:
                failures.append(f"{item.get('id')}: missing languages {missing}")
            for lang, variant in variants.items():
                if set((variant.get("options") or {}).keys()) != {"A", "B", "C", "D"}:
                    failures.append(f"{item.get('id')}:{lang}: invalid option set")
            if item.get("gold") not in {"A", "B", "C", "D"}:
                failures.append(f"{item.get('id')}: invalid gold")
    leakage = leakage_scan()
    failures.extend(leakage)
    return {"ok": not failures, "failures": failures[:100], "items": count}


def leakage_scan() -> list[str]:
    failures: list[str] = []
    data_path = ROOT / "data" / "s1" / "items.jsonl"
    prompt_path = ROOT / "runner" / "prompts.py"
    if not data_path.exists() or not prompt_path.exists():
        return failures
    prompt_text = prompt_path.read_text(encoding="utf-8")
    with data_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            for variant in (item.get("variants") or {}).values():
                q = str(variant.get("question", "")).strip()
                if q and q in prompt_text:
                    failures.append(f"stimulus leakage in prompt template: {item.get('id')}")
    return failures


def render_report(status: str, details: list[str], acceptance: dict[str, Any]) -> str:
    lines = [
        "# Ingest Report",
        "",
        f"- status: {status}",
        f"- S1 items checked: {acceptance.get('items', 0)}",
        f"- acceptance ok: {acceptance.get('ok')}",
        "",
        "## Details",
        "",
    ]
    lines.extend(f"- {item}" for item in details)
    lines.extend(["", "## Failures", ""])
    failures = acceptance.get("failures") or []
    lines.extend(f"- {item}" for item in failures)
    if not failures:
        lines.append("- none")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
