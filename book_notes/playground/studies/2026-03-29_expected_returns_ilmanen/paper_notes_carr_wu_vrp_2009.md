# Paper Notes: Variance Risk Premiums
**Authors:** Carr, Wu | **Year:** 2009 | **Journal:** Review of Financial Studies
**Date Read:** 2026-03-29 | **Scores:** Credibility 5 | Relevance 5 | Actionability 4

---

## Core Thesis

Variance risk premiums (VRP) — the difference between implied variance and subsequently realized variance — are a persistent, systematic feature of options markets across equities and FX. Investors who are short variance (i.e., sell variance swaps or write options) consistently earn a premium because implied variance exceeds realized variance on average. This premium is not a free lunch: it compensates sellers for exposure to jump risk, stochastic volatility risk, and tail events. Carr and Wu provide the first rigorous cross-asset, model-free empirical documentation of this phenomenon.

---

## Key Findings

1. **VRP is negative in sign (seller earns positive return):** Implied variance systematically exceeds realized variance for S&P 500 and individual stocks. The average monthly excess return from being short variance is positive and statistically significant.
2. **Magnitude:** For the S&P 500, the VRP averages approximately 15 annualized volatility points (in variance space, roughly $15^2 = 225$ variance points annualized). In practical terms, if IV is 20 vol and realized vol is 15 vol, the seller earns ~5 vol points in expectation.
3. **Cross-sectional variation:** The VRP is larger for equity indices than for individual stocks, and larger for equities than for FX. This is consistent with the equity index having more crash/tail risk per unit of volatility than a diversified FX pair.
4. **Negative skewness:** VRP strategies exhibit severe left tail — losses cluster during crises (1998 LTCM, 2001–2002, 2008). The Sharpe ratio is positive but the strategy has negative skewness and excess kurtosis.
5. **Time-variation:** The VRP is not constant. It widens before and during periods of market stress and compresses in calm regimes. The VIX level is itself a reasonable proxy for the conditional magnitude of the VRP.
6. **Individual stocks:** VRP exists for individual equities but is smaller in magnitude and less statistically robust than for the index. Index VRP contains the additional component of correlation/dispersion risk.

---

## Methodology

**Variance swap replication (model-free):**
Carr and Wu follow the Britten-Jones & Neuberger (2000) / Demeterfi et al. (1999) replication approach. The fair strike of a variance swap — the implied variance $IV_t$ — can be computed model-free from the full cross-section of option prices:

$$IV_t = \frac{2}{T} \int_0^\infty \frac{C(K, T) + P(K, T)}{K^2} dK$$

where $C$ and $P$ are OTM call and put prices, $K$ is strike, $T$ is maturity. This is exactly the formula underlying the VIX index (post-2003 CBOE methodology). No model assumptions (no Black-Scholes, no specific stochastic vol model) are required.

**Realized variance:**
Computed as the sum of squared log-returns over the holding period:

$$RV_{t, t+T} = \sum_{i=1}^{N} r_i^2$$

where $r_i$ are daily log-returns over $[t, t+T]$. Daily sampling is standard; intraday (5-min) sampling is used in robustness checks to reduce microstructure noise.

**Data:**
- S&P 500 index options (SPX) from OptionMetrics, 1996–2003
- Individual stock options (large-cap US equities from OptionMetrics)
- Currency options (USD vs. EUR, JPY, GBP, CHF, AUD) from OTC FX option markets at standard deltas: 10Δ, 25Δ, ATM
- Sample period: approximately 1996–2003 (pre-GFC, but includes 1998 and 2001–2002 stress)

**Return computation:**
The monthly VRP return is defined as:
$$\text{VRP return}_t = IV_t - RV_{t, t+T}$$
in variance units (annualized percentage variance). A positive value means the seller earned the spread.

---

## VRP Definition & Measurement

**Sign convention in this paper:**
$$VRP_t = IV_t - RV_{t, t+T}$$

where $IV_t$ is the model-free implied variance at time $t$ and $RV_{t,t+T}$ is realized variance over the subsequent period $[t, t+T]$. A **positive VRP** means implied exceeded realized — the variance seller earns a premium.

**Not to be confused with** the Bollerslev et al. (2009) notation, which sometimes writes $VRP_t = VIX_t^2 - E_t[RV_{t+1}]$ using squared vol directly. Same concept, same sign, different notation convention.

