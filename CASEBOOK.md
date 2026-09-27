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
