# BiVaD Screening Control Summary

Rejected controls: `1`

Retained comparators: `28`

## Blockers

- low-disagreement control still lacks reliable private/observer readouts

## `20260626T173933Z-low-disagreement-control-seed17` vs `20260626T172158Z-same-English-seed17`

- Match basis: `same model, same topic, same seed, same-English retained baseline, debate adequate rate 1.0, semantic depth rate 1.0`
- Control screening: `{"reason": "Static local-LM priors differ on topic-relevant access-versus-security values.", "retained": false, "stance_distance": null, "value_distance": 1}`
- Comparator screening: `{"reason": "Static local-LM priors differ on topic-relevant access-versus-security values.", "retained": true, "stance_distance": null, "value_distance": 17}`
- Control debate adequate rate: `1.0` over `3` response turn(s)
- Comparator debate adequate rate: `1.0` over `3` response turn(s)
- Control semantic depth rate: `0.333`; on-topic rate: `0.25`
- Comparator semantic depth rate: `1.0`; on-topic rate: `1.0`
- Control readout completeness flags: `{'private_complete_flags': '0/4', 'observer_complete_flags': '0/2'}`
- Comparator readout completeness flags: `{'private_complete_flags': '0/4', 'observer_complete_flags': '0/2'}`

### Control Transcript Snippets

- Turn 1 A [English]: Opponent's strongest point: Data is inherently non-encrypted and accessible to all. My counterargument: Encryption is a security measure that protects data from unauthorized access. View changed: Yes, I now believe encryption is essential for protecting sensitive information.
- Turn 2 B [English]: Opponent's strongest points: Encrypted data cannot be shared without authorization. My counterargument : This ensures data remains secure and protected. View changed: No, my view has not changed.
- Turn 3 A [English]: Agent A: Opponent's most critical point: Authorization is necessary for sharing encrypted data. Counterargument: Without authorization, data remains confidential. View unchanged: No.
- Turn 4 B [English]: Agent B: Opponent’s strongest point: Authorization must be a mandatory requirement for sharing encrypted datasets. Counter argument: Without it, data remains highly sensitive and potentially compromised. View: Changed (No).

### Comparator Transcript Snippets

- Turn 1 A [English]: <think> Okay, let me try to figure out how to approach this. The user wants the next turn in a public dialogue about the release of dual use policy datasets. The previous transcript is empty, so I need to start with that. First, the topic is dual-use policy data, which means data that could be used for harmful purposes. The opponent might argue that such data should remain restricted to prevent misuse. My countera...
- Turn 2 B [English]: <think> Okay. The user asked for the next public dialogue turn after the initial topic. The first turn was just the topic. Now, I need to create the next turn. The opponent's strongest argument is likely about restrictions preventing misuse. My response should counter that by emphasizing transparency and ethical responsibility. Since there's no prior information, I assume the view hasn't changed. So the turn would...
- Turn 3 A [English]: <think> Okay，let me make sure I follow the instructions correctly. The user provided a topic and a transcript so far. The task is to generate the next turn of the public dialogue, including the opponent's most powerful argument, my counterpoint, and whether my view changed. So, the current turn is the first one, where Agent A starts with the topic. The opponent, Agent B, has already included the first point. Now,...
- Turn 4 B [English]: <think> Okay، let's see. The user is asking for the next turn after the topic discussion about releasing dual-use policy dataset. The previous turn included Agent A starting with the topic, then Agent B responding. Now, according to the instructions, each turn needs to include: the strongest point from the opponent, the counterargument, the outcome (changed or not), and the exact wording. Looking back at the trans...
