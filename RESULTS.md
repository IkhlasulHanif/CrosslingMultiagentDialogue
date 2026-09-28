# grounded-arena · results so far

Status as of 2026-09-28: **Stage A S0–S7 complete**, S8 paused at 8/100, S9 has smoke games only, S10 and Stage B not started.
Model: K2 Horizon (`IFM/K2-Horizon-375B-A23B`) in both seats, temperature 1.0, top_p 0.95. All games are English–English, 100 games per step, on the upstream NegotiationArena buy-sell game.

**Metrics.** s = (v − p)/(v − c) is the buyer's share of the surplus: 0 means it paid its full value, 1 means it paid the seller's cost. Cap-collapse is the share of deals with s ≤ 0.1. Spread is IQR(s).
**Gate.** A step passes if cap-collapse ≤ 50%, IQR(s) ≥ 0.25, and (for games with a right or wrong answer) the correct rate is between 20% and 90%.

## Stage A verdicts

| step | variant | cap-collapse | IQR(s) | median s | correct | leak | gate |
|---|---|---|---|---|---|---|---|
| S1 | baseline (40/60) | 25% | 0.33 | 0.50 | – | 80% | **pass** |
| S2 | noleak | 47% | 0.50 | 0.25 | – | 15% | **pass** |
| S3 | zopa (random c, v; 31% impossible) | 28% | 0.70 | 0.47 | 92% | 85% | fail: correct > 90% |
| S4 | batna (outside options) | 23% | 0.57 | 0.50 | 97% | 49% | fail: correct > 90% |
| S5 | deadline (secret time pressure) | 29% | 0.40 | 0.50 | – | 83% | **pass** |
| S6 | multiissue (price + delivery + warranty) | 1% | 0.20 | 0.36 | – | 58% | fail: IQR < 0.25 |
| S7 | item (real Amazon product) | 37% | 0.46 | 0.21 | – | 62% | **pass** |
| S8 | quality (hidden condition) | – | – | – | – | – | paused, 8/100 |
| S9 | currency (USD / IDR market / IDR PPP) | – | – | – | – | – | smoke games only |
| S10 | grounded-v1 | – | – | – | – | – | not started |

## Findings

1. **No collapse with K2 at temperature 1.0.** Unlike x-arena, the plain 40/60 baseline already passes the gate. Prices land in two places: 33% of deals at the midpoint (50) and 23% at the buyer's maximum (60). Which one happens mostly depends on who names their own number first: the seller's disclosed cost pulls the price to the middle, and the buyer's stated maximum pulls it to the cap.
2. **Hiding values backfires.** "Never state your own value or budget" cut leaks from 80% to 15% but raised cap-collapse from 25% to 47% and lowered median s from 0.50 to 0.25. Without the disclosed cost as an anchor, sellers open high (often 100) and buyers concede up to their private maximum. The line was therefore not adopted as the default for S3 onward.
3. **Right-or-wrong games are too easy.** Random values (S3) and outside options (S4) give the widest spread (IQR 0.70 and 0.57), but agents take nearly every feasible deal and mostly walk away from impossible ones, so the correct rate goes above the 90% ceiling. The typical mistakes are sellers selling below their own cost at the buyer's cap (S3) and buyers paying more than their outside option (S4).
4. **Time pressure hurts whoever carries it.** With a pressured buyer, median s is 0.25; with a pressured seller it is 0.50, and those games close fastest. No pressured seat ever revealed its deadline.
5. **Multi-issue deals remove collapse but compress spread.** Delivery and warranty make up for a high price, so the buyer's points share stays in a narrow band (IQR 0.20). Integrative capture is 0.86. Only 8% of deals find the best joint package (fast delivery, no warranty); the most common deal gives the buyer everything (fast delivery and a 2-year warranty). This is also the most expensive variant, at about 39k tokens per game.
6. **Real products favour the seller.** A public price history lets sellers anchor on the historical high, and median s falls from 0.50 to 0.21.
7. **Early S8/S9 signals (smoke games only).** Hidden condition creates real persuasion: a defective item was sold as "like new" (the buyer walked away), and a genuinely new item failed to sell because the claim was not credible. The IDR arms parse correctly at 6–8-digit amounts.

## Not yet answered

Stage B (does the language each agent speaks change who wins?) has not run. Translations for id, ar, ja and es and the language-ID code are written and tested, but S10 must pass first.

## Operational notes

- **Cost.** $0: the IFM API is a free preview. The binding limit is **10M tokens per rolling 24 h** per key, plus an unpublished per-minute request guard (keep it at 8 calls/min or less).
- **Remaining work.** About 24–33M tokens, roughly 3–4 days at the cap.
- **Where things are.** Full details, histograms and transcripts are in `reports/results.html`, `STATE.md` (with handoff steps), `CASEBOOK.md`, `DEVIATIONS.md` and `runs/<run>/`, all on branch `grounded-arena`.
