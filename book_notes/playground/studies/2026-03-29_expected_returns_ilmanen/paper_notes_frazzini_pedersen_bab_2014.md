# Paper Notes: Betting Against Beta

**Authors:** Andrea Frazzini, Lasse Heje Pedersen | **Year:** 2014 | **Journal:** Journal of Financial Economics
**Date Read:** 2026-03-30 | **Scores:** Credibility 5 | Relevance 4 | Actionability 4

---

## Core Thesis

The Security Market Line (SML) predicted by CAPM is too flat — empirically, high-beta assets earn *lower* risk-adjusted returns than low-beta assets. This violates CAPM pricing. The mechanism is **leverage aversion**: investors who cannot (or will not) use leverage to amplify returns instead tilt toward high-beta assets to achieve target return levels, bidding up their prices and compressing their future returns. Conversely, low-beta assets are underpriced relative to CAPM predictions. A dollar-neutral, beta-neutral strategy — Betting Against Beta (BAB) — that goes long leveraged low-beta assets and short deleveraged high-beta assets earns large, significant excess returns across virtually every asset class tested.

---

## Key Findings

- **US equities (1926–2012):** BAB earns **0.78%/month** (9.36% annualized) with a Sharpe ratio of **0.70**.
- **International equities:** BAB is profitable in **20 of 20** equity markets tested, with an average Sharpe of ~0.60 across markets. The effect is pervasive and not a data-mining artifact.
- **Cross-asset:** BAB earns positive returns in US Treasuries, international government bonds, corporate bonds, credit indices, equity index futures, commodity futures, and FX — a remarkably broad result.
- **Alpha vs. standard factors:** BAB alpha survives controlling for MKT, SMB, HML, UMD (Carhart 4-factor). The alpha is not subsumed by value or momentum.
- **Crisis behavior:** BAB *crashes* during funding liquidity crises. During 2008–2009, BAB drawdown was severe. This is endogenous: when margin calls force de-leveraging, the very mechanism that sustains BAB unwinds simultaneously, creating crowded-exit risk.
- **Funding liquidity beta:** BAB returns are negatively correlated with the TED spread (a proxy for funding tightness). When liquidity tightens, BAB suffers.
- **Flat SML:** Beta sorts on 10 decile portfolios show a nearly flat — or slightly negative — relationship between realized beta and realized alpha, consistent with a flat SML.

---

## Methodology

### Beta Estimation

Frazzini & Pedersen use a **Dimson-style shrinkage beta** to reduce estimation error:

$$\hat{\beta}_i = \rho \cdot \frac{\hat{\sigma}_i}{\hat{\sigma}_m}$$

where:
- $\hat{\sigma}_i$ = 1-year rolling standard deviation of daily returns for stock $i$
- $\hat{\sigma}_m$ = 1-year rolling standard deviation of daily returns for the market
- $\hat{\rho}$ = 5-year rolling correlation of monthly returns (longer window reduces noise)
- The ratio $\hat{\sigma}_i / \hat{\sigma}_m$ is estimated at **daily** frequency (better precision)
- The correlation $\hat{\rho}$ is estimated at **monthly** frequency (less sensitive to microstructure)

This split-frequency estimator is a practical improvement over OLS beta and is less affected by bid-ask bounce and non-synchronous trading.

Final betas are **shrunk toward 1** using: $\beta^{adj} = 0.6 \cdot \hat{\beta} + 0.4 \cdot 1$, consistent with Vasicek (1973) shrinkage.

### Portfolio Formation

- Stocks ranked by pre-formation beta into deciles (or two halves: above/below median).
- **Long portfolio:** Bottom-beta stocks. Each stock weighted by the **rank** (not equal weight), scaled so portfolio beta = 1 after levering up.
- **Short portfolio:** Top-beta stocks. Weighted by rank, scaled so portfolio beta = 1 after deleveraging down.
- The BAB factor = $r^L / \beta^L - r^S / \beta^S$, where $\beta^L$ and $\beta^S$ are the ex-ante betas of the long and short legs at formation.
- Rebalanced **monthly**.
- Both legs are **self-financing** (dollar-neutral within each leg); overall factor is long-short and beta-neutral.

