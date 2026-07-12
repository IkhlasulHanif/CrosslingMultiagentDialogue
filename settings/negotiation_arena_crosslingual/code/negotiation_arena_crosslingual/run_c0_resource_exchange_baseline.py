#!/usr/bin/env python3
"""Run one Qwen/local C0 EN resource-exchange baseline episode."""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "external" / "NegotiationArena"
sys.path.insert(0, str(ROOT / "code" / "negotiation_arena_crosslingual"))
sys.path.insert(0, str(UPSTREAM))

from run_c0_smoke import (  # noqa: E402
    append_event,
    benchmark_openai_allowed,
    install_optional_upstream_import_shims,
    load_benchmark_model_config,
    make_chat_client,
    run_endpoint_probe,
    upstream_commit,
    utc_now,
    write_json,
    write_metrics,
)
from language_channels import output_channel_instruction  # noqa: E402


FAILED_COMMAND = "bash scripts/run_c0_resource_exchange_baseline.sh"
OPENAI_FAILED_COMMAND = "bash scripts/run_c0_openai_resource_exchange_baseline.sh"
PLAN_PATH = ROOT / "config" / "c0_resource_exchange_plan.json"

TRADING_TAGS = (
    "my name",
    "my resources",
    "my goals",
    "reason",
    "player answer",
    "message",
    "newly proposed trade",
)


def load_plan() -> dict[str, Any]:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def selected_benchmark_provider() -> str:
    override = os.environ.get("NEGOTIATION_BENCHMARK_PROVIDER")
    if override:
        return override
    return "local_qwen"


def provider_artifacts(artifacts: dict[str, str], provider: str) -> dict[str, str]:
    if provider != "openai_benchmark":
        return artifacts
    return {
        "transcript": artifacts["transcript"].replace(".json", ".openai_benchmark.json"),
        "metrics": artifacts["metrics"].replace(".metrics.json", ".openai_benchmark.metrics.json"),
    }


def command_for_provider(provider: str) -> str:
    return OPENAI_FAILED_COMMAND if provider == "openai_benchmark" else FAILED_COMMAND


