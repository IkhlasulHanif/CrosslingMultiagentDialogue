#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
repo_root="$(git rev-parse --show-toplevel)"

if [[ ! -f STATE.yaml ]]; then
  make bootstrap
fi

while true; do
  if ! next="$(python3 scripts/state.py next)"; then
    mkdir -p reports
    {
      echo "# DONE"
      echo
      echo "All STATE.yaml tasks are done."
    } > reports/DONE.md
    git -C "$repo_root" add -- xduetpd
    git -C "$repo_root" commit -m "[done] X-DuET-PD loop complete" || true
    git -C "$repo_root" push
    exit 0
  fi

  task_id="$(printf '%s\n' "$next" | sed -n '1p')"
  make_cmd="$(printf '%s\n' "$next" | sed -n '2p')"
  check_cmd="$(printf '%s\n' "$next" | sed -n '3p')"
  status="$(printf '%s\n' "$next" | sed -n '4p')"

  if [[ "$status" == "blocked" ]]; then
    mkdir -p "reports/blockers"
    blocker="reports/blockers/${task_id}.md"
    if [[ ! -f "$blocker" ]]; then
      {
        echo "# Blocker ${task_id}"
        echo
        echo "- what blocked: task already marked blocked in STATE.yaml"
        echo "- why: no further automated progress is allowed"
        echo "- smallest human question: what should change before retrying this task?"
      } > "$blocker"
    fi
    git -C "$repo_root" add -- xduetpd
    git -C "$repo_root" commit -m "[${task_id}] blocked" || true
    git -C "$repo_root" push
    exit 1
  fi

  python3 scripts/state.py mark --id "$task_id" --status doing
  attempts=0
  until [[ "$attempts" -ge 3 ]]; do
    attempts=$((attempts + 1))
    if make $make_cmd && make "$check_cmd"; then
      evidence="reports/evidence/${task_id}/"
      python3 scripts/state.py mark --id "$task_id" --status done --evidence "$evidence"
      git -C "$repo_root" add -- xduetpd
      git -C "$repo_root" commit -m "[${task_id}] ${make_cmd}"
      git -C "$repo_root" push
      break
    fi
    if [[ "$attempts" -ge 3 ]]; then
      mkdir -p reports/blockers
      {
        echo "# Blocker ${task_id}"
        echo
        echo "- what blocked: make target or acceptance check failed after 3 attempts"
        echo "- why: automated retry budget exhausted"
        echo "- smallest human question: should this task be debugged further, relaxed, or marked as a substantive finding?"
      } > "reports/blockers/${task_id}.md"
      python3 scripts/state.py mark --id "$task_id" --status blocked
      git -C "$repo_root" add -- xduetpd
      git -C "$repo_root" commit -m "[${task_id}] blocked"
      git -C "$repo_root" push
      exit 1
    fi
  done
done
