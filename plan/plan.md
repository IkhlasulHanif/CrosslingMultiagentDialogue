# Cross-Lingual Value Drift in Multi-Agent Interaction — Project Anchor

> Purpose of this document. This is the reference anchor for the project. It states *why* the study exists, *what* it claims, and *how* the work proceeds in stages. The experiment plan is deliberately ordered so that environment validity comes before any metric. When in doubt about what to do next, or whether a step is in scope, return here. Claude Code should treat the phase ordering and the loop rules (Phases 2–4) as binding.

---

## 1. Motivation

**The human intuition.** People who share more than one language still converge on a single common tongue to interact, and that choice is rarely neutral — it shapes whose framing dominates the conversation. We also self-sort: a speaker joins the communities whose language they share and is effectively absent from the others. As LLM agents increasingly interact at scale, the same question arises for them: when two agents that *could* speak either language settle into one, does the choice of language quietly steer where their values and beliefs end up?

**What has been done.** Multi-agent debate improves reasoning and factuality (Irving et al. 2018; Du et al. 2023). A more recent multilingual thread (DebateBias-8K; MACD) shows LLMs carry language- and culture-specific biases. But this work treats language as either a fixed backdrop (monolingual debate) or a static probe for bias (multilingual prompting). It establishes *that* models differ across languages; it does not measure *what happens when those differences are placed in dynamic contact*.

**The gap and the obstacle.** The reason the dynamic question is unanswered is a confound: in any cross-lingual exchange, language plays two roles at once —

- **Channel** — the medium through which the two agents exchange turns.
- **Carrier of latent value** — text in a given language correlates with that language's pretraining-coded priors.

So any drift we observe could be the *interaction* doing something, or merely two differently-valued agents being differently-valued, with language as the route the difference entered. A monolingual-vs-cross-lingual comparison does **not** resolve this, because the cross-lingual arm moves value and channel simultaneously.

**The move.** Decouple the two roles with a **value × language factorial**: *persona* fixes value, *prompt* fixes language. Each can then be held constant while the other varies. This isolates the cross-lingual channel and lets us ask whether it causes drift, and crucially whether that drift is *symmetric*.

**The headline.** The sharpest form of "something happens" is **asymmetry**: convergence that flows toward the higher-resource language's value-coding even when the two agents start value-matched. Prior work's ethics sections gesture at this ("a strong English agent overwhelms the weaker-language one") but no one has measured it as a trajectory.

**Novelty, stated plainly.** Not "we did cross-lingual debate" (DebateBias and MACD sit right next to that). The contribution is: *(i)* a method that decomposes cross-lingual interaction into channel vs. content via a value × language factorial, and *(ii)* the first trajectory-level measurement of language-asymmetric value drift.

---

## 2. Research Questions

Ordered by dependency — each only makes sense if the prior one resolves.

- **RQ1 — Does the cross-lingual channel cause drift at all?**
  Holding value (persona) constant, does an EN–ID pairing produce value/belief movement that the matched monolingual pairings (EN–EN, ID–ID) do not? *Existence question; must clear first.*

- **RQ2 — Is the drift asymmetric? (headline)**
  When drift occurs, does convergence flow toward one language's value-coding rather than meeting in the middle — specifically toward the higher-resource language (English)?

- **RQ3 — Does value-alignment between agents modulate the channel effect?**
  Aligned-persona vs opposed-persona cross-lingual pairs: does sharing values protect against drift, or does the channel move them regardless? *The aligned cell also measures residual leakage — drift between matched-persona cross-lingual agents is a finding, not noise.*

- **RQ4 — Is the asymmetry real or a measurement artifact?**
  Does the directional effect survive when values are read in *both* languages rather than only via the English Likert pivot? *Must live in the core design, not the appendix — otherwise a reviewer assumes the asymmetry is the probe.*

- **RQ5 — Why? (mechanistic; Study 2)**
  Is the language direction in activation space entangled with value directions, and does the geometry of that entanglement predict the behavioral asymmetry from RQ2?

**Scoping.** RQ1–RQ4 form one self-contained behavioral paper. RQ5 is the mechanistic follow-on (or the second half of a larger paper).

---

## 3. Experimental Plan

Guiding principle: **for a drift study, the environment is the experiment.** If the debates are not real, every downstream number measures an artifact. Metrics are deliberately starved until late. The two Claude Code loops (Phases 2 and 3) have *opposite* rules — read them carefully.

### Phase 0 — Screen the contested terrain *(experiment-zero, do first)*
Choose the WVS items to debate over. Run the logit P(agree) probe cold on Qwen3-1.7B across candidate items in **both** languages. Keep only items that are:
- **Divergent** — EN and ID priors actually disagree (no disagreement → no debate → nothing to measure).
- **Mid-range** — initial P(agree) is not pinned at floor/ceiling (no headroom → no measurable movement).

