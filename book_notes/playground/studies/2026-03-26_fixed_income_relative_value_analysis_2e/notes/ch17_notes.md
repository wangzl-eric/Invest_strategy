# FIRV Chapter 17 Notes: Global Bond Relative Value via Fitted Curves and SOFR ASW Spreads

## Core Concept and Author Intent

Chapter 17 appears to be the culmination of the fitted-curve, asset-swap, and basis chapters. The core idea is that global bond relative value should not be done in purely local yield terms. Instead, bonds should be compared:

- after adjusting for fitted-curve richness / cheapness within each market
- after converting local funding/spread packages into a common basis, notably via SOFR asset-swap logic

The authorial intent seems to be:

1. extend single-market bond RV into a cross-market framework
2. use fitted curves for within-market screening
3. use SOFR-based asset-swap spreads as a cross-market comparison language
4. show why swap spreads can become a global rich/cheap indicator once the reference-rate problem is handled correctly

## Author Intent

The chapter is trying to unify the previous tools:

- Chapter 8 fitted curves for local bond selection
- Chapter 10–16 swap/basis logic for cross-market comparability

The point is not merely to say "Bunds are rich vs Treasuries." It is to say:

- which bond is rich or cheap versus its own local fitted curve
- which market is rich or cheap after funding and basis adjustment
- how those two layers interact in a practical global RV screen

## Key Technicalities

### 1. Two-Layer Relative Value

The chapter's practical setup appears to have two layers:

#### Within-market RV

Use a fitted local curve to compute:

$$
\varepsilon_i = P_i^{\text{market}} - P_i^{\text{fitted}}
$$

or the analogous residual in spread / basis-point terms.

This identifies whether an individual bond is rich or cheap versus its local curve.

#### Cross-market RV

Then compare bonds or benchmark packages across countries on a common funding basis.

This is the key transition from domestic curve analysis to global bond RV.

### 2. SOFR ASW as Common Comparison Language

The chapter title strongly suggests the common comparison metric is the SOFR-referenced asset-swap spread.

Conceptually:

$$
\text{Global RV metric} \approx \text{local ASW} + \text{basis adjustment into SOFR terms}
$$

This matters because local swap spreads are not directly comparable across markets if:

- reference rates differ
- secured/unsecured conventions differ
- basis wedges are ignored

Using a common SOFR-style lens is meant to make global bond comparison more coherent.

### 3. Basis-Swapped Bond Comparisons

The chapter likely assumes that a foreign bond can be transformed into a USD/SOFR comparison framework through basis and funding adjustments.

Stylized:

$$
\text{Bond value on common basis} =
\text{local bond package} + \text{cross-currency basis transformation}
$$

This links directly back to Chapter 15 and Chapter 16.

The practical point is that:

- local yield alone is not enough
- local asset swap alone is not enough
- global RV requires the full funding path into a common comparison metric

### 4. Why Fitted Curves Still Matter

Chapter 17 does not replace local fitted-curve analysis; it layers on top of it.

The local fitted curve provides:

- bond-specific rich/cheap residuals

The SOFR ASW framework provides:

- market-level comparability across issuers and currencies

So a high-conviction trade may require both:

$$
\text{signal quality} \uparrow
\quad \text{if} \quad
\text{bond cheap on local curve} \;+\; \text{market cheap on common SOFR basis}
$$

### 5. Limits of Swap Spreads as Global Indicators

The TOC explicitly mentions "problems with the use of swap spreads as relative value indicators for bonds." That implies the authors do not treat SOFR ASW as perfect.

Likely issues:

- residual balance-sheet and collateral effects
- country-specific liquidity and scarcity
- central-bank distortion
- bond-specific specialness
- credit differences that are not fully normalized away

So the chapter likely argues:

- SOFR ASW is useful as a global comparison tool
- but still must be interpreted with structural caution

### 6. Interaction with Structural Distortions

The chapter sits after the basis and equilibrium chapters, so it likely assumes that global bond RV is shaped by:

- QE / central-bank ownership
- safe-asset scarcity
- regulatory HQLA demand
- balance-sheet cost

That means a large cross-market wedge is not automatically a short-horizon convergence trade. It may be a structural premium.

## How It Connects to Our Practical Notebooks

Primary notebook:

- [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb)

Secondary notebooks:

- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)

Practical implication:

- Chapter 17 is where these notebooks should eventually converge into one multi-layer workflow:
  1. local fitted residual
  2. asset-swap transformation
  3. basis adjustment
  4. common-currency comparison

We do not yet have the full data stack for that.

## Open Questions and Things to Verify Empirically

- Once swap/basis data is available, which sovereign markets look cheapest on a common SOFR basis?
- How often does local fitted-curve cheapness agree with global SOFR-ASW cheapness?
- Which part of a global wedge is structural and which part is likely to mean revert?
- Are SOFR-based global comparisons materially better than local spread comparisons for predicting subsequent RV convergence?

## Immediate Next Steps

1. Extend [03_fitted_curves.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/03_fitted_curves.ipynb) so local residual ranking is robust.
2. Keep [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb) and [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb) aligned with this eventual global comparison framework.
3. Treat Chapter 17 as the destination architecture for a future integrated global bond RV notebook.
