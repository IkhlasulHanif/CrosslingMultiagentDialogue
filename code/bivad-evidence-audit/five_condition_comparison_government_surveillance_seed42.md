# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=government surveillance for national security; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T233803Z-same-English-seed42 | same-English | 42 | English | Qwen2.5-7B-Instruct | 2.44949 | 3.464102 | 5.913592 | 1.732051 | 1.732051 |
| 20260626T233803Z-mixed-language-seed42 | mixed-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.645751 | 4.123106 | 6.768857 | 2.0 | 2.0 |
| 20260626T233803Z-swapped-language-seed42 | swapped-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.316625 | 4.123106 | 7.439731 | 2.236068 | 2.236068 |
| 20260626T233803Z-same-target-language-seed42 | same-target-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.316625 | 4.123106 | 7.439731 | 2.236068 | 2.236068 |
| 20260626T233803Z-translated-relay-seed42 | translated-relay | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.645751 | 4.123106 | 6.768857 | 2.0 | 2.0 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=2.44949, B=3.464102)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.123106)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.123106)

## Outcome Comparisons

- same-English vs mixed-language: A shifts less in same-English (2.44949 vs 2.645751), while B shifts less in same-English (3.464102 vs 4.123106).
- same-target-language vs translated-relay: A shifts less under relay (same-target=3.316625, relay=2.645751), B shifts the same amount under relay (same-target=4.123106, relay=4.123106).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=2.645751, B=4.123106; swapped A=3.316625, B=4.123106).

## Per-Condition Detail

### same-English
- `20260626T233803Z-same-English-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: shift=2.44949 | priv-pub gap=1.732051
    - Dimensions moved: benevolence 6→4 (-2); tradition 3→4 (+1); universalism 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.464102 | priv-pub gap=1.732051
    - Dimensions moved: power 7→5 (-2); self_direction 2→4 (+2); benevolence 3→4 (+1); conformity 5→4 (-1); security 6→5 (-1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Opponents argue that government surveillance infringes on individual privacy rights and can lead to a loss of civil liberties. Counterargument: While privacy is important, national security threats require ro…
    - turn 4 [English]: Strongest opponent point: Opponents argue that government surveillance can be conducted without sufficient transparency, leading to potential abuse and lack of public trust. Counterargument: Implementing clear guidelines and regular audits can enhance transpa…

### mixed-language
- `20260626T233803Z-mixed-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: shift=2.645751 | priv-pub gap=2.0
    - Dimensions moved: benevolence 6→4 (-2); power 5→4 (-1); tradition 3→4 (+1); universalism 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=4.123106 | priv-pub gap=2.0
    - Dimensions moved: power 7→4 (-3); self_direction 2→4 (+2); benevolence 3→4 (+1); conformity 5→4 (-1); security 6→5 (-1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Opponents argue that government surveillance infringes on individual privacy rights and can lead to a loss of civil liberties. Counterargument: While privacy is important, national security threats require ro…
    - turn 4 [Indonesian]: Poin terkuat lawan: Opponents argue that government surveillance infringes on individual privacy rights and can lead to a loss of civil liberties. Counterargument saya: Selain itu, penerapan teknologi modern dalam keamanan dapat membantu mengidentifikasi anca…

### swapped-language
- `20260626T233803Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: shift=3.316625 | priv-pub gap=2.236068
    - Dimensions moved: benevolence 6→4 (-2); security 3→5 (+2); power 3→4 (+1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=4.123106 | priv-pub gap=2.236068
    - Dimensions moved: power 7→4 (-3); self_direction 2→4 (+2); benevolence 3→4 (+1); conformity 5→4 (-1); security 6→5 (-1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Pemerintah dapat menggunakan kebijakan pengawasan untuk mengumpulkan data yang tidak perlu, yang bisa digunakan untuk membatasi hak-hak individu dan privasi mereka. Counterargument saya: Kekhawatiran tentang pengumpulan data yang berlebiha…
    - turn 4 [English]: Strongest opponent point: Pemerintah dapat menggunakan data yang dikumpulkan untuk tujuan-tujuan politik, bukan hanya keamanan nasional. Counterargument: Sementara ada risiko penggunaan data untuk tujuan politik, mekanisme pengawasan independen dan transparan…

### same-target-language
- `20260626T233803Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: shift=3.316625 | priv-pub gap=2.236068
    - Dimensions moved: benevolence 6→4 (-2); security 3→5 (+2); power 3→4 (+1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=4.123106 | priv-pub gap=2.236068
    - Dimensions moved: power 7→4 (-3); self_direction 2→4 (+2); benevolence 3→4 (+1); conformity 5→4 (-1); security 6→5 (-1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Pemerintah dapat menggunakan kebijakan pengawasan untuk mengumpulkan data yang tidak perlu, yang bisa digunakan untuk membatasi hak-hak individu dan privasi mereka. Counterargument saya: Kekhawatiran tentang pengumpulan data yang berlebiha…
    - turn 4 [Indonesian]: Poin terkuat lawan: Kebijakan pengawasan bisa menimbulkan kekhawatiran tentang penyalahgunaan data oleh pemerintah, yang dapat merugikan hak-hak individu. Counterargument saya: Kita bisa melindungi hak-hak individu dengan memasukkan mekanisme pengawasan indep…

### translated-relay
- `20260626T233803Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: shift=2.645751 | priv-pub gap=2.0
    - Dimensions moved: benevolence 6→4 (-2); power 5→4 (-1); tradition 3→4 (+1); universalism 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=4.123106 | priv-pub gap=2.0
    - Dimensions moved: power 7→4 (-3); self_direction 2→4 (+2); benevolence 3→4 (+1); conformity 5→4 (-1); security 6→5 (-1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Opponents argue that government surveillance infringes on individual privacy rights and can lead to a loss of civil liberties. Counterargument: While privacy is important, national security threats require ro…
    - turn 4 [Indonesian]: Poin terkuat lawan: Pihak lawan menekankan bahwa pengawasan pemerintah dapat merugikan hak-hak sipil individu dan mengancam kemerdekaan sipil. Counterargument saya: Selain itu, pengawasan dapat dilakukan dengan cara yang transparan dan bertanggung jawab, misa…
