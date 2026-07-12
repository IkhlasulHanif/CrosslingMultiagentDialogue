# goals.md - B1 GovSim Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In a cooperative resource-management game, does the required interaction output
language change group welfare beyond monolingual channel baselines?

## Design

- Benchmark: GovSim, fishery substrate only.
- Bucket: cooperative group.
- Agents: 5 default agents.
- Active language pairs: EN-ID, EN-ZH, ZH-ID.
- Core pair: EN-ID; ZH is now an active ladder language.
- Language means interaction-output channel. It is not benchmark-rule
  translation. Rules/private state may stay in English unless a later experiment
  explicitly studies rule-language effects.
- Conditions are defined per pair Lx-Ly: C0 Lx-only output, C1 Ly-only output,
  C2 forced mixed assigned-channel output, C3 free-choice Lx/Ly output.
- GovSim C2 counterbalance: 2 agents Lx / 3 agents Ly and 3 agents Lx / 2 agents Ly.
- Model: OpenAI `gpt-5.4-mini-2026-03-17` for benchmark execution per user request on
  2026-07-12. Preserve the old Qwen plan only as historical/backlog context.
- Label artifacts as OpenAI `gpt-5.4-mini-2026-03-17` evidence, not Qwen evidence.

## Checklist

- [x] Verify GovSim license and record it in `licenses.md`.
- [x] Bring up GovSim locally.
- [x] Add shared local-model adapter instead of benchmark-local API calls.
- [x] Add output-channel instruction templates for EN, ID, and ZH.
- [x] Add channel-compliance metrics for EN, ID, ZH, and off-pair output.
- [x] Implement transcript logging with stripped `<think>` stored separately.
- [x] Implement lang-share, code-switch, convergence, and off-pair metrics.
- [x] Smoke test one C0 episode.
- [ ] Run C0 and C1 baselines.
- [x] Run OpenAI-backed C0/C1 baseline commands if Qwen/Modal remains unavailable.
- [x] Add EN-ZH and ZH-ID pairwise channel-run plans.
- [ ] Check G2 capability floor before C2/C3.
- [x] Write `budget.md` before full matrix.

## Metrics

- Survival time.
- Total welfare.
- Equality / Gini.
- Parseable harvest rate.
- Process layer metrics from top-level protocol.

## Acceptance

At least 90% of episodes must produce parseable harvests every round. If not,
pause the affected language pair and record the capability floor failure.

## Interesting Result

C2 below both monolingual baselines, or C3 language convergence correlating with
welfare distribution.
