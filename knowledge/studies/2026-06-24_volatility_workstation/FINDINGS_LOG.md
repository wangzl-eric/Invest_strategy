# Findings Log — Volatility Workstation

Lightweight running log (playground style). One dated entry per session.

---

### 2026-06-24 — Workstation set up

- Built `vol_data.py` + `notebooks/00_volatility_workstation.ipynb` loading VIX, US Dollar Index, gold
  spot, and gold futures akshare-first at the highest resolution available.
- **akshare coverage reality** (verified live):
  - Gold is fully covered and reliable from any network — spot (`XAU` USD, `Au99.99` CNY), futures
    (`GC` COMEX USD, `AU0` SHFE CNY), and **1-minute SHFE** intraday (`futures_zh_minute_sina`).
  - akshare has **no CBOE VIX** → using FRED `VIXCLS`.
  - US Dollar Index via akshare EastMoney (`index_global_hist_em('美元指数')`) is region-gated and
    hangs from this network → falls back to ICE DXY (`DX-Y.NYB`).
- Notebook executes clean end-to-end (0 errors, 4 plots, 4 tables).
- **Open question to explore:** is gold's safe-haven bid (gold up when VIX spikes) actually present in the
  rolling correlation, or only in tail events? Cells 4–5 are the starting point.

### 2026-06-24 — Added S&P 500, OIS, ON RRP; switched to Plotly

- Added three new instruments to `vol_data.py`:
  - **S&P 500** via akshare `index_us_stock_sina('.INX')` — daily OHLCV back to 2004, Sina (reliable).
    Fallback: yfinance `^GSPC`.
  - **OIS rates**: FRED `SOFR` (from 2018-04) + `EFFR` (from 2000-07), merged on date. SOFR is the
    post-LIBOR OIS benchmark; EFFR gives 18 extra years of overnight rate history.
  - **ON RRP**: FRED `RRPONTSYD` — Fed Overnight Reverse Repo facility usage in $B (from 2003-02).
    Peaked at ~$2,554B in late 2022, now near zero.
- **All charts converted from matplotlib to Plotly** — interactive zoom, hover, pan. 9 Plotly figures
  in the notebook.
- New analysis sections: correlation heatmap, S&P vs VIX inverted overlay, ON RRP drain vs equity rally.
- **akshare does NOT carry US OIS/SOFR or Fed ON RRP** — these are FRED-only series.
- **Open question:** does the ON RRP drain → equity rally relationship hold up formally (lead/lag, Granger)?

<!-- Add new dated entries above this line as you research. -->
