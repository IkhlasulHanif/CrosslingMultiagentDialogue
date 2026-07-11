#!/usr/bin/env bash
# Run a setting-local harness from the workspace root.
# Usage: ./run_setting.sh crosslingual_debate [harness args...]

set -euo pipefail

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "usage: $0 <setting-name> [args...]" >&2
    exit 2
fi

setting="$1"
shift

root="$(cd "$(dirname "$0")" && pwd)"
setting_dir="$root/settings/$setting"
harness="$setting_dir/harness.sh"

if [[ ! -x "$harness" ]]; then
    echo "no executable harness found at $harness" >&2
    exit 1
fi

cd "$setting_dir"
exec ./harness.sh "$@"
