# Paper Notes: The Equity Premium: A Puzzle

**Authors:** Mehra, Rajnish & Prescott, Edward C.
**Year:** 1985
**Journal:** Journal of Monetary Economics, Vol. 15, pp. 145–161
**Domain:** Equity / Macro / Asset Pricing Theory
**Tags:** `[BOOK/ARTICLE]` `equity-premium` `consumption-capm` `risk-aversion` `asset-pricing`
**Credibility:** 5/5 | **Relevance:** 4/5 | **Actionability:** 3/5

---

## 1. Core Focus & Central Claim

Mehra and Prescott document that the historical excess return of US equities over the risk-free rate (~6% annualised, 1889–1978) is **quantitatively irreconcilable** with a standard Arrow-Debreu general equilibrium model calibrated to plausible levels of risk aversion and consumption growth volatility. They label this irreconcilability the **Equity Premium Puzzle**.

The central claim: a consumption-based CAPM with power utility and reasonable CRRA coefficients (≤10) can only generate an equity premium of **~0.35%**, roughly 17× smaller than the observed 6%. Closing the gap demands either implausibly high risk aversion (γ ≈ 30–50) or implausibly high consumption volatility — neither is consistent with micro data or investor survey evidence.

---

## 2. Model & Methodology

### 2.1 Economy Setup

- **Endowment economy** (Lucas 1978): a single perishable consumption good, no production.
- **Preferences:** Representative agent with time-separable power (CRRA) utility:

$$U = E_0 \sum_{t=0}^{\infty} \beta^t \frac{c_t^{1-\gamma}}{1-\gamma}$$

where $\beta \in (0,1)$ is the time-discount factor and $\gamma \geq 0$ is the coefficient of relative risk aversion.

- **Endowment process:** Consumption growth $x_t = c_t / c_{t-1}$ follows a **two-state Markov chain** with states $\{\lambda_1, \lambda_2\}$ and transition matrix $\Pi$. Calibrated to match US per-capita consumption growth 1889–1978:
  - Mean growth: $\mu_c \approx 1.8\%$
  - Standard deviation: $\sigma_c \approx 3.6\%$

### 2.2 Asset Pricing in Equilibrium

In equilibrium, all consumption equals the endowment. Asset prices satisfy the **Euler equation**:

$$p_t = E_t \left[ \beta \left(\frac{c_{t+1}}{c_t}\right)^{-\gamma} (p_{t+1} + d_{t+1}) \right]$$

For the risk-free asset (real bill):

$$R_f = \frac{1}{\beta E_t[(c_{t+1}/c_t)^{-\gamma}]}$$

### 2.3 Calibration & Result

For $\gamma \in [0, 10]$ and $\beta \in (0, 1)$:

| Quantity | Data (1889–1978) | Model max |
|---|---|---|
| Equity premium $E[R_e - R_f]$ | ~6.18% | ~0.35% |
| Risk-free rate | ~0.80% | ~4.0% (too high at high γ) |
| Sharpe ratio (annual) | ~0.37 | ~0.04 |

The model cannot simultaneously match both the equity premium **and** the level of the risk-free rate. Raising γ increases the predicted risk-free rate far above its observed near-zero level (the companion **Risk-Free Rate Puzzle**, formalised by Weil 1989).

---

## 3. Empirical Evidence

- **Data:** Cowles Commission + Ibbotson Associates US equity returns, US T-bill rates, BEA per-capita real consumption, 1889–1978 (90 years).
- **Equity premium:** 6.18% arithmetic, ~4% geometric.
- **Risk-free rate:** 0.80% real.
- **Consumption growth volatility:** 3.57% — low relative to equity return volatility (~16.7%).
- **Equity / consumption growth correlation:** Low, making equities appear **insufficiently risky** from a consumption-hedging perspective under CRRA.

---

## 4. Author's Narrative & Argument Arc

1. **Start from Lucas (1978):** Establish the endowment economy as the natural baseline for asset pricing without market frictions.
2. **Calibrate carefully:** Use Markov chain rather than i.i.d. shocks to allow for persistence in consumption growth.
3. **Demonstrate the gap:** Show analytically that the SDF variance implied by observed consumption is far too low to price the observed equity premium (a Hansen-Jagannathan bound argument in embryo).
4. **Stress-test parameters:** Sweep $\gamma$ and $\beta$ exhaustively — the gap persists across all plausible combinations.
5. **Name it a puzzle, not an anomaly:** The paper deliberately leaves the resolution open, inviting future theoretical work.

