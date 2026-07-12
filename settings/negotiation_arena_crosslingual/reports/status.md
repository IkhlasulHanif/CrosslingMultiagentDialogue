# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user
request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and
ZH-ID. The old Qwen C0 runs remain useful historical capability evidence, but
new benchmark runs should be labeled as OpenAI `gpt-5.4-mini-2026-03-17` evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. For this setting, benchmark rules/private state may
remain in English; C0/C1/C2/C3 constrain only the agents' visible negotiation
messages and validate channel compliance from transcripts.

Output-channel instruction templates for EN, ID, and ZH are implemented in
`config/language_channels.json`. Channel-compliance metrics inspect visible

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

BLOCKED: C1 ID baseline blocked on benchmark provider openai_benchmark; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T00:42:03+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T00:42:03+00:00` BLOCKED: OpenAI benchmark model probe failed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T00:42:03+00:00` BLOCKED: C1 ID baseline blocked on benchmark provider openai_benchmark; failed_command=bash scripts/run_c1_baseline.sh
- `2026-07-12T00:42:40+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T00:42:40+00:00` BLOCKED: OpenAI benchmark model probe failed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T00:42:40+00:00` BLOCKED: C1 ID baseline blocked on benchmark provider openai_benchmark; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh
- `2026-07-12T00:42:40+00:00` OK: Output-channel templates and EN/ID/ZH compliance metrics validated; artifact=artifacts/results/language_channel_validation.json
- `2026-07-12T00:43:41+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 15 |
| Logs | 61 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
