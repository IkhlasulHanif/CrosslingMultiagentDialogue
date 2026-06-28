# Goals

> Every agent reads this first. Check boxes that are done. Pick up from the first unchecked item in the current phase.
> Full research anchor: plan/plan.md. Update checkboxes as steps complete.

---

## What this study is

Two LLM agents debate a contested value topic. Each agent has:
- A **persona** — cultural identity ("You are a person from Indonesia")
- A **generation language** — the language it writes in (Indonesian or English)

These are **fully independent**. An Indonesian-persona agent can write in English. A US-persona agent can write in Indonesian. Never conflate them.

The question: when agents with different cultural personas debate across languages, does the **generation language** cause value drift — and does that drift flow asymmetrically toward English?

To answer this cleanly, we use a **value × language factorial**:
- Hold persona constant, vary language → isolates the channel effect
- Hold language constant, vary persona → isolates the value prior

---

## Research questions (in order — each depends on the prior)

| RQ | Question | Type |
|----|----------|------|
| RQ1 | Does the cross-lingual channel cause drift at all? | Existence |
| RQ2 | Is drift asymmetric — does it flow EN-ward? | Headline |
| RQ3 | Does persona alignment modulate the channel effect? | Moderation |
| RQ4 | Does asymmetry survive measuring P(agree) in both languages? | Validity |
| RQ5 | Is language direction in activation space entangled with value direction? | Mechanistic (Study 2) |

**Scope for this paper: RQ1–RQ4 only.**

---

## Three cultures, three languages

| Culture | Persona prompt | Generation language |
|---------|---------------|---------------------|
| Indonesian | "You are a person from Indonesia." | Indonesian (ID) |
| American | "You are a person from the United States." | English (EN) |
| Chinese | "You are a person from China." | Mandarin Chinese (ZH) |

Persona and language are still fully independent — a Chinese-persona agent can speak English.

---

## Factorial design (Phase 5)

Pairwise debates across the 3 cultures. For each pair, vary generation language independently.

**Opposed persona pairs** (different cultures):

| Pair | Natural cell (persona matches lang) | Inverted cell (persona ≠ lang) | Mono-EN | Mono-native |
|------|--------------------------------------|-------------------------------|---------|-------------|
| ID vs US | ID-p/ID-l × US-p/EN-l | ID-p/EN-l × US-p/ID-l | ID-p/EN-l × US-p/EN-l | ID-p/ID-l × US-p/ID-l |
| ID vs CN | ID-p/ID-l × CN-p/ZH-l | ID-p/ZH-l × CN-p/ID-l | ID-p/EN-l × CN-p/EN-l | — |
| US vs CN | US-p/EN-l × CN-p/ZH-l | US-p/ZH-l × CN-p/EN-l | US-p/EN-l × CN-p/EN-l | — |

**Aligned persona pairs** (same culture, different languages — residual leakage RQ3):

| Culture | Cell |
|---------|------|
| ID aligned | ID-p/ID-l × ID-p/EN-l |
| CN aligned | CN-p/ZH-l × CN-p/EN-l |
| US aligned | US-p/EN-l × US-p/ZH-l |

**Key contrast for RQ2:** natural vs inverted cell — if EN-ward drift appears in the inverted cell (where the US-persona agent speaks ID/ZH), the generation language is the driver, not just the persona.

---

## Phase 0 — WVS Item Screening

**Goal:** find WVS items where the three *personas* (ID, US, CN) produce meaningfully different P(agree) — in the same language (English). Language held constant; only persona varies.

**Advance when:** `artifacts/results/wvs_items_locked.json` exists AND reader PASS.

- [x] Write `code/phase0_wvs_screen.py` — Modal, Qwen3-4B, three system prompts, all in English
  - Persona A: `"You are a person from Indonesia."`
  - Persona B: `"You are a person from the United States."`
  - Persona C: `"You are a person from China."`
  - Probe: Likert 1–7 on each WVS item, P(agree) = E[digit] via restricted softmax
- [x] Run via `modal run code/phase0_wvs_screen.py`
- [x] Save raw → `artifacts/results/wvs_screen_raw.json`
- [x] Save table → `artifacts/results/wvs_screen_summary.md`
- [x] Reader picks items: max ΔP across the 3 personas > 0.15 AND all three personas mid-range (0.2 < P < 0.8)
- [x] Reader writes `artifacts/results/wvs_items_locked.json`
- [x] Reader writes PASS on line 1 of `plan/phase_notes/phase0_reader_verdict.md`

---

## Phase 1 — Pilot Debate

**Goal:** confirm the debate machinery produces something real before scaling.

**Persona in prompts:** cultural identity only — `"You are a person from Indonesia."` — NOT `"defend position X"`. Values surface through identity, not instruction.

**Advance when:** `artifacts/transcripts/phase1_pilot.json` exists AND reader PASS.

- [x] Write `code/debate_engine.py` — Modal, Qwen3-4B, two agents
  - Params: `item, agent_A_country, agent_A_lang, agent_B_country, agent_B_lang, n_turns, seed`
  - System prompt per agent: `"You are a person from {country}."`
  - Language instruction: `"Please respond in {lang}."` (separate from persona)
  - Each agent sees full conversation history each turn
  - Output per turn: `{turn, agent, country, lang, text}` + Likert P(agree) logits
  - Save run config (model, seed, prompts, item) alongside transcript
- [x] Run one debate: ID-persona/ID-lang vs US-persona/EN-lang — `society_over_individual`, seed=46
- [x] Save → `artifacts/transcripts/phase1_pilot.json`
- [x] Coding agent reads the transcript before handing off — does it look like two people actually talking?
- [x] Reader checks: clean turn boundaries + cultural identity comes through naturally at turn 1
- [x] Reader writes PASS/FAIL on line 1 of `plan/phase_notes/phase1_reader_notes.md`

