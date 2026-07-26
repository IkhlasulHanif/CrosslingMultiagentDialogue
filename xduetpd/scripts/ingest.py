#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ["EN", "ID", "ZH", "ES", "AR", "HI", "SW", "JV"]
GLOBAL_MMLU_LANG = {
    "EN": "en",
    "ID": "id",
    "ZH": "zh",
    "ES": "es",
    "AR": "ar",
    "HI": "hi",
    "SW": "sw",
}
MULTIJAIL_URL = "https://huggingface.co/datasets/DAMO-NLP-SG/MultiJail/resolve/main/MultiJail.csv"
OPINION_URL = "https://huggingface.co/datasets/Anthropic/llm_global_opinions/resolve/main/data/global_opinions.csv"


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
    details.extend(configure_tls())
    try:
        from datasets import load_dataset
    except Exception as exc:
        return False, [f"datasets import failed: {exc}"]
    details.append("datasets import available")
    ok = True
    try:
        s1_count = ingest_global_mmlu(load_dataset, details)
        details.append(f"Global-MMLU downloaded CA-aligned rows: {s1_count}")
    except Exception as exc:
        ok = False
        details.append(f"Global-MMLU ingest not completed: {exc}")
    try:
        s2_count = ingest_multijail(details)
        details.append(f"MultiJail downloaded rows: {s2_count}")
    except Exception as exc:
        ok = False
        details.append(f"MultiJail ingest not completed: {exc}")
    try:
        s3_count = ingest_global_opinion(details)
        details.append(f"GlobalOpinionQA downloaded rows: {s3_count}")
    except Exception as exc:
        ok = False
        details.append(f"GlobalOpinionQA ingest not completed: {exc}")
    return ok, details


def configure_tls() -> list[str]:
    details: list[str] = []
    if os.environ.get("REQUESTS_CA_BUNDLE") and os.environ.get("SSL_CERT_FILE"):
        details.append("TLS bundle supplied by environment")
        return details
    certifi_path: str | None = None
    try:
        import certifi

        certifi_path = certifi.where()
    except Exception as exc:
        details.append(f"certifi unavailable: {exc}")
    roots = find_macos_certificates("Zscaler Root CA")
    if not certifi_path or not roots:
        details.append("no local Zscaler CA bundle generated")
        return details
    bundle = ROOT / ".cache" / "hf_ca_bundle.pem"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    with bundle.open("wb") as out:
        out.write(Path(certifi_path).read_bytes())
        out.write(b"\n")
        for cert in roots:
            out.write(cert)
            out.write(b"\n")
    os.environ["REQUESTS_CA_BUNDLE"] = str(bundle)
    os.environ["SSL_CERT_FILE"] = str(bundle)
    details.append(f"generated local HF CA bundle: {bundle.relative_to(ROOT)}")
    return details


