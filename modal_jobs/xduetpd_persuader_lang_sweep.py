from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import modal


APP_NAME = "xduetpd-persuader-lang-sweep"
VOLUME_NAME = "xduetpd-runs"
DEFAULT_LANGUAGES = ("EN", "ID", "ZH", "ES", "AR", "HI", "SW")
DEFAULT_DIRECTIONS = ("misleading", "corrective")
DEFAULT_SEEDS = (1001, 2001, 3001, 4001, 5001)

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_XDUETPD = REPO_ROOT / "xduetpd"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("certifi", "jsonschema", "pyyaml")
    .add_local_dir(LOCAL_XDUETPD / "runner", remote_path="/root/xduetpd/runner", copy=True)
    .add_local_dir(LOCAL_XDUETPD / "data", remote_path="/root/xduetpd/data", copy=True)
    .add_local_dir(LOCAL_XDUETPD / "configs", remote_path="/root/xduetpd/configs", copy=True)
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-api-key")],
    volumes={"/outputs": volume},
    timeout=60 * 60 * 24,
)
def run_sweep(
    n_dialogues: int = 30,
    languages_csv: str = "",
    directions_csv: str = "",
    run_label: str = "",
    model_t: str = "gpt-4o-mini",
    model_p: str = "gpt-4o-mini",
) -> dict[str, Any]:
    os.environ["XDUETPD_PROVIDER"] = "openai"
    languages = _parse_languages(languages_csv)
    directions = _parse_directions(directions_csv)
    run_label = run_label or _default_run_label(n_dialogues, languages, directions)

    source = Path("/root/xduetpd")
    work = Path("/tmp/xduetpd_run")
    output_dir = Path("/outputs") / run_label
    _prepare_workdir(source, work, output_dir)

    sys.path.insert(0, str(work))
    from runner.dialogue import run_cell
    from runner.providers import build_provider

    provider = build_provider("openai")
    configs = [
        _cell_config(
            persuader_lang=persuader_lang,
            direction=direction,
            n_dialogues=n_dialogues,
            model_t=model_t,
            model_p=model_p,
        )
        for persuader_lang in languages
        for direction in directions
    ]

    (output_dir / "configs").mkdir(parents=True, exist_ok=True)
    (output_dir / "configs" / "cells.json").write_text(
        json.dumps(configs, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_progress(output_dir, run_label, configs, [], "running")
    volume.commit()

    results: list[dict[str, Any]] = []
    for config in configs:
        result = run_cell(config, provider, work)
        results.append(result)
        _sync_outputs(work, output_dir)
        _write_progress(output_dir, run_label, configs, results, "running")
        volume.commit()

    summary = _summarize_results(work)
    final = {
        "status": "done",
        "run_label": run_label,
        "volume": VOLUME_NAME,
        "output_path": str(output_dir),
        "n_dialogues_per_cell": n_dialogues,
        "target_lang": "EN",
        "persuader_langs": languages,
        "directions": directions,
        "model_T": model_t,
        "model_P": model_p,
        "cells_planned": len(configs),
        "cells_finished": len(results),
        "cell_results": results,
        "metrics": summary,
        "finished_at": datetime.now(UTC).isoformat(),
    }
    _sync_outputs(work, output_dir)
    (output_dir / "summary.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_markdown_report(output_dir, final)
    _write_progress(output_dir, run_label, configs, results, "done")
    volume.commit()
    return final


@app.local_entrypoint()
def main(
    n_dialogues: int = 30,
    languages: str = "",
    directions: str = "",
    run_label: str = "",
    model_t: str = "gpt-4o-mini",
    model_p: str = "gpt-4o-mini",
) -> None:
    planned_langs = _parse_languages(languages)
    planned_dirs = _parse_directions(directions)
    label = run_label or _default_run_label(n_dialogues, planned_langs, planned_dirs)
    call = run_sweep.spawn(
        n_dialogues=n_dialogues,
        languages_csv=languages,
        directions_csv=directions,
        run_label=label,
        model_t=model_t,
        model_p=model_p,
    )
    print(
        json.dumps(
            {
                "status": "spawned",
                "app": APP_NAME,
                "function_call_id": call.object_id,
                "dashboard_url": call.get_dashboard_url(),
                "volume": VOLUME_NAME,
                "output_path": f"/{label}",
                "target_lang": "EN",
                "persuader_langs": planned_langs,
                "directions": planned_dirs,
                "n_dialogues_per_cell": n_dialogues,
                "model_T": model_t,
                "model_P": model_p,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _cell_config(
    *,
    persuader_lang: str,
    direction: str,
    n_dialogues: int,
    model_t: str,
    model_p: str,
) -> dict[str, Any]:
    lang_slug = persuader_lang.lower()
    return {
        "cell_id": f"plang_ten_p{lang_slug}_{direction}_{_model_slug(model_t)}_n{n_dialogues}",
        "phase": "persuader_lang_sweep",
        "target_lang": "EN",
        "persuader_lang": persuader_lang,
        "direction": direction,
        "persona": "none",
        "reasoning": "native",
        "model_T": model_t,
        "model_P": model_p,
        "n_dialogues": n_dialogues,
        "stimulus_set": "s1",
        "seeds": list(DEFAULT_SEEDS),
        "temperature_dialogue": 0.7,
        "probe_k": 8,
    }


def _prepare_workdir(source: Path, work: Path, output_dir: Path) -> None:
    if work.exists():
        shutil.rmtree(work)
    (work / "results").mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / "runner", work / "runner")
    shutil.copytree(source / "data", work / "data")
    shutil.copytree(source / "configs", work / "configs")

    previous_results = output_dir / "results"
    previous_inspect = output_dir / "inspect"
    if previous_results.exists():
        shutil.copytree(previous_results, work / "results", dirs_exist_ok=True)
    if previous_inspect.exists():
        shutil.copytree(previous_inspect, work / "inspect", dirs_exist_ok=True)


def _sync_outputs(work: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("results", "inspect"):
        src = work / name
        if src.exists():
            shutil.copytree(src, output_dir / name, dirs_exist_ok=True)


def _write_progress(
    output_dir: Path,
    run_label: str,
    configs: list[dict[str, Any]],
    results: list[dict[str, Any]],
    status: str,
) -> None:
    completed = {result.get("cell_id") for result in results}
    rows = []
    for config in configs:
        rows.append(
            {
                "cell_id": config["cell_id"],
                "target_lang": config["target_lang"],
                "persuader_lang": config["persuader_lang"],
                "direction": config["direction"],
                "n_dialogues": config["n_dialogues"],
                "status": "done" if config["cell_id"] in completed else "todo",
            }
        )
    payload = {
        "status": status,
        "run_label": run_label,
        "updated_at": datetime.now(UTC).isoformat(),
        "cells_done": len(completed),
        "cells_planned": len(configs),
        "cells": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "progress.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _summarize_results(work: Path) -> dict[str, Any]:
    per_cell = []
    aggregate = {
        "dialogues": 0,
        "excluded": 0,
        "ftw": 0,
        "ftr": 0,
        "final_is_gold": 0,
    }
    for path in sorted((work / "results" / "summaries").glob("*.jsonl")):
        rows = [_read_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [row for row in rows if row]
        if not rows:
            continue
        valid = [row for row in rows if not row.get("excluded")]
        record = {
            "cell_id": rows[0].get("cell_id", path.stem),
            "target_lang": rows[0].get("target_lang"),
            "persuader_lang": rows[0].get("persuader_lang"),
            "direction": rows[0].get("direction"),
            "dialogues": len(rows),
            "excluded": len(rows) - len(valid),
            "ftw": sum(1 for row in valid if row.get("ftw")),
            "ftr": sum(1 for row in valid if row.get("ftr")),
            "final_is_gold": sum(1 for row in valid if row.get("final_is_gold")),
        }
        denominator = max(1, len(valid))
        record["ftw_rate"] = record["ftw"] / denominator
        record["ftr_rate"] = record["ftr"] / denominator
        record["final_gold_rate"] = record["final_is_gold"] / denominator
        per_cell.append(record)
        aggregate["dialogues"] += record["dialogues"]
        aggregate["excluded"] += record["excluded"]
        aggregate["ftw"] += record["ftw"]
        aggregate["ftr"] += record["ftr"]
        aggregate["final_is_gold"] += record["final_is_gold"]

    valid_total = max(1, aggregate["dialogues"] - aggregate["excluded"])
    aggregate["ftw_rate"] = aggregate["ftw"] / valid_total
    aggregate["ftr_rate"] = aggregate["ftr"] / valid_total
    aggregate["final_gold_rate"] = aggregate["final_is_gold"] / valid_total
    return {"aggregate": aggregate, "per_cell": per_cell}


def _write_markdown_report(output_dir: Path, final: dict[str, Any]) -> None:
    metrics = final["metrics"]
    lines = [
        "# X-DuET-PD Persuader-Language Sweep",
        "",
        f"- status: {final['status']}",
        "- target_lang: EN",
        f"- persuader_langs: {', '.join(final['persuader_langs'])}",
        f"- directions: {', '.join(final['directions'])}",
        f"- n_dialogues_per_cell: {final['n_dialogues_per_cell']}",
        f"- model_T: {final['model_T']}",
        f"- model_P: {final['model_P']}",
        "",
        "## Aggregate",
        "",
        f"- dialogues: {metrics['aggregate']['dialogues']}",
        f"- excluded: {metrics['aggregate']['excluded']}",
        f"- FtW rate: {metrics['aggregate']['ftw_rate']:.3f}",
        f"- FtR rate: {metrics['aggregate']['ftr_rate']:.3f}",
        f"- final gold rate: {metrics['aggregate']['final_gold_rate']:.3f}",
        "",
        "## Cells",
        "",
        "| cell | P lang | direction | n | excluded | FtW | FtR | final gold |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics["per_cell"]:
        lines.append(
            "| {cell_id} | {persuader_lang} | {direction} | {dialogues} | {excluded} | "
            "{ftw_rate:.3f} | {ftr_rate:.3f} | {final_gold_rate:.3f} |".format(**row)
        )
    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_languages(raw: str) -> list[str]:
    if not raw:
        return list(DEFAULT_LANGUAGES)
    parsed = [part.strip().upper() for part in raw.split(",") if part.strip()]
    if not parsed:
        return list(DEFAULT_LANGUAGES)
    return parsed


def _parse_directions(raw: str) -> list[str]:
    if not raw:
        return list(DEFAULT_DIRECTIONS)
    parsed = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not parsed:
        return list(DEFAULT_DIRECTIONS)
    unknown = sorted(set(parsed) - set(DEFAULT_DIRECTIONS))
    if unknown:
        raise ValueError(f"unsupported directions: {', '.join(unknown)}")
    return parsed


def _default_run_label(n_dialogues: int, languages: list[str], directions: list[str]) -> str:
    lang_slug = "-".join(lang.lower() for lang in languages)
    direction_slug = "-".join(direction[0] for direction in directions)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"plang_ten_{lang_slug}_{direction_slug}_n{n_dialogues}_{stamp}"


def _model_slug(model: str) -> str:
    return model.replace("gpt-", "").replace("-", "")


def _read_json(line: str) -> dict[str, Any] | None:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None
