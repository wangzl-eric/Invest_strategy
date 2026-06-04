# Chapter 11 Notes: Reference Rates — SOFR, Repo, and Secured vs Unsecured Spreads

**Book:** Fixed Income Relative Value Analysis (Huggins & Schaller, 2nd ed., 2024)
**Chapter:** 11 — Reference Rates
*Notes by Cerebro — 2026-03-26*

---

## Chapter Argument Arc

Ch11 covers the plumbing layer of fixed income markets: the short-term reference rates
that anchor the entire yield curve and derivative pricing. The central story is the
**LIBOR-to-SOFR transition** and what it changed: LIBOR was a credit-sensitive,
unsecured, panel-bank rate; SOFR is a secured, nearly risk-free, transaction-based rate.
This difference has profound implications for basis trading, swap pricing, and the
interpretation of short-end spread relationships.

---

## 1. What Is a Reference Rate?

A reference rate is a benchmark interest rate used as the floating leg of derivatives,
loans, and bonds. It must be:
- **Reliable** — based on actual transactions, not bank estimates
- **Liquid** — underpinning a deep derivatives market
- **Risk-appropriate** — reflecting the credit profile of the instrument it prices

**Pre-2023 world:** LIBOR (London Interbank Offered Rate)
- Unsecured interbank lending rate
- Submitted by a panel of banks (not always transaction-based)
- Embedded a credit premium: spread to overnight risk-free rate widened in stress
  (e.g. LIBOR-OIS spread blew out to 350bps in 2008)
- Ceased: USD LIBOR discontinued June 2023

**Post-2023 world:** SOFR (Secured Overnight Financing Rate)
- Rate on overnight Treasury repo transactions
- Published by NY Fed; based on $~1 trillion/day in actual transactions
- Secured: virtually no credit risk (Treasury collateral)
- No term premium: overnight only (term SOFR is derived, not directly observed)

---

## 2. The Repo Market: Mechanics

SOFR is constructed from the **repo market** — so understanding repo is prerequisite.

### What Is Repo?

A repurchase agreement (repo) is a collateralized short-term loan:
- **Seller (borrower):** sells a security today, agrees to buy it back tomorrow
  at a higher price. Effective borrowing rate = **repo rate**.
- **Buyer (lender):** buys the security today, agrees to sell it back. Effective
  lending rate = repo rate. Earns interest with Treasury collateral protection.

### Why Repo Rates Vary

| Driver | Effect |
|--------|--------|
| **Collateral quality** | Treasury GC (general collateral) trades cheapest; agency and MBS trade wider |
| **Special repo** | High-demand bonds (on-the-run Treasuries, recently auctioned) trade at special (below GC) rates — lenders accept lower rate for access to the specific bond |
| **Term** | Overnight vs. term repo (1W, 1M, 3M) — term premium reflects funding risk |
| **Counterparty** | Bilateral vs. tri-party (BNY Mellon, JPM) affects credit exposure and haircuts |

---

## 3. SOFR Construction

SOFR is a **volume-weighted median** of overnight Treasury repo rates across three segments:
- **Tri-party repo** (ex GCF) — BNY Mellon-cleared, ~$500bn/day
- **GCF Repo** — DTCC-cleared interdealer general collateral, ~$50bn/day
- **Bilateral Treasury repo** — directly negotiated, ~$500bn/day

Volume-weighted **median** (not mean) is used to reduce sensitivity to outliers
(e.g. month-end repo rate spikes from bank balance sheet constraints).

---

## 4. SOFR vs. LIBOR: Key Differences

| Property | LIBOR | SOFR |
|----------|-------|------|
| Security | Unsecured | Secured (Treasury collateral) |
| Credit risk | Embedded bank credit premium | Near risk-free |
| Basis | Submission-based (manipulation risk) | Transaction-based |
| Term structure | 1W, 1M, 3M, 6M, 12M directly observed | Overnight only; term SOFR is derived |
| Stress behavior | Spikes in crises (LIBOR-OIS blowout 2008) | More stable; repo can spike at quarter-end |
| Legacy | Trillions in legacy contracts (now converted) | New standard for USD derivatives |

---

## 5. The LIBOR-OIS Spread as a Stress Indicator

The **LIBOR-OIS spread** (3M LIBOR minus 3M OIS rate) was the canonical
credit/funding stress indicator pre-2023:
- Normal: ~10–15bps (credit premium of unsecured interbank lending)
- GFC 2008: spiked to ~365bps (banks feared counterparty default)
- COVID March 2020: spiked to ~140bps

Post-SOFR, the equivalent is the **SOFR-EFFR spread** or **term SOFR vs. OIS**.
But because SOFR is secured, the spread is structurally narrower and reflects
collateral dynamics rather than bank credit risk.

---

## 6. Secured vs. Unsecured Spread Decomposition

The spread between SOFR (secured) and EFFR (unsecured Fed funds) reflects:
1. **Credit component** — unsecured lending carries counterparty default risk
2. **Collateral scarcity** — when Treasury supply is abundant, repo rates rise
   (less excess demand for collateral), compressing the SOFR-EFFR spread
3. **Regulatory capital** — leverage ratio constraints cause repo rates to spike
   at quarter-end and year-end as banks shrink balance sheets

This decomposition matters for RV: a widening SOFR-EFFR spread could signal
collateral scarcity (bullish for Treasuries) or credit stress (bearish for risk).

---

## 7. Term SOFR and the SOFR Futures Curve

Since SOFR is overnight-only, **term SOFR** is derived from SOFR futures and OIS swaps.
This creates a new basis: **Term SOFR vs. Daily SOFR compounding** — because term
SOFR is a forward expectation while daily compounding is realized.

For RV traders: the SOFR futures strip encodes the market's expectation of the
fed funds path. Deviations from OIS forwards are tradeable basis opportunities.

---

## Key Takeaways

1. **SOFR is not a drop-in replacement for LIBOR.** The credit component is missing.
   Products pricing credit risk (corporate FRNs, leveraged loans) needed spread
   adjustments — the ARRC recommended 26bps for 3M LIBOR-to-SOFR conversion.

2. **Repo specialness contaminates SOFR.** When on-the-run Treasuries are in high
   demand (e.g. around auctions), SOFR can print below EFFR temporarily.
   This creates noise in any SOFR-based fixed income carry calculation.

3. **Quarter-end effects are structural.** Bank balance sheet constraints reliably
   spike repo rates at quarter-end (G-SIB surcharge, leverage ratio). This creates
   predictable seasonal patterns in SOFR that are exploitable in rates vol.

4. **Term SOFR is the relevant rate for asset swaps post-transition.** Ch12's asset
   swap spreads are now quoted vs. Term SOFR; historical LIBOR-based spreads need
   basis adjustment for any pre-2023 comparison.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch12 — Asset Swaps** | The floating leg of an asset swap is now Term SOFR; pre-2023 data uses LIBOR |
| **Ch13–18 — Spreads** | Cross-currency basis involves SOFR vs. other secured rates (ESTR, SONIA) |
| **Ch9 — Analytic Process** | Repo specialness of a bond affects its effective carry; must be netted from the ASW spread signal |

---

*Cerebro — 2026-03-26 | FIRV study: Ch11 Reference Rates / SOFR*
