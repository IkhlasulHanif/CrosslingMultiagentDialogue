# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

One real C0 EN-monolingual buy/sell smoke episode ran through upstream
NegotiationArena using the explicitly allowed OpenAI smoke override; it is
runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence.
Two real Qwen3-1.7B C0 EN-monolingual baselines have run through the same
checkout via `hf-cache://Qwen/Qwen3-1.7B`: `buy_sell` and `resource_exchange`.
Both reached deals in 2 turns with `deal_rate=1.0` and `offer_parse_rate=1.0`.
`artifacts/results/g2_capability_floor.json` confirms the C0 floor passes on
existing Qwen evidence, but G2 remains blocked until C1 ID metrics exist.

Buy/sell result: deal reached at price 40. First-offer price and final price
were both 40, anchoring signed delta was 0, seller payoff was 0, and buyer
payoff was 60. Payoff asymmetry is not defined for C0 because both roles are EN.

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

BLOCKED: C1 ID baseline is gated on pending bilingual human review of the EN-ID
prompt translations. Artifact:
`artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json`.
Next command after review approval: `bash scripts/run_c1_baseline.sh`.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T14:56:55+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T14:57:00+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T14:57:00+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-11T14:57:00+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T14:57:00+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T14:57:02+00:00` OK: Codex pass 12 completed
- `2026-07-11T15:12:02+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260711_231202.txt
- `2026-07-11T15:13:14+00:00` OK: Harness scaffold check passed
- `2026-07-11T15:13:18+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T15:13:18+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T15:13:22+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 11 |
| Logs | 29 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
