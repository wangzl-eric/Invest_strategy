"""Common performance metrics for strategy evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return 0.0
    std = float(r.std())
    if std == 0.0 or np.isnan(std) or np.isinf(std):
        return 0.0
    return float(np.sqrt(periods_per_year) * r.mean() / std)


def max_drawdown(equity: pd.Series) -> float:
    e = equity.dropna()
    if len(e) < 2:
        return 0.0
    peak = e.cummax()
    dd = (e / peak) - 1.0
    m = float(dd.min())
    if np.isnan(m) or np.isinf(m):
        return 0.0
    return m


def total_return(equity: pd.Series) -> float:
    e = equity.dropna()
    if len(e) < 2:
        return 0.0
    return float(e.iloc[-1] / e.iloc[0] - 1.0)


def turnover(positions: pd.Series) -> float:
    """Simple turnover estimate: sum(abs(delta position))."""
    p = positions.fillna(0.0)
    return float(p.diff().abs().sum())

