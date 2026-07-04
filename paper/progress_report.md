# Cross-Lingual Value Drift: Progress Report

Date: 2026-06-29  
Repository: `MultiAgent`

## 1. Objective

This project studies whether the **language used during agent interaction**
changes value movement in multi-agent debate.

Each agent has two independent settings:

| Field | Meaning | Examples |
|---|---|---|
| `persona` | cultural identity assigned to the agent | `persona=id`, `persona=us` |
| `lang` | language used to generate the response | `lang=id`, `lang=en` |

Example: `persona=id, lang=en` means an Indonesian-persona agent writing in
English. The main question is whether cross-lingual interaction causes value
movement beyond ordinary language-prior differences.

## 2. Experimental Setting

Model: `Qwen/Qwen3-4B`  
Inference backend: Modal  
Main item: `society_over_individual`  
Statement: “The interests of society should take priority over the rights of the individual.”

Primary ID-US cells:

| Cell | Agent A | Agent B | Purpose |
|---|---|---|---|
| `idus_idid` | `persona=id, lang=id` | `persona=us, lang=id` | Mono-ID baseline |
| `idus_enen` | `persona=id, lang=en` | `persona=us, lang=en` | Mono-EN baseline |
| `idus_nat` | `persona=id, lang=id` | `persona=us, lang=en` | Natural cross-lingual cell |
| `idus_inv` | `persona=id, lang=en` | `persona=us, lang=id` | Inverted cross-lingual cell |
| `id_aln` | `persona=id, lang=id` | `persona=id, lang=en` | Same-persona language leakage test |

Interpretation rule:

- A turn-1 difference is a **generation-language prior**.
- A cross-lingual effect requires movement after interaction that is not already explained by matched monolingual baselines.
- Therefore, compare `idus_nat` against both `idus_idid` and `idus_enen` before making a causal claim.

## 3. Loop Design

The experiment is run by `harness_codex.sh`, which delegates to `harness.sh`.

Current loop behavior:

- Reads phase state from `.harness_state_codex`.
- Runs coding, judging, reading, discovery, and supervisor agents through Codex.
- Uses Modal for model inference.
- Saves transcripts, judgments, logs, and selected golden examples under `artifacts/`.
- A detached `screen` session keeps the Codex harness loop running.

Active loop:

- Screen session: `harness_codex_loop`
- Log: `artifacts/logs/harness_codex_screen_loop.log`

## 4. Completed Work

### Phase 0: Item Screening

Completed. Candidate items were screened for persona divergence and non-saturated `P(agree)`.

Key artifacts:

- `artifacts/results/wvs_items_locked.json`
- `artifacts/results/wvs_screen_summary.md`

Selected ID-US item:

- `society_over_individual`

### Phase 1: Pilot Debate

Completed. The pilot verified that the debate engine can produce readable two-agent transcripts.

Validated properties:

- clear turn boundaries,
- separate `persona` and `lang` controls,
- per-turn `P(agree)` probes,
- saved prompt and seed metadata.

Key artifact:

- `artifacts/transcripts/phase1_pilot.json`

### Phase 2: Validity Loop

Completed. The debate environment passed the reader rubric.

Validity checks:

- no immediate sycophantic collapse,
- agents respond to each other,
- assigned languages mostly hold,
- personas remain visible,
- no major repetition or degeneration.

Recent passing batch:

- `artifacts/transcripts/phase2_iter9_17.json`
- `artifacts/transcripts/phase2_iter9_31.json`
- `artifacts/transcripts/phase2_iter9_89.json`
- `plan/phase_notes/phase2_validity.md`

### Phase 3: Discovery Loop

In progress. The loop is generating multi-cell debate batches and judgments.

Current artifact state:

- 169 transcript-side files under `artifacts/transcripts`
- 30 selected golden transcripts under `artifacts/golden`
- Phase 3 manifests through `phase3_iter5_manifest.txt`
- discovery notes in `plan/phase_notes/phase3_discovery.md`

## 5. Current Findings With Examples

These are qualitative discovery findings, not final metrics.

### Finding 1: Opening language priors are strong

`persona=id` often opens pro-society with `lang=id`, but opens more rights-forward with `lang=en`.

Matched seed 17 example:

| Cell | Agent A setting | Opening | `P(agree)` |
|---|---|---|---|
| `idus_idid` | `persona=id, lang=id` | “Saya setuju dengan pernyataan tersebut...” | `0.6025` |
| `idus_enen` | `persona=id, lang=en` | “I DISAGREE with the statement...” | `0.4943` |

Files:

- `artifacts/transcripts/phase3_iter0_idus_idid_17.json`
- `artifacts/golden/phase3_iter0_idus_enen_17.json`

Interpretation: this is a language-prior difference at turn 1, not cross-lingual interaction drift.

### Finding 2: Natural cross-lingual debates show ID-side softening

In `idus_nat`, Agent A is `persona=id, lang=id`; Agent B is `persona=us, lang=en`.

Example:

- File: `artifacts/golden/phase3_iter0_idus_nat_17.json`
- Agent A opens: “Saya setuju...” with `P(agree)=0.6121`.
- Agent B introduces a U.S. constitutional-rights frame.
- Agent A then says individual rights remain protected within collective values.
- Agent A drops to `P(agree)=0.5396`.

Interpretation: this is a candidate cross-lingual movement case, but it must be compared against `idus_idid` and `idus_enen` for the same seed.

### Finding 3: Same-persona cross-lingual debates still move

In `id_aln`, both agents use `persona=id`, but their languages differ:

- Agent A: `persona=id, lang=id`
- Agent B: `persona=id, lang=en`

Example:

- File: `artifacts/golden/phase3_iter0_id_aln_17.json`
- Agent A starts pro-society in Indonesian.
- Agent B challenges strict collective priority in English.
- Agent A shifts toward rights-balancing.
- Agent A trajectory: `0.6121 -> 0.5077 -> 0.4808`.

Interpretation: matched persona does not remove language-channel effects. This supports the need for same-persona leakage tests.

### Finding 4: Monolingual baselines are required

Some rights-ward movement appears inside monolingual English debates.

Example:

- File: `artifacts/golden/phase3_iter0_idus_enen_17.json`
- Agent A: `persona=id, lang=en`
- Agent A moves from `P(agree)=0.4943` to `0.3316`.

Interpretation: similar rights-ward movement in `idus_nat` cannot be attributed to cross-lingual interaction unless it exceeds this mono-EN baseline.

## 6. Reporting Artifacts

Draft narrative:

- `paper/story.tex`
- `paper/story.pdf`

This draft summarizes the research story and includes a dialogue-level comparison between monolingual and cross-lingual cells.

## 7. Next Steps

1. Continue Phase 3 until enough matched triples are available:
   - `idus_idid`
   - `idus_enen`
   - `idus_nat`
2. For each matched seed, compare the first three turns side by side.
3. Report three quantities separately:
   - turn-1 language-prior gap,
   - movement inside monolingual baselines,
   - excess movement in the cross-lingual cell.
4. Add or prioritize `idus_inv` to test whether drift direction follows language rather than persona.
5. Move to Phase 4 after selecting representative golden transcripts for probe sanity checks.

## 8. Risks and Caveats

- Current findings are qualitative and should not be reported as final metrics.
- `lang=en` can change the opening stance before interaction begins.
- Some transcripts contain language or script artifacts.
- Final claims must measure `P(agree)` in both English and Indonesian to reduce probe-language bias.
