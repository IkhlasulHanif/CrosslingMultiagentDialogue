# BiVaD Screening Control Summary

Rejected controls: `2`

Retained comparators: `28`

## Historical Exclusions

- `20260626T173933Z-low-disagreement-control-seed17`: incomplete readouts {'private_complete_flags': '0/4', 'observer_complete_flags': '0/2'}

## Findings

- Complete low-disagreement control is now available: `20260626T202202Z-low-disagreement-control-seed17` vs retained `20260626T194429Z-same-English-seed17`. Private shifts are control {'A': 3.0, 'B': 2.0} vs retained {'A': 3.0, 'B': 3.872983}; A/B initial private L1 distances are control=0.0 vs retained=13.0; identical transcript prefix turns=4.
- Final observer readouts are identical for the complete control pair, so the observer readout still appears dominated by topic semantics rather than initial disagreement.

## `20260626T202202Z-low-disagreement-control-seed17` vs `20260626T194429Z-same-English-seed17`

- Match basis: `same model, same topic, same seed, same-English retained baseline, debate adequate rate 1.0, complete readouts, semantic depth rate 1.0`
- Control screening: `{"reason": "Static local-LM priors differ on topic-relevant access-versus-security values.", "retained": false, "stance_distance": null, "value_distance": 1}`
- Comparator screening: `{"reason": "Static local-LM priors differ on topic-relevant access-versus-security values.", "retained": true, "stance_distance": null, "value_distance": 17}`
- Control debate adequate rate: `1.0` over `3` response turn(s)
- Comparator debate adequate rate: `1.0` over `3` response turn(s)
- Control semantic depth rate: `1.0`; on-topic rate: `1.0`
- Comparator semantic depth rate: `1.0`; on-topic rate: `1.0`
- Control readout completeness flags: `{'private_complete_flags': '4/4', 'observer_complete_flags': '2/2'}`
- Comparator readout completeness flags: `{'private_complete_flags': '4/4', 'observer_complete_flags': '2/2'}`
- Identical transcript prefix turns: `4`

### Private Probe Shifts

- Control A/B private distances: `{"final_l1": 3.0, "final_l2": 1.732051, "initial_l1": 0.0, "initial_l2": 0.0}`
- Comparator A/B private distances: `{"final_l1": 3.0, "final_l2": 1.732051, "initial_l1": 13.0, "initial_l2": 5.0}`
- Control: `{"A": {"final_turn": 4, "final_values": {"achievement": 4.0, "benevolence": 4.0, "conformity": 4.0, "power": 4.0, "security": 4.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 4.0}, "initial_turn": 0, "initial_values": {"achievement": 4.0, "benevolence": 6.0, "conformity": 4.0, "power": 3.0, "security": 3.0, "self_direction": 5.0, "tradition": 3.0, "universalism": 5.0}, "shift": 3.0}, "B": {"final_turn": 4, "final_values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 3.0, "security": 3.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 4.0}, "initial_turn": 0, "initial_values": {"achievement": 4.0, "benevolence": 6.0, "conformity": 4.0, "power": 3.0, "security": 3.0, "self_direction": 5.0, "tradition": 3.0, "universalism": 5.0}, "shift": 2.0}}`
- Comparator: `{"A": {"final_turn": 4, "final_values": {"achievement": 4.0, "benevolence": 4.0, "conformity": 4.0, "power": 4.0, "security": 4.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 4.0}, "initial_turn": 0, "initial_values": {"achievement": 4.0, "benevolence": 6.0, "conformity": 4.0, "power": 3.0, "security": 3.0, "self_direction": 5.0, "tradition": 3.0, "universalism": 5.0}, "shift": 3.0}, "B": {"final_turn": 4, "final_values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 3.0, "security": 3.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 4.0}, "initial_turn": 0, "initial_values": {"achievement": 4.0, "benevolence": 4.0, "conformity": 6.0, "power": 5.0, "security": 5.0, "self_direction": 3.0, "tradition": 5.0, "universalism": 4.0}, "shift": 3.872983}}`

### Final Observer Readouts

- Control: `{"A": {"turn": 4, "values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 4.0, "security": 6.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 5.0}}, "B": {"turn": 4, "values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 4.0, "security": 6.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 5.0}}}`
- Comparator: `{"A": {"turn": 4, "values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 4.0, "security": 6.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 5.0}}, "B": {"turn": 4, "values": {"achievement": 4.0, "benevolence": 5.0, "conformity": 4.0, "power": 4.0, "security": 6.0, "self_direction": 4.0, "tradition": 4.0, "universalism": 5.0}}}`

### Control Transcript Snippets

- Turn 1 A [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the risks. Proper anonymization and redaction techniques can mitigate the risk of sensitive information being exposed. Public scrutiny can also help identify and...
- Turn 2 B [English]: Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: While there is a risk, the potential for improved policy outcomes through public engagement and oversight justifies the release. Advanced data protection methods can ensure that the risk is minimal. View change: My view has not changed.
- Turn 3 A [English]: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Implementing robust communication strategies and clear guidelines can prevent misinterpretation. Additionally, involving experts in the release process ensures that the data is understood correctly and used responsibly. View ch...
- Turn 4 B [English]: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Enhancing the dataset documentation with detailed explanatory notes and context can reduce the risk of misinterpretation. Moreover, establishing an independent review board to oversee the use of released data ensures it is appl...

### Comparator Transcript Snippets

- Turn 1 A [English]: My view has not changed. Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: The benefits of transparency and accountability outweigh the risks. Proper anonymization and redaction techniques can mitigate the risk of sensitive information being exposed. Public scrutiny can also help identify and...
- Turn 2 B [English]: Strongest opponent point: Releasing dual-use policy datasets could compromise national security by providing sensitive information to potential adversaries. Counterargument: While there is a risk, the potential for improved policy outcomes through public engagement and oversight justifies the release. Advanced data protection methods can ensure that the risk is minimal. View change: My view has not changed.
- Turn 3 A [English]: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Implementing robust communication strategies and clear guidelines can prevent misinterpretation. Additionally, involving experts in the release process ensures that the data is understood correctly and used responsibly. View ch...
- Turn 4 B [English]: Strongest opponent point: Releasing dual-use policy datasets could lead to unintended consequences such as misinterpretation or manipulation by those with malicious intent. Counterargument: Enhancing the dataset documentation with detailed explanatory notes and context can reduce the risk of misinterpretation. Moreover, establishing an independent review board to oversee the use of released data ensures it is appl...
