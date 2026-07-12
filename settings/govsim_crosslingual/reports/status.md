# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

Current empirical story: EN-ID C0/C1 baselines and both EN-ID C2 counterbalances ran successfully as OpenAI benchmark evidence. C0 artifact `artifacts/results/govsim_c0_openai_baseline_20260712T174917Z.json` and C1 artifact `artifacts/results/govsim_c1_openai_baseline_20260712T174935Z.json` each report survival time 1, total welfare 100.0, gini 0.0, and parseable harvest rate 1.0. G2 passed in `artifacts/logs/g2_en_id_openai_capability_floor_20260712T174935Z.json`.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 constrain only the agents' visible dialogue output and validate channel compliance in transcripts. Output-channel instruction templates for EN/ID/ZH are implemented in `code/channel_instructions.py`; v2 process metrics now report EN/ID/ZH active-language shares, assigned-channel compliance, code switching, convergence, and off-pair language.

EN-ID C2 counterbalance A artifact `artifacts/results/govsim_c2_openai_en_id_a_20260712T175459Z.json` used 2 EN / 3 ID agents and reports survival time 1, total welfare 100.0, gini 0.0, parseable harvest rate 1.0, channel compliance 1.0, and language share EN 0.432 / ID 0.568. Counterbalance B artifact `artifacts/results/govsim_c2_openai_en_id_b_20260712T175531Z.json` used 3 EN / 2 ID agents and reports the same outcome metrics with language share EN 0.651 / ID 0.349.

Process-metric caveat: the C1 baseline framework summary contained one Hebrew-script token. The process metric tokenizer now classifies Hebrew as off-pair `HE`; regenerated artifact `artifacts/logs/govsim_c1_openai_baseline_20260712T174935Z_process_metrics.json` reports `off_pair_token_count=1` while the assigned-channel compliance rate remains 1.0.

Pairwise channel-run plan state: `plan/channel_run_plan.md` now lists EN-ID, EN-ZH, and ZH-ID C0/C1 commands and C2 counterbalances. Thin ladder wrappers are available at `scripts/run_openai_en_zh_c0_baseline.sh`, `scripts/run_openai_en_zh_c1_baseline.sh`, `scripts/run_openai_zh_id_c0_baseline.sh`, and `scripts/run_openai_zh_id_c1_baseline.sh`.


Next useful work: **Implement/run EN-ID C3 free-choice episodes**.

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
| Final report | missing `reports/paper/main.pdf` |

## Blockers / Errors

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T17:48:31+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260713_014831.txt
- `2026-07-12T17:49:29+00:00` OK: GovSim C0 OpenAI baseline produced transcript/result artifact=artifacts/results/govsim_c0_openai_baseline_20260712T174917Z.json transcript=artifacts/transcripts/govsim_c0_openai_baseline_20260712T174917Z.jsonl
- `2026-07-12T17:49:50+00:00` OK: GovSim C1 OpenAI baseline produced transcript/result artifact=artifacts/results/govsim_c1_openai_baseline_20260712T174935Z.json transcript=artifacts/transcripts/govsim_c1_openai_baseline_20260712T174935Z.jsonl
- `2026-07-12T17:55:10+00:00` OK: GovSim C2 OpenAI EN-ID counterbalance A produced artifact=artifacts/results/govsim_c2_openai_en_id_a_20260712T175459Z.json transcript=artifacts/transcripts/govsim_c2_openai_en_id_a_20260712T175459Z.jsonl
- `2026-07-12T17:55:41+00:00` OK: GovSim C2 OpenAI EN-ID counterbalance B produced artifact=artifacts/results/govsim_c2_openai_en_id_b_20260712T175531Z.json transcript=artifacts/transcripts/govsim_c2_openai_en_id_b_20260712T175531Z.jsonl
- `2026-07-12T17:56:10+00:00` OK: Updated GovSim process metrics to tokenize Hebrew script as off-pair HE and regenerated fresh C0/C1 process summaries; focused process-metrics tests pass.
- `2026-07-12T17:56:20+00:00` OK: GovSim EN-ID G2 capability floor passed for OpenAI baselines; artifact=artifacts/logs/g2_en_id_openai_capability_floor_20260712T174935Z.json.
- `2026-07-12T17:57:36+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 58 |
| Result summaries | 59 |
| Logs | 91 |

## Open Questions

- EN-ID C3 free-choice episodes are not implemented/run yet.
- EN-ZH and ZH-ID C0/C1 ladder baselines remain open.
- The final TeX/PDF is still missing.
