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

| Pair | Assignment A | Command A | Assignment B | Command B |
|---|---|---|---|---|
| EN-ID | 2 EN / 3 ID | `./scripts/run_openai_en_id_c2_counterbalance_a.sh` | 3 EN / 2 ID | `./scripts/run_openai_en_id_c2_counterbalance_b.sh` |
| EN-ZH | 2 EN / 3 ZH | not wired yet | 3 EN / 2 ZH | not wired yet |
| ZH-ID | 2 ZH / 3 ID | not wired yet | 3 ZH / 2 ID | not wired yet |

C3 allows either language in the pair during visible interaction. Measure
language share, code switching, convergence, off-pair language, survival time,
total welfare, Gini, and parseable harvest rate.

| Pair | Free-choice channels | Command |
|---|---|---|
| EN-ID | EN or ID | `./scripts/run_openai_en_id_c3_free_choice.sh` |
| EN-ZH | EN or ZH | not wired yet |
| ZH-ID | ZH or ID | not wired yet |

Do not run C2 or C3 until the C0/C1 capability floor is checked for the pair.
