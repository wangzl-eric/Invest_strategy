---
name: data_fetcher
description: >
  Unified market data interface — NL ticker resolution, local-first Parquet
  lookup with API fallback, and code generation. Use whenever a researcher,
  agent, or user says "pull data for X", "get prices for Y", or "fetch macro
  series Z". Owns the documentation and Python scripts for the data layer.
---

# data_fetcher Skill

## Purpose

This skill is the single entry point for all market data work:
1. **Resolve** natural-language queries → canonical ticker IDs
2. **Generate** ready-to-run `get_data()` code cells
3. **Detect gaps** — report local Parquet coverage vs API fetch requirement
4. **Maintain** the Python scripts and their inline documentation

---

## Managed Python Scripts

| Script | Purpose | Owner |
|--------|---------|-------|
| `quant_data/api.py` | Public `get_data()` interface, local-first + API fallback | data_fetcher |
| `quant_data/ticker_map.py` | Ticker registry, NL alias resolver, `auto_detect_source()` | data_fetcher |
| `quant_data/analytics.py` | `compute_rolling_sharpe`, `compute_drawdown`, `compute_correlation_matrix` | data_fetcher |
| `book_notes/playground/shared/data_helpers.py` | Backward-compat shim → re-exports from api.py | data_fetcher |

> `quant_data/` lives at repo root. Always import from `quant_data.*` (not `workstation.quant_data.*`).

When **adding a new ticker or series**: edit `ticker_map.py` `_FRED_ENTRIES` /
`_ETF_ENTRIES` / `_FX_ENTRIES` / `_CRYPTO_ENTRIES` and add aliases.

When **adding a new connector**: add a `_fetch_<source>()` function in `api.py`
and register the source string in `auto_detect_source()` in `ticker_map.py`.

---

## Step 1 — Resolve Tickers

Use `resolve_strict(query)` from `quant_data/ticker_map.py`.

### Built-in alias table

| Natural language | Canonical ID | Source | Class |
|-----------------|--------------|--------|-------|
| "10-year yield", "treasury yield", "10y yield" | `DGS10` | fred | macro |
| "2-year yield", "2y yield" | `DGS2` | fred | macro |
| "yield curve", "inversion", "2s10s" | `T10Y2Y` | fred | macro |
| "S&P 500", "SPX", "s&p" | `SPY` | yfinance | etf |
| "nasdaq", "nasdaq 100" | `QQQ` | yfinance | etf |
| "high yield spread", "HY OAS", "junk bond spread" | `BAMLH0A0HYM2` | fred | macro |
| "investment grade spread", "IG OAS" | `BAMLC0A0CM` | fred | macro |
| "fed funds", "policy rate", "ffr" | `DFF` | fred | macro |
| "VIX", "fear index", "volatility index" | `VIXCLS` | fred | macro |
| "long bond", "TLT", "20-year treasury" | `TLT` | yfinance | etf |
| "gold", "GLD" | `GLD` | yfinance | etf |
| "oil", "USO" | `USO` | yfinance | etf |
| "bitcoin", "BTC" | `BTCUSDT` | binance | crypto |
| "ethereum", "ETH" | `ETHUSDT` | binance | crypto |
| "euro", "EUR/USD", "EURUSD" | `EURUSD=X` | yfinance | fx |
| "sterling", "cable", "GBP/USD" | `GBPUSD=X` | yfinance | fx |
| "breakeven inflation", "TIPS spread" | `T10YIE` | fred | macro |
| "fed balance sheet", "QE" | `WALCL` | fred | macro |

For **unrecognised terms**, raise `ValueError` and show `resolve_strict()` suggestions.

---

## Step 2 — Check Local Coverage

```python
import json
from pathlib import Path

catalog_path = Path("data/market_data/catalog.json")
catalog = json.loads(catalog_path.read_text()) if catalog_path.exists() else {}
coverage = catalog.get("DGS10")  # → {"start": "2000-01-03", "end": "2026-03-24"} or None
```

Report format:
```
[TICKER RESOLUTION]
Input: "10-year treasury yield, S&P 500"
Resolved: DGS10 (FRED, macro), SPY (yfinance, etf)
Local coverage: DGS10 ✓ (2000-01-03 – 2026-03-24)  |  SPY ✗ (not cached — will fetch)
```

---

## Step 3 — Generate Code

Always use `quant_data.api.get_data()` as the canonical call:

```python
from quant_data.api import get_data

# Single series (NL alias or canonical ID both work)
df = get_data("10-year yield", start="2010-01-01")
df = get_data("DGS10", start="2010-01-01")           # equivalent

# Multiple tickers / mixed asset classes
df = get_data(["DGS10", "SPY", "BTCUSDT"], start="2010-01-01")

# Explicit source override
df = get_data("DGS10", start="2000-01-01", source="fred")

# Weekly / monthly resampling
df = get_data("SPY", start="2020-01-01", frequency="1w")
df = get_data("SPY", start="2020-01-01", frequency="1m")

# Convenience aliases (backward-compat)
from quant_data.api import get_vix, get_spy, get_fred
vix = get_vix(start="2010-01-01")
spy = get_spy(start="2010-01-01")
yields = get_fred(["DGS10", "DGS2"], start="2000-01-01")
```

**Return schemas:**
- Price data → `(date, ticker, open, high, low, close, volume)`
- Macro/FRED data → `(date, series_id, value)`

On a cache miss `get_data()` emits `logger.warning("cache miss for %s — fetching from %s", ...)`
and writes the result back to `data/market_data/prices/` automatically.

---

## Source Reference

| source= | Asset classes | API key |
|---------|--------------|--------|
| `yfinance` | equities, ETFs, FX (`=X`), commodities | None |
| `fred` | macro, treasury yields, credit spreads | `FRED_API_KEY` (env) |
| `binance` | crypto OHLCV (`*USDT`) | None |
| `ecb` | EUR-base FX reference rates | None |
| `stooq` | deep equity history, intl markets | None |
| `polygon` | US equities adjusted | `POLYGON_API_KEY` (env) |
| `ibkr` | live/paper quotes | TWS running locally |

---

## Maintaining This Skill

When the data layer changes, update **both** this SKILL.md **and** the
corresponding Python script:

- New alias → `ticker_map.py` `_FRED_ENTRIES` / `_ETF_ENTRIES` / etc. + alias table above
- New connector → `api.py` `_fetch_<source>()` + Source Reference table above
- New analytics helper → `analytics.py` + re-export in `api.py` `__all__`
- New backward-compat shim needed → `data_helpers.py` + note in Managed Scripts table

Run verification after any change:
```bash
python -c "from quant_data.api import get_data; print('api ok')"
python -c "from quant_data.ticker_map import resolve_strict; print(resolve_strict('10-year yield'))"
python -c "from quant_data.analytics import compute_rolling_sharpe; print('analytics ok')"
```


