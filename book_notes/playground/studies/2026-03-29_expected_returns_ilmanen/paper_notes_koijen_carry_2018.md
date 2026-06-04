# Paper Notes: Carry
**Authors:** Koijen, Moskowitz, Pedersen, Vrugt
**Year:** 2018 | **Journal:** Journal of Financial Economics
**Date Read:** 2026-03-29
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

---

## Core Thesis

Carry — the return an investor receives if prices stay the same — is a pervasive, economically large predictor of returns **across all major asset classes**. A single, unified carry definition unifies seemingly disparate phenomena (FX carry trade, commodity roll yield, bond term premium, equity dividend yield) into one framework. Carry strategies earn significant risk-adjusted returns that cannot be explained by standard risk factors, and their co-movement across asset classes suggests a common global carry factor rather than asset-class-specific mechanisms.

---

## Definition of Carry

For any asset, carry is defined as the **expected return if spot prices remain unchanged**:

$$C_t = \frac{F_t - S_t}{S_t} \approx \text{futures basis} = \text{cost of carry residual}$$

More precisely, the carry of holding the asset financed at the risk-free rate is:

$$C_t = \frac{\text{forward price (or equivalent)}} {\text{spot price}} - 1 - r_f$$

This can be computed from futures prices directly without forecasting price movements:

| Asset Class | Carry Measure |
|-------------|---------------|
| FX | Interest rate differential (covered interest parity deviation) |
| Equities | Dividend yield minus risk-free rate (or futures basis) |
| Fixed Income | Yield minus risk-free rate; slope of yield curve |
| Commodities | Roll yield (spot-to-futures basis; convenience yield minus storage cost) |
| Credit | Credit spread above risk-free |
| Options | Variance risk premium (implied minus realized vol) |

Key insight: **carry is observable today** — it requires no price forecast. It is a sufficient statistic for expected returns under the assumption that spot prices follow a random walk.

---

## Data and Methodology

### Sample
- **Period:** 1972–2012 (40 years), with asset-class-specific start dates
- **Universe:** 8 asset classes, ~50+ instruments across:
  - **FX:** 10 developed market currencies vs. USD
  - **Equities:** 18 equity index futures (global developed)
  - **Fixed Income:** 10 government bond futures
  - **Commodities:** 24 commodity futures
  - **Credit:** CDX investment grade and high yield indices
  - **Options:** S&P 500 and other equity index options

### Portfolio Construction
- Within each asset class: sort instruments by carry at each month-end → go long top-third, short bottom-third (rank-weighted)
- **Univariate carry portfolios** constructed for each asset class independently
- **Diversified carry portfolio:** equal-volatility weighted combination across all asset classes
- Returns measured in excess of risk-free rate; portfolios volatility-scaled to 10% p.a.

---

## Key Empirical Findings

### 1. Carry Predicts Returns Across All Asset Classes

In panel regressions, carry positively and significantly predicts future returns in **every asset class tested**:
- Coefficient on carry ≈ 1.0 in most specifications (carry = expected return)
- FX: coefficient ~0.97; Commodities: ~1.2; Equities: ~0.85; Fixed Income: ~0.90
- The random-walk assumption (price does not mean-revert) is not the driving force — carry earns positive returns even net of subsequent price changes

### 2. Carry Portfolio Sharpe Ratios

| Asset Class | Sharpe Ratio (approx.) |
|-------------|------------------------|
| FX | 0.69 |
| Equities | 0.44 |
| Fixed Income | 0.55 |
| Commodities | 0.41 |
| Global Diversified | **0.81** |

Diversification benefit is large: combined Sharpe substantially exceeds individual asset-class carry.

### 3. Carry Is Not Explained by Standard Factors
- Alphas survive controlling for: market beta, size, value, momentum, liquidity
- Not explained by: Fama-French factors, Carhart momentum, BAB, QMJ
- CAPM betas of carry portfolios are low and mostly insignificant

### 4. A Global Carry Factor Exists
- Carry portfolios across asset classes are **positively correlated** with each other (avg pairwise ~0.15–0.30)
- First PC of all carry strategies explains a disproportionate share of variance
- A **global carry factor** (equal-vol weighted combination) earns SR ~0.81 with positive skewness once diversified

### 5. Carry vs. Momentum and Value
- Carry is distinct from momentum (correlation ~0.10–0.25) and value (~0.10–0.20)
- Combining carry + momentum + value improves Sharpe further (multi-style diversification)
- Carry subsumes some of what momentum and value capture in certain markets

