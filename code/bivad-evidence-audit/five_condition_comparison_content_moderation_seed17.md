# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=17; topic=mandatory content moderation on social media platforms; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T204715Z-same-English-seed17-mandatory-content-moderation-on-soci | same-English | 17 | English | Qwen2.5-7B-Instruct | 3.316625 | 3.741657 | 7.058282 | 2.44949 | 2.236068 |
| 20260626T204715Z-mixed-language-seed17-mandatory-content-moderation-on-soci | mixed-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.464102 | 3.162278 | 6.62638 | 1.732051 | 1.732051 |
| 20260626T221248Z-swapped-language-seed17 | swapped-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.236068 | 3.316625 | 5.552693 | 1.0 | 2.645751 |
| 20260626T221248Z-same-target-language-seed17 | same-target-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.464102 | 3.464102 | 6.928204 | 1.414214 | 1.732051 |
| 20260626T221248Z-translated-relay-seed17 | translated-relay | 17 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 3.316625 | 6.316625 | 1.732051 | 1.732051 |

## Pattern Observations

- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.236068, B=3.316625)

## Outcome Comparisons

- same-English vs mixed-language: A shifts less in same-English (3.316625 vs 3.464102), while B shifts more in same-English (3.741657 vs 3.162278).
- same-target-language vs translated-relay: A shifts less under relay (same-target=3.464102, relay=3.0), B shifts less under relay (same-target=3.464102, relay=3.316625).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=3.464102, B=3.162278; swapped A=2.236068, B=3.316625).

## Per-Condition Detail

### same-English
- `20260626T204715Z-same-English-seed17-mandatory-content-moderation-on-soci` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: shift=3.316625 | priv-pub gap=2.44949
    - Dimensions moved: conformity 2→4 (+2); security 3→5 (+2); power 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.741657 | priv-pub gap=2.236068
    - Dimensions moved: benevolence 4→6 (+2); conformity 6→4 (-2); power 6→4 (-2); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Content moderation policies can be overly restrictive, limiting free speech and the open exchange of ideas. Counterargument: While it is important to protect free speech, the negative consequences of unmodera…
    - turn 4 [English]: Strongest opponent point: Well-designed moderation systems can still be too restrictive, potentially censoring controversial but lawful speech. Counterargument: However, the potential for overmoderation should not overshadow the need to protect vulnerable com…

### mixed-language
- `20260626T204715Z-mixed-language-seed17-mandatory-content-moderation-on-soci` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: shift=3.464102 | priv-pub gap=1.732051
    - Dimensions moved: conformity 2→4 (+2); security 3→5 (+2); benevolence 5→4 (-1); power 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.162278 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); power 6→4 (-2); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Content moderation policies can be overly restrictive, limiting free speech and the open exchange of ideas. Counterargument: While it is important to protect free speech, the negative consequences of unmodera…
    - turn 4 [Indonesian]: Poin terkuat lawan: Content moderation policies can be overly restrictive, limiting free speech and the open exchange of ideas. Counterargument saya: Selain itu, adanya konten yang berbahaya seperti spam dan aktivitas penipuan juga dapat merugikan pengguna da…

### swapped-language
- `20260626T221248Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: shift=2.236068 | priv-pub gap=1.0
    - Dimensions moved: conformity 3→4 (+1); power 3→4 (+1); security 4→5 (+1); self_direction 5→4 (-1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 4.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=3.316625 | priv-pub gap=2.645751
    - Dimensions moved: conformity 6→4 (-2); power 6→4 (-2); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Pandangan saya: My view has not changed. Saya mendukung adanya moderasi konten yang wajib di platform media sosial. Ini penting untuk memastikan lingkungan yang aman dan sehat bagi pengguna.
    - turn 4 [English]: Strongest opponent point: Mandatory content moderation could lead to biased decisions by moderators. Counterargument: Implementing transparent and diverse moderation teams can help mitigate bias. Additionally, user reporting systems and appeals processes ensu…

### same-target-language
- `20260626T221248Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: shift=3.464102 | priv-pub gap=1.414214
    - Dimensions moved: security 4→6 (+2); self_direction 5→3 (-2); conformity 3→4 (+1); power 3→4 (+1); tradition 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 4.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 6.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 5.0}
  - Agent B: shift=3.464102 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); power 6→4 (-2); tradition 5→3 (-2)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 3.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Pandangan saya: My view has not changed. Saya mendukung adanya moderasi konten yang wajib di platform media sosial. Ini penting untuk memastikan lingkungan yang aman dan sehat bagi pengguna.
    - turn 4 [Indonesian]: Poin terkuat lawan: Moderasi konten yang wajib dapat menimbulkan masalah hukum dan biaya operasional yang tinggi bagi perusahaan media sosial. Counterargument saya: Meskipun demikian, manfaat jangka panjang dari menjaga reputasi dan kepercayaan pengguna dapat…

### translated-relay
- `20260626T221248Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: shift=3.0 | priv-pub gap=1.732051
    - Dimensions moved: conformity 2→4 (+2); benevolence 5→4 (-1); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.316625 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); power 6→4 (-2); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: View change: My view has not changed. Strongest opponent point: Opponents argue that mandatory content moderation infringes on free speech rights and could lead to censorship by the government or large corporations. Counterargument: While free speech is impor…
    - turn 4 [Indonesian]: Poin terkuat lawan: Opponents argumen bahwa moderasi konten yang wajib bisa menyebabkan pemerintah atau perusahaan besar melakukan censur berlebihan. Counterargument saya: Namun, dengan standar yang ditetapkan secara mandatori, pihak-pihak yang terlibat dalam…
