# Paper Notes: Volatility Risk Premia and the Cross-Section of Stock Returns

**Authors:** Cremers, Halling, Weinbaum
**Year:** 2015
**Journal:** Journal of Finance
**Date Read:** 2026-03-30
**Scores:** Credibility 4 | Relevance 4 | Actionability 4

---

## Core Thesis

Individual stock volatility risk premia (VRP) — the difference between option-implied volatility and realized volatility at the stock level — are systematically negative (investors overpay for options as insurance), and **cross-sectional variation in individual stock VRP predicts next-month returns**. Stocks with more negative VRP (expensive insurance) earn lower future returns; stocks with less negative or near-zero VRP earn higher returns. This is a distinct and additive effect to both the index-level VRP documented by Carr-Wu (2009) and the IVOL puzzle of Ang et al. (2006).

---

## Key Findings

- **Long-short return spread:** Stocks sorted on individual VRP (Q5 minus Q1, value-weighted) generate approximately **0.50–0.70% per month** in raw returns, with annualized **Sharpe ratios around 0.6–0.8**.
- **Factor-adjusted alpha:** Four-factor (Fama-French + Momentum) alpha is **~0.40–0.55% per month**, t-statistics of **3–4**. Survives Carhart four-factor, five-factor, and liquidity adjustments.
- **Direction:** Stocks with **more negative VRP** (IV >> RV, expensive options) earn **lower** future returns. The seller of insurance on these stocks is compensated; the buyer/holder suffers a return drag.
- **Persistence:** Predictability strongest at **one-month horizon**, decays over 3–6 months, essentially zero at six months. Consistent with limits-to-arbitrage and options market segmentation.
- **Robustness:** Holds across size quintiles (weakest in micro-caps), across bull/bear market regimes, after controlling for short-term reversal, bid-ask spreads, and options illiquidity.

---

## Methodology

**Sample:** OptionMetrics universe, approximately 1996–2010. Monthly frequency.

**Filters:** Positive open interest, moneyness within ±20%, minimum option volume, price > $5, minimum market cap.

**Portfolio sorts:** Univariate quintile sorts by VRP at end of each month, held one month. Fama-MacBeth cross-sectional regressions controlling for size, B/M, momentum, reversal, IVOL, beta, and liquidity.

**Liquidity screens are critical:** Illiquid options produce distorted IV estimates. The paper's filters remove a large fraction of the OptionMetrics universe — survivorship on options liquidity is a material constraint.


---

## Individual Stock VRP Construction

| Component | Specification |
|-----------|---------------|
| IV source | OptionMetrics (standardized implied vol surface) |
| Maturity | 30-day constant maturity (interpolated from the surface) |
| Moneyness | At-the-money (delta ~0.50 calls) |
| RV window | 22 trading days (trailing, daily log returns) |
| VRP definition | IV − RV (negative = expensive options) |
| Holding period | 1 month, rebalanced monthly |

**Key construction details:**
- The paper uses **call IV** (not put IV) to avoid the put-skew contaminating the VRP signal. Robustness checks use average of call and put IV; results are directionally stable.
- **Why ATM only:** Deep OTM options embed crash/tail risk premium (separate phenomenon); using ATM isolates the pure variance risk premium from skew and jump premia.
- The variance risk premium in this paper is measured in **volatility space** (not variance space), unlike Carr-Wu (2009) which uses variance swap conventions. The practical difference is small for short-dated options but material for longer maturities.

---

## Cross-Sectional Predictability

- **Direction:** More negative VRP → lower next-month return. Q1 (most negative VRP, most expensive options) = lowest returns; Q5 (least negative) = highest returns.
- **Economic magnitude:** ~0.50–0.70%/month gross spread (6–8% annualized). After realistic transaction costs, net alpha estimated at 3–5% annualized for institutional-scale portfolios.
- **Fama-MacBeth slope on VRP:** Positive (~0.05–0.10 per unit of volatility), t-stat > 3.0, after controlling for size, B/M, momentum, IVOL, and beta.
- **Persistence:** Strongest at 1-month, marginally significant at 3-month, essentially zero at 6-month. Consistent with slow arbitrage capital flows into the single-stock options market.
- **Nonlinearity:** Effect strongest in extreme quintiles. Middle quintiles show weak monotonicity, suggesting a threshold effect — the most mispriced options (extreme negative VRP) carry the most predictive content.


