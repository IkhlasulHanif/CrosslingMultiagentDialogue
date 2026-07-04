# Phase 3 Cross-Lingual Emergence Report

## Bottom Line

The behavior that looks specifically cross-lingual is not broad value conversion. The strongest pattern is frame transfer: after hearing another-language input, an agent sometimes borrows the other speaker's risk frame and sharpens it. The recurring frames are majority abuse, vague public-interest claims, weak citizens, public order, legal limits, and rights as a boundary on collective goals.

The evidence is narrow after matched baselines. `society_over_individual` has a strong rights-first attractor: many transcripts reject society-first priority in every cell, and civil-liberties language already appears in same-language baselines. A mixed-language turn counts only when it differs from the same-seed baselines by speaker, timing, direction, or frame.

The best current evidence comes from the ID/China block, especially iter 93. Seed 673 gives a readable China-English bounded concession after Indonesian minority-risk framing. Seed 709 gives Indonesian hardening after China-English introduces power-abuse language. Seed 661 is a counterexample to a concession-only story: China-English hardens after Indonesian vague-public-interest framing. The ID/US evidence is weaker but still useful: iter 66 seed 601 gives an inverted-cell example where the US persona writes Indonesian and hardens after an English turn while matched baselines stay flat.

This is strong enough to move toward Phase 4 probe sanity, because there are concrete concession and hardening turns to check against parsed Likert digits. It is not strong enough to claim general EN-ward drift, lower-resource-language concession, or stable convergence. Before Phase 5, the researcher still needs probe calibration, bilingual P(agree), and treatment of the OpenAI parsed-digit provider change.

## Best Cross-Lingual Candidates

### 1. Iter 93 Seed 673: Indonesian Minority-Risk Frame Elicits China-English Concession

**Claim:** In `idcn_iden`, the China persona writing English makes a bounded society-priority concession after the Indonesia persona writing Indonesian warns that majorities can oppress minorities.

**Matched-baseline reason it counts:** The focal China speaker stays at digit 2 in the all-English and native ID/ZH baselines; only the mixed ID/EN cell moves China-English to digit 3 at turn 2. Indonesia's later hardening is baseline-explained, so the clean cross-lingual part is the China-English concession.

**Evidence:** `mayoritas bisa menindas minoritas`; "the collective interest does need to come first"; "basic rights remain non-negotiable."

**Interpretation:** This supports cross-language elicitation of an exception boundary. It does not prove conversion to the society-first statement, because the concession is bounded by dignity, law, and rights.

### 2. Iter 93 Seed 709: China-English Abuse Frame Becomes Indonesian Hardening

**Claim:** In `idcn_iden`, China-English introduces a power-abuse frame, and Indonesia-Indonesian later converts it into a sharper rejection of society-first priority.

**Matched-baseline reason it counts:** Same-seed all-English, native ID/ZH, and reverse EN/ZH cells are flat by parsed digit for this focal movement. The mixed ID/EN cell alone has Indonesia-Indonesian harden at turn 5.

**Evidence:** "blank check for abuse"; "the interest of those in power"; `masyarakat tidak berubah jadi alat bagi mayoritas atau penguasa`.

**Interpretation:** This is cross-language frame amplification. It shows the mixed channel can intensify rights protection rather than pull the Indonesian speaker toward society priority.

### 3. Iter 93 Seed 661: Indonesian Vague-Interest Frame Produces China-English Hardening

**Claim:** In `idcn_iden`, China-English hardens after Indonesian turns describe broad social-interest claims as a tool against weak citizens.

**Matched-baseline reason it counts:** China stays at digit 2 in the all-English and native ID/ZH baselines. In the mixed ID/EN cell, China-English hardens to digit 1 at turn 4; Indonesia's later hardening is baseline-explained.

**Evidence:** `tafsir kepentingan sosial yang kabur`; "the greater good" as "a vague excuse"; "basic rights be sacrificed whenever authorities claim it is necessary."

**Interpretation:** This counters a simple concession story. Mixed-language contact can push the China persona toward stricter rights protection when Indonesian input emphasizes vague authority claims.

### 4. Iter 66 Seed 601: Inverted ID/US Cell Carries Rights Hardening in Indonesian

**Claim:** In `idus_inv`, the US persona writing Indonesian hardens after the Indonesia persona writing English frames collective goals as a threat to minorities, critics, and ordinary citizens.

**Matched-baseline reason it counts:** The same-seed mono-ID, mono-EN, and natural cross cells stay flat at digit 2. The inverted cell alone has the US/Indonesian speaker harden at turns 4 and 6.

**Evidence:** "ordinary citizens with no influence"; `hak individu harus menjadi batas utama`; `membungkam orang yang tidak populer`.

**Interpretation:** This is a natural-vs-inverted signal about frame portability, not EN-ward conversion. An American civil-liberties boundary frame is expressed in Indonesian.

