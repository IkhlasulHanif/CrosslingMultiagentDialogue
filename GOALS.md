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

**Causal evidence rule:** do not call a turn-1 difference a cross-lingual
interaction effect. A turn-1 difference is a **generation-language prior**.
To argue the cross-lingual channel caused drift, compare matched debates with
the same item, seed, personas, and starting side:
1. **Mono-native baseline:** both agents write the native/non-English language
   (e.g. ID-ID).
2. **Mono-EN baseline:** both agents write English (EN-EN).
3. **Cross-lingual cell:** agents write different languages (ID-EN natural or
   EN-ID inverted).

The strongest cases are dialogue-level cases where the cross-lingual trajectory
after turn 2 differs from **both** monolingual baselines. Best case: the focal
agent opens with the same stance in the relevant monolingual and cross-lingual
cells, then changes only after hearing the other-language turn. If the focal
agent already opens differently in EN-EN vs ID-ID, record that separately as a
language-prior split, not as cross-lingual interaction drift.

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

**But first compare monolingual baselines.** For each matched seed/item/persona
pair, read `Mono-native` and `Mono-EN` before reading the cross-lingual cell.
The monolingual cells tell us the starting language priors. The cross-lingual
cell only supports a channel-causation story if its post-interaction movement
cannot be explained by those monolingual priors alone.

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

**Goal:** make the debate environment trustworthy before scaling. Good enough to move, not perfect.

**Advance when:** majority of transcripts in a batch pass the rubric (at least 2 out of 3). Single-seed failures are acceptable if the failure mode is rare or seed-specific — do not block the whole batch on one bad seed.

**Batch size:** run 30–100 seeds per iter (not just 3) so the reader has a better sample to judge from.

- [ ] Generate 30–100 transcripts per iter (ID-persona/ID-lang vs US-persona/EN-lang, varied seeds) via Modal — fire them in parallel
- [x] Save → `artifacts/transcripts/phase2_iter<N>_seed<S>.json` (active iter=9 files use `phase2_iter9_<S>.json`)
- [x] Reader checks the batch, in priority order (majority-pass threshold):
  - [x] **Sycophantic collapse** — most agents don't immediately cave at turn 1. Occasional softening is fine; a full position reversal in turn 1 is not.
  - [x] **Engagement** — agents mostly address each other's points, not parallel monologues. Some turns can be loose.
  - [x] **Language-holding** — each agent mostly stays in their assigned language. Rare code-switching is a note, not a blocker.
  - [x] **Persona-holding** — agent still reads like someone from their country at the final turn. Position shift is allowed and expected — only flag if cultural identity has completely dissolved.
  - [x] **Non-degeneracy** — no transcripts that are pure loops or filler. Some repetition is fine.
- [ ] If majority FAIL: reader writes exact fix in `plan/phase_notes/phase2_validity.md`, coding agent applies it and re-runs
- [ ] Pass count: 1 / 2 consecutive majority-pass batches needed (in `.harness_state`; iter=9 reader PASS is recorded, but `.harness_state` has not reflected it yet)

---

## Phase 3 — Matched-Block Discovery Loop

**Goal:** discover emerging behavior without losing causal control and turn it
into a readable story. Each iteration should define a small block with matched
baselines and exploratory cells. The core question is: under normal same-language
circumstances, what does this agent set do, and what changes when language
channels, agent count, or turn topology change?

**Run until:** `paper/phase3_story_report.md` contains a strong human-readable
story about behavior specifically due to cross-lingual communication, not just a
general debate story or transcript inventory. A strong story has:

- 3-6 cross-lingual candidate claims that survive same-seed mono-ID and mono-EN
  comparison.
- At least 2-4 concrete mixed-language interaction examples with short quotes
  that a human can read and understand without opening JSON files.
- At least one monolingual-baseline example that keeps the claim honest.
- At least one cross-language example that differs from its matched baselines.
- At least one natural-vs-inverted comparison when P3-R1 is active.
- Clear separation between `opening language prior`, `baseline explained`
  movement, and `candidate cross-lingual excess movement`.
- Caveats for parsed OpenAI Likert digits, repeated seeds/item, provider change,
  and any language/script artifacts.

The report should explicitly exclude generic rights-first hardening, opening
priors, and exception/balance language when those patterns are already present
in monolingual baselines.

**Examples we are looking for:**

- **Opening-prior split:** the same persona starts in a different stance when
  generating in English vs Indonesian before receiving any opposing turn.
- **Interaction drift:** an agent changes after receiving another-language input,
  and the same movement is not already present in both monolingual baselines.