### 6. Decomposition: "Carry" vs. "Convergence"
- Total carry return = carry income (if prices unchanged) + price appreciation component
- In most asset classes, **most of carry return comes from carry income**, not price convergence
- Price changes are slightly positive on average, adding to carry; rare crash-driven price declines partly offset carry in FX

---

## Risk and Return Decomposition

### Crash Risk (FX)
- FX carry has **negative skewness** (crash risk) — high-yield currencies depreciate sharply in crises
- Skewness ~ -0.8 for FX carry; much less negative for other asset classes
- However, global diversified carry has near-zero skewness (crash risks partially offsetting)

### Downside Betas
- Carry strategies have elevated downside betas in crisis periods (2008–2009)
- Conditional on poor global equity market returns, carry strategies tend to lose
- This suggests a risk explanation: carry compensates for global crash/liquidity risk

### Transaction Costs
- FX: ~5 bps per trade (bid-ask); carry remains profitable net of costs
- Commodities: roll costs matter; futures liquidity varies by contract
- Net Sharpe ratios reduced by ~10–20% after realistic cost estimates, but remain strongly positive

---

## Theoretical Explanations

The paper is deliberately agnostic about the mechanism but surveys candidate explanations:

### Risk-Based
1. **Global crash risk / liquidity risk:** Carry strategies lose when global risk appetite collapses. Investors demand a premium for holding assets that decline in crises.
2. **Rare disaster risk (Gabaix, Brunnermeier):** High-carry assets have larger exposure to rare disasters. Expected returns embed a disaster premium.
3. **Intermediary capital constraints (He-Krishnamurthy):** When broker-dealer capital is scarce, carry spreads widen as arbitrage is limited.

### Behavioral
4. **Trend-following amplification:** Carry and momentum interact — carry trends reinforce themselves until crash.
5. **Peso problem / peso events:** Investors underweight low-probability crash scenarios; apparent alpha is compensation for unobserved tail events.
6. **Inattention / slow capital:** Persistent mispricing because investors are slow to arbitrage interest rate differentials.

### The paper's position: Risk and behavior **both** contribute. No single model fully explains the global co-movement.

---

## Practical Implementation Notes

### Signal Construction
```
For futures-traded instruments:
  Carry = (F_near - F_far) / F_near  [roll yield, annualized]
  or equivalently = spot_rate_differential for FX

For FX specifically:
  Carry_i = (1 + r_i) / (1 + r_USD) - 1  ≈ r_i - r_USD
  where r_i = 1-month LIBOR for currency i

For bonds:
  Carry = yield - duration * yield_change_if_unchanged
        = yield + rolldown_return
```

### Portfolio Construction Rules (from paper)
- Sort by carry rank within asset class each month
- Equal or vol-weighted long top tercile, short bottom tercile
- Scale each asset-class carry portfolio to target volatility (e.g., 10%)
- Combine asset class carry with equal vol weights
- Rebalance monthly

### Correlation Structure
- Within-asset-class carry positions: moderate positive correlation
- Across-asset-class: low but positive (diversification benefit is large)
- Carry correlates positively with momentum within FX (~0.3), less in other classes

---

## Connections to Other Literature

| Paper | Connection |
|-------|------------|
| Fama (1984) — Forward premium puzzle | FX carry is the empirical violation of UIP; this paper generalizes the puzzle |
| Lustig, Roussanov, Verdelhan (2011) | HML_FX factor is the FX-specific case of the global carry factor |
| Asness, Moskowitz, Pedersen (2013) | Carry complements value and momentum; all three are distinct return premia |
| Koijen & Yogo (2016) | Demand-system asset pricing; carry reflects inelastic demand from constrained investors |
| Brunnermeier, Nagel, Pedersen (2008) | Carry trade crash risk and liquidity spirals in FX |
| Gorton & Rouwenhorst (2006) | Commodity futures risk premium; roll yield as carry in commodities |
| Ilmanen (2011) — Expected Returns | Carry as one of the four major return drivers (carry, value, momentum, liquidity) |

---

## Critical Assessment

### Strengths
- **Unified framework:** The single carry definition spanning 8 asset classes is conceptually elegant and empirically powerful. This is the paper's greatest contribution.
- **Long sample:** 40-year sample with broad cross-section mitigates data-snooping concerns.
- **Robust to costs:** Carry survives realistic transaction cost estimates in most asset classes.
- **Global factor:** The co-movement finding is novel — it shifts the question from "why does carry work in FX" to "what is the global risk that carry everywhere compensates for."
- **Decomposition clarity:** The carry vs. price-change decomposition is methodologically clean.

