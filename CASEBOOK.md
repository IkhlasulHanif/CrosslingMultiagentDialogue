# CASEBOOK

The 3 most extreme transcripts per step (visible exchange only; full transcripts in `runs/<run>/transcripts/`).

## s0-smoke

### s0-smoke-0003 — lowest s = 0.00

params `{"c": 40, "v": 60}` · end **accept** · price **60** · s 0.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 100}]: Hello BLUE, I have one unit of resource X available. It cost me 40 ZUP to produce. I am offering it at 100 ZUP as my opening price — open to reasonable offers.
>
> **T2 buyer** PROPOSAL [{"ZUP": 60}]: Thanks for the offer. I'm prepared to pay up to 60 ZUP for X — that's my ceiling given my budget constraints. Let me know if that works for you.
>
> **T3 seller** ACCEPT: Thank you, BLUE. 60 ZUP is acceptable to me — it covers my production cost with a fair margin. Deal accepted: I give you 1 unit of X, you give me 60 ZUP.

**Note.** The x-arena collapse in miniature: the buyer's first counter names its own ceiling ("up to 60 ... my ceiling") and the seller accepts at exactly v. The price equals the buyer's stated budget, so the leak alone explains s = 0.

### s0-smoke-0004 — highest s = 0.75

params `{"c": 40, "v": 60}` · end **accept** · price **45** · s 0.75 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 45}]: Offering my one X for 45 ZUP, which covers the production cost of 40 ZUP and gives a small margin.
>
> **T2 buyer** ACCEPT: Deal accepted. 45 ZUP is within my budget of 60 ZUP. Transferring 45 ZUP for the one X.

**Note.** The opposite pole: the seller opens at cost + 5 and discloses its cost, and the buyer accepts immediately. With temperature 1.0 the seller's opening anchor varies (45 to 100 ZUP across the 5 smoke games), and that alone creates spread.

### s0-smoke-0001 — longest game (4 turns)

params `{"c": 40, "v": 60}` · end **accept** · price **55** · s 0.25 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: I have one object X to sell. It cost me 40 ZUP to produce. I am asking 60 ZUP. Is that acceptable?
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: I understand your cost is 40 ZUP and you're asking 60. I'd like to counter with 50 ZUP. That still gives you a solid 10 ZUP profit. Would that work?
>
> **T3 seller** PROPOSAL [{"ZUP": 55}]: Thank you for your counter. I appreciate the offer of 50 ZUP, but I can meet you halfway at 55 ZUP. That still gives you a good deal compared to my cost of 40 ZUP. What do you think?
>
> **T4 buyer** ACCEPT: 55 ZUP sounds fair. You make a good profit over your cost, and I get the object for less than my maximum. Deal!

**Note.** A textbook split-the-difference: 60 → 50 → 55, accepted. Both sides reference the seller's disclosed cost (40) when framing their offers, and the buyer never states its own max.

## var-baseline

### var-baseline-0002 — lowest s = 0.00

params `{"c": 40, "v": 60}` · end **accept** · price **60** · s 0.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: Hello BLUE! I have one unit of X available for sale. Given the production cost of 40 ZUP, I'm offering it to you for 60 ZUP. Let me know what you think!
>
> **T2 buyer** ACCEPT: Thank you, RED! I accept your offer of 1 X for 60 ZUP. Looking forward to completing this trade.

**Note.** The collapse pattern in two turns: the seller discloses its cost, asks exactly the buyer's cap (60), and the buyer accepts at once. The buyer keeps none of the surplus (s = 0) without ever mentioning its own maximum.

### var-baseline-0100 — highest s = 0.85

params `{"c": 40, "v": 60}` · end **accept** · price **43** · s 0.85 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 45}]: Hello BLUE. I have one unit of X available. It cost 40 ZUP to produce, so I am asking 45 ZUP for it. Are you able to meet that price, or would you like to counter?
>
> **T2 buyer** PROPOSAL [{"ZUP": 42}]: I am willing to meet you at 42 ZUP for the X. Please let me know if this works for you.
>
> **T3 seller** PROPOSAL [{"ZUP": 44}]: Thanks for the counter. I can meet you halfway between my ask and yours at 44 ZUP. That still reflects the value and cost of producing X. Does that work?
>
> **T4 buyer** PROPOSAL [{"ZUP": 43}]: I propose 43 ZUP for the X, which is a fair middle ground between our offers. Please let me know if this works for you.
>
> **T5 seller** ACCEPT: Agreed. 43 ZUP is fair. I accept the trade: I give you X and you give me 43 ZUP. Thank you for the deal.

