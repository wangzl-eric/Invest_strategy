# Paper Notes: SOFR Transition — Federal Reserve and ARRC Technical Notes (2018–2023)

**Authors:** Federal Reserve Bank of New York; Alternative Reference Rates Committee (ARRC)
**Year:** 2018–2023 series
**Source:** NY Fed staff reports; ARRC publications; BIS working papers
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 4

---

## Core Claim

The transition from LIBOR to SOFR (completed June 2023 for USD LIBOR) is
the largest reference rate reform in financial market history. SOFR is a
**secured overnight rate** constructed from Treasury repo transactions —
fundamentally different from LIBOR (unsecured, term, bank panel). The
transition required: new fallback language in contracts, spread adjustments
for legacy LIBOR exposure, new term rate conventions, and market-making
infrastructure for SOFR derivatives. For FIRV practitioners, understanding
the SOFR construction, its behavior relative to LIBOR/EFFR, and the spread
adjustments embedded in legacy contracts is essential for pricing any
instrument with SOFR-linked cashflows.

---

## 1. SOFR Construction (NY Fed)

### Three-Segment Methodology

SOFR is computed daily by the NY Fed as the **volume-weighted median**
of eligible Treasury repo transactions across three segments:

| Segment | Description | Daily Volume |
|---------|-------------|-------------|
| **Tri-party repo** | BNY Mellon-cleared overnight GC Treasury repo | ~$500–800bn |
| **GCF repo** | DTCC-cleared interdealer GC repo | ~$50–100bn |
| **Bilateral repo** | DVP Treasury repo cleared through DTCC | ~$500–700bn |

**Total:** ~$1.0–1.5 trillion per day — the deepest, most liquid short-term
rate market in the world. This makes SOFR far more robust to manipulation
than LIBOR (which was based on 16 bank panel submissions).

### Key Properties vs. LIBOR

| Property | LIBOR | SOFR |
|----------|-------|------|
| **Secured/Unsecured** | Unsecured (interbank) | Secured (Treasury repo) |
| **Term** | Overnight to 12 months | Overnight only (spot) |
| **Credit component** | Yes — bank credit spread embedded | No — risk-free rate |
| **Construction** | Panel bank submissions (16 banks) | Transaction-based (all eligible repo) |
| **Manipulation risk** | High (proven in 2012 scandal) | Very low (volume-weighted median) |
| **Volume** | ~$0.5bn/day underlying transactions | ~$1.0–1.5tn/day |

### SOFR vs. EFFR Spread

SOFR is typically **below EFFR** by 5–15bps in normal conditions:
- SOFR = secured rate (Treasury collateral); EFFR = unsecured (fed funds)
- Secured lending commands lower rate than unsecured
- SOFR–EFFR spread widens in stress (flight to Treasuries compresses SOFR;
  bank credit stress widens EFFR) and at quarter-end (balance sheet compression)

---

## 2. LIBOR-SOFR Transition Mechanics (ARRC)

### The Spread Adjustment

Legacy LIBOR contracts (loans, bonds, swaps) had fallback language triggered
by LIBOR cessation. ARRC recommended a **fixed spread adjustment** to convert
LIBOR rates to SOFR equivalents:

| Tenor | ARRC Spread Adjustment (bps) |
|-------|-----------------------------|
| 1-month LIBOR → 1M SOFR compounded | **11.448 bps** |
| 3-month LIBOR → 3M SOFR compounded | **26.161 bps** |
| 6-month LIBOR → 6M SOFR compounded | **42.826 bps** |
| 12-month LIBOR → 12M SOFR compounded | **71.513 bps** |

These spreads were fixed as the **5-year median of the historical LIBOR–OIS
(SOFR) spread** over the 2016–2021 reference period, per ISDA protocol.

