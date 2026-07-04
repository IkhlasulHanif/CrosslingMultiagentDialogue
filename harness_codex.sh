#!/usr/bin/env bash
# Codex backend entry point — same harness, same state, different executor.
# Usage: bash harness_codex.sh
#
# Requires: `codex` CLI on PATH and a working Codex login.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Load an OpenAI key if present, but do not require one. The Codex CLI can use
# its own stored login.
if [[ -f "$ROOT/secrets/openai.env" ]]; then
    set -a; source "$ROOT/secrets/openai.env"; set +a
fi

if ! command -v codex &>/dev/null; then
    echo "[harness_codex] ERROR: 'codex' not found on PATH. Install with: npm i -g @openai/codex"
    exit 1
fi

# Override backend before harness.sh sets its defaults
export BACKEND="codex"
export CODEX_BYPASS_APPROVALS_AND_SANDBOX="${CODEX_BYPASS_APPROVALS_AND_SANDBOX:-1}"
export GIT_EDITOR="${GIT_EDITOR:-true}"
export VISUAL="${VISUAL:-true}"
export EDITOR="${EDITOR:-true}"

# Use a separate state file so Codex and Claude runs don't clobber each other
export STATE="$ROOT/.harness_state_codex"

# Run the shared harness logic
exec bash "$ROOT/harness.sh"
