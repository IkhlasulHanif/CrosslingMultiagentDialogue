#!/usr/bin/env python3
"""Run a narrow C0 GovSim fishery smoke with the configured OpenAI smoke model.

This is bring-up evidence only. It uses the upstream GovSim fishery environment
and fishery prompt text from ``vendor/govsim``, but bypasses the unavailable
PathFinder submodule by calling the explicitly configured OpenAI smoke endpoint
through the setting-local chat adapter.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = ROOT / "code"
GOVSIM_DIR = ROOT / "vendor" / "govsim"
RESULT_DIR = ROOT / "artifacts" / "results"
LOG_DIR = ROOT / "artifacts" / "logs"
RUN_STORAGE_ROOT = RESULT_DIR / "govsim_openai_smoke_runs"

sys.path.insert(0, str(CODE_DIR))
sys.path.insert(0, str(GOVSIM_DIR))

from local_model_adapter import ChatMessage, LocalModelError, VLLMChatAdapter  # noqa: E402
from channel_instructions import (  # noqa: E402
    append_system_channel_instruction,
    conversation_instruction,
    harvest_instruction,
    limit_instruction,
    normalize_language,
    summary_instruction,
)
from process_metrics import summarize_transcript  # noqa: E402
from transcript_logger import TranscriptContext, TranscriptWriter  # noqa: E402

from simulation.persona.common import (  # noqa: E402
    PersonaAction,
    PersonaActionChat,
    PersonaActionHarvesting,
    PersonaIdentity,
)
from simulation.scenarios.fishing.environment import FishingConcurrentEnv  # noqa: E402
from subskills.fishing.utils import get_sytem_prompt_v4, prompt_description_simulation  # noqa: E402


NAMES = ["John", "Kate", "Jack", "Emma", "Luke"]
HARVEST_RE = re.compile(r"-?\d+")
TRANSLATION_PACK_PATH = ROOT / "config" / "translations" / "en_id_fishery_draft.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def append_event(kind: str, status: str, message: str) -> None:
    event = {"ts": utc_now(), "kind": kind, "status": status, "message": message}
    path = ROOT / "plan" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def translation_entries() -> dict[str, str]:
    pack = json.loads(TRANSLATION_PACK_PATH.read_text(encoding="utf-8"))
    return {entry["id"]: entry["id_text"] for entry in pack.get("entries", [])}


def tr(entry_id: str, **values: Any) -> str:
    text = translation_entries()[entry_id]
    return text.format(**values)


def load_smoke_config() -> dict[str, Any]:
    path = ROOT / "config" / "smoke_model.json"
    if not path.exists():
        raise RuntimeError("missing config/smoke_model.json")
    return json.loads(path.read_text(encoding="utf-8"))


def read_api_key(config: dict[str, Any]) -> tuple[str | None, str | None]:
    env_key = config.get("env_key") or "OPENAI_API_KEY"
    value = os.environ.get(env_key)
    if value:
        return value.strip(), f"env:{env_key}"

    for candidate in config.get("api_key_file_candidates", []):
        path = (ROOT / candidate).resolve()
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text, str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return None, None


def make_env(run_storage: Path) -> FishingConcurrentEnv:
    cfg = OmegaConf.create(
        {
            "name": "fish_baseline_concurrent_openai_smoke",
            "class_name": "fishing_perturbation_concurrent_env",
            "max_num_rounds": 1,
            "initial_resource_in_pool": 100,
            "poupulation_change_after_round": "double_100_cap",
            "observation_other_agents_harvesting": True,
            "language_nature": "unconstrained",
            "num_agents": 5,
            "harvesting_order": "concurrent",
            "assign_resource_strategy": "stochastic",
            "inject_universalization": False,
            "inject_scenario_dynamic": False,
            "perturbations": [],
        }
    )
    id_to_name = {f"persona_{i}": name for i, name in enumerate(NAMES)}
    id_to_name["framework"] = "framework"
    return FishingConcurrentEnv(cfg, str(run_storage), id_to_name)


def identities() -> dict[str, PersonaIdentity]:
    return {f"persona_{i}": PersonaIdentity(f"persona_{i}", name) for i, name in enumerate(NAMES)}


def system_prompt(identity: PersonaIdentity, language: str) -> str:
    language = normalize_language(language)
    return append_system_channel_instruction(get_sytem_prompt_v4(identity), language)


def harvest_user_prompt(identity: PersonaIdentity, obs: Any, language: str) -> str:
    language = normalize_language(language)
    memory_lines = "\n".join(f"- {event.created:%Y-%m-%d}: {event.description}" for event in obs.events)
    return (
        f"{prompt_description_simulation(identity.name, obs.current_resource_num)}\n"
        f"Key memories of {identity.name} (format: YYYY-MM-DD: memory):\n{memory_lines}\n\n"
        f"Task: With a fishing range set between 0-{obs.current_resource_num}, "
        "how many tons of fish would you catch this month?\n"
        f"{harvest_instruction(language)}"
    )


def prompt_harvest(identity: PersonaIdentity, obs: Any, language: str = "EN") -> list[dict[str, str]]:
    user_text = harvest_user_prompt(identity, obs, language)
    return [
        {"role": "system", "content": system_prompt(identity, language)},
        {"role": "user", "content": user_text},
    ]


def prompt_harvest_en(identity: PersonaIdentity, obs: Any) -> list[dict[str, str]]:
    """Backward-compatible helper for older smoke callers."""

    memory_lines = "\n".join(f"- {event.created:%Y-%m-%d}: {event.description}" for event in obs.events)
    user_text = (
        f"{prompt_description_simulation(identity.name, obs.current_resource_num)}\n"
        f"Key memories of {identity.name} (format: YYYY-MM-DD: memory):\n{memory_lines}\n\n"
        f"Task: With a fishing range set between 0-{obs.current_resource_num}, "
        "how many tons of fish would you catch this month?\n"
        'Answer with brief reasoning and put the final integer after "Answer:".'
    )
    return [
        {"role": "system", "content": get_sytem_prompt_v4(identity)},
        {"role": "user", "content": user_text},
    ]


def parse_harvest(text: str, lower: int, upper: int) -> tuple[int, bool]:
    matches = HARVEST_RE.findall(text)
    if not matches:
        return lower, False
    value = int(matches[-1])
    return max(lower, min(upper, value)), lower <= value <= upper


def complete(
    adapter: VLLMChatAdapter,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = 220,
    temperature: float = 0.2,
):
    return adapter.complete(
        [ChatMessage(**message) for message in messages],
        temperature=temperature,
        max_tokens=max_tokens,
    )


def choose_harvest(
    adapter: VLLMChatAdapter,
    transcript: TranscriptWriter,
    identity: PersonaIdentity,
    obs: Any,
    language: str = "EN",
) -> tuple[PersonaActionHarvesting, dict[str, Any]]:
    messages = prompt_harvest(identity, obs, language)
    response = complete(adapter, messages)
    quantity, parseable = parse_harvest(response.visible_text, 0, int(obs.current_resource_num))
    transcript.log_model_response(
        round_index=0,
        phase="harvest",
        agent_id=identity.agent_id,
        role="assistant",
        response=response,
        language=language,
        prompt_messages=messages,
        extra={"parsed_harvest": quantity, "parseable": parseable},
    )
    action = PersonaActionHarvesting(
        identity.agent_id,
        "lake",
        quantity,
        stats={f"{identity.agent_id}_collected_resource": quantity},
        html_interactions=[response.visible_text],
    )
    return action, {"agent_id": identity.agent_id, "wanted_resource": quantity, "parseable": parseable}


def conversation_prompt(
    identity: PersonaIdentity,
    resource_report: str,
    conversation: list[tuple[PersonaIdentity, str]],
    language: str = "EN",
) -> list[dict[str, str]]:
    language = normalize_language(language)
    history = "\n".join(f"- {speaker.name}: {utterance}" for speaker, utterance in conversation)
    user_text = (
        f"Monthly report: {resource_report}\n\n"
        f"Conversation so far:\n{history or '- No one has spoken yet.'}\n\n"
        f"{conversation_instruction(language)}"
    )
    return [
        {"role": "system", "content": system_prompt(identity, language)},
        {"role": "user", "content": user_text},
    ]


def resource_report_for_language(obs: Any, ids: dict[str, PersonaIdentity], language: str) -> str:
    return " ".join(f"{ids[agent_id].name} caught {amount} tons." for agent_id, amount in obs.agent_resource_num.items())


def run_conversation(
    adapter: VLLMChatAdapter,
    transcript: TranscriptWriter,
    ids: dict[str, PersonaIdentity],
    obs: Any,
    language: str = "EN",
) -> PersonaActionChat:
    language = normalize_language(language)
    report = resource_report_for_language(obs, ids, language)
    conversation: list[tuple[PersonaIdentity, str]] = []
    html_interactions: list[str] = []

    for identity in ids.values():
        messages = conversation_prompt(identity, report, conversation, language)
        response = complete(adapter, messages, max_tokens=140)
        utterance = response.visible_text.strip().splitlines()[0].strip('" ')
        conversation.append((identity, utterance))
        html_interactions.append(utterance)
        transcript.log_model_response(
            round_index=0,
            phase="conversation",
            agent_id=identity.agent_id,
            role="assistant",
            response=response,
            language=language,
            prompt_messages=messages,
        )

    transcript_text = "\n".join(f"{speaker.name}: {utterance}" for speaker, utterance in conversation)
    summary_messages = [
        {
            "role": "system",
            "content": append_system_channel_instruction(
                "You summarize group decisions for a fishery simulation.",
                language,
            ),
        },
        {"role": "user", "content": f"{summary_instruction(language)}\n{transcript_text}"},
    ]
    summary = complete(adapter, summary_messages, max_tokens=100, temperature=0.0)
    transcript.log_model_response(
        round_index=0,
        phase="conversation_summary",
        agent_id="framework",
        role="assistant",
        response=summary,
        language=language,
        prompt_messages=summary_messages,
    )

    limit_messages = [
        {
            "role": "system",
            "content": append_system_channel_instruction(
                "Extract numeric agreements from fishery conversations.",
                language,
            ),
        },
        {"role": "user", "content": f"{limit_instruction(language)}\n\nConversation:\n{transcript_text}"},
    ]
    limit_response = complete(adapter, limit_messages, max_tokens=20, temperature=0.0)
    transcript.log_model_response(
        round_index=0,
        phase="conversation_resource_limit",
        agent_id="framework",
        role="assistant",
        response=limit_response,
        language=language,
        prompt_messages=limit_messages,
    )
    limit, parseable = parse_harvest(limit_response.visible_text, 0, 100)
    resource_limit = limit if parseable and limit > 0 else None
    html_interactions.extend([summary.visible_text, limit_response.visible_text])

    current_agent_id = obs.current_location_agents and next(
        (agent_id for agent_id, location in obs.current_location_agents.items() if location == "restaurant"),
        "persona_0",
    )
    return PersonaActionChat(
        current_agent_id,
        "restaurant",
        conversation,
        resource_limit,
        stats={"conversation_resource_limit": resource_limit},
        html_interactions=html_interactions,
    )


def gini(values: list[float]) -> float:
    if not values or sum(values) == 0:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    weighted = sum((index + 1) * value for index, value in enumerate(ordered))
    return (2 * weighted) / (n * sum(ordered)) - (n + 1) / n


def run_episode(
    adapter: VLLMChatAdapter,
    model_name: str,
    run_id: str,
    *,
    provider: str = "openai",
    evidence_scope: str = "OpenAI smoke bring-up only; not Qwen3-1.7B research-matrix evidence",
    condition: str = "C0",
    language: str = "EN",
    language_pair: str = "EN-ID",
    schema_version: str = "govsim-c0-openai-smoke-v1",
    episode_id: str = "c0-openai-smoke-0001",
    run_storage_root: Path = RUN_STORAGE_ROOT,
) -> dict[str, Any]:
    language = normalize_language(language)
    pair_languages = tuple(part.strip().upper() for part in language_pair.split("-"))
    if len(pair_languages) != 2:
        raise ValueError(f"expected two-language pair, got {language_pair!r}")
    run_storage = run_storage_root / run_id
    run_storage.mkdir(parents=True, exist_ok=True)
    ids = identities()
    env = make_env(run_storage)
    context = TranscriptContext(
        run_id=run_id,
        condition=condition,
        language_pair=language_pair,
        episode_id=episode_id,
        seed=42,
        metadata={
            "benchmark": "GovSim",
            "substrate": "fishery",
            "provider": provider,
            "model": model_name,
            "evidence_scope": evidence_scope,
            "rule_prompt_policy": "rules/private state in English; interaction output constrained by assigned channel",
            "assigned_output_language": language,
        },
    )
    transcript = TranscriptWriter.for_run(ROOT, context)

    agent_id, obs = env.reset(seed=42)
    harvest_rows: list[dict[str, Any]] = []
    step_count = 0
    terminations: dict[str, bool] = {}

    while step_count < 80:
        step_count += 1
        if obs.current_location == "lake" and obs.phase == "lake":
            action, row = choose_harvest(adapter, transcript, ids[agent_id], obs, language)
            harvest_rows.append(row)
        elif obs.current_location == "lake" and obs.phase == "pool_after_harvesting":
            action = PersonaAction(agent_id, "lake")
        elif obs.current_location == "restaurant":
            action = run_conversation(adapter, transcript, ids, obs, language)
        elif obs.current_location == "home":
            action = PersonaAction(agent_id, "home")
        else:
            raise RuntimeError(f"unexpected GovSim state: agent={agent_id} phase={obs.phase} location={obs.current_location}")

        next_state = env.step(action)
        if next_state is None:
            break
        agent_id, obs, rewards, terminations = next_state
        if terminations and any(terminations.values()):
            break
    else:
        raise RuntimeError("episode step cap reached before termination")

    welfare = {agent: float(value) for agent, value in env.rewards.items()}
    transcript_summary_path = LOG_DIR / f"{run_id}_process_metrics.json"
    process_summary = summarize_transcript(transcript.path, pair_languages=pair_languages)
    write_json(transcript_summary_path, process_summary)

    parseable_count = sum(1 for row in harvest_rows if row["parseable"])
    total_harvest_prompts = len(harvest_rows)
    result = {
        "schema_version": schema_version,
        "timestamp_utc": utc_now(),
        "empirical_episode_ran": True,
        "evidence_scope": evidence_scope,
        "condition": condition,
        "language": language,
        "model_provider": provider,
        "model": model_name,
        "upstream_env": "vendor/govsim/simulation/scenarios/fishing/environment/env.py",
        "upstream_prompt_source": "vendor/govsim/subskills/fishing/utils.py",
        "pathfinder_submodule_status": "unresolved; bypassed for smoke with setting-local OpenAI-compatible adapter",
        "rounds_configured": 1,
        "step_count": step_count,
        "survival_time": int(env.num_round),
        "total_welfare": sum(welfare.values()),
        "agent_welfare": welfare,
        "gini": gini(list(welfare.values())),
        "parseable_harvest_count": parseable_count,
        "harvest_prompt_count": total_harvest_prompts,
        "parseable_harvest_rate": parseable_count / total_harvest_prompts if total_harvest_prompts else 0.0,
        "harvests": harvest_rows,
        "resource_remaining_before_reproduction": int(env.internal_global_state["resource_in_pool"]),
        "transcript_path": str(transcript.path.relative_to(ROOT)),
        "process_metrics_path": str(transcript_summary_path.relative_to(ROOT)),
        "env_log_path": str((run_storage / "log_env.json").relative_to(ROOT)),
    }
    return result


def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    run_id = f"govsim_c0_openai_smoke_{stamp()}"
    result_path = RESULT_DIR / f"{run_id}.json"

    try:
        config = load_smoke_config()
        if config.get("provider") != "openai":
            raise RuntimeError("config/smoke_model.json does not allow provider=openai for smoke")
        api_key, key_source = read_api_key(config)
        if not api_key:
            raise RuntimeError("missing OpenAI smoke API key from env or configured key files")
        model_name = os.environ.get(config.get("env_model") or "OPENAI_SMOKE_MODEL") or config.get("default_model")
        adapter = VLLMChatAdapter(
            base_url="https://api.openai.com/v1",
            model=model_name,
            api_key=api_key,
            timeout_s=90.0,
            max_retries=2,
            retry_sleep_s=2.0,
        )
        result = run_episode(adapter, model_name, run_id)
        result["api_key_source"] = key_source
        write_json(result_path, result)
        append_event(
            "smoke",
            "OK",
            f"GovSim C0 OpenAI smoke produced transcript/result artifact={result_path.relative_to(ROOT)} transcript={result['transcript_path']}",
        )
        print(result_path.relative_to(ROOT))
        return 0
    except (LocalModelError, Exception) as exc:
        result = {
            "schema_version": "govsim-c0-openai-smoke-v1",
            "timestamp_utc": utc_now(),
            "empirical_episode_ran": False,
            "evidence_scope": "blocked OpenAI smoke bring-up only; not Qwen3-1.7B research-matrix evidence",
            "condition": "C0",
            "model_provider": "openai",
            "blockers": [f"{type(exc).__name__}: {exc}"],
            "traceback_tail": traceback.format_exc()[-4000:],
            "next_command_once_unblocked": "./harness.sh run-smoke",
        }
        write_json(result_path, result)
        append_event("smoke", "BLOCKED", f"GovSim C0 OpenAI smoke blocked: {type(exc).__name__}: {exc}; artifact={result_path.relative_to(ROOT)}")
        print(result_path.relative_to(ROOT))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
