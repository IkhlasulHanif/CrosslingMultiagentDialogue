# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked only on
pending human review of 16 EN-ID translation units. This pass refreshed the
real C1 command artifact and the G2 gate summary at 2026-07-11T16:10 UTC.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix
evidence. An earlier pass saw `bash scripts/run_smoke.sh` blocked by DNS for
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

- `2026-07-11T15:54:40+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T15:54:42+00:00` OK: Codex pass 15 completed
- `2026-07-11T16:09:42+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260712_000942.txt
- `2026-07-11T16:10:34+00:00` OK: Harness scaffold check passed
- `2026-07-11T16:10:39+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T16:10:39+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T16:10:44+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T16:11:31+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 11 |
| Logs | 32 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