---

## How This Extends Carr-Wu (2009)

| Dimension | Carr-Wu (2009) | Cremers-Halling-Weinbaum (2015) |
|-----------|---------------|----------------------------------|
| Level of analysis | Index (S&P 500, aggregate) | Individual stocks (cross-section) |
| VRP definition | Variance swap rate − realized variance | ATM call IV − realized vol (stock level) |
| Prediction target | Time-series: does aggregate VRP predict market returns? | Cross-section: does stock VRP predict relative stock returns? |
| Main result | Aggregate VRP is a time-series predictor of index returns | Cross-sectional VRP spread predicts which stocks outperform |
| Mechanism | Compensation for systematic variance risk | Dispersion in insurance overpricing across individual stocks |

**What is genuinely new in CHW 2015:**
1. The analysis is entirely cross-sectional — it does not rely on time-series variation in aggregate VRP.
2. Even after removing the common (market-level) VRP component, **idiosyncratic VRP retains predictive power** for cross-sectional returns.
3. The paper provides evidence that option markets at the individual stock level contain incremental information not yet reflected in equity prices, even after controlling for aggregate VRP dynamics.
4. Extends the Carr-Wu finding from a macro timing signal to a stock selection signal — a categorically different use case.

---

## Common vs. Idiosyncratic VRP

The paper decomposes individual stock VRP into:
- **Common VRP component:** Projection of stock-level VRP onto market-level VRP (VIX² − realized market variance). This captures the Carr-Wu aggregate channel.
- **Idiosyncratic VRP component:** Residual stock-level VRP after removing the common component.

**Key finding:** Both components contribute to return predictability, but the **idiosyncratic VRP component is the dominant driver**.

Implications:
- The signal is not just a re-expression of aggregate VRP in disguise.
- Idiosyncratic VRP reflects stock-specific demand for insurance: earnings uncertainty, M&A event risk, concentrated ownership hedging needs.
- A pure idiosyncratic VRP factor (residualized against VIX) is cleaner and less correlated with macro regimes — more suitable as a standalone cross-sectional equity signal.
- Time-series VRP regime (high vs. low aggregate VRP) does not subsume the cross-sectional effect. The two signals are complementary.


---

## Connection to IVOL Puzzle (Ang et al. 2006)

Ang et al. (2006) document that **high idiosyncratic volatility stocks earn anomalously low returns** — the IVOL puzzle, widely replicated but poorly understood.

CHW (2015) directly asks: *Is individual VRP just IVOL in disguise?*

- **Correlation:** Individual VRP and IVOL are positively correlated (both larger for volatile stocks) but are not identical constructs.
- **Independent effects in regressions:** With both VRP and IVOL in Fama-MacBeth regressions, the VRP coefficient remains significant and of similar magnitude. IVOL loses significance in some (not all) specifications when VRP is included.
- **Interpretation offered:** The IVOL puzzle may partially be a manifestation of VRP. High-IVOL stocks tend to have more negative VRP (expensive options), and it is the **overpriced insurance** that depresses returns, not idiosyncratic volatility per se.
- **Not fully settled:** Some specifications retain both effects. CHW does not claim to fully explain the IVOL puzzle, only to show that VRP contains incremental and partially overlapping information.

**Practical implication for signal construction:** Use **VRP directly rather than IVOL** as the primary signal. VRP has a clearer theoretical mechanism (variance risk compensation), partially subsumes IVOL's effect, and avoids the lottery-demand interpretation that contaminates IVOL (see Hou & Loh 2016).

---

## Failure Modes & Limitations

