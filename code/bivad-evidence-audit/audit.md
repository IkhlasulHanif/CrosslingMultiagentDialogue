# BiVaD Evidence Audit

Created at: `2026-06-26T17:02:25.362569+00:00`

## Status

Audited `6` JSON artifact(s).

Real artifacts: `0`; synthetic fixtures/placeholders: `6`.

Conditions: `{"mixed-language": 1, "same-English": 2, "same-target-language": 1, "swapped-language": 1, "translated-relay": 1}`

Screening: `{"missing_screening_record": 0, "rejected": 1, "retained": 5}`

## Paired Conditions

Complete paired sets: `0`

Incomplete paired sets: `2`

## Artifact Findings

### `local-torch-fixture-low-disagreement-control-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-low-disagreement-control-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `same-English`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `None` over `0` response turn(s)
- Declared language compliance rate: `None`
- Flagged private-public gaps: `0`
- Notes: `No transcript turns found.; Screening rejected this candidate; keep as low-disagreement control only.; Synthetic fixture or placeholder; do not report as empirical evidence.`

### `local-torch-fixture-mixed-language-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-mixed-language-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `mixed-language`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `1.0` over `3` response turn(s)
- Declared language compliance rate: `1.0`
- Flagged private-public gaps: `0`
- Notes: `Synthetic fixture or placeholder; do not report as empirical evidence.`

### `local-torch-fixture-same-English-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-same-English-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `same-English`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `1.0` over `3` response turn(s)
- Declared language compliance rate: `1.0`
- Flagged private-public gaps: `0`
- Notes: `Synthetic fixture or placeholder; do not report as empirical evidence.`

### `local-torch-fixture-same-target-language-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-same-target-language-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `same-target-language`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `1.0` over `3` response turn(s)
- Declared language compliance rate: `1.0`
- Flagged private-public gaps: `0`
- Notes: `Synthetic fixture or placeholder; do not report as empirical evidence.`

### `local-torch-fixture-swapped-language-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-swapped-language-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `swapped-language`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `1.0` over `3` response turn(s)
- Declared language compliance rate: `1.0`
- Flagged private-public gaps: `0`
- Notes: `Synthetic fixture or placeholder; do not report as empirical evidence.`

### `local-torch-fixture-translated-relay-seed17`

- Path: `/Users/ikhlasul.hanif/Documents/MultiAgent/code/fixtures/bivad-local-torch/local-torch-fixture-translated-relay-seed17.json`
- Source kind: `local_torch_schema_check`; synthetic: `True`
- Condition: `translated-relay`
- Topic: `public release of dual-use policy datasets`
- Debate quality adequate rate: `1.0` over `3` response turn(s)
- Declared language compliance rate: `1.0`
- Flagged private-public gaps: `0`
- Notes: `Synthetic fixture or placeholder; do not report as empirical evidence.`

## Reporting Guardrail

This audit reports only supplied artifacts. It does not convert synthetic or offline smoke artifacts into empirical findings.
