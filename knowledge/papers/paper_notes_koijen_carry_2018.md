# Paper Notes: Carry

**Authors:** Ralph S.J. Koijen, Tobias J. Moskowitz, Lasse Heje Pedersen, Evert B. Vrugt
**Year:** 2018 | **Journal:** Journal of Financial Economics, 127(2), 197–225
**DOI:** 10.1016/j.jfineco.2018.04.002
**Scores:** Credibility 5 | Relevance 5 | Actionability 5

> **Canonical merged note.** Surfaced independently while studying three books —
> *Expected Returns* (Ilmanen), *Fixed Income Relative Value Analysis* (Darbyshire),
> and *Global Macro Trading* (Gliner). The per-book "connection" tables are preserved
> below under **Cross-Book Context**. Linked from each book's `reading_queue.md`.

---

## Core Thesis

Carry — the return an investor receives if prices stay the same — is a pervasive,
economically large predictor of returns **across all major asset classes**. A single,
unified carry definition unifies seemingly disparate phenomena (FX carry trade,
commodity roll yield, bond term premium, equity dividend yield) into one framework.
Carry strategies earn significant risk-adjusted returns that cannot be explained by
standard risk factors, and their co-movement across asset classes suggests a common
**global carry factor** rather than asset-class-specific mechanisms.

---

## Definition of Carry

For any asset, carry is the **expected return if spot prices remain unchanged**:

$$C_t = \frac{F_t - S_t}{S_t} \approx \text{futures basis} = \text{cost-of-carry residual}$$

More precisely, carry of holding the asset financed at the risk-free rate is:

$$C_t = \frac{\text{Income}_t + \text{Roll Return}_t}{P_t}$$

where **Income** = dividends, coupons, or convenience yield, and **Roll Return** =
gain/loss from the passage of time on the futures curve (positive in backwardation,
negative in contango). Carry is **observable today** — it requires no price forecast.
It is a sufficient statistic for expected returns under a random-walk assumption on spot.

| Asset Class | Carry Measure |
|-------------|---------------|
| FX | Interest rate differential (covered interest parity / forward premium) |
| Equities | Dividend yield minus risk-free rate (or futures basis) |
| Fixed Income | Yield + roll-down minus financing; slope of yield curve |
| Commodities | Roll yield (spot-to-futures basis; convenience yield minus storage) |
| Credit | Credit spread above risk-free |
| Options | Variance risk premium (implied minus realized vol) |

---

## Fixed-Income Carry Deep-Dive (from FIRV reading)

For a bond with yield $y(\tau)$ at maturity $\tau$:

$$\text{Bond Carry} = y(\tau) + \underbrace{\frac{\partial y}{\partial \tau}\Big|_{\tau}\cdot(-1)}_{\text{roll-down}} - r_f$$

- $y(\tau)$ = current yield (income component)
- Roll-down = yield change as the bond ages one period along a static curve
  (positive if upward sloping — bond rolls to a lower yield = price gain)
- $r_f$ = financing rate (repo / SOFR)

**Example.** 10Y Treasury yielding 4.5%, 9Y yield 4.3% (normal curve), SOFR 5.3%:
income carry = 4.5%, roll-down = +20bps, financing = 5.3% → **net carry = −0.6%**
(funding cost exceeds income). In an *inverted* curve both income and roll-down are
negative for long duration — double-negative carry, which is why carry was deeply
negative for US Treasuries in 2022–2023.

Key FIRV takeaway: **roll-down is part of carry, not a separate concept.** Both income
and roll-down are returns "if prices don't change"; the combined carry is the correct signal.

---

## Data and Methodology

- **Period:** 1972–2012 (40 years), asset-class-specific start dates.
- **Universe:** 8 asset classes, 50+ instruments — FX (10–36 currencies vs USD),
  equity index futures (18 markets), government bond futures (10 markets), commodity
  futures (24–26), credit (CDX IG/HY), equity-index options (S&P 500 + others).
