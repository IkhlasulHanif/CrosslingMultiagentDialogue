#!/usr/bin/env python3
"""Run CAA (Contrastive Activation Addition) language steering probe on Modal GPU.

CAA uses instruction-contrast pairs to compute a steering vector in the
instruction-following subspace rather than the language-content subspace.
This is more targeted than mean hidden-state differences from parallel corpora.

Usage:
    modal run code/modal_steer_language_caa.py \\
        --model-id Qwen/Qwen2.5-1.5B-Instruct \\
        --layer-indices 14,16,18 \\
        --alpha-sweep 15,25,40,60
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE_CODE = "/root/repo/code"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.8.0",
        "transformers==4.53.2",
        "accelerate==1.8.1",
        "sentencepiece==0.2.0",
        "protobuf==6.31.1",
    )
    .add_local_file(
        REPO_ROOT / "code" / "steer_language_caa.py",
        remote_path=f"{REMOTE_CODE}/steer_language_caa.py",
        copy=True,
    )
)

app = modal.App("multilingual-value-drift-caa-steering", image=image)


@app.function(gpu="L4", timeout=60 * 90)
def run_probe(options: dict) -> str:
    out_path = "/root/caa_probe.json"
    cmd = [
        "python",
        f"{REMOTE_CODE}/steer_language_caa.py",
        "--model-id", str(options["model_id"]),
        "--out", out_path,
        "--max-new-tokens", str(options["max_new_tokens"]),
        "--layer-indices", str(options["layer_indices"]),
        "--temperature", str(options["temperature"]),
        "--top-p", str(options["top_p"]),
        "--device", "cuda",
        "--allow-download",
    ]
    for t in options["target_langs"]:
        cmd.extend(["--target-lang", str(t)])
    for pr in options.get("prompts") or []:
        cmd.extend(["--prompt", str(pr)])
    if options.get("alpha_sweep"):
        cmd.extend(["--alpha-sweep", str(options["alpha_sweep"])])
    else:
        cmd.extend(["--alpha", str(options["alpha"])])

    subprocess.run(cmd, check=True)
    return Path(out_path).read_text(encoding="utf-8")


@app.local_entrypoint()
def main(
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
    target_langs: str = "ind_Latn,spa_Latn",
    prompts: str = "",
    out_dir: str = "runs/language-steering-caa",
    max_new_tokens: int = 100,
    layer_indices: str = "14,16,18",
    alpha: float = 20.0,
    alpha_sweep: str = "15,25,40,60",
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> None:
    targets = [t.strip() for t in target_langs.split(",") if t.strip()]
    prompt_items = [p.strip() for p in prompts.split(",") if p.strip()] if prompts else []

    options = {
        "model_id": model_id,
        "target_langs": targets,
        "prompts": prompt_items,
        "max_new_tokens": max_new_tokens,
        "layer_indices": layer_indices,
        "alpha": alpha,
        "alpha_sweep": alpha_sweep,
        "temperature": temperature,
        "top_p": top_p,
    }
    text = run_probe.remote(options)
    report = json.loads(text)

    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-".join(report.get("targets") or ["targets"])
    ts = report["created_at"].replace(":", "").replace("+", "Z").replace("-", "")[:16]
    model_slug = report["model"].split("/")[-1].lower().replace(".", "-")
    alphas = report.get("alpha_values", [alpha])
    alpha_str = "_".join(str(int(a)) for a in alphas)
    layers = report.get("active_layers", [])
    layer_str = "L" + "_".join(str(l) for l in layers)
    out_path = output_dir / f"{ts}-{model_slug}-{layer_str}-a{alpha_str}-{suffix}.json"
    out_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")

    for row in report.get("generations", []):
        st = row["steered_language_heuristic"]
        bl = row["baseline_language_heuristic"]
        print(
            f"  {row['target_lang']}  alpha={row['alpha']:<5}  "
            f"baseline_hits={bl['stopword_hit_count']}  steered_hits={st['stopword_hit_count']}  "
            f"steered[:80]={row['steered'][:80]!r}"
        )