### Weaknesses / Limitations
- **No single theory:** The paper does not commit to a mechanism. It surveys explanations without adjudicating.
- **Post-publication decay:** Carry has been well-known since at least 2011 (Lustig et al.); this 2018 paper documents what practitioners already traded. Out-of-sample performance since publication is weaker.
- **Equity carry is weak:** The equity index carry (dividend yield basis) has the lowest Sharpe (~0.44) and is most sensitive to the carry definition used.
- **Long/short assumption:** Real-world implementation is often long-only (ETF-constrained); long-short carry is not accessible to all investors.
- **Crash risk not fully resolved:** The global diversification argument for crash risk reduction is empirically supported but not theoretically guaranteed — all carry assets can crash together in a severe crisis (2008).

---

## Replication Potential (This Codebase)

### Feasibility Assessment

| Asset Class | Data Available | Carry Signal | Verdict |
|-------------|---------------|--------------|----------|
| FX (G10) | FRED + ECB FX | Interest rate differential | **High** — FRED rates + ECB FX rates |
| Commodities | Stooq / Binance (crypto) | Futures roll yield | **Medium** — limited futures data |
| Fixed Income | FRED yield curve | Yield + rolldown | **Medium** — FRED series available |
| Equities (index) | Stooq index futures | Dividend yield / futures basis | **Low** — no dividend yield series yet |

### Recommended Implementation Order
1. **FX carry** — most feasible; data fully available via FRED + ECB FX connector
2. **Fixed income carry** — yield curve already partially implemented; rolldown needs to be added
3. **Commodity carry** — needs futures chain data (near vs. far contract)
4. **Equity carry** — blocked on dividend yield data pipeline

### Key Data Gaps
- No dividend yield time series for equity index carry
- No futures chain data (near/far) for commodity roll yield
- FX carry signal (`FXCarrySignal`) not yet implemented in `backtests/strategies/signals.py` (see KNOWLEDGE_FX.md — `CarrySignal` is a momentum proxy, not true carry)

### Code Pointer
- `backtests/strategies/signals.py` — add `FXCarrySignal` class using FRED rate differentials
- `quant_data/connectors/ecb_fx.py` — source for G10 FX spot rates
- `quant_data/connectors/polygon.py` — potential source for futures chain data

---

## Key Takeaways for Research Pipeline

1. **Carry is a genuine risk premium**, not just a data artifact. The multi-asset evidence across 40 years is hard to dismiss.
2. **Diversification is the killer app.** Single-asset carry has modest Sharpe (0.4–0.7); diversified global carry reaches ~0.81. Combining FX + bonds + commodities dramatically reduces crash risk.
3. **Carry and momentum are complementary.** The paper confirms low correlation (~0.15–0.30) between carry and momentum signals. Combining them is not redundant — this directly supports the FX Carry + Momentum (Priority 1) strategy in the research pipeline.
4. **FX carry crash risk is real but manageable.** Negative skewness in FX carry is largely offset when combined with other asset classes. A momentum filter further reduces crash exposure (see KNOWLEDGE_FX.md).
5. **The global carry factor is unexplained.** This is an open research question — whoever prices the global carry factor first has a significant academic and practical edge.
6. **Implementation note:** Carry should be computed from futures basis or rate differentials, NOT from price momentum. The existing `CarrySignal` in this codebase is mis-named and must be replaced before any carry strategy goes live.

---

## Open Questions / Follow-Up

- [ ] Does the global carry factor subsume the HML_FX factor, or are they orthogonal?
- [ ] How does carry perform in the 2012–2025 out-of-sample period (post-paper)?
- [ ] Can rolldown be cleanly computed from FRED yield curve data for a fixed-income carry signal?
- [ ] Does a carry × momentum interaction (high carry AND positive momentum) produce better crash-adjusted returns than carry alone? (Priority: answer this in Marco's R1 notebook)
- [ ] Is crypto carry (funding rate differential) a viable signal using Binance public data?

---

## Citation

Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., & Vrugt, E. B. (2018). Carry. *Journal of Financial Economics*, 127(2), 197–225.

**Related in reading queue:** Lustig, Roussanov & Verdelhan (2011); Asness, Moskowitz & Pedersen (2013); Brunnermeier, Nagel & Pedersen (2008)