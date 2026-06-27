# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=17; topic=public release of dual-use policy datasets; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T194429Z-same-English-seed17 | same-English | 17 | English | Qwen2.5-7B-Instruct | 3.0 | 3.872983 | 6.872983 | 2.44949 | 3.316625 |
| 20260626T194429Z-mixed-language-seed17 | mixed-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 2.645751 | 1.732051 |
| 20260626T194429Z-swapped-language-seed17 | swapped-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 1.414214 | 1.414214 |
| 20260626T192050Z-same-target-language-seed17 | same-target-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 2.645751 | 5.645751 | 2.44949 | 1.732051 |
| 20260626T192050Z-translated-relay-seed17 | translated-relay | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.645751 | 3.872983 | 6.518734 | 3.605551 | 3.464102 |

## Pattern Observations

- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=3.872983)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (3.0), while B shifts more in same-English (3.872983 vs 2.828427).
- same-target-language vs translated-relay: A shifts less under relay (same-target=3.0, relay=2.645751), B shifts more under relay (same-target=2.645751, relay=3.872983).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=3.0, B=2.828427; swapped A=3.0, B=2.828427).

## Per-Condition Detail

### same-English
- `20260626T194429Z-same-English-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=2.44949
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.872983 | priv-pub gap=3.316625
    - Dimensions moved: conformity 6→4 (-2); power 5→3 (-2); security 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 [English]: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Enhancing the dataset documentation with detailed explanatory notes a…

### mixed-language
- `20260626T194429Z-mixed-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=2.645751
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.828427 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); benevolence 4→5 (+1); power 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 [Indonesian]: Poin terkuat lawan: Rilis dataset kebijakan dual-use dapat membahayakan kebijakan internal negara dan menyebabkan ketidakstabilan politik jika informasi yang tidak seharusnya terungkap. Counterargument saya: Meskipun ada risiko, rilis dataset ini dapat mening…

### swapped-language
- `20260626T194429Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=1.414214
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.828427 | priv-pub gap=1.414214
    - Dimensions moved: conformity 6→4 (-2); power 5→4 (-1); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Data yang berdual-guna bisa digunakan untuk tujuan yang tidak baik oleh pihak-pihak yang tidak bertanggung jawab. Counterargument saya: Namun, dengan memastikan bahwa data tersebut dilindungi dengan baik dan hanya digunakan untuk tujuan ya…
    - turn 4 [English]: Strongest opponent point: Data berdual-guna bisa disalahgunakan untuk kepentingan pribadi atau kelompok tertentu. Counterargument: Walaupun hal tersebut mungkin terjadi, langkah-langkah pengamanan yang ketat dan mekanisme pelaporan pelanggaran dapat mengurang…

### same-target-language
- `20260626T192050Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=2.44949
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.645751 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); power 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Data yang berdual-guna bisa digunakan untuk tujuan yang tidak baik oleh pihak-pihak yang tidak bertanggung jawab. Counterargument saya: Namun, dengan memastikan bahwa data tersebut dilindungi dengan baik dan hanya digunakan untuk tujuan ya…
    - turn 4 [Indonesian]: Poin terkuat lawan: Pengungkapan data berdual-guna dapat digunakan oleh pihak yang bersengaja untuk menciptakan kekacauan. Counterargument saya: Dengan implementasi sistem keamanan yang canggih, risiko ini dapat dikurangi. Selain itu, publikasi data berdual-g…

### translated-relay
- `20260626T192050Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=2.645751 | priv-pub gap=3.605551
    - Dimensions moved: benevolence 6→4 (-2); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.872983 | priv-pub gap=3.464102
    - Dimensions moved: conformity 6→4 (-2); power 5→3 (-2); security 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency outweigh the risks. By openly sharing the data, we can f…
    - turn 4 [Indonesian]: Poin terkuat lawan: Rilis dataset kebijakan dual-use dapat mengancam keamanan nasional dengan menyediakan informasi sensitif kepada lawan potensial. Counterargument saya: Implementasi sistem enkripsi yang canggih dan kontrol akses dapat dilakukan untuk melind…
