# goals.md - B1 GovSim Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In a cooperative resource-management game, does forced or free-choice
cross-lingual contact reduce group welfare beyond what monolingual capability
baselines predict?

## Design

- Benchmark: GovSim, fishery substrate only.
- Bucket: cooperative group.
- Agents: 5 default agents.
- Core pair: EN-ID.
- Conditions: C0 EN-mono, C1 ID-mono, C2 forced mixed, C3 free choice.
- C2 counterbalance: 2 EN / 3 ID and 3 EN / 2 ID.
- Model: Qwen3-1.7B unless G2 escalates the whole benchmark to Qwen3-8B.
- Active execution override: OpenAI benchmark calls are allowed per user on
  2026-07-12. Label those artifacts as OpenAI evidence, not Qwen evidence.

## Checklist

- [x] Verify GovSim license and record it in `licenses.md`.
- [x] Bring up GovSim locally.
- [x] Add shared local-model adapter instead of benchmark-local API calls.
- [x] Translate rules, instructions, and resource descriptions to ID.
- [ ] Human-check ID translation.
- [x] Implement transcript logging with stripped `<think>` stored separately.
- [x] Implement lang-share, code-switch, convergence, and off-pair metrics.
- [x] Smoke test one C0 episode.
- [ ] Run C0 and C1 baselines.
- [ ] Run OpenAI-backed C0/C1 baseline commands if Qwen/Modal remains unavailable.
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
escalate this benchmark as a whole to Qwen3-8B or pause it.

## Interesting Result

C2 below both monolingual baselines, or C3 language convergence correlating with
welfare distribution.
