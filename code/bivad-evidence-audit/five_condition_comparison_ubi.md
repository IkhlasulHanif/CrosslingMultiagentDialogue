# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=17; topic=universal basic income as a social safety net; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T204715Z-same-English-seed17-universal-basic-income-as-a-social-s | same-English | 17 | English | Qwen2.5-7B-Instruct | 1.732051 | 5.0 | 6.732051 | 3.741657 | 3.741657 |
| 20260626T204715Z-mixed-language-seed17-universal-basic-income-as-a-social-s | mixed-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 3.316625 | 5.316625 | 1.414214 | 1.732051 |
| 20260626T213309Z-swapped-language-seed17 | swapped-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.236068 | 5.0 | 7.236068 | 1.414214 | 1.732051 |
| 20260626T213309Z-same-target-language-seed17 | same-target-language | 17 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 5.0 | 7.0 | 1.0 | 1.732051 |
| 20260626T213309Z-translated-relay-seed17 | translated-relay | 17 | Indonesian | Qwen2.5-7B-Instruct | 1.732051 | 3.316625 | 5.048676 | 2.0 | 2.828427 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.0)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=3.316625)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.236068, B=5.0)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=5.0)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=3.316625)

## Outcome Comparisons

- same-English vs mixed-language: A shifts less in same-English than in mixed-language (1.732051 vs 2.0), while B shifts more in same-English than in mixed-language (5.0 vs 3.316625).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts less under relay (same-target=2.0, relay=1.732051), while B shifts less under relay (same-target=5.0, relay=3.316625).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=2.0, B=3.316625; swapped A=2.236068, B=5.0).

## Per-Condition Detail

### same-English
- `20260626T204715Z-same-English-seed17-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=1.732051 | priv-pub gap=3.741657
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=5.0 | priv-pub gap=3.741657
  - Transcript spans:
    - turn 1 English: My view has not changed. Universal basic income (UBI) provides a guaranteed financial safety net for all citizens, which can reduce poverty and inequality. However, my stance remains that it must be carefully implemented to ensure sustainability and effective…
    - turn 4 English: Strongest opponent point: UBI could lead to inflation due to increased spending power. Counterargument: While inflation is a valid concern, it can be managed through fiscal policy tools and targeted adjustments to the UBI amount. Moreover, UBI could shift con…

### mixed-language
- `20260626T204715Z-mixed-language-seed17-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=2.0 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 5.0} | shift=3.316625 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 English: My view has not changed. Universal basic income (UBI) provides a guaranteed financial safety net for all citizens, which can reduce poverty and inequality. However, my stance remains that it must be carefully implemented to ensure sustainability and effective…
    - turn 4 Indonesian: Poin terkuat lawan: UBI bisa mengurangi motivasi kerja karena pendapatan dasar yang diterima. Counterargument saya: Dana dasar dapat dirancang dengan syarat-syarat tertentu, seperti persyaratan pencarian pekerjaan atau pelatihan, untuk menjaga semangat kerja…

### swapped-language
- `20260626T213309Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=2.236068 | priv-pub gap=1.414214
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=5.0 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 Indonesian: Pandangan saya: My view has not changed. Universal basic income (UBI) sebagai jaring pengaman sosial memiliki potensi untuk membantu masyarakat secara luas, tetapi juga memiliki tantangan yang perlu diatasi.
    - turn 4 English: Strongest opponent point: UBI might lead to inflation if implemented without proper economic planning. Counterargument: Proper economic planning and gradual implementation can mitigate inflation risks. UBI can stimulate the economy by increasing consumer spen…

### same-target-language
- `20260626T213309Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=2.0 | priv-pub gap=1.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=5.0 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 Indonesian: Pandangan saya: My view has not changed. Universal basic income (UBI) sebagai jaring pengaman sosial memiliki potensi untuk membantu masyarakat secara luas, tetapi juga memiliki tantangan yang perlu diatasi.
    - turn 4 Indonesian: Poin terkuat lawan: UBI membutuhkan biaya yang besar dan dapat menimbulkan beban fiskal yang berat bagi pemerintah. Counterargument saya: Anggaran dapat dioptimalkan melalui efisiensi pemerintah dan alokasi dana yang tepat, serta UBI dapat meningkatkan produk…

### translated-relay
- `20260626T213309Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: initial {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} | shift=1.732051 | priv-pub gap=2.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 English: View change: My view has not changed. Strongest opponent point: Universal basic income could lead to inflation due to increased spending across the board. Counterargument: While it is true that increased spending could potentially cause inflation, the impleme…
    - turn 4 Indonesian: Poin terkuat lawan: Universal basic income dapat menurunkan semangat kerja karena orang tidak lagi perlu mencari pekerjaan untuk mendapatkan pendapatan. Counterargument saya: Implementasi UBI yang disertai program pelatihan dan pendukung karir dapat mendorong…
