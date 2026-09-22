# Paper Notes: Time Series Momentum
**Authors:** Moskowitz, Ooi, Pedersen
**Year:** 2012 | **Journal:** Journal of Financial Economics
**Date Read:** 2026-03-29
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

---

## Core Thesis

Time series momentum (TSMOM) — going long assets whose price has risen over the past 12 months and short assets whose price has fallen — generates positive risk-adjusted returns across every major asset class studied. This is distinct from cross-sectional momentum (Jegadeesh-Titman), which bets on relative performance within an asset class. The key claim is that an asset's own past return predicts its own future return, not just its performance relative to peers. The authors argue the effect is driven by the interplay of initial underreaction (anchoring, gradual diffusion of information) followed by delayed overreaction (herding, feedback trading), with an eventual reversal beyond 12 months as prices correct. TSMOM is also the dominant structural driver behind CTA and managed futures performance.

---

## Key Findings

1. **Universal effect across asset classes:** TSMOM is positive on average in all four asset classes — equity index futures, bond futures, currency forwards, and commodity futures — across a 1965–2009 sample.
2. **Magnitude:** A diversified TSMOM portfolio delivers annualized excess returns of approximately 1.4% per month (roughly 17% annualized) with a Sharpe ratio of approximately 1.28 before trading costs, rising to ~1.5 after controlling for common risk factors.
3. **Autocorrelation structure:** Individual futures returns show statistically significant positive serial correlation at lags 1–12 months, and significant negative serial correlation (mean reversion) at lags of 2–5 years. This is the empirical signature underlying TSMOM.
4. **Crisis alpha:** TSMOM delivers its largest returns during periods of extreme equity market stress. In the worst equity market months it averages about +0.5% per month; in the 2008–2009 financial crisis it produced strongly positive returns.
5. **Low correlation to cross-sectional momentum:** Correlation with the Jegadeesh-Titman UMD factor is approximately 0.49–0.50, meaning they share risk but are far from identical.
6. **CTA explanation:** TSMOM explains 50–75% of the return variation in major CTA indices over the sample period (R² in regressions). A simple TSMOM replication portfolio closely tracks the Fung-Hsieh trend-following factor.

---

## Methodology

- **Universe:** 58 highly liquid futures contracts: 24 commodities, 12 cross-rate currency forwards, 9 equity index futures, 13 bond futures. Liquidity filter applied throughout.
- **Sample period:** January 1965 – December 2009 (44 years). Not all instruments have full histories; each added as data becomes available.
- **Returns:** Total excess returns on futures (fully collateralized, i.e., futures price return).
- **Portfolio construction:** Monthly rebalancing. Each instrument receives a long or short position based on the sign of its past 12-month return. Position size scaled by inverse ex-ante volatility (see Signal Construction below).
- **Statistical tests:** Newey-West corrected standard errors (12 lags) throughout. Fama-MacBeth regressions for cross-sectional tests. Fung-Hsieh 7-factor model for alpha estimation. CAPM, Fama-French 3-factor, and Carhart 4-factor alphas reported.
- **Transaction costs:** Estimated from bid-ask spreads on futures markets; TSMOM remains profitable after costs due to low turnover relative to cross-sectional strategies.

---

## Signal Construction

**Look-back window:** 12-month return (excluding the most recent month, i.e., months $t-12$ to $t-2$, following the literature convention on skip-month to avoid microstructure bias — though the authors also test the full 12 months including month $t-1$).

**Signal direction:**
$$s_{i,t} = \text{sign}\left(r_{i,t-12:t-1}\right) \in \{+1, -1\}$$

**Position sizing (volatility scaling):**
$$w_{i,t} = \frac{s_{i,t}}{\hat{\sigma}_{i,t}}$$

where $\hat{\sigma}_{i,t}$ is the ex-ante annualized volatility estimated from daily returns over the past 1–3 months (exponentially weighted). This ensures each position contributes approximately equal risk regardless of the asset's own volatility.

**Portfolio return:** The TSMOM portfolio return for month $t$ is:
$$r^{TSMOM}_t = \sum_{i=1}^{N} w_{i,t} \cdot r_{i,t}$$

**Hold period:** The authors test 1-month holding (with monthly rebalancing) as the primary specification, and confirm results are robust across 1, 3, 6, and 12-month formation/holding combinations.

**Target volatility:** For the diversified TSMOM portfolio, a target annualized volatility of 40% is used to scale the aggregate portfolio — meaning the weights $w_{i,t}$ are further scaled so that the predicted portfolio volatility equals 40% per annum.

**Key insight:** The signal is purely time-series (comparing the asset to itself). It does not require ranking assets against each other. This means the signal can be applied to a single asset in isolation.

---

## TSMOM vs Cross-Sectional Momentum

