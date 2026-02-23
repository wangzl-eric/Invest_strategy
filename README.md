# IBKR Analytics Infrastructure

A full-stack quantitative analytics platform to analyze and visualize PnL, positions, and performance metrics from Interactive Brokers (IBKR) accounts.

## Features

- **Account Data Fetching**: Automated connection to IBKR TWS/Gateway API
- **Data Storage**: Historical snapshots of account state, positions, PnL, and trades
- **Performance Analytics**: Calculate returns, Sharpe ratio, Sortino ratio, maximum drawdown, and trade statistics
- **Interactive Dashboard**: Web-based visualization with real-time updates
- **Scheduled Updates**: Automatic intraday data refresh at configurable intervals

## Architecture

```
IBKR API (TWS/Gateway)
    ↓
Data Fetcher (ib_insync)
    ↓
Database (SQLite/PostgreSQL)
    ↓
FastAPI Server (REST API)
    ↓
Dash Frontend (Visualization)
```

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, ib_insync
- **Database**: SQLite (development) / PostgreSQL (production)
- **Data Processing**: pandas, numpy
- **Scheduling**: APScheduler
- **Frontend**: Plotly Dash
- **Deployment**: Docker containers

## Prerequisites

1. **Python 3.10+** installed
2. **IBKR Account** with API access enabled
3. **TWS or IB Gateway** installed and running
4. **Docker** (optional, for containerized deployment)
5. **Conda** (recommended) or virtual environment manager

## Python Environment Setup

**⚠️ IMPORTANT: This project REQUIRES the `ibkr-analytics` conda environment. All scripts MUST use this environment.**

### Environment Details

- **Environment name:** `ibkr-analytics`
- **Python version:** 3.10.18
- **Path:** `/Users/zelin/opt/anaconda3/envs/ibkr-analytics/bin/python`

### ⚠️ Always Use Conda Environment

**All Python scripts in this project MUST be run using the `ibkr-analytics` conda environment.** Never use system Python or other environments.

### Using the Environment

#### Option 1: Use conda run (Recommended - Always Works)

```bash
# Always use conda run to ensure correct environment
conda run -n ibkr-analytics python scripts/download_portfolio_analyst.py
conda run -n ibkr-analytics python scripts/automate_pa_daily.py
conda run -n ibkr-analytics python scripts/import_portfolio_analyst.py report.csv U1234567
```

#### Option 2: Use Wrapper Script (Easiest)

```bash
# Use the wrapper script (automatically uses conda environment)
chmod +x scripts/run_with_env.sh
./scripts/run_with_env.sh scripts/download_portfolio_analyst.py
./scripts/run_with_env.sh scripts/automate_pa_daily.py
```

#### Option 3: Activate Environment (Interactive Use Only)

```bash
# Only for interactive shell sessions
conda activate ibkr-analytics
python scripts/download_portfolio_analyst.py
```

#### Option 4: Create Aliases (Recommended for Daily Use)

Add these to your `~/.zshrc` or `~/.bashrc`:

```bash
# Portfolio Analyst automation aliases
alias pa-download='conda run -n ibkr-analytics python /Users/zelin/Desktop/PA\ Investment/Invest_strategy/scripts/download_portfolio_analyst.py'
alias pa-automate='conda run -n ibkr-analytics python /Users/zelin/Desktop/PA\ Investment/Invest_strategy/scripts/automate_pa_daily.py'
alias pa-import='conda run -n ibkr-analytics python /Users/zelin/Desktop/PA\ Investment/Invest_strategy/scripts/import_portfolio_analyst.py'
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

Now you can use:
```bash
pa-download
pa-automate
pa-import report.csv U1234567
```

### Verify Environment

Test that all packages are installed:
```bash
conda run -n ibkr-analytics python -c "import pandas, numpy, sqlalchemy, playwright; print('✓ All packages OK')"
```

### IDE Configuration

For **Cursor/VS Code**, the project includes `.vscode/settings.json` that automatically points to the conda environment. Reload the window or restart Cursor to use it.

The IDE will automatically use: `/Users/zelin/opt/anaconda3/envs/ibkr-analytics/bin/python`

## Setup Instructions

### 1. Clone and Install Dependencies

**⚠️ IMPORTANT: This project REQUIRES conda. Do not use pip/venv directly.**

**Using Conda (Required):**

```bash
cd Invest_strategy

# Create conda environment (if not already created)
conda create -n ibkr-analytics python=3.10