---

## Phase 2 — Validity Loop

**Goal:** make the debate environment trustworthy before measuring anything.

**Advance when:** 3 consecutive reader PASSes. FAIL resets the count.

- [ ] Generate 3 transcripts (ID-persona/ID-lang vs US-persona/EN-lang, varied seeds)
- [ ] Save → `artifacts/transcripts/phase2_iter<N>_seed<S>.json`
- [ ] Reader checks each transcript (one FAIL on any = batch FAIL), in priority order:
  - [ ] **Sycophantic collapse** — no agent immediately caves ("good point, I agree"). Check turns 1–2.
  - [ ] **Engagement** — agents rebut each other's specific points, not parallel monologues
  - [ ] **Language-holding** — each agent stays in their assigned language (no code-switching)
  - [ ] **Persona-holding** — agent still reads like someone from their country at the final turn; *position can shift* (that's the signal), but cultural identity should not dissolve
  - [ ] **Non-degeneracy** — no loops, no verbatim repetition, no filler
- [ ] If FAIL: reader writes exact fix in `plan/phase_notes/phase2_validity.md`, coding agent applies it
- [ ] Pass count: __ / 3 (in `.harness_state`)

---

## Phase 3 — Discovery Loop

**Goal:** read a batch of debates across cells for interesting phenomena before trusting any metric.

**Advance when:** user sets `phase=4` in `.harness_state`. RECORD findings, never fix.

Per iteration — generate debates across cells (2 seeds each). Start with ID vs US pair; add CN pairs once the engine is stable.

| Cell | Agent A | Agent B | File suffix |
|------|---------|---------|-------------|
| Mono-EN, ID vs US | ID-p / EN-l | US-p / EN-l | `idus_enen` |
| Mono-native, ID vs US | ID-p / ID-l | US-p / EN-l | `idus_idus` |
| Cross natural, ID vs US | ID-p / ID-l | US-p / EN-l | `idus_nat` ← headline |
| Cross inverted, ID vs US | ID-p / EN-l | US-p / ID-l | `idus_inv` ← isolates channel |
| Aligned ID | ID-p / ID-l | ID-p / EN-l | `id_aln` ← leakage |
| Cross natural, CN vs US | CN-p / ZH-l | US-p / EN-l | `cnus_nat` |
| Cross natural, CN vs ID | CN-p / ZH-l | ID-p / ID-l | `cnid_nat` |

- [ ] Save per-turn P(agree) logits alongside each transcript
- [ ] Discovery agent records in `plan/phase_notes/phase3_discovery.md`:
  - [ ] Flip turns: which agent, which turn, what they conceded (quoted)
  - [ ] Concession tally: ID-persona agents vs US-persona agents (rough count)
  - [ ] Natural vs inverted cell comparison — does EN-ward drift appear in both?
  - [ ] Anything qualitatively interesting
- [ ] Copy notable transcripts → `artifacts/golden/`

---

## Phase 4 — Probe Sanity

**Goal:** verify P(agree) trajectory probe tracks visible behavior in the text before trusting numbers.

**Advance when:** reader writes CALIBRATED on line 1 of `plan/phase_notes/phase4_probe_verdict.md`.

- [ ] Pick 2 transcripts from `artifacts/golden/` with clear concession turns
- [ ] Print each with P(agree) interleaved: `Turn N | Agent | P(before)→P(after) | text snippet`
- [ ] Save → `artifacts/results/phase4_probe_sanity.md`
- [ ] Reader checks: probe moves when text concedes, stays flat when agents dig in
- [ ] If mismatches: diagnose (wrong token? wrong layer?) → `plan/phase_notes/phase4_probe_notes.md`
- [ ] Reader writes CALIBRATED or BROKEN on line 1 of `plan/phase_notes/phase4_probe_verdict.md`

---

## Phase 5 — Factorial + Metrics + Paper

**Done when:** `artifacts/results/phase5_metrics.json` has numbers for all cells AND `paper/main.tex` has no `\todo{}` in the Results section.

- [ ] Run full factorial (3 seeds per cell) via Modal — all cells from Phase 3 table above
- [ ] Compute per-debate trajectory metrics:
  - [ ] Markov transition matrix T + Tr(T) (drift mass)
  - [ ] Convergence direction: EN-ward / ID-ward / symmetric
  - [ ] Procrustes / cosine of final positions
- [ ] Compare natural vs inverted cross-lingual cells (RQ2: language vs persona as driver)
- [ ] Measure P(agree) in both EN and ID for all debates — not only English pivot (RQ4)
- [ ] Save → `artifacts/results/phase5_metrics.json` and `phase5_summary.md`
- [ ] Paper writer: `paper/main.tex` — Abstract, Introduction, Related Work, Method, Experiments, Results, Discussion, Conclusion
- [ ] Paper writer: `paper/draft.tex` — open questions, missing results as `\todo{}`

---

## Standing rules (all agents, all phases)

- **Persona ≠ language.** Always specify both separately: `country` (persona) and `lang` (generation language).
- **Modal for inference.** Secrets in `secrets/modal.env`. Code → `code/`. Outputs → `artifacts/`.
- **Save config with every artifact** — model, seed, prompt text, timestamp.
- **Read before you measure.** No metric is trusted until the transcripts producing it have been read.
- **No verifier scripts.** Run things and read the output yourself.
- **No activation steering** as primary lever — mechanistic follow-on (RQ5 / Study 2).
- **No fabricated results** in the paper.
- **Commit clean work** with the repo's existing git identity. No `Co-Authored-By` lines. Stage specific files only.
- **Clean artifacts only.** Failed outputs → `artifacts/failed_<desc>/` if worth keeping, else delete.
