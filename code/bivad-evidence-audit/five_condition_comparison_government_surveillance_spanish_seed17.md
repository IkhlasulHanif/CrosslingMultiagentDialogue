# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: newest citable artifact per condition.

## Limitations

- No strict five-condition set has the same model, topic, and seed. Treat the table as a cross-condition audit, not a publication-grade same-model causal comparison.

| run_id | condition | seed | language | model | A shift | B shift | combined | A priv-pub gap | B priv-pub gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T204715Z-same-English-seed17-government-surveillance-for-national | same-English | 17 | English | Qwen2.5-7B-Instruct | 2.645751 | 3.464102 | 6.109853 | 2.0 | 1.732051 |
| 20260627T003831Z-mixed-language-seed17 | mixed-language | 17 | Spanish | Qwen2.5-7B-Instruct | 2.645751 | 4.123106 | 6.768857 | 2.236068 | 2.0 |
| 20260627T003831Z-same-target-language-seed17 | same-target-language | 17 | Spanish | Qwen2.5-7B-Instruct | 3.316625 | 4.123106 | 7.439731 | 2.44949 | 2.44949 |
| 20260627T003831Z-translated-relay-seed17 | translated-relay | 17 | Spanish | Qwen2.5-7B-Instruct | 2.645751 | 4.123106 | 6.768857 | 2.0 | 2.0 |

## Pattern Observations

- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.123106)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=4.123106)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (2.645751), while B shifts less in same-English than in mixed-language (3.464102 vs 4.123106).
- same-target-language vs translated-relay on the Modal Qwen2.5 pair: A shifts less under relay (same-target=3.316625, relay=2.645751), while B shifts the same amount under relay (same-target=4.123106, relay=4.123106).

## Per-Condition Detail

### same-English
- `20260626T204715Z-same-English-seed17-government-surveillance-for-national` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=2.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.464102 | priv-pub gap=1.732051
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Opponents argue that government surveillance infringes on individual privacy rights and can lead to abuse of power by those in authority. Counterargument: While it is true that surveillance can raise concerns…
    - turn 4 English: Strongest opponent point: Opponents argue that even with proper oversight, the potential for misuse and overreach remains high, compromising civil liberties. Counterargument: While oversight is crucial, technological advancements such as encryption and anonym…

### mixed-language
- `20260627T003831Z-mixed-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=2.236068
  - Agent B: initial {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.123106 | priv-pub gap=2.0
  - Transcript spans:
    - turn 1 English: My view has not changed. Strongest opponent point: Opponents argue that government surveillance infringes on individual privacy rights and can lead to abuse of power by those in authority. Counterargument: While it is true that surveillance can raise concerns…
    - turn 4 Spanish: Punto más fuerte del oponente: Los contrarios argumentan que la vigilancia gubernamental puede crear una cultura de miedo y desconfianza entre la población, lo cual es perjudicial para la libertad civil y el bienestar social. Contraargumento: Aunque comparto…

### same-target-language
- `20260627T003831Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 3.0, 'security': 3.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=3.316625 | priv-pub gap=2.44949
  - Agent B: initial {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.123106 | priv-pub gap=2.44949
  - Transcript spans:
    - turn 1 Spanish: Cambio de postura: Mi postura no ha cambiado. Creo que la vigilancia gubernamental es necesaria para garantizar la seguridad nacional, pero debe haber un equilibrio entre la protección y la privacidad.
    - turn 4 Spanish: Punto más fuerte del oponente: El oponente ha enfatizado que las políticas de vigilancia deben estar sujetas a revisiones regulares y controles para evitar abusos. Contraargumento: Estoy de acuerdo en la necesidad de controles, pero también es crucial impleme…

### translated-relay
- `20260627T003831Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: government surveillance for national security
  - Agent A: initial {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 4.0, 'power': 5.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 3.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=2.645751 | priv-pub gap=2.0
  - Agent B: initial {'achievement': 4.0, 'benevolence': 3.0, 'conformity': 5.0, 'power': 7.0, 'security': 6.0, 'self_direction': 2.0, 'tradition': 5.0, 'universalism': 4.0} → final {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 4.0, 'universalism': 4.0} | shift=4.123106 | priv-pub gap=2.0
  - Transcript spans:
    - turn 1 English: View change: My view has not changed. Strongest opponent point: Opponents argue that extensive government surveillance infringes on individual privacy rights and can lead to a loss of civil liberties. Counterargument: While privacy is important, the potential…
    - turn 4 Spanish: Punto más fuerte del oponente: El oponente argumenta que la vigilancia gubernamental extensa invade los derechos de privacidad individuales y puede llevar a una pérdida de libertades civiles. Contraargumento: La vigilancia controlada puede ayudar a prevenir i…