# Activate environment
conda activate ibkr-analytics

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (for Portfolio Analyst automation)
conda run -n ibkr-analytics playwright install chromium
```

**Note:** Virtual environments (venv) are NOT supported. Always use the `ibkr-analytics` conda environment.

### 2. Configure IBKR API Access

**📖 For detailed setup instructions, see [IBKR_SETUP_GUIDE.md](guides/IBKR_SETUP_GUIDE.md)**

#### Quick Setup:

1. **Install TWS or IB Gateway** and log in with your IBKR username/password
   - Download: https://www.interactivebrokers.com/en/index.php?f=16042
   - **Note**: You log into TWS/Gateway with your credentials - the app connects to TWS/Gateway locally

2. **Enable API in TWS/Gateway:**
   - Go to **Configure → API → Settings**
   - Enable **"Enable ActiveX and Socket Clients"**
   - Set **Socket port** to `7497` (paper) or `7496` (live)
   - Add `127.0.0.1` to **"Trusted IPs"**
   - Click **OK** and restart TWS/Gateway

3. **Configure Application:**
   - Edit `config/app_config.yaml`:
   ```yaml
   ibkr:
     host: "127.0.0.1"
     port: 7497  # 7497 for paper, 7496 for live
     client_id: 1
   ```

### 3. Initialize Database

**Using Conda:**
```bash
conda run -n ibkr-analytics python scripts/init_db.py
```

**Using Virtual Environment:**
```bash
python scripts/init_db.py
```

### 4. Run the Application

#### Option A: Automated Startup Script (Recommended)

**Mac/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

The startup script will:
- ✅ Check for conda and `ibkr-analytics` environment
- ✅ Create conda environment if missing (Python 3.10+)
- ✅ Install dependencies automatically
- ✅ Create configuration files if missing
- ✅ Initialize database if needed
- ✅ Check port availability
- ✅ Start both backend and frontend services using conda
- ✅ Monitor services and handle cleanup on exit

Once started:
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend Dashboard: `http://localhost:8050`

Press `Ctrl+C` to stop all services.

#### Option B: Manual Startup (Two Terminals)

**Terminal 1 - Backend:**
```bash
conda run -n ibkr-analytics python backend/main.py
```

The API will be available at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
conda run -n ibkr-analytics python frontend/app.py
```

The dashboard will be available at `http://localhost:8050`

#### Option C: Docker Deployment

1. Copy environment variables:
   ```bash
   cp infrastructure/.env.example infrastructure/.env
   ```

2. Edit `infrastructure/.env` with your settings

3. Build and start containers:
   ```bash
   cd infrastructure
   docker-compose up --build
   ```

4. Access:
   - API: `http://localhost:8000`
   - Dashboard: `http://localhost:8050`

## Documentation

| Guide | Description |
|-------|-------------|
| [DATABASE_GUIDE.md](guides/DATABASE_GUIDE.md) | **Database queries, P&L analysis, sample code** |
| [FLEX_QUERY_SETUP.md](guides/FLEX_QUERY_SETUP.md) | Setting up IBKR Flex Queries |
| [IBKR_SETUP_GUIDE.md](guides/IBKR_SETUP_GUIDE.md) | IBKR TWS/Gateway configuration |
| [PA_AUTOMATION_SETUP.md](guides/PA_AUTOMATION_SETUP.md) | Portfolio Analyst automation |

## Usage

### API Endpoints

- `GET /api/account/summary` - Get latest account summary
- `GET /api/positions` - Get current positions
- `GET /api/pnl` - Get PnL history
- `GET /api/performance` - Get performance metrics
- `GET /api/trades` - Get trade history
- `GET /api/flex-query/status` - Check Flex Query configuration
- `POST /api/flex-query/fetch-all-reports` - Fetch all configured Flex Query reports

### Dashboard Pages

1. **Overview**: Account summary cards and account value chart
2. **Positions**: Current positions table with PnL breakdown
3. **Performance**: Returns chart, risk metrics (Sharpe, Sortino, drawdown)
4. **Trades**: Trade history with filters

### Fetching Account Data

#### Option 1: Manual Fetch (via API)

1. Make sure TWS/Gateway is running and logged in
2. Start the application: `./start.sh`
3. Fetch data manually:
   - Via API docs: `http://localhost:8000/docs` → `/api/fetch-data` endpoint
   - Or via curl: `curl -X POST "http://localhost:8000/api/fetch-data?account_id=YOUR_ACCOUNT_ID"`

#### Option 2: Automatic Scheduler

Start the scheduler to automatically fetch data at intervals:

**Using Conda:**
```bash
conda run -n ibkr-analytics python start_scheduler.py YOUR_ACCOUNT_ID
```

**Using Virtual Environment:**
```bash
python start_scheduler.py YOUR_ACCOUNT_ID
```

Or leave account ID blank to auto-detect:
```bash
conda run -n ibkr-analytics python start_scheduler.py
```

The scheduler will fetch data every 15 minutes (configurable in `config/app_config.yaml`).

#### Option 3: Portfolio Analyst Automation

For automated daily Portfolio Analyst report downloads, see [PA_AUTOMATION_SETUP.md](guides/PA_AUTOMATION_SETUP.md).

Quick start:
```bash
# Set up credentials in .env file
cp .env.example .env
# Edit .env with your IBKR credentials

# Test download
conda run -n ibkr-analytics python scripts/automate_pa_daily.py

# Set up daily scheduler (macOS)
bash scripts/setup_pa_scheduler.sh
```

