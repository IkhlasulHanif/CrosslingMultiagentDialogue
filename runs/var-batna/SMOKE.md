# var-batna — smoke notes (seeds 1–5)

I read all 5 transcripts. Each alternative appears only in its own seat's prompt (`alt_leaked_by_other` is silent). Parsed prices (45, 40) match. Three seeds are infeasible (floor = max(40, seller_alt) ≥ cap = min(60, buyer_alt)): 56/47, 55/45 and 44/38. In all three the buyer walks away citing its outside option, and each scores `correct`. The two feasible seeds close inside [floor, cap].
Both sides argue with their alternatives openly ("I can get the same resource elsewhere for 47"). The leak metric only counts own-value statements, so these are not leaks. Fix made here: shared COMMON checks were being counted once per variant (`fixed:` and `batna:`), and they now run once per game.
