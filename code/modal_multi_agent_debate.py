"""
Modal/Qwen fallback runner for Phase 3 multi-agent debate blocks.

This mirrors code/openai_multi_agent_debate.py's artifact layout while using
Qwen on Modal. Use it when the OpenAI Responses API is unavailable or quota
limited.

Examples:
  modal run code/modal_multi_agent_debate.py --block p3_r2_id_cn_native_english --iter-num 155
  modal run code/modal_multi_agent_debate.py --block p3_r2_id_cn_native_english --iter-num 155 --limit-jobs 2
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import modal


DEFAULT_BLOCKS_PATH = "config/discovery_blocks.json"
DEFAULT_PROMPTS_PATH = "config/prompts.json"
DEFAULT_MODEL = "Qwen/Qwen3-4B"
OUTPUT_DIR = Path("artifacts/transcripts")

app = modal.App("phase3-modal-multi-agent-debate")
image = modal.Image.debian_slim().pip_install(
    "transformers", "torch", "accelerate", "sentencepiece"
)


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def display_name(mapping: dict[str, str], key: str) -> str:
    return mapping.get(key, key)


def format_turn(
    turn: dict[str, Any], countries: dict[str, str], languages: dict[str, str]
) -> str:
    country = display_name(countries, turn["country"])
    lang = display_name(languages, turn["lang"])
    return (
        f"Turn {turn['turn']} | Agent {turn['agent']} | "
        f"{country} persona | {lang}:\n{turn['text']}"
    )


def make_system_prompt(
    agent: dict[str, str],
    prompts: dict[str, Any],
    countries: dict[str, str],
    languages: dict[str, str],
) -> str:
    country = display_name(countries, agent["country"])
    lang = display_name(languages, agent["lang"])
    persona = prompts["debate"]["persona"].format(country=country)
    language = prompts["debate"]["language"].format(lang=lang)
    return (
        f"{persona} {language} You are Agent {agent['id']} in this discussion. "
        "Do not speak for the other agents."
    )


def build_generation_input(
    *,
    agent: dict[str, str],
    item_statement: str,
    turns: list[dict[str, Any]],
    prompts: dict[str, Any],
    countries: dict[str, str],
    languages: dict[str, str],
) -> str:
    lang = display_name(languages, agent["lang"])
    task_intro = prompts["debate"]["task_intro"].format(item=item_statement)

    if not turns:
        opener = prompts["debate"]["opener"].format(lang=lang)
        return f"{task_intro}\n\n{opener}"

    transcript = "\n\n".join(format_turn(t, countries, languages) for t in turns)
    multi_turn_template = prompts["debate"].get("multi_agent_other_turn")
    if multi_turn_template:
        country = display_name(countries, agent["country"])
        return (
            f"{task_intro}\n\n"
            + multi_turn_template.format(
                my_country=country,
                my_lang=lang,
                text=transcript,
            )
        )

    return (
        f"{task_intro}\n\nDiscussion so far:\n{transcript}\n\n"
        f"Now respond as Agent {agent['id']} in {lang}. Keep your response to 3-5 sentences."
    )


def build_probe_input(
    *,
    item_statement: str,
    turns: list[dict[str, Any]],
    probe_template: str,
    countries: dict[str, str],
    languages: dict[str, str],
) -> str:
    transcript = "\n\n".join(format_turn(t, countries, languages) for t in turns)
    probe = probe_template.format(item=item_statement)
    return f"Discussion so far:\n{transcript}\n\n{probe}"


def select_jobs(
    *,
    blocks_config: dict[str, Any],
    block_name: str,
    iter_num: int,
    seeds_override: list[int] | None,
    cells_filter: set[str] | None,
) -> list[dict[str, Any]]:
    block = blocks_config["blocks"][block_name]
    items = blocks_config["items"]
    item_key = block["item_key"]
    item_statement = items[item_key]
    seeds = seeds_override if seeds_override is not None else block["seeds"]
    jobs: list[dict[str, Any]] = []

    for cell in block["cells"]:
        if cells_filter and cell["cell"] not in cells_filter:
            continue
        for seed in seeds:
            jobs.append(
                {
                    "phase": 3,
                    "iter": iter_num,
                    "block": block_name,
                    "block_description": block["description"],
                    "cell": cell["cell"],
                    "cell_role": cell.get("role", "unspecified"),
                    "cell_description": cell["description"],
                    "agents": cell["agents"],
                    "seed": seed,
                    "n_turns": block["n_turns"],
                    "item_key": item_key,
                    "item_statement": item_statement,
                }
            )
    return jobs


def parse_int_list(value: str | None) -> list[int] | None:
    if not value:
        return None
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def parse_str_set(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {part.strip() for part in value.split(",") if part.strip()}


def chunked(values: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


@app.function(
    gpu="A10G",
    image=image,
    secrets=[modal.Secret.from_dotenv(path="secrets/modal.env")],
    max_containers=4,
    timeout=7200,
)
def run_job_batch(payload: dict[str, Any]) -> list[dict[str, Any]]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    job_batch = payload["jobs"]
    prompts = payload["prompts"]
    countries = payload["countries"]
    languages = payload["languages"]
    runtime = payload["runtime"]

    model_name = runtime.get("modal_model") or runtime.get("model") or DEFAULT_MODEL
    if str(model_name).startswith("gpt-"):
        model_name = DEFAULT_MODEL
    temperature = float(runtime.get("temperature", 0.8))
    max_new_tokens = int(runtime.get("max_output_tokens", 420))

    print(f"Loading {model_name} for {len(job_batch)} debate job(s)")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="auto"
    )
    model.eval()

    digit_token_ids = [
        tokenizer.encode(str(d), add_special_tokens=False)[0] for d in range(1, 8)
    ]

    def generate_text(
        *,
        instructions: str,
        input_text: str,
        seed: int,
        turn_idx: int,
        max_tokens: int,
        temp: float,
    ) -> str:
        torch.manual_seed(seed + turn_idx)
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": input_text},
        ]
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
                max_new_tokens=max_tokens,
                temperature=temp,
                do_sample=temp > 0,
                repetition_penalty=1.12,
                pad_token_id=tokenizer.eos_token_id,
            )
        new_ids = output_ids[0][inputs["input_ids"].shape[1] :]
        return tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    def probe_digit_logits(
        *,
        instructions: str,
        input_text: str,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": input_text},
        ]
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
            "provider": "modal_qwen",
            "method": "next_token_digit_logits",
            "p_agree": round(float(p_agree), 4),
            "expected_digit": round(float(expected_digit), 4),
            "digit_token_ids": {
                str(d): int(digit_token_ids[i]) for i, d in enumerate(range(1, 8))
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

    def run_one(job: dict[str, Any]) -> dict[str, Any]:
        n_turns = int(job["n_turns"])
        agents = job["agents"]
        turns: list[dict[str, Any]] = []

        for idx in range(n_turns):
            agent = agents[idx % len(agents)]
            instructions = make_system_prompt(agent, prompts, countries, languages)
            input_text = build_generation_input(
                agent=agent,
                item_statement=job["item_statement"],
                turns=turns,
                prompts=prompts,
                countries=countries,
                languages=languages,
            )
            print(
                f"  {job['cell']} seed={job['seed']} turn={idx + 1} "
                f"agent={agent['id']} {agent['country']}/{agent['lang']}"
            )
            text = generate_text(
                instructions=instructions,
                input_text=input_text,
                seed=int(job["seed"]),
                turn_idx=idx,
                max_tokens=max_new_tokens,
                temp=temperature,
            )
            if not text:
                text = generate_text(
                    instructions=instructions,
                    input_text=input_text,
                    seed=int(job["seed"]) + 1000,
                    turn_idx=idx,
                    max_tokens=max_new_tokens,
                    temp=temperature,
                )
            turn_record = {
                "turn": idx + 1,
                "agent": agent["id"],
                "country": agent["country"],
                "lang": agent["lang"],
                "text": text,
            }
            turns.append(turn_record)

            probe_input = build_probe_input(
                item_statement=job["item_statement"],
                turns=turns,
                probe_template=prompts["probe"]["likert"],
                countries=countries,
                languages=languages,
            )
            turn_record["probe"] = probe_digit_logits(
                instructions=instructions,
                input_text=probe_input,
            )

        return {
            "cell": job["cell"],
            "cell_description": job["cell_description"],
            "cell_role": job["cell_role"],
            "item_key": job["item_key"],
            "item_statement": job["item_statement"],
            "agents": agents,
            "n_turns": n_turns,
            "seed": job["seed"],
            "provider": "modal_qwen",
            "model": model_name,
            "reasoning_effort": None,
            "debate_turns": turns,
        }

    return [run_one(job) for job in job_batch]


def write_outputs(
    *,
    jobs: list[dict[str, Any]],
    results: list[dict[str, Any]],
    prompts: dict[str, Any],
    runtime: dict[str, Any],
    iter_num: int,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().isoformat()
    results_by_key = {(r["cell"], r["seed"]): r for r in results}
    generated_files: list[str] = []

    for job in jobs:
        result = results_by_key[(job["cell"], job["seed"])]
        out_path = OUTPUT_DIR / f"phase3_iter{iter_num}_{job['cell']}_{job['seed']}.json"
        output = {
            "config": {
                **job,
                "timestamp": timestamp,
                "provider": "modal_qwen",
                "model": result["model"],
                "temperature": runtime.get("temperature"),
                "max_output_tokens": runtime.get("max_output_tokens"),
                "prompts": prompts,
            },
            "debate": result,
        }
        out_path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        generated_files.append(str(out_path))
        print(f"Saved -> {out_path}")

    manifest_path = OUTPUT_DIR / f"phase3_iter{iter_num}_manifest.txt"
    manifest_path.write_text("\n".join(generated_files) + "\n", encoding="utf-8")
    print(f"Saved -> {manifest_path}")


@app.local_entrypoint()
def main(
    block: str = "p3_r2_id_cn_native_english",
    iter_num: int = 0,
    config: str = DEFAULT_BLOCKS_PATH,
    prompts_path: str = DEFAULT_PROMPTS_PATH,
    seeds: str = "",
    cells: str = "",
    limit_jobs: int = 0,
    model: str = DEFAULT_MODEL,
    shard_size: int = 4,
    dry_run: bool = False,
) -> None:
    if iter_num <= 0:
        raise ValueError("Pass --iter-num with the Phase 3 harness iteration.")

    blocks_config = load_json(config)
    prompts = load_json(prompts_path)
    runtime = dict(blocks_config["runtime"])
    runtime["modal_model"] = model or runtime.get("modal_model") or DEFAULT_MODEL

    jobs = select_jobs(
        blocks_config=blocks_config,
        block_name=block,
        iter_num=iter_num,
        seeds_override=parse_int_list(seeds),
        cells_filter=parse_str_set(cells),
    )
    if limit_jobs:
        jobs = jobs[:limit_jobs]

    print(
        f"Block={block} iter={iter_num} provider=modal_qwen "
        f"model={runtime['modal_model']} jobs={len(jobs)}"
    )
    for job in jobs:
        agents = " ".join(
            f"{a['id']}={a['country']}/{a['lang']}" for a in job["agents"]
        )
        print(f"  {job['cell']} seed={job['seed']} {agents}")

    if dry_run:
        return

    shard_size = max(1, int(shard_size))
    batches = chunked(jobs, shard_size)
    print(f"Submitting {len(jobs)} job(s) as {len(batches)} Modal batch(es)")

    payloads = [
        {
            "jobs": batch,
            "prompts": prompts,
            "countries": blocks_config["countries"],
            "languages": blocks_config["languages"],
            "runtime": runtime,
        }
        for batch in batches
    ]
    batch_results = list(run_job_batch.map(payloads))
    results = [result for batch in batch_results for result in batch]
    if len(results) != len(jobs):
        raise RuntimeError(
            f"Expected {len(jobs)} Modal results, received {len(results)}."
        )

    write_outputs(
        jobs=jobs,
        results=results,
        prompts=prompts,
        runtime=runtime,
        iter_num=iter_num,
    )

    print("\nP(agree) trajectories:")
    for result in results:
        values = [
            f"T{t['turn']}{t['agent']}={t['probe']['p_agree']:.3f}"
            for t in result["debate_turns"]
            if "probe" in t
        ]
        print(f"  {result['cell']} seed={result['seed']}: " + " ".join(values))