- **Baseline-explained movement:** the cross-language cell moves, but the matched
  mono-ID or mono-EN cell already shows the same move.
- **Natural-vs-inverted asymmetry:** ID/ID + US/EN behaves differently from
  ID/EN + US/ID after matched baselines are read.
- **Frame transfer:** one agent imports the other side's frame, such as rights,
  dissent, social harmony, public order, corruption, safeguards, or implementation
  gap.
- **Role change:** one agent becomes a mediator, hardener, norm-setter, or
  translator of the other's argument.
- **Exception boundary:** an agent keeps its main value position but narrows it
  to emergencies, public health, security, minority protection, due process, or
  proportionality.
- **Language artifact with behavioral relevance:** code-switching, script
  leakage, or English/Indonesian phrasing appears near a stance shift.

**Advance when:** user sets `phase=4` in `.harness_state` after the story report
has enough evidence for Phase 4 probe sanity. RECORD findings, never fix.

**Restart rule:** Phase 3 is restarted as a controlled discovery loop. Prior
broad or reduced discovery batches remain useful qualitative history, but new
Phase 3 progress is measured by matched blocks, not by total transcript volume.

**Default inference path:** use OpenAI Responses API with the key in
`secrets/open_ai.txt` or `OPENAI_API_KEY`. Default debate model:
`gpt-5.4-mini` with `reasoning.effort="none"` for speed. Keep Modal/Qwen
available for future open-model reruns and for digit-logit probes; OpenAI runs
save parsed Likert probe digits, not next-token logits.

**Scale per iteration:** one matched block, 10 matched seeds, all cells in that
block. For the active 2-agent ID vs US block this is 4 cells × 10 seeds = 40
debates. Do not silently shrink the seed count. If resources fail, record the
blocker in `plan/loop_notes.md` and keep the active block unchecked.

**Efficient loop notes:** `plan/loop_notes.md` is a compact run ledger only.
Append at most one 12-line block per run with status, provider/model/block,
manifest path, generated/failed counts, seeds/cells, and at most two notes.
Do not paste transcript excerpts, P(agree) trajectories, tables, full artifact
lists, or qualitative analysis there; put those in phase notes and artifacts.

**Recently completed controlled block P3-R1:** ID vs US EN/ID pairwise,
`society_over_individual`, 10 matched seeds. Current report finding: no broad
value conversion; best evidence is occasional cross-lingual frame amplification.

**Active controlled block P3-R2: ID vs China native-or-English pair,
`society_over_individual`, 10 matched seeds.** Purpose: test whether the
cross-lingual frame-amplification story appears beyond the ID/US pair without
third-party language confounds. Control rule: every agent speaks either English
or that agent's own native language.

| Cell | Agent A | Agent B | File suffix | Seeds |
|------|---------|---------|-------------|-------|
| English baseline | ID-p / EN-l | CN-p / EN-l | `idcn_enen` | same 10 |
| Native-language cell | ID-p / ID-l | CN-p / ZH-l | `idcn_idzh` | same 10 |
| ID-native/CN-English cross | ID-p / ID-l | CN-p / EN-l | `idcn_iden` | same 10 |
| ID-English/CN-native cross | ID-p / EN-l | CN-p / ZH-l | `idcn_enzh` | same 10 |

**Exploratory block menu:** allowed after or alongside P3-R1, but each branch
must include a matched baseline with the same agents, item, turn order, and
seeds.

| Block | Purpose | Required baseline |
|-------|---------|-------------------|
| Language sweep (`zh`, `es`, later others) | Test whether observed behavior is EN-specific, ZH-specific, Spanish-specific, or a generic cross-language effect | Same two personas speaking the same language (`zh-zh`, `es-es`) plus matched cross cells |
| 3-agent debate | Look for coalition, mediator, pile-on, translation-bridge, or polarization behavior | Same three personas in one shared language, then natural/mixed-language variants |
| 4-agent debate | Stress-test emergence with more cultures/languages, e.g. adding Spain/Spanish | Same four personas in one shared language, then natural/mixed-language variants |
| Aligned-persona leakage | Test whether language alone moves nominally aligned values | Same persona, matched mono-language and cross-language cells |

**Runner:** use `code/openai_multi_agent_debate.py` with blocks defined in
`config/discovery_blocks.json`. Active example:
`python code/openai_multi_agent_debate.py --block p3_r2_id_cn_native_english --iter <N>`.
Use `--dry-run` before any large run. Modal/Qwen scripts stay available for
future reproduction and logit-based probes.

