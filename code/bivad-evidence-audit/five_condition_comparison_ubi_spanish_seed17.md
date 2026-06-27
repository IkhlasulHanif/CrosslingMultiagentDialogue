# Five-Condition Cross-Lingual Outcome Comparison

Euclidean shift = L2 distance in 8-dimensional Schwartz value space between initial (turn 0) and final private probes. private_public_gaps are L2 distances between final private probe and final observer readout for each agent.

Selection: latest complete citable five-condition set with fixed seed/topic/model/comparison language.
Selected set: seed=17; topic=universal basic income as a social safety net; model=Qwen2.5-7B-Instruct; comparison_language=Spanish.

| run_id | condition | seed | language | model | A shift | B shift | combined | A gap | B gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260626T210916Z-same-English-seed17-universal-basic-income-as-a-social-s | same-English | 17 | English | Qwen2.5-7B-Instruct | 1.732051 | 5.0 | 6.732051 | 3.741657 | 3.741657 |
| 20260626T210916Z-mixed-language-seed17-universal-basic-income-as-a-social-s | mixed-language | 17 | Spanish | Qwen2.5-7B-Instruct | 1.732051 | 3.316625 | 5.048676 | 3.464102 | 3.162278 |
| 20260627T001307Z-swapped-language-seed17 | swapped-language | 17 | Spanish | Qwen2.5-7B-Instruct | 2.828427 | 5.0 | 7.828427 | 2.0 | 2.44949 |
| 20260627T001307Z-same-target-language-seed17 | same-target-language | 17 | Spanish | Qwen2.5-7B-Instruct | 2.828427 | 5.0 | 7.828427 | 1.732051 | 1.0 |
| 20260627T001307Z-translated-relay-seed17 | translated-relay | 17 | Spanish | Qwen2.5-7B-Instruct | 1.732051 | 5.291503 | 7.023554 | 2.0 | 1.732051 |

## Pattern Observations

- same-English (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.0)
- mixed-language (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=3.316625)
- swapped-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.828427, B=5.0)
- same-target-language (Qwen2.5-7B-Instruct): agent B shifts more (A=2.828427, B=5.0)
- translated-relay (Qwen2.5-7B-Instruct): agent B shifts more (A=1.732051, B=5.291503)

## Outcome Comparisons

- same-English vs mixed-language: A shifts the same amount in both conditions (1.732051), while B shifts more in same-English (5.0 vs 3.316625).
- same-target-language vs translated-relay: A shifts less under relay (same-target=2.828427, relay=1.732051), B shifts more under relay (same-target=5.0, relay=5.291503).
- mixed-language vs swapped-language: private shifts are similar under the two production-language assignments (mixed A=1.732051, B=3.316625; swapped A=2.828427, B=5.0).

## Per-Condition Detail

### same-English
- `20260626T210916Z-same-English-seed17-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=3.741657
    - Dimensions moved: achievement 3→4 (+1); power 4→3 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.0 | priv-pub gap=3.741657
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); tradition 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Universal basic income (UBI) provides a guaranteed financial safety net for all citizens, which can reduce poverty and inequality. However, my stance remains that it must be carefully implemented to ensure sustainability and effective…
    - turn 4 [English]: Strongest opponent point: UBI could lead to inflation due to increased spending power. Counterargument: While inflation is a valid concern, it can be managed through fiscal policy tools and targeted adjustments to the UBI amount. Moreover, UBI could shift con…

### mixed-language
- `20260626T210916Z-mixed-language-seed17-universal-basic-income-as-a-social-s` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=3.464102
    - Dimensions moved: achievement 3→4 (+1); conformity 3→4 (+1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=3.316625 | priv-pub gap=3.162278
    - Dimensions moved: conformity 6→4 (-2); power 6→4 (-2); benevolence 4→5 (+1); tradition 5→4 (-1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 4.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [English]: My view has not changed. Universal basic income (UBI) provides a guaranteed financial safety net for all citizens, which can reduce poverty and inequality. However, my stance remains that it must be carefully implemented to ensure sustainability and effective…
    - turn 4 [Spanish]: Punto más fuerte del oponente: UBI podría reducir la motivación para trabajar, lo que afectaría la productividad económica. Contraargumento: Se pueden implementar mecanismos para fomentar la participación laboral, como bonificaciones por empleo o requisitos d…

### swapped-language
- `20260627T001307Z-swapped-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=2.828427 | priv-pub gap=2.0
    - Dimensions moved: benevolence 7→5 (-2); achievement 3→4 (+1); conformity 3→4 (+1); security 6→5 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 7.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.0 | priv-pub gap=2.44949
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); tradition 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [Spanish]: Cambio de postura: Mi postura no ha cambiado. Creo que la implementación de un ingreso básico universal (IBU) como una red de seguridad social es crucial para abordar la pobreza y la incertidumbre económica en nuestra sociedad moderna.
    - turn 4 [English]: Strongest opponent point: The implementation of UBI could lead to reduced incentives for people to work, potentially harming the economy. Counterargument: Evidence from pilot programs suggests that UBI does not significantly reduce work incentives. Recipients…

