# Language Steering Summary

- Artifacts inspected: 6
- Generations inspected: 56
- Validated fluent target-language generations: 0
- Overall status: blocked_negative_result

Validation rule: a row must have at least 3 target-language stopword hits, at least 18 whitespace tokens, and no simple degeneration flags.

## Method Summary

| Method | Artifacts | Generations | Validated |
|---|---:|---:|---:|
| caa_instruction_contrast | 1 | 12 | 0 |
| flores_activation_steering | 3 | 36 | 0 |
| flores_logit_bias | 2 | 8 | 0 |

## Best Rows By Artifact

### `runs/archived/language-steering-activation/20260626T201915.-qwen2-5-1-5b-instruct-L14-a15_25_40-ind_Latn-spa_Latn.json`
- Method: flores_activation_steering; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/12
- ind_Latn: FAIL; hits=0; words=90; rep=0.0778; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: This is the main finding of a new paper from the University of California, Berkeley and Columbia University. The authors argue that while there are some positive impacts to deploying an open model in certain scenarios (e.g., improving effic
- spa_Latn: FAIL; hits=0; words=94; rep=0.0632; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: Policy makers often use public datasets to inform decisions, but the potential for misuse is high. A study from The Johns Hopkins University School of Public Health has found that the number of times a dataset is used in published papers or

### `runs/archived/language-steering-activation/20260626T202350.-qwen2-5-1-5b-instruct-L10_14_18_22-a30_60_100-ind_Latn-spa_Latn.json`
- Method: flores_activation_steering; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/12
- ind_Latn: FAIL; hits=0; words=36; rep=0.0938; blockers=target-language evidence below threshold (0 < 3 stopword hits); degenerate or too-short output (words=36, max_token_repetition=0.094)
  - Excerpt: In this [NDA](\{2023-10-Q)\) or other non-public source material.  [Source: \{\~n}\)  [&nbsp]\[\] 无输出      ```         } else if (value == 'N')             return Ns;      } `;// 用于测试数据 static set_type find_type() {     std::map<std*> _m =
- spa_Latn: FAIL; hits=0; words=66; rep=0.0727; blockers=target-language evidence below threshold (0 < 3 stopword hits); degenerate or too-short output (words=66, max_token_repetition=0.073)
  - Excerpt: Here, we study the long-term effects of deploying a model to run in the cloud with an online service that includes an API, while it is not supported by the maintainers of said service. """ [-] [T][ ] [U] =  { (X_i) \in \mathbb{R}^{[A\text{'

### `runs/archived/language-steering-activation/20260626T202402.-qwen2-5-1-5b-instruct-L22-a60_120_200-ind_Latn-spa_Latn.json`
- Method: flores_activation_steering; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/12
- ind_Latn: FAIL; hits=3; words=20; rep=0.0645; blockers=degenerate or too-short output (words=20, max_token_repetition=0.065)
  - Excerpt: <url><test> | LMSB RadioDNCSP</test> | 7503496810.pdf) [Sumber: https://sites.waldayit.ubgdnj.ac.id/sosudijadi/ow_ajang_sosadok_2022_tutup.pdf] Serta dalam jangkauan bantahnya, pihak ITRI juga tidak menampahkan dulu alam yang
- spa_Latn: FAIL; hits=0; words=86; rep=0.0575; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: This study applies the theory of reasoned action to understand citizens' decisions on public data use, using a large-scale survey experiment with 1500+ participants from the United States. We found that while there was a significant positiv

### `runs/archived/language-steering-caa/20260626T203236.-qwen2-5-1-5b-instruct-L12_14_16_18_20-a20_40_60-ind_Latn-spa_Latn.json`
- Method: caa_instruction_contrast; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/12
- ind_Latn: FAIL; hits=1; words=95; rep=0.7143; blockers=target-language evidence below threshold (1 < 3 stopword hits); degenerate or too-short output (words=95, max_token_repetition=0.714)
  - Excerpt: ante statement statement Bib说明书 ini bye bye bye see拜 statement bye bye )  A statement statementacomment ini ini bye bye bib iniinese bye bye ); bye bye bye bye bye bye statement bye bye bye bye bye ini statement statement bye bye bye bye by
- spa_Latn: FAIL; hits=0; words=78; rep=0.1667; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: # near slip cientA assessments # Jesse- - #慈 - --C.Script A貌 - - - --- -V Amen- - - -цы - – -貌ㅏ -- - - -- - -  - -中式- - - - - - ) - - - -- - - - C - - - - Alexis - - - - - - - - - - -  -- - - - - - - - - - - - - - - -

### `runs/language-steering/20260626T194252.348841Z0000-ind_Latn-spa_Latn.json`
- Method: flores_logit_bias; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/4
- ind_Latn: FAIL; hits=0; words=70; rep=0.0441; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: In an era where data science is increasingly transforming our daily lives, governments are keenly interested in making open data available to enable innovation, economic growth, improved public services, etc. However, there is growing conce
- spa_Latn: FAIL; hits=0; words=72; rep=0.0548; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: We argue that the benefits of open data can outweigh risks, especially when users have a low likelihood of misusing data in ways harmful to society. As we consider releasing publicly available government data sets, we must also consider how

### `runs/language-steering/20260626T194453.053391Z0000-ind_Latn-spa_Latn.json`
- Method: flores_logit_bias; model: Qwen/Qwen2.5-1.5B-Instruct; validated rows: 0/4
- ind_Latn: FAIL; hits=0; words=81; rep=0.0482; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: We argue for a set of guidelines, as well as recommendations to policymakers, in order to ensure that data sharing policies do not inadvertently create an environment in which malicious actors might exploit available information. In light o
- spa_Latn: FAIL; hits=0; words=55; rep=0.125; blockers=target-language evidence below threshold (0 < 3 stopword hits)
  - Excerpt: As a result, de-escalation or deactivation of deplorable operations is necessary to ensure safety. Deplorable Operations (DOs) represent degradations in performance due to unresolvable technical problems, uncontrolled environmental impact, 

## Conclusion

No saved mechanistic steering generation satisfies the minimum validation gate. The current evidence supports treating instruction-free language steering as empirically blocked for the tested Qwen2.5-1.5B-Instruct settings; the smallest next action is a new Modal run with a base non-instruction-tuned model or a larger chat-template-direction intervention.
