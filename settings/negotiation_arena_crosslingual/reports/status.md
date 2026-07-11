# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. In this pass, buy/sell was rerun after
the runtime prompt was wired to `config/prompt_translations.json`; it again
reached a deal in 2 turns. C1 ID and G2 remain blocked only on pending human
review of 16 EN-ID translation units.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix
evidence. In this pass, `bash scripts/run_smoke.sh` was blocked by DNS for
`api.openai.com`; the blocker is recorded in
`artifacts/results/smoke_model_probe.json`.

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

BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T15:50:32+00:00` ERROR: scripts/run_smoke.sh exited 2
- `2026-07-11T15:50:38+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T15:50:38+00:00` BLOCKED: OpenAI smoke model probe failed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T15:51:06+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T15:51:12+00:00` OK: Local Qwen provider probe passed; artifact=artifacts/results/model_endpoint_probe.json
- `2026-07-11T15:52:01+00:00` OK: C0 baseline buy_sell episode completed; transcript=artifacts/transcripts/baseline_c0_buy_sell_en_seed001.json; metrics=artifacts/results/baseline_c0_buy_sell_en_seed001.metrics.json
- `2026-07-11T15:52:16+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T15:52:59+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 11 |
| Logs | 31 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
