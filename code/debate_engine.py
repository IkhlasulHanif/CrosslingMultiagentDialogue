"""
Phase 1+ — Two-Agent Debate Engine.

Each agent has an independent persona (country) and generation language.
Persona and language are specified separately — an ID-persona agent can speak English.

Prompts are loaded from config/prompts.json by main() and passed to Modal as
plain strings — no file I/O inside the Modal function.

Conversation structure:
  - Agent A opens: [system, user: task_intro+opener]
  - Agent B's opening: [system, user: task_intro + wrapped(A1)]
    A1 is incorporated into B's first user message to avoid consecutive user msgs.
  - Subsequent turns: opponent turns wrapped with attribution + "respond from YOUR view"
  - After every turn: Likert P(agree) probe appended as user message, NOT added to history

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
    # Prompt templates — loaded from config/prompts.json by main(), passed as strings
    persona_template: str,
    lang_template: str,
    task_intro_template: str,
    opener_template: str,
    other_turn_template: str,
    probe_template: str,
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

    # ── Prompt builders (closures over template strings from outer scope) ──────

    def make_system_prompt(country_key: str, lang_key: str) -> str:
        country = COUNTRY_NAMES.get(country_key, country_key)
        lang = LANGUAGE_NAMES.get(lang_key, lang_key)
        persona = persona_template.format(country=country)
        lang_instr = lang_template.format(lang=lang)
        return f"{persona} {lang_instr}"

    def wrap_opponent_turn(turn: dict, my_lang_key: str, my_country_key: str) -> str:
        """Wrap an opponent's turn with attribution + respond-from-YOUR-view instruction."""
        my_lang = LANGUAGE_NAMES.get(my_lang_key, my_lang_key)
        my_country = COUNTRY_NAMES.get(my_country_key, my_country_key)
        other_country = COUNTRY_NAMES.get(turn["country"], turn["country"])
        other_lang = LANGUAGE_NAMES.get(turn["lang"], turn["lang"])
        return other_turn_template.format(
            other_country=other_country,
            other_lang=other_lang,
            text=turn["text"],
            my_country=my_country,
            my_lang=my_lang,
        )

    def build_debate_messages(
        agent_id: str,
        country_key: str,
        lang_key: str,
        debate_turns: list,
    ) -> list:
        """
        Build the chat message list for agent_id's next generation.

        Agent A:
          [system, user: task_intro+opener, assistant: A1, user: wrapped(B1), assistant: A2, ...]

        Agent B:
          [system, user: task_intro+wrapped(A1), assistant: B1, user: wrapped(A2), ...]
          A1 is embedded in B's opening user message — no consecutive user messages.

        All opponent turns appear as 'user' role with attribution header and
        "respond from YOUR own perspective" instruction to prevent echo loops.
        """
        lang = LANGUAGE_NAMES.get(lang_key, lang_key)
        system_prompt = make_system_prompt(country_key, lang_key)
        task_intro = task_intro_template.format(item=item_statement)

        messages = [{"role": "system", "content": system_prompt}]
        a_turns = [t for t in debate_turns if t["agent"] == "A"]

        if agent_id == "A":
            opener = opener_template.format(lang=lang)
            messages.append({"role": "user", "content": f"{task_intro}\n\n{opener}"})
            for turn in debate_turns:
                if turn["agent"] == "A":
                    messages.append({"role": "assistant", "content": turn["text"]})
                else:
                    messages.append({
                        "role": "user",
                        "content": wrap_opponent_turn(turn, lang_key, country_key),
                    })

        else:  # agent_id == "B"
            if not a_turns:
                opener = opener_template.format(lang=lang)
                messages.append({"role": "user", "content": f"{task_intro}\n\n{opener}"})
                for turn in debate_turns:
                    if turn["agent"] == "B":
                        messages.append({"role": "assistant", "content": turn["text"]})
                    else:
                        messages.append({
                            "role": "user",
                            "content": wrap_opponent_turn(turn, lang_key, country_key),
                        })
            else:
                # Embed A's first turn in B's opening to avoid consecutive user messages
                a1_wrapped = wrap_opponent_turn(a_turns[0], lang_key, country_key)
                messages.append({
                    "role": "user",
                    "content": f"{task_intro}\n\n{a1_wrapped}",
                })
                first_a_consumed = False
                for turn in debate_turns:
                    if turn["agent"] == "A" and not first_a_consumed:
                        first_a_consumed = True
                        continue
                    if turn["agent"] == "B":
                        messages.append({"role": "assistant", "content": turn["text"]})
                    else:
                        messages.append({
                            "role": "user",
                            "content": wrap_opponent_turn(turn, lang_key, country_key),
                        })

        return messages

    # ── Inference helpers ──────────────────────────────────────────────────────

    def generate_turn(messages, max_new_tokens=600):
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
                temperature=0.8,
                do_sample=True,
                repetition_penalty=1.15,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_ids = output_ids[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    def probe_p_agree(messages_for_probe):
        text = tokenizer.apply_chat_template(
            messages_for_probe,
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

    # ── Debate loop ────────────────────────────────────────────────────────────

    agents = [
        {"id": "A", "country": agent_a_country, "lang": agent_a_lang},
        {"id": "B", "country": agent_b_country, "lang": agent_b_lang},
    ]
    debate_turns = []
    probe_q = probe_template.format(item=item_statement)

    for turn_idx in range(n_turns):
        agent = agents[turn_idx % 2]

        gen_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"], debate_turns,
        )

        # Print message structure for first 4 turns to verify role labels
        if turn_idx < 4:
            print(f"\n=== MSG STRUCTURE: Turn {turn_idx + 1} | Agent {agent['id']} ===")
            for msg in gen_messages:
                role = msg["role"]
                preview = msg["content"][:150].replace("\n", "↵")
                print(f"  [{role:9}] {preview}…")
            print("===")

        print(
            f"\n--- Turn {turn_idx + 1} | Agent {agent['id']} "
            f"({agent['country']}/{agent['lang']}) ---"
        )
        response = generate_turn(gen_messages)

        if not response:
            print("WARNING: empty response, retrying")
            response = generate_turn(gen_messages, max_new_tokens=600)

        print(f"TEXT: {response[:600]}")

        turn_record = {
            "turn": turn_idx + 1,
            "agent": agent["id"],
            "country": agent["country"],
            "lang": agent["lang"],
            "text": response,
        }
        debate_turns.append(turn_record)

        # Probe P(agree): build messages up through this turn, then append probe
        probe_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"],
            debate_turns,  # now includes this turn as the final assistant msg
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
    # Load prompts from config — no hardcoded prompt text below this line
    with open("config/prompts.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    d = cfg["debate"]
    persona_template     = d["persona"]
    lang_template        = d["language"]
    task_intro_template  = d["task_intro"]
    opener_template      = d["opener"]
    other_turn_template  = d["other_turn"]
    probe_template       = cfg["probe"]["likert"]

    # Phase 1 pilot: society_over_individual, ID-persona/ID-lang vs US-persona/EN-lang
    # society_over_individual: P(ID)=0.512 (neutral), P(US)=0.372 (leans disagree)
    # Agents start from opposite sides of 0.5 — genuine debate tension possible.
    item_key = "society_over_individual"
    item_statement = LOCKED_ITEMS[item_key]

    config_record = {
        "phase": 1,
        "iter": 0,
        "item_key": item_key,
        "item_statement": item_statement,
        "agent_A": {"country": "indonesia", "lang": "id"},
        "agent_B": {"country": "usa", "lang": "en"},
        "n_turns": 6,
        "seed": 45,
        "model": MODEL_NAME,
        "timestamp": datetime.datetime.now().isoformat(),
        "prompts": {
            "persona": persona_template,
            "language": lang_template,
            "task_intro": task_intro_template,
            "opener": opener_template,
            "other_turn": other_turn_template,
            "probe": probe_template,
        },
        "fixes_from_reader_fail": [
            "Prompts loaded from config/prompts.json — no hardcoded prompt text",
            "Anti-sycophancy in persona: 'do not agree just to be polite or diplomatic'",
            "Anti-sycophancy in other_turn: 'if you disagree, express that disagreement directly'",
            "History construction: all opponent turns wrapped with attribution + respond-from-YOUR-view",
            "B opening: task_intro + wrapped(A1) in single user message — no consecutive user turns",
            "Format constraint applied: 3-5 sentences in opener and other_turn templates",
            "Repetition penalty 1.15 added to generation to reduce cascading repetition loops",
            "Max new tokens reduced to 600 (format constraint makes 800 unnecessary)",
            "Temperature raised to 0.8 for more natural variation across turns",
            "Debug: message role structure printed for turns 1-4 to verify correctness",
        ],
    }

    print(f"Submitting debate to Modal ...")
    print(f"  Item:    {item_key}")
    print(f"  Agent A: indonesia / id")
    print(f"  Agent B: usa / en")
    print(f"  Turns: 6, seed=45")

    result = run_debate.remote(
        item_key=item_key,
        item_statement=item_statement,
        agent_a_country="indonesia",
        agent_a_lang="id",
        agent_b_country="usa",
        agent_b_lang="en",
        n_turns=6,
        seed=45,
        persona_template=persona_template,
        lang_template=lang_template,
        task_intro_template=task_intro_template,
        opener_template=opener_template,
        other_turn_template=other_turn_template,
        probe_template=probe_template,
    )

    output = {
        "config": config_record,
        "debate": result,
    }

    out_path = "artifacts/transcripts/phase1_pilot.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved → {out_path}")

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