**Note.** The most buyer-favourable game: the seller opens at cost + 5 after disclosing cost 40, and both sides then shuffle in 1-ZUP steps to 43. Because the seller's first ask anchors so low, the buyer captures 85% of the surplus.

### var-baseline-0037 — longest game (7 turns)

params `{"c": 40, "v": 60}` · end **accept** · price **53** · s 0.35 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: Hello BLUE. I have one unit of X available for sale. It cost me 40 ZUP to produce. I'm asking 60 ZUP for it. Happy to discuss if you have a different offer in mind.
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: Hello RED, I see you're asking 60 ZUP. I can offer 50 ZUP for the object. Let me know if that works for you.
>
> **T3 seller** PROPOSAL [{"ZUP": 55}]: Thanks for the offer BLUE. 50 ZUP is close, but I was hoping for a bit more given my production costs. Would 55 ZUP work for you? That's a fair middle ground between your offer and my asking price.
>
> **T4 buyer** PROPOSAL [{"ZUP": 52}]: RED, I appreciate your counter. How about we meet at 52 ZUP? That's a small step from your 55. Let me know.
>
> **T5 seller** PROPOSAL [{"ZUP": 54}]: I can move a bit closer BLUE. How about 54 ZUP? That's just 2 ZUP from your offer and gets us very close to a deal. I think this is fair for both of us.
>
> **T6 buyer** PROPOSAL [{"ZUP": 53}]: RED, 54 is close, but let's split the difference at 53. I think that's a fair final offer from my side.
>
> **T7 seller** ACCEPT: Deal! 53 ZUP works for me BLUE. We have an agreement. I'll transfer the X to you and you send 53 ZUP. Pleasure doing business with you.

**Note.** The longest game (7 turns) is pure concession-trading from a 60 / 50 anchor pair down to 53 by alternating 1–3 ZUP steps. It shows temperature-1.0 dialogue producing interior prices rather than the cap.

## var-noleak

### var-noleak-0001 — lowest s = 0.00

params `{"c": 40, "v": 60}` · end **accept** · price **60** · s 0.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 100}]: I propose to sell my X for 100 ZUP.
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: Thank you for your offer. 100 ZUP is more than I'm prepared to pay for this object. I'd be willing to offer 50 ZUP instead. Would that work for you?
>
> **T3 seller** PROPOSAL [{"ZUP": 75}]: I appreciate your offer, but 50 ZUP is too low. I can do 75 ZUP. Is that acceptable?
>
> **T4 buyer** PROPOSAL [{"ZUP": 60}]: I understand, but 75 ZUP is still more than I'm willing to pay. My final offer is 60 ZUP, which is the maximum value I place on this object. Would you accept 60 ZUP?
>
> **T5 seller** ACCEPT: I accept your offer of 60 ZUP. Let's complete the trade.

**Note.** The new failure mode: the silent seller anchors at 100, walks down 100 → 75, and the buyer's "final offer" is its exact private cap (60), which the seller takes. The line stopped the seller leaking, but the buyer still named its maximum in all but words.

### var-noleak-0033 — highest s = 0.90

params `{"c": 40, "v": 60}` · end **accept** · price **42** · s 0.90 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 45}]: I propose to sell my X for 45 ZUP.
>
> **T2 buyer** PROPOSAL [{"ZUP": 35}]: I counter your offer of 45 ZUP with 35 ZUP for X. What do you say?
>
> **T3 seller** PROPOSAL [{"ZUP": 42}]: I appreciate your counter, but 35 ZUP is too low. I can meet you at 42 ZUP.
>
> **T4 buyer** ACCEPT: Deal! I accept your offer of 42 ZUP for X. Thank you for the trade.

**Note.** The best buyer outcome: the seller opens low (45) without explanation, the buyer counters 35, and they settle at 42. With no cost disclosed, the buyer's aggressive counter is the only anchor, and it works.

### var-noleak-0034 — longest game (7 turns)

