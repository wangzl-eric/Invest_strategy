# Chapter 9 Notes: Analytic Process for Government Bond Markets

**Book:** Fixed Income Relative Value Analysis (Huggins & Schaller, 2nd ed., 2024)
**Chapter:** 9 — Analytic Process for Government Bond Markets
*Notes by Cerebro — 2026-03-26*

---

## Chapter Argument Arc

Ch9 is the synthesis chapter of Part II. It shows how to combine the tools from Ch3
(PCA), Ch6 (yield curve models), and Ch8 (fitted curves) into a **systematic, repeatable
process** for identifying which individual government bonds are rich or cheap relative to
their fitted curve — and then constructing trades that are neutral to the dominant
risk factors (level, slope, curvature).

The chapter answers: *given a fitted yield curve and a PCA decomposition, how do you
go from "this bond looks cheap" to a structured, factor-hedged trade?*

---

## 1. The Analytic Process: Overview

The process has five steps:

1. **Fit the curve** — Use a discount function (NS, Svensson, or cubic spline) to fit
   the on-the-run and off-the-run government bond universe. Obtain a smooth theoretical
   yield for every maturity.

2. **Compute fitting residuals** — For each bond, compute:
   $$\text{residual}_i = y_i^{\text{market}} - y_i^{\text{fitted}}$$
   A positive residual = bond yields more than the curve predicts = **cheap**.
   A negative residual = bond yields less = **rich**.

3. **Decompose residuals by PCA factor** — Project the residual vector onto the PCA
   factor loadings (level, slope, curvature). Identify whether cheapness is:
   - Idiosyncratic (bond-specific liquidity, supply/demand)
   - Factor-driven (residual is correlated with a PCA shift)

4. **Select trade pairs** — Find two bonds where one is cheap and one is rich on the
   same sector of the curve, so that a spread trade captures the richness/cheapness
   while cancelling most factor exposure.

5. **Hedge residual factor exposure** — Use DV01 weighting + PCA factor loadings to
   construct weights that are neutral to level, slope, and curvature simultaneously.

---

## 2. Factor-Neutral Hedge Construction

### DV01 Neutrality (Level Hedge)

A DV01-neutral spread between bond $A$ (cheap) and bond $B$ (rich) requires:

$$w_A \cdot \text{DV01}_A = w_B \cdot \text{DV01}_B$$

This cancels the **level** (parallel shift) exposure. But the trade still has slope
and curvature exposure if the two bonds sit at different maturities.

### PCA Factor Neutrality

Let $f_k(\tau)$ be the loading of maturity $\tau$ on PCA factor $k$. For a portfolio
of $N$ bonds with face amounts $w_i$, factor $k$ exposure is:

$$F_k = \sum_i w_i \cdot \text{DV01}_i \cdot f_k(\tau_i)$$

For a three-factor neutral trade, solve the system:
$$F_1 = 0,\quad F_2 = 0,\quad F_3 = 0$$

This requires at least **four bonds** (one equation per factor + the long/short
constraint). In practice, practitioners often relax curvature neutrality and use
three bonds (DV01 + slope neutral), accepting residual curvature risk.

### Butterfly Trades as Factor-Hedged RV

A **butterfly** (long belly, short wings) is the canonical factor-hedged vehicle:
- Long the bond that is cheap relative to fitted curve at the belly maturity
- Short two bonds (wings) that are rich, weighted to be DV01 and slope neutral
- Net exposure: approximately curvature-neutral if weighted correctly

The P&L driver is **convergence of the fitting residual**, not directional rate moves.

---

## 3. Bond Selection Criteria

Not all fitting residuals are worth trading. Ch9 applies filters:

| Criterion | Description |
|-----------|-------------|
| **Liquidity** | On-the-run bonds are most liquid; off-the-run residuals may reflect a liquidity premium, not a true mispricing |
| **Financing cost** | Special repo bonds trade at lower repo rates (lending them is cheap); the specialness offsets apparent cheapness in yield space |
| **Supply technicals** | Large new supply in a maturity sector can make nearby bonds appear cheap temporarily |
| **Residual persistence** | A residual that has been positive for months may reflect a structural premium, not a convergence opportunity |
| **Roll-down** | A cheap bond with favorable roll-down has carry support; prefer trades where carry and mean reversion point the same way |

---

## 4. Ex Ante Risk-Adjusted Return

Ch9 introduces the **ex ante Sharpe ratio** as the selection metric:

$$\text{SR}_{\text{ex ante}} = \frac{E[\Delta P]}{\sigma[\Delta P]}$$

Under the Vasicek/OU framework (Ch2), if the fitting residual $x_t$ follows OU with
mean reversion speed $\kappa$ and long-run mean $\bar{x} = 0$:

$$E[x_{t+h} - x_t] = (e^{-\kappa h} - 1)\,x_t \approx -\kappa h\,x_t \quad \text{(for small }h\text{)}$$

$$\text{Var}[x_{t+h}] = \frac{\sigma^2}{2\kappa}(1 - e^{-2\kappa h})$$

The ex ante Sharpe is maximized at horizon $h^* = 1/\kappa$ (one half-life).
This gives a principled way to choose trade horizon — not arbitrary.

---

## 5. Macro Context and the Analytic Process

The analytic process is not purely mechanical. Ch9 emphasizes:

- **Macro regime matters:** If the central bank is in an aggressive hiking cycle,
  the slope factor is systematically shifting. A slope-neutral trade may still have
  P&L driven by regime change. Overlay Kim-Wright term premia to assess regime.
- **Fitting model risk:** Different curve models (NS vs. Svensson vs. spline) give
  different residuals for the same bond. Use at least two models and only trade
  residuals that are consistently rich/cheap across specifications.
- **Cross-market opportunities:** The same process applies across sovereign markets.
  A German Bund that is cheap vs. French OATs on a fitted-curve basis is a cross-market
  RV trade — Ch4's multivariate mean reversion is the statistical foundation.

---

## Connection to Other Chapters

| Chapter | Role in the Analytic Process |
|---------|------------------------------|
| **Ch3 — PCA** | Provides the factor loadings used to construct factor-neutral hedge ratios |
| **Ch6 — Yield Curve Models** | Provides the ex ante expected return model (affine dynamics, risk-neutral vs. physical measure) |
| **Ch8 — Fitted Curves** | Provides the theoretical yield and fitting residual for each bond |
| **Ch2 — Mean Reversion** | Calibrates $\kappa$ and $\sigma$ of the residual process; sets optimal trade horizon |
| **Ch4 — Multivariate** | Extends the process to cross-market spreads |
| **Ch12 — Asset Swaps** | ASW spreads can substitute for yield fitting residuals in the RV selection step |

---

## Key Takeaways

1. **Fitting residuals are the raw material.** The analytic process converts a yield curve
   fit into actionable cheapness/richness signals for individual bonds.
2. **Factor neutrality is non-trivial.** DV01 neutrality is necessary but not sufficient.
   Full PCA factor neutrality requires at least four bonds and explicit factor loading math.
3. **Carry and convergence must align.** A cheap bond with negative carry will underperform
   unless mean reversion is fast enough to overcome the carry drag.
4. **The process is iterative.** Macro context, liquidity screens, and model robustness
   checks filter the initial set of candidates. The trade list is never just "all positive residuals."
5. **Cross-market is the frontier.** Once the single-curve process is mastered, extending
   to multi-country spreads (Bunds vs. OATs, USTs vs. JGBs) opens the richest RV universe.

---

*Cerebro — 2026-03-26 | FIRV study: Ch9 Analytic Process*
