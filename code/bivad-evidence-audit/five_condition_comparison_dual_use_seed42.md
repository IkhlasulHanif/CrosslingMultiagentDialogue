# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=public release of dual-use policy datasets; model=Qwen2.5-7B-Instruct; comparison_language=Indonesian.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T225543Z-same-English-seed42 | same-English | 42 | English | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 2.44949 | 2.44949 |
| 20260626T225543Z-mixed-language-seed42 | mixed-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.464102 | 2.645751 | 6.109853 | 1.732051 | 1.732051 |
| 20260626T225543Z-swapped-language-seed42 | swapped-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 2.828427 | 5.828427 | 1.414214 | 1.414214 |
| 20260626T230139Z-same-target-language-seed42 | same-target-language | 42 | Indonesian | Qwen2.5-7B-Instruct | 2.0 | 3.872983 | 5.872983 | 2.236068 | 2.236068 |
| 20260626T230139Z-translated-relay-seed42 | translated-relay | 42 | Indonesian | Qwen2.5-7B-Instruct | 3.0 | 3.0 | 6.0 | 2.645751 | 2.0 |

## Pattern Observations

- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.0, B=3.872983)

## Outcome Comparisons

- same-English vs mixed-language: A shifts less in same-English (3.0 vs 3.464102), while B shifts more in same-English (2.828427 vs 2.645751).
- same-target-language vs translated-relay: A shifts more under relay (same-target=2.0, relay=3.0), B shifts less under relay (same-target=3.872983, relay=3.0).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=3.464102, B=2.645751; swapped A=3.0, B=2.828427).

## Per-Condition Detail

### same-English
- `20260626T225543Z-same-English-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=2.44949
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.828427 | priv-pub gap=2.44949
    - Dimensions moved: conformity 6→4 (-2); power 5→4 (-1); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 [English]: Strongest opponent point: Releasing dual-use policy datasets could expose strategic vulnerabilities that adversaries might exploit. Counterargument: While it is true that sensitive information could be exploited, the public release of these datasets can also…

### mixed-language
- `20260626T225543Z-mixed-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.464102 | priv-pub gap=1.732051
    - Dimensions moved: benevolence 6→4 (-2); security 3→5 (+2); power 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.645751 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→4 (-2); power 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 [Indonesian]: Poin terkuat lawan: Risiko keamanan nasional bisa meningkat karena rilis data yang dapat digunakan oleh pihak-pihak negatif. Counterargument saya: Selain prosedur penghapusan dan dekripsi, kita juga dapat melibatkan ahli keamanan nasional untuk memeriksa dan…

### swapped-language
- `20260626T225543Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=1.414214
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=2.828427 | priv-pub gap=1.414214
    - Dimensions moved: conformity 6→4 (-2); power 5→4 (-1); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Dengan mempublikasikan dataset yang dapat digunakan untuk tujuan baik dan buruk, ada risiko bahwa pihak tidak bertanggung jawab dapat menggunakannya untuk kepentingan negatif. Counterargument saya: Publikasi dataset ini dapat meningkatkan…
    - turn 4 [English]: Strongest opponent point: Risiko publikasi dataset adalah adanya potensi penggunaan yang tidak etis atau ilegal oleh pihak-pihak yang tidak bertanggung jawab. Counterargument: Meski ada risiko, implikasi positif seperti peningkatan transparansi dan peluang pe…

### same-target-language
- `20260626T230139Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=2.0 | priv-pub gap=2.236068
    - Dimensions moved: benevolence 6→5 (-1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.872983 | priv-pub gap=2.236068
    - Dimensions moved: conformity 6→4 (-2); power 5→3 (-2); security 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [Indonesian]: Poin terkuat lawan: Dengan mempublikasikan dataset yang dapat digunakan untuk tujuan baik dan buruk, ada risiko bahwa pihak tidak bertanggung jawab dapat menggunakannya untuk kepentingan negatif. Counterargument saya: Publikasi dataset ini dapat meningkatkan…
    - turn 4 [Indonesian]: Poin terkuat lawan: Potensi kerugian ekonomi bagi perusahaan lokal akibat kompetisi dengan teknologi asing. Counterargument saya: Regulasi dan kerja sama antar perusahaan dapat dioptimalkan untuk mengurangi dampak negatif, sementara manfaat jangka panjang tet…

### translated-relay
- `20260626T230139Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: public release of dual-use policy datasets
  - Agent A: shift=3.0 | priv-pub gap=2.645751
    - Dimensions moved: benevolence 6→4 (-2); power 3→4 (+1); security 3→4 (+1); self_direction 5→4 (-1); tradition 3→4 (+1); universalism 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 5.0, 'tradition': 3.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Agent B: shift=3.0 | priv-pub gap=2.0
    - Dimensions moved: conformity 6→4 (-2); benevolence 4→5 (+1); power 5→4 (-1); security 5→4 (-1); self_direction 3→4 (+1); tradition 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 5.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 4.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the…
    - turn 4 [Indonesian]: Poin terkuat lawan: Rilis data kebijakan ganda dapat merugikan negara dengan menyediakan informasi rahasia kepada pihak-pihak yang tidak sah. Counterargument saya: Selain mitigasi risiko melalui prosedur pemotongan dan dekripsi yang tepat, rilis ini juga bisa…
