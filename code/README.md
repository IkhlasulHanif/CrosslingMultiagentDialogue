# Experiment Code

Keep experiment implementation and experiment harnesses in this directory.

- `audit_bivad_evidence.py`: API-free audit harness for BiVaD-style JSON run artifacts.
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

Operational repository scripts, such as the Codex goal loop, belong in `scripts/`. New experiment runners, probes, scoring code, and analysis harnesses should go under `code/`.