1. **OptionMetrics dependency (critical):** The entire paper rests on standardized implied volatility from OptionMetrics ($35,000+/year license). No realistic substitute for individual stock IV at scale. This is the single largest barrier to implementation.
2. **Options liquidity:** The majority of single-stock options are illiquid or have wide bid-ask spreads. After applying CHW's own liquidity filters, the investable universe shrinks to roughly the top 500–800 stocks by market cap and options volume. The signal strength in micro/small-caps is unreliable due to wide bid-ask spreads distorting IV estimates.
3. **Transaction costs underestimated:** Monthly rebalancing of a quintile long-short strategy across hundreds of stocks incurs substantial costs. The paper's net alpha estimates use institutional cost assumptions and may not hold at smaller AUM.
4. **Options execution not modeled:** The paper documents a price-of-variance-risk signal derived from listed options prices — it does not require trading options. But harvesting the premium directly via delta-hedged straddles or variance swaps adds complexity and margin requirements far beyond a simple equity long-short.
5. **Short-sale constraints:** The alpha is concentrated in the short leg (high negative VRP = low return stocks). Short-borrow costs and crowding in that leg will erode net returns.
6. **Sample period concerns:** 1996–2010 includes the dotcom bubble and 2008 crisis — periods with extreme options mispricing that may flatter the backtest. Post-2010 out-of-sample performance is not documented in the paper.
7. **Survivorship in the options market:** Stocks that lose options liquidity mid-sample drop from the universe, creating a form of survivorship bias not fully addressed.

---

## Connection to Ilmanen Ch15 (VRP) and Ch12 (Value in Equity Selection)

**Chapter 15 (Volatility Risk Premium):**
Ilmanen treats VRP as a carry-like premium — compensation for bearing variance risk. CHW (2015) is a direct extension: while Ilmanen focuses on the aggregate VRP as a premium available to options sellers broadly, CHW shows that **cross-sectional dispersion in VRP is an equity selection signal**, not just an asset-class-level premium. The idiosyncratic VRP component maps precisely onto Ilmanen's framework of within-asset-class carry variation driving relative returns.

**Chapter 12 (Value in Equity Selection):**
Ilmanen discusses using options-derived signals as value indicators — stocks with expensive options (high IV relative to RV) may be "overvalued" in a risk-adjusted sense. CHW formalizes this: VRP directly measures how much the options market overprices insurance on each stock. Ilmanen would classify this as a **demand-pressure or sentiment signal** rather than pure fundamental value. The cross-sectional VRP effect is most naturally grouped with other demand-pressure anomalies (IVOL, skewness, lottery stocks).

**Synthesis:** CHW bridges the VRP-as-premium literature (Ch15) with the cross-sectional equity anomaly literature (Ch12), showing the same variance-risk-compensation mechanism operates at both the aggregate and individual stock level.

---

## Codebase Check

### Data Availability

| Dataset | Status | Notes |
|---------|--------|-------|
| `data/market_data/prices/equities.parquet` | Available | OHLCV equity prices — sufficient for RV computation |
| `data/market_data/prices/vix_daily.parquet` | Available | Aggregate VIX — proxy for market-level IV only |
| `data/market_data/prices/vix3m_daily.parquet` | Available | 3-month VIX — useful for term structure analysis |
| `data/market_data/prices/spy_ohlc.parquet` | Available | SPY OHLCV — market realized vol computation |
| Individual stock IV (OptionMetrics) | **NOT available** | Critical gap. No options data anywhere in the codebase. |
| Individual stock IV (free proxy) | **NOT available** | No yfinance options pull, no CBOE individual IV feed. |

### Signal Registry (`backtests/strategies/signals.py`)

Signals present: `MomentumSignal`, `CarrySignal`, `MeanReversionSignal`, `VolatilitySignal`, `ATRSignal`, `RSISignal`, `MACDSignal`, `BollingerPositionSignal`, `SMACrossoverSignal`, `VolumeSignal`.

**No VRP signal exists.** The `VolatilitySignal` computes historical realized volatility (contrarian — lower RV = higher expected return) with no implied volatility component. `ATRSignal` is a price-based volatility proxy. Neither is related to the options-derived individual stock VRP of CHW.

**Partial validation:** The existing `VolatilitySignal` direction (low RV → high return) is loosely consistent with the CHW finding that stocks with less negative VRP (where RV is closer to IV) earn higher returns. The signal is not equivalent but the direction is coherent.

### Runners (`backtests/runners/`)

`momentum.py` and `portfolio_opt.py` are present. No volatility-specific or options-based runner exists. No VRP cross-section runner.