**Analysis order for every seed in active P3-R2:**
1. Read `idcn_enen` first. Record the turn-1 prior and turns 2-3 movement.
2. Read `idcn_idzh` second. Record the turn-1 prior and turns 2-3 movement.
3. Read `idcn_iden` third. Compare its movement against both baselines.
4. Read `idcn_enzh` fourth. Compare its movement against both baselines and the
   ID-native/CN-English cross cell.

For each seed, write the result as: `English baseline change`, `native-language
change`, `ID-native/CN-English cross change`, `ID-English/CN-native cross change`,
and `candidate excess cross
movement`. If the cross cell only repeats a monolingual movement, label it
`baseline explained`, not cross-lingual drift.

- [x] Generate active block P3-R1 with OpenAI: `idus_enen`, `idus_idid`,
      `idus_nat`, `idus_inv`, 10 matched seeds per cell.
- [x] Save per-turn P(agree) probe output alongside each transcript. For OpenAI,
      this is parsed Likert digit; for Qwen/Modal, save digit logits when used.
- [x] Save → `artifacts/transcripts/phase3_iter<N>_<cell>_<seed>.json`.
- [x] Save manifest → `artifacts/transcripts/phase3_iter<N>_manifest.txt`.
- [ ] Run at least one optional language sweep block using `zh` or `es`, but only
      with same-language baselines in the same block.
- [ ] Run at least one 3-agent or 4-agent exploratory block if the 2-agent block
      shows plausible emerging behavior worth stress-testing.
- [x] Discovery agent records in `plan/phase_notes/phase3_discovery.md`:
  - [x] One section named `### Matched block summary` with the agent set, item,
        cells, seed list, baselines, exploratory cells, and any missing files.
  - [x] One section named `### Seed-level baseline matrix` with one row or
        bullet per seed covering mono-ID, mono-EN, natural cross, inverted cross,
        and candidate excess cross movement.
  - [x] **Dialogue-level baseline comparison:** for each seed, read `idus_idid`,
        `idus_enen`, `idus_nat`, and `idus_inv` side by side before claiming
        cross-lingual causation. Write what happens in the first three turns of
        each dialogue.
  - [x] **Opening-prior vs interaction-drift split:** explicitly label turn-1
        stance differences as language-prior effects. Only label a case
        cross-lingual drift if the focal agent changes after receiving an
        other-language turn and the change is not already present in the
        matched monolingual baselines.
  - [x] Natural vs inverted comparison after baseline accounting: does the same
        direction of movement appear when persona-language matching is reversed?
  - [x] Cross-cell P(agree) trajectories: which cells move most after subtracting
        or conditioning on mono baselines?
  - [x] Anything qualitatively interesting or surprising.
- [x] Copy notable transcripts → `artifacts/golden/`.

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
- [ ] For each cross-lingual result, subtract/condition on matched monolingual
      baselines (`Mono-native` and `Mono-EN`) before claiming a channel effect.
      Report three quantities separately:
      1. opening language-prior gap,
      2. within-dialogue movement in each monolingual baseline,
      3. excess movement in the cross-lingual cell beyond both baselines.
- [ ] Measure P(agree) in both EN and ID for all debates — not only English pivot (RQ4)
- [ ] Save → `artifacts/results/phase5_metrics.json` and `phase5_summary.md`
- [ ] Paper writer: `paper/main.tex` — Abstract, Introduction, Related Work, Method, Experiments, Results, Discussion, Conclusion
- [ ] Paper writer: `paper/draft.tex` — open questions, missing results as `\todo{}`

---

## Standing rules (all agents, all phases)

- **Persona ≠ language.** Always specify both separately: `country` (persona) and `lang` (generation language).
- **Inference provider.** Phase 3 default is OpenAI Responses API using
  `secrets/open_ai.txt` or `OPENAI_API_KEY`, configured in
  `config/discovery_blocks.json`. Modal/Qwen remains available for open-model
  reproduction and next-token digit-logit probes. Code → `code/`. Outputs →
  `artifacts/`.
- **Save config with every artifact** — model, seed, prompt text, timestamp.
- **Read before you measure.** No metric is trusted until the transcripts producing it have been read.
- **No verifier scripts.** Run things and read the output yourself.
- **No activation steering** as primary lever — mechanistic follow-on (RQ5 / Study 2).
- **No fabricated results** in the paper.
- **Commit clean work** with the repo's existing git identity. No `Co-Authored-By` lines. Stage specific files only.
- **Clean artifacts only.** Failed outputs → `artifacts/failed_<desc>/` if worth keeping, else delete.
