# Paper Notes: Value and Momentum Everywhere
**Authors:** Asness, Clifford S.; Moskowitz, Tobias J.; Pedersen, Lasse Heje
**Year:** 2013 | **Journal:** Journal of Finance, Vol. 68, No. 3
**Date Read:** 2026-03-29
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

---

## Core Thesis

Value and momentum premia are pervasive across eight diverse asset classes — individual stocks (US, UK, Europe, Japan), equity indices, government bonds, currencies, and commodity futures — and cannot be dismissed as data-mined artefacts of a single market. The two strategies are negatively correlated with each other (~−0.50), so combining them in a 50/50 portfolio produces a diversified composite with a Sharpe ratio materially higher than either factor alone. Co-movement of value and momentum *across* asset classes points to a common underlying factor, with funding-liquidity risk (the Asness-Frazzini-Pedersen AMP factor) providing the most compelling risk-based explanation for the co-movement.

---

## Key Findings

- **Coverage:** 8 asset classes tested: US stocks, UK stocks, European stocks, Japanese stocks, equity index futures, government bond futures, FX forward contracts, commodity futures. Sample spans 1972–2011 (length varies by asset class).
- **Sharpe ratios (approximate, long-short, after costs):**
  - Momentum-only composite across all asset classes: ~0.65–0.73
  - Value-only composite across all asset classes: ~0.53–0.61
  - 50/50 value+momentum composite: ~1.00–1.13 (roughly double either alone)
- **Within-asset-class value-momentum correlation:** approximately −0.49 on average across all markets tested.
- **Across-asset-class co-movement:** value strategies in different asset classes are positively correlated with each other; same for momentum. This co-movement is *not* explained by standard equity market beta, bond beta, or currency risk.
- **Funding liquidity (AMP factor):** co-movement of value and momentum returns across asset classes is significantly explained by an innovation to a funding-liquidity proxy (TED spread, broker-dealer leverage). Liquidity shocks hit momentum positively and value negatively, consistent with the negative correlation.
- **Transaction costs:** value is cheaper to trade than momentum (slower turnover). Even after realistic transaction costs, both strategies remain significantly profitable.
- **Individual stock results:** four separate equity markets (US, UK, Europe, Japan) all show significant value and momentum premia individually; momentum somewhat stronger than value in gross terms.
- **Non-stock assets:** value and momentum premia in equity indices, bonds, FX, and commodities are of comparable magnitude to stock-level results, which is a key novel finding relative to prior literature.
- **Factor spanning tests:** value and momentum in each asset class remain significant after controlling for value and momentum in all other asset classes, suggesting partially independent sources of return.

---

## Methodology

- **Data:** Futures and forward prices from Datastream and Bloomberg; individual stock data from CRSP (US) and Datastream (international). Commodity futures from various exchanges. Government bond futures from Bloomberg.
- **Sample period:** Equity individual stocks back to 1972 (US) / 1984 (international); equity index futures 1978–2011; FX forwards 1979–2011; government bond futures 1983–2011; commodity futures 1972–2011.
- **Portfolio formation:** At each monthly rebalance date, assets within each class are sorted into terciles (or quintiles for individual stocks) based on the relevant value and momentum signals. Long-short portfolios buy the top third and short the bottom third, value-weighted within buckets.
- **Return measurement:** Excess returns over a risk-free rate (T-bill). All returns are in USD for non-US assets (hedged and unhedged variants examined).
- **Combination:** A 50/50 equal-volatility-weighted blend of value and momentum within each asset class; a further combination across all eight asset classes forms the global composite.
- **Costs:** Transaction cost estimates are based on bid-ask spreads and price impact models; momentum strategies are estimated to cost ~1–2% per annum in equities and somewhat less in futures markets.

---

## Signal Construction