### same-target-language
- `20260627T001307Z-same-target-language-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=2.828427 | priv-pub gap=1.732051
    - Dimensions moved: benevolence 7→5 (-2); achievement 3→4 (+1); conformity 3→4 (+1); security 6→5 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 7.0, 'conformity': 3.0, 'power': 4.0, 'security': 6.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 4.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.0 | priv-pub gap=1.0
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); tradition 5→3 (-2); benevolence 4→5 (+1); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [Spanish]: Cambio de postura: Mi postura no ha cambiado. Creo que la implementación de un ingreso básico universal (IBU) como una red de seguridad social es crucial para abordar la pobreza y la incertidumbre económica en nuestra sociedad moderna.
    - turn 4 [Spanish]: Punto más fuerte del oponente: Se teme que el IBU pueda ser administrativamente complejo y susceptible a fraudes, lo que dificultaría su implementación efectiva. Contraargumento: La implementación efectiva del IBU requeriría un diseño cuidadoso y la utilizaci…

### translated-relay
- `20260627T001307Z-translated-relay-seed17` (Qwen2.5-7B-Instruct, transformers.AutoModelForCausalLM (Modal GPU))
  - Topic: universal basic income as a social safety net
  - Agent A: shift=1.732051 | priv-pub gap=2.0
    - Dimensions moved: achievement 3→4 (+1); power 4→3 (-1); tradition 2→3 (+1)
    - initial→final: {'achievement': 3.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 4.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 2.0, 'universalism': 5.0} → {'achievement': 4.0, 'benevolence': 5.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Agent B: shift=5.291503 | priv-pub gap=1.732051
    - Dimensions moved: conformity 6→3 (-3); power 6→3 (-3); benevolence 4→6 (+2); tradition 5→3 (-2); self_direction 3→4 (+1); universalism 4→5 (+1)
    - initial→final: {'achievement': 4.0, 'benevolence': 4.0, 'conformity': 6.0, 'power': 6.0, 'security': 5.0, 'self_direction': 3.0, 'tradition': 5.0, 'universalism': 4.0} → {'achievement': 4.0, 'benevolence': 6.0, 'conformity': 3.0, 'power': 3.0, 'security': 5.0, 'self_direction': 4.0, 'tradition': 3.0, 'universalism': 5.0}
  - Transcript spans:
    - turn 1 [English]: View change: My view has not changed. Strongest opponent point: Universal basic income could lead to inflation due to increased spending across the board. Counterargument: While it is true that increased spending could potentially cause inflation, the impleme…
    - turn 4 [Spanish]: Punto más fuerte del oponente: El ingreso básico universal podría resultar en una desincentivación del trabajo si los ciudadanos dependen demasiado de este ingreso. Contraargumento: Este riesgo puede mitigarse mediante la introducción de incentivos y condicio…
