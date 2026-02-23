# IBKR Account Setup Guide

## How IBKR Authentication Works

**Important**: IBKR API does NOT use username/password directly in the application. Instead:

1. You log into **TWS (Trader Workstation)** or **IB Gateway** with your IBKR username/password
2. TWS/Gateway runs locally on your computer and exposes an API socket
3. This application connects to TWS/Gateway via the local socket
4. TWS/Gateway handles all authentication with IBKR servers

## Step-by-Step Setup

### Step 1: Install TWS or IB Gateway

1. Download **TWS** (Trader Workstation) or **IB Gateway** from:
   - https://www.interactivebrokers.com/en/index.php?f=16042
   - **IB Gateway** is recommended (lighter, no GUI needed)

2. Install and launch the application

3. **Log in with your IBKR username and password** when TWS/Gateway starts

### Step 2: Enable API Access in TWS/Gateway

1. In TWS: Go to **Configure → API → Settings**
2. Enable **"Enable ActiveX and Socket Clients"**
3. Set **Socket port** to:
   - `7497` for **paper trading** (recommended for testing)
   - `7496` for **live trading** (real money)
4. Add `127.0.0.1` to **"Trusted IPs"** (click "Add" button)
5. Click **"OK"** and **restart TWS/Gateway**

### Step 3: Configure the Application

Edit `config/app_config.yaml`:

```yaml
ibkr:
  host: "127.0.0.1"           # Localhost (TWS/Gateway runs locally)
  port: 7497                  # 7497 for paper, 7496 for live
  client_id: 1                # Any unique integer
  timeout: 30

database:
  url: "sqlite:///./ibkr_analytics.db"
  echo: false

app:
  debug: false
  log_level: "INFO"
  update_interval_minutes: 15  # How often to fetch data automatically
```

### Step 4: Start TWS/Gateway

**IMPORTANT**: TWS/Gateway must be running before starting this application!

1. Launch TWS or IB Gateway
2. Log in with your IBKR credentials
3. Keep it running (minimize it if using IB Gateway)

### Step 5: Start the Application

Run the startup script:

```bash
./start.sh
```

This will:
- Start the backend API server (port 8000)
- Start the frontend dashboard (port 8050)
- **Note**: The scheduler will NOT start automatically - you need to manually trigger data fetching

### Step 6: Fetch Your Account Data

You have two options:

#### Option A: Manual Fetch (Recommended for First Time)

1. Open your browser to: `http://localhost:8000/docs`
2. Find the `/api/fetch-data` endpoint
3. Click "Try it out"
4. Optionally enter your account ID (leave blank to auto-detect)
5. Click "Execute"

Or use curl:

```bash
curl -X POST "http://localhost:8000/api/fetch-data?account_id=YOUR_ACCOUNT_ID"
```

#### Option B: Start Automatic Scheduler

Create a script to start the scheduler (or add it to your startup):

```python
# start_scheduler.py
import asyncio
from backend.scheduler import scheduler
from backend.ibkr_client import IBKRClient

async def main():
    # Connect to IBKR
    ibkr_client = IBKRClient()
    await ibkr_client.connect()
    
    # Start scheduler (replace with your account ID)
    scheduler.start(account_id="YOUR_ACCOUNT_ID")
    
    print("Scheduler started! Data will be fetched every 15 minutes.")
    print("Press Ctrl+C to stop.")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        scheduler.stop()
        await ibkr_client.disconnect()
        print("Scheduler stopped.")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python start_scheduler.py
```

### Step 7: View Your Data

1. Open the dashboard: `http://localhost:8050`
2. You should see:
   - **Overview**: Account summary and value chart
   - **Positions**: Your current positions
   - **Performance**: Returns and risk metrics
   - **Trades**: Trade history

## Troubleshooting

### "Failed to connect to IBKR TWS/Gateway"

**Solutions:**
1. ✅ Make sure TWS/Gateway is running and you're logged in
2. ✅ Check that API is enabled in TWS/Gateway settings
3. ✅ Verify port number matches (7497 for paper, 7496 for live)
4. ✅ Ensure `127.0.0.1` is in Trusted IPs
5. ✅ Restart TWS/Gateway after changing API settings
6. ✅ Check firewall isn't blocking localhost connections

### "No account snapshot found"

**Solutions:**
1. ✅ Make sure you've fetched data at least once (use `/api/fetch-data`)
2. ✅ Verify TWS/Gateway is connected to your account
3. ✅ Check backend logs for errors

### "Connection refused"

**Solutions:**
1. ✅ TWS/Gateway must be running BEFORE starting this application
2. ✅ Check the port in `config/app_config.yaml` matches TWS/Gateway port
3. ✅ Try restarting TWS/Gateway

## Security Notes

- ✅ **Never commit** your IBKR credentials to version control
- ✅ TWS/Gateway handles authentication - no passwords in this app
- ✅ Only allow `127.0.0.1` in Trusted IPs (local connections only)
- ✅ Use paper trading port (7497) for testing
- ✅ Keep TWS/Gateway updated

## Finding Your Account ID

Your account ID is usually:
- Displayed in TWS/Gateway when you log in
- Found in TWS: Account → Account Window
- Format: Usually starts with "DU" (for demo) or "U" (for live)

You can also leave `account_id` blank when fetching - the system will auto-detect it from your account.

## Next Steps

1. ✅ Set up TWS/Gateway and enable API
2. ✅ Configure `config/app_config.yaml`
3. ✅ Start TWS/Gateway and log in
4. ✅ Run `./start.sh` to start the application
5. ✅ Fetch data using `/api/fetch-data` endpoint
6. ✅ View dashboard at `http://localhost:8050`
7. ✅ Set up scheduler for automatic updates (optional)

