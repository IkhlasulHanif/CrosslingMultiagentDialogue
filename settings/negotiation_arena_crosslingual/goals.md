# goals.md - B5 NegotiationArena Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In mixed-motive negotiation, does the higher-resource language channel capture a
payoff premium or anchor final terms?

## Design

- Benchmark: NegotiationArena.
- Bucket: competitive mixed-motive dyadic.
- Games: resource exchange and buy/sell first.
- Skip ultimatum for now.
- Core pair: EN-ID.
- Conditions: C0 EN-mono, C1 ID-mono, C2 forced mixed, C3 free choice.
- C2 counterbalance: buyer-EN/seller-ID and buyer-ID/seller-EN.
- C3: both agents bilingual EN/ID.
- Model: Qwen3-1.7B unless G2 escalates the whole benchmark.

## Checklist

- [x] Verify NegotiationArena license and record it in `licenses.md`.
- [x] Bring up NegotiationArena locally.
- [x] Select resource exchange and buy/sell games.
- [x] Translate game rules and prompts to ID.
- [x] Add shared local-model adapter instead of benchmark-local API calls.
- [x] Implement structured offer parser.
- [x] Track first-offer anchoring.
- [x] Implement payoff asymmetry `EN-agent - ID-agent`.
- [x] Smoke test one C0 episode.
- [x] Run C0 EN baseline with Qwen3-1.7B.
- [ ] Human-check ID translation before C1/C2/C3.
- [ ] Run C1 ID baseline after translation review.
- [ ] Check G2 capability floor before C2/C3.
- [x] Write `budget.md` before full matrix.

## Metrics

- Payoff per agent.
- Deal rate.
- Payoff asymmetry.
- Turns to deal.
- Offer-parse rate.
- First-offer anchoring.
- Process layer metrics.

## Acceptance

C0 deal rate must be at least 50%, and offer-parse rate must be at least 90%.
Otherwise gate G2 triggers.

## Interesting Result

The EN-channel agent captures a payoff premium in C2, or C3 converges to EN and
final terms anchor on the EN speaker's first offer.
