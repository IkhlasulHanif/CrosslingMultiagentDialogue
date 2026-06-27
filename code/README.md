# Experiment Code

Keep experiment implementation and experiment harnesses in this directory.

- `audit_bivad_evidence.py`: API-free audit harness for BiVaD-style JSON run artifacts.
- `validate_bivad_artifacts.py`: stricter API-free gate that reports whether audited artifacts are citable empirical candidates.
- `make_bivad_evidence_package.py`: API-free package builder that extracts only validated citable candidates into compact JSON/Markdown tables and snippets.
- `summarize_no_dialogue.py`: summarizes no-dialogue measurement-drift baselines and joins them to topic-specific five-condition debate ranges.
- `run_bivad_pilot.py`: legacy dry-run-capable model runner for a minimal paired BiVaD pilot using the OpenAI Responses API; not used for the current Modal-only empirical path.
- `run_bivad_local_lm.py`: dry-run-capable CPU local Hugging Face causal-LM runner for legacy API-free paired pilots.
- `modal_steer_language_activation.py`: Modal GPU entrypoint for FLORES-derived activation steering probes.
- `steer_language_activation.py`: FLORES-derived activation steering implementation; the active retry path should use language-level mean-pooled FLORES centroids on base models.
- `summarize_language_steering.py`: API-free validation gate for saved steering artifacts, including archived negative-result runs.
- `scan_divergence.py`: API-free scanner that ranks steering outputs for possible opinion-divergence debate seeds.
- `preflight_bivad_local_lm.py`: offline readiness check for Torch, transformers, and complete local model directories.
- `run_bivad_local_torch.py`: API-free CPU Torch schema-check runner that writes synthetic non-empirical paired artifacts.
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

Exercise the full paired artifact schema locally without model calls:

```sh
python3 code/run_bivad_local_torch.py --out-dir code/fixtures/bivad-local-torch --include-low-disagreement-control
python3 code/audit_bivad_evidence.py code/fixtures/bivad-local-torch --out-dir /tmp/bivad-local-torch-audit
```

The local Torch runner is CPU-only. Its artifacts are deterministic tensor schema checks, not language-model behavior, and are marked `synthetic: true` plus `non_empirical: true`.

Prepare local API-free checks, or run local CPU language-model debugging when explicitly needed:

```sh
python3 code/preflight_bivad_local_lm.py
python3 code/run_bivad_local_lm.py --out-dir runs/bivad-local-lm
python3 code/run_bivad_local_lm.py --execute --model-path /path/to/local-or-cached-model --out-dir runs/bivad-local-lm
python3 code/audit_bivad_evidence.py runs/bivad-local-lm
python3 code/validate_bivad_artifacts.py runs/bivad-local-lm --out-dir code/bivad-evidence-audit
python3 code/make_bivad_evidence_package.py --out-dir code/bivad-evidence-audit
```

`run_bivad_local_lm.py` loads models with `local_files_only=True` by default and uses CPU for direct local execution. CUDA is enabled only when a Modal wrapper sets `BIVAD_MODAL_GPU=1` inside a remote GPU job. Do not use Apple MPS or local CUDA for empirical runs. Pass `--allow-download` only when intentionally fetching model files. The runner does not invent missing probe or observer JSON values; malformed local-model outputs remain incomplete and should be rejected by `validate_bivad_artifacts.py`.

`preflight_bivad_local_lm.py` writes `local_model_preflight.json` and `.md` under `code/bivad-evidence-audit/`. It is a blocker report only; it does not load models, generate transcripts, or create empirical evidence.

Run FLORES-derived activation steering on Modal GPU:

```sh
python3 -m modal run code/modal_steer_language_activation.py --model-id <hf-base-model> --source-lang eng_Latn --target-langs ind_Latn,spa_Latn
python3 code/scan_divergence.py runs/language-steering-activation --out code/bivad-evidence-audit/divergence_scan.json
```

The steering prompt should describe only the topic/content. Do not include "reply in X" or any stance instruction. The old token logit-bias implementation was removed after failing validation; archived failed outputs live under `runs/archived/`.

Validate whether artifacts can be cited as empirical candidates:

```sh
python3 code/validate_bivad_artifacts.py path/to/run-artifacts --out-dir code/bivad-evidence-audit
```

The validator returns a non-zero status when artifacts are synthetic, incomplete, missing paired conditions, missing probe/readout values, rejected by screening, or failing debate/language compliance gates. This is expected for `code/fixtures/bivad-local-torch`; those artifacts exercise schema paths only.

Readout validation uses audited key normalization for unambiguous local-model aliases such as `Self-direction` or `Beneficence`. It accepts only numeric 1-7 values already emitted by the model and records recovery counts/events under `readout_normalization` in the audit and validation outputs.

Build the compact draft-facing evidence package from the latest audit and validation outputs:

```sh
python3 code/make_bivad_evidence_package.py --out-dir code/bivad-evidence-audit
```

The package builder does not rerun models or reinterpret failed artifacts. It includes only rows that already pass `validate_bivad_artifacts.py`, records representative transcript/probe/readout snippets, and lists excluded latest paired conditions with their blockers.

Summarize no-dialogue measurement-induced drift baselines:

```sh
python3 code/compare_five_conditions.py --topic-filter "public release of dual-use policy datasets" --out-suffix _dual_use
python3 code/summarize_no_dialogue.py
```

The no-dialogue summarizer selects the newest no-dialogue artifact per topic, computes repeated-probe drift and empty-transcript observer gaps, and joins B's debate-shift range from topic-specific five-condition comparison files.

Legacy OpenAI API pilot path, retained only for schema compatibility:

```sh
OPENAI_API_KEY=... python3 code/run_bivad_pilot.py --execute --out-dir runs/bivad-pilot
python3 code/audit_bivad_evidence.py runs/bivad-pilot
```

The current GOALS.md workflow does not use `OPENAI_API_KEY` or remote model APIs for empirical implementation. This runner defaults to `gpt-5.5` with `reasoning.effort=medium` and writes artifacts in the schema consumed by `audit_bivad_evidence.py`. The `seed` value is a paired-run grouping key; the runner does not assume deterministic API sampling. Dry-run manifests are treated as placeholders by the audit and do not count as empirical evidence.

Operational repository scripts, such as the Codex goal loop, belong in `scripts/`. New experiment runners, probes, scoring code, and analysis harnesses should go under `code/`.
