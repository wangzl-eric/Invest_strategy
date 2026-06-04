# Paper Notes: The Cross-Section of Volatility and Expected Returns

**Authors:** Ang, Hodrick, Xing, Zhang
**Year:** 2006
**Journal:** Journal of Finance, Vol. 61, No. 1, pp. 259–299
**Date Read:** 2026-03-30
**Scores:** Credibility 5 | Relevance 4 | Actionability 4

---

## Core Thesis

Two empirically distinct anomalies link volatility to the cross-section of expected equity returns — both in the *wrong* direction relative to standard risk-pricing intuition:

1. **Aggregate volatility risk (VIX-beta effect):** Stocks with high sensitivity to innovations in aggregate market volatility earn significantly *lower* future returns. They are priced as expensive hedges against volatility uncertainty.
2. **Idiosyncratic volatility puzzle (IVOL effect):** Stocks with high idiosyncratic volatility — the residual from a Fama-French 3-factor model — earn significantly *lower* future returns. This is the opposite of what Merton (1987) predicts and constitutes a genuine pricing anomaly.

Both effects survive controlling for size, value, momentum, liquidity, and turnover. They are statistically and economically large. The paper demonstrates they are distinct — a stock can score high on one without scoring high on the other.

---

## Key Findings

| Effect | Metric | Magnitude |
|---|---|---|
| VIX-beta | Monthly return spread (low minus high VIX-beta quintile) | **~+1.00% per month** |
| IVOL | Monthly return spread (low minus high IVOL quintile) | **~+1.06% per month** |
| IVOL | 4-factor alpha of high-IVOL quintile | **−1.31% per month** (t ≈ −3.09) |
| IVOL international | G7 markets | Negative in all G7 countries |

Both effects survive: market beta, size, BM ratio, momentum, liquidity, turnover, co-skewness, and maximum daily return controls.

---

## Methodology

### Data & Sample
- US equities from CRSP, July 1963 – December 2000 (monthly)
- Accounting data from Compustat for Fama-French factors
- VIX constructed from S&P 100 options (VXO) for the full sample

### VIX Sensitivity Estimation

For each stock $i$, a rolling 5-year window (minimum 24 months) time-series regression:

$$r_{i,t} = \alpha_i + \beta^{MKT}_i r^{MKT}_t + \beta^{\Delta VIX}_i \Delta VIX_t + \epsilon_{i,t}$$

where $\Delta VIX_t$ is the monthly change in the VIX index. $\beta^{\Delta VIX}_i$ is the VIX-beta. Estimated monthly on a rolling window; used to sort stocks into quintiles the following month.

### IVOL Measurement

For each stock, daily returns *within* each month are regressed on the FF3 model:

$$r_{i,d} = \alpha_i + \beta^{MKT}_i r^{MKT}_d + \beta^{SMB}_i SMB_d + \beta^{HML}_i HML_d + \epsilon_{i,d}$$

IVOL is the standard deviation of daily residuals $\epsilon_{i,d}$ within the month. This backward-looking current-month IVOL predicts *next-month* returns — no look-ahead bias, no multi-month estimation window required.

### Cross-Sectional Tests

Fama-MacBeth (1973) regressions of individual stock returns on lagged characteristics. Reported coefficients are time-series averages of monthly cross-sectional slopes; $t$-statistics use Newey-West (1987) standard errors.

---

## The VIX Sensitivity Effect

Stocks with **high $\beta^{\Delta VIX}$** — those that move positively with VIX innovations — earn **lower expected returns**.

**Economic intuition:** These stocks are natural hedges against aggregate uncertainty. Risk-averse investors (pension funds, institutions) demand them as insurance against volatility regimes. The resulting excess demand bids up prices and compresses future returns. This is a *rational* ICAPM story: investors willingly accept below-average returns in exchange for hedging value.

**Magnitude:** The spread between the lowest and highest VIX-beta quintile is approximately **+1% per month** (~+12% annualised) in favour of low-VIX-beta stocks. The price of aggregate volatility risk $\lambda_{\Delta VIX}$ is estimated to be **negative and significant** in cross-sectional regressions — bearing aggregate vol risk earns a positive premium; hedging against it earns a negative premium.

---

## The Idiosyncratic Volatility Puzzle

High-IVOL stocks earn **significantly lower** returns than low-IVOL stocks.

