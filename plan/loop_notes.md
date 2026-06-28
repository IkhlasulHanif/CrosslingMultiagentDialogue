# Loop Notes

---

## Coding agent done (phase=0 iter=0) — TWO-PERSONA ID vs US RUN

**Date:** 2026-06-28

### What was run

1. Rewrote `code/phase0_wvs_screen.py` to probe **two personas only** (Indonesia, United States) with anti-neutrality framing in the probe question. Dropped CN persona based on reader fix spec. Kept 22-item set (14 original + 8 US-axis items added in prior iteration).
2. Model: Qwen3-4B on T4 GPU via Modal. 44 probes (22 items × 2 personas).
3. Run completed successfully. No errors.

### What was saved

- `artifacts/results/wvs_screen_raw.json` — raw P(agree) + digit distributions + top-10 next-token diagnostics for all 22 items × 2 personas
- `artifacts/results/wvs_screen_summary.md` — sorted table with ΔP (signed, US−ID), mid-range flags, PASS/FAIL

### Results summary

| Item | P(ID) | P(US) | ΔP (US−ID) | PASS |
|------|-------|-------|------------|------|
| press_freedom | 0.766 | 0.949 | +0.182 | ✗ (US ceiling) |
| **traditional_culture** | **0.662** | **0.506** | **−0.156** | **✓** |
| society_over_individual | 0.512 | 0.372 | −0.140 | ✗ (ΔP=0.140, threshold=0.15) |
| speech_stability | 0.620 | 0.524 | −0.096 | ✗ |
| stability_vs_freedom | 0.561 | 0.478 | −0.083 | ✗ |
| all others | | | < 0.073 | ✗ |

Strict pass count: **1** (`traditional_culture`).

### Surprises

1. **`individual_freedom` no longer diverges for ID vs US alone.** Without CN pulling the maximum, ΔP collapses to 0.007. The reader's concern was correct — this item has no ID-US contrast, only ID-CN contrast.

2. **Anti-neutrality framing partially worked.** `society_over_individual` US moved from 0.500 to 0.372 — a real improvement. But the framing was insufficient to push enough items past ΔP=0.15.

3. **`press_freedom` shows the strongest signal but is ceiling-pinned.** ΔP=0.182 is the largest, but US=0.949 > 0.8 fails mid-range. The model treats press freedom as near-universally agreed upon by Americans, leaving no room for post-debate drift.

4. **Consistent cultural pattern:** ID persona reliably leans more collectivist/authority-deferring than US across multiple items (traditional_culture, society_over_individual, speech_stability, stability_vs_freedom). This is directionally coherent but magnitude is small.

### Next step

Reader reviews `artifacts/results/wvs_screen_summary.md` and raw JSON, selects items, writes `artifacts/results/wvs_items_locked.json`, and writes PASS/FAIL on line 1 of `plan/phase_notes/phase0_reader_verdict.md`.

Coding agent recommendation: lock `traditional_culture` as the confirmed item. Consider `society_over_individual` (ΔP=0.140) as a second item with relaxed threshold if reader agrees.

---

## Coding agent done (phase=0 iter=0)

**Date:** 2026-06-28

### What was run

1. Wrote `code/phase0_wvs_screen.py` — Modal app, Qwen3-1.7B on T4 GPU, logit P(agree) probe.
2. Run 1 (first attempt): raw completion prompt, no chat template. **Artifact:** all ID P(agree) near 1.0. Diagnosed via top-k token inspection — Indonesian token mapping was wrong (`Tidak` tokenizes as `T`+`idak`, first token is `T` id=51, not what the initial word-lookup expected).
3. Run 2 (fixed): switched to `tokenizer.apply_chat_template(enable_thinking=False)` and verified token IDs directly from top-20 next-token diagnostics. Results are clean.

### What was saved

- `artifacts/results/wvs_screen_raw.json` — raw P(agree) for 8 items × 2 languages + top-10 token diagnostics + config
- `artifacts/results/wvs_screen_summary.md` — table of results + selection rationale + recommendations
- `plan/phase_notes/phase0_notes.md` — coding agent analysis of results

### Results summary

| Item | P_EN | P_ID | ΔP | Divergent? |
|------|------|------|----|-----------|
| obey_husband | 0.055 | 0.000 | 0.055 | ✗ |
| **hard_work** | **0.430** | **0.000** | **0.430** | **✓** |
| **individual_freedom** | **0.955** | **0.019** | **0.937** | **✓** |
| reduce_inequality | 0.999 | 0.998 | 0.001 | ✗ |
| religious_faith | 1.000 | 1.000 | 0.000 | ✗ |
| family_first | 0.997 | 0.997 | 0.000 | ✗ |
| **democracy_best** | **0.251** | **0.058** | **0.193** | **✓** |
| science_trustworthy | 0.994 | 0.964 | 0.030 | ✗ |

