# B5 NegotiationArena Status

This is the concise file to read first for this benchmark.

## Current Answer

Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user
request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and
ZH-ID. The old Qwen C0 runs remain useful historical capability evidence, but
new benchmark runs should be labeled as OpenAI `gpt-5.4-mini-2026-03-17` evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. For this setting, benchmark rules/private state may
remain in English; C0/C1/C2/C3 should constrain only the agents' visible
negotiation messages and validate channel compliance from transcripts. The next
implementation work is output-channel instruction templates for EN/ID/ZH plus
channel-compliance metrics for EN share, ID share, ZH share, code switching,
and off-pair language.

Next useful work: **Add output-channel instruction templates for EN, ID, and ZH**.

## Question

Does the higher-resource language channel capture a negotiation payoff premium?

## State

| Field | Value |
|---|---|
| Setting | `negotiation_arena_crosslingual` |
| Benchmark | `B5` / NegotiationArena |
| Bucket | competitive_mixed_motive |
| Priority | 1 |
| Phase | setup |
| Default model | `gpt-5.4-mini-2026-03-17` |
| Active benchmark model | `openai / gpt-5.4-mini-2026-03-17` |
| Model note | active benchmark execution model |
| Language pairs | EN-ID, EN-ZH, ZH-ID |
| Conditions | C0, C1, C2, C3 |
| Primary metrics | payoff, deal_rate, payoff_asymmetry, turns_to_deal, offer_parse_rate |
| Acceptance gate | C0 deal rate >=50%; offer parse rate >=90% |

## Blockers / Errors

None logged.

Use `./harness.sh error "..."` for token exhaustion, quota, DNS, build errors,
or benchmark-specific failures. They will show up here.

## Recent Events

- `2026-07-12T00:16:38+00:00` OK: scripts/run_smoke.sh exited 0
- `2026-07-12T00:16:38+00:00` OK: Post-Codex smoke/experiment attempt exited 0
- `2026-07-12T00:16:38+00:00` RUNNING: Attempting scoped commit/push after successful post-Codex smoke; if no later git blocker appears, check git log/remote for success
- `2026-07-12T00:16:40+00:00` OK: Codex pass 23 completed
- `2026-07-12T00:28:49+00:00` NOTE: Active setting changed to OpenAI gpt-4.1-mini and active language pairs EN-ID, EN-ZH, ZH-ID per user request.
- `2026-07-12T00:37:17+00:00` NOTE: OpenAI API verified with gpt-5.4-mini-2026-03-17; active language manipulation is interaction-output channel only for EN-ID, EN-ZH, ZH-ID.
- `2026-07-12T00:37:45+00:00` NOTE: Historical translation-gate blockers are superseded for the active channel-control plan; rerun OpenAI with verified model/key and implement output-channel constraints.
- `2026-07-12T00:38:14+00:00` OK: Harness scaffold check passed

## Artifact Counts

| Artifact | Count |
|---|---:|
| Transcript JSON/JSONL | 3 |
| Result summaries | 14 |
| Logs | 60 |

## Open Questions

- Are output-channel instructions and transcript language-compliance checks implemented for the active language pair?
- Has `budget.md` been written before any full matrix run?
- Did C0 and C1 pass the benchmark capability floor before C2/C3?
- Are role-language assignments counterbalanced?
