# Goldman Sachs Strategy Ideas — Feasibility Assessment

**Date:** 2026-03-17
**Assessor:** PM (Portfolio Manager)
**Source:** Goldman Sachs Global Strategy Views (16 March 2026)

---

## Executive Summary

**Verdict:** 3 of 4 strategies are **REJECT** due to data/infrastructure gaps. 1 strategy (**Strategy 4: Quality + Safe-Haven**) is **P1** with conditional data requirements.

**Key Blockers:**
- No sector classification data (GICS/ICB)
- No geographic index data (MSCI Europe, TOPIX, MSCI EM)
- No quality factor data (ROE, debt/equity, earnings stability)
- No commodity spot data (gold, oil) — only ETF proxies available
- No futures infrastructure for JPY/CHF positioning

**Actionable Path Forward:** Focus on **Strategy 4** (Quality + Safe-Haven) using available proxies. Defer sector/geographic strategies until data pipeline expansion (P3+ priority).

---

## Strategy 1: Defensive Sector Rotation

### Description
- **Long:** Utilities, Staples, Healthcare (defensives)
- **Short/Underweight:** Industrials, Materials (cyclicals)
- **Rationale:** Cyclicals now as expensive as Defensives (rare historically)

### Feasibility Assessment

| Dimension | Status | Details |
|-----------|--------|---------|
| **Data Infrastructure** | ❌ **CRITICAL GAP** | No sector classification data (GICS/ICB). No sector ETF history beyond 2016 (Alpaca). Stooq has XLU/XLP/XLV/XLI/XLB but coverage gaps pre-2010. |
| **Execution Capabilities** | ✅ **AVAILABLE** | Can trade sector ETFs (XLU, XLP, XLV, XLI, XLB) via IBKR. Long/short execution supported. |
| **Conflicts** | ⚠️ **PARTIAL** | Overlaps with existing "Sector Rotation (Macro-Linked)" strategy (CONDITIONAL, Priority 4). GS version is valuation-driven, ours is macro-linked — different signals but same universe. |
| **Implementation Complexity** | **MEDIUM** | Requires: (1) sector ETF history stitching (Stooq + Alpaca), (2) valuation data (P/E, P/B by sector — not in current pipeline), (3) relative value signal construction. |

### Data Gaps
1. **Sector constituent data:** No point-in-time GICS/ICB classifications for individual stocks
2. **Sector valuation metrics:** No P/E, P/B, EV/EBITDA by sector (would need to compute from constituents or use sector ETF proxies)
3. **Historical depth:** Sector ETFs only exist since ~1998 (XLK) to ~2015 (XLRE). MinBTL for 15yr history = need Sharpe > 0.8 to pass statistical gates.

### Priority Recommendation
**REJECT** — Data infrastructure insufficient. Sector rotation requires either:
- Point-in-time constituent data ($5K+/yr from Norgate or FactSet), OR
- Sector ETF history with valuation overlays (requires FRED sector P/E data or manual construction)

**Alternative:** Wait for P3 data pipeline expansion (sector classification + valuation data). Current priority is FX Carry (P1) and CS Momentum (P3).

---

## Strategy 2: HALO Factor (High Asset, Low Obsolescence)

### Description
- **Long:** Physical assets, infrastructure, industrial capacity, power infrastructure
- **Rationale:** World under-invested in physical assets, AI capex driving demand

### Feasibility Assessment

| Dimension | Status | Details |
|-----------|--------|---------|
| **Data Infrastructure** | ❌ **CRITICAL GAP** | No "asset intensity" factor data. No infrastructure/industrial capacity classifications. Would require custom factor construction from balance sheet data (PP&E / Total Assets, Capex / Sales). |
| **Execution Capabilities** | ⚠️ **PARTIAL** | Can trade individual stocks or thematic ETFs (e.g., infrastructure ETFs like IGF, IFRA). No direct "HALO factor" ETF exists. |
| **Conflicts** | ✅ **NONE** | No overlap with existing strategies. |
| **Implementation Complexity** | **HIGH** | Requires: (1) fundamental data pipeline (balance sheets, cash flows), (2) custom factor construction, (3) universe definition (what qualifies as "high asset"?), (4) obsolescence scoring (subjective — AI risk, regulatory risk). |

### Data Gaps
1. **Fundamental data:** No balance sheet data (PP&E, Total Assets, Capex, Depreciation)
2. **Factor definition:** "Low Obsolescence" is qualitative — requires manual scoring or NLP on 10-Ks
3. **Universe:** Unclear if this is US-only or global (GS likely means global, we only have US equities)

### Priority Recommendation
**REJECT** — Requires fundamental data pipeline (not in current roadmap). Factor definition is vague and subjective. Even with data, backtesting would be challenging due to look-ahead bias in "obsolescence" scoring.

**Alternative:** If AI capex theme is compelling, consider thematic ETF basket (SOXX, SMH, XLI) as proxy. But this is sector bet, not factor strategy.

---

