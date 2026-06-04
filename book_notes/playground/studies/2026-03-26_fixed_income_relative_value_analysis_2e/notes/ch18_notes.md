# FIRV Chapter 18 Notes: Repo Mechanics, Haircuts, and Collateral

## Core Concept and Author Intent

Chapter 18 appears to explain the financing and collateral layer that sits underneath fixed-income relative value. The key point is that swap spreads, basis, and bond RV cannot be understood correctly unless repo and collateral mechanics are included.

The authorial intent seems to be:

1. make repo and collateral part of the analytical framework, not an afterthought
2. show how haircuts and margining affect leverage and carry
3. explain why collateral quality and regulatory treatment move spreads
4. connect these mechanics to swap spreads and basis, especially in stressed markets

This chapter is the plumbing chapter for financing reality.

## Author Intent

The chapter likely says that many apparent RV opportunities disappear or reverse once the analyst includes:

- repo funding cost
- specialness
- haircuts
- collateral scarcity

In that sense, it is a corrective chapter. It stops the reader from treating financing as a passive detail.

## Key Technicalities

### 1. Repo as the Financing Layer

Repo is the mechanism by which a bond holder turns collateral into funding. In stylized form:

$$
\text{cash received} = \text{market value of collateral} - \text{haircut amount}
$$

More explicitly, if collateral value is $V$ and haircut is $h$:

$$
\text{cash lent} = V(1-h)
$$

This immediately matters for RV because financing cost is part of the all-in trade economics.

### 2. Haircuts Set Effective Leverage

If only a fraction $1-h$ of the collateral value is financed, then the trader must fund the remainder with equity or other capital.

In a simple approximation:

$$
\text{effective leverage} \approx \frac{1}{h}
$$

So:

- low haircut -> high leverage capacity
- high haircut -> lower leverage capacity and lower capital efficiency

This is crucial for carry trades and bond RV because two trades with identical spread may have very different capital consumption.

### 3. Carry Depends on Repo

A stylized net carry expression is:

$$
\text{net carry} \approx \text{bond income} - \text{repo funding cost} + \text{roll-down} - \text{capital cost}
$$

This means a bond that appears cheap on a fitted curve may still be unattractive if:

- repo funding is expensive
- haircuts are high
- collateral is difficult to finance efficiently

### 4. General Collateral vs Specialness

Repo should not be thought of as a single funding rate. There is a distinction between:

- general collateral (GC)
- special collateral

A stylized measure of specialness is:

$$
\text{specialness} = r_{\text{GC}} - r_{\text{special}}
$$

where a large positive gap means a specific bond is especially valuable as collateral.

This matters because:

- a bond may be "rich" in yield terms partly because it earns special collateral value
- shorting that bond may be more expensive than a simple spread analysis suggests

### 5. Margining and Variation Mechanics

Collateralized financing also involves mark-to-market margining. If bond value changes, margin calls adjust the effective financed amount.

This creates a nonlinear practical effect:

- funding availability shrinks when volatility rises
- trades that look good ex ante can become difficult to hold under margin stress

So Chapter 18 likely reinforces that realized PnL is path-dependent through financing mechanics, not just through end-state prices.

### 6. Regulatory and Collateral Effects

The TOC explicitly includes regulatory considerations. That implies the chapter goes beyond pure mechanics and into structural drivers:

- HQLA demand
- collateral eligibility
- haircut schedules from central banks / clearing frameworks
- capital treatment of different assets

These factors enter fixed-income RV because they affect:

- balance-sheet usage
- funding demand for specific collateral
- equilibrium spread levels

### 7. Why Repo and Haircuts Matter for Swap Spreads

Earlier chapters connect asset-swap spreads to funding and credit. Chapter 18 adds the financing detail:

$$
\text{observed spread} = \text{pricing component} + \text{funding / collateral component}
$$

If repo and collateral conditions change, a swap spread can move even when:

- the bond's cashflows do not change
- the pure credit story does not change

That makes repo and haircut dynamics part of the explanatory model, not a trading footnote.

## How It Connects to Our Practical Notebooks

Closest notebooks:

- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)

Practical implication:

- both notebooks currently understate real-world financing complexity
- Chapter 18 tells us what must be added later:
  - repo assumptions
  - haircut assumptions
  - collateral/regulatory overlays

This chapter also informs the interpretation of [ch17_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch17_notes.md), because global bond RV cannot ignore financing differences across jurisdictions.

## Open Questions and Things to Verify Empirically

- Which repo or collateral datasets are most important to ingest first for realistic fixed-income RV?
- How sensitive are swap-spread and bond-RV signals to haircut assumptions?
- Which local or global bond trades are most exposed to specialness rather than pure curve or spread dislocation?
- Can we build a useful proxy model for funding / haircut stress before having full repo data?

## Immediate Next Steps

1. Add repo / haircut assumptions explicitly into [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb) as placeholders.
2. Use Chapter 18 as a required realism check when interpreting later bond, swap, and basis signals.
3. Consider a future repo-plumbing note or notebook once usable repo data is available.
