#!/bin/bash
# Cleanup Zelin Investment Research team sessions
# Usage: ./scripts/cleanup_research_team.sh [--remove]
#   --remove: also remove conductor and worktrees (default: just stop sessions)

set -euo pipefail

AD="$HOME/.local/bin/agent-deck"
REMOVE_ALL=false

if [ "${1:-}" = "--remove" ]; then
  REMOVE_ALL=true
fi

echo "=== Cleaning Up Research Team ==="

# 1. Stop all research group sessions
echo "[1/3] Stopping research sessions..."
for session in research-marco research-elena research-dev research-pm research-cerebro codex-runner; do
  $AD session stop "$session" 2>/dev/null && echo "  Stopped: $session" || true
done

# 2. Handle worktrees
if [ "$REMOVE_ALL" = true ]; then
  echo "[2/3] Cleaning up worktrees..."
  $AD worktree cleanup 2>/dev/null || true

  echo "[3/3] Tearing down conductor..."
  $AD conductor teardown research --remove 2>/dev/null || true

  echo ""
  echo "=== Full Cleanup Complete ==="
  echo "All sessions stopped, worktrees removed, conductor torn down."
else
  echo "[2/3] Worktrees preserved (use --remove to clean them)"
  echo "[3/3] Conductor preserved (use --remove to tear down)"
  echo ""
  echo "=== Sessions Stopped ==="
  echo "Worktrees and conductor are still available for resume."
  echo "Run with --remove for full cleanup."
fi
