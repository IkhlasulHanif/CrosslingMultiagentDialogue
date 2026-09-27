# goals.md: grounded-arena

Single source of truth for the coding agent: question, model access, variant rules, metrics, steps, layout. Read all of it before writing code.

## 0. The question

In x-arena, buy-sell outcomes collapsed. Deals landed near the buyer's maximum (the 40/60 setting ends near 60), and only 2 of 4,860 games ended without a deal. With no spread in outcomes, language has no room to show an effect.

This run asks two things, in order:

- **Stage A:** which game variables make buy-sell outcomes spread out, while keeping two-way dialogue and a right-or-wrong outcome?
- **Stage B:** once outcomes spread, does the language each agent speaks change who wins?

Stage B starts only after Stage A produces a setting that passes the variance gate (§5).

## 1. Fixed inputs

| Input | Where | Note |
|---|---|---|
| Upstream game | `vendor/NegotiationArena/`, pinned commit | Buy-sell game only. The commit hash goes in every manifest. |
| Model | K2 Horizon via the IFM API | Same model in both seats. |
| API key | `secrets/api.txt` | Put there by the human. Gitignored. |
| Endpoint + model id | `.env` → `IFM_BASE_URL`, `IFM_MODEL` | Agent fills these in S0 from docs.ifm.ai. |
| Item catalog | AmazonHistoryPrice (Xia et al. 2024, arXiv 2402.15813) | Real products with a reference price and historical low/high. Fetched in S7. |
| Exchange rates | `configs/fx.toml` | USD→IDR market rate and World Bank PPP factor, one fixed date, source URL recorded. |

## 2. Rules

1. Every model call goes through `arena_plus/k2.py` (§3). No direct API calls anywhere else.
2. Upstream code stays untouched; variants are layered on top (§4).
3. Stage A changes one variable at a time against the baseline. The only exception is S10, which combines variables on purpose.
4. Deterministic metrics carry every number in §5. An LLM may tag transcripts for description, but never inside a test.
5. Every run has a meaningful name (listed in §6–§7). Never `exp1`, `test`, `new`, `final2`.
6. After each step, update `STATE.md`, regenerate the report, then commit and push.
7. The only stop is the budget circuit breaker (§3). When it fires, commit, write the stopping point in `STATE.md`, and wait for the human.

## 3. Model access (K2 Horizon)

### 3.1 Setup (S0)

- Confirm `secrets/` and `.env` are in `.gitignore` **before** the first commit. Never print, log or commit the key.
- Write `.env` with two lines:
  - `IFM_BASE_URL=<from docs.ifm.ai>`
  - `IFM_MODEL=<largest K2 Horizon id the endpoint serves>`
  
  The fleet goes 0.9B, 3.7B, 7B, 32B, 36B-A4B, 375B-A23B. Pick the largest one that is served, and record the choice in `DEVIATIONS.md`.
- `pip install openai`.
- Fill `USD_PER_M_IN` and `USD_PER_M_OUT` in `arena_plus/k2.py` from the IFM price page. The human may change `BUDGET_USD`.

### 3.2 Client: create `arena_plus/k2.py` exactly like this

```python
"""Only entry point for K2 calls. Logs every call to logs/api_calls.jsonl (cost meter source)."""
import hashlib, json, os, time
from pathlib import Path
from openai import OpenAI

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / "logs" / "api_calls.jsonl"
USD_PER_M_IN, USD_PER_M_OUT = 0.0, 0.0   # fill in S0
BUDGET_USD = 50.0                        # human sets; never raise it yourself
SAMPLING = dict(temperature=1.0, top_p=0.95, max_tokens=8192)  # max_tokens frozen in S0

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
```

### 3.3 Multi-turn rule (from the IFM docs, important)

K2 returns its thinking in `reasoning_content`, separate from the reply in `content`. **Each seat keeps its own message list**, built like this:

- `system`: that seat's private prompt, containing only its own hidden values.
- `user`: the opponent's visible reply, as `content` only.
- `assistant`: this seat's own previous turn. It must carry **both** fields, with `reasoning_content` passed back exactly as returned (keep `""` as `""`; do not drop it or turn it into `None`).

```python
messages.append({"role": "assistant", "content": msg.content, "reasoning_content": msg.reasoning_content})
```

Consequences:
- The opponent never sees `reasoning_content`.
- Each seat keeps its own thinking in context, as the model expects.
- The transcript logs both fields. The language of the thinking is an analysis object, as it was in x-arena.

### 3.4 Sampling, truncation, cost

