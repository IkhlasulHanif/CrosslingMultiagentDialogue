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

BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T18:50:01+00:00` BLOCKED: Translation review validation blocked; artifact=artifacts/results/translation_review_validation.json; pending_units=16; next_command=Fill config/translation_review.json with reviewer.completed=true, reviewer.name, reviewer.reviewed_at, and reviewer_status=approved for every unit; then run python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh.
- `2026-07-11T18:50:01+00:00` OK: Harness scaffold check passed
- `2026-07-11T18:51:27+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_024657.txt
- `2026-07-11T18:51:27+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T18:51:28+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-11T18:51:29+00:00` OK: OpenAI smoke model probe passed; artifact=artifacts/results/smoke_model_probe.json
- `2026-07-11T18:51:35+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-11T18:51:35+00:00` OK: scripts/run_smoke.sh exited 0

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
