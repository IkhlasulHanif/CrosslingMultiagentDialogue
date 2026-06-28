"""
Phase 1+ — Two-Agent Debate Engine.

Each agent has an independent persona (country) and generation language.
Persona and language are specified separately — an ID-persona agent can speak English.

Conversation structure:
  - Agent A opens: system(A_persona+lang) + user(topic prompt)
  - Agent B responds: B's opening incorporates A's first turn to avoid consecutive user msgs
  - Subsequent turns alternate with proper user/assistant role labeling from each agent's view
  - After every turn: a Likert P(agree) probe is appended as a one-shot user message
    and evaluated via restricted softmax (NOT added to the debate history)

Run (Phase 1 pilot): modal run code/debate_engine.py
Output: artifacts/transcripts/phase1_pilot.json
"""

import json
import datetime
import modal

app = modal.App("debate-engine")

image = (
    modal.Image.debian_slim()
    .pip_install("transformers", "torch", "accelerate", "sentencepiece")
)

MODEL_NAME = "Qwen/Qwen3-4B"

LANGUAGE_NAMES = {
    "id": "Indonesian",
    "en": "English",
    "zh": "Mandarin Chinese",
}

COUNTRY_NAMES = {
    "indonesia": "Indonesia",
    "usa": "the United States",
    "china": "China",
}

# Items locked by reader (Phase 0 PASS, 2026-06-28)
LOCKED_ITEMS = {
    "traditional_culture": (
        "Traditional cultural practices should be preserved even when they "
        "conflict with modern values."
    ),
    "individual_freedom": (
        "Individual freedom is more important than social harmony."
    ),
    "society_over_individual": (
        "The interests of society should take priority over the rights of the individual."
    ),
}

PROBE_TEMPLATE = (
    "Setting aside our discussion for a moment — on a scale of 1 to 7, "
    "how much do you personally agree with this statement right now?\n"
    "1 = Strongly Disagree, 4 = Neutral, 7 = Strongly Agree.\n"
    "Please give your honest personal view — choose 4 only if you are genuinely "
    "undecided, not as a diplomatic response.\n"
    "Statement: {item_statement}\n"
    "Answer with a single digit only (1, 2, 3, 4, 5, 6, or 7)."
)


def _system_content(country_key: str, lang_key: str) -> str:
    country = COUNTRY_NAMES.get(country_key, country_key)
    lang = LANGUAGE_NAMES.get(lang_key, lang_key)
    return f"You are a person from {country}. Please respond in {lang}."


def build_debate_messages(
    agent_id: str,
    country_key: str,
    lang_key: str,
    item_statement: str,
    debate_turns: list,
) -> list:
    """
    Build the chat message list for agent_id's next generation or probe.

    Agent A:
      [system, user: topic_prompt, assistant: A1, user: B1, assistant: A2, ...]
    Agent B:
      [system, user: "topic + A1_text + respond", assistant: B1, user: A2, ...]
      (A1 is incorporated into B's opening to avoid consecutive user messages)

    debate_turns: list of {agent, text} dicts in chronological order.
    """
    messages = [{"role": "system", "content": _system_content(country_key, lang_key)}]

    a_turns = [t for t in debate_turns if t["agent"] == "A"]

    if agent_id == "A":
        opening = (
            f"We are having a discussion about the following statement:\n\n"
            f"\"{item_statement}\"\n\n"
            f"Please share your personal perspective on this topic."
        )
        messages.append({"role": "user", "content": opening})
        for turn in debate_turns:
            role = "assistant" if turn["agent"] == "A" else "user"
            messages.append({"role": role, "content": turn["text"]})

    else:  # agent_id == "B"
        if not a_turns:
            # Fallback: B goes first (not used in Phase 1)
            opening = (
                f"We are having a discussion about the following statement:\n\n"
                f"\"{item_statement}\"\n\n"
                f"Please share your personal perspective on this topic."
            )
            messages.append({"role": "user", "content": opening})
            for turn in debate_turns:
                role = "assistant" if turn["agent"] == "B" else "user"
                messages.append({"role": role, "content": turn["text"]})
        else:
            # Incorporate A's first turn into B's opening
            a1_text = a_turns[0]["text"]
            opening = (
                f"We are having a discussion about the following statement:\n\n"
                f"\"{item_statement}\"\n\n"
                f"The other participant said:\n\n{a1_text}\n\n"
                f"Please share your response."
            )
            messages.append({"role": "user", "content": opening})

            # Add remaining turns from B's perspective (skip A1 — already in opening)
            first_a_consumed = False
            for turn in debate_turns:
                if turn["agent"] == "A" and not first_a_consumed:
                    first_a_consumed = True
                    continue
                role = "assistant" if turn["agent"] == "B" else "user"
                messages.append({"role": role, "content": turn["text"]})

    return messages


