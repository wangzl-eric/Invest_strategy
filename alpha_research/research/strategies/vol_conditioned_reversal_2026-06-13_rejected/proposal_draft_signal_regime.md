<!-- 2026-06-14: S2 proposal draft (independent) — lens: signal construction & regime conditioning. Spec only; no code, no manifest, no runner, no ledger row. Backtest numbers do not exist yet — every Sharpe/return is a labelled EXPECTATION. -->

# S2 Proposal Draft — Vol-Conditioned Sector Reversal

> **Lens:** signal construction & regime conditioning (one of several independent S2 drafts)
> **Strategy id (proposed):** `vol_conditioned_reversal`
> **Folder:** `vol_conditioned_reversal_2026-06-13_PENDING` · **Track:** `etf_rotation`
> **Date:** 2026-06-14 · **Decision owner:** Zelin · **Stage:** S2 (independent proposal draft)
> **Scope guard:** SPEC ONLY — no code, no `manifest.yaml`, no runner, no trial-ledger row.
> **Status of every number below:** there is **no backtest of this strategy.** Every Sharpe/return
> is a reasoned **EXPECTATION**, explicitly labelled. Numbers attributed to OTHER strategies
> (`ee3a7b06`, `vix_regime`, `vol_scaled_momentum`) are HISTORICAL and labelled as such.

---

## 0. One-line thesis (carried from S0/S1, unchanged)

In high-vol regimes (VIX above its trailing 60-day median), a **dollar-neutral, cross-sectional
5-day reversal** among the liquid SPDR sector ETFs — **long the worst 5-day performers, short the
best** — earns a positive **net-of-cost** return because volatility-constrained intermediaries
withdraw liquidity and demand higher compensation to absorb uninformed sector flow (Nagel 2012).
**Falsified** if the VIX-gated L/S net Sharpe at 2× costs ≤ 0, OR it fails to beat equal-weight,
OR it is statistically indistinguishable from an *unconditional* reversal that ignores the gate.

This draft's job, through the signal-construction & regime-conditioning lens, is to pin down the
**exact signal**, **every parameter with a rationale**, and the **regime gate mechanics** such that
the strategy is fully pre-committed and look-ahead-clean before a single backtest is run.

---

## 1. Economic rationale — who loses money, and why the edge can exist

**The edge is compensation for supplying immediacy when intermediaries cannot.** In a high-vol
regime, volatility-targeting funds, dealers, leveraged-ETF hedgers, and market-neutral stat-arb
desks all hit risk limits at once and reduce inventory. The resulting one-sided *sector-level* flow
(a de-risking fund dumping cyclicals, a panic rotation into staples) pushes sector ETF prices away
from fair value over a few days. Whoever stands ready to take the other side — buy what was just
dumped, sell what was just bid — is paid an inventory/adverse-selection premium that **mechanically
scales with volatility** because that is when risk capital is scarcest and the price concession
largest. The reversal long/short *is* the liquidity-provision return.

**Who is on the other side (who loses):** forced and uninformed flow that pays to transact *now* —
vol-target deleveraging, margin-driven liquidation, leveraged/inverse-ETF daily rebalancing
(which mechanically buys winners and sells losers — the *opposite* of us — into the close), and
retail/panic sector rotation. They demand immediacy; we sell it.

**Two papers from the S1 briefing that establish this (load-bearing):**

1. **Nagel, "Evaporating Liquidity," *RFS* 25(7), 2012** (cred 5, verified). Short-term reversal
   return ≈ liquidity-provision return; expected return and **conditional Sharpe rise strongly with
   the VIX** as constrained intermediaries withdraw liquidity. **Decisively for us:** reversal
   formed from **INDUSTRY portfolios "do not yield high returns unconditionally" but DO produce high
   returns/Sharpe conditional on high VIX.** This is the literature basis for *gating* sector
   reversal on VIX rather than trading it always-on — i.e., it is the reason the gate is not a
   curve-fit but a structural prediction.
2. **Hameed, Kang & Viswanathan, "Stock Market Declines and Liquidity," *JF* 65(1), 2010** (cred 5,
   verified). Independent confirmation of the **supply-side** mechanism: negative market returns
   reduce liquidity (worse when funding is tight) and there are economically significant returns to
   *supplying* liquidity after large drops. Critically, it documents **inter-industry liquidity
   spillovers** from market-maker capital constraints — tying the mechanism to the *sector* level we
   actually trade, not just single names.

Supporting the horizon: **Lehmann, *QJE* 1990** (weekly winners reverse / losers rebound the
following week — validates the ~5-day window as the natural reversal horizon).

**The honest counter-case (S1, carried forward, not hidden):** the strongest measured results are
*single-stock* (Nagel, Lehmann, Da-Liu-Schaumburg 2014) or *index-futures overnight/intraday*
(Della Corte et al.). The peer-reviewed daily **close-to-close sector-ETF** version is essentially
untested. AP creation/redemption arbitrage keeps ETF prices tight, so the harvestable dispersion at
the ETF layer is structurally thinner than at the single-name layer (**Avramov-Chordia-Goyal 2006**:
the reversal premium is concentrated in illiquid names and there is ≈ smaller than costs even there;
sector ETFs are the *most* liquid population). **This is why the modal outcome is net Sharpe near
zero, and why this draft's signal design is built around cost minimization and the gate, not around
chasing a large gross number.**

