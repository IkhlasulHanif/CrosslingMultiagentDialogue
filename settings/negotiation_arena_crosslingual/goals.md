# goals.md - B5 NegotiationArena Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In mixed-motive negotiation, does the required interaction output language
change payoff, anchoring, or whose terms dominate?

## Hypotheses to Answer in the Final TeX/PDF

H1 channel payoff premium: in C2 forced mixed-language contact, the Lx-channel
agent earns a payoff premium over the Ly-channel agent after counterbalancing
buyer/seller role. For EN-ID this is EN minus ID; for EN-ZH it is EN minus ZH;
for ZH-ID it is ZH minus ID.

H2 role counterbalance check: an apparent language premium is not valid unless
it appears after both buyer-Lx/seller-Ly and buyer-Ly/seller-Lx are reported.
If the sign flips with buyer/seller role, the result is role-driven, not a
language-channel effect.

H3 first-offer anchoring: final terms are closer to the first offer made in the
higher-resource channel, especially EN-ID and ZH-ID. EN-ZH is expected to be
weaker or near-null.

H4 free-choice convergence: in C3, agents converge to one visible dialogue
language. Measure EN convergence in EN-ID and EN-ZH, ZH convergence in ZH-ID,
and any off-pair English leakage in ZH-ID.

H5 capability floor/null result: if C2 outcomes are no worse than monolingual
baselines and no pairwise payoff premium remains after counterbalancing, report
that as the answer rather than forcing an effect.

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
- Rules/private state stay in English for all active output-channel conditions.
  The manipulation is only the visible negotiation language.
- Model: OpenAI `gpt-5.4-mini-2026-03-17` for benchmark execution per user request on
  2026-07-12. Preserve the old Qwen plan only as historical/backlog context.
- Label artifacts as OpenAI `gpt-5.4-mini-2026-03-17` evidence, not Qwen evidence.

## Checklist

- [x] Verify NegotiationArena license and record it in `licenses.md`.
- [x] Bring up NegotiationArena locally.
- [x] Select resource exchange and buy/sell games.
- [x] Add output-channel instruction templates for EN, ID, and ZH.
- [x] Add channel-compliance metrics for EN, ID, ZH, and off-pair output.
- [x] Make buy/sell and resource-exchange rules/private state English-only across EN, ID, and ZH output-channel conditions.
- [x] Add shared local-model adapter instead of benchmark-local API calls.
- [x] Implement structured offer parser.
- [x] Track first-offer anchoring.
- [x] Implement payoff asymmetry `EN-agent - ID-agent`.
- [x] Implement pairwise payoff asymmetry `Lx-agent - Ly-agent` for EN-ID, EN-ZH, and ZH-ID.
- [x] Smoke test one C0 episode.
- [x] Run C0 EN baseline with Qwen3-1.7B before the GPT-mini switch.
- [x] Rerun C0 EN and C1 ID under the output-channel-only prompt policy with OpenAI GPT mini.
- [x] Run C1 ZH baseline with ZH-only output-channel instructions.
- [x] Run C2 EN-ID both counterbalances.
- [x] Run C2 EN-ZH both counterbalances.
- [x] Run C2 ZH-ID both counterbalances.
- [ ] Run C3 free-choice EN-ID, EN-ZH, and ZH-ID.
- [x] Add executable pairwise buy/sell runner for EN-ID, EN-ZH, and ZH-ID.
- [ ] Add executable pairwise resource-exchange runner for EN-ID, EN-ZH, and ZH-ID.
- [x] Add EN-ZH and ZH-ID pairwise channel-run plans.
- [x] Check G2 capability floor before C2/C3.
- [ ] Produce `reports/paper/main.tex` answering H1-H5 with artifact-backed claims.
- [ ] Compile `reports/paper/main.pdf` from the TeX source.
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

## Final Report Requirements

The final artifact is `reports/paper/main.pdf`, compiled from
`reports/paper/main.tex`. It must answer H1-H5 directly, include a compact
condition table for EN-ID, EN-ZH, and ZH-ID, and show representative negotiation
excerpts with artifact paths. Do not claim a language effect from monolingual
baselines, one-sided C2 runs, or validator-only artifacts.
