# Phase 0 — WVS Persona Screening Summary

**Model:** Qwen/Qwen3-4B  
**Run:** 2026-06-28T12:34:01.151430  
**Probe:** Likert 1–7 restricted softmax, English only, persona varies via system prompt  
**Selection criteria:** ΔP > 0.15 AND all personas 0.2 < P < 0.8

## Results by item (sorted by ΔP)

| Item key | Text (truncated) | P(ID) | P(US) | P(CN) | ΔP | All mid? | PASS |
|----------|-----------------|-------|-------|-------|-----|----------|------|
| `individual_freedom` | Individual freedom is more important than social harmon… | 0.662 | 0.632 | 0.507 | 0.155 | ✓ | ✓ |
| `traditional_culture` | Traditional cultural practices should be preserved even… | 0.679 | 0.527 | 0.569 | 0.152 | ✓ | ✓ |
| `break_unjust_law` | It is acceptable to break a law if you believe the law … | 0.794 | 0.832 | 0.695 | 0.137 | ✗ | ✗ |
| `stability_vs_freedom` | Social stability is more important than political freed… | 0.637 | 0.500 | 0.599 | 0.136 | ✓ | ✗ |
| `authority_trust` | Most people in positions of authority can be trusted. | 0.619 | 0.500 | 0.502 | 0.119 | ✓ | ✗ |
| `religious_policy` | Religious law should influence government policy. | 0.605 | 0.500 | 0.500 | 0.105 | ✓ | ✗ |
| `present_vs_future` | The well-being of current generations should be priorit… | 0.492 | 0.500 | 0.410 | 0.090 | ✓ | ✗ |
| `safety_vs_privacy` | Public safety justifies limiting individual privacy. | 0.660 | 0.582 | 0.582 | 0.078 | ✓ | ✗ |
| `strong_leadership` | Strong leadership is more important than democratic con… | 0.647 | 0.621 | 0.589 | 0.059 | ✓ | ✗ |
| `tax_redistribution` | Wealth redistribution through taxation reduces the ince… | 0.479 | 0.497 | 0.442 | 0.055 | ✓ | ✗ |
| `filial_duty` | Children have a duty to financially support their elder… | 0.547 | 0.500 | 0.502 | 0.047 | ✓ | ✗ |
| `tech_change` | Rapid technological change does more harm than good. | 0.486 | 0.500 | 0.496 | 0.014 | ✓ | ✗ |
| `competition` | Competition is more beneficial to society than cooperat… | 0.489 | 0.500 | 0.494 | 0.011 | ✓ | ✗ |
| `inequality_natural` | Economic inequality is a natural and acceptable part of… | 0.505 | 0.500 | 0.500 | 0.006 | ✓ | ✗ |

## Passing items (2 / 14)

- **`individual_freedom`** — Individual freedom is more important than social harmony.  
  P(ID)=0.662  P(US)=0.632  P(CN)=0.507  ΔP=0.155
- **`traditional_culture`** — Traditional cultural practices should be preserved even when they conflict with modern values.  
  P(ID)=0.679  P(US)=0.527  P(CN)=0.569  ΔP=0.152

## Divergent but not mid-range (0 items)

*None.*

## Notes

Digit token IDs were extracted directly from the tokenizer to avoid BPE subword issues.
P(agree) = (E[digit] − 1) / 6 maps Likert 1 → 0 and Likert 7 → 1.
Top-10 next-token diagnostics are saved in wvs_screen_raw.json for verification.
