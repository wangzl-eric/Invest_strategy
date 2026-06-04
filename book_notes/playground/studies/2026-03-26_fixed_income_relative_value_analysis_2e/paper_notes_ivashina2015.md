# Paper Notes: Dollar Funding and the Lending Behavior of Global Banks

**Authors:** Victoria Ivashina, David Scharfstein, Jeremy Stein
**Year:** 2015
**Journal:** American Economic Review, Vol. 105, No. 5, pp. 82–87
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 4

---

## Core Claim

Non-US global banks that fund themselves in US wholesale dollar markets
(CP, repo, money market funds) are **structurally vulnerable** to dollar
funding runs. When dollar funding dries up — as it did in 2008 and 2011 —
these banks cannot roll their short-term dollar liabilities and are forced
to contract dollar lending, sell dollar assets, and scramble to acquire
dollars via the FX swap market. This **dollar funding scarcity** is the
primary mechanism behind cross-currency basis widening in stress periods:
European and Japanese banks pay a premium above CIP to obtain dollars via
FX swaps when their normal wholesale dollar funding channels are disrupted.

The paper provides the **banking channel explanation** for the structural
CIP deviations documented by Du-Tepper-Verdelhan (2018).

---

## 1. The Dollar Funding Structure of Global Banks

### How Non-US Banks Fund in Dollars

European and Japanese banks had large dollar asset books (USD loans,
MBS, Treasuries) funded via:

| Funding Source | Maturity | Vulnerability |
|---------------|----------|---------------|
| US money market funds (MMFs) | Overnight to 3M CP | Very high — MMF runs (2008, 2011) |
| Tri-party repo | Overnight | High — rollover risk |
| FX swaps (borrow USD, lend EUR/JPY) | 1W to 3M | Medium — basis widens but market stays open |
| Long-term bond issuance | 3–10Y | Low — stable but expensive |

In 2008, Lehman's collapse triggered a run on US MMFs (Reserve Primary
Fund broke the buck). MMFs stopped rolling CP → European banks lost
$500bn+ of overnight dollar funding within days.

---

## 2. The Dollar Funding Channel

### How Dollar Scarcity Transmits to FX Swap Markets

When US MMFs pull back from European bank CP:
1. European banks lose dollar funding → must source dollars elsewhere
2. Only remaining option: **FX swap market** (borrow dollars, post EUR/JPY as collateral)
3. Surge in demand for dollar legs of FX swaps → **cross-currency basis widens**
4. EUR/USD basis goes deeply negative (European banks pay extra to borrow dollars)
5. CIP deviation = cross-currency basis = dollar scarcity premium

This mechanism explains why CIP deviations (Du-Tepper-Verdelhan 2018)
are **largest in stress periods** (2008, 2011 Eurozone crisis, 2020 COVID)
and largest for EUR and JPY banks which had the largest dollar asset books
relative to their natural dollar funding base.

### The Balance Sheet Constraint

Post-2008 regulatory reforms (Basel III, leverage ratio, G-SIB surcharge)
reinforced the structural dollar scarcity:
- Banks cannot expand FX swap books without consuming leverage ratio capacity
- Arbitrageurs who could close CIP deviations face balance sheet constraints
- Result: **CIP deviations persist** even in calm markets — not just in stress

Ivashina-Scharfstein-Stein identified the mechanism; Du-Tepper-Verdelhan
quantified the persistence and its regulatory drivers.

---

## 3. Implications for Cross-Currency Basis Trading

### When the Basis Is Wide: Structural Alpha vs. Crisis Risk

| Basis Driver | Signal Type | RV Implication |
|-------------|------------|----------------|
| **Stress (MMF run, bank crisis)** | Crisis premium | Avoid — basis can widen further; counterparty risk |
| **Regulatory (leverage ratio, G-SIB)** | Structural premium | Tradeable — persistent, mean-reverting around regulatory calendar |
| **Quarter-end window dressing** | Technical premium | Tradeable — predictable, short-lived |

**Key distinction:** Ivashina et al. show that dollar scarcity in stress is
**not mean-reverting on short horizons** — it can persist and worsen as
funding conditions deteriorate. Only regulatory-driven basis is the
structural carry that Du-Tepper-Verdelhan describe as tradeable.

### Stress Indicator: MMF Flows to European Banks

The paper shows MMF exposure to European bank CP is a **leading indicator**
of basis widening:
- MMF outflows from EU bank CP → basis widens within 1–2 weeks
- Monitor: SEC Form N-MFP (monthly MMF portfolio disclosure) or
  iMoneyNet weekly MMF data for European bank CP allocation

---

## 4. Key Takeaways

1. **Dollar funding structure explains basis stress dynamics.** CIP
   deviations in stress are not arbitrage opportunities — they reflect
   genuine scarcity that arbitrageurs cannot close. Distinguish stress-
   driven from regulatory-driven basis before trading.

2. **MMF exposure is the canary.** When US MMFs pull back from European
   bank CP, expect basis to widen within weeks. This is an actionable
   leading indicator for EUR/USD and JPY/USD basis positions.

3. **Non-US banks are structurally short dollars.** Their asset books
   (USD loans, Treasuries) are partially funded by short-term dollar
   liabilities that can run. This structural mismatch creates a permanent
   basis floor and explains why EUR/USD basis is almost always negative.

4. **Post-Basel III, the mechanism is regularized.** Quarter-end and
   year-end balance sheet compression creates predictable spikes in
   dollar demand. These are the highest-Sharpe basis trading windows.

5. **Complements Du-Tepper-Verdelhan.** Ivashina et al. provide the
   banking channel story (WHY basis widens in stress); Du-Tepper-Verdelhan
   provide the regulatory persistence story (WHY basis persists in calm).
   Both are needed for a complete cross-currency basis framework.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch13–16 — Cross-Currency Basis** | Ivashina et al. is the banking channel explanation for the basis mechanics described across these chapters |
| **Ch17 — Global Bond RV** | Dollar scarcity affects USD-equiv ASW calculations; wide basis = European bonds look cheaper than they are in common currency |
| **Ch11 — SOFR** | SOFR spikes in stress partly reflect dollar scarcity premium leaking into repo markets |
| **Ch18 — Repo** | Dollar repo scarcity and tri-party collateral transformation are the repo-market analog of the FX swap dollar demand |

---

*Cerebro — 2026-03-26 | FIRV study: Ivashina, Scharfstein & Stein (2015)*