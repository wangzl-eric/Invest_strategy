#!/bin/bash
# Start backend with Flex Query token from .env file

cd "$(dirname "$0")/.."
source /Users/zelin/opt/anaconda3/etc/profile.d/conda.sh
conda activate ibkr-analytics

# Load .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✓ Loaded environment variables from .env"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Please create .env file with: FLEX_TOKEN=\"your_token_here\""
fi

# Kill existing backend
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

# Start backend (token will be loaded from .env via environment)
echo "Starting backend..."
PYTHONPATH="$(pwd)" nohup python backend/main.py > backend.log 2>&1 &

echo "Backend started. Check logs with: tail -f backend.log"
