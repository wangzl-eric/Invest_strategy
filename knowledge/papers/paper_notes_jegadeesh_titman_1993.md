# Paper Notes: Returns to Buying Winners and Selling Losers
**Authors:** Jegadeesh, Titman
**Year:** 1993 | **Journal:** Journal of Finance
**Date Read:** 2026-03-29
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

---

## Core Thesis

Stocks that have performed well over the past 3–12 months continue to outperform, and stocks that have performed poorly continue to underperform, over the subsequent 3–12 months. This momentum in individual stock returns is statistically and economically significant, and cannot be explained by standard risk factors available in 1993. The finding directly challenges the semi-strong form of the Efficient Market Hypothesis.

---

## Key Findings

- **Momentum is pervasive:** 28 out of 32 J/K strategy combinations produce positive returns. The pattern is not a statistical fluke confined to one parameter choice.
- **Best strategies (monthly excess return, top-minus-bottom decile):**
  - J=12, K=3: ~1.31% per month (~15.7% annualized)
  - J=12, K=6: ~1.13% per month (~13.6% annualized)
  - J=6,  K=6: ~0.99% per month (~11.9% annualized)
  - J=6,  K=3: ~1.00% per month (~12.0% annualized)
  - Shorter J (3 months) tends to produce slightly weaker but still positive results
- **Long-run reversal:** At 2–5 year horizons, winner portfolios underperform and loser portfolios outperform — the momentum fully reverses, consistent with initial overreaction followed by correction.
- **January seasonality:** Momentum profits are sharply negative in January. Losers rebound strongly in January (tax-loss selling reversal), which partially offsets the annual Sharpe. Outside January, the momentum premium is even stronger.
- **Risk does not explain it:** The winner-minus-loser portfolio has near-zero beta and is not explained by size or book-to-market (to the extent those factors existed in 1993 tests). Excess returns survive simple risk adjustment.

---

## Methodology

- **Universe:** NYSE and AMEX common stocks, January 1965 – December 1989 (25 years).
- **Formation period (J):** Look back J months (J ∈ {3, 6, 9, 12}) to rank stocks by cumulative return.
- **Holding period (K):** Hold the resulting portfolio for K months (K ∈ {3, 6, 9, 12}).
- **Skip month:** A one-month gap is inserted between the end of the formation period and the start of the holding period. This eliminates the mechanical bid-ask bounce and short-term reversal documented by Jegadeesh (1990) that would otherwise contaminate momentum returns with microstructure noise.
- **Portfolio construction:** At each rebalancing date, stocks are ranked into deciles based on J-month past returns. The long portfolio buys the top decile (winners); the short portfolio sells the bottom decile (losers). The spread is the zero-cost winner-minus-loser (WML) return.
- **Overlapping portfolios:** To increase statistical power, Jegadeesh and Titman use overlapping K-month holding periods — at each month, a new cohort's strategy is initiated, and the reported return is the equally weighted average across all cohorts active in that month. This is the standard JT implementation convention.
- **Equal weighting:** Stocks within each decile are equally weighted at formation.

---

## Signal Construction

1. At the end of month $t$, compute the cumulative return of each stock over months $[t-J, t-1]$ (skipping month $t$ itself).
2. Rank all NYSE/AMEX stocks by this J-month return.
3. Assign decile labels: decile 10 = top 10% (winners), decile 1 = bottom 10% (losers).
4. Form equal-weight long portfolio in decile 10, equal-weight short portfolio in decile 1.
5. Hold for K months, then rebalance.
6. Report the time-series average of monthly WML returns.

**Key signal properties:**
- Raw past return (not risk-adjusted, not residual) — simple price momentum
- No volatility normalization (this comes later, e.g., Blitz et al. 2011 on residual momentum)
- No fundamental data required — purely price-based

---

## The J/K Parameter Grid

