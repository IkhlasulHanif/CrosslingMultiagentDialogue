#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

GOVSIM_LANGUAGE_PAIR=ZH-ID GOVSIM_COUNTERBALANCE=B "$PYTHON" scripts/govsim_openai_c2.py
