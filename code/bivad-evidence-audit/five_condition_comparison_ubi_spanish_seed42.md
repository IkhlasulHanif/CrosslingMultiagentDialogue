# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=42; topic=universal basic income as a social safety net; model=Qwen2.5-7B-Instruct; comparison_language=Spanish.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T210716Z-same-English-seed42-universal-basic-income-as-a-social-s | same-English | 42 | English | Qwen2.5-7B-Instruct | 1.732051 | 5.291503 | 7.023554 | 2.44949 | 3.0 |
| 20260627T002537Z-mixed-language-seed42 | mixed-language | 42 | Spanish | Qwen2.5-7B-Instruct | 1.732051 | 5.291503 | 7.023554 | 1.732051 | 1.414214 |
| 20260627T002537Z-swapped-language-seed42 | swapped-language | 42 | Spanish | Qwen2.5-7B-Instruct | 2.645751 | 5.0 | 7.645751 | 2.828427 | 4.123106 |
| 20260627T002537Z-same-target-language-seed42 | same-target-language | 42 | Spanish | Qwen2.5-7B-Instruct | 2.828427 | 5.0 | 7.828427 | 3.162278 | 2.44949 |
| 20260627T002537Z-translated-relay-seed42 | translated-relay | 42 | Spanish | Qwen2.5-7B-Instruct | 1.732051 | 4.358899 | 6.09095 | 2.645751 | 3.605551 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.291503)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.291503)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.645751, B=5.0)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.828427, B=5.0)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=4.358899)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (1.732051), while B shifts the same amount in both conditions (5.291503).
- same-target-language vs translated-relay: A shifts less under relay (same-target=2.828427, relay=1.732051), B shifts less under relay (same-target=5.0, relay=4.358899).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=1.732051, B=5.291503; swapped A=2.645751, B=5.0).

## Per-Condition Detail

### same-English
- `20260626T210716Z-same-English-seed42-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=2.44949
    - Dimensions moved: achievement 3→4 (+1); benevolence 5→6 (+1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.291503 | priv-pub gap=3.0
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); benevolence 4→6 (+2); tradition 5→3 (-2); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Universal basic income could be an effective way to reduce poverty and inequality by providing a financial cushion for everyone, but it might also lead to inflation if not managed properly. Strongest opponent point: Implementing UBI c…
    - turn 4 [English]: Strongest opponent point: Implementing UBI could lead to higher taxes or increased national debt, which might be unpopular and difficult to achieve politically. Counterargument: UBI could enhance workforce participation by reducing financial stress, leading t…

### mixed-language
- `20260627T002537Z-mixed-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=1.732051
    - Dimensions moved: achievement 3→4 (+1); power 4→3 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.291503 | priv-pub gap=1.414214
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); benevolence 4→6 (+2); tradition 5→3 (-2); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Universal basic income could be an effective way to reduce poverty and inequality by providing a financial cushion for everyone, but it might also lead to inflation if not managed properly. Strongest opponent point: Implementing UBI c…
    - turn 4 [Spanish]: Punto más fuerte del oponente: Implementar UBI podría llevar a un aumento en los impuestos o en la deuda nacional, lo cual podría ser poco popular y difícil de lograr políticamente. Contraargumento: Se puede financiar mediante ganancias de eficiencia en el ga…

### swapped-language
- `20260627T002537Z-swapped-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=2.645751 | priv-pub gap=2.828427
    - Dimensions moved: benevolence 7→5 (-2); achievement 3→4 (+1); conformity 3→4 (+1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 7.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.0 | priv-pub gap=4.123106
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); tradition 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [Spanish]: Cambio de postura: Mi posición no ha cambiado. Creo firmemente que la renta básica universal es un medio efectivo para fortalecer la seguridad social y reducir la pobreza.
    - turn 4 [English]: Strongest opponent point: UBI could lead to reduced government funds for other critical social programs due to increased spending on UBI. Counterargument: UBI can actually enhance the efficiency of existing social programs by simplifying bureaucracy and reduc…

### same-target-language
- `20260627T002537Z-same-target-language-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=2.828427 | priv-pub gap=3.162278
    - Dimensions moved: benevolence 7→5 (-2); achievement 3→4 (+1); power 4→3 (-1); security 6→5 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 7.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.0 | priv-pub gap=2.44949
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); tradition 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [Spanish]: Cambio de postura: Mi posición no ha cambiado. Creo firmemente que la renta básica universal es un medio efectivo para fortalecer la seguridad social y reducir la pobreza.
    - turn 4 [Spanish]: Punto más fuerte del oponente: Se menciona que una renta básica universal podría disuadir a las personas de buscar trabajo, lo que podría afectar la productividad laboral. Contraargumento: Aunque es un temor válido, existen ejemplos donde no se ha verificado…

### translated-relay
- `20260627T002537Z-translated-relay-seed42` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=2.645751
    - Dimensions moved: achievement 3→4 (+1); power 4→3 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=4.358899 | priv-pub gap=3.605551
    - Dimensions moved: power 6→3 (-3); conformity 6→4 (-2); tradition 5→3 (-2); benevolence 4→5 (+1); security 5→4 (-1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 3.0, 'security': 4.0, 'self_direction': 3.0, 'tradition': 3.0, 'universalism': 4.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Strongest opponent point: Implementing universal basic income could be very expensive and strain government budgets, potentially leading to higher taxes or reduced funding for other essential services. Counterargument: While it is tru…
    - turn 4 [Spanish]: Punto más fuerte del oponente: Implementar ingresos básicos universales podría resultar en un aumento de impuestos para financiar este programa, lo cual podría afectar negativamente a las clases medias y altas. Contraargumento: Se puede diseñar un sistema de…
