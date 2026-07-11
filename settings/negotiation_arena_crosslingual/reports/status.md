# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

No benchmark data has run yet, so there is no empirical answer on whether the
higher-resource language channel captures a negotiation payoff premium.

Current empirical story: null state; no transcripts, result summaries, or
smoke-test episodes exist yet.

Latest run: `./harness.sh run-smoke` reached the OpenAI smoke endpoint gate and
exited 2 before any model episode ran. OpenAI smoke is explicitly allowed by
`config/smoke_model.json` for first runner bring-up only, not as Qwen3-1.7B
research-matrix evidence.

Current blocker: DNS/network access to `https://api.openai.com/v1/chat/completions`

Next useful work: **Human-check ID translation**.

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

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T11:07:03+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260711_190237.txt
- `2026-07-11T11:07:03+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T11:07:03+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T11:07:04+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T11:07:12+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T11:07:12+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-11T11:07:12+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T11:07:12+00:00` OK: Codex pass 2 completed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 1 |
| Result summaries | 4 |
| Logs | 15 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
