#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "STATE.yaml"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["next", "mark"])
    parser.add_argument("--id")
    parser.add_argument("--status", choices=["todo", "doing", "done", "blocked"])
    parser.add_argument("--evidence")
    args = parser.parse_args()
    if args.cmd == "next":
        task = first_pending()
        if not task:
            return 1
        print(task["id"])
        print(task["make"])
        print(task["check"])
        print(task.get("status", "todo"))
        return 0
    if not args.id or not args.status:
        raise SystemExit("mark requires --id and --status")
    mark(args.id, args.status, args.evidence)
    return 0


def load() -> list[dict]:
    if not STATE.exists():
        raise SystemExit("STATE.yaml missing; run make bootstrap")
    return yaml.safe_load(STATE.read_text(encoding="utf-8")) or []


def save(rows: list[dict]) -> None:
    STATE.write_text(yaml.safe_dump(rows, sort_keys=False), encoding="utf-8")


def first_pending() -> dict | None:
    for row in load():
        if row.get("status") != "done":
            return row
    return None


def mark(task_id: str, status: str, evidence: str | None) -> None:
    rows = load()
    for row in rows:
        if row["id"] == task_id:
            row["status"] = status
            if evidence:
                row["evidence"] = evidence
            save(rows)
            return
    raise SystemExit(f"task not found: {task_id}")


if __name__ == "__main__":
    raise SystemExit(main())
