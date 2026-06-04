# FIRV Chapter 10 Notes: Overview of the Following Chapters

## Core Concept and Author Intent

Chapter 10 is a transition chapter. Its function is to bridge the book from:

- Part I: statistical models
- Part II: pricing and curve-model tools

into the market-application chapters on:

- reference rates
- asset swaps
- basis swaps
- credit default swaps
- their mutual interactions

The authorial intent is to stop the reader from treating those later chapters as isolated product notes. The authors frame the entire "swap block" as one connected system whose logic starts from funding and cash-flow decomposition.

## Author's Transition Framing

The transition is built around one key conceptual move:

$$
\text{bond financed in repo} \approx \text{receive coupon (fixed)} - \text{pay repo (floating)}
$$

Once that equivalence is accepted, later market chapters become easier to read because:

- asset swap spreads become funding-rate spreads
- basis swaps become links across reference-rate conventions
- CDS becomes the credit leg that connects into the same system

So Chapter 10 is less a technical pricing chapter than a map for how to think across the following chapters.

## Key Technicalities

### 1. Bond-as-Swap Equivalence

Buying a bond and financing it through repo can be viewed as:

$$
\text{receive coupon} - \text{pay repo}
$$

That is the conceptual anchor for the whole swap block.

### 2. Asset Swap Interpretation

If an asset swap exchanges coupon for a floating reference rate, then the combined package becomes approximately:

$$
\text{asset-swapped bond} \approx \text{receive reference rate} - \text{pay repo}
$$

So the swap spread is naturally interpreted as a basis between:

- the bond's funding rate
- the swap's floating reference rate

### 3. Why Later Chapters Must Be Read Together

The chapter text makes clear that swap-spread analysis contains at least two conceptual pieces:

$$
\text{swap spread} \approx \text{funding component} + \text{credit component} + \text{residual structural effects}
$$

That is why the later chapters need to cover:

- reference rates
- basis swaps
- CDS
- cross-currency links

as one interdependent block.

### 4. Global Linkages Matter

The chapter emphasizes that bonds, asset swaps, basis swaps, and CDS are globally connected. In conceptual form:

$$
\text{local bond RV} \leftrightarrow \text{asset swap} \leftrightarrow \text{basis swap} \leftrightarrow \text{CDS / credit}
$$

This is the key transition from model chapters to market chapters: practical relative-value analysis now depends on plumbing, not just on statistical signals or fitted curves.

## How It Connects to Our Practical Notebooks

Chapter 10 is primarily conceptual, but it frames how we should interpret:

- [04_asset_swaps.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/04_asset_swaps.ipynb)
- [05_cross_currency_basis.ipynb](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/05_cross_currency_basis.ipynb)

and the later chapter notes:

- [ch11_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch11_notes.md)
- [ch12_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch12_notes.md)
- [ch13_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch13_notes.md)
- [ch15_notes.md](/Users/zelin/Desktop/PA Investment/Invest_strategy/workstation/playground/studies/2026-03-26_fixed_income_relative_value_analysis_2e/ch15_notes.md)

Practical implication:

- later market notebooks should eventually be connected through a shared funding / credit decomposition rather than treated as isolated studies.

## Open Questions and Things to Verify Empirically

- How much of observed asset-swap variation in practice is funding, how much is credit, and how much is residual market structure?
- When we eventually ingest the missing data, can we turn the chapter's "driver map" into a factor decomposition for swap spreads?
- Which later-market relationships are most useful to prototype first in the playground: reference-rate spreads, asset swaps, or cross-currency basis?
