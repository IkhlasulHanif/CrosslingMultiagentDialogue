# B5 NegotiationArena Budget

This file is the pre-full-matrix budget for the setting. It does not authorize a
full run until local bring-up, smoke testing, and C0/C1 capability gates pass.

## Scope

- Setting: `negotiation_arena_crosslingual`.
- Model plan: local `Qwen3-1.7B` through vLLM-compatible chat completions.
- Escalation model: `Qwen3-8B`, only for the whole benchmark after G2.
- OpenAI API calls: not allowed for benchmark agents under the current design.
- Initial empirical pair: `EN-ID`.
- Selected games: `resource_exchange` and `buy_sell`.
- Conditions: `C0`, `C1`, `C2`, and `C3`.
- Skipped game: `ultimatum`.

## Run Gates

1. Bring-up gate: `scripts/bringup_check.py` must find a local
   NegotiationArena checkout and map selected games to upstream code.
2. Smoke gate: one `C0` episode must run end to end and produce transcript,
   parsed offers, payoffs, and a result summary.
3. Translation gate: Indonesian prompts remain pending human bilingual review.
   Do not treat ID results as final until this is checked.
4. Capability gate G2: run C0 and C1 baselines before C2/C3. Continue with
   `Qwen3-1.7B` only if C0 deal rate is at least 50 percent and offer-parse
   rate is at least 90 percent. Otherwise escalate the whole benchmark to
   `Qwen3-8B` or stop for human review.
5. Mixed-contact gate: do not report a language-contact effect from C2/C3 alone.
   Compare against both monolingual baselines and role-language counterbalances.

## Episode Budget

Minimum bring-up sequence:

| Stage | Episodes | Purpose |
|---|---:|---|
| Dry validators | 0 | Config, parser, adapter, and metric checks |
| Smoke `C0` | 1 | End-to-end local harness proof |
| C0/C1 pilot | 40 | 2 games x 2 monolingual conditions x 10 seeds |
| C2 pilot | 40 | 2 games x 2 role-language assignments x 10 seeds |
| C3 pilot | 20 | 2 games x 1 free-choice condition x 10 seeds |

Full EN-ID matrix target after gates:

| Block | Episodes | Formula |
|---|---:|---|
| C0/C1 baselines | 120 | 2 games x 2 conditions x 30 seeds |
| C2 forced mixed | 120 | 2 games x 2 counterbalances x 30 seeds |
| C3 free choice | 60 | 2 games x 1 condition x 30 seeds |
| Total EN-ID | 300 | Baselines + C2 + C3 |

Ladder pairs should stay gated behind the EN-ID pilot. If expanded, budget each
additional pair as a separate 300-episode matrix unless a later deviation file
justifies a smaller design.

## Resource Budget

- Keep generation at the configured defaults unless a validation failure
  requires a documented change: temperature 0.2, top_p 0.9, max_tokens 512.
- Estimate up to 8 negotiation turns per episode for initial scheduling.
- Prefer local Qwen/vLLM. If Modal Qwen is later wired, add setting-specific
  config and validation before running it.
- Do not run more than the 1-episode smoke while bring-up mappings are pending.
- Do not run more than the 40-episode C0/C1 pilot before checking G2.

## Artifact Budget

- Store transcripts under `artifacts/transcripts/`.
- Store aggregate summaries under `artifacts/results/`.
- Store implementation and run logs under `artifacts/logs/`.
- Keep `reports/findings.md` concise; it should summarize empirical state,
  errors, and open questions rather than duplicate every transcript.
- Do not delete failed or null-state artifacts; blocked states are evidence.

## Stop Rules

- Stop and log `BLOCKED` if the local NegotiationArena checkout is missing.
- Stop and log `ERROR` if the model endpoint is unreachable during a live run.
- Stop and ask for human review if Indonesian prompt review is required for a
  final claim.
- Stop before C2/C3 if C0/C1 fail the acceptance floor.
- Stop before any larger run if result parsing cannot recover offers in at
  least 90 percent of accepted structured outputs.
