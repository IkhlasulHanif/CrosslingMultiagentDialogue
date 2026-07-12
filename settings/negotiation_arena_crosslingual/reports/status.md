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
OpenAI benchmark provider by default. It was rerun at 2026-07-12T03:46:43 UTC.

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

BLOCKED: Direct shell curl to https://api.openai.com/v1/models cannot resolve api.openai.com; C1 OpenAI benchmark runner remains blocked before transcript generation; failed_command=bash scripts/run_c1_baseline.sh; artifact=artifacts/results/network_sandbox_probe_20260712T034720Z.json

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T03:47:20+00:00` BLOCKED: Direct shell curl to https://api.openai.com/v1/models cannot resolve api.openai.com; C1 OpenAI benchmark runner remains blocked before transcript generation; failed_command=bash scripts/run_c1_baseline.sh; artifact=artifacts/results/network_sandbox_probe_20260712T034720Z.json
- `2026-07-12T03:48:41+00:00` OK: Harness scaffold check passed
- `2026-07-12T03:49:47+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_114617.txt
- `2026-07-12T03:49:47+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T03:49:48+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T03:49:49+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T03:49:52+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-12T03:49:52+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 20 |
| Logs | 71 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
