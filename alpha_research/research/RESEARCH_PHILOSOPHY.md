# Investment Research Philosophy & Methodology

> Created 2026-06-12 (Zelin, with Claude). Canonical statement of how research is done on
> this platform — synthesized from `next_gen_investment_plan.md` (the brief),
> `EXECUTION_PLAN.md` (locked decisions D1–D8), the 2026-03 PM review cycle, and the
> lessons earned from seven reviewed strategy proposals (4 rejected). Operative docs:
> `docs/guides/strategy_pool_workflow.md` (how), `STRATEGY_TRACKER.md` (history).
> Update this file when a principle changes — and log why in the tracker.

---

## 0. Document canon — this is the single source of truth

**This document is the constitution for how we invest** (the *why* — the science and the
art). It does not restate the logistics or the numbers; it **points** to them. When in
doubt, start here, then follow the map. One subject, one owning document — no duplicated
specs.

| Layer | Question it answers | Owning document |
|---|---|---|
| **Why / principles** (science + art) | *Why this edge, what rigor, what discipline* | **this file** — the constitution |
| **How it's orchestrated** (logistics) | *Which idea to work, stage flow, WIP, factory rigor* | `docs/guides/alpha_factory_workflow.md` |
| **Team collaboration & feedback** | *The adversarial challenge loop, hard-stops, who-challenges-whom, knowledge capture* | `docs/guides/alpha_factory_workflow.md` §7 + `.claude/agents/*.md` (per-role protocols) |
| **The numbers** (tunables) | *Every threshold, limit, weight, gate value* | `alpha_research/research/factory/factory_config.yaml` |
| **The commands** (hands-on) | *How to actually run manifest → review → pool* | `docs/guides/strategy_pool_workflow.md` |
| **The build plan** | *Locked decisions D1–D8, work packages, phase gates* | `EXECUTION_PLAN.md` |
| **The history** | *What was decided/changed and why, dated* | `alpha_research/research/STRATEGY_TRACKER.md` |
| **The origin brief** *(historical)* | *The original goal statement* | `next_gen_investment_plan.md` |

**Precedence when documents disagree:** numbers → `factory_config.yaml` wins (fix the
prose); locked decisions → `EXECUTION_PLAN.md` (D1–D8) wins; everything else →
**this file** wins. Any change to a principle, gate, or tunable requires a
`STRATEGY_TRACKER.md` entry.

*Superseded docs are archived under `docs/archive/` with tombstones — they are history,
not live specs: `QUANT_PLATFORM_VISION.md` (Mar-2026 platform essay) and
`RESEARCH_COLLABORATION_MODEL.md` (pre-factory, notebook-era; its 11-gate checklist and
capital policy were absorbed here and into `factory_config.yaml`).*

---

## 1. What we are building, in one paragraph

A solo-operated, milestone-gated multi-asset platform on IBKR targeting **3–4 genuinely
uncorrelated return streams** (ETF rotation, CTA futures trend/carry, factor-ETF rotation)
blended to **~10% portfolio volatility**, with per-strategy net Sharpe expectations of
**0.4–0.8** and a blended target of **0.8–1.2**. Capital is $25k–$100k. Anything claiming
more than ~1.5 net Sharpe for retail systematic trading is treated as evidence of
overfitting, not of skill.

## 2. First principles

1. **The backtest is the null hypothesis, not the evidence.** Every attractive result is
   assumed overfit until it survives the rigor battery (§4). We deflate for the trials we
   ran, not the trials we remember running.
2. **Costs and data realism come before alpha.** A strategy is its *net* return stream
   under honest costs, point-in-time data, and executable position sizes at our capital.
   This is why single-name equity L/S was cut (IBKR per-order minimums ≈ 4–5%/yr drag at
   our size) and why CTA waits for a real futures cost/roll model.
3. **Beat the dumbest credible alternative or don't ship.** Every review runs an
   equal-weight baseline automatically. Sector rotation's first honest run: Sharpe 0.84 vs
   EW 0.83 — that gap, not the 0.84, is the finding.
4. **Pre-commit, then measure.** Signal rules, parameter choices, and promotion/demotion
   thresholds are written down *before* the backtest (in the proposal and the manifest).
   Changing them afterward requires bumping `n_trials` — the deflation follows you.
