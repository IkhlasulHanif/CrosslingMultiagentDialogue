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

BLOCKED: C0 baseline blocked on local Qwen endpoint; artifact=artifacts/results/baseline_c0_buy_sell_en_seed001.blocked.json; failed_command=bash scripts/run_c0_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T12:16:05+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T12:16:07+00:00` OK: Codex pass 4 completed
- `2026-07-11T12:31:07+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260711_203107.txt
- `2026-07-11T12:31:53+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T12:31:54+00:00` BLOCKED: Local Qwen endpoint probe failed; artifact=artifacts/results/model_endpoint_probe.json; failed_command=python3 scripts/local_model_adapter.py --live-probe
- `2026-07-11T12:31:54+00:00` BLOCKED: C0 baseline blocked on local Qwen endpoint; artifact=artifacts/results/baseline_c0_buy_sell_en_seed001.blocked.json; failed_command=bash scripts/run_c0_baseline.sh
- `2026-07-11T12:32:01+00:00` OK: Harness scaffold check passed
- `2026-07-11T12:32:30+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 1 |
| Result summaries | 6 |
| Logs | 21 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
