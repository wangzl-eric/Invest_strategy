# Paper Notes: Common Risk Factors in the Returns on Stocks and Bonds
**Authors:** Fama, Eugene F. and French, Kenneth R. | **Year:** 1993 | **Journal:** Journal of Financial Economics
**Date Read:** 2026-03-29 | **Scores:** Credibility 5 | Relevance 5 | Actionability 4

---

## Core Thesis

A three-factor model for equity returns — comprising the market excess return, a size factor (SMB), and a value factor (HML) — absorbs most of the cross-sectional variation in average stock returns that the CAPM fails to explain. The same framework extends to bonds via two additional factors (TERM and DEF). The paper's central claim is that size and book-to-market equity are proxies for exposure to common, priced risk factors, not merely characteristics that happen to correlate with returns.

---

## Key Findings

- The CAPM market beta alone leaves large, systematic intercepts (pricing errors) on portfolios sorted by size and B/M — the two dimensions that dominate the cross-section of average equity returns.
- Adding SMB and HML drives adjusted $R^2$ to 0.90–0.97 across the 25 size/B/M sorted portfolios; intercepts become statistically indistinguishable from zero for most cells.
- Small-cap stocks earn higher average returns than large-cap stocks after controlling for beta (the size effect, documented by Banz 1981).
- High B/M (value) stocks earn higher average returns than low B/M (growth) stocks (the value effect, documented by Rosenberg, Reid & Lanstein 1985; Fama & French 1992).
- The two equity factors are largely independent: size and value effects are both present after controlling for each other.
- Bond returns share exposure to TERM and DEF; stocks also load on DEF, linking equity and fixed income risk premia.

---

## Methodology

**Data period:** July 1963 – December 1991 (342 months). NYSE, AMEX, and NASDAQ common stocks (SIC codes excluding financials in some variants).

**Portfolio formation — 25 equity portfolios:**
- Each June, all stocks are independently sorted into five size quintiles (market cap) and five B/M quintiles.
- The intersection of these sorts creates 25 value-weighted portfolios.
- B/M is computed as book equity (fiscal year ending in prior calendar year, i.e., December $t-1$) divided by market equity (December $t-1$).
- Portfolios are rebalanced annually in June to capture the most recent fiscal-year book values while ensuring the accounting data is publicly available.
- Monthly returns are tracked from July $t$ to June $t+1$.

**Test assets:** The 25 size/B/M portfolios are the primary left-hand-side variables in time-series regressions. Industry portfolios serve as additional out-of-sample validation.

**Estimation:** OLS time-series regressions of portfolio excess returns on factor returns. GRS F-statistic (Gibbons, Ross & Shanken 1989) used to jointly test whether intercepts are zero.

---

## The Three Factors

### MKT (Market Excess Return)
- **Definition:** $R_m - R_f$ — value-weighted return of all NYSE/AMEX/NASDAQ stocks minus the one-month Treasury bill rate.
- **Source:** CRSP value-weighted index; T-bill from Ibbotson Associates.
- **Role:** Captures overall equity market risk (covariance with aggregate wealth).

### SMB (Small Minus Big)
- **Definition:** Each June, stocks are split at the NYSE median market cap into "Small" and "Big" groups. Within each size group, stocks are further sorted into three B/M terciles: Low (bottom 30%), Medium (middle 40%), High (top 30%), using NYSE breakpoints.
- **Construction:** $\text{SMB} = \frac{1}{3}(\text{Small/Low} + \text{Small/Medium} + \text{Small/High}) - \frac{1}{3}(\text{Big/Low} + \text{Big/Medium} + \text{Big/High})$
- **Rebalancing:** Annually each June.
- **Average return (1963–1991):** approximately +0.27% per month.
- **Interpretation:** Compensates for some form of size-related distress or illiquidity risk that is not captured by market beta.