---

## BAB Factor Construction (Exact)

```
Step 1: Estimate beta for each stock i at month t
  σ_i  = std(daily returns, trailing 1 year)
  σ_m  = std(daily returns, trailing 1 year, market)
  ρ_im = corr(monthly returns, trailing 5 years)
  β_raw = ρ_im × (σ_i / σ_m)
  β_adj = 0.6 × β_raw + 0.4 × 1.0   [shrinkage toward 1]

Step 2: Rank stocks by β_adj, assign rank weights
  z_i = (rank_i − mean_rank) / (sum of absolute deviations)
  Positive z → long portfolio (low-beta stocks)
  Negative z → short portfolio (high-beta stocks)

Step 3: Scale each leg so its portfolio beta = 1
  w^L = z^L / β^L_portfolio    [leverage low-beta leg up]
  w^S = z^S / β^S_portfolio    [deleverage high-beta leg down]

Step 4: BAB return at t+1:
  r_BAB = (1/β^L) × r^L − (1/β^S) × r^S

Key property: Factor is beta-neutral by construction. Any market move
cancels across long and short legs. Pure alpha from mispricing of beta.
```

The leverage applied to the long leg can be substantial — if median low-beta stocks have $\beta \approx 0.5$, they are leveraged $2\times$ to achieve beta = 1. This is the precise channel through which funding constraints matter: real-world investors with margin limits cannot execute this cleanly.

---

## Economic Mechanism

The theory builds on a **leverage-constrained CAPM** (Pedersen 2009, Black 1972). Key steps:

1. **Heterogeneous constraints:** Some investors (individuals, many mutual funds, pension funds with mandate constraints) cannot use leverage. To hit a return target above the risk-free rate, they overweight high-beta assets.

2. **Equilibrium pricing distortion:** Excess demand for high-beta assets pushes their prices up and their *expected* excess returns down. Low-beta assets are relatively neglected, so their prices are lower and expected returns higher than CAPM predicts.

3. **The SML tilts:** In equilibrium, the empirical SML is flatter than the theoretical CAPM SML. Low-beta stocks plot *above* the SML (positive alpha); high-beta stocks plot *below* (negative alpha).

4. **Margin requirements as the binding constraint:** In Pedersen's model, the tightness of leverage constraints is proxied by the **TED spread** (3-month LIBOR minus T-bill rate). Higher TED → tighter constraints → greater pricing distortion → higher future BAB returns (the effect strengthens when constraints bind hardest).

5. **Crisis dynamics:** During crises, funding liquidity evaporates. Leveraged BAB investors face margin calls, are forced to unwind long low-beta / cover short high-beta positions simultaneously. This mechanical unwind is the BAB crash — the strategy suffers exactly when the economic stress it was designed to exploit becomes acute. This is the central risk of the strategy.

---

## Cross-Asset Evidence

| Asset Class | BAB Sharpe (approx.) | Notes |
|---|---|---|
| US Equities | 0.70 | 1926–2012, strongest single-market result |
| International Equities | ~0.60 avg | 20/20 markets profitable |
| US Treasuries | Positive | Low-duration bonds outperform on risk-adj. basis |
| International Govt Bonds | Positive | Consistent across G10 |
| Corporate Bonds / Credit | Positive | Low-spread bonds outperform on risk-adj. |
| Equity Index Futures | Positive | Low-beta country indices outperform |
| Commodity Futures | Positive | Lower-beta commodities |
| FX | Positive | Lower-volatility currencies |

The cross-asset generality is the paper's strongest empirical contribution. The same leverage-aversion mechanism applies wherever investors face borrowing constraints and substitute toward higher-risk instruments to achieve return targets.

