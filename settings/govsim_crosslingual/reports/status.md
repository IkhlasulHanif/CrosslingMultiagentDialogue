# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

One C0 OpenAI smoke episode has run. Current OpenAI smoke, baseline, and contact artifacts are not Qwen3-1.7B research-matrix evidence.

Current blockers: none for the active OpenAI pilot stop condition. `reports/paper/main.tex` and compiled `reports/paper/main.pdf` now exist. The historical Qwen path remains blocked on a reachable local or Modal Qwen endpoint, but the active OpenAI benchmark path is unblocked.

Current empirical story: EN-ID C0/C1 baselines, both EN-ID C2 counterbalances, one EN-ID C3 free-choice episode, and the EN-ZH/ZH-ID ladder C0/C1/C2/C3 pilot cells ran successfully as OpenAI benchmark evidence. All newly run ladder baselines reached parseable harvest rate 1.0, survival time 1, total welfare 100.0, and gini 0.0: EN-ZH C0 `artifacts/results/govsim_c0_openai_baseline_20260712T180942Z.json`, EN-ZH C1 `artifacts/results/govsim_c1_openai_baseline_20260712T181003Z.json`, ZH-ID C0 `artifacts/results/govsim_c0_openai_baseline_20260712T181024Z.json`, and ZH-ID C1 `artifacts/results/govsim_c1_openai_baseline_20260712T181044Z.json`. G2 passed for EN-ID in `artifacts/logs/g2_en_id_openai_capability_floor_20260712T174935Z.json`; the ladder baselines also clear the parseability floor.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 constrain only the agents' visible dialogue output and validate channel compliance in transcripts. Output-channel instruction templates for EN/ID/ZH are implemented in `code/channel_instructions.py`; v2 process metrics now report EN/ID/ZH active-language shares, assigned-channel compliance, code switching, convergence, and off-pair language.

EN-ID C2 counterbalance A artifact `artifacts/results/govsim_c2_openai_en_id_a_20260712T175459Z.json` used 2 EN / 3 ID agents and reports survival time 1, total welfare 100.0, gini 0.0, parseable harvest rate 1.0, channel compliance 1.0, and language share EN 0.432 / ID 0.568. Counterbalance B artifact `artifacts/results/govsim_c2_openai_en_id_b_20260712T175531Z.json` used 3 EN / 2 ID agents and reports the same outcome metrics with language share EN 0.651 / ID 0.349.


Next useful work: **No unchecked checklist item found**.

## Question

Does cross-lingual contact reduce cooperative resource-management outcomes beyond monolingual capability baselines?

## State

| Field | Value |
|---|---|
| Setting | `govsim_crosslingual` |
| Benchmark | `B1` / GovSim |
| Bucket | cooperative_group |
| Priority | 5 |
| Phase | setup |
| Default model | `gpt-5.4-mini-2026-03-17` |
| Active benchmark model | `openai / gpt-5.4-mini-2026-03-17` |
| Model note | active benchmark execution model |
| Language pairs | EN-ID, EN-ZH, ZH-ID |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | survival_time, total_welfare, gini, parseable_harvest_rate |
| Acceptance gate | >=90% parseable harvests every round |
| Final report | `reports/paper/main.pdf` exists |

## Blockers / Errors

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T18:15:43+00:00` OK: Harness scaffold check passed
- `2026-07-12T18:16:12+00:00` OK: Harness scaffold check passed
- `2026-07-12T18:19:54+00:00` OK: Harness scaffold check passed
- `2026-07-12T18:20:07+00:00` OK: Produced final GovSim cross-lingual TeX/PDF report from OpenAI pilot evidence; tex=reports/paper/main.tex pdf=reports/paper/main.pdf.
- `2026-07-12T18:21:31+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260713_020902.txt
- `2026-07-12T18:21:31+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T18:21:47+00:00` OK: GovSim C0 OpenAI smoke produced transcript/result artifact=artifacts/results/govsim_c0_openai_smoke_20260712T182135Z.json transcript=artifacts/transcripts/govsim_c0_openai_smoke_20260712T182135Z.jsonl
- `2026-07-12T18:21:47+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 72 |
| Result summaries | 87 |
| Logs | 93 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
