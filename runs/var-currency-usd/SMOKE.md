# var-currency-usd — smoke notes (seeds 1–5)

I read all 5 transcripts. They share seeds and products with var-item seeds 1–5 (same config). Only the public product line and each seat's own number reach each prompt, and parsed prices (147, 2021, 43, 39, 310) match. Four of five land exactly on the buyer's cap after the buyer names it ("My maximum budget for this saw is $43"), and the leak checks catch those.
One detector edge case: on seed 4 `buyer_states_max` fires on "39 USD it is — that works within my budget", where 39 is both the price and v. The regex cannot tell a price quote from a cap statement when the two coincide (§5 limitation, noted in DEVIATIONS).