**Why is this puzzling?**
- CAPM / APT: idiosyncratic risk is fully diversifiable → should be *unpriced* (zero coefficient)
- Merton (1987) incomplete markets: undiversified investors require compensation → high IVOL should earn *higher* returns

Ang et al. find the opposite. Key statistics:
- Monthly spread: approximately $-1.06\%$ per month (high minus low IVOL quintile)
- 4-factor alpha of high-IVOL quintile: $-1.31\%$ per month ($t \approx -3.09$)
- Not subsumed by: size, value, momentum, liquidity, turnover, co-skewness, maximum daily return, bid-ask spread

This is among the largest and most robust anomalies documented in the equity return cross-section.

---

## Are These the Same Effect?

**Paper's answer: No — they are empirically distinct.**

Horse-race Fama-MacBeth regressions including both $\beta^{\Delta VIX}$ and IVOL simultaneously show both remain significant with full magnitudes. Double-sorted portfolios confirm:
- Within low-IVOL stocks, the VIX-beta effect still operates
- Within low-VIX-beta stocks, the IVOL effect still operates

Both involve volatility thematically but measure different constructs: VIX-beta is a *systematic* factor exposure; IVOL is *idiosyncratic* residual dispersion that is by construction orthogonal to the FF3 factors. Both predict lower returns for higher volatility exposure but through separate economic channels.

---

## Risk vs Mispricing

### Risk-based explanation for VIX-beta (clean)

The VIX-beta effect fits rational ICAPM pricing. Aggregate volatility is an ICAPM state variable (Merton 1973): when vol rises, expected returns rise and prices fall — bad news for long-horizon investors. Stocks that hedge this (positive VIX-beta) are valuable insurance, priced at a premium, earning lower returns. The mechanism is the same as why long-duration treasuries earn less than equities despite being "safe" — investors pay for the hedge.

### Mispricing explanations for IVOL (contested)

**1. Lottery preference (Barberis & Huang 2008; Kumar 2009)**
High-IVOL stocks have positively skewed return distributions. Retail investors overweight small probabilities of large gains (cumulative prospect theory). Excess demand bids up prices and reduces future returns. Consistent with concentration of the IVOL puzzle in small-cap, low-price, high-retail-ownership stocks.

**2. Short-sale constraints + disagreement (Miller 1977)**
When investors disagree and short selling is constrained, only optimists hold the stock. High-IVOL generates more disagreement. Prices reflect optimist valuations → overpricing → low future returns. Stronger where short-sale costs are high and institutional ownership is low.

**3. Limits to arbitrage (Stambaugh, Yu & Yuan 2015)**
IVOL proxies for arbitrage risk — the idiosyncratic risk that deters arbitrageurs from correcting mispricing. High IVOL → harder to arbitrage → overpricing persists → lower returns. A self-reinforcing dynamic.

**4. Information uncertainty (Zhang 2006)**
High-IVOL stocks have greater information uncertainty. Combined with investor overconfidence, this amplifies momentum effects and generates subsequent underperformance.

The paper does not fully adjudicate. Literature consensus: mispricing (lottery demand + short-sale constraints) for IVOL; rational hedging demand for VIX-beta.

---

## International Evidence

The IVOL analysis is extended to **G7 markets** (US, UK, Japan, France, Germany, Canada, Italy) using MSCI country-level data:

- The IVOL puzzle holds in **all G7 countries** individually
- Effect is statistically significant in most individual markets
- The cross-country consistency rules out US-specific data-mining as the explanation
- Effect magnitude varies by country but the direction is uniformly negative
- Particularly strong in Japan and the UK alongside the US

This international robustness significantly strengthens the paper's claim. A pure noise result would not replicate across seven independent markets with different investor bases, regulations, and market microstructures.

---

## Failure Modes & Limitations

- **Sample period ends 2000:** The paper predates the 2008 crisis and post-GFC low-vol environment. The IVOL puzzle has been documented as weaker or reversed in some post-2000 subperiods (Hou & Loh 2016 decomposition).
- **No transaction costs:** The IVOL quintile spread is concentrated in small, illiquid, high-turnover stocks. After realistic bid-ask spreads and market impact, the net alpha is substantially smaller. This is a known limitation and a key reason IVOL is hard to trade in practice.
- **Short-sale costs:** The IVOL long-short requires shorting the highest-IVOL quintile — precisely the stocks where short-sale costs are highest. Net-of-borrowing-cost alphas are significantly reduced.
- **Factor model sensitivity:** IVOL is measured relative to FF3. With FF5 (adding profitability and investment) or a 6-factor model, some of the IVOL effect is absorbed. The puzzle is smaller but not eliminated.
- **VIX-beta instability:** Rolling 5-year betas are noisy estimators, especially for individual stocks. The VIX-beta sort has high classification noise month-to-month.
- **No out-of-sample test:** The paper does not hold out a post-estimation test period. Subsequent work (e.g., Bali & Cakici 2008) shows the IVOL effect is sensitive to the exact methodology and sample.

