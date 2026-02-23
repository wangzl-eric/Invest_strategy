#!/bin/bash

# IBKR Analytics Startup Script
# This script ensures the environment is ready and starts both backend and frontend

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}Cleanup complete.${NC}"
    exit 0
}

# Set trap for cleanup on exit
trap cleanup SIGINT SIGTERM EXIT

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if ! command -v "$python_cmd" &> /dev/null; then
        return 1
    fi
    
    local version=$($python_cmd --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    local major=$(echo $version | cut -d'.' -f1)
    local minor=$(echo $version | cut -d'.' -f2)
    
    if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 10 ]); then
        echo "$python_cmd"
        return 0
    fi
    return 1
}

# ALWAYS use conda environment - this is required
USE_CONDA_ENV="ibkr-analytics"

if ! command -v conda &> /dev/null; then
    print_error "conda is required but not found in PATH"
    print_error "Please install Anaconda or Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

print_status "Checking for conda environment 'ibkr-analytics'..."

# Check if conda environment exists
if conda env list | grep -q "^${USE_CONDA_ENV} "; then
    print_status "Found conda environment 'ibkr-analytics'"
    # Check Python version in conda env using conda run
    CONDA_PYTHON_VERSION=$(conda run -n ibkr-analytics python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    CONDA_PYTHON_MAJOR=$(echo $CONDA_PYTHON_VERSION | cut -d'.' -f1)
    CONDA_PYTHON_MINOR=$(echo $CONDA_PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$CONDA_PYTHON_MAJOR" -gt 3 ] || ([ "$CONDA_PYTHON_MAJOR" -eq 3 ] && [ "$CONDA_PYTHON_MINOR" -ge 10 ]); then
        PYTHON_CMD="conda run -n ibkr-analytics python"
        print_success "Using Python $CONDA_PYTHON_VERSION from conda environment 'ibkr-analytics'"
    else
        print_status "Updating conda environment to Python 3.10+..."
        conda install -y python=3.10 -n ibkr-analytics
        PYTHON_CMD="conda run -n ibkr-analytics python"
        print_success "Conda environment updated"
    fi
else
    print_status "Creating conda environment 'ibkr-analytics' with Python 3.10..."
    conda create -y -n ibkr-analytics python=3.10
    PYTHON_CMD="conda run -n ibkr-analytics python"
    print_success "Conda environment created"
    print_warning "Don't forget to install dependencies: conda run -n ibkr-analytics pip install -r requirements.txt"
fi

# Export Python command for later use
export PYTHON_CMD
export USE_CONDA_ENV

# Always use conda environment (no venv needed)
print_status "Using conda environment: $USE_CONDA_ENV"

# Check/install dependencies
print_status "Checking dependencies..."
DEPS_MARKER_FILE="venv/.deps_installed"
if [ ! -z "$USE_CONDA_ENV" ]; then
    DEPS_MARKER_FILE=".conda_deps_installed"
fi

if [ ! -f "$DEPS_MARKER_FILE" ] || [ "requirements.txt" -nt "$DEPS_MARKER_FILE" ]; then
    print_status "Installing dependencies from requirements.txt..."
    $PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1
    $PYTHON_CMD -m pip install -r requirements.txt
    touch "$DEPS_MARKER_FILE"
    print_success "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Check configuration files
print_status "Checking configuration files..."

# Check app_config.yaml
if [ ! -f "config/app_config.yaml" ]; then
    print_warning "config/app_config.yaml not found. Creating from defaults..."
    mkdir -p config
    cat > config/app_config.yaml << EOF
# Application Configuration

ibkr:
  host: "127.0.0.1"
  port: 7497  # 7497 for paper trading, 7496 for live trading
  client_id: 1
  timeout: 30

database:
  url: "sqlite:///./ibkr_analytics.db"
  echo: false

app:
  debug: false
  log_level: "INFO"
  update_interval_minutes: 15
EOF
    print_success "Created config/app_config.yaml"
fi

# Check ibkr_config.yaml (optional, can use app_config.yaml)
if [ ! -f "config/ibkr_config.yaml" ]; then
    print_warning "config/ibkr_config.yaml not found (optional, using app_config.yaml)"
fi

# Initialize database if needed
print_status "Checking database..."
DB_FILE="ibkr_analytics.db"
if [ ! -f "$DB_FILE" ]; then
    print_status "Database not found. Initializing database..."
    $PYTHON_CMD scripts/init_db.py
    print_success "Database initialized"
else
    print_status "Database found"
fi

# Check if ports are available
print_status "Checking if ports are available..."

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

if ! check_port 8000; then
    print_error "Port 8000 is already in use. Please stop the service using it or change the backend port."
    exit 1
fi

if ! check_port 8050; then
    print_error "Port 8050 is already in use. Please stop the service using it or change the frontend port."
    exit 1
fi

print_success "Ports 8000 and 8050 are available"

# Start backend
print_status "Starting backend server..."
# Set PYTHONPATH to include project root for module imports
if [ ! -z "$USE_CONDA_ENV" ]; then
    # For conda, use conda run with PYTHONPATH environment variable
    (cd "$SCRIPT_DIR" && PYTHONPATH="$SCRIPT_DIR" conda run --no-capture-output -n "$USE_CONDA_ENV" python backend/main.py) > backend.log 2>&1 &
else
    (cd "$SCRIPT_DIR" && PYTHONPATH="$SCRIPT_DIR" $PYTHON_CMD backend/main.py) > backend.log 2>&1 &
fi
BACKEND_PID=$!

# Wait for backend to start
print_status "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start. Check backend.log for details."
    exit 1
fi

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is running on http://localhost:8000 (PID: $BACKEND_PID)"
else
    print_warning "Backend started but health check failed. It may still be starting up..."
fi

# Start frontend
print_status "Starting frontend dashboard..."
# Set PYTHONPATH to include project root for module imports
if [ ! -z "$USE_CONDA_ENV" ]; then
    # For conda, use conda run with PYTHONPATH environment variable
    (cd "$SCRIPT_DIR" && PYTHONPATH="$SCRIPT_DIR" conda run --no-capture-output -n "$USE_CONDA_ENV" python frontend/app.py) > frontend.log 2>&1 &
else
    (cd "$SCRIPT_DIR" && PYTHONPATH="$SCRIPT_DIR" $PYTHON_CMD frontend/app.py) > frontend.log 2>&1 &
fi
FRONTEND_PID=$!

# Wait for frontend to start
print_status "Waiting for frontend to start..."
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start. Check frontend.log for details."
    cleanup
    exit 1
fi

print_success "Frontend is running on http://localhost:8050 (PID: $FRONTEND_PID)"

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  IBKR Analytics Platform Started!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e "Frontend:     ${BLUE}http://localhost:8050${NC}"
echo ""
echo -e "Logs:"
echo -e "  Backend:  ${YELLOW}backend.log${NC}"
echo -e "  Frontend: ${YELLOW}frontend.log${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running and monitor processes
while true; do
    sleep 5
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend process died unexpectedly!"
        cleanup
        exit 1
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend process died unexpectedly!"
        cleanup
        exit 1
    fi
done
