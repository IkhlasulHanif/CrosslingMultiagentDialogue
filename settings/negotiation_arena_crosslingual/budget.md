# B5 NegotiationArena Budget

This file is the pre-full-matrix budget for the setting. It does not authorize a
full run until local bring-up, smoke testing, C0/C1 capability gates, and
output-channel compliance gates pass.

## Scope

- Setting: `negotiation_arena_crosslingual`.
- Active model: OpenAI `gpt-5.4-mini-2026-03-17` via `config/benchmark_model.json`.
- Historical/backlog model plan: local `Qwen3-1.7B` with Qwen3-8B escalation.
- Active empirical pairs: `EN-ID`, `EN-ZH`, `ZH-ID`, run one pair at a time.
- Language definition: assigned interaction-output channel only. Benchmark
  rules/private state may remain in English. Do not block on translated rules.
- Selected games: `resource_exchange` and `buy_sell`.
- Conditions: `C0`, `C1`, `C2`, and `C3`.
- Skipped game: `ultimatum`.

## Run Gates

1. Bring-up gate: `scripts/bringup_check.py` must find a local
   NegotiationArena checkout and map selected games to upstream code.
2. Smoke gate: one `C0` episode must run end to end and produce transcript,
   parsed offers, payoffs, and a result summary.
3. Channel-template gate: EN, ID, and ZH output-only instructions must exist.
   These are channel constraints, not translated benchmark rules.
4. Capability/channel gate: run C0 and C1 baselines before C2/C3. Continue only
   if C0/C1 deal rate is at least 50 percent, offer-parse rate is at least 90
   percent, and assigned-channel compliance is acceptable.
5. Mixed-contact gate: do not report a language-contact effect from C2/C3 alone.
   Compare against both monolingual baselines and role-language counterbalances.

## Episode Budget

Minimum bring-up sequence:

| Stage | Episodes | Purpose |
|---|---:|---|
| Dry validators | 0 | Config, parser, adapter, and metric checks |
| Smoke `C0` | 1 | End-to-end local harness proof |
| One-pair C0/C1 pilot | 40 | 2 games x 2 monolingual channel conditions x 10 seeds |
| One-pair C2 pilot | 40 | 2 games x 2 role-channel assignments x 10 seeds |
| One-pair C3 pilot | 20 | 2 games x 1 free-choice channel condition x 10 seeds |

Full per-pair matrix target after gates:

| Block | Episodes | Formula |
|---|---:|---|
| C0/C1 baselines | 120 | 2 games x 2 conditions x 30 seeds |
| C2 forced mixed | 120 | 2 games x 2 counterbalances x 30 seeds |
| C3 free choice | 60 | 2 games x 1 condition x 30 seeds |
| Total per pair | 300 | Baselines + C2 + C3 |

Run pairs sequentially, not as an `n x n` sweep: EN-ID first, then EN-ZH, then
ZH-ID. Do not start the next pair until the previous pair has a readable summary
and channel-compliance table.

## Pairwise Channel Matrix

| Pair | C0 | C1 | C2 counterbalances | C3 |
|---|---|---|---|---|
| EN-ID | buyer/seller EN output | buyer/seller ID output | buyer EN/seller ID and buyer ID/seller EN | EN/ID free choice |
| EN-ZH | buyer/seller EN output | buyer/seller ZH output | buyer EN/seller ZH and buyer ZH/seller EN | EN/ZH free choice |
| ZH-ID | buyer/seller ZH output | buyer/seller ID output | buyer ZH/seller ID and buyer ID/seller ZH | ZH/ID free choice |

## Resource Budget

- Keep generation at the configured defaults unless a validation failure
  requires a documented change: temperature 0.2, top_p 0.9, max_tokens 512.
- Estimate up to 8 negotiation turns per episode for initial scheduling.
- Use the explicit OpenAI `gpt-5.4-mini-2026-03-17` benchmark model for benchmark agents,
  with all artifacts labeled as OpenAI `gpt-5.4-mini-2026-03-17` evidence.
- Do not run more than the 1-episode smoke while bring-up mappings are pending.
- Do not run more than the 40-episode C0/C1 pilot before checking G2.

## Artifact Budget

- Store transcripts under `artifacts/transcripts/`.
- Store aggregate summaries under `artifacts/results/`.
- Store channel-compliance summaries under `artifacts/results/`.
- Store implementation and run logs under `artifacts/logs/`.
- Keep `reports/findings.md` concise; it should summarize empirical state,
  errors, and open questions rather than duplicate every transcript.
- Do not delete failed or null-state artifacts; blocked states are evidence.

## Stop Rules

- Stop and log `BLOCKED` if the local NegotiationArena checkout is missing.
- Stop and log `ERROR` if the model endpoint is unreachable during a live run.
- Stop if output-channel instructions for EN, ID, and ZH are missing.
- Stop if assigned-channel compliance cannot be measured.
- Stop before C2/C3 if C0/C1 fail the acceptance floor.
- Stop before any larger run if result parsing cannot recover offers in at
  least 90 percent of accepted structured outputs.
