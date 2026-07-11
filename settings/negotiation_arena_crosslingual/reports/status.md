# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout. The smoke used the explicitly allowed OpenAI override
for runner bring-up only, so it is not Qwen3-1.7B research-matrix evidence.

Current Qwen baseline blocker: `bash scripts/run_c0_baseline.sh` is wired but
needs a reachable local Qwen/vLLM endpoint; `modal run scripts/run_c0_baseline_modal.py`
is also wired but Modal app creation is blocked by the workspace billing cycle
spend limit.

Smoke artifact: `artifacts/transcripts/smoke_c0_buy_sell_en_001.json`.
Metrics artifact: `artifacts/results/smoke_c0_buy_sell_en_001.metrics.json`.
The smoke reached a deal in 2 turns with `offer_parse_rate=1.0`; this is only

Next useful work: **Run C0 EN baseline with Qwen3-1.7B**.

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

- `2026-07-11T11:16:46+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T11:16:46+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T11:16:48+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T11:16:56+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T11:16:56+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-11T11:16:56+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T11:16:56+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T11:16:58+00:00` OK: Codex pass 1 completed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 1 |
| Result summaries | 6 |
| Logs | 16 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
