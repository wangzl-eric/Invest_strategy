# Macro Liquidity: QT, QE, and RRP — Key Lessons

> Created: 2026-06-25 | Source: study session discussion

---

## 1. What RRP Is

**RRP (Reverse Repurchase Agreement / Overnight Reverse Repo Facility)** is a Fed tool where the Fed sells securities to counterparties (money market funds, banks, GSEs) overnight and buys them back the next day at a slightly higher price. The difference is the interest paid — effectively a risk-free overnight rate floor.

- FRED series: `RRPONTSYD`
- Sets a **floor on short-term interest rates** (lower bound on effective Fed Funds Rate)
- Balance of the facility signals **excess liquidity** in the financial system

---

## 2. The Fed Balance Sheet — Plumbing Mental Model

```
ASSETS                        LIABILITIES
─────────────────────         ─────────────────────────────────
Treasuries, MBS               Bank Reserves
                              RRP balances
                              Treasury General Account (TGA)
                              Currency in circulation
```

- **QT** = Fed shrinks its *asset* side (lets bonds mature, doesn't reinvest) → reserves fall
- **RRP increase** = money moves *between liability buckets* (reserves → RRP), NOT an asset-side change

---

## 3. Increasing RRP ≠ QT, But Has the Same Liquidity Effect

When RRP rises, money market funds prefer parking at the Fed over deploying into markets:

1. **Bank reserves fall** — money migrates from reserves into RRP
2. **Net system liquidity tightens** — fewer reserves available to the banking system
3. **Credit and risk appetite shrink** — less money seeking yield in risk assets

Economically equivalent to QT in its liquidity-draining effect, even though the mechanism is different.

---

## 4. The Key Metric: Net Fed Liquidity

$$\text{Net Liquidity} = \text{WALCL} - \text{RRP} - \text{TGA}$$

| Scenario | Net Liquidity | Market Implication |
|---|---|---|
| WALCL flat, RRP ↑ | Decreases | Tightening |
| WALCL flat, RRP ↓ | Increases | Loosening |
| QT (WALCL ↓), RRP flat | Decreases | Tightening |
| QT (WALCL ↓), RRP ↓ | Can be flat or up | Neutral / loosening |

> **Implication:** RRP changes can fully offset or amplify QT. Watch net liquidity, not just the balance sheet headline.

---

## 5. The 2022–2023 Lesson

- Fed began QT (balance sheet shrinkage) from mid-2022
- RRP simultaneously peaked at **~$2.5T** — absorbing excess liquidity built during COVID QE
- As RRP drained from $2.5T → ~$0 through 2023–2024, it **injected liquidity back**, offsetting QT
- Net liquidity *increased* even while "QT was ongoing" — a key reason risk assets rallied in 2023

---

## 6. Conceptual Summary

| | QT | QE | RRP Rising | RRP Falling |
|---|---|---|---|---|
| Fed balance sheet | Shrinks | Expands | Unchanged | Unchanged |
| Bank reserves | Fall | Rise | Fall | Rise |
| Net liquidity | Decreases | Increases | Decreases | Increases |
| Market effect | Tightening | Loosening | Shadow tightening | Shadow easing |

**Key takeaway:** RRP acts as a *shadow lever* on liquidity conditions.
- **Rising RRP** = shadow QT (tightening without balance sheet reduction)
- **Falling RRP** = shadow QE (easing that can neutralize active QT)

---

## 7. Signals to Watch

| Series | Source | What It Tells You |
|---|---|---|
| `RRPONTSYD` | FRED | Daily RRP balance — excess liquidity proxy |
| `WALCL` | FRED | Total Fed assets — QE/QT tracker |
| `WTREGEN` | FRED | Treasury General Account balance |
| Net Liquidity = WALCL - RRP - TGA | Derived | True system liquidity pulse |

Net liquidity is a **leading indicator** for risk appetite: rising net liquidity historically precedes equity rallies; falling net liquidity precedes corrections.
