# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout using the explicitly allowed OpenAI smoke override.
It reached a deal in 2 turns with `offer_parse_rate=1.0`, but this is only
runner bring-up evidence, not Qwen3-1.7B research-matrix evidence.

One real Qwen3-1.7B C0 EN-monolingual buy/sell baseline has now run through the
same upstream checkout using the cached local Transformers provider
`hf-cache://Qwen/Qwen3-1.7B`. Artifact paths:
`artifacts/transcripts/baseline_c0_buy_sell_en_seed001.json` and
`artifacts/results/baseline_c0_buy_sell_en_seed001.metrics.json`.

Baseline result: deal reached in 2 turns at price 40. Metrics:
`deal_rate=1.0`, `offer_parse_rate=1.0`, first-offer price 40, final price 40,
anchoring signed delta 0, seller payoff 0, buyer payoff 60.

One real Qwen3-1.7B C0 EN-monolingual resource-exchange baseline has also run
through upstream `games/trading_game` on the same paper branch. Artifact paths:
`artifacts/transcripts/baseline_c0_resource_exchange_en_seed001.json` and
`artifacts/results/baseline_c0_resource_exchange_en_seed001.metrics.json`.

Resource-exchange result: upstream accepted a deal in 2 turns, with
`deal_rate=1.0` and `offer_parse_rate=1.0`, but the accepted allocation was
effectively unchanged from the initial resources and both upstream ResourceGoal
outcomes were false. The transcript records numeric 1/0 goal satisfaction as the
temporary setting-local payoff for this game.

Next useful work: **Human-check ID translation before C1/C2/C3**.

## Question

Does the higher-resource language channel capture a negotiation payoff premium?

## State

| Field | Value |
|---|---|
| Setting | `negotiation_arena_crosslingual` |
| Benchmark | `B5` / NegotiationArena |
| Bucket | competitive_mixed_motive |
| Priority | 1 |
| Phase | setup |
| Default model | `Qwen3-1.7B` |
| Language pairs | EN-ID, EN-ZH, EN-AR, ZH-ID, AR-ID, ID-AR |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | payoff, deal_rate, payoff_asymmetry, turns_to_deal, offer_parse_rate |
| Acceptance gate | C0 deal rate >=50%; offer parse rate >=90% |

## Blockers / Errors

Human bilingual review of the Indonesian prompt/rule translations is still
pending. `bash scripts/run_c1_baseline.sh` remains gated until
`config/translation_review.json` is completed and
`python3 scripts/validate_translation_review.py` passes.

Resource-exchange C0 execution is now live, but the first Qwen episode shows a
zero-progress accepted trade; inspect trade-legality/payoff semantics before
using resource_exchange in a full matrix.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T13:57:37+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T13:57:37+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T13:57:38+00:00` OK: Codex pass 9 completed
- `2026-07-11T14:12:38+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260711_221238.txt
- `2026-07-11T14:16:23+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T14:16:30+00:00` OK: Local Qwen provider probe passed; artifact=artifacts/results/model_endpoint_probe.json
- `2026-07-11T14:17:08+00:00` OK: C0 resource_exchange episode completed; transcript=artifacts/transcripts/baseline_c0_resource_exchange_en_seed001.json; metrics=artifacts/results/baseline_c0_resource_exchange_en_seed001.metrics.json
- `2026-07-11T14:18:04+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 10 |
| Logs | 26 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
