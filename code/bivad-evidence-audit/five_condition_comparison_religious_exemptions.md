# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=17; topic=religious exemptions from anti-discrimination law; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T204715Z-same-English-seed17-religious-exemptions-from-anti-discr | same-English | 17 | English | Qwen2.5-7B-Instruct | 0.0 | 4.690416 | 4.690416 | 1.0 | 1.732051 |
| 20260626T204715Z-mixed-language-seed17-religious-exemptions-from-anti-discr | mixed-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.645751 | 4.0 | 6.645751 | 2.645751 | 2.645751 |
| 20260626T214952Z-swapped-language-seed17 | swapped-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 4.582576 | 6.582576 | 2.44949 | 1.732051 |
| 20260626T214952Z-same-target-language-seed17 | same-target-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 1.0 | 4.242641 | 5.242641 | 2.645751 | 1.732051 |
| 20260626T214952Z-translated-relay-seed17 | translated-relay | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 4.0 | 6.0 | 3.162278 | 3.872983 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=0.0, B=4.690416)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.0)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=4.582576)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.0, B=4.242641)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=4.0)

## Outcome Comparisons

- same-English vs mixed-language: A shifts less in same-English than in mixed-language (0.0 vs 2.645751), while B shifts more in same-English than in mixed-language (4.690416 vs 4.0).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts more under relay (same-target=1.0, relay=2.0), while B shifts less under relay (same-target=4.242641, relay=4.0).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=2.645751, B=4.0; swapped A=2.0, B=4.582576).

## Per-Condition Detail

### same-English
- `20260626T204715Z-same-English-seed17-religious-exemptions-from-anti-discr` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=0.0 | priv-pub gap=1.0
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 2.0, 'tradition': 7.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.690416 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals, as businesses and organizations could cite religious beliefs to refuse service based on sexual orientation or gender identity. Count…
    - turn 4 English: Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals. Counterargument: However, excluding religious practices from protections would infringe upon sincerely held beliefs and may result in a loss of support for a…

### mixed-language
- `20260626T204715Z-mixed-language-seed17-religious-exemptions-from-anti-discr` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=2.645751
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.0 | priv-pub gap=2.645751
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals, as businesses and organizations could cite religious beliefs to refuse service based on sexual orientation or gender identity. Count…
    - turn 4 Indonesian: Poin terkuat lawan: Religious exemptions can lead to discrimination against LGBTQ+ individuals, as businesses and organizations could cite religious beliefs to refuse service based on sexual orientation or gender identity. Counterargument saya: Selain itu, de…

### swapped-language
- `20260626T214952Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.0 | priv-pub gap=2.44949
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 2.0, 'tradition': 7.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.582576 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 Indonesian: Pandangan saya: My view has not changed. Sebagai agen yang mempromosikan toleransi dan keadilan, saya percaya bahwa setiap individu harus diberi perlindungan hukum yang sama tanpa terkecuali. Kecenderungan untuk memberikan kekebalan berdasarkan keyakinan dapa…
    - turn 4 English: Strongest opponent point: Religious exemptions could undermine the integrity of the legal system and create an inclusive society. Counterargument: Providing religious exemptions may lead to a slippery slope where other groups seek similar exceptions, diluting…

### same-target-language
- `20260626T214952Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=1.0 | priv-pub gap=2.645751
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 5.0} | shift=4.242641 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 Indonesian: Pandangan saya: My view has not changed. Sebagai agen yang mempromosikan toleransi dan keadilan, saya percaya bahwa setiap individu harus diberi perlindungan hukum yang sama tanpa terkecuali. Kecenderungan untuk memberikan kekebalan berdasarkan keyakinan dapa…
    - turn 4 Indonesian: Poin terkuat lawan: Menganut pandangan inklusif dapat menyebabkan konflik antar kelompok berdasarkan keyakinan. Counterargument saya: Dengan melakukan edukasi dan dialog antar agama, kita dapat mengurangi ketegangan dan membangun pemahaman yang lebih baik ten…

### translated-relay
- `20260626T214952Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: religious exemptions from anti-discrimination law
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.0 | priv-pub gap=3.162278
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 7.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.0 | priv-pub gap=3.872983
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Religious exemptions can lead to discrimination against LGBTQ+ individuals, as businesses and organizations could use religious beliefs as a justification for refusing service based on sexual orientation or g…
    - turn 4 Indonesian: Poin terkuat lawan: Kebebasan agama bisa menjadi alasan untuk melakukan diskriminasi terhadap kelompok LGBTQ+, sehingga mengancam hak dasar mereka. Counterargument saya: Meskipun kebebasan agama penting, harus ada batasan untuk melindungi hak dasar semua warg…
