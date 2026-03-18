# Cerebro Briefing: Vol-Scaled Momentum
Date: 2026-03-15

---

## Strategy Context

- **Strategy:** Volatility-Scaled Momentum (Low-Turnover Core)
- **Researcher:** Elena
- **Universe:** US Large Cap (~30 stocks)
- **Signals:** Inverse vol (60d, 0.40), Risk-adj momentum 12-1m (0.40), Mean-reversion dampener 20d (-0.20)
- **Rebalance:** Bi-monthly; long-only; 10-15 positions

---

## Supporting Evidence

### 1. Moreira & Muir (2017) — "Volatility-Managed Portfolios"
*Journal of Finance, vol. 72(4), pp. 1611–1644*
- **Finding:** Reducing factor exposure during high-volatility periods produces large in-sample alphas and substantially increases Sharpe ratios. Momentum is among the factors with the largest gains from vol scaling.
- **Relevance: 90/100** — The direct academic foundation for this strategy's core mechanism.

### 2. DeMiguel, Martin-Utrera & Uppal (2024) — "A Multifactor Perspective on Volatility-Managed Portfolios"
*Journal of Finance, December 2024*
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3982504)
- **Finding:** A conditional mean-variance multifactor portfolio whose weights decrease with market volatility achieves 13% higher out-of-sample, net-of-costs Sharpe ratio vs. unconditional multifactor. Estimation error and transaction costs do not explain the multifactor gains. This rehabilitates vol management as an approach—but only at the portfolio level, not factor by factor.
- **Relevance: 88/100** — Validates the vol-scaling principle when applied to a blended signal portfolio. Elena's 3-signal blend may benefit from this insight.

### 3. Enhanced Momentum Strategies (Journal of Banking & Finance, 2023)
[ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0378426622002928)
- **Finding:** All three vol-scaling variants (constant-vol, semi-vol, dynamic) reduce momentum crashes and raise risk-adjusted returns across 48 international markets. No single variant consistently dominates, but all outperform unmanaged momentum.
- **Relevance: 85/100** — Direct confirmation that the risk-adjusted momentum signal Elena uses is empirically sound.

### 4. International Evidence on Vol-Managed Equity Factors (ScienceDirect, 2024)
[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S092753982400094X)
- **Finding:** Across 45 international markets and 9 factor portfolios, volatility management is most promising for momentum (and market) portfolios. Vol-managed momentum is "partially robust" to transaction costs — the only factor where this holds.
- **Relevance: 84/100** — Momentum is specifically named as the factor most suited to vol management. Supports Elena's choice of momentum as the primary alpha signal.