## Strategy 3: Geographic Rotation

### Description
- **Overweight:** Europe, Japan, EM
- **Underweight:** US
- **Rationale:** "New economy" growth favors non-US, asset-heavy businesses

### Feasibility Assessment

| Dimension | Status | Details |
|-----------|--------|---------|
| **Data Infrastructure** | ❌ **CRITICAL GAP** | No international equity data. No MSCI Europe, TOPIX, MSCI EM index data. No country ETF history (EWJ, EWG, VGK, EEM) in current pipeline. |
| **Execution Capabilities** | ❌ **NOT AVAILABLE** | IBKR account limited to US equities + FX spot. No international equity permissions. Cannot trade EWJ, EWG, VGK, EEM without account upgrade. |
| **Conflicts** | ✅ **NONE** | No overlap with existing strategies. |
| **Implementation Complexity** | **LOW** (if data/permissions available) | Simple geographic allocation. Could use country ETFs (EWJ, EWG, VGK, EEM, SPY) with momentum/value overlays. |

### Data Gaps
1. **International equity data:** No MSCI indices, no country ETF history
2. **IBKR permissions:** Account does not have international equity trading enabled
3. **FX hedging:** If trading international ETFs, need FX hedging logic (or accept currency risk)

### Priority Recommendation
**REJECT** — Infrastructure blocker. Cannot execute without:
1. IBKR account upgrade (international equity permissions)
2. Country ETF data ingestion (Stooq has EWJ/EWG/VGK/EEM — could add to pipeline)
3. FX hedging framework (if desired)

**Alternative:** Defer until IBKR account upgraded and P2 data pipeline includes country ETFs. Not a priority given existing US-focused strategy pipeline.

---

## Strategy 4: Quality + Safe-Haven Overlay

### Description
- **Long:** Quality stocks (high ROE, low debt, stable earnings)
- **Overlay:** Gold / Oil / JPY / CHF as geopolitical hedge
- **Rationale:** High valuations + deteriorating macro + geopolitical risks

### Feasibility Assessment

| Dimension | Status | Details |
|-----------|--------|---------|
| **Data Infrastructure** | ⚠️ **PARTIAL** | **Quality factor:** No ROE, debt/equity, earnings stability data (requires fundamental data pipeline). **Safe-haven assets:** Gold (GLD ETF ✅), Oil (USO ETF ✅), JPY (USDJPY FX ✅), CHF (USDCHF FX ✅). |
| **Execution Capabilities** | ⚠️ **PARTIAL** | Can trade: GLD, USO (ETFs), USDJPY, USDCHF (FX spot). Cannot trade: JPY/CHF futures (no futures infrastructure). Quality stock selection requires fundamental data. |
| **Conflicts** | ⚠️ **PARTIAL** | Overlaps with existing "Cross-Sectional Equity Momentum" (CONDITIONAL, Priority 3) — both are equity long strategies. Quality factor is orthogonal to momentum but universe overlaps. |
| **Implementation Complexity** | **MEDIUM** | Requires: (1) quality factor proxy (can use low-vol ETF like USMV as proxy, or construct from available data), (2) safe-haven allocation logic (fixed % or dynamic based on VIX/credit spreads), (3) rebalancing rules. |

### Data Gaps
1. **Quality factor data:** No fundamental data (ROE, debt/equity, earnings quality). **Workaround:** Use quality ETF (QUAL, USMV) as proxy.
2. **Commodity spot prices:** Only have ETF proxies (GLD, USO) — acceptable for backtesting but introduces tracking error and contango drag.
3. **JPY/CHF positioning:** Can only trade FX spot (not futures) — acceptable but limits leverage and introduces rollover costs.

### Priority Recommendation
**P1 (CONDITIONAL)** — Most feasible of the four strategies, but requires workarounds:

**Implementation Path:**
1. **Quality proxy:** Use QUAL ETF (iShares MSCI USA Quality Factor) or USMV (iShares MSCI USA Min Vol) as quality basket. Avoids need for fundamental data pipeline.
2. **Safe-haven basket:**
   - Gold: GLD ETF (data available via Stooq/Alpaca)
   - Oil: USO ETF (data available, but note contango drag)
   - JPY: Long USDJPY FX spot (data available via ECB + yfinance)
   - CHF: Long USDCHF FX spot (data available via ECB + yfinance)
3. **Overlay logic:**
   - Base allocation: 70% QUAL, 30% cash
   - Safe-haven trigger: When VIX > 20 or credit spreads widen (use HYG-LQD spread as proxy), shift 30% cash → 10% GLD + 10% USO + 5% long JPY + 5% long CHF
   - Rebalance: Weekly (regime signal persistence)
4. **Backtest period:** 2016+ (limited by Alpaca data for QUAL/GLD/USO)

**Conflicts Resolution:**
- Run as separate strategy from CS Momentum (different signal: quality + regime vs pure momentum)
- If both approved, allocate capital separately (max 20% each per capital policy)

