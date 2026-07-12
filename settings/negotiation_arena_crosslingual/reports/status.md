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

Fresh pass result: two EN-ID C2 buy/sell counterbalances and one EN-ZH C1
ZH-only buy/sell baseline completed with OpenAI benchmark execution at
2026-07-12T17:49-17:50 UTC. Artifacts:
`artifacts/transcripts/pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101.json`,
`artifacts/transcripts/pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101.json`,
and `artifacts/transcripts/pair_en_zh_c1_buy_sell_seed101.json`.

EN-ID C2 is now counterbalanced for buy/sell seed 101. Buyer-EN/seller-ID
ended at price 52 with EN minus ID payoff asymmetry 36; buyer-ID/seller-EN
ended at price 70 with EN minus ID payoff asymmetry 0. Deal rate,
offer-parse rate, and assigned channel compliance are 1.0 for both runs.

Next useful work: **Run the remaining EN-ZH and ZH-ID C2 buy/sell
counterbalances, then C3 free-choice runs.**

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

- `2026-07-12T17:49:26+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T17:49:35+00:00` OK: pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101 completed; transcript=artifacts/transcripts/pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101.json; metrics=artifacts/results/pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101.metrics.json; provider=openai_benchmark
- `2026-07-12T17:49:41+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T17:49:46+00:00` OK: pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101 completed; transcript=artifacts/transcripts/pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101.json; metrics=artifacts/results/pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101.metrics.json; provider=openai_benchmark
- `2026-07-12T17:50:21+00:00` OK: OpenAI benchmark model probe passed; artifact=artifacts/results/benchmark_model_probe.json
- `2026-07-12T17:50:24+00:00` OK: pair_en_zh_c1_buy_sell_seed101 completed; transcript=artifacts/transcripts/pair_en_zh_c1_buy_sell_seed101.json; metrics=artifacts/results/pair_en_zh_c1_buy_sell_seed101.metrics.json; provider=openai_benchmark
- `2026-07-12T17:51:59+00:00` OK: Pairwise EN-ID, EN-ZH, and ZH-ID channel-run plan validated; artifact=artifacts/results/pairwise_channel_plan_validation.json
- `2026-07-12T17:51:59+00:00` OK: Harness scaffold check passed
- `2026-07-12T17:54:04+00:00` OK: G2 capability floor check ok with active OpenAI benchmark buy/sell C0/C1 metric paths; artifact=artifacts/results/g2_capability_floor.json

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 8 |
| Result summaries | 26 |
| Logs | 75 |

## Open Questions

- EN-ZH and ZH-ID C2 buy/sell counterbalances still need to run before any
  cross-pair payoff claim.
- C3 free-choice convergence is still unrun.
- Pairwise resource-exchange runner is still missing.