- **Sampling.** Temperature 1.0 and top_p 0.95 (model-card recommendation). x-arena ran at temperature 0, which likely fed the collapse. Variance across games comes from repeated games, one seed id each. S0 checks that the hosted API accepts these parameters. If it rejects one, drop that parameter and log it.
- **Truncation.** If `finish_reason == "length"` on more than 2% of turns in a run, raise `max_tokens` between runs and log it. Never parse an offer from a truncated reply: mark the turn `truncated` and count it.
- **Frozen settings.** Once S0 ends, `SAMPLING` stays frozen for all of Stage A.
- **Budget stop.** On `BudgetExceeded`, stop, commit, and write the stopping point in `STATE.md`.

## 4. Adding a variant (no forking)

A **variant** is one named change to the buy-sell scenario. Example: `batna` gives each side a private walk-away alternative. Upstream stays untouched in `vendor/`; wrap or subclass its classes. If an upstream edit is truly unavoidable, it goes in `patches/*.patch`, applied at build time, and gets logged.

Each variant is one file, `arena_plus/variants/<name>.py`, exporting:

| Piece | What it is | Example (`batna`) |
|---|---|---|
| `sample(seed) -> dict` | Draws the hidden episode parameters. | `{"seller_cost": 38, "buyer_value": 61, "buyer_alt": 55}` |
| `prompt_fragments(params, seat) -> str` | Text added to that seat's system prompt, in its language. | "Another seller offers the same item for 55." |
| `score(transcript, params) -> dict` | Deterministic outcome fields, no LLM involved. | `{"deal": True, "price": 53, "buyer_share": 0.35, "correct": True}` |
| `CHECKS` | Rule/regex checks run on every transcript. | Buyer states its own max; price out of bounds. |

Rules:
- **Composition.** Variants compose from a list in the run config. Their `sample` dicts merge, and a key collision raises an error.
- **Reproducible parameters.** Every hidden number goes into the game record. `game_id = f"{run}-{seed:04d}"`. The same seed must give the same sampled params.
- **Right-or-wrong outcome.** Any variant that can make a deal impossible or unwise must emit `correct: bool`: did the agent take the action its private information called for?
- **Smoke first.** `make smoke RUN=x N=5`, then read all 5 transcripts in full. Check that each seat sees only its own private info, that parsed prices match the text, and that `CHECKS` fire where expected. Write 2–3 lines in `runs/<run>/SMOKE.md`, and only then run in full.
- **Manifest.** Every run writes `runs/<run>/manifest.json` with: variant list, config hash, model id, sampling, upstream commit, number of games, git SHA. A directory without a manifest is not a run.

## 5. Outcome metrics (all deterministic)

For a deal at price `p`, where the seller's cost is `c` and the buyer's value is `v`:

- **Buyer share** `s = (v − p) / (v − c)`: how much of the available surplus the buyer kept. 0 means the buyer paid its full value; 1 means it paid the seller's cost. Example: `c=40, v=60, p=58` gives `s = 0.1`.
- **Cap-collapse rate:** share of feasible deals with `s ≤ 0.1`, i.e. the price landed near the buyer's maximum. This is the x-arena failure, measured directly.
- **Spread:** interquartile range (IQR) of `s`, the width of the middle 50% of outcomes. x-arena's was near zero.
- **Deal rate:** reported separately for feasible and infeasible games.
- **Correct rate** (right-or-wrong): the share of games where the agent took the action its private information called for. Examples: walking away when no deal is possible; not buying a defective item at a good-item price.
- **Leak rate:** share of games where a seat states its own private value outright ("my budget is 60"). Detected by regex plus a number match against the hidden params.
- **Integrative capture** (multi-issue games only, replaces `s`): joint points achieved divided by the best joint points possible.

**Variance gate.** A variant passes if all three hold:
- cap-collapse ≤ 50%;
- IQR(s) ≥ 0.25;
- if it has right-or-wrong games, the correct rate is between 20% and 90%, i.e. neither floor nor ceiling.

The thresholds are fixed now. Changing one requires a line in `DEVIATIONS.md` with the reason.

## 6. Stage A: find the variables that create spread (English–English)

Each step is 100 games unless stated. "vs baseline" means the same seeds with only that variable changed. Every step ends with:

- one histogram of `s` overlaid on baseline;
- one plain paragraph in the report;
- a gate verdict in `STATE.md`;
- the 3 most extreme transcripts copied into `CASEBOOK.md`, with a 2-line note each.

**S0 `s0-smoke`: setup and cost.**
- Do everything in §3.1 and ping the model.
- Play 5 baseline games and check the multi-turn rule (§3.3) on real transcripts.
- Measure cost per turn and the truncation rate.
- Write a cost-per-game table and the projected Stage A cost into `STATE.md`, then freeze `SAMPLING`.

**S1 `var-baseline`: replicate the collapse.**
- Upstream buy-sell, values 40/60.
- Expected: high cap-collapse and spread near 0.
- If it does not collapse with K2 at temperature 1.0, that is a finding. Record it and continue.

