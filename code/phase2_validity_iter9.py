"""
Phase 2 — Validity Loop (iter 9).

Fixes applied vs iter 8 (coding agent assessment — all 3 seeds FAIL):

  Fix 12 (iter9): Restore the EXACT iter4 opener to config/prompts.json;
          keep Fix 8/9/11b improvements only in other_turn.

          Root cause of iter7 and iter8 failures (DISAGREE/DISAGREEMENT as
          literal first English word):

          iter4 opener had:
              "Every word must use only the Latin alphabet — for Indonesian,
               this means writing Indonesian words only, never Chinese or
               other script."

          Fixes 7–11 all replaced this with a generic Latin-only prohibition
          (Fix 8) and then added an AKUI prohibition (Fixes 10–11). Neither
          approach reproduced iter4's behavior, because:

          1. Removing "for Indonesian" unanchored the model from Indonesian-
             writing mode. The model interpreted "clearly stating whether you
             AGREE or DISAGREE" as a requirement to output those English words.

          2. Adding an AKUI prohibition ("state your position directly" or
             "begin your response in {lang}") further entrenched the English-
             word-first behavior across all 3 seeds.

          The opener is ONLY shown to Agent A (Indonesian writer). It is never
          used by Agent B (US writer). So "for Indonesian, this means writing
          Indonesian words only" cannot cause Agent B to ignore the Chinese
          character prohibition in their own turns.

          Fix 8 was correctly motivated: iter5 seed=89 Agent B turn 4 produced
          "集体" — the "for Indonesian" qualifier in other_turn was being
          ignored by the English-writing Agent B. Removing it from other_turn
          fixed that. But Fix 8 was incorrectly also applied to the opener,
          which only Agent A reads.

          Fix 12: Restore iter4 opener exactly (with "for Indonesian" qualifier,
          without AKUI prohibition). Keep current other_turn (Fix 8 — generic
          Latin-only prohibition, Fix 9 + Fix 11b — explicit prohibited openers).

Prior fixes confirmed working and kept (in other_turn):
  - Fix 2 (iter2): block B from endorsing A's framing (extended by Fix 9, Fix 11b)
  - Fix 3 (iter2): item = society_over_individual
  - Fix 4 (iter3): language prohibition names Chinese/Japanese/Korean scripts
  - Fix 5 (iter4): removed 'tidak setuju' example from opener
  - Fix 8 (iter6): no 'for Indonesian' qualifier in other_turn language prohibition
  - Fix 9 (iter6): other_turn explicitly names prohibited openers (extended by Fix 11b)

Same cell as Phase 1 pilot:
  Agent A: Indonesia persona / Indonesian language
  Agent B: USA persona / English language

Seeds: 17, 71, 89

Expected behavior (based on iter4):
  - Seeds 17 and 89 should open AGREE (P=0.663/0.652 in iter4)
  - Seed 71 behavior unknown; may produce AGREE, DISAGREE, or AKUI hedge

Outputs:
  artifacts/transcripts/phase2_iter9_<seed>.json  (one per seed)

Run with: modal run code/phase2_validity_iter9.py
"""

import json
import datetime
import modal

app = modal.App("phase2-validity-iter9")

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

