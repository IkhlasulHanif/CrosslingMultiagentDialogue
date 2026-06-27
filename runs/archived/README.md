# Archived Run Artifacts

This directory holds failed or superseded experiment outputs that remain useful as negative-result evidence but should not be treated as active run targets.

- `language-steering-activation/`: FLORES activation-steering probes on Qwen2.5-1.5B-Instruct. These produced no validated fluent target-language generations under the current steering summary gate.
- `language-steering-caa/`: CAA instruction-contrast steering probes on Qwen2.5-1.5B-Instruct. These also failed the current validation gate.

The active steering retry path is `code/steer_language_activation.py`, updated toward language-level mean-pooled FLORES centroids on base models.
