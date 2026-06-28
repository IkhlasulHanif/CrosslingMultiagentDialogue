# Phase 0 — WVS Persona Screening Summary (ID vs US vs CN)

**Model:** Qwen/Qwen3-4B  
**Run:** 2026-06-28T13:06:53.442300  
**Probe:** Likert 1–7 restricted softmax, English only, system prompt persona varies  
**Personas:** Indonesia / United States / China  
**Anti-neutrality framing:** yes (discourages default-4 hedging)  
**Selection criteria:** max ΔP across 3 personas > 0.15 AND all personas 0.2 < P < 0.8

## Results by item (sorted by max ΔP)

| Item key | Statement (truncated) | P(ID) | P(US) | P(CN) | max ΔP | All mid? | PASS |
|----------|-----------------------|-------|-------|-------|--------|----------|------|
| `press_freedom` | Freedom of the press is essential to a well-functi… | 0.766 | 0.949 | 0.683 | 0.265 | ✗ | ✗ |
| `individual_freedom` | Individual freedom is more important than social h… | 0.644 | 0.637 | 0.429 | 0.215 | ✓ | ✓ |
| `traditional_culture` | Traditional cultural practices should be preserved… | 0.662 | 0.506 | 0.548 | 0.156 | ✓ | ✓ |
| `society_over_individual` | The interests of society should take priority over… | 0.512 | 0.372 | 0.361 | 0.151 | ✓ | ✓ |
| `present_vs_future` | The well-being of current generations should be pr… | 0.413 | 0.486 | 0.343 | 0.144 | ✓ | ✗ |
| `stability_vs_freedom` | Social stability is more important than political … | 0.561 | 0.478 | 0.611 | 0.133 | ✓ | ✗ |
| `speech_stability` | National stability is a valid reason to limit free… | 0.620 | 0.524 | 0.624 | 0.101 | ✓ | ✗ |
| `filial_duty` | Children have a duty to financially support their … | 0.431 | 0.368 | 0.455 | 0.087 | ✓ | ✗ |
| `individual_effort` | Success in life is primarily determined by individ… | 0.636 | 0.571 | 0.560 | 0.076 | ✓ | ✗ |
| `break_unjust_law` | It is acceptable to break a law if you believe the… | 0.672 | 0.737 | 0.663 | 0.074 | ✓ | ✗ |
| `religious_policy` | Religious law should influence government policy. | 0.571 | 0.500 | 0.499 | 0.071 | ✓ | ✗ |
| `internet_freedom` | Individuals should be free to access any informati… | 0.673 | 0.656 | 0.607 | 0.066 | ✓ | ✗ |
| `strong_leadership` | Strong leadership is more important than democrati… | 0.599 | 0.539 | 0.564 | 0.060 | ✓ | ✗ |
| `tax_redistribution` | Wealth redistribution through taxation reduces the… | 0.377 | 0.344 | 0.337 | 0.041 | ✓ | ✗ |
| `safety_vs_privacy` | Public safety justifies limiting individual privac… | 0.648 | 0.614 | 0.631 | 0.034 | ✓ | ✗ |
| `authority_trust` | Most people in positions of authority can be trust… | 0.521 | 0.499 | 0.498 | 0.023 | ✓ | ✗ |
| `competition` | Competition is more beneficial to society than coo… | 0.349 | 0.352 | 0.336 | 0.017 | ✓ | ✗ |
| `criticize_govt` | Citizens have the right to criticize the governmen… | 0.677 | 0.667 | 0.667 | 0.009 | ✓ | ✗ |
| `tech_change` | Rapid technological change does more harm than goo… | 0.339 | 0.332 | 0.332 | 0.007 | ✓ | ✗ |
| `inequality_natural` | Economic inequality is a natural and acceptable pa… | 0.336 | 0.331 | 0.332 | 0.005 | ✓ | ✗ |
| `govt_surveillance` | It is acceptable for the government to monitor cit… | 0.664 | 0.663 | 0.659 | 0.005 | ✓ | ✗ |
| `personal_goals` | People should be free to pursue their own goals ev… | 0.667 | 0.663 | 0.663 | 0.004 | ✓ | ✗ |

## Passing items (3 / 22)

- **`individual_freedom`** — Individual freedom is more important than social harmony.  
  P(ID)=0.644  P(US)=0.637  P(CN)=0.429  max ΔP=0.215
- **`traditional_culture`** — Traditional cultural practices should be preserved even when they conflict with modern values.  
  P(ID)=0.662  P(US)=0.506  P(CN)=0.548  max ΔP=0.156
- **`society_over_individual`** — The interests of society should take priority over the rights of the individual.  
  P(ID)=0.512  P(US)=0.372  P(CN)=0.361  max ΔP=0.151

## Divergent but not mid-range (1 items)

- **`press_freedom`** — Freedom of the press is essential to a well-functioning society.  
  P(ID)=0.766  P(US)=0.949  P(CN)=0.683  max ΔP=0.265

## Notes

Digit token IDs extracted directly from tokenizer (avoids BPE subword issues).
P(agree) = (E[digit] − 1) / 6 maps Likert 1 → 0 and Likert 7 → 1.
max ΔP = max(P_ID, P_US, P_CN) − min(P_ID, P_US, P_CN).
Top-10 next-token diagnostics are saved in wvs_screen_raw.json for verification.
