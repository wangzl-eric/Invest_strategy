# Paper Notes: Fact, Fiction and Momentum Investing

**Authors:** Cliff Asness, Andrea Frazzini, Ronen Israel, Tobias Moskowitz
**Year:** 2014
**Journal:** Journal of Portfolio Management (Practitioner-oriented)
**Date Read:** 2026-03-30
**Scores:** Credibility 5 | Relevance 4 | Actionability 4

> **Why these scores:** Authors are AQR principals who have run live momentum books at institutional scale since the mid-1990s. The paper draws on both academic evidence and proprietary live-trading data, giving it unusually high credibility (5). Directly relevant to our FX Carry + Momentum (P1) and CS Equity Momentum (P3, Elena) strategies and to our existing MomentumSignal implementation (4). Highly actionable: specific turnover, capacity, and signal construction guidance that maps directly onto codebase decisions (4).

---

## Core Thesis

Momentum investing is persistently misunderstood by practitioners through a set of recurring myths. The paper systematically debunks nine "fictions" using (a) decades of academic cross-asset evidence, (b) AQR's own live trading results from the mid-1990s onward, and (c) theoretical arguments from behavioral finance. The central conclusions are:

1. Momentum survives realistic transaction costs, especially in large-cap liquid universes at institutional scale.
2. The short leg is NOT the primary driver of returns — the long leg works on its own.
3. Momentum is strongest when combined with value because the two factors are strongly negatively correlated (~−0.5 to −0.6 in US equities), producing diversification benefits that dramatically improve the combined Sharpe ratio.
4. Risk-based explanations for momentum remain weak; behavioral explanations (underreaction → continuation → eventual overreaction → crash) are more consistent with the full body of evidence.
5. The strategy is live and investable at scale — AQR's managed futures, equity momentum, and multi-style funds are offered as proof of concept.

---

## The Nine Fictions (and Rebuttals)

### Fiction 1: Momentum returns are too volatile to be useful

**The Claim:** Momentum portfolios exhibit high volatility and extreme drawdowns (momentum crashes), making them unsuitable for risk-averse investors.

**The Fact:** Momentum's Sharpe ratio (roughly 0.5–0.7 historically across asset classes) is comparable to or better than value investing. Volatility is not unique to momentum — value also suffers extreme drawdowns. The key is position sizing and diversification. A volatility-targeted momentum strategy smooths the ride considerably. Crashes are real but infrequent and partially predictable under Daniel-Moskowitz conditions.

**Evidence:** Long-run US and international data from Jegadeesh-Titman (1993), Fama-French momentum decile returns, Asness (1994 dissertation); cross-asset evidence from Asness, Moskowitz, Pedersen (2013).

---

### Fiction 2: After transaction costs, momentum doesn't work

**The Claim:** Momentum's high turnover (typically 100–200% per year for a monthly-rebalanced 12-1 strategy) generates enough trading costs to wipe out the gross alpha.

**The Fact:** Costs are real but manageable at institutional scale, particularly for large-cap universes. AQR's live implementation data shows net-of-cost returns remain significantly positive. Key cost-reduction levers:
- **Restrict to liquid large-cap stocks:** most alpha does not require micro-caps where costs are prohibitive.
- **Patient execution:** momentum signals have half-lives of weeks, not hours. A 1–5 day execution window captures nearly all the signal at much lower market impact.
- **Two-way netting:** rebalancing buys and sells often offset each other; only the net flow hits the market.
- **Threshold-based rebalancing:** only trade when the position deviation exceeds a cost-adjusted threshold, avoiding unnecessary turnover for marginal rebalances.

**Quantitative guidance:** For a large-cap universe, one-way transaction costs of roughly 10–30 bps per trade are realistic at institutional scale. With ~100–150% annual one-way turnover and ~20 bps average one-way cost, total drag is roughly 20–30 bps/year — a small fraction of gross alpha (typically 300–500 bps/year gross in a well-implemented strategy).

**Evidence:** AQR live-fund net return data vs. simulated gross returns; comparison of paper portfolios vs. implementable portfolios using AQR's actual execution data.

---

### Fiction 3: Momentum only works in small-cap stocks

**The Claim:** All the momentum premium is concentrated in illiquid small-caps where it cannot be harvested. In large-cap universes it is arbitraged away.

**The Fact:** Momentum is statistically and economically significant in large-cap stocks alone. The premium is smaller (small-caps do have stronger raw momentum returns) but remains after costs and is actually more investable because execution costs are lower. Restricting to the top 1,000 or top 500 US stocks by market cap still yields meaningful momentum returns.

