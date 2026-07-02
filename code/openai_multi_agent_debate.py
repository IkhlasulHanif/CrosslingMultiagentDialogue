"""
OpenAI-backed multi-agent debate runner.

This is the fast discovery path for Phase 3. It supports 2-4 agents, arbitrary
persona/language assignments, and matched baseline/exploratory blocks defined in
config/discovery_blocks.json.

Examples:
  python code/openai_multi_agent_debate.py --block p3_r1_id_us_pairwise --iter 39 --dry-run
  python code/openai_multi_agent_debate.py --block p3_r1_id_us_pairwise --iter 39
  python code/openai_multi_agent_debate.py --block p3_r3_three_agent_emergence --iter 40 --limit-jobs 3

OpenAI API docs used for this path:
  - Responses API endpoint: POST /v1/responses
  - reasoning.effort supports "none" on GPT-5.1 and later models.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BLOCKS_PATH = Path("config/discovery_blocks.json")
DEFAULT_PROMPTS_PATH = Path("config/prompts.json")
OUTPUT_DIR = Path("artifacts/transcripts")
API_URL = "https://api.openai.com/v1/responses"
MODELS_URL = "https://api.openai.com/v1/models"
API_HOST = "api.openai.com"


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_api_key(api_key_file: str | None) -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    if api_key_file:
        path = Path(api_key_file)
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    raise RuntimeError(
        "OPENAI_API_KEY is not set and no readable api_key_file was found."
    )


def describe_url_error(exc: urllib.error.URLError) -> str:
    reason = getattr(exc, "reason", exc)
    if isinstance(reason, socket.gaierror):
        return f"DNS resolution failed for {API_HOST}: {reason}"
    if isinstance(reason, ssl.SSLError):
        return f"TLS certificate/handshake failed for {API_HOST}: {reason}"
    if isinstance(reason, TimeoutError):
        return f"Timed out connecting to {API_HOST}: {reason}"
    return f"Network error reaching {API_HOST}: {reason}"


def preflight_openai_api(api_key: str) -> None:
    try:
        resolved = socket.getaddrinfo(API_HOST, 443)[0][4][0]
    except socket.gaierror as exc:
        raise RuntimeError(f"OpenAI preflight failed: DNS resolution failed for {API_HOST}: {exc}") from exc

    request = urllib.request.Request(
        MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "multi-agent-discovery-preflight",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=20, context=ssl_context()
        ) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"OpenAI preflight failed: unexpected HTTP {response.status}"
                )
            response.read(512)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI preflight failed: HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI preflight failed: {describe_url_error(exc)}") from exc

    print(f"OpenAI preflight passed: {API_HOST} resolved to {resolved}; auth accepted.")


def display_name(mapping: dict[str, str], key: str) -> str:
    return mapping.get(key, key)


def extract_output_text(response: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    return "\n".join(part for part in parts if part).strip()


def openai_response(
    *,
    api_key: str,
    model: str,
    instructions: str,
    input_text: str,
    reasoning_effort: str,
    temperature: float,
    max_output_tokens: int,
    seed: int | None = None,
    retries: int = 3,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "instructions": instructions,
        "input": input_text,
        "reasoning": {"effort": reasoning_effort},
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    # Keep seed in the experiment metadata and filenames, but do not send it to
    # the Responses API: this endpoint currently rejects a top-level seed field.
    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            API_URL, data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(
                request, timeout=120, context=ssl_context()
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenAI HTTP {exc.code}: {message}")
            if exc.code not in {408, 409, 429, 500, 502, 503, 504}:
                raise last_error
        except urllib.error.URLError as exc:
            last_error = RuntimeError(describe_url_error(exc))
        except (TimeoutError, ConnectionResetError, socket.timeout) as exc:
            last_error = RuntimeError(f"Transient connection error reaching {API_HOST}: {exc}")

        if attempt < retries:
            time.sleep(2 * attempt)

    assert last_error is not None
    raise last_error


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


def format_turn(turn: dict[str, Any], countries: dict[str, str], languages: dict[str, str]) -> str:
    country = display_name(countries, turn["country"])
    lang = display_name(languages, turn["lang"])
    return (
        f"Turn {turn['turn']} | Agent {turn['agent']} | "
        f"{country} persona | {lang}:\n{turn['text']}"
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


def parse_likert_digit(text: str) -> int | None:
    match = re.search(r"\b([1-7])\b", text)
    if match:
        return int(match.group(1))
    compact = text.strip()
    if compact and compact[0] in "1234567":
        return int(compact[0])
    return None


def probe_to_record(response: dict[str, Any]) -> dict[str, Any]:
    text = extract_output_text(response)
    digit = parse_likert_digit(text)
    p_agree = round((digit - 1) / 6, 4) if digit is not None else None
    return {
        "provider": "openai",
        "method": "parsed_likert_digit",
        "p_agree": p_agree,
        "digit": digit,
        "text": text,
        "raw_response_id": response.get("id"),
        "usage": response.get("usage"),
        "note": "OpenAI path does not expose next-token digit logits here; use Qwen/Modal path for digit logits.",
    }


def run_job(
    *,
    job: dict[str, Any],
    prompts: dict[str, Any],
    countries: dict[str, str],
    languages: dict[str, str],
    api_key: str,
    runtime: dict[str, Any],
) -> dict[str, Any]:
    model = runtime["model"]
    reasoning_effort = runtime.get("reasoning_effort", "none")
    temperature = float(runtime.get("temperature", 0.8))
    max_output_tokens = int(runtime.get("max_output_tokens", 420))
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
        response = openai_response(
            api_key=api_key,
            model=model,
            instructions=instructions,
            input_text=input_text,
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            seed=int(job["seed"]),
        )
        text = extract_output_text(response)
        turn_record = {
            "turn": idx + 1,
            "agent": agent["id"],
            "country": agent["country"],
            "lang": agent["lang"],
            "text": text,
            "response_id": response.get("id"),
            "usage": response.get("usage"),
        }
        turns.append(turn_record)

        probe_input = build_probe_input(
            item_statement=job["item_statement"],
            turns=turns,
            probe_template=prompts["probe"]["likert"],
            countries=countries,
            languages=languages,
        )
        probe_response = openai_response(
            api_key=api_key,
            model=model,
            instructions=instructions,
            input_text=probe_input,
            reasoning_effort=reasoning_effort,
            temperature=0.0,
            max_output_tokens=16,
            seed=int(job["seed"]),
        )
        turn_record["probe"] = probe_to_record(probe_response)

    return {
        "cell": job["cell"],
        "cell_description": job["cell_description"],
        "cell_role": job["cell_role"],
        "item_key": job["item_key"],
        "item_statement": job["item_statement"],
        "agents": agents,
        "n_turns": n_turns,
        "seed": job["seed"],
        "provider": "openai",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "debate_turns": turns,
    }


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
    generated_files: list[str] = []

    for job, result in zip(jobs, results):
        out_path = OUTPUT_DIR / f"phase3_iter{iter_num}_{job['cell']}_{job['seed']}.json"
        output = {
            "config": {
                **job,
                "timestamp": timestamp,
                "provider": "openai",
                "model": runtime["model"],
                "reasoning_effort": runtime.get("reasoning_effort", "none"),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", default="p3_r1_id_us_pairwise")
    parser.add_argument("--iter", type=int, required=True)
    parser.add_argument("--config", default=str(DEFAULT_BLOCKS_PATH))
    parser.add_argument("--prompts", default=str(DEFAULT_PROMPTS_PATH))
    parser.add_argument("--seeds", help="Comma-separated seed override.")
    parser.add_argument("--cells", help="Comma-separated cell suffix filter.")
    parser.add_argument("--limit-jobs", type=int, default=0)
    parser.add_argument("--model")
    parser.add_argument("--reasoning-effort")
    parser.add_argument("--api-key-file")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    blocks_config = load_json(Path(args.config))
    prompts = load_json(Path(args.prompts))
    runtime = dict(blocks_config["runtime"])
    if args.model:
        runtime["model"] = args.model
    if args.reasoning_effort:
        runtime["reasoning_effort"] = args.reasoning_effort
    if args.api_key_file:
        runtime["api_key_file"] = args.api_key_file

    jobs = select_jobs(
        blocks_config=blocks_config,
        block_name=args.block,
        iter_num=args.iter,
        seeds_override=parse_int_list(args.seeds),
        cells_filter=parse_str_set(args.cells),
    )
    if args.limit_jobs:
        jobs = jobs[: args.limit_jobs]

    print(
        f"Block={args.block} iter={args.iter} provider=openai "
        f"model={runtime['model']} reasoning={runtime.get('reasoning_effort', 'none')}"
    )
    print(f"Jobs={len(jobs)}")
    for job in jobs:
        agents = " ".join(
            f"{a['id']}={a['country']}/{a['lang']}" for a in job["agents"]
        )
        print(f"  {job['cell']} seed={job['seed']} {agents}")

    if args.dry_run:
        return 0

    api_key = read_api_key(runtime.get("api_key_file"))
    if args.preflight:
        preflight_openai_api(api_key)
        return 0
    if not args.skip_preflight:
        preflight_openai_api(api_key)

    results: list[dict[str, Any]] = []
    for job in jobs:
        result = run_job(
            job=job,
            prompts=prompts,
            countries=blocks_config["countries"],
            languages=blocks_config["languages"],
            api_key=api_key,
            runtime=runtime,
        )
        results.append(result)

    write_outputs(
        jobs=jobs,
        results=results,
        prompts=prompts,
        runtime=runtime,
        iter_num=args.iter,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