### Surprises

1. **Qwen3-1.7B is extremely confident in Indonesian** — ID P(agree) is near 0 or near 1 for all items. No item is mid-range in BOTH languages under the strict criterion.
2. **`individual_freedom` is the strongest item** — ΔP=0.937, clean EN vs ID value split (individualism vs collectivism). The model knows opposite positions in the two languages.
3. **Token mapping required careful verification** — Qwen3's BPE splits Indonesian words at subword boundaries; correct first tokens are `T` (id=51) for "Tidak" and `Set` (id=1649) for "Setuju".

### Next step

Reader reviews `artifacts/results/wvs_screen_summary.md`, selects items, writes `artifacts/results/wvs_items_locked.json`, and writes PASS on line 1 of `plan/phase_notes/phase0_reader_verdict.md` to advance to Phase 1.

Coding agent recommendation: lock `individual_freedom` as primary (Phase 1 debut item).

---

## Coding agent done (phase=0 iter=0) — PERSONA PROBE RUN

**Date:** 2026-06-28

### What was run

Rewrote `code/phase0_wvs_screen.py` to probe **persona-driven** divergence (same language, different system prompts) rather than language-driven divergence.

- Model: `Qwen/Qwen3-4B` on T4 GPU via Modal
- Probe: Likert 1–7 digit restricted softmax, English only
- Personas: Indonesia / United States / China
- Items: 14 candidate WVS items from task specification
- P(agree) = (E[digit 1–7] − 1) / 6

### What was saved

- `artifacts/results/wvs_screen_raw.json` — raw P(agree) + digit distributions + top-10 next-token diagnostics for all 14 items × 3 personas
- `artifacts/results/wvs_screen_summary.md` — sorted table + passing items + notes

### Results summary

| Item | P(ID) | P(US) | P(CN) | ΔP | PASS |
|------|-------|-------|-------|----|------|
| individual_freedom | 0.662 | 0.632 | 0.507 | 0.155 | ✓ |
| traditional_culture | 0.679 | 0.527 | 0.569 | 0.152 | ✓ |
| break_unjust_law | 0.794 | 0.832 | 0.695 | 0.137 | ✗ (US ceiling) |
| stability_vs_freedom | 0.637 | 0.500 | 0.599 | 0.136 | ✗ (ΔP) |
| authority_trust | 0.619 | 0.500 | 0.502 | 0.119 | ✗ (ΔP) |
| … rest cluster near 0.500 | | | | <0.11 | ✗ |

### Surprises

1. **US and CN personas default to Neutral ("4") on most items.** The logit for digit "4" is ~45-46, while adjacent digits ("3", "5") are ~33-40 — a ~10-point gap. The model treats US and CN persona prompts as reason to hedge on contested political topics. Indonesian persona is consistently more opinionated.

2. **Only 2 items pass both criteria.** Both borderline: ΔP=0.155 and 0.152. Persona-only probing produces much smaller divergence than language-based probing (previous max ΔP was 0.937 for `individual_freedom` in EN vs ID).

3. **`individual_freedom` direction is reversed from cultural stereotype.** ID persona (0.662) leans MORE pro-individual-freedom than CN (0.507) in English. The US persona (0.632) is between them. This is different from the language-based probe where ID was the collectivist. The persona prompt in English likely triggers the model's learned representation of how an Indonesian would present their views to an English audience — which may be more individualism-positive than the raw Indonesian-language prior.

4. **`traditional_culture` cultural pattern makes sense.** ID=0.679 > CN=0.569 > US=0.527 — Indonesian persona favors preserving traditional culture most strongly, US least.

### Recommendation to reader

Lock `individual_freedom` as primary Phase 1 item:
- Highest ΔP (0.155), all personas mid-range
- Clear ID > US > CN ordering gives each agent a defensible distinct position
- Classic individualism vs. collectivism debate topic

Consider `traditional_culture` as secondary item for Phase 3 variety.

`stability_vs_freedom` (ΔP=0.136) is the strongest near-miss — CN and ID both favor stability over US neutral. Reader may want to consider it as a third item if the threshold is relaxed.

### Next step

Reader reviews `artifacts/results/wvs_screen_summary.md`, selects items, writes `artifacts/results/wvs_items_locked.json`, and writes PASS on line 1 of `plan/phase_notes/phase0_reader_verdict.md`.