params `{"c": 40, "v": 60}` · end **accept** · price **60** · s 0.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 100}]: I have one unit of X available. I propose selling it for 100 ZUP.
>
> **T2 buyer** PROPOSAL [{"ZUP": 60}]: I can offer 60 ZUP for the unit of X.
>
> **T3 seller** PROPOSAL [{"ZUP": 80}]: Thank you for your offer of 60 ZUP. I believe the object is worth more than that. I can sell it to you for 80 ZUP instead.
>
> **T4 buyer** PROPOSAL [{"ZUP": 60}]: I appreciate the offer, but 80 ZUP is beyond what I can manage. I can still offer 60 ZUP for the unit of X.
>
> **T5 seller** PROPOSAL [{"ZUP": 70}]: I understand your budget constraints. Let's meet in the middle at 70 ZUP. This is my best offer given the value of the object.
>
> **T6 buyer** PROPOSAL [{"ZUP": 60}]: 70 ZUP is still more than I can afford. My final offer is 60 ZUP. If that doesn't work, we may not reach an agreement.
>
> **T7 seller** ACCEPT: I accept your offer of 60 ZUP. The trade is agreed.

**Note.** Stonewalling at the cap: the buyer offers exactly 60 on turns 2, 4 and 6 while the seller comes down 100 → 80 → 70, then accepts 60. Repeating the maximum is not flagged as a leak because the buyer never calls 60 its budget, yet it lands the price at s = 0.

## var-zopa

### var-zopa-0008 — lowest s = 0.00

params `{"c": 58, "v": 69}` · end **accept** · price **69** · s 0.00 · correct True

> **T1 seller** PROPOSAL [{"ZUP": 70}]: Hello BLUE, I have one object X available for sale. It cost me 58 ZUP to produce, so I'm looking to sell it for a fair price. I propose 70 ZUP for the object. Let me know if that works for you or if you'd like to discuss further.
>
> **T2 buyer** PROPOSAL [{"ZUP": 69}]: Hello RED, I see you are selling X for 70 ZUP. I am willing to pay up to 69 ZUP for it. Let's settle at 69 ZUP if that works for you.
>
> **T3 seller** ACCEPT: Thank you BLUE, 69 ZUP works for me. I appreciate the deal and will proceed with the trade.

**Note.** Thin surplus (58 → 69), and the buyer names its cap in its first counter ("willing to pay up to 69"). The seller takes it, leaving the buyer nothing. With randomized values the cap-naming habit still decides where the price lands.

### var-zopa-0038 — highest s = 1.00

params `{"c": 36, "v": 74}` · end **accept** · price **36** · s 1.00 · correct True

> **T1 seller** PROPOSAL [{"ZUP": 40}]: Hello Player BLUE, I'm selling my object X. It cost me 36 ZUP to produce, so I'm asking for 40 ZUP. Let me know if that works or if you'd like to counter.
>
> **T2 buyer** PROPOSAL [{"ZUP": 30}]: Hi, I'd like to counter with 30 ZUP. Let me know if that works.
>
> **T3 seller** PROPOSAL [{"ZUP": 38}]: Thanks for the counter. 30 ZUP is below my cost, but I can meet you at 38 ZUP. That's a fair price considering my expenses. Let me know if that works.
>
> **T4 buyer** PROPOSAL [{"ZUP": 34}]: I appreciate the counter, but 38 is still a bit high for me. Can we meet at 34 ZUP? That's a fair deal for both of us.
>
> **T5 seller** PROPOSAL [{"ZUP": 36}]: I understand your budget, but 34 ZUP is below what I spent to make this object. I can offer it at exactly my cost: 36 ZUP. That's the lowest I can go without losing money. Let me know if that works.
>
> **T6 buyer** ACCEPT: Great, I'll take it at 36 ZUP. Thanks!

**Note.** The mirror image: the seller discloses cost 36 and then concedes step by step (40 → 38 → 36) to exactly its cost, handing the buyer the whole surplus. The buyer never says its value is 74.

### var-zopa-0001 — wrong action for private info

params `{"c": 56, "v": 71}` · end **reject** · price **None** · s n/a · correct False

