# Chapter 14 Notes: Intra-Currency Basis Swap Spreads

**Book:** Fixed Income Relative Value Analysis (Huggins & Schaller, 2nd ed., 2024)
**Chapter:** 14 — Intra-Currency Basis Swap Spreads
*Notes by Cerebro — 2026-03-26*

---

## Chapter Argument Arc

An intra-currency basis swap exchanges two floating-rate cashflow streams denominated
in the **same currency** — but referencing **different floating benchmarks**. The
spread between them (the basis) should theoretically be zero under a single risk-free
curve, but in practice it is non-zero and time-varying. Ch14 explains what drives
these basis spreads, how they are quoted and traded, and how they create RV
opportunities within a single currency's fixed income market.

---

## 1. What Is an Intra-Currency Basis Swap?

A basis swap exchanges two floating legs in the same currency:
- **Leg A:** 3M SOFR flat (or + spread)
- **Leg B:** 1M SOFR + basis spread $b$

The basis spread $b$ is the amount added to one leg to make the swap fair at inception.

### Common Intra-Currency Basis Pairs

| Pair | Description |
|------|-------------|
| **3M SOFR vs. 1M SOFR** | Tenor basis — most liquid USD basis swap |
| **3M SOFR vs. Overnight SOFR compounded** | OIS vs. term basis |
| **SOFR vs. EFFR** | Secured vs. unsecured overnight basis |
| **Prime vs. SOFR** | Credit-sensitive vs. risk-free (commercial bank lending) |
| **EURIBOR 3M vs. EURIBOR 6M** | EUR tenor basis (pre-ESTR transition) |
| **ESTR vs. EURIBOR 3M** | EUR secured vs. unsecured post-transition |

---

## 2. Why Intra-Currency Basis Is Non-Zero

### Tenor Basis (3M vs. 1M)

The 3M-1M SOFR basis exists because:
- **Rollover risk:** 1M SOFR must be rolled 3 times to match a 3M investment;
  each roll carries uncertainty about the future rate → investors demand a premium
  for bearing this rollover risk in the 1M leg
- **Demand imbalance:** corporate treasurers prefer 1M funding; banks prefer 3M
  funding — structural supply/demand mismatch creates a persistent spread
- **Historical LIBOR legacy:** the 3M-1M LIBOR basis trained market participants
  to hedge with 3M instruments, creating path-dependent demand patterns

### Secured vs. Unsecured Basis (SOFR vs. EFFR)

- SOFR is secured (Treasury collateral) → near risk-free
- EFFR is unsecured → carries residual bank credit premium
- Normal spread: SOFR ~5–10bps below EFFR (secured cheaper to borrow)
- Inverts when Treasury collateral is scarce (e.g. debt ceiling periods,
  large Treasury supply relative to repo demand)

### Credit-Sensitive Basis (Prime vs. SOFR)

Post-LIBOR, some commercial loan contracts use credit-sensitive rates:
- **BSBY** (Bloomberg Short-Term Bank Yield): embeds bank credit risk
- **Ameribor**: small bank funding rate
- These trade at a spread over SOFR reflecting the bank credit premium that
  SOFR (being secured) lacks — similar to the old LIBOR-OIS spread

---

## 3. Drivers of Tenor Basis Over Time

| Driver | Effect on 3M-1M basis |
|--------|---------------------|
| **Fed rate hike cycle** | Flattens basis — market prices in rapid moves, reducing term uncertainty |
| **Fed on hold / low vol** | Widens basis — rollover risk premium rises when path is uncertain |
| **Quarter-end** | Temporary widening — balance sheet constraints affect short-end funding |
| **Regulatory tightening** | Widens basis — higher capital costs increase the value of longer-term funding |
| **Crisis / liquidity stress** | Widens sharply — 1M becomes risky to roll; term premium spikes |

---

## 4. Trading Intra-Currency Basis

### The Basis Swap Trade

A long 3M-1M basis position:
- Receive 3M SOFR flat
- Pay 1M SOFR + basis spread $b$
- P&L: earn if 3M SOFR outperforms 1M SOFR + $b$ over the tenor
- Directional bet: expects the basis to widen (3M premium to increase)

### Basis as a Carry Component in Fixed Income

For bond carry calculations, the funding leg must match the basis:
- A bond financed in 1M repo hedged with a 3M SOFR receiver swap has basis
  exposure equal to the 3M-1M spread
- Ignoring the basis overstates carry by the amount of the tenor mismatch
- In carry-rich environments (steep 3M-1M basis), financing at 1M and hedging
  at 3M creates positive carry from the basis alone

### Basis in Asset Swap Pricing

When structuring an asset swap (Ch12) with a 1M floating leg vs. a 3M floating leg,
the ASW spread differs by exactly the 3M-1M basis:
$$\text{ASW}_{1M} = \text{ASW}_{3M} - b_{3M-1M}$$
Comparison across asset swaps quoted on different tenors requires basis adjustment.

---

## 5. Key Takeaways

1. **Tenor basis is a structural premium for rollover risk.** It is not an
   arbitrage opportunity — it compensates for genuine uncertainty about future
   rates at each roll date.

2. **Basis adjustments are mandatory in carry calculations.** Ignoring the
   3M-1M basis in a bond carry calculation introduces systematic error —
   particularly important for short-dated bonds where basis is largest relative
   to carry.

3. **SOFR-EFFR basis is a collateral scarcity signal.** Inversion (SOFR > EFFR)
   signals Treasury collateral scarcity — a useful macro indicator for UST demand.

4. **Quarter-end patterns are exploitable.** Basis reliably widens at quarter-end;
   entering basis receivers (pay 1M, receive 3M) a week before quarter-end and
   unwinding after is a well-documented seasonal strategy.

5. **Post-LIBOR complexity.** The proliferation of SOFR-based tenors (1D, 1M, 3M,
   term SOFR) creates a richer basis landscape than the LIBOR era — more
   opportunities but also more basis risk to manage in hedging.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch11 — Reference Rates** | SOFR mechanics underpin all intra-currency basis; tenor SOFR vs. overnight compounding is the primary basis |
| **Ch12 — Asset Swaps** | ASW spread comparisons require basis adjustment when floating legs use different tenors |
| **Ch13 — Cross-Currency Basis** | Intra-currency basis + cross-currency basis = total hedging cost for a foreign bond investment |
| **Ch9 — Analytic Process** | Bond carry calculations must include basis adjustment to get accurate ex ante returns |

---

*Cerebro — 2026-03-26 | FIRV study: Ch14 Intra-Currency Basis Swap Spreads*