def find_macos_certificates(common_name: str) -> list[bytes]:
    if not shutil.which("security"):
        return []
    certs: list[bytes] = []
    keychains = [
        "/Library/Keychains/System.keychain",
        str(Path.home() / "Library/Keychains/login.keychain-db"),
    ]
    for keychain in keychains:
        if not Path(keychain).exists():
            continue
        proc = subprocess.run(
            ["security", "find-certificate", "-a", "-p", "-c", common_name, keychain],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if proc.stdout:
            certs.append(proc.stdout)
    return certs


def ingest_global_mmlu(load_dataset, details: list[str]) -> int:
    out_path = ROOT / "data" / "s1" / "items.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    selected = select_global_mmlu_ids(load_dataset, target_n=100)
    variants_by_lang: dict[str, dict[str, dict[str, Any]]] = {}
    wanted = set(selected)
    for lang, config_name in GLOBAL_MMLU_LANG.items():
        rows: dict[str, dict[str, Any]] = {}
        ds = load_dataset("CohereLabs/Global-MMLU", config_name, split="test", streaming=True)
        for row in ds:
            sample_id = str(row.get("sample_id"))
            if sample_id in wanted:
                rows[sample_id] = row
            if len(rows) == len(wanted):
                break
        missing = sorted(wanted - set(rows))
        if missing:
            details.append(f"Global-MMLU {lang} missing aligned ids: {missing[:5]}")
        variants_by_lang[lang] = rows
    count = 0
    with out_path.open("w", encoding="utf-8") as handle:
        for sample_id in selected:
            en_row = variants_by_lang["EN"].get(sample_id)
            if not en_row:
                continue
            item = {
                "id": sample_id.replace("/", "_"),
                "source": "CohereLabs/Global-MMLU",
                "subject": en_row.get("subject", "unknown"),
                "gold": normalize_gold(en_row.get("answer")),
                "variants": {},
                "metadata": {
                    "sample_id": sample_id,
                    "cultural_sensitivity_label": en_row.get("cultural_sensitivity_label"),
                    "jv_status": "missing_translation_review_required",
                },
            }
            for lang in GLOBAL_MMLU_LANG:
                row = variants_by_lang[lang].get(sample_id)
                if row:
                    item["variants"][lang] = global_mmlu_variant(row)
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    write_jv_review_for_ids(selected)
    return count


def select_global_mmlu_ids(load_dataset, target_n: int) -> list[str]:
    ds = load_dataset("CohereLabs/Global-MMLU", "en", split="test", streaming=True)
    by_subject: dict[str, list[str]] = {}
    for row in ds:
        if str(row.get("cultural_sensitivity_label")) != "CA":
            continue
        subject = str(row.get("subject") or "unknown")
        by_subject.setdefault(subject, []).append(str(row["sample_id"]))
        total = sum(len(values) for values in by_subject.values())
        if total >= target_n * 4:
            break
    selected: list[str] = []
    while len(selected) < target_n and any(by_subject.values()):
        for subject in sorted(by_subject):
            if by_subject[subject] and len(selected) < target_n:
                selected.append(by_subject[subject].pop(0))
    if len(selected) < target_n:
        raise RuntimeError(f"only found {len(selected)} Global-MMLU CA items")
    return selected


def global_mmlu_variant(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "question": row["question"],
        "options": {
            "A": row["option_a"],
            "B": row["option_b"],
            "C": row["option_c"],
            "D": row["option_d"],
        },
    }


def normalize_gold(answer: Any) -> str:
    value = str(answer).strip().upper()
    if value in {"A", "B", "C", "D"}:
        return value
    if value in {"0", "1", "2", "3"}:
        return "ABCD"[int(value)]
    raise ValueError(f"unsupported answer label: {answer}")


def ingest_multijail(details: list[str]) -> int:
    text = download_text(MULTIJAIL_URL)
    out_path = ROOT / "data" / "s2" / "items.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(io.StringIO(text.lstrip("\ufeff"))))
    required = {"en", "sw", "jv"}
    if not rows or not required.issubset(rows[0]):
        raise RuntimeError("MultiJail missing required en/sw/jv columns")
    lang_columns = {"EN": "en", "ZH": "zh", "AR": "ar", "SW": "sw", "JV": "jv"}
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            item = {
                "id": f"multijail_{row['id']}",
                "source": "DAMO-NLP-SG/MultiJail",
                "tags": row.get("tags"),
                "variants": {
                    lang: {"prompt": row[column]}
                    for lang, column in lang_columns.items()
                    if row.get(column)
                },
            }
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    details.append("MultiJail JV and SW columns present")
    return len(rows)


def ingest_global_opinion(details: list[str]) -> int:
    text = download_text(OPINION_URL)
    out_path = ROOT / "data" / "s3" / "items.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(io.StringIO(text)))
    kept = []
    for row in rows:
        if len(kept) >= 60:
            break
        if country_count(row.get("selections", "")) >= 5:
            kept.append(row)
    with out_path.open("w", encoding="utf-8") as handle:
        for idx, row in enumerate(kept):
            item = {
                "id": f"global_opinion_{idx:03d}",
                "source": "Anthropic/llm_global_opinions",
                "question": row.get("question"),
                "options": row.get("options"),
                "selections": row.get("selections"),
                "survey_source": row.get("source"),
            }
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    details.append(f"GlobalOpinionQA rows with >=5 countries: {len(kept)}")
    return len(kept)


def country_count(raw: str) -> int:
    return raw.count("': [") + raw.count('": [')


def download_text(url: str) -> str:
    proc = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "120", url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))
    return proc.stdout.decode("utf-8-sig")


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


def write_jv_review_for_ids(sample_ids: list[str]) -> None:
    write_jv_review()
    path = ROOT / "data" / "s1" / "jv_review.csv"
    existing = path.read_text(encoding="utf-8")
    with path.open("a", encoding="utf-8", newline="") as handle:
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
        for sample_id in sample_ids:
            item_id = sample_id.replace("/", "_")
            if item_id in existing:
                continue
            writer.writerow(
                {
                    "item_id": item_id,
                    "source_lang": "EN",
                    "mt_engine_1": "",
                    "mt_engine_2": "",
                    "backtranslation_1": "",
                    "backtranslation_2": "",
                    "chrf_engine_pair": "",
                    "chrf_vs_source": "",
                    "flagged": "true",
                    "adjudicated": "false",
                    "adjudicator": "",
                    "notes": "JV translation pending; M1 cannot pass until adjudicated.",
                }
            )


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
