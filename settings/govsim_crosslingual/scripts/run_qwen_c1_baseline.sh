#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

GOVSIM_CONDITION=C1 GOVSIM_LANGUAGE=ID "$PYTHON" scripts/govsim_qwen_c0_baseline.py
