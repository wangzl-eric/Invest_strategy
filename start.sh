#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# IBKR Portfolio Analytics — start backend + frontend
# Usage:  ./start.sh          (start both)
#         ./start.sh backend  (backend only)
#         ./start.sh frontend (frontend only)
# ──────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONDA_ENV="ibkr-analytics"
BACKEND_PORT=8000
FRONTEND_PORT=8050

export PYTHONPATH="$PROJECT_DIR:${PYTHONPATH:-}"

# ── colours ──────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${BLUE}[launcher]${NC} $*"; }
ok()   { echo -e "${GREEN}[launcher]${NC} $*"; }
warn() { echo -e "${YELLOW}[launcher]${NC} $*"; }
err()  { echo -e "${RED}[launcher]${NC} $*"; }

# ── activate conda ───────────────────────────────────────
activate_conda() {
    if [ -z "${CONDA_EXE:-}" ]; then
        # Try common conda locations
        for p in "$HOME/opt/anaconda3" "$HOME/anaconda3" "$HOME/miniconda3" "/opt/homebrew/Caskroom/miniconda/base"; do
            if [ -f "$p/etc/profile.d/conda.sh" ]; then
                source "$p/etc/profile.d/conda.sh"
                break
            fi
        done
    else
        source "$(dirname "$(dirname "$CONDA_EXE")")/etc/profile.d/conda.sh"
    fi

    if command -v conda &>/dev/null; then
        conda activate "$CONDA_ENV" 2>/dev/null || {
            warn "Conda env '$CONDA_ENV' not found — using current Python"
        }
    else
        warn "conda not found — using current Python ($(python3 --version 2>&1))"
    fi
}

# ── cleanup on exit ──────────────────────────────────────
PIDS=()
cleanup() {
    log "Shutting down…"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            wait "$pid" 2>/dev/null || true
        fi
    done
    ok "All services stopped."
}
trap cleanup EXIT INT TERM

# ── launch helpers ───────────────────────────────────────
start_backend() {
    log "Starting backend (FastAPI) on port $BACKEND_PORT …"
    cd "$PROJECT_DIR"
    python -m uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
    PIDS+=($!)
    ok "Backend PID: ${PIDS[-1]}"
}

start_frontend() {
    log "Starting frontend (Dash) on port $FRONTEND_PORT …"
    cd "$PROJECT_DIR"
    python frontend/app.py &
    PIDS+=($!)
    ok "Frontend PID: ${PIDS[-1]}"
}

# ── main ─────────────────────────────────────────────────
activate_conda

MODE="${1:-all}"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   IBKR Portfolio Analytics Platform          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""

case "$MODE" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all|*)
        start_backend
        sleep 2
        start_frontend
        echo ""
        ok "Dashboard:  http://localhost:$FRONTEND_PORT"
        ok "API docs:   http://localhost:$BACKEND_PORT/docs"
        echo ""
        # Wait for frontend to be ready, then open in default browser
        log "Waiting for dashboard to be ready…"
        for i in $(seq 1 15); do
            if curl -s -o /dev/null -w "" "http://localhost:$FRONTEND_PORT/" 2>/dev/null; then
                ok "Opening dashboard in browser…"
                open "http://localhost:$FRONTEND_PORT/"
                break
            fi
            sleep 1
        done
        ;;
esac

log "Press Ctrl+C to stop all services."
wait