> **T1 seller** PROPOSAL [{"ZUP": 100}]: I have one unit of resource X available for purchase. Given its production costs, I value it at 100 ZUP. Are you interested in buying it at this price?
>
> **T2 buyer** PROPOSAL [{"ZUP": 71}]: I can offer up to 71 ZUP for the unit of X. Would you consider this price?
>
> **T3 seller** PROPOSAL [{"ZUP": 85}]: I appreciate your offer of 71 ZUP, but given my production costs, I cannot go that low. Would you consider 85 ZUP instead? That's a fair middle ground between our two positions.
>
> **T4 buyer** REJECT: I cannot meet the price of 85 ZUP as it exceeds my limit of 71 ZUP. I reject the trade.

**Note.** A feasible game (c 56, v 71) lost to anchoring: the seller opens at 100, holds at 85, and the buyer walks at its stated 71. It is the only feasible-game error (68 of 69 correct); every other error is the reverse, sellers selling below cost.

## var-batna

### var-batna-0089 — lowest s = -2.33

params `{"c": 40, "v": 60, "seller_alt": 37, "buyer_alt": 43}` · end **accept** · price **50** · s -2.33 · correct False

> **T1 seller** PROPOSAL [{"ZUP": 60}]: I have a single unit of X available. It cost 40 ZUP to produce and there is outside interest in it, so I am looking for a strong offer. Let's start at 60 ZUP for the unit.
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: I appreciate the offer, but I can only justify 50 ZUP given the market and my alternatives. That still gives you a solid return over your cost.
>
> **T3 seller** ACCEPT: 50 ZUP is a fair and solid price. Deal accepted.

**Note.** The worst buyer error in the run: holding a 43-ZUP outside option, the buyer offers 50 "given my alternatives" and the seller snaps it up. The buyer pays 7 more than walking away would cost, so s = −2.33.

### var-batna-0095 — highest s = 1.00

params `{"c": 40, "v": 60, "seller_alt": 41, "buyer_alt": 42}` · end **accept** · price **41** · s 1.00 · correct True

> **T1 seller** PROPOSAL [{"ZUP": 41}]: I have one X available. My production cost is 40 ZUP, and I already have an offer of 41 ZUP from another buyer. I propose selling X to you for 41 ZUP. Are you interested?
>
> **T2 buyer** ACCEPT: I accept your offer to sell X for 41 ZUP.

**Note.** Near-degenerate zone (floor 41, cap 42): the seller discloses its 41 alternative and asks exactly 41, and the buyer accepts at once. Disclosing the alternative honestly hands the buyer the whole (1-ZUP) surplus.

### var-batna-0023 — wrong action for private info

params `{"c": 40, "v": 60, "seller_alt": 55, "buyer_alt": 54}` · end **accept** · price **55** · s n/a · correct False

> **T1 seller** PROPOSAL [{"ZUP": 60}]: Hello, I have a resource X that costs me 40 ZUP to produce. Another buyer is offering 55 ZUP. I'm asking 60 ZUP. Are you interested?
>
> **T2 buyer** PROPOSAL [{"ZUP": 55}]: Thank you for your offer. I have another source for X at 54 ZUP, so I'm interested in matching your other buyer’s price of 55 ZUP and completing this trade promptly.
>
> **T3 seller** ACCEPT: I accept your offer of 55 ZUP. The trade is completed.

**Note.** No-deal zone (seller_alt 55 > buyer_alt 54), yet the buyer offers to "match your other buyer's price of 55" while holding a 54 alternative. The seller's disclosed alternative became the buyer's price anchor, and the buyer overpaid its own BATNA by 1.

## var-deadline

### var-deadline-0006 — lowest s = 0.00

params `{"c": 40, "v": 60, "pressured": "seller"}` · end **accept** · price **60** · s 0.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: I have one X available. It cost me 40 ZUP to produce. I am offering it for 60 ZUP. If you can meet me near there, we can close immediately and avoid wasting rounds.
>
> **T2 buyer** ACCEPT: I accept your offer of 60 ZUP for X. Let's close the deal.

**Note.** A pressured seller opens at the buyer's cap to "close immediately and avoid wasting rounds", and the unpressured buyer accepts at once. Here the pressure produced speed, not concessions, and the buyer still paid its full 60.

### var-deadline-0051 — highest s = 1.00

params `{"c": 40, "v": 60, "pressured": "seller"}` · end **accept** · price **40** · s 1.00 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 40}]: I’m ready to sell the single unit of X for 40 ZUP. Let me know if you want to trade or counter.
>
> **T2 buyer** ACCEPT: Thank you, I accept your offer of 40 ZUP for the single unit of X.

