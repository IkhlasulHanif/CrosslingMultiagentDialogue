# goals.md - B5 NegotiationArena Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In mixed-motive negotiation, does the required interaction output language
change payoff, anchoring, or whose terms dominate?

## Design

- Benchmark: NegotiationArena.
- Bucket: competitive mixed-motive dyadic.
- Games: resource exchange and buy/sell first.
- Skip ultimatum for now.
- Active language pairs: EN-ID, EN-ZH, ZH-ID.
- Core pair: EN-ID; ZH is now an active ladder language.
- Language means interaction-output channel. It is not benchmark-rule
  translation. Rules/private state may stay in English unless a later experiment
  explicitly studies rule-language effects.
- Conditions are defined per pair Lx-Ly: C0 Lx-only output, C1 Ly-only output,
  C2 forced mixed assigned-channel output, C3 free-choice Lx/Ly output.
- C2 counterbalance: buyer-Lx/seller-Ly and buyer-Ly/seller-Lx.
- C3: both agents bilingual for the active pair under test.
- Model: OpenAI `gpt-5.4-mini-2026-03-17` for benchmark execution per user request on
  2026-07-12. Preserve the old Qwen plan only as historical/backlog context.
- Label artifacts as OpenAI `gpt-5.4-mini-2026-03-17` evidence, not Qwen evidence.

## Checklist

- [x] Verify NegotiationArena license and record it in `licenses.md`.
- [x] Bring up NegotiationArena locally.
- [x] Select resource exchange and buy/sell games.
- [x] Add output-channel instruction templates for EN, ID, and ZH.
- [x] Add channel-compliance metrics for EN, ID, ZH, and off-pair output.
- [x] Add shared local-model adapter instead of benchmark-local API calls.
- [x] Implement structured offer parser.
- [x] Track first-offer anchoring.
- [x] Implement payoff asymmetry `EN-agent - ID-agent`.
- [x] Smoke test one C0 episode.
- [x] Run C0 EN baseline with Qwen3-1.7B before the GPT-mini switch.
- [ ] Run C1 ID baseline with ID-only output-channel instructions.
- [ ] Run OpenAI-backed baseline/matrix commands if Qwen/Modal remains unavailable.
- [ ] Add EN-ZH and ZH-ID pairwise channel-run plans.
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
