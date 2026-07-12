# GovSim Pairwise Channel Run Plan

Language is the required interaction-output channel. Benchmark rules and
private state stay in English for these runs.

## Baselines

| Pair | Condition | Output channel | Command |
|---|---|---|---|
| EN-ID | C0 | EN | `./scripts/run_openai_c0_baseline.sh` |
| EN-ID | C1 | ID | `./scripts/run_openai_c1_baseline.sh` |
| EN-ZH | C0 | EN | `./scripts/run_openai_en_zh_c0_baseline.sh` |
| EN-ZH | C1 | ZH | `./scripts/run_openai_en_zh_c1_baseline.sh` |
| ZH-ID | C0 | ZH | `./scripts/run_openai_zh_id_c0_baseline.sh` |
| ZH-ID | C1 | ID | `./scripts/run_openai_zh_id_c1_baseline.sh` |

## Mixed Contact

C2 requires both counterbalances for each pair:

| Pair | Assignment A | Assignment B |
|---|---|---|
| EN-ID | 2 EN / 3 ID | 3 EN / 2 ID |
| EN-ZH | 2 EN / 3 ZH | 3 EN / 2 ZH |
| ZH-ID | 2 ZH / 3 ID | 3 ZH / 2 ID |

C3 allows either language in the pair during visible interaction. Measure
language share, code switching, convergence, off-pair language, survival time,
total welfare, Gini, and parseable harvest rate.

Do not run C2 or C3 until the C0/C1 capability floor is checked for the pair.
