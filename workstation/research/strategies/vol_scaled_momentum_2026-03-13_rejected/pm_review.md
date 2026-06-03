# PM Review: Vol-Scaled Momentum (Core)

> **Reviewer:** PM | **Date:** 2026-03-15 | **Strategy Folder:** `research/strategies/vol_scaled_momentum_2026-03-13_conditional/`

---

## [ROUND 1 REVIEW]

**Strategy:** Volatility-Scaled Momentum (Low-Turnover Core)
**Researcher:** Elena
**Folder:** `research/strategies/vol_scaled_momentum_2026-03-13_conditional/`
**Notebook:** `research_r1.ipynb`

---

### PRE-REVIEW FINDING: NOTEBOOK NOT EXECUTED

**This is a blocking issue.** I verified all 17 cells in `research_r1.ipynb`: every code cell has `execution_count: null` and zero outputs. This notebook contains only code -- there are no actual results, no equity curves, no gate values, no regime analysis outputs.

My PM protocol requires reviewing **executed notebooks with actual results**, not code proposals. I cannot issue a meaningful quantitative assessment without cell outputs.

**Elena must execute the notebook and re-submit with all cell outputs before any gate evaluation can proceed.**

---

### CHALLENGES

#### 1. [CRITICAL] Notebook not executed -- no results to review
- **Cell reference:** All code cells (cells 2-14, 16)
- **Detail:** Every code cell shows `execution_count: null` and empty `outputs: []`. There are no performance metrics, no equity curves, no gate values. The `signals_plot.png` exists in the folder (154KB) which suggests a partial run may have occurred outside the notebook, but the notebook itself has no evidence of execution.
- **Required action:** Execute the full notebook end-to-end and save with outputs. All 11 gates must have computed values visible in the cell outputs.

#### 2. [CRITICAL] Rebalance frequency `2ME` not supported by `PortfolioBuilder.backtest()`
- **Cell reference:** Cell 6 (line: `builder.config.rebalance_frequency = '2ME'`)
- **Detail:** I reviewed the `backtest()` method at `builder.py:461-468`. The rebalance frequency handler has three branches: `"daily"`, `"weekly"`, and `else` (which uses `"M"` monthly). The string `"2ME"` will fall into the `else` branch and be resampled as `"M"` (monthly), NOT bi-monthly. This means the strategy is actually rebalancing monthly, not bi-monthly as claimed.
- **Code evidence:** `builder.py:468` -- `rebal_dates = returns.resample("M").last().dropna().index`
- **Impact:** Monthly rebalancing doubles turnover relative to bi-monthly, which directly affects cost sensitivity gates. It also means the backtest does not match the proposal specification.
- **Required action:** Either (a) fix the `backtest()` method to handle `"2ME"` correctly (pass the frequency string to `resample()` directly), or (b) explicitly state in the notebook that the strategy is monthly-rebalanced and update the proposal accordingly.

#### 3. [CRITICAL] Sharpe ratio not risk-free adjusted
- **Cell reference:** Cell 7 (metrics) and `builder.py:530-534`
- **Detail:** The Sharpe ratio computation in `builder.py` is `mean / std * sqrt(252)` -- it does NOT subtract the risk-free rate. With Fed funds at ~4-5% during 2023-2024, this overstates Sharpe by approximately 0.2-0.3. This was flagged in my PM Framework Advisory as a known issue (A1), but for a formal gate evaluation the Sharpe MUST be risk-free adjusted.
- **Impact:** A full-period Sharpe of 0.7 would become ~0.4-0.5 after adjustment -- potentially failing the `Sharpe (IS) > 0.5` gate.
- **Required action:** Compute Sharpe as `(mean_return - rf_rate) / std * sqrt(252)`. Use the FRED DGS3MO series or a constant 0.02 floor for the risk-free rate. Report both adjusted and unadjusted.

#### 4. [HIGH] Walk-forward uses initial weight seed from full IS period, not per-window training
- **Cell reference:** Cell 10 (walk-forward)
- **Detail:** In the walk-forward loop, `wf_builder.optimize_weights(as_of_date=train_end)` optimizes using the full price history up to `train_end`. However, `wf_builder.prices = prices` assigns the FULL 2010-2024 price history. Combined with `dynamic_reoptimize=True`, the backtest will re-optimize at each rebalance date using `_optimize_weights_as_of()` which calls `_alpha_as_of()` with `sig_df.loc[:as_of_date]`. This correctly limits the signal data, but the `_optimize_weights_as_of()` method at `builder.py:350-374` computes covariance from `self.prices.loc[:as_of_date].pct_change()` -- which uses all available price data up to that date, including data before the training window start.
- **Impact:** For a walk-forward window with training from 2014-2018 and test from 2018-2019, the covariance estimation in the test period uses data from 2010-2018 (not just the training window 2014-2018). This is not technically look-ahead bias (it only uses past data), but it means the walk-forward is not a true "rolling window" test -- it's an expanding-window test. This is more forgiving and may overstate walk-forward hit rates.
- **Required action:** Document this clearly. If the strategy is meant to use expanding-window covariance (defensible), state it explicitly. If rolling-window is intended, restrict the price data to the training window.

#### 5. [HIGH] `expanding_zscore()` in notebook differs from `SignalBlender.compute()` normalization
- **Cell reference:** Cell 4 (signal construction)
- **Detail:** Elena implements her own `expanding_zscore()` function in Cell 4 that applies cross-sectional z-scoring first (across tickers at each date), then time-series expanding normalization. This is a TWO-STAGE normalization. Meanwhile, the `SignalBlender.compute()` at `signals.py:332-336` uses a single-stage expanding-window z-score on the raw signal values (no cross-sectional normalization first).
- **Impact:** These are mathematically different transformations. The notebook's approach is arguably better (cross-sectional normalization removes level effects), but it means the notebook results are NOT reproducible using the framework's `SignalBlender` class. If the strategy is approved, which normalization will be used in production?
- **Required action:** Either (a) use `SignalBlender.compute()` directly for reproducibility, or (b) propose Elena's two-stage normalization as an upgrade to `SignalBlender` and get Dev to implement it before approval. The notebook must use whichever method will be used in production.

#### 6. [HIGH] Annual turnover calculation is incorrect
- **Cell reference:** Cell 7 (core metrics)
- **Detail:** The code computes `annual_turnover = daily_returns.diff().abs().sum() / (n_days / 252) * 100`. This is computing the sum of absolute changes in *portfolio returns*, not the sum of absolute changes in *portfolio weights*. These are completely different quantities. Turnover should be calculated from `weight_matrix.diff().abs().sum(axis=1).sum() / (n_days/252)`, which is available from the backtest internals but is not exposed in the result dict.
- **Impact:** The annual turnover gate (`< 150%`) cannot be evaluated with this metric. The actual turnover could be significantly different from what is reported.
- **Required action:** Compute turnover correctly from weight changes, not return changes. If the backtest result dict doesn't expose the weight matrix, add it or compute turnover inside the `backtest()` method and include it in the results.

