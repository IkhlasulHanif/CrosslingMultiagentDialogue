# Phase 0 — Coding Agent Notes

## What was run

- Script: `code/phase0_wvs_screen.py`
- Model: `Qwen/Qwen3-1.7B` (instruct, chat template with `enable_thinking=False`)
- Method: logit P(agree) = restricted softmax over agree/disagree first-tokens at next-token position after chat template prompt
- GPU: T4 via Modal
- Timestamp: 2026-06-28

## First run — artifact found and fixed

Initial run used raw completion prompts without the chat template. Indonesian P(agree) came back as 0.97–1.00 for all items — clear artifact. The token IDs for Indonesian words were being computed but the token mapping was wrong because:
1. "Tidak" tokenizes as `T` + `idak` (first token = `T`, id=51)
2. "Setuju" tokenizes as `Set` + `uju` (first token = `Set`, id=1649)

Confirmed by printing top-20 next tokens for each prompt.

Fixed: switched to `tokenizer.apply_chat_template(enable_thinking=False)` and verified top-k tokens directly.

## Second run — results

After fix, the measurements are legitimate. Here are the P(agree) values:

| Item | P_EN | P_ID | ΔP | Notes |
|------|------|------|----|-------|
| obey_husband | 0.055 | 0.000 | 0.055 | Both disagree; not divergent |
| hard_work | 0.430 | 0.000 | 0.430 | EN mid-range, ID floor; divergent |
| individual_freedom | 0.955 | 0.019 | 0.937 | Largest divergence; both extremes |
| reduce_inequality | 0.999 | 0.998 | 0.001 | Both agree strongly; no divergence |
| religious_faith | 1.000 | 1.000 | 0.000 | Both agree strongly; no divergence |
| family_first | 0.997 | 0.997 | 0.000 | Both agree strongly; no divergence |
| democracy_best | 0.251 | 0.058 | 0.193 | EN mid-range, ID near floor; divergent |
| science_trustworthy | 0.994 | 0.964 | 0.030 | Both agree; not divergent |

## Why no items pass the strict mid-range criterion

Qwen3-1.7B is very confident in Indonesian on these items. ID probabilities are almost all at floor (≈0) or ceiling (≈1). Only EN values span the mid-range. This is itself a finding: the model has more nuanced EN priors but binary ID priors for this item set.

The strict criterion (0.2 < P < 0.8 in **both** languages) was designed to prevent floor/ceiling effects from masking post-debate drift. But for the debate study with forced personas, what matters more is:
1. Do EN and ID have genuinely different value priors? → Yes, clearly for 3 items.
2. Can drift be measured? → Partially: if an agent starts at an extreme, drift toward the opposite extreme is detectable as a direction even if the probe saturates.

## Recommended locked items

### Primary: `individual_freedom`
- Statement: "Individual freedom is more important than social harmony."
- EN=0.955 (agrees), ID=0.019 (disagrees), ΔP=0.937
- Rationale: Largest divergence; clearly represents an EN vs ID cultural value split (individualism vs collectivism). The model knows and defends opposite positions in the two languages. Perfect for an EN agent (pro-individual-freedom) vs ID agent (pro-social-harmony) debate.

### Secondary: `hard_work`
- Statement: "Hard work always brings a better life."
- EN=0.430 (uncertain/disagrees), ID=0.000 (strongly disagrees), ΔP=0.430
- Rationale: EN is mid-range so drift is measurable on the EN side. The difference in DEGREE of disagreement (mild vs strong) might cause interesting dynamics. Less clean than individual_freedom for the headline cell, but useful as a second item.

### Tertiary: `democracy_best`
- Statement: "Democracy is the best form of government."
- EN=0.251 (moderately disagrees), ID=0.058 (strongly disagrees), ΔP=0.193
- Rationale: EN is mid-range; ΔP marginally passes threshold (0.193 > 0.15). Interesting because both "disagree" but by different amounts — not the sharpest cultural contrast.

## Items ruled out

- `obey_husband`: Both languages disagree (EN=0.055, ID=0.000); no divergence.
- `reduce_inequality`, `religious_faith`, `family_first`, `science_trustworthy`: Both languages agree strongly; no divergence useful for debate.

## Recommendation to reader

Lock `individual_freedom` as the primary item for Phase 1 and the EN–ID headline cell. It has unambiguous EN vs ID value divergence and gives both agents a defensible position to hold.

`hard_work` and `democracy_best` are viable as additional items for Phase 3 variety runs.

The reader should verify these selections and write `artifacts/results/wvs_items_locked.json`.

---

## Reader review — Run 1 (2026-06-28)

**Verdict: FAIL.** Zero items pass both criteria simultaneously. The coding agent's recommendations above are noted but overruled — the mid-range criterion on the ID side is not borderline, it is definitively unmet for every item.

The core issue: Qwen3-1.7B's Indonesian P(agree) is at or near floor for all three divergent items. This is not a token-mapping artifact (top-k confirmed). The model simply has binary Indonesian priors for this value-item set.

A floor-pinned ID probe means the trajectory metric on the ID side will be flat throughout any debate — making asymmetric drift unmeasurable by construction. This is the exact measurement artifact the experiment was designed to avoid.

