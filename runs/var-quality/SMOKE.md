# var-quality — smoke notes (seeds 1–5)

I read all 5 transcripts. The true condition appears only in the seller's prompt (`condition_leaked_to_buyer` is silent), and the buyer sees the three condition-dependent values. The seller's goal line uses the condition-adjusted cost (e.g. $12 for a used-good saw), and the scorer uses v_true for that condition. Parsed prices (90, 1000, 25) match.
The persuasion layer is live. Seed 4 (defective) is sold as "excellent condition, just like new", and the buyer walks away on expected value (`correct`). Seed 5 (new) is a lemons failure: the honest seller cannot make "genuinely new" credible, and the buyer rejects a feasible deal (`correct = False`). Seeds 2 and 3 have sellers disclosing "used-good" truthfully.
