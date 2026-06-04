---
name: get-market-data
description: Unified data query interface — local Parquet first, API fallback. Use whenever querying prices, macro series, FX, crypto, or any market data in research or playground notebooks.
---

# /get-market-data Skill

This skill does three things:
1. **NL → Ticker resolution** — map natural language to canonical IDs via `quant_data.ticker_map`
2. **Code generation** — emit a ready-to-run `get_data()` cell
3. **Gap detection** — report local vs API coverage from `data/market_data/catalog.json`

---

## Step 1 — Resolve Tickers

Use `quant_data.ticker_map.resolve_strict()` to map natural language to canonical IDs.

| Natural language | Canonical ID | Source | Asset class |
|-----------------|--------------|--------|-------------|
| "10-year yield" / "treasury yield" | `DGS10` | FRED | macro |
| "2-year yield" | `DGS2` | FRED | macro |
| "yield curve" / "inversion" | `T10Y2Y` | FRED | macro |
| "S&P 500" / "SPX" | `SPY` | yfinance | etf |
| "high yield spread" / "HY OAS" | `BAMLH0A0HYM2` | FRED | macro |
| "investment grade spread" / "IG OAS" | `BAMLC0A0CM` | FRED | macro |
| "fed funds" / "policy rate" | `DFF` | FRED | macro |
| "VIX" / "fear index" | `VIXCLS` | FRED | macro |
| "long bond" / "TLT" | `TLT` | yfinance | etf |
| "bitcoin" / "BTC" | `BTCUSDT` | binance | crypto |
| "euro" / "EUR/USD" | `EURUSD=X` | yfinance | fx |
| "gold" | `GLD` | yfinance | etf |
| "oil" | `USO` | yfinance | etf |

For unrecognised terms, `resolve_strict()` raises `ValueError` with suggestions — surface them.
# __CONTINUE_HERE__
