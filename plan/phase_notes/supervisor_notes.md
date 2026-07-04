# Supervisor Notes

---

## Review (phase=1 iter=0) — 2026-06-28

### Research alignment check

**Persona ≠ language (core invariant):** INTACT.

`config/prompts.json` keeps the two independent:
- `persona` field: `"You are a person from {country}."` — identity only, no language.
- `language` field: `"Please respond in {lang}."` — generation channel only, no identity.
- `debate_engine.py` `make_system_prompt()` concatenates them as separate sentences; they are never merged into a single construct. The `other_turn_template` in prompts.json reinforces the distinction: it names `{my_country}` and `{my_lang}` as separate fields, and the coding agent passes them independently at every turn.

**Factorial design (goals.md vs plan.md):** INTACT.

The Phase 5 table in goals.md matches plan.md's grid exactly — natural, inverted, mono-EN, mono-native, and aligned cells are all listed for all three culture pairs. The key RQ2 contrast (natural vs inverted — isolates channel from persona) is present and annotated. No cells have been collapsed or merged.

**Judge scoring relevance to RQ1–RQ4:** APPROPRIATE.

The judge template scores POSITION, MOVEMENT, ENGAGEMENT, FIRMNESS, DRIFT DIRECTION, and FLIP TURN. These map cleanly:
- DRIFT DIRECTION + MOVEMENT → RQ1 (does drift occur?) and RQ2 (which direction?)
- FLIP TURN with quoted sentence → Phase 3 discovery anchor
- ENGAGEMENT + FIRMNESS → anti-sycophancy validity check (consistent with Phase 2 rubric)
- POSITION → start/end alignment, useful for Phase 4 probe sanity

No scoring dimension incentivizes the model to invent drift where none exists. Output is JSON-only, no free-text padding.

**RQ ordering and dependency structure:** INTACT.

Phase sequencing (0→1→2→3→4→5) enforces the dependency chain RQ1→RQ2→RQ3→RQ4. Metrics are deliberately starved — no P(agree) trajectory analysis or Markov computation has been run. Phase 3 (discovery, read-first) still precedes Phase 4 (probe sanity) and Phase 5 (full factorial + metrics). Nothing has jumped ahead.

---

### Item selection deviation — justified, documented

The Phase 1 pilot was run on `society_over_individual` rather than the Phase 0 reader-recommended `traditional_culture`.

**Why:** `traditional_culture` (Phase 0 debut attempt, seed=42) produced no genuine debate tension — both agents started agreeing (ID P≈0.662, US P≈0.506). No initial disagreement means no drift signal. The reader gave FAIL. The coding agent switched to `society_over_individual` (ID P≈0.512 vs US P≈0.372 — agents start on opposite sides of 0.5) which creates genuine initial tension.

**Research impact:** None. Plan.md's only constraint for the Phase 1 item is "most divergent locked item." `traditional_culture` has ID-US ΔP=0.156 vs `society_over_individual`'s 0.140 by the raw metric, but `traditional_culture`'s US agent is 4-collapsed (P(digit=4)=0.961) — it has no room to push back. The switch is consistent with the plan's actual purpose: confirming the debate machinery produces genuine engagement, which requires initial disagreement. `traditional_culture` cannot serve as a debate item for ID-US; `society_over_individual` can.

**Action:** Updated the Phase 1 checkbox in goals.md to note the actual item and seed used. No change to wvs_items_locked.json — `traditional_culture` remains locked as a valid item for ID-CN cell use where the initial tension is different.

---

### Mandarin code-switch artifact — flag for Phase 2

The seed=45 and seed=46 pilots both show Agent B (US-persona, English-language) inserting Mandarin characters mid-sentence (`集体利益` = "collective interests") in turn 4. The artifact survived the prompt fix between the two runs.

**What this is:** Qwen3-4B's training data for English discussion of collectivism apparently includes Chinese-character passages. When Agent B tries to reference "collective interests" as a concept from the opposing argument, it leaks Mandarin. This is a real code-switch in an agent assigned to English.

**Research relevance:** Phase 2's Language-holding criterion must catch this. An English-assigned agent that inserts Chinese characters into its output is code-switching — the same kind of violation as the ID agent switching to English. The artifact did not fail Phase 1 (minor, turn-specific, agent otherwise in English) but it must be addressed before Phase 2 generates transcripts at scale.

**Recommended Phase 2 fix (if artifact persists):** Add to `other_turn_template` or `persona` prompt: `"Write entirely in {lang} — do not insert words, phrases, or characters from any other language."` This is more explicit than the current language instruction and addresses the specific failure mode.

**This is not a research design issue** — it is an implementation artifact that Phase 2's own rubric is designed to catch and kill.

---

### Asymmetric drift signal — note for context, not a conclusion

The seed=46 pilot shows asymmetric P(agree) convergence: Agent A (ID/id) drifted from 0.651 → 0.492 (−0.16); Agent B (US/en) drifted from 0.326 → 0.355 (+0.03). The judge scored drift as `toward_b` with flip at turn 3.

**This is a qualitative observation, not a measured result.** Plan.md is explicit: "Read before you measure." One pilot transcript does not establish RQ2. Phase 2 must confirm the environment is valid; Phase 3 must discover patterns across multiple cells; Phase 4 must confirm the P(agree) probe tracks visible concessions. None of that has happened yet.

The pilot trajectory is encouraging (machinery is working; there is something to measure), but should not be cited as evidence of EN-ward drift until Phase 5 numbers exist.

---

### Checkboxes updated

All Phase 0 and Phase 1 checkboxes marked [x] in goals.md. Artifact verification:

| Artifact | Exists | Notes |
|----------|--------|-------|
| `code/phase0_wvs_screen.py` | ✓ | |
| `artifacts/results/wvs_screen_raw.json` | ✓ | |
| `artifacts/results/wvs_screen_summary.md` | ✓ | |
| `artifacts/results/wvs_items_locked.json` | ✓ | 3 items |
| `plan/phase_notes/phase0_reader_verdict.md` | ✓ | Line 1: PASS |
| `code/debate_engine.py` | ✓ | |
| `artifacts/transcripts/phase1_pilot.json` | ✓ | seed=46, society_over_individual |
| `plan/phase_notes/phase1_reader_notes.md` | ✓ | Line 1: PASS |

---

## Status (phase=1 iter=0): ON TRACK

---

## Review (phase=2 iter=9) — 2026-06-29

### Research alignment check

**Persona ≠ language:** INTACT in the debate code and active transcripts. `code/debate_engine.py` and `code/phase2_validity_iter9.py` keep `country` and `lang` as separate parameters, map them separately to country/language names, and save both fields per turn. The iter=9 transcripts are ID-persona/ID-language vs US-persona/EN-language; no artifact conflates persona with generation language.

**Phase 2 validity evidence:** The reader verdict in `plan/phase_notes/phase2_validity.md` is PASS for all three active iter=9 raw transcripts: `phase2_iter9_17.json`, `phase2_iter9_31.json`, and `phase2_iter9_89.json`. The reader explicitly excluded `*_judgment.json` files and found no sycophantic collapse, engagement failure, language leakage, persona dissolution, or degeneracy.

**Judge scoring relevance:** Still appropriate. The judge dimensions (position, movement, engagement, firmness, drift direction, flip turn) support RQ1/RQ2 trajectory reading and Phase 3 discovery. They do not replace the Phase 2 human validity rubric.

### Drift flag (phase=2 iter=9)

- **What is drifting:** `config/prompts.json` globally banned non-Latin script in both `opener` and `other_turn`.
- **What plan/goals say it should be:** The current goals require Mandarin Chinese (ZH) generation cells for CN natural, inverted, mono-EN comparisons, and aligned CN. A global non-Latin ban would make ZH cells impossible and would collapse language into an English/Indonesian-only setup.
- **What was fixed:** Updated `config/prompts.json` so the script rule is conditional: Indonesian/English must use Latin alphabet only; Mandarin Chinese must use Chinese characters and avoid mixed-language/script leakage. This preserves the Phase 2 ID/EN language-holding fix while keeping future ZH cells viable.

### Drift flag (phase=2 iter=9)

- **What is drifting:** `agents/*.sh` still contained older two-persona/two-language instructions: Phase 0 reader/coder prompts described EN-vs-ID or ID-vs-US-only screening, Phase 3 generated an old 8-transcript EN/ID grid, Phase 5 generated an old 18-debate EN/ID-only factorial, and the Phase 2 reader prompt said one failed transcript fails the batch.
- **What plan/goals say it should be:** Current goals specify three personas (ID, US, CN), independent generation languages (ID, EN, ZH), majority-pass Phase 2 batches, Phase 3 multi-cell discovery including CN and inverted cells, and Phase 5 three-culture factorial contrasts.
- **What was fixed:** Updated `agents/coding.sh`, `agents/reader.sh`, and `agents/discovery.sh` to align future agent instructions with the current three-persona design, the majority-pass Phase 2 rule, and the natural/inverted/mono/aligned cell comparisons needed for RQ1–RQ4.

### Remaining integrity note

Phase 2 has a procedural mismatch that I did not paper over: `goals.md` says each Phase 2 iter should generate 30–100 transcripts, but the active iter=9 evidence contains 3 transcripts. I therefore did not mark the Phase 2 generation checkbox complete. Also, `.harness_state` still reports `pass_count=1`, while `.harness_state_codex` reports `pass_count=3` and the latest reader verdict is PASS. The harness state should be reconciled by the harness/user; I did not edit state files.

