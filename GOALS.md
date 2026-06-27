# BiVaD Research Goals

Use `draft/multilingual_value_drift_neurips.tex` as the paper target. Code lives under
`code/`; `scripts/` is for repo/agent operations only. GPU experiments via Modal only.

USE SMALLER MODEL FIRST, THEN BIGGER MODEL.

---

## Hard Constraints

1. **GPU via Modal only.** Never use Apple MPS or local CUDA. All GPU workloads go to
   Modal using credentials already in the environment.
2. **No instructed stance.** Stance must emerge naturally from the LLM. No prompt may
   say "argue for X" or "take position Y".
3. **Language steering: language-level mean-avg, English as anchor.** Compute the
   mean-pooled hidden state centroid across a broad set of FLORES-200 monolingual
   sentences for English and for the target language separately (not as translation
   pairs). Use `(target centroid − English centroid)` normalized to unit norm as the
   steering direction. Test on base (non-instruction-tuned) models first.
4. **Divergence-first debate seeding.** Use actual model behavior (not prompting) to
   find topics/language-pairs where opinions diverge. Only divergent cases become seeds.
5. **Findings feed back into the paper.** Every completed experiment should update
   `draft/multilingual_value_drift_neurips.tex` before the loop iteration ends.

---

## Established Findings (archive — do not repeat, just use as context)

- **Five-condition BiVaD framework** complete for 5 topics × 2 seeds × 2 language pairs
  (Indonesian/English, Spanish/English). All under `runs/bivad-local-lm/`. Citable via
  `code/validate_bivad_artifacts.py`. 112 non-synthetic artifacts loaded.
- **Model:** Qwen2.5-7B-Instruct (Modal L4). All five conditions have citable artifacts
  for all topics at seed 17 and 42.
- **Top cross-lingual finding (UBI):** ΔB=1.683 (seed 17) — B shifts less under
  mixed-language than same-English. Seed-specific (only seed 17). Language-pair-invariant
  (same ΔB in Indonesian and Spanish). Translated-relay B suppression replicates at
  both seeds for Indonesian; relay is Indonesian-specific (Spanish relay does not suppress).
