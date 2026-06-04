# Paper Notes: Stock Prices, Earnings, and Expected Dividends

**Authors:** Campbell, John Y. & Shiller, Robert J.
**Year:** 1988
**Journal:** Journal of Finance, Vol. 43, No. 3, pp. 661–676
**Date Read:** 2026-03-30
**Scores:** Credibility 5 | Relevance 4 | Actionability 4

---

## Core Thesis

Stock prices contain information about future returns, not future earnings growth. At long horizons (5–10 years), valuation ratios — specifically the Cyclically Adjusted Price-to-Earnings ratio (CAPE) and the dividend-price ratio (D/P) — explain a substantial fraction of subsequent real returns. The paper formalises this using a log-linear present value decomposition (the **Campbell-Shiller decomposition**), which shows that price variation must reflect either variation in expected future returns or expected future dividend/earnings growth. Empirically, nearly all of the predictable variation is attributed to time-varying discount rates (expected returns), not to earnings or dividend news. This is the central insight: **high valuations signal low future returns, not high future earnings.**

---

## Key Findings

| Signal | Horizon | Approximate R² (in-sample) |
|--------|---------|----------------------------|
| CAPE (P / 10yr avg real EPS) | 1-year | ~1–3% |
| CAPE | 5-year | ~20–25% |
| CAPE | 10-year | ~35–40% |
| Dividend-price ratio (D/P) | 1-year | ~2–4% |
| Dividend-price ratio (D/P) | 10-year | ~25–30% |
| Short-horizon P/E (current-year EPS) | 1-year | near zero |

- CAPE dominates single-year P/E because it smooths cyclical earnings swings; a recession year produces an artificially elevated P/E that adds noise.
- D/P also predicts but is somewhat less stable than CAPE across structural shifts in payout policy (buybacks replacing dividends post-1980s).
- Variance decomposition result: virtually none of the variance in log price-dividend ratios is explained by news about future dividend/earnings growth; nearly all reflects news about future returns. This reframes Shiller's (1981) excess volatility finding — prices are volatile because expected returns are volatile, not because cashflows are.


---

## Methodology

### Data
- **Source:** Robert Shiller's long-run U.S. equity dataset, assembled for this paper; now public at `http://www.econ.yale.edu/~shiller/data.htm`
- **Sample:** 1871–1986 (~115 years of annual observations)
- **Series:** S&P Composite Index (price, dividends, earnings), CPI for real deflation

### VAR Framework
The authors estimate a first-order Vector Autoregression:

$$z_t = A z_{t-1} + \varepsilon_t$$

where $z_t$ contains the log dividend-price ratio and log earnings growth. The VAR is used to compute multi-year expectations as linear functions of current state variables, enabling a clean decomposition of unexpected returns into a cashflow-news component and a discount-rate-news component.

### Log-Linearization (the Methodological Contribution)
Campbell and Shiller derive a log-linear approximation to the present value identity:

$$p_t - d_t \approx \text{const} + \sum_{j=1}^{\infty} \rho^j (\Delta d_{t+j} - r_{t+j})$$

where $\rho \approx 0.96$ is a log-linearization constant (ratio of price to price-plus-dividend). This identity holds by construction; the empirical question is which term on the right drives the left-hand side. Combined with the VAR, they compute each term's variance contribution. Result: discount-rate news dominates overwhelmingly.

### 10-Year Averaging Rationale
Using a 10-year moving average of real EPS as the CAPE denominator serves two purposes:
1. Averages out business cycle fluctuations — recession-year EPS collapses inflate single-year P/E artificially
2. Approximates "trend" or "fundamental" earnings, making the ratio comparable across cycles


---

## The CAPE Signal Construction

**Exact formula:**

$$\text{CAPE}_t = \frac{P_t^{\text{real}}}{\frac{1}{10} \sum_{i=0}^{9} E_{t-i}^{\text{real}}}$$

where $P_t^{\text{real}}$ is the CPI-deflated S&P price and $E_{t-i}^{\text{real}}$ is real EPS lagged $i$ years.

- **Rebalancing:** Annual (January or year-end CAPE reading)
- **Data source:** Shiller's online file `ie_data.xls` — monthly series since 1871, freely downloadable
- **Historical long-run mean:** ~16–17x (subject to debate; structural shifts in ROE, accounting, sector mix may justify a higher modern mean of ~20x)
- **Interpretation:** CAPE above the long-run mean → below-average prospective 10-year real returns; below mean → above-average returns
- **FRED proxy:** No native FRED series for CAPE. Proxies: `MULTPL/SHILLER_PE_RATIO_MONTH` via Nasdaq Data Link (formerly Quandl); or direct CSV from Shiller's site. FRED does carry `SP500` and earnings components separately.