def tag_value(text: str, tag: str) -> str | None:
    match = re.search(rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>", text, flags=re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def replace_or_append_tag(text: str, tag: str, value: str) -> str:
    replacement = f"<{tag}> {value} </{tag}>"
    pattern = re.compile(rf"<{re.escape(tag)}>.*?</{re.escape(tag)}>", flags=re.DOTALL)
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return f"{text.rstrip()}\n{replacement}"


def canonicalize_xml_tags(text: str) -> str:
    normalized = text.strip()
    if normalized.startswith("```"):
        normalized = re.sub(r"^```[a-zA-Z]*\s*", "", normalized)
        normalized = re.sub(r"\s*```$", "", normalized).strip()
    for tag in TRADING_TAGS:
        pattern = re.compile(rf"<\s*(/?)\s*{re.escape(tag)}\s*>", re.IGNORECASE)
        normalized = pattern.sub(lambda match, t=tag: f"</{t}>" if match.group(1) else f"<{t}>", normalized)
    return normalized


def normalize_trading_response(
    text: str,
    *,
    agent_name: str,
    initial_resources: str,
    goal: str,
) -> str:
    normalized = canonicalize_xml_tags(text)
    lower = normalized.lower()

    answer = (tag_value(normalized, "player answer") or "").strip().upper()
    trade = (tag_value(normalized, "newly proposed trade") or "").strip()
    if "accept" in lower and "reject" not in lower:
        answer = "ACCEPT"
        trade = "NONE"
    elif answer not in {"ACCEPT", "NONE"}:
        answer = "NONE"

    if answer == "ACCEPT":
        trade = "NONE"
    elif not is_parseable_trade_text(trade):
        trade = "NONE"

    normalized = replace_or_append_tag(normalized, "my name", agent_name)
    normalized = replace_or_append_tag(normalized, "my resources", initial_resources)
    normalized = replace_or_append_tag(normalized, "my goals", goal)
    normalized = replace_or_append_tag(normalized, "reason", tag_value(normalized, "reason") or "Follow the rules.")
    normalized = replace_or_append_tag(normalized, "player answer", answer)
    normalized = replace_or_append_tag(normalized, "message", tag_value(normalized, "message") or "")
    normalized = replace_or_append_tag(normalized, "newly proposed trade", trade)
    return normalized


def is_parseable_trade_text(text: str) -> bool:
    if not text or text.strip().upper() == "NONE":
        return True
    if "|" not in text or "Gives" not in text or "Player RED" not in text or "Player BLUE" not in text:
        return False
    try:
        for player in text.strip().replace("\n", " ").split("|"):
            resources = player.split("Gives", 1)[1].strip()
            for item in resources.split(","):
                name, value = item.split(":", 1)
                if not name.strip():
                    return False
                int(value.strip())
    except (IndexError, ValueError):
        return False
    return True


def resources_dict(resources: Any) -> dict[str, int | float]:
    values = getattr(resources, "resource_dict", resources)
    if not isinstance(values, dict):
        return {}
    return {str(key): value for key, value in values.items()}


def trade_allocations(trade: Any, initial_resources: list[Any]) -> dict[str, dict[str, int | float]] | None:
    if trade in {None, "NONE"}:
        return None
    return {
        "agent_a": resources_dict(trade.execute_trade(initial_resources[0], 0)),
        "agent_b": resources_dict(trade.execute_trade(initial_resources[1], 1)),
    }


def allocation_line(action: str, allocations: dict[str, dict[str, int | float]] | None) -> str:
    if action == "REJECT" or not allocations:
        return "REJECT:"
    a = ", ".join(f"{key}={value}" for key, value in allocations["agent_a"].items())
    b = ", ".join(f"{key}={value}" for key, value in allocations["agent_b"].items())
    return f"{action}: agent_a gets {a}; agent_b gets {b}"


def build_episode(game: Any, plan: dict[str, Any]) -> dict[str, Any]:
    episode = plan["episode"]
    settings = game.game_state[0]["settings"]
    initial_resources = settings["player_initial_resources"]
    role_by_turn = {0: "agent_a", 1: "agent_b"}
    messages: list[dict[str, Any]] = []
    last_offer_allocations: dict[str, dict[str, int | float]] | None = None

    for state in game.game_state[1:]:
        if state.get("current_iteration") == "END":
            continue
        role = role_by_turn.get(state.get("turn"), str(state.get("turn")))
        public = state.get("player_public_info_dict", {})
        answer = str(public.get("player answer", "NONE")).strip().upper()
        proposed_trade = public.get("newly proposed trade")
        offered_allocations = trade_allocations(proposed_trade, initial_resources)
        if offered_allocations is not None:
            last_offer_allocations = offered_allocations

        if answer == "ACCEPT":
            structured = allocation_line("ACCEPT", last_offer_allocations)
        elif offered_allocations is not None:
            structured = allocation_line("OFFER", offered_allocations)
        else:
            structured = "REJECT:"

        messages.append(
            {
                "turn_index": state.get("current_iteration"),
                "role": role,
                "language": episode["role_languages"][role],
                "text": (
                    f"{structured}\n{public.get('message', '')}\n\n"
                    f"RAW_UPSTREAM_RESPONSE:\n{state.get('player_complete_answer', '')}"
                ).strip(),
                "upstream_public": {key: str(value) for key, value in public.items()},
            }
        )

    summary = {}
    if game.game_state and game.game_state[-1].get("current_iteration") == "END":
        summary = game.game_state[-1].get("summary", {})

    final_response = str(summary.get("final_response", "NONE")).upper()
    deal = final_response == "ACCEPT"
    final_resources = summary.get("final_resources", initial_resources)
    final_terms = {
        "agent_a": resources_dict(final_resources[0]),
        "agent_b": resources_dict(final_resources[1]),
    }
    outcomes = summary.get("player_outcome", [False, False])
    payoffs = {
        "agent_a": int(bool(outcomes[0])) if len(outcomes) > 0 else 0,
        "agent_b": int(bool(outcomes[1])) if len(outcomes) > 1 else 0,
    }

    return {
        "episode_id": episode["episode_id"],
        "condition": episode["condition"],
        "game_id": episode["game_id"],
        "language_pair": episode["language_pair"],
        "role_languages": episode["role_languages"],
        "model": episode["model"],
        "seed": episode["seed"],
        "upstream": upstream_commit(),
        "deal": deal,
        "final_terms": final_terms,
        "payoffs": payoffs,
        "payoff_definition": "numeric 1/0 ResourceGoal satisfaction from upstream player_outcome",
        "upstream_player_outcome": [bool(item) for item in outcomes],
        "messages": messages,
    }


def run_episode(plan: dict[str, Any], provider: str, model_metadata: dict[str, Any]) -> dict[str, Any]:
    install_optional_upstream_import_shims()

    from games.trading_game.game import TradingGame
    from ratbench.agents.agents import Agent
    from ratbench.constants import AGENT_ONE, AGENT_TWO
    from ratbench.game_objects.goal import ResourceGoal
    from ratbench.game_objects.resource import Resources

    class AgentImpl(Agent):
        def __init__(
            self,
            agent_name: str,
            role_name: str,
            language: str,
            condition: str,
            model_label: str,
            initial_resources: str,
            goal: str,
        ) -> None:
            super().__init__(agent_name=agent_name)
            self.role_name = role_name
            self.language = language
            self.condition = condition
            self.model = model_label
            self.initial_resources = initial_resources
            self.goal = goal
            self.prompt_entity_initializer = "system"
            self.client, _metadata = make_chat_client(provider)
            self.conversation: list[dict[str, str]] = []
            self.run_epoch_time_ms = None

        def chat(self) -> str:
            raw = self.client.complete(self.conversation, max_tokens=700, temperature=0.2)
            return normalize_trading_response(
                raw,
                agent_name=self.agent_name,
                initial_resources=self.initial_resources,
                goal=self.goal,
            )

        def update_conversation_tracking(self, entity: str, message: Any) -> None:
            role = entity if entity in {"system", "user", "assistant"} else "user"
            content = str(message)
            if role == "system":
                content += (
                    "\n\n"
                    + output_channel_instruction(self.language, self.condition)
                    + " Follow the XML tag format exactly. "
                    "For a proposal, use this exact trade syntax inside <newly proposed trade>: "
                    "Player RED Gives X: integer, Y: integer | Player BLUE Gives X: integer, Y: integer. "
                    "If accepting the prior offer, set <player answer>ACCEPT</player answer> and "
                    "<newly proposed trade>NONE</newly proposed trade>. If rejecting or waiting, set "
                    "<player answer>NONE</player answer> and <newly proposed trade>NONE</newly proposed trade>."
                )
            self.conversation.append({"role": role, "content": content})

        def get_state(self) -> dict[str, Any]:
            return {
                "class": self.__class__.__name__,
                "agent_name": self.agent_name,
                "model": self.model,
                "language": self.language,
                "conversation": list(self.conversation),
                "run_epoch_time_ms": self.run_epoch_time_ms,
            }

    episode = plan["episode"]
    role_languages = episode["role_languages"]
    initial_a = Resources({"X": 25, "Y": 5})
    initial_b = Resources({"X": 5, "Y": 25})
    goal_a = ResourceGoal({"X": 15, "Y": 15})
    goal_b = ResourceGoal({"X": 15, "Y": 15})
    log_dir = ROOT / "artifacts" / "upstream_logs" / episode["episode_id"]
    log_dir.mkdir(parents=True, exist_ok=True)
    agent_a = AgentImpl(
        AGENT_ONE,
        "agent_a",
        role_languages["agent_a"],
        episode["condition"],
        episode["model"],
        str(initial_a),
        str(goal_a),
    )
    agent_b = AgentImpl(
        AGENT_TWO,
        "agent_b",
        role_languages["agent_b"],
        episode["condition"],
        episode["model"],
        str(initial_b),
        str(goal_b),
    )

    game = TradingGame(
        players=[agent_a, agent_b],
        iterations=int(episode["turn_limit"]),
        resources_support_set=Resources({"X": 0, "Y": 0}),
        player_goals=[goal_a, goal_b],
        player_initial_resources=[initial_a, initial_b],
        player_roles=[
            f"You are {AGENT_ONE}; you are agent_a and start by making a proposal.",
            f"You are {AGENT_TWO}; you are agent_b and respond to trades.",
        ],
        player_social_behaviour=["", ""],
        log_dir=str(log_dir),
    )
    game.run()
    built = build_episode(game, plan)
    built["model"] = model_metadata["model"]
    built["model_plan"] = {
        "planned_default_model": episode["model"],
        "execution_provider": model_metadata["provider"],
        "execution_model": model_metadata["model"],
        "evidence_scope": model_metadata["evidence_scope"],
    }
    return built


def write_blocked_artifact(reason: str, error: str | None = None) -> Path:
    payload = {
        "checked_at": utc_now(),
        "status": "BLOCKED",
        "blocker": reason,
        "failed_command": FAILED_COMMAND,
        "message": "C0 resource_exchange baseline requires a usable local Qwen provider.",
        "error": error,
        "next_command": FAILED_COMMAND,
        "related_probe": "artifacts/results/model_endpoint_probe.json",
        "openai_smoke_override_used": False,
    }
    return write_json("artifacts/results/baseline_c0_resource_exchange_en_seed001.blocked.json", payload)


def main() -> int:
    plan = load_plan()
    provider = selected_benchmark_provider()
    failed_command = command_for_provider(provider)
    if provider == "openai_benchmark" and not benchmark_openai_allowed(load_benchmark_model_config()):
        artifact = write_json(
            "artifacts/results/baseline_c0_resource_exchange_en_seed001.openai_benchmark.blocked.json",
            {
                "checked_at": utc_now(),
                "status": "BLOCKED",
                "blocker": "openai_benchmark_override_not_allowed",
                "failed_command": failed_command,
                "message": "OpenAI benchmark provider was requested but config/benchmark_model.json does not allow it.",
                "next_command": (
                    "Use local Qwen with bash scripts/run_c0_resource_exchange_baseline.sh or update "
                    "config/benchmark_model.json explicitly."
                ),
            },
        )
        append_event(
            "baseline",
            "BLOCKED",
            f"C0 OpenAI benchmark resource_exchange baseline blocked by config; "
            f"artifact={artifact.relative_to(ROOT)}; failed_command={failed_command}",
        )
        return 2
    plan = dict(plan)
    plan["expected_artifacts"] = provider_artifacts(plan["expected_artifacts"], provider)

    try:
        model_metadata = run_endpoint_probe(provider, failed_command=failed_command)
    except SystemExit as exc:
        if provider == "openai_benchmark":
            append_event(
                "baseline",
                "BLOCKED",
                f"C0 OpenAI benchmark resource_exchange baseline blocked on provider probe; "
                f"failed_command={failed_command}",
            )
            return int(exc.code) if isinstance(exc.code, int) else 2
        artifact = write_blocked_artifact("local_qwen_endpoint_unreachable", str(exc))
        append_event(
            "baseline",
            "BLOCKED",
            f"C0 resource_exchange baseline blocked on local Qwen endpoint; artifact={artifact.relative_to(ROOT)}; "
            f"failed_command={failed_command}",
        )
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        episode = run_episode(plan, provider, model_metadata)
    except Exception as exc:
        artifact = write_json(
            "artifacts/results/baseline_c0_resource_exchange_en_seed001.error.json",
            {
                "checked_at": utc_now(),
                "status": "ERROR",
                "failed_command": failed_command,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(),
                "upstream": upstream_commit(),
            },
        )
        append_event("baseline", "ERROR", f"C0 resource_exchange baseline failed; artifact={artifact.relative_to(ROOT)}")
        raise

    artifacts = plan["expected_artifacts"]
    transcript_path = write_json(artifacts["transcript"], episode)
    metrics_path = write_metrics(episode, artifacts["metrics"])
    append_event(
        "baseline",
        "OK",
        f"C0 resource_exchange episode completed; transcript={transcript_path.relative_to(ROOT)}; "
        f"metrics={metrics_path.relative_to(ROOT)}; provider={provider}",
    )
    print(json.dumps({"transcript": str(transcript_path), "metrics": str(metrics_path)}, indent=2))
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
