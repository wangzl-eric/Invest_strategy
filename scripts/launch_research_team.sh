#!/bin/bash
# Launch Zelin Investment Research team via agent-deck
# Usage: ./scripts/launch_research_team.sh [strategy_name] [researcher]
# Example: ./scripts/launch_research_team.sh fx_carry_momentum marco

set -euo pipefail

STRATEGY_NAME="${1:-}"
RESEARCHER="${2:-elena}"
PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/research_team.sh"

if [ -z "$STRATEGY_NAME" ]; then
  echo "Usage: $0 <strategy_name> [researcher: elena|marco]"
  echo "Example: $0 fx_carry_momentum marco"
  exit 1
fi

case "$RESEARCHER" in
  elena|marco) ;;
  *)
    echo "Invalid researcher: $RESEARCHER"
    echo "Expected one of: elena, marco"
    exit 1
    ;;
esac

RESEARCHER_TOOL="claude"
RESEARCHER_WRAPPER="$(claude_wrapper_for_agent "$RESEARCHER")"
RESEARCHER_COMMAND="$(claude_command_for_agent "$RESEARCHER")"
CEREBRO_TOOL="claude"
CEREBRO_WRAPPER="$(claude_wrapper_for_agent "cerebro")"
CEREBRO_COMMAND="$(claude_command_for_agent "cerebro")"
PM_TOOL="claude"
PM_WRAPPER="$(claude_wrapper_for_agent "pm")"
PM_COMMAND="$(claude_command_for_agent "pm")"
DEV_TOOL="claude"
DEV_WRAPPER="$(claude_wrapper_for_agent "dev")"
DEV_COMMAND="$(claude_command_for_agent "dev")"
DATA_TOOL="claude"
DATA_WRAPPER="$(claude_wrapper_for_agent "data")"
DATA_COMMAND="$(claude_command_for_agent "data")"
CODEX_TOOL="codex"
CODEX_WRAPPER="$(codex_wrapper)"
CODEX_COMMAND="$(codex_command)"

ensure_research_session() {
  local title="$1"
  local tool="$2"
  local wrapper="$3"
  local message="$4"
  shift 4

  $AD add -t "$title" -g research -c "$tool" -wrapper "$wrapper" "$@" "$PROJECT_DIR" >/dev/null 2>&1 || true
  $AD session set "$title" tool "$tool" >/dev/null 2>&1 || true
  $AD session set "$title" command "$tool" >/dev/null 2>&1 || true
  $AD session set "$title" wrapper "$wrapper" >/dev/null 2>&1 || true
  $AD session restart "$title" >/dev/null 2>&1 || $AD session start "$title" >/dev/null 2>&1 || true
  $AD session send "$title" "$message" --no-wait -q >/dev/null 2>&1 || true
}

echo "=== Launching Research Team ==="
echo "Strategy: $STRATEGY_NAME"
echo "Lead researcher: $RESEARCHER"
echo "Project: $PROJECT_DIR"
echo "Models:"
echo "  $RESEARCHER: $(effective_claude_agent_model "$RESEARCHER") (override: $(agent_model_override_var_name "$RESEARCHER"))"
echo "  cerebro: $(effective_claude_agent_model "cerebro") (override: $(agent_model_override_var_name "cerebro"))"
echo "  pm: $(effective_claude_agent_model "pm") (override: $(agent_model_override_var_name "pm"))"
echo "  dev: $(effective_claude_agent_model "dev") (override: $(agent_model_override_var_name "dev"))"
echo "  data: $(effective_claude_agent_model "data") (override: $(agent_model_override_var_name "data"))"
echo "  codex-runner: $(effective_codex_model) (override: RESEARCH_CODEX_MODEL)"
echo ""

# 1. Ensure conductor is running
echo "[1/4] Checking conductor..."
$AD conductor status research 2>/dev/null || {
  echo "Starting conductor session..."
  $AD session start conductor-research
}

# 2. Launch researcher with worktree
echo "[2/4] Launching research sessions..."

ensure_research_session \
  "research-$RESEARCHER" \
  "$RESEARCHER_TOOL" \
  "$RESEARCHER_WRAPPER" \
  "You are $RESEARCHER. Read .claude/agents/$RESEARCHER.md for your full identity. Begin research on: $STRATEGY_NAME. Start by requesting a Cerebro literature briefing." \
  --worktree "research/$RESEARCHER" -b

# 3. Launch support agents
ensure_research_session \
  "research-cerebro" \
  "$CEREBRO_TOOL" \
  "$CEREBRO_WRAPPER" \
  "You are Cerebro. Read .claude/agents/cerebro.md for your identity. Stand by for briefing requests on: $STRATEGY_NAME"

ensure_research_session \
  "research-pm" \
  "$PM_TOOL" \
  "$PM_WRAPPER" \
  "You are PM. Read .claude/agents/pm.md for your identity. Prepare to review strategy: $STRATEGY_NAME"

ensure_research_session \
  "research-dev" \
  "$DEV_TOOL" \
  "$DEV_WRAPPER" \
  "You are Dev. Read .claude/agents/dev.md for your identity. Stand by for code review requests." \
  --worktree "research/dev" -b

ensure_research_session \
  "research-data" \
  "$DATA_TOOL" \
  "$DATA_WRAPPER" \
  "You are Data. Read .claude/agents/data.md for your identity. Assess data coverage and pipeline requirements for strategy: $STRATEGY_NAME. Report any coverage gaps to the researcher." \
  --worktree "research/data" -b

# 4. Launch Codex as backtest runner & execution assistant
echo "[3/5] Launching Codex execution assistant..."
$AD add \
  -c "$CODEX_TOOL" -wrapper "$CODEX_WRAPPER" -t "codex-runner" -g research \
  "$PROJECT_DIR" 2>/dev/null || true
$AD session set "codex-runner" tool "$CODEX_TOOL" 2>/dev/null || true
$AD session set "codex-runner" command "$CODEX_TOOL" 2>/dev/null || true
$AD session set "codex-runner" wrapper "$CODEX_WRAPPER" 2>/dev/null || true

# 5. Attach MCPs
echo "[4/5] Attaching shared MCPs..."
$AD mcp attach research-cerebro exa 2>/dev/null || true
for session in research-$RESEARCHER research-cerebro research-pm research-dev research-data; do
  $AD mcp attach "$session" filesystem 2>/dev/null || true
done

echo ""
echo "=== Research Team Ready ==="
echo "Open TUI:  agent-deck"
echo "Group:     research"
echo "Sessions:  research-$RESEARCHER, research-cerebro, research-pm, research-dev, research-data, codex-runner"
echo ""
echo "Researcher:  $RESEARCHER  — leads strategy research on $STRATEGY_NAME"
echo "Cerebro:     literature briefing & contradiction search (blocks researcher + PM)"
echo "Data:        coverage gap analysis & pipeline readiness (blocks researcher)"
echo "Dev:         backtesting framework & code review"
echo "PM:          strategy gatekeeper — 11-gate challenge loop"
echo "Codex:       backtest execution, parameter sweeps (Path B only)"
echo ""
echo "Tip: run ./scripts/show_agent_team.sh to inspect defaults and override points."
echo ""
echo "[5/5] Team ready. The researcher has been prompted to begin work on: $STRATEGY_NAME"