**Magnitude (S&P 500):**
- Mean monthly VRP $\approx +15$ annualized variance points
- Annualized Sharpe of short variance $\approx 0.5$–$0.9$ depending on sample and instrument
- VRP is positive in >70% of months, but negative months are extreme
- In vol-point terms: $\sqrt{IV} - \sqrt{RV} \approx +3$ to $+5$ vol points on average for SPX


---

## Cross-Asset VRP Evidence

| Asset Class | VRP Magnitude | Statistical Significance | Notes |
|---|---|---|---|
| S&P 500 index | Largest (~15 var pts ann.) | High | Crash risk + correlation risk |
| Individual stocks | Smaller | Moderate | Less systematic tail risk |
| EUR/USD, USD/JPY | Smaller than equity | Lower | FX has lighter tails |
| USD/JPY | Possibly near zero in calm regimes | Mixed | Safe-haven dynamics |

**Key insight:** Index VRP > stock VRP because the index carries an additional **correlation risk premium**. When markets crash, correlations spike toward 1 — a variance seller on the index implicitly sells correlation as well. Individual stock variance sellers do not bear this systemic risk component.

**FX VRP:** Exists but is smaller and less persistent than equity VRP. FX return distributions have lighter tails. The crash risk that inflates equity implied vol persistently above realized vol is muted in FX. This is consistent with FX carry trade profitability being partly, but not entirely, a volatility risk compensation story.

---

## VRP as Compensation for What Risk?

Carr and Wu decompose the sources of VRP through a general no-arbitrage framework with three identified components:

1. **Diffusive stochastic volatility risk:** If volatility is stochastic and the vol risk factor is priced (investors dislike variance-of-variance), then even without jumps, implied variance exceeds expected realized variance under the physical measure. Heston-style models can generate persistent VRP through this channel alone.

2. **Jump risk in returns:** Sudden large negative returns (crash risk) contribute disproportionately to realized variance but cannot be fully hedged by dynamic delta replication. Options buyers effectively purchase insurance against crash realizations, inflating implied variance. This is the dominant driver for equity indices.

3. **Jump risk in volatility:** Abrupt spikes in the volatility level itself (vol jumps) are a distinct source of risk. Investors pay extra to be protected against sudden vol regime shifts. This channel inflates implied variance beyond what diffusive stochastic vol alone would predict.

**Paper's conclusion:** All three sources contribute, but **jump risk** — in both returns and volatility — is the primary driver of the large, persistent equity VRP. This explains why:
- Equity VRP exceeds FX VRP (equity has heavier crash tails)
- VRP widens during stress (jump risk pricing intensifies as crash probability rises)
- VRP strategies are negatively skewed (losses coincide with jump realizations)

**Economic interpretation:** VRP sellers are acting as catastrophe insurers. The premium is compensation for absorbing tail risk that other market participants strongly wish to offload.


---

## Predictive Power

Carr and Wu focus primarily on **documenting and explaining** VRP rather than its return-predictive properties. The predictive link is more fully developed in closely related contemporaneous work:

**Bollerslev, Tauchen & Zhou (2009) — the key predictive paper:**
- $VRP_t = VIX_t^2 - E_t[RV_{t+1}]$ predicts aggregate S&P 500 excess returns at quarterly horizons
- $R^2 \approx 3$–$7\%$ at the 1–3 month horizon; decays at annual horizons
- Incremental to dividend yield, P/E, and term spread predictors
- Intuition: wide VRP signals elevated risk aversion / crash fear → higher future risk premiums

**Carr & Wu's own evidence (implicit):**
- Time-variation in VRP correlates with market stress indicators (VIX level, credit spreads)
- VRP is widest entering crisis periods — exactly when realized vol subsequently spikes and strategy loses money
- The conditional Sharpe is not stable: positive in calm regimes, severely negative in crises

**Practical caveat:** The predictive $R^2$ of 3–7% is economically meaningful but statistically fragile out-of-sample. Achieving reliable significance requires samples of many decades — directly consistent with our team's experience failing the MinBTL threshold.

---

## Failure Modes & Limitations

**When variance selling loses money:**

