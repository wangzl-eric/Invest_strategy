# 2026-06-14: PRELIMINARY local-data diagnostic for vol_conditioned_reversal.
# NOT the canonical review path. It bypasses python -m alpha_research.review (which
# needs FRED VIXCLS + the ~1999 backfill, both network) and runs the engine + stats
# directly on the LOCAL lake using the stale ^VIX cache as a VIXCLS stand-in. It does
# NOT register a pool entry or write an experiment_ledger row. Caveats: sample is
# 2012->2026-02 (not the approved ~1999 backfill), VIX is ^VIX close (not FRED VIXCLS),
# stale to 2026-02-27, costs are the placeholder flat 8 bps (NO $1 floor). Use only as a
# fail-fast read on K1 (2x cost) and K9 (MinBTL); the canonical numbers come from the
# networked review run.
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from alpha_research.backtests.runners.vol_conditioned_reversal import (
    DEFAULT_PARAMS,
    SECTOR_ETFS,
    _neutralize_cap_normalize,
    _zscore_xs,
    build_weights,
)
from alpha_research.backtests.stats import (
    deflated_sharpe_ratio,
    minimum_backtest_length,
    probabilistic_sharpe_ratio,
    sharpe_confidence_interval,
)
from alpha_research.review.engine import (
    equal_weight_baseline,
    rebalance_dates,
    run_weights_backtest,
)

PRICE_DIR = "data/market_data/prices"
COST_BPS = 8.0  # manifest placeholder (flat; no $1 floor)
SHIFT = 2  # t+1_open
N_TRIALS = 24
ANN = 252


def _load_prices():
    frames = {}
    for t in SECTOR_ETFS + ["SPY"]:
        f = os.path.join(PRICE_DIR, f"{t}.parquet")
        if os.path.exists(f):
            df = pd.read_parquet(f)
            frames[t] = df.set_index("date")["close"]
    px = pd.DataFrame(frames).sort_index()
    px.index = pd.to_datetime(px.index)
    return px


def _load_vix():
    v = pd.read_parquet(os.path.join(PRICE_DIR, "vix_daily.parquet"))["close"]
    v.index = pd.to_datetime(v.index)
    return v.sort_index()


def _sharpe(r):
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(ANN)) if r.std() > 0 else 0.0


def _unconditional_reversal_weights(px, params):
    """K2 baseline: identical reversal, traded EVERY week (no VIX gate)."""
    p = {**DEFAULT_PARAMS, **params}
    lb = int(p["reversal_lookback"])
    cap, gross, band = (
        float(p["max_weight"]),
        float(p["gross"]),
        float(p["no_trade_band"]),
    )
    universe = [t for t in px.columns if t in SECTOR_ETFS]
    pp = px[universe]
    r5 = pp / pp.shift(lb) - 1.0
    rebal = rebalance_dates(pp.index, "weekly")
    w = pd.DataFrame(np.nan, index=pp.index, columns=universe)
    prev = pd.Series(0.0, index=universe)
    for d in rebal:
        elig = [t for t in universe if pd.notna(r5.loc[d, t])]
        if len(elig) < int(p["min_eligible"]):
            continue
        tgt = _neutralize_cap_normalize(-_zscore_xs(r5.loc[d, elig]), cap, gross)
        prev_e = prev.reindex(tgt.index).fillna(0.0)
        hold = (tgt - prev_e).abs() <= band
        book = tgt.copy()
        book[hold] = prev_e[hold]
        book = _neutralize_cap_normalize(book, cap, gross)
        w.loc[d, universe] = 0.0
        w.loc[d, list(book.index)] = book.values
        prev = pd.Series(0.0, index=universe)
        prev[list(book.index)] = book
    return w


def _bt(weights, px):
    return run_weights_backtest(weights, px, cost_bps=COST_BPS, shift_bars=SHIFT)


