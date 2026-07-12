Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17`
per user request on 2026-07-12, and active language pairs are EN-ID, EN-ZH,
and ZH-ID. New benchmark artifacts must be labeled as OpenAI evidence, not
Qwen evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. Rules/private state may remain in English; C0/C1/C2/C3
constrain visible negotiation messages and validate channel compliance from
transcripts.

Fresh pass result: three OpenAI benchmark buy/sell runs completed.

- EN-ID C2 buyer-EN/seller-ID:
  `artifacts/transcripts/pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101.json`
  and `artifacts/results/pair_en_id_c2_buyer_lx_seller_ly_buy_sell_seed101.metrics.json`.
  Deal reached at price 52. Payoffs: EN buyer 48, ID seller 12. Pairwise
  payoff asymmetry is EN minus ID = 36. Offer parse rate, deal rate, and
  assigned channel compliance are all 1.0.
- EN-ID C2 buyer-ID/seller-EN:
  `artifacts/transcripts/pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101.json`
  and `artifacts/results/pair_en_id_c2_buyer_ly_seller_lx_buy_sell_seed101.metrics.json`.
  Deal reached at price 70. Payoffs: ID buyer 30, EN seller 30. Pairwise
  payoff asymmetry is EN minus ID = 0. Offer parse rate, deal rate, and
  assigned channel compliance are all 1.0.
- EN-ZH C1 ZH-only:
  `artifacts/transcripts/pair_en_zh_c1_buy_sell_seed101.json` and
  `artifacts/results/pair_en_zh_c1_buy_sell_seed101.metrics.json`. Deal reached
  at price 80. Offer parse rate, deal rate, and assigned channel compliance are
  all 1.0, with ZH share 1.0 and off-pair share 0.0.

Current empirical story: EN-ID C2 is now counterbalanced for buy/sell, but this
single seed does not support a language-channel payoff claim. The EN minus ID
payoff asymmetry is positive when EN is the buyer and ID is the seller, then
falls to zero when EN is the seller and ID is the buyer. Treat this as early
role-sensitive evidence until more seeds and the remaining pairs run.

Completed active OpenAI baseline artifacts include C0 EN buy/sell at
`artifacts/transcripts/baseline_c0_buy_sell_en_seed001.openai_benchmark.json`
with metrics at
`artifacts/results/baseline_c0_buy_sell_en_seed001.openai_benchmark.metrics.json`,
and C1 ID buy/sell at
`artifacts/transcripts/baseline_c1_buy_sell_id_seed001.json` with metrics at
`artifacts/results/baseline_c1_buy_sell_id_seed001.metrics.json`.

Pairwise channel-run planning is in place for EN-ID, EN-ZH, and ZH-ID at
`config/pairwise_channel_plan.json`. It covers C0, C1, both C2 role-language
counterbalances, and C3 free-choice rows for each active pair. Validator
artifact: `artifacts/results/pairwise_channel_plan_validation.json`.

Source bring-up remains resolved. `external/NegotiationArena` is a local
checkout of `https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. License evidence is recorded in
`licenses.md` and `artifacts/results/bringup_check.json`.

Next exact commands:

```bash
python3 scripts/run_pairwise_buy_sell.py --pair EN-ZH --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
python3 scripts/run_pairwise_buy_sell.py --pair EN-ZH --condition C2 --counterbalance buyer_ly_seller_lx --seed 101
python3 scripts/run_pairwise_buy_sell.py --pair ZH-ID --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
python3 scripts/run_pairwise_buy_sell.py --pair ZH-ID --condition C2 --counterbalance buyer_ly_seller_lx --seed 101
```