### Individual Stocks (US, UK, Europe, Japan)
- **Value:** Book-to-market ratio (B/M), where book equity is the most recent annual figure and market equity is the prior month-end price. Matches Fama-French HML construction.
- **Momentum:** Cumulative gross return from month $t-12$ to $t-2$ (i.e., skipping the most recent month to avoid short-term reversal). Matches Jegadeesh-Titman UMD construction.

### Equity Index Futures
- **Value:** The negative of the past 5-year log return of the equity index (i.e., a *contrarian* price signal — markets that have underperformed over 5 years are considered cheap). Rationale: in the absence of reliable cross-country B/M data, long-run price reversion proxies for cheapness.
- **Momentum:** Past 12-month return (skipping last month), same as stock-level.

### Government Bond Futures
- **Value:** The 10-year bond yield minus a 5-year average of the trailing inflation rate (i.e., a real-yield proxy). Higher real yield = cheaper bond.
- **Momentum:** Past 12-month return on the bond futures contract (skipping last month).

### Foreign Exchange Forwards
- **Value:** Negative of the past 5-year log change in the nominal spot exchange rate (PPP-inspired contrarian signal — currencies that have appreciated a lot over 5 years are expensive).
- **Momentum:** Past 12-month spot return of the currency (skipping last month).

### Commodity Futures
- **Value:** Negative of the past 5-year log return of the commodity futures contract (same contrarian price approach as equity indices and FX).
- **Momentum:** Past 12-month return on the futures contract (skipping last month).

**Note:** For all non-equity asset classes, value is operationalized as a *long-run mean-reversion signal* (past 5-year return reversed), not a fundamental-to-price ratio. The authors acknowledge this is a practical compromise and test whether it captures the same underlying phenomenon.

---

## What This Adds Beyond Jegadeesh-Titman / Fama-French

| Prior Work | Limitation | This Paper's Extension |
|---|---|---|
| Jegadeesh & Titman (1993) | US stocks only | Extends momentum to 7 additional asset classes and 3 non-US stock markets |
| Fama & French (1992, 1996) | US stocks only; value and momentum tested separately | Tests both signals jointly; documents their negative correlation globally |
| Rouwenhorst (1998) | International equity momentum | Extends to non-equity assets (bonds, FX, commodities) |
| Asness (1997) | Value and momentum in US stocks | Demonstrates same relationship holds universally across asset classes |
| Carhart (1997) | Four-factor model (US equities) | Shows momentum is not a US equity artifact — it is a global multi-asset phenomenon |

The single most important new contribution is the **co-movement result**: value strategies across different asset classes move together, and momentum strategies across different asset classes move together, even after controlling for common equity and macro factors. This strongly implies a *common factor* driving both premia globally — something prior single-asset-class work could not have detected.

---

## Failure Modes & Limitations

- **Momentum crashes:** Momentum is subject to severe drawdowns during sharp market reversals (e.g., 2001 and 2009). During liquidity crises, crowded momentum positions unwind rapidly. The authors acknowledge this but do not fully resolve it.
- **Value drawdowns:** Value can underperform for extended periods when growth/quality stocks are bid up (e.g., late 1990s tech bubble). The 5-year reversal signal for non-stock assets may capture trend rather than true fundamental cheapness.
- **Transaction costs for momentum:** Momentum in individual equities is turnover-intensive and cost-sensitive. The authors show it survives but the margin is thinner than gross returns suggest.
- **Crowding risk:** If many investors use the same signals, co-movement amplifies and the premium may compress. The liquidity-risk explanation implies crowding is the mechanism — meaning the strategy is most exposed precisely when it matters most.
- **Look-back window choice:** The paper uses 12-1 momentum and 5-year value universally. These are somewhat arbitrary and may be in-sample optimized to some degree.
- **Value signal for non-stocks is a price signal:** The 5-year reversal proxy for FX, bonds, and commodities is theoretically weaker than a fundamental-to-price ratio. It conflates value with long-run mean reversion.
- **Survivorship and backfill bias:** Futures and FX data are relatively clean, but individual stock databases (especially international) may have some survivorship contamination in early periods.
- **The sample ends in 2011:** Factor crowding and fee compression since 2013 have likely eroded gross premia, particularly in equities.

