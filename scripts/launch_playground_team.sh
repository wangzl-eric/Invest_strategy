#!/bin/bash
# Launch the playground paper-reading and knowledge-expansion team via agent-deck.
# Usage: ./scripts/launch_playground_team.sh [focus]

set -euo pipefail

FOCUS="${1:-paper reading and knowledge scope expansion}"
PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDUCTOR_PROMPT="$PROJECT_DIR/book_notes/playground/agents/conductor.md"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/playground_team.sh"

EXPLORER_TOOL="$(playground_tool_for_agent "explorer")"
EXPLORER_WRAPPER="$(playground_wrapper_for_agent "explorer")"
EXPLORER_COMMAND="$(playground_command_for_agent "explorer")"
TUTOR_TOOL="$(playground_tool_for_agent "tutor")"
TUTOR_WRAPPER="$(playground_wrapper_for_agent "tutor")"
TUTOR_COMMAND="$(playground_command_for_agent "tutor")"
CEREBRO_TOOL="$(playground_tool_for_agent "cerebro")"
CEREBRO_WRAPPER="$(playground_wrapper_for_agent "cerebro")"
CEREBRO_COMMAND="$(playground_command_for_agent "cerebro")"
DEV_TOOL="$(playground_tool_for_agent "dev")"
DEV_WRAPPER="$(playground_wrapper_for_agent "dev")"
DEV_COMMAND="$(playground_command_for_agent "dev")"

ensure_playground_session() {
  local title="$1"
  local tool="$2"
  local wrapper="$3"
  local message="$4"
  shift 4

  $AD add -t "$title" -g playground -c "$tool" -wrapper "$wrapper" "$@" "$PROJECT_DIR" >/dev/null 2>&1 || true
  $AD session set "$title" tool "$tool" >/dev/null 2>&1 || true
  $AD session set "$title" command "$tool" >/dev/null 2>&1 || true
  $AD session set "$title" wrapper "$wrapper" >/dev/null 2>&1 || true
  $AD session restart "$title" >/dev/null 2>&1 || $AD session start "$title" >/dev/null 2>&1 || true
  if [ -n "$message" ]; then
    $AD session send "$title" "$message" --no-wait -q >/dev/null 2>&1 || true
  fi
}

echo "=== Launching Playground Team ==="
echo "Focus: $FOCUS"
echo "Project: $PROJECT_DIR"
echo "Models:"
echo "  explorer: $(effective_playground_agent_runtime "explorer") / $(effective_playground_agent_model "explorer")"
echo "  tutor: $(effective_playground_agent_runtime "tutor") / $(effective_playground_agent_model "tutor")"
echo "  cerebro: $(effective_playground_agent_runtime "cerebro") / $(effective_playground_agent_model "cerebro")"
echo "  dev: $(effective_playground_agent_runtime "dev") / $(effective_playground_agent_model "dev")"
echo ""

echo "[1/5] Ensuring playground conductor is registered..."
$AD conductor status playground >/dev/null 2>&1 || \
  $AD conductor setup playground \
    -description "Playground paper-reading and knowledge-expansion team" \
    -instructions-md "$CONDUCTOR_PROMPT" >/dev/null

echo "[2/5] Ensuring playground group exists..."
$AD group create playground >/dev/null 2>&1 || true

echo "[3/5] Starting playground conductor..."
$AD session start conductor-playground >/dev/null 2>&1 || true

echo "[4/5] Launching playground sessions..."
ensure_playground_session \
  "playground-explorer" \
  "$EXPLORER_TOOL" \
  "$EXPLORER_WRAPPER" \
  "You are Explorer. Read book_notes/playground/agents/explorer.md for your identity. Focus area: $FOCUS. Start by surfacing open hypotheses from the KBs and propose 3 reading-led playground study directions." \
  --worktree "playground-explorer" -b

ensure_playground_session \
  "playground-tutor" \
  "$TUTOR_TOOL" \
  "$TUTOR_WRAPPER" \
  "You are Tutor. Read book_notes/playground/agents/tutor.md for your identity. Focus area: $FOCUS. Stand by to explain papers, methods, and study workflows in the playground." \
  --worktree "playground-tutor" -b

ensure_playground_session \
  "playground-cerebro" \
  "$CEREBRO_TOOL" \
  "$CEREBRO_WRAPPER" \
  "" \
  --worktree "playground-cerebro" -b

ensure_playground_session \
  "playground-dev" \
  "$DEV_TOOL" \
  "$DEV_WRAPPER" \
  "You are Dev. Read book_notes/playground/agents/dev.md for your identity. Focus area: $FOCUS. Stand by to create notebook scaffolds, lightweight utilities, and reproducible paper-reading support inside the playground." \
  --worktree "playground-dev" -b

echo "[5/5] Attaching MCPs..."
for session in playground-explorer playground-tutor playground-cerebro playground-dev; do
  $AD mcp attach "$session" filesystem 2>/dev/null || true
done
$AD mcp attach playground-explorer exa 2>/dev/null || true
$AD mcp attach playground-cerebro exa 2>/dev/null || true

echo ""
echo "=== Playground Team Ready ==="
echo "Open TUI:  agent-deck"
echo "Group:     playground"
echo "Sessions:  playground-explorer, playground-tutor, playground-cerebro, playground-dev, conductor-playground"
echo ""
echo "Explorer:  study ideas and KB-driven hypotheses"
echo "Tutor:     paper interpretation and learning guidance"
echo "Cerebro:   reading queue, summaries, adjacent-literature expansion"
echo "Dev:       notebook scaffolds and reproducible study support"
echo ""
echo "Tip: run ./scripts/show_playground_team.sh to inspect defaults and override points."
