# 2026-06-14: Comprehensive, dependency-light performance metrics for the shared
# weights-contract backtester. Computed in-house (numpy/pandas only) so the full
# quantstats-grade suite is ALWAYS produced regardless of optional deps; the
# quantstats HTML tear sheet (reporting/review.py) is the rich visual layer on top.
"""Comprehensive return-stream performance metrics.

`compute_performance_metrics(returns, benchmark=...)` turns a daily net-returns
series into the full risk/return suite a reviewer expects — the same family of
statistics QuantStats reports, computed here without the dependency so every
review run emits them (written as ``performance.json`` in the run bundle).

Grouped output:
  * returns      — total, CAGR, annualized, best/worst day, win rate, payoff
  * risk         — vol, downside dev, max drawdown (+ duration/recovery), VaR/CVaR,
                   skew, kurtosis, tail ratio, ulcer index
  * risk_adjusted— Sharpe, Sortino, Calmar, gain-to-pain, common-sense ratio
  * periodic     — monthly / yearly return tables, positive-period rates
  * vs_benchmark — beta, alpha, correlation, R2, tracking error, info ratio,
                   up/down capture (only when a benchmark is supplied)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def _f(x: Any) -> float:
    """NaN/inf-safe float coercion for JSON-friendly output."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v if np.isfinite(v) else float("nan")


