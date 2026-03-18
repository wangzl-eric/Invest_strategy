# PM Review — VIX Regime (VRP + Term Structure)

**Strategy:** VRP + Term Structure Slope as equity exposure scalar
**Researcher:** Elena (equity notebook), Marco (macro concerns)
**Reviewer:** PM
**Date:** 2026-03-15
**Verdict:** REJECT

---

## Round 1 — Pre-Review (Headline Numbers)

Elena submitted R1 with daily rebalancing. Key findings:

- IS Sharpe 0.175 vs B&H 0.385 — underperforms by more than half
- Max DD -34.4% vs B&H -51.6% — drawdown protection works but still fails -15% gate
- Annual turnover 2430% — catastrophic design error (daily regime switching)
- Cost drag 30.56% at 10bps — strategy-killing
- Beat-B&H rate 7.1% (1/14 folds) — nearly always worse than doing nothing

**Round 1 disposition:** Daily rebalancing is a design error, not a signal failure.
Weekly resampling approved as R2 fix (not a post-hoc hack — regimes don't change daily).

---

## Round 2 — Full Gate Assessment (Weekly Resampling Applied)

### What Weekly Resampling Fixed
- WF hit rate: 57.1% → 85.7% (dramatic improvement)
- 2x cost survival: now PASS (Sharpe 0.222)
- Turnover: 2430% → 916% (still high but survivable)

### Quantitative Gate Table

| # | Gate | Threshold | Result | Status |
|---|------|-----------|--------|--------|
| 1 | Top VRP quintile return | ≥ 0.5% | +1.65% | PASS |
| 2 | Quintile monotonicity | monotonic | yes | PASS |
| 3 | Regression t-stat | ≥ 1.5 | 1.33 | **FAIL** |
| 4 | WF OOS hit rate | > 55% | 85.7% | PASS |
| 5 | WF avg OOS Sharpe | > 0 | 0.462 | PASS |
| 6 | PSR | > 80% | 85.4% | PASS |
| 7 | Deflated Sharpe | > 0 | 0.017 | PASS (barely) |
| 8 | MinBTL < available history | < 12.6yr | 3,968yr | **CRITICAL FAIL** |
| 9 | Spanning alpha t-stat | significant | -0.18 | **FAIL** |
| 10 | Crisis interaction t-stat | significant | -3.77 | PASS |
| 11 | 2x cost Sharpe | > 0 | 0.222 | PASS |
| 12 | Parameter robustness | > 80% stable | 71.3% | FLAG |

**Score: 8 PASS, 3 FAIL, 1 FLAG**

### Three Structural Failures (No Path to Fix)

**MinBTL = 3,968 years (need 12.6 available)**
Off by a factor of 315x. Bootstrap CI spans zero [-0.167, 0.824]. Analytical CI barely
positive [-0.022, 0.467]. The strategy's Sharpe ratio is statistically indistinguishable
from random chance. Even 100 years of data would be insufficient. No parameter tweak
or resampling frequency can fix this — it's a property of the signal's low information ratio.

**Spanning alpha t = -0.18**
After controlling for SPY returns and momentum, VRP contributes zero independent alpha.
Negative point estimate. The strategy adds no information beyond being long equities with
a momentum tilt. This is fatal for standalone viability.

**Regression t = 1.33 (threshold 1.5)**
The linear relationship between VRP and forward returns is not statistically significant.
Note: Q5 quintile t = 9.45 shows the signal IS informative at extremes (non-linear), but
this extreme-only power doesn't translate into a tradeable edge at portfolio level.

### Cell 13 — Head-to-Head Comparison (VRP Loses to Simpler Signals)

| Signal | Sharpe | MaxDD | Turnover |
|--------|--------|-------|----------|
| VRP (ours) | 0.299 | -32.2% | 916%/yr |
| VIX Level | 0.326 | -18.5% | 551%/yr |
| Trailing Vol | 0.341 | -20.0% | 187%/yr |
| SPY B&H | 0.385 | -51.6% | 0% |

VRP is dominated on every metric. A simple trailing vol signal achieves:
- Higher Sharpe (0.341 vs 0.299)
- Better drawdown protection (-20.0% vs -32.2%)
- 5x less turnover (187% vs 916%)

This is the most damning comparison in the notebook. There is no dimension on which
the more complex VRP + term structure signal outperforms a 21-day trailing vol filter
that requires no options data, no term structure calculation, and no VIX subscription.

### Cell 15 — Overlay Test (Decisive — FAILS PM Condition)

The overlay test was the last path to survival. PM required:
- Sharpe improvement of at least +0.15 when overlaid on momentum
- Statistically significant improvement (p < 0.10)

Actual results:

| Strategy | IS Sharpe | OOS Sharpe | IS MaxDD | OOS MaxDD |
|----------|-----------|------------|----------|-----------|
| Momentum only | 0.271 | 0.503 | -34.1% | -25.4% |
| Momentum + VRP overlay | 0.186 | 0.206 | -17.1% | -13.8% |

- **IS Sharpe delta: -0.084** (overlay HURTS performance)
- **OOS Sharpe delta: -0.297** (overlay DESTROYS OOS performance)
- **NW t-stat of differential: -1.16 IS, -1.54 OOS** (not significant, wrong direction)
- **Drawdown improvement: +17pp IS, +11.6pp OOS** (meaningful but insufficient)

The overlay reduces drawdown but at catastrophic cost to returns. The OOS Sharpe drops
from 0.503 to 0.206 — a 59% destruction of risk-adjusted returns. The drawdown
improvement is real (+11.6pp OOS) but the price is unacceptable.

---

## Verdict: REJECT

### Rejection Rationale

1. **No statistical significance.** MinBTL of 3,968 years means we cannot distinguish
   this strategy from random chance. This alone is disqualifying.

2. **No independent alpha.** Spanning regression alpha t = -0.18. After controlling for
   market beta and momentum, VRP adds nothing.

3. **Dominated by simpler alternatives.** Trailing vol (21-day) beats VRP on Sharpe,
   drawdown, and turnover simultaneously. The added complexity of VRP computation,
   VIX options data dependency, and term structure modeling generates negative value.

4. **Overlay destroys performance.** The final overlay test — the last viable path —
   showed VRP overlay REDUCES Sharpe by 0.297 OOS while improving drawdown by 11.6pp.
   This is expensive insurance, not alpha.

5. **Crowding risk unaddressed.** VRP is a widely published signal. Feb 2018 (XIV blow-up)
   and Mar 2020 (vol unwind) are documented failure modes. No evidence of differentiation
   from the standard implementation.

### What Was Genuinely Good

- Crisis interaction t = -3.77 — the signal DOES detect vol events
- Q5 quintile return +1.65% — extremes are informative
- Walk-forward hit rate 85.7% after weekly fix — signal direction is correct
- Elena's 5 kill gates are excellent research discipline
- The R1→R2 weekly resampling fix was correct and well-executed

### Lessons for the Team

1. **Check head-to-head vs simple baselines in R1.** If trailing vol dominates, stop early.
   This would have saved an entire research round.

2. **VRP is a crisis signal, not an alpha signal.** The Q5 quintile power and crisis
   interaction t-stat are real, but they don't survive translation to a tradeable strategy.
   Academic significance ≠ economic significance.

3. **Drawdown reduction ≠ alpha.** Reducing drawdown by cutting exposure is always possible
   (cash does it perfectly). The question is whether the TIMING of exposure reduction adds
   value vs simpler approaches. Here, it doesn't — trailing vol does it better.

4. **MinBTL is the ultimate filter.** When MinBTL exceeds available data by 300x, no amount
   of parameter tuning can save the strategy. Check MinBTL early in the research process.

### For Future Reference

The VRP crisis detection capability (t = -3.77) could be useful as a risk management
input — not as a signal, but as an alert trigger. If we build a risk monitoring dashboard,
VRP percentile could be one input to a multi-signal "reduce gross exposure" rule. But
that is a risk management project, not a strategy.

---

**PM signature:** Reviewed and rejected after 2 rounds. No Round 3 warranted —
failures are structural, not addressable with additional analysis.

*Reviewed: 2026-03-15*
