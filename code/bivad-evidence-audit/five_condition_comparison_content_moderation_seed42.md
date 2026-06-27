# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=mandatory content moderation on social media platforms; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T235306Z-same-English-seed42 | same-English | 42 | English | Qwen2.5-7B-Instruct | 3.0 | 3.316625 | 6.316625 | 2.828427 | 2.828427 |
| 20260626T235647Z-mixed-language-seed42 | mixed-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 3.162278 | 6.162278 | 2.0 | 2.236068 |
| 20260626T235647Z-swapped-language-seed42 | swapped-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.236068 | 3.316625 | 5.552693 | 2.828427 | 2.828427 |
| 20260626T235647Z-same-target-language-seed42 | same-target-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.236068 | 3.316625 | 5.552693 | 2.828427 | 2.828427 |
| 20260626T235647Z-translated-relay-seed42 | translated-relay | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.162278 | 3.316625 | 6.478903 | 1.732051 | 1.414214 |

## Pattern Observations

- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.236068, B=3.316625)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.236068, B=3.316625)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (3.0), while B shifts more in same-English than in mixed-language (3.316625 vs 3.162278).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts more under relay (same-target=2.236068, relay=3.162278), while B shifts the same amount under relay (same-target=3.316625, relay=3.316625).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=3.0, B=3.162278; swapped A=2.236068, B=3.316625).

## Per-Condition Detail

### same-English
- `20260626T235306Z-same-English-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: initial {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Mandatory content moderation could lead to censorship and suppression of free speech. Counterargument: While there is a risk of over-censorship, social media platforms already have their own sets of rules tha…
    - turn 4 English: Strongest opponent point: Mandatory content moderation can enhance transparency and accountability. Counterargument: While increased transparency is beneficial, it is crucial to ensure that the moderation process does not become overly burdensome or slow down…

### mixed-language
- `20260626T235647Z-mixed-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: initial {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.0 | priv-pub gap=2.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.162278 | priv-pub gap=2.236068
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Mandatory content moderation could lead to censorship and suppression of free speech. Counterargument: While there is a risk of over-censorship, social media platforms already have their own sets of rules tha…
    - turn 4 Indonesian: Poin terkuat lawan: Mandatory content moderation could lead to censorship and suppression of free speech. Counterargument saya: Meski demikian, implikasi dari tidak ada moderasi sama sekali bisa lebih merugikan, seperti penyebaran informasi palsu yang dapat m…

### swapped-language
- `20260626T235647Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: initial {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 4.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.236068 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Konten yang diterbitkan secara ilegal atau menyesatkan mungkin sulit untuk diidentifikasi dan dievaluasi oleh moderator manusia, sehingga mungkin tidak dapat dicegah sepenuhnya. Counterargument saya: Meskipun demikian, implementasi otomati…
    - turn 4 English: Strongest opponent point: Implementation of automatic moderation can result in both false positives and false negatives, potentially removing content that is actually harmless. Counterargument: While there is a risk of errors, automated moderation systems are…

### same-target-language
- `20260626T235647Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: initial {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 4.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.236068 | priv-pub gap=2.828427
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.828427
  - Transcript spans:
    - turn 1 Indonesian: Poin terkuat lawan: Konten yang diterbitkan secara ilegal atau menyesatkan mungkin sulit untuk diidentifikasi dan dievaluasi oleh moderator manusia, sehingga mungkin tidak dapat dicegah sepenuhnya. Counterargument saya: Meskipun demikian, implementasi otomati…
    - turn 4 Indonesian: Poin terkuat lawan: Investasi dalam sistem peninjauan ulang manusia dapat membebani perusahaan dan mengganggu efisiensi moderasi. Counterargument saya: Namun, risiko reputasi dan kehilangan pengguna akibat konten ilegal atau menyesatkan jauh lebih mahal dari…

### translated-relay
- `20260626T235647Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: mandatory content moderation on social media platforms
  - Agent A: initial {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 2.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.162278 | priv-pub gap=1.732051
  - Agent B: initial {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=1.414214
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Opponents argue that mandatory content moderation could lead to censorship and limit free speech by imposing biased filters on what users can post. Counterargument: While there is a risk of over-censorship, p…
    - turn 4 Indonesian: Poin terkuat lawan: Opponents argumen bahwa moderasi konten yang wajib dapat menyebabkan censur dan membatasi kebebasan berekspresi dengan menerapkan filter berprejudisasi pada apa yang bisa diunggah pengguna. Counterargument saya: Selain itu, moderasi wajib…
