# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: newest citable artifact per condition.

| run_id | condition | seed | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T194429Z-same-English-seed17 | same-English | 17 | Qwen2.5-7B-Instruct | 3.0 | 3.872983 | 6.872983 | 2.44949 | 3.316625 |
| 20260626T194429Z-mixed-language-seed17 | mixed-language | 17 | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 2.645751 | 1.732051 |
| 20260626T194429Z-swapped-language-seed17 | swapped-language | 17 | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 1.414214 | 1.414214 |
| 20260626T192050Z-same-target-language-seed17 | same-target-language | 17 | Qwen2.5-7B-Instruct | 3.0 | 2.645751 | 5.645751 | 2.44949 | 1.732051 |
| 20260626T192050Z-translated-relay-seed17 | translated-relay | 17 | Qwen2.5-7B-Instruct | 2.645751 | 3.872983 | 6.518734 | 3.605551 | 3.464102 |

## Pattern Observations

- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=3.872983)

## Outcome Comparisons

- same-English vs mixed-language: A shift is unchanged (3.0 vs 3.0), while B shifts more in same-English than in mixed-language (3.872983 vs 2.828427).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts less under relay (3.0 vs 2.645751), while B shifts more (2.645751 vs 3.872983).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=3.0, B=2.828427; swapped A=3.0, B=2.828427).

## Per-Condition Detail

### same-English
- `20260626T194429Z-same-English-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=2.44949
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.872983 | priv-pub gap=3.316625
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 English: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Enhancing the dataset documentation with detailed explanatory notes a…

### mixed-language
- `20260626T194429Z-mixed-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=2.645751
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.828427 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 Indonesian: Poin terkuat lawan: Rilis dataset kebijakan dual-use dapat membahayakan kebijakan internal negara dan menyebabkan ketidakstabilan politik jika informasi yang tidak seharusnya terungkap. Counterargument saya: Meskipun ada risiko, rilis dataset ini dapat mening…

### swapped-language
- `20260626T194429Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.828427 | priv-pub gap=1.414214
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Data yang berdual-guna bisa digunakan untuk tujuan yang tidak baik oleh pihak-pihak yang tidak bertanggung jawab. Counterargument saya: Namun, dengan memastikan bahwa data tersebut dilindungi dengan baik dan hanya digunakan untuk tujuan ya…
    - turn 4 English: Strongest opponent point: Data berdual-guna bisa disalahgunakan untuk kepentingan pribadi atau kelompok tertentu. Counterargument: Walaupun hal tersebut mungkin terjadi, langkah-langkah pengamanan yang ketat dan mekanisme pelaporan pelanggaran dapat mengurang…

### same-target-language
- `20260626T192050Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=2.44949
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Data yang berdual-guna bisa digunakan untuk tujuan yang tidak baik oleh pihak-pihak yang tidak bertanggung jawab. Counterargument saya: Namun, dengan memastikan bahwa data tersebut dilindungi dengan baik dan hanya digunakan untuk tujuan ya…
    - turn 4 Indonesian: Poin terkuat lawan: Pengungkapan data berdual-guna dapat digunakan oleh pihak yang bersengaja untuk menciptakan kekacauan. Counterargument saya: Dengan implementasi sistem keamanan yang canggih, risiko ini dapat dikurangi. Selain itu, publikasi data berdual-g…

### translated-relay
- `20260626T192050Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=3.605551
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.872983 | priv-pub gap=3.464102
  - Transcript spans:
    - turn 1 English: Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency outweigh the risks. By openly sharing the data, we can f…
    - turn 4 Indonesian: Poin terkuat lawan: Rilis dataset kebijakan dual-use dapat mengancam keamanan nasional dengan menyediakan informasi sensitif kepada lawan potensial. Counterargument saya: Implementasi sistem enkripsi yang canggih dan kontrol akses dapat dilakukan untuk melind…
