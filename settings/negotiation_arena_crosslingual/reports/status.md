# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17`
per user request on 2026-07-12, and active language pairs are EN-ID, EN-ZH,
and ZH-ID. New benchmark artifacts must be labeled as OpenAI evidence, not
Qwen evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. Rules/private state may remain in English; C0/C1/C2/C3
constrain visible negotiation messages and validate channel compliance from
transcripts.

Current executable blocker: `bash scripts/run_c1_baseline.sh` uses the active
OpenAI benchmark provider by default. It was rerun at 2026-07-12T02:16:19 UTC.

Next useful work: **Run C1 ID baseline with ID-only output-channel instructions**.

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
| Default model | `gpt-5.4-mini-2026-03-17` |
| Active benchmark model | `openai / gpt-5.4-mini-2026-03-17` |
| Model note | active benchmark execution model |
| Language pairs | EN-ID, EN-ZH, ZH-ID |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | payoff, deal_rate, payoff_asymmetry, turns_to_deal, offer_parse_rate |
| Acceptance gate | C0 deal rate >=50%; offer parse rate >=90% |

## Blockers / Errors

BLOCKED: Direct top-level shell curl to https://api.openai.com/v1/models resolved and returned HTTP 401, but Python urllib and Python subprocess curl still report DNS failure for api.openai.com; C1 runner remains blocked before transcript generation; failed_command=bash scripts/run_c1_baseline.sh; artifacts=artifacts/results/benchmark_model_probe.json,artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T02:17:24+00:00` BLOCKED: Direct top-level shell curl to https://api.openai.com/v1/models resolved and returned HTTP 401, but Python urllib and Python subprocess curl still report DNS failure for api.openai.com; C1 runner remains blocked before transcript generation; failed_command=bash scripts/run_c1_baseline.sh; artifacts=artifacts/results/benchmark_model_probe.json,artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json
- `2026-07-12T02:17:56+00:00` OK: Harness scaffold check passed
- `2026-07-12T02:19:00+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_101528.txt
- `2026-07-12T02:19:00+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T02:19:01+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T02:19:03+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T02:19:09+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-12T02:19:09+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 17 |
| Logs | 66 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
