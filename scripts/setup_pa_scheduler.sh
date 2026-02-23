#!/bin/bash
# Setup script for Portfolio Analyst daily automation scheduler

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
PLIST_NAME="com.ibkr.pa_automation"
PLIST_FILE="$SCRIPT_DIR/${PLIST_NAME}.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "Setting up Portfolio Analyst automation scheduler..."

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Warning: .env file not found. Creating from template..."
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo "Please edit .env and add your IBKR credentials"
    else
        echo "Error: .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Update plist with actual project path
sed -i.bak "s|/Users/zelin/Desktop/PA Investment/Invest_strategy|$PROJECT_ROOT|g" "$PLIST_FILE"
rm -f "${PLIST_FILE}.bak"

# Find conda path
CONDA_PATH=$(which conda)
if [ -z "$CONDA_PATH" ]; then
    echo "Error: conda not found in PATH"
    echo "Please ensure conda is installed and in your PATH"
    exit 1
fi

# Get conda base directory (usually parent of bin/conda)
CONDA_BASE=$(dirname $(dirname "$CONDA_PATH"))

# Update plist to use conda run with ibkr-analytics environment
# Replace the ProgramArguments array to use conda run
sed -i.bak "s|<string>/Users/zelin/opt/anaconda3/bin/conda</string>|<string>$CONDA_BASE/bin/conda</string>|g" "$PLIST_FILE"
sed -i.bak "s|<string>/Users/zelin/Desktop/PA Investment/Invest_strategy/scripts/automate_pa_daily.py</string>|<string>$PROJECT_ROOT/scripts/automate_pa_daily.py</string>|g" "$PLIST_FILE"
rm -f "${PLIST_FILE}.bak"

echo "✓ Updated plist to use conda environment: $CONDA_BASE/bin/conda"

# Copy plist to LaunchAgents
mkdir -p "$LAUNCHD_DIR"
cp "$PLIST_FILE" "$LAUNCHD_DIR/${PLIST_NAME}.plist"

# Load the service
if launchctl list | grep -q "$PLIST_NAME"; then
    echo "Unloading existing service..."
    launchctl unload "$LAUNCHD_DIR/${PLIST_NAME}.plist" 2>/dev/null || true
fi

echo "Loading service..."
launchctl load "$LAUNCHD_DIR/${PLIST_NAME}.plist"

echo ""
echo "✓ Portfolio Analyst scheduler installed successfully!"
echo ""
echo "Service will run daily at 9:00 AM"
echo ""
echo "To check status:"
echo "  launchctl list | grep $PLIST_NAME"
echo ""
echo "To view logs:"
echo "  tail -f $PROJECT_ROOT/pa_automation.log"
echo ""
echo "To uninstall:"
echo "  launchctl unload $LAUNCHD_DIR/${PLIST_NAME}.plist"
echo "  rm $LAUNCHD_DIR/${PLIST_NAME}.plist"
