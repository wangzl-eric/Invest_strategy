#!/usr/bin/env bash
# Backtest-engine change guardrail — PreToolUse advisory (non-blocking).
#
# Reads the tool-call JSON on stdin. When the file being edited is part of the
# backtest engine, it injects a policy reminder into Claude's context so engine
# changes stay minimal, backward-compatible, and non-redundant. It never blocks
# the edit (always exits 0; emits context only on a match).
set -uo pipefail

input="$(cat)"
f="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"

case "$f" in
  *alpha_research/backtests/* | *alpha_research/review/engine.py | *alpha_research/review/validation.py)
    msg="BACKTEST-ENGINE GUARDRAIL — you are editing the backtest engine. Keep the change MINIMAL and BACKWARD-COMPATIBLE: preserve the weights contract and the public signatures (run_weights_backtest; backtest_weights / backtest_strategy; the Strategy / Context API). REUSE the existing cost / stats / calendar / performance utilities instead of duplicating them. Do NOT add a parallel or redundant engine or code path — edit in place rather than adding new modules. Any behavior change MUST (1) keep no-look-ahead intact (strategies see only history up to the decision bar) and (2) reconcile PnL with the existing engines via alpha_research.backtests.equivalence.compare_engines. Keep it compact, with no redundancy."
    jq -n --arg m "$msg" \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", additionalContext: $m}}'
    ;;
esac

exit 0
