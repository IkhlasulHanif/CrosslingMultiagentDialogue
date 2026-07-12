#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

"$PYTHON" code/capability_floor.py \
  --root . \
  --pair EN-ID \
  --c0-result artifacts/results/govsim_c0_openai_baseline_20260712T174917Z.json \
  --c1-result artifacts/results/govsim_c1_openai_baseline_20260712T174935Z.json \
  --out artifacts/logs/g2_en_id_openai_capability_floor_20260712T174935Z.json
