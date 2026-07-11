# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked on pending
human review of 16 EN-ID translation units.

OpenAI benchmark override wrappers exist for C0 buy/sell and resource_exchange.
A fresh real C0 OpenAI buy/sell attempt at 2026-07-11T23:19:50 UTC produced no
transcript because `api.openai.com` could not be resolved by urllib or curl.
Blocker artifact: `artifacts/results/benchmark_model_probe.json`. Retry after
network/DNS access is restored with `bash scripts/run_c0_openai_baseline.sh`.
No OpenAI benchmark evidence was produced in this pass.

C1 and G2 gate artifacts were refreshed at 2026-07-11T23:20:05 UTC and
2026-07-11T23:20:10 UTC. `bash scripts/run_c1_baseline.sh` is executable but
stops at the human translation gate before reading the OpenAI key or producing
C1 metrics.

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

BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T23:19:49+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T23:19:50+00:00` BLOCKED: OpenAI benchmark model probe failed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-11T23:19:50+00:00` BLOCKED: C0 OpenAI benchmark baseline blocked on provider probe; failed_command=bash scripts/run_c0_openai_baseline.sh
- `2026-07-11T23:20:00+00:00` BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.
- `2026-07-11T23:20:05+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T23:20:05+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T23:20:10+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T23:21:13+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 14 |
| Logs | 57 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
