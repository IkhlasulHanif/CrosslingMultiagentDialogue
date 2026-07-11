# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-11T16:59:10+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260711T165849Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260711T165849Z.jsonl`.

Current blockers: no Qwen3-1.7B C0/C1 baseline has run yet, the ID translation pack still needs human review, and no local/Modal Qwen endpoint is reachable from this sandbox.

The Qwen C0 command `./scripts/run_qwen_c0_baseline.sh` is wired and was attempted at `2026-07-11T16:55:11+00:00` after resolving the PathFinder source and minimal import dependencies. It is blocked at `http://127.0.0.1:8000/v1/chat/completions` by sandbox/network permission `[Errno 1] Operation not permitted`; artifact `artifacts/results/govsim_c0_qwen_baseline_20260711T165511Z.json`. The attached endpoint probe `artifacts/logs/qwen_endpoint_probe_20260711T165511Z.json` found no reachable server at `http://127.0.0.1:8000/v1/models`.

The Qwen C1 ID command `./scripts/run_qwen_c1_baseline.sh` enforces the human translation gate before any model call. It was attempted at `2026-07-11T17:15:41+00:00` and exited `2` before a model call; artifact `artifacts/results/govsim_c1_qwen_baseline_20260711T171541Z.json`. The translation pack `config/translations/en_id_fishery_draft.json` covers the active fishery prompt primitives and passes mechanical QA for all 17 entries, but remains `DRAFT` because `human_checked=false`. On this pass, `python3 code/translation_pack.py --root . --out artifacts/logs/translation_status.json --review-out artifacts/logs/translation_human_review_packet.md --strict` regenerated the artifacts and exited `3`, as expected for a structurally valid pack awaiting human review.

Source/license state: `licenses.md` and `artifacts/logs/source_license_status.json` report `READY_FOR_REVIEW`. The source manifest records the paper/README canonical GovSim URL `https://github.com/giorgiopiatti/GovSim`; the local checkout remote resolves to `https://github.com/giorgio-piatti/GovSim.git`, branch `main`, commit `1d11adf047b24fa2ba0d44a1d4931015ea2e5210`. The local license file is MIT license text, 1071 bytes, SHA-256 `55be1b08220f411edf83dbf7ac9b3b3e7e56b92fb2ef9b10af91526edd38f15e`.


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
| Language pairs | EN-ID |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | survival_time, total_welfare, gini, parseable_harvest_rate |
| Acceptance gate | >=90% parseable harvests every round |

## Blockers / Errors

BLOCKED: Regenerated translation_status.json and translation_human_review_packet.md; strict translation check exited 3 because the EN-ID fishery pack is structurally valid but still DRAFT with 17 entries, source_coverage_complete=true, human_checked=false, mechanical_qa=PASS. Next after human review: set accepted entries human_checked=true, then run `python3 code/translation_pack.py --root . --out artifacts/logs/translation_status.json --review-out artifacts/logs/translation_human_review_packet.md --strict`.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T17:15:41+00:00` BLOCKED: GovSim C1 Qwen baseline blocked before model call by translation gate: TranslationPackNotReady: ID translation pack is not ready for benchmark use: status=DRAFT, source_coverage_complete=True, human_checked=False, pack=/Users/ikhlasul.hanif/Documents/MultiAgent/settings/govsim_crosslingual/config/translations/en_id_fishery_draft.json; artifact=artifacts/results/govsim_c1_qwen_baseline_20260711T171541Z.json
- `2026-07-11T17:16:13+00:00` BLOCKED: Regenerated translation_status.json and translation_human_review_packet.md; strict translation check exited 3 because the EN-ID fishery pack is structurally valid but still DRAFT with 17 entries, source_coverage_complete=true, human_checked=false, mechanical_qa=PASS. Next after human review: set accepted entries human_checked=true, then run `python3 code/translation_pack.py --root . --out artifacts/logs/translation_status.json --review-out artifacts/logs/translation_human_review_packet.md --strict`.
- `2026-07-11T17:17:03+00:00` OK: Harness scaffold check passed
- `2026-07-11T17:17:26+00:00` OK: Focused no-network validation passed under setting-local .venv: `.venv/bin/python -m unittest scripts/test_translation_pack.py scripts/test_qwen_baseline_blockers.py scripts/test_local_model_adapter.py scripts/test_process_metrics.py` ran 16 tests. System python3 lacks omegaconf, so .venv is the supported validation environment.
- `2026-07-11T17:18:10+00:00` OK: Codex implementation pass exited 0; log=codex_once_20260712_011412.txt
- `2026-07-11T17:18:10+00:00` RUNNING: Parent harness starting post-Codex smoke/experiment attempt
- `2026-07-11T17:18:44+00:00` OK: GovSim C0 OpenAI smoke produced transcript/result artifact=artifacts/results/govsim_c0_openai_smoke_20260711T171813Z.json transcript=artifacts/transcripts/govsim_c0_openai_smoke_20260711T171813Z.jsonl
- `2026-07-11T17:18:45+00:00` OK: scripts/run_smoke.sh exited 0

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 21 |
| Result summaries | 65 |
| Logs | 54 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
