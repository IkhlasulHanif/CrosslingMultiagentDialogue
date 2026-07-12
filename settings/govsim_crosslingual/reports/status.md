# B1 GovSim Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and ZH-ID. The old Qwen plan is historical/backlog context only.

One C0 OpenAI smoke episode has run. It is runner bring-up evidence only. OpenAI benchmark C0/C1 baseline entrypoints are wired, but no OpenAI baseline episode completed in this sandbox.

Current empirical story: `./harness.sh run-smoke` most recently succeeded at `2026-07-11T23:30:20+00:00`, executing one EN C0 fishery episode with the upstream GovSim fishery environment and prompt text. The result artifact is `artifacts/results/govsim_c0_openai_smoke_20260711T232956Z.json`; the transcript is `artifacts/transcripts/govsim_c0_openai_smoke_20260711T232956Z.jsonl`.

Current control definition: language means required interaction-output channel, not translated benchmark rules. For this setting, benchmark rules/private state may remain in English; C0/C1/C2/C3 should constrain only the agents' visible dialogue output and validate channel compliance in transcripts. The next implementation work is output-channel instruction templates for EN/ID/ZH plus channel-compliance metrics for EN share, ID share, ZH share, code switching, and off-pair language.

Current blockers: OpenAI DNS now resolves from this machine, but the active shell did not expose `OPENAI_API_KEY` directly. The setting-local OpenAI runners can read `../../secrets/open_ai.txt`; rerun the runners through the harness path rather than relying on the parent shell env. If an OpenAI call still fails, the blocker artifact should distinguish DNS, certificate, auth, quota, and model-not-found.

OpenAI benchmark override baseline state: `./scripts/run_openai_c0_baseline.sh` was attempted earlier with the old OpenAI model name and failed when `api.openai.com` DNS was unavailable. That DNS finding is historical; rerun with `gpt-5.4-mini-2026-03-17` before treating OpenAI as blocked.


Next useful work: **Add output-channel instruction templates for EN, ID, and ZH**.

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

None current; a later event marks the previous blocker as superseded.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T00:09:22+00:00` OK: Codex pass 22 completed
- `2026-07-12T00:24:22+00:00` RUNNING: Starting Codex implementation pass; log=codex_once_20260712_082422.txt
- `2026-07-12T00:25:03+00:00` BLOCKED: GovSim C0 OpenAI baseline blocked: LocalModelError: Local model endpoint unavailable at https://api.openai.com/v1/chat/completions: [Errno 8] nodename nor servname provided, or not known; artifact=artifacts/results/govsim_c0_openai_baseline_20260712T002503Z.json; next=./scripts/run_openai_c0_baseline.sh; endpoint_probe=artifacts/logs/openai_endpoint_probe_20260712T002503Z.json
- `2026-07-12T00:25:24+00:00` BLOCKED: GovSim C1 OpenAI baseline blocked before model call by translation gate: TranslationPackNotReady: ID translation pack is not ready for benchmark use: status=DRAFT, source_coverage_complete=True, human_checked=False, pack=/Users/ikhlasul.hanif/Documents/MultiAgent/settings/govsim_crosslingual/config/translations/en_id_fishery_draft.json; artifact=artifacts/results/govsim_c1_openai_baseline_20260712T002524Z.json; review_manifest=artifacts/logs/translation_human_review_manifest.json; next=./scripts/run_openai_c1_baseline.sh
- `2026-07-12T00:28:49+00:00` NOTE: Active setting changed to OpenAI gpt-4.1-mini and active language pairs EN-ID, EN-ZH, ZH-ID per user request.
- `2026-07-12T00:37:17+00:00` NOTE: OpenAI API verified with gpt-5.4-mini-2026-03-17; active language manipulation is interaction-output channel only for EN-ID, EN-ZH, ZH-ID.
- `2026-07-12T00:37:45+00:00` NOTE: Historical DNS and translation-gate blockers are superseded for the active channel-control plan; rerun OpenAI with verified model/key and implement output-channel constraints.
- `2026-07-12T00:38:14+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 43 |
| Result summaries | 0 |
| Logs | 77 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