---

## Forecasting Horizon Dependence

The near-zero short-horizon R² and substantial long-horizon R² arise from mean-reversion dynamics:

- **1-year:** Idiosyncratic return variance (~15–20% annualised vol) overwhelms the signal. CAPE changes slowly; its forecast of the 1-year return is swamped by noise.
- **5-year:** Mean-reversion dominates. Overvalued markets begin correcting; the negative CAPE-return correlation becomes detectable.
- **10-year:** The full mean-reversion cycle is largely captured. Most transitory valuation premium or discount has unwound.
- **Intuition:** If valuations are stationary (mean-reverting), then high CAPE must eventually resolve via (a) lower future prices, (b) higher future earnings, or (c) lower future returns — and the variance decomposition shows (c) and (a) dominate; earnings growth does not systematically accelerate after low-CAPE periods.
- **Implication for implementation:** CAPE is a **strategic / tactical asset allocation** signal, not a trading signal. Holding periods must be measured in years, not months.


---

## Connection to Dividend Discount Model

The Gordon Growth Model (single-stage DDM):

$$P_0 = \frac{D_1}{r - g} \implies r = \frac{D_1}{P_0} + g$$

Campbell-Shiller generalises this. The **earnings yield** $E/P$ (inverse of CAPE) is a direct proxy for the **Equity Risk Premium (ERP)** under the assumption that real earnings grow at a stable long-run trend:

$$\text{ERP}_{\text{forward}} \approx \frac{\overline{E}_{10\text{yr}}}{P} - r_f^{\text{real}} + g_{\text{real}}$$

where $g_{\text{real}} \approx 1.5\%$ (long-run real EPS CAGR, Dimson-Marsh-Staunton) and $r_f^{\text{real}}$ is the real risk-free rate (TIPS yield or deflated T-bill).

- The VAR decomposition closes the loop: high $P/D$ (low D/P) is almost entirely explained by low expected future returns, not high expected dividend growth. Therefore CAPE-based ERP forecasts are internally consistent with the present value identity — they are not just empirical regularities but theoretically grounded.
- When CAPE is at 30x, the earnings yield is ~3.3%. If real risk-free is 2% and real growth is 1.5%, the implied ERP is ~2.8% — well below the historical average of ~4–5%, suggesting equities are expensive relative to bonds.

---

## Out-of-Sample Performance

### Post-1988 Record
- **1990s bull market:** CAPE rose from ~15 (1988) to >40 by late 1999. The model predicted dramatically below-average 10-year real returns from 1999 onward.
- **2000–2010 outcome:** S&P 500 delivered approximately −1% to 0% real annualised return over the decade. CAPE's directional call was correct and quantitatively meaningful.
- **2009 trough:** CAPE fell to ~13, implying above-average prospective returns. The subsequent decade (2010–2020) delivered ~13% nominal annualised — consistent with the model's direction.
- **Post-2010 elevated CAPE:** CAPE has remained above 25 for most of the period since 2013, implying below-average 10-year returns. Realised returns have been above average — the main ongoing challenge to the model (low-rate environment, structural shift in profit margins, index composition shift toward asset-light tech).

### The 1990s "Non-Failure"
During 1995–1999, CAPE signalled expensive markets yet prices continued to rise sharply. This is not a model failure in the forecasting sense — CAPE predicts 10-year forward returns, not 1-year. Investors who exited in 1996 missed 4 more years of gains but were vindicated by 2003. **CAPE is not a timing tool; it is a 10-year return forecaster.**

---

## Failure Modes & Limitations

1. **Structural breaks in earnings accounting:** Post-1990s adoption of GAAP write-downs, stock-based compensation expensing, and goodwill impairment rules all depress reported EPS relative to economic earnings, mechanically inflating CAPE. Adjusted earnings (operating EPS, NIPA profits) tell a less extreme story.
2. **Share buybacks replacing dividends:** The D/P signal is structurally broken post-1990 because firms return capital via buybacks rather than dividends, making D/P artificially low and not comparable to pre-1980 history.
3. **Survivorship bias:** The 1871–1986 U.S. dataset benefits from survivorship — the U.S. is the winner economy. Global evidence (Goyal-Welch 2008, Dimson-Marsh-Staunton) shows weaker and more variable predictability.
4. **Low predictability at short horizons:** R² near zero at 1-year makes CAPE useless for tactical trading. A strategy acting on CAPE monthly would be indistinguishable from noise.
5. **Regime dependence:** The predictability relationship is estimated over 115 years with major structural changes (Gold Standard, Great Depression, WWII price controls, Bretton Woods, stagflation, QE). The slope coefficient may not be stable across sub-periods.
6. **Real-time data problem:** In real time, earnings are revised, CPI is revised, and the 10-year average denominator changes. Goyal & Welch (2008) show that most return predictors — including D/P — fail in recursive OOS tests using only data available at the time of prediction.
7. **Interest rate interaction:** A high-CAPE / low-rate environment (post-2010) may rationally justify higher valuations via lower discount rates. CAPE does not control for the level of real interest rates, which Shiller himself has acknowledged ("CAPE-adjusted for rates" or FARE/ECY frameworks).

