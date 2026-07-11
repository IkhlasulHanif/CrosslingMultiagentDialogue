#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/validate_smoke_plan.py"
python3 "$ROOT/scripts/bringup_check.py" --write-event
python3 "$ROOT/scripts/validate_offer_parser.py"
python3 "$ROOT/scripts/validate_process_metrics.py"
python3 "$ROOT/scripts/run_c0_smoke.py"
