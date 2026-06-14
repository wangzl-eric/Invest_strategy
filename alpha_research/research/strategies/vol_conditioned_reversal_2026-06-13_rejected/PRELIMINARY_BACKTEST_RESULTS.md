# PRELIMINARY backtest — vol_conditioned_reversal (LOCAL DATA, NOT canonical)

- Sample: 2012-01-03 -> 2026-02-27 (3559 trading days, ~14.1y)
- VIX source: LOCAL ^VIX close (stale to 2026-02-27); canonical run uses FRED VIXCLS
- Cost: flat 8 bps placeholder (NO $1 floor); shift_bars=2 (t+1_open); n_trials=24
- NOT the ~1999 backfill, NO ledger/pool write. Fail-fast read only.

## Headline (VIX-gated, canonical config on local data)

| metric | value |
|---|---|
| Net Sharpe (1x cost) | **-0.844** |
| Net Sharpe (2x cost) — K1 | **-1.464** (FAIL <=0) |
| Net Sharpe (3x cost) — K11 | -2.039 (FAIL) |
| Ann. return (net, 1x) | -3.21% |
| Ann. vol | 3.78% |
| Max drawdown | -36.6% |
| Ann. turnover (2-sided) | 3045% |
| Duty cycle (gate-active days) | 43% |
| PSR (vs 0) | 0.1% (FAIL) |
| DSR (n_trials=24) | 0.000 (FAIL) |
| Sharpe 95% CI | [-1.36, -0.33] |

## MinBTL — the modal kill (K9)

| basis | Sharpe | MinBTL (days) | available | verdict |
|---|---|---|---|---|
| full sample | -0.844 | 1000000 | 3496 | FAIL |
| **high-VIX active sub-sample** | -1.090 | inf (Sharpe<=0) | 1489 | **FAIL** |

## Baselines — does the VIX gate earn its place? (K2 / K4 / K3)

| strategy | net Sharpe (1x) | net Sharpe (2x) | maxDD | turnover |
|---|---|---|---|---|
| **VIX-gated reversal (ours)** | **-0.844** | -1.464 | -37% | 3045% |
| unconditional reversal (K2) | -0.965 | -1.809 | -52% | 5752% |
| 21d trailing-vol-gated (K4) | -0.622 | -1.247 | -31% | 3228% |
| equal-weight long-only (K3 ctx) | 0.835 | n/a | -36% | 7% |

- **K2** (gate must add >= +0.15 vs unconditional): delta = +0.121 -> FAIL
- **K4 (HARD)** (must beat 21d trailing-vol gate): delta = -0.222 -> FAIL — dressed-up vol timing

## Honest reading
- These are REAL engine outputs on local data, but NOT the canonical run. Costs omit the
  $1 IBKR floor (~50-65 bps/yr at 25k), so net is FLATTERED here. K9 active-sub-sample MinBTL
  and K4 are the decisive reads. Re-run the networked canonical battery before any verdict.