**Cross-sectional momentum (CS-MOM, Jegadeesh-Titman 1993):** Goes long the top decile and short the bottom decile of stocks ranked by past 12-month return within a universe. The signal is a relative ranking.

**Time-series momentum (TSMOM):** Goes long any asset with a positive past 12-month return, short any with a negative past 12-month return. The signal is absolute direction.

| Dimension | TSMOM | CS-MOM |
|---|---|---|
| Signal | Own past return sign | Rank within universe |
| Asset coverage | Any single tradeable asset | Requires a ranked universe |
| Correlation | ~0.50 with UMD | — |
| Crisis alpha | Strong positive (long/short) | Negative in crashes (long crashes) |
| Market exposure | Can be net long or short | Dollar-neutral by construction |
| Diversification | Cross-asset diversification | Within-asset-class |

**When they diverge:**
- If all assets in the universe are declining (bear market), CS-MOM is still long the least-bad stocks while TSMOM goes short everything. CS-MOM therefore suffers in bear markets; TSMOM does not by construction.
- In a recovery after a crash, CS-MOM benefits from mean reversion within the cross-section; TSMOM may be slow to flip direction.
- The correlation of ~0.50 implies they share approximately 25% of return variance — related but meaningfully distinct.

**Decomposition:** Moskowitz et al. show that CS-MOM can be decomposed into a TSMOM component and a cross-sectional dispersion component. The TSMOM component is what drives CS-MOM's performance during trending markets.

---

## Crisis Alpha Properties

**The core finding:** TSMOM has a convex, option-like payoff profile relative to equity markets. In normal trending environments TSMOM participates in upside because it is long rising assets. Its defining property is what happens during crashes: equity indices enter persistent downtrends, so TSMOM builds short equity exposure. Bonds and safe-haven currencies simultaneously trend up as capital flows to safety. The combined effect is a large positive TSMOM return precisely when equity-only portfolios suffer most.

**2008–2009 financial crisis:** The TSMOM portfolio delivered approximately +18% in 2008 on a 40%-vol-target basis, while global equity indices fell ~40–50%. This is the clearest illustration of crisis alpha in the paper. By mid-2008, commodity and equity futures had already established persistent downtrends, putting TSMOM short those positions before the acute phase of the crisis.

**Worst equity month deciles:** Sorting months by equity market return, TSMOM's average return in the worst decile of equity months is approximately +0.5% per month. In the best equity months it is slightly negative (roughly -0.1%). This nonlinear, crisis-positive payoff profile resembles long optionality.

**Mechanism for crisis alpha:**
1. Trends in futures markets build slowly (anchoring, gradual information diffusion).
2. During crises, trends accelerate and persist for months as forced selling cascades through markets.
3. TSMOM is positioned in the direction of the prevailing trend before the crisis peak, generating profits as the trend continues.
4. This is structurally different from options-based tail hedges, which require paying premium continuously.

**Post-crisis reversal risk:** Once trends reverse (e.g., equity market recovery in 2009 Q2), TSMOM can suffer drawdowns. The 12-month signal is slow to rotate from short to long. This is the primary source of left-tail risk for TSMOM strategies.

---

## Connection to CTA / Trend-Following

**CTA return explanation:** The authors regress major CTA index returns (BTOP50, BarclayHedge CTA Index) and the Fung-Hsieh (2001) trend-following factor (PTFSBD, PTFSFX, PTFSCOM) on the TSMOM portfolio return. Key results:
- TSMOM alone explains **50–75% of CTA return variation** (R² range across specifications and index choices).
- The TSMOM loading is highly significant (t-stats typically >5).
- The intercept (unexplained alpha beyond TSMOM) is close to zero and insignificant for most CTA indices.

**Fung-Hsieh trend factor:** The Fung-Hsieh (2001) primitive trend-following factors are constructed from lookback straddle payoffs on bonds, currencies, and commodities. These are meant to capture the option-like payoff of trend-following. TSMOM is a simpler, more direct construction that produces similar empirical properties:
- Both have the convex, crisis-alpha payoff shape.
- TSMOM has slightly higher explanatory power because it is more precisely calibrated to actual CTA exposures across all four asset classes.
- TSMOM is a cleaner research construct: no need to model straddle prices or implied vols.

**Implication:** A researcher or allocator who wants CTA-like exposure without paying CTA fees can replicate the majority of CTA returns using a TSMOM strategy on 20–60 liquid futures contracts. The replication quality degrades when using fewer instruments or less liquid contracts.

**CTA dispersion not explained:** The remaining 25–50% of CTA return variation unexplained by TSMOM reflects: (a) idiosyncratic model differences (signal lookbacks, blending of short- and long-term signals), (b) discretionary overlays, (c) capacity constraints and execution differences, and (d) within-asset-class cross-sectional bets that some CTAs run.

