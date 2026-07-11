# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. C1 ID and G2 remain blocked only on
pending human review of 16 EN-ID translation units. This pass added
`python3 scripts/generate_translation_review_packet.py`, which regenerates the
human review packet from `config/prompt_translations.json` and
`config/translation_review.json`. The latest packet artifact is
`artifacts/results/translation_review_packet.json`, refreshed at
2026-07-11T18:49:15 UTC, and records 16 pending units. The translation
validator artifact was refreshed at 2026-07-11T18:50:01 UTC, the real C1
command artifact at 2026-07-11T18:48:50 UTC, and the G2 gate summary at
2026-07-11T18:48:54 UTC. After human review clears, the runner will select the
explicit OpenAI benchmark override (`openai_benchmark` / `gpt-4.1-mini`) and
label resulting artifacts as OpenAI benchmark evidence, not Qwen evidence.

Next useful work: **Fill `config/translation_review.json` from
`docs/id_translation_review.md`, then run
`python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh`.**

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

BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T18:48:45+00:00` BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.
- `2026-07-11T18:48:49+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T18:48:50+00:00` BLOCKED: C1 ID baseline blocked on pending human translation review; artifact=artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json; failed_command=bash scripts/run_c1_baseline.sh; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T18:48:54+00:00` BLOCKED: G2 capability floor check blocked; artifact=artifacts/results/g2_capability_floor.json; next_command=bash scripts/run_c1_baseline.sh
- `2026-07-11T18:48:54+00:00` OK: Harness scaffold check passed
- `2026-07-11T18:49:15+00:00` BLOCKED: Generated EN-ID translation review packet; packet=docs/id_translation_review.md; artifact=artifacts/results/translation_review_packet.json; pending_units=16
- `2026-07-11T18:50:01+00:00` BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.
- `2026-07-11T18:50:01+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 14 |
| Logs | 42 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