#### 7. [HIGH] Cerebro HIGH contradiction not addressed: Cederburg et al. (2020) OOS instability
- **Cell reference:** N/A (missing from notebook)
- **Detail:** Cederburg et al. (2020, JFE) found that individual-factor vol management does not produce OOS gains. DeMiguel et al. (2024) partially rehabilitates this for multifactor portfolios. Elena's notebook does not reference or address this contradiction. The walk-forward analysis is the primary defense, but there is no explicit discussion of why her 3-signal blend should escape the Cederburg critique.
- **Required action:** Address in the hypothesis section or a dedicated discussion cell. Specifically: (a) acknowledge the Cederburg finding, (b) argue how the multifactor blend differs from single-factor vol management, (c) show that OOS walk-forward results are consistent with the DeMiguel multifactor finding (OOS Sharpe ratio should not collapse relative to IS).

#### 8. [HIGH] Cerebro HIGH contradiction not addressed: Barroso & Detzel (2021) cost erosion in low-sentiment
- **Cell reference:** Cell 11 (cost sensitivity)
- **Detail:** Barroso & Detzel (2021) find vol-managed portfolio gains disappear in low-sentiment periods after transaction costs. Elena's cost sensitivity analysis runs costs uniformly across the entire backtest period, which does not test whether the strategy survives in low-sentiment subperiods specifically.
- **Required action:** Add a regime-conditional cost analysis. At minimum, show the strategy's Sharpe at 2x costs during the worst regime (from the regime analysis cell). If the strategy only survives costs in bull markets, that is a material weakness.

#### 9. [MEDIUM] MTUM holdings overlap not computed
- **Cell reference:** Missing
- **Detail:** Cerebro flagged that iShares MTUM ($10B+ AUM) runs near-identical signals (6-12m risk-adjusted returns + low vol). If Elena's 10-15 stock portfolio overlaps >70% with MTUM, the strategy is effectively a concentrated version of a commodity ETF with no differentiated alpha.
- **Required action:** Download MTUM top holdings (available from iShares website) and compute Jaccard overlap with the strategy's portfolio at the most recent rebalance date. Report the overlap percentage.

#### 10. [MEDIUM] Mean-reversion dampener weight (-0.20) -- regime sensitivity not tested
- **Cell reference:** Cell 13 (parameter sensitivity)
- **Detail:** The parameter sensitivity analysis tests vol lookback, momentum lookback, and risk aversion -- but does NOT test the mean-reversion dampener weight. The -0.20 weight is flagged in both the proposal and Cerebro briefing as ad hoc. Cerebro specifically notes it hurts in trending regimes (2024 momentum was +32.89%).
- **Required action:** Add sensitivity tests for the mean-reversion weight: -0.40, -0.30, -0.20 (base), -0.10, 0.00 (no dampener). If the strategy performs better with weight=0 than weight=-0.20, the dampener is not earning its place.

#### 11. [MEDIUM] IS/OOS split hardcoded but not used in full-sample backtest
- **Cell reference:** Cell 2 (config) and Cell 6 (backtest)
- **Detail:** Elena defines `IS_END = '2021-12-31'` and `OOS_START = '2022-01-01'` but the main backtest (Cell 6) runs from the warmup period through `END_DATE = '2024-12-31'`. The full-sample Sharpe therefore includes both IS and OOS data. This is not inherently wrong, but the gate table should separately report IS Sharpe and OOS Sharpe.
- **Required action:** Report IS Sharpe (2010-2021) and OOS Sharpe (2022-2024) separately in the gate table. The `Sharpe (IS) > 0.5` gate should use only IS data.

#### 12. [MEDIUM] No benchmark comparison
- **Cell reference:** Missing
- **Detail:** There is no SPY or equal-weight benchmark comparison. Without a benchmark, it is impossible to determine whether the strategy produces alpha or merely tracks the market with higher fees.
- **Required action:** Add an equal-weight benchmark (buy-and-hold all 30 tickers) and SPY benchmark. Compute excess returns, information ratio, and beta. The strategy must demonstrate positive alpha net of costs vs. the equal-weight benchmark.

---

### POSITIVE NOTES

1. **Signal weights pre-committed.** Cell 2 clearly documents `WEIGHT_INVVOL = 0.40`, `WEIGHT_MOMENTUM = 0.40`, `WEIGHT_MEANREV = -0.20` with a comment "from proposal.md -- DO NOT TUNE." This addresses the prior CONDITIONAL blocker about in-sample weight optimization.

2. **Expanding-window normalization implemented.** Cell 4's `expanding_zscore()` function correctly uses `expanding(min_periods=60)` to avoid look-ahead bias in signal normalization. This addresses the prior SignalBlender look-ahead blocker, though via custom code rather than the framework class (see Challenge #5).

3. **CompositeCostModel used correctly.** Cell 6 uses `CompositeCostModel` with `FixedCostModel(0.005)` and `ProportionalCostModel(10 bps)`. This is a realistic cost structure and addresses the prior blocker about flat commission rates.

4. **dynamic_reoptimize=True enabled.** Cell 6 correctly passes `dynamic_reoptimize=True` to the backtest, which addresses B3 (static weights overstating stability).

5. **Cost sensitivity analysis at multiple levels.** Cell 11 tests 0x, 1x, 1.5x, 2x, 3x costs -- exceeding the minimum requirement of just 2x.

6. **Warmup period enforced.** Cell 4 computes `WARMUP = 252 + 60 = 312` trading days and Cell 5 drops the warmup period before alpha computation.

7. **N_TRIALS = 1 declared honestly.** Cell 2 sets `N_TRIALS = 1` with a comment that only one pre-committed configuration is tested. This is honest accounting for the Deflated Sharpe computation.

8. **Well-structured notebook.** The 16-cell template is followed correctly, with proper separation of concerns. The code is readable and well-commented.

---

### REQUIRED ACTIONS (before Round 2)

**Must-fix (CRITICAL -- Round 2 cannot proceed without these):**
1. Execute the notebook end-to-end and save with all cell outputs
2. Fix the `2ME` rebalance frequency issue (currently defaults to monthly)
3. Compute risk-free-adjusted Sharpe ratio

**High-priority (must address quantitatively in Round 2 notebook):**
4. Clarify expanding-window vs. rolling-window covariance in walk-forward
5. Reconcile notebook's `expanding_zscore()` with `SignalBlender.compute()` -- decide which is production
6. Fix annual turnover calculation
7. Address Cederburg et al. OOS instability finding with IS vs. OOS Sharpe comparison
8. Add regime-conditional cost analysis (Barroso & Detzel critique)

**Medium-priority (address in Round 2 or document as known limitation):**
9. Compute MTUM holdings overlap
10. Test mean-reversion dampener weight sensitivity
11. Report IS and OOS Sharpe separately
12. Add SPY and equal-weight benchmark comparison

---

### GATE EVALUATION STATUS

**Cannot evaluate.** Notebook was not executed. All 11 gates are PENDING.

