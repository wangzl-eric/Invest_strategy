# Paper Notes: "Hedge Fund Benchmarks: A Risk-Based Approach" — Fung & Hsieh (2004)

**Citation:** Fung, W., Hsieh, D. (2004). Hedge Fund Benchmarks: A Risk-Based Approach. *Financial Analysts Journal*, 60(5), 65–80.
**DOI:** 10.2469/faj.v60.n5.2657
**Scores:** C:5 / R:5 / A:4

---

## Core Thesis

Hedge fund returns — including global macro — can be largely explained by a small set of systematic risk factors: equity market, bond market, credit spread, and three trend-following (lookback straddle) factors across equities, bonds, and currencies/commodities. Alpha net of these factors is small and concentrated.

---

## Key Findings

- **7-factor model explains ~80% of hedge fund index returns:** Equity market factor, bond factor, credit spread, plus three trend-following factors (bond TSMOM, equity TSMOM, FX/commodity TSMOM).
- **Trend-following factors are option-like:** Lookback straddle payoffs (long the best trend, short the worst) capture the non-linear return profile of CTA/trend strategies.
- **Global macro returns are ~70% systematic:** The 7-factor model explains most macro fund returns; idiosyncratic alpha is modest after factor adjustment.
- **Implication for allocation:** Investors paying 2-and-20 for macro hedge funds are largely buying systematic factor exposure — much of which can be replicated cheaply.
- **Style consistency:** Global macro funds have more variable factor loadings than equity long-short — consistent with Gliner's discretionary, theme-driven approach.

---

## Connection to Gliner (GMT)

- **Ch1 (macro landscape):** Provides quantitative context for where macro fund returns actually come from — validates Gliner's multi-asset, trend+carry framework.
- **Ch6 (systematic trading):** The 7 factors are a direct decomposition of the systematic premia Gliner describes.
- **Ch2 (risk management):** Factor exposures define the risk budget — useful for stress-testing a macro portfolio.

---

## Implementation Notes

- Use 7-factor model as a benchmark to evaluate any macro strategy — alpha net of factors is the true value-add.
- The three trend-following factors are replicable with TSMOM signals on equity index, bond, and FX futures.
- Credit spread factor: IG−Treasury spread (FRED: BAMLC0A0CMEY minus 10Y Treasury yield).

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*