**Data Requirements (P1 priority):**
- [ ] Ingest QUAL, USMV, GLD, USO ETF history (Stooq + Alpaca)
- [ ] Ingest VIX history (CBOE free data, already in backlog)
- [ ] Compute HYG-LQD spread (both available via Alpaca)
- [ ] Verify USDJPY, USDCHF FX data (ECB connector already exists)

**Estimated Timeline:** 1-2 weeks (data ingestion + backtest)

---

## Summary Table

| Strategy | Data Infra | Execution | Conflicts | Complexity | Priority | Blocker |
|----------|-----------|-----------|-----------|------------|----------|---------|
| 1. Defensive Sector Rotation | ❌ | ✅ | ⚠️ | Medium | **REJECT** | No sector classification data |
| 2. HALO Factor | ❌ | ⚠️ | ✅ | High | **REJECT** | No fundamental data pipeline |
| 3. Geographic Rotation | ❌ | ❌ | ✅ | Low | **REJECT** | No intl equity data/permissions |
| 4. Quality + Safe-Haven | ⚠️ | ⚠️ | ⚠️ | Medium | **P1** | Requires ETF proxies + VIX data |

---

## Recommended Actions

### Immediate (This Week)
1. **Strategy 4 Data Ingestion:**
   - Add QUAL, USMV, GLD, USO to `quant_data` ingestion pipeline
   - Ingest VIX history from CBOE (free, 1990+)
   - Verify HYG, LQD data availability (Alpaca)
   - Test USDJPY, USDCHF FX data quality (ECB connector)

2. **Assign to Researcher:**
   - **Elena** (equity quant) to research Strategy 4
   - Use strategy research template (`notebooks/templates/strategy_research_template.ipynb`)
   - Target: Round 1 notebook by end of week

### Short-Term (Next 2 Weeks)
3. **Strategy 4 Research:**
   - Cerebro literature briefing on quality factor + safe-haven strategies
   - Backtest 2016-2026 (limited by QUAL inception date)
   - Walk-forward analysis (6 folds, 2yr train / 6mo test)
   - Compare vs SPY benchmark and vs QUAL-only (no overlay)

### Medium-Term (Next Quarter)
4. **Data Pipeline Expansion (P3):**
   - Evaluate Norgate Data ($50/mo) for sector constituents + delisted stocks
   - Add country ETF data (EWJ, EWG, VGK, EEM) to pipeline
   - Research IBKR account upgrade for international equity permissions

5. **Revisit Rejected Strategies:**
   - Strategy 1 (Sector Rotation) — revisit after sector data available
   - Strategy 3 (Geographic Rotation) — revisit after IBKR upgrade

### Long-Term (6+ Months)
6. **Fundamental Data Pipeline:**
   - Evaluate fundamental data sources (Quandl, Alpha Vantage, Polygon)
   - Build balance sheet / income statement ingestion
   - Enables Strategy 2 (HALO Factor) and custom quality factor construction

---

## Lessons Applied

This assessment applied the following lessons from `LESSONS_LEARNED.md`:

- **L-INFRA-1:** No futures infrastructure = reject commodity/yield curve strategies (applied to Strategy 2 commodity exposure)
- **L-INFRA-2:** IBKR account = US equities + FX spot only (applied to Strategy 3 rejection)
- **L-SIGNAL-3:** Always compare against simplest alternative (Strategy 4 will benchmark vs QUAL-only)
- **L-PROCESS-1:** Check data availability before research (prevented wasted research time on Strategies 1-3)

---

## PM Notes

**Why Strategy 4 is prioritized despite data gaps:**
1. **Feasible workarounds:** Quality ETF proxy avoids need for fundamental data pipeline (6+ month build)
2. **Timely thesis:** Geopolitical risk + high valuations is current market concern (March 2026)
3. **Orthogonal to existing pipeline:** Quality + safe-haven is different from momentum/carry strategies
4. **Fast validation:** Can backtest in 1-2 weeks with existing infrastructure + minor data additions

**Why Strategies 1-3 are rejected:**
1. **Strategy 1:** Sector rotation requires either expensive data ($5K+/yr) or 6+ months to build valuation pipeline
2. **Strategy 2:** HALO factor is too vague and requires fundamental data we don't have
3. **Strategy 3:** Geographic rotation blocked by IBKR permissions (account upgrade is 2-4 week process)

**Capital allocation consideration:**
- If Strategy 4 passes PM review (APPROVED), max allocation = 20% per capital policy
- Current pipeline: FX Carry (P1), CS Momentum (P3), Sector Rotation (P4)
- Strategy 4 would compete with CS Momentum for equity allocation — may need to reduce CS Momentum to 15% if both approved

---

**Next Steps:**
1. Message **Data** to ingest QUAL, USMV, GLD, USO, VIX, HYG, LQD
2. Message **Elena** to begin Strategy 4 research after data ready
3. Update `research/STRATEGY_TRACKER.md` with Strategy 4 entry

*Assessment complete: 2026-03-17*
