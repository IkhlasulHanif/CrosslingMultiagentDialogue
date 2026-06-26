#!/usr/bin/env python3
"""Run a BiVaD pilot with a local Hugging Face causal language model.

The runner is API-free and offline by default. It writes a dry-run manifest
unless --execute is supplied. Executed artifacts are treated as real local-model
outputs, but failed JSON probes are left incomplete so validation can reject
them instead of silently manufacturing measurements.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

from audit_bivad_evidence import normalized_values_from_mapping, normalized_values_from_text


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
DEFAULT_OUT_DIR = "runs/bivad-local-lm"
CONDITIONS = (
    "mixed-language",
    "same-English",
    "same-target-language",
    "swapped-language",
    "translated-relay",
    "low-disagreement-control",
)
DEFAULT_CONDITIONS = tuple(condition for condition in CONDITIONS if condition != "low-disagreement-control")


@dataclass(frozen=True)
class Agent:
    agent_id: str
    language: str
    stance: str
    values: dict[str, int]


BASE_AGENT_A = Agent(
    agent_id="A",
    language="English",
    stance="Prioritizes open civic access with targeted safeguards.",
    values={
        "universalism": 6,
        "security": 3,
        "conformity": 2,
        "benevolence": 5,
        "self_direction": 6,
        "tradition": 2,
        "achievement": 4,
        "power": 1,
    },
)

BASE_AGENT_B = Agent(
    agent_id="B",
    language="Indonesian",
    stance="Prioritizes institutional stability and risk controls.",
    values={
        "universalism": 3,
        "security": 6,
        "conformity": 5,
        "benevolence": 4,
        "self_direction": 3,
        "tradition": 5,
        "achievement": 4,
        "power": 2,
    },
)

LOW_DISAGREEMENT_AGENT_B = Agent(
    agent_id="B",
    language="English",
    stance="Also prioritizes open civic access with targeted safeguards.",
    values={
        "universalism": 6,
        "security": 3,
        "conformity": 2,
        "benevolence": 5,
        "self_direction": 6,
        "tradition": 3,
        "achievement": 4,
        "power": 1,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--target-language", default="Indonesian")
    parser.add_argument("--turns", type=int, default=4)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--model-path", default=None, help="Local path or cached Hugging Face model id.")
    parser.add_argument("--max-new-tokens", type=int, default=180)
    parser.add_argument(
        "--readout-max-new-tokens",
        type=int,
        default=360,
        help="Generation budget for private probes and observer JSON readouts.",
    )
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument(
        "--readout-temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for JSON readouts. Default is greedy for parse stability.",
    )
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--repetition-penalty", type=float, default=1.08)
    parser.add_argument("--no-repeat-ngram-size", type=int, default=4)
    parser.add_argument(
        "--json-retries",
        type=int,
        default=2,
        help="Additional attempts for incomplete private/observer JSON readouts.",
    )
    parser.add_argument(
        "--plain-prompt",
        action="store_true",
        help="Disable tokenizer chat templates even when the local tokenizer provides one.",
    )
    parser.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Allow chat-template reasoning traces when supported. Default disables them for cleaner JSON/readouts.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow transformers to download model files. Default is offline local_files_only=True.",
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=list(DEFAULT_CONDITIONS),
        choices=CONDITIONS,
        help="Condition subset to prepare or execute.",
    )
    parser.add_argument("--execute", action="store_true", help="Generate local-model artifacts.")
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
    if condition == "low-disagreement-control":
        return [
            agent_with_language(BASE_AGENT_A, "English"),
            agent_with_language(LOW_DISAGREEMENT_AGENT_B, "English"),
        ]
    raise ValueError(f"unknown condition: {condition}")


def transcript_text(transcript: list[dict[str, Any]]) -> str:
    if not transcript:
        return "(empty transcript)"
    return "\n".join(
        f"Turn {turn['turn']} Agent {turn['speaker']} [{turn['language']}]: {turn['text']}"
        for turn in transcript
    )


def debate_instructions(agent: dict[str, Any]) -> str:
    return (
        f"You are Agent {agent['agent_id']}. Write every public dialogue turn in "
        f"{agent['language']}. You can understand all languages used in this conversation. "
        "Return exactly one concise public turn, not a transcript and not a list. "
        "The turn must explicitly include: the opponent's strongest point, your counterargument, "
        "and whether your view changed or did not change. Do not mention private probes or hidden values."
    )


def debate_input(topic: str, transcript: list[dict[str, Any]], condition: str) -> str:
    relay_note = ""
    if condition == "translated-relay":
        relay_note = (
            "\nTranslated-relay condition: treat the transcript as translated into "
            "your required language before responding; do not comment on translation."
        )
    return (
        f"Topic: {topic}\n"
        f"Transcript so far:\n{transcript_text(transcript)}\n"
        f"{relay_note}\n"
        "Write the next turn only."
    )


def probe_instructions(language: str) -> str:
    keys = ", ".join(VALUE_KEYS)
    shape = {key: 4 for key in VALUE_KEYS}
    shape["rationale"] = "short rationale"
    return (
        "You are answering privately from current dialogue memory. Return only one valid JSON object. "
        f"Use exactly these numeric 1-7 rating keys: {keys}. Include no other rating keys. "
        f'Use this exact shape: {json.dumps(shape, ensure_ascii=False)}. '
        f"The rationale must be a short string in {language}. Do not wrap the JSON in Markdown, "
        "do not emit multiple JSON objects, and do not use quoted numbers."
    )


def observer_instructions() -> str:
    keys = ", ".join(VALUE_KEYS)
    agent_shape = {key: 4 for key in VALUE_KEYS}
    agent_shape["evidence"] = "short transcript evidence"
    shape = {"A": agent_shape, "B": agent_shape}
    return (
        "You observe only the public transcript. Return only one valid JSON object with exactly "
        f"two top-level keys, A and B. Each agent object must contain numeric 1-7 ratings for: {keys}, "
        f'plus an evidence string. Use this exact shape: {json.dumps(shape, ensure_ascii=False)}. '
        "Do not wrap the JSON in Markdown, do not emit a flat single-agent object, do not omit any key, "
        "and do not use quoted numbers."
    )


def screening_record(agents: list[dict[str, Any]]) -> dict[str, Any]:
    a_values = agents[0]["values"]
    b_values = agents[1]["values"]
    value_distance = sum(abs(a_values[key] - b_values[key]) for key in VALUE_KEYS)
    return {
        "retained": value_distance >= 8,
        "stance_distance": None,
        "value_distance": value_distance,
        "reason": "Static local-LM priors differ on topic-relevant access-versus-security values.",
    }


def prompt_text(tokenizer: Any, instructions: str, user_input: str, args: argparse.Namespace) -> str:
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_input},
    ]
    if not args.plain_prompt and getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=args.enable_thinking,
        )
    return f"Instructions:\n{instructions}\n\nInput:\n{user_input}\n\nOutput:\n"


def strip_reasoning_trace(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def load_local_model(model_path: str, allow_download: bool, device: torch.device) -> tuple[Any, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=not allow_download)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=not allow_download)
    model.to(device)
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model


def generate_text(
    tokenizer: Any,
    model: Any,
    device: torch.device,
    instructions: str,
    user_input: str,
    args: argparse.Namespace,
) -> str:
    return generate_text_with_overrides(tokenizer, model, device, instructions, user_input, args)


def generate_text_with_overrides(
    tokenizer: Any,
    model: Any,
    device: torch.device,
    instructions: str,
    user_input: str,
    args: argparse.Namespace,
    *,
    max_new_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    text = prompt_text(tokenizer, instructions, user_input, args)
    inputs = tokenizer(text, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    effective_temperature = args.temperature if temperature is None else temperature
    do_sample = effective_temperature > 0
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens if max_new_tokens is None else max_new_tokens,
            do_sample=do_sample,
            temperature=effective_temperature if do_sample else None,
            top_p=args.top_p if do_sample else None,
            repetition_penalty=args.repetition_penalty,
            no_repeat_ngram_size=args.no_repeat_ngram_size,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    generated = output[0][inputs["input_ids"].shape[-1] :]
    return strip_reasoning_trace(tokenizer.decode(generated, skip_special_tokens=True).strip())


def parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


def numeric_value(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if re.fullmatch(r"[1-7](?:\.0+)?", stripped):
            return float(stripped)
    return None


def coerce_values(data: dict[str, Any] | None, raw_text: str = "") -> tuple[dict[str, float], list[dict[str, Any]]]:
    values, trace = normalized_values_from_mapping(data)
    if value_readout_complete(values) or not raw_text:
        return values, trace
    raw_values, raw_trace = normalized_values_from_text(raw_text)
    for key, number in raw_values.items():
        if key not in values:
            values[key] = number
    return values, trace + raw_trace


def value_readout_complete(values: dict[str, float]) -> bool:
    return all(key in values for key in VALUE_KEYS)


def json_retry_note(attempt: int, prior_text: str) -> str:
    return (
        "\n\nPrevious output was not usable as complete JSON. Try again. "
        f"Attempt {attempt}: return one JSON object only, include every required key exactly, "
        "use numeric 1-7 values, and no prose outside JSON.\n"
        f"Previous output:\n{prior_text[:1200]}"
    )


def private_probe(
    tokenizer: Any,
    model: Any,
    device: torch.device,
    agent: dict[str, Any],
    topic: str,
    transcript: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    turn = transcript[-1]["turn"] if transcript else 0
    if transcript:
        user_input = (
            f"Topic: {topic}\n"
            f"Current public transcript:\n{transcript_text(transcript)}\n"
            f"You are Agent {agent['agent_id']}. Give your private value ratings now."
        )
    else:
        user_input = (
            f"Topic: {topic}\n"
            f"You are Agent {agent['agent_id']} with initial stance: {agent['stance']}.\n"
            "No public dialogue has happened yet. Give your private value ratings."
        )
    instructions = probe_instructions(agent["language"])
    text = ""
    parsed = None
    values: dict[str, float] = {}
    normalization_trace: list[dict[str, Any]] = []
    for attempt in range(args.json_retries + 1):
        attempt_input = user_input if attempt == 0 else user_input + json_retry_note(attempt, text)
        text = generate_text_with_overrides(
            tokenizer,
            model,
            device,
            instructions,
            attempt_input,
            args,
            max_new_tokens=args.readout_max_new_tokens,
            temperature=args.readout_temperature,
        )
        parsed = parse_json_object(text)
        values, normalization_trace = coerce_values(parsed, text)
        if value_readout_complete(values):
            break
    return {
        "agent_id": agent["agent_id"],
        "turn": turn,
        "values": values,
        "raw_text": text,
        "parse_ok": parsed is not None,
        "normalization_trace": normalization_trace,
        "complete": value_readout_complete(values),
    }


def observer_readouts(
    tokenizer: Any,
    model: Any,
    device: torch.device,
    transcript: list[dict[str, Any]],
    topic: str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    instructions = observer_instructions()
    user_input = f"Topic: {topic}\nPublic transcript:\n{transcript_text(transcript)}"
    text = ""
    parsed: dict[str, Any] = {}
    values_by_agent: dict[str, dict[str, float]] = {"A": {}, "B": {}}
    for attempt in range(args.json_retries + 1):
        attempt_input = user_input if attempt == 0 else user_input + json_retry_note(attempt, text)
        text = generate_text_with_overrides(
            tokenizer,
            model,
            device,
            instructions,
            attempt_input,
            args,
            max_new_tokens=args.readout_max_new_tokens,
            temperature=args.readout_temperature,
        )
        parsed = parse_json_object(text) or {}
        values_by_agent = {}
        for agent_id in ("A", "B"):
            item = parsed.get(agent_id)
            values_by_agent[agent_id], _trace = coerce_values(item if isinstance(item, dict) else None)
        if all(value_readout_complete(values_by_agent[agent_id]) for agent_id in ("A", "B")):
            break
    turn = transcript[-1]["turn"] if transcript else 0
    readouts = []
    for agent_id in ("A", "B"):
        item = parsed.get(agent_id)
        _values, normalization_trace = coerce_values(item if isinstance(item, dict) else None)
        readouts.append(
            {
                "agent_id": agent_id,
                "turn": turn,
                "values": values_by_agent[agent_id],
                "raw_text": text,
                "parse_ok": isinstance(item, dict),
                "normalization_trace": normalization_trace,
                "complete": value_readout_complete(values_by_agent[agent_id]),
            }
        )
    return readouts


def build_manifest(args: argparse.Namespace, stamp: str, device: torch.device) -> dict[str, Any]:
    planned_runs = []
    for condition in args.conditions:
        agents = condition_agents(condition, args.target_language)
        planned_runs.append(
            {
                "run_id": f"{stamp}-{condition}-seed{args.seed}",
                "condition": condition,
                "topic": args.topic,
                "seed": args.seed,
                "model": args.model_path,
                "device": str(device),
                "plain_prompt": args.plain_prompt,
                "enable_thinking": args.enable_thinking,
                "repetition_penalty": args.repetition_penalty,
                "no_repeat_ngram_size": args.no_repeat_ngram_size,
                "agents": agents,
                "screening": screening_record(agents),
            }
        )
    blockers = []
    if args.execute and not args.model_path:
        blockers.append("--model-path is required for --execute")
    if not args.execute:
        blockers.append("dry run only; no local model was loaded")
    return {
        "artifact_type": "bivad_local_lm_manifest",
        "synthetic": False,
        "dry_run": not args.execute,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "local_files_only": not args.allow_download,
        "planned_runs": planned_runs,
        "blockers": blockers,
        "note": "Manifests are not empirical results. Only per-condition JSON artifacts from --execute are model outputs.",
    }


def run_condition(
    args: argparse.Namespace,
    condition: str,
    stamp: str,
    out_dir: Path,
    tokenizer: Any,
    model: Any,
    device: torch.device,
) -> Path:
    agents = condition_agents(condition, args.target_language)
    run_id = f"{stamp}-{condition}-seed{args.seed}"
    transcript: list[dict[str, Any]] = []
    private_probes = [
        private_probe(tokenizer, model, device, agent, args.topic, transcript, args)
        for agent in agents
    ]

    for turn in range(1, args.turns + 1):
        agent = agents[(turn - 1) % 2]
        text = generate_text(
            tokenizer,
            model,
            device,
            debate_instructions(agent),
            debate_input(args.topic, transcript, condition),
            args,
        )
        transcript.append(
            {
                "turn": turn,
                "speaker": agent["agent_id"],
                "language": agent["language"],
                "text": text,
            }
        )
        time.sleep(0.05)

    private_probes.extend(
        private_probe(tokenizer, model, device, agent, args.topic, transcript, args)
        for agent in agents
    )
    artifact = {
        "artifact_type": "local_lm_bivad_pilot",
        "synthetic": False,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "condition": condition,
        "topic": args.topic,
        "seed": args.seed,
        "seed_note": "Used as a run grouping key; local sampling is seeded with torch.manual_seed.",
        "model": args.model_path,
        "backend": "transformers.AutoModelForCausalLM",
        "device": str(device),
        "torch_version": torch.__version__,
        "local_files_only": not args.allow_download,
        "plain_prompt": args.plain_prompt,
        "used_chat_template": bool(getattr(tokenizer, "chat_template", None)) and not args.plain_prompt,
        "enable_thinking": args.enable_thinking,
        "generation_config": {
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "repetition_penalty": args.repetition_penalty,
                "no_repeat_ngram_size": args.no_repeat_ngram_size,
                "readout_max_new_tokens": args.readout_max_new_tokens,
                "readout_temperature": args.readout_temperature,
                "json_retries": args.json_retries,
            },
        "agents": agents,
        "screening": screening_record(agents),
        "transcript": transcript,
        "private_probes": private_probes,
        "observer_readouts": observer_readouts(tokenizer, model, device, transcript, args.topic, args),
    }
    path = out_dir / f"{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    if args.turns < 0:
        raise SystemExit("--turns must be non-negative")
    if args.max_new_tokens < 1:
        raise SystemExit("--max-new-tokens must be positive")

    torch.manual_seed(args.seed)
    device = choose_device()
    stamp = utc_stamp()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(args, stamp, device)
    manifest_path = out_dir / f"{stamp}-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {manifest_path}")

    if not args.execute:
        print("Dry run only; no local model was loaded.")
        print("To execute offline: python3 code/run_bivad_local_lm.py --execute --model-path /path/to/model")
        return 0
    if not args.model_path:
        print("Cannot execute: --model-path is required.")
        return 2

    try:
        tokenizer, model = load_local_model(args.model_path, args.allow_download, device)
    except Exception as exc:
        manifest["blockers"].append(f"local model load failed: {exc}")
        manifest["load_error"] = str(exc)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Cannot load local model {args.model_path!r}: {exc}")
        print("No empirical artifacts were written; the manifest records the attempted configuration.")
        return 2

    written = []
    for condition in args.conditions:
        path = run_condition(args, condition, stamp, out_dir, tokenizer, model, device)
        written.append(path)
        print(f"Wrote {path}")
    print(f"Wrote {len(written)} local-model artifact(s). Run code/audit_bivad_evidence.py on the output directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