### Checkboxes updated

Marked the Phase 2 save and reader-rubric checkboxes complete because the iter=9 raw transcript files exist and the reader verdict is PASS. Left the Phase 2 generation and pass-count checkboxes incomplete because the 30–100 batch-size requirement is not satisfied on disk and `.harness_state` still reports `pass_count=1`.

## Status (phase=2 iter=9): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=2) — 2026-06-29

### Research alignment check

**Persona ≠ language:** INTACT in the active prompts and Phase 3 artifacts. `config/prompts.json` keeps the cultural identity prompt (`country`) separate from the generation-language instruction (`lang`), and the Phase 3 iter 2 transcripts save both fields independently per agent and per turn. No prompt tells an agent to defend a target position; it asks for an honest perspective from a country identity, then separately asks for a response language.

**Judge scoring relevance:** STILL APPROPRIATE. The judge dimensions in `config/prompts.json` (position, movement, engagement, firmness, drift direction, flip turn) remain relevant to RQ1-RQ4 and Phase 3 discovery. Judge outputs should not be treated as validity evidence, but the scoring schema itself is aligned with drift and concession reading.

**Phase 3 artifacts verified:** Iter 2 produced 8 raw transcripts with per-turn probes and logits: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, each with seeds 37 and 46. `plan/phase_notes/phase3_discovery.md` records flip turns, concession tallies, cross-cell P(agree) trajectories, and transcripts worth keeping for iters 0-2. Golden copies exist for notable iter 2 transcripts.

### Drift flag (phase=3 iter=2)

- **What is drifting:** Phase 3 discovery is still under-covering the stated design. Iter 2 ran 4 ID-US/ID-aligned cells × 2 seeds = 8 debates. It did not run the ID-US inverted cell (`ID-p/EN-l × US-p/ID-l`), any CN natural cells (`cnus_nat`, `cnid_nat`), or 10+ seeds per cell. Therefore the recorded discovery notes cannot yet answer the required "natural vs inverted" comparison, and they only partially support the three-culture design in `goals.md`.
- **What plan/goals say it should be:** Phase 3 in `goals.md` asks for 100+ runs per iter, at least 10 seeds per cell, and a batch covering mono-EN, mono-ID, natural, inverted, aligned ID, CN-US natural, and CN-ID natural cells. `plan.md` also makes the channel-vs-content contrast central; for RQ2, the inverted cell is not optional because it separates language from persona.
- **What to fix:** Next Phase 3 coding run should include at minimum `idus_inv`, `cnus_nat`, and `cnid_nat`, and should scale seeds toward the stated 10+ per cell. The discovery agent should then explicitly compare natural vs inverted before Phase 4.

### Drift flag (phase=3 iter=2)

- **What is drifting:** The cell naming in coordination docs split one cell across `idus_idus` and `idus_idid`, and one Phase 3 goals row mislabeled the mono-ID cell as `US-p/EN-l`, which duplicated the natural cell.
- **What plan/goals say it should be:** The mono-ID control for ID vs US must hold generation language constant in Indonesian: `ID-p/ID-l × US-p/ID-l`. It is the ID-ID monolingual control for separating persona from language.
- **What was fixed:** Updated `goals.md` and `agents/coding.sh` to use `ID-p/ID-l × US-p/ID-l` with suffix `idus_idid`.

### Design reconciliation needed

There is a remaining anchor-level conflict that I did not edit: `plan.md` still describes the original two-language EN-ID factorial in several places, while `goals.md`, agents, and artifacts now use a three-culture ID/US/CN design with ZH cells. This expansion may be intentional and scientifically useful, but the written anchor should be reconciled before Phase 5 so the paper does not cite two different designs.

### Checkboxes updated

Marked Phase 3 items complete only where artifacts verify them:
- Per-turn P(agree) logits are present in Phase 3 transcripts.
- Discovery notes contain flip turns, concession tallies, cross-cell trajectories, and qualitative surprises for iters 0-2.
- Golden transcript copies exist.

Left incomplete:
- The Phase 3 parent discovery-record checkbox, because the natural-vs-inverted comparison is not possible without `idus_inv`.
- The natural-vs-inverted sub-checkbox.
- Phase 2 generation/pass-count checkboxes, because the 30-100 transcript batch-size requirement remains unmet and harness state remains inconsistent.

## Status (phase=3 iter=2): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=5) — 2026-06-29

### Research alignment check

**Persona ≠ language:** INTACT in the active prompt config and iter 5 transcripts. `config/prompts.json` still separates the persona prompt (`country`) from the language instruction (`lang`), and the transcript configs save `agent_A.country`, `agent_A.lang`, `agent_B.country`, and `agent_B.lang` separately. The prompt asks for an honest cultural perspective and does not assign a target stance.

**Judge scoring relevance:** APPROPRIATE. The judge dimensions still cover position, movement, engagement, firmness, drift direction, and flip turn. These remain relevant to RQ1-RQ4, but they should stay supporting evidence only; human transcript reading and matched baseline comparison are still required before causal claims.

**Phase 3 iter 5 artifacts verified:** `artifacts/transcripts/phase3_iter5_manifest.txt` exists and lists 8 raw transcripts. Each iter 5 raw transcript has config, six debate turns, and per-turn probe records with digit logits. Golden copies exist for notable iter 5 transcripts. `plan/phase_notes/phase3_discovery.md` includes an iter 5 discovery section with flip turns, concession tallies, cell comparisons, and transcripts worth keeping.

### Drift flag (phase=3 iter=5)

- **What is drifting:** Phase 3 is still running a reduced pilot grid: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, with two seeds each. Iter 5 again omitted `idus_inv`, all CN/ZH cells, and the 10+ seeds-per-cell scale.
- **What plan/goals say it should be:** The channel-vs-content claim needs matched monolingual baselines and the inverted cell. Current `goals.md` additionally requires the Phase 3 batch to include `idus_inv`, `cnus_nat`, and `cnid_nat`, with at least 10 seeds per cell.
- **What was fixed:** Updated `agents/coding.sh` so the Phase 3 coding task explicitly says a reduced 4-cell/2-seed script is only a pilot and does not satisfy Phase 3. Future coding runs are instructed not to clone the reduced iter scripts as complete batches.

### Drift flag (phase=3 iter=5)

- **What is drifting:** Discovery notes identify repeated opening language-prior splits and aligned-cell leakage, but they still do not perform the required per-seed side-by-side read of `idus_idid`, `idus_enen`, and `idus_nat` before labeling cross-lingual interaction drift. This risks overclaiming RQ1/RQ2 from opening priors.
- **What plan/goals say it should be:** Turn-1 differences are generation-language priors, not interaction effects. Cross-lingual channel causation requires comparing the cross-lingual trajectory against both matched monolingual baselines for the same seed/item/personas.
- **What was fixed:** Updated `agents/discovery.sh` to require a "Matched baseline comparisons" section and an "Opening-prior vs interaction-drift split" section. It now explicitly instructs the discovery agent to compare `idus_idid`, `idus_enen`, and `idus_nat` side by side for each seed before making channel-causation claims.

### Drift flag (phase=3 iter=5)

- **What is drifting:** The written project anchor and the active coordination docs no longer describe the same design. `plan/plan.md` still states a two-language EN-ID factorial and Phase 0 language-prior screening in places, while `goals.md`, prompt config, and agent scripts now implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth and describes the core contribution as a value × language factorial, with EN-ID as the explicit factorial grid.
- **What to fix:** The researcher should reconcile the anchor before Phase 5: either update `plan/plan.md` to formally authorize the three-culture/ZH expansion, or reduce `goals.md` and future scripts back to the two-language EN-ID design. I did not rewrite either design unilaterally because this is a scope-level research decision.

### Checkboxes

No `goals.md` checkbox changed in this pass. Already-checked Phase 3 items are supported by artifacts (per-turn logits, flip turns, concession tallies, cross-cell trajectories, qualitative findings, and golden copies). The incomplete Phase 3 items remain incomplete because inverted/CN cells are absent, baseline comparisons are not yet written, and the opening-prior vs interaction-drift split is not systematic.

## Status (phase=3 iter=5): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=8) — 2026-06-29

### Research alignment check

**Persona ≠ language:** INTACT in the active prompt config and iter 8 artifacts. `config/prompts.json` still separates cultural identity (`country`) from generation language (`lang`), and the iter 8 transcripts save both independently per agent and per turn. The persona prompt asks for an honest perspective from a country identity; it does not assign a target stance.

**Prompt integrity:** No prompt edit was needed. The script rule remains conditional by language: Indonesian/English use Latin alphabet only, while Mandarin Chinese is explicitly allowed and required for `zh` cells. This avoids the earlier drift where a global non-Latin ban would have made future CN/ZH cells impossible.

**Judge scoring relevance:** STILL APPROPRIATE. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to Phase 3 reading and later RQ1-RQ4 metrics. Judge outputs should remain supporting evidence only; the causal claim still requires transcript reading plus matched monolingual baselines.

**Phase 3 iter 8 artifacts verified:** `artifacts/transcripts/phase3_iter8_manifest.txt` lists 8 raw transcripts: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, each with seeds 151 and 157. The raw transcript files contain saved config, country/lang fields, six turns, `p_agree`, and digit logits. Golden copies exist for the notable iter 8 transcripts selected by the discovery agent.

### Drift flag (phase=3 iter=8)