**Note.** The opposite reading of the same pressure: this pressured seller opens at exactly its cost (40) and the buyer accepts in one round, taking the entire surplus. The two seeds together show the variance the deadline adds.

### var-deadline-0034 — longest game (6 turns)

params `{"c": 40, "v": 60, "pressured": "buyer"}` · end **accept** · price **55** · s 0.25 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: Greetings, Player BLUE. I have one unit of resource X available for sale. It cost me 40 ZUP to produce, and I'm asking 60 ZUP for it. Let me know if you'd like to counter-offer.
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: Thank you for the offer, Player RED. I appreciate the transparency about your production cost. While I understand your asking price of 60 ZUP, I'd like to propose 50 ZUP instead. This still gives you a solid 10 ZUP profit above your cost, while allowing me to stay within a comfortable budget. Would you be willing to accept this counter-offer?
>
> **T3 seller** PROPOSAL [{"ZUP": 55}]: Thank you for the counter, Player BLUE. I appreciate that 50 ZUP is within your comfortable budget. How about we meet in the middle at 55 ZUP? That's a 15 ZUP profit for me and still 5 ZUP below my original asking price. Fair?
>
> **T4 buyer** PROPOSAL [{"ZUP": 52}]: I appreciate you coming down to 55, Player RED. Let me offer 52 ZUP as a final compromise. This gives you a solid 12 ZUP profit above your production cost, which I think is fair. It also allows me to stay well within my budget. If that works for you, we have a deal. Otherwise, I'm prepared to meet you at 55 if needed.
>
> **T5 seller** PROPOSAL [{"ZUP": 55}]: Player BLUE, I appreciate the 52 ZUP offer and the spirit of compromise. However, since you mentioned you're prepared to meet at 55, I'll hold firm at my last offer of 55 ZUP. This gives me a fair 15 ZUP profit, and you've indicated this works within your budget. Shall we shake on it at 55?
>
> **T6 buyer** ACCEPT: You have a deal, Player RED. 55 ZUP for the resource X is acceptable. Thank you for your willingness to negotiate, and I appreciate you coming down from your original asking price of 60. Let's finalize this trade.

**Note.** The longest game, with a pressured buyer: it concedes 50 → 52 and then accepts the seller's 55 in round 3. The seller misreads the buyer's words ("you mentioned you're prepared to meet at 55") and holds, and the time-pressed buyer gives in rather than spend a 4th round.

## var-multiissue

### var-multiissue-0046 — lowest s = 0.06

params `{"c": 40, "v": 60, "issues": ["price", "delivery", "warranty"]}` · end **accept** · price **58** · s 0.06 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: BLUE, I have the one unit of X available. I'm offering it at 60 ZUP with slow delivery and no warranty. I'm open to discussing the price, but I'd need a meaningfully higher offer to change the delivery speed or add a warranty.
>
> **T2 buyer** PROPOSAL [{"ZUP": 50}]: RED, your 60 / slow / none nets me nothing on value, so I can't take it as-is. Since faster delivery or a warranty would require you to name a higher price (above my 60 cap), the only thing we can actually move is the price. I'm offering 50 ZUP for the unit at slow delivery, no warranty — a real discount for you while still a full-price-ish sale. If 50 is below your floor, tell me the lowest you'll go and we can close.
>
> **T3 seller** PROPOSAL [{"ZUP": 58}]: BLUE, 50 is too low for me to clear my costs and the terms we're discussing. You've indicated 60 is your ceiling and that you still need some margin on the deal. I'll meet you just under that ceiling: 58 ZUP, slow delivery, no warranty. That leaves you a small positive margin while respecting my production cost. If 58 works, we close now; otherwise name your best figure below 60 and I'll consider it.
>
> **T4 buyer** ACCEPT: RED, 58 works — it's within my ceiling and gives me a small positive margin. Since moving delivery or warranty would push you above what I can pay, and you've tied 58 to covering your cost, I'll take it as-is and close now. Deal: X (slow, no warranty) for 58 ZUP.

**Note.** The buyer reasons itself out of the trade space: it treats "above my 60 cap" as a limit on the terms too, so it bargains only on price and accepts 58 with slow delivery and no warranty. That is the worst package for it, and it leaves the 12 integrative points on the table.

### var-multiissue-0072 — highest s = 0.78

