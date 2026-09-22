# Paper Notes: Value and Momentum Everywhere

**Authors:** Asness, Clifford S.; Moskowitz, Tobias J.; Pedersen, Lasse Heje
**Year:** 2013 | **Journal:** Journal of Finance, 68(3), 929–985
**DOI:** 10.1111/jofi.12021
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

> **Canonical merged note.** Surfaced while studying *Expected Returns* (Ilmanen) and
> *Global Macro Trading* (Gliner). Per-book connection tables preserved under
> **Cross-Book Context**. The companion paper "Currency Value" (Asness et al. 2013) is a
> **separate** note: `paper_notes_asness2013_fx.md`. Linked from each book's `reading_queue.md`.

---

## Core Thesis

Value and momentum premia are pervasive across eight diverse asset classes — individual
stocks (US, UK, Europe, Japan), equity indices, government bonds, currencies, and commodity
futures — and cannot be dismissed as data-mined artefacts of a single market. The two
strategies are negatively correlated with each other (~−0.50), so a 50/50 combination produces
a composite with a Sharpe ratio materially higher than either factor alone. Co-movement of
value and momentum *across* asset classes points to a common underlying factor, with
**funding-liquidity risk** (the Asness-Frazzini-Pedersen AMP factor) the most compelling
risk-based explanation.

---

## Key Findings

- **Coverage:** 8 asset classes — US/UK/Europe/Japan stocks, equity index futures, government
  bond futures, FX forwards, commodity futures. Sample 1972–2011 (length varies by class).
- **Sharpe ratios (long-short, after costs):** momentum-only composite ~0.65–0.73; value-only
  ~0.53–0.61; **50/50 value+momentum composite ~1.00–1.13** (roughly double either alone).
- **Within-asset-class value-momentum correlation:** ≈ −0.49 on average.
- **Across-asset-class co-movement:** value strategies co-move across classes; momentum
  co-moves across classes — *not* explained by equity-market beta, bond beta, or FX risk.
- **Funding liquidity (AMP):** innovations to a funding-liquidity proxy (TED spread,
  broker-dealer leverage) significantly explain the co-movement. Liquidity shocks hit momentum
  positively and value negatively, consistent with the negative correlation.
- **Costs:** value is cheaper to trade (slower turnover); both survive realistic costs.
- **Spanning:** value/momentum in each class stay significant after controlling for value/
  momentum in all other classes — partially independent sources of return.

---

## Methodology

- **Data:** Datastream/Bloomberg futures & forwards; CRSP (US) + Datastream (international)
  stocks; commodity futures from various exchanges; bond futures from Bloomberg.
- **Sample:** US stocks from 1972 (intl from 1984); index futures 1978–2011; FX forwards
  1979–2011; bond futures 1983–2011; commodities 1972–2011.
- **Formation:** monthly rebalance, sort within each class into terciles (quintiles for single
  stocks), long top / short bottom, value-weighted within buckets, excess over T-bill (USD).
- **Combination:** 50/50 equal-vol blend of value & momentum within each class; further
  equal-vol combination across all eight classes → global composite.
- **Costs:** bid-ask + price-impact models; equity momentum ~1–2% p.a., less in futures.

---

## Signal Construction

- **Single stocks (US/UK/EU/JP):** Value = book-to-market (FF HML style); Momentum =
  cumulative return $t-12$ to $t-2$ (skip last month; JT UMD style).
- **Equity index futures:** Value = negative past 5-year log return (contrarian price signal);
  Momentum = 12-1.
- **Government bond futures:** Value = 10y yield − 5-year trailing-inflation average (real-yield
  proxy); Momentum = 12-1.
- **FX forwards:** Value = negative past 5-year log spot change (PPP-inspired contrarian);
  Momentum = 12-1 spot return.
- **Commodity futures:** Value = negative past 5-year log return; Momentum = 12-1.

**Note:** for all non-equity classes, value is a *long-run mean-reversion signal* (5-year
return reversed), not a fundamental-to-price ratio — a practical compromise the authors flag.

---

## What This Adds Beyond Jegadeesh-Titman / Fama-French

| Prior Work | Limitation | This Paper's Extension |
|---|---|---|
| Jegadeesh & Titman (1993) | US stocks only | Momentum to 7 more classes + 3 non-US stock markets |
| Fama & French (1992, 1996) | US stocks; value/momentum separate | Both jointly; documents global negative correlation |
| Rouwenhorst (1998) | International equity momentum | Extends to bonds, FX, commodities |
| Asness (1997) | Value & momentum in US stocks | Same relationship holds universally |
| Carhart (1997) | Four-factor (US equity) | Momentum is a global multi-asset phenomenon |

Single most important contribution: the **co-movement result** — value across classes moves
together, momentum across classes moves together, even after controlling for common factors —
implying a *common global factor* prior single-class work could not detect.

---

## Behavioral vs Risk Explanations

