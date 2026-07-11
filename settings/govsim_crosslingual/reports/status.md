# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence. OpenAI benchmark-override C0/C1 baseline entrypoints are wired, but no OpenAI baseline episode completed in this sandbox.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-11T23:30:20+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260711T232956Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260711T232956Z.jsonl`.

Current blockers: no Qwen3-1.7B C0/C1 baseline has run yet, the ID translation pack still needs human review, no local/Modal Qwen endpoint is reachable from this sandbox, and `api.openai.com` DNS resolution is currently unavailable from this sandbox for OpenAI benchmark baseline calls.

OpenAI benchmark override baseline state: `./scripts/run_openai_c0_baseline.sh` was attempted again at `2026-07-11T23:46:06+00:00`; it attempted an OpenAI model call with `gpt-4.1-mini` and is blocked by DNS resolution for `api.openai.com`, artifact `artifacts/results/govsim_c0_openai_baseline_20260711T234605Z.json`, endpoint probe `artifacts/logs/openai_endpoint_probe_20260711T234606Z.json`. The endpoint probe includes both `curl` and `urllib` evidence; `curl` reports `Could not resolve host: api.openai.com`, and `urllib` reports `[Errno 8] nodename nor servname provided, or not known`. `./scripts/run_openai_c1_baseline.sh` was attempted at `2026-07-11T23:46:25+00:00`; it stopped before any model call on the translation review gate, artifact `artifacts/results/govsim_c1_openai_baseline_20260711T234625Z.json`.

The Qwen C0 command `./scripts/run_qwen_c0_baseline.sh` is wired and was attempted at `2026-07-11T16:55:11+00:00` after resolving the PathFinder source and minimal import dependencies. It is blocked at `http://127.0.0.1:8000/v1/chat/completions` by sandbox/network permission `[Errno 1] Operation not permitted`; artifact `artifacts/results/govsim_c0_qwen_baseline_20260711T165511Z.json`. The attached endpoint probe `artifacts/logs/qwen_endpoint_probe_20260711T165511Z.json` found no reachable server at `http://127.0.0.1:8000/v1/models`.

The Qwen C1 ID command `./scripts/run_qwen_c1_baseline.sh` enforces the human translation gate before any model call. It was attempted at `2026-07-11T17:15:41+00:00` and exited `2` before a model call; artifact `artifacts/results/govsim_c1_qwen_baseline_20260711T171541Z.json`. The translation pack `config/translations/en_id_fishery_draft.json` covers the active fishery prompt primitives and passes mechanical QA for all 17 entries, but remains `DRAFT` because `human_checked=false`. The latest strict translation check regenerated `artifacts/logs/translation_status.json` and `artifacts/logs/translation_human_review_packet.md` in this pass, then exited `3` as expected for a structurally valid pack awaiting human review.


Next useful work: **Human-check ID translation**.

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
| Default model | `Qwen3-1.7B` |
| Active benchmark model | `openai / gpt-4.1-mini` |
| Model note | benchmark execution override |
| Language pairs | EN-ID |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | survival_time, total_welfare, gini, parseable_harvest_rate |
| Acceptance gate | >=90% parseable harvests every round |

## Blockers / Errors

BLOCKED: GovSim C1 OpenAI baseline blocked before model call by translation gate: TranslationPackNotReady: ID translation pack is not ready for benchmark use: status=DRAFT, source_coverage_complete=True, human_checked=False, pack=/Users/ikhlasul.hanif/Documents/MultiAgent/settings/govsim_crosslingual/config/translations/en_id_fishery_draft.json; artifact=artifacts/results/govsim_c1_openai_baseline_20260711T234625Z.json; next=./scripts/run_openai_c1_baseline.sh

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T23:45:23+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260712_074523.txt
- `2026-07-11T23:46:06+00:00` BLOCKED: GovSim C0 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c0_openai_baseline_20260711T234605Z.json; next=./scripts/run_openai_c0_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260711T234606Z.json
- `2026-07-11T23:46:25+00:00` BLOCKED: GovSim C1 OpenAI baseline blocked before model call by translation gate: TranslationPackNotReady: ID translation pack is not ready for benchmark use: status=DRAFT, source_coverage_complete=True, human_checked=False, pack=/Users/ikhlasul.hanif/Documents/MultiAgent/settings/govsim_crosslingual/config/translations/en_id_fishery_draft.json; artifact=artifacts/results/govsim_c1_openai_baseline_20260711T234625Z.json; next=./scripts/run_openai_c1_baseline.sh
- `2026-07-11T23:47:42+00:00` OK: Harness scaffold check passed
- `2026-07-11T23:48:33+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_074523.txt
- `2026-07-11T23:48:33+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T23:48:56+00:00` OK: GovSim C0 OpenAI smoke produced transcript/result artifact=artifacts/results/govsim_c0_openai_smoke_20260711T234837Z.json transcript=artifacts/transcripts/govsim_c0_openai_smoke_20260711T234837Z.jsonl
- `2026-07-11T23:48:56+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 42 |
| Result summaries | 135 |
| Logs | 75 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