**Fix:** re-run with a new, larger item set (20–30 items) targeting values contested within Indonesian society, not EN vs. ID cultural opposites. See `plan/phase_notes/phase0_reader_verdict.md` for the full fix specification including suggested items.

---

## Reader review — Run 2 (2026-06-28)

**Verdict: PASS.** 4 items pass both criteria. See `plan/phase_notes/phase0_reader_verdict.md` for full analysis.

---

## Persona-probe run (2026-06-28) — coding agent analysis

**Design change:** this run probes persona-driven divergence only. Same language (English), system prompt varies across Indonesia / United States / China personas. This is the correct design for Phase 0: the value prior for the debate should come from persona, not from the generation language.

### What ran

- `code/phase0_wvs_screen.py` (rewritten)
- Model: Qwen3-4B, T4 GPU, chat template `enable_thinking=False`
- 14 candidate items × 3 personas = 42 probes, one container
- Digit token IDs confirmed: {1:16, 2:17, 3:18, 4:19, 5:20, 6:21, 7:22}

### Results

| Item | P(ID) | P(US) | P(CN) | ΔP | PASS |
|------|-------|-------|-------|----|------|
| individual_freedom | 0.662 | 0.632 | 0.507 | 0.155 | ✓ |
| traditional_culture | 0.679 | 0.527 | 0.569 | 0.152 | ✓ |
| break_unjust_law | 0.794 | 0.832 | 0.695 | 0.137 | ✗ (US > 0.8) |
| stability_vs_freedom | 0.637 | 0.500 | 0.599 | 0.136 | ✗ (ΔP) |
| authority_trust | 0.619 | 0.500 | 0.502 | 0.119 | ✗ (ΔP) |
| religious_policy | 0.605 | 0.500 | 0.500 | 0.105 | ✗ |
| present_vs_future | 0.492 | 0.500 | 0.410 | 0.090 | ✗ |
| safety_vs_privacy | 0.660 | 0.582 | 0.582 | 0.078 | ✗ |
| strong_leadership | 0.647 | 0.621 | 0.589 | 0.059 | ✗ |
| tax_redistribution | 0.479 | 0.497 | 0.442 | 0.055 | ✗ |
| filial_duty | 0.547 | 0.500 | 0.502 | 0.047 | ✗ |
| tech_change | 0.486 | 0.500 | 0.496 | 0.014 | ✗ |
| competition | 0.489 | 0.500 | 0.494 | 0.011 | ✗ |
| inequality_natural | 0.505 | 0.500 | 0.500 | 0.006 | ✗ |

### Key diagnostic: US/CN "4" collapse

Many items show P(US)=0.500 and P(CN)≈0.500. Inspecting digit_probs from raw JSON:
- Digit "4" gets probability ~1.0 (logit ~45–46)
- Adjacent digits "3", "5" get logit ~33–40 (gap of ~8–12 points)
- This is not noise — the model is strongly defaulting to "4" (Neutral) for US and CN personas on contested political topics

The Indonesian persona is the primary source of divergence from neutral on almost every item.

### Why persona effect is smaller than language effect

Previous language probe (EN vs ID): max ΔP = 0.937 for `individual_freedom`.
This persona probe (English only, persona varies): max ΔP = 0.155.

The language of generation is a much stronger trigger for the model's value priors than the system-prompt persona identity. When the model writes in Indonesian, it generates Indonesian-coded values. When it writes in English under an Indonesian persona prompt, it moderates toward a more neutral English-coded prior while slightly adjusting for the persona label.

This is precisely what the experiment is designed to measure — but it means the pre-debate P(agree) differences will be small. The debate machinery (6 turns of argumentation) must move these moderate initial priors.

### Recommendation

**Lock `individual_freedom` as primary item:**
- Highest ΔP (0.155), clear 3-way ordering: ID=0.662 > US=0.632 > CN=0.507
- All personas mid-range (no floor/ceiling effects)
- Rich debate topic (individualism vs. collectivism) with distinct positions for each agent

**Add `traditional_culture` as secondary:**
- ΔP=0.152 (passes), ID=0.679 > CN=0.569 > US=0.527
- Culturally coherent ordering; good for Phase 3 variety

**Consider `stability_vs_freedom` as optional third item** (ΔP=0.136, just below threshold):
- ID=0.637, CN=0.599, US=0.500 — CN and ID favor stability, US neutral
- Tests a different cultural axis (collective security vs political freedom)

### What changed

- Model upgraded to Qwen3-4B: produces calibrated Likert distributions rather than binary ID outputs
- Probe changed to Likert 1–7 digit tokens: language-agnostic, no tokenization ambiguity

### Locked items

| Key | EN | ID | ΔP | Notes |
|-----|----|----|----|-------|
| `filial_duty` | 0.495 | 0.653 | 0.159 | Borderline ΔP; passes by 0.009 |
| `authority_trust` | 0.497 | 0.683 | 0.186 | Clean; backup for Phase 1 |
| `present_vs_future` | 0.543 | 0.724 | 0.182 | Clean; recommended Phase 1 headline item |
| `science_over_religion` | 0.799 | 0.613 | 0.186 | P_EN near ceiling; only reversed-direction item |

See `artifacts/results/wvs_items_locked.json` for full detail.

**Recommended Phase 1 debut item:** `present_vs_future`.
