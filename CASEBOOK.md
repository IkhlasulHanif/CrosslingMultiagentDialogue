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
