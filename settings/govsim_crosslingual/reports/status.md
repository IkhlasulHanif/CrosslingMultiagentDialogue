# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

Current empirical story: EN-ID C0/C1 baselines, both EN-ID C2 counterbalances, and one EN-ID C3 free-choice episode ran successfully as OpenAI benchmark evidence. C0 artifact `artifacts/results/govsim_c0_openai_baseline_20260712T174917Z.json` and C1 artifact `artifacts/results/govsim_c1_openai_baseline_20260712T174935Z.json` each report survival time 1, total welfare 100.0, gini 0.0, and parseable harvest rate 1.0. G2 passed in `artifacts/logs/g2_en_id_openai_capability_floor_20260712T174935Z.json`.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 constrain only the agents' visible dialogue output and validate channel compliance in transcripts. Output-channel instruction templates for EN/ID/ZH are implemented in `code/channel_instructions.py`; v2 process metrics now report EN/ID/ZH active-language shares, assigned-channel compliance, code switching, convergence, and off-pair language.

EN-ID C2 counterbalance A artifact `artifacts/results/govsim_c2_openai_en_id_a_20260712T175459Z.json` used 2 EN / 3 ID agents and reports survival time 1, total welfare 100.0, gini 0.0, parseable harvest rate 1.0, channel compliance 1.0, and language share EN 0.432 / ID 0.568. Counterbalance B artifact `artifacts/results/govsim_c2_openai_en_id_b_20260712T175531Z.json` used 3 EN / 2 ID agents and reports the same outcome metrics with language share EN 0.651 / ID 0.349.

EN-ID C3 free-choice artifact `artifacts/results/govsim_c3_openai_en_id_free_20260712T180413Z.json` allowed EN or ID output and reports survival time 1, total welfare 100.0, gini 0.0, parseable harvest rate 1.0, and harvests of 20 tons from all five agents. Its process metrics `artifacts/logs/govsim_c3_openai_en_id_free_20260712T180413Z_process_metrics.json` classify all pair-language output as EN (`language_share` EN 1.0 / ID 0.0), with no code-switching and no off-pair tokens. Because C3 has no assigned output channel, assigned-channel compliance is intentionally not evaluable for this artifact.

Process-metric caveat: the C1 baseline framework summary contained one Hebrew-script token. The process metric tokenizer now classifies Hebrew as off-pair `HE`; regenerated artifact `artifacts/logs/govsim_c1_openai_baseline_20260712T174935Z_process_metrics.json` reports `off_pair_token_count=1` while the assigned-channel compliance rate remains 1.0.


Next useful work: **Add ZH ladder runs: EN-ZH and ZH-ID C0/C1, then C2/C3 if baselines pass**.

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

- `2026-07-12T17:59:36+00:00` OK: GovSim C0 OpenAI smoke produced transcript/result artifact=artifacts/results/govsim_c0_openai_smoke_20260712T175925Z.json transcript=artifacts/transcripts/govsim_c0_openai_smoke_20260712T175925Z.jsonl
- `2026-07-12T17:59:36+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-12T17:59:36+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-12T17:59:37+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-12T17:59:39+00:00` OK: Codex pass 1 completed
- `2026-07-12T18:00:39+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260713_020039.txt
- `2026-07-12T18:04:27+00:00` OK: GovSim C3 OpenAI EN-ID free-choice produced artifact=artifacts/results/govsim_c3_openai_en_id_free_20260712T180413Z.json transcript=artifacts/transcripts/govsim_c3_openai_en_id_free_20260712T180413Z.jsonl
- `2026-07-12T18:05:53+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 60 |
| Result summaries | 63 |
| Logs | 92 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
