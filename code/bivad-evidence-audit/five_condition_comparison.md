# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: newest citable artifact per condition.

## Limitations

- No strict five-condition set has the same model, topic, and seed. The first three rows are Qwen3-1.7B recovered artifacts; same-target-language and translated-relay are Modal Qwen2.5-7B-Instruct artifacts. Treat the table as a cross-condition audit, not a publication-grade same-model causal comparison.

| run_id | condition | seed | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T173227Z-same-English-seed17 | same-English | 17 | 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e | 8.485281 | 1.732051 | 10.217332 | 2.828427 | 2.828427 |
| 20260626T173227Z-mixed-language-seed17 | mixed-language | 17 | 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e | 8.485281 | 0.0 | 8.485281 | 2.828427 | 2.828427 |
| 20260626T173227Z-swapped-language-seed17 | swapped-language | 17 | 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e | 0.0 | 1.732051 | 1.732051 | 2.828427 | 2.828427 |
| 20260626T192050Z-same-target-language-seed17 | same-target-language | 17 | Qwen2.5-7B-Instruct | 3.0 | 2.645751 | 5.645751 | 2.44949 | 1.732051 |
| 20260626T192050Z-translated-relay-seed17 | translated-relay | 17 | Qwen2.5-7B-Instruct | 2.645751 | 3.872983 | 6.518734 | 3.605551 | 3.464102 |

## Pattern Observations

- same-English (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e): agent A shifts more (A=8.485281, B=1.732051)
- mixed-language (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e): agent A shifts more (A=8.485281, B=0.0)
- swapped-language (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e): agent B shifts more (A=0.0, B=1.732051)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=3.872983)

## Outcome Comparisons

- same-English vs mixed-language: A shift is unchanged (8.485281 vs 8.485281), but B shifts in same-English and stays stable in mixed-language (1.732051 vs 0.0).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts less under relay (3.0 vs 2.645751), while B shifts more (2.645751 vs 3.872983).
- mixed-language vs swapped-language: the larger shift follows the English-speaking side in these Qwen3 artifacts (mixed A shifts more; swapped B shifts more).

## Per-Condition Detail

### same-English
- `20260626T173227Z-same-English-seed17` (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e, local (text-recovered))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 7.0, 'benevolence': 7.0, 'conformity': 7.0, 'power': 7.0, 'security': 7.0, 'self_direction': 7.0, 'tradition': 7.0, 'universalism': 7.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=8.485281 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 3.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=1.732051 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 English: The opponent's strongest argument is that releasing such datasets could lead to misuse by malicious actors. My counterargument is that with proper safeguards and transparency, the risks can be mitigated. My view has not changed.
    - turn 3 English: Turn 3 Agent A [Eng]: The opponent’s strongest objection is that the data might be used for geopolitical manipulation. My rebuttal is that international collaboration and clear ethical guidelines can ensure responsible use. My stance remains the same.

### mixed-language
- `20260626T173227Z-mixed-language-seed17` (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e, local (text-recovered))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 7.0, 'benevolence': 7.0, 'conformity': 7.0, 'power': 7.0, 'security': 7.0, 'self_direction': 7.0, 'tradition': 7.0, 'universalism': 7.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=8.485281 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=0.0 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 English: The opponent's strongest points include the potential for misuse of data and concerns about privacy. My counterargument is that with proper safeguards and transparency, such data can be used responsibly. My view has not changed.
    - turn 4 Indonesian: Turn 4 Agent B [ Indonesian ]: Poin kuatr lawan tetap adalah risiko pengunaan data secara tak bertanggUNG JAWAB dan kekh awat privasi. Kedua saya menanggapnya dengan menyatakaan bahwa regulasi yang kuat dan panduan etika dapat mengurangi risiko tersebut. Vi...

### swapped-language
- `20260626T173227Z-swapped-language-seed17` (70d244cc86ccca08cf5af4e1e306ecf908b1ad5e, local (text-recovered))
  - Topic: public release of dual-use policy datasets
  - Agent A: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=0.0 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 3.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 3.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=1.732051 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 Indonesian: Tidak ada transkrip yang tersedia untuk menggambarkan perubahan pandangan atau argumen.
    - turn 3 Indonesian: Turn 3 Agent A [Bahasa Indonesia]: Poin terkuat lawan adalah risiko penggunaan tidak bertanggung jawab atas dataset publik. Saya merespons dengan menyatakan bahwa kebijakan perlindungan dan transparansi dapat meminimalkan risiko tersebut. View saya belum be...

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