5. **Economic rationale is a hard requirement.** Every proposal must explain *why the edge
   exists and who is on the other side* (risk premium, behavioral, structural/flows) with
   literature support — and Cerebro briefings must include *contradicting* evidence, not
   just confirmation.
6. **Process over outcome.** A REVISE verdict on a marginal strategy is the system working,
   not failing. We promote on rule satisfaction, demote on rule violation, and treat
   gate overrides as audited, written exceptions — never silent ones.
7. **The researcher is the scarcest resource and the biggest risk.** The agent team
   amplifies throughput, but the solo decision-maker's discretion is where overfitting,
   goalpost-moving, and narrative-fitting enter. The machinery (manifests, gates, audited
   state history) exists chiefly to constrain *us*, not the market.

## 3. The lifecycle

```
Data ──► Research ──► Registration ──► Portfolio ──► Paper ──► Live ──► Monitoring
 ▲         (idea → proposal →           (manifest →   (vol-      (ops    (rule-based
 │          weights entrypoint)          review →      budgeted   gate)   health checks,
 │                                       pool)         blend)             decay stats)
 └──────────────────────────── feedback: realized PnL, decay, regime drift ─────────┘
```

Phase status lives in `EXECUTION_PLAN.md`. Phase 1 (reproducible research loop + pool) is
implemented; Phases 2–4 (futures data + CTA/factor tracks, paper deployment, go-live +
refinement) are gated on it.

## 4. Methodology: the rigor battery

Every strategy enters the pool through one door —
`python -m alpha_research.review run <manifest>` — which enforces, in order:

| Layer | Discipline | Why it exists |
|---|---|---|
| **Data** | PIT-shifted macro (publication lags, default-on); QC preflight (missing bars, stale prices, extreme returns, coverage) | CPI look-ahead and silently stale caches are the two data failures we've actually caught here |
| **Engine** | Vectorized weights-contract backtest; weights at *t* use data ≤ *t*; execution shift applied by the engine, never by the strategy | One canonical engine, one place to audit look-ahead |
| **Baseline** | Equal-weight buy-and-rebalance over the same universe, same costs | Lesson L1/L6: most "alpha" is beta plus complexity |
| **Significance** | PSR (vs SR\*=0), DSR (deflated by declared `n_trials`), MinBTL vs sample length, block-bootstrap CI | Multiple-testing honesty; a 14-year monthly strategy with 10 trials is *marginal*, and the numbers should say so |
| **Robustness** | Cost sensitivity 1×/2×/3×; every numeric parameter ±20%/±40%; walk-forward segment Sharpes | Edges that die at 2× costs or ±20% parameters are noise |
| **Portfolio fit** | Pairwise correlation vs every active pool strategy, gate \|ρ\| ≤ 0.4 | We are buying diversification, not collecting strategies |
| **Regime honesty** | Regime-conditional Sharpe (vol terciles) | A strategy that only works in low-vol is a different product |

Default promotion gates (overridable per manifest, but pre-committed at registration):
**DSR ≥ 0.95, PSR ≥ 0.90, Sharpe > 0 at 2× costs, |ρ| ≤ 0.4 vs pool.**

**The 11-gate kill checklist** (gates 1–8 machine-checked in S5; 9–11 PM/owner judgment).
Thresholds mirror `factory_config.yaml` — **config wins on any disagreement**:

| # | Gate | Kill threshold | Owner |
|---|------|----------------|-------|
| 1 | Annualised Sharpe (IS) | < 0.5 | auto (S5) |
| 2 | Annualised Sharpe (OOS walk-forward) | < 0.3 | auto (S5) |
| 3 | Max drawdown | > −30% | auto (S5) |
| 4 | PSR vs benchmark | < 95% confidence | auto (S5) |
| 5 | Deflated Sharpe (multiple-testing corrected) | < 0 | auto (S5) |
| 6 | IS/OOS Sharpe ratio | < 0.5 (overfitting proxy) | auto (S5) |
| 7 | MinBTL (minimum backtest length) | exceeds available history | auto (S5) |
| 8 | Cost sensitivity (3× costs) | Sharpe < 0 | auto (S5) |
| 9 | Spanning-alpha t-stat vs existing streams | < 1.96 | auto (F-1) / PM until then |
| 10 | Capacity estimate at our AUM | < AUM target | PM/owner |
| 11 | Economic rationale | no credible mechanism | PM/owner |