---

## Connection to Ilmanen Ch7 (Equity Risk Premium — Forward-Looking ERP Measures)

Ilmanen's Chapter 7 in *Expected Returns* (2011) treats CAPE as one of three forward-looking ERP measures alongside the DDM-implied ERP and the Fed Model. The connection points:

- **CAPE earnings yield as ERP proxy:** Ilmanen uses $1/\text{CAPE} - r_f^{\text{real}}$ as a direct ERP estimate. Campbell-Shiller (1988) is the theoretical and empirical foundation for this choice.
- **Horizon consistency:** Ilmanen emphasises that valuation-based ERP estimates are 7–10 year forecasts, not 1-year forecasts — exactly the horizon dependence documented by Campbell-Shiller.
- **Discount rate vs cashflow decomposition:** Ilmanen's discussion of why ERP varies over time maps directly onto the Campbell-Shiller VAR decomposition — the answer is time-varying discount rates, not time-varying growth expectations.
- **Regime framing:** Ilmanen overlays CAPE with the real bond yield to construct a "equity vs bond" relative value framework (the excess CAPE yield, ECY = 1/CAPE − 10yr real yield). This addresses failure mode #7 above — adjusting for the rate environment.
- **Ch7 notebook (this study):** `01_equity_risk_premium.ipynb` in this study folder implements a CAPE-based ERP panel using FRED data. Campbell-Shiller (1988) is the direct theoretical input to that notebook.

---

## Codebase Check

### `backtests/strategies/signals.py` — Valuation Signals
**Finding: No valuation or CAPE signals exist.** The registry contains: `MomentumSignal`, `CarrySignal`, `MeanReversionSignal`, `VolatilitySignal`, `ATRSignal`, `RSISignal`, `MACDSignal`, `BollingerPositionSignal`, `SMACrossoverSignal`, `VolumeSignal`. All are price/volume/carry-based. No `EarningsYieldSignal`, `CAPESignal`, or `ValuationSignal` class exists (`signals.py` lines 807–827, `__all__` list).

**Implication:** A `CAPESignal` or `EarningsYieldSignal` would need to be built from scratch. It would require fundamental data (EPS history) not currently in the Parquet lake — a non-trivial data pipeline addition.

### `quant_data/connectors/` — FRED & Shiller Data
**Finding: No dedicated Shiller CAPE connector exists.** Connectors present: `stooq.py` (free OHLCV), `polygon.py` (paid OHLCV), `ecb_fx.py` (FX rates), `binance_public.py` (crypto). No FRED connector module.

**However:** `quant_data/api.py` (lines 139–219) implements `_fetch_fred()` using `pandas_datareader.DataReader(..., "fred", ...)` keyed on `FRED_API_KEY`. `quant_data/ticker_map.py` (lines 29–96) maintains a `_FRED_ENTRIES` list with FRED series shortcuts. **CAPE is not in this list** — but the infrastructure to add it exists.

**Concrete path to CAPE data:**
- Option A: Add `MULTPL/SHILLER_PE_RATIO_MONTH` to `_FRED_ENTRIES` in `quant_data/ticker_map.py` (requires Nasdaq Data Link key, not FRED key)
- Option B: Download Shiller's `ie_data.xls` directly and ingest via `quant_data/io/parquet_writer.py` into the Parquet lake
- Option C: Derive CAPE from S&P 500 prices (Stooq/Polygon) + FRED earnings series `SP500EPS` — requires custom 10-year averaging logic

### `memory/knowledge/KNOWLEDGE_EQUITY.md` — Existing CAPE/ERP Entries
**Finding: No CAPE or ERP entries exist.** The knowledge base covers: momentum, quality, low-volatility, sector-rotation, crowding. No `valuation` topic section. This paper note should seed a new `valuation` topic in `KNOWLEDGE_EQUITY.md`.

