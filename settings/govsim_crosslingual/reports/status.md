# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence. OpenAI benchmark C0/C1 baseline entrypoints are wired with output-channel constraints, and the shared adapter now uses `max_completion_tokens` for OpenAI GPT-5-style chat-completions calls while preserving `max_tokens` for local/vLLM-compatible Qwen endpoints.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-12T03:22:55+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260712T032243Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260712T032243Z.jsonl`. This is runner bring-up evidence only; no C0/C1 baseline episode has completed yet.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 constrain only the agents' visible dialogue output and validate channel compliance in transcripts. Output-channel instruction templates for EN/ID/ZH are implemented in `code/channel_instructions.py`; v2 process metrics now report EN/ID/ZH active-language shares, assigned-channel compliance, code switching, convergence, and off-pair language.

Current blockers: C0/C1 baseline commands reach the model-call path, but this sandbox currently cannot resolve `api.openai.com`. Fresh baseline blocker artifacts from the 2026-07-12T03:38Z retry are `artifacts/results/govsim_c0_openai_baseline_20260712T033844Z.json` with endpoint probe `artifacts/logs/openai_endpoint_probe_20260712T033844583749Z.json`, and `artifacts/results/govsim_c1_openai_baseline_20260712T033851Z.json` with endpoint probe `artifacts/logs/openai_endpoint_probe_20260712T033851694982Z.json`. Curl reports `Could not resolve host: api.openai.com`; urllib reports `[Errno 8] nodename nor servname provided, or not known`. No C0/C1 baseline episode has completed yet.

OpenAI benchmark override baseline state: C0 and C1 were rerun with `gpt-5.4-mini-2026-03-17` after the active channel-control update. The historical translation gate is superseded for this setting; C1 no longer blocks before model call on translated benchmark-rule review. OpenAI artifacts record configured key sources as `configured_file:<candidate>` or `env:<name>` instead of absolute secret-file paths. Endpoint probe filenames are now microsecond-stamped so parallel baseline retries keep separate probe artifacts. The next retry commands after DNS is available are `./scripts/run_openai_c0_baseline.sh` and `./scripts/run_openai_c1_baseline.sh`.


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

BLOCKED: Scoped commit/push attempt for fresh GovSim C0/C1 baseline DNS blocker artifacts blocked by sandbox permission: git could not create /Users/ikhlasul.hanif/Documents/MultiAgent/.git/index.lock (Operation not permitted). Relevant local artifacts remain under settings/govsim_crosslingual/.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T03:38:51+00:00` BLOCKED: GovSim C1 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c1_openai_baseline_20260712T033851Z.json; next=./scripts/run_openai_c1_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260712T033851694982Z.json
- `2026-07-12T03:40:05+00:00` OK: Harness scaffold check passed
- `2026-07-12T03:40:36+00:00` BLOCKED: Scoped commit/push attempt for fresh GovSim C0/C1 baseline DNS blocker artifacts blocked by sandbox permission: git could not create /Users/ikhlasul.hanif/Documents/MultiAgent/.git/index.lock (Operation not permitted). Relevant local artifacts remain under settings/govsim_crosslingual/.
- `2026-07-12T03:40:44+00:00` OK: Harness scaffold check passed
- `2026-07-12T03:41:06+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_113757.txt
- `2026-07-12T03:41:06+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-12T03:41:24+00:00` OK: GovSim C0 OpenAI smoke produced transcript/result artifact=artifacts/results/govsim_c0_openai_smoke_20260712T034111Z.json transcript=artifacts/transcripts/govsim_c0_openai_smoke_20260712T034111Z.jsonl
- `2026-07-12T03:41:25+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 52 |
| Result summaries | 43 |
| Logs | 87 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
