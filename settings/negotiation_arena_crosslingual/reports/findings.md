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

Control definition: language means required interaction-output channel, not
translated benchmark rules. Rules/private state may remain in English; C0/C1/C2/C3
constrain visible negotiation messages and validate channel compliance from
transcripts.

Fresh pass result: pairwise resource-exchange runner added for EN-ID, EN-ZH,
and ZH-ID, and one EN-ID C2 resource-exchange episode completed with OpenAI
`gpt-5.4-mini-2026-03-17` benchmark evidence at seed 101.

- EN-ID C2 resource exchange agent_a-EN/agent_b-ID:
  `artifacts/transcripts/pair_en_id_c2_buyer_lx_seller_ly_resource_exchange_seed101.json`
  and
  `artifacts/results/pair_en_id_c2_buyer_lx_seller_ly_resource_exchange_seed101.metrics.json`.
  Deal reached after 2 visible messages. Final allocation was agent_a
  X=15/Y=15 and agent_b X=15/Y=15. Both agents satisfied the upstream
  ResourceGoal, so pairwise payoff asymmetry is EN minus ID = 0. Offer parse
  rate, deal rate, and assigned channel compliance are all 1.0. First-offer
  anchoring L1 distance is 0 because the accepted final allocation matched the
  first offer exactly.

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
- EN-ZH C2 buyer-EN/seller-ZH:
  `artifacts/transcripts/pair_en_zh_c2_buyer_lx_seller_ly_buy_sell_seed101.json`
  and
  `artifacts/results/pair_en_zh_c2_buyer_lx_seller_ly_buy_sell_seed101.metrics.json`.
  Deal reached at price 75. Payoffs: EN buyer 25, ZH seller 35. Pairwise
  payoff asymmetry is EN minus ZH = -10. Offer parse rate and deal rate are
  1.0, but assigned-channel compliance is only 0.50 because the EN-assigned
  buyer produced ZH visible messages. Final price moved 5 ZUP below the ZH
  seller's first offer.
- EN-ZH C2 buyer-ZH/seller-EN:
  `artifacts/transcripts/pair_en_zh_c2_buyer_ly_seller_lx_buy_sell_seed101.json`
  and
  `artifacts/results/pair_en_zh_c2_buyer_ly_seller_lx_buy_sell_seed101.metrics.json`.
  Deal reached at price 74. Payoffs: ZH buyer 26, EN seller 34. Pairwise
  payoff asymmetry is EN minus ZH = 8. Offer parse rate and deal rate are
  1.0, but assigned-channel compliance is 0.667 because the EN-assigned seller
  drifted into ZH after the opening message. Final price moved 6 ZUP below the
  EN seller's first offer.
- ZH-ID C2 buyer-ZH/seller-ID:
  `artifacts/transcripts/pair_zh_id_c2_buyer_lx_seller_ly_buy_sell_seed101.json`
  and
  `artifacts/results/pair_zh_id_c2_buyer_lx_seller_ly_buy_sell_seed101.metrics.json`.
  Deal reached at price 80. Payoffs: ZH buyer 20, ID seller 40. Pairwise
  payoff asymmetry is ZH minus ID = -20. Offer parse rate, deal rate, and
  assigned channel compliance are all 1.0. Final price exactly matched the ID
  seller's first offer.
- ZH-ID C2 buyer-ID/seller-ZH:
  `artifacts/transcripts/pair_zh_id_c2_buyer_ly_seller_lx_buy_sell_seed101.json`
  and
  `artifacts/results/pair_zh_id_c2_buyer_ly_seller_lx_buy_sell_seed101.metrics.json`.
  Deal reached at price 70. Payoffs: ID buyer 30, ZH seller 30. Pairwise
  payoff asymmetry is ZH minus ID = 0. Offer parse rate and deal rate are 1.0,
  but assigned-channel compliance is 0.50 because the ID-assigned buyer used ZH
  visible messages. Final price moved 10 ZUP below the ZH seller's first offer.