---

## Failure Modes & Limitations

1. **Whipsaw / choppy markets:** TSMOM loses money when prices oscillate without sustained trends. A market that rises 6 months then falls 6 months triggers entries and exits at the worst times. This is the primary regime failure mode.
2. **Sharp trend reversals:** After a prolonged trend, rapid reversals hit TSMOM hard before the 12-month signal can flip. The 2009 equity recovery and the 2020 COVID recovery rebound are canonical examples from the post-sample period.
3. **Crowding:** As TSMOM/CTA strategies have grown in AUM, the strategy has become more crowded. Crowding amplifies reversal losses because many managers exit simultaneously when trends turn.
4. **Slow signal rotation:** The 12-month window means the signal contains 11 months of stale information. A sharp 2-month reversal barely moves the 12-month sum. This creates lag risk in fast-moving markets.
5. **Cost sensitivity in less liquid markets:** The strategy is viable in the 58 liquid futures studied. Extending to less liquid instruments substantially increases transaction costs and slippage.
6. **No fundamental anchor:** Unlike carry (where the forward rate provides a no-arbitrage anchor), TSMOM has no fundamental value it reverts to. This makes it harder to size positions with conviction.
7. **Sample period concerns:** The bulk of the out-of-sample record (equity index futures back to 1965) relies on a small number of markets in the early decades. The diversified results depend heavily on post-1985 data when the full 58-contract universe is available.
8. **Survivorship and backfill bias:** While the authors use liquid futures (less prone to survivorship), futures contracts themselves can be delisted; the lookback uses contracts with the longest available histories.

---

## Behavioral vs Risk Explanations