| Gate | Status | Notes |
|------|--------|-------|
| Deflated Sharpe > 0 | PENDING | No outputs |
| WF hit rate > 55% | PENDING | No outputs |
| Survives 2x costs (Sharpe > 0) | PENDING | No outputs |
| PSR > 0.80 | PENDING | No outputs |
| Worst regime loss > -15% | PENDING | No outputs |
| Strategy half-life > 2 yrs | PENDING | No outputs |
| MinBTL < data length | PENDING | No outputs |
| Max drawdown < 25% | PENDING | No outputs |
| Annual turnover < 150% | PENDING | Calculation is wrong (Challenge #6) |
| Sharpe (IS) > 0.5 | PENDING | Must be risk-free adjusted (Challenge #3), must use IS-only data (Challenge #11) |
| 3x cost sensitivity (Sharpe > 0) | PENDING | No outputs |

---

*PM -- Zelin Investment Research | Round 1 Review | 2026-03-15*

---
---

## [ROUND 2 REVIEW]

**Strategy:** Volatility-Scaled Momentum (Low-Turnover Core)
**Researcher:** Elena
**Folder:** `research/strategies/vol_scaled_momentum_2026-03-13_conditional/`
**Notebook:** `research_r1.ipynb` (now executed)
**Date:** 2026-03-15

---

### ROUND 1 CHALLENGE RESOLUTION

#### CRITICAL #1 -- Notebook not executed: RESOLVED
All 17 cells now have execution outputs. The notebook ran end-to-end without errors. Data downloaded: 28/30 tickers retained (META and ABBV likely dropped due to shorter history -- need to confirm which 2 dropped). Backtest period: 2011-03-30 to 2024-12-30 (3,460 trading days, 13.7 years).

#### CRITICAL #2 -- Rebalance frequency `2ME` bug: RESOLVED
Elena changed from `'2ME'` to `'2M'` in Cell 2. Dev fixed `builder.py:469-472` to add an `else` branch that passes the configured frequency string directly to `resample()`. The strategy is now correctly rebalancing bi-monthly. Confirmed by reading the updated `builder.py` code.

#### CRITICAL #3 -- Sharpe not risk-free adjusted: **NOT RESOLVED**
The Sharpe ratio in Cell 7 (`sharpe = result['sharpe_ratio']`) still comes from `builder.py:530-534`, which computes `mean / std * sqrt(252)` without subtracting the risk-free rate. The reported 0.885 is unadjusted.

**PM adjustment:** Over 2011-2024, the average 3-month T-bill rate was approximately 1.5% (near-zero from 2011-2021, rising to 4-5% in 2022-2024). The time-weighted average risk-free rate for this period is roughly 1.5-2.0%. The Sharpe adjustment is:
- Risk-free adjusted Sharpe = (15.42% - 1.5%) / 18.06% = **0.770** (using 1.5% average rf)
- Risk-free adjusted Sharpe = (15.42% - 2.0%) / 18.06% = **0.743** (using 2.0% average rf)

Either way, the risk-free adjusted Sharpe remains above the 0.5 gate threshold. **The gate PASSES even after adjustment**, but the reported number is overstated by ~0.12-0.14 and Elena must fix this in R2.

#### HIGH #4 -- Walk-forward expanding-window covariance: **NOT EXPLICITLY ADDRESSED**
The walk-forward in Cell 10 still passes `prices = prices` (full history). However, I note that `dynamic_reoptimize=True` calls `_optimize_weights_as_of()` which uses `self.prices.loc[:as_of_date]` -- this is an expanding window by design. Since the signals are also computed on an expanding window (via `expanding_zscore()`), this is internally consistent. The expanding-window approach is defensible for covariance estimation (more data = more stable estimates), and is commonly used in practice (Ledoit-Wolf shrinkage targets benefit from larger samples).

**PM assessment:** Accept as-is. Document in the final strategy specification that the covariance estimator uses all available history (expanding window), not a rolling window.

#### HIGH #5 -- Custom `expanding_zscore()` vs `SignalBlender.compute()`: **NOT ADDRESSED**
Elena's notebook still uses the custom two-stage normalization (cross-sectional z-score first, then time-series expanding normalization). The `SignalBlender.compute()` uses single-stage expanding z-score.

**PM assessment:** Downgraded to MEDIUM for R2. Elena's approach is defensible and arguably superior. However, if the strategy is approved, Dev must implement the two-stage normalization into the production `SignalBlender` (or create a new `CrossSectionalBlender` class) before paper trading begins. This is a production readiness item, not a research validity issue.

#### HIGH #6 -- Annual turnover calculation: **NOT FIXED**
Cell 7 still computes: `annual_turnover = daily_returns.diff().abs().sum() / (n_days / 252) * 100`. This computes the sum of absolute daily return changes (a measure of return volatility), not portfolio turnover. The reported 283% is meaningless.

**PM assessment:** This gate CANNOT be evaluated. The actual turnover depends on the weight changes at each bi-monthly rebalance. Given 6 rebalances per year with `turnover_penalty=0.5` in the optimizer, I would expect annual one-way turnover in the 40-80% range for a 28-stock mean-variance optimized portfolio. The 283% reported number is clearly wrong -- it's measuring something completely different. **This gate remains PENDING until correctly computed in R2.**

#### HIGH #7 -- Cederburg et al. OOS instability: **NOT EXPLICITLY ADDRESSED IN NOTEBOOK**
No discussion cell was added. However, the walk-forward results provide the quantitative rebuttal:
- Average OOS Sharpe: 1.073 across 9 windows
- Average OOS return: 17.62%
- The OOS Sharpe (1.073) *exceeds* the full-sample IS Sharpe (0.885)
- 8 of 9 windows have positive OOS Sharpe

This is strong evidence against the Cederburg critique, though the OOS Sharpe exceeding IS Sharpe is itself unusual and warrants scrutiny (see New Challenges below).

#### HIGH #8 -- Barroso & Detzel regime-conditional costs: **NOT ADDRESSED**
No regime-conditional cost analysis was added. The cost sensitivity (Cell 11) still runs uniformly across the full period. We know from the regime analysis that `trend_bear` has -52.69% annualized return -- applying 2x costs to this regime would make it even worse, not better.

**PM assessment:** This is less critical than it appeared in R1. The Barroso & Detzel finding concerns *high-frequency vol-managed portfolios* where turnover is the primary cost driver. Elena's bi-monthly rebalancing has much lower turnover sensitivity. At 3x costs the strategy still shows Sharpe 0.595. However, the trend_bear regime itself is the bigger problem (see Gate Analysis below).

#### MEDIUM #9-12 -- MTUM overlap, dampener sensitivity, IS/OOS split, benchmark: **NOT ADDRESSED**
None of these were addressed in the executed notebook. These remain open for R2.

---

### DETAILED GATE ANALYSIS

| # | Gate | Value | Threshold | Status | PM Notes |
|---|------|-------|-----------|--------|----------|
| 1 | Sharpe (IS) | 0.885 (unadj) / ~0.77 (adj) | > 0.5 | **PASS** | Passes even after rf adjustment of ~0.12. Must compute properly in R2. |
| 2 | Deflated Sharpe | 1.0000 | > 0 | **PASS** | N_TRIALS=1 with honest pre-committed config. DSR is mechanically high with N=1. |
| 3 | PSR | 99.9% | > 80% | **PASS** | Very strong. PSR vs benchmark_sharpe=0 with 3,460 observations. Robust. |
| 4 | WF Hit Rate | 88.9% (8/9) | > 55% | **PASS** | Strong. Only Window 5 (Apr 2019 - Apr 2020, COVID crash) has negative OOS Sharpe. |
| 5 | Survives 2x Costs | 0.740 | Sharpe > 0 | **PASS** | Comfortable margin. Even 3x costs gives 0.595. |
| 6 | Cost Sensitivity (3x) | 0.595 | Sharpe > 0 | **PASS** | Good. Cost erosion is ~0.12 Sharpe per 1x cost multiplier -- linear and moderate. |
| 7 | Worst Regime Loss | -52.69% (trend_bear) | > -15% | **FAIL** | Severe failure. -52.69% annualized in trend_bear regime (738 days). This is not a minor miss -- it is 3.5x the threshold. See detailed analysis below. |
| 8 | Strategy Half-Life | 11.7 years | > 2 years | **PASS** | Comfortable. |
| 9 | MinBTL | 11.8 years | < 13.7 years | **PASS** | Narrow margin: only 1.9 years of headroom. If the data were shorter by 2 years, this would fail. |
| 10 | Max Drawdown | -32.00% | < 25% | **FAIL** | 7 percentage points above threshold. Consistent with the trend_bear regime failure. |
| 11 | Annual Turnover | 283% (WRONG) | < 150% | **PENDING** | Calculation is return-based, not weight-based. Cannot evaluate. |
| 12 | LLM Verdict | Not run | != ABANDON | **PENDING** | No API key. Not blocking but noted. |

**Summary: 8 PASS, 2 FAIL, 2 PENDING**

---

### NEW CHALLENGES (Round 2)

#### 1. [CRITICAL] trend_bear regime: -52.69% annualized, -88.64% max drawdown
This is the hard blocker. The strategy loses more than half its value annualized during bear trends, with a drawdown approaching -89%. This is not a momentum strategy that "reduces crash exposure" as the hypothesis claims -- this is a strategy that gets destroyed in bear markets.

**Root cause analysis:** The trend_bear regime spans 738 days (approximately 3 years out of 13.7). During these periods, the strategy is fully invested (long-only, 100% gross) in stocks selected for momentum and low-vol. When the market regime shifts to bear:
- Momentum stocks reverse violently (Daniel & Moskowitz 2016 momentum crash)
- Low-vol stocks, which have become crowded, also underperform
- The mean-reversion dampener (-0.20 weight) is too weak to provide meaningful protection
- The strategy has NO cash allocation, NO hedging, NO exposure reduction mechanism

The vol-scaling in this strategy only affects *which* stocks to hold (via the signal blend), not *how much* to hold. There is no portfolio-level vol targeting that would reduce gross exposure during high-vol regimes -- which is exactly the mechanism that Moreira & Muir (2017) found produces the alpha.

**What would satisfy me:** Elena must demonstrate ONE of the following approaches in R2:
- **(a) Portfolio-level vol targeting:** Scale gross exposure inversely with realized portfolio vol (e.g., target 12% annualized vol). When 60-day realized vol exceeds the target, reduce gross from 1.0x to (target_vol / realized_vol). This is the Moreira & Muir mechanism and would mechanically reduce exposure before crashes.
- **(b) Regime filter with cash:** When the RegimeAnalyzer identifies `trend_bear`, move to 50%+ cash. This is crude but effective. Must show it does not destroy the bull market returns via whipsawing.
- **(c) Lower the gate threshold with explicit risk budget:** If the strategy is intended as a 10-15% allocation in a diversified portfolio (not standalone), the -15% worst-regime gate could be relaxed. But then Elena must show the strategy-level drawdown stop at -15% (from Capital Policy) would be triggered, AND show what happens to the portfolio after the stop is triggered (recovery time, re-entry logic).
- **(d) Tail hedge overlay:** Add a VIX-based or put-spread hedge that activates in high-vol regimes. Must show cost of the hedge in normal times and protection in bear regime.

The raw strategy as presented CANNOT be approved for standalone use. -52.69% annual and -88.64% drawdown in bear markets would violate our per-strategy drawdown stop (-15%) within weeks.

#### 2. [CRITICAL] Max drawdown -32.00% exceeds -25% gate
This is directly related to Challenge #1 above. The -32.00% max DD occurs during the trend_bear regime (likely the 2020 COVID crash, visible in WF Window 5 which shows -30.72% DD). Any solution to Challenge #1 that reduces bear-market exposure will also address this gate.

**What would satisfy me:** Max drawdown below -25% after applying the vol-targeting or regime-filter mechanism from Challenge #1.

#### 3. [HIGH] Annual turnover gate cannot be evaluated
The 283% number is wrong (computes return diffs, not weight diffs). Elena must compute actual annual one-way turnover from weight changes.

**What would satisfy me:** Compute turnover as: `sum(|w_t - w_{t-1}|) / 2` per rebalance, annualized. If the builder does not expose weight history in the result dict, compute it externally by re-running the backtest and tracking weight changes, or modify the builder to return the weight matrix.

Given bi-monthly rebalancing with turnover_penalty=0.5, I expect true one-way turnover to be in the 40-80% range. If it exceeds 150%, the bi-monthly rebalance frequency needs to be reduced to quarterly.

#### 4. [HIGH] OOS Sharpe (1.073) exceeds IS Sharpe (0.885) -- suspicious
In my PM Framework Advisory, I listed "Walk-forward OOS Sharpe exceeds IS Sharpe" as an escalation trigger. This is happening here. The average OOS Sharpe across 9 walk-forward windows (1.073) exceeds the full-sample Sharpe (0.885).

**Possible explanations:**
- (a) The 2020-2021 post-COVID recovery (Window 6: Sharpe 2.428, return 66.74%) is an extreme outlier that pulls up the OOS average. Without Window 6, the average OOS Sharpe drops to (1.073*9 - 2.428) / 8 = 0.904, which is close to the IS Sharpe. This is the most benign explanation.
- (b) The expanding-window covariance estimation actually helps OOS performance because more data = better estimates. Plausible.
- (c) Some form of forward leakage that I haven't identified. Less likely given the code review, but not impossible.

**What would satisfy me:** Report OOS Sharpe with and without the 2020-2021 window. If the ex-Window-6 OOS Sharpe is <= IS Sharpe, the anomaly is explained by the COVID recovery outlier and is acceptable. Also compute the IS-only Sharpe (2011-2021) and OOS-only Sharpe (2022-2024) for the full backtest.

#### 5. [MEDIUM] Risk aversion parameter has ZERO effect on results
The parameter sensitivity (Cell 13) shows that risk aversion variations from 1.8 to 4.2 produce Sharpe ratios of 0.883-0.885 -- essentially identical. This means the optimizer is not actually varying weights in response to risk aversion changes, which suggests the optimization is hitting the max_weight constraint (0.12) for most assets and the risk_aversion parameter is inoperative.

**What would satisfy me:** Investigate why risk aversion has no effect. Show the weight distribution at a sample rebalance date under risk_aversion=1.8 vs 4.2. If the weights are identical because of binding constraints, either: (a) relax max_weight to 0.15-0.20 and re-test, or (b) acknowledge that the optimizer is effectively constraint-driven, not alpha-driven, and document this.

#### 6. [MEDIUM] Deflated Sharpe Ratio = 1.0000 is suspiciously perfect
DSR = 1.0000 exactly. With N_TRIALS=1, the deflation adjustment is minimal, which is expected. However, a DSR of exactly 1.0 (not 0.9998 or 0.9973) suggests the implementation may be clipping or saturating. This should be at least a few basis points below 1.0 for any realistic return distribution.

**What would satisfy me:** Print the raw DSR value to 8 decimal places. If it is truly 1.0000000, check the `deflated_sharpe_ratio()` implementation -- it may be clipping the output or using an incorrect formula for N=1. This does not affect the gate (DSR > 0 passes regardless), but it affects confidence in the statistical testing suite.

#### 7. [MEDIUM] Walk-Forward Window 5 (2019-2020): the COVID stress test
Window 5 is the only negative OOS window: Sharpe -0.111, return -8.32%, DD -30.72%. This period includes the COVID crash (March 2020). The strategy LOST money during the fastest and deepest crash in the backtest -- and this is before the trend_bear regime analysis shows even worse numbers (-52.69% annualized).

This window is actually the BEST argument for why the vol-targeting mechanism (Challenge #1) is essential. The strategy had no mechanism to reduce exposure as vol spiked in February-March 2020.

---

### VERDICT: CONDITIONAL

**The strategy CANNOT receive APPROVED at this time.**

**Reasons:**
1. Two hard gate failures (worst regime -52.69%, max DD -32.00%) that are structurally related -- the strategy has no downside protection mechanism
2. One gate cannot be evaluated (annual turnover -- calculation is wrong)
3. One gate is pending (LLM verdict -- no API key)
4. Sharpe ratio is not risk-free adjusted (passes either way, but must be fixed for accuracy)
5. Several Round 1 HIGH/MEDIUM challenges remain unaddressed

**What is needed for APPROVED:**

Elena must submit `research_r2.ipynb` that addresses:

| # | Requirement | Priority | Concrete Target |
|---|-------------|----------|-----------------|
| 1 | Add portfolio-level vol targeting OR regime filter | CRITICAL | Worst regime annual loss > -15%, max DD < 25% |
| 2 | Fix annual turnover calculation (weight-based, not return-based) | CRITICAL | Must compute correctly; target < 150% |
| 3 | Compute risk-free adjusted Sharpe | HIGH | Use average T-bill rate over backtest period |
| 4 | Report IS-only and OOS-only Sharpe separately | HIGH | IS Sharpe (2011-2021), OOS Sharpe (2022-2024) |
| 5 | Explain OOS > IS Sharpe anomaly | HIGH | Report ex-Window-6 OOS Sharpe |
| 6 | Investigate risk_aversion having zero effect | MEDIUM | Show weight distributions under different risk aversion |
| 7 | Print DSR to 8 decimal places | MEDIUM | Verify not clipped at 1.0 |
| 8 | Add SPY/equal-weight benchmark comparison | MEDIUM | Demonstrate positive alpha vs benchmarks |

**If Elena can bring worst regime above -15% and max DD below -25% via a vol-targeting mechanism, while maintaining Sharpe > 0.5 (risk-free adjusted), I will approve the strategy for paper trading.**

The other passing gates are strong: PSR 99.9%, WF hit rate 88.9%, cost sensitivity excellent, half-life 11.7 years, parameter sensitivity robust. The core signal construction is sound. The strategy needs a risk management wrapper, not a fundamental redesign.

---

*PM -- Zelin Investment Research | Round 2 Review | 2026-03-15*

---
---

## [ROUND 3 — FINAL REVIEW AND VERDICT]

**Strategy:** Volatility-Scaled Momentum (Low-Turnover Core)
**Researcher:** Elena
**Folder:** `research/strategies/vol_scaled_momentum_2026-03-13_conditional/`
**Notebook:** `research_r2.ipynb`
**Date:** 2026-03-15

---

### EXECUTIVE SUMMARY

This is the final review round. Elena submitted `research_r2.ipynb` addressing Round 1 challenges. The notebook is fully executed (18 code cells, all with outputs). Elena addressed many of my Round 1 concerns well -- risk-free adjusted Sharpe, proper weight-based turnover, rolling-window walk-forward, Cederburg holdout test, Barroso VIX analysis, MTUM overlap, benchmark comparison, and mean-reversion sensitivity.

However, the **primary CRITICAL requirement from Round 2 was not addressed**: Elena did NOT implement portfolio-level vol targeting despite Dev having implemented the `target_vol` parameter in `builder.backtest()`. The strategy still runs at 100% gross exposure at all times, which is why the regime and drawdown gates remain in failure.

The R2 notebook also revealed new problems: the strategy DETERIORATED from 8/11 gates passing (R1) to 7/11 gates passing (R2) after applying the corrections I required. Additionally, the Barroso VIX-conditioned analysis revealed a devastating weakness that was not visible in R1.

---

### ROUND 2 CHALLENGE RESOLUTION STATUS

#### R2 CRITICAL #1 — Portfolio-level vol targeting for worst regime: **NOT ADDRESSED**
This was the single most important requirement in my Round 2 review. I stated: "Elena must demonstrate ONE of: (a) portfolio-level vol targeting, (b) regime filter, (c) risk budget framing, (d) tail hedge overlay."

Dev implemented `target_vol` in `builder.backtest()` at `builder.py:424,508-524`. The parameter is available and functional. Elena simply did not use it. The backtest call in Cell 6 (R2) passes `dynamic_reoptimize=True` but does NOT pass `target_vol=0.12`.

**Result:** Worst regime is -52.94% annualized (WORSE than R1's -52.69%). Max drawdown is unchanged at -32.00%. Both gates remain in hard failure.

#### R2 CRITICAL #2 — Max drawdown below -25%: **NOT ADDRESSED**
Same root cause as #1. Without vol targeting, the strategy is fully invested during crash periods.

#### R2 CRITICAL #3 — Fix annual turnover calculation: **RESOLVED, but gate FAILS**
Elena correctly recomputed turnover from weight diffs using the weight matrix. The proper annual turnover is 369%, which is 2.5x the 150% threshold. This is a NEW gate failure that was masked in R1 by the incorrect calculation.

**Root cause analysis:** With bi-monthly rebalancing (6 times per year) and mean-variance optimization with `turnover_penalty=0.5`, 369% one-way annual turnover means the portfolio turns over approximately 62% per rebalance event. For a 28-stock long-only portfolio with max_weight=0.12, this is extremely high. The optimizer is making large position shifts at each rebalance, which suggests the alpha signal is noisy and the optimizer is chasing short-lived signal variations.

#### R2 HIGH #4 — IS and OOS Sharpe separation: **RESOLVED, reveals severe decay**
- IS Sharpe (2011-2021, RF-adjusted): **0.700** -- PASSES gate (> 0.5)
- OOS Sharpe (2022-2024, RF-adjusted): **0.117** -- severe decay
- IS/OOS Ratio: **0.17** -- the OOS Sharpe is only 17% of the IS Sharpe

This is a damning result. The strategy's edge has largely evaporated in the most recent 3-year period. While the IS Sharpe passes the gate, the OOS decay ratio of 0.17 indicates the strategy may not be viable going forward.

**Mitigating factor:** The Cederburg holdout test (Cell 15) using a 2010-2019 / 2020-2024 split shows a decay ratio of 0.78 (IS Sharpe 0.656, OOS Sharpe 0.510). This is much more favorable. The discrepancy arises because the 2020-2021 COVID recovery period (which includes WF Window 6 with Sharpe 2.134) falls into OOS in the Cederburg test but IS in the formal IS/OOS split. The 2022-2024 period is simply a poor one for the strategy.

#### R2 HIGH #5 — OOS > IS Sharpe anomaly explained: **PARTIALLY RESOLVED**
The WF OOS average (0.706 RF-adjusted) no longer exceeds IS (0.700), which removes the anomaly. With rolling-window covariance, the WF results are more conservative: hit rate dropped from 88.9% to 66.7%, average OOS Sharpe from 1.073 to 0.706. These are more realistic numbers.

#### R2 HIGH #6 — Risk aversion zero effect: **NOT ADDRESSED**
Risk aversion still has essentially zero effect (Sharpe range: 0.589-0.591 across 1.8-4.2 risk aversion). This confirms the optimizer is constraint-bound, not alpha-driven. Elena did not investigate this.

#### R2 HIGH #7 — Barroso VIX-conditioned costs: **RESOLVED, confirms weakness**
This was thoroughly addressed and the result is devastating:
- **High VIX (>20, 27% of days):** Sharpe = **-1.305** at 1x costs, **-1.318** at 2x costs
- **Low VIX (<=20, 73% of days):** Sharpe = **+2.255** at 1x costs

The strategy is a **pure fair-weather fund**. It earns all its returns during calm markets and gives back catastrophically during stressed markets. This confirms the Barroso & Detzel critique exactly. The aggregate Sharpe of 0.591 is an average of a +2.255 calm-weather Sharpe and a -1.305 stressed-weather Sharpe, weighted by time spent in each regime.

This is not merely a "vol-scaled momentum" strategy -- it is a **leveraged bet on continued low-volatility bull markets**. When VIX exceeds 20, the strategy annualizes at -31% returns. This is EXACTLY what portfolio-level vol targeting was designed to prevent.

#### R2 MEDIUM #8 — Mean-reversion dampener sensitivity: **RESOLVED**
Elena tested MR weights from -0.40 to 0.00:
- MR = -0.40: Sharpe 0.654, DD -27.68% (BEST Sharpe and BEST DD)
- MR = -0.30: Sharpe 0.641, DD -30.79%
- MR = -0.20: Sharpe 0.591, DD -32.00% (BASE)
- MR = -0.10: Sharpe 0.525, DD -31.17%
- MR = 0.00: Sharpe 0.533, DD -28.94%

The current -0.20 weight is NOT optimal. The dampener works better at -0.40 (Sharpe +0.063 improvement, DD -4.32 percentage points improvement). However, this was a pre-committed parameter and I would not allow in-sample re-optimization. The fact that the strategy is sensitive to the MR weight (range 0.525-0.654) is notable but not disqualifying, since all tested values produce positive Sharpe.

#### R2 MEDIUM #9 — MTUM overlap: **RESOLVED, LOW risk**
Overlap: 8/20 stocks (40%), Jaccard index 0.25. The strategy is differentiated from MTUM. This is a good result.

#### R2 MEDIUM #10 — Benchmark comparison: **RESOLVED, reveals alpha concern**
- vs SPY: Alpha +2.64%, Beta 0.944, IR 0.223 -- modest positive alpha
- vs Equal-Weight: Alpha **-2.60%**, Beta 1.009, IR -0.331 -- **NEGATIVE alpha**

The strategy UNDERPERFORMS a naive equal-weight buy-and-hold of the same 28 stocks by 2.60% annually. The dynamic optimization and signal-driven stock selection actually DESTROY value compared to simply equal-weighting and rebalancing. This is a serious concern. It suggests the signal blend and mean-variance optimization are adding noise, not alpha.

The positive alpha vs SPY (+2.64%) comes from the universe selection (US large-cap stocks that happened to outperform SPY in this period), not from the signal-driven weight optimization.

---

### FINAL GATE TABLE (Round 3)

| # | Gate | R1 Value | R2 Value | Threshold | R1 Status | R2 Status | Trend |
|---|------|----------|----------|-----------|-----------|-----------|-------|
| 1 | Sharpe IS (RF-adj) | 0.885 (unadj) | 0.700 (adj) | > 0.5 | PASS | **PASS** | Corrected |
| 2 | Deflated Sharpe | 1.0000 | 1.0000 | > 0 | PASS | **PASS** | Stable |
| 3 | PSR | 99.9% | 98.5% | > 80% | PASS | **PASS** | Slight decline |
| 4 | WF Hit Rate | 88.9% | 66.7% | > 55% | PASS | **PASS** | Declined (rolling cov) |
| 5 | Survives 2x Costs | 0.740 | 0.449 | Sharpe > 0 | PASS | **PASS** | Declined (RF adj) |
| 6 | 3x Cost Sensitivity | 0.595 | 0.307 | Sharpe > 0 | PASS | **PASS** | Declined (RF adj) |
| 7 | Worst Regime Loss | -52.69% | -52.94% | > -15% | FAIL | **FAIL** | Worsened |
| 8 | Strategy Half-Life | 11.7 yrs | 2935.6 yrs | > 2 yrs | PASS | **PASS** | Unstable metric |
| 9 | MinBTL | 11.8 yrs | 16.4 yrs | < 13.7 yrs | PASS | **FAIL** | NEW FAIL |
| 10 | Max Drawdown | -32.00% | -32.00% | < 25% | FAIL | **FAIL** | Unchanged |
| 11 | Annual Turnover | 283% (wrong) | 369% (correct) | < 150% | PENDING | **FAIL** | NEW FAIL |

**Final score: 7 PASS, 4 FAIL (down from 8/11 in R1)**

---

### COMPREHENSIVE RISK ASSESSMENT

#### Structural Weaknesses Confirmed in R2

1. **No downside protection mechanism.** Despite being called "volatility-scaled momentum," the strategy does not scale portfolio exposure with volatility. It only uses vol to select stocks. The `target_vol` parameter was implemented by Dev and available for Elena's use -- she simply did not use it. This is the single biggest structural gap.

2. **Fair-weather fund dynamics.** The Barroso VIX analysis proves the strategy earns ALL its returns during low-VIX environments (Sharpe +2.255) and LOSES catastrophically during high-VIX environments (Sharpe -1.305). The 27% of days spent in high-VIX regime produces -31% annualized returns. No risk management overlay is applied.

3. **Negative alpha vs equal-weight.** The signal-driven optimization destroys value compared to naive diversification. This calls into question whether the signal blend is adding any genuine alpha or merely introducing noise and turnover costs.

4. **Severe OOS decay.** The 2022-2024 OOS Sharpe (0.117) is only 17% of the IS Sharpe (0.700). While the Cederburg holdout with 2020-2024 OOS shows a more favorable 0.78 decay ratio, the most recent 3 years show the edge has largely evaporated.

5. **Excessive turnover.** 369% annual one-way turnover is 2.5x the 150% threshold. This indicates the optimizer is chasing short-lived signal variations rather than capturing persistent alpha. The turnover also means higher real-world costs than modeled.

6. **MinBTL exceeds data length.** At 16.4 years required vs 13.7 years available, the backtest is too short to statistically validate the observed Sharpe ratio. This is a newly revealed failure from the RF-adjusted Sharpe (lower observed Sharpe requires longer backtest).

#### What Is Still Sound

1. **Pre-committed signal weights** -- no in-sample optimization of the blend
2. **Expanding-window normalization** -- no look-ahead in signal construction
3. **Dynamic reoptimization** -- weights re-computed at each rebalance using only past data
4. **CompositeCostModel** -- realistic transaction cost structure
5. **PSR 98.5%** -- statistically significant even after RF adjustment
6. **Cederburg holdout decay ratio 0.78** -- multifactor blend partially mitigates OOS instability
7. **MTUM overlap 40%** -- differentiated from smart beta ETFs
8. **Parameter sensitivity 15.7%** -- robust to parameter perturbations

---

### FINAL VERDICT: CONDITIONAL

**I cannot approve this strategy in its current form.**

**Primary reasons for non-approval:**
1. Four gate failures (worst regime, max DD, turnover, MinBTL) -- up from 2 in R1
2. The primary CRITICAL requirement from Round 2 (vol targeting) was not implemented
3. The Barroso VIX analysis reveals the strategy is a pure fair-weather fund
4. Negative alpha vs equal-weight benchmark undermines the entire signal-driven thesis
5. Severe OOS decay (2022-2024 Sharpe 0.117)

**Why CONDITIONAL and not REJECT:**
1. The underlying signal construction is methodologically sound (pre-committed, no look-ahead)
2. The Cederburg holdout shows 0.78 decay ratio -- the edge has not fully disappeared
3. The `target_vol` mechanism exists in the framework and could fix the regime/DD failures
4. With vol targeting, the turnover would likely decrease (lower gross = fewer weight changes)
5. The IS Sharpe of 0.700 (RF-adjusted) is respectable for US large-cap equity
6. If vol targeting brings worst regime above -15% and max DD below -25%, this could become a viable low-conviction satellite allocation

**Specific requirements for re-entry:**

Elena may re-enter the review loop with a new notebook (`research_r3.ipynb`) ONLY if she addresses ALL of the following:

| # | Requirement | Concrete Target |
|---|-------------|-----------------|
| 1 | Use `target_vol=0.12` in `builder.backtest()` | Worst regime > -15%, max DD < -25% |
| 2 | Re-run the Barroso VIX analysis WITH vol targeting | High-VIX Sharpe must be > -0.5 (not -1.3) |
| 3 | Turnover must be below 150% | Either vol targeting reduces it, or use quarterly rebalance |
| 4 | Re-run Cederburg holdout WITH vol targeting | OOS Sharpe decay ratio > 0.5 |
| 5 | Benchmark comparison WITH vol targeting | Alpha vs equal-weight must be >= 0% |
| 6 | IS and OOS Sharpe WITH vol targeting | IS Sharpe > 0.5 (RF-adj), OOS Sharpe > 0 |
| 7 | MinBTL must be < available data | May require longer backtest window or higher Sharpe |

**If all 7 requirements are met, the strategy will be approved for paper trading at a maximum 10% allocation (reduced from the standard 20% maximum, given the fair-weather characteristics and OOS decay).**

**If Elena cannot bring all 11 gates into PASS status with vol targeting, I will issue a REJECT verdict. This is the final CONDITIONAL extension.**

---

### ALLOCATION POLICY (if eventually approved)

Given the documented weaknesses:
- **Max allocation: 10%** of portfolio (reduced from standard 20%)
- **Drawdown stop: -10%** strategy-level (tighter than standard -15%)
- **Paper trading: 6 months** minimum (extended from standard 3 months due to OOS decay concerns)
- **Regime monitoring: mandatory** -- if VIX exceeds 25 for 5 consecutive days, reduce allocation to 5%
- **Performance trigger: if paper trading Sharpe < 0.3 after 3 months, terminate**

---

*PM -- Zelin Investment Research | Round 3 FINAL Review | 2026-03-15*
*Verdict: CONDITIONAL (final extension) -- strategy needs vol targeting to pass remaining gates*

---
---

## [FINAL VERDICT — REJECT]

**Strategy:** Volatility-Scaled Momentum (Low-Turnover Core)
**Researcher:** Elena
**Folder:** `research/strategies/vol_scaled_momentum_2026-03-13_rejected/`
**Notebook:** `research_r2.ipynb` (contains R3 work with `target_vol=0.12`)
**Date:** 2026-03-15

---

### EXECUTIVE SUMMARY

After three rounds of review, the Vol-Scaled Momentum strategy has failed to meet our quantitative gates. The final submission applies `target_vol=0.12` as I required, but the results are unambiguous: **4 of 11 gates remain in failure, and the strategy has deteriorated across every round of corrections.** The vol-targeting mechanism, which was the last remaining path to approval, proved ineffective at addressing the structural weaknesses.

I stated in Round 3: *"If she cannot bring all 11 gates into PASS, I will issue REJECT."* Elena could not. The verdict is **REJECT**.

---

### WHY VOL TARGETING FAILED

The vol-targeting mechanism (`target_vol=0.12`) was supposed to reduce gross exposure during high-volatility periods, thereby reducing drawdowns and regime losses. Here is what actually happened:

1. **Max drawdown: UNCHANGED at -32.00%.** The vol-targeting mechanism uses a 60-day trailing realized vol to compute a scale factor. The COVID crash (March 2020) was a sudden vol spike -- by the time the trailing vol estimator detected the regime change, the drawdown had already occurred. Backward-looking vol targeting cannot protect against sudden shocks. This is a fundamental limitation of the Moreira & Muir mechanism when applied to equity long-only portfolios during crash events.

2. **Worst regime improved only marginally: -52.94% to -48.12%.** The trend_bear regime spans 798 days. Vol targeting reduced average gross exposure to 0.861 (only a 14% reduction from 1.0), which is insufficient to meaningfully change bear-market losses. The -48.12% remains 3.2x the -15% threshold.

3. **Sharpe DECREASED: 0.591 to 0.454 (full-period RF-adjusted).** Vol targeting reduced returns proportionally to exposure reduction, but did not reduce vol proportionally. The net effect was a lower Sharpe ratio. This is because the max_weight=0.12 constraint means the portfolio is already diversified across ~9 equal-weighted stocks, so reducing gross exposure just scales everything down without changing the risk profile.

4. **MinBTL WORSENED: 16.4 years to 26.4 years.** Lower Sharpe requires longer backtest to achieve statistical significance. The strategy now needs nearly twice the available data length to be significant.

5. **Turnover improved but still fails: 369% to 178%.** Closer to the 150% threshold but still over. Vol targeting helped by reducing the effective position sizes that change at each rebalance, but the optimizer still churns excessively.

### THE DEEPER STRUCTURAL PROBLEM

The R3 results confirm what was already visible in R2 but is now undeniable:

**The signal blend and mean-variance optimization do not add value.** The equal-weight benchmark (naive buy-and-hold of the same 28 stocks, monthly rebalanced) produces:
- Sharpe 0.801 vs strategy's 0.454
- Cumulative return 940% vs strategy's 375%
- Alpha: **-3.32% annualized** (strategy DESTROYS value)

This means Elena's entire signal construction pipeline -- the inverse-vol signal, the Sharpe-scaled momentum signal, the mean-reversion dampener, the expanding-window normalization, and the mean-variance optimizer -- collectively make the portfolio WORSE than doing nothing. The "alpha" is negative.

**Why does this happen?** The weight distribution analysis (Cell 15) reveals the answer: the max_weight=0.12 constraint binds for an average of 4 stocks per day. The optimizer consistently wants to concentrate into a few stocks but is constrained. The result is that on average 9 stocks are held at each rebalance, with 4-5 at the max weight of 12% and the rest filling in. This constraint-driven allocation:
- Generates high turnover (178% one-way) as the optimizer shuffles which stocks hit the 12% cap
- Produces a portfolio that is neither truly equal-weight (stable) nor truly concentrated (high-conviction alpha)
- Burns alpha through transaction costs on the high turnover

Risk aversion has zero effect on the portfolio (Sharpe range 0.452-0.454 across RA=1.8 to 4.2) because the optimizer is entirely constraint-driven, not alpha-driven. The mean-variance optimization is not performing its intended function.

### FAIR-WEATHER FUND DYNAMICS CONFIRMED

The Barroso VIX analysis from R2 (which remains unchanged with vol targeting, since vol targeting did not prevent the high-VIX losses) showed:
- High VIX (>20, 27% of days): Sharpe = -1.305, return = -31% annualized
- Low VIX (<=20, 73% of days): Sharpe = +2.255, return = +33% annualized

The strategy earns ALL its returns during calm, trending markets and gives back catastrophically during stressed markets. Vol targeting did not fix this because (a) VIX spikes faster than the 60-day trailing vol estimator can react, and (b) even when exposure is reduced, the remaining positions still lose money because the stock selection favors momentum names that crash hardest.

### FINAL GATE TABLE -- TRAJECTORY ACROSS 3 ROUNDS

| Gate | R1 | R2 | R3 (Final) | Threshold | Trend |
|------|-----|-----|-----|-----------|-------|
| Sharpe IS (RF-adj) | 0.885 (unadj) | 0.700 | **0.516** | > 0.5 | Declining -- barely passes |
| Deflated Sharpe | 1.0000 | 1.0000 | **1.0000** | > 0 | PASS (mechanically, N=1) |
| PSR | 99.9% | 98.5% | **95.3%** | > 80% | Declining |
| WF Hit Rate | 88.9% | 66.7% | **66.7%** | > 55% | Declined after rolling cov |
| Survives 2x Costs | 0.740 | 0.449 | **0.297** | > 0 | Declining -- marginal |
| 3x Cost Sensitivity | 0.595 | 0.307 | **0.142** | > 0 | Declining -- barely passes |
| Worst Regime Loss | -52.69% | -52.94% | **-48.12%** | > -15% | FAIL -- 3.2x threshold |
| Strategy Half-Life | 11.7 yrs | 2935.6 yrs | **No decay** | > 2 yrs | PASS (metric unreliable) |
| MinBTL | 11.8 yrs | 16.4 yrs | **26.4 yrs** | < 13.7 yrs | WORSENING |
| Max Drawdown | -32.00% | -32.00% | **-32.00%** | < 25% | FAIL -- unchanged |
| Annual Turnover | 283% (wrong) | 369% | **178%** | < 150% | Improving but still FAIL |

**Final score: 7 PASS, 4 FAIL**

Every passing gate has DECLINED across rounds. The corrections (RF adjustment, rolling-window cov, proper turnover, vol targeting) all revealed the strategy was weaker than initially appeared. This is not a strategy that improves under scrutiny -- it degrades.

---

### DECISION: REJECT

**The Vol-Scaled Momentum strategy is REJECTED.**

**Grounds:**
1. **4 gate failures after 3 rounds** -- worst regime, max DD, turnover, and MinBTL all fail
2. **Vol targeting (the last remediation path) proved ineffective** -- max DD unchanged, worst regime improved only 9%, Sharpe decreased
3. **Negative alpha vs equal-weight benchmark** (-3.32%) -- the signal-driven approach destroys value
4. **Fair-weather fund dynamics** -- all returns from low-VIX calm markets, catastrophic losses in stressed markets
5. **Severe OOS decay** -- IS Sharpe 0.516, OOS Sharpe 0.180 (ratio = 0.35)
6. **MinBTL exceeds available data by 93%** (26.4 years needed vs 13.7 available)
7. **Every passing gate declined across rounds** -- the strategy gets worse under rigorous scrutiny

**What I credit Elena for:**
- Methodologically sound signal construction (pre-committed weights, expanding-window normalization)
- Thorough response to challenges (Cederburg holdout, Barroso VIX analysis, MTUM overlap, benchmark comparison, weight distribution analysis)
- Honest self-assessment acknowledging the structural limitations
- Clean, well-structured notebook following the template

The problem is not the methodology -- it is the underlying signal combination. Inverse-vol + risk-adjusted momentum + mean-reversion dampener, applied to a 28-stock US large-cap universe with bi-monthly rebalancing and mean-variance optimization constrained to 12% max weight, does not produce enough alpha to survive realistic costs, bear markets, and statistical scrutiny.

---

### LESSONS FOR FUTURE STRATEGIES

1. **Vol targeting does not fix crash risk for equity long-only.** The Moreira & Muir mechanism works best for long-short factor portfolios where exposure can be reduced to near zero. For a long-only equity portfolio with binding weight constraints, vol targeting merely scales down an already-diversified portfolio by 10-15%, which is insufficient.

2. **Equal-weight is a demanding benchmark for 28-stock US large-cap.** Any signal-driven strategy must BEAT naive diversification. If the signals and optimizer cannot outperform 1/N allocation, they are not adding value. Future strategies should be benchmarked against equal-weight from the start.

3. **Mean-variance optimization with binding max_weight constraints is effectively equal-weight with noise.** When 4 of 9 held stocks are at the 12% cap, the optimizer has very little room to express alpha views. The result is high turnover from shuffling which stocks hit the cap, with minimal return benefit. Future strategies should either use unconstrained optimization (allowing higher concentration) or abandon MVO in favor of simpler signal-ranked allocation.

4. **IS/OOS splits reveal more than walk-forward.** The walk-forward hit rate (66.7%) looks acceptable, but the simple IS/OOS split (Sharpe 0.516 vs 0.180) reveals severe decay. Both tests should be reported.

5. **Start with benchmark comparison.** If the alpha vs equal-weight is negative in R1, stop immediately. Do not iterate a strategy that cannot beat naive diversification.

---

### POST-REJECTION ACTIONS

1. **Rename strategy folder** to `vol_scaled_momentum_2026-03-13_rejected`
2. **Archive** -- retain all notebooks and reviews for future reference
3. **Priority reallocation** -- FX Carry + Momentum (P2) moves to Priority 1 after data pipeline gaps are closed
4. **Lessons learned** should inform Elena's approach to Cross-Sectional Momentum (P3) -- specifically: benchmark against equal-weight early, use simpler ranking-based allocation instead of MVO, and test crash-protection mechanisms from the start

---

*PM -- Zelin Investment Research | FINAL VERDICT | 2026-03-15*
*Strategy: Vol-Scaled Momentum (Low-Turnover Core)*
*Verdict: **REJECT***
*Grounds: 4/11 gate failures after 3 rounds, negative alpha vs benchmark, vol targeting ineffective*
