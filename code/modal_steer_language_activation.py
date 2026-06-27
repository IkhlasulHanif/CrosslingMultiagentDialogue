#!/usr/bin/env python3
"""Run activation-steering language probe on Modal GPU.

Downloads FLORES-200 from HuggingFace inside the container, computes separate
language-level mean-pooled hidden-state centroids for English and each target
language, then adds alpha * normalized(target - English) via a forward hook
during generation.

Usage:
    modal run code/modal_steer_language_activation.py \\
        --model-id Qwen/Qwen2.5-7B \\
        --layer-idx 22 --alpha-sweep 5,10,20,40 \\
        --out-dir runs/language-steering-activation

    modal run code/modal_steer_language_activation.py \\
        --model-id Qwen/Qwen2.5-7B \\
        --layer-indices 20,22,24,26 --alpha-sweep 5,10,20,40
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE_CODE = "/root/repo/code"
REMOTE_FLORES = "/root/flores"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.8.0",
        "transformers==4.53.2",
        "accelerate==1.8.1",
        "sentencepiece==0.2.0",
        "protobuf==6.31.1",
        "datasets==3.6.0",
    )
    .add_local_file(REPO_ROOT / "code" / "steer_language_activation.py", remote_path=f"{REMOTE_CODE}/steer_language_activation.py", copy=True)
)

app = modal.App("multilingual-value-drift-activation-steering", image=image)


def _download_flores_hf(
    source_lang: str,
    target_langs: list[str],
    split: str,
    flores_dir: Path,
    max_pairs: int,
) -> None:
    from datasets import load_dataset  # type: ignore[import]

    flores_dir.mkdir(parents=True, exist_ok=True)
    all_langs = [source_lang, *target_langs]
    hf_split = "devtest" if split in ("devtest", "dev") else split

    for lang in all_langs:
        dest = flores_dir / f"{split}.{lang}"
        if dest.exists():
            continue
        ds = load_dataset("Muennighoff/flores200", lang, split=hf_split, trust_remote_code=True)
        sentences = [row["sentence"] for row in ds]
        if max_pairs > 0:
            sentences = sentences[:max_pairs]
        dest.write_text("\n".join(sentences), encoding="utf-8")
        print(f"  Downloaded {len(sentences)} FLORES sentences for {lang}")


@app.function(
    gpu="L4",
    timeout=60 * 90,
)
def run_probe(options: dict) -> str:
    remote_flores = Path(REMOTE_FLORES)
    _download_flores_hf(
        source_lang=str(options["source_lang"]),
        target_langs=[str(t) for t in options["target_langs"]],
        split=str(options["split"]),
        flores_dir=remote_flores,
        max_pairs=int(options["max_pairs"]),
    )

    out_path = "/root/activation_steering_probe.json"
    cmd = [
        "python",
        f"{REMOTE_CODE}/steer_language_activation.py",
        "--model-id", str(options["model_id"]),
        "--flores-dir", str(remote_flores),
        "--source-lang", str(options["source_lang"]),
        "--split", str(options["split"]),
        "--max-pairs", str(options["max_pairs"]),
        "--out", out_path,
        "--max-new-tokens", str(options["max_new_tokens"]),
        "--temperature", str(options["temperature"]),
        "--top-p", str(options["top_p"]),
        "--device", "cuda",
        "--allow-download",
    ]
    if options.get("layer_indices"):
        cmd.extend(["--layer-indices", str(options["layer_indices"])])
    else:
        cmd.extend(["--layer-idx", str(options.get("layer_idx", 14))])
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
    model_id: str = "Qwen/Qwen2.5-7B",
    source_lang: str = "eng_Latn",
    target_langs: str = "ind_Latn,spa_Latn",
    split: str = "devtest",
    max_pairs: int = 0,
    prompts: str = "",
    out_dir: str = "runs/language-steering-activation",
    max_new_tokens: int = 100,
    layer_idx: int = 22,
    layer_indices: str = "",
    alpha: float = 20.0,
    alpha_sweep: str = "5,10,20,40",
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> None:
    targets = [t.strip() for t in target_langs.split(",") if t.strip()]
    prompt_items = [p.strip() for p in prompts.split(",") if p.strip()] if prompts else []

    options = {
        "model_id": model_id,
        "source_lang": source_lang,
        "target_langs": targets,
        "split": split,
        "max_pairs": max_pairs,
        "prompts": prompt_items,
        "max_new_tokens": max_new_tokens,
        "layer_idx": layer_idx,
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
    active = report.get("active_layers", [layer_idx])
    layer_str = "L" + "_".join(str(l) for l in active)
    out_path = output_dir / f"{ts}-{model_slug}-{layer_str}-a{alpha_str}-{suffix}.json"
    out_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")

    # Print summary
    for row in report.get("generations", []):
        st = row["steered_language_heuristic"]
        bl = row["baseline_language_heuristic"]
        print(
            f"  {row['target_lang']}  alpha={row['alpha']:<5}  layers={row.get('active_layers',[])}  "
            f"baseline_hits={bl['stopword_hit_count']}  steered_hits={st['stopword_hit_count']}  "
            f"steered[:80]={row['steered'][:80]!r}"
        )
