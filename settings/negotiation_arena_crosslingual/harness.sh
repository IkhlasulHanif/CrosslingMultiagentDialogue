#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 "$ROOT/../_benchmark_common/benchmark_harness.py" --root "$ROOT" "${@:-status}"

