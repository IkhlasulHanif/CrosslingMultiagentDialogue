#!/usr/bin/env python3
"""Create local Torch BiVaD schema-check artifacts without remote APIs.

This runner is deliberately non-empirical. It uses deterministic tensor updates
to exercise the full artifact schema and downstream audits on local hardware.
The generated artifacts are marked synthetic so they cannot be mistaken for
model-backed evidence.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch


VALUE_KEYS = (
    "universalism",
    "security",
    "conformity",
    "benevolence",
    "self_direction",
    "tradition",
    "achievement",
    "power",
)

DEFAULT_TOPIC = "public release of dual-use policy datasets"
DEFAULT_SEED = 17
DEFAULT_OUT_DIR = "code/fixtures/bivad-local-torch"
CONDITIONS = (
    "mixed-language",
    "same-English",
    "same-target-language",
    "swapped-language",
    "translated-relay",
)


@dataclass(frozen=True)
class Agent:
    agent_id: str
    language: str
    stance: str
    values: dict[str, float]


BASE_AGENT_A = Agent(
    agent_id="A",
    language="English",
    stance="Prioritizes open civic access with targeted safeguards.",
    values={
        "universalism": 6.0,
        "security": 3.0,
        "conformity": 2.0,
        "benevolence": 5.0,
        "self_direction": 6.0,
        "tradition": 2.0,
        "achievement": 4.0,
        "power": 1.0,
    },
)

BASE_AGENT_B = Agent(
    agent_id="B",
    language="Indonesian",
    stance="Prioritizes institutional stability and risk controls.",
    values={
        "universalism": 3.0,
        "security": 6.0,
        "conformity": 5.0,
        "benevolence": 4.0,
        "self_direction": 3.0,
        "tradition": 5.0,
        "achievement": 4.0,
        "power": 2.0,
    },
)

LANGUAGE_BIASES = {
    "English": {
        "universalism": 0.12,
        "self_direction": 0.10,
        "security": -0.05,
        "conformity": -0.04,
    },
    "Indonesian": {
        "security": 0.12,
        "conformity": 0.10,
        "tradition": 0.08,
        "self_direction": -0.05,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--target-language", default="Indonesian")
    parser.add_argument("--turns", type=int, default=4)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--stamp", default=None, help="Optional fixed run-id stamp for reproducible fixtures.")
    parser.add_argument("--created-at", default=None, help="Optional fixed ISO timestamp for reproducible fixtures.")
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=list(CONDITIONS),
        choices=CONDITIONS,
        help="Condition subset to generate.",
    )
    parser.add_argument(
        "--include-low-disagreement-control",
        action="store_true",
        help="Also write a rejected same-prior control artifact.",
    )
    return parser.parse_args()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def choose_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def agent_with_language(agent: Agent, language: str) -> dict[str, Any]:
    return {
        "agent_id": agent.agent_id,
        "language": language,
        "stance": agent.stance,
        "values": agent.values,
    }


def condition_agents(condition: str, target_language: str) -> list[dict[str, Any]]:
    if condition == "mixed-language":
        return [agent_with_language(BASE_AGENT_A, "English"), agent_with_language(BASE_AGENT_B, target_language)]
    if condition == "same-English":
        return [agent_with_language(BASE_AGENT_A, "English"), agent_with_language(BASE_AGENT_B, "English")]
    if condition == "same-target-language":
        return [
            agent_with_language(BASE_AGENT_A, target_language),
            agent_with_language(BASE_AGENT_B, target_language),
        ]
    if condition == "swapped-language":
        return [agent_with_language(BASE_AGENT_A, target_language), agent_with_language(BASE_AGENT_B, "English")]
    if condition == "translated-relay":
        return [agent_with_language(BASE_AGENT_A, "English"), agent_with_language(BASE_AGENT_B, target_language)]
    raise ValueError(f"unknown condition: {condition}")


def values_to_tensor(values: dict[str, float], device: torch.device) -> torch.Tensor:
    return torch.tensor([float(values[key]) for key in VALUE_KEYS], dtype=torch.float32, device=device)


def tensor_to_values(tensor: torch.Tensor) -> dict[str, float]:
    clipped = torch.clamp(tensor.detach().to("cpu"), 1.0, 7.0)
    return {key: round(float(value), 3) for key, value in zip(VALUE_KEYS, clipped.tolist())}


def bias_for_language(language: str, device: torch.device) -> torch.Tensor:
    bias = torch.zeros(len(VALUE_KEYS), dtype=torch.float32, device=device)
    for key, value in LANGUAGE_BIASES.get(language, {}).items():
        bias[VALUE_KEYS.index(key)] = float(value)
    return bias


def screening_record(agents: list[dict[str, Any]]) -> dict[str, Any]:
    a_values = agents[0]["values"]
    b_values = agents[1]["values"]
    value_distance = sum(abs(float(a_values[key]) - float(b_values[key])) for key in VALUE_KEYS)
    return {
        "retained": value_distance >= 8.0,
        "stance_distance": None,
        "value_distance": round(value_distance, 3),
        "reason": "Local schema-check priors differ on topic-relevant access-versus-security values.",
    }


def disagreement_direction(
    speaker_values: torch.Tensor,
    opponent_values: torch.Tensor,
    condition: str,
    speaker_language: str,
    opponent_language: str,
    device: torch.device,
) -> tuple[torch.Tensor, dict[str, float]]:
    semantic_exposure = 0.16 * (opponent_values - speaker_values)
    production_language = bias_for_language(speaker_language, device)
    readout_language = bias_for_language(opponent_language, device) * 0.25

    if condition == "translated-relay":
        trajectory = semantic_exposure * 0.55
        production_component = torch.zeros_like(production_language)
    else:
        trajectory = semantic_exposure * 0.65 + production_language
        production_component = production_language

    return trajectory, {
        "semantic_exposure_norm": round(float(torch.linalg.vector_norm(semantic_exposure).to("cpu")), 6),
        "production_language_norm": round(float(torch.linalg.vector_norm(production_component).to("cpu")), 6),
        "readout_probe_wording_norm": round(float(torch.linalg.vector_norm(readout_language).to("cpu")), 6),
    }


def turn_text(
    speaker: str,
    language: str,
    condition: str,
    turn: int,
    shifted: bool,
) -> str:
    if language == "Indonesian":
        change = "berubah sedikit" if shifted else "tidak berubah"
        return (
            "Poin lawan yang paling kuat adalah keseimbangan antara akses publik "
            "dan keamanan. Namun, argumen lawan belum cukup untuk menghapus "
            f"kebutuhan kontrol risiko. Pandangan saya {change} pada giliran {turn}."
        )
    change = "changed slightly" if shifted else "did not change"
    relay = " In this relay condition I respond to translated semantic content." if condition == "translated-relay" else ""
    return (
        "Your strongest point is the tradeoff between public access and security. "
        "However, that point does not remove the need to protect the value I began "
        f"with. My view {change} on turn {turn}.{relay}"
    )


def observer_values(private_values: torch.Tensor, language: str, device: torch.device) -> torch.Tensor:
    return torch.clamp(private_values + bias_for_language(language, device) * 0.5, 1.0, 7.0)


def build_artifact(
    args: argparse.Namespace,
    condition: str,
    stamp: str,
    device: torch.device,
    low_disagreement: bool = False,
) -> dict[str, Any]:
    agents = condition_agents(condition, args.target_language)
    if low_disagreement:
        agents[1]["stance"] = agents[0]["stance"]
        agents[1]["values"] = dict(agents[0]["values"])

    state = {
        agent["agent_id"]: values_to_tensor(agent["values"], device)
        for agent in agents
    }
    initial_state = {agent_id: values.clone() for agent_id, values in state.items()}
    language_by_agent = {agent["agent_id"]: agent["language"] for agent in agents}
    transcript: list[dict[str, Any]] = []
    components_by_turn: list[dict[str, Any]] = []

    if not low_disagreement:
        for turn in range(1, args.turns + 1):
            speaker = agents[(turn - 1) % 2]["agent_id"]
            opponent = "B" if speaker == "A" else "A"
            trajectory, components = disagreement_direction(
                state[speaker],
                state[opponent],
                condition,
                language_by_agent[speaker],
                language_by_agent[opponent],
                device,
            )
            before = state[speaker].clone()
            state[speaker] = torch.clamp(state[speaker] + trajectory, 1.0, 7.0)
            shifted = bool(torch.linalg.vector_norm(state[speaker] - before).to("cpu") >= 0.2)
            transcript.append(
                {
                    "turn": turn,
                    "speaker": speaker,
                    "language": language_by_agent[speaker],
                    "addressed_counterpoint": turn > 1,
                    "stated_change": "shifted" if shifted else "unchanged",
                    "text": turn_text(speaker, language_by_agent[speaker], condition, turn, shifted),
                }
            )
            components_by_turn.append({"turn": turn, "speaker": speaker, **components})

    final_turn = transcript[-1]["turn"] if transcript else 0
    private_probes = []
    observer_readouts = []
    for agent in agents:
        agent_id = agent["agent_id"]
        language = agent["language"]
        private_probes.append(
            {
                "agent_id": agent_id,
                "turn": 0,
                "values": tensor_to_values(initial_state[agent_id]),
                "rationale": "Local tensor baseline before dialogue; non-empirical.",
            }
        )
        private_probes.append(
            {
                "agent_id": agent_id,
                "turn": final_turn,
                "values": tensor_to_values(state[agent_id]),
                "rationale": "Local tensor endpoint after deterministic update; non-empirical.",
            }
        )
        observer_readouts.append(
            {
                "agent_id": agent_id,
                "turn": 0,
                "values": tensor_to_values(observer_values(initial_state[agent_id], language, device)),
                "evidence": "Readout wording component only; non-empirical.",
            }
        )
        observer_readouts.append(
            {
                "agent_id": agent_id,
                "turn": final_turn,
                "values": tensor_to_values(observer_values(state[agent_id], language, device)),
                "evidence": "Public expression proxy with language readout bias; non-empirical.",
            }
        )

    suffix = "low-disagreement-control" if low_disagreement else condition
    created_at = args.created_at or datetime.now(timezone.utc).isoformat()
    return {
        "artifact_type": "local_torch_schema_check",
        "synthetic": True,
        "non_empirical": True,
        "run_id": f"{stamp}-{suffix}-seed{args.seed}",
        "created_at": created_at,
        "condition": "same-English" if low_disagreement else condition,
        "topic": args.topic,
        "seed": args.seed + 1 if low_disagreement else args.seed,
        "model": "local-deterministic-torch",
        "device": str(device),
        "torch_version": torch.__version__,
        "agents": agents,
        "screening": screening_record(agents),
        "transcript": transcript,
        "private_probes": private_probes,
        "observer_readouts": observer_readouts,
        "toy_components": {
            "purpose": (
                "Schema and audit exercise only. These tensors are not language-model "
                "behavior and must not be cited as empirical results."
            ),
            "separates_readout_from_trajectory": True,
            "turn_components": components_by_turn,
            "language_biases": LANGUAGE_BIASES,
        },
    }


def main() -> int:
    args = parse_args()
    if args.turns < 0:
        raise SystemExit("--turns must be non-negative")

    torch.manual_seed(args.seed)
    device = choose_device()
    stamp = args.stamp or utc_stamp()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for condition in args.conditions:
        artifact = build_artifact(args, condition, stamp, device)
        path = out_dir / f"{artifact['run_id']}.json"
        path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
        written.append(path)
        print(path)

    if args.include_low_disagreement_control:
        artifact = build_artifact(args, "same-English", stamp, device, low_disagreement=True)
        path = out_dir / f"{artifact['run_id']}.json"
        path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
        written.append(path)
        print(path)

    print(f"Wrote {len(written)} local Torch schema-check artifact(s) on device={device}.")
    print("These artifacts are synthetic/non-empirical and should only exercise audits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
