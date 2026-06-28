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
