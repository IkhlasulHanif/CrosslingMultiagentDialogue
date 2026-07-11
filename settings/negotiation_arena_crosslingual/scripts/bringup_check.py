#!/usr/bin/env python3
"""Check whether the upstream NegotiationArena checkout is locally usable.

This script intentionally does not clone or install anything. Network access and
dependency setup are environment concerns; the benchmark setting should report a
clear blocked state when the upstream repo is absent.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def append_event(kind: str, status: str, message: str) -> None:
    path = ROOT / "plan" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": utc_now(), "kind": kind, "status": status, "message": message}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def candidate_paths(upstream: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    env_name = upstream.get("env_override", "NEGOTIATION_ARENA_REPO")
    env_value = os.environ.get(env_name)
    if env_value:
        candidates.append(Path(env_value).expanduser())

    for rel_path in upstream.get("expected_local_paths", []):
        candidates.append(ROOT / rel_path)

    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve(strict=False)
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def selected_game_patterns() -> dict[str, list[str]]:
    games = load_json(ROOT / "config" / "games.json")
    patterns: dict[str, list[str]] = {}
    for game in games.get("selected_games", []):
        game_id = str(game.get("id", ""))
        mapping = game.get("upstream_mapping", {})
        raw_patterns = mapping.get("candidate_name_patterns", [])
        if game_id and isinstance(raw_patterns, list):
            patterns[game_id] = [str(item).lower() for item in raw_patterns]
    return patterns


def git_text(path: Path, spec: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "show", spec],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout


def git_value(path: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = completed.stdout.strip()
    return value or None


def readme_mentions_mit(text: str) -> bool:
    lowered = text.lower()
    return (
        "license-mit" in lowered
        or "license: mit" in lowered
        or "badge/license-mit" in lowered
        or "opensource.org/licenses/mit" in lowered
    )


def inspect_repo(path: Path) -> dict[str, Any]:
    readme_paths = [path / name for name in ["README.md", "README.rst", "readme.md"]]
    readme_text = ""
    for readme_path in readme_paths:
        if readme_path.exists():
            readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
            break
    files = {
        "readme": any((path / name).exists() for name in ["README.md", "README.rst", "readme.md"]),
        "license": any((path / name).exists() for name in ["LICENSE", "LICENSE.md", "LICENCE"]),
        "requirements": (path / "requirements.txt").exists(),
        "pyproject": (path / "pyproject.toml").exists(),
        "setup_py": (path / "setup.py").exists(),
    }
    python_files = [str(item.relative_to(path)) for item in path.rglob("*.py") if ".git" not in item.parts]
    patterns = selected_game_patterns()
    game_hits = {}
    for game_id, name_patterns in patterns.items():
        game_hits[game_id] = [
            item
            for item in python_files
            if any(pattern in item.lower() for pattern in name_patterns)
        ]
    branch = None
    head_path = path / ".git" / "HEAD"
    if head_path.exists():
        raw_head = head_path.read_text(encoding="utf-8", errors="replace").strip()
        if raw_head.startswith("ref: refs/heads/"):
            branch = raw_head.rsplit("/", 1)[-1]

    remote_url = git_value(path, "remote", "get-url", "origin")
    head_commit = git_value(path, "rev-parse", "HEAD")
    main_commit = git_value(path, "rev-parse", "main")
    main_readme_text = git_text(path, "main:README.md") if main_commit else ""
    readme_has_mit = readme_mentions_mit(readme_text)
    main_readme_has_mit = readme_mentions_mit(main_readme_text)
    license_source = None
    if files["license"]:
        license_source = "experiment branch LICENSE file"
    elif readme_has_mit:
        license_source = "experiment branch README MIT badge/text"
    elif main_readme_has_mit:
        license_source = "local main branch README MIT badge/text"

    license_evidence = {
        "has_license_file": files["license"],
        "experiment_readme_mentions_mit": readme_has_mit,
        "main_readme_mentions_mit": main_readme_has_mit,
        "source": license_source,
        "remote_url": remote_url,
        "head_commit": head_commit,
        "main_commit": main_commit,
        "main_readme_pointer_to_experiment_branch": "paper_experiment_code" in main_readme_text,
    }

    return {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "git_branch": branch,
        "git_head_commit": head_commit,
        "git_remote_url": remote_url,
        "files": files,
        "license_evidence": license_evidence,
        "python_file_count": len(python_files),
        "package_metadata_present": files["requirements"] or files["pyproject"] or files["setup_py"],
        "game_file_candidates": game_hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-event", action="store_true", help="append result to plan/events.jsonl")
    args = parser.parse_args()

    upstream_path = ROOT / "config" / "upstream.json"
    upstream = load_json(upstream_path)
    candidates = candidate_paths(upstream)
    existing = [path for path in candidates if path.is_dir()]

    inspections = [inspect_repo(path) for path in existing]
    selected = inspections[0] if inspections else None

    result: dict[str, Any] = {
        "checked_at": utc_now(),
        "setting_root": str(ROOT),
        "upstream": upstream,
        "candidate_paths": [str(path) for path in candidates],
        "selected_repo": selected,
        "status": "OK" if selected else "BLOCKED",
        "message": "NegotiationArena checkout found" if selected else "No local NegotiationArena checkout found",
    }

    if selected:
        missing = [
            name
            for name, present in selected["files"].items()
            if name in {"readme"} and not present
        ]
        if missing:
            result["status"] = "BLOCKED"
            result["message"] = "Local checkout is missing required metadata: " + ", ".join(missing)
        if result["status"] == "OK" and not selected.get("license_evidence", {}).get("source"):
            result["status"] = "BLOCKED"
            result["message"] = "Local checkout has no license evidence in LICENSE or README"
        elif result["status"] == "OK" and not selected.get("files", {}).get("license"):
            result.setdefault("warnings", []).append(
                "No LICENSE file is present in the checked branch; using README MIT badge/text as license evidence."
            )
        missing_games = [
            game_id for game_id, matches in selected.get("game_file_candidates", {}).items() if not matches
        ]
        if result["status"] == "OK" and missing_games:
            result["status"] = "BLOCKED"
            result["message"] = "Local checkout has no obvious selected-game implementation files: " + ", ".join(missing_games)
        if result["status"] == "OK" and not selected.get("package_metadata_present"):
            result["status"] = "BLOCKED"
            result["message"] = "Local checkout lacks Python package metadata: requirements.txt, pyproject.toml, or setup.py"
    else:
        env_name = upstream.get("env_override", "NEGOTIATION_ARENA_REPO")
        result["next_action"] = (
            f"Place a NegotiationArena checkout under external/NegotiationArena or set {env_name} "
            "to an existing checkout, then rerun scripts/bringup_check.py."
        )

    output = ROOT / "artifacts" / "results" / "bringup_check.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.write_event:
        append_event("bringup", result["status"], f"{result['message']}; artifact={output.relative_to(ROOT)}")

    return 0 if result["status"] == "OK" else 2


if __name__ == "__main__":
    sys.exit(main())
