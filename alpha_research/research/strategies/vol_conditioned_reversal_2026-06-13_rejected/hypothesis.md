<!-- 2026-06-13: S0 framing (Cerebro+Data intake) for vol-conditioned sector reversal — falsifiable mechanism, duplicate/cooling adjudication vs vix_regime, data readiness. -->

# S0 Framing — Vol-Conditioned Sector Reversal

> **Strategy id (proposed):** `vol_conditioned_reversal`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING`
> **Stage:** S0 intake (act as Cerebro + Data) · **Date:** 2026-06-13 · **Decision owner:** Zelin
> **Verdict of this stage:** **PASS to S1** (not a near-duplicate; falsifiable; data CONDITIONAL)
> **Scope guard:** spec only — no code, no `manifest.yaml`, no runner, no trial-ledger row.

---

## 1. The mechanism in one falsifiable sentence

> **In high-volatility regimes (VIX above its trailing 60-day median), a cross-sectional 5-day
> reversal among the 11 liquid SPDR sector ETFs — long the worst-performing sectors, short the
> best — earns a positive NET-of-cost return because volatility-constrained intermediaries
> withdraw liquidity and demand higher compensation to absorb uninformed sector-level flow
> (Nagel 2012); FALSIFIED if the high-VIX-conditioned long/short reversal portfolio's NET
> Sharpe at 2× modeled costs is ≤ 0, OR if it does not beat an equal-weight baseline, OR if its
> edge is statistically indistinguishable from an unconditional reversal that ignores the VIX
> gate.**

- **Who is on the other side / why the edge exists:** sellers of immediacy. In stress, dealers,
  market-neutral stat-arb desks, and ETF authorized participants reduce risk capital; whoever
  steps in to absorb the resulting one-sided sector flow is paid for bearing inventory/adverse-
  selection risk. The reversal long/short *is* the liquidity-provision return, and Nagel (2012)
  shows that compensation scales with the VIX. The counterparties are forced/uninformed flow
  (de-risking funds, panic rebalancers, leveraged-ETF hedging) who pay to exit now.
- **is_falsifiable = true.** The sentence states a sign condition (NET Sharpe > 0 at 2× cost),
  a baseline condition (> equal-weight), and a *conditioning* condition (the VIX gate must add
  value over the unconditional reversal). All three are machine-checkable in the rigor battery.

**Falsifiable kill predicates carried into later stages (pre-committed framing):**
1. NET Sharpe at 2× cost ≤ 0 → kill (battery gate 8 analogue).
2. Conditioned reversal NET Sharpe ≤ unconditional reversal NET Sharpe (VIX gate adds nothing) → kill the *thesis* (it's just reversal, not vol-conditioned).
3. |ρ| > 0.4 vs any active pool stream (esp. `sector_rotation`) → portfolio-fit kill.
4. Turnover so high that NET ≤ 0 once realistic ETF spreads/impact at 25k–100k AUM are applied → kill (this is the most likely failure mode — see §5).

---

## 2. Asset track & predicted correlation family

- **asset_track = `etf_rotation`.** Same instrument class and execution venue as `sector_rotation`
  (11 SPDR sector ETFs, daily liquid US equities). Long/short tilt around the cross-section, not
  futures, not single-name factor sleeves.
- **predicted_correlation_family — should be LOW / slightly NEGATIVE vs the monthly
  sector-momentum stream (`sector_rotation`).** Reasoning, explicitly:
  - **Opposite sign by construction.** `sector_rotation` buys recent winners (6-1 month
    momentum); this strategy buys recent *losers* at a 5-day horizon. Momentum and short-horizon
    reversal are near-orthogonal-to-anti-correlated factors in the cross-section. At the same
    universe, a winner at 6 months is frequently *not* a loser over the last 5 days, so the
    overlap is partial, but the directional tilt is opposing.
  - **Different horizon & duty cycle.** Monthly rebalance, always-on (momentum) vs daily signal
    that is *flat whenever VIX ≤ its 60-day median* (reversal). The reversal stream is dollar-
    neutral and only active in a fraction of days, which mechanically decorrelates it from an
    always-invested monthly tilt.
  - **Net prediction:** pairwise ρ in roughly **[-0.3, +0.2]**, comfortably inside the |ρ| ≤ 0.4
    gate — *plausibly* a genuine diversifier. THIS IS A PREDICTION, NOT A MEASUREMENT; the gate
    is decided by the engine's measured correlation, and §5 flags the hidden-common-factor risk
    (both are long/short bets on the *same 11 sectors*, so a sector-dispersion regime could drive
    both at once). Must be measured, not assumed.
- **Correlation family it should RESEMBLE:** short-horizon liquidity-provision / mean-reversion
  return streams (Nagel reversal, Khandani-Lo "contrarian" book). It will carry a latent
  **short-volatility / short-liquidity** exposure — it makes money providing immediacy and loses
  in a forced-deleveraging cascade (Aug-2007 quant quake). That tail is the family signature.

---

## 3. Duplicate / cooling adjudication (graveyard + strategy folders inspected)

**Folders inspected:** `strategies/` (8 entries) and `graveyard/README.md`. Pre-factory kills
table confirms `vix_regime_vrp` killed 2026-03-15 (L4/L5/L6/L7); `vol_scaled_momentum`,
`yield_curve`, `commodity_momentum` killed 2026-03-13.

### Nearest neighbor: `vix_regime_2026-03-15_rejected` — NOT a near-duplicate

| Dimension | `vix_regime` (rejected) | This idea (vol-conditioned reversal) | Same? |
|---|---|---|---|
| **Mechanism** | VRP + VIX term-structure slope as an **equity EXPOSURE SCALAR** (market timing — how much SPY/momentum beta to hold) | **Cross-sectional liquidity provision** — long/short among sectors; dollar-neutral, no net market timing | **NO** |
| **What VIX does** | VIX/VRP *is the signal* (predict the market's direction/sizing) | VIX is only a **regime GATE** (when to switch the reversal on); the tradeable signal is the 5-day sector return cross-section | **NO** |
| **Net market exposure** | Long-biased exposure overlay (timing beta) | ~Dollar-neutral long/short (beta ≈ 0 by design) | **NO** |
| **Horizon** | Weekly/monthly regime switching | 5-day reversal, daily evaluation | **NO** |
| **Why it died** | MinBTL 3,968 yr; spanning-alpha t = −0.18 (no alpha after SPY+momentum); dominated by 21-day trailing vol; overlay HURT OOS Sharpe −0.297 | n/a — different signal entirely; spanning control here is reversal vs momentum, not VRP vs SPY | — |

**Adjudication:** **GENUINELY DISTINCT, not a resurrection.** The only shared atom is the word
"VIX." `vix_regime` used VIX as a *directional/sizing* signal on aggregate equity beta; this idea
uses VIX as a *binary regime switch* that turns on an orthogonal *cross-sectional* trade. The
return source is different (timing premium vs liquidity-provision premium), the net exposure is
different (long-biased vs dollar-neutral), and the spanning control is different (here we must
span the *unconditional reversal* and *monthly momentum*, not SPY+VRP). The duplicate test is on
*mechanism*, and the mechanism differs.

### Cooling status

- **Cooling window:** `vix_regime` was rejected 2026-03-15; a 90-day cooling window ends
  **2026-06-13 = today.** The window is satisfied to the day — but this is **moot**, because
  cooling only binds a *resurrection of the same hypothesis*, and this is not that hypothesis.
- **If it WERE adjudicated a resurrection** (it is not), the resurrection bar would require
  *materially new evidence* directly answering the three structural kills of `vix_regime`:
  1. A signal whose **MinBTL ≤ available history** (the 3,968-yr failure was the decisive one) —
     i.e., evidence that the conditional reversal's information ratio is high enough that the
     sample can actually distinguish it from chance.
  2. **Independent spanning alpha** (t ≥ 1.96) after controlling for SPY *and* momentum *and*
     trailing-vol timing — `vix_regime` failed at t = −0.18.
  3. A **head-to-head win vs the simplest baseline** (here: unconditional reversal, and a plain
     trailing-vol filter), since `vix_regime` lost to 21-day trailing vol on every metric.
  None of this is needed as a *cooling* matter — but note these three become **direct S1/S3
  challenge requirements anyway**, because the PM will (correctly) ask "is this just dressed-up
  vol timing?" given the universe and VIX overlap.

### Secondary neighbors (carry forward as challenges, not duplicates)

- **`vol_scaled_momentum_2026-03-13_rejected`** — pointed lesson: it was a *fair-weather* fund
  (Barroso VIX-conditioned: Sharpe +2.255 low-VIX vs −1.305 high-VIX), all profit in calm markets.
  **This idea claims the OPPOSITE** — it makes money *in* high-VIX. That is the right direction
  to avoid the L3 fair-weather trap, **but it inverts the burden of proof onto the high-VIX cost,
  turnover, and short-vol tail**: high-VIX is exactly when spreads blow out and forced unwinds
  happen, so the NET edge must survive *stressed* costs, not average costs.
- **`sector_rotation_2026-03-13_conditional` (now `sector_rotation_v1`)** — SAME 11-ETF universe,
  monthly momentum. The |ρ| ≤ 0.4 gate vs this stream is **central** (see §2). Different
  sign/horizon makes low correlation plausible but it MUST be measured.

---

## 4. Data readiness — **CONDITIONAL**

Local Parquet inventory verified (`data/market_data/prices/*.parquet`, schema
`(date, ticker, open, high, low, close, volume)`; VIX files are OHLC indexed by date):

| Series | Local start | Local end | Note |
|---|---|---|---|
| XLK XLF XLE XLV XLY XLP XLI XLB XLU | **2012-01-03** | 2026-06-11 | 9 of 11 sectors, ~14.4 yr local |
| XLRE | **2015-10-08** | 2026-06-11 | added 2015 (real estate carve-out from financials) |
| XLC | **2018-06-19** | 2026-06-11 | added 2018 (comms-services GICS reclassification) |
| `vix_daily` (^VIX) | 2006-01-03 | **2026-02-27** | **STALE ~3.5 mo** vs ETF data |
| `vix3m_daily` | 2006-07-17 | 2026-02-27 | not needed for this signal |
| SPY | 2012-01-03 | 2026-06-11 | benchmark/beta control |

**Why CONDITIONAL (not READY, not BLOCKED):**

1. **History is ~14 yr local, NOT the ~1999 / 27-yr the idea brief assumes.** Local sector ETFs
   begin **2012-01-03**, so the headline "9-sector history to ~1999" is **not satisfied by the
   local lake**. To reach the 1999 start the brief contemplates, sector ETF closes must be pulled
   from yfinance/Stooq (the SPDRs inception ~Dec-1998). **MinBTL risk is real and unresolved**:
   with only ~14 yr local — and the trade *flat* on roughly half the days (VIX ≤ median) — the
   *effective* high-VIX sample is far smaller than the calendar span. Given `vix_regime` died on
   MinBTL = 3,968 yr, **estimating MinBTL on the conditional sub-sample is a gating S1 task.**
2. **VIX local data is stale (ends 2026-02-27, ~3.5 mo behind the ETFs ending 2026-06-11).** Must
   refresh ^VIX (yfinance) **or** switch to **FRED `VIXCLS`** for a clean, vendor-stable,
   PIT-friendly daily close. Decision needed: `^VIX` (Cboe via yfinance, same-day close) vs
   `VIXCLS` (FRED, 1-day publication lag). For a *daily-close, trade-next-open* convention the
   VIX gate at date *t* uses VIX close at *t*; with `VIXCLS` confirm no extra lag is injected.
   The 60-day rolling median needs ≥ 60 consecutive VIX closes before the first tradeable signal.
3. **9-vs-11 sector problem (pre/post survivorship of the universe itself).** XLC (2018) and XLRE
   (2015) post-date the others. The cross-section must be handled as a **dynamic universe**: trade
   the 9-sector cross-section before 2015, 10 sectors 2015–2018, 11 thereafter — never backfill
   XLC/XLRE with synthetic history (that is look-ahead on the universe definition). Pre-commit the
   universe-membership-by-date rule in the proposal.
4. **Survivorship/splits:** SPDR sector ETFs are non-delisting, dividend-paying; confirm
   close is **total-return / split-adjusted** consistently across all 11 (yfinance "Adj Close"
   vs raw close) — a 5-day reversal is sensitive to dividend ex-dates and any adjustment
   discontinuity. QC preflight (`quant_data/qc.py`) must flag stale prices / extreme returns
   around ex-div and the 2018/2015 splice points.
5. **What the signal minimally needs (daily):** for each tradeable date *t* — (a) 5-day trailing
   total return per sector (data *t−5..t*), cross-sectionally ranked; (b) VIX close *t* and its
   trailing 60-day median; gate active iff VIX_t > median(VIX_{t−59..t}). Execution shift applied
   by the engine (weights at *t* use only data ≤ *t*). All inputs are daily closes — no
   intraday/options data required (a plus vs `vix_regime`, which needed VRP/term-structure).

**Verdict: CONDITIONAL.** All instruments exist locally and the signal is computable today on the
2012→ window with a VIX refresh; but (i) the long-history claim requires a yfinance/Stooq pull,
(ii) VIX must be refreshed or moved to `VIXCLS`, and (iii) the dynamic-universe rule must be
pinned down before the backtest is trustworthy. None of these are blockers — they are S1/S2
data tasks.

---

## 5. Open risks the later stages MUST resolve

1. **Costs & turnover (THE primary kill risk).** A 5-day reversal evaluated daily is high-turnover
   by nature, and it trades *only in high-VIX windows — exactly when bid/ask spreads and market
   impact are widest.* The literature is blunt: the unconditional reversal is *unprofitable after
   costs* for most participants (costs of immediacy ≈ 1.9%/yr exceed liquidity-provision returns;
   ScienceDirect 2022). The whole thesis lives or dies on whether the *high-VIX* premium (Nagel)
   exceeds *high-VIX* costs. S2/S3 must model **regime-dependent (stressed) spreads/impact at
   25k–100k AUM**, not flat average bps. Pre-commit a rebalance-frequency / no-trade-band design
   (recall L7: daily rebalancing of regime signals produced 2430%/yr turnover in `vix_regime`).
2. **ETF-level efficiency / is sector reversal even there.** Nagel's strong results are largely at
   the **stock** level; he notes *industry* reversal portfolios "do not yield high returns
   unconditionally" and only pay off *conditional on high VIX*. With only 11 well-arbitraged,
   liquid sector ETFs (vs thousands of single names), the cross-sectional dispersion to harvest is
   far thinner and the liquidity-provision premium at the ETF layer may be largely arbitraged away
   (AP creation/redemption keeps ETF prices tight). **Risk: the edge that exists in stocks is too
   small to clear ETF costs.** S1 must find ETF-specific (not single-stock) evidence; absent it,
   this is a translation-risk kill.
3. **Short-volatility / forced-deleveraging tail (Khandani-Lo Aug-2007 quant quake).** Providing
   liquidity in stress is structurally short-vol / short-liquidity: it earns small premia most of
   the time and suffers a violent loss when a crowded contrarian book is force-unwound (Aug 6–9,
   2007). The strategy is *most active precisely in the regimes where this tail detonates.* S3 must
   stress the high-VIX days for left-tail / cascade behavior and size for survivability, not just
   average Sharpe. Crowding/decay is documented (post-2000 reversal decline; institutional
   anomaly crowding → elevated crash risk).
4. **"Is this just dressed-up vol timing?" / spanning alpha.** Mirror the `vix_regime` kills: the
   conditioned reversal must show **independent spanning alpha (t ≥ 1.96) vs (a) the unconditional
   reversal, (b) monthly sector momentum / `sector_rotation`, and (c) a plain trailing-vol filter.**
   If the VIX gate adds no measured value over always-on reversal, the "vol-conditioned" claim is
   falsified (§1 predicate 2).
5. **MinBTL on the conditional sub-sample.** Because the trade is flat on ~half the days, the
   *effective* sample backing the Sharpe is much shorter than the calendar history. Estimate MinBTL
   on the high-VIX sub-sample early (S1) — `vix_regime` died here at 315× over-budget.
6. **Correlation realization vs `sector_rotation` (portfolio fit).** Predicted low/negative (§2),
   but both are long/short bets on the *same 11 sectors*; a sector-dispersion regime could co-move
   them. Measure pairwise ρ in the engine before any promotion; |ρ| ≤ 0.4 is a hard gate.
7. **VIX-gate robustness / look-ahead hygiene.** The 60-day-median threshold is a free parameter
   (battery requires ±20/40% perturbation). Confirm the gate at *t* uses only VIX ≤ *t* (no
   centered window), and that the VIX-vs-VIXCLS choice injects no extra information at the open.

---

## 6. References (verified at S0 — real titles/venues/URLs)

- **Nagel, S. (2012). "Evaporating Liquidity." *Review of Financial Studies* 25(7): 2005–2039.**
  Core supporting mechanism: short-term reversal return ≈ liquidity-provision return; expected
  return and conditional Sharpe rise strongly with the VIX; **industry/sector reversal portfolios
  pay off specifically conditional on high VIX**. NBER w17653 / SSRN 1988706 /
  https://academic.oup.com/rfs/article-abstract/25/7/2005/1602153
- **Khandani, A. & Lo, A. (2011). "What happened to the quants in August 2007? Evidence from
  factors and transactions data." *Journal of Financial Markets* 14(1): 1–46.** Contradicting /
  failure-mode evidence: the short-horizon contrarian (reversal) book is the locus of the Aug-2007
  forced-unwind cascade — the short-vol tail of this exact strategy. NBER w14465 /
  https://www.nber.org/papers/w14465
- **Drechsler, Moreira & Savov (and related) / "Short-term reversals, returns to liquidity
  provision and the costs of immediacy" — *Journal of Banking & Finance* (2022).** Contradicting:
  costs of immediacy frequently exceed liquidity-provision returns; classic reversal has decayed
  post-2000. https://www.sciencedirect.com/science/article/pii/S0378426622000309
  *(NOTE: exact author list not individually re-verified at S0 — confirm in S1 briefing before
  citing in the proposal.)*
- **Quantpedia — "Short Term Reversal Effect in Stocks."** Practitioner note on decay /
  cost-sensitivity of the unconditional effect. https://quantpedia.com/strategies/short-term-reversal-in-stocks

**S0 disposition: PASS to S1.** Falsifiable in one sentence; distinct mechanism from the nearest
neighbor (`vix_regime`); cooling moot (not a resurrection); data CONDITIONAL with named tasks.
S1 briefing must deliver ≥ 2 supporting + ≥ 1 contradicting (Khandani-Lo and the cost-of-immediacy
decay both qualify) and resolve the ETF-level-efficiency and MinBTL-on-subsample questions before
any proposal is written.
