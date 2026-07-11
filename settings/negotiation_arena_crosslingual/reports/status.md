# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked on pending
human review of 16 EN-ID translation units.

This pass added dedicated OpenAI benchmark override wrappers:
`bash scripts/run_c0_openai_baseline.sh` and
`bash scripts/run_c0_openai_resource_exchange_baseline.sh`. They reuse the C0
baseline runners with `NEGOTIATION_BENCHMARK_PROVIDER=openai_benchmark` and
write separate `.openai_benchmark.*` transcript/metrics paths so they do not
overwrite Qwen evidence. A real C0 OpenAI buy/sell baseline attempt was made at
2026-07-11T19:09:31 UTC. No transcript was produced because the provider probe
failed before the episode: `api.openai.com` could not be resolved by urllib or

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

BLOCKED: Scoped commit/push blocked by sandbox filesystem permissions: git could not create parent repo .git/index.lock; failed_command=git add <negotiation_arena_crosslingual scoped files>

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T19:10:43+00:00` OK: Harness scaffold check passed
- `2026-07-11T19:11:35+00:00` BLOCKED: Scoped commit/push blocked by sandbox filesystem permissions: git could not create parent repo .git/index.lock; failed_command=git add <negotiation_arena_crosslingual scoped files>
- `2026-07-11T19:12:07+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_030637.txt
- `2026-07-11T19:12:07+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T19:12:07+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T19:12:08+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T19:12:14+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T19:12:14+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 14 |
| Logs | 43 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
