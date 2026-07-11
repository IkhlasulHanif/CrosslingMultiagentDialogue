No benchmark data has run yet, so there is no empirical answer on whether the
higher-resource language channel captures a negotiation payoff premium.

Current empirical story: null state; no transcripts, result summaries, or
smoke-test episodes exist yet.

Latest run: `./harness.sh run-smoke` reached the OpenAI smoke endpoint gate and
exited 2 before any model episode ran. OpenAI smoke is explicitly allowed by
`config/smoke_model.json` for first runner bring-up only, not as Qwen3-1.7B
research-matrix evidence.

Current blocker: DNS/network access to `https://api.openai.com/v1/chat/completions`
is unavailable from this session. The configured API key source was found, but
the key was not printed. The smoke client now retries Python DNS/certificate
failures with `curl --config -` so the key is not placed in command-line
arguments. The current artifact records both failures:
`urllib failed: <urlopen error [Errno 8] nodename nor servname provided, or not known>`;
`curl fallback exit 6: curl: (6) Could not resolve host: api.openai.com`.
Blocker artifact: `artifacts/results/smoke_model_probe.json`.

Next command once DNS/network access is available, or once the local Qwen endpoint
is preferred by setting `NEGOTIATION_SMOKE_PROVIDER=local_qwen` and starting
`LOCAL_QWEN_BASE_URL`:

```bash
./harness.sh run-smoke
```

Source bring-up is resolved. `external/NegotiationArena` is a local checkout of
`https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. `artifacts/results/bringup_check.json`
verifies README presence, requirements, selected-game Python files for resource
exchange and buy/sell, and branch-aware license evidence. The experiment branch
has no `LICENSE` file and no MIT text in its README; the probe records evidence
from local `main` commit `c447fafd439a20b84cdedeb2f8a85c4fad764745`, whose
README has the MIT badge and points paper users to `paper_experiment_code`.

Smoke execution is wired to a real upstream path. `scripts/run_smoke.sh`
validates the smoke plan, verifies source bring-up, validates the offer parser
and process metrics, probes the selected model endpoint, and then calls
`scripts/run_c0_smoke.py` for exactly one C0 EN-monolingual buy/sell episode.
The runner uses upstream `BuySellGame` and writes:

- `artifacts/transcripts/smoke_c0_buy_sell_en_001.json`
- `artifacts/results/smoke_c0_buy_sell_en_001.metrics.json`

The OpenAI smoke runner uses a standard-library chat-completions client and
records `model_plan.evidence_scope` so outputs cannot be confused with Qwen3-1.7B
research-matrix evidence. The upstream package imports optional OpenAI/Anthropic
agent modules from `ratbench.agents.__init__`; the smoke runner installs
import-only shims for those unused SDKs and uses its own agent class.

Human bilingual review of the Indonesian translations remains pending and must
be completed before ID baselines or mixed-language conditions are treated as
valid benchmark evidence.