### HML (High Minus Low)
- **Definition:** Stocks are sorted at the NYSE median market cap into Small and Big, then into three B/M groups using 30th and 70th NYSE percentile breakpoints.
- **Construction:** $\text{HML} = \frac{1}{2}(\text{Small/High} + \text{Big/High}) - \frac{1}{2}(\text{Small/Low} + \text{Big/Low})$
- **Rebalancing:** Annually each June, using December $t-1$ book equity and June $t$ market equity.
- **Average return (1963–1991):** approximately +0.46% per month.
- **Interpretation:** Fama-French argue it proxies for relative distress — high B/M firms are more likely to be in financial distress and thus riskier in bad times.
- **Key detail:** Book equity excludes deferred taxes and investment tax credits; preferred stock book value is subtracted. Negative-book-equity firms are excluded.

---

## Factor Loadings and Explanatory Power

The three-factor model is estimated as:
$$R_{i,t} - R_{f,t} = \alpha_i + b_i(R_{m,t} - R_{f,t}) + s_i \cdot \text{SMB}_t + h_i \cdot \text{HML}_t + \epsilon_{i,t}$$

**What the model explains:**
- Adjusted $R^2$ ranges from 0.83 to 0.97 across the 25 portfolios — a dramatic improvement over the CAPM ($R^2$ of 0.60–0.92, with large residuals in corner cells).
- Intercepts ($\alpha_i$) are close to zero and jointly insignificant (GRS test) for most groupings.
- Factor loadings are intuitive: small stocks load positively on SMB; value stocks load positively on HML; growth stocks load negatively on HML.

**What the CAPM misses:**
- The CAPM produces a monotone pattern of negative alphas for large/growth portfolios and positive alphas for small/value portfolios — exactly the cells that earn the highest average returns.
- Beta alone does not account for the size premium or the value premium; both survive after full beta adjustment.
- The CAPM intercepts are economically large: the small/high-B/M portfolio earns ~0.65% per month more than the CAPM predicts.


---

## Bond Factors

Fama-French extend the framework to government and corporate bonds with two additional factors:

### TERM (Term Premium)
- **Definition:** Return on a long-term government bond portfolio minus the one-month T-bill rate.
- **Captures:** Compensation for interest rate duration risk — the risk that long-term rates rise unexpectedly.
- **Data:** Long-term government bond returns from Ibbotson Associates.
- **Finding:** Both stock and bond portfolios load positively on TERM, with stronger loadings for bonds (as expected). Equity TERM loadings are modest but statistically significant, reflecting the discount-rate channel linking equity valuations to the yield curve.

### DEF (Default Premium)
- **Definition:** Return on a long-term corporate bond portfolio minus the long-term government bond return of the same maturity.
- **Captures:** Compensation for default/credit risk — the risk of corporate default or credit spread widening.
- **Finding:** Stocks load positively on DEF; small and value stocks tend to have higher DEF loadings, connecting equity distress risk to credit market conditions.
- **Insight:** The comovement of stock returns with DEF links the equity value premium to credit risk — high B/M firms are more likely to be financially distressed, so their stocks behave more like below-investment-grade bonds.

**Combined five-factor bond model:** For bond portfolios, TERM and DEF largely suffice. For stocks, all five factors together (MKT, SMB, HML, TERM, DEF) increase explanatory power modestly beyond the three equity factors, but the equity factors dominate.

---

## What Fama-French Leaves Unexplained

### Momentum (the most important gap)
- Jegadeesh & Titman (1993) document that stocks with high prior 12-month returns continue to outperform over the next 3–12 months (momentum effect).
- The three-factor model not only fails to explain momentum — it predicts the *opposite*. Recent winners tend to be large/growth stocks with negative HML loadings, yet they earn positive abnormal returns.
- Fama-French (1996, JFE) explicitly acknowledge this failure: "The momentum effect of Jegadeesh and Titman (1993) is the biggest problem for the three-factor model."
- Carhart (1997) adds a fourth factor (WML — Winners Minus Losers, i.e., the momentum factor) to address this.