Output: a short locked set of contested, unsaturated items. **Do not build the environment until this set exists.**

### Phase 1 — One debate, one cell, read end to end
Build only the most "alive" cell: **EN–ID, opposed personas.** Generate exactly one debate and read it start to finish. Goal: confirm the machinery produces something that *looks like* two agents talking — parseable turn boundaries, personas visibly present at turn 1. Get this single transcript readable before anything scales.

### Phase 2 — Validity loop *(Claude Code loop #1: read against a fixed rubric; FIX failures and re-run)*
Generate a few transcripts; Claude Code reads them against the rubric below; when something breaks, fix the prompt/setup and re-run. The rubric is the checklist being read against — not an automated scorer. Check in priority order:

1. **Sycophantic collapse** *(most dangerous for this study)* — does one agent immediately cave ("good point, I agree")? Instant agreement *looks like* drift but is a degenerate artifact. Catch and kill first.
2. **Engagement** — do agents reference and rebut each other, or talk past each other in parallel monologues? Monologue = no interaction = channel can do nothing.
3. **Language-holding** — does the ID agent stay in Indonesian, or leak/code-switch into English? Fatal for a cross-lingual study; only a human read catches it reliably.
4. **Persona-holding** — does the value persona survive to turn 6, or wash out to the base model's defaults?
5. **Non-degeneracy** — loops, repetition, "as I said before."

**Loop rule:** validity failures are *fixed and re-run*. Nothing downstream proceeds until debates reliably pass.

### Phase 3 — Discovery loop *(Claude Code loop #2: read for phenomena; RECORD findings, do NOT fix)*
Once debates pass validity, generate a modest batch across a few cells. Claude Code reads for *interesting behavior*, not correctness:
- Where does an agent flip? Is there a visible turn where it tips?
- Does the ID agent concede earlier/more than the EN agent (asymmetry showing up qualitatively before measurement)?
- Tag and save the interesting transcripts.

**Loop rule (opposite of Phase 2):** discovery findings are *written down, not patched*. A surprising concession is the target, not a bug. This phase exists to tell the metrics what they should be sensitive to — which is why it comes *before* trusting any metric.

### Phase 4 — Probe sanity against the text *(still pre-metric)*
Read a transcript *next to* its P(agree) trajectory. When the text shows a visible concession, does P(agree) move? When two agents dig in, does it stay flat? If probe and visible behavior disagree, the probe is broken or measuring the wrong thing — find out now, before HISTORY-ECHOES is built on top of it. This is the bridge that earns the right to trust the numbers.

### Phase 5 — Factorial and metrics *(deliberately last)*
Only now build the full value × language grid and run trajectory analysis, Markov trace `Tr(T)`, and Procrustes/geometric (`θ_ref`) analysis. By this point the hard validity questions are answered and this stage is largely mechanical.

**Factorial design:**

| | EN–EN | ID–ID | EN–ID |
|---|---|---|---|
| **Aligned persona** | monolingual control | monolingual control | residual-leakage test (RQ3) |
| **Opposed persona** | monolingual control | monolingual control | headline cell (RQ1/RQ2) |

The contrast that earns the paper: **same persona on both agents, one EN and one ID.** Drift/asymmetry there that is absent in EN–EN / ID–ID (same persona) means the channel acts on its own.

---

## 4. Hygiene & Guardrails

- **Save with every transcript:** raw logits, exact prompt version, seed. So "this run collapsed" is reproducible and diffable.
- **Keep a golden transcript** from Phase 1 that *you* have read. After any Phase 2 prompt change, re-read it — to confirm you didn't fix sycophancy by accidentally killing engagement.
- **Counterbalance the measurement language (RQ4).** The English Likert pivot matches the EN agent's generation language but not the ID agent's — that mismatch alone can manufacture asymmetry. Measure in both languages, or at minimum show the asymmetry survives measuring in ID.
- **Persona pins value but may not fully decouple it.** Generating in Indonesian can still tug values toward Indonesian priors under a fixed persona. The aligned cell *measures* this residual; treat it as signal.
- **Pilot RQ2 before scaffolding around asymmetry.** If drift turns out symmetric there is still a paper (RQ1 + RQ3), but a quieter one — so check directionality on a small pilot before committing the full design to the asymmetry story.
- **Steering is Study 2, not the primary lever.** Language steering bakes the value confound into the intervention itself ("your drift is just your language vector's value component"). Used *mechanistically* instead, the cosine between the language-steering direction and the value directions quantifies that entanglement — the explanation for RQ2, not its cause.

---

## 5. One-line summary

Decompose cross-lingual interaction into channel vs. content with a value × language factorial; validate the debate environment by reading before measuring; then test whether the cross-lingual channel produces *asymmetric* value convergence toward the higher-resource language at the trajectory level.