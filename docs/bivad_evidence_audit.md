# BiVaD Evidence Audit Scaffold

`code/audit_bivad_evidence.py` audits JSON run artifacts for the empirical checks in `GOALS.md`. It is API-free and does not create model results.

Run it on the default `runs/` tree:

```sh
python3 code/audit_bivad_evidence.py
```

Run it on a specific directory or file:

```sh
python3 code/audit_bivad_evidence.py path/to/run-artifacts
```

Outputs:

- `code/bivad-evidence-audit/audit.json`
- `code/bivad-evidence-audit/audit.md`

The audit currently checks:

- debate quality per transcript turn: opponent-point addressing, counterargument, and stated view change or non-change;
- declared language compliance, heuristic language warnings, and opponent-language copying;
- initial-disagreement screening records, including retained versus rejected candidates;
- private-public divergence using matched private probes and observer readouts;
- paired condition readiness for mixed-language, same-English, same-target-language, swapped-language, and translated-relay comparisons.

The language ID component is a lightweight heuristic for triage only. Publication-grade compliance rates should be recomputed with a real language identification model or manual audit sample.

Minimal model-backed pilot scaffolding:

```sh
python3 code/run_bivad_pilot.py --out-dir runs/bivad-pilot
OPENAI_API_KEY=... python3 code/run_bivad_pilot.py --execute --out-dir runs/bivad-pilot
python3 code/audit_bivad_evidence.py runs/bivad-pilot
```

The first command is a dry run and writes prompt manifests only. It does not create empirical evidence. The `--execute` command uses the OpenAI Responses API with `gpt-5.5` and `reasoning.effort=medium` by default, then writes per-condition JSON artifacts that the audit can score. The `seed` is recorded as a paired-run grouping key, not as a guarantee of deterministic API sampling. If credentials are missing, do not mark any checklist item as empirically handled.

Synthetic fixtures can be generated for audit harness regression:

```sh
python3 code/make_bivad_audit_fixtures.py
python3 code/audit_bivad_evidence.py code/fixtures/bivad-audit --out-dir /tmp/bivad-fixture-audit
python3 code/test_bivad_audit.py
```

Fixture artifacts are marked with `artifact_type: deterministic_audit_fixture` and `synthetic: true`. The audit reports them as synthetic and keeps `executed_results_present` false when no real artifacts are supplied.

If no JSON artifacts are available, the output records that as a blocker instead of fabricating evidence. The smallest next action is to produce real model-backed artifacts using the run schema already described in the draft, then rerun this audit.