## Configuration

### Environment Variables

You can override configuration using environment variables:

- `IBKR_HOST` - IBKR TWS/Gateway host (default: 127.0.0.1)
- `IBKR_PORT` - IBKR port (default: 7497)
- `IBKR_CLIENT_ID` - Client ID (default: 1)
- `DB_URL` - Database connection URL
- `APP_UPDATE_INTERVAL_MINUTES` - Data update interval (default: 15)

### Configuration Files

- `config/app_config.yaml` - Application settings
- `config/ibkr_config.yaml` - IBKR connection settings (not committed to git)

## Project Structure

```
Invest_strategy/
├── backend/              # Backend API service
│   ├── api/             # API routes and schemas
│   ├── ibkr_client.py   # IBKR API client
│   ├── data_fetcher.py  # Data fetching logic
│   ├── data_processor.py # Performance calculations
│   ├── models.py        # Database models
│   ├── database.py      # Database connection
│   ├── scheduler.py     # Scheduled jobs
│   └── main.py         # FastAPI app entry point
├── frontend/            # Frontend dashboard
│   ├── app.py          # Dash application
│   └── components/     # Visualization components
├── infrastructure/      # Docker configuration
├── config/             # Configuration files
├── scripts/            # Utility scripts
└── requirements.txt    # Python dependencies
```

## Security Considerations

- **Never commit** IBKR credentials or API keys to version control
- Use environment variables for sensitive configuration
- Keep TWS/Gateway updated
- Use strong passwords for database in production
- Consider using PostgreSQL with SSL in production

## Troubleshooting

### Connection Issues

1. **Cannot connect to IBKR:**
   - Ensure TWS/Gateway is running
   - Check that API is enabled in TWS/Gateway settings
   - Verify port number matches configuration (7497 for paper, 7496 for live)
   - Check firewall settings

2. **"Connection refused" error:**
   - Verify TWS/Gateway is listening on the correct port
   - Check that `127.0.0.1` is in Trusted IPs

### Data Issues

1. **No data showing:**
   - Check database is initialized: `conda run -n ibkr-analytics python scripts/init_db.py`
   - Verify scheduler is running and fetching data
   - Check API logs for errors

2. **Stale data:**
   - Verify scheduler is running
   - Check update interval configuration
   - Manually trigger data fetch if needed

### Environment Issues

1. **"Module not found" errors:**
   - Ensure you're using the correct environment: `conda activate ibkr-analytics`
   - Verify packages are installed: `conda run -n ibkr-analytics pip list | grep pandas`
   - Reinstall dependencies: `conda run -n ibkr-analytics pip install -r requirements.txt`

2. **IDE not recognizing imports:**
   - Reload Cursor/VS Code window (Cmd+Shift+P → "Reload Window")
   - Verify `.vscode/settings.json` points to conda environment
   - Check `pyrightconfig.json` is configured correctly

3. **Wrong Python version:**
   - Verify conda environment: `conda run -n ibkr-analytics python --version`
   - Should show Python 3.10.x or higher
   - Update if needed: `conda install python=3.10 -n ibkr-analytics`

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black backend/ frontend/
```

### Linting

```bash
flake8 backend/ frontend/
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is for personal use. Please ensure compliance with IBKR API terms of service.

## Support

For issues related to:
- **IBKR API**: Consult IBKR API documentation
- **Application**: Check logs in `logs/` directory
- **Database**: Verify connection string and permissions

## Database & P&L Analysis

### Quick Database Commands

```bash
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
source /Users/zelin/opt/anaconda3/etc/profile.d/conda.sh
conda activate ibkr-analytics

# Import trades from Flex Query files
PYTHONPATH="$(pwd)" python -m backend.db_utils import

# View trade summary (both USD and HKD)
PYTHONPATH="$(pwd)" python -m backend.db_utils summary

# View daily P&L
PYTHONPATH="$(pwd)" python -m backend.db_utils daily

# Run custom SQL query
PYTHONPATH="$(pwd)" python -m backend.db_utils query "SELECT * FROM trades WHERE symbol = 'IAU'"
```

### Python API

```python
from backend.db_utils import get_trades_df, get_daily_pnl, get_trade_summary, query_trades

# Query trades
trades = get_trades_df(symbol="IAU", start_date="2025-01-01")

# Get P&L summary
summary = get_trade_summary()
daily = get_daily_pnl()

# Run SQL
df = query_trades("SELECT symbol, SUM(realized_pnl) as pnl FROM trades GROUP BY symbol")
```

📖 **For complete database documentation, see [guides/DATABASE_GUIDE.md](guides/DATABASE_GUIDE.md)**

## Future Enhancements

- Real-time position updates
- Advanced risk metrics (VaR, CVaR)
- Portfolio optimization tools
- Multi-account support
- Email/SMS alerts
- Export reports (PDF, Excel)
- Market data storage and analysis

