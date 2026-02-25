#!/usr/bin/env bash
# Stop any running backend / frontend processes.
set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

killed=0

for pattern in "uvicorn backend.main:app" "python frontend/app.py"; do
    pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${BLUE}[stop]${NC} Killing: $pattern (PIDs: $pids)"
        echo "$pids" | xargs kill 2>/dev/null || true
        killed=1
    fi
done

if [ "$killed" -eq 1 ]; then
    echo -e "${GREEN}[stop]${NC} Services stopped."
else
    echo -e "${RED}[stop]${NC} No running services found."
fi
