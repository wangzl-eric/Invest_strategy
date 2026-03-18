#!/bin/bash
# Launch Zelin Investment Research team via agent-deck
# Usage: ./scripts/launch_research_team.sh [strategy_name] [researcher]
# Example: ./scripts/launch_research_team.sh fx_carry_momentum marco

set -euo pipefail

STRATEGY_NAME="${1:-}"
RESEARCHER="${2:-elena}"
PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AD="$HOME/.local/bin/agent-deck"

if [ -z "$STRATEGY_NAME" ]; then
  echo "Usage: $0 <strategy_name> [researcher: elena|marco]"
  echo "Example: $0 fx_carry_momentum marco"
  exit 1
fi

echo "=== Launching Research Team ==="
echo "Strategy: $STRATEGY_NAME"
echo "Lead researcher: $RESEARCHER"
echo "Project: $PROJECT_DIR"
echo ""

# 1. Ensure conductor is running
echo "[1/4] Checking conductor..."
$AD conductor status research 2>/dev/null || {
  echo "Starting conductor session..."
  $AD session start conductor-research
}

# 2. Launch researcher with worktree
echo "[2/4] Launching research sessions..."

$AD launch "$PROJECT_DIR" \
  -c claude -t "research-$RESEARCHER" -g research \
  --worktree "research/$RESEARCHER" -b \
  -m "You are $RESEARCHER. Read .claude/agents/$RESEARCHER.md for your full identity. Begin research on: $STRATEGY_NAME. Start by requesting a Cerebro literature briefing."

# 3. Launch support agents
$AD launch "$PROJECT_DIR" \
  -c claude -t "research-cerebro" -g research \
  -m "You are Cerebro. Read .claude/agents/cerebro.md for your identity. Stand by for briefing requests on: $STRATEGY_NAME"

$AD launch "$PROJECT_DIR" \
  -c claude -t "research-pm" -g research \
  -m "You are PM. Read .claude/agents/pm.md for your identity. Prepare to review strategy: $STRATEGY_NAME"

$AD launch "$PROJECT_DIR" \
  -c claude -t "research-dev" -g research \
  --worktree "research/dev" -b \
  -m "You are Dev. Read .claude/agents/dev.md for your identity. Stand by for code review requests."

# 4. Launch Codex as backtest runner & execution assistant
echo "[3/4] Launching Codex execution assistant..."
$AD add "$PROJECT_DIR" \
  -c codex -t "codex-runner" -g research 2>/dev/null || true

# 5. Attach MCPs
echo "[4/4] Attaching shared MCPs..."
$AD mcp attach research-cerebro exa 2>/dev/null || true
for session in research-$RESEARCHER research-cerebro research-pm research-dev; do
  $AD mcp attach "$session" filesystem 2>/dev/null || true
done

echo ""
echo "=== Research Team Ready ==="
echo "Open TUI:  agent-deck"
echo "Group:     research"
echo "Sessions:  research-$RESEARCHER, research-cerebro, research-pm, research-dev, codex-runner"
echo ""
echo "The researcher has been prompted to begin work on: $STRATEGY_NAME"