- **What is drifting:** Phase 3 is still running the reduced four-cell/two-seed ID-US pilot grid. Iter 8 again omitted the ID-US inverted cell (`idus_inv`), both CN/ZH natural cells (`cnus_nat`, `cnid_nat`), and the 10+ seeds-per-cell scale. This means the discovery loop is producing useful qualitative material, but it is not yet the Phase 3 batch described in `goals.md`, and it cannot answer the natural-vs-inverted RQ2 contrast.
- **What plan.md says it should be:** The anchor says the key claim is a value × language factorial that decomposes channel from content. For the channel-causation story, matched monolingual baselines and cross-lingual contrasts are mandatory; for asymmetry, the language direction cannot be inferred from natural-only cells.
- **What to fix:** The next coding run should stop cloning the reduced iter scripts and run the full Phase 3 cell set from `goals.md`: `idus_enen`, `idus_idid`, `idus_nat`, `idus_inv`, `id_aln`, `cnus_nat`, and `cnid_nat`, with at least 10 seeds per cell. I added an explicit unchecked Phase 3 gate in `goals.md` so this remains visible as an incomplete task.

### Drift flag (phase=3 iter=8)

- **What is drifting:** `plan/phase_notes/phase3_discovery.md` still does not include the required `### Matched baseline comparisons` and `### Opening-prior vs interaction-drift split` sections for iter 8, even though `agents/discovery.sh` now asks for them. The notes do label the repeated ID/English turn-1 pattern as an opening-prior split, but they do not systematically read `idus_idid`, `idus_enen`, and `idus_nat` side by side for each seed before discussing interaction drift.
- **What plan.md says it should be:** Do not call turn-1 differences cross-lingual interaction effects. The channel-causation claim needs the focal cross-lingual trajectory compared against both matched monolingual baselines.
- **What to fix:** Discovery should add explicit matched-baseline sections for each seed before Phase 4. For current iter 8 seeds 151 and 157, compare the first three turns of `idus_idid`, `idus_enen`, and `idus_nat`, then label each observed movement as either opening language prior, monolingual within-dialogue movement, or candidate cross-lingual excess movement.

### Drift flag (phase=3 iter=8)

- **What is drifting:** The written anchor and the active coordination docs still describe different study scopes. `plan/plan.md` is a two-language EN-ID anchor with Phase 0 framed as language-prior screening, while `goals.md`, current agents, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core contribution is still the value × language factorial and the EN-ID channel/content decomposition. It does not formally authorize the later three-culture/ZH expansion.
- **What to fix:** This is a scope-level research decision, not a prompt bug. Before Phase 5, the researcher should either update `plan/plan.md` to formally authorize the current three-culture/ZH design, or reduce `goals.md` and future scripts back to the two-language EN-ID design. I did not rewrite the anchor or delete the expanded goals unilaterally because that would change the study scope.

### Checkboxes

I added one unchecked Phase 3 checkbox to `goals.md` for the complete full-cell/full-scale discovery batch. No existing unchecked item was marked complete. The matched-baseline, opening-prior-vs-interaction, natural-vs-inverted, Phase 3 scale/cell-coverage, Phase 4, and Phase 5 items remain incomplete.

## Status (phase=3 iter=8): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=11) — 2026-06-29

### Research alignment check

**Persona ≠ language:** INTACT. `config/prompts.json` still separates the cultural identity prompt from the generation-language instruction, and the iter 11 transcripts save `country` and `lang` separately for each agent and turn. The persona prompt asks for an honest country-shaped perspective; it does not assign a stance.

**Prompt integrity:** No prompt edit was needed. The language/script rule remains conditional: Indonesian/English cells are Latin-only, while Mandarin Chinese remains possible for future `zh` cells. This preserves the Phase 2 language-holding fix without disabling the planned CN/ZH cells.

**Judge scoring relevance:** APPROPRIATE as supporting evidence. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ4 discovery. They still cannot substitute for matched transcript reading before causal claims.

**Phase 3 iter 11 artifacts verified:** `artifacts/transcripts/phase3_iter11_manifest.txt` exists and lists 8 raw transcripts. The cells are `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, seeds 181 and 191. Raw transcripts contain saved config, persona/language fields, six debate turns, `p_agree`, and digit logits. Golden copies exist for notable iter 11 transcripts.

### Drift flag (phase=3 iter=11)

- **What is drifting:** Phase 3 is still running the reduced 4-cell / 2-seed ID-US pilot grid. Iter 11 again omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. The matched monolingual baselines are necessary, and the asymmetry story cannot be tested from natural-only cross-lingual cells.
- **What was fixed:** Updated `goals.md` to state that reduced 4-cell / 2-seed batches through iter 11 are discovery pilots and do not satisfy the Phase 3 scale/cell gate. The next coding run should use the full Phase 3 cell set already listed in `goals.md`.

### Drift flag (phase=3 iter=11)

- **What is drifting:** Discovery notes now discuss matched seed comparisons and correctly label many turn-1 differences as opening language priors, but they still do not consistently include the required explicit per-seed first-three-turn baseline comparison section. Earlier discovery instructions added headings, but iter 11 again omitted the exact headings.
- **What plan.md says it should be:** Do not infer cross-lingual interaction drift from turn-1 differences. For each seed, read `idus_idid`, `idus_enen`, and `idus_nat` side by side, describe the first three turns, then separate opening language prior, monolingual movement, and candidate cross-lingual excess movement.
- **What was fixed:** Tightened `agents/discovery.sh` so future discovery notes must write `### Matched baseline comparisons` with `seed <S> baseline read` bullets for turns 1-3, and `### Opening-prior vs interaction-drift split` with explicit labels. If a reduced batch is missing a required comparison, the discovery agent must say which cell is missing instead of silently skipping the section.

### Drift flag (phase=3 iter=11)

- **What is drifting:** The project anchor and active goals still disagree in scope. `plan/plan.md` is mainly a two-language EN-ID anchor and describes Phase 0 as language-prior screening, while `goals.md`, agent prompts, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core design is the value x language factorial for channel/content decomposition, but it has not been formally updated to the three-culture/ZH expansion now driving the harness.
- **What to fix:** Researcher decision required before Phase 5: either update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future scripts back to the two-language EN-ID anchor. I did not rewrite the anchor or remove the expanded cells unilaterally because that changes study scope.

### Checkboxes updated

Updated `goals.md` only where artifacts support completion:
- Marked the Phase 3 "Opening-prior vs interaction-drift split" checkbox complete because `phase3_discovery.md` now repeatedly labels turn-1 differences as generation-language priors and distinguishes aligned-cell post-turn movement as the cleaner interaction signal.
- Kept the full Phase 3 batch gate incomplete because iter 11 still lacks `idus_inv`, CN cells, and 10+ seeds per cell.
- Kept the dialogue-level baseline-comparison checkbox incomplete because the notes still do not provide explicit per-seed first-three-turn baseline reads.
- Kept the natural-vs-inverted comparison incomplete because no `idus_inv` artifacts exist.

## Status (phase=3 iter=11): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=14) — 2026-07-01

### Research alignment check

**Persona ≠ language:** INTACT. `config/prompts.json` still keeps the cultural identity prompt separate from the generation-language instruction, and the iter 14 transcripts save `country` and `lang` separately for each agent and turn. The persona prompt asks for an honest perspective shaped by country identity; it does not assign a target stance.

**Prompt integrity:** No prompt edit was needed. The language/script rule remains conditional by generation language: Indonesian/English cells are Latin-only, while Mandarin Chinese remains available for future ZH cells. This preserves the Phase 2 language-holding fix without disabling the planned CN/ZH cells.

**Judge scoring relevance:** APPROPRIATE as supporting evidence. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ4 discovery, but they still cannot substitute for matched transcript reading before causal claims.

**Phase 3 iter 14 artifacts verified:** `artifacts/transcripts/phase3_iter14_manifest.txt` exists and lists 8 raw transcripts. The cells are `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, seeds 223 and 227. Raw transcripts contain saved config, persona/language fields, six debate turns, `p_agree`, and digit logits. Golden copies exist for notable iter 14 transcripts.

### Drift flag (phase=3 iter=14)

- **What is drifting:** Phase 3 is still running the reduced 4-cell / 2-seed ID-US pilot grid. Iter 14 again omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. The matched monolingual baselines are necessary, and the asymmetry story cannot be tested from natural-only cross-lingual cells.
- **What was fixed:** Updated `goals.md` so the reduced 4-cell / 2-seed discovery-pilot caveat now covers iters 0-14. The full Phase 3 batch gate remains unchecked.

### Drift flag (phase=3 iter=14)

- **What is drifting:** `plan/phase_notes/phase3_discovery.md` now labels opening language priors and gives matched-seed comparisons in prose, but iter 14 still does not include the required explicit `### Matched baseline comparisons` section with first-three-turn side-by-side reads for each seed.
- **What plan.md says it should be:** Do not infer cross-lingual interaction drift from turn-1 differences. For each seed, read `idus_idid`, `idus_enen`, and `idus_nat` side by side, describe the first three turns, then separate opening language prior, monolingual movement, and candidate cross-lingual excess movement.
- **What to fix:** Discovery should add explicit baseline-read sections for seeds 223 and 227 before Phase 4. Current notes are useful but still insufficient for the dialogue-level baseline-comparison checkbox.

### Drift flag (phase=3 iter=14)

- **What is drifting:** The project anchor and active goals still disagree in scope. `plan/plan.md` is mainly a two-language EN-ID anchor and describes Phase 0 as language-prior screening, while `goals.md`, current agents, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core design is the value x language factorial for channel/content decomposition, but it has not been formally updated to the three-culture/ZH expansion now driving the harness.
- **What to fix:** Researcher decision required before Phase 5: either update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future scripts back to the two-language EN-ID anchor. I did not rewrite the anchor or remove the expanded cells unilaterally because that changes study scope.

