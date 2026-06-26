#!/usr/bin/env python3
"""Offline BiVaD smoke runner.

This runner is intentionally deterministic and API-free. It exercises the
research protocol mechanics before any model-backed dialogue is attempted:
screening, public dialogue, private probes, observer readouts, and metrics.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


VALUE_DIMS = ("universalism", "security", "conformity", "benevolence")


@dataclass(frozen=True)
class AgentPrior:
    agent_id: str
    stance: str
    language: str
    values: dict[str, float]


@dataclass(frozen=True)
class Turn:
    turn: int
    speaker: str
    language: str
    text: str
    addressed_counterpoint: bool
    stated_change: str


@dataclass(frozen=True)
class ProbeReadout:
    agent_id: str
    turn: int
    probe_language: str
    values: dict[str, float]


@dataclass(frozen=True)
class ObserverReadout:
    agent_id: str
    turn: int
    judge_view: str
    values: dict[str, float]
    evidence: str
    uncertain: bool


def clamp(value: float, lo: float = 1.0, hi: float = 7.0) -> float:
    return max(lo, min(hi, round(value, 3)))


def euclidean(a: dict[str, float], b: dict[str, float]) -> float:
    return round(
        math.sqrt(sum((a[dim] - b[dim]) ** 2 for dim in VALUE_DIMS)),
        6,
    )


def mean_vectors(vectors: Iterable[dict[str, float]]) -> dict[str, float]:
    items = list(vectors)
    return {
        dim: round(sum(vector[dim] for vector in items) / len(items), 3)
        for dim in VALUE_DIMS
    }


def make_priors(language_a: str, language_b: str) -> tuple[AgentPrior, AgentPrior]:
    agent_a = AgentPrior(
        agent_id="A",
        stance="prioritizes open civic debate with safeguards",
        language=language_a,
        values={
            "universalism": 6.3,
            "security": 3.2,
            "conformity": 2.4,
            "benevolence": 5.6,
        },
    )
    agent_b = AgentPrior(
        agent_id="B",
        stance="prioritizes social stability and harm prevention",
        language=language_b,
        values={
            "universalism": 3.7,
            "security": 6.1,
            "conformity": 5.8,
            "benevolence": 4.4,
        },
    )
    return agent_a, agent_b


def screen_candidate(agent_a: AgentPrior, agent_b: AgentPrior, gamma: float) -> dict:
    distance = euclidean(agent_a.values, agent_b.values)
    retained = distance >= gamma
    largest_gap_dims = sorted(
        VALUE_DIMS,
        key=lambda dim: abs(agent_a.values[dim] - agent_b.values[dim]),
        reverse=True,
    )[:2]
    return {
        "distance": distance,
        "gamma": gamma,
        "retained": retained,
        "largest_gap_dimensions": largest_gap_dims,
    }


def localized_sentence(language: str, agent_id: str, topic: str, stance: str) -> str:
    if language.lower() == "indonesian":
        return (
            f"Agen {agent_id}: Untuk topik {topic}, saya tetap melihat {stance}. "
            "Saya menanggapi poin lawan dengan menimbang kebebasan, risiko, dan dampak sosial."
        )
    if language.lower() == "spanish":
        return (
            f"Agente {agent_id}: Sobre {topic}, mantengo que {stance}. "
            "Respondo al punto más fuerte del otro agente sopesando libertad, riesgo e impacto social."
        )
    return (
        f"Agent {agent_id}: On {topic}, I maintain that {stance}. "
        "I address the other agent's strongest point by weighing liberty, risk, and social impact."
    )


def run_dialogue(
    topic: str,
    condition: str,
    agent_a: AgentPrior,
    agent_b: AgentPrior,
    turns: int,
) -> list[Turn]:
    if condition == "no-dialogue":
        return []

    transcript: list[Turn] = []
    agents = (agent_a, agent_b)
    for idx in range(turns):
        agent = agents[idx % 2]
        has_prior_turn = bool(transcript)
        stated_change = "softened" if has_prior_turn and idx == turns - 1 else "unchanged"
        text = localized_sentence(agent.language, agent.agent_id, topic, agent.stance)
        if stated_change == "softened":
            text += " My view changed slightly: I give more weight to the other side's main concern."
        transcript.append(
            Turn(
                turn=idx + 1,
                speaker=agent.agent_id,
                language=agent.language,
                text=text,
                addressed_counterpoint=has_prior_turn,
                stated_change=stated_change,
            )
        )
    return transcript


def probe(agent: AgentPrior, turn: int, transcript: list[Turn], probe_language: str) -> ProbeReadout:
    exposure = len([item for item in transcript if item.speaker != agent.agent_id])
    shifted = dict(agent.values)
    if exposure:
        if agent.agent_id == "A":
            shifted["security"] = clamp(shifted["security"] + 0.25 * exposure)
            shifted["conformity"] = clamp(shifted["conformity"] + 0.15 * exposure)
        else:
            shifted["universalism"] = clamp(shifted["universalism"] + 0.25 * exposure)
            shifted["benevolence"] = clamp(shifted["benevolence"] + 0.1 * exposure)
    return ProbeReadout(agent.agent_id, turn, probe_language, shifted)


def observe(agent: AgentPrior, turn: int, transcript: list[Turn]) -> ObserverReadout:
    agent_turns = [item for item in transcript if item.speaker == agent.agent_id]
    if not agent_turns:
        return ObserverReadout(
            agent_id=agent.agent_id,
            turn=turn,
            judge_view="original_multilingual",
            values=dict(agent.values),
            evidence="No public turn; observer falls back to independent draft prior.",
            uncertain=True,
        )

    public_values = dict(agent.values)
    if any(item.stated_change == "softened" for item in agent_turns):
        public_values = mean_vectors(
            [
                public_values,
                {
                    "universalism": 5.2,
                    "security": 5.0,
                    "conformity": 4.2,
                    "benevolence": 5.1,
                },
            ]
        )
    evidence = agent_turns[-1].text[:220]
    return ObserverReadout(
        agent_id=agent.agent_id,
        turn=turn,
        judge_view="original_multilingual",
        values=public_values,
        evidence=evidence,
        uncertain=False,
    )


def language_compliance(transcript: list[Turn], agent_a: AgentPrior, agent_b: AgentPrior) -> dict[str, bool]:
    required = {agent_a.agent_id: agent_a.language, agent_b.agent_id: agent_b.language}
    return {
        f"turn_{item.turn}_{item.speaker}": item.language == required[item.speaker]
        for item in transcript
    }


def run_trial(args: argparse.Namespace) -> dict:
    agent_a, agent_b = make_priors(args.language_a, args.language_b)
    screen = screen_candidate(agent_a, agent_b, args.gamma)
    transcript = run_dialogue(args.topic, args.condition, agent_a, agent_b, args.turns)

    probe_turns = [0]
    if transcript:
        probe_turns.append(len(transcript))
    probes: list[ProbeReadout] = []
    observers: list[ObserverReadout] = []
    for turn in probe_turns:
        prefix = transcript[:turn]
        probes.append(probe(agent_a, turn, prefix, agent_a.language))
        probes.append(probe(agent_b, turn, prefix, agent_b.language))
        observers.append(observe(agent_a, turn, prefix))
        observers.append(observe(agent_b, turn, prefix))

    start_private = {item.agent_id: item.values for item in probes if item.turn == 0}
    end_private = {item.agent_id: item.values for item in probes if item.turn == probe_turns[-1]}
    end_observed = {item.agent_id: item.values for item in observers if item.turn == probe_turns[-1]}
    initial_distance = euclidean(start_private["A"], start_private["B"])
    final_distance = euclidean(end_private["A"], end_private["B"])
    metrics = {
        "private_drift": {
            "A": euclidean(start_private["A"], end_private["A"]),
            "B": euclidean(start_private["B"], end_private["B"]),
        },
        "final_private_distance": final_distance,
        "convergence_ratio": round((initial_distance - final_distance) / initial_distance, 6),
        "private_public_gap": {
            "A": euclidean(end_private["A"], end_observed["A"]),
            "B": euclidean(end_private["B"], end_observed["B"]),
        },
    }

    return {
        "run_id": args.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline_deterministic_smoke",
        "topic": args.topic,
        "condition": args.condition,
        "turn_budget": args.turns,
        "agents": [asdict(agent_a), asdict(agent_b)],
        "screening": screen,
        "transcript": [asdict(item) for item in transcript],
        "private_probes": [asdict(item) for item in probes],
        "observer_readouts": [asdict(item) for item in observers],
        "checks": {
            "screening_retained": screen["retained"],
            "language_compliance": language_compliance(transcript, agent_a, agent_b),
            "context_layers_separated": True,
            "synthetic_or_offline_only": True,
        },
        "metrics": metrics,
    }


def write_summary(result: dict, summary_path: Path, json_path: Path) -> None:
    compliance = result["checks"]["language_compliance"]
    compliance_text = "n/a" if not compliance else json.dumps(compliance, sort_keys=True)
    lines = [
        f"# BiVaD Offline Smoke Trial - {result['run_id']}",
        "",
        "This is an offline deterministic smoke trial, not empirical model evidence.",
        "",
        "## Settings",
        "",
        f"- Topic: {result['topic']}",
        f"- Condition: {result['condition']}",
        f"- Turn budget: {result['turn_budget']}",
        f"- JSON artifact: `{json_path.name}`",
        "",
        "## Screening",
        "",
        f"- Baseline distance: {result['screening']['distance']}",
        f"- Gamma: {result['screening']['gamma']}",
        f"- Retained: {result['screening']['retained']}",
        f"- Largest gap dimensions: {', '.join(result['screening']['largest_gap_dimensions'])}",
        "",
        "## Checks",
        "",
        f"- Language compliance: {compliance_text}",
        f"- Context layers separated: {result['checks']['context_layers_separated']}",
        "",
        "## Metrics",
        "",
        f"- Private drift: {json.dumps(result['metrics']['private_drift'], sort_keys=True)}",
        f"- Final private distance: {result['metrics']['final_private_distance']}",
        f"- Convergence ratio: {result['metrics']['convergence_ratio']}",
        f"- Private-public gap: {json.dumps(result['metrics']['private_public_gap'], sort_keys=True)}",
        "",
        "## Next Step",
        "",
        "Replace the deterministic speaker and judge functions with API-backed calls while preserving this artifact schema.",
        "",
    ]
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an offline deterministic BiVaD smoke trial.")
    parser.add_argument("--topic", default="whether platforms should remove harmful misinformation")
    parser.add_argument("--condition", choices=("mixed-language", "same-language", "no-dialogue"), default="mixed-language")
    parser.add_argument("--language-a", default="English")
    parser.add_argument("--language-b", default="Indonesian")
    parser.add_argument("--turns", type=int, default=2)
    parser.add_argument("--gamma", type=float, default=3.0)
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--out-dir", type=Path, default=Path("runs/bivad-smoke"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.turns < 0:
        raise SystemExit("--turns must be non-negative")
    if args.condition == "no-dialogue" and args.turns != 0:
        args.turns = 0

    result = run_trial(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / f"{args.run_id}.json"
    summary_path = args.out_dir / f"{args.run_id}.md"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(result, summary_path, json_path)
    print(f"wrote {json_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
