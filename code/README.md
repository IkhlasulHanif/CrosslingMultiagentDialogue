# Experiment Code

Keep experiment implementation and experiment harnesses in this directory.

- `audit_bivad_evidence.py`: API-free audit harness for BiVaD-style JSON run artifacts.
- `bivad-evidence-audit/`: generated audit package from the current available artifacts.

Run the audit harness from the repository root:

```sh
python3 code/audit_bivad_evidence.py
```

Operational repository scripts, such as the Codex goal loop, belong in `scripts/`. New experiment runners, probes, scoring code, and analysis harnesses should go under `code/`.