def main():
    px_all = _load_prices()
    vix = _load_vix()
    sectors = [t for t in SECTOR_ETFS if t in px_all.columns]
    # common window where BOTH sector prices and VIX exist
    start = max(px_all[sectors].dropna(how="all").index.min(), vix.index.min())
    end = min(px_all.index.max(), vix.index.max())
    px = px_all.loc[start:end]
    sec_px = px[sectors]
    spy = px["SPY"]
    vix_c = vix.loc[start:end]

    out = []

    def log(s=""):
        out.append(s)
        print(s)

    log("# PRELIMINARY backtest — vol_conditioned_reversal (LOCAL DATA, NOT canonical)")
    log("")
    log(
        f"- Sample: {px.index.min().date()} -> {px.index.max().date()} "
        f"({len(px)} trading days, ~{len(px)/ANN:.1f}y)"
    )
    log(
        f"- VIX source: LOCAL ^VIX close (stale to {vix.index.max().date()}); "
        "canonical run uses FRED VIXCLS"
    )
    log(
        f"- Cost: flat {COST_BPS:.0f} bps placeholder (NO $1 floor); shift_bars={SHIFT} (t+1_open); "
        f"n_trials={N_TRIALS}"
    )
    log("- NOT the ~1999 backfill, NO ledger/pool write. Fail-fast read only.")
    log("")

    # ---- canonical config (VIX-gated) ----
    macro = {"VIXCLS": vix_c}
    w = build_weights(sec_px, macro, DEFAULT_PARAMS)
    res = _bt(w, sec_px)
    r = res.daily_returns
    weff = res.weights
    active_mask = weff.abs().sum(axis=1) > 1e-9
    duty = float(active_mask.mean())

    # cost sweep (K1 / K11)
    sweep = {
        m: _bt(w, sec_px).metrics
        if m == 1
        else run_weights_backtest(
            w, sec_px, cost_bps=COST_BPS * m, shift_bars=SHIFT
        ).metrics
        for m in (1, 2, 3)
    }

    # baselines
    ew = equal_weight_baseline(
        sec_px, rebalance="weekly", cost_bps=COST_BPS, shift_bars=SHIFT
    )
    w_unc = _unconditional_reversal_weights(sec_px, DEFAULT_PARAMS)  # K2
    res_unc = _bt(w_unc, sec_px)
    spy_rv = spy.pct_change().rolling(21).std() * np.sqrt(ANN)  # K4 gate signal
    w_tv = build_weights(
        sec_px, {"VIXCLS": spy_rv}, DEFAULT_PARAMS
    )  # trailing-vol gate
    res_tv = _bt(w_tv, sec_px)

    arr = r.to_numpy(float)
    psr = float(probabilistic_sharpe_ratio(arr, benchmark_sharpe=0.0))
    dsr = float(deflated_sharpe_ratio(arr, n_trials=N_TRIALS))
    try:
        ci = sharpe_confidence_interval(arr)
        ci_s = f"[{ci[0]:.2f}, {ci[2]:.2f}]"
    except Exception:
        ci_s = "n/a"
    sh_full = res.metrics["sharpe_ratio"]
    minbtl_full = int(minimum_backtest_length(sh_full, n_trials=N_TRIALS))

    # active-only sub-sample (the MODAL kill K9)
    act = r[active_mask]
    sh_act = _sharpe(act)
    minbtl_act = (
        int(minimum_backtest_length(sh_act, n_trials=N_TRIALS))
        if sh_act > 0
        else 10**9
    )

    log("## Headline (VIX-gated, canonical config on local data)")
    log("")
    log("| metric | value |")
    log("|---|---|")
    log(f"| Net Sharpe (1x cost) | **{sh_full:.3f}** |")
    log(
        f"| Net Sharpe (2x cost) — K1 | **{sweep[2]['sharpe_ratio']:.3f}** "
        f"({'PASS >0' if sweep[2]['sharpe_ratio']>0 else 'FAIL <=0'}) |"
    )
    log(
        f"| Net Sharpe (3x cost) — K11 | {sweep[3]['sharpe_ratio']:.3f} "
        f"({'PASS' if sweep[3]['sharpe_ratio']>0 else 'FAIL'}) |"
    )
    log(f"| Ann. return (net, 1x) | {res.metrics['annualized_return']*100:.2f}% |")
    log(f"| Ann. vol | {res.metrics['volatility']*100:.2f}% |")
    log(f"| Max drawdown | {res.metrics['max_drawdown']*100:.1f}% |")
    log(f"| Ann. turnover (2-sided) | {res.metrics['annual_turnover']*100:.0f}% |")
    log(f"| Duty cycle (gate-active days) | {duty*100:.0f}% |")
    log(f"| PSR (vs 0) | {psr*100:.1f}% ({'PASS>=90' if psr>=0.9 else 'FAIL'}) |")
    log(
        f"| DSR (n_trials={N_TRIALS}) | {dsr:.3f} ({'PASS>=0.95' if dsr>=0.95 else 'FAIL'}) |"
    )
    log(f"| Sharpe 95% CI | {ci_s} |")
    log("")
    log("## MinBTL — the modal kill (K9)")
    log("")
    log("| basis | Sharpe | MinBTL (days) | available | verdict |")
    log("|---|---|---|---|---|")
    log(
        f"| full sample | {sh_full:.3f} | {minbtl_full} | {len(r)} | "
        f"{'PASS' if len(r)>=minbtl_full else 'FAIL'} |"
    )
    actv = "PASS" if len(act) >= minbtl_act else "FAIL"
    log(
        f"| **high-VIX active sub-sample** | {sh_act:.3f} | "
        f"{minbtl_act if minbtl_act<10**8 else 'inf (Sharpe<=0)'} | {len(act)} | **{actv}** |"
    )
    log("")
    log("## Baselines — does the VIX gate earn its place? (K2 / K4 / K3)")
    log("")
    log("| strategy | net Sharpe (1x) | net Sharpe (2x) | maxDD | turnover |")
    log("|---|---|---|---|---|")
    log(
        f"| **VIX-gated reversal (ours)** | **{sh_full:.3f}** | {sweep[2]['sharpe_ratio']:.3f} | "
        f"{res.metrics['max_drawdown']*100:.0f}% | {res.metrics['annual_turnover']*100:.0f}% |"
    )
    log(
        f"| unconditional reversal (K2) | {res_unc.metrics['sharpe_ratio']:.3f} | "
        f"{run_weights_backtest(w_unc, sec_px, cost_bps=COST_BPS*2, shift_bars=SHIFT).metrics['sharpe_ratio']:.3f} | "
        f"{res_unc.metrics['max_drawdown']*100:.0f}% | {res_unc.metrics['annual_turnover']*100:.0f}% |"
    )
    log(
        f"| 21d trailing-vol-gated (K4) | {res_tv.metrics['sharpe_ratio']:.3f} | "
        f"{run_weights_backtest(w_tv, sec_px, cost_bps=COST_BPS*2, shift_bars=SHIFT).metrics['sharpe_ratio']:.3f} | "
        f"{res_tv.metrics['max_drawdown']*100:.0f}% | {res_tv.metrics['annual_turnover']*100:.0f}% |"
    )
    log(
        f"| equal-weight long-only (K3 ctx) | {ew.metrics['sharpe_ratio']:.3f} | n/a | "
        f"{ew.metrics['max_drawdown']*100:.0f}% | {ew.metrics['annual_turnover']*100:.0f}% |"
    )
    log("")
    gate_vs_unc = sh_full - res_unc.metrics["sharpe_ratio"]
    gate_vs_tv = sh_full - res_tv.metrics["sharpe_ratio"]
    log(
        f"- **K2** (gate must add >= +0.15 vs unconditional): delta = {gate_vs_unc:+.3f} "
        f"-> {'PASS' if gate_vs_unc>=0.15 else 'FAIL'}"
    )
    log(
        f"- **K4 (HARD)** (must beat 21d trailing-vol gate): delta = {gate_vs_tv:+.3f} "
        f"-> {'PASS' if gate_vs_tv>0 else 'FAIL — dressed-up vol timing'}"
    )
    log("")
    log("## Honest reading")
    log(
        "- These are REAL engine outputs on local data, but NOT the canonical run. Costs omit the"
    )
    log(
        "  $1 IBKR floor (~50-65 bps/yr at 25k), so net is FLATTERED here. K9 active-sub-sample MinBTL"
    )
    log(
        "  and K4 are the decisive reads. Re-run the networked canonical battery before any verdict."
    )

    report = "\n".join(out)
    with open(
        os.path.join(os.path.dirname(__file__), "PRELIMINARY_BACKTEST_RESULTS.md"), "w"
    ) as fh:
        fh.write(report + "\n")


if __name__ == "__main__":
    main()
