#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runner.dialogue import run_cell
from runner.providers import build_provider


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell", required=True)
    parser.add_argument("--no-git", action="store_true")
    args = parser.parse_args()
    config = load_config(args.cell)
    provider = build_provider()
    result = run_cell(config, provider, ROOT)
    evidence = ROOT / "reports" / "evidence" / "run" / f"{config['cell_id']}.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        "# Cell Run Evidence\n\n"
        f"```json\n{json.dumps(result, indent=2, sort_keys=True)}\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    if not args.no_git and os.environ.get("XDUETPD_NO_GIT") != "1" and not result.get("skipped"):
        commit_cell(config["cell_id"], int(config["n_dialogues"]), True)
    return 0


def load_config(cell_id: str) -> dict:
    path = ROOT / "configs" / "cells" / f"{cell_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"missing cell config: {path}; run make cells first")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def commit_cell(cell_id: str, n_dialogues: int, ok: bool) -> None:
    repo_rel = f"xduetpd"
    message = f"[run] cell={cell_id} n={n_dialogues} ok={str(ok).lower()}"
    subprocess.run(["git", "add", "--", repo_rel], cwd=ROOT.parent, check=True)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", repo_rel],
        cwd=ROOT.parent,
        check=False,
    )
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT.parent, check=True)
    subprocess.run(["git", "push"], cwd=ROOT.parent, check=True)


if __name__ == "__main__":
    raise SystemExit(main())