- EN-ID C3 free-choice:
  `artifacts/transcripts/pair_en_id_c3_buy_sell_seed101.json` and
  `artifacts/results/pair_en_id_c3_buy_sell_seed101.metrics.json`. Deal reached
  at price 50 after 3 visible messages. Payoffs: buyer 50, seller 10. Offer
  parse rate, deal rate, and free-choice channel compliance are all 1.0. The
  heuristic language classifier saw EN share 1.0, ID share 0.0, and off-pair
  share 0.0, so this run converged to English.
- EN-ZH C3 free-choice:
  `artifacts/transcripts/pair_en_zh_c3_buy_sell_seed101.json` and
  `artifacts/results/pair_en_zh_c3_buy_sell_seed101.metrics.json`. Deal reached
  at price 50 after 4 visible messages. Payoffs: buyer 50, seller 10. Offer
  parse rate, deal rate, and free-choice channel compliance are all 1.0. The
  heuristic language classifier saw ZH share 1.0, EN share 0.0, and off-pair
  share 0.0, so this run converged to Chinese rather than English.
- ZH-ID C3 free-choice:
  `artifacts/transcripts/pair_zh_id_c3_buy_sell_seed101.json` and
  `artifacts/results/pair_zh_id_c3_buy_sell_seed101.metrics.json`. Deal reached
  at price 60 after 2 visible messages. Payoffs: buyer 40, seller 20. Offer
  parse rate, deal rate, and free-choice channel compliance are all 1.0. The
  heuristic language classifier saw ZH share 1.0, ID share 0.0, EN share 0.0,
  and off-pair share 0.0, so this run converged to Chinese with no detected
  English leakage.

Current empirical story: EN-ID, EN-ZH, and ZH-ID C2 are counterbalanced for
buy/sell at seed 101, and C3 free-choice has now run for all active pairs. This
single seed does not support a stable language-channel payoff claim. The EN
minus ID payoff asymmetry is positive when EN is the buyer and ID is the seller,
then falls to zero when EN is the seller and ID is the buyer. The EN minus ZH
payoff asymmetry flips sign across the EN-ZH counterbalance (-10, then +8). The
ZH minus ID asymmetry is negative when ZH is the buyer and ID is the seller,
then falls to zero when ZH is the seller and ID is the buyer. C3 convergence is
EN for EN-ID, ZH for EN-ZH, and ZH for ZH-ID at seed 101. EN-ZH C2 and one
ZH-ID C2 run have poor assigned-channel compliance because visible dialogue
mostly converged to ZH. Treat these as early role-sensitive and
compliance-limited execution results until more seeds run.

The resource-exchange path is now executable for all active pairs via
`scripts/run_pairwise_resource_exchange.py`. Only the EN-ID C2
agent_a-EN/agent_b-ID row has been empirically run so far; do not treat
resource exchange as counterbalanced until the remaining EN-ID, EN-ZH, and
ZH-ID rows are executed.

Note on metrics: pairwise payoff asymmetry is intentionally unavailable for C3
because both roles are assigned bilingual free-choice channels such as EN-ID,
not unique one-language role labels. Use C3 primarily for H4 convergence and
off-pair leakage, not H1/H2 payoff attribution.

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
python3 scripts/validate_pairwise_channel_plan.py
python3 scripts/run_pairwise_resource_exchange.py --pair EN-ID --condition C2 --counterbalance buyer_ly_seller_lx --seed 101
python3 scripts/run_pairwise_resource_exchange.py --pair EN-ZH --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
python3 scripts/run_pairwise_resource_exchange.py --pair EN-ZH --condition C2 --counterbalance buyer_ly_seller_lx --seed 101
python3 scripts/run_pairwise_resource_exchange.py --pair ZH-ID --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
python3 scripts/run_pairwise_resource_exchange.py --pair ZH-ID --condition C2 --counterbalance buyer_ly_seller_lx --seed 101
```
