# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout using the explicitly allowed OpenAI smoke override.
It reached a deal in 2 turns with `offer_parse_rate=1.0`, but this is only
runner bring-up evidence, not Qwen3-1.7B research-matrix evidence.

Latest real C0 baseline attempt: `bash scripts/run_c0_baseline.sh` passed source
bring-up and parser/process validators, then blocked before any episode ran
because this sandbox cannot reach the local Qwen/vLLM chat-completions endpoint
at `http://127.0.0.1:8000/v1/chat/completions`
(`<urlopen error [Errno 1] Operation not permitted>`). The next Qwen/local C0
baseline command remains `bash scripts/run_c0_baseline.sh`.


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

BLOCKED: Commit/push skipped because unrelated settings/govsim_crosslingual files are already staged in the parent repository index; avoiding mixed benchmark commit. Scoped NegotiationArena changes remain in settings/negotiation_arena_crosslingual.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T11:38:27+00:00` OK: Harness scaffold check passed
- `2026-07-11T11:38:53+00:00` BLOCKED: Commit/push skipped because unrelated settings/govsim_crosslingual files are already staged in the parent repository index; avoiding mixed benchmark commit. Scoped NegotiationArena changes remain in settings/negotiation_arena_crosslingual.
- `2026-07-11T11:39:42+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260711_193657.txt
- `2026-07-11T11:39:42+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T11:39:43+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T11:39:44+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T11:39:53+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T11:39:53+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 1 |
| Result summaries | 6 |
| Logs | 18 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
