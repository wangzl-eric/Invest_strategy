#!/bin/bash
# Wrapper script to ensure ibkr-analytics conda environment is always used
# Usage: ./run_with_env.sh <script_name> [args...]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
ENV_NAME="ibkr-analytics"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Anaconda/Miniconda first."
    exit 1
fi

# Check if environment exists
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "Error: conda environment '${ENV_NAME}' not found."
    echo "Please create it first: conda create -n ${ENV_NAME} python=3.10"
    exit 1
fi

# Get the script path
SCRIPT_PATH="$1"
shift  # Remove first argument

if [ -z "$SCRIPT_PATH" ]; then
    echo "Usage: $0 <script_name> [args...]"
    exit 1
fi

# Resolve script path
if [[ "$SCRIPT_PATH" != /* ]]; then
    # Relative path - resolve relative to script directory
    SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found: $SCRIPT_PATH"
    exit 1
fi

# Run script with conda environment
exec conda run -n "$ENV_NAME" python "$SCRIPT_PATH" "$@"
