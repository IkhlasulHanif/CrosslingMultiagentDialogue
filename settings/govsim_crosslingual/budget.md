# B1 GovSim Run Budget

Status: draft budget for the first empirical matrix. Do not execute the full
matrix until GovSim license verification, local bring-up, output-channel
instruction templates, C0 smoke test, C0/C1 baselines, and the channel
compliance floor are complete.

## Scope

- Benchmark: GovSim fishery substrate only.
- Model: OpenAI `gpt-5.4-mini-2026-03-17` for active benchmark execution.
- Historical/backlog model plan: Qwen3-1.7B with Qwen3-8B escalation.
- Agents per episode: 5.
- Language pairs: EN-ID, EN-ZH, ZH-ID.
- Language definition: assigned interaction-output channel only. Benchmark
  rules/private state may remain in English. Do not block on translated rules.
- Conditions per pair Lx-Ly: C0 Lx-only output, C1 Ly-only output, C2 forced
  mixed assigned-channel output, C3 free-choice Lx/Ly output.
- C2 counterbalance cells: 2 Lx / 3 Ly and 3 Lx / 2 Ly.

## Gated Sequence

1. One C0 smoke episode to validate local GovSim execution, model adapter calls,
   transcript logging, parseable harvest extraction, and result summarization.
2. C0/C1 capability baselines with a small seed set.
3. Capability/channel check: continue only if at least 90% of episodes produce
   parseable harvests every round and assigned-channel output compliance is
   acceptable.
4. C2/C3 contact runs after baselines pass, preserving role-language
   counterbalancing.

## Initial Budget Envelope

Use the smallest seed count that can expose parser and wiring failures before
scaling:

| Stage | Cells | Seeds per cell | Episodes |
|---|---:|---:|---:|
| C0 smoke | 1 | 1 | 1 |
| One-pair C0/C1 pilot baselines | 2 | 3 | 6 |
| One-pair C2 pilot counterbalance | 2 | 3 | 6 |
| One-pair C3 pilot | 1 | 3 | 3 |

Initial pilot maximum: 16 episodes per pair after setup gates pass. Run one pair
at a time in this order: EN-ID, EN-ZH, ZH-ID. Increase seed count only after
parseability, transcript, result artifacts, and channel-compliance artifacts are
verified on disk.

## Pairwise Channel Matrix

Do not run an `n x n` sweep. Each pair is a controlled mini-matrix:

| Pair | C0 | C1 | C2 counterbalances | C3 |
|---|---|---|---|---|
| EN-ID | all EN output | all ID output | 2 EN/3 ID and 3 EN/2 ID | EN/ID free choice |
| EN-ZH | all EN output | all ZH output | 2 EN/3 ZH and 3 EN/2 ZH | EN/ZH free choice |
| ZH-ID | all ZH output | all ID output | 2 ZH/3 ID and 3 ZH/2 ID | ZH/ID free choice |

## Required Outputs Per Episode

- Raw transcript JSONL with visible text and stripped thinking separated.
- Result summary with survival time, total welfare, Gini, and parseable harvest
  rate.
- Process metrics summary for language share, code-switching, convergence,
  off-pair script use, and declared-language mismatches.
- Channel-compliance summary: fraction of output tokens in assigned channel,
  off-pair share, violations by agent and turn.
- Run metadata: condition, seed, model, language assignment, prompt version, and
  GovSim source/license revision.

## Stop Conditions

- License or upstream source cannot be verified.
- Local GovSim cannot be brought up reproducibly.
- Output-channel templates for EN, ID, and ZH are missing.
- Assigned-channel compliance cannot be measured for EN, ID, and ZH.
- C0/C1 baselines fail the 90% parseable-harvest capability floor.
- Any condition has missing transcripts or mismatched run metadata.

## Current State

No episodes have run. This budget records execution gates and a bounded pilot
size only; it is not empirical evidence.