---

## Failure Modes & Limitations

1. **Funding liquidity crisis (the BAB crash):** The strategy's worst episodes coincide exactly with periods of acute funding stress — 2008 GFC, LTCM 1998, dot-com unwind. When margin calls hit leveraged investors simultaneously, the low-beta long leg is force-sold and the high-beta short leg is force-covered. BAB can lose 15–20% in a single month during these episodes. This is a systematic, non-diversifiable risk within the strategy.

2. **Leverage is not free:** The long leg requires real leverage (e.g., 2x for $\beta=0.5$ stocks). Margin costs, short rebate haircuts, and borrowing fees eat into returns. The paper's pre-cost returns do not fully account for implementation frictions at scale.

3. **Beta estimation error:** Rolling beta estimates are noisy, especially for small/illiquid stocks. Misranking due to noise pollutes the long and short portfolios. The Dimson shrinkage mitigates but does not eliminate this.

4. **Crowding:** BAB/low-vol strategies have been widely adopted (AQR, factor ETFs like USMV, SPLV). As the trade crowds, the mispricing may partially arbitrage away, and the crash risk from simultaneous unwinding increases — consistent with the crowding failure mode already in `KNOWLEDGE_EQUITY.md`.

5. **Factor decay post-2012:** Post-publication evidence shows BAB Sharpe has declined, particularly in US large-cap where institutional adoption of min-vol strategies has been heaviest.

6. **Long-only constraint kills the factor:** Removing the short leg degenerates BAB into a low-vol tilt on the long side only. This retains some benefit but forfeits the beta-neutrality that isolates the anomaly cleanly. Most of the alpha is in the short leg (overpriced high-beta assets).

7. **Interaction with momentum:** High-beta growth stocks often carry positive momentum; shorting them means being inadvertently short momentum at times. BAB and momentum can be adversely correlated in the short book.

---

## Connection to Ilmanen Expected Returns Ch5 + Ch16

**Chapter 5 (Volatility / Low-Risk Anomaly):**
Ilmanen frames the low-vol anomaly as one of the most robust cross-asset patterns and links it directly to Frazzini & Pedersen. He argues the flat SML is structural — driven by leverage aversion among real-money investors, not data mining. Key synthesis: the low-vol premium is best understood as compensation for *illiquidity of leverage* rather than traditional risk compensation. Ilmanen notes that the premium is not explained by quality (profitability, earnings stability) alone; beta aversion adds independent explanatory power.

**Chapter 16 (Alternative Risk Premia / Factor Investing):**
Ilmanen places BAB alongside carry, momentum, and value as a core liquid alternative risk premium. He notes the factor is negatively skewed (crash risk during deleveraging) and advises diversifying it with positively-skewed factors. He warns that ARP crowding has compressed Sharpe ratios post-2012 and that BAB's crisis behavior correlates with other leveraged strategies — portfolio-level BAB allocation must account for its funding-liquidity beta.

**Key tension Ilmanen identifies:** BAB is best in environments of loose funding (low TED spread, ample margin credit). During tightening cycles or crises, BAB is the worst place to be leveraged — and it is precisely then that the strategy *needs* leverage to function.


---

## Codebase Check

### `backtests/strategies/signals.py`

**`VolatilitySignal` (lines 116–133) — present but misaligned with BAB.**
The class inverts rolling vol (`signal = -vol`) and its docstring says "Lower vol = higher expected return (contrarian)". The comment at line 131 reads: `# Invert: low vol = high signal (expect vol to expand)`. This is a *mean-reversion* bet on volatility expansion — categorically different from BAB's structural mispricing thesis. BAB says low-beta stocks persistently outperform on risk-adjusted terms because they are chronically underpriced; `VolatilitySignal` treats low-vol as a transient state before reversion. These are conflicting explanations for the same empirical pattern.