- **Construction:** within each asset class, sort by carry monthly → long top tercile,
  short bottom tercile (rank/vol-weighted); scale each asset-class carry portfolio to
  ~10% vol; combine across classes with equal-vol weights; rebalance monthly.
- **Tests:** panel predictive regressions; factor-model spanning regressions
  (Fama-French, momentum, value, BAB, QMJ); crash risk via realized skewness, tail
  beta, option-implied measures.

---

## Key Empirical Findings

**1. Carry predicts returns in every asset class.** Panel-regression coefficient on
carry ≈ 1.0 (carry ≈ expected return): FX ~0.97, commodities ~1.2, equities ~0.85,
fixed income ~0.90.

**2. Carry portfolio Sharpe ratios (long-short):**

| Asset Class | Sharpe | t-stat |
|-------------|--------|--------|
| FX / Currencies | ~0.69–0.70 | 3.8 |
| Fixed Income | ~0.50–0.55 | 2.9 |
| Equities | ~0.44–0.45 | 2.6 |
| Commodities | ~0.40–0.41 | 2.3 |
| **Global Diversified** | **~0.80–0.81** | 5.1 |

Diversification benefit is large — combined Sharpe far exceeds any single class.

**3. Not explained by standard factors.** Alphas survive market beta, size, value,
momentum, liquidity, BAB, QMJ. CAPM betas are low and mostly insignificant.

**4. A global carry factor exists.** Carry portfolios are positively correlated across
classes (avg pairwise ~0.15–0.30); the first PC explains a disproportionate share of
variance. The global factor earns SR ~0.81 with near-zero skewness once diversified.

**5. Crash risk is the price.** All carry strategies show negative skewness + high
kurtosis. FX carry skew ~−0.8 (high-yielders depreciate sharply in crises). Canonical
crashes: FX carry 2008; bond carry 1994 and 2022. Global diversification offsets much
of the single-asset crash risk but not a severe joint crisis (2008).

**6. Carry vs momentum/value.** Distinct (corr ~0.10–0.30); combining carry + momentum
+ value improves Sharpe further (multi-style diversification).

---

## Theoretical Explanations (paper is deliberately agnostic)

- **Risk-based:** global crash/liquidity risk; rare-disaster premium (Gabaix,
  Brunnermeier); intermediary capital constraints (He–Krishnamurthy).
- **Behavioral:** trend-following amplification; peso problem / under-weighted tails;
  inattention / slow-moving capital.
- **Position:** risk and behavior both contribute; no single model explains the global
  co-movement — an open research question.

---

## Replication Potential (This Codebase)

| Asset Class | Data Available | Carry Signal | Verdict |
|-------------|---------------|--------------|---------|
| FX (G10) | FRED + ECB FX | Interest-rate differential | **High** |
| Fixed Income | FRED yield curve | Yield + rolldown | **Medium** |
| Commodities | Stooq / futures | Front/second roll yield | **Medium** |
| Equities (index) | Stooq | Dividend yield / basis | **Low** (no div-yield series) |

**Recommended order:** (1) FX carry — fully feasible via FRED rates + ECB FX connector;
(2) fixed-income carry — yield curve partly implemented, add rolldown; (3) commodity
carry — needs futures-chain (near/far) data; (4) equity carry — blocked on dividend-yield pipeline.

**Code pointers / gaps:**
- `backtests/strategies/signals.py` — add a real `FXCarrySignal` (FRED rate differentials).
  The existing `CarrySignal` is a momentum proxy, **not** true carry — mis-named, must be
  replaced before any carry strategy goes live.
- `quant_data/connectors/ecb_fx.py` — G10 FX spot.
- `quant_data/connectors/polygon.py` — potential futures-chain source.