### Other known gaps
- **Short-term reversal:** 1-month return reversal is not captured (and partially exploited by the Jegadeesh-Titman construction).
- **Profitability and investment:** Profitable firms and low-investment firms earn higher returns than three-factor loadings predict — motivating Fama-French (2015) to add RMW (Robust Minus Weak) and CMA (Conservative Minus Aggressive).
- **Accruals anomaly** (Sloan 1996): firms with high accounting accruals underperform; not captured.
- **The model is empirically derived, not theoretically grounded:** it describes what factors work, not why, leaving the economic mechanism open to debate.


---

## Risk vs Mispricing Debate

### Fama-French interpretation: Rational risk pricing
- SMB and HML are proxies for underlying state variables that rational investors care about (in the spirit of Merton's ICAPM or Ross's APT).
- High B/M firms tend to be financially distressed — they have low earnings, high leverage, and uncertain cash flows. Investors demand a premium for holding them precisely because they underperform in bad economic states.
- Small firms are more sensitive to business-cycle conditions, credit availability, and liquidity shocks — again, rational risk compensation.
- The factors are therefore priced because they represent systematic risks that cannot be diversified away; the average investor must hold them and must be compensated for doing so.

### Daniel-Titman (1997): Characteristics, not covariances
- Daniel and Titman argue that it is the *characteristics* themselves (small size, high B/M) — not the factor loadings — that predict returns.
- Their test: form portfolios matched on B/M and size but with *different* HML/SMB betas. If Fama-French is correct, high-beta portfolios should earn more. If characteristics drive returns, beta should not matter after controlling for characteristics.
- Their 1963–1993 sample finds that characteristics dominate: stocks with high B/M earn high returns regardless of their HML loading, inconsistent with a pure risk-based story.
- This supports a behavioral explanation: investors systematically overprice glamour (low B/M) stocks and underprice value (high B/M) stocks due to extrapolation bias or overconfidence.
- **Counter-response:** Davis, Fama & French (2000) extend the sample to 1929–1963 and find the risk-based model holds up in the longer history — the Daniel-Titman result appears sample-specific.

### Current consensus
- The debate is unresolved. Both stories have empirical support. Most practitioners treat the factors as empirical regularities worth harvesting regardless of the underlying mechanism.
- Behavioral interpretation supports momentum (past losers are underpriced); risk interpretation struggles to explain momentum.
- Risk interpretation better explains why value spreads widen in crises (value is riskier precisely when it matters most).

---

## Connection to Ilmanen Expected Returns Ch5 + Ch12 + Ch16

**Chapter 5 — Equity Risk Premium:**
Fama-French provides the foundational decomposition of equity returns into market, size, and value components. Ilmanen uses it as the baseline framework when discussing equity factor premia and argues the ERP itself is best understood as compensation for bad-times risk — the same logic Fama-French apply to HML and SMB.

**Chapter 12 — Value Premium:**
Ilmanen synthesizes global evidence on value (B/M, E/P, CF/P, D/P) and concludes the premium is real but has declined post-publication, partly due to crowding. He presents both the risk story (Fama-French distress) and the behavioral story (Daniel-Titman, Lakonishok-Shleifer-Vishny) and argues for a blended view: distress risk and mispricing both contribute. The post-2007 underperformance of HML is discussed as potentially structural (rising intangibles making book value less informative of firm value) or cyclical (value spread compression from rate environment).

**Chapter 16 — Size Premium:**
Ilmanen is skeptical of the pure SMB premium after controlling for quality. The raw size premium largely disappears when accounting for the fact that small stocks are disproportionately low-quality (junk). Asness, Frazzini & Pedersen's Quality Minus Junk (QMJ) factor substantially reduces residual size premium — small-but-quality stocks do earn a premium, but the average small stock does not reliably outperform after transaction costs. This is a significant qualification to the Fama-French SMB narrative.

---

## Implementability for This Team

**Core constraint:** Compustat B/M data is not available in this platform. Direct replication of the Fama-French portfolio construction (firm-level book equity from Compustat + CRSP market cap) is not feasible without a data vendor subscription.

