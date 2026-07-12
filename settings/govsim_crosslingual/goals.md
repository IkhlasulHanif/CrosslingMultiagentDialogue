# goals.md - B1 GovSim Cross-Lingual Contact

**Status:** BINDING for this setting. Deviations go in `plan/deviations.md`.

## Question

In a cooperative resource-management game, does the required interaction output
language change group welfare beyond monolingual channel baselines?

## Hypotheses to Answer in the Final TeX/PDF

H1 coordination tax: forced mixed-language contact (C2) lowers survival time,
total welfare, or parseable-harvest rate below the interpolation of the two
monolingual baselines, not just below English C0.

H2 shared-norm failure: mixed groups are less likely to form a clear numeric
harvest norm during the conversation phase, or the extracted norm is less
stable across rounds.

H3 language-channel anchoring: the final or acted-on harvest norm is closer to
the first numeric proposal made in the higher-resource channel for the pair
(EN over ID; EN versus ZH should be weaker; ZH over ID in the no-English pair).

H4 free-choice convergence: in C3, the group converges to one visible dialogue
language; if the pair is ZH-ID, measure whether English appears as an off-pair
pivot language rather than assuming it cannot.

H5 outcome link: if convergence happens, welfare/parseability should be
reported separately for converged and non-converged episodes. A null result is
valid if the C2/C3 cells track the monolingual baselines.

## Design

- Benchmark: GovSim, fishery substrate only.
- Bucket: cooperative group.
- Agents: 5 default agents.
- Active language pairs: EN-ID, EN-ZH, ZH-ID.
- Core pair: EN-ID; ZH is now an active ladder language.
- Language means interaction-output channel. It is not benchmark-rule
  translation. Rules/private state may stay in English unless a later experiment
  explicitly studies rule-language effects.
- For this run, keep benchmark rules/private state in English. Manipulate only
  the visible language that agents speak to each other.
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
- [x] Run C0 and C1 baselines.
- [x] Run OpenAI-backed C0/C1 baseline commands if Qwen/Modal remains unavailable.
- [x] Add EN-ZH and ZH-ID pairwise channel-run plans.
- [x] Check G2 capability floor before C2/C3.
- [x] Run EN-ID C2 counterbalances: 2 EN / 3 ID and 3 EN / 2 ID.
- [x] Run EN-ID C3 free-choice episodes.
- [x] Add ZH ladder runs: EN-ZH and ZH-ID C0/C1, then C2/C3 if baselines pass.
- [x] Produce `reports/paper/main.tex` answering H1-H5 with artifact-backed claims.
- [x] Compile `reports/paper/main.pdf` from the TeX source.
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

## Final Report Requirements

The final artifact is `reports/paper/main.pdf`, compiled from
`reports/paper/main.tex`. It must be concise and readable: state the question,
answer each hypothesis above, show a compact condition table, and include at
least two transcript excerpts with artifact paths. Do not claim an effect from
validators, smoke tests, or one-sided counterbalances.