### KNOWLEDGE_VOL.md — Existing VRP Entries

The KB already contains:
- VRP as a **crisis signal, not alpha signal** (from our rejected VIX Regime strategy)
- Carr-Wu (2009) cited under Key Papers
- **No entry for individual stock VRP cross-section (CHW 2015)**

The existing KB warns against VRP as standalone strategy based on our index-level experience. This does **not** contradict CHW — our rejection was of a time-series, index-level VRP overlay. CHW is a cross-sectional, stock-level equity selection signal. These are different use cases and the KB needs a clarifying entry to prevent future agents from incorrectly dismissing this signal.

### Options Data — Feasibility Assessment

| Source | Cost | Coverage | Verdict |
|--------|------|----------|---------|
| OptionMetrics | ~$35k+/yr | Full US options, standardized surface | Required for full replication; unavailable |
| CBOE DataShop | Per-dataset | Historical VIX products, limited single-stock | Index only — insufficient |
| yfinance options | Free | Live chain only, no historical IV surface | Not usable for backtesting |
| Polygon.io options | $79–$199/mo | Historical NBBO, no standardized IV surface | Possible but requires bespoke surface construction |
| WRDS/OptionMetrics (academic) | Free with access | Full standardized surface | Best path if academic credentials available |

**Bottom line:** Full CHW replication requires OptionMetrics or equivalent. A partial proxy (VIX as aggregate IV, idiosyncratic RV from equity prices) collapses to an IVOL-adjacent signal — not true individual stock VRP.

### Conflicts and Validations vs. Existing Codebase Work

**Conflict — KB framing risk:** `KNOWLEDGE_VOL.md` states `(none — VRP as standalone strategy rejected; crisis monitoring use-case possible)` under Confirmed Signals. This is accurate for index-level VRP but could mislead a future agent into dismissing the cross-sectional individual stock VRP signal. A clarifying KB entry is needed.

**Validation — VolatilitySignal direction:** Our existing `VolatilitySignal` (lower realized vol = higher expected return) is directionally consistent with CHW's finding. Not the same signal, but no directional conflict.

**Validation — IVOL topic in KB:** The `ivol` topic already notes that the IVOL short leg drives most of the long-short return and that large-cap-only universes attenuate the effect — consistent with CHW's findings about signal concentration in liquid, large-cap stocks.

**Gap — no options data pipeline:** Neither `quant_data/connectors/` nor any other module fetches individual stock implied volatility. This is the binding constraint for any implementation attempt.

---

## Suggested KNOWLEDGE_VOL.md Addition

Add under `## Topic: vrp`, `### Market Facts & Structural Observations`:

```
- DISTINGUISH index-level VRP time-series overlay (REJECTED, vix_regime strategy) from individual
  stock VRP cross-sectional sort (CHW 2015, unresolved — requires OptionMetrics). Different signals,
  different mechanisms. Do not dismiss cross-sectional VRP based on the index-level rejection.
  | [BOOK/ARTICLE: Cremers-Halling-Weinbaum 2015] | 2026-03-30
```

---

## Follow-Up Papers

| Paper | Authors | Year | Why Relevant |
|-------|---------|------|--------------|
| Variance Risk Premia in the Cross-Section | Driessen, Maenhout, Vilkov | 2009 | JoF | Correlation risk premium; extends VRP decomposition |
| Individual Equity Option Prices and Credit Spreads | Cao, Chen, Griffin | 2005 | JFQA | Options-implied information at stock level |
| The Information in Option Volume for Future Stock Prices | Pan & Poteshman | 2006 | RFS | Options order flow predicts stock returns — complementary signal |
| Expected Idiosyncratic Skewness | Boyer, Mitton, Vorkink | 2010 | RFS | Cross-sectional skewness premium; overlaps with VRP signal |
| Option-Implied Volatility Measures and Stock Return Predictability | Bali & Hovakimian | 2009 | JoB | Call-put IV spread as predictor — close relative of CHW signal |
| Implied Volatility Spreads and Expected Market Returns | Cremers & Weinbaum | 2010 | JFQA | Deviations from put-call parity predict individual stock returns |