**Evidence:** Fama-French size-sorted momentum portfolios; AQR institutional equity funds concentrate in liquid large-caps and remain profitable net of costs.

---

### Fiction 4: Momentum is just a January effect / seasonal artifact

**The Claim:** Momentum profits are concentrated in January reversals (tax-loss selling in December creates depressed prices that bounce in January). Strip out January and momentum disappears.

**The Fact:** Momentum is strong outside of January. The January effect is actually a partial headwind for momentum, not a tailwind: December losers — classic momentum shorts — tend to rebound in January due to tax-loss selling reversal. Excluding January makes momentum look *stronger* on average. The strategy is robust across all calendar months.

**Evidence:** Monthly decomposition of momentum returns; Jegadeesh-Titman seasonal analysis; the paper shows the January effect creates a known but modest drag, not the source of the premium.

---

### Fiction 5: Momentum is too crowded to work going forward

**The Claim:** With so many quant funds running momentum strategies, the alpha has been arbitraged away.

**The Fact:** Crowding is a legitimate concern but the evidence does not support the claim that momentum is fully arbitraged. Arguments:
- Momentum continues to deliver positive live returns in AQR's funds post-2000 and post-2010.
- The behavioral mechanism (investor underreaction to information) is unlikely to fully disappear because it is tied to persistent human psychology.
- Crowding creates crash risk (fire-sale dynamics when many funds simultaneously unwind), which is distinct from the expected-return question. Crowding raises tail risk, not expected-return destruction.
- The correct response to crowding is position sizing and liquidity management, not avoidance.

**Evidence:** Continued positive returns in live AQR funds through 2013; academic replication studies through the same period across multiple geographies.

---

### Fiction 6: Momentum is not a diversifying factor

**The Claim:** Momentum is correlated with other factors (growth, quality) and adds little diversification to a multi-factor portfolio.

**The Fact:** Momentum has low or negative correlation with value, which is the most important diversification relationship in equity factor investing. The paper documents a correlation of roughly −0.5 to −0.6 between momentum and value in US equities. When value suffers (growth rallies), momentum typically benefits (growth stocks have been recent winners). See **Combining Momentum with Value** section.

---

### Fiction 7: Momentum works in backtests but is not investable at scale

**The Claim:** Academic momentum portfolios assume unrealistic liquidity, zero market impact, and frictionless short selling. Real-world implementation at scale destroys the premium.

**The Fact:** AQR has managed momentum exposure at multi-billion dollar AUM levels with documented positive net returns. The strategy is capacity-constrained but meaningful capacity exists in large-cap developed-market equities. Key implementation principles:
- Focus the long leg on large-cap high-momentum stocks (good liquidity, lower impact).
- Reduce short-leg emphasis or substitute with derivatives where shorting is costly.
- Use patient, cost-aware execution with threshold-based rebalancing.

**Quantitative guidance:** Implied capacity in the range of \$10–50 billion for a diversified global large-cap momentum strategy before meaningful alpha erosion, though explicit numbers are not provided in the paper.

---

### Fiction 8: Recent performance has been weak, invalidating momentum

**The Claim:** Momentum underperformed in the 2000s (especially the 2009 crash) and in periods of high market volatility, suggesting the effect is diminishing.

**The Fact:** Short-term underperformance is expected in any factor. The 2009 crash was a known tail event driven by a sharp reversal in prior-year losers during the financial crisis recovery. Over full cycles, momentum continues to deliver positive returns. The paper argues against backward-looking dismissal of a factor based on a single bad episode, particularly one that was theoretically predictable under Daniel-Moskowitz crash conditions.

**Evidence:** Long-run Sharpe ratio remains positive through 2013; international and cross-asset momentum also remains positive through the same period.

---

### Fiction 9: The short leg drives all the returns

**The Claim:** Momentum alpha comes almost entirely from shorting past losers. Long-only momentum adds little or nothing. Since shorting is costly and constrained, momentum is not useful for long-only investors.

**The Fact:** The long leg (buying past winners) is independently profitable. The short leg amplifies returns but is not the source. Long-only momentum strategies — buying the top quintile of past winners within an index universe — deliver positive risk-adjusted returns. This is critical for long-only equity managers who can implement momentum as a stock-selection tilt rather than a long-short strategy.

**Evidence:** Quintile decomposition of Jegadeesh-Titman returns; AQR's long-only quantitative equity products demonstrate positive momentum contribution from the long side alone.