LOCKED_ITEMS = {
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

    def make_system_prompt(country_key: str, lang_key: str) -> str:
        country = COUNTRY_NAMES.get(country_key, country_key)
        lang = LANGUAGE_NAMES.get(lang_key, lang_key)
        persona = persona_template.format(country=country)
        lang_instr = lang_template.format(lang=lang)
        return f"{persona} {lang_instr}"

    def wrap_opponent_turn(turn: dict, my_lang_key: str, my_country_key: str) -> str:
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
        system_prompt = make_system_prompt(country_key, lang_key)
        task_intro = task_intro_template.format(item=item_statement)

        messages = [{"role": "system", "content": system_prompt}]
        a_turns = [t for t in debate_turns if t["agent"] == "A"]

        if agent_id == "A":
            lang = LANGUAGE_NAMES.get(lang_key, lang_key)
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
        else:
            if not a_turns:
                lang = LANGUAGE_NAMES.get(lang_key, lang_key)
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

        probe_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"],
            debate_turns,
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
    with open("config/prompts.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    d = cfg["debate"]
    persona_template    = d["persona"]
    lang_template       = d["language"]
    task_intro_template = d["task_intro"]
    opener_template     = d["opener"]
    other_turn_template = d["other_turn"]
    probe_template      = cfg["probe"]["likert"]

    item_key = "society_over_individual"
    item_statement = LOCKED_ITEMS[item_key]

    # Seeds 17 and 89 opened AGREE (P=0.663/0.652) in iter4 with the exact
    # opener now restored. Seed 71 behavior unknown.
    seeds = [17, 71, 89]

    common_config = {
        "phase": 2,
        "iter": 9,
        "item_key": item_key,
        "item_statement": item_statement,
        "agent_A": {"country": "indonesia", "lang": "id"},
        "agent_B": {"country": "usa", "lang": "en"},
        "n_turns": 6,
        "model": MODEL_NAME,
        "fixes_applied": [
            "Fix 2 (iter2): block B from endorsing A's framing (extended by Fix 9 and Fix 11b)",
            "Fix 3 (iter2): item = society_over_individual",
            "Fix 4 (iter3): language prohibition names Chinese/Japanese/Korean scripts",
            "Fix 5 (iter4): removed 'tidak setuju' example from opener",
            "Fix 8 (iter6): no 'for Indonesian' qualifier in other_turn language prohibition",
            "Fix 9 (iter6): other_turn explicitly names prohibited openers (extended by Fix 11b)",
            "Fix 11b (iter8): Added 'I largely agree' to Fix 9's prohibited opener list.",
            "Fix 12 (iter9): Restored EXACT iter4 opener (with 'for Indonesian, this means "
            "writing Indonesian words only' qualifier in language prohibition; no AKUI "
            "prohibition). Fix 8's generic Latin-only prohibition is kept ONLY in other_turn "
            "where Agent B (English writer) reads it. The opener is only shown to Agent A "
            "(Indonesian writer), so the 'for Indonesian' qualifier cannot cause Agent B to "
            "produce Chinese characters. Root cause of iter7/iter8 FAIL: Fix 8 was applied to "
            "both opener AND other_turn, removing the grounding that caused iter4 seeds 17 and "
            "89 to open naturally with 'Saya setuju' (P=0.663/0.652). Adding AKUI prohibitions "
            "(Fixes 10, 11) made this worse by triggering literal English DISAGREE output.",
        ],
        "prompts": {
            "persona": persona_template,
            "language": lang_template,
            "task_intro": task_intro_template,
            "opener": opener_template,
            "other_turn": other_turn_template,
            "probe": probe_template,
        },
    }

    sep = "=" * 80

    for seed in seeds:
        print(f"\n{sep}")
        print(f"RUNNING DEBATE — seed={seed}  item={item_key}  iter=9")
        print(sep)

        result = run_debate.remote(
            item_key=item_key,
            item_statement=item_statement,
            agent_a_country="indonesia",
            agent_a_lang="id",
            agent_b_country="usa",
            agent_b_lang="en",
            n_turns=6,
            seed=seed,
            persona_template=persona_template,
            lang_template=lang_template,
            task_intro_template=task_intro_template,
            opener_template=opener_template,
            other_turn_template=other_turn_template,
            probe_template=probe_template,
        )

        config_record = {
            **common_config,
            "seed": seed,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        output = {"config": config_record, "debate": result}

        out_path = f"artifacts/transcripts/phase2_iter9_{seed}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nSaved → {out_path}")

        print(f"\n{sep}")
        print(f"TRANSCRIPT: seed={seed}  item={item_key}  iter=9")
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

        print(f"\nP(agree) TRAJECTORY (seed={seed}):")
        print(f"{'Turn':>5}  {'Agent':>7}  {'Country/Lang':>15}  {'P(agree)':>10}")
        print("-" * 45)
        for turn in result["debate_turns"]:
            label = f"{turn['country']}/{turn['lang']}"
            print(
                f"{turn['turn']:>5}  {turn['agent']:>7}  {label:>15}  "
                f"{turn['probe']['p_agree']:>10.3f}"
            )

    print(f"\n{sep}")
    print("ALL 3 DEBATES COMPLETE — phase2 iter9.")
    print(sep)
