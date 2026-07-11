#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

GOVSIM_CONDITION=C0 GOVSIM_LANGUAGE=EN "$PYTHON" scripts/govsim_openai_baseline.py
