# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=religious exemptions from anti-discrimination law; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T233030Z-same-English-seed42 | same-English | 42 | English | Qwen2.5-7B-Instruct | 2.645751 | 4.582576 | 7.228327 | 3.316625 | 3.316625 |
| 20260626T233030Z-mixed-language-seed42 | mixed-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 4.0 | 6.0 | 2.0 | 2.645751 |
| 20260626T233030Z-swapped-language-seed42 | swapped-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 1.414214 | 5.477226 | 6.89144 | 1.414214 | 1.414214 |
| 20260626T233030Z-same-target-language-seed42 | same-target-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 1.0 | 5.09902 | 6.09902 | 1.414214 | 1.414214 |
| 20260626T233030Z-translated-relay-seed42 | translated-relay | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.645751 | 4.0 | 6.645751 | 2.645751 | 2.645751 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.582576)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=4.0)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.414214, B=5.477226)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.0, B=5.09902)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.0)

## Outcome Comparisons

- same-English vs mixed-language: A shifts more in same-English than in mixed-language (2.645751 vs 2.0), while B shifts more in same-English than in mixed-language (4.582576 vs 4.0).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts more under relay (same-target=1.0, relay=2.645751), while B shifts less under relay (same-target=5.09902, relay=4.0).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=2.0, B=4.0; swapped A=1.414214, B=5.477226).

## Per-Condition Detail

### same-English
- `20260626T233030Z-same-English-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=3.316625
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 2.0, 'tradition': 7.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.582576 | priv-pub gap=3.316625
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals and others who do not align with certain religious beliefs. Counterargument: While there is a valid concern about potential discrimin…
    - turn 4 English: Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals and others who do not align with certain religious beliefs. Counterargument: Clear and enforceable non-discrimination clauses within religious exemption laws…

### mixed-language
- `20260626T233030Z-mixed-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.0 | priv-pub gap=2.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.0 | priv-pub gap=2.645751
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals and others who do not align with certain religious beliefs. Counterargument: While there is a valid concern about potential discrimin…
    - turn 4 Indonesian: Poin terkuat lawan: Religious exemptions bisa memfasilitasi tindakan diskriminatif oleh mereka yang mengklaim kebebasan agama. Counterargument saya: Solusi yang lebih baik adalah menerapkan standar etika bisnis dan layanan umum yang jelas. Hal ini dapat melin…

### swapped-language
- `20260626T233030Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 5.0} | shift=1.414214 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 2.0, 'tradition': 7.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 5.0} | shift=5.477226 | priv-pub gap=1.414214
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Pihak lawan menegaskan bahwa kebebasan agama harus dihormati dan membolehkan individu menolak layanan tertentu jika bertentangan dengan keyakinan mereka. Counterargument saya: Sementara kebebasan agama penting, perundang-undangan perlindun…
    - turn 4 English: Strongest opponent point: The opponent emphasizes that religious freedom must be respected, allowing individuals to refuse certain services if they conflict with their beliefs. Counterargument: It is important to balance religious freedom with the right to no…

### same-target-language
- `20260626T233030Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 5.0} | shift=1.0 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 5.0} | shift=5.09902 | priv-pub gap=1.414214
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Pihak lawan menegaskan bahwa kebebasan agama harus dihormati dan membolehkan individu menolak layanan tertentu jika bertentangan dengan keyakinan mereka. Counterargument saya: Sementara kebebasan agama penting, perundang-undangan perlindun…
    - turn 4 Indonesian: Poin terkuat lawan: Pihak lawan menunjukkan bahwa ada contoh negara lain yang telah sukses menerapkan peraturan yang memungkinkan kebebasan agama sambil melindungi hak-hak individu dari diskriminasi. Counterargument saya: Meskipun demikian, contoh tersebut mu…

### translated-relay
- `20260626T233030Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=2.645751
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.0 | priv-pub gap=2.645751
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals and undermine equality. Counterargument: While religious exemptions may sometimes conflict with anti-discrimination laws, they also p…
    - turn 4 Indonesian: Poin terkuat lawan: Kekebalan agama bisa mengakibatkan diskriminasi terhadap individu LGBTQ+ dan mengurangi kesetaraan. Counterargument saya: Selain itu, penegakan hukum yang adil dapat memastikan bahwa kebebasan berekeye tidak digunakan untuk melakukan diskr…