### 5. Downside Risk & Volatility-Managed Portfolios (Wang & Yan, Lehigh)
[Lehigh PDF](https://www.lehigh.edu/~xuy219/research/Downside.pdf)
- **Finding:** Downside volatility scaling outperforms total volatility scaling in 70 of 103 equity factors. Enhanced performance is driven by return timing: downside vol negatively predicts future returns.
- **Relevance: 72/100** — Suggests Elena's 60-day realized vol could be improved by switching to a downside vol measure (semi-deviation). Actionable enhancement.

### 6. Man Group — "The Impact of Volatility Targeting"
[Man Group](https://www.man.com/insights/the-impact-of-volatility-targeting)
- **Finding:** Sharpe ratios are higher with vol scaling specifically for risk assets (equities, credit). Vol targeting introduces a momentum overlay via the leverage effect. For bonds, FX, commodities: negligible effect.
- **Relevance: 75/100** — Confirms equity is the right asset class for this approach.

### 7. Jiang, Li, Ning & Xue (2025) — "Scaled Factor Portfolio"
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5392547)
- **Finding:** Scaling each factor by its Sharpe ratio, then extracting PCA components, produces 12–19% annual alpha, Sharpe ratios up to 2.0 across 50 anomalies.
- **Relevance: 70/100** — Elena's risk-adjusted momentum signal (momentum/vol) is a simplified version of this approach. Paper validates the direction.

### 8. Mitsui Commodity Prediction Challenge (Kaggle, 3rd Place)
- **Finding:** "Directional Trends over Volatility" approach — trend signals normalized by volatility — was a top solution even in non-equity markets. Stability of normalized signals mattered as much as raw accuracy.
- **Relevance: 65/100** — Practitioner validation from a competitive ML setting.

---

## Contradicting Evidence & Failure Cases

### 1. Cederburg, O'Doherty, Wang & Yan (2020) — "On the Performance of Volatility-Managed Portfolios"
*Journal of Financial Economics, 138(1), pp. 95–117*
[Lehigh PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
- **Finding:** In-sample alphas for vol-managed portfolios do NOT translate to out-of-sample gains due to structural instability in spanning regressions. Across 103 equity strategies, no statistical or economic evidence that vol-managed portfolios systematically earn higher Sharpe ratios OOS. The optimal combination weights are only knowable ex post.
- **Severity: HIGH** — This is the primary OOS challenge to the entire approach. Elena must demonstrate robust OOS results, not just in-sample.

### 2. Barroso & Detzel (2021) — Transaction Costs Erode Gains
- **Finding:** Performance gains from vol-managed portfolios disappear in low-sentiment periods once transaction costs are accounted for. Vol-managed market portfolio outperforms during high-sentiment, underperforms during low-sentiment.
- **Severity: HIGH** — With bi-monthly rebalancing and 50-70% annual turnover, Elena must show the strategy survives 2x realistic costs. Currently only a requirement ("Survives 2x realistic costs: Sharpe > 0"), not yet demonstrated.

### 3. Post-2020 Momentum Crash Risk (2022 Bear Market)
*Sources: Robeco (2023), Morningstar, Daniel & Moskowitz JFE 2016*
[Robeco](https://www.robeco.com/en-int/insights/2023/02/quant-chart-taming-momentum-crashes)
- **Finding:** November 2022 and early 2023 saw classic momentum crashes — revival of prior-year losers destroyed momentum factor returns. Higher realized variance is associated with more negative momentum strategy betas. The strategy's vol scaling should theoretically reduce exposure before crashes, but the trigger is regime reversal speed, not simply high realized vol.
- **Severity: MEDIUM** — Vol scaling helps but cannot fully prevent crash risk if regime reversals are fast (vol spikes AFTER the reversal starts, not before).

### 4. Crowding & Valuation Risk (2024-2025)
*Source: SSGA Analysis, Morningstar 2025*
[SSGA](https://www.ssga.com/us/en/intermediary/insights/what-drove-momentums-strong-2024-and-what-it-could-mean-for-2025)
- **Finding:** After 2024's record momentum run (MTUM +32.89%), crowding is elevated. In 7 of 11 times momentum was the best-performing US factor, excess returns were negative the next year (avg -5%). Valuations are at richer-than-usual premiums. Low-vol + momentum overlap in MTUM (which screens for 3-year risk-adjusted returns) means both signals may be crowded simultaneously.
- **Severity: MEDIUM** — Not a structural failure, but timing risk is elevated. 2025 may be a poor start for paper trading given elevated crowding.

### 5. Mean Reversion Dampener — Regime Dependence
*Sources: Medhat & Schmeling (RFS), Hudson & Thames, Morningstar*
- **Finding:** 20-day short-term reversal dampener likely hurt performance in 2024's strong trending regime (one of momentum's best years in decades). Short-term reversal's high transaction costs also subsume much of the gross return from the dampening effect. The -0.20 weight is ad hoc.
- **Severity: MEDIUM** — The dampener's value is regime-dependent. PM has already flagged this as an overfitting risk. Literature does not strongly support a fixed -0.20 weight.

### 6. Low Volatility Anomaly — Low Information Ratio Warning
*Source: BNP Paribas AM, Rational Reminder Podcast 264*
[BNP Paribas](https://viewpoint.bnpparibas-am.com/low-volatility-the-hidden-factor/)
- **Finding:** Low-vol anomaly has "a lot of tracking error and a little bit of outperformance" — information ratio close to zero. Adding low-vol to a multi-factor strategy tends to *lower* overall information ratio. Most institutions explicitly avoid it for this reason.
- **Severity: MEDIUM** — The inverse-vol component (0.40 weight) may drag down the combined strategy's information ratio. Consider reducing its weight or replacing with a quality/profitability screen.

---

## Alpha Decay Analysis

### Moreira & Muir Decay
- **Publication:** 2017 (JoF); working paper widely circulated from 2016
- **Decay evidence:** Cederburg et al. (2020) is the most rigorous post-publication test. Individual-factor vol management has decayed out-of-sample. Multifactor approach (DeMiguel 2024) partially restores the alpha — Elena's blended signal is closer to the multifactor design, which is more favorable.
- **Half-life estimate:** Uncertain. 4-8 years if the multifactor mechanism holds; shorter if crowding in low-vol + momentum smart beta accelerates decay.

### Momentum Factor Decay
- **Rönkkö & Holmi (2025) — "Revisiting Factor Momentum: A One-month Lag Perspective"**
  [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5333744)
  - Questions whether factor momentum profitability is driven by static tilts toward historically positive factors rather than genuine timing.
- **van Vliet et al. (2025) — "Momentum Factor Investing: Evidence and Evolution"**
  [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5561720)
  - Evidence that momentum remains present but increasingly concentrated in periods of strong macro trends.
- **Assessment:** Momentum alpha has not fully decayed but is more episodic. The 12-1 lookback used by Elena is the most well-documented specification — less subject to data mining concerns than shorter or longer windows.

### Smart Beta / ETF Crowding Effect
- MTUM ($10B+ AUM) screens for 6-12m risk-adjusted returns (vol-scaled momentum) and 3-year low vol — essentially the same combination as Elena's strategy, but at institutional scale.
- The existence of large ETFs tracking similar factors is the strongest crowding evidence. Returns are now partially competed away at the entry level, though the specific 30-stock US large cap implementation differs from MTUM's 125-stock index.
- **Assessment:** Mild to moderate decay from ETF crowding in the US large cap space. Severity depends on whether Elena's universe overlaps heavily with MTUM holdings.

---

## Key Papers (with citations)

| Paper | Authors | Year | Key Finding | Relevance |
|---|---|---|---|---|
| "Volatility-Managed Portfolios" | Moreira & Muir | 2017 | Vol scaling increases Sharpe, especially for momentum | 90/100 |
| "A Multifactor Perspective on Vol-Managed Portfolios" | DeMiguel, Martin-Utrera, Uppal | 2024 | 13% OOS Sharpe gain at multifactor level, net of costs | 88/100 |
| "Enhanced Momentum Strategies" | Multiple authors | 2023 | All vol-scaling variants reduce crashes, raise Sharpe | 85/100 |
| "International Evidence on Vol-Managed Factors" | Multiple authors | 2024 | Momentum + market are most robust factors to vol management | 84/100 |
| "On the Performance of Volatility-Managed Portfolios" | Cederburg, O'Doherty, Wang, Yan | 2020 | OOS gains do not hold; structural instability | HIGH contra |
| "Downside Risk & Vol-Managed Portfolios" | Wang & Yan | 2021 | Downside vol outperforms total vol scaling | 72/100 |
| "VIX-Managed Portfolios" | Multiple authors | 2024 | VIX scaling reduces systematic risk during downturns | 68/100 |
| "Scaled Factor Portfolio" | Jiang, Li, Ning, Xue | 2025 | Sharpe-scaled PCA factors: 12-19% alpha, Sharpe up to 2.0 | 70/100 |
| "Momentum Factor Investing" | van Vliet, Baltussen, Dom, Vidojevic | 2025 | Momentum remains present but episodic | 65/100 |
| "Revisiting Factor Momentum" | Rönkkö & Holmi | 2025 | Profitability may be static tilts, not genuine timing | 60/100 contra |

---

## Book References

- **Ang, *Asset Management* (Tier 6, Equity/CTA):** Systematic coverage of low-vol anomaly, momentum, and factor investing. Relevant to how equity factors interact. Notes that combining momentum and low-vol requires careful construction to avoid crowding both at the same time.

- **López de Prado, *Advances in Financial Machine Learning* (Tier 4):** Ch. 11: "Backtesting is NOT a research tool" — all in-sample alpha estimates for vol-scaling must be validated through CPCV before trust. Ch. 14: Deflated Sharpe adjusts for the number of trials; Elena's three-signal combination must pass DSR > 0.

- **Harvey, Rattray & Van Hemert, *Strategic Risk Management* (Tier 0):** Directly addresses volatility targeting in systematic portfolios. Discusses the leverage effect and why equities specifically benefit from vol scaling — consistent with the Man Group practitioner finding.

- **Grinold & Kahn, *Active Portfolio Management* (Tier 8):** IC-IR-BR framework. Low-vol signal combined with momentum may have low IC (accuracy of each signal) despite reasonable IR for momentum alone. Warns against diluting a high-IC signal with a low-IC signal.

- **Clenow, *Following the Trend* + Greyserman/Kaminski (Tier 6):** Trend-following / CTA literature consistently validates momentum across asset classes. However, the equity long-only constraint and the mean-reversion dampener diverge from standard CTA approaches.

---

## Known Failure Modes

1. **Fast regime reversals after bear markets** (2009, 2020, 2022 Q4): Vol scaling reduces exposure before the crash, but if the reversal (loser stocks rebounding sharply) is faster than the vol signal adjusts, the portfolio is caught short on exposure at exactly the wrong moment.

2. **Low-sentiment / risk-off periods** (Barroso & Detzel 2021): After transaction costs, vol management gains disappear in low-sentiment environments. A prolonged risk-off period erodes the strategy's net edge.

3. **Combined low-vol + momentum crowding unwind** (Crowding risk, 2025): When both signals are crowded simultaneously and trigger a factor unwind, losses are amplified because both sides of the portfolio move adversely at the same time.

4. **Mean-reversion dampener misfires in trending markets** (2024): In years like 2024 when momentum is strongest, the -0.20 dampener actively reduces exposure to the best-performing stocks, costing alpha.

5. **OOS parameter instability in signal blend** (Cederburg et al. 2020): The 0.40/0.40/-0.20 weights that look optimal in-sample will not hold OOS. This is the core finding that must be addressed through CPCV.

---

## Suggested Approaches from Literature

1. **Switch from total to downside volatility scaling** (Wang & Yan 2021): Replace the 60-day realized vol scaling with 60-day semi-deviation (downside only). Outperforms in 70/103 factors. Low implementation cost.

2. **Multifactor vol management rather than factor-by-factor** (DeMiguel et al. 2024): Vol management works better at the portfolio level — scale all signals simultaneously based on market vol, not each signal by its own realized vol. Elena's implementation already blends signals before optimization, which partially achieves this.

3. **Add a regime awareness layer to the dampener** (dynamic approach): Instead of a fixed -0.20 mean-reversion weight, make it conditional on market vol regime (VIX above/below threshold). In high-vol regimes, drop the dampener; in low-vol trending regimes, activate it.

4. **Add a profitability/quality overlay** (Asness, Frazzini & Pedersen 2019, cited in proposal): Proposal itself notes "quality is not in the signal." Literature consistently shows quality + momentum is the strongest combination. Adding a simple ROE or earnings stability screen would improve factor diversification and reduce pure low-vol crowding risk.

5. **Check MTUM overlap** before paper trading: Compute the overlap between Elena's 10-15 stock portfolio and MTUM's ~125 holdings. If overlap > 70%, the strategy is effectively a higher-concentration, higher-tracking-error version of a commodity ETF — not truly differentiated alpha.

---

## Cerebro Assessment

**Confidence in Academic Foundation: 72/100**

The core mechanism (vol-scaled momentum) has strong theoretical and empirical support, particularly from Moreira & Muir (2017) and DeMiguel et al. (2024). The multifactor approach in DeMiguel is directly relevant to Elena's blended signal design.

**Confidence in OOS Viability: 55/100**

The primary risk is Cederburg et al.'s OOS finding. In-sample results will overstate performance. The 11 quantitative gates (especially DSR > 0, walk-forward hit rate > 55%, and PSR > 0.80) are correctly specified to guard against this. Pass rate on those gates is uncertain until the notebook runs.

**Feasibility Note:**

The strategy is technically implementable with existing codebase signals. The main unresolved risks are:
1. OOS instability of the 0.40/0.40/-0.20 blend weights — must be pre-committed, not optimized in-sample (PM correctly flagged this)
2. Transaction cost survival — 50-70% annual turnover must clear the 2x cost gate
3. Crowding timing — 2025 may be a challenging period to begin paper trading given post-2024 elevated momentum valuations

**Recommended pre-notebook check:** Run the MTUM holdings overlap analysis and consider a downside-vol variant as a second specification to test alongside the baseline.

---

*Compiled by Cerebro | 2026-03-15*
*Sources searched: research/external_ideas.md, books_and_papers/reading-list-summary.md, research/STRATEGY_TRACKER.md, SSRN, arXiv q-fin, Springer, ScienceDirect, Man Group, SSGA, Robeco, Morningstar*