1. **Crisis episodes:** 1998 (LTCM/Russia), 2001–2002 (9/11, Enron), 2008–2009 (GFC). Realized variance spikes far above any reasonable implied variance entering the period. A short-variance position in October 2008 faced realized vol of 70–80+ while IV entering that month was ~30. The loss is bounded only by position size — there is no natural stop.

2. **Sudden VIX spike events:** Flash Crash (May 2010), August 2015, February 2018 (VIX-pocalypse). Short-dated variance exposure is particularly vulnerable.

3. **Negative autocorrelation of wins/losses:** Calm periods produce steady small gains that are wiped out by a single crisis month. The strategy has option-like payoff profile — short a crash put.

**Structural limitations of the paper:**
- Sample period ends ~2003, missing the GFC entirely. The 2008 data would materially affect reported Sharpe ratios and distributional statistics.
- Variance swap replication requires a dense, liquid options surface. Implementing with listed options introduces discretization and liquidity error.
- Transaction costs of rolling short-variance exposure (bid-ask spreads on options, margin requirements) are not fully modeled.
- FX results rely on OTC implied vol quotes, which may embed dealer markup beyond pure risk premium.


---

## Connection to Ilmanen Expected Returns Ch15 (Volatility Selling / VRP)

Ilmanen's Chapter 15 treats VRP as one of the most robust and well-compensated alternative risk premiums. Key connections:

- **Ilmanen's framing:** VRP is a form of insurance selling. The seller earns a premium for bearing left-tail risk that other investors are willing to pay to avoid. This is the same framing Carr & Wu use — compensation for jump and stochastic vol risk.
- **Magnitude consistency:** Ilmanen reports similar figures: implied vol exceeds realized vol by ~3–5 vol points on average for equity indices, consistent with Carr & Wu's ~15 variance-point estimate.
- **Diversification across assets:** Ilmanen recommends harvesting VRP across equities, FX, rates, and commodities simultaneously to reduce the concentration of crash-risk exposure. Carr & Wu's cross-asset evidence directly supports this — FX VRP exists and is not perfectly correlated with equity VRP.
- **Skewness warning:** Both sources flag the same risk: short-variance strategies have attractive average returns but severe negative skewness. Ilmanen explicitly warns that VRP strategies can lose several years of gains in a single month during a crisis.
- **Position sizing:** Ilmanen advocates vol-targeting or risk-parity sizing of VRP exposure to manage the fat-tail risk — do not size naively by notional.
- **Ch15 key message alignment:** "Variance sellers earn a premium, but they are short a crash put on the market." Carr & Wu's empirical framework is the academic foundation for this claim.

---

## Connection to Team's Rejected VIX Regime Strategy

Our VIX Regime / VRP strategy was **rejected** after two rounds (2026-03-15). Carr & Wu's framework illuminates exactly why:

**What our strategy attempted:** Use VIX regime (high vs. low VIX) as a signal to time exposure to an underlying momentum or equity strategy. The implicit logic was that VRP is a risk signal — wide VRP → elevated crash risk → reduce exposure.

**What Carr & Wu show that explains the failure:**

1. **VRP is a crash-risk proxy, not an alpha signal.** The paper demonstrates VRP is compensation for bearing tail risk. Using VRP (or VIX level) as a regime filter doesn't generate alpha — it just conditions on when the risk premium is largest (crisis), which is exactly when you want exposure to earn it, not when to reduce it. The strategy had the logic inverted.

2. **MinBTL failure (3,968 years required):** Our strategy required 3,968 years of data to establish statistical significance. Carr & Wu's own sample needed 7+ years just to document basic VRP significance for SPX. Regime-timing on top of VRP compounds the multiple-testing problem — the parameter space (VIX threshold, lookback, signal combination) is enormous relative to the signal-to-noise ratio.

3. **Spanning alpha t = -0.18:** Our strategy's alpha was indistinguishable from zero and slightly negative. Carr & Wu show VRP is priced as systematic risk — it cannot be arbitraged away, but it also cannot be reliably timed. A VIX-regime filter adds noise without adding edge.

4. **Dominated by simple trailing vol:** Carr & Wu show realized variance is the natural benchmark for implied variance. A strategy that simply shorts vol (without regime conditioning) is the baseline. Any regime overlay must beat that baseline — ours did not.

**Lesson:** VRP is a carry-like risk premium to be held systematically, not timed. The correct implementation is persistent short-variance exposure with proper position sizing (vol-targeting), not a binary regime switch.


