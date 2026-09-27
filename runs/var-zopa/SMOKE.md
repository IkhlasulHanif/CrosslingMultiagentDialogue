# var-zopa — smoke notes (seeds 1–5)

I read all 5 transcripts. Each seat sees only its own sampled number (the seller's cost line, e.g. 34, and the buyer's cap, e.g. 32). Parsed prices (60, 50, 50) match the accepted proposals. Seed 3 is infeasible (v 32 < c 34): the buyer rejects at 34 and it scores `correct` (walked away). Seed 1 is feasible (56 < 71) but ends in a REJECT after the seller holds at 85, and it scores `correct = False`. Both are the intended right-or-wrong verdicts.
`buyer_states_max` fires on seeds 1 and 3 ("I can offer up to 71", "My maximum is 32") and `seller_states_cost` on seeds 2 and 3, all true hits. `deal_when_impossible` does not fire.