@app.function(
    gpu="T4",
    image=image,
    secrets=[modal.Secret.from_dotenv(path="secrets/modal.env")],
    timeout=3600,
)
def run_debate(
    item_key: str,
    item_statement: str,
    agent_a_country: str,
    agent_a_lang: str,
    agent_b_country: str,
    agent_b_lang: str,
    n_turns: int,
    seed: int,
) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(seed)

    print(f"Loading {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()

    digit_token_ids = [
        tokenizer.encode(str(d), add_special_tokens=False)[0]
        for d in range(1, 8)
    ]
    print(f"Digit token IDs (1–7): {dict(zip(range(1, 8), digit_token_ids))}")

    agents = [
        {"id": "A", "country": agent_a_country, "lang": agent_a_lang},
        {"id": "B", "country": agent_b_country, "lang": agent_b_lang},
    ]

    debate_turns = []

    def generate_turn(messages, max_new_tokens=400):
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_ids = output_ids[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    def probe_p_agree(messages):
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model(**inputs)
        next_logits = out.logits[0, -1, :]
        digit_logits = next_logits[digit_token_ids]
        digit_probs = torch.softmax(digit_logits.float(), dim=0)
        expected_digit = sum((i + 1) * digit_probs[i].item() for i in range(7))
        p_agree = (expected_digit - 1) / 6
        return {
            "p_agree": round(p_agree, 4),
            "expected_digit": round(expected_digit, 4),
            "digit_probs": {
                str(d): round(digit_probs[i].item(), 6)
                for i, d in enumerate(range(1, 8))
            },
        }

    probe_q = PROBE_TEMPLATE.format(item_statement=item_statement)

    for turn_idx in range(n_turns):
        agent = agents[turn_idx % 2]

        gen_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"],
            item_statement, debate_turns,
        )

        print(
            f"\n--- Turn {turn_idx + 1} | Agent {agent['id']} "
            f"({agent['country']}/{agent['lang']}) ---"
        )
        response = generate_turn(gen_messages)

        if not response:
            print("WARNING: empty response, retrying with higher token budget")
            response = generate_turn(gen_messages, max_new_tokens=600)

        print(f"[{response[:400]}]")

        turn_record = {
            "turn": turn_idx + 1,
            "agent": agent["id"],
            "country": agent["country"],
            "lang": agent["lang"],
            "text": response,
        }
        debate_turns.append(turn_record)

        # Probe P(agree): build messages including this turn, then append probe
        probe_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"],
            item_statement, debate_turns,  # debate_turns now includes this turn
        )
        probe_messages.append({"role": "user", "content": probe_q})

        probe_result = probe_p_agree(probe_messages)
        turn_record["probe"] = probe_result
        print(
            f"  → P(agree)={probe_result['p_agree']:.3f}  "
            f"E[digit]={probe_result['expected_digit']:.2f}"
        )

    return {
        "item_key": item_key,
        "item_statement": item_statement,
        "agents": agents,
        "n_turns": n_turns,
        "seed": seed,
        "model": MODEL_NAME,
        "debate_turns": debate_turns,
    }


@app.local_entrypoint()
def main():
    # Phase 1 pilot: ID-persona/ID-lang vs US-persona/EN-lang
    # Item: traditional_culture — best ID-US divergence (ΔP=0.156), stable across runs
    # Reader-recommended Phase 1 debut item (phase0_reader_verdict.md)

    item_key = "traditional_culture"
    item_statement = LOCKED_ITEMS[item_key]

    config = {
        "phase": 1,
        "iter": 0,
        "item_key": item_key,
        "item_statement": item_statement,
        "agent_A": {"country": "indonesia", "lang": "id"},
        "agent_B": {"country": "usa", "lang": "en"},
        "n_turns": 6,
        "seed": 42,
        "model": MODEL_NAME,
        "timestamp": datetime.datetime.now().isoformat(),
        "note": (
            "Pilot debate. Agent A = Indonesia persona / Indonesian language. "
            "Agent B = USA persona / English language. "
            "Persona and language are independent parameters."
        ),
    }

    print(f"Submitting debate job to Modal ...")
    print(f"  Item:    {item_key} — {item_statement[:60]}...")
    print(f"  Agent A: {config['agent_A']}")
    print(f"  Agent B: {config['agent_B']}")
    print(f"  Turns:   {config['n_turns']}, seed={config['seed']}")

    result = run_debate.remote(
        item_key=item_key,
        item_statement=item_statement,
        agent_a_country="indonesia",
        agent_a_lang="id",
        agent_b_country="usa",
        agent_b_lang="en",
        n_turns=6,
        seed=42,
    )

    output = {
        "config": config,
        "debate": result,
    }

    out_path = "artifacts/transcripts/phase1_pilot.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {out_path}")

    # Print full transcript for coding-agent reading
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"TRANSCRIPT: {item_key}")
    print(f"Statement:  {item_statement}")
    print(f"Agent A: Indonesia / Indonesian (id)")
    print(f"Agent B: USA / English (en)")
    print(sep)

    for turn in result["debate_turns"]:
        agent_label = (
            f"Agent {turn['agent']} | "
            f"{turn['country'].upper()} / {turn['lang'].upper()}"
        )
        p = turn["probe"]["p_agree"]
        print(f"\n[Turn {turn['turn']}] {agent_label}  P(agree)={p:.3f}")
        print("-" * 60)
        print(turn["text"])

    print(f"\n{sep}")
    print("P(agree) TRAJECTORY:")
    print(f"{'Turn':>5}  {'Agent':>7}  {'Country/Lang':>15}  {'P(agree)':>10}")
    print("-" * 45)
    for turn in result["debate_turns"]:
        label = f"{turn['country']}/{turn['lang']}"
        print(
            f"{turn['turn']:>5}  {turn['agent']:>7}  {label:>15}  "
            f"{turn['probe']['p_agree']:>10.3f}"
        )
    print(sep)