---

## Behavioral vs Risk Explanations

The authors evaluate three categories of explanation:

### 1. Risk-Based
- Standard CAPM beta, SMB, HML, and bond/FX risk factors do *not* explain the cross-asset co-movement.
- **Funding liquidity risk (AMP factor):** Innovations to a proxy for funding conditions (TED spread + broker-dealer leverage) explain a significant portion of the co-movement. The intuition: leveraged arbitrageurs hold value long / momentum long; when funding tightens, they are forced to unwind both, creating correlated losses. This is consistent with Brunnermeier & Pedersen (2009) market-liquidity/funding-liquidity spiral theory.
- The authors view liquidity risk as the *most promising* rational explanation, though it does not fully span the returns.

### 2. Behavioral
- **Value = overreaction correction:** Investors overreact to long-run fundamental deterioration and push prices too low; subsequent mean reversion generates value premia.
- **Momentum = underreaction continuation:** Investors underreact to news in the short-to-medium run (anchoring, slow diffusion of information); prices continue drifting in the direction of the signal before eventually correcting.
- The negative correlation between value and momentum is naturally explained behaviorally: assets that have fallen far in price become cheap (value) precisely when recent momentum is negative, so the two signals mechanically oppose each other at the individual-asset level.

### 3. Data Mining / Chance
- The authors strongly reject this: the same signals work across eight independently-constructed asset classes spanning four decades. The probability of this pattern arising by chance is negligible.
- The co-movement across asset classes is a particularly powerful out-of-sample test — factor zoo criticism cannot explain coordinated global co-movement.

**Authors' conclusion:** Both behavioral and liquidity-risk mechanisms are likely operative. Neither alone is fully satisfying. The negative value-momentum correlation is robust regardless of explanation.

---

## Connection to Ilmanen (Expected Returns 2011)

| Ilmanen Chapter | Connection |
|---|---|
| **Ch. 12 — Value** | Directly supports Ilmanen's treatment of value as a multi-asset phenomenon. The B/M signal for equities and the 5-year reversal proxy for non-stocks map to Ilmanen's value taxonomy. The cross-asset evidence is among the strongest support for a universal value premium. |
| **Ch. 13 — Carry** | FX carry and FX value (PPP-based) overlap: high-interest-rate currencies tend to have depreciated over 5 years, scoring high on the reversal measure. Ilmanen's carry chapter acknowledges this overlap explicitly. |
| **Ch. 14 — Momentum** | The paper is the definitive multi-asset extension of the momentum literature Ilmanen surveys. The 12-1 signal used here is the same standard construction Ilmanen describes. The cross-asset co-movement result informs Ilmanen's discussion of a global momentum factor. |
| **Ch. 17 — Combining Strategies** | The core practical lesson — combining negatively correlated value and momentum at ~50/50 roughly doubles the Sharpe ratio — is the empirical foundation for Ilmanen's multi-strategy diversification argument. The composite Sharpe of ~1.0+ is a key reference point. |
| **Ch. 6 — Crash Risk & Liquidity** | The AMP funding-liquidity explanation connects to Ilmanen's treatment of liquidity risk as a systematic factor priced across assets. |

---

## Implementability for This Team

### What We Can Implement Now
- **Individual US equity momentum (12-1):** Fully feasible. Price data available via Stooq/Alpaca. Replicates the US stock momentum result directly.
- **Equity index momentum:** Feasible with SPY and international ETF proxies (EWJ, EWG, EWU) as stand-ins for futures. Signal construction is trivial.
- **FX momentum (major pairs):** Feasible using spot rates from ECB FX connector already in `quant_data/connectors/ecb_fx.py`. USD-base pairs available.
- **FX value (5-year reversal):** Feasible with ECB FX data — only requires 5+ years of spot rate history, which we have.
- **Commodity value + momentum (5-year reversal):** Partially feasible via Stooq commodity price history.