**`ATRSignal` (lines 144–171) — same issue.** `signal = -atr`, docstring: "Buy low volatility." Again a single-asset contrarian signal, not a cross-sectional beta sort.

**No `BetaSignal` exists.** There is no signal that estimates rolling market beta per stock, ranks the cross-section, and constructs a long-low/short-high beta portfolio. BAB is not implemented anywhere in the codebase.

**No beta-neutral weighting.** No mechanism scales positions by $1/\beta$ to achieve beta-neutrality as Frazzini & Pedersen specify.

### `portfolio/optimizer.py` + `portfolio/advanced_analytics.py`

**MVO (`mean_variance_optimize`, lines 23–84):** Standard CVXPY solver. Has weight bounds and optional gross leverage (`target_gross`), but no beta-neutrality constraint. A BAB implementation would need: `cp.sum(w * beta_vector) == 0` added to the constraints list.

**Risk parity (`risk_parity_optimize`, `portfolio/advanced_analytics.py` line 229):** Full equal-risk-contribution implementation using `scipy.optimize`. This is *related* to BAB in spirit (both allocate more to low-risk assets) but mechanically different — risk parity equalizes risk contributions across assets, not beta exposures. It does not short high-beta assets or lever up low-beta ones. Partial validation: the existence of risk parity confirms the codebase already reasons about allocating by risk rather than by dollar weight, which is the conceptual parent of BAB weighting.

**`portfolio/risk.py` — `ledoit_wolf_cov` (line 19):** Shrinkage covariance via scikit-learn. Directly usable for BAB beta estimation: extract diagonal standard deviations, compute pairwise correlation with market, derive $\hat{\beta}_i = \hat{\rho}_{im} \cdot (\hat{\sigma}_i / \hat{\sigma}_m)$.

### `memory/knowledge/KNOWLEDGE_EQUITY.md` — line 74

BAB already cited as a stub: `"Betting Against Beta" | Frazzini & Pedersen | 2014 | relevance: 85/100`. No implementation notes or failure modes. These notes supersede that entry.

### Summary Table

| BAB Requirement | Codebase Status | File |
|---|---|---|
| Rolling market-beta estimation per stock | **Missing** | — |
| Cross-sectional beta sort (long low / short high) | **Missing** | — |
| Inverse-beta position scaling for beta-neutral legs | **Missing** | — |
| Beta-neutrality constraint in MVO | **Missing** | `portfolio/optimizer.py` |
| Low-vol long-only signal (directional) | **Partial conflict** | `signals.py` L116–133 (wrong mechanism) |
| Risk parity (conceptual parent) | **Present** | `portfolio/advanced_analytics.py` L229 |
| Ledoit-Wolf covariance for beta estimation | **Present** | `portfolio/risk.py` L19 |
| SPY daily OHLCV for market vol | **Present** | `data/market_data/prices/spy_ohlc.parquet` |
| Equity cross-section daily OHLCV | **Present** | `data/market_data/prices/equities.parquet` |


---

## Implementability

### Data Requirements

- **Equity cross-section:** `data/market_data/prices/equities.parquet` — daily OHLCV, schema `(date, ticker, open, high, low, close, volume)`. Need sufficient cross-section depth (ideally 200+ stocks) for robust beta sorting.
- **Market index:** `data/market_data/prices/spy_ohlc.parquet` — SPY daily OHLCV for $\hat{\sigma}_m$ and $\hat{\rho}_{im}$.
- **Risk-free rate:** FRED series `DGS3MO` (3-month T-bill) for excess return calculation. Already in FRED pipeline.
- **No fundamental data required** — purely price-based factor, unlike quality or value.

### Implementation Steps