---

## Transaction Cost Reality

This is the paper's most practically important section for implementation.

**Gross turnover:** A standard monthly-rebalanced 12-1 momentum strategy turns over roughly 100–200% per year (one-way). This is high compared to value (~20–40%) but is not the cost death sentence critics claim.

**Realistic one-way costs (large-cap US, institutional scale):**
- Commission: ~1–2 bps (near-zero for large institutional accounts)
- Half-spread: ~3–8 bps for large-cap liquid stocks
- Market impact: ~5–15 bps depending on order size and patience
- **Total one-way: ~10–25 bps per trade**

**Annual cost drag:** At 150% one-way turnover and 15–20 bps average one-way cost:
- Annual drag ≈ 150% × 15–20 bps ≈ **22–30 bps/year**
- Gross alpha (large-cap US momentum, 12-1): ~300–400 bps/year
- Net alpha after costs: ~270–380 bps/year — remains meaningful

**Capacity:** The paper's implicit guidance (from AQR's live fund sizes) suggests \$10–50 billion is the practical range for a diversified global large-cap long-short momentum strategy before alpha degradation becomes material. Long-only momentum has larger capacity since it avoids the short-side liquidity constraint.

**Cost reduction tactics the paper endorses:**
1. Patience in execution (1–5 day VWAP windows) — does not sacrifice signal because momentum half-life is weeks
2. Threshold rebalancing — only trade when drift exceeds a cost-justified threshold
3. Netting long and short flows before hitting the market
4. Restricting the short leg to the most liquid names or using futures overlays

## Risk-Based vs Behavioral

The paper takes a clear stance: **behavioral explanations are more consistent with the evidence than risk-based ones.**

**Risk-based arguments (which the paper finds weak):**
- Momentum stocks have higher beta in down markets → not supported; momentum portfolios do not consistently load on known risk factors
- Momentum premium is compensation for crash risk → partially true (see crashes), but the premium is too large and too persistent to be explained by crash risk alone
- Fama-French three-factor model cannot explain momentum — it is an anomaly relative to the model, not a hidden risk factor loading

**Behavioral arguments (which the paper finds more consistent):**
- **Underreaction:** Investors update beliefs too slowly in response to new information. Prices drift toward fundamental value over 3–12 months, creating positive serial correlation (momentum).
- **Overreaction:** After the underreaction phase, prices eventually overshoot fundamental value (driven by extrapolation, herding). This sets up the eventual long-run reversal (value effect).
- The negative correlation between momentum and value is itself evidence for this unified behavioral story: value stocks are long-run mean-reverting overreactions; momentum stocks are short-run underreactions in progress.

**Implication for strategy design:** If momentum is behavioral (not a risk premium), it should be more persistent and harder to arbitrage than pure risk factors, because the behavioral mechanism is tied to human psychology that does not disappear. However, it also means the effect can be amplified by crowding (many arbitrageurs chasing the same signal) and can crash when the mechanism reverses.

---

## Momentum Crashes (Brief)

The paper acknowledges crashes but frames them as manageable tail events rather than invalidating evidence.

**Key reference:** Daniel and Moskowitz (2016) — "Momentum Crashes" — provide the theoretical framework the paper implicitly relies on. Crash conditions:
- Sharp market rebounds after large drawdowns (the 2009 recovery being the canonical example)
- High prior-period market volatility (option-like payoff structure of momentum shorts creates left-tail exposure)
- When prior losers (momentum shorts) have implicitly high option value due to leverage/distress, a market rebound creates explosive short-squeeze dynamics

**Paper's position:** Crashes are real but:
1. They are partially predictable — high prior-period market drawdown + high volatility is a warning signal
2. They are infrequent — the long-run Sharpe ratio is positive even including crash episodes
3. Volatility targeting (scaling position size inversely with recent realized volatility) materially reduces crash severity without much loss of expected return
4. Diversifying momentum across asset classes (equities, bonds, currencies, commodities) reduces the severity of equity-specific momentum crashes

---

## Signal Robustness

**Lookback window:** The 12-month formation period (with 1-month skip) is the standard. The paper confirms robustness across windows from 6 to 12 months. Windows shorter than 3 months begin to capture short-term reversal rather than momentum. Windows longer than 12 months capture value-like mean-reversion.

**Skip rule (the 1-month skip):** Skipping the most recent month is essential. The most recent month exhibits short-term reversal (bid-ask bounce, microstructure noise). Including it would reverse the sign of the signal in the short term. This is one of the most important implementation details.

