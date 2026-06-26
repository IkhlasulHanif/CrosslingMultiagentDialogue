#!/usr/bin/env python3
"""Run `code/steer_language.py` on Modal GPU.

Two modes:
- Local FLORES (default): pass --flores-dir pointing to a local FLORES-200 directory.
- HF FLORES (--hf-flores): skip local FLORES requirement; the Modal container downloads
  FLORES-200 sentences from Hugging Face datasets (facebook/flores200 or Muennighoff/flores200)
  and feeds them to steer_language.py automatically.

Usage examples:
    # Download FLORES inside Modal (no local files needed):
    modal run code/modal_steer_language.py --hf-flores \\
        --model-id Qwen/Qwen2.5-1.5B-Instruct

    # Use local FLORES directory:
    modal run code/modal_steer_language.py \\
        --flores-dir /path/to/flores200 \\
        --model-id Qwen/Qwen2.5-1.5B-Instruct
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
    .add_local_dir(REPO_ROOT / "code", remote_path=REMOTE_CODE)
)

app = modal.App("multilingual-value-drift-steering", image=image)


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _download_flores_hf(
    source_lang: str,
    target_langs: list[str],
    split: str,
    flores_dir: Path,
    max_pairs: int,
) -> None:
    """Download FLORES-200 sentences from HuggingFace into flores_dir.

    Tries 'Muennighoff/flores200' first, then falls back to inline devtest
    sentence pairs embedded directly if the dataset is unavailable.
    """
    from datasets import load_dataset  # type: ignore[import]

    flores_dir.mkdir(parents=True, exist_ok=True)
    all_langs = [source_lang, *target_langs]

    # FLORES-200 HF split names: 'devtest' is common; try both
    hf_split = "devtest" if split in ("devtest", "dev") else split
    for lang in all_langs:
        dest = flores_dir / f"{split}.{lang}"
        if dest.exists():
            continue
        try:
            ds = load_dataset("Muennighoff/flores200", lang, split=hf_split, trust_remote_code=True)
            sentences = [row["sentence"] for row in ds][:max_pairs]
        except Exception as e:
            raise RuntimeError(
                f"Could not download FLORES-200 for lang={lang} split={hf_split}: {e}"
            ) from e
        dest.write_text("\n".join(sentences), encoding="utf-8")
        print(f"  Downloaded {len(sentences)} sentences for {lang} → {dest}")


@app.function(
    gpu="L4",
    timeout=60 * 60,
)
def run_probe(options: dict[str, object]) -> str:
    remote_flores = Path(REMOTE_FLORES)

    if options.get("hf_flores"):
        # Download FLORES sentences from Hugging Face within the container
        _download_flores_hf(
            source_lang=str(options["source_lang"]),
            target_langs=[str(t) for t in options["target_langs"]],
            split=str(options["split"]),
            flores_dir=remote_flores,
            max_pairs=int(options["max_pairs"]),
        )
    else:
        # Caller sent FLORES file content directly
        flores_files = options.get("flores_files") or {}
        remote_flores.mkdir(parents=True, exist_ok=True)
        for name, lines in flores_files.items():
            (remote_flores / str(name)).write_text(
                "\n".join(str(line) for line in lines), encoding="utf-8"
            )

    out_path = "/root/steering_probe.json"
    cmd = [
        "python",
        f"{REMOTE_CODE}/steer_language.py",
        "--model-id",
        str(options["model_id"]),
        "--flores-dir",
        str(remote_flores),
        "--source-lang",
        str(options["source_lang"]),
        "--split",
        str(options["split"]),
        "--max-pairs",
        str(options["max_pairs"]),
        "--out",
        out_path,
        "--max-new-tokens",
        str(options["max_new_tokens"]),
        "--bias-scale",
        str(options["bias_scale"]),
        "--min-token-count",
        str(options["min_token_count"]),
        "--temperature",
        str(options["temperature"]),
        "--top-p",
        str(options["top_p"]),
        "--device",
        "cuda",
        "--allow-download",
    ]
    for target in options["target_langs"]:
        cmd.extend(["--target-lang", str(target)])
    for prompt in options.get("prompts") or []:
        cmd.extend(["--prompt", str(prompt)])
    subprocess.run(cmd, check=True)
    return Path(out_path).read_text(encoding="utf-8")


@app.local_entrypoint()
def main(
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
    flores_dir: str = "",
    hf_flores: bool = False,
    source_lang: str = "eng_Latn",
    target_langs: str = "ind_Latn,spa_Latn",
    split: str = "devtest",
    max_pairs: int = 200,
    prompts: str = "",
    out_dir: str = "runs/language-steering",
    max_new_tokens: int = 96,
    bias_scale: float = 3.0,
    min_token_count: int = 2,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> None:
    targets = split_csv(target_langs) or ["ind_Latn", "spa_Latn"]
    prompt_items = split_csv(prompts)

    flores_files: dict[str, list[str]] = {}
    if not hf_flores:
        flores_dir_path = Path(flores_dir).expanduser().resolve() if flores_dir else None
        if not flores_dir_path or not flores_dir_path.is_dir():
            raise SystemExit(
                "Provide --flores-dir pointing to a local FLORES-200 directory, "
                "or use --hf-flores to download from Hugging Face inside the container."
            )
        needed_langs = [source_lang, *targets]
        for lang in needed_langs:
            path = flores_dir_path / f"{split}.{lang}"
            if not path.exists():
                path = flores_dir_path / f"{split}.{lang}.txt"
            if not path.exists():
                path = flores_dir_path / split / f"{lang}.txt"
            if not path.exists():
                path = flores_dir_path / split / lang
            if not path.exists():
                raise SystemExit(f"Missing FLORES file for {lang} under {flores_dir_path}")
            flores_files[f"{split}.{lang}"] = [
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

    options = {
        "model_id": model_id,
        "source_lang": source_lang,
        "target_langs": targets,
        "flores_files": flores_files,
        "hf_flores": hf_flores,
        "split": split,
        "max_pairs": max_pairs,
        "prompts": prompt_items,
        "max_new_tokens": max_new_tokens,
        "bias_scale": bias_scale,
        "min_token_count": min_token_count,
        "temperature": temperature,
        "top_p": top_p,
    }
    text = run_probe.remote(options)
    report = json.loads(text)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-".join(report.get("targets") or ["targets"])
    ts = report["created_at"].replace(":", "").replace("+", "Z").replace("-", "")
    out_path = output_dir / f"{ts}-{suffix}.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}")
