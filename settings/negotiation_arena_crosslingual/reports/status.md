# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked on pending
human review of 16 EN-ID translation units.

OpenAI benchmark override wrappers exist for C0 buy/sell and resource_exchange.
A fresh real C0 OpenAI buy/sell attempt at 2026-07-11T20:40:47 UTC produced no
transcript because `api.openai.com` could not be resolved by urllib or curl.
Blocker artifact: `artifacts/results/benchmark_model_probe.json`. Retry after
network/DNS access is restored with `bash scripts/run_c0_openai_baseline.sh`.
No OpenAI benchmark evidence was produced in this pass.



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
| Active benchmark model | `openai / gpt-4.1-mini` |
| Model note | benchmark execution override |
| Language pairs | EN-ID, EN-ZH, EN-AR, ZH-ID, AR-ID, ID-AR |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | payoff, deal_rate, payoff_asymmetry, turns_to_deal, offer_parse_rate |
| Acceptance gate | C0 deal rate >=50%; offer parse rate >=90% |

## Blockers / Errors

BLOCKED: C0 OpenAI benchmark baseline blocked on provider probe; failed_command=bash scripts/run_c0_openai_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T20:40:47+00:00` BLOCKED: C0 OpenAI benchmark baseline blocked on provider probe; failed_command=bash scripts/run_c0_openai_baseline.sh
- `2026-07-11T20:41:37+00:00` OK: Harness scaffold check passed
- `2026-07-11T20:42:19+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_044022.txt
- `2026-07-11T20:42:19+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T20:42:19+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T20:42:20+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T20:42:27+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T20:42:27+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 14 |
| Logs | 48 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
