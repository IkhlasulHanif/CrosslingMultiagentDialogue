"""
Phase 3 - Discovery batch (iter 7).

Runs 4 cells x 2 seeds = 8 debates as one Modal batch. The local entrypoint
writes one transcript per result plus a one-line manifest.

Run with:
  modal run code/phase3_discovery_iter7.py
"""

import datetime
import json
from pathlib import Path

import modal

app = modal.App("phase3-discovery-iter7")

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
    gpu="A10G",
    image=image,
    secrets=[modal.Secret.from_dotenv(path="secrets/modal.env")],
    timeout=3600,
)
def run_debate_job(job: dict) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    seed = job["seed"]
    item_statement = job["item_statement"]
    prompts = job["prompts"]

    torch.manual_seed(seed)

    print(
        f"Loading {MODEL_NAME} for {job['cell']} seed={seed} "
        f"({job['agent_A']['country']}/{job['agent_A']['lang']} vs "
        f"{job['agent_B']['country']}/{job['agent_B']['lang']})"
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()

    digit_token_ids = [
        tokenizer.encode(str(d), add_special_tokens=False)[0]
        for d in range(1, 8)
    ]

    def make_system_prompt(country_key: str, lang_key: str) -> str:
        country = COUNTRY_NAMES.get(country_key, country_key)
        lang = LANGUAGE_NAMES.get(lang_key, lang_key)
        persona = prompts["persona"].format(country=country)
        lang_instr = prompts["language"].format(lang=lang)
        return f"{persona} {lang_instr}"

    def wrap_opponent_turn(turn: dict, my_lang_key: str, my_country_key: str) -> str:
        my_lang = LANGUAGE_NAMES.get(my_lang_key, my_lang_key)
        my_country = COUNTRY_NAMES.get(my_country_key, my_country_key)
        other_country = COUNTRY_NAMES.get(turn["country"], turn["country"])
        other_lang = LANGUAGE_NAMES.get(turn["lang"], turn["lang"])
        return prompts["other_turn"].format(
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
        lang = LANGUAGE_NAMES.get(lang_key, lang_key)
        system_prompt = make_system_prompt(country_key, lang_key)
        task_intro = prompts["task_intro"].format(item=item_statement)

        messages = [{"role": "system", "content": system_prompt}]
        a_turns = [t for t in debate_turns if t["agent"] == "A"]

        if agent_id == "A":
            opener = prompts["opener"].format(lang=lang)
            messages.append({"role": "user", "content": f"{task_intro}\n\n{opener}"})
            for turn in debate_turns:
                if turn["agent"] == "A":
                    messages.append({"role": "assistant", "content": turn["text"]})
                else:
                    messages.append(
                        {
                            "role": "user",
                            "content": wrap_opponent_turn(turn, lang_key, country_key),
                        }
                    )
        else:
            if not a_turns:
                opener = prompts["opener"].format(lang=lang)
                messages.append({"role": "user", "content": f"{task_intro}\n\n{opener}"})
                for turn in debate_turns:
                    if turn["agent"] == "B":
                        messages.append({"role": "assistant", "content": turn["text"]})
                    else:
                        messages.append(
                            {
                                "role": "user",
                                "content": wrap_opponent_turn(turn, lang_key, country_key),
                            }
                        )
            else:
                a1_wrapped = wrap_opponent_turn(a_turns[0], lang_key, country_key)
                messages.append(
                    {"role": "user", "content": f"{task_intro}\n\n{a1_wrapped}"}
                )
                first_a_consumed = False
                for turn in debate_turns:
                    if turn["agent"] == "A" and not first_a_consumed:
                        first_a_consumed = True
                        continue
                    if turn["agent"] == "B":
                        messages.append({"role": "assistant", "content": turn["text"]})
                    else:
                        messages.append(
                            {
                                "role": "user",
                                "content": wrap_opponent_turn(turn, lang_key, country_key),
                            }
                        )

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
            "digit_token_ids": {
                str(d): int(digit_token_ids[i])
                for i, d in enumerate(range(1, 8))
            },
            "digit_logits": {
                str(d): round(float(digit_logits[i].item()), 6)
                for i, d in enumerate(range(1, 8))
            },
            "digit_probs": {
                str(d): round(float(digit_probs[i].item()), 6)
                for i, d in enumerate(range(1, 8))
            },
        }

    agents = [
        {"id": "A", **job["agent_A"]},
        {"id": "B", **job["agent_B"]},
    ]
    debate_turns = []
    probe_q = prompts["probe"].format(item=item_statement)

    for turn_idx in range(job["n_turns"]):
        agent = agents[turn_idx % 2]
        gen_messages = build_debate_messages(
            agent["id"], agent["country"], agent["lang"], debate_turns
        )

        print(
            f"\n--- {job['cell']} seed={seed} | Turn {turn_idx + 1} | "
            f"Agent {agent['id']} ({agent['country']}/{agent['lang']}) ---"
        )
        response = generate_turn(gen_messages)
        if not response:
            print("WARNING: empty response, retrying")
            response = generate_turn(gen_messages)

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
            agent["id"], agent["country"], agent["lang"], debate_turns
        )
        probe_messages.append({"role": "user", "content": probe_q})

        probe_result = probe_p_agree(probe_messages)
        turn_record["probe"] = probe_result
        print(
            f"  -> P(agree)={probe_result['p_agree']:.3f}  "
            f"E[digit]={probe_result['expected_digit']:.2f}"
        )

    return {
        "cell": job["cell"],
        "cell_description": job["cell_description"],
        "item_key": job["item_key"],
        "item_statement": item_statement,
        "agents": agents,
        "n_turns": job["n_turns"],
        "seed": seed,
        "model": MODEL_NAME,
        "debate_turns": debate_turns,
    }


