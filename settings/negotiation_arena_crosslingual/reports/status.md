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

BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T13:56:01+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T13:56:22+00:00` OK: Harness scaffold check passed
- `2026-07-11T13:57:29+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260711_215513.txt
- `2026-07-11T13:57:29+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T13:57:30+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T13:57:31+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T13:57:37+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T13:57:37+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 2 |
| Result summaries | 9 |
| Logs | 25 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
