# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked only on
pending human review of 16 EN-ID translation units. This pass added a direct
translation-review gate artifact at 2026-07-11T18:29:48 UTC:
`artifacts/results/translation_review_validation.json`. It confirms the review
queue is structurally aligned with `config/prompt_translations.json`, but human
approval remains pending. The real C1 command artifact was refreshed at
2026-07-11T18:29:54 UTC, and the G2 gate summary was refreshed at
2026-07-11T18:29:54 UTC.

After human review clears, the C1 runner will select the explicit OpenAI
benchmark override (`openai_benchmark` / `gpt-4.1-mini`) and label resulting
artifacts as OpenAI benchmark evidence, not Qwen evidence.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix
evidence.

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

BLOCKED: Human approval is still required for 16 EN-ID translation units.
Artifact: `artifacts/results/translation_review_validation.json`. Fill
`config/translation_review.json` with `reviewer.completed=true`,
`reviewer.name`, `reviewer.reviewed_at`, and `reviewer_status=approved` for
every unit; then run `python3 scripts/validate_translation_review.py &&
bash scripts/run_c1_baseline.sh`.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T18:13:14+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T18:13:14+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-11T18:13:14+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T18:13:14+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T18:13:15+00:00` OK: Codex pass 3 completed
- `2026-07-11T18:28:16+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260712_022815.txt
- `2026-07-11T18:29:48+00:00` BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.
- `2026-07-11T18:29:48+00:00` OK: Harness scaffold check passed
- `2026-07-11T18:29:54+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T18:29:54+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 13 |
| Logs | 41 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