---

## 2. The EXACT signal (this lens's core contribution)

### 2.1 Construction, step by step

For each tradeable date *t* (daily evaluation, but **traded weekly** — see §4):

1. **Raw reversal score.** For each eligible sector *i*, compute the trailing **5-trading-day total
   return** using closes available at *t*:
   `r5_i(t) = close_i(t) / close_i(t-5) − 1`.
   The reversal signal is the **negative** of this return (buy losers, short winners):
   `rev_i(t) = − r5_i(t)`.

2. **Cross-sectional demeaning (dollar-neutrality at the signal level).** Subtract the
   cross-sectional mean across the eligible universe:
   `rev_demean_i(t) = rev_i(t) − mean_j rev_j(t)`.
   This removes the common (market) component so the score reflects *relative* dispersion only —
   exactly the sector-rotation flow we are paid to absorb, not aggregate beta.

3. **Cross-sectional standardization.** Divide by the cross-sectional standard deviation to get a
   z-score `z_i(t) = rev_demean_i(t) / std_j(rev_demean_j(t))`. Standardization (not raw return)
   matters because high-VIX days have larger return magnitudes; z-scoring keeps the book's gross
   exposure stable across regimes and prevents the position size from exploding exactly when the
   tail is worst (a direct defense against the Khandani-Lo unwind, §6).

4. **Regime gate (the heart of the strategy — see §3).** Multiply the entire book by a binary gate
   `G(t) ∈ {0, 1}`: `G(t) = 1` iff `VIX_close(t) > median(VIX_close over the trailing 60 trading
   days, inclusive of t)`. When `G(t)=0` the strategy is **flat / 100% cash** — no positions, no
   turnover.

5. **Weighting to target positions (dollar-neutral L/S).** Map z-scores to weights proportional to
   the z-score, capped per name, scaled to a fixed gross exposure, and forced dollar-neutral:
   - `w_raw_i(t) = G(t) · z_i(t)`
   - **per-name cap:** clip `w_raw_i` to `[−cap, +cap]` with `cap = 0.20` of gross.
   - **dollar-neutral renormalization:** subtract the mean again post-cap so `Σ w_i = 0` exactly
     (longs fund shorts), then scale so `Σ |w_i| = GROSS` with `GROSS = 1.0` (100% gross, 50% long
     / 50% short, net 0). At our capital this is ~50% of equity long and ~50% short — well within
     IBKR Reg-T / portfolio-margin headroom and trivially executable in 11 ETFs.

**Why proportional-to-z and not pure rank (e.g., top-3 long / bottom-3 short):** with only 9–11
names, a top-k/bottom-k design throws away the magnitude of dispersion (the very thing we are paid
for) and is highly sensitive to the k cutoff (an extra free parameter the battery would perturb).
Proportional-to-z uses the full cross-section, is smooth (lower turnover than a hard rank flip when
a name crosses the cutoff), and has exactly one shape parameter (the cap). **This is a deliberate
turnover-minimizing choice**, motivated by the L7 turnover hazard and the cost-kill risk.

### 2.2 Long-only tilt vs L/S — and why this draft chooses **L/S dollar-neutral**

The PM prior is "long-only tilt 1–2% alpha, L/S 2–4%." The mechanism here is **liquidity provision
in relative sector dispersion**, which is intrinsically a *relative* bet — there is no directional
sector view. A long-only tilt around equal weight would (a) carry a large always-on market/sector
beta that swamps the thin reversal signal, (b) make the |ρ| vs `sector_rotation_v1` gate *harder*
(both become long-biased sector baskets), and (c) directly relive the `vol_scaled_momentum` trap of
a long-biased equity book whose return is dominated by beta timing, not the claimed edge. **L/S
dollar-neutral is the construction that actually tests the mechanism** (it isolates dispersion, kills
the beta, and is what the literature measures). The cost is that L/S doubles the gross turnover and
adds short borrow/financing — both are priced honestly in §7 and are the primary kill risk.

### 2.3 The Da-Liu-Schaumburg residual point — confronted, not ignored

**Da, Liu & Schaumburg (2014, *Mgmt Sci*)** decompose short-term reversal into across-industry
momentum, within-industry expected-return variation, cash-flow underreaction, and a **residual** —
and find **only the residual (reaction to recent NON-fundamental price moves) is robustly positive.**
Their result is *within*-industry (cross-sectional across stocks inside an industry). At the **sector
ETF** level we are trading the *across-industry* cross-section, where the **across-industry-momentum
term works AGAINST raw reversal** (a sector that fell over 5 days may be continuing a fundamental
trend, not mean-reverting). This is the single most important transfer risk and this draft addresses
it three ways:

