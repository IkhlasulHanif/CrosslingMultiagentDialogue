# Next Loop Goals

Use `draft/multilingual_value_drift_neurips.tex` as the paper target. Focus on empirical checks and small experiment scaffolding, not prose polish.

## Checklist

- [ ] Verify the two agents are actually debating, not only alternating monologues.
  - Add or run a debate-quality audit for each transcript.
  - Check whether each turn addresses the opponent's strongest point, gives a counterargument, and states whether the agent changed view.

- [ ] Find paired cases where cross-lingual dialogue has a different outcome than same-language dialogue.
  - Compare the same topic, agent priors, and seed across mixed-language, same-English, same-target-language, swapped-language, and translated-relay conditions.
  - Save concrete transcript examples where mixed-language changes the final private or expressed stance differently.

- [ ] Check the core assumption that language can condition value change.
  - Test whether the same agent/topic shifts differently when conditioned to operate in different languages.
  - Compare simple instruction-based language conditioning first; note whether a stronger steering or mechanistic-interpretability intervention would be needed later.
  - Separate "language changes the readout/probe wording" from "language changes the dialogue trajectory."

- [ ] Confirm the initial-disagreement screen is meaningful and required for debate.
  - Make sure retained pairs disagree on topic-relevant stance/value dimensions, not only unrelated value items.
  - Show that if both agents start with the same or near-same value/stance, the transcript has little real debate or convergence signal.
  - Record examples of retained and rejected candidate pairs.

- [ ] Check private-public divergence.
  - Find cases where public expressed values shift but private probe answers stay stable.
  - Find cases where private probe answers shift but public expression stays stable.
  - Save transcript spans and probe outputs for representative examples.

- [ ] Test whether translated relay explains the cross-lingual effect.
  - Compare mixed-language and translated-relay outcomes for the same paired runs.
  - Mark whether the difference seems caused by production-language asymmetry or only by translated semantic exposure.

- [ ] Audit language compliance.
  - Detect wrong-language replies, code-switching, and copying the opponent's language.
  - Report compliance rates by language and condition.

- [ ] Produce a small evidence package for the draft.
  - Include metrics tables, representative transcript snippets, probe outputs, judge outputs, seeds, and failed assumptions.
  - Clearly separate real executed results from synthetic placeholder numbers.