**RV implication:** Any LIBOR-linked bond or loan that converted via
fallback language now pays SOFR + fixed spread. The fixed spread is
not the current LIBOR-SOFR differential — it is the historical median.
In periods where actual SOFR–LIBOR spread deviates from the fixed adjustment,
there is a basis between fallback-converted instruments and new SOFR instruments.

---

## 3. Term SOFR

### Why Term SOFR Was Needed

Overnight SOFR requires **compounding in arrears** — you don't know the
rate for a period until the period ends. Loan markets (commercial real
estate, leveraged loans) need to know interest payments in advance
("in advance" convention). ARRC developed **Term SOFR** to address this.

### Term SOFR Construction

Term SOFR (1M, 3M, 6M, 12M) is derived from:
- SOFR futures prices (CME 1-month and 3-month SOFR futures)
- Forward-looking rate = market expectation of compounded overnight
  SOFR over the term period
- Published daily by CME Group

**Key distinction:**
- **Compounded SOFR in arrears** = average of actual overnight rates (backward-looking)
- **Term SOFR** = market expectation of that average (forward-looking)
- Difference = convexity adjustment + expectation error

---

## 4. SOFR Behavior and RV Implications

### Quarter-End and Year-End Spikes

SOFR spikes predictably at quarter-end (March, June, September, December):
- Banks compress repo book at quarter-end to reduce balance sheet for
  regulatory reporting → less cash in repo market → SOFR rises
- Magnitude: typically 10–40bps above trend; can exceed 100bps at year-end
- 2019 September repo spike: SOFR jumped to 5.25% (from ~2.10%) — EFFR
  briefly exceeded Fed Funds upper band

**Trading implication:** SOFR-linked instruments that reset near quarter-end
receive elevated SOFR fixes. This creates a predictable carry premium for
holding SOFR receiver swaps through quarter-end vs. EFFR-linked instruments.

### SOFR OIS Curve Construction

The SOFR OIS curve is constructed from:
- Fed Funds futures (front end, < 1Y) — still more liquid than SOFR futures
- SOFR OIS swaps (1Y to 30Y) — dealer market, increasingly standardized
- SOFR futures (1M and 3M contracts) — CME; used for curve interpolation

---

## 5. Key Takeaways

1. **SOFR is the new risk-free rate for USD fixed income.** All new USD
   derivative contracts, most new bonds, and all new loans use SOFR.
   The FIRV framework's ASW spreads, carry calculations, and OIS curves
   are all SOFR-based as of 2023.

2. **The 26bps ARRC spread adjustment is embedded in legacy contracts.**
   When comparing a fallback-converted LIBOR bond to a new SOFR bond,
   check whether the spread adjustment is at fair value vs. the current
   SOFR-EFFR differential and credit premium.

3. **Quarter-end SOFR spikes are structural and predictable.** They reflect
   bank balance sheet mechanics, not monetary policy. Model them as
   calendar effects in carry calculations, not as information about rates.

4. **Term SOFR ≠ compounded SOFR.** The difference is small in calm
   markets but can be meaningful in volatile periods. Know which
   convention your instrument uses before computing carry.

5. **SOFR OIS is now the discount curve for USD derivatives.** All
   CSA-collateralized USD swap PVs are discounted at SOFR OIS. The
   dual-curve framework (LIBOR forwarding + OIS discounting) is now
   single-curve SOFR.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch11 — Reference Rates and SOFR** | This note IS the companion reference to Ch11; ARRC publications are the primary source |
| **Ch12 — Asset Swaps** | ASW spreads are now vs. SOFR OIS; the Par-par ASW formula uses SOFR as the floating leg |
| **Ch18 — Repo** | SOFR is constructed from repo; Ch18's repo mechanics directly explain SOFR behavior |
| **Ch14 — Intra-Currency Basis** | SOFR vs EFFR basis, SOFR vs Term SOFR basis — all intra-currency tenor/credit bases |

---

*Cerebro — 2026-03-26 | FIRV study: SOFR/ARRC Transition Notes (2018–2023)*