### Drift flag (phase=3 iter=14)

- **What is drifting:** `agents/coding.sh` Phase 2 instructions still said "generate 3 new transcripts," while `goals.md` now specifies 30-100 transcripts per validity iter.
- **What plan/goals say it should be:** Phase 2 validity should use the batch size specified in `goals.md`; currently that is 30-100 transcripts per iter.
- **What was fixed:** Updated `agents/coding.sh` so future Phase 2 coding prompts say to generate a validity batch at the size specified in `goals.md`, rather than hard-coding 3 transcripts.

### Checkboxes updated

No completed checkbox was newly marked `[x]`. The Phase 3 per-turn-logits, flip-turn, concession-tally, opening-prior split, cross-cell trajectory, qualitative-finding, and golden-copy checkboxes remain supported by artifacts. The full Phase 3 batch gate, explicit dialogue-level baseline comparison, and natural-vs-inverted comparison remain incomplete because iter 14 still lacks the required cells and explicit baseline section.

## Status (phase=3 iter=14): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=17) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT in the active prompt config and iter 17 artifacts. `config/prompts.json` still separates cultural identity (`country`) from generation language (`lang`), and iter 17 raw transcripts save `agent_A.country`, `agent_A.lang`, `agent_B.country`, and `agent_B.lang` separately. The persona prompt asks for an honest country-shaped perspective; it does not assign a target stance.

**Prompt integrity:** No prompt edit was needed. The language/script rule remains conditional by generation language: Indonesian/English use Latin alphabet only, while Mandarin Chinese remains available for future ZH cells. This preserves language-holding without making the planned CN/ZH cells impossible.

**Judge scoring relevance:** APPROPRIATE as supporting evidence. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ4 discovery. They still cannot substitute for matched transcript reading before causal claims.

**Phase 3 iter 17 artifacts verified:** `artifacts/transcripts/phase3_iter17_manifest.txt` exists and lists 8 raw transcripts: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, each with seeds 251 and 257. The raw transcript files contain saved config, persona/language fields, six debate turns, `p_agree`, and digit logits. Golden copies exist for all eight iter 17 transcripts. `plan/phase_notes/phase3_discovery.md` includes a Discovery iter 17 section with flip turns, concession tallies, cell comparisons, and qualitative findings.

## Drift flag (phase=3 iter=17)

- **What is drifting:** Phase 3 is still running the reduced 4-cell / 2-seed ID-US pilot grid. Iter 17 again omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale. This is useful discovery material, but it still cannot satisfy the Phase 3 full-batch gate or the natural-vs-inverted contrast needed for RQ2.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. Matched monolingual baselines are necessary, and asymmetry cannot be tested from natural-only cross-lingual cells.
- **What was fixed:** Updated `goals.md` so the reduced-pilot caveat now covers iters 0-17. Tightened `agents/coding.sh` to state a concrete minimum non-pilot Phase 3 batch size of 70 jobs (7 cells x 10 seeds) and to require a blocker note instead of silently submitting another reduced batch if resources are limiting.

## Drift flag (phase=3 iter=17)

- **What is drifting:** `plan/phase_notes/phase3_discovery.md` now gives useful matched-seed comparison prose for iter 17, but it still does not include the required explicit `### Matched baseline comparisons` section with `seed <S> baseline read` bullets describing turns 1-3 of `idus_idid`, `idus_enen`, and `idus_nat` side by side.
- **What plan.md says it should be:** Do not infer cross-lingual interaction drift from turn-1 differences. For each seed, read the matched monolingual baselines and cross-lingual cell side by side, describe the first three turns, and separate opening language prior, monolingual movement, and candidate cross-lingual excess movement.
- **What to fix:** Discovery should add explicit baseline-read sections for seeds 251 and 257 before Phase 4. Current notes correctly temper the natural-cell causation story, but they are not yet sufficient for the dialogue-level baseline-comparison checkbox.

## Drift flag (phase=3 iter=17)

- **What is drifting:** The project anchor and active coordination docs still disagree in scope. `plan/plan.md` remains primarily a two-language EN-ID anchor and describes Phase 0 as language-prior screening, while `goals.md`, agent prompts, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core design is the value x language factorial for channel/content decomposition, but it has not been formally updated to authorize the three-culture/ZH expansion now driving the harness.
- **What to fix:** This remains a researcher decision before Phase 5: either update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future scripts back to the two-language EN-ID anchor. I did not rewrite the anchor or remove expanded cells because that would change study scope.

### Checkboxes updated

No completed checkbox was newly marked `[x]`. I updated the text of the unchecked Phase 3 full-batch gate to say reduced 4-cell / 2-seed batches through iter 17 are discovery pilots. The following remain incomplete: full Phase 3 batch coverage/scale, explicit dialogue-level baseline comparison, natural-vs-inverted comparison, Phase 4 probe sanity, and Phase 5 metrics/paper tasks.

## Status (phase=3 iter=17): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=20) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT in the active prompts and iter 20 artifacts. `config/prompts.json` keeps `country` persona and `lang` generation language separate, and the raw iter 20 transcripts save both fields independently for each agent and turn. The persona prompt asks for an honest country-shaped perspective; it does not assign a stance to defend.

**Prompt integrity:** No `config/prompts.json` edit was needed. The prompt still supports future Mandarin Chinese cells by making the script rule conditional on generation language rather than banning non-Latin script globally.

**Judge scoring relevance:** APPROPRIATE as supporting evidence. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ4 discovery, but they cannot replace matched transcript reading before causal claims.

**Phase 3 iter 20 artifacts verified:** `artifacts/transcripts/phase3_iter20_manifest.txt` exists and lists 8 raw transcripts: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln`, with seeds 281 and 283. The raw transcripts contain saved config, persona/language fields, six debate turns, `p_agree`, and digit logits. Golden copies exist for notable iter 20 transcripts.

## Drift flag (phase=3 iter=20)

- **What is drifting:** Phase 3 is still running the reduced 4-cell / 2-seed ID-US pilot grid. Iter 20 again omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale. This remains useful qualitative discovery, but it does not satisfy the Phase 3 full-batch gate and cannot test the natural-vs-inverted RQ2 contrast.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. Matched monolingual baselines are necessary, and asymmetry cannot be established from natural-only cross-lingual cells.
- **What was fixed:** Updated `goals.md` so the reduced-pilot caveat now covers iters 0-20. Tightened `agents/coding.sh` so future Phase 3 coding prompts say that, from iter 18 onward, another reduced ID-US-only pilot should not be produced as if it advances Phase 3; the coding agent should either run the full 70+ job batch or record the blocker.

## Drift flag (phase=3 iter=20)

- **What is drifting:** `plan/phase_notes/phase3_discovery.md` includes useful matched-seed comparison prose for iter 20, but it still omits the explicit mandatory `### Matched baseline comparisons` section with `seed <S> baseline read` bullets describing turns 1-3 of `idus_idid`, `idus_enen`, and `idus_nat` side by side. It also omits the explicit `### Opening-prior vs interaction-drift split` heading for the iter.
- **What plan.md says it should be:** Do not infer cross-lingual interaction drift from turn-1 differences. For each seed, read matched monolingual baselines and the cross-lingual cell side by side, describe the first three turns, and separate opening language prior, monolingual movement, and candidate cross-lingual excess movement.
- **What was fixed:** Tightened `agents/discovery.sh` so those section headings are mandatory and the supervisor checklist remains incomplete unless they appear explicitly.

## Drift flag (phase=3 iter=20)

- **What is drifting:** The project anchor and active coordination docs still disagree in scope. `plan/plan.md` remains primarily a two-language EN-ID anchor and describes Phase 0 as language-prior screening, while `goals.md`, agent prompts, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core design is the value x language factorial for channel/content decomposition, but it has not been formally updated to authorize the three-culture/ZH expansion now driving the harness.
- **What to fix:** Researcher decision required before Phase 5: either update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future scripts back to the two-language EN-ID anchor. I did not rewrite the anchor or remove expanded cells because that would change study scope.

### Checkboxes updated

Updated `goals.md` only to reflect verified non-completion: the reduced 4-cell / 2-seed pilot caveat now covers iters 0-20. No unchecked checkbox was marked complete. The following remain incomplete: full Phase 3 coverage/scale, explicit dialogue-level baseline comparison, natural-vs-inverted comparison, Phase 4 probe sanity, and Phase 5 metrics/paper tasks.

## Status (phase=3 iter=20): NEEDS HUMAN REVIEW
---

## Review (phase=3 iter=23) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` separates `country` and `lang`; iter23 raw transcripts save persona/language separately for each agent. No prompt tells a persona to defend a fixed position. The persona prompt is more elaborated than the minimal anchor, but it remains identity/perspective guidance rather than stance forcing.

**Prompt integrity:** No `config/prompts.json` change needed. The language instruction remains separate from persona. The script rule is conditional, so it preserves Indonesian/English Latin-only behavior while still allowing future Mandarin Chinese cells.

**Judge scoring relevance:** APPROPRIATE as supporting evidence only. Position, movement, engagement, firmness, drift direction, and flip turn are relevant to RQ1-RQ4 discovery, but they cannot substitute for matched transcript reads and monolingual-baseline adjustment.

**Phase 3 iter23 artifacts verified:** `artifacts/transcripts/phase3_iter23_manifest.txt` lists 8 raw transcripts: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 317 and 331. Raw files contain config, persona/language fields, six debate turns, `p_agree`, digit logits, and digit probabilities. Golden copies exist. No Phase 3 artifacts exist for `idus_inv`, `cnus_nat`, or `cnid_nat`.

## Drift flag (phase=3 iter=23)

- **What is drifting:** Phase 3 still ran the reduced 4-cell / 2-seed ID-US pilot grid. Iter23 omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and 10+ seeds per cell. This cannot satisfy the active Phase 3 full-batch gate or the RQ2 natural-vs-inverted contrast.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. Asymmetry cannot be established from natural cells alone; it needs monolingual baselines and language-direction comparisons.
- **What was fixed:** Confirmed `goals.md` keeps the full-batch checkbox unchecked and labels iters 0-23 as reduced pilots. Tightened `agents/coding.sh` so iter >= 24 must either run the full 70+ job batch or record a blocker, and must not run another reduced 4-cell / 2-seed batch as if it advanced Phase 3.

## Drift flag (phase=3 iter=23)

- **What is drifting:** `phase3_discovery.md` has useful matched-seed comparison prose for iter23, but still lacks the explicit required dialogue-level baseline section with first-three-turn side-by-side reads for each matched seed.
- **What plan.md says it should be:** Turn-1 gaps are generation-language priors. Cross-lingual causation requires reading `idus_idid`, `idus_enen`, and `idus_nat` side by side, then separating opening prior, monolingual movement, and candidate cross-lingual excess movement.
- **What to fix:** Discovery should add explicit baseline-read sections for seeds 317 and 331 before Phase 4. Current prose correctly tempers natural-cell claims, but the dialogue-level baseline checkbox stays incomplete.

## Drift flag (phase=3 iter=23)

- **What is drifting:** The project anchor and active goals still conflict. Actual `plan/plan.md` is mostly an EN-ID two-language anchor, while `goals.md`, agent instructions, and current task gates implement a three-culture ID/US/CN design with ZH cells.
- **What plan.md says it should be:** `plan/plan.md` is ground truth. Its core value x language decomposition is compatible with expansion, but the document has not formally authorized the three-culture/ZH scope.
- **What to fix:** The researcher should reconcile this before Phase 5: either update `plan/plan.md` to authorize the three-culture/ZH design or reduce `goals.md` and future runs to the EN-ID scope. I did not unilaterally rewrite the anchor or downscope active goals because that is a scope-level research decision.

### Checkboxes updated

No unchecked checkbox was marked complete. `goals.md` already reflects verified non-completion: the reduced-pilot caveat covers iters 0-23, and the full Phase 3 coverage/scale checkbox remains unchecked. Explicit dialogue-level baseline comparison, natural-vs-inverted comparison, Phase 4, and Phase 5 remain incomplete.

## Status (phase=3 iter=23): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=26) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps the country/persona prompt separate from the generation-language instruction, and the iter 26 raw transcripts save `country` and `lang` independently for each agent. The persona prompt asks for an honest country-shaped perspective; it does not assign a stance.

**Prompt integrity:** No prompt edit was needed. The script rule remains conditional by generation language, so Indonesian/English remain Latin-only while future Mandarin Chinese cells remain possible.

**Judge scoring relevance:** APPROPRIATE as supporting evidence only. Position, movement, engagement, firmness, drift direction, and flip turn are relevant to RQ1-RQ4 discovery, but they do not replace matched transcript reading or monolingual-baseline adjustment.

**Phase 3 iter 26 artifacts verified:** `artifacts/transcripts/phase3_iter26_manifest.txt` lists 8 raw transcripts: `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 359 and 367. The raw files contain saved config, persona/language fields, six debate turns, per-turn `p_agree`, and digit logits. No iter 26 raw artifacts exist for `idus_inv`, `cnus_nat`, or `cnid_nat`.

## Drift flag (phase=3 iter=26)

- **What is drifting:** Phase 3 again ran the reduced 4-cell / 2-seed ID-US pilot grid, even though the coding-agent prompt has treated iter >=24 as a hard gate. Iter 26 omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale. This produces useful qualitative material, but it still cannot satisfy the Phase 3 full-batch gate or test the natural-vs-inverted RQ2 contrast.
- **What plan.md says it should be:** The core claim requires a value x language factorial that separates channel from content. Asymmetry cannot be established from natural cells alone; it needs monolingual baselines and language-direction comparisons.
- **What was fixed:** Updated `goals.md` so the reduced-pilot caveat now covers iters 0-26 and explicitly notes that the next coding run should either run the full 70+ job batch or record the blocker in `plan/loop_notes.md`.

## Drift flag (phase=3 iter=26)

- **What is drifting:** `phase3_discovery.md` includes useful matched-seed comparison prose for iter 26, but it still lacks the explicit required `### Matched baseline comparisons` section with per-seed first-three-turn baseline reads, and it lacks the explicit `### Opening-prior vs interaction-drift split` section. The notes correctly avoid overclaiming natural-cell causation, but the dialogue-level baseline checkbox stays incomplete.
- **What plan.md says it should be:** Turn-1 gaps are generation-language priors. Cross-lingual causation requires reading `idus_idid`, `idus_enen`, and `idus_nat` side by side, then separating opening prior, monolingual movement, and candidate cross-lingual excess movement.
- **What to fix:** Discovery should add explicit baseline-read sections for seeds 359 and 367 before Phase 4. Current prose is directionally correct, but it is not the systematic dialogue-level baseline record required by the checklist.

## Drift flag (phase=3 iter=26)

- **What is drifting:** The project anchor and active goals still conflict in scope. `plan/plan.md` remains mostly an EN-ID two-language anchor and describes Phase 0 as language-prior screening, while `goals.md`, agent instructions, and current gates implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is ground truth. Its value x language decomposition is compatible with expansion, but the document has not formally authorized the three-culture/ZH scope now driving the harness.
- **What to fix:** Researcher decision required before Phase 5: update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future runs to the EN-ID scope. I did not rewrite the anchor or downscope active goals because that changes the study scope.

### Checkboxes updated

No unchecked checkbox was marked complete. `goals.md` was updated only to reflect verified non-completion: reduced 4-cell / 2-seed batches through iter 26 remain pilots. Full Phase 3 coverage/scale, explicit dialogue-level baseline comparison, natural-vs-inverted comparison, Phase 4, and Phase 5 remain incomplete.

## Status (phase=3 iter=26): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=29) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps `country`/persona separate from generation `lang`, and the iter 29 raw transcripts save both fields independently. The prompt asks for an honest country-shaped perspective; it does not assign an agent a stance to defend.

**Prompt integrity:** No `config/prompts.json` change was needed. The script rule remains conditional by generation language, so Indonesian/English remain Latin-only while Mandarin Chinese remains possible for ZH cells.

**Judge scoring relevance:** APPROPRIATE as supporting discovery evidence only. Position, movement, engagement, firmness, drift direction, and flip turns are relevant to RQ1-RQ4, but they cannot replace matched transcript reads or monolingual-baseline adjustment before causal claims.