**ETF proxies (viable approach):**

| Factor | ETF Proxy | Notes |
|--------|-----------|-------|
| MKT | SPY, IVV | S&P 500 vs T-bill — standard |
| HML (value, large-cap) | IWD (iShares Russell 1000 Value) | Blended, not pure HML long leg |
| HML (value, small-cap) | IWN (iShares Russell 2000 Value) | Small-cap value tilt |
| SMB | IWM minus IWB (Russell 2000 minus Russell 1000) | Rough size spread; long-only bias |
| Growth (short leg proxy) | IWF (iShares Russell 1000 Growth) | For constructing L/S spreads |

**Limitations of ETF approach:**
- ETF factor exposures are diluted — IWD holds value stocks but also blend names; it is not a pure HML long portfolio.
- Cannot replicate the 25-portfolio decomposition or recover clean factor loadings from ETF returns alone.
- Long-only ETF proxies do not capture the short leg, which contributes meaningfully to historical HML returns.
- Factor timing research requires clean factor returns, not ETF NAV returns with management fees.

**What is feasible:**
- **Exposure analysis:** Regressing a portfolio's returns against the publicly available Fama-French factor returns (Ken French data library — free CSV download) to decompose alpha and beta. This requires only a one-time ingest into the DuckDB store.
- **Factor tilt overlay:** Long IWD / short IWF or long IWN / short IWB as a value tilt on top of existing equity positions.
- **Regime analysis:** Examining when value (HML) spreads widen or compress using available macro data (FRED yield curve, credit spreads via HYG/LQD) — fully feasible with current infrastructure.
- **Connection to approved research:** The Quality + Safe-Haven Overlay (PM-approved, Priority 2) using QUAL and USMV blends HML-adjacent value signals with profitability and low-vol screens — the FF framework directly informs factor exposure attribution for that strategy.

**Recommended first step:** Pull Fama-French 3-factor daily/monthly returns from French's data library and store in `data/market_data/` as a Parquet file. This enables factor regression on any portfolio without Compustat access.

---

## Key Quotes

> "If assets are priced rationally, our results suggest that stock risks are multidimensional. One dimension of risk is proxied by size, ME. Another dimension of risk is proxied by BE/ME."
> — Fama & French (1993), p. 5

> "The three-factor model captures the average returns on portfolios formed on E/P, C/P, and sales growth... The main embarrassment of the model is its inability to explain the continuation of short-term returns."
> — Fama & French (1996, JFE)

> "Rejecting the [CAPM] is rejecting the whole framework for thinking about expected returns."
> — Fama (paraphrased; underscores why they resist the mispricing interpretation and insist on rational risk)

---

## Follow-Up Papers

| Paper | Key Contribution |
|-------|------------------|
| Fama & French (1992, JF) | Cross-sectional precursor; establishes size and B/M dominate beta in predicting average returns |
| Fama & French (1996, JFE) | Extends 3-factor model to other anomalies; explicitly acknowledges momentum failure |
| Carhart (1997, JF) | Adds momentum (WML) as 4th factor; industry standard for mutual fund performance evaluation |
| Daniel & Titman (1997, JF) | Characteristics vs. covariances test; primary empirical challenge to the risk interpretation |
| Davis, Fama & French (2000, JF) | Extends to 1929–1963; rebuts Daniel-Titman result as sample-specific |
| Fama & French (2015, JFE) | 5-factor model adds RMW (profitability) and CMA (investment); motivated by dividend discount model |
| Asness, Frazzini & Pedersen (2019, JFE) | Quality Minus Junk (QMJ); shows raw size premium largely explained by quality tilt |
| Hou, Xue & Zhang (2015, RFS) | q-factor model (investment + profitability); alternative to FF5 |
| Novy-Marx (2013, JFE) | Gross profitability as powerful value complement; profitable firms outperform |
| Jegadeesh & Titman (1993, JF) | Momentum — the anomaly FF cannot explain; essential companion reading |