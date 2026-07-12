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

Fresh pass result: seven OpenAI benchmark buy/sell runs completed.


Next useful work: **Run C3 free-choice EN-ID, EN-ZH, and ZH-ID**.

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

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T18:00:54+00:00` OK: Codex pass 2 completed
- `2026-07-12T18:01:54+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260713_020154.txt
- `2026-07-12T18:02:25+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T18:02:28+00:00` OK: pair_zh_id_c2_buyer_lx_seller_ly_buy_sell_seed101 completed; transcript=artifacts/transcripts/pair_zh_id_c2_buyer_lx_seller_ly_buy_sell_seed101.json; metrics=artifacts/results/pair_zh_id_c2_buyer_lx_seller_ly_buy_sell_seed101.metrics.json; provider=openai_benchmark
- `2026-07-12T18:02:33+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T18:02:41+00:00` OK: pair_zh_id_c2_buyer_ly_seller_lx_buy_sell_seed101 completed; transcript=artifacts/transcripts/pair_zh_id_c2_buyer_ly_seller_lx_buy_sell_seed101.json; metrics=artifacts/results/pair_zh_id_c2_buyer_ly_seller_lx_buy_sell_seed101.metrics.json; provider=openai_benchmark
- `2026-07-12T18:03:01+00:00` OK: ZH-ID C2 buy_sell counterbalances documented as OpenAI benchmark evidence; buyer-ZH/seller-ID asymmetry=-20 compliance=1.0; buyer-ID/seller-ZH asymmetry=0 compliance=0.50; next_command=python3 scripts/run_pairwise_buy_sell.py --pair EN-ID --condition C3 --seed 101
- `2026-07-12T18:04:14+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 12 |
| Result summaries | 30 |
| Logs | 77 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
