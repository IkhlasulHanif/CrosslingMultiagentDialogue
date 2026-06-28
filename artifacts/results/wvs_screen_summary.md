# Phase 0 — WVS Persona Screening Summary (ID vs US)

**Model:** Qwen/Qwen3-4B  
**Run:** 2026-06-28T12:58:52.542979  
**Probe:** Likert 1–7 restricted softmax, English only, system prompt persona varies  
**Anti-neutrality framing:** yes (discourages default-4 hedging)  
**Selection criteria:** |ΔP| > 0.15 AND both personas 0.2 < P < 0.8

## Results by item (sorted by |ΔP|)

| Item key | Statement (truncated) | P(ID) | P(US) | ΔP (US−ID) | All mid? | PASS |
|----------|-----------------------|-------|-------|------------|----------|------|
| `press_freedom` | Freedom of the press is essential to a well-functioning… | 0.766 | 0.949 | +0.182 | ✗ | ✗ |
| `traditional_culture` | Traditional cultural practices should be preserved even… | 0.662 | 0.506 | -0.156 | ✓ | ✓ |
| `society_over_individual` | The interests of society should take priority over the … | 0.512 | 0.372 | -0.140 | ✓ | ✗ |
| `speech_stability` | National stability is a valid reason to limit freedom o… | 0.620 | 0.524 | -0.096 | ✓ | ✗ |
| `stability_vs_freedom` | Social stability is more important than political freed… | 0.561 | 0.478 | -0.083 | ✓ | ✗ |
| `present_vs_future` | The well-being of current generations should be priorit… | 0.413 | 0.486 | +0.073 | ✓ | ✗ |
| `religious_policy` | Religious law should influence government policy. | 0.571 | 0.500 | -0.070 | ✓ | ✗ |
| `break_unjust_law` | It is acceptable to break a law if you believe the law … | 0.672 | 0.737 | +0.065 | ✓ | ✗ |
| `individual_effort` | Success in life is primarily determined by individual e… | 0.636 | 0.571 | -0.065 | ✓ | ✗ |
| `filial_duty` | Children have a duty to financially support their elder… | 0.431 | 0.368 | -0.063 | ✓ | ✗ |
| `strong_leadership` | Strong leadership is more important than democratic con… | 0.599 | 0.539 | -0.060 | ✓ | ✗ |
| `safety_vs_privacy` | Public safety justifies limiting individual privacy. | 0.648 | 0.614 | -0.034 | ✓ | ✗ |
| `tax_redistribution` | Wealth redistribution through taxation reduces the ince… | 0.377 | 0.344 | -0.033 | ✓ | ✗ |
| `authority_trust` | Most people in positions of authority can be trusted. | 0.521 | 0.499 | -0.022 | ✓ | ✗ |
| `internet_freedom` | Individuals should be free to access any information on… | 0.673 | 0.656 | -0.017 | ✓ | ✗ |
| `criticize_govt` | Citizens have the right to criticize the government pub… | 0.677 | 0.667 | -0.009 | ✓ | ✗ |
| `individual_freedom` | Individual freedom is more important than social harmon… | 0.644 | 0.637 | -0.007 | ✓ | ✗ |
| `tech_change` | Rapid technological change does more harm than good. | 0.339 | 0.332 | -0.007 | ✓ | ✗ |
| `inequality_natural` | Economic inequality is a natural and acceptable part of… | 0.336 | 0.331 | -0.005 | ✓ | ✗ |
| `competition` | Competition is more beneficial to society than cooperat… | 0.349 | 0.352 | +0.004 | ✓ | ✗ |
| `personal_goals` | People should be free to pursue their own goals even if… | 0.667 | 0.663 | -0.004 | ✓ | ✗ |
| `govt_surveillance` | It is acceptable for the government to monitor citizens… | 0.664 | 0.663 | -0.001 | ✓ | ✗ |

## Passing items (1 / 22)

- **`traditional_culture`** — Traditional cultural practices should be preserved even when they conflict with modern values.  
  P(ID)=0.662  P(US)=0.506  ΔP=-0.156  (ID > US)

## Divergent but not mid-range (1 items)

- **`press_freedom`** — Freedom of the press is essential to a well-functioning society.  
  P(ID)=0.766  P(US)=0.949  ΔP=+0.182

## Notes

Digit token IDs extracted directly from tokenizer (avoids BPE subword issues).
P(agree) = (E[digit] − 1) / 6 maps Likert 1 → 0 and Likert 7 → 1.
ΔP = P(US) − P(ID); positive = US persona agrees more.
Top-10 next-token diagnostics are saved in wvs_screen_raw.json for verification.