- **The VIX gate IS the residual filter, by economic argument.** Da et al.'s positive residual is
  the *non-fundamental, liquidity-shock* component. High-VIX, constrained-intermediary regimes are
  precisely when 5-day sector moves are *most* dominated by non-fundamental flow (deleveraging,
  panic rotation) rather than fundamental re-rating. Gating on high-VIX is the economically-motivated
  way to select the residual-dominated days without estimating a fundamental model. **This is the
  central, falsifiable claim of the conditioning lens.**
- **Pre-committed optional momentum-neutralization variant, declared as a trial.** I pre-register a
  **secondary variant** `momentum_neutralize ∈ {off, on}` (`off` is primary). When `on`, before
  z-scoring, project the 5-day reversal score orthogonal to a 126-day (6-1) cross-sectional sector
  momentum vector — removing the across-industry momentum term Da et al. and Blitz et al. flag.
  Declaring this as a variant (not silently choosing the better one) is honest n_trials accounting:
  **both variants count toward `n_trials`** regardless of which the backtest favors.
- **The unconditional-reversal baseline (§8) is the direct empirical test:** if raw sector reversal
  is dragged to zero by across-industry momentum (as Blitz et al. 2024 predict — "naive STR loses
  partly because it bets against short-term industry momentum"), the *unconditional* arm will show
  it, and the gate's job is to rescue the residual-dominated subset.

### 2.4 Look-ahead safety (explicit, per the weights contract)

- **Weights at *t* use only data ≤ *t*.** `r5_i(t)` uses closes at `t` and `t−5` (both ≤ t). The
  function returns **unshifted** target weights; **the review engine applies the execution-convention
  shift** (`shift_bars`, default 1 → trade next bar). The signal function must NOT pre-shift (canon
  weights contract).
- **VIX gate uses VIX ≤ *t* only.** The 60-day median is a **trailing** window
  `median(VIX_{t−59..t})` — never centered, never forward. The gate at *t* uses `VIX_close(t)` and
  the 60 closes ending at *t*. With the engine's 1-bar execution shift, the position formed from
  `G(t)` and `z(t)` is *executed* at `t+1`, so even the same-day VIX close is used only to decide a
  next-bar trade — no contemporaneous-execution look-ahead.
- **VIX data convention (must be pinned at manifest time):** use **`^VIX` same-day close** (Cboe via
  yfinance, refreshed — local `vix_daily` is stale to 2026-02-27) **or FRED `VIXCLS`** (1-day
  publication lag, PIT-clean). This draft's **recommendation: `VIXCLS` via the PIT layer**, because
  (a) it is vendor-stable and the platform PIT-shifts macro by default, and (b) the 1-day lag is
  *conservative* (it can only remove information, never add it) — so the gate is provably
  look-ahead-safe even before the engine shift. If `^VIX` same-day is used instead, the engine's
  1-bar shift already prevents same-day-close-to-same-day-execution leakage; either is defensible,
  but pick ONE in the manifest and never switch silently.
- **Look-ahead unit test (pre-committed, pattern `test_no_lookahead_truncation_invariance`):**
  truncating the price/VIX history at any date *T* must leave all weights at dates ≤ *T* bit-identical
  to the full-sample run. This is the canonical guard and is a hard pre-commit.

---

## 3. Regime conditioning — the gate, in full (this lens's other core contribution)

### 3.1 Binary on/off, flat in low-VIX — and why

- **Binary, not continuous.** `G(t) ∈ {0,1}`. I deliberately reject a *continuous* gate (e.g., scale
  the book by `VIX/median` or by a sigmoid) for three reasons: (1) **mechanism** — Nagel's finding is
  that industry reversal pays *conditional on high VIX* and ≈ nothing unconditionally; a binary
  high/low split is the cleanest test of that exact claim. (2) **n_trials hygiene** — a continuous
  transform adds a shape parameter (slope/center) that the battery must perturb, inflating trials and
  inviting curve-fit. (3) **turnover** — a continuous gate produces small positions on many marginal
  days, adding cost-bleeding low-conviction trades; binary keeps us flat (zero cost) on calm days.
- **Flat / 100% cash in low-VIX.** When `G(t)=0`, **no positions, zero gross, zero turnover.** This
  is the duty-cycle that (a) decorrelates us from the always-on `sector_rotation_v1`, (b) avoids
  paying costs to harvest a premium the literature says is ≈ zero outside the gate, and (c) is the
  source of the "effective sample ≈ half the calendar" stat risk we confront head-on in §5/§9.

### 3.2 Threshold = 60-day rolling **median** (not 60th/70th percentile) — pre-committed

- **Median (50th percentile of the trailing 60-day VIX distribution).** Rationale: the median is the
  *least* parameterized regime split — it is the natural "above/below typical recent vol" line and,
  by construction, makes the gate active ~50% of the time, maximizing the effective sample (the
  binding stat constraint). A higher percentile (60th/70th) would trade *fewer*, more-extreme days —
  arguably higher per-day edge but a *shorter* effective sample and a worse MinBTL, the exact thing
  that killed `vix_regime`. **The battery will perturb the threshold ±20/40%** by construction; if
  the edge only survives at a hand-picked percentile, that is a curve-fit and a kill.
- **Trailing window = 60 trading days (~3 months).** Rationale: long enough to define a stable
  "recent normal" that does not whipsaw with a single spike, short enough to adapt to a genuine
  regime shift within a quarter. 60 days is also the canonical medium-term vol-memory window and is
  *not* tuned to the data. The battery perturbs it ±20/40% (→ 48/72 and 36/84 days); a robust edge
  must survive all four.
- **Absolute-VIX vs relative-median — pre-committed to relative.** A fixed absolute threshold (e.g.
  VIX > 20) is regime-non-stationary (20 was high in 2017, low in 2008/2020) and would bake in a
  level view. The trailing-median relative gate is self-calibrating and is the look-ahead-clean
  choice. (Pre-committed; not a free variant.)

### 3.3 "Is this just dressed-up vol timing?" — the vix_regime trap, confronted

`vix_regime` died because VIX was used as a **directional exposure scalar** on aggregate equity beta,
and a plain 21-day trailing-vol signal **dominated it** on Sharpe/DD/turnover (HISTORICAL:
trailing-vol Sharpe 0.341 vs vix_regime 0.299; spanning-alpha t = −0.18). The structural differences
here, and the pre-committed tests that prove they matter:

| Dimension | `vix_regime` (died) | This strategy |
|---|---|---|
| What VIX controls | **size of a long equity-beta bet** (timing) | **on/off switch for a dollar-neutral cross-sectional bet** (no beta) |
| Net market exposure | long-biased | ≈ 0 (dollar-neutral by construction) |
| The tradeable signal | VIX/VRP itself | the 5-day sector return **cross-section** (VIX only gates it) |
| What "winning" requires | beat trailing-vol timing | the **gate must add Sharpe over the unconditional reversal**, AND the reversal must beat a plain trailing-vol filter |

**Pre-committed discriminating tests (the gate must pass ALL, else the "vol-conditioned" claim is
falsified):**
1. **Gate adds value (P0 predicate 2, L4):** VIX-gated reversal net Sharpe **>** unconditional
   reversal net Sharpe by a meaningful margin (pre-commit ≥ +0.15 incremental Sharpe, mirroring L5's
   "overlays must ADD ≥ +0.15"). If the gate adds < +0.15, it is not earning its complexity → revert
   to plain reversal or kill.
2. **Not dressed-up vol timing (L6, the vix_regime kill):** the strategy must beat — and show
   independent spanning alpha **t ≥ 1.96** versus — a **plain trailing-vol filter** applied to the
   *same* reversal (i.e., gate on realized 21-day sector vol instead of VIX). If a cheaper vol proxy
   reproduces the result, VIX is not doing independent work.
3. **VIX is doing regime-selection, not return prediction:** the gate is binary and the book is
   dollar-neutral, so the gate cannot smuggle in a directional VIX→return bet. This is structural,
   not just empirical.

---

## 4. Rebalance frequency & no-trade band — the L7 turnover defense

**Pre-committed: WEEKLY rebalance (signal evaluated daily for the gate, positions traded weekly), with
a no-trade band.** Rationale and the L7 lesson are decisive here.

- **L7 (HISTORICAL):** daily rebalancing of a regime signal produced **2430%/yr turnover in
  `vix_regime`; weekly resampling cut it to 916%/yr.** A 5-day reversal *evaluated and traded daily*
  in high-VIX bursts is the textbook L7 hazard — and it trades exactly when spreads are widest (C6,
  IOSCO/Mar-2020). Daily trading would almost certainly drive net ≤ 0 (the modal kill).
- **The horizon and the rebalance match:** the signal *is* a 5-day reversal, so the natural holding
  period is ~5 trading days (one week). Trading weekly aligns turnover with the alpha horizon — we
  capture roughly one full reversal cycle per trade rather than churning the same view daily.
- **Engine support:** `alpha_research.review.engine.rebalance_dates(index, "weekly")` already exists
  (last trading day of each week); the weights function emits target weights only on weekly rebalance
  rows (other rows NaN = hold), exactly like the `sector_rotation` reference runner.
- **Gate timing within the week — pre-committed:** the gate `G(t)` is read **on the rebalance date
  only** (the last trading day of the week, evaluated on data ≤ t). If `G=0` on the rebalance date,
  the book goes flat for the coming week; if `G=1`, the week's target weights are set from `z(t)`.
  Intra-week the book is held (no daily re-gating), which keeps turnover bounded and is honest about
  the fact that we cannot trade the daily intraday reversal with daily-close data anyway (the Della
  Corte overnight/intraday leg is explicitly out of reach — S1 §4.5).
- **No-trade band (pre-committed):** only rebalance a name if its target weight has moved by more
  than **`band = 0.02` (2% of gross)** since the last held weight; otherwise carry the existing
  position. This suppresses cost-bleeding micro-adjustments when the cross-section is stable. The band
  is a numeric parameter → the battery perturbs it ±20/40% (→ 1.6%/2.4% and 1.2%/2.8%).
- **Turnover budget (pre-committed kill, §6):** report annualized two-way turnover; pre-commit that
  **net Sharpe at 2× costs > 0** must hold *at the realized turnover*, and flag for review if
  annualized turnover exceeds **~600%/yr** (below the 916%/yr weekly `vix_regime` figure — we are
  flat half the time, so weekly + half-duty-cycle + no-trade band should land well under that;
  exceeding it signals the design failed and is a revise/kill trigger).

---

## 5. Universe & dynamic membership

- **Universe:** the liquid SPDR sector ETFs — `XLK XLF XLE XLV XLC XLY XLP XLI XLB XLRE XLU`.
- **Dynamic membership by date (pre-committed; never backfill — that is universe look-ahead):**
  - **9 sectors** before 2015-10-08 (`XLK XLF XLE XLV XLY XLP XLI XLB XLU`),
  - **+XLRE** from 2015-10-08 (10 sectors),
  - **+XLC** from 2018-06-19 (11 sectors).
  A sector enters the cross-section only once it has ≥ 5 trading days of local history (for `r5`) and
  the gate is computed on the full universe-by-date. The reference runner's eligibility pattern
  (`mom.loc[d].notna()`) is the model: ineligible sectors get an explicit weight of 0, never a
  phantom slot. Dollar-neutral renormalization is over the *eligible* set on each date.
- **Local history:** 9 core sectors from **2012-01-03** (~14.4 yr local), XLRE 2015, XLC 2018,
  all to 2026-06-11 (S0-verified). The brief's "~1999" start is **not** in the local lake; if a
  longer sample is wanted to relieve MinBTL, sector ETF closes back to the SPDR ~Dec-1998 inception
  must be pulled (yfinance/Stooq) and QC'd — **a data task, not assumed here.** This draft specs the
  signal to run on whatever history the manifest declares; the **binding stat risk is that the
  high-VIX SUB-sample is ~half of even the available calendar** (§9).
- **VIX series:** `VIXCLS` (FRED, PIT) recommended, or refreshed `^VIX` — one, declared in manifest.
- **Adjustment:** confirm consistent total-return / split-adjusted closes across all 11 (a 5-day
  reversal is sensitive to dividend ex-dates and adjustment discontinuities); QC preflight
  (`quant_data/qc.py`) flags stale prices / extreme returns around ex-div and the 2015/2018 splices.

---

## 6. Tail risk — the short-vol signature, owned not hidden

This strategy is **structurally short-volatility / short-liquidity** (Khandani-Lo 2011, *JFM*,
verified): it earns small premia on most high-VIX days and can suffer a violent loss when a crowded
contrarian book is force-unwound (the Aug 6–9, 2007 quant quake; the Mar-2020 dislocation). **The
edge and the tail are the same trade, and we are most active precisely when the tail detonates.**
This is the defining risk and the design mitigates it explicitly:

- **z-score gross-stabilization (§2.1 step 3):** standardizing keeps gross exposure ≈ constant rather
  than scaling up with the larger high-VIX dispersion — the book does not lever into the worst days.
- **per-name cap 0.20 and dollar-neutrality:** bound single-sector and net-market blowups.
- **weekly hold (not daily):** we are not whipsawed into the bottom of a cascade and back out at
  daily frequency; but we accept we cannot dodge a multi-day unwind with daily-close data.
- **Pre-committed left-tail diagnostics (engine, conditional on VIX > median):** skew, worst-week
  return, MaxDD, and explicit inspection of the Aug-2007 and Mar-2020 windows. **Pre-committed kill
  (Gate 3 analogue): MaxDD worse than −30%** on the high-VIX-conditional path → kill. The strategy
  must be *sized for survivability of this tail*, not just average Sharpe (the `vol_scaled_momentum`
  lesson, inverted: that book was fair-weather and blew up in stress; ours claims the opposite
  direction but inherits the burden of proving the stress-state tail is survivable, not fatal).

---

## 7. Costs — volatility-conditional, the primary kill risk

Per S1 §6 and the canon (costs before alpha), **flat bps is not acceptable here** because the gate
trades when spreads/impact are widest (C1 Avramov-Chordia-Goyal; C6 IOSCO/Mar-2020 ETF dislocations).
Pre-committed cost treatment (this is a spec for the manifest's `cost_model`, evaluated by the engine):

- **Volatility-conditional spread + impact**, not flat average bps: per-name half-spread + impact
  scaled by contemporaneous VIX/realized vol, so the cost of a high-VIX trade is higher than a calm
  trade. Calibrate the calm-regime baseline to SPDR sector ETFs (among the tightest spreads on the
  tape) but **let the high-VIX multiplier do the work** the gate creates.
- **Short financing / borrow:** sector SPDRs are highly liquid, GC-easy-to-borrow → small but
  non-zero borrow + the short rebate/financing on the 50% short book must be included (the L/S draft
  cannot pretend shorts are free).
- **Battery cost sensitivity 1×/2×/3×** (standard). **Pre-committed kill: net Sharpe ≤ 0 at 2× costs
  (P0 falsification, Gate 8 analogue); net Sharpe < 0 at 3× costs is the hard auto-kill.**
- **Turnover reported and budgeted** (§4). The cost-kill and the turnover budget are the same fight.

---

## 8. Baselines to beat (pre-registered — changing these later bumps n_trials)

1. **Equal-weight buy-and-rebalance** over the same dynamic universe, same costs (L1, canon). The
   strategy must beat EW net (a dollar-neutral L/S is structurally different from EW, but EW is the
   mandated "dumbest credible alternative" floor and the |ρ|/Sharpe comparison is informative).
2. **Unconditional 5-day reversal** (identical signal, **gate removed / always on**), same costs.
   **The gate must add ≥ +0.15 net Sharpe over this** (P0 predicate 2, L4, L5). If the unconditional
   arm is ≈ zero net (as S1 §3 predicts — "decayed to zero") and the gated arm is positive, the
   conditioning thesis is supported; if the gated arm is *not* better, the thesis is **falsified**.
3. **Plain trailing-vol filter** (gate on realized 21-day sector vol instead of VIX), same signal.
   The strategy must beat this and show independent spanning alpha **t ≥ 1.96** over it — the exact
   discriminator that killed `vix_regime` (L6).
4. **(Variant control) momentum-neutralized reversal** (§2.3) vs raw — to show whether the
   across-industry-momentum drag (Da et al., Blitz et al.) is material; both count as trials.

**Additional must-measure (engine, not a baseline I choose):** **|ρ| ≤ 0.4 vs `sector_rotation_v1`**
(predicted [−0.3, +0.2] per S0 — opposite sign, different duty cycle — but UNMEASURED; both are L/S
on the same 11 sectors so a sector-dispersion regime could co-move them); spanning alpha t ≥ 1.96 vs
the unconditional reversal AND monthly momentum AND the trailing-vol filter.

---

## 9. Expected NET Sharpe (EXPECTATION — no backtest exists)

**Reasoned working estimate, labelled as an expectation, consistent with S1 §3 and the PM prior:**

- **PM prior:** long-only tilt 1–2% alpha; **L/S 2–4% alpha**; "be realistic — net could be near zero
  after costs." This draft is **L/S dollar-neutral**, so the 2–4% gross-alpha band applies *before*
  the 50–58% post-publication decay haircut (McLean-Pontiff 2016) and *before* volatility-conditional
  costs.
- **Decay (S1 §3):** the **unconditional** component is treated as decayed to ≈ 0. The **high-VIX
  conditioned** residual is the durable part (stress-state liquidity premium needing balance-sheet
  capacity), haircut ~50%.
- **My net Sharpe expectation: 0.3–0.6, centered ~0.4 — the LOW end of the platform's 0.4–0.8 band,
  with material probability of landing ≤ 0 after volatility-conditional costs.** This is an
  expectation with reasoning, NOT a backtest result. Rationale: a thin ETF-level gross premium
  (Avramov-Chordia-Goyal), a heavily-decayed unconditional base (Chordia et al., Blitz et al.), and
  high-VIX-stressed costs on a high-turnover L/S book together cap the realistic upside; the gate +
  weekly + no-trade-band design is what gives it a *chance* of clearing zero. Anything the backtest
  reports **above ~1.0 net Sharpe on this universe should be treated as a bug or look-ahead**
  (standing red flag), not skill.
- **Most likely kills (ranked):** (1) **MinBTL on the high-VIX sub-sample** — flat ~half the days
  means the effective sample is far below even the ~14 yr local calendar; `vix_regime` died at MinBTL
  3,968 yr and `sector_rotation_v1` (Sharpe 0.84, full sample) *already* fails MinBTL (HISTORICAL:
  needs 4095d vs 3485 available). A half-length L/S sample is the **single most likely kill.** (2)
  **Net Sharpe ≤ 0 at 2× costs** (the cost-of-immediacy / stressed-spread fight). (3) **|ρ| > 0.4 vs
  `sector_rotation_v1`** if a sector-dispersion regime co-moves them.

---

## 10. Pre-committed kill thresholds (this draft's hard pre-commitments)

Numeric/auto gates (engine-checked) and thesis gates, pre-committed BEFORE any backtest:

1. **DSR < 0.95** (deflated by honestly-declared `n_trials`) → kill. (Default promotion gate.)
2. **PSR < 0.90** → kill. (Default promotion gate.)
3. **Net Sharpe ≤ 0 at 2× costs** → kill (P0 falsification; Gate 8 analogue).
4. **Net Sharpe < 0 at 3× costs** → hard auto-kill (Gate 8).
5. **MinBTL exceeds available history** on the **high-VIX conditional sub-sample** → kill (Gate 7;
   the `vix_regime` killer — computed EARLY).
6. **Gate adds < +0.15 net Sharpe over the unconditional reversal** → the "vol-conditioned" thesis is
   falsified → revert to plain reversal or kill (P0 predicate 2, L4/L5).
7. **No independent spanning alpha (t < 1.96)** vs {unconditional reversal, monthly momentum /
   `sector_rotation_v1`, plain trailing-vol filter} → kill (Gate 9; the vix_regime t = −0.18 lesson).
8. **|ρ| > 0.4 vs `sector_rotation_v1`** (or any active pool stream) → portfolio-fit kill (Gate;
   default promotion gate).
9. **IS Sharpe < 0.5** (Gate 1) or **OOS walk-forward Sharpe < 0.3** (Gate 2) → kill.
10. **MaxDD worse than −30%** on the high-VIX-conditional path (Gate 3) → kill.
11. **Does not beat equal-weight net** (L1) → kill.
12. **Turnover > ~600%/yr** annualized two-way → design-failure flag → revise/kill (§4).

(1–5, 9–12 are auto/numeric; 6–8 are the thesis/spanning discriminators the PM/owner adjudicates.)

---

## 11. Parameter table — EVERY value with rationale (pre-committed; battery perturbs each ±20/40%)

| Parameter | Value | Rationale | Battery perturbation |
|---|---|---|---|
| `reversal_lookback` | **5 trading days** | The canonical short-term reversal horizon (Lehmann 1990 weekly; Nagel daily-to-weekly). Long enough to accumulate a tradeable liquidity-shock, short enough that the move is transitory not fundamental. | 4/6 (±20%), 3/7 (±40%) |
| `vix_median_window` | **60 trading days (~3mo)** | Defines "recent normal" vol; stable to single spikes, adapts within a quarter; standard medium-term vol memory, untuned. | 48/72, 36/84 |
| `vix_threshold` | **trailing 60-day median (50th pct)** | Least-parameterized regime split; ~50% duty cycle maximizes effective sample (the binding stat risk); relative (not absolute VIX) → regime-stationary & look-ahead-clean. | shift the percentile ±20/40% (→ ~40th/60th, ~30th/70th) |
| `gross_exposure` | **1.0 (100% gross: 50% long / 50% short)** | Modest, executable in 11 ETFs at 25k–100k within IBKR margin; keeps the short-vol tail bounded; not a return-scaling free parameter (it scales Sharpe-neutrally pre-cost). | 0.8/1.2, 0.6/1.4 |
| `per_name_cap` | **0.20 of gross** | Prevents one sector dominating a 9–11 name book; matches the `sector_rotation` reference cap; bounds tail concentration. | 0.16/0.24, 0.12/0.28 |
| `rebalance_frequency` | **weekly** | Matches the 5-day alpha horizon; L7 (daily → 2430%/yr; weekly → 916%/yr); cuts turnover/cost, the primary kill. | (frequency is structural, not a ±% knob; test daily & biweekly as declared trials) |
| `no_trade_band` | **0.02 (2% of gross)** | Suppresses cost-bleeding micro-rebalances when the cross-section is stable; turnover defense. | 0.016/0.024, 0.012/0.028 |
| `weighting` | **proportional-to-z, cross-sectionally demeaned, dollar-neutral** | Uses full dispersion (the paid quantity); smooth/low-turnover vs hard rank; one shape param (cap). | n/a (compare vs top-k/bottom-k as a declared trial) |
| `momentum_neutralize` | **off (primary); on (variant)** | Confronts Da-Liu-Schaumburg / Blitz across-industry-momentum drag; declared as a trial so both count toward n_trials. | n/a (binary variant) |
| `vix_source` | **`VIXCLS` (FRED, PIT) recommended** | Vendor-stable, PIT-clean, 1-day lag is conservative (cannot leak); alt `^VIX` refreshed same-day close also defensible — pick ONE in manifest. | n/a (data choice, declared) |
| `cost_model` | **volatility-conditional spread+impact + short financing** | Gate trades when spreads widest (C1, C6); flat bps would understate stressed costs. | 1×/2×/3× (standard) |
| `execution_convention` | **trade next bar (engine `shift_bars=1`)** | Weights at t use data ≤ t; engine applies the shift; function never pre-shifts (canon). | n/a (engine) |

**n_trials honesty (feeds DSR):** the declared variation set spans {reversal_lookback, vix window,
threshold percentile, gross, cap, rebalance frequency, no-trade band, weighting scheme,
momentum_neutralize on/off, vix_source}. This is a **multi-trial family**; `n_trials` must be declared
honestly (the ledger value is a FLOOR and accumulates across versions). Under-declaring n_trials to
pass DSR is the exact failure mode the canon forbids.

---

## 12. How this draft discharges the four S1 REVISE pre-commitments

| S1 §7 requirement | Where discharged in this draft |
|---|---|
| **1. Beat the gate's own null — two head-to-head baselines (unconditional reversal + trailing-vol filter) plus EW** | §8 (baselines 1–3) + §3.3 + kill #6, #7, #11; gate must add ≥ +0.15 Sharpe and beat trailing-vol with spanning t ≥ 1.96 |
| **2. Address the sector-momentum headwind (Da et al., Blitz et al.) explicitly** | §2.3 (VIX gate as the residual filter + pre-committed `momentum_neutralize` variant, declared as a trial); §8 baseline 4 |
| **3. Volatility-conditional cost model + rebalance/no-trade-band (L7)** | §7 (vol-conditional spread+impact+financing, 1×/2×/3×) + §4 (weekly + 2% no-trade band + turnover budget/kill) |
| **4. MinBTL on the high-VIX SUB-sample, computed early** | §9 (named #1 most-likely kill) + kill #5; the half-duty-cycle effective-sample problem is owned, not deferred |

**Plus the three vix_regime structural kills, mirrored:** MinBTL ≤ available history on the
sub-sample (kill #5); independent spanning alpha t ≥ 1.96 (kill #7); head-to-head win vs the simplest
baselines including trailing-vol (§8, kill #11). And the **|ρ| ≤ 0.4 vs `sector_rotation_v1`** gate
(kill #8) is the central portfolio-fit test, predicted [−0.3, +0.2] but explicitly UNMEASURED.

---

## 13. References (verified in S1 §8 — real titles/venues; safe to cite)

- **Nagel, S. (2012). "Evaporating Liquidity." *Review of Financial Studies* 25(7):2005–2039.**
  Core mechanism; industry reversal pays *conditional on high VIX*, ≈ nothing unconditionally.
- **Hameed, A., Kang, W. & Viswanathan, S. (2010). "Stock Market Declines and Liquidity."
  *Journal of Finance* 65(1):257–293.** Supply-side mechanism; inter-industry liquidity spillovers.
- **Lehmann, B. (1990). "Fads, Martingales, and Market Efficiency." *QJE* 105(1):1–28.** Validates
  the ~5-day/weekly reversal horizon.
- **Da, Z., Liu, Q. & Schaumburg, E. (2014). "A Closer Look at the Short-Term Return Reversal."
  *Management Science* 60(3):658–674.** Only the non-fundamental RESIDUAL reverses robustly;
  across-industry-momentum term works against raw sector reversal.
- **Avramov, D., Chordia, T. & Goyal, A. (2006). "Liquidity and Autocorrelations in Individual
  Stock Returns." *Journal of Finance* 61(5):2365–2394.** Reversal concentrated in illiquid names;
  net ≈ costs even there → thin gross premium at the (most-liquid) ETF layer.
- **Blitz, D., van der Grient, B. & Honarvar, I. (2024). "Reversing the Trend of Short-Term
  Reversal." *JPM* 50(6); SSRN 4575689.** STR "vanished" in most regions; naive STR bets against
  short-term industry momentum.
- **Chordia, T., Subrahmanyam, A. & Tong, Q. (2014).** *JAE* 58(1):41–58. Anomalies ≈ halved
  post-decimalization (arbitrage-capacity channel).
- **Khandani, A. & Lo, A. (2011). "What Happened to the Quants in August 2007?" *JFM* 14(1):1–46
  (NBER w14465).** The short-vol / forced-deleveraging tail of this exact contrarian book.
- **McLean, R. D. & Pontiff, J. (2016).** *JF* 71(1):5–32. ~58% post-publication decay base rate.
- **IOSCO (2020, PD682) + Mar-2020 ETF-AP-constraint literature.** ETF spreads not guaranteed in
  stress → volatility-conditional cost model is mandatory.

*(Flagged in S1 §8, NOT relied upon here: Della Corte et al. ≈2023 is a non-peer-reviewed WP whose
strongest leg is overnight/intraday — out of reach for daily-close data; the
Dai-Medhat-Novy-Marx-Rizova vol-conditioned-reversal cite was only partially verified — verify before
leaning on it; the S0 "cost-of-immediacy JBF 2022" paper is excluded pending re-verification.)*

---

### Disposition of this draft

A complete, look-ahead-clean, fully pre-committed **L/S dollar-neutral, weekly, VIX-median-gated
5-day sector reversal** spec, built through the signal-construction & regime-conditioning lens. The
signal isolates relative sector dispersion (demeaned z-score), the gate is the binary
economically-motivated residual filter (Nagel's "conditional on high VIX"), and the design choices
(weekly + no-trade band + z-gross-stabilization + dollar-neutrality) are turnover- and tail-defenses
against the named kills. **Honest expectation: low-end-of-band net Sharpe ~0.4 (range 0.3–0.6) with
material probability of dying at MinBTL on the half-length high-VIX sub-sample or at the 2× cost
gate** — exactly the outcomes the rigor battery exists to surface. The "is this just dressed-up vol
timing?" challenge is met structurally (dollar-neutral, binary gate) and empirically (must beat the
unconditional reversal by ≥ +0.15 Sharpe and a trailing-vol filter with spanning t ≥ 1.96).
