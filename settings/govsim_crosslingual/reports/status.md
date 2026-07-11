# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only, not Qwen3-1.7B research-matrix evidence.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-11T12:14:37+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260711T121414Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260711T121414Z.jsonl`; process metrics are `artifacts/logs/govsim_c0_openai_smoke_20260711T121414Z_process_metrics.json`. That smoke had 5/5 parseable harvests, survival_time 1, total_welfare 50.0, gini 0.0, and EN language share 1.0. This is runner bring-up evidence only.

Current blockers: no Qwen3-1.7B C0/C1 baseline has run yet, the ID translation pack still needs human review, and the real upstream PathFinder submodule is still unresolved for full upstream entry-point replication. The Qwen C0 command `./scripts/run_qwen_c0_baseline.sh` is wired, but the latest attempt at `2026-07-11T12:30:36+00:00` is blocked at `http://127.0.0.1:8000/v1/chat/completions` by sandbox/network permission `[Errno 1] Operation not permitted`; artifact `artifacts/results/govsim_c0_qwen_baseline_20260711T123036Z.json`. The Qwen C1 ID command `./scripts/run_qwen_c1_baseline.sh` is wired through the same runner with Indonesian prompts, and the latest attempt is blocked by the same endpoint permission issue; artifact `artifacts/results/govsim_c1_qwen_baseline_20260711T121153Z.json`.

OpenAI smoke retry state: the latest `./harness.sh run-smoke` attempt succeeded at `2026-07-11T12:14:37+00:00`. Earlier transient DNS failures for `api.openai.com` are recorded in prior result artifacts. The OpenAI smoke bypasses PathFinder with the setting-local adapter and must not be reported as final benchmark evidence.

Source/license state: `licenses.md` and `artifacts/logs/source_license_status.json` report `READY_FOR_REVIEW`. The local GovSim checkout is `vendor/govsim` at upstream `https://github.com/giorgio-piatti/GovSim.git`, branch `main`, commit `1d11adf047b24fa2ba0d44a1d4931015ea2e5210`. The local license file is MIT license text, 1071 bytes, SHA-256 `55be1b08220f411edf83dbf7ac9b3b3e7e56b92fb2ef9b10af91526edd38f15e`. PathFinder source resolution was retried from canonical submodule `https://github.com/giorgiopiatti/PathFinder.git` at commit `69b8d646ad3e618380dd0d47ec4d1e8d2d4c930e`; generated cache files blocking clone were removed, and the remaining blocker is GitHub DNS (`Could not resolve host: github.com`) for `git ls-remote`, `git submodule update --init --depth 1 pathfinder`, and `curl -L -I`; latest artifact `artifacts/logs/govsim_pathfinder_source_resolution_20260711T121143Z.log`.

Translation state: `config/translations/en_id_fishery_draft.json` now covers the upstream fishery prompt primitives used by the current runner: system rules, dynamic resource text, memory text, harvest tasks, conversation instructions, summaries, and numeric limit extraction. `artifacts/logs/translation_status.json` reports `DRAFT` because `source_coverage_complete` is true but `human_checked` is false.


Next useful work: **Human-check ID translation**, then rerun the Qwen C0/C1 baseline commands from an environment allowed to reach the local or Modal Qwen OpenAI-compatible endpoint.

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

BLOCKED: GovSim C0 Qwen baseline blocked at http://127.0.0.1:8000/v1/chat/completions: LocalModelError: Local model endpoint unavailable at http://127.0.0.1:8000/v1/chat/completions: [Errno 1] Operation not permitted; artifact=artifacts/results/govsim_c0_qwen_baseline_20260711T123036Z.json

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-11T12:14:37+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-11T12:14:37+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-11T12:14:37+00:00` BLOCKED: git add failed during checkpoint: The following paths are ignored by one of your .gitignore files:
settings/govsim_crosslingual/.venv
hint: Use -f if you really want to add them.
hint: Disable this message with "git config set advice.addIgnoredFile false"
- `2026-07-11T12:14:37+00:00` OK: Codex pass 4 completed
- `2026-07-11T12:29:37+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260711_202937.txt
- `2026-07-11T12:30:32+00:00` OK: Harness scaffold check passed
- `2026-07-11T12:30:36+00:00` BLOCKED: GovSim C0 Qwen baseline blocked at http://127.0.0.1:8000/v1/chat/completions: LocalModelError: Local model endpoint unavailable at http://127.0.0.1:8000/v1/chat/completions: [Errno 1] Operation not permitted; artifact=artifacts/results/govsim_c0_qwen_baseline_20260711T123036Z.json
- `2026-07-11T12:32:07+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 6 |
| Result summaries | 20 |
| Logs | 42 |

## Open Questions

- Are translated rules/prompts human-checked for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
