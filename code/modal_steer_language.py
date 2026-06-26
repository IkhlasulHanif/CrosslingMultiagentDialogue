#!/usr/bin/env python3
"""Run `code/steer_language.py` on Modal GPU.

The local entrypoint copies the repository `code/` directory into the Modal
image, sends the needed FLORES sentence files to the remote function, runs the
probability-steering probe on an L4 GPU by default, and writes the returned JSON
artifact back under `runs/`.
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
    )
    .add_local_dir(REPO_ROOT / "code", remote_path=REMOTE_CODE)
)

app = modal.App("multilingual-value-drift-steering", image=image)


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@app.function(
    gpu="L4",
    timeout=60 * 60,
)
def run_probe(options: dict[str, object]) -> str:
    flores_files = options["flores_files"]
    remote_flores = Path(REMOTE_FLORES)
    remote_flores.mkdir(parents=True, exist_ok=True)
    for name, lines in flores_files.items():
        (remote_flores / str(name)).write_text("\n".join(str(line) for line in lines), encoding="utf-8")

    out_path = "/root/steering_probe.json"
    cmd = [
        "python",
        f"{REMOTE_CODE}/steer_language.py",
        "--model-id",
        str(options["model_id"]),
        "--flores-dir",
        REMOTE_FLORES,
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
    ]
    for target in options["target_langs"]:
        cmd.extend(["--target-lang", str(target)])
    for prompt in options["prompts"]:
        cmd.extend(["--prompt", str(prompt)])
    if options["allow_download"]:
        cmd.append("--allow-download")
    subprocess.run(cmd, check=True)
    return Path(out_path).read_text(encoding="utf-8")


@app.local_entrypoint()
def main(
    model_id: str,
    flores_dir: str,
    source_lang: str = "eng_Latn",
    target_langs: str = "ind_Latn,spa_Latn",
    split: str = "dev",
    max_pairs: int = 512,
    prompts: str = "",
    out_dir: str = "runs/language-steering",
    max_new_tokens: int = 96,
    bias_scale: float = 3.0,
    min_token_count: int = 2,
    temperature: float = 0.7,
    top_p: float = 0.9,
    allow_download: bool = False,
) -> None:
    flores_dir_path = Path(flores_dir).expanduser().resolve()
    if not flores_dir_path.is_dir():
        raise SystemExit(f"FLORES directory does not exist: {flores_dir_path}")
    targets = split_csv(target_langs) or ["ind_Latn", "spa_Latn"]
    prompt_items = split_csv(prompts)
    needed_langs = [source_lang, *targets]
    flores_files: dict[str, list[str]] = {}
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
        "split": split,
        "max_pairs": max_pairs,
        "prompts": prompt_items,
        "max_new_tokens": max_new_tokens,
        "bias_scale": bias_scale,
        "min_token_count": min_token_count,
        "temperature": temperature,
        "top_p": top_p,
        "allow_download": allow_download,
    }
    text = run_probe.remote(options)
    report = json.loads(text)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "-".join(report.get("targets") or ["targets"])
    out_path = output_dir / f"{report['created_at'].replace(':', '').replace('+', 'Z')}-{suffix}.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}")