@app.local_entrypoint()
def main():
    with open("config/prompts.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    d = cfg["debate"]
    prompt_bundle = {
        "persona": d["persona"],
        "language": d["language"],
        "task_intro": d["task_intro"],
        "opener": d["opener"],
        "other_turn": d["other_turn"],
        "probe": cfg["probe"]["likert"],
    }

    item_key = "society_over_individual"
    item_statement = LOCKED_ITEMS[item_key]
    seeds = [131, 149]
    n_turns = 6

    cells = [
        {
            "cell": "idus_enen",
            "cell_description": "EN-EN opposed persona: ID persona in English vs US persona in English",
            "agent_A": {"country": "indonesia", "lang": "en"},
            "agent_B": {"country": "usa", "lang": "en"},
        },
        {
            "cell": "idus_idid",
            "cell_description": "ID-ID opposed persona: ID persona in Indonesian vs US persona in Indonesian",
            "agent_A": {"country": "indonesia", "lang": "id"},
            "agent_B": {"country": "usa", "lang": "id"},
        },
        {
            "cell": "idus_nat",
            "cell_description": "EN-ID opposed persona headline cell: ID persona in Indonesian vs US persona in English",
            "agent_A": {"country": "indonesia", "lang": "id"},
            "agent_B": {"country": "usa", "lang": "en"},
        },
        {
            "cell": "id_aln",
            "cell_description": "EN-ID aligned persona residual-leakage cell: ID persona in Indonesian vs ID persona in English",
            "agent_A": {"country": "indonesia", "lang": "id"},
            "agent_B": {"country": "indonesia", "lang": "en"},
        },
    ]

    jobs = []
    for cell in cells:
        for seed in seeds:
            jobs.append(
                {
                    **cell,
                    "phase": 3,
                    "iter": 7,
                    "seed": seed,
                    "n_turns": n_turns,
                    "item_key": item_key,
                    "item_statement": item_statement,
                    "model": MODEL_NAME,
                    "prompts": prompt_bundle,
                }
            )

    print("Submitting Phase 3 discovery batch iter 7 to Modal:")
    for job in jobs:
        print(
            f"  {job['cell']} seed={job['seed']}: "
            f"A={job['agent_A']['country']}/{job['agent_A']['lang']} "
            f"B={job['agent_B']['country']}/{job['agent_B']['lang']}"
        )

    results = list(run_debate_job.map(jobs))
    results_by_key = {(r["cell"], r["seed"]): r for r in results}

    out_dir = Path("artifacts/transcripts")
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    timestamp = datetime.datetime.now().isoformat()

    for job in jobs:
        result = results_by_key[(job["cell"], job["seed"])]
        out_path = out_dir / f"phase3_iter7_{job['cell']}_{job['seed']}.json"
        config_record = {
            "phase": 3,
            "iter": 7,
            "cell": job["cell"],
            "cell_description": job["cell_description"],
            "item_key": item_key,
            "item_statement": item_statement,
            "agent_A": job["agent_A"],
            "agent_B": job["agent_B"],
            "n_turns": n_turns,
            "seed": job["seed"],
            "model": MODEL_NAME,
            "timestamp": timestamp,
            "prompts": prompt_bundle,
        }
        output = {"config": config_record, "debate": result}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        generated_files.append(str(out_path))
        print(f"Saved -> {out_path}")

    manifest_path = out_dir / "phase3_iter7_manifest.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(" ".join(generated_files) + "\n")
    print(f"Saved -> {manifest_path}")

    print("\nP(agree) trajectories:")
    for job in jobs:
        result = results_by_key[(job["cell"], job["seed"])]
        values = [
            f"T{t['turn']}{t['agent']}={t['probe']['p_agree']:.3f}"
            for t in result["debate_turns"]
        ]
        print(f"  {job['cell']} seed={job['seed']}: " + " ".join(values))
