@echo off
REM IBKR Analytics Startup Script for Windows
REM This script ensures the environment is ready and starts both backend and frontend

setlocal enabledelayedexpansion

echo ========================================
echo   IBKR Analytics Startup Script
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check Python
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ first.
    exit /b 1
)
echo [SUCCESS] Python found
echo.

REM Check/create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment found
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check/install dependencies
echo [INFO] Checking dependencies...
if not exist "venv\.deps_installed" (
    echo [INFO] Installing dependencies...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    echo. > venv\.deps_installed
    echo [SUCCESS] Dependencies installed
) else (
    echo [INFO] Dependencies already installed
)
echo.

REM Check configuration files
echo [INFO] Checking configuration files...
if not exist "config\app_config.yaml" (
    echo [WARNING] config\app_config.yaml not found. Creating from defaults...
    if not exist "config" mkdir config
    (
        echo # Application Configuration
        echo.
        echo ibkr:
        echo   host: "127.0.0.1"
        echo   port: 7497  # 7497 for paper trading, 7496 for live trading
        echo   client_id: 1
        echo   timeout: 30
        echo.
        echo database:
        echo   url: "sqlite:///./ibkr_analytics.db"
        echo   echo: false
        echo.
        echo app:
        echo   debug: false
        echo   log_level: "INFO"
        echo   update_interval_minutes: 15
    ) > config\app_config.yaml
    echo [SUCCESS] Created config\app_config.yaml
)
echo.

REM Initialize database if needed
echo [INFO] Checking database...
if not exist "ibkr_analytics.db" (
    echo [INFO] Database not found. Initializing database...
    python scripts\init_db.py
    echo [SUCCESS] Database initialized
) else (
    echo [INFO] Database found
)
echo.

REM Check if ports are available (basic check)
echo [INFO] Checking if ports are available...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] Port 8000 is already in use. Please stop the service using it.
    exit /b 1
)

netstat -an | findstr ":8050" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] Port 8050 is already in use. Please stop the service using it.
    exit /b 1
)
echo [SUCCESS] Ports 8000 and 8050 are available
echo.

REM Start backend
echo [INFO] Starting backend server...
start "IBKR Backend" /min python backend\main.py > backend.log 2>&1
timeout /t 3 /nobreak >nul
echo [SUCCESS] Backend started on http://localhost:8000
echo.

REM Start frontend
echo [INFO] Starting frontend dashboard...
start "IBKR Frontend" python frontend\app.py > frontend.log 2>&1
timeout /t 3 /nobreak >nul
echo [SUCCESS] Frontend started on http://localhost:8050
echo.

echo ========================================
echo   IBKR Analytics Platform Started!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend:     http://localhost:8050
echo.
echo Logs:
echo   Backend:  backend.log
echo   Frontend: frontend.log
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause

