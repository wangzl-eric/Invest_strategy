---
type: concept
id: CONCEPT-010
slug: free-float-and-price-insensitive-holders
domain: rates
status: stable
sources: 3
---

# CONCEPT-010 · free float and price-insensitive holders

**Definition.** The quantity that prices a bond market is not the amount outstanding but the amount held
by investors who *can* say no. Central-bank QE stock, mandated pensions and liability-matching insurers
remove the elastic part of supply. The same absolute flow moves price more, the smaller the free float.

## The arithmetic

$$\text{free float} = \text{outstanding} - \sum \text{price-insensitive holdings}$$

$$\text{impact (bp)} = \underbrace{\frac{\Delta Q}{\text{free float}}}_{\text{ppt of float}} \times \underbrace{\beta}_{\text{bp per ppt, market- and regime-specific}}$$

**Both factors must be estimated, and errors in opposite directions are invisible in the product** — the
corollary that generalises beyond bonds: whenever a headline number is the product of two independently
estimated inputs, verify each separately.

Worked instance: GPIF JGB holdings ≈ USD 643bn at "~5% of the market" implies a USD 12.9tn market; less a
~50% BoJ holding gives free float ≈ USD 6.4tn; so USD 75bn is **1.17ppt**, worth **1.2bp** at $\beta = 1$
— against a printed **3–6bp**, which requires $\beta_{\text{eff}} = 2.6$–$5.1$. The published $\beta$ was
invoked twice with no sample period, estimation window, functional form, standard error or citation, and
transplanted from UST/Bund/Gilt against the note's own concession that JGB supply sensitivity is
historically lower.

## Reading demand from the maturity ladder

A holder's *stated* policy is weaker evidence than the drift in its portfolio weighted-average maturity.
Roll-down mechanically shortens a static portfolio by one year per year, so **holding WAM flat requires
continuously buying longer** — and observed WAM drift is a direct read on the replacement rate of the
holder's long-end bid.

GPIF's JGB WAM fell 10.7y (2020) → 9.7y (2026): a ~83% replacement rate, so the holder is a **net
supplier of duration even while a net buyer of bonds**. That is the cleanest available falsification of
any "constrained buyer supports the long end" story. → [IDEA-030](../../reports/IDEAS.md#idea-030)

## Why it persists

The denominator requires netting officially-disclosed-with-lag holdings, and almost nobody rebuilds it.
The holders themselves are named and constrained by regulation — solvency rules fix insurers' liability
duration; statutory bands fix a sovereign fund's weights; a central bank's taper is on a published
schedule. **None of them can decline to trade**, which is what makes the flow forecastable and the
sector-level claim durable even though the calendars are public.

## How to measure it here

| Route | Status |
|---|---|
| `WSHOMCB`, `TREAST` (SOMA holdings) | in `fed_liquidity.parquet` but raise `ValueError` — registry gap |
| `GFDEBTN`, US Treasury Fiscal Data | public, **unregistered** |
| NY Fed SOMA holdings **by maturity bucket** | weekly, public, no connector — the cleanest test bed |
| GPIF annual ISIN-level holdings | public since 2019, needs a scraper |
| MoF JGB outstanding, BoJ holdings, JPY swap curve | **entirely absent** — the JGB side cannot be checked at all |
| `fed_liquidity.parquet` coverage | **2024-02 onward only** |

The US analogue is reachable; the market the source analysed is not.

## Where it fails

- **$\beta$ does not transfer.** Post-2008 the basis is set by intermediary balance-sheet capacity
  (dealer balance sheets, G-SIB surcharges) at least as much as by supply, so a beta estimated in one
  regime cannot be carried to another — and $\beta$ is the parameter carrying the number.
- The link from a slowly drifting replacement rate to realised curve shape is **established nowhere** —
  many other duration suppliers and demanders sit in between.
- A mandate review or ALM regime change resets tenor demand discontinuously.
- It is a **denominator discipline**: it improves the sizing of other people's claims rather than
  generating a position. Its productive use is to shrink an overstated claim
  ([IDEA-042](../../reports/IDEAS.md#idea-042) is what cuts
  [IDEA-005](../../reports/IDEAS.md#idea-005)'s 3–6bp to ~1.2bp — the pool records these two as being in
  deliberate tension rather than merging them).

## What it underpins

[IDEA-042](../../reports/IDEAS.md#idea-042) · [IDEA-005](../../reports/IDEAS.md#idea-005) ·
[IDEA-030](../../reports/IDEAS.md#idea-030) · [IDEA-006](../../reports/IDEAS.md#idea-006) ·
[IDEA-016](../../reports/IDEAS.md#idea-016) · [IDEA-007](../../reports/IDEAS.md#idea-007) ·
[VERDICT-003](../VERDICTS.md#verdict-003)

## Related

[[CONCEPT-001-term-premium]] — what the float feeds into ·
[[CONCEPT-005-effective-sample-size]] — the other "the label overstates what you have" correction

## Sources

[bernanke2020](../../papers/paper_notes_bernanke2020.md) ·
[du_tepper_verdelhan2018](../../papers/paper_notes_du_tepper_verdelhan2018.md) ·
[litterman1991](../../papers/paper_notes_litterman1991.md)

*Study lane: `studies/2026-03-26_fixed_income_relative_value_analysis_2e/` covers this material at
length and has not yet been harvested into atoms.*
