# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked only on
pending human review of 16 EN-ID translation units. This pass refreshed the
real C1 command artifact at 2026-07-11T18:11:05 UTC and the G2 gate summary at
2026-07-11T18:11:09 UTC. The C1 gate artifact now records that, after human
review clears, the runner will select the explicit OpenAI benchmark override
(`openai_benchmark` / `gpt-4.1-mini`) and label resulting artifacts as OpenAI
benchmark evidence, not Qwen evidence.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix

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

- `2026-07-11T18:11:09+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T18:12:31+00:00` OK: Scoped commit/push succeeded for refreshed B5 C1 translation-gate artifact; commit=df01e3a2; remote=origin/main
- `2026-07-11T18:13:07+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_020934.txt
- `2026-07-11T18:13:07+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T18:13:07+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T18:13:09+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T18:13:14+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T18:13:14+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 12 |
| Logs | 40 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