## 5. Lessons we paid for (from rejected strategies — full detail in the tracker)

- **L1** Benchmark vs equal-weight from Round 1 — Vol-Scaled Momentum had *negative* alpha vs EW.
- **L2** Mean-variance optimization with tight constraints adds noise, not alpha; prefer ranking-based allocation.
- **L3** Vol targeting does not fix crash risk for long-only equity (backward-looking vol can't see shocks coming).
- **L4** VRP is a crisis indicator, not an alpha signal, once you control for market/momentum.
- **L5** Position-sizing overlays face a structural headwind — they must *add* Sharpe (≥ +0.15), not merely reduce drawdown.
- **L6** Always compare against the simplest alternative (VRP lost to trailing vol on every metric).
- **L7** Daily rebalancing of regime signals generates catastrophic turnover (2,430%/yr observed).

These are now structural where possible: L1/L6 are automated in the review pipeline; L7 is
why rebalance frequency is a manifest field reviewed against turnover; L2/L5 are PM-review
checks.

## 6. Portfolio construction & risk philosophy

- **Strategies are the assets.** Allocation happens over strategy return streams
  (risk-parity baseline with shrinkage, vol-targeted to ~10%), not over tickers. Capital
  fractions, not fully-invested weights — futures margin makes `Σw=1` the wrong constraint.
- **Designed for 15–20% max drawdown, survivable to 25–30%.** The vol target is the budget
  the optimizer manages to; drawdown is the constraint we size capital around.
- **Diversification is counted in correlations, not strategy count.** Three streams at
  pairwise ρ < 0.4 beat five at 0.7 — "done" is blended-portfolio behavior, not a number
  of pool entries.
- **Tax-aware tilt (taxable account):** futures get 60/40 treatment; monthly-turnover ETF
  strategies generate short-term gains — a structural argument for weighting the CTA track
  up at equal expected Sharpe.

## 7. Deployment & promotion philosophy

- **Paper trading validates operations and consistency, not performance.** 3–6 months of
  daily returns cannot statistically separate Sharpe 0.8 from 0. The `paper → live` gate is
  therefore: a clean unattended-ops record, returns within the backtest's PSR confidence
  band, realized vol within ±25% of design, zero unexplained reconciliation breaks.
- **Capital ramps 25% → 50% → 100%**; live capital touches only promoted strategies.
- **Demotion is mechanical.** Retire/refit rules are written in the manifest at
  registration; monthly health reports (decay rate, half-life, tracking error) trigger
  them. Overrides require a written, audited reason in the pool's state history.

## 8. Division of labor

| Who | Owns |
|---|---|
| **Zelin (solo PM/owner)** | All go/no-go decisions: promotion, demotion, capital, data spend, design changes (D1–D8) |
| **Researchers (Elena/Marco)** | Hypotheses, proposals, signal design — every claim challenged in the v2 loop |
| **PM agent** | Adversarial review; realistic alpha haircuts; verdict recommendations |
| **Cerebro** | Literature briefings incl. *contradicting* evidence (currently frozen as a build target, D8) |
| **Dev/Codex** | Framework integrity, execution, test coverage — the machinery that makes rigor cheap |

The review pipeline renders verdicts; **only the human promotes.**

## 9. Standing red flags

Treat any of these as a stop-and-investigate, regardless of how good the headline looks:

- Net Sharpe > 1.5 on a daily/monthly retail strategy → assume overfitting or a data bug.
- Backtest improves when costs are added, or is insensitive to 3× costs → engine bug.
- Strategy Sharpe ≫ equal-weight baseline with long-only construction → check for a
  hidden beta or look-ahead.
- Macro signal that "works" with raw FRED reference dates but dies PIT-shifted → it was
  never real.
- A trend strategy uncorrelated (< 0.3) with the SG Trend index → broken data or broken
  signal, not originality (Phase 2 check).
- The urge to relax a gate *after* seeing the result it blocks — that urge is the
  documented failure mode this entire document exists to prevent.