The table below summarizes approximate monthly WML returns across the 16 core combinations (annualized in parentheses). All are long top decile, short bottom decile.

| Formation J \ Holding K | K=3 | K=6 | K=9 | K=12 |
|---|---|---|---|---|
| **J=3**  | ~0.68% (8.2%) | ~0.78% (9.4%) | ~0.72% (8.6%) | ~0.69% (8.3%) |
| **J=6**  | ~1.00% (12.0%) | ~0.99% (11.9%) | ~0.88% (10.6%) | ~0.77% (9.2%) |
| **J=9**  | ~1.08% (13.0%) | ~1.07% (12.8%) | ~0.97% (11.6%) | ~0.78% (9.4%) |
| **J=12** | ~1.31% (15.7%) | ~1.13% (13.6%) | ~0.96% (11.5%) | ~0.70% (8.4%) |

**Key observations from the grid:**
- Longer formation periods (J=9, J=12) tend to deliver stronger momentum in short holding periods
- Returns decay as K lengthens — momentum fades and eventually reverses beyond K=12
- The J=12, K=3 combination is the single strongest in-sample strategy but also the highest-turnover
- The "sweet spot" for practical implementation is J=6–12, K=3–6

---

## Long-Run Reversal Finding

When holding periods are extended to 13–60 months (outside the paper's main 16 strategies but tested in robustness tables), the WML spread **reverses sign**: former winners underperform former losers. This is consistent with the De Bondt and Thaler (1985, 1987) overreaction hypothesis — prices initially overshoot, momentum profits during the continuation phase, and then mean-revert.

This creates a conceptual link between:
- **Short-term reversal** (1-month, Jegadeesh 1990): microstructure/bid-ask noise
- **Intermediate momentum** (3–12 month formation, 3–12 month holding): JT 1993
- **Long-run reversal** (3–5 year horizon): De Bondt-Thaler 1985

All three phenomena can be unified under a model of initial under-reaction to information followed by subsequent overreaction and correction — the framework later formalized by Daniel, Hirshleifer, and Subrahmanyam (1998) and Hong and Stein (1999).

---

## Risk-Based vs Behavioral Explanations

**What JT 1993 concluded:**
- Momentum cannot be explained by CAPM beta — winner-minus-loser portfolios have approximately zero market beta.
- Size (market cap) partially accounts for some return, but not enough to eliminate momentum.
- The authors were careful not to over-claim: they acknowledged their tests were limited to the risk factors understood in 1993 (pre-Fama-French three-factor model).
- They left open whether a risk-based explanation could be constructed, but noted the burden of proof was high given the pattern's characteristics.

**What was left open in 1993:**
- Whether momentum reflected a missing risk factor (compensation for bearing some priced risk)
- Whether it was purely a behavioral artifact (under-reaction to firm-specific news)
- Whether it would survive out-of-sample (answered by JT 2001: yes)

**Subsequent debate:**
- Fama and French (1996) documented that their three-factor model fails to explain momentum — calling it "the premier anomaly" and the one challenge to their framework they could not address
- Behavioral models: Hong-Stein (1999) gradual information diffusion; Daniel-Hirshleifer-Subrahmanyam (1998) investor overconfidence
- Risk-based attempts: Berk, Green, Naik (1999); Johnson (2002) — mostly unconvincing to the field
- Consensus circa 2010: momentum is likely behavioral in origin, but the debate is not fully resolved

---

## Why It Was Surprising in 1993

By 1993, the Efficient Market Hypothesis (EMH) in its semi-strong form — that prices fully reflect all publicly available information — was mainstream doctrine in academic finance. Under EMH, past prices contain no information useful for earning abnormal future returns.

The prior empirical landscape:
- Fama (1970) codified EMH and the evidence seemed broadly supportive
- Random walk tests (Lo and MacKinlay 1988) had found some weak serial correlation at weekly horizons, but it was too small to trade profitably
- De Bondt and Thaler (1985) showed 3–5 year reversal, but this was attributed to a risk story by Fama-French
- There was **no accepted evidence** of intermediate-term momentum in individual stocks before JT 1993

JT 1993 was shocking because:
1. It used a 25-year sample — not data mining on a short window
2. The strategy was simple, transparent, and replicable
3. The returns were economically large (1% per month)
4. The result was robust across 32 parameter combinations, not a single cherry-picked strategy
5. It implied that a naive investor following a mechanical rule could beat the market — the central EMH violation

The paper effectively forced the profession to either (a) find a risk explanation or (b) admit that prices do not fully and immediately incorporate information.

---

## The 2001 Follow-Up (Jegadeesh-Titman 2001)

Jegadeesh and Titman (2001, *Journal of Finance*, "Profitability of Momentum Strategies: An Evaluation of Alternative Explanations") tested whether the 1993 findings were in-sample overfit by examining the 1990–1998 out-of-sample period.

Key results of the 2001 paper:
- Momentum profits continued in the 1990s, out-of-sample, with similar magnitude
- The returns were not explained by the Conrad-Kaul (1998) risk explanation (which turned out to be due to a methodology error)
- The continuation was broadly consistent with behavioral under-reaction models (Hong-Stein)
- Long-run reversal (beyond 12 months) also persisted, consistent with eventual overreaction correction

The 2001 paper is important for validating that JT 1993 was not a look-back artifact. Combined, the two papers cover 1965–1998 — a 33-year period.

---

## Failure Modes & Limitations

1. **January effect:** Momentum returns are significantly negative in January. The loser portfolio rebounds sharply in January (tax-loss selling reversal), while winners do not keep pace. This means a long-only implementation or a strategy that avoids January short positions captures more stable returns. The annual Sharpe is noticeably higher when January is excluded.

2. **Small-cap and illiquid stocks:** The strongest momentum effects are concentrated in smaller, less liquid stocks with wider bid-ask spreads. For a large institutional investor, the universe must be restricted to liquid large-caps, which reduces but does not eliminate the signal.

3. **Bid-ask bounce:** Without the skip-month, short-term reversal (microstructure noise) contaminates the signal and overstates returns for very short formation periods. JT 1993 address this with the one-month skip, but the issue resurfaces if the skip is omitted.

4. **Transaction costs:** The strategy involves significant monthly turnover, particularly for short K (K=3). With realistic round-trip costs (bid-ask spread plus commissions), net returns shrink materially, especially for the K=3 combinations. The K=6 or K=12 variants are more cost-efficient.

5. **Crashes:** Momentum is subject to sharp, rapid reversals during market stress (e.g., 2009 momentum crash). This tail risk is not visible in the 1965–1989 sample and was only fully appreciated after Daniel and Moskowitz (2016). The strategy can lose 40–50% in a single quarter during momentum crashes.

6. **Universe dependency:** Results are for NYSE/AMEX. The signal generalizes internationally (Rouwenhorst 1998) and across asset classes (Asness, Moskowitz, Pedersen 2013), but the exact return magnitudes differ by universe.

7. **Data period:** The 1965–1989 sample predates decimalization and Reg NMS. Post-2000 microstructure changes (tighter spreads, faster price discovery) may affect the signal's raw magnitude.

---

## Connection to Ilmanen (Expected Returns 2011)

In *Expected Returns* (2011), Chapter 14 ("Momentum"), Ilmanen treats JT 1993 as the foundational empirical anchor for the equity momentum premium. Key connections:

- **Ch14 structure:** Ilmanen presents momentum as one of the four major return premia alongside value, carry, and defensive/low-beta. JT 1993 is the primary citation establishing that the equity momentum premium is real and large.
- **Universality argument:** Ilmanen extends JT's stock-level finding to argue for momentum across asset classes — the same price continuation logic applies to bonds, commodities, currencies, and country indices. JT 1993 is the starting point for this generalization.
- **Interaction with value:** Ilmanen discusses the momentum-value combination at length (negative correlation between the two premia creates diversification benefits). The JT framework defines what "momentum" means in that combination.
- **Risk vs. behavioral:** Ilmanen's view is that momentum is primarily behavioral (under-reaction, gradual information diffusion) rather than risk compensation — consistent with the JT 2001 conclusion and the Fama-French (1996) acknowledgment that the three-factor model cannot explain it.
- **Practical implementation:** Ilmanen notes that net-of-cost momentum returns are substantially smaller than gross returns, echoing the JT limitation on transaction costs, and recommends longer rebalancing intervals and large-cap universes to improve implementability.

---

## Implementability for This Team

**Data requirements:**
- Monthly or daily total returns (price + dividends) for individual equities
- Current available universe: `data/market_data/prices/equities.parquet` — check ticker coverage
- For a clean implementation, need a minimum of 500–1000 liquid US stocks; S&P 500 constituents are sufficient

**Practical signal construction:**
- Formation: 12-month cumulative return, skip last month (J=12, skip=1)
- Holding: 1–6 months with monthly rebalancing of overlapping cohorts
- Universe: Top 500–1000 stocks by market cap to avoid small-cap/liquidity issues
- Rebalancing: Monthly, equal-weight within winner/loser quintiles or deciles

**Cost management:**
- Avoid K=3 (high turnover); prefer K=6 or K=12 for lower transaction costs
- Cap individual position size to avoid concentrated bets in high-momentum names
- Consider excluding January rebalancing or hedging January exposure

**Integration with team's existing work:**
- The `backtests/strategies/signals.py` framework can accommodate a momentum signal via cumulative return ranking
- `backtests/costs/transaction_costs.py` and `slippage.py` should be applied — gross returns are not investable
- The stats module (`backtests/stats/`) can run PSR and MinBTL on the strategy output
- Given prior rejection of Vol-Scaled Momentum (strategy-level, not stock-level), this stock-selection momentum is a different beast — cross-sectional rather than time-series

---

## Key Quotes

> "The returns of the zero-cost winner-minus-loser portfolio are positive for each of the 32 strategies tested."

> "Stocks that perform the best over the previous 3 to 12 months tend to continue to perform well over the following 3 to 12 months."

> "The profitability of the momentum strategies is not due to their systematic risk." [referring to CAPM beta]

> "The returns of the winner portfolio are negative in January relative to the loser portfolio; however, the winner portfolio significantly outperforms the loser portfolio in the remaining 11 months of the year."

> "The returns of the zero-cost momentum portfolio are positive in the first year, but become negative in years two to five."

---

## Follow-Up Papers

| Paper | Contribution |
|---|---|
| Jegadeesh & Titman (2001) | Out-of-sample confirmation 1990–1998; rules out Conrad-Kaul risk explanation |
| Fama & French (1996) | Three-factor model fails to explain momentum; calls it "the premier anomaly" |
| Rouwenhorst (1998) | Momentum confirmed in 12 European markets — not a US data artifact |
| Asness, Moskowitz & Pedersen (2013) | Value and Momentum Everywhere — extends to 8 asset classes, 4 markets |
| Daniel, Hirshleifer & Subrahmanyam (1998) | Behavioral model: investor overconfidence generates momentum then reversal |
| Hong & Stein (1999) | Gradual information diffusion model — under-reaction drives continuation |
| Daniel & Moskowitz (2016) | Momentum crashes: options-like payoff, crash prediction, dynamic scaling |
| Barroso & Santa-Clara (2015) | Managed momentum: vol-scaling cuts crash risk, improves Sharpe |
| Novy-Marx (2012) | Intermediate momentum (7–12 month formation) drives most of the JT signal |
| Blitz, Huij & Martens (2011) | Residual momentum (vs. factor returns) stronger and more stable than raw JT |