---

## 5. Key Implications & Follow-On Literature

### Proposed Resolutions (post-1985)

| Resolution Class | Mechanism | Key Papers |
|---|---|---|
| **Habit formation** | Utility depends on surplus consumption; γ_effective rises | Campbell & Cochrane (1999) |
| **Recursive preferences** | Separate risk aversion from EIS; breaks γ = 1/EIS straitjacket | Epstein & Zin (1989), Bansal & Yaron (2004) |
| **Rare disasters** | Fat-tailed consumption disasters; large precautionary premium | Rietz (1988), Barro (2006) |
| **Idiosyncratic risk** | Incomplete markets; agents cannot diversify labour income shocks | Constantinides & Duffie (1996) |
| **Heterogeneous agents** | Wealthy stockholders have higher effective risk aversion | Mankiw & Zeldes (1991) |
| **Behavioral / loss aversion** | Myopic loss aversion; short evaluation horizon | Benartzi & Thaler (1995) |
| **Liquidity / transactions costs** | Participation costs deter marginal investor | Heaton & Lucas (1996) |
| **Survivorship bias** | US was a survivorship winner; unconditional ERP overstated | Brown, Goetzmann & Ross (1995) |
| **Long-run risks** | Small persistent component in consumption growth | Bansal & Yaron (2004) |

### The Risk-Free Rate Puzzle (Weil 1989)
Raising γ to match the equity premium simultaneously drives $R_f$ to implausibly high levels (8–14%). This requires $\beta > 1$ (negative time preference) to correct — equally implausible.

---

## 6. Validation & Replication Paths

1. **Replicate the Markov-chain calibration** using 1889–2024 CRSP/Shiller data — test whether the puzzle has narrowed with a longer sample and post-2000 consumption data.
2. **Compute Hansen-Jagannathan bounds** on the SDF using realised excess returns — a tighter modern diagnostic than the original parameter sweep.
3. **Compare geometric vs arithmetic premia** — Dimson, Marsh & Staunton (2002) find the geometric ERP (~3.5%) is roughly half the arithmetic figure used by Mehra-Prescott.
4. **International replication** — Does the puzzle hold across Dimson-Marsh-Staunton 21-country dataset? Relevant because survivorship bias may inflate the US figure.
5. **Conditioning on regimes** — Does the ERP vary predictably with VIX regimes, yield-curve shape, or business cycle state? (Connects to existing `backtests/strategies/` regime work.)

---

## 7. Codebase Connections

### 7.1 Sharpe / Excess Return Infrastructure

The framework at `/Users/zelin/Desktop/PA Investment/Invest_strategy/backtests/metrics.py` computes excess-return based performance metrics (Sharpe, Calmar). The Mehra-Prescott puzzle is the theoretical foundation for *why* a positive Sharpe is expected in the first place — the equity premium is the numerator of the Sharpe ratio evaluated over long horizons.

**Relevant functions in `backtests/metrics.py`:**
- `sharpe_ratio()` — computes annualised excess return / volatility, the empirical analogue of the puzzle's 6% / 16.7%.
- `max_drawdown()` — captures the left tail that habit-formation and rare-disaster models are designed to explain.

### 7.2 Statistical Testing (`backtests/stats/sharpe_tests.py`)

The Probabilistic Sharpe Ratio (PSR) and Deflated Sharpe Ratio (DSR) modules implement the López de Prado framework for testing whether observed Sharpe ratios are significant. The Mehra-Prescott puzzle implies that a strategy earning an unconditional equity premium (~0.37 Sharpe) is the **minimum credible baseline** — any strategy claiming alpha must beat this before statistical testing even begins.

**Connection:** The minimum backtest length (`backtests/stats/minimum_backtest.py`) encodes the same insight: a strategy must survive a sufficiently long track record before its Sharpe can be trusted. For equity long-only strategies, the ~0.37 unconditional Sharpe of the market itself sets the floor; a strategy must clear this bar with statistical significance.

