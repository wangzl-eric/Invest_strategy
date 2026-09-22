# Volatility Workstation

**Created:** 2026-06-24 · **Space:** playground (exploratory, no rigor gates)

A ready-to-go bench for studying **CBOE VIX**, the **US Dollar Index**, **gold (spot + futures)**,
**S&P 500**, **OIS rates (SOFR/EFFR)**, and **Fed ON RRP facility** —
loaded **akshare-first at the highest resolution akshare offers**, with transparent fallbacks.
All charts use **Plotly** (interactive zoom, hover, pan).

## Layout

```
2026-06-24_volatility_workstation/
├── README.md                              # this file
├── vol_data.py                            # data loaders (akshare-first, timeout-guarded, parquet cache)
├── notebooks/
│   └── 00_volatility_workstation.ipynb    # START HERE — loads everything, plots, starter analyses
├── data/                                  # parquet cache (auto-created on first load)
└── FINDINGS_LOG.md
```

## Quick start

```bash
conda activate ibkr-analytics
cd knowledge/studies/2026-06-24_volatility_workstation
jupyter lab notebooks/00_volatility_workstation.ipynb
```

Or in any Python session from this folder:

```python
import vol_data as vd
frames = vd.load_all(start="2018-01-01")
vd.coverage(frames)   # source / resolution / rows / date range per instrument
```

## Data sources (verified live 2026-06-24, akshare 1.18.x)

| Instrument | Loader | Primary source | Resolution | Unit | History from | Fallback |
|---|---|---|---|---|---|---|
| CBOE VIX | `load_vix()` | FRED `VIXCLS` | daily | index | 1990 | — |
| US Dollar Index | `load_usd_index()` | akshare `index_global_hist_em('美元指数')` | daily | index | ~2008 | ICE DXY `DX-Y.NYB` (yfinance) |
| Gold spot | `load_gold_spot()` | akshare `futures_foreign_hist('XAU')` | daily | USD/oz | ~2015 | SGE `Au99.99` (CNY/g) |
| Gold futures | `load_gold_futures()` | akshare `futures_foreign_hist('GC')` (COMEX) | daily | USD/oz | ~2015 | SHFE `AU0` (CNY/g) |
| **Gold intraday** | `load_gold_futures_minute()` | akshare `futures_zh_minute_sina('AU0')` | **1-minute** | CNY/g | rolling window | — |
| **S&P 500** | `load_sp500()` | akshare `index_us_stock_sina('.INX')` | daily | index | 2004 | yfinance `^GSPC` |
| **OIS rates** | `load_ois()` | FRED `SOFR` + `EFFR` | daily | % | 2000 (EFFR) / 2018 (SOFR) | — |
| **ON RRP** | `load_on_rrp()` | FRED `RRPONTSYD` | daily | $B | 2003 | — |
| China QVIX (bonus) | `load_china_qvix()` | akshare `index_option_300etf_qvix` | daily/minute | vol pts | — | — |

### Key notes on data sources
1. **CBOE VIX is not in akshare** — it only carries China's QVIX. We use FRED `VIXCLS`.
2. **S&P 500 via akshare Sina** is reliable back to 2004 with full OHLCV.
3. **OIS**: SOFR is the post-LIBOR benchmark (from 2018-04); EFFR extends the overnight rate history back to 2000.
4. **ON RRP** peaked at ~$2.5T in late 2022 and has since drained to near zero — a key liquidity indicator.
5. **EastMoney endpoints are region-gated** (USDX, QVIX). All akshare calls are timeout-guarded with fallbacks.

## What's in the notebook (Plotly interactive)
1. Load all instruments + coverage table
2. 4×2 instrument dashboard
3. Normalized overlay (rebased to 100) — VIX, USDX, gold, S&P
4. Full-sample correlation heatmap
5. 63-day rolling correlation: gold vs VIX, USDX, S&P
6. Gold return by VIX regime (histogram)
7. OIS rates + ON RRP plumbing panel
8. S&P 500 vs VIX (inverted axis)
9. ON RRP drain vs S&P 500 — liquidity thesis
10. 1-minute SHFE gold intraday + realized vol
11. Bonus: China QVIX
12. Scratch space (all frames pre-loaded)

## Possible next steps
- Promote the reliable akshare gold/SP500 functions into the shared `akshare_global.py` connector catalog.
- Pull intraday VIX/DXY for true high-res vol work (needs a paid/intraday feed — akshare is daily for these).
- Explore the ON RRP drain → equity rally relationship more formally (lead/lag, Granger causality).