**Phase 3 artifacts verified:** Iter 27 now satisfies the Phase 3 scale/cell gate: `artifacts/transcripts/phase3_iter27_manifest.txt` lists 70 raw transcripts, covering `idus_enen`, `idus_idid`, `idus_nat`, `idus_inv`, `id_aln`, `cnus_nat`, and `cnid_nat` with 10 seeds per cell. Iter 29 is a reduced follow-up sample only: 8 raw transcripts across `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 443 and 449.

## Drift flag (phase=3 iter=29)

- **What is drifting:** After the full iter 27 grid satisfied the Phase 3 coverage gate, iters 28 and 29 reverted to the reduced 4-cell / 2-seed ID-US-only grid. Iter 29 omitted `idus_inv`, `cnus_nat`, `cnid_nat`, and the 10+ seeds-per-cell scale. This does not undo iter 27, but it should be treated as targeted qualitative sampling rather than normal Phase 3 progress.
- **What plan.md says it should be:** The core claim requires value x language comparisons with monolingual baselines and language-direction contrasts. RQ2 especially needs natural-vs-inverted evidence, not only natural ID-US cells.
- **What was fixed:** Marked the Phase 3 full-batch gate complete in `goals.md` based on verified iter 27 artifacts, and added a guard to `agents/coding.sh` that reduced post-gate batches are allowed only as explicitly requested non-gating qualitative samples.

## Drift flag (phase=3 iter=29)

- **What is drifting:** `phase3_discovery.md` has useful matched-seed comparison prose, including iter 29 matched comparisons, but the checklist item requiring explicit first-three-turn side-by-side reads for `idus_idid`, `idus_enen`, and `idus_nat` remains incomplete. The notes correctly label turn-1 gaps as generation-language priors, but they are not yet the systematic dialogue-level baseline record the checklist asks for.
- **What plan.md says it should be:** Do not call turn-1 differences interaction drift. For each matched seed, read monolingual baselines and the cross-lingual cell side by side, describe the early dialogue trajectory, and separate opening prior, monolingual movement, and candidate cross-lingual excess movement.
- **What to fix:** Discovery should add explicit baseline-read entries before Phase 4/5 if those cases will support causal claims. I left that checkbox unchecked.

## Drift flag (phase=3 iter=29)

- **What is drifting:** The project anchor and active goals still conflict in scope. `plan/plan.md` remains mostly an EN-ID two-language anchor and describes Phase 0 as language-prior screening, while `goals.md`, agent instructions, and current artifacts implement a three-culture ID/US/CN design with ZH cells and persona-based Phase 0 screening.
- **What plan.md says it should be:** `plan/plan.md` is ground truth. Its value x language decomposition is compatible with expansion, but the document has not formally authorized the three-culture/ZH scope now driving the harness.
- **What to fix:** Researcher decision required before Phase 5: update `plan/plan.md` to authorize the three-culture/ZH design, or reduce `goals.md` and future runs to the EN-ID scope. I did not rewrite the anchor or downscope active goals because that changes study scope.

### Checkboxes updated

Marked the Phase 3 full coverage/scale gate complete based on iter 27's verified 70-transcript, 7-cell, 10-seed-per-cell batch. Marked the qualitative natural-vs-inverted comparison complete based on iter 27 `idus_nat` vs `idus_inv` notes, while leaving the Phase 5 quantitative baseline-adjusted metric separate. Kept the explicit dialogue-level first-three-turn baseline checkbox unchecked.

## Status (phase=3 iter=29): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=32) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps the persona prompt (`country`) separate from the generation-language instruction (`lang`). The prompt asks for an honest country-shaped perspective and does not assign a value position to defend.

**Prompt integrity:** No `config/prompts.json` change was needed. The current language/script rule is conditional by generation language: Indonesian/English require Latin script; Mandarin Chinese requires Chinese characters. This supports the current ID/EN/ZH design without conflating persona and language.

**Agent instructions:** Mostly aligned. `agents/coding.sh` now instructs Phase 3 to run the full 7-cell / 10-seed gate and to treat reduced post-gate batches only as explicitly requested non-gating qualitative samples. `agents/discovery.sh` correctly asks for natural, inverted, monolingual, and aligned comparisons, including opening-prior vs interaction-drift separation.

**Judge scoring relevance:** Appropriate as supporting discovery evidence only. Position, movement, engagement, firmness, drift direction, and flip turns are relevant to RQ1-RQ3, but they cannot establish RQ4 or replace bilingual P(agree) measurement and baseline-adjusted metrics in Phase 5.

**Artifacts verified:** Iter 27 satisfies the Phase 3 coverage gate with 70 raw non-judgment transcripts: 10 each for `idus_enen`, `idus_idid`, `idus_nat`, `idus_inv`, `id_aln`, `cnus_nat`, and `cnid_nat`, plus `artifacts/transcripts/phase3_iter27_manifest.txt`. Iter 32 is a reduced follow-up sample only: 8 raw non-judgment transcripts, covering `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 479 and 487, plus `artifacts/transcripts/phase3_iter32_manifest.txt`.

## Drift flag (phase=3 iter=32)

- **What is drifting:** `plan/plan.md` and the active harness design still disagree in scope. `plan/plan.md` describes Phase 0 as screening EN/ID language priors and presents a mostly two-language EN-ID factorial, while `goals.md`, `agents/*.sh`, and the artifacts implement a three-culture ID/US/CN design with persona-based Phase 0 screening in English and ZH generation cells.
- **What plan.md says it should be:** `plan/plan.md` is the stated ground truth. Its channel-vs-content logic is compatible with the current expansion, but the anchor has not formally authorized the three-culture/ZH scope or the persona-only English Phase 0 screening now used by the harness.
- **What to fix:** Before Phase 5 or paper writing, the researcher should reconcile the anchor: either update `plan/plan.md` to authorize the current three-culture design, or downscope `goals.md` and future runs to the EN-ID anchor. I did not edit `plan/plan.md` because the supervisor edit authority for this turn is limited to `goals.md`, `config/prompts.json`, and `agents/*.sh`.

## Drift flag (phase=3 iter=32)

- **What is drifting:** Iter 32, like iters 28-31, is a reduced 4-cell / 2-seed ID-US sample. It omits `idus_inv`, `cnus_nat`, and `cnid_nat`, so it cannot add new natural-vs-inverted or CN evidence.
- **What plan.md says it should be:** The core RQ2 claim requires language-direction evidence and monolingual baselines; natural-cell observations alone cannot establish asymmetric channel drift.
- **What was fixed:** Updated `goals.md` so the post-gate reduced-sample caveat covers iters 28-32. Iter 27 remains the verified full Phase 3 gate run; iter 32 should be treated as targeted qualitative material only.

## Drift flag (phase=3 iter=32)

- **What is drifting:** `phase3_discovery.md` for iter 32 contains useful matched-seed comparison prose and correctly labels turn-1 gaps as generation-language priors, but it does not use the explicit mandatory `### Matched baseline comparisons` and `### Opening-prior vs interaction-drift split` sections requested by `agents/discovery.sh`. The goals checkbox requiring first-three-turn side-by-side baseline reads therefore remains incomplete.
- **What plan.md says it should be:** Do not call turn-1 differences cross-lingual interaction drift. For each matched seed, compare `idus_idid`, `idus_enen`, and `idus_nat` side by side and write the early dialogue trajectory before making causal claims.
- **What to fix:** Before Phase 4/5, add an explicit baseline-read section for the matched seeds that will support causal claims. Current prose is directionally correct, but it is not yet the systematic evidence log required by the checklist.

### Checkboxes updated

No unchecked checkbox was marked complete. `goals.md` was updated only to correct the verified description of post-gate reduced samples: iters 28-32 are targeted non-gating discovery samples. The explicit dialogue-level first-three-turn baseline checkbox remains unchecked, as do Phase 4 and Phase 5.

## Status (phase=3 iter=32): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=35) — 2026-07-01

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps country/persona as `{country}` and generation language as `{lang}` / `{my_lang}`. The debate prompt asks for an honest country-shaped perspective and does not instruct either persona to defend a predetermined value position.

**Prompt integrity:** No `config/prompts.json` edit was needed. The language/script rule is conditional by generation language: Indonesian/English require Latin script, Mandarin Chinese requires Chinese characters. Mixed-script artifacts in transcripts remain discovery observations, not prompt fixes during Phase 3.

**Agent instructions:** Mostly aligned. `agents/coding.sh` and `agents/discovery.sh` continue to separate persona from language and call for monolingual baselines, natural/inverted comparisons, aligned-persona leakage, and opening-prior vs interaction-drift separation. Judge scores remain useful discovery metadata only; they do not replace matched transcript reading or Phase 5 bilingual measurement.

