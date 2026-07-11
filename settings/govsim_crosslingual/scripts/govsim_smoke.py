#!/usr/bin/env python3
"""Run the narrowest GovSim C0 source/install smoke available.

This is not an empirical episode runner. It records whether the local GovSim
source checkout, PathFinder submodule, setting-local Python environment, and
upstream fishery entry point can reach the point where a real model endpoint is
needed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
ARTIFACT_DIR = ROOT / "artifacts" / "logs"
RESULT_DIR = ROOT / "artifacts" / "results"
GOVSIM_DIR = ROOT / "vendor" / "govsim"
REAL_C0_COMMAND = [
    str(VENV_PYTHON),
    "-m",
    "simulation.main",
    "experiment=fish_baseline_concurrent",
    "llm.path=Qwen/Qwen3-1.7B",
    "llm.backend=vllm",
    "debug=true",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_command(
    name: str,
    command: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = ARTIFACT_DIR / f"{name}_{utc_stamp()}.log"
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = proc.stdout
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        output += f"\nTIMEOUT after {timeout}s\n"
        returncode = 124
        timed_out = True

    log_path.write_text(
        "$ " + " ".join(command) + "\n\n" + output,
        encoding="utf-8",
    )
    return {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "returncode": returncode,
        "timed_out": timed_out,
        "log_path": str(log_path.relative_to(ROOT)),
        "output_tail": output[-2000:],
    }


def import_probe() -> dict[str, str]:
    modules = [
        "hydra",
        "omegaconf",
        "wandb",
        "transformers",
        "pathfinder",
        "numpy",
        "pettingzoo",
        "sentence_transformers",
    ]
    if not VENV_PYTHON.exists():
        return {module: "missing .venv/bin/python" for module in modules}
    code = "\n".join(
        [
            "mods = " + repr(modules),
            "for mod in mods:",
            "    try:",
            "        __import__(mod)",
            "        print(f'{mod}\\tOK')",
            "    except Exception as exc:",
            "        print(f'{mod}\\t{type(exc).__name__}: {exc}')",
        ]
    )
    proc = subprocess.run(
        [str(VENV_PYTHON), "-c", code],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "\t" in line:
            module, status = line.split("\t", 1)
            result[module] = status
    return result


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = RESULT_DIR / f"govsim_c0_smoke_preflight_{utc_stamp()}.json"

    summary: dict[str, Any] = {
        "schema_version": "govsim-c0-smoke-preflight-v1",
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "empirical_episode_ran": False,
        "real_c0_command": " ".join(REAL_C0_COMMAND),
        "govsim_dir": str(GOVSIM_DIR.relative_to(ROOT)),
        "venv_python": str(VENV_PYTHON.relative_to(ROOT)),
        "commands": [],
        "import_probe": {},
        "blockers": [],
        "next_command_once_unblocked": "./harness.sh run-smoke",
    }

    summary["commands"].append(
        run_command("govsim_license_report", [sys.executable, "scripts/update_license_report.py", "--root", "."])
    )
    summary["commands"].append(
        run_command("govsim_git_head", ["git", "-C", "vendor/govsim", "log", "-1", "--format=%H%n%ci%n%s"])
    )
    summary["commands"].append(
        run_command("govsim_pathfinder_submodule", ["git", "-C", "vendor/govsim", "submodule", "status", "--recursive"])
    )

    if VENV_PYTHON.exists():
        summary["commands"].append(run_command("govsim_venv_python", [str(VENV_PYTHON), "-V"]))
        summary["commands"].append(
            run_command(
                "govsim_pip_install",
                [str(VENV_PYTHON), "-m", "pip", "install", "-r", "vendor/govsim/requirements.txt"],
                timeout=120,
            )
        )
    else:
        summary["blockers"].append("missing setting-local .venv/bin/python")

    pathfinder_files = list((GOVSIM_DIR / "pathfinder").glob("*"))
    if not pathfinder_files:
        summary["blockers"].append(
            "PathFinder submodule is uninitialized: run `git -C vendor/govsim submodule update --init --depth 1 pathfinder`"
        )

    summary["import_probe"] = import_probe()
    missing_imports = {
        module: status
        for module, status in summary["import_probe"].items()
        if status != "OK"
    }
    if missing_imports:
        summary["blockers"].append(
            "missing GovSim Python imports in .venv: "
            + ", ".join(f"{module} ({status})" for module, status in missing_imports.items())
        )

    summary["commands"].append(
        run_command(
            "govsim_real_c0_entrypoint",
            REAL_C0_COMMAND,
            cwd=GOVSIM_DIR,
            env={"PYTHONPATH": str(GOVSIM_DIR)},
            timeout=60,
        )
    )

    entrypoint_rc = summary["commands"][-1]["returncode"]
    if entrypoint_rc != 0:
        summary["blockers"].append(
            "upstream fishery C0 entry point failed before episode execution; see "
            + summary["commands"][-1]["log_path"]
        )

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(summary_path.relative_to(ROOT))
    return 0 if not summary["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
