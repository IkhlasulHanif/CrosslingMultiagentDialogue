# B1 GovSim Run Budget

Status: draft budget for the first empirical matrix. Do not execute the full
matrix until GovSim license verification, local bring-up, EN-ID prompt
translation, human translation check, C0 smoke test, C0/C1 baselines, and the G2
capability floor are complete.

## Scope

- Benchmark: GovSim fishery substrate only.
- Model: Qwen3-1.7B for all initial runs.
- Escalation: Qwen3-8B only if the whole benchmark fails the G2 capability floor.
- Agents per episode: 5.
- Language pair: EN-ID.
- Conditions: C0 EN-mono, C1 ID-mono, C2 forced mixed, C3 free choice.
- C2 counterbalance cells: 2 EN / 3 ID and 3 EN / 2 ID.

## Gated Sequence

1. One C0 smoke episode to validate local GovSim execution, model adapter calls,
   transcript logging, parseable harvest extraction, and result summarization.
2. C0/C1 capability baselines with a small seed set.
3. G2 capability check: continue only if at least 90% of episodes produce
   parseable harvests every round and no setup bug explains failures.
4. C2/C3 contact runs after baselines pass, preserving role-language
   counterbalancing.

## Initial Budget Envelope

Use the smallest seed count that can expose parser and wiring failures before
scaling:

| Stage | Cells | Seeds per cell | Episodes |
|---|---:|---:|---:|
| C0 smoke | 1 | 1 | 1 |
| C0/C1 pilot baselines | 2 | 3 | 6 |
| C2 pilot counterbalance | 2 | 3 | 6 |
| C3 pilot | 1 | 3 | 3 |

Initial pilot maximum: 16 episodes after setup gates pass. Increase seed count
only after parseability, transcript, and result artifacts are verified on disk.

## Required Outputs Per Episode

- Raw transcript JSONL with visible text and stripped thinking separated.
- Result summary with survival time, total welfare, Gini, and parseable harvest
  rate.
- Process metrics summary for language share, code-switching, convergence,
  off-pair script use, and declared-language mismatches.
- Run metadata: condition, seed, model, language assignment, prompt version, and
  GovSim source/license revision.

## Stop Conditions

- License or upstream source cannot be verified.
- Local GovSim cannot be brought up reproducibly.
- Human-checked ID prompt translations are unavailable.
- C0/C1 baselines fail the 90% parseable-harvest capability floor.
- Any condition has missing transcripts or mismatched run metadata.

## Current State

No episodes have run. This budget records execution gates and a bounded pilot
size only; it is not empirical evidence.