---

## Connection to Ilmanen: Ch15 (VRP) + Ch16 (Equity Factors)

**Ch15 — Volatility Risk Premium:**
The VIX-beta result is the *cross-sectional* counterpart to the aggregate VRP documented in Ch15. Ch15 shows that *selling* aggregate vol (short VIX futures, variance swaps) earns a premium because vol buyers are willing to pay for insurance. Ang et al. show the same insurance demand operates in the *equity cross-section*: stocks that provide vol insurance (high VIX-beta) are overpriced and earn negative excess returns. The mechanisms are mirror images.

**Ch16 — Equity Factors / Low-Vol Anomaly:**
Ilmanen Ch16 discusses the low-volatility anomaly (BAB — Betting Against Beta, Frazzini & Pedersen 2014) as a related phenomenon. The IVOL puzzle is a close cousin: both show that high-risk stocks earn lower returns than standard theory predicts. Ch16 attributes low-vol outperformance to leverage constraints (forced buyers of high-beta stocks), lottery demand, and benchmarking distortions — the same mechanisms invoked for IVOL. Ang et al. 2006 is the foundational empirical paper that Ilmanen Ch16 draws on for the idiosyncratic side of the anomaly.

**Key distinction:** Ch15 VRP is about *time-series* variation in aggregate vol compensation; Ang et al. is about *cross-sectional* sorting on vol sensitivity. Both are unified by the idea that volatility insurance is expensive and those who provide it earn lower average returns.

---

## Codebase Check

### `backtests/strategies/signals.py` — volatility signals

**`VolatilitySignal` (line 116–141):** Implements historical vol as a signal by computing rolling return standard deviation and *inverting* it (`signal = -vol`), so low vol = high signal. The docstring says "Lower vol = higher expected return (contrarian)." This is directionally aligned with the IVOL puzzle (low IVOL → higher returns) but the implementation is a simple 21-day realised vol, not IVOL from FF3 residuals. It operates on raw price returns, not factor-adjusted residuals — so it mixes systematic and idiosyncratic vol together.

**`ATRSignal` (line 144–171):** Also inverts ATR so low ATR = buy signal. Same directional alignment, same limitation: no factor adjustment.

**No VIX-beta signal exists.** There is no signal that estimates a stock's sensitivity to $\Delta VIX$ or any aggregate volatility factor. The VIX-beta effect from Ang et al. is entirely unimplemented.

**No idiosyncratic vol (IVOL) signal exists.** The `VolatilitySignal` computes total realised vol, not residual vol from a factor regression. True IVOL requires regressing daily returns on FF3 factors and taking the residual standard deviation — this is not implemented anywhere in `backtests/`.

### `data/market_data/prices/`

Both required data files are present:
- `vix_daily.parquet` — VIX daily series (confirmed present)
- `vix3m_daily.parquet` — VIX 3-month series (confirmed present)
- `equities.parquet` — equity prices (confirmed present)

All three files needed to implement both effects are available in the data lake.

### `backtests/runners/`

No vol-sorted strategies exist. `momentum.py` implements a pure price-momentum runner. `portfolio_opt.py` implements a mean-variance optimisation runner. Neither sorts on vol, IVOL, or VIX-beta.

### `memory/knowledge/KNOWLEDGE_VOL.md`

The existing knowledge base covers VRP, VIX regime, vol-targeting, and tail-risk but has **no entry for the IVOL cross-sectional puzzle or the VIX-beta cross-sectional effect.** The closest entry is in `vrp` topic: "VRP reflects compensation for variance risk" — thematically related but a different mechanism (time-series vs cross-section).

### Rejected VIX Regime strategy (`vix_regime_2026-03-15_rejected`)

