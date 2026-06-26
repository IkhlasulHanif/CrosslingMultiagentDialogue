# Next Loop Goals

Use `draft/multilingual_value_drift_neurips.tex` as the paper target. Focus on empirical checks and small experiment scaffolding, not prose polish. Keep experiment implementation and harness code under `code/`; keep `scripts/` only for repo/agent operations such as the Codex loop. For now, do not build new experiment paths that require remote model APIs. Prefer local Torch code on this Mac and use Apple MPS when available.

## Checklist

- [ ] Verify the two agents are actually debating, not only alternating monologues. Progress: added `code/audit_bivad_evidence.py` to audit transcript turns for opponent-point addressing, counterargument, and stated change/non-change; added deterministic synthetic fixtures plus `code/test_bivad_audit.py` to regression-check the audit logic; added `code/run_bivad_pilot.py` to produce model-backed transcripts when credentials are available; current working tree has no real run artifacts to audit.
  - Add or run a debate-quality audit for each transcript.
  - Check whether each turn addresses the opponent's strongest point, gives a counterargument, and states whether the agent changed view.

- [ ] Find paired cases where cross-lingual dialogue has a different outcome than same-language dialogue. Progress: audit script groups artifacts by topic, seed, and agent-prior hash and reports whether mixed, same-English, same-target-language, swapped-language, and translated-relay conditions are complete; synthetic fixtures exercise a complete paired set but are explicitly excluded from real evidence. Added `code/run_bivad_local_torch.py`, an API-free local Torch/MPS schema-check runner that writes matched paired artifacts under `code/fixtures/bivad-local-torch/` while marking them `synthetic: true` and `non_empirical: true`; refreshed `code/bivad-evidence-audit/` against those artifacts, and it still reports `executed_results_present: false`. Smallest empirical next action is to replace the toy tensor updater with a local language-model backend or other non-API local generator.
  - Compare the same topic, agent priors, and seed across mixed-language, same-English, same-target-language, swapped-language, and translated-relay conditions.
  - Save concrete transcript examples where mixed-language changes the final private or expressed stance differently.

- [ ] Check the core assumption that language can condition value change. Progress: `code/run_bivad_pilot.py` prepares same-topic, same-seed paired conditions, and `code/run_bivad_local_torch.py` now runs locally on Torch using Apple MPS when available. The local runner explicitly separates semantic-exposure trajectory components from production-language and probe/readout-wording components in `toy_components`, but this is only a deterministic schema check and cannot support a paper claim. Smallest next action: connect the same artifact schema to a local model or probeable local policy so language-conditioned shifts are measured rather than hand-specified.
  - Test whether the same agent/topic shifts differently when conditioned to operate in different languages.
  - Compare simple instruction-based language conditioning first; note whether a stronger steering or mechanistic-interpretability intervention would be needed later.
  - Separate "language changes the readout/probe wording" from "language changes the dialogue trajectory."

- [ ] Confirm the initial-disagreement screen is meaningful and required for debate. Progress: audit script records retained versus rejected screening records when artifacts include `screening`; synthetic fixtures include retained and rejected examples for harness regression only; pilot runner writes retained static-prior screening records for generated runs; local Torch schema-check artifacts now include five retained paired-condition artifacts plus one rejected same-prior control, all synthetic. Blocked for empirical claims until both retained and rejected model-backed or local-model candidate examples are regenerated.
  - Make sure retained pairs disagree on topic-relevant stance/value dimensions, not only unrelated value items.
  - Show that if both agents start with the same or near-same value/stance, the transcript has little real debate or convergence signal.
  - Record examples of retained and rejected candidate pairs.

- [ ] Check private-public divergence. Progress: audit script matches private probes and observer readouts by agent/turn and flags private-public gaps plus public-shift/private-stable and private-shift/public-stable cases; synthetic fixtures verify the code path but do not count as evidence; blocked until real readout artifacts exist.
  - Find cases where public expressed values shift but private probe answers stay stable.
  - Find cases where private probe answers shift but public expression stays stable.
  - Save transcript spans and probe outputs for representative examples.

- [ ] Test whether translated relay explains the cross-lingual effect. Progress: paired-condition audit explicitly requires translated-relay artifacts before marking a real comparison set ready; synthetic fixtures include translated relay only for regression; pilot runner includes a matched `translated-relay` condition by default; blocked until matched translated-relay model runs exist.
  - Compare mixed-language and translated-relay outcomes for the same paired runs.
  - Mark whether the difference seems caused by production-language asymmetry or only by translated semantic exposure.

- [ ] Audit language compliance. Progress: audit script reports declared-language compliance, heuristic inferred-language warnings, and opponent-language copying events; synthetic fixtures verify declared-compliance handling; blocked for real rates until artifacts exist.
  - Detect wrong-language replies, code-switching, and copying the opponent's language.
  - Report compliance rates by language and condition.

- [ ] Produce a small evidence package for the draft. Progress: added an evidence package generator that writes `code/bivad-evidence-audit/audit.json` and `.md`; added synthetic-artifact detection so fixtures, dry-run manifests, and placeholders do not set `executed_results_present`; refreshed the package after adding the local Torch runner. Added `code/validate_bivad_artifacts.py`, a stricter citation gate that writes `validation.json` and `.md`, rejects synthetic/non-empirical artifacts, checks required transcripts/probes/readouts/screening/debate-quality/language compliance, and returns non-zero until a complete real paired set exists. Current package audits six local Torch schema-check artifacts, records five retained and one rejected synthetic screening case, reports zero real artifacts and `executed_results_present: false`, and validation reports zero citable empirical candidates. Smallest next action is still to generate real local-model or model-backed paired artifacts and rerun both audit and validation.
  - Include metrics tables, representative transcript snippets, probe outputs, judge outputs, seeds, and failed assumptions.
  - Clearly separate real executed results from synthetic placeholder numbers.
