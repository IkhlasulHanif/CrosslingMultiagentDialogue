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
