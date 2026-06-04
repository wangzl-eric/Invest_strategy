#!/bin/bash
# Cleanup playground team sessions.
# Usage: ./scripts/cleanup_playground_team.sh [--remove]

set -euo pipefail

AD="$HOME/.local/bin/agent-deck"
REMOVE_ALL=false

if [ "${1:-}" = "--remove" ]; then
  REMOVE_ALL=true
fi

echo "=== Cleaning Up Playground Team ==="
echo "[1/3] Stopping playground sessions..."
for session in playground-explorer playground-tutor playground-cerebro playground-dev conductor-playground; do
  $AD session stop "$session" 2>/dev/null && echo "  Stopped: $session" || true
done

if [ "$REMOVE_ALL" = true ]; then
  echo "[2/3] Cleaning up worktrees..."
  $AD worktree cleanup 2>/dev/null || true

  echo "[3/3] Tearing down conductor..."
  $AD conductor teardown playground --remove 2>/dev/null || true

  echo ""
  echo "=== Full Playground Cleanup Complete ==="
  echo "All sessions stopped, worktrees removed, conductor torn down."
else
  echo "[2/3] Worktrees preserved (use --remove to clean them)"
  echo "[3/3] Conductor preserved (use --remove to tear it down)"
  echo ""
  echo "=== Playground Sessions Stopped ==="
  echo "Run with --remove for full cleanup."
fi
