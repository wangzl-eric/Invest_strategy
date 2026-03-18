# Portfolio Analyst Automation

Automated daily download and import of IBKR Portfolio Analyst reports.

## Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  IBKR Portal    │────▶│   CSV File      │────▶│   Database      │
│  (Browser Auto) │     │  pa_reports/    │     │  pnl_history    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
    download_portfolio    automate_pa_daily      Frontend/API
       _analyst.py              .py                 queries
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure credentials
cp .env.example .env
# Edit .env with your IBKR credentials

# 3. Test download (visible browser)
python scripts/download_portfolio_analyst.py --no-headless

# 4. Run full automation
python scripts/automate_pa_daily.py
```

## Configuration

Create `.env` file with:

```bash
IBKR_USERNAME=your_username
IBKR_PASSWORD=your_password
IBKR_ACCOUNT_ID=U1234567
```

## Scheduling

### macOS (LaunchAgent)

```bash
bash scripts/setup_pa_scheduler.sh
```

Runs daily at 9:00 AM. Edit `scripts/com.ibkr.pa_automation.plist` to change time.

**Commands:**
```bash
# Status
launchctl list | grep pa_automation

# Logs
tail -f pa_automation.log

# Uninstall
launchctl unload ~/Library/LaunchAgents/com.ibkr.pa_automation.plist
```

### Python Daemon

```bash
# Run at specific time daily
python scripts/pa_scheduler.py --daemon --time "09:00"

# Run once now
python scripts/pa_scheduler.py --run-now
```

### Cron (Linux/macOS)

```bash
# Add to crontab (runs daily at 9 AM)
0 9 * * * cd /path/to/Invest_strategy && python3 scripts/automate_pa_daily.py >> pa_automation.log 2>&1
```

## Manual Operations

| Command | Description |
|---------|-------------|
| `python scripts/download_portfolio_analyst.py` | Download CSV only |
| `python scripts/import_portfolio_analyst.py <file> <account>` | Import existing CSV |
| `python scripts/automate_pa_daily.py` | Full workflow |

## Troubleshooting

**Browser issues:**
```bash
# Run with visible browser to debug
python scripts/download_portfolio_analyst.py --no-headless
```

**Custom CSV columns:**
```bash
python scripts/automate_pa_daily.py \
  --date-column "Trade Date" \
  --equity-column "Account Value"
```

**Files:**
- Logs: `pa_automation.log`, `logs/pa_download_*.log`
- Downloads: `data/pa_reports/`
- Screenshots: `data/pa_reports/error_screenshot_*.png`

## Data Access

```bash
# API
curl http://localhost:8000/api/pnl/history?account_id=U1234567

# Frontend
open http://localhost:8050
```