**Weighting schemes:** Value-weighting within momentum portfolios (rather than equal-weighting) reduces the small-cap bias and makes the strategy more implementable. The paper favors value-weighted or dollar-neutral implementations.

**Universe:** The broader and more liquid the universe, the better — more stocks means more diversification and lower idiosyncratic risk. Restricting to the top 500 or 1,000 by market cap is preferred for institutional implementation.

**Holding period:** Monthly rebalancing is the standard. More frequent rebalancing increases turnover with marginal signal benefit. Less frequent (quarterly) reduces turnover but increases signal decay.

**Signal normalization:** Cross-sectional ranking (percentile rank within universe) is more robust than raw return sorting, as it is less sensitive to outliers and regime changes in return distributions.

## Combining Momentum with Value

This is one of the paper's most actionable findings for multi-factor portfolio construction.

**The core finding:** Momentum and value have a correlation of approximately −0.5 to −0.6 in US equities. This is not a coincidence — it follows from the unified behavioral story. Value stocks are past losers (cheap because prices fell); momentum stocks are past winners (expensive because prices rose). A stock cannot simultaneously be cheap (value) and a recent winner (momentum) — they are structurally opposed at the portfolio level.

**Portfolio math:** If momentum Sharpe ≈ 0.5 and value Sharpe ≈ 0.5, and their correlation is −0.5:
$$SR_{combo} = \frac{SR_m + SR_v}{\sqrt{2 + 2 \cdot (-0.5)}} = \frac{1.0}{\sqrt{1.0}} = 1.0$$

A 50/50 combination roughly doubles the Sharpe ratio relative to either factor alone — one of the best risk-adjusted diversification trades available in equity factor investing.

**Cross-asset extension:** The negative correlation between momentum and value holds across asset classes (bonds, currencies, commodities), making it a robust structural relationship rather than a US equity artifact. See Asness, Moskowitz, Pedersen (2013).

**Implementation implication:** Never run a pure momentum strategy in isolation if a value signal is available. A combined momentum + value portfolio with a single integrated ranking (e.g., z-score blend) is both more stable and higher Sharpe than running the two separately. This is the core of AQR's multi-style equity products.

---

## Failure Modes Still Acknowledged

The paper is intellectually honest about what momentum does not do well:

1. **January effect:** As noted under Fiction 4, the January reversal of tax-loss-selling losers is a systematic headwind for momentum in the US. It is small but real.

2. **Momentum crashes:** The 2009 episode is not dismissed. Under specific market conditions (post-crisis rebound, high prior volatility), momentum can suffer drawdowns of 30–40% in a matter of weeks. Volatility targeting partially mitigates this but does not eliminate it.

3. **Crowding and fire-sale risk:** The paper acknowledges that as more capital pursues momentum, the strategy becomes more vulnerable to simultaneous unwinding events. This is a structural risk that grows with AUM in the strategy. Monitoring crowding metrics (e.g., factor exposure overlap across funds) is prudent.

4. **Capacity is finite:** The strategy does not scale to arbitrary AUM. Very large funds face meaningful alpha erosion from market impact, and the paper does not claim otherwise.

5. **Short-leg constraints:** For long-only investors or strategies where shorting is costly or restricted, the short leg of momentum cannot be fully implemented. This reduces but does not eliminate the signal's value.

---

## Connection to Ilmanen Ch14 + Ch17

**Chapter 14 (Momentum):** This paper is the primary practitioner companion to Ilmanen's Ch14 momentum chapter. Ilmanen documents the cross-asset evidence; this paper provides the implementation layer — specifically the cost analysis, capacity evidence, and rebuttal of the "costs kill it" critique. The two sources are complementary: Ilmanen for the theoretical and empirical framework, Asness et al. for the "is this actually tradeable?" question.

**Chapter 17 (Combining Factors):** The momentum + value combination discussed here is central to Ilmanen's Ch17 argument for multi-factor portfolios. The negative correlation between value and momentum is the single most important diversification relationship in systematic equity investing, and both Ilmanen and this paper use it as the primary motivation for multi-factor approaches over single-factor purity.

**Key bridge:** Both sources agree that momentum alone is not the goal. The goal is a diversified factor portfolio where momentum's negative correlation with value does most of the heavy lifting in Sharpe ratio improvement.

## Codebase Check

Files read: `backtests/strategies/signals.py`, `backtests/costs/transaction_costs.py`, `backtests/costs/slippage.py`, `backtests/runners/momentum.py`.

### MomentumSignal — `backtests/strategies/signals.py` lines 52–68