**S2 `var-noleak`: prompt-artifact check.**
- Baseline plus one system-prompt line: "Never state your own value or budget."
- Compare leak rate and cap-collapse with S1.
- If S1's leak rate was above 20% and S2 lowers collapse, this line becomes the default from S3 on.

**S3 `var-zopa`: randomized values, some deals impossible.**
- Sample `c` and `v` per game. In 25% of games `v < c`: no deal is possible and walking away is correct.

**S4 `var-batna`: outside options.**
- Each side privately knows an alternative, e.g. "another seller offers this for 55". It is sampled per game.
- Walking away counts as correct whenever the alternative beats every feasible price.

**S5 `var-deadline`: asymmetric time pressure.**
- One seat, chosen at random, loses 5% of its payoff per round. The other seat does not know this.

**S6 `var-multiissue`: price + delivery + warranty.**
- Each side gets a private points table, with opposed priorities on delivery vs. warranty. That creates room for cross-issue trades ("higher price for faster delivery").
- Define the tables and the max-joint-points computation in `arena_plus/variants/multiissue.py` before running.
- Report integrative capture.

**S7 `var-item`: real product.**
- The abstract item becomes a sampled AmazonHistoryPrice product. Both seats see its name, category, and public historical price range.
- `c` and `v` are sampled around the reference price.
- If the dataset can't be fetched, build a 60-item fallback list with the same fields and log it.

**S8 `var-quality`: hidden condition (persuasion layer).**
- Built on S7. The seller privately knows the condition: new, used-good, or defective. The buyer's value depends on it.
- The seller argues freely; the buyer decides.
- Correct = the buyer's final action is right for the true condition.

**S9 `var-currency`: currency and numeral scale.**
- Built on S7. Three arms of 60 games on shared seeds:
  - USD;
  - IDR at the market rate: same value, only the numbers get large;
  - IDR at the PPP-adjusted price: the item costs what it would feel like locally.
- **PPP (purchasing power parity)** converts a price into local purchasing-power terms using the World Bank PPP conversion factor in `configs/fx.toml`.

**S10 `grounded-v1`: combine what passed.**
- Merge every variant that passed the gate; 200 games.
- If fewer than two passed, combine the two with the lowest cap-collapse and note it.
- If `grounded-v1` fails the gate, stop Stage A and write a one-page `runs/grounded-v1/DIAGNOSIS.md` for the human.

## 7. Stage B: language (only after S10 passes)

- **Roster:** en, id, ar, ja, es.
- **Localization:** the task frame is localized per language, and each seat's reply language is pinned in its prompt.
- **Language check:** language ID runs on every reply, and off-language replies are counted.
- **Cost:** projected from S0's cost-per-game table and written to `STATE.md` before each step.

Steps:
- **B1 `lang-diag`:** both seats speak the same language, 5 × 100 games. Does the language shift the outcome distribution at all?
- **B2 `lang-cross`:** buyer language × seller language, 20 off-diagonal pairs × 60 games. Report the buyer-row and seller-column marginals first (x-arena found mostly additive per-side effects), then the pairing interaction.
- **B3 `lang-currency`:** an id-speaking buyer seeing IDR vs. seeing USD, against an en seller, 2 × 100 games. This is the realistic cross-border purchase.

If projected Stage B cost exceeds the remaining budget, cut B2 to en↔x pairs only and log the cut.

## 8. Layout and commands

```
vendor/NegotiationArena/    upstream, pinned, untouched
arena_plus/k2.py            K2 client (§3.2)
arena_plus/variants/        one file per variant (§4)
configs/                    fx.toml, runs/<run>.toml
runs/<run>/                 manifest.json, SMOKE.md, games.jsonl, transcripts/
logs/api_calls.jsonl        every call; cost meter source
reports/results.html        regenerated each step
STATE.md                    current step, gate verdicts, spend, next action
DEVIATIONS.md               every departure from this file: one line + reason
CASEBOOK.md                 flagged transcripts with notes
.env, secrets/api.txt       gitignored
```

`make smoke RUN=x N=5` · `make run RUN=x` · `make score RUN=x` (scores the run and writes the gate verdict) · `make report` · `make cost`

**Report style:** follow the report/figure law in `AGENTS.md` if the repo has one. Otherwise: self-contained HTML, inline SVG, no JS chart libraries, and one fixed color per language everywhere.

## 9. Done

- **Stage A is done** when S0–S10 each have a manifest, a report section, a gate verdict and casebook entries, and `grounded-v1` has a verdict.
- **Stage B is done** when B1–B3 are either run or explicitly cut in `DEVIATIONS.md`.
- **Final report:** it opens with one table: each variant, its cap-collapse, IQR(s), correct rate, and pass/fail.
