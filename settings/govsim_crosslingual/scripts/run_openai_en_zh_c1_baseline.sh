#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

GOVSIM_LANGUAGE_PAIR=EN-ZH GOVSIM_CONDITION=C1 GOVSIM_LANGUAGE=ZH "$PYTHON" scripts/govsim_openai_baseline.py
