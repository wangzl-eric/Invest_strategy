# Source Map

## Asset-Class Keys

Use these repository-native keys when pulling or querying data:

- `equities`
- `fx`
- `commodities`
- `rates_yf`
- `treasury_yields`
- `macro_indicators`
- `fed_liquidity`
- `ibkr_equities`
- `ibkr_fx`
- `ibkr_futures`
- `ibkr_options`

## Pull Paths

Direct Python entry points in `backend/market_data_store.py`:

- `pull_yf_data(tickers, start_date, end_date, asset_class)`
- `pull_fred_data(series_ids, start_date, end_date, category)`
- `pull_ibkr_data(tickers, start_date, end_date, asset_class, interval="1 day", sec_type="STK", exchange="SMART")`

API routes in `backend/api/data_routes.py`:

- `POST /data/pull`
- `GET /data/query`
- `GET /data/catalog`
- `POST /data/update-all`
- `GET /data/pull-status/{job_id}`
- `POST /data/ibkr/pull-historical`
- `GET /data/ibkr/subscription-status`

## Query Paths

For read-heavy research, prefer DuckDB through `backend/research/duckdb_utils.py`:

- `ResearchDB.query_prices(...)`
- `ResearchDB.get_returns(...)`
- `ResearchDB.get_fred_series(...)`
- `ResearchDB.join_price_macro(...)`

## Validation Checklist

After a pull or query, verify:

- distinct symbols or series IDs requested vs returned
- min and max available dates
- duplicate keys on `(date, ticker)` or `(date, series_id)`
- empty tail rows or NaN-heavy last observations
- catalog freshness in `data/market_data/catalog.json`

## Source-Specific Caveats

- `IBKR`: highest-quality tradable history here, but requires TWS or IB Gateway plus subscriptions.
- `FRED`: strong for rates and macro, but releases can lag the market and later be revised.
- `yfinance`: useful fallback, but not the standard for execution-grade claims.
