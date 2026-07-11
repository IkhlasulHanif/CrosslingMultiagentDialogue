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

BLOCKED: Scoped commit/push attempt failed before staging because git could not create /Users/ikhlasul.hanif/Documents/MultiAgent/.git/index.lock: Operation not permitted. Validated NegotiationArena C0 baseline artifacts remain local in settings/negotiation_arena_crosslingual.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T13:15:44+00:00` OK: Resolved local Qwen blocker by wiring cached Transformers provider hf-cache://Qwen/Qwen3-1.7B and added narrow XML normalization for Qwen accept-tag formatting; C0 seed001 completed after rerun.
- `2026-07-11T13:16:10+00:00` BLOCKED: Scoped commit/push attempt failed before staging because git could not create /Users/ikhlasul.hanif/Documents/MultiAgent/.git/index.lock: Operation not permitted. Validated NegotiationArena C0 baseline artifacts remain local in settings/negotiation_arena_crosslingual.
- `2026-07-11T13:17:15+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260711_210653.txt
- `2026-07-11T13:17:15+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T13:17:16+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T13:17:17+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T13:17:25+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T13:17:25+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 2 |
| Result summaries | 8 |
| Logs | 23 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
