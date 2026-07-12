# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17`
per user request on 2026-07-12, and active language pairs are EN-ID, EN-ZH,
and ZH-ID. New benchmark artifacts must be labeled as OpenAI evidence, not
Qwen evidence.

Final report result: `reports/paper/main.tex` and `reports/paper/main.pdf`
now exist. The paper answers H1-H5 directly from local artifacts as a
constrained null/role-sensitive seed-101 OpenAI result: no robust
counterbalanced higher-resource payoff premium is supported; C3 convergence is
EN for EN-ID and ZH for EN-ZH/ZH-ID; ZH-ID shows no detected English leakage.
The paper records that EN-ZH C2 and one ZH-ID C2 row are compliance-limited,
and that resource exchange is executable but not yet counterbalanced.

Next useful work: **No unchecked checklist item found**.

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
| Final report | `reports/paper/main.pdf` exists |

## Blockers / Errors

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T18:20:53+00:00` OK: Final report produced from artifact-backed OpenAI benchmark evidence; tex=reports/paper/main.tex; pdf=reports/paper/main.pdf; note=pdftotext and pypdf unavailable for text-extraction sanity check
- `2026-07-12T18:21:18+00:00` OK: Harness scaffold check passed
- `2026-07-12T18:22:12+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260713_021818.txt
- `2026-07-12T18:22:12+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T18:22:12+00:00` OK: NegotiationArena checkout found; artifact=artifacts/results/bringup_check.json
- `2026-07-12T18:22:13+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T18:22:16+00:00` OK: C0 buy_sell smoke completed; transcript=artifacts/transcripts/smoke_c0_buy_sell_en_001.json; metrics=artifacts/results/smoke_c0_buy_sell_en_001.metrics.json
- `2026-07-12T18:22:16+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 16 |
| Result summaries | 34 |
| Logs | 80 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