```python
# 1. Estimate per-stock beta (Frazzini-Pedersen split-frequency)
#    sigma_i, sigma_m : 1-year rolling daily std
#    rho_im           : 5-year rolling monthly corr
#    beta_raw         : rho_im * (sigma_i / sigma_m)
#    beta_adj         : 0.6 * beta_raw + 0.4  [shrinkage toward 1]

# 2. Cross-sectional rank -> z-scores at each rebalance date
#    Long leg  : z > 0 (low-beta stocks, lever up to beta=1)
#    Short leg : z < 0 (high-beta stocks, deleverage down to beta=1)

# 3. Scale each leg so portfolio beta = 1
#    w_i^L = z_i / beta_portfolio^L
#    w_i^S = z_i / beta_portfolio^S

# 4. BAB return = (1/beta^L) * r^L - (1/beta^S) * r^S
```

### ETF Proxies (Long-Only Approximation)

- **USMV** — iShares MSCI USA Min Vol Factor ETF. Long-only low-vol tilt, no short leg. Captures roughly half of BAB signal.
- **SPLV** — Invesco S&P 500 Low Volatility ETF. 100 lowest-vol S&P 500 stocks, equal-weighted. Same caveat.
- **Limitation:** ETF proxies forfeit the short leg and beta-neutrality. Useful for directional low-vol exposure but do not replicate BAB's alpha or its factor structure.

### Codebase Integration Path

1. Add `BetaSignal` class to `backtests/strategies/signals.py` — split-frequency Dimson estimator, outputs per-stock `beta_adj` as a DataFrame.
2. Add `bab_weights()` function — rank by beta, compute z-scores, scale each leg to beta=1, return long/short weight vectors.
3. Add beta-neutrality constraint to `portfolio/optimizer.py`: `cp.sum(cp.multiply(w, beta_series.values)) == 0`.
4. Reuse `ledoit_wolf_cov` from `portfolio/risk.py` (line 19) for covariance-based beta cross-check.
5. Add `backtests/runners/bab.py` runner (parallel to `momentum.py`).

### Minimum Viable Test

- Universe: all tickers in `equities.parquet` with 5+ years of history
- Period: 2010–2024 (post-paper, true out-of-sample)
- Monthly rebalance, 1-day execution lag (no look-ahead)
- Gate: Sharpe > 0.40 (half of paper's US result, accounting for small universe)

---

## Key Quotes

> "Stocks with high betas have lower returns than their CAPM-implied levels, while stocks with low betas have higher returns." — Abstract

> "Investors who are constrained against using leverage overweight high-beta assets, causing them to be overpriced relative to the CAPM." — Section 2

> "The BAB factor earns a Sharpe ratio of 0.70 in the United States over 1926–2012 and is consistently profitable in 20 equity markets." — Section 4

> "When funding liquidity tightens, leveraged investors unwind, causing BAB to crash." — Section 5 (paraphrase)

---

## Follow-Up Papers

- **Frazzini & Pedersen (2022)** — "Embedded Leverage" — extends BAB to options and derivatives where embedded leverage creates analogous mispricing.
- **Black, Jensen & Scholes (1972)** — original flat SML finding; the empirical predecessor to BAB.
- **Black (1972)** — "Capital Market Equilibrium with Restricted Borrowing" — theoretical foundation for the leveraged CAPM.
- **Asness, Frazzini & Pedersen (2019)** — "Quality Minus Junk" — companion factor; BAB and QMJ are correlated (low-beta firms tend to be high-quality).
- **Baker, Bradley & Wurgler (2011)** — "Benchmarks as Limits to Arbitrage" — alternative mechanism for the flat SML (benchmark-relative mandates, not leverage constraints).
- **Ang, Hodrick, Xing & Zhang (2006)** — "The Cross-Section of Volatility and Expected Returns" — idiosyncratic volatility puzzle; related but distinct (idio vol != market beta).
- **Novy-Marx & Velikov (2016)** — "A Taxonomy of Anomalies and Their Trading Costs" — BAB survives transaction costs but returns shrink meaningfully after realistic cost models.
- **Pedersen (2009)** — "When Everyone Runs for the Exit" — theoretical model of funding liquidity crises that produces the BAB crash mechanism.