### 7.3 Benchmark Returns (`backtests/stats/multiple_testing.py`)

The White's Reality Check implementation uses a benchmark return array to test whether the best strategy in a sweep genuinely outperforms. The theoretically appropriate benchmark for equity strategies is the buy-and-hold market portfolio — whose expected excess return is precisely what Mehra-Prescott found inexplicably large. Setting `benchmark_returns` to the S&P 500 buy-and-hold is consistent with using the ERP as the null.

### 7.4 No Direct ERP Estimation Code Found

A search for `equity_premium`, `ERP`, and `risk_premium` in `backtests/` returned no matches. The codebase does not currently have a standalone equity premium estimation module. Opportunity: a forward-looking ERP estimator (dividend yield + growth + repricing) would fit naturally into `quant_data/analytics.py` or `portfolio/risk_analytics.py`.

---

## 8. Connections to This Study (Expected Returns — Ilmanen 2011)

- **Ch7 (Equity Risk Premium):** Ilmanen's Chapter 7 is the direct practitioner extension of this paper. Where Mehra-Prescott ask *why* the ERP is so large, Ilmanen asks *how large will it be going forward* and which forward-looking indicators best predict it (CAPE, dividend yield, earnings yield, surveys).
- **Ch5 (Rational Theories):** Ilmanen covers all major resolutions to the puzzle — habit formation, recursive preferences, rare disasters — under the umbrella of rational risk pricing. This paper is the empirical root of that section.
- **Ch1 (Introduction):** Ilmanen's opening frame — that assets command premia for performing poorly in bad times — is the intuition behind why habit-formation (Campbell-Cochrane) and rare-disaster (Barro) models succeed where simple CRRA fails.
- **Fama-French (1993) notes** in this study folder: FF factors add cross-sectional structure to the ERP. Mehra-Prescott establish the aggregate puzzle; FF establish that size and value represent additional cross-sectional slices of it.

---

## 9. Connections to Active Research

- **No active ERP-specific strategy** is in `research/STRATEGY_TRACKER.md`. The tracker shows equity work focused on momentum (Elena) and Quality + Safe-Haven (Elena, IN REVIEW).
- **Quality + Safe-Haven Overlay (Priority 2):** This strategy partly bets on the ERP being positive and persistent. Mehra-Prescott's puzzle is why the premium exists at all; the strategy's rationale is that quality stocks earn a premium above the market. The theoretical grounding should reference habit-formation or long-run risk models as the reason equity premia exist.
- **KNOWLEDGE_EQUITY.md** has no existing ERP entries. This paper warrants a new `equity-premium` topic block (see Section 10 below).

---

## 10. Suggested Knowledge Base Entry

New entry for `memory/knowledge/KNOWLEDGE_EQUITY.md` under a new `## Topic: equity-premium` block:

```
### Market Facts & Structural Observations
- US equity premium (1889–1978): ~6.18% arithmetic, ~4% geometric over T-bills | Mehra & Prescott (1985)
- Consumption growth volatility (~3.6%) is far too low to justify a 6% equity premium under CRRA with γ ≤ 10 | Mehra & Prescott (1985)
- Standard CRRA model predicts ERP of only ~0.35% — the puzzle gap is ~17× | [BOOK/ARTICLE] | 2026-03-30

### Key Papers & Concepts
- "The Equity Premium: A Puzzle" | Mehra & Prescott | 1985 | JME | relevance: 100/100 | foundational ERP puzzle paper | [BOOK/ARTICLE] | 2026-03-30
- Proposed resolutions: habit formation (Campbell-Cochrane 1999), recursive prefs (Epstein-Zin 1989, Bansal-Yaron 2004), rare disasters (Barro 2006), idiosyncratic risk (Constantinides-Duffie 1996), survivorship bias (Brown et al. 1995)

### Known Failure Modes
- Raising γ to match ERP simultaneously drives modelled R_f to 8–14% (Risk-Free Rate Puzzle, Weil 1989) — both puzzles must be solved jointly
- Geometric ERP (~3.5–4%) is roughly half the arithmetic figure; using arithmetic premia overstates the long-run compounded reward
```