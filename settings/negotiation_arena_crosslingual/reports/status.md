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

Current executable blocker: `./harness.sh run-smoke` and
`bash scripts/run_c1_baseline.sh` now use the active OpenAI benchmark provider
by default. They were rerun at 2026-07-12T01:21:05 UTC and
2026-07-12T01:21:17 UTC. Bring-up, offer parser validation, process-metric
validation, and EN/ID/ZH channel validation all pass before the provider probe.
The probe is blocked because both urllib and curl cannot resolve
`api.openai.com`.

Next useful work: **Restore network/API access for the configured OpenAI
benchmark model, then rerun `bash scripts/run_c1_baseline.sh`.**

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

BLOCKED: OpenAI benchmark provider probe failed before smoke/C1 transcript
creation. Current artifacts:

- `artifacts/results/benchmark_model_probe.json`
- `artifacts/results/smoke_c0_buy_sell_en_001.blocked.json`
- `artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json`

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T01:21:04+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T01:21:05+00:00` BLOCKED: OpenAI benchmark model probe failed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T01:21:05+00:00` BLOCKED: C0 smoke blocked on provider openai_benchmark; artifact=artifacts/results/smoke_c0_buy_sell_en_001.blocked.json; failed_command=bash scripts/run_smoke.sh
- `2026-07-12T01:21:05+00:00` ERROR: scripts/run_smoke.sh exited 2
- `2026-07-12T01:21:17+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T01:21:17+00:00` BLOCKED: OpenAI benchmark model probe failed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T01:21:17+00:00` BLOCKED: C1 ID baseline blocked on benchmark provider openai_benchmark; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh
- `2026-07-12T01:22:00+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 17 |
| Logs | 63 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
