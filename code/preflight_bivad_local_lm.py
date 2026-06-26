#!/usr/bin/env python3
"""Preflight local resources for the offline BiVaD Hugging Face runner.

This script does not download models or execute experiments. It records whether
Torch and transformers are available and scans local filesystem locations for
candidate causal-LM model directories that contain config, tokenizer, and weight
files.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

import torch


DEFAULT_OUT_DIR = "code/bivad-evidence-audit"
WEIGHT_GLOBS = ("*.safetensors", "pytorch_model*.bin", "model*.bin", "model*.gguf")
TOKENIZER_FILES = ("tokenizer.json", "tokenizer.model", "vocab.json", "sentencepiece.bpe.model")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--search-root",
        action="append",
        default=[],
        help="Additional local directory to scan for model candidates. May be repeated.",
    )
    parser.add_argument(
        "--out-dir",
        default=DEFAULT_OUT_DIR,
        help="Directory for local_model_preflight JSON and Markdown outputs.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=7,
        help="Maximum directory depth below each search root to consider.",
    )
    return parser.parse_args()


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def relative_depth(root: Path, path: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 999999


def has_any(path: Path, names: tuple[str, ...]) -> bool:
    return any((path / name).exists() for name in names)


def has_weight_file(path: Path) -> bool:
    return any(next(path.glob(pattern), None) is not None for pattern in WEIGHT_GLOBS)


def read_model_config(path: Path) -> dict[str, Any]:
    config_path = path / "config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(config, dict):
        return {}
    return {
        "model_type": config.get("model_type"),
        "architectures": config.get("architectures"),
        "torch_dtype": config.get("torch_dtype"),
    }


def candidate_score(path: Path) -> tuple[bool, list[str]]:
    missing = []
    if not (path / "config.json").exists():
        missing.append("config.json")
    if not has_any(path, TOKENIZER_FILES) and not (path / "tokenizer_config.json").exists():
        missing.append("tokenizer files")
    if not has_weight_file(path):
        missing.append("model weights")
    return not missing, missing


def discover_candidates(search_roots: list[Path], max_depth: int) -> list[dict[str, Any]]:
    candidates: dict[Path, dict[str, Any]] = {}
    for root in search_roots:
        root = root.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            continue
        for config_path in root.rglob("config.json"):
            model_dir = config_path.parent
            if relative_depth(root, model_dir) > max_depth:
                continue
            complete, missing = candidate_score(model_dir)
            candidates[model_dir] = {
                "path": str(model_dir),
                "complete_for_transformers_load": complete,
                "missing": missing,
                "config": read_model_config(model_dir),
            }
    return sorted(candidates.values(), key=lambda item: item["path"])


def default_search_roots(extra_roots: list[str]) -> list[Path]:
    roots = [
        Path("~/.cache/huggingface/hub"),
        Path("~/models"),
        Path("~/Documents/models"),
        Path("/tmp"),
    ]
    roots.extend(Path(item) for item in extra_roots)
    return roots


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Local LM Preflight",
        "",
        f"Created at: `{summary['created_at']}`",
        "",
        f"Torch: `{summary['torch_version']}`",
        "",
        f"Transformers: `{summary['transformers_version'] or 'not installed'}`",
        "",
        f"Local execution device: `cpu`",
        "",
        f"Candidate model directories: `{summary['candidate_count']}`",
        "",
        f"Complete candidates: `{summary['complete_candidate_count']}`",
        "",
    ]
    if summary["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for blocker in summary["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    lines.append("## Candidates")
    lines.append("")
    if not report["candidates"]:
        lines.append("No local Hugging Face model candidates were found in the scanned roots.")
        lines.append("")
    for candidate in report["candidates"]:
        lines.extend(
            [
                f"### `{candidate['path']}`",
                "",
                f"- Complete: `{candidate['complete_for_transformers_load']}`",
                f"- Missing: `{', '.join(candidate['missing']) if candidate['missing'] else 'none'}`",
                f"- Model type: `{candidate['config'].get('model_type') or 'unknown'}`",
                f"- Architectures: `{candidate['config'].get('architectures') or 'unknown'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Action",
            "",
            "For GPU-backed language-steering probes, use "
            "`python3 -m modal run code/modal_steer_language.py --model-id <hf-model> --flores-dir <flores200>`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    transformers_version = package_version("transformers")
    candidates = discover_candidates(default_search_roots(args.search_root), args.max_depth)
    complete_candidates = [item for item in candidates if item["complete_for_transformers_load"]]
    blockers = []
    if transformers_version is None:
        blockers.append("transformers is not installed")
    if not complete_candidates:
        blockers.append("no complete local Hugging Face model directory found")

    report = {
        "artifact_type": "bivad_local_lm_preflight",
        "synthetic": False,
        "summary": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "torch_version": torch.__version__,
            "local_execution_device": "cpu",
            "transformers_version": transformers_version,
            "search_roots": [str(path.expanduser()) for path in default_search_roots(args.search_root)],
            "candidate_count": len(candidates),
            "complete_candidate_count": len(complete_candidates),
            "blockers": blockers,
        },
        "candidates": candidates,
        "note": "Preflight only; no model was loaded, no model output was generated, and no empirical result is implied.",
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "local_model_preflight.json").write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "local_model_preflight.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"Wrote {out_dir / 'local_model_preflight.json'}")
    print(f"Wrote {out_dir / 'local_model_preflight.md'}")
    if blockers:
        print("Preflight found blockers; see local_model_preflight.md.")
        return 1
    print("Preflight found at least one complete local model candidate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
