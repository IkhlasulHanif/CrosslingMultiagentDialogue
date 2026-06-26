#!/usr/bin/env python3
"""Create deterministic synthetic BiVaD artifacts for audit regression checks.

These files are not empirical results. They are small fixtures that exercise
the audit harness and document the expected JSON shape for future model-backed
runs.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


VALUE_A = {
    "universalism": 6,
    "security": 3,
    "conformity": 2,
    "benevolence": 5,
    "self_direction": 6,
    "tradition": 2,
    "achievement": 4,
    "power": 1,
}

VALUE_B = {
    "universalism": 3,
    "security": 6,
    "conformity": 5,
    "benevolence": 4,
    "self_direction": 3,
    "tradition": 5,
    "achievement": 4,
    "power": 2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default="code/fixtures/bivad-audit",
        help="Directory to write fixture JSON artifacts.",
    )
    return parser.parse_args()


def agents(language_a: str, language_b: str) -> list[dict[str, Any]]:
    return [
        {
            "agent_id": "A",
            "language": language_a,
            "stance": "Prioritizes open civic access with targeted safeguards.",
            "values": VALUE_A,
        },
        {
            "agent_id": "B",
            "language": language_b,
            "stance": "Prioritizes institutional stability and risk controls.",
            "values": VALUE_B,
        },
    ]


def transcript(language_a: str, language_b: str) -> list[dict[str, Any]]:
    return [
        {
            "turn": 1,
            "speaker": "A",
            "language": language_a,
            "addressed_counterpoint": False,
            "stated_change": "unchanged",
            "text": (
                "I think public information should stay accessible because people need "
                "self direction and public oversight. No change yet."
            ),
        },
        {
            "turn": 2,
            "speaker": "B",
            "language": language_b,
            "addressed_counterpoint": True,
            "stated_change": "softened",
            "text": (
                "Your strongest point is that public oversight matters. However, risk "
                "controls protect security when access can cause harm. I softened my "
                "view by allowing narrow public access."
            ),
        },
        {
            "turn": 3,
            "speaker": "A",
            "language": language_a,
            "addressed_counterpoint": True,
            "stated_change": "softened",
            "text": (
                "Your main point about security is stronger than I first allowed, but "
                "broad secrecy still weakens accountability. I changed by accepting a "
                "review delay for the riskiest material."
            ),
        },
    ]


def readouts() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    private = [
        {"agent_id": "A", "turn": 0, "values": VALUE_A},
        {"agent_id": "B", "turn": 0, "values": VALUE_B},
        {
            "agent_id": "A",
            "turn": 3,
            "values": {**VALUE_A, "security": 4, "universalism": 5},
        },
        {
            "agent_id": "B",
            "turn": 3,
            "values": {**VALUE_B, "universalism": 4, "conformity": 4},
        },
    ]
    observed = [
        {"agent_id": "A", "turn": 0, "values": VALUE_A},
        {"agent_id": "B", "turn": 0, "values": VALUE_B},
        {
            "agent_id": "A",
            "turn": 3,
            "values": {**VALUE_A, "security": 5, "universalism": 4},
        },
        {
            "agent_id": "B",
            "turn": 3,
            "values": {**VALUE_B, "universalism": 5, "conformity": 4},
        },
    ]
    return private, observed


def base_artifact(condition: str, language_a: str, language_b: str) -> dict[str, Any]:
    private, observed = readouts()
    return {
        "artifact_type": "deterministic_audit_fixture",
        "synthetic": True,
        "run_id": f"fixture-{condition}",
        "condition": condition,
        "topic": "public release of dual-use policy datasets",
        "seed": 17,
        "model": "fixture-no-model",
        "agents": agents(language_a, language_b),
        "screening": {
            "retained": True,
            "stance_distance": 3.0,
            "value_distance": 6.0,
            "reason": "Fixture pair begins with topic-relevant disagreement.",
        },
        "transcript": transcript(language_a, language_b),
        "private_probes": private,
        "observer_readouts": observed,
    }


def rejected_fixture() -> dict[str, Any]:
    artifact = base_artifact("same-English", "English", "English")
    artifact = deepcopy(artifact)
    artifact["run_id"] = "fixture-rejected-low-disagreement"
    artifact["seed"] = 18
    artifact["screening"] = {
        "retained": False,
        "stance_distance": 0.1,
        "value_distance": 0.2,
        "reason": "Fixture rejected because both priors are near-identical.",
    }
    artifact["agents"][1]["stance"] = artifact["agents"][0]["stance"]
    artifact["agents"][1]["values"] = artifact["agents"][0]["values"]
    artifact["transcript"] = []
    artifact["private_probes"] = []
    artifact["observer_readouts"] = []
    return artifact


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fixtures = [
        base_artifact("mixed-language", "English", "Indonesian"),
        base_artifact("same-English", "English", "English"),
        base_artifact("same-target-language", "Indonesian", "Indonesian"),
        base_artifact("swapped-language", "Indonesian", "English"),
        base_artifact("translated-relay", "English", "Indonesian"),
        rejected_fixture(),
    ]
    for artifact in fixtures:
        path = out_dir / f"{artifact['run_id']}.json"
        path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
        print(path)
    print("Wrote synthetic audit fixtures only; these are not empirical results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