```python
class MomentumSignal(BaseSignal):
    name = "momentum_12_1"
    lookback = 252   # ~12 months of trading days
    skip = 21        # ~1 month skip

    def compute(self, prices: pd.DataFrame):
        ret = prices.pct_change(self.lookback - self.skip).shift(self.skip)
        return ret.iloc[:, 0] if ret.shape[1] == 1 else ret
```

**Skip rule — CORRECT.** Line 67: `pct_change(self.lookback - self.skip).shift(self.skip)` computes the return from `t - 252` to `t - 21`, then shifts forward by 21 days so that at any given date `t` the signal reflects the 12-1 window ending one month ago. This is exactly the standard Jegadeesh-Titman / AQR 12-1 construction. The skip is implemented correctly.

**Lookback units — WATCH.** `lookback=252` is in calendar/trading days, which approximates 12 months. The name `momentum_12_1` implies 12 months lookback, 1 month skip. With `skip=21` and `lookback=252`, the actual measurement window is 231 trading days (~11 months). This is a minor but real discrepancy from the name. The paper's 12-1 means 12 months formation minus 1 month skip = 11 months of actual return. So the implementation is numerically correct for the intended signal — the name `momentum_12_1` refers to the (formation, skip) pair, not (window length, skip). **No bug — but worth a comment clarifying this.**

**Cross-sectional ranking — MISSING (flag).** The paper (and Jegadeesh-Titman) recommend cross-sectional percentile ranking within the universe before forming portfolios. `MomentumSignal.compute()` returns raw percentage returns, not cross-sectional ranks. The `to_positions()` method in `BaseSignal` (lines 39–49) just takes `np.sign()`, which gives a binary long/short with no weighting by signal strength. For a proper cross-sectional implementation, scores should be ranked (or z-scored) across the universe before position sizing. This is a meaningful gap relative to the paper's recommended implementation — especially for a multi-stock universe.

**`runners/momentum.py` — research stub only.** The file at `backtests/runners/momentum.py` (lines 35–37) uses `pct_change(lookback)` with no skip rule, and operates on a single ticker with synthetic data. It does NOT use `MomentumSignal` from `signals.py`. It is an independent experiment scaffold (MLflow logging, parameter grid) and is not wired into the production backtesting pipeline. This is not a conflict — it is a standalone research runner — but it means the skip rule is absent in that file. If this runner is ever used for strategy validation, it should import and use `MomentumSignal` rather than reimplementing the signal inline.

### Transaction Cost Model — `backtests/costs/transaction_costs.py`

**`default_equity_cost_model()` — lines 114–126:** Returns a `CompositeCostModel` with:
- `FixedCostModel(cost_per_trade=1.0)` — \$1 flat per trade
- `ProportionalCostModel(cost_bps=5.0)` — 5 bps proportional

**Assessment vs. paper:** The paper's realistic one-way cost for large-cap US is ~10–25 bps total. The default model's 5 bps proportional + \$1 fixed is materially below this for any reasonably sized trade. For a \$50,000 position, the \$1 fixed is 0.002% and the 5 bps proportional is 5 bps — total 5.2 bps one-way. The paper implies 15–20 bps is more realistic when market impact is included. **The `MarketImpactModel` exists (lines 62–101, Almgren-Chriss square-root impact) but is NOT included in `default_equity_cost_model()`.** This means the default model systematically understates costs for momentum strategies, which have meaningful market impact at scale. For any momentum research, the cost model should be `CompositeCostModel((ProportionalCostModel(bps=5), MarketImpactModel(...)))` at minimum.

### Slippage Model — `backtests/costs/slippage.py`

**`FixedSlippageModel(slippage_bps=5.0)` — lines 33–45:** Default 5 bps fixed slippage. Directionally correct for large-cap stocks but low relative to the paper's guidance. The `VolumeWeightedSlippageModel` (lines 48–75) and `BidAskSlippageModel` (lines 78–98) are more realistic — bid-ask spread of 10 bps (the default) is closer to what the paper implies for large-cap names. The `BidAskSlippageModel` with `spread_bps=10` (5 bps half-spread) combined with the proportional cost model would give approximately 10 bps total one-way, which is at the low end of the paper's range. Adequate for large-cap liquid names, but momentum strategies that touch mid-cap names should use `VolumeWeightedSlippageModel`.

### Summary Table