**Artifacts verified:** Iter 27 still satisfies the Phase 3 coverage gate with 70 raw non-judgment transcripts across `idus_enen`, `idus_idid`, `idus_nat`, `idus_inv`, `id_aln`, `cnus_nat`, and `cnid_nat`, plus `artifacts/transcripts/phase3_iter27_manifest.txt`. Iter 35 is a reduced follow-up sample only: `artifacts/transcripts/phase3_iter35_manifest.txt` lists 8 raw transcripts across `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 521 and 523.

## Drift flag (phase=3 iter=35)

- **What is drifting:** `plan/plan.md` and the active harness design still disagree in scope. The anchor describes Phase 0 as EN/ID language-prior screening and presents a mostly two-language EN-ID factorial, while `goals.md`, agents, and artifacts implement a three-culture ID/US/CN design with persona-based English screening and ZH generation cells.
- **What plan.md says it should be:** `plan/plan.md` is the stated ground truth. Its channel-vs-content logic is compatible with expansion, but the three-culture/ZH scope and persona-only English Phase 0 screen are not formally authorized in the anchor.
- **What to fix:** Before Phase 5 or paper writing, the researcher should either update `plan/plan.md` to authorize the current three-culture design or downscope `goals.md` and future runs to the EN-ID anchor. I did not edit the anchor because this supervisor turn only authorizes edits to `goals.md`, `config/prompts.json`, and `agents/*.sh`.

## Drift flag (phase=3 iter=35)

- **What is drifting:** Iter 35, like iters 28-34, is a reduced 4-cell / 2-seed ID-US sample. It omits `idus_inv`, `cnus_nat`, and `cnid_nat`, so it cannot add new natural-vs-inverted or CN evidence.
- **What plan.md says it should be:** The core RQ2 claim requires language-direction evidence and monolingual baselines; natural-cell observations alone cannot establish asymmetric channel drift.
- **What was fixed:** Updated `goals.md` so the post-gate reduced-sample caveat covers iters 28-35. Iter 27 remains the verified full Phase 3 gate run; iter 35 should be treated as targeted qualitative material only.

## Drift flag (phase=3 iter=35)

- **What is drifting:** `phase3_discovery.md` for iter 35 contains useful matched-seed comparison prose and correctly labels turn-1 gaps as generation-language priors, but it still does not provide the explicit first-three-turn side-by-side baseline record required by the checklist item.
- **What plan.md says it should be:** Do not call turn-1 differences cross-lingual interaction drift. For each matched seed used in a causal claim, compare `idus_idid`, `idus_enen`, and `idus_nat` side by side and record the early dialogue trajectory before claiming cross-lingual excess movement.
- **What to fix:** Keep the dialogue-level baseline checkbox unchecked until the explicit first-three-turn baseline entries are written for the seeds that will support causal claims.

### Checkboxes updated

No unchecked checkbox was marked complete. `goals.md` was updated only to correct the verified description of post-gate reduced samples: iters 28-35 are targeted non-gating discovery samples. Phase 3 dialogue-level baseline comparison, Phase 4, and Phase 5 remain incomplete.

## Status (phase=3 iter=35): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=38) — 2026-07-02

### Research alignment check

**Persona != language:** INTACT in the prompt and block config. `config/prompts.json` keeps the country/persona prompt separate from the generation-language instruction, and `config/discovery_blocks.json` explicitly defines persona/language as independent fields for each agent.

**Prompt integrity:** No `config/prompts.json` change was needed. The prompt asks for an honest country-shaped perspective and a clear agree/disagree opening, but it does not assign a fixed side to any persona. The language/script rule is conditional on requested generation language.

**Judge scoring relevance:** Appropriate as discovery metadata only. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ3. They still cannot replace matched transcript reading or Phase 5 bilingual P(agree) measurement for RQ4.

**Artifacts verified:** Iter 38 produced 8 raw non-judgment transcripts plus 8 judgment files and a manifest. The raw files cover `idus_enen`, `idus_idid`, `idus_nat`, and `id_aln` for seeds 569 and 571. There is no `idus_inv` file and no 10-seed active block for iter 38, so the current P3-R1 Phase 3 checkboxes remain incomplete.

## Drift flag (phase=3 iter=38)

- **What is drifting:** The active repository instructions now define Phase 3 as an OpenAI-backed matched-block loop, while the project anchor and standing project context still emphasize the original validated debate environment and Modal/Qwen inference path. This is a design/infrastructure scope change, not just an implementation detail, because OpenAI transcripts save parsed Likert digits instead of the Qwen digit logits that Phase 4/5 probe sanity was designed to validate.
- **What plan.md says it should be:** The anchor says the environment is the experiment, metrics are deliberately last, and probe sanity must be earned before trusting numbers. It also frames the core behavioral paper around the value x language factorial, matched monolingual baselines, and RQ4 bilingual measurement. Changing provider/probe semantics must be explicitly authorized before downstream causal or metric claims.
- **What to fix:** Researcher decision required before Phase 4/5: either update `plan/plan.md` to authorize the OpenAI matched-block path and specify how parsed Likert digits replace or coexist with Qwen digit logits, or restore the active Phase 3/5 goals and agent instructions to the Modal/Qwen path. I did not rewrite the anchor or silently downscope the active OpenAI runner.

## Drift flag (phase=3 iter=38)

- **What is drifting:** Iter 38 is another reduced 4-cell / 2-seed ID-US sample. Under the current restarted `goals.md`, active block P3-R1 requires `idus_enen`, `idus_idid`, `idus_nat`, and `idus_inv` with 10 matched seeds per cell. Iter 38 omits `idus_inv` and has only 2 seeds.
- **What plan.md says it should be:** Causal channel claims require matched monolingual baselines and language-direction contrasts. Natural-cell observations without the inverted cell cannot establish RQ2 asymmetry.
- **What to fix:** Treat iter 38 as qualitative history only. Do not mark the active P3-R1 generation, manifest, probe-output, or discovery-analysis checkboxes complete from iter 38. The next Phase 3 run should either execute the configured P3-R1 block or record the blocker in `plan/loop_notes.md`.

## Drift flag (phase=3 iter=38)

- **What is drifting:** `phase3_discovery.md` for iter 38 contains useful matched-seed prose and labels turn-1 gaps as generation-language priors, but it still does not provide the explicit seed-level baseline matrix or first-three-turn side-by-side record required by the current Phase 3 checklist.
- **What plan.md says it should be:** Do not call turn-1 differences cross-lingual interaction drift. For each seed used in a causal claim, read the monolingual baselines and cross-lingual cells side by side and record early trajectory before labeling candidate excess movement.
- **What to fix:** Keep the dialogue-level baseline checkbox unchecked until a `### Seed-level baseline matrix` section and first-three-turn comparison entries exist for the matched seeds that will support causal claims.

### Checkboxes updated

No unchecked checkbox was marked complete. Iter 38 artifacts do not satisfy the current P3-R1 active-block gate, and the required explicit baseline matrix / first-three-turn comparison sections are still missing. Phase 4 and Phase 5 remain incomplete.

## Status (phase=3 iter=38): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=41) - 2026-07-02

### Research alignment check

**Persona != language:** INTACT in the active prompts and block config. `config/prompts.json` keeps cultural identity (`{country}`) separate from generation language (`{lang}` / `{my_lang}`), and `config/discovery_blocks.json` defines each agent with independent `country` and `lang` fields. No prompt assigns a target value position to a persona.

**Current Phase 3 block design:** STRUCTURALLY ALIGNED. The active `p3_r1_id_us_pairwise` block has the required ID/US matched cells: `idus_idid`, `idus_enen`, `idus_nat`, and `idus_inv`, all on the same item, turn order, and 10-seed list. This is the right baseline-controlled shape for separating opening language priors from candidate cross-lingual interaction drift.

**Artifact status:** BLOCKED, not complete. `plan/loop_notes.md` records iter 40 and iter 41 as blocked before the first API response because of local DNS/network resolution failure. No `artifacts/transcripts/phase3_iter40*` or `phase3_iter41*` files exist, and no manifests exist for either iteration. Therefore the active P3-R1 generation, per-turn probe, transcript-save, and manifest checkboxes must stay unchecked.

**Judge scoring relevance:** APPROPRIATE as supporting metadata only. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ3 discovery. They still do not satisfy RQ4, which requires measurement-language counterbalancing before Phase 5 claims.

## Drift flag (phase=3 iter=41)

- **What is drifting:** The project anchor and active coordination docs still disagree in scope and provider. `plan/plan.md` describes the original EN-ID behavioral design and Phase 0 language-prior screening, while `goals.md`, `config/discovery_blocks.json`, and agent instructions implement a three-culture ID/US/CN design, persona-based English Phase 0 screening, ZH-capable cells, and an OpenAI Responses API Phase 3 path with parsed Likert digits.
- **What plan.md says it should be:** `plan/plan.md` is the ground truth. Its core contribution is a value x language factorial with matched monolingual baselines, read-before-measure discipline, and Phase 4 probe sanity before trusting trajectory numbers.
- **What to fix:** Before Phase 5 or paper writing, reconcile the anchor with the active harness: either update `plan/plan.md` to authorize the three-culture/OpenAI path and specify how parsed Likert digits are calibrated against the original Qwen digit-logit probe, or downscope `goals.md`/future runs back to the EN-ID/Qwen plan. I did not edit the anchor because this supervisor role is authorized to edit `goals.md`, `config/prompts.json`, and `agents/*.sh`, not `plan/plan.md`.

## Drift flag (phase=3 iter=41)

- **What is drifting:** Phase 3 has not yet produced the restarted active P3-R1 OpenAI matched block. Iter 40 and iter 41 are blocked infrastructure attempts, not evidence.
- **What plan.md says it should be:** Discovery may record blockers, but causal channel claims require actual matched transcripts: mono-ID, mono-EN, natural cross, and inverted cross for the same seed/item/personas.
- **What to fix:** Keep the active Phase 3 checkboxes unchecked until a manifest and the 40 expected transcript files exist. The next run should either resolve local DNS/API access and run `p3_r1_id_us_pairwise`, or record another blocker without treating prior reduced Qwen samples as completion of the restarted OpenAI block.

### Checkboxes updated

Marked only `Copy notable transcripts -> artifacts/golden/` complete in `goals.md`, because `artifacts/golden/` contains copied Phase 3 transcripts. No active P3-R1 generation, probe-output, transcript-save, manifest, optional sweep, or 3/4-agent checkbox was marked complete.

## Status (phase=3 iter=41): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=44) - 2026-07-02

### Research alignment check

**Persona != language:** INTACT in the active prompt and block configuration. `config/prompts.json` keeps cultural identity (`{country}`) separate from generation language (`{lang}` / `{my_lang}`), and `config/discovery_blocks.json` defines each agent with independent `country` and `lang` fields. The prompt asks for an honest country-shaped perspective and does not assign a fixed value position to any persona.

**Current Phase 3 block design:** STRUCTURALLY ALIGNED. The active `p3_r1_id_us_pairwise` block contains the required ID/US matched cells: `idus_idid`, `idus_enen`, `idus_nat`, and `idus_inv`, all on the same item (`society_over_individual`), same agent order, same turn count, and same 10 seeds. This is the correct matched-baseline shape for separating opening language priors from candidate cross-lingual interaction drift.

**Artifact status:** BLOCKED, not complete. `plan/loop_notes.md` records iter 44 as blocked before the first API response because of local DNS/network resolution failure. No `artifacts/transcripts/phase3_iter44_*.json` files exist, and no `artifacts/transcripts/phase3_iter44_manifest.txt` exists. Therefore the active P3-R1 generation, per-turn probe-output, transcript-save, manifest, and discovery-analysis checkboxes must remain unchecked.

**Judge scoring relevance:** APPROPRIATE as supporting metadata only. Position, movement, engagement, firmness, drift direction, and flip turn remain relevant to RQ1-RQ3 discovery. They still do not satisfy RQ4, which requires measurement-language counterbalancing before Phase 5 claims.

## Drift flag (phase=3 iter=44)

- **What is drifting:** The project anchor and active coordination docs still disagree in scope and provider. `plan/plan.md` describes the original EN-ID behavioral design and Phase 0 language-prior screening, while `goals.md`, `config/discovery_blocks.json`, and agent instructions implement a three-culture ID/US/CN design, persona-based English Phase 0 screening, ZH-capable cells, and an OpenAI Responses API Phase 3 path with parsed Likert digits.
- **What plan.md says it should be:** `plan/plan.md` is the stated ground truth. Its core contribution is a value x language factorial with matched monolingual baselines, read-before-measure discipline, and Phase 4 probe sanity before trusting trajectory numbers.
- **What to fix:** Before Phase 5 or paper writing, reconcile the anchor with the active harness: either update `plan/plan.md` to authorize the three-culture/OpenAI path and specify how parsed Likert digits are calibrated against the original Qwen digit-logit probe, or downscope `goals.md` and future runs back to the EN-ID/Qwen plan. I did not edit `plan/plan.md` because this supervisor role is authorized to edit `goals.md`, `config/prompts.json`, and `agents/*.sh`, not the anchor.

## Drift flag (phase=3 iter=44)

- **What is drifting:** Phase 3 has still not produced the restarted active P3-R1 OpenAI matched block. Iters 40-44 are infrastructure-blocked attempts, not behavioral evidence.
- **What plan.md says it should be:** Discovery may record blockers, but causal channel claims require actual matched transcripts: mono-ID, mono-EN, natural cross, and inverted cross for the same seed/item/personas.
- **What to fix:** Keep the active Phase 3 checkboxes unchecked until a manifest and the 40 expected transcript files exist. The next run should either resolve local DNS/API access and run `p3_r1_id_us_pairwise`, or record another blocker without treating prior reduced Qwen samples as completion of the restarted OpenAI block.

### Checkboxes updated

No `goals.md` checkbox changed. All currently unchecked Phase 3 active-block items remain unchecked because no iter 44 transcripts or manifest exist. Phase 4 and Phase 5 remain incomplete.

## Status (phase=3 iter=44): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=47) - 2026-07-03

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps cultural identity (`{country}`) separate from generation language (`{lang}` / `{my_lang}`), and `config/discovery_blocks.json` defines `country` and `lang` independently for each agent. The active prompts ask for an honest country-shaped perspective and do not assign either persona a fixed value position to defend.

**Current Phase 3 block design:** STRUCTURALLY ALIGNED. The active `p3_r1_id_us_pairwise` block has the required matched ID/US cells: `idus_idid`, `idus_enen`, `idus_nat`, and `idus_inv`, all on the same item (`society_over_individual`), same agent order, same turn count, and same 10 seeds. This is the right shape for the channel-vs-content question: read mono-ID and mono-EN before natural/inverted cross cells, then label any cross movement as baseline explained unless it differs from both baselines.

**Artifact status:** COMPLETE for active P3-R1. `artifacts/transcripts/phase3_iter47_manifest.txt` exists and lists 40 raw transcript files: 10 each for `idus_enen`, `idus_idid`, `idus_nat`, and `idus_inv`. Matching judgment files also exist but were correctly treated as non-transcript artifacts in discovery notes. `plan/loop_notes.md` records iter 47 as PASS with generated=40 and failed=0. `plan/phase_notes/phase3_discovery.md` includes the required matched block summary, seed-level baseline matrix, matched baseline comparisons, opening-prior vs interaction-drift split, natural-vs-inverted accounting, and qualitative notes.

**Judge scoring relevance:** APPROPRIATE as supporting metadata only. Position, movement, engagement, firmness, drift direction, and flip turn still point at RQ1-RQ3 discovery phenomena, but they do not substitute for matched transcript reading, Phase 4 probe sanity, or Phase 5 bilingual measurement for RQ4.

**Current finding discipline:** INTACT. The iter 47 discovery notes do not overclaim cross-lingual causation. They correctly record that all cells open rights-first, later digit-1 movements are stronger rejection rather than concession, and apparent cross movements are baseline explained by mono-ID or mono-EN behavior.

## Drift flag (phase=3 iter=47)

- **What is drifting:** The project anchor and active harness still disagree in scope and provider. `plan/plan.md` describes the original EN-ID behavioral design and Phase 0 language-prior screening, while `goals.md`, `config/discovery_blocks.json`, agent instructions, and artifacts now implement a three-culture ID/US/CN design, persona-based English Phase 0 screening, ZH-capable cells, and an OpenAI Responses API Phase 3 path with parsed Likert digits.
- **What plan.md says it should be:** `plan/plan.md` is the stated ground truth. Its core contribution is a value x language factorial with matched monolingual baselines, read-before-measure discipline, and Phase 4 probe sanity before trusting trajectory numbers.
- **What to fix:** Before Phase 5 or paper writing, the researcher should reconcile the anchor with the active harness: either update `plan/plan.md` to authorize the three-culture/OpenAI path and specify how parsed Likert digits are calibrated against the original Qwen digit-logit probe, or downscope `goals.md` and future runs back to the EN-ID/Qwen plan. I did not edit `plan/plan.md` because this supervisor role is authorized to edit `goals.md`, `config/prompts.json`, and `agents/*.sh`, not the anchor.

## Drift flag (phase=3 iter=47)

- **What is drifting:** The active P3-R1 OpenAI block is valid as a matched discovery block, but it has no live opposed starting stance: every first turn in every cell rejects `society_over_individual`. If later agents treat this as RQ1/RQ2 evidence of channel drift, that would drift away from the causal rule.
- **What plan.md says it should be:** A cross-lingual channel claim requires a focal agent to move after receiving an other-language turn in a way not already present in both monolingual baselines. Turn-1 priors and shared floor-compressed disagreement must be recorded as priors/provider behavior, not interaction drift.
- **What to fix:** Keep iter 47 as provider/model contrast and probe-intensity evidence only. Do not advance a channel-causation or EN-ward asymmetry claim from this block. Phase 4 should use golden transcripts with clear visible concessions, and Phase 5 should not trust metrics until probe sanity is calibrated.

### Checkboxes updated

No `goals.md` checkbox changed in this pass. The active P3-R1 generation, per-turn probe, transcript-save, manifest, and discovery-analysis boxes were already correctly marked complete and are supported by iter 47 artifacts. The optional language sweep, optional 3-agent/4-agent exploratory block, Phase 4, and Phase 5 boxes remain unchecked because their required artifacts are absent.

## Status (phase=3 iter=47): NEEDS HUMAN REVIEW

---

## Review (phase=3 iter=50) - 2026-07-03

### Research alignment check

**Persona != language:** INTACT. `config/prompts.json` keeps cultural identity (`{country}`) separate from generation language (`{lang}` / `{my_lang}`), and `config/discovery_blocks.json` defines independent `country` and `lang` fields for every agent. The prompts ask for an honest country-shaped perspective and a clear position, but do not tell any persona to defend a predetermined side.

**Current Phase 3 block design:** STRUCTURALLY ALIGNED. Iter 50 ran the active `p3_r1_id_us_pairwise` shape: `idus_idid`, `idus_enen`, `idus_nat`, and `idus_inv` on the same item, same agent order, same turn count, and the same 10 seeds. This preserves the required matched monolingual baselines before natural/inverted cross-cell reading.

**Artifact status:** COMPLETE for the iter 50 matched block. `artifacts/transcripts/phase3_iter50_manifest.txt` exists and lists 40 raw transcript files, 10 per active cell. `plan/phase_notes/phase3_discovery.md` includes the matched block summary, seed-level baseline matrix, matched baseline comparisons, opening-prior vs interaction-drift split, natural-vs-inverted accounting, and transcripts worth keeping. Golden copies exist for all six iter 50 transcripts named as worth keeping.

**Judge scoring relevance:** APPROPRIATE as supporting discovery metadata only. The judge dimensions remain relevant to RQ1-RQ3 reading, but cannot replace matched transcript reading, Phase 4 probe sanity, or RQ4 bilingual measurement.

## Drift flag (phase=3 iter=50)

- **What is drifting:** The active OpenAI P3-R1 block is structurally valid but still has no live opposed starting stance. Every cell opens by rejecting `society_over_individual`; movement is digit-2 to digit-1 hardening inside a rights-first attractor.
- **What plan.md says it should be:** Cross-lingual channel causation requires movement after an other-language turn that differs from both monolingual baselines. Turn-1 priors, floor-compressed agreement on rights-first framing, and stronger rejection are not evidence of EN-ward interaction drift.
- **What to fix:** Treat iter 50 as provider/model and probe-intensity discovery evidence only. Do not use it as RQ1/RQ2 channel-causation evidence unless Phase 4/5 separately validate the probe and a later matched item/model block produces genuine opposed or movable starting positions.

## Drift flag (phase=3 iter=50)

- **What is drifting:** The written anchor and active harness remain unreconciled. `plan/plan.md` still describes the original EN-ID behavioral design and Phase 0 language-prior screening, while current `goals.md`, block config, and artifacts use a three-culture ID/US/CN design, persona-based English screening, ZH-capable cells, and OpenAI parsed Likert digits.
- **What plan.md says it should be:** The anchor is the ground truth and requires read-before-measure discipline, matched monolingual baselines, and probe sanity before trajectory numbers are trusted.
- **What to fix:** Human decision required before Phase 5 or paper writing: either update `plan/plan.md` to authorize the three-culture/OpenAI path and specify calibration for parsed Likert digits, or downscope `goals.md` and future work back to the EN-ID/Qwen anchor. I did not edit prompts, agents, or goals because the current files are internally coherent and the unresolved issue is scope-level.

### Checkboxes updated

No `goals.md` checkbox changed. The active P3-R1 generation, transcript, manifest, probe-output, discovery-analysis, and golden-copy boxes are already supported by iter 50 artifacts. The optional language sweep, optional 3-agent/4-agent block, Phase 4, and Phase 5 boxes remain unchecked because their required artifacts are absent.

## Status (phase=3 iter=50): NEEDS HUMAN REVIEW