### `research/STRATEGY_TRACKER.md` — Active Valuation Strategies
**Finding: No active strategy uses valuation signals.** The tracker references "valuation" only in the context of:
- QUAL ETF P/E (27.84x) as a crowding/risk flag for the Quality + Safe-Haven Overlay strategy (`STRATEGY_TRACKER.md` line 266)
- GS Defensive Sector Rotation rejection citing a "6-month valuation pipeline build" as a blocker (line 237)

**No strategy is currently using CAPE, earnings yield, or ERP-based signals as primary alpha.** This is a gap — and an opportunity given the data infrastructure partially exists.

---

## Implementability

### Data Acquisition
- **Primary:** Download Shiller's `ie_data.xls` directly from `http://www.econ.yale.edu/~shiller/data.htm` — monthly since 1871, free, no API key required. Contains price, dividends, earnings, CPI, 10yr Treasury yield, and pre-computed CAPE.
- **Secondary:** `quant_data/api.py` `_fetch_fred()` can pull `SP500` price and `SP500EPS` from FRED to construct a forward-looking version with more recent data.
- **Ingest path:** Parse `ie_data.xls` → compute real price, real EPS, 10yr rolling average → write to Parquet via `quant_data/io/parquet_writer.py`

### Signal Use Cases in This Codebase
1. **ERP overlay / regime filter:** Use CAPE earnings yield vs 10yr real yield (ECY) as a binary regime flag — `ECY > 0` (equities cheap vs bonds) → risk-on; `ECY < 0` → risk-off. Can be overlaid on any existing signal (MomentumSignal, CarrySignal).
2. **Tactical asset allocation weight:** Scale equity allocation by percentile rank of CAPE (inverted) over a rolling 20-year window. Lower weight at high CAPE, higher weight at low CAPE.
3. **Return forecasting for strategy evaluation:** Use CAPE-implied 10yr ERP as the hurdle rate input in `backtests/stats/minimum_backtest.py` MinBTL calculations — current hurdle rate assumptions may be too generous if CAPE implies low prospective returns.

### Fit with Existing Infrastructure
- `BaseSignal.compute()` interface in `backtests/strategies/signals.py` can accommodate a `CAPESignal` if fundamental data is added to the Parquet lake
- The signal would need to accept a separate `fundamentals` DataFrame (not just `prices`) — requires a minor interface extension
- Alternatively, implement as a standalone ERP module in `quant_data/analytics.py` (which already exists as a new file in this branch) rather than a `BaseSignal` subclass

---

## Key Quotes

> "We find that the stock price-earnings ratio and the dividend-price ratio both forecast stock returns, but that the price-earnings ratio with earnings averaged over ten years performs best." (p. 661)

> "The variance of the log price-dividend ratio is almost entirely accounted for by changing forecasts of future returns rather than changing forecasts of future dividend growth." (p. 668)

> "Our results suggest that the stock market may be excessively volatile relative to fundamentals, in the sense that fluctuations in stock prices are hard to justify by reference to subsequent dividend news." (p. 675)

---

## Follow-Up Papers

| Paper | Authors | Year | Why It Matters |
|-------|---------|------|----------------|
| Dividend yields and expected stock returns | Fama & French | 1988 | Parallel paper on D/P predictability; same-year companion to Campbell-Shiller |
| The equity premium: A puzzle | Mehra & Prescott | 1985 | Why is ERP so high? Sets the stage for return forecasting literature |
| Predicting excess stock returns out of sample: Can anything beat the historical average? | Goyal & Welch | 2008 | The critical OOS failure paper — shows CAPE and D/P fail in real-time recursive forecasting |
| Presidential address: Discount rates | Cochrane | 2011 | Definitive synthesis: all asset price variation is discount rate variation, not cashflow variation |
| The term structure of the risk-return tradeoff | Campbell & Viceira | 2005 | Extends the VAR framework to multi-asset long-horizon allocation |
| Excess cyclically adjusted P/E (ECAY) | Siegel | 2016 | Argues CAPE is overstated due to accounting changes; proposes NIPA earnings adjustment |
| An examination of long-horizon return predictability | Ang & Bekaert | 2007 | Challenges long-horizon predictability; argues short-horizon D/P is more robust than 10yr |

---

## Tags

`[BOOK/ARTICLE]` `equity` `valuation` `CAPE` `ERP` `return-forecasting` `present-value` `VAR` `long-horizon` `Campbell-Shiller` `2026-03-30`