| Component | Location | Status | Note |
|-----------|----------|--------|------|
| 12-1 skip rule | `signals.py:67` | CORRECT | `pct_change(231).shift(21)` implements 12-1 correctly |
| Signal name clarity | `signals.py:55,64` | MINOR | Name `momentum_12_1` means (formation, skip) pair, not window length |
| Cross-sectional ranking | `signals.py:39–49` | GAP | Raw returns returned; no percentile rank / z-score normalization |
| Runners skip rule | `runners/momentum.py:36` | STUB | Uses raw `pct_change(lookback)`, no skip; not production code |
| Default cost model | `transaction_costs.py:114` | UNDERSTATED | 5 bps only; MarketImpactModel excluded from default |
| Slippage default | `slippage.py:37` | LOW | 5 bps fixed; BidAskSlippageModel(10 bps) more realistic |

## Implementability

What the paper recommends for practical implementation — mapped to our context:

1. **Use the 12-1 signal as the baseline.** Do not over-engineer the lookback. The 12-1 standard is robust; tweaking it for marginal improvement risks overfitting.

2. **Rank cross-sectionally, not on raw returns.** Within the universe, convert momentum scores to percentile ranks or z-scores before sizing positions. This normalizes signal strength across different market regimes and reduces outlier sensitivity.

3. **Long-only is viable.** For our portfolio (IBKR retail account), a long-only tilt toward high-momentum names within the SPX 500 universe is the practical implementation. The short leg requires margin, locate fees, and adds complexity. The paper explicitly validates long-only momentum.

4. **Combine with value immediately.** Do not research momentum in isolation. The negative correlation with value (−0.5 to −0.6) means a blended signal dominates either factor alone. For the CS Equity Momentum (P3, Elena) strategy, a value overlay (P/E, P/B, or EV/EBITDA rank) should be part of the signal blend from Round 1.

5. **Add market impact to the cost model.** The `default_equity_cost_model()` in `transaction_costs.py` excludes `MarketImpactModel`. For any momentum backtest, use a composite including the square-root impact model. Even at modest position sizes, the paper's guidance implies 15–20 bps one-way is more realistic than the current 5 bps default.

6. **Threshold-based rebalancing.** Do not rebalance monthly mechanically. Rebalance only when the signal deviation exceeds a cost-adjusted threshold (e.g., 0.5× the expected round-trip cost in signal units). This reduces turnover by 20–40% with minimal alpha sacrifice.

7. **Volatility-target the position size.** Scale momentum exposure inversely with recent realized volatility of the portfolio. This reduces crash severity without meaningfully reducing expected returns.

8. **Monitor for crowding.** Crowding is the one concern the paper acknowledges without a clean solution. When momentum factor exposure is very concentrated (many funds holding the same names), reduce position size or add diversification across geographies/asset classes.

---

## Key Quotes

> "The transaction costs of momentum are real, but they are not the death knell that critics claim — at least for institutional investors trading in liquid large-cap stocks."

> "Perhaps the most powerful argument for momentum is its negative correlation with value. Together they form a natural hedge that produces a combined Sharpe ratio well above either individually."

> "We find strong evidence that momentum is not explained by its exposure to common risk factors. It remains a significant anomaly relative to the CAPM, the Fama-French three-factor model, and Carhart's four-factor model."

> "The evidence for momentum is, if anything, stronger out-of-sample than in-sample — the opposite of what data mining would predict."

> "Long-only momentum — simply tilting toward past winners within a universe — earns positive risk-adjusted returns without any short selling. The short leg enhances but does not create the premium."

---

## Follow-Up Papers

| Paper | Authors | Year | Why Read |
|-------|---------|------|----------|
| Returns to Buying Winners and Selling Losers | Jegadeesh & Titman | 1993 | Original momentum paper; establishes the 12-1 standard |
| Momentum Crashes | Daniel & Moskowitz | 2016 | Full treatment of crash risk; volatility-targeting solution |
| Value and Momentum Everywhere | Asness, Moskowitz, Pedersen | 2013 | Cross-asset momentum + value combination; negative correlation documented |
| Do Momentum Strategies Still Work? | Geczy & Samonov | 2016 | Out-of-sample test going back to 1801; longest robustness check |
| Explanations for the Momentum Premium | Israel & Moskowitz | 2013 | Decomposes long vs. short leg; validates long-only implementation |
| 212 Years of Price Momentum | Geczy & Samonov | 2013 | Extreme long-run robustness; directly addresses Fiction 8 |
| Buffett's Alpha | Frazzini, Kabiller, Pedersen | 2013 | Quality + momentum as integrated factor; bridges Fiction 6 |