The rejected VIX Regime strategy used VIX *levels* as a regime classifier to gate a long/short equity position — a time-series overlay strategy. This is a different construct from Ang et al.'s VIX-*beta* sort (sensitivity to VIX *innovations* in the cross-section). The rejection reasons (MinBTL 3,968yr, spanning alpha t=−0.18) do not invalidate the cross-sectional VIX-beta effect documented here.

---

## Implementability

### IVOL signal — fully implementable with current data

`equities.parquet` contains daily OHLCV for the equity universe. The FF3 factor series (MKT, SMB, HML) can be downloaded from Ken French's data library or approximated from the existing equity universe. Implementation steps:

1. Load daily returns from `equities.parquet`
2. Load FF3 daily factors (French data library or approximate from universe)
3. For each stock, each month: regress daily returns on FF3 factors using that month's daily observations
4. Compute standard deviation of daily residuals → IVOL for that month
5. Sort stocks into quintiles; long Q1 (low IVOL), short Q5 (high IVOL)
6. Hold for one month, rebalance monthly

This fits directly into the existing `BaseSignal` interface in `backtests/strategies/signals.py`. A new `IVOLSignal` class would:
- Accept a factor returns DataFrame alongside prices
- Run rolling monthly OLS on daily data
- Return the negative residual standard deviation as signal (so high signal = low IVOL = long)

### VIX-beta signal — fully implementable with current data

`vix_daily.parquet` and `equities.parquet` are both present. Implementation:

1. Compute monthly VIX changes ($\Delta VIX_t$) from `vix_daily.parquet`
2. For each stock, rolling 60-month window: regress monthly stock returns on market return + $\Delta VIX$
3. Extract $\beta^{\Delta VIX}_i$ coefficient
4. Sort into quintiles; long Q1 (low / negative VIX-beta), short Q5 (high VIX-beta)
5. Rebalance monthly

**Practical constraints to flag:**
- The equity universe in `equities.parquet` is likely a small curated set, not the full CRSP universe. The IVOL and VIX-beta effects are strongest in small-cap stocks — if the universe is large-cap-only (e.g., SPY components), effect magnitudes will be attenuated.
- Transaction costs: high-IVOL stocks tend to be illiquid. Cost modelling via `backtests/costs/` is essential before drawing conclusions.
- Short-sale constraints: the long-short IVOL strategy requires shorting high-IVOL names. With IBKR, stock borrow availability and rates must be checked.
- FF3 factors: if not available locally, need a data pipeline addition. French data library CSV is publicly available and easy to ingest.

---

## Key Quotes

> "We find that stocks with high sensitivities to innovations in aggregate volatility have low average returns... The price of aggregate volatility risk is negative and significant."

> "Stocks with high idiosyncratic volatility have abysmally low average returns... This effect is not explained by exposure to aggregate volatility risk."

> "The value-weighted average return of stocks in the highest IVOL quintile is −1.06% per month lower than stocks in the lowest IVOL quintile."

> "The puzzle is robust to controls for size, value, momentum, liquidity, volume, turnover, bid-ask spreads, coskewness, and dispersion in analyst forecasts."

---

## Follow-Up Papers

| Paper | Relevance |
|---|---|
| Ang, Hodrick, Xing, Zhang (2009) — *High Idiosyncratic Volatility and Low Returns: International and Further U.S. Evidence* | JFE follow-up; deeper international evidence; G7 decomposition |
| Bali & Cakici (2008) — *Idiosyncratic Volatility and the Cross-Section of Expected Returns* | Shows IVOL effect is sensitive to weighting scheme; value-weighted portfolios weaken it |
| Stambaugh, Yu & Yuan (2015) — *Arbitrage Asymmetry and the Idiosyncratic Volatility Puzzle* | Limits-to-arbitrage explanation; short-leg drives IVOL anomaly |
| Hou & Loh (2016) — *Have We Solved the Idiosyncratic Volatility Puzzle?* | Lottery demand (maximum daily return) explains ~50% of IVOL puzzle |
| Frazzini & Pedersen (2014) — *Betting Against Beta* | Related low-risk anomaly; leverage constraints mechanism; BAB factor |
| Baker, Bradley & Wurgler (2011) — *Benchmarking as a Source of Bias Against Low Volatility Investing* | Institutional benchmarking explains why low-vol anomaly persists |
| Barberis & Huang (2008) — *Stocks as Lotteries* | Cumulative prospect theory; lottery preference for positively skewed stocks |