### What Requires Additional Data
- **Individual stock value (B/M):** Requires fundamental data (book equity). No current pipeline. Compustat or a fundamentals API (Polygon, Tiingo) needed.
- **Government bond value (real yield):** Requires 10-year yields by country + CPI series. FRED has US TIPS yield as a proxy; international requires additional sources.
- **Clean commodity futures rolls:** Actual futures roll mechanics require a dedicated futures data subscription (e.g., Quandl Continuous Futures, Refinitiv).

### Main Obstacles
- No fundamental data pipeline for B/M ratio — blocks full equity value replication.
- No futures roll data for clean commodity and bond futures return series.
- Short history for some assets in the Parquet store (< 5 years blocks value signal for recent additions).

### Recommended Entry Point
Start with **FX momentum + FX value (5-year reversal)** combination. ECB FX data is already ingested, signal construction is mechanical, and this directly supports the FX Carry + Momentum strategy (Priority 1 on the tracker). Equity index momentum is the second easiest addition.

---

## Failure Modes & Limitations

- **Momentum crashes:** Momentum is subject to severe drawdowns during sharp market reversals (e.g., 2001 and 2009). During liquidity crises, crowded momentum positions unwind rapidly. The authors acknowledge this but do not fully resolve it.
- **Value drawdowns:** Value can underperform for extended periods when growth/quality stocks are bid up (e.g., late 1990s tech bubble). The 5-year reversal signal for non-stock assets may capture trend rather than true fundamental cheapness.
- **Transaction costs for momentum:** Momentum in individual equities is turnover-intensive and cost-sensitive. The authors show it survives costs, but the margin is thinner than gross returns suggest; estimated at ~1–2% p.a. in equities.
- **Crowding risk:** If many investors use the same signals, co-movement amplifies and the premium may compress. The liquidity-risk explanation implies crowding is the mechanism — the strategy is most exposed precisely when it matters most.
- **Look-back window choice:** The paper uses 12-1 momentum and 5-year value universally. These are somewhat arbitrary and may be partially in-sample optimized.
- **Value signal for non-stocks is a price signal:** The 5-year reversal proxy for FX, bonds, and commodities is theoretically weaker than a fundamental-to-price ratio. It conflates value with long-run mean reversion.
- **Survivorship and backfill bias:** Futures and FX data are relatively clean, but individual stock databases (especially international) may have survivorship contamination in early periods.
- **Post-2011 evidence:** Factor crowding and fee compression since publication have eroded gross premia, particularly in equities. The decade 2010–2020 was notably unkind to value strategies globally.

---

## Key Quotes

> "Value and momentum ubiquitously generate abnormal returns across diverse asset classes and markets, and their co-movement and correlation structure present a puzzle to existing models."

> "The negative correlation between value and momentum within each asset class, and the positive correlation of each strategy across asset classes, present a set of stylized facts that any theory of these phenomena must explain."

> "A funding liquidity risk factor captures a significant part of the common variation in value and momentum strategies across all asset classes and markets, consistent with a liquidity-based explanation of these strategies."

---

## Follow-Up Papers

1. **Asness, Frazzini & Pedersen (2013) — "Quality Minus Junk"** — Extends the multi-asset factor framework to quality. Directly relevant to the Quality + Safe-Haven strategy (Priority 2 on the tracker).
2. **Brunnermeier & Pedersen (2009) — "Market Liquidity and Funding Liquidity"** — The theoretical foundation for the AMP liquidity spiral mechanism invoked here. Essential for understanding why value and momentum co-move during crises.
3. **Israel & Moskowitz (2013) — "The Role of Shorting, Firm Size, and Time Horizon in Long-Run Momentum"** — Tests robustness of momentum to implementation constraints; useful for cost-aware replication planning.