**Behavioral explanations (authors' preferred framing):**
- **Initial underreaction:** Investors anchor on prior prices, process information slowly, and are subject to herding delays. News diffuses gradually into prices, creating positive autocorrelation at short horizons.
- **Delayed overreaction:** Once a trend is established, feedback traders (trend followers, momentum chasers) pile in, pushing prices beyond fundamental value. This extends the trend beyond what fundamentals justify.
- **Eventual reversal:** The overreaction unwinds at 2–5 year horizons, producing the negative autocorrelation observed at longer lags. This is consistent with De Bondt-Thaler long-term reversal.
- **Disposition effect:** Investors hold losers too long and sell winners too early, creating supply/demand imbalances that sustain trends.

**Risk-based explanations (the authors consider but find insufficient):**
- TSMOM alphas survive controls for CAPM beta, Fama-French 3 factors, and Carhart 4 factors. The alpha is not explained by standard systematic risk exposures.
- Time-varying risk: One could argue TSMOM loads on distress risk or liquidity risk. But the crisis alpha (positive returns in the worst equity months) is the opposite of what a distress risk story would predict — distressed risk premiums should be *negative* in crises.
- The authors do not fully resolve the behavioral vs. risk debate, which remains open in the literature.

**AQR follow-up work (Asness, Moskowitz, Pedersen 2013):** Finds that value and momentum are negatively correlated across asset classes, consistent with a shared behavioral mechanism. Momentum's crash risk is largely the mirror of value's crisis outperformance.

---

## Connection to Ilmanen (Expected Returns 2011)

**Chapter 14 — Momentum:** Ilmanen treats momentum as one of the three core return sources alongside carry and value. His framing aligns closely with this paper:
- Momentum is presented as a behavioral premium — a compensation for being on the other side of investors who underreact and then overreact.
- Ilmanen emphasizes the cross-asset universality of momentum, directly anticipating (or summarizing early versions of) Moskowitz et al.
- He notes that time-series momentum is particularly useful in multi-asset contexts because it does not require a cross-sectional ranking — you can apply it to a single asset.
- Ilmanen's treatment of lookback windows (12-month standard, robustness across 3–12 months) matches the empirical findings here.

**Chapter 18 — Tail Risk / Crisis Alpha:**
- Ilmanen discusses the convex payoff profile of trend-following strategies in the context of tail risk hedging.
- He frames managed futures / CTA allocations as "cheap optionality" — they provide positive skew and crisis protection without requiring explicit premium payments (unlike put options).
- The Moskowitz et al. paper is the quantitative backbone of this claim: TSMOM's crisis alpha is documented across 44 years and four asset classes.
- Ilmanen connects TSMOM's crisis alpha to the autocorrelation structure: crises are not instantaneous jumps but multi-month trends (the 2008 drawdown took ~15 months), which is exactly the regime where a 12-month trend signal performs best.
- **Key tension Ilmanen identifies:** TSMOM is not pure tail insurance — it can lose in fast-crash-and-recover episodes (e.g., 1987 crash, 2020 COVID). Pure optionality hedges would not suffer this; TSMOM does.

---

## Implementability for This Team

**Futures data required:** The paper uses 58 liquid futures. Minimum viable replication requires:

| Asset Class | Key Contracts | Approximate Count |
|---|---|---|
| Equity indices | S&P 500, NASDAQ, Russell 2000, EuroStoxx, FTSE, Nikkei, Hang Seng | 7–10 |
| Government bonds | US 2yr, 5yr, 10yr, 30yr; Bund, Gilt, JGB | 6–8 |
| Currencies | EUR, GBP, JPY, AUD, CAD, CHF, SEK vs USD | 6–8 |
| Commodities | WTI crude, Brent, natural gas, gold, silver, copper, corn, soybeans, wheat | 8–12 |

**Without futures — ETF approximation:**
For a team without futures access (our current situation), TSMOM can be approximated using ETFs:
- Equity index trend: SPY, QQQ, IWM, EFA, EEM — apply 12-month return sign, long/short via inverse ETFs or underweighting.
- Bonds: TLT, IEF, SHY for duration; HYG, LQD for credit spread.
- Commodities: GLD, SLV, USO, DBA, PDBC.
- Currencies: FXE, FXB, FXY, FXA, FXC.
- **Key limitation:** ETFs cannot be shorted as easily as futures; margin requirements differ; no roll yield; transaction costs higher per unit of exposure. The signal is the same but execution is less clean.

**Vol-targeting implementation:** Ex-ante volatility can be estimated with a 1-month or 3-month exponentially weighted standard deviation of daily returns. Target 10–15% annualized for a multi-asset ETF portfolio (not 40% as in the paper, which uses leverage).

**Data sources available in this repo:**
- `data/market_data/prices/equities.parquet` — equity price history
- `quant_data/connectors/` — Stooq, Polygon, ECB FX connectors
- SPY, VIX data already in `data/market_data/prices/`
- Missing: commodity futures, bond futures, currency forwards — would need Polygon futures or broker API

**Minimum viable test:** Apply TSMOM to SPY, TLT, GLD, UUP (USD index ETF) as a 4-asset proof of concept using existing data. This captures equity/bond/commodity/FX in a minimal universe.

---

## Key Quotes

> "We find strong time series momentum in equity index, currency, commodity, and bond futures for each of the 58 liquid instruments we study... Every asset class we examine exhibits positive average time series momentum profits."

> "Time series momentum is related to, but distinct from, the cross-sectional momentum of Jegadeesh and Titman (1993). The correlation between TSMOM and cross-sectional momentum is about 0.5."

> "TSMOM exhibits the largest average returns during the most extreme market environments — large positive returns when equity markets experience large losses and large positive returns when equity markets experience large gains."

> "A portfolio of TSMOM strategies can explain between 50 and 75 percent of the return variation of CTA indices."

> "The 12-month return predicts positively the next month return, while 2- to 5-year returns predict negatively, consistent with initial underreaction followed by delayed overreaction and eventual correction."

> "Position sizes are determined by the sign of the past 12-month return, scaled by the inverse of the instrument's volatility, so that each position contributes equal risk to the portfolio."

---

## Follow-Up Papers

1. **Asness, Moskowitz, Pedersen (2013)** — "Value and Momentum Everywhere." Extends momentum (and value) to stocks, bonds, FX, and commodities cross-sectionally; documents negative value-momentum correlation. *JF.*
2. **Hurst, Ooi, Pedersen (2017)** — "A Century of Evidence on Trend-Following Investing." Extends TSMOM back to 1880 across four asset classes; confirms crisis alpha in WWI, WWII, Great Depression. *Journal of Portfolio Management.*
3. **Barroso, Santa-Clara (2015)** — "Momentum Has Its Moments." Documents that momentum crash risk can be managed by scaling exposure by predicted variance. Directly applicable to TSMOM vol-targeting.
4. **Daniel, Moskowitz (2016)** — "Momentum Crashes." Studies the mechanism of momentum crashes post-bear-markets; shows option-like exposure to market rebounds.
5. **Fung, Hsieh (2001)** — "The Risk in Hedge Fund Strategies: Theory and Evidence from Trend Followers." Original trend-following factor construction using lookback straddles.
6. **Jegadeesh, Titman (1993)** — "Returns to Buying Winners and Selling Losers." The cross-sectional momentum benchmark; essential contrast paper.
7. **Baz, Granger, Harvey, Le Roux, Rattray (2015)** — "Dissecting Investment Strategies in the Cross Section and Time Series." AQR practitioners' guide to combining TSMOM and CS-MOM.
8. **Lim, Nguyen, Nguyen (2020+)** — Various papers on TSMOM with alternative signal specifications (binary vs. continuous signals, different lookbacks).