```python
def bond_carry(yield_tau, yield_tau_minus_1, repo_rate, dt=1/12):
    """Annualized bond carry: income + roll-down - financing."""
    income = yield_tau
    roll_down = yield_tau - yield_tau_minus_1  # +ve if curve upward sloping
    return income + roll_down - repo_rate
```

---

## Cross-Book Context

**Connections to FIRV (Darbyshire) chapters**

| Chapter | Connection |
|---------|------------|
| Ch12 — Asset Swaps | ASW spread = carry component of a bond position; Koijen unifies into one carry framework |
| Ch9 — Analytic Process | Carry is the second pillar alongside fitting residuals; high-conviction = positive carry AND cheap residual |
| Ch5 — Yield/Duration/Convexity | Roll-down needs duration-aging; convexity affects roll-down for long-dated bonds |
| Ch20 — Broader Perspective | Global carry factor links FIRV to multi-asset construction (rates + FX + credit) |

**Connections to Global Macro Trading (Gliner) chapters**

| Chapter | Connection |
|---------|------------|
| Ch4 — Building blocks | Carry is the unifying signal across all four asset classes |
| Ch6 — Systematic trading | Multi-asset carry factor is a direct implementation of Gliner's systematic framework |
| Ch7 — FX | Interest-rate differentials = FX carry; most liquid, widely traded |
| Ch10 — Commodities | Roll yield = commodity carry; backwardation signals high expected carry |
| Ch11 — Central banks | Rate policy sets FX carry levels; QE compressed carry by flattening curves |

**Connections to Expected Returns (Ilmanen):** carry is one of Ilmanen's four major
return drivers (carry, value, momentum, liquidity); this paper is the cross-asset
empirical backbone for the "carry" chapter.

---

## Critical Assessment

**Strengths:** unified definition across 8 classes; 40-year broad sample mitigates
snooping; survives realistic costs in most classes; the global-factor co-movement
reframes the question from "why FX carry" to "what global risk does carry compensate."

**Weaknesses:** commits to no single mechanism; post-publication decay (carry was
well-known since Lustig et al. 2011, weaker out-of-sample); equity-index carry is the
weakest and most definition-sensitive (~0.44); long-short assumption is inaccessible to
long-only investors; global-diversification crash argument is empirical, not guaranteed
(all carry can crash together, 2008).

---

## Key Takeaways for Research Pipeline

1. Carry is a genuine, multi-asset risk premium — 40-year cross-section is hard to dismiss.
2. **Diversification is the killer app** — single-asset SR 0.4–0.7 → diversified ~0.81.
3. Carry and momentum are complementary (corr ~0.15–0.30) — supports an FX Carry + Momentum strategy.
4. FX carry crash risk is real but manageable via cross-asset diversification + a momentum filter + vol-targeting.
5. The global carry factor is **unexplained** — open edge for whoever prices it.
6. Compute carry from futures basis / rate differentials, **never** from price momentum.

---

## Open Questions / Follow-Up

- [ ] Does the global carry factor subsume HML_FX, or are they orthogonal?
- [ ] How does carry perform 2012–2025 (post-paper out-of-sample)?
- [ ] Can rolldown be cleanly computed from FRED yield-curve data for a fixed-income carry signal?
- [ ] Does carry × momentum (high carry AND positive momentum) beat carry alone on crash-adjusted returns?
- [ ] Is crypto carry (funding-rate differential) viable from Binance public data?

---

## Adjacent Papers

Fama (1984) forward premium puzzle · Fama & Bliss (1987) · Cochrane & Piazzesi (2005) ·
Lustig, Roussanov & Verdelhan (2011) HML_FX · Asness, Moskowitz & Pedersen (2013)
value & momentum everywhere · Brunnermeier, Nagel & Pedersen (2008) carry-trade crashes ·
Gorton & Rouwenhorst (2006) commodity futures.

## Citation

Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., & Vrugt, E. B. (2018). Carry.
*Journal of Financial Economics*, 127(2), 197–225.
