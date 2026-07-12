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

Fresh pass result: pairwise resource-exchange runner added for EN-ID, EN-ZH,
and ZH-ID, and one EN-ID C2 resource-exchange episode completed with OpenAI

Next useful work: **Produce `reports/paper/main.tex` answering H1-H5 with artifact-backed claims**.

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
| Final report | missing `reports/paper/main.pdf` |

## Blockers / Errors

BLOCKED: Scoped commit created for pairwise resource_exchange runner and EN-ID C2 evidence, but push failed: fatal unable to access https://github.com/IkhlasulHanif/CrosslingMultiagentDialogue.git/ Recv failure Operation timed out

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T18:15:59+00:00` BLOCKED: Scoped commit created for pairwise resource_exchange runner and EN-ID C2 evidence, but push failed: fatal unable to access https://github.com/IkhlasulHanif/CrosslingMultiagentDialogue.git/ Recv failure Operation timed out
- `2026-07-12T18:16:35+00:00` OK: Retry push succeeded for local commit 4ffb92f6 containing pairwise resource_exchange runner and EN-ID C2 evidence
- `2026-07-12T18:17:10+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260713_021109.txt
- `2026-07-12T18:17:10+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T18:17:10+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T18:17:11+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T18:17:17+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-12T18:17:17+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 16 |
| Result summaries | 34 |
| Logs | 79 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
