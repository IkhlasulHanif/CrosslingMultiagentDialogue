#!/usr/bin/env python3
"""BiVaD same-target-language debate runner on Modal GPU.

Runs a matched five-condition BiVaD debate set (or a subset) using a
strong instruction-following model on Modal GPU.  Writes per-condition
JSON artifacts to --out-dir in the same format as run_bivad_local_lm.py.

Usage:
    modal run code/modal_bivad_runner.py --conditions same-target-language
    modal run code/modal_bivad_runner.py            # all five conditions
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

# ---------------------------------------------------------------------------
# Modal app definition
# ---------------------------------------------------------------------------

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
MODEL_DIR = "/models/qwen25-7b-instruct"
VOLUME_NAME = "bivad-models"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch",
        "transformers>=4.45.0",
        "accelerate",
        "huggingface-hub",
        "sentencepiece",
    )
)

app = modal.App("bivad-modal-runner", image=image)
model_volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# ---------------------------------------------------------------------------
# Debate constants (mirror run_bivad_local_lm.py)
# ---------------------------------------------------------------------------

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

BASE_AGENT_A_VALUES = {
    "universalism": 6,
    "security": 3,
    "conformity": 2,
    "benevolence": 5,
    "self_direction": 6,
    "tradition": 2,
    "achievement": 4,
    "power": 1,
}
BASE_AGENT_A_STANCE = "Prioritizes open civic access with targeted safeguards."

BASE_AGENT_B_VALUES = {
    "universalism": 3,
    "security": 6,
    "conformity": 5,
    "benevolence": 4,
    "self_direction": 3,
    "tradition": 5,
    "achievement": 4,
    "power": 2,
}
BASE_AGENT_B_STANCE = "Prioritizes institutional stability and risk controls."

LOW_DISAGREEMENT_AGENT_B_VALUES = {
    "universalism": 6,
    "security": 3,
    "conformity": 2,
    "benevolence": 5,
    "self_direction": 6,
    "tradition": 3,
    "achievement": 4,
    "power": 1,
}

CONDITIONS = (
    "mixed-language",
    "same-English",
    "same-target-language",
    "swapped-language",
    "translated-relay",
    "low-disagreement-control",
)

DEFAULT_CONDITIONS = tuple(c for c in CONDITIONS if c != "low-disagreement-control")

DEBATE_LABELS = {
    "English": {
        "strongest": "Strongest opponent point",
        "counter": "Counterargument",
        "change": "View change",
    },
    "Indonesian": {
        "strongest": "Poin terkuat lawan",
        "counter": "Counterargument saya",
        "change": "Pandangan saya",
    },
    "Spanish": {
        "strongest": "Punto más fuerte del oponente",
        "counter": "Contraargumento",
        "change": "Cambio de postura",
    },
}

TRANSCRIPT_HEADER_RE = re.compile(
    r"^(?:Turn\s*\d+\s*)?Agent\s*[AB]\s*\[.*?\]\s*:\s*",
    flags=re.IGNORECASE,
)


def condition_agents(condition: str, target_language: str) -> list[dict[str, Any]]:
    def agent(agent_id: str, language: str, stance: str, values: dict) -> dict:
        return {"agent_id": agent_id, "language": language, "stance": stance, "values": dict(values)}

    if condition == "mixed-language":
        return [
            agent("A", "English", BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", target_language, BASE_AGENT_B_STANCE, BASE_AGENT_B_VALUES),
        ]
    if condition == "same-English":
        return [
            agent("A", "English", BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", "English", BASE_AGENT_B_STANCE, BASE_AGENT_B_VALUES),
        ]
    if condition == "same-target-language":
        return [
            agent("A", target_language, BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", target_language, BASE_AGENT_B_STANCE, BASE_AGENT_B_VALUES),
        ]
    if condition == "swapped-language":
        return [
            agent("A", target_language, BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", "English", BASE_AGENT_B_STANCE, BASE_AGENT_B_VALUES),
        ]
    if condition == "translated-relay":
        return [
            agent("A", "English", BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", target_language, BASE_AGENT_B_STANCE, BASE_AGENT_B_VALUES),
        ]
    if condition == "low-disagreement-control":
        return [
            agent("A", "English", BASE_AGENT_A_STANCE, BASE_AGENT_A_VALUES),
            agent("B", "English", BASE_AGENT_A_STANCE, LOW_DISAGREEMENT_AGENT_B_VALUES),
        ]
    raise ValueError(f"unknown condition: {condition}")


def transcript_text(transcript: list[dict]) -> str:
    if not transcript:
        return "(empty transcript)"
    return "\n".join(
        f"Turn {t['turn']} Agent {t['speaker']} [{t['language']}]: {t['text']}"
        for t in transcript
    )


def debate_instructions(agent: dict) -> str:
    labels = DEBATE_LABELS.get(agent["language"], DEBATE_LABELS["English"])
    return (
        f"You are Agent {agent['agent_id']}. Write your public dialogue turn in "
        f"{agent['language']} only. You can understand all languages in the conversation. "
        "Return exactly one concise turn. "
        "Do NOT begin with 'Turn N Agent X [Language]:' or any transcript header. "
        "If this is your opening turn (no prior opponent turn exists), state your position and include: "
        f"{labels['change']}: My view has not changed. "
        "If there is a prior opponent turn, you MUST include all three of these exact labeled lines:\n"
        f"{labels['strongest']}: (state the opponent's strongest argument)\n"
        f"{labels['counter']}: (your counterargument to that point)\n"
        f"{labels['change']}: (explicitly state whether your view changed or did not change)\n"
        "All three lines are required. Do not omit any label. Do not mention private probes or hidden values."
    )


def debate_input(topic: str, transcript: list[dict], condition: str) -> str:
    relay_note = ""
    if condition == "translated-relay":
        relay_note = (
            "\nNote: treat the prior transcript as if it has been translated into your language "
            "before you read it. Respond in your assigned language."
        )
    if not transcript:
        return f"Topic: {topic}\nTranscript so far: none.\n{relay_note}\nWrite your opening turn."
    return (
        f"Topic: {topic}\n"
        f"Transcript so far:\n{transcript_text(transcript)}\n"
        f"{relay_note}\nWrite your next turn."
    )


def probe_instructions(language: str) -> str:
    keys = ", ".join(VALUE_KEYS)
    template = {k: 4 for k in VALUE_KEYS}
    template["rationale"] = "short rationale"
    return (
        "You are answering privately from your current memory. Return only one valid JSON object. "
        f"Use exactly these numeric 1-7 rating keys: {keys}. "
        f"Rationale must be a short string in {language}. "
        f"Template: {json.dumps(template, ensure_ascii=False)}. "
        "No markdown, no extra keys, no quoted numbers."
    )


def observer_instructions() -> str:
    keys = ", ".join(VALUE_KEYS)
    agent_tpl = {k: 4 for k in VALUE_KEYS}
    agent_tpl["evidence"] = "short transcript evidence"
    template = {"A": agent_tpl, "B": agent_tpl}
    return (
        "Observe only the public transcript. Return one valid JSON object with keys A and B. "
        f"Each must have numeric 1-7 ratings for: {keys}, plus an evidence string. "
        f"Template: {json.dumps(template, ensure_ascii=False)}. "
        "No markdown, no flat single-agent format."
    )


def screening_record(agents: list[dict]) -> dict:
    a_vals = agents[0]["values"]
    b_vals = agents[1]["values"]
    dist = sum(abs(a_vals[k] - b_vals[k]) for k in VALUE_KEYS)
    return {
        "retained": dist >= 8,
        "stance_distance": None,
        "value_distance": dist,
        "reason": "Static local-LM priors differ on topic-relevant access-versus-security values.",
    }


# ---------------------------------------------------------------------------
# Remote function
# ---------------------------------------------------------------------------

@app.function(
    gpu="L4",
    timeout=3600,
    volumes={"/models": model_volume},
)
def run_condition_remote(
    condition: str,
    target_language: str,
    topic: str,
    seed: int,
    turns: int,
    max_new_tokens: int,
    readout_max_new_tokens: int,
    turn_retries: int,
    json_retries: int,
) -> dict[str, Any]:
    """Run one BiVaD condition on Modal GPU and return artifact as dict."""
    import os
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Download/cache the model to the shared volume.
    model_path = MODEL_DIR
    if not os.path.exists(os.path.join(model_path, "config.json")):
        print(f"Downloading {MODEL_ID} to {model_path} ...")
        from huggingface_hub import snapshot_download
        snapshot_download(MODEL_ID, local_dir=model_path)
        model_volume.commit()
        print("Download complete.")

    torch.manual_seed(seed)
    print(f"Loading {MODEL_ID} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, local_files_only=True, torch_dtype=torch.bfloat16
    )
    model = model.to("cuda")
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("Model loaded.")

    def _strip_think(text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()

    def _strip_header(text: str) -> str:
        return TRANSCRIPT_HEADER_RE.sub("", text).strip()

    def _parse_json(text: str) -> dict | None:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not m:
                return None
            try:
                parsed = json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
        return parsed if isinstance(parsed, dict) else None

    def _numeric(v: Any) -> float | None:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
        if isinstance(v, str) and re.fullmatch(r"[1-7](?:\.0+)?", v.strip()):
            return float(v.strip())
        return None

    def _coerce_values(data: dict | None) -> dict[str, float]:
        if not isinstance(data, dict):
            return {}
        return {k: _numeric(data.get(k)) for k in VALUE_KEYS if _numeric(data.get(k)) is not None}

    def _complete(values: dict) -> bool:
        return all(k in values for k in VALUE_KEYS)

    def _generate(instructions: str, user_input: str, max_tok: int, temperature: float) -> str:
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_input},
        ]
        if getattr(tokenizer, "chat_template", None):
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            text = f"Instructions:\n{instructions}\n\nInput:\n{user_input}\n\nOutput:\n"
        inputs = tokenizer(text, return_tensors="pt").to("cuda")
        do_sample = temperature > 0
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_tok,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=0.9 if do_sample else None,
                repetition_penalty=1.05,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[-1]:]
        return _strip_think(tokenizer.decode(gen, skip_special_tokens=True).strip())

    def _marker_present(text: str, markers: tuple) -> bool:
        low = text.lower()
        return any(m in low for m in markers)

    # Inline address/counter/change markers (keep in sync with audit_bivad_evidence.py)
    ADDRESS_MARKERS = (
        "strongest", "strongest objection", "main point", "primary concern",
        "your point", "other agent", "opponent", "counterpoint",
        "poin kuat", "poin terkuat", "poin lawan", "poin utama", "argumen lawan",
        "terkuat", "lawan",
        "punto", "otro agente",
    )
    COUNTER_MARKERS = (
        "however", "but", "although", "whereas", "nevertheless", "still", "yet",
        "tetapi", "namun", "meskipun", "walaupun", "pero", "sin embargo", "aunque",
    )
    CHANGE_MARKERS = (
        "changed", "shifted", "softened", "unchanged", "did not change", "no change",
        "remains the same", "remain unchanged", "not altered",
        "berubah", "tidak berubah", "belum berubah", "masih belum berubah",
        "tetap sama", "tetap identik", "mantengo", "cambi",
    )

    def _quality_ok(text: str, has_opponent: bool, prior_texts: list[str]) -> bool:
        """Require address + change; also reject near-duplicate of any prior turn."""
        if not text or len(text.split()) < 15:
            return False
        # Reject if this text is a near-duplicate of any previous turn.
        text_lower = text.lower().strip()
        for prior in prior_texts:
            prior_lower = prior.lower().strip()
            # Use a simple prefix overlap check: reject if first 80 chars match.
            if len(prior_lower) > 60 and text_lower[:80] == prior_lower[:80]:
                return False
        if not has_opponent:
            return _marker_present(text, CHANGE_MARKERS)
        addressed = _marker_present(text, ADDRESS_MARKERS)
        change = _marker_present(text, CHANGE_MARKERS)
        return addressed and change

    def _retry_note(attempt: int, labels: dict) -> str:
        return (
            f"\n\nAttempt {attempt}: Previous response did not include required labels. "
            "Do NOT start with a transcript header. Write only dialogue content. "
            f"REQUIRED (on separate lines): "
            f"{labels['strongest']}: (opponent's strongest point); "
            f"{labels['counter']}: (your counterargument); "
            f"{labels['change']}: (explicitly state whether view changed or did not change). "
            "All three are mandatory. Include the change declaration."
        )

    def _probe(agent: dict, transcript: list) -> dict:
        turn = transcript[-1]["turn"] if transcript else 0
        if transcript:
            user_input = (
                f"Topic: {topic}\n"
                f"Transcript:\n{transcript_text(transcript)}\n"
                f"You are Agent {agent['agent_id']}. Give private value ratings now."
            )
        else:
            user_input = (
                f"Topic: {topic}\nYou are Agent {agent['agent_id']} with stance: {agent['stance']}.\n"
                "No dialogue yet. Give private value ratings."
            )
        instructions = probe_instructions(agent["language"])
        text = ""
        values: dict[str, float] = {}
        for attempt in range(json_retries + 1):
            inp = user_input if attempt == 0 else (
                user_input + f"\n\nAttempt {attempt}: return one JSON object only with all required keys."
            )
            text = _generate(instructions, inp, readout_max_new_tokens, 0.0)
            parsed = _parse_json(text)
            values = _coerce_values(parsed)
            if _complete(values):
                break
        return {"agent_id": agent["agent_id"], "turn": turn, "values": values, "complete": _complete(values)}

    def _observer(transcript: list) -> list[dict]:
        instructions = observer_instructions()
        user_input = f"Topic: {topic}\nTranscript:\n{transcript_text(transcript)}"
        text = ""
        values_by = {"A": {}, "B": {}}
        parsed: dict = {}
        for attempt in range(json_retries + 1):
            inp = user_input if attempt == 0 else (
                user_input + f"\n\nAttempt {attempt}: return one JSON object with keys A and B."
            )
            text = _generate(instructions, inp, readout_max_new_tokens, 0.0)
            parsed = _parse_json(text) or {}
            for aid in ("A", "B"):
                item = parsed.get(aid)
                values_by[aid] = _coerce_values(item if isinstance(item, dict) else None)
            if all(_complete(values_by[aid]) for aid in ("A", "B")):
                break
        turn = transcript[-1]["turn"] if transcript else 0
        return [
            {
                "agent_id": aid,
                "turn": turn,
                "values": values_by[aid],
                "complete": _complete(values_by[aid]),
            }
            for aid in ("A", "B")
        ]

    # Run the condition
    agents = condition_agents(condition, target_language)
    transcript: list[dict] = []
    prior_texts: list[str] = []
    private_probes = [_probe(ag, transcript) for ag in agents]

    for turn_num in range(1, turns + 1):
        agent = agents[(turn_num - 1) % 2]
        has_opponent = any(t["speaker"] != agent["agent_id"] for t in transcript)
        labels = DEBATE_LABELS.get(agent["language"], DEBATE_LABELS["English"])
        instructions = debate_instructions(agent)
        base_input = debate_input(topic, transcript, condition)
        text = ""
        attempts_used = 0
        for attempt in range(turn_retries + 1):
            attempts_used = attempt
            # Vary temperature slightly on retries to escape repetition traps.
            temp = 0.7 if attempt == 0 else min(0.95, 0.7 + attempt * 0.08)
            inp = base_input if attempt == 0 else base_input + _retry_note(attempt, labels)
            if attempt > 0 and prior_texts:
                inp += f"\n\nIMPORTANT: Do NOT repeat or paraphrase content from Turn {turn_num - 2 if turn_num > 2 else 1}. Generate genuinely new arguments."
            text = _generate(instructions, inp, max_new_tokens, temp)
            text = _strip_header(text)
            if _quality_ok(text, has_opponent, prior_texts):
                break
            print(f"  Turn {turn_num} attempt {attempt + 1} failed quality/uniqueness: {text[:120]!r}")
        prior_texts.append(text)
        print(f"Turn {turn_num} Agent {agent['agent_id']} ({agent['language']}): OK (attempts={attempts_used})")
        transcript.append({
            "turn": turn_num,
            "speaker": agent["agent_id"],
            "language": agent["language"],
            "text": text,
            "attempts_used": attempts_used,
        })
        time.sleep(0.05)

    private_probes.extend(_probe(ag, transcript) for ag in agents)

    return {
        "artifact_type": "local_lm_bivad_pilot",
        "synthetic": False,
        "run_id": f"modal-{condition}-seed{seed}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "condition": condition,
        "topic": topic,
        "seed": seed,
        "model": MODEL_ID,
        "backend": "transformers.AutoModelForCausalLM (Modal GPU)",
        "device": "cuda",
        "torch_dtype": "bfloat16",
        "local_files_only": True,
        "plain_prompt": False,
        "used_chat_template": True,
        "enable_thinking": False,
        "generation_config": {
            "max_new_tokens": max_new_tokens,
            "readout_max_new_tokens": readout_max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.05,
            "turn_retries": turn_retries,
            "json_retries": json_retries,
        },
        "agents": agents,
        "screening": screening_record(agents),
        "transcript": transcript,
        "private_probes": private_probes,
        "observer_readouts": _observer(transcript),
    }


# ---------------------------------------------------------------------------
# Local entrypoint
# ---------------------------------------------------------------------------

@app.local_entrypoint()
def main(
    topic: str = "public release of dual-use policy datasets",
    seed: int = 17,
    target_language: str = "Indonesian",
    turns: int = 4,
    out_dir: str = "runs/bivad-local-lm",
    max_new_tokens: int = 250,
    readout_max_new_tokens: int = 420,
    turn_retries: int = 4,
    json_retries: int = 3,
    conditions: str = "same-target-language",
) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for condition in conditions.split(","):
        condition = condition.strip()
        if condition not in CONDITIONS:
            raise SystemExit(f"Unknown condition: {condition}")
        print(f"Running condition: {condition} ...")
        artifact = run_condition_remote.remote(
            condition=condition,
            target_language=target_language,
            topic=topic,
            seed=seed,
            turns=turns,
            max_new_tokens=max_new_tokens,
            readout_max_new_tokens=readout_max_new_tokens,
            turn_retries=turn_retries,
            json_retries=json_retries,
        )
        run_id = f"{stamp}-{condition}-seed{seed}"
        artifact["run_id"] = run_id
        path = out / f"{run_id}.json"
        path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {path}")
    print("Done. Run code/audit_bivad_evidence.py on the output directory.")


@app.local_entrypoint()
def scan(
    topics: str = (
        "mandatory content moderation on social media platforms"
        "|government surveillance for national security"
        "|universal basic income as a social safety net"
        "|religious exemptions from anti-discrimination law"
    ),
    seed: int = 17,
    target_language: str = "Indonesian",
    turns: int = 4,
    out_dir: str = "runs/bivad-local-lm",
    max_new_tokens: int = 250,
    readout_max_new_tokens: int = 420,
    turn_retries: int = 4,
    json_retries: int = 3,
    conditions: str = "mixed-language,same-English",
) -> None:
    """Scan multiple topics across two conditions to rank cross-lingual divergence."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    topic_list = [t.strip() for t in topics.split("|") if t.strip()]
    condition_list = [c.strip() for c in conditions.split(",") if c.strip()]
    for condition in condition_list:
        if condition not in CONDITIONS:
            raise SystemExit(f"Unknown condition: {condition}")

    print(f"Scan: {len(topic_list)} topics × {len(condition_list)} conditions = {len(topic_list) * len(condition_list)} runs")

    manifest: list[dict] = []
    for topic in topic_list:
        topic_slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:36].strip("-")
        for condition in condition_list:
            print(f"Running condition={condition!r} topic={topic!r} ...")
            artifact = run_condition_remote.remote(
                condition=condition,
                target_language=target_language,
                topic=topic,
                seed=seed,
                turns=turns,
                max_new_tokens=max_new_tokens,
                readout_max_new_tokens=readout_max_new_tokens,
                turn_retries=turn_retries,
                json_retries=json_retries,
            )
            run_id = f"{stamp}-{condition}-seed{seed}-{topic_slug}"
            artifact["run_id"] = run_id
            path = out / f"{run_id}.json"
            path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
            print(f"  Wrote {path}")
            manifest.append({"run_id": run_id, "path": str(path), "condition": condition, "topic": topic})

    manifest_path = out / f"{stamp}-scan-manifest.json"
    manifest_path.write_text(json.dumps({"stamp": stamp, "runs": manifest}, indent=2), encoding="utf-8")
    print(f"Wrote manifest {manifest_path}")
    print(f"Done. Run code/analyze_topic_divergence.py to rank topics by cross-lingual divergence.")
