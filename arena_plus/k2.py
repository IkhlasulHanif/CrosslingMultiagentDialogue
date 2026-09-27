"""Only entry point for K2 calls. Logs every call to logs/api_calls.jsonl (cost meter source)."""
import hashlib, json, os, time
from pathlib import Path
from openai import OpenAI

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / "logs" / "api_calls.jsonl"
USD_PER_M_IN, USD_PER_M_OUT = 0.0, 0.0   # fill in S0
BUDGET_USD = 50.0                        # human sets; never raise it yourself
SAMPLING = dict(temperature=1.0, top_p=0.95, max_tokens=16384)  # max_tokens frozen in S0; raised 8192 -> 16384 after S4 (§3.4 truncation rule)

def _load_env():
    for line in (REPO / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
    os.environ.setdefault("IFM_API_KEY", (REPO / "secrets" / "api.txt").read_text().strip())

_load_env()
client = OpenAI(base_url=os.environ["IFM_BASE_URL"], api_key=os.environ["IFM_API_KEY"], timeout=600)

class BudgetExceeded(RuntimeError): ...

def spent_usd() -> float:
    if not LOG.exists(): return 0.0
    rows = [json.loads(l) for l in LOG.read_text().splitlines()]
    return sum(r["prompt_tokens"] / 1e6 * USD_PER_M_IN + r["completion_tokens"] / 1e6 * USD_PER_M_OUT for r in rows)

def chat(messages, *, run, game_id, turn, seat):
    if spent_usd() >= BUDGET_USD:
        raise BudgetExceeded(f"spent >= ${BUDGET_USD}")
    for attempt in range(6):
        try:
            resp = client.chat.completions.create(model=os.environ["IFM_MODEL"], messages=messages, **SAMPLING)
            break
        except Exception as e:
            print(f"[k2] {type(e).__name__}: {e}; retry in {2**attempt}s"); time.sleep(2 ** attempt)
    else:
        raise RuntimeError("K2 call failed after retries")
    msg, u = resp.choices[0].message, resp.usage
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps({"ts": time.time(), "run": run, "game_id": game_id, "turn": turn, "seat": seat,
            "model": resp.model, "prompt_tokens": u.prompt_tokens, "completion_tokens": u.completion_tokens,
            "finish_reason": resp.choices[0].finish_reason,
            "prompt_sha": hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()[:12]}) + "\n")
    return msg, resp.choices[0].finish_reason

if __name__ == "__main__":   # S0 ping: python -m arena_plus.k2
    m, fr = chat([{"role": "user", "content": "hello"}], run="s0-smoke", game_id="ping", turn=0, seat="none")
    print(m.content, "| reasoning:", repr(getattr(m, "reasoning_content", None))[:200], "| finish:", fr)
    print(f"spent ${spent_usd():.4f}")