def _drawdown(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    return (equity - peak) / peak


def _drawdown_stats(returns: pd.Series) -> Dict[str, float]:
    """Max drawdown depth, longest drawdown duration (days), current drawdown,
    average drawdown, time-in-drawdown share, and Ulcer index."""
    equity = (1.0 + returns).cumprod()
    dd = _drawdown(equity)
    max_dd = _f(dd.min())

    # Longest underwater run (consecutive days below the prior peak).
    underwater = dd < -1e-12
    longest = cur = 0
    for u in underwater.to_numpy():
        cur = cur + 1 if u else 0
        longest = max(longest, cur)

    # Average depth across distinct drawdown episodes (trough per episode).
    troughs, run_min = [], 0.0
    for d, u in zip(dd.to_numpy(), underwater.to_numpy()):
        if u:
            run_min = min(run_min, d)
        elif run_min < 0:
            troughs.append(run_min)
            run_min = 0.0
    if run_min < 0:
        troughs.append(run_min)

    return {
        "max_drawdown": max_dd,
        "max_drawdown_days": int(longest),
        "current_drawdown": _f(dd.iloc[-1]) if len(dd) else float("nan"),
        "avg_drawdown": _f(np.mean(troughs)) if troughs else 0.0,
        "n_drawdown_episodes": int(len(troughs)),
        "time_in_drawdown_pct": _f(underwater.mean()),
        "ulcer_index": _f(np.sqrt(np.mean(np.square(dd.to_numpy() * 100.0)))),
    }


def _periodic_table(returns: pd.Series, period: str) -> pd.Series:
    # to_period grouping is stable across pandas versions (avoids the M/ME, Y/YE
    # resample-alias churn between pandas 2.1 and 2.2+).
    return (1.0 + returns).groupby(returns.index.to_period(period)).prod() - 1.0


def _benchmark_block(
    returns: pd.Series, benchmark: pd.Series, rf_daily: float, ppy: int
) -> Dict[str, Any]:
    joined = pd.concat([returns.rename("r"), benchmark.rename("b")], axis=1).dropna()
    if len(joined) < 20 or joined["b"].std() == 0:
        return {"available": False, "reason": "insufficient overlapping data"}
    r, b = joined["r"], joined["b"]
    cov = float(np.cov(r, b)[0, 1])
    var_b = float(np.var(b))
    beta = cov / var_b if var_b > 0 else float("nan")
    corr = float(r.corr(b))
    # annualized alpha (CAPM): mean daily excess - beta * mean daily bench excess
    alpha_daily = (r.mean() - rf_daily) - beta * (b.mean() - rf_daily)
    active = r - b
    te = float(active.std() * np.sqrt(ppy))
    up = b > 0
    down = b < 0
    up_cap = (
        _f((r[up].mean() / b[up].mean()))
        if up.any() and b[up].mean() != 0
        else float("nan")
    )
    down_cap = (
        _f((r[down].mean() / b[down].mean()))
        if down.any() and b[down].mean() != 0
        else float("nan")
    )
    return {
        "available": True,
        "beta": _f(beta),
        "alpha_annualized": _f(alpha_daily * ppy),
        "correlation": _f(corr),
        "r_squared": _f(corr * corr),
        "tracking_error": te,
        "information_ratio": _f(active.mean() / active.std() * np.sqrt(ppy))
        if active.std() > 0
        else float("nan"),
        "up_capture": up_cap,
        "down_capture": down_cap,
        "benchmark_sharpe": _f((b.mean() - rf_daily) / b.std() * np.sqrt(ppy))
        if b.std() > 0
        else float("nan"),
        "n_obs": int(len(joined)),
    }


def compute_performance_metrics(
    returns: pd.Series,
    *,
    benchmark: Optional[pd.Series] = None,
    rf_annual: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> Dict[str, Any]:
    """Full risk/return metric suite for a daily net-returns series.

    Args:
        returns: daily net returns (DatetimeIndex). NaNs are dropped.
        benchmark: optional daily benchmark returns for relative metrics.
        rf_annual: annual risk-free rate (Sharpe/Sortino are excess of this).
        periods_per_year: 252 for daily.
    Returns a nested, JSON-serializable dict (see module docstring).
    """
    r = pd.to_numeric(pd.Series(returns), errors="coerce").dropna()
    ppy = int(periods_per_year)
    if len(r) < 2:
        return {"available": False, "reason": "fewer than 2 return observations"}
    rf_daily = rf_annual / ppy

    n = len(r)
    years = n / ppy
    equity = (1.0 + r).cumprod()
    total_return = _f(equity.iloc[-1] - 1.0)
    cagr = (
        _f(equity.iloc[-1] ** (1.0 / years) - 1.0)
        if equity.iloc[-1] > 0
        else float("nan")
    )
    vol = _f(r.std() * np.sqrt(ppy))
    excess = r - rf_daily
    sharpe = _f(excess.mean() / r.std() * np.sqrt(ppy)) if r.std() > 0 else 0.0

    downside_dev = _f(np.sqrt(np.mean(np.square(r.clip(upper=0.0)))) * np.sqrt(ppy))
    sortino = (
        _f(excess.mean() * ppy / downside_dev) if downside_dev > 0 else float("nan")
    )

    dd = _drawdown_stats(r)
    calmar = (
        _f(cagr / abs(dd["max_drawdown"])) if dd["max_drawdown"] < 0 else float("nan")
    )

    wins, losses = r[r > 0], r[r < 0]
    win_rate = _f(len(wins) / n)
    avg_win = _f(wins.mean()) if len(wins) else 0.0
    avg_loss = _f(losses.mean()) if len(losses) else 0.0
    profit_factor = (
        _f(wins.sum() / abs(losses.sum())) if losses.sum() != 0 else float("inf")
    )
    gain_to_pain = (
        _f(r.sum() / abs(losses.sum())) if losses.sum() != 0 else float("inf")
    )

    p95, p05 = _f(np.percentile(r, 95)), _f(np.percentile(r, 5))
    var95 = p05
    cvar95 = _f(r[r <= np.percentile(r, 5)].mean())
    tail_ratio = _f(abs(p95) / abs(p05)) if p05 != 0 else float("nan")

    monthly = _periodic_table(r, "M")
    yearly = _periodic_table(r, "Y")

    out: Dict[str, Any] = {
        "available": True,
        "window": {
            "start": str(r.index.min().date()),
            "end": str(r.index.max().date()),
            "n_days": n,
            "years": _f(years),
        },
        "returns": {
            "total_return": total_return,
            "cagr": cagr,
            "annualized_return": _f(r.mean() * ppy),
            "best_day": _f(r.max()),
            "worst_day": _f(r.min()),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "win_loss_ratio": _f(avg_win / abs(avg_loss))
            if avg_loss != 0
            else float("inf"),
            "profit_factor": profit_factor,
            "gain_to_pain_ratio": gain_to_pain,
        },
        "risk": {
            "annual_volatility": vol,
            "downside_deviation": downside_dev,
            "skew": _f(r.skew()),
            "kurtosis": _f(r.kurtosis()),  # excess kurtosis
            "var_95_daily": var95,
            "cvar_95_daily": cvar95,
            "tail_ratio": tail_ratio,
            **dd,
        },
        "risk_adjusted": {
            "sharpe": sharpe,
            "sortino": sortino,
            "calmar": calmar,
            "common_sense_ratio": _f(tail_ratio * profit_factor),
        },
        "periodic": {
            "monthly_returns": {str(k): _f(v) for k, v in monthly.items()},
            "yearly_returns": {str(k.year): _f(v) for k, v in yearly.items()},
            "positive_months_pct": _f((monthly > 0).mean())
            if len(monthly)
            else float("nan"),
            "best_month": _f(monthly.max()) if len(monthly) else float("nan"),
            "worst_month": _f(monthly.min()) if len(monthly) else float("nan"),
            "best_year": _f(yearly.max()) if len(yearly) else float("nan"),
            "worst_year": _f(yearly.min()) if len(yearly) else float("nan"),
        },
        "config": {"rf_annual": _f(rf_annual), "periods_per_year": ppy},
    }

    if benchmark is not None:
        b = pd.to_numeric(pd.Series(benchmark), errors="coerce").dropna()
        out["vs_benchmark"] = _benchmark_block(r, b, rf_daily, ppy)
    return out


def performance_headline(metrics: Dict[str, Any]) -> Dict[str, float]:
    """The few rich metrics worth surfacing in verdict.md (beyond Sharpe/MaxDD)."""
    if not metrics.get("available"):
        return {}
    ra, ret, risk = metrics["risk_adjusted"], metrics["returns"], metrics["risk"]
    return {
        "cagr": ret["cagr"],
        "sortino": ra["sortino"],
        "calmar": ra["calmar"],
        "max_drawdown_days": risk["max_drawdown_days"],
        "tail_ratio": risk["tail_ratio"],
        "win_rate": ret["win_rate"],
        "profit_factor": ret["profit_factor"],
    }


__all__ = ["compute_performance_metrics", "performance_headline", "TRADING_DAYS"]