1. **Risk-based.** CAPM/SMB/HML/bond/FX factors do *not* explain the cross-asset co-movement.
   **Funding-liquidity risk (AMP):** leveraged arbitrageurs hold value-long/momentum-long; when
   funding tightens they unwind both → correlated losses (Brunnermeier–Pedersen 2009 spiral).
   The most promising rational explanation, though it doesn't fully span returns.
2. **Behavioral.** Value = overreaction correction; momentum = underreaction continuation. The
   negative value-momentum correlation falls out naturally (assets that fell far become cheap
   exactly when recent momentum is negative).
3. **Data mining / chance:** strongly rejected — same signals across 8 independent classes over
   four decades; coordinated global co-movement defeats factor-zoo criticism.

**Conclusion:** both behavioral and liquidity-risk mechanisms likely operate; the negative
value-momentum correlation is robust regardless of explanation.

---

## Failure Modes & Limitations

- **Momentum crashes:** severe drawdowns in sharp reversals (2001, 2009); crowded positions
  unwind fast in liquidity crises — acknowledged, not fully resolved.
- **Value drawdowns:** long underperformance when growth/quality is bid up (late-1990s bubble);
  the 5-year reversal proxy may capture trend, not true cheapness.
- **Momentum transaction costs:** turnover-intensive in single equities (~1–2% p.a.); survives,
  but thinner margin than gross.
- **Crowding risk:** the liquidity explanation implies the strategy is most exposed precisely
  when it matters most.
- **Look-back choice:** 12-1 momentum, 5-year value applied universally — somewhat arbitrary,
  possibly partly in-sample.
- **Non-stock value is a price signal:** the 5-year reversal proxy conflates value with long-run
  mean reversion.
- **Survivorship/backfill:** early international stock databases may be contaminated.
- **Post-2011:** crowding + fee compression eroded gross premia; 2010–2020 was unkind to value.

---

## Implementability for This Team

**Feasible now:** US equity momentum (12-1, Stooq/Alpaca); equity index momentum (SPY + EWJ/
EWG/EWU proxies); FX momentum (ECB FX connector); FX value (5-year reversal, ECB FX, ≥5y
history available); commodity value+momentum (5-year reversal, Stooq, partial).

**Needs more data:** single-stock value (B/M — no fundamentals pipeline; needs Compustat/Polygon/
Tiingo); government-bond value (real yield by country — FRED TIPS proxy for US only); clean
futures rolls (commodity/bond — dedicated futures feed).

**Main obstacles:** no fundamentals pipeline for B/M; no futures-roll data; <5y history blocks
the value signal for recent additions.

**Recommended entry point:** **FX momentum + FX value (5-year reversal)** — ECB FX already
ingested, mechanical signal, directly supports the FX Carry + Momentum priority. Equity index
momentum is the easy second add.

---

## Cross-Book Context

**Connections to Expected Returns (Ilmanen) chapters**

| Chapter | Connection |
|---|---|
| Ch12 — Value | Strong support for value as a multi-asset phenomenon; B/M + 5-year reversal map to Ilmanen's value taxonomy |
| Ch13 — Carry | FX carry and FX value (PPP) overlap: high-rate currencies tend to have depreciated over 5 years |
| Ch14 — Momentum | Definitive multi-asset extension; 12-1 = Ilmanen's standard construction; informs the global momentum factor |
| Ch17 — Combining Strategies | Combining negatively-correlated value+momentum ~50/50 ≈ doubles Sharpe — the empirical foundation for multi-strategy diversification |
| Ch6 — Crash Risk & Liquidity | AMP funding-liquidity link connects to liquidity risk as a priced systematic factor |

**Connections to Global Macro Trading (Gliner) chapters**

| Chapter | Connection |
|---|---|
| Ch4 — Building blocks | Value and momentum are the two most fundamental cross-asset signals underlying discretionary macro |
| Ch5 — Technical analysis | Momentum is the quantitative formalization of Gliner's trend-following discussion |
| Ch6 — Systematic trading | Combined value-momentum is the backbone of any multi-asset systematic factor approach |
| Ch7–10 — Asset classes | Each class has its own value & momentum signal with consistent positive premia |

---

## Key Quotes

> "Value and momentum ubiquitously generate abnormal returns across diverse asset classes and
> markets, and their co-movement and correlation structure present a puzzle to existing models."

> "A funding liquidity risk factor captures a significant part of the common variation in value
> and momentum strategies across all asset classes and markets."

---

## Follow-Up Papers

1. Asness, Frazzini & Pedersen (2013) — **Quality Minus Junk** (extends the framework to quality).
2. Brunnermeier & Pedersen (2009) — **Market Liquidity and Funding Liquidity** (AMP spiral theory).
3. Israel & Moskowitz (2013) — **Shorting, Firm Size, and Time Horizon in Momentum** (cost-aware robustness).

## Citation

Asness, C. S., Moskowitz, T. J., & Pedersen, L. H. (2013). Value and Momentum Everywhere.
*Journal of Finance*, 68(3), 929–985.
