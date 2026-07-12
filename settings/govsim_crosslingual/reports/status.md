# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence. OpenAI benchmark C0/C1 baseline entrypoints are wired and now reach the model-call stage with output-channel constraints, but no OpenAI baseline episode completed in this sandbox.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-11T23:30:20+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260711T232956Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260711T232956Z.jsonl`.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 constrain only the agents' visible dialogue output and validate channel compliance in transcripts. Output-channel instruction templates for EN/ID/ZH are implemented in `code/channel_instructions.py`; v2 process metrics now report EN/ID/ZH active-language shares, assigned-channel compliance, code switching, convergence, and off-pair language.

Current blockers: both `./scripts/run_openai_c1_baseline.sh` and `./scripts/run_openai_c0_baseline.sh` now attempt OpenAI model calls using the configured key file, but this sandbox cannot resolve `api.openai.com`. Current blocker artifacts are `artifacts/results/govsim_c1_openai_baseline_20260712T004213Z.json` with endpoint probe `artifacts/logs/openai_endpoint_probe_20260712T004213Z.json`, and `artifacts/results/govsim_c0_openai_baseline_20260712T004231Z.json` with endpoint probe `artifacts/logs/openai_endpoint_probe_20260712T004231Z.json`.

OpenAI benchmark override baseline state: C0 and C1 were rerun with `gpt-5.4-mini-2026-03-17` after the active channel-control update. The historical translation gate is superseded for this setting; C1 no longer blocks before model call on translated benchmark-rule review.


Next useful work: **Run C0 and C1 baselines**.

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

## Blockers / Errors

BLOCKED: GovSim C0 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c0_openai_baseline_20260712T004231Z.json; next=./scripts/run_openai_c0_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260712T004231Z.json

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T00:38:14+00:00` OK: Harness scaffold check passed
- `2026-07-12T00:38:51+00:00` RUNNING: Starting Codex implementation loop sleep=900s max_iters=infinite
- `2026-07-12T00:38:51+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260712_083851.txt
- `2026-07-12T00:42:04+00:00` OK: Harness scaffold check passed
- `2026-07-12T00:42:13+00:00` BLOCKED: GovSim C1 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c1_openai_baseline_20260712T004213Z.json; next=./scripts/run_openai_c1_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260712T004213Z.json
- `2026-07-12T00:42:31+00:00` BLOCKED: GovSim C0 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c0_openai_baseline_20260712T004231Z.json; next=./scripts/run_openai_c0_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260712T004231Z.json
- `2026-07-12T00:43:49+00:00` OK: Implemented EN/ID/ZH output-channel templates and v2 channel-compliance metrics; C0/C1 OpenAI baselines now bypass translated-rule gate and block only at api.openai.com DNS in this sandbox.
- `2026-07-12T00:44:01+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 43 |
| Result summaries | 2 |
| Logs | 78 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
