<!-- 2026-06-14: S2 proposal draft (independent, lens = cost & turnover realism FIRST) for vol_conditioned_reversal. Spec only — no code, no manifest, no runner, no ledger row. All Sharpe/return figures are reasoned EXPECTATIONS, not backtest results. -->

# S2 Proposal Draft — Vol-Conditioned Sector Reversal
## Lens: cost & turnover realism FIRST

> **Strategy id (proposed):** `vol_conditioned_reversal`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING`
> **Stage:** S2 proposal draft (independent author) · **Date:** 2026-06-14 · **Decision owner:** Zelin
> **Track:** `etf_rotation` · **Construction:** dollar-neutral cross-sectional long/short, gated on VIX
> **Upstream:** `hypothesis.md` (S0, PASS to S1) · `cerebro_briefing.md` (S1, REVISE → 4 pre-commitments)
> **Scope guard:** SPEC ONLY. No code, no `manifest.yaml`, no runner, no trial-ledger row.
> **Honesty flag:** No `vol_conditioned_reversal` backtest exists. **Every Sharpe / return / turnover
> figure below is a reasoned EXPECTATION or a HISTORICAL result for a DIFFERENT in-repo strategy
> (labelled). None is a realized result for this strategy.**

---

## 0. Lead with the net story (read this first)

This is a **cost-bound** strategy, not an alpha-bound one. The mechanism (liquidity provision in
stress, Nagel 2012) is well-evidenced, but **the entire harvestable edge lives in the spread between
a thin high-VIX gross premium and the cost of trading a high-turnover reversal precisely when spreads
and impact are widest.** The decision is therefore made at the cost layer, and I build the spec from
the cost layer up.

The honest net arithmetic, stated up front (all EXPECTATIONS):

| Quantity | Reasoned expectation | Basis |
|---|---|---|
| Gross L/S Sharpe, high-VIX days only, before costs | **~0.7–1.1** | Nagel: industry-reversal conditional Sharpe rises strongly with VIX; haircut 50–60% for decay (McLean-Pontiff) and the ETF-vs-stock translation (Avramov-Chordia-Goyal small gross premium). |
| Gross annualized L/S edge (full-period, flat ~half the days) | **~2–4%/yr** | PM prior for L/S; the gate is on ~50% of days, so per-active-day edge is ~2× the full-period figure. |
| **All-in round-trip cost per rebalance, 25k–100k AUM, IBKR** | **~10–22 bps of gross notional in calm, ~25–45 bps in stressed (high-VIX) windows** | §6 cost stack: commission floor + volatility-conditional half-spread + small impact. The strategy trades ONLY in the stressed column. |
| Annual cost drag at the pre-committed turnover budget (≤ ~500%/yr two-sided) | **~1.0–2.5%/yr** | turnover × stressed per-trade cost; §6. |
| **Net annualized L/S edge** | **~0.5–2.5%/yr, with a real probability of ≤ 0** | gross minus drag; the band straddles zero by construction. |
| **NET L/S Sharpe (full-period, the number that ships)** | **~0.3–0.6, mode ~0.4, left tail < 0** | low end of the 0.4–0.8 platform band; **material probability of failing Gate 1 (IS Sharpe < 0.5) and a live probability of failing Gate 8 (Sharpe < 0 at 3× costs).** |

**Bottom line:** I expect this to land at the **bottom of the platform's 0.4–0.8 per-strategy net
band, or fail.** I am proposing it anyway because (a) the mechanism is real and falsifiable, (b) it is
a genuine candidate *diversifier* (predicted |ρ| < 0.4 vs the only active pool peer), and (c) the
binding kill — cost-vs-premium on the high-VIX sub-sample — is exactly what the rigor battery is built
to adjudicate. **If the no-trade-band design below cannot keep net Sharpe > 0 at 2× costs, the
strategy is dead, and that is the correct outcome.** I am not proposing a long-only variant as the
headline because the long-only tilt PM prior (1–2% alpha) is *smaller than* the L/S edge while
carrying directional sector beta that pollutes the |ρ| story and the clean liquidity-provision
interpretation; L/S dollar-neutral is the right construction for this mechanism (§4).

---

## 1. Economic rationale — who loses money, and why (≥ 2 papers)

**The trade is selling immediacy in stress.** In high-volatility regimes, volatility-constrained
intermediaries — dealers, market-neutral stat-arb desks, leveraged liquidity providers, and ETF
authorized participants — cut risk capital and widen the price they demand to absorb one-sided sector
flow. Whoever steps in to take the other side of forced, uninformed sector-level selling/buying is
paid an inventory- and adverse-selection premium. The **5-day cross-sectional reversal portfolio
(long the worst recent sectors, short the best) IS that liquidity-provision return**, and the premium
**scales with the VIX** because that is when intermediary balance-sheet capacity is scarcest.

**Who is on the other side (who loses money to us):** de-risking funds dumping the recently-weakest
sectors and chasing the recently-strongest ones, panic rebalancers, and leveraged/inverse-ETF
hedging flow — all of whom pay to transact *now*. We are compensated for warehousing the resulting
inventory across the ~5-day horizon until the transitory price pressure mean-reverts.

**Primary supporting papers (from the S1 briefing, verified):**

1. **Nagel, "Evaporating Liquidity," *Review of Financial Studies* 25(7) (2012).** The near-exact
   statement of our mechanism: short-term reversal return ≈ the return to liquidity provision;
   expected return and conditional Sharpe **rise strongly with the VIX**. Critically for *this* spec,
   Nagel finds **industry/sector-portfolio reversal "does not yield high returns unconditionally"**
   but **does** pay off **conditional on high VIX**. This is simultaneously the strongest support
   (it blesses a *sector-level, VIX-gated* trade specifically) and the source of our central design
   constraint: **the unconditional leg is ~zero, so the VIX gate is not an enhancement — it is the
   entire strategy.**

2. **Hameed, Kang & Viswanathan, "Stock Market Declines and Liquidity," *Journal of Finance* 65(1)
   (2010).** Independent confirmation of the **supply-side** channel and, decisively for trading
   *sectors*, documents **inter-industry liquidity spillovers** when market-maker capital is
   constrained. Negative market returns reduce liquidity (worse when funding is tight) and there are
   economically significant returns to *supplying* liquidity after large drops — i.e., the premium
   exists at the level we actually trade, not only in single names.

**Supporting the horizon (secondary):** Lehmann, *QJE* 105(1) (1990) validates the ~5-day weekly
contrarian horizon (weekly winners reverse, losers rebound) as a real, transitory-price-pressure
effect — though net-of-cost survival was a 1990-era claim and has since decayed.

**The cost lens reads this rationale as a warning, not just a thesis:** the same constrained-
intermediary state that creates the premium (wide intermediary risk-aversion) is the state in which
**bid/ask spreads, depth, and impact are worst** (Hameed et al.'s liquidity *withdrawal* is two-sided
— it raises both our premium and our cost). So the premium and the cost are driven by the **same
latent variable**. The strategy is only viable if, on the high-VIX sub-sample, the premium curve sits
**above** the cost curve net — an empirical question I force the battery to answer (§9).

---

## 2. Signal construction (precise, pre-committed)

All quantities computed from **daily total-return (split- & dividend-adjusted) closes**. Weights at
date *t* use only data **≤ t**; the review engine applies the execution-convention shift. **The
strategy function must NOT pre-shift** (weights contract).

**Step 1 — 5-day reversal score (the tradable signal).** For each eligible sector *i*, compute the
trailing 5-trading-day total return `r_i = P_i(t) / P_i(t-5) - 1`. Cross-sectionally z-score across
the eligible universe: `z_i = zscore_xs(r_i)`. The **reversal** signal is the *negation*:
`s_i = -z_i` (long the worst recent performers, short the best).

**Step 2 — VIX regime gate (binary, the duty cycle).** Let `V(t)` be the VIX close at *t* and
`M(t) = median(V(t-59 .. t))` the trailing 60-trading-day median (inclusive, backward-only — no
centered window). **Gate is ACTIVE iff `V(t) > M(t)`**; otherwise the portfolio is **flat (all
weights 0)**. The 60-day median needs ≥ 60 consecutive VIX closes before the first tradable date.

**Step 3 — short-term sector-momentum neutralization (pre-committed design choice).** The S1 briefing
(Da-Liu-Schaumburg 2014; Blitz et al. 2024) is explicit that **raw sector reversal is partly a bet
*against* short-term industry momentum**, which is a known drag AND is mechanically the
`sector_rotation_v1` peer. **Decision: do NOT neutralize in the baseline (`mom_neutralize = off`).**
Rationale: (a) with only 9–11 assets, projecting out a momentum factor estimated on the same 11-name
cross-section is noisy and burns degrees of freedom (echoes L2 — tight constraints add noise); (b)
the 5-day reversal horizon and the 6–1-month momentum horizon are far enough apart that the
contamination is modest at 5 days; (c) carrying the raw signal keeps the construction transparent and
the |ρ| vs `sector_rotation` *measurable as-is* rather than entangled with a neutralization choice.
**`mom_neutralize` is an explicit, declared parameter** (off in baseline, on as a pre-registered
variant) so the trial is counted honestly in `n_trials`. If the engine shows the raw signal is
dominated by the momentum-neutralized version, that is a documented variant, not a silent refit.

**Step 4 — raw target weights (dollar-neutral).** On an active rebalance date with `n` eligible
sectors, demean the signal cross-sectionally and scale to gross leverage 1.0 (dollar-neutral, so
long notional = short notional = 0.5):
`w_raw_i = s_i / Σ_j |s_j|` (after cross-sectional demeaning, which `zscore_xs` already provides up to
rounding; renormalize so `Σ|w| = 1`, `Σ w ≈ 0`).

**Step 5 — per-name cap.** Clip `|w_i| ≤ max_weight` then renormalize to `Σ|w| = 1`. Prevents a single
extreme 5-day mover from dominating the book (e.g., XLE on an oil shock).

**Step 6 — no-trade band (THE cost-control primitive, §6).** Do not trade from current weights
`w_prev` to `w_target` unless the per-name change exceeds a band: hold `w_prev_i` if
`|w_target_i - w_prev_i| < band`; otherwise move to `w_target_i`. This converts a continuously-drifting
5-day signal into a **discrete, low-churn** book and is the single most important turnover lever.

**Look-ahead hygiene (unit-test target `test_no_lookahead_truncation_invariance`):** truncating the
price/VIX panel at any date `T` must leave all weights at dates `≤ T` unchanged. The VIX gate uses
only `V(≤ t)`; the 60-day median is strictly backward; the 5-day return uses `P(t-5..t)`.

---

## 3. Universe (dynamic — no universe look-ahead)

Eleven SPDR sector ETFs, **membership by date** (never backfill late inceptions — that is look-ahead
on the universe definition):

| Window | Members | n |
|---|---|---|
| start → 2015-10-07 | XLK XLF XLE XLV XLY XLP XLI XLB XLU | 9 |
| 2015-10-08 → 2018-06-18 | + XLRE | 10 |
| 2018-06-19 → end | + XLC | 11 |

A sector is **eligible** on date *t* only once it has a full 5-day return history AND ≥ 60 VIX closes
exist for the gate. **Local history starts 2012-01-03** (not ~1999 as the original brief assumed); a
yfinance/Stooq pull back to SPDR inception (~Dec 1998) is a *data task*, not assumed here. The
proposal's `backtest_start` is set conservatively to **after the 60-day VIX warmup on the available
history** (see §8). VIX source decision in §8.

**Benchmark / control series (not universe members):** SPY (beta/spanning control). **VIX** (`^VIX`
refreshed, or FRED `VIXCLS`) drives the gate only.

---

## 4. Why dollar-neutral L/S (not long-only tilt)

The PM prior offers two constructions: long-only tilt (1–2% alpha) or L/S (2–4%). For **this
mechanism** L/S dominates:

- **The mechanism is cross-sectional, not directional.** Liquidity provision is "long the
  oversold, short the overbought" — a long-only tilt throws away the short leg, which is exactly half
  the immediacy premium, and replaces it with **net sector beta** that (a) is not the edge, (b)
  pollutes the |ρ| ≤ 0.4 story (directional beta co-moves with everything), and (c) reintroduces the
  L3 "vol targeting doesn't fix crash risk for long-only equity" trap that killed `vol_scaled_momentum`.
- **Dollar-neutral isolates the residual.** `Σ w ≈ 0` removes the market factor so the spanning-alpha
  and |ρ| tests measure the *liquidity-provision residual*, not hidden beta (Standing Red Flag:
  "long-only Sharpe >> EW → hidden beta or look-ahead").
- **Cost honesty cuts the other way too:** L/S trades both legs, so gross notional per rebalance is
  larger and the cost stack is heavier. This is a feature for the rigor test — it makes the cost
  hurdle *harder*, so surviving it is more credible. The no-trade band (§6) is what keeps L/S turnover
  bounded.

I therefore set `construction = long_short`, gross leverage **1.0** (0.5 long / 0.5 short),
dollar-neutral. (A long-only variant is a possible fallback only if the short leg proves
uncostable — declared, not silently substituted.)

---

## 5. Rebalance frequency & the L7 turnover hazard (cost lens, central)

**The signal updates daily; the book must NOT.** L7 is explicit: daily rebalancing of regime signals
produced **2430%/yr turnover** in `vix_regime` (HISTORICAL, other strategy), cut to **916%/yr** by a
**weekly resample** — still high. A 5-day reversal traded daily in high-VIX bursts is a direct L7
hazard. Pre-committed design:

1. **Weekly rebalance clock, not daily.** `rebalance.frequency = "weekly"` (review-engine
   `rebalance_dates(..., "weekly")`). The 5-day signal naturally implies a ~weekly hold; evaluating
   the book weekly aligns the decision cadence to the signal horizon and **cuts turnover by ~5×**
   versus daily without materially changing the captured premium (the 5-day reversal is largely
   spent within the week).
2. **VIX gate evaluated on the weekly rebalance date** using `V(≤ that date)`. Between rebalances the
   book is held; if the gate flips to inactive at a rebalance date, **flatten to zero at that
   rebalance** (do not wait — being flat is the default state and carries no signal cost).
3. **No-trade band on top of the weekly clock (§6).** Even on a weekly date, only rebalance names
   whose target moved beyond the band. This is what defends against the gate flickering on/off around
   the 60-day-median threshold and churning the whole book.
4. **Execution convention: `t+1_open`** (decided at the weekly rebalance date *t* from data ≤ *t*,
   executed at next session's open). This is the realistic retail convention (we cannot trade the
   close we used to compute the signal) and it is more conservative than `t_close`. The engine applies
   the shift.

**Turnover budget (pre-committed):** **two-sided annual turnover ≤ ~500%/yr** as a *hard design
target*, and **reported** in the artifact bundle. For calibration only: `vix_regime` weekly was
916%/yr (HISTORICAL); our weekly + no-trade-band + ~50% duty cycle (flat half the year) target is
materially below that. **If realized turnover > ~800%/yr, the no-trade band is too loose — widen it
(declared parameter move, bumps `n_trials`) or kill.**

---

## 6. Cost model — volatility-conditional, NOT flat bps (the lens, in full)

Flat average-bps cost models are the cardinal error for this strategy because **it trades only in the
high-VIX column where spreads/impact are worst** (C1 Avramov-Chordia-Goyal; C6 IOSCO/Mar-2020). The
cost model must be **regime-dependent**.

### 6.1 The per-trade cost stack (per leg, one-way), 25k–100k AUM on IBKR

| Component | Calm-regime value | High-VIX (gate-active) value | Source / rationale |
|---|---|---|---|
| **Commission** | IBKR Pro: $0.005/share, min $1.00/order; ≈ **0.5–1.5 bps** of a 1–3k notional clip; the **$1 floor binds at 25k AUM** (a 0.5%-of-25k = $125 clip of a $90 ETF ≈ 1.4 shares → $1 floor → ~0.8%? — see §6.2 sizing). | same | IBKR published schedule. **At 25k the per-order floor is the dominant cost** — this drives the universe-clip and sizing design in §6.2. |
| **Half-spread** | SPDR sector ETFs are among the tightest on the tape: XLK/XLF effective spread **~1 bp**; broader sectors (XLB/XLRE/XLU) **~1–3 bps**. | **2×–5× wider**: model **~3–8 bps** half-spread in gate-active windows; tail to **15–30 bps** on Mar-2020-type dislocation days. | SSGA practitioner materials (cred 2); IOSCO PD682 / Mar-2020 ETF-NAV dislocation (C6). Equity sector ETFs dislocated far less than bond ETFs but the direction is unambiguous. |
| **Market impact** | Negligible at 25k–100k (we do not move XLK). | Small but nonzero in thin high-VIX books; model a **square-root impact** floor of ~1–3 bps on the clip. | We are not at HFT scale; impact is the smallest term. Capacity (Gate 10) passes comfortably. |
| **All-in per leg, one-way** | **~2–5 bps** | **~6–14 bps** (tail to 30–50 bps on dislocation days) | sum of above |
| **Round-trip per name (in + out)** | ~4–10 bps | **~12–28 bps** | the cost the battery applies to turnover |

**The battery runs this at 1× / 2× / 3×.** The 2× and 3× multipliers are applied to the
**high-VIX (stressed) column**, not the calm column, because that is the only column we trade in.
Gate 8 (Sharpe < 0 at 3× costs) is therefore a **3× stressed-cost** test — appropriately brutal.

### 6.2 The 25k-AUM commission-floor problem (cost lens, often missed)

At **25k AUM**, an 11-name L/S book at gross 1.0 puts ~**$1.1k notional per name per side**. IBKR's
**$1.00 order minimum** is then **~9 bps per order** *before* any spread — and a full rebalance of all
22 legs (11 long + 11 short) is **22 orders ≈ $22 ≈ 9 bps of the 25k book per round trip.** This is
**larger than the calm half-spread** and is **fixed**, so it does not scale away. Pre-committed
mitigations, in order:

1. **The no-trade band is also a commission-floor defense:** by only trading names that moved beyond
   the band, a typical weekly rebalance touches ~4–8 legs, not 22 — cutting fixed-commission drag
   proportionally.
2. **Concentrate, don't spread:** trade only the **extreme tails** of the cross-section (e.g., the
   2 most-oversold long, 2 most-overbought short) rather than a full 11-name tilt, so each clip is
   larger relative to the $1 floor. **Declared parameter `n_legs_per_side` (baseline 2–3).** This is
   a genuine trade-off (fewer names = less diversification, more idiosyncratic risk) and is
   battery-perturbed.
3. **Floor-aware accounting:** the cost model must charge the **max(per-share commission, $1 order
   floor)** explicitly — a percentage-bps model understates cost at 25k. At 100k the floor binds far
   less; report cost drag **at both 25k and 100k** so the capacity story is honest.

### 6.3 Net cost arithmetic (EXPECTATION)

At the pre-committed ~500%/yr turnover budget and ~12–28 bps round-trip stressed cost:
`cost drag ≈ 5.0 (turnover) × ~0.20% (mid stressed round-trip) ≈ ~1.0%/yr`, scaling to **~2.5%/yr**
at the high end of the stressed-cost range and the 2× multiplier. **Against a gross L/S edge of
~2–4%/yr, the net edge is ~0.5–2.5%/yr and can be ≤ 0** — this is the entire risk, stated honestly.

---

## 7. Every parameter, with value and rationale

| Parameter | Baseline value | Rationale | Battery perturbation (±20/40%) |
|---|---|---|---|
| `reversal_lookback` | **5 trading days** | Lehmann weekly horizon; Nagel's reversal window. Short enough to be liquidity-pressure, long enough to dodge 1-day microstructure noise/bid-ask bounce. | 4 / 3 and 6 / 7 days |
| `vix_lookback` (median window) | **60 trading days** | The pre-registered gate window from the hypothesis; ~3 trading-months balances responsiveness vs. a stable regime estimate. **Free parameter — battery must perturb it.** | 48 / 36 and 72 / 84 days |
| `vix_gate_rule` | **`V(t) > median60`** (binary) | Pre-committed; a median (not mean) is robust to VIX spikes. Backward-only window (no look-ahead). | also test `> 1.1×median` / `> 0.9×median` as the ±20% threshold perturbation |
| `construction` | **long_short, dollar-neutral, gross 1.0** | §4 — isolates the residual, removes hidden beta. | gross 0.8 / 1.2 |
| `max_weight` (per-name cap) | **0.20** (|w_i| ≤ 0.20) | Mirrors `sector_rotation` cap; prevents one extreme 5-day mover dominating. | 0.16 / 0.12 and 0.24 / 0.28 |
| `n_legs_per_side` | **2–3** (trade tails only) | §6.2 — defends the $1 commission floor at 25k; larger clips per order. | 1 / 2 and 3 / 4 |
| `no_trade_band` | **0.05** (5% per-name) | §6 — the core turnover/commission control. Set so weekly rebalances touch ~4–8 legs, target turnover ≤ 500%/yr. | 0.03 / 0.04 and 0.06 / 0.07 |
| `rebalance.frequency` | **weekly** | §5 — kills the L7 daily-turnover hazard; matches the 5-day hold. | (structural; report daily and biweekly as sensitivity variants — each a declared trial) |
| `execution_convention` | **`t+1_open`** | Realistic retail; conservative; engine applies shift. | (structural) |
| `mom_neutralize` | **off** (baseline); on (declared variant) | §2 Step 3 — noisy to project out on 11 names; declared so it counts in `n_trials`. | on/off both reported |
| `cost_model` | **volatility-conditional**, evaluated 1×/2×/3× on the **stressed** column | §6 — the whole point of the lens. | 1× / 2× / 3× |

**`n_trials` (declared honestly, feeds DSR — this is a FLOOR that accumulates across versions):**
the design space deliberately explored is `reversal_lookback` (≈3) × `vix_lookback`/threshold (≈3) ×
`no_trade_band` (≈3) × `n_legs_per_side` (≈3) × `mom_neutralize` (2) × `rebalance freq` (3) ≈ a few
hundred nominal combinations, but the **honestly declared** count of *distinct variations I will
actually run/consider* is **`n_trials = 24`** (the cross of the headline perturbations above that I
commit to evaluating), explicitly NOT 1. **DSR is deflated by this. If the realized DSR < 0.95 only
because `n_trials` is high, that is the system working — I will not retroactively shrink `n_trials` to
pass the gate** (the URGE to do so is the documented failure mode).

---

## 8. Data prerequisites (decided here)

1. **VIX source — DECISION: use FRED `VIXCLS`** (not `^VIX` via yfinance) for the gate. Rationale:
   vendor-stable, PIT-friendly daily close; the local `^VIX` (`vix_daily`) is **stale (ends
   2026-02-27)**. `VIXCLS` carries a ~1-business-day publication characteristic; **resolve cleanly by
   the execution convention:** with `t+1_open` execution, the gate at rebalance date *t* uses the
   `VIXCLS` value for *t* that is published before next-session open — no extra look-ahead. Confirm in
   QC that no centered/forward fill injects future VIX. (If `t_close` execution were ever chosen, the
   1-day lag would need explicit handling; `t+1_open` sidesteps it.)
2. **Dynamic universe** per §3 — enforced by eligibility (full 5-day history), never backfilled.
3. **Total-return / split-adjusted closes** consistent across all 11 ETFs; QC preflight
   (`quant_data/qc.py`) flags stale prices / extreme returns around dividend ex-dates and the
   2015/2018 universe splice points (a 5-day reversal is sensitive to unadjusted ex-div jumps).
4. **`backtest_start`:** first tradable date after the 60-day VIX warmup on available history
   (≈ 2012-Q2 on the local lake). A yfinance/Stooq pull back to ~1999 would lengthen the calendar but
   **does not fix the binding constraint** — the *effective* high-VIX sub-sample is ~half the calendar
   regardless (§9). `backtest_end` = latest common date (ETFs to 2026-06-11; refresh VIX to match).

---

## 9. Baselines to beat (pre-registered) & MinBTL on the sub-sample

**Per L1/L6 and the S1 four pre-commitments, I pre-register THREE baselines, all on the same
universe/costs/dates:**

1. **Equal-weight buy-and-rebalance** (the platform default, L1). Long-only EW of the eligible
   sectors, weekly rebalance. *The strategy must beat this net.* (Note: a dollar-neutral L/S vs a
   long EW is partly an apples-to-oranges return-stream comparison; the binding L1 test is that net
   risk-adjusted return clears EW and that the L/S Sharpe is positive on its own terms.)
2. **Unconditional 5-day reversal** (same signal, **no VIX gate**, traded always-on). *This is the
   P0 falsification baseline (L4): the VIX-gated version must add MEASURED Sharpe over this.* Per the
   briefing, the unconditional version is expected to be **~zero net** — so beating it is necessary
   but the gap is the whole thesis.
3. **Plain trailing-vol filter** (gate the reversal on **realized 21-day portfolio/SPY vol > its own
   median** instead of VIX). *This is the exact challenge that killed `vix_regime` (dominated by a
   21-day trailing-vol signal, L6).* If a cheaper, simpler trailing-vol gate matches the VIX gate, the
   "VIX" framing adds nothing and the strategy is just dressed-up vol timing.

**Spanning alpha (engine, must measure):** independent spanning-alpha **t ≥ 1.96** vs the unconditional
reversal, vs monthly momentum / `sector_rotation_v1`, AND vs the trailing-vol filter (mirrors the
`vix_regime` t = −0.18 kill). **L5 overlay rule:** the VIX gate must ADD ≥ +0.15 Sharpe over the
unconditional reversal, not merely reduce drawdown.

**MinBTL on the high-VIX sub-sample (the most likely kill — compute EARLY).** The trade is flat ~half
the days, so the **effective sample** backing the Sharpe is far shorter than the ~14-yr local calendar
(or even a ~27-yr pulled history). `sector_rotation_v1`, a *monthly* always-on momentum, already FAILS
MinBTL (needs 4095d vs 3485 available — HISTORICAL). A 5-day reversal active ~half the days has an
**even shorter effective sample**. **I pre-commit to estimating MinBTL on the conditional sub-sample
before any optimization**, and accept that **MinBTL > available history is the modal kill (Gate 7).**

---

## 10. Pre-committed kill thresholds

These are committed BEFORE any backtest. **I will not relax any of them after seeing the result it
blocks** (the documented failure mode).

| # | Kill predicate | Maps to |
|---|---|---|
| K1 | **NET L/S Sharpe < 0 at 2× stressed costs** | Hypothesis predicate 1; battery Gate 8 analogue (the PRIMARY cost kill) |
| K2 | **VIX-gated net Sharpe ≤ unconditional-reversal net Sharpe** (gate adds nothing) OR gate adds < +0.15 Sharpe | Hypothesis predicate 2; L4/L5; "is it just reversal?" |
| K3 | **Net Sharpe ≤ equal-weight** (does not beat the dumbest credible alternative) | L1; first-principles (3) |
| K4 | **Trailing-vol filter matches or beats the VIX gate** (it's just dressed-up vol timing) | L6; the `vix_regime` kill |
| K5 | **Spanning-alpha t < 1.96** vs {unconditional reversal, sector_rotation, trailing-vol filter} | Gate 9; the `vix_regime` t = −0.18 kill |
| K6 | **\|ρ\| > 0.4 vs `sector_rotation_v1`** (or any active pool stream) | Portfolio-fit gate; first-principles (uncorrelated streams) |
| K7 | **IS Sharpe < 0.5** | Kill-checklist Gate 1 |
| K8 | **OOS walk-forward Sharpe < 0.3**, or IS/OOS Sharpe ratio < 0.5 | Gates 2 / 6 |
| K9 | **MinBTL > available history on the high-VIX sub-sample** | Gate 7 — the most likely kill |
| K10 | **DSR < 0.95 or PSR < 0.90** (with honestly-declared `n_trials = 24`) | Gates 4/5; default promotion gate |
| K11 | **Sharpe < 0 at 3× stressed costs** | Gate 8 |
| K12 | **Realized two-sided turnover > ~800%/yr** with no band setting that both controls turnover AND keeps net Sharpe > 0 | L7; cost-lens design failure |
| K13 | **Max drawdown > −30%**, or the conditional-on-high-VIX left tail (worst-week, Aug-2007/Mar-2020 days) shows a Khandani-Lo forced-deleveraging blowup that violates survivability at our sizing | Gate 3; C5 short-vol tail |

**Auto kills (1–8 analogues):** K1, K3, K7, K8, K9, K10, K11, K13(DD). **PM/owner judgment:** K2, K4,
K5, K6, K12, K13(tail) — and Gate 11 (credible mechanism), which §1 satisfies.

---

## 11. How this draft discharges the four S1 REVISE pre-commitments

1. **Beat the gate's own null (two head-to-head baselines + EW).** §9: unconditional reversal,
   trailing-vol filter, equal-weight — all pre-registered; K2/K3/K4 enforce.
2. **Sector-momentum headwind addressed explicitly.** §2 Step 3: `mom_neutralize = off` in baseline
   with stated rationale; `on` as a declared, trial-counted variant; doubles as the `sector_rotation`
   |ρ| story.
3. **Volatility-conditional cost model + no-trade-band.** §6 (regime-dependent spread/impact, $1
   commission-floor accounting at 25k AND 100k, 1×/2×/3× on the stressed column) and §5 (weekly clock
   + no-trade band + turnover budget ≤ 500%/yr, reported). Defuses L7.
4. **MinBTL on the high-VIX sub-sample, computed early.** §9 + K9; flagged as the modal kill.

**Also addressed:** ETF translation risk (§1 cost-lens reading; small-gross-premium expectation baked
into §0); unconditional-reversal decay-to-zero (§9 baseline 2, expected ~zero net); the three
`vix_regime` kills (K5 spanning, K4 trailing-vol dominance, K9 MinBTL); the `vol_scaled_momentum`
fair-weather inversion (we claim profit IN high-VIX, so the burden is stressed costs/tail — §6, K13);
|ρ| vs `sector_rotation_v1` (K6, predicted [−0.3, +0.2], UNMEASURED).

---

## 12. References (verified upstream; real titles/venues — no fabrication)

- **Nagel, S. (2012). "Evaporating Liquidity." *Review of Financial Studies* 25(7): 2005–2039.** —
  core mechanism; reversal ≈ liquidity provision; conditional Sharpe rises with VIX; *industry*
  reversal pays only conditional on high VIX.
- **Hameed, A., Kang, W. & Viswanathan, S. (2010). "Stock Market Declines and Liquidity." *Journal of
  Finance* 65(1): 257–293.** — supply-side mechanism; inter-industry liquidity spillovers (sector level).
- **Lehmann, B. (1990). "Fads, Martingales, and Market Efficiency." *Quarterly Journal of Economics*
  105(1): 1–28.** — validates the ~5-day weekly contrarian horizon.
- **Avramov, D., Chordia, T. & Goyal, A. (2006). *Journal of Finance* 61(5): 2365–2394.** —
  reversal concentrated in illiquid names; gross < costs even there → small gross premium expected at
  the liquid ETF layer (the central cost-lens contradiction).
- **Khandani, A. & Lo, A. (2011). *Journal of Financial Markets* 14(1): 1–46 (NBER w14465).** —
  Aug-2007 quant quake; the short-vol / forced-deleveraging tail of this exact book (K13).
- **Blitz, van der Grient & Honarvar (2024). "Reversing the Trend of Short-Term Reversal." *Journal of
  Portfolio Management* 50(6) (SSRN 4575689).** — classic STR "vanished"; raw sector reversal bets
  against short-term industry momentum.
- **Chordia, Subrahmanyam & Tong (2014). *Journal of Accounting & Economics* 58(1): 41–58.** —
  post-decimalization anomaly decay (~halved).
- **McLean, R. D. & Pontiff, J. (2016). "Does Academic Research Destroy Stock Return Predictability?"
  *Journal of Finance* 71(1): 5–32.** — ~58% post-publication decay → 50–60% haircut prior.
- **IOSCO (2020, PD682) + Mar-2020 ETF-arbitrage/AP-constraint literature.** — tight ETF spreads not
  guaranteed in stress → volatility-conditional cost model (§6).

*(Della Corte et al. ≈2023 and Dai-Medhat-Novy-Marx-Rizova are NOT relied upon here: the former is a
working paper whose strongest leg is overnight/intraday — uncapturable on daily-close data; the latter
was only partially verified at S1 and must be cite-checked before any reliance.)*

---

**Disposition:** A cost-bound, mechanism-sound, genuinely-diversifying *candidate* whose viability is
decided entirely by whether a thin high-VIX liquidity-provision premium clears a volatility-conditional
cost stack on a half-length effective sample. The spec is built so the **kill is fast and honest**: if
the no-trade-band / weekly / tail-only design cannot hold net Sharpe > 0 at 2× stressed costs, or
MinBTL exceeds the high-VIX sub-sample, the strategy dies at K1/K9 — exactly as it should.
