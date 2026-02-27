# Known Issues & Bug Log

Tracks bugs, gotchas, and workarounds encountered during development to prevent recurrence.

---

## Resolved Issues

### 1. `fredapi` not installed in conda environment
- **Date**: 2026-02-24
- **Symptom**: Macro Pulse, Rates FRED data, Fed QE/QT Monitor all showed no data. Backend returned empty arrays for all FRED-dependent panels.
- **Root cause**: `fredapi` was listed in `requirements.txt` but never installed in the `ibkr-analytics` conda environment. The `_get_fred()` function caught the `ImportError` silently and returned `None`.
- **Fix**: `pip install fredapi` in the conda env.
- **Prevention**: When adding new packages to `requirements.txt`, also run `pip install <package>` in the active environment. Consider adding a startup check that logs missing packages.

### 2. FRED API key not loaded after setting in `.env`
- **Date**: 2026-02-24
- **Symptom**: After adding `FRED_API_KEY` to `.env`, the API still returned "FRED_API_KEY not configured".
- **Root cause**: The backend uses an in-memory TTL cache. The previous call (with empty key) cached an empty result. The `--reload` flag hot-reloads code changes but does NOT re-read `.env` because `dotenv.load_dotenv()` runs at import time and the module was already loaded.
- **Fix**: Full server restart (kill + restart both backend and frontend).
- **Prevention**: After any `.env` change, always restart both servers. Document this in the workflow rule.

### 3. Dash frontend not picking up code changes
- **Date**: 2026-02-24
- **Symptom**: Backend API returned correct data but the dashboard UI still showed old layout/behavior.
- **Root cause**: The frontend is started with `nohup python frontend/app.py &`. Even though Dash runs in debug mode, it doesn't detect changes when launched this way. The backend's `--reload` flag works because uvicorn watches for file changes, but the Dash process doesn't.
- **Fix**: Kill the old Dash process (`lsof -ti:8050 | xargs kill -9`) and restart.
- **Prevention**: Always restart the frontend after code changes. Consider using a process manager or adding file watching.

### 4. WRESBAL (Reserve Balances) showing ~2950 T$ instead of ~2.95 T$
- **Date**: 2026-02-24
- **Symptom**: The Fed QE/QT Monitor showed Reserve Balances as 2949.804 T$ — clearly wrong.
- **Root cause**: Assumed WRESBAL was reported in billions on FRED, but it's actually in **millions** of dollars. The divisor was set to `1e3` (billions→trillions) instead of `1e6` (millions→trillions).
- **Fix**: Changed `"divisor": 1e3` to `"divisor": 1e6` in `FED_LIQUIDITY_SERIES`.
- **Prevention**: Always check the "Units" field on the FRED series page before setting a divisor. Add a comment with the raw unit in the config dict.

### 5. DSWP swap rate series returning empty data
- **Date**: 2026-02-24
- **Symptom**: Swap rates, swap spreads, and asset swap spreads all showed no data. The swap curve chart was empty.
- **Root cause**: The FRED series `DSWP2`, `DSWP5`, `DSWP10`, `DSWP30` (USD interest rate swap rates from the H.15 release) were **discontinued** by the Federal Reserve. No alternative free source for USD swap rates exists on FRED.
- **Fix**: Removed DSWP series from config. Replaced with TIPS real yield series (`DFII5`, `DFII10`, `DFII30`) which provide complementary rate information. The swap spread/asset swap spread categories remain in the UI code and will activate if a data source is added later.
- **Prevention**: Before adding any FRED series to production config, test it with `fred.get_series('SERIES_ID', observation_start='recent_date')` to confirm it returns data.

---

## Open Issues

### 1. No free source for USD swap rates
- **Status**: Open (data limitation)
- **Impact**: Swap curve, swap spread, and asset swap spread panels are empty.
- **Workaround**: Bloomberg Terminal or a professional data feed (Refinitiv, Databento) would provide swap rates. Could also scrape from CME or ICE if terms allow.
- **Possible alternatives**: SOFR swap rate futures from CME (if FRED adds them), or compute a proxy from Treasury futures implied yields.

### 2. Sparkline rendering may slow down with many instruments
- **Status**: Open (performance)
- **Impact**: Each sparkline is a separate `dcc.Graph` with `staticPlot: True`. With 30+ instruments across all panels, initial render may be slower. Not a problem on modern hardware but noticeable on older machines.
- **Workaround**: Sparklines are cached server-side for 5 minutes (`SPARKLINE_TTL = 300`). If rendering is too slow, could switch to SVG path strings or base64 PNG sparklines in a future iteration.

### 3. Meeting-specific Fed probabilities (e.g. CME FedWatch) not available
- **Status**: Open (data limitation)
- **Impact**: Central bank meeting tracker shows countdown and implied path proxy (2Y-FF spread) but not meeting-by-meeting probabilities (e.g. "70% chance of 25bp cut in March").
- **Workaround**: Use CME FedWatch or Atlanta Fed Market Probability Tracker for meeting-specific probabilities. CME Fed Funds futures data would require a paid feed or scraping.

### 4. Parquet data lake requires manual initial population
- **Status**: Open (by design)
- **Impact**: The `data/market_data/` directory starts empty. Users must click "Update All" in the Data Manager tab or trigger individual pulls to populate it.
- **Workaround**: Run `POST /api/data/update-all` once after setup to backfill 2 years of data for all tracked instruments.

### 5. IBKR API requires Gateway to remain running
- **Status**: Open (known limitation)
- **Impact**: Historical data pulls via the IBKR pipeline require IB Gateway or TWS to be running with API access enabled.
- **Workaround**: Keep IB Gateway running in the background. For automated pipelines, consider using a scheduled task that starts Gateway before fetching data.
- **Prevention**: Document this requirement in the usage guide.

### 6. Market data subscriptions expire after 60 days of inactivity
- **Status**: Open (IBKR policy)
- **Impact**: If you don't log into IBKR for 60 days, market data subscriptions become inactive and data pulls will fail.
- **Workaround**: Log into IB Gateway at least once every 60 days to keep subscriptions active.
- **Prevention**: Add a calendar reminder to log in regularly.

### 7. Rate limiting on IBKR API
- **Status**: Open (IBKR policy)
- **Impact**: Bulk data fetches may be throttled if too many requests are made quickly.
- **Workaround**: The code includes 0.2-0.3 second delays between requests. For very large fetches, use the background job endpoint which includes rate limiting.
- **Prevention**: Don't make more than ~50 requests per second to avoid IP bans.

---

## Debugging Checklist

When a panel shows no data, check in this order:

1. **Is the package installed?** — `python -c "import <package>"`
2. **Is the API key set?** — Check `.env` for the relevant key
3. **Is the server restarted?** — Kill + restart after `.env` or package changes
4. **Is the FRED series valid?** — Test with `fred.get_series()` directly
5. **Is the cache stale?** — Restart server to clear TTL cache
6. **Are the units correct?** — Check FRED page for "Units" field
7. **Is the frontend restarted?** — Dash doesn't hot-reload from `nohup`
