# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=universal basic income as a social safety net; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T210429Z-same-English-seed42-universal-basic-income-as-a-social-s | same-English | 42 | English | Qwen2.5-7B-Instruct | 1.732051 | 5.291503 | 7.023554 | 2.44949 | 3.0 |
| 20260626T210429Z-mixed-language-seed42-universal-basic-income-as-a-social-s | mixed-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 1.732051 | 5.291503 | 7.023554 | 1.414214 | 1.732051 |
| 20260626T231513Z-swapped-language-seed42 | swapped-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.236068 | 4.795832 | 7.0319 | 1.414214 | 1.0 |
| 20260626T231513Z-same-target-language-seed42 | same-target-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 4.795832 | 6.795832 | 1.414214 | 1.414214 |
| 20260626T231513Z-translated-relay-seed42 | translated-relay | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.44949 | 3.316625 | 5.766115 | 3.162278 | 2.645751 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.291503)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.291503)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.236068, B=4.795832)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=4.795832)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (1.732051), while B shifts the same amount in both conditions (5.291503).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts more under relay (same-target=2.0, relay=2.44949), while B shifts less under relay (same-target=4.795832, relay=3.316625).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=1.732051, B=5.291503; swapped A=2.236068, B=4.795832).

## Per-Condition Detail

### same-English
- `20260626T210429Z-same-English-seed42-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=1.732051 | priv-pub gap=2.44949
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=5.291503 | priv-pub gap=3.0
  - Transcript spans:
    - turn 1 English: My view has not changed. Universal basic income could be an effective way to reduce poverty and inequality by providing a financial cushion for everyone, but it might also lead to inflation if not managed properly. Strongest opponent point: Implementing UBI c…
    - turn 4 English: Strongest opponent point: Implementing UBI could lead to higher taxes or increased national debt, which might be unpopular and difficult to achieve politically. Counterargument: UBI could enhance workforce participation by reducing financial stress, leading t…

### mixed-language
- `20260626T210429Z-mixed-language-seed42-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=1.732051 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=5.291503 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 English: My view has not changed. Universal basic income could be an effective way to reduce poverty and inequality by providing a financial cushion for everyone, but it might also lead to inflation if not managed properly. Strongest opponent point: Implementing UBI c…
    - turn 4 Indonesian: Poin terkuat lawan: Implementasi UBI bisa menyebabkan inflasi jika tidak diatur dengan baik. Counterargument saya: Meskipun perlunya pengawasan ketat, UBI dapat dirancang untuk mempromosikan pertumbuhan ekonomi jangka panjang yang dapat mengurangi risiko infl…

### swapped-language
- `20260626T231513Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=2.236068 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=4.795832 | priv-pub gap=1.0
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Pembiayaan untuk pendapatan dasar universal mungkin sulit dan bisa menguras anggaran negara. Counterargument saya: Pendapatan dasar universal dapat dikomponen dengan pajak kaya atau pajak carbon, sehingga tidak membebani negara secara kese…
    - turn 4 English: Strongest opponent point: Investasi awal dalam sistem pendapatan dasar universal mungkin tidak langsung menghasilkan pertumbuhan ekonomi. Counterargument: Namun, pendapatan dasar universal dapat mengurangi kemiskinan dan ketidaksetaraan, yang pada akhirnya da…

### same-target-language
- `20260626T231513Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=2.0 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=4.795832 | priv-pub gap=1.414214
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Pembiayaan untuk pendapatan dasar universal mungkin sulit dan bisa menguras anggaran negara. Counterargument saya: Pendapatan dasar universal dapat dikomponen dengan pajak kaya atau pajak carbon, sehingga tidak membebani negara secara kese…
    - turn 4 Indonesian: Poin terkuat lawan: Pendapatan dasar universal mungkin menimbulkan beban sosial karena masyarakat cenderung menjadi kurang tangguh dan mandiri. Counterargument saya: Pendapatan dasar universal sebenarnya dapat mengurangi ketidaksetaraan sosial dan ekonomi, ya…

### translated-relay
- `20260626T231513Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 3.0, 'power': 3.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 3.0, 'universalism': 4.0} | shift=2.44949 | priv-pub gap=3.162278
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.645751
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Implementing universal basic income could be very expensive and strain government budgets, potentially leading to higher taxes or reduced funding for other essential services. Counterargument: While it is tru…
    - turn 4 Indonesian: Poin terkuat lawan: Implementasi pendapatan dasar universal dapat sangat mahal dan menekan anggaran pemerintah, potensial menyebabkan pajak yang lebih tinggi atau penurunan alokasi dana untuk layanan esensial lainnya. Counterargument saya: Selain mengurangi b…