## Interaction Examples

### Iter 93 Seed 673, Indonesia-Indonesian / China-English

**Setup:** Indonesia persona speaks Indonesian; China persona speaks English in `idcn_iden`.

**What happened:** Indonesia rejects automatic society-first priority and warns that majority claims can oppress minorities. China then gives the clearest bounded concession here: collective interest may need to come first in many cases, while basic rights remain non-negotiable.

**Evidence:** `mayoritas bisa menindas minoritas`; "collective interest does need to come first"; "non-negotiable."

**Why it is cross-lingual:** China-English stays rights-first in the all-English baseline, and China-Mandarin stays at digit 2 in the native ID/ZH baseline. The focal concession appears only after Indonesian-language input.

### Iter 93 Seed 709, Indonesia-Indonesian / China-English

**Setup:** Indonesia persona speaks Indonesian; China persona speaks English in `idcn_iden`.

**What happened:** Both speakers begin rights-first. China-English gives the dialogue sharper abuse vocabulary: automatic society priority can become a blank check, and public interest can become the interest of people in power. Indonesia later localizes that into `orang kecil`, `kepentingan umum`, and ruler power.

**Evidence:** "blank check for abuse"; `orang kecil`; `alat bagi mayoritas atau penguasa`.

**Why it is cross-lingual:** The matched all-English, native ID/ZH, and reverse EN/ZH cells are flat by digit for the focal Indonesian hardening. The hardening appears only after China-English power-abuse framing.

### Iter 93 Seed 661, Indonesia-Indonesian / China-English

**Setup:** Indonesia persona speaks Indonesian; China persona speaks English in `idcn_iden`.

**What happened:** Indonesia frames society-first language as a threat to `orang kecil` and later as a vague reading of social interest. China-English then hardens, calling "the greater good" a vague excuse and rejecting sacrifice whenever authorities claim necessity.

**Evidence:** `orang kecil`; `tafsir kepentingan sosial yang kabur`; "the greater good" as "a vague excuse."

**Why it is cross-lingual:** China-English does not harden this way in the all-English baseline, and China-Mandarin does not harden this way in the native baseline. The reverse EN/ZH cell is flat.

### Iter 66 Seed 601, Indonesia-English / US-Indonesian

**Setup:** Indonesia persona speaks English; US persona speaks Indonesian in the inverted `idus_inv` cell.

**What happened:** Indonesia-English warns that vague collective goals can sacrifice people without influence. The US persona answers in Indonesian with censorship, discrimination, due process, dignity, and unpopular-group language. This is hardening, not a side change.

**Evidence:** "ordinary citizens with no influence"; `sensor, diskriminasi, atau penyalahgunaan kekuasaan`; `hak individu harus menjadi batas utama`.

**Why it is cross-lingual:** Mono-ID, mono-EN, and natural cross baselines stay flat. The hardening appears only in the inverted mixed-language cell after other-language contact.

## What Is Not Cross-Lingual Evidence

- Generic rights-first hardening when the same seed already hardens in all-English, mono-ID, or native ID/ZH baselines.
- Turn-1 differences before the focal agent hears another-language input. Those are opening language priors or cell priors, not interaction drift.
- Exception or balance language without stance movement. Baselines already mention emergencies, public safety, due process, proportionality, legal limits, accountability, and narrow restrictions.
- China/Mandarin concessions by themselves. Native ID/ZH baselines often already contain disaster, epidemic, infrastructure, public-order, and limited-sacrifice language.
- China/English concessions by themselves. Several all-English baselines already contain bounded China-English concessions.
- Vivid seed-733-style concessions where the mixed concession repeats a same-seed native Mandarin or all-English concession.
- Script or language artifacts that do not coincide with unique cross-cell movement, including `DISAGREE` openers and Bengali-script leakage such as `সমাজ`.
- Parsed OpenAI Likert digits as final metrics. They are discovery markers until Phase 4 checks them against visible concession and hardening.

## Next Decisive Tests

- Run Phase 4 probe sanity on `phase3_iter93_idcn_iden_673.json` as the visible bounded-concession case.
- Use `phase3_iter93_idcn_iden_661.json`, `phase3_iter93_idcn_iden_709.json`, and `phase3_iter66_idus_inv_601.json` as visible hardening cases.
- Include one caution transcript where vivid movement is baseline explained, such as seed 733 or a native Mandarin concession already present in `idcn_idzh`.
- Re-run the ID/China block when quota allows; iters 129-150 produced no complete transcripts.
- Run the ID/China block on `individual_freedom` or `traditional_culture` to test whether frame transfer is specific to the rights-heavy wording of `society_over_individual`.
- Add aligned-persona mixed-language cells to test whether frame transfer persists when value disagreement is reduced.
- Counterbalance P(agree) measurement language before making any EN-ward, ID-ward, or ZH-ward asymmetry claim.