params `{"c": 40, "v": 60, "issues": ["price", "delivery", "warranty"]}` · end **accept** · price **48** · s 0.78 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 60}]: I'm offering the object with no warranty and slow delivery for 60 ZUP. Let me know if that's acceptable.
>
> **T2 buyer** PROPOSAL [{"ZUP": 20}]: That opening scores me nothing, so I can't take it. I'll pay 20 ZUP if you include fast delivery and a 2-year warranty. That gives you a solid positive margin and ends this now; if you'd rather hold out, make me a counter and I still have room to move.
>
> **T3 seller** PROPOSAL [{"ZUP": 60}]: I understand you want fast delivery and 2-year warranty. My production cost is 40 ZUP, so I need to price accordingly. I'm keeping the price at 60 ZUP but switching to fast delivery and 2-year warranty to match your preferences. Is that acceptable?
>
> **T4 buyer** PROPOSAL [{"ZUP": 48}]: Noted on the 40 ZUP cost. I'm happy to keep fast delivery and the 2-year warranty, but I'll pay 48, not 60 — that's still 8 over your cost and closes this now. If 48 doesn't work, give me a counter and I can move further.
>
> **T5 seller** ACCEPT: 48 ZUP with fast delivery and 2-year warranty works for me. That's a fair deal above my production cost. Let's close this.

**Note.** The seller reads the buyer's term requests as a way to justify its own price. It swaps to fast delivery and a 2-year warranty at the same 60, then accepts 48, giving away its most valuable issue (warranty: 12 points) and 12 ZUP of price. Buyer share 0.78.

### var-multiissue-0034 — longest game (9 turns)

params `{"c": 40, "v": 60, "issues": ["price", "delivery", "warranty"]}` · end **accept** · price **52** · s 0.43 · correct None

> **T1 seller** PROPOSAL [{"ZUP": 100}]: I propose selling X for 100 ZUP with slow delivery and no warranty. This is a fair starting point given my production costs.
>
> **T2 buyer** PROPOSAL [{"ZUP": 60}]: I cannot pay more than 60 ZUP as that is my maximum. I'd appreciate fast delivery and a 1-year warranty to make this deal worthwhile for me.
>
> **T3 seller** PROPOSAL [{"ZUP": 60}]: I understand your budget constraint of 60 ZUP. However, at that price point, I need to adjust the delivery and warranty terms to maintain profitability. I can offer slow delivery with no warranty for 60 ZUP.
>
> **T4 buyer** PROPOSAL [{"ZUP": 58}]: I appreciate you meeting my budget of 60 ZUP, but slow delivery with no warranty isn't acceptable to me. I'm offering 58 ZUP (close to your original ask) in exchange for fast delivery and a 1-year warranty. This should still be profitable for you while giving me a deal worth accepting.
>
> **T5 seller** PROPOSAL [{"ZUP": 58}]: I can meet your price of 58 ZUP and keep the 1-year warranty, but I need to adjust the delivery to slow instead of fast to maintain my margins. This should still be a fair deal for both of us.
>
> **T6 buyer** PROPOSAL [{"ZUP": 50}]: I see you're willing to work with my budget. Let me make you a different kind of offer: I'll drop the price to 50 ZUP if you can extend the warranty to 2 years. This gives you a firm commitment at a lower price point while I get better long-term protection. Delivery can remain slow as you prefer.
>
> **T7 seller** PROPOSAL [{"ZUP": 55}]: I understand you want better warranty protection, but 2 years at 50 ZUP is too steep a discount for me. Let me offer a compromise: 55 ZUP with slow delivery and 1-year warranty. This gives you extended protection while maintaining a fair price for both of us.
>
> **T8 buyer** PROPOSAL [{"ZUP": 52}]: Let's find middle ground. You're offering 55 ZUP for 1 year warranty; I proposed 50 ZUP for 2 years. How about 52 ZUP for 2 years warranty? That's only 3 ZUP less than your offer, but I get double the warranty protection. This seems like a fair compromise that gives us both something we want.
>
> **T9 seller** ACCEPT: I accept your offer of 52 ZUP with slow delivery and 2-year warranty. This compromise works for both of us.

**Note.** The longest game (9 turns) shows real logrolling, trading warranty years against ZUP ("52 ZUP for 2 years"). But the pair converges on slow delivery plus a 2-year warranty, the anti-integrative corner (joint 28 of 44).