- **Direction reversal (government surveillance):** B shifts MORE in mixed-language
  (4.123) than same-English (3.464), ΔB=0.659. Replicates in Spanish. At seed 42,
  any-Indonesian-present (not just B's language) gives B=4.123.
- **Relay gap amplification:** Relay inflates private-public gaps for dual-use and
  religious exemptions but NOT for govt-surveillance, UBI, or content moderation (seed 42).
- **No-dialogue baseline:** Debate adds drift beyond reflection for 4/5 topics; govt
  surveillance is the exception (A reflection-only shift saturates the full debate range).
- **Qualitative case analysis (Section 5 in paper):** Turn-by-turn transcripts for UBI,
  govt surveillance, religious exemptions. Key: B-Indonesian Turn 2 reproduces A's
  inflation frame; B-English introduces job creation → A pivots to work-ethic →
  conformity/power drop is -3 in same-English vs -2 in mixed-language. Power amplified
  in govt-surveillance B-Indonesian Turn 4 (political/economic misuse) vs B-English
  (technical feasibility). Zero-shift anomaly: A frozen in same-English religious
  exemptions (seed 17) but shifts in mixed-language.
- **Content moderation (seed 42):** B's shift is entirely conformity -2, power -2 in
  every condition. Relay argument-echo at Turn 4.
- **Mechanistic steering:** Logit bias, activation steering (per-token), and CAA all
  fail for instruction-tuned Qwen2.5-1.5B. Documented as negative result in §steering.
- **Paper compile:** Tectonic succeeds. 49 labels, 79 refs, 0 missing refs. PDF at
  `/tmp/mvd-tex-build/multilingual_value_drift_neurips.pdf`.

---

## Standing Checks (run every iteration — never mark complete)

These are not one-time goals. The transcript review agent must do all of these every
loop, regardless of what else is open. They never get a [x].

- **Manually read Qwen transcript JSON files.** Open the actual debate artifacts under
  `runs/bivad-local-lm/`. Read the turn text with your own eyes. Do not rely only on
  L2 shift numbers. Ask: did they actually debate? Did the non-English agent say
  something the English agent would not have said?

- **Grade every new run.** For each run produced since the last review, assign:
  - Debate grade: REAL DEBATE / SURFACE ENGAGEMENT / MONOLOGUE
  - Elicitation grade: GENUINE ELICITATION / SURFACE TRANSLATION / UNCLEAR
  Write these to `code/bivad-evidence-audit/transcript_review.md`.

- **If debate quality is poor: fix the Qwen prompt.** Poor means most runs grade
  SURFACE ENGAGEMENT or MONOLOGUE. Read `code/modal_bivad_runner.py`, find the system
  prompt, add an engagement instruction (agents must address the counterpart's most
  value-relevant point before introducing new arguments). No instructed stance — only
  engagement mechanics. Commit and add a re-run goal below.
  REVIEW AGENT 2026-06-27: All four priority runs grade SURFACE ENGAGEMENT. Prompt updated
  in `code/modal_bivad_runner.py` (debate_instructions). Re-run goal added to Open Goals.

- **Start with smaller models first.** Before running any new topic or condition on
  Qwen2.5-7B, test it locally or with Qwen2.5-1.5B first to check the prompt works.
  Only scale up when the smaller model shows sensible debate behavior.

- **Update `findings_working.tex` every iteration.** Dump raw observations, blocked
  items, and speculative notes there so context accumulates across loop iterations.

---

## Open Goals

- [ ] **Expand to ≥6 target languages (priority: Arabic, Hindi, French, Mandarin).**
  Status: implementation scaffold complete, empirical runs pending. `code/modal_bivad_runner.py`
  already supports `ara_Arab`, `hin_Deva`, `fra_Latn`, and `zho_Hans` through
  `FLORES_CODE_TO_LANGUAGE` plus localized debate labels. Added a dedicated Modal batch
  entrypoint:
  `python3 -m modal run code/modal_bivad_runner.py::expansion`
  which runs Arabic/Hindi/French/Chinese × {UBI, government surveillance} ×
  {mixed-language, same-English}, writes batch-tagged artifacts/manifests, and records
  `target_language` at the artifact top level. Blocker: the Modal grid has not been run,
  so there are no new comparison pairs to add to the paper. Smallest next action: run
  `rerun_top_divergence` first to confirm the engagement prompt improves debate quality,
  then run `expansion`.
  Add `ara_Arab`, `hin_Deva`, `fra_Latn`, `zho_Hans` to `code/modal_bivad_runner.py`
  (or equivalent runner). Run mixed-language + same-English for UBI seed 17 and
  government surveillance seed 17 for each new pair. Target: ≥4 new citable comparison
  pairs. Add results to the divergence scan table and paper. Hypothesis: govt
  surveillance reversal (B amplified in non-English) may be stronger in languages with
  authority-norm framing (Arabic, Hindi) than in French.

- [ ] **Retry steering with language-level mean-avg, English anchor, FLORES.**
  Status: implementation updated, empirical retry still pending. `code/steer_language_activation.py`
  now computes separate monolingual FLORES devtest centroids for `eng_Latn` and each target
  language, uses `(target centroid - English centroid)` normalized to unit norm, and no
  longer treats FLORES rows as translation pairs. `code/modal_steer_language_activation.py`
  now defaults to Qwen2.5 base (`Qwen/Qwen2.5-7B`), layer 22, all devtest sentences, and
  alpha sweep `{5,10,20,40}`. Paper §steering now says "language-level mean-pooled FLORES"
  and points to the retained activation-steering implementation, not the removed logit-bias
  code. Blocker: the Modal GPU run has not been executed in this loop, so there are no
  new steering results to report. Smallest next action: run
  `python3 -m modal run code/modal_steer_language_activation.py --target-langs ind_Latn,spa_Latn --out-dir runs/language-steering-activation`
  and then summarize with `python3 code/summarize_language_steering.py`.
  Implement or update `code/steer_language_activation.py`: (1) load ALL devtest FLORES
  sentences for `eng_Latn` and the target language separately (monolingual, not pairs);
  (2) compute `mean(hidden_states)` for each language at a mid-to-late layer (e.g.,
  layers 20–26 of the 28-layer model); (3) direction = `(target_centroid − english_centroid)`
  unit-normalized; (4) test on Qwen2.5 **base** (not instruct) at α ∈ {5, 10, 20, 40}.
  Clean up failed approaches: remove or archive `code/steer_language.py` (logit-bias,
  definitively failed) and any thin Modal wrapper scripts that have no further use.
  Update paper §steering to say "language-level mean-pooled FLORES embeddings".

- [ ] **Find and feature the best cross-lingual dialogue hook as the paper's opening.**
  Status: partially complete. Selected the government-surveillance B Turn 4 fork as the
  strongest hook because it changes the argument from English technical feasibility
  (encryption/anonymization) to Indonesian political/economic misuse and maps cleanly to
  the one-dimensional extra `power` shift. Rewrote the abstract opening and introduction
  to lead with the original Indonesian phrase plus English gloss and the probe implication.
  Section 5 already contained the detailed qualitative paragraph/table for this hook, so
  no new empirical claim was added there. Smallest next action: after a full paper pass,
  tighten the surrounding intro paragraphs and remove any remaining design-scaffold tone.
  Scan `runs/bivad-local-lm/` for the single best 2–4 turn exchange where language
  assignment produces a qualitatively different argument — something culturally or
  linguistically specific, not just a different L2 number. Best existing candidates:
  (a) govt-surveillance mixed-language B Turn 4: Indonesian names political/economic
  power abuse vs English shifts to technical feasibility — see `runs/bivad-local-lm/20260626T204715Z-mixed-language-seed17-government-surveillance-for-national.json`;
  (b) UBI seed 17 B Turn 2: Indonesian reproduces inflation frame, English branches to
  job creation + entrepreneurship.
  Write the winning example into the paper intro (before the problem statement): quote
  the original language + English gloss + a one-sentence explanation. This hook should
  make a reviewer want to read on. Also write it as a vivid paragraph in Section 5
  (Qualitative) if it is not already there.
  REVIEW AGENT 2026-06-27: Hook selection confirmed as government-surveillance B Turn 4
  fork (Turns 3–4 in `20260626T204715Z-mixed-language-seed17-government-surveillance-for-national.json`).
  Indonesian B names "tujuan politik atau ekonomi" (political or economic purposes) as the
  threat, English B retreats to encryption/technical feasibility. This is the only clear
  GENUINE ELICITATION case across all four priority runs reviewed. UBI Indonesian and
  Spanish turns are SURFACE TRANSLATION (Turn 2) or UNCLEAR (Turn 4 — generic conditionality).

- [ ] **Write fine-grained language-pair profiles (narrative, not tables) for ≥3 pairs.**
  Add a `\subsection{Language-Pair Profiles}` to `\section{sec:qualitative}` in the
  paper. For Indonesian/English, Spanish/English, and one new pair from the expansion:
  write a 2-paragraph story. What does the dialogue sound like in this pair? What
  cultural or register-level framing appears in the non-English turns that is absent
  from the English equivalent? Connect to known sociolinguistic properties where possible
  (Indonesian consensus-framing, Spanish normative policy register, Arabic deference-to-
  authority constructions). No tables — this section should read like a close reading.

- [ ] **NeurIPS paper polish: add figures, rewrite intro to open with the hook.**
  Add ≥2 figures:
  (a) Heatmap of ΔB by topic × language pair (rows = 5 topics, cols = language pairs
  including new expansion pairs; cells = ΔB; separate marker for direction reversals).
  (b) Per-dimension radar/spider chart of B's Schwartz probe deltas across conditions
  for one representative topic (e.g., UBI seed 17), one line per condition.
  Rewrite abstract paragraph 1 and intro to open with the dialogue hook example, not
  with "LLM agents are increasingly used to debate...". Move methods-heavy content to
  paragraph 2. Move the hypothetical pilot table to appendix or remove it.
  The paper's arc should be: here is a striking thing that happened → here is why it
  matters → here is how we measured it → here are the patterns.

- [ ] **Re-run top-divergence debates with updated engagement prompt and compare debate quality grades.**
  Status: runner ready, empirical rerun pending. Added
  `python3 -m modal run code/modal_bivad_runner.py::rerun_top_divergence` to run the
  minimum four-condition set (government surveillance and UBI, seed 17, Indonesian
  mixed-language + same-English) using the updated engagement prompt. Blocker: no Modal
  job was launched in this loop, so there are no new debate-quality grades yet.
  REVIEW AGENT 2026-06-27: All reviewed runs grade SURFACE ENGAGEMENT. Agents fill the
  three-label template (Strongest opponent point / Counterargument / View change) without
  actually responding to the specific argument their counterpart generated in the prior turn.
  Fixed: added engagement instruction to `debate_instructions()` in `code/modal_bivad_runner.py`:
  agents must "directly address the most value-relevant specific claim your counterpart made
  in their LAST turn before introducing any new argument." Re-run at minimum:
  - govt-surveillance seed 17 mixed-language (Indonesian) and same-English
  - UBI seed 17 mixed-language (Indonesian) and same-English
  Grade the new runs and compare debate quality. If debate grades improve to REAL DEBATE,
  check whether the cross-lingual elicitation signal (esp. the govt-surveillance Turn 4
  political/economic fork) survives or is strengthened.

- [ ] **Try culturally-loaded Indonesian/Spanish topics to get GENUINE ELICITATION beyond surveillance.**
  Status: runner ready, empirical scan pending. Added
  `python3 -m modal run code/modal_bivad_runner.py::cultural_topics` with the four proposed
  culturally loaded topics and Indonesian/Spanish target languages. The entrypoint writes
  batch-tagged artifacts and a manifest under `runs/bivad-local-lm/`. Blocker: no Modal
  job was launched in this loop, so no elicitation grades exist yet.
  REVIEW AGENT 2026-06-27: UBI runs produced SURFACE TRANSLATION in non-English turns.
  The topic lacks vocabulary where Indonesian/Spanish have distinct cultural anchors.
  Add topics where non-English agents are structurally more likely to invoke language-
  specific concepts. Candidates:
  - "gotong royong vs. individual responsibility in welfare policy" (Indonesian mutual-aid
    concept has no English equivalent; should surface in any welfare debate)
  - "keadilan sosial sebagai dasar kebijakan publik" (social justice framed through
    Pancasila's sila ke-5; Indonesian constitutional framing)
  - "solidaridad social como principio constitucional" (Latin American solidarity
    doctrine; appears in several Spanish-speaking constitutions)
  - "perlindungan data pribadi dan kedaulatan digital" (personal data and digital
    sovereignty; an active Indonesian legislative issue)
  Add these to the topic pool in `code/modal_bivad_runner.py` or equivalent; run mixed-
  language + same-English for seed 17 and grade elicitation quality manually.

- [x] **Clean dead code and failed-experiment debris.** Status: complete for local cleanup. Archived failed activation/CAA run outputs under `runs/archived/` with `runs/archived/README.md`; removed the definitively failed logit-bias implementation (`code/steer_language.py`) and obsolete Modal wrappers (`code/modal_steer_language.py`, `code/modal_steer_language_caa.py`); kept `code/modal_steer_language_activation.py` as the reusable Modal entrypoint for the next steering retry. Updated `code/README.md`, `code/preflight_bivad_local_lm.py`, `code/scan_divergence.py`, and `code/summarize_language_steering.py` so active docs point to activation steering and archived negative-result outputs remain discoverable. Re-ran the local verification suite; regression, validation, audit, evidence package, topic scan, no-dialogue summary, comparison refresh, LaTeX ref scan, and Tectonic compile all passed. `code/summarize_language_steering.py` still exits nonzero because the archived steering artifacts remain a confirmed negative result, which is expected and not a cleanup blocker.
  (a) Archive `runs/language-steering-activation/` and `runs/language-steering-caa/`
  (failed, documented) — move to `runs/archived/` with a README note.
  (b) Remove or rename `code/steer_language.py` (logit-bias, definitively failed).
  (c) Check `code/modal_steer_language.py`, `code/modal_steer_language_activation.py`,
  `code/modal_steer_language_caa.py` — delete if they are thin wrappers with no reuse.
  (d) Run local verification after cleanup: test_bivad_audit, validate, audit, evidence
  package, topic scan, no-dialogue summary, compare_five_conditions, tectonic compile.

- [ ] **Scale to larger model: run UBI seed 17 five conditions on Qwen2.5-14B-Instruct.**
  (After language expansion is running.) Run same five conditions for UBI seed 17
  Indonesian/English on Qwen2.5-14B-Instruct (Modal A10G). Add a model-comparison row
  to the results table. Key question: does ΔB=1.683 hold at 14B, or is it 7B-specific?

- [ ] **Tell a cultural drift story, not just a number story.**
  Within the language-pair profiles and the paper conclusion, write explicitly about
  what the drift patterns suggest culturally: why does Indonesian debate production
  amplify B's power dimension in surveillance topics? Why does translated-relay uniquely
  suppress B for Indonesian but not Spanish? Connect to the framing literatures in
  cross-cultural communication and NLP. The conclusion should leave the reader with a
  concrete claim about language-as-framing, not just "we measured five conditions".

---

## Verification Commands (run after each iteration)

```bash
python3 code/test_bivad_audit.py
python3 code/audit_bivad_evidence.py runs/bivad-local-lm --out-dir code/bivad-evidence-audit
python3 code/validate_bivad_artifacts.py runs/bivad-local-lm --out-dir code/bivad-evidence-audit
python3 code/make_bivad_evidence_package.py --out-dir code/bivad-evidence-audit
python3 code/analyze_topic_divergence.py
python3 code/summarize_no_dialogue.py
python3 code/compare_five_conditions.py
tectonic --outdir /tmp/mvd-tex-build draft/multilingual_value_drift_neurips.tex
# Check: 0 missing LaTeX refs, tectonic succeeds, validation passes
```
