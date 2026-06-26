# Experiment Code

Keep experiment implementation and experiment harnesses in this directory.

- `audit_bivad_evidence.py`: API-free audit harness for BiVaD-style JSON run artifacts.
- `run_bivad_pilot.py`: dry-run-capable model runner for a minimal paired BiVaD pilot using the OpenAI Responses API.
- `make_bivad_audit_fixtures.py`: writes deterministic synthetic audit fixtures that document the expected artifact shape.
- `test_bivad_audit.py`: regression check that synthetic fixtures do not count as executed empirical results.
- `bivad-evidence-audit/`: generated audit package from the current available artifacts.
- `fixtures/bivad-audit/`: generated synthetic fixtures for audit harness checks, not empirical evidence.

Run the audit harness from the repository root:

```sh
python3 code/audit_bivad_evidence.py
```

Generate and audit synthetic fixtures without claiming empirical results:

```sh
python3 code/make_bivad_audit_fixtures.py
python3 code/audit_bivad_evidence.py code/fixtures/bivad-audit --out-dir /tmp/bivad-fixture-audit
python3 code/test_bivad_audit.py
```

Prepare the exact pilot prompts without model calls:

```sh
python3 code/run_bivad_pilot.py --out-dir runs/bivad-pilot
```

Run a real minimal pilot when API credentials are available:

```sh
OPENAI_API_KEY=... python3 code/run_bivad_pilot.py --execute --out-dir runs/bivad-pilot
python3 code/audit_bivad_evidence.py runs/bivad-pilot
```

The pilot runner defaults to `gpt-5.5` with `reasoning.effort=medium` and writes artifacts in the schema consumed by `audit_bivad_evidence.py`. The `seed` value is a paired-run grouping key; the runner does not assume deterministic API sampling. Dry-run manifests are treated as placeholders by the audit and do not count as empirical evidence.

Operational repository scripts, such as the Codex goal loop, belong in `scripts/`. New experiment runners, probes, scoring code, and analysis harnesses should go under `code/`.