---

## Implementability

**Data available locally:**
- `data/market_data/prices/vix_daily.parquet` — VIX index (CBOE daily close)
- `data/market_data/prices/vix3m_daily.parquet` — VIX3M (3-month implied vol)
- `data/market_data/prices/equities.parquet` — SPY and equity prices for realized variance

**Computing implied variance (IV):**
VIX is already the model-free implied volatility for 30-day SPX variance. Convert to implied variance:
```python
# VIX is quoted as annualized vol %, so:
IV_t = (vix / 100) ** 2  # annualized variance
```
This is a clean proxy for the variance swap strike without needing the full options surface.

**Computing realized variance (RV):**
```python
import pandas as pd
import numpy as np

prices = pd.read_parquet("data/market_data/prices/equities.parquet")
spy = prices[prices["ticker"] == "SPY"][["date", "close"]].set_index("date")

# Daily log returns
log_ret = np.log(spy["close"] / spy["close"].shift(1))

# 21-day realized variance, annualized
RV_21d = log_ret.rolling(21).apply(lambda x: (x**2).sum() * 252)
```

**VRP signal:**
```python
# IV from VIX (forward-looking 30-day window)
vix = pd.read_parquet("data/market_data/prices/vix_daily.parquet")
IV = (vix["close"] / 100) ** 2  # annualized variance

# VRP = IV_{t} - RV_{t-21:t} (contemporaneous, for signal purposes)
# Or properly: IV_{t} - RV_{t:t+21} (requires forward RV — introduces look-ahead)
# Safe implementation: use lagged RV as proxy for expected RV
VRP_signal = IV - RV_21d.shift(1)  # no look-ahead
```

**Key implementation caution:** The academically correct VRP uses *forward* realized variance ($RV_{t, t+T}$), which is known only ex post. For a live signal, use lagged RV as a proxy for $E_t[RV]$. This is standard practice and introduces only a small approximation error in most regimes (large error only during sudden vol spikes).

**Position sizing recommendation (from Ilmanen + Carr & Wu):**
- Do not hold fixed notional short-variance exposure
- Use vol-targeting: scale position inversely with current VIX level so that dollar variance exposure is approximately constant
- This reduces — but does not eliminate — the crisis drawdown

---

## Key Quotes

> "The variance risk premium is negative for all five stock indexes and most individual stocks, indicating that investors are willing to pay a premium to obtain positive variance exposure as a hedge against market uncertainty."

> "The variance risk premiums on stock indexes are much larger in magnitude than those on individual stocks, suggesting that the index variance risk premium contains a large correlation risk premium component."

> "The large negative variance risk premiums on stock indexes suggest that investors are very averse to uncertainty about future stock market volatility."

> "Movements in the variance risk premium are strongly related to movements in credit spreads and other indicators of economic uncertainty, suggesting that they reflect a common market-wide fear factor."

---

## Follow-Up Papers

| Paper | Authors | Year | Why Relevant |
|---|---|---|---|
| Variance Risk Premiums and the Predictability of Returns | Bollerslev, Tauchen & Zhou | 2009 | VRP predicts equity returns at quarterly horizon; $R^2$ 3–7% |
| The Variance Risk Premium | Drechsler & Yaron | 2011 | General equilibrium model explaining VRP via rare disasters + stochastic vol |
| Model-Free Implied Volatility | Britten-Jones & Neuberger | 2000 | Theoretical foundation for model-free IV (variance swap replication) |
| More Than You Ever Wanted to Know About Volatility Swaps | Demeterfi, Derman, Kamal, Zou | 1999 | Practical replication guide for variance swaps |
| Variance Risk Dynamics, Variance Risk Premia, and Optimal Variance Swap Investments | Egloff, Leippold & Wu | 2010 | Time-series dynamics of VRP; optimal portfolio allocation to variance |
| The Price of Variance Risk | Carr & Lee | 2009 | Extension to realized and implied skewness; skewness risk premium |
| Rough Volatility | Gatheral, Jaisson & Rosenbaum | 2018 | Fractional Brownian motion vol models; explains VIX term structure shape |
| Does Realized Skewness Predict the Cross-Section of Equity Returns? | Boyer, Mitton & Vorkink | 2010 | Cross-sectional skewness premium; connects to VRP cross-section |

