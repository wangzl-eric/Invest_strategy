"""Decay analysis and strategy lifecycle diagnostics.

Tools for understanding whether a strategy's edge is persistent or
decaying, how correlated it is with existing strategies, and its
approximate capacity.

References:
- "The Half-Life of Facts" (Arbesman, 2012) for decay modeling
- Square-root market impact model (Almgren & Chriss, 2000)

Usage:
    from backtests.stats.decay_analysis import (
        rolling_sharpe,
        strategy_half_life,
        correlation_with_existing,
        capacity_estimate,
        regime_conditional_sharpe,
        strategy_capacity_estimate,
        sharpe_decay_rate,
    )

    rs = rolling_sharpe(daily_returns, window=252)
    hl = strategy_half_life(rs)
    corr = correlation_with_existing(new_rets, {"a": rets_a, "b": rets_b})
    cap = capacity_estimate(returns, volumes)
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_TRADING_DAYS_PER_YEAR = 252


def rolling_sharpe(
    returns: pd.Series,
    window: int = 63,
    risk_free_rate: float = 0.0,
    annualize: bool = True,
) -> pd.Series:
    """Compute rolling annualized Sharpe ratio.

    Args:
        returns: Daily return series with DatetimeIndex.
        window: Rolling window in trading days (default 63 ~ 3 months).
        risk_free_rate: Annual risk-free rate.
        annualize: Scale to annualised Sharpe (default True).

    Returns:
        Series of Sharpe ratios, same index as returns.
        NaN for the initial warmup period.
    """
    returns = pd.Series(returns, dtype=float)
    daily_rf = risk_free_rate / _TRADING_DAYS_PER_YEAR

    excess = returns - daily_rf
    roll_mean = excess.rolling(window, min_periods=window).mean()
    roll_std = excess.rolling(window, min_periods=window).std()

    sharpe = roll_mean / roll_std.replace(0, np.nan)

    if annualize:
        sharpe = sharpe * np.sqrt(_TRADING_DAYS_PER_YEAR)

    return sharpe.rename("rolling_sharpe")


def strategy_half_life(
    rolling_sharpes_or_returns: pd.Series,
    window: int = 252,
) -> Optional[float]:
    """Estimate the half-life of a strategy's Sharpe ratio decay.

    Accepts either a pre-computed rolling Sharpe series or raw daily
    returns (in which case rolling Sharpe is computed internally with
    the given *window*).

    Fits an exponential decay model ``SR(t) = SR_peak * exp(-lambda * t)``
    to the rolling Sharpe series after its peak.

    Args:
        rolling_sharpes_or_returns: Series of rolling Sharpe ratios
            (e.g. from :func:`rolling_sharpe`) **or** daily returns.
        window: If the input looks like raw returns (values mostly in
            [-0.2, 0.2]), compute rolling Sharpe with this window first.

    Returns:
        Half-life in trading days (``ln(2) / lambda``), or None if
        no meaningful decay is detected.
    """
    series = rolling_sharpes_or_returns.dropna()

    # Heuristic: if most values are tiny, treat as raw returns
    if len(series) > window and series.abs().median() < 0.5:
        series = rolling_sharpe(series, window=window).dropna()

    sharpes = series
    if len(sharpes) < 60:
        return None

    # Find the peak Sharpe
    peak_idx = sharpes.idxmax()
    peak_loc = sharpes.index.get_loc(peak_idx)
    post_peak = sharpes.iloc[peak_loc:]

    if len(post_peak) < 30:
        return None

    peak_val = post_peak.iloc[0]
    if peak_val <= 0:
        return None

    # Normalize: SR_norm = SR(t) / SR_peak
    sr_norm = post_peak / peak_val

    # Filter to positive values for log fit
    sr_positive = sr_norm[sr_norm > 0]
    if len(sr_positive) < 30:
        return None

    # Fit log(SR_norm) = -lambda * t via least squares
    t = np.arange(len(sr_positive), dtype=float)
    log_sr = np.log(sr_positive.values)

    valid_mask = np.isfinite(log_sr)
    t_valid = t[valid_mask]
    log_sr_valid = log_sr[valid_mask]

    if len(t_valid) < 20:
        return None

    # OLS: log_sr = a + b*t, where b = -lambda
    n = len(t_valid)
    t_mean = t_valid.mean()
    log_mean = log_sr_valid.mean()

    numerator = np.sum((t_valid - t_mean) * (log_sr_valid - log_mean))
    denominator = np.sum((t_valid - t_mean) ** 2)

    if denominator == 0:
        return None

    slope = numerator / denominator

    if slope >= -1e-6:
        return None

    lam = -slope
    half_life = np.log(2) / lam

    if half_life <= 0 or half_life > 10_000:
        return None

    return float(half_life)


def correlation_with_existing(
    new_returns: pd.Series,
    existing_returns: Dict[str, pd.Series],
    min_overlap: int = 60,
) -> pd.DataFrame:
    """Correlation matrix showing diversification value of a new strategy.

    Builds a DataFrame of *all* strategies (existing + new) and computes
    pairwise Pearson correlation on overlapping dates.

    Args:
        new_returns: Daily returns of the candidate strategy.
        existing_returns: Dict of strategy_name -> daily return series.
        min_overlap: Minimum overlapping observations required.

    Returns:
        Square correlation DataFrame.  If fewer than ``min_overlap``
        dates overlap, the matrix will contain NaNs for those pairs.
    """
    combined: Dict[str, pd.Series] = {}
    for name, existing in existing_returns.items():
        combined[name] = existing
    combined["new_strategy"] = new_returns

    aligned = pd.DataFrame(combined).dropna()

    if len(aligned) < min_overlap:
        logger.warning(
            "Only %d overlapping dates (need %d); returning partial correlations",
            len(aligned),
            min_overlap,
        )
        # Fall back to pairwise correlations with varying overlap
        all_data = pd.DataFrame(combined)
        return all_data.corr()

    return aligned.corr()


def capacity_estimate(
    returns: pd.Series,
    volumes: pd.Series,
    participation_rate: float = 0.01,
    avg_spread_bps: float = 5.0,
) -> Dict[str, float]:
    """Estimate maximum AUM before market-impact erodes alpha.

    Uses a square-root market-impact model:
        cost = spread + k * sqrt(participation)
    where *participation* = strategy_volume / market_volume.

    The capacity is the AUM at which impact costs consume half the gross
    alpha (a conservative breakpoint).

    Args:
        returns: Daily strategy returns (gross of costs).
        volumes: Daily dollar volume Series of the traded instrument(s).
        participation_rate: Fraction of daily volume the strategy trades
            on each rebalance (default 1%).
        avg_spread_bps: Average half-spread in basis points.

    Returns:
        Dict with ``gross_alpha_bps``, ``estimated_impact_bps``,
        ``max_aum``, and ``breakeven_aum``.
    """
    common = returns.index.intersection(volumes.index)
    if len(common) < 20:
        logger.warning("Insufficient overlapping data for capacity estimate")
        return {
            "gross_alpha_bps": float("nan"),
            "estimated_impact_bps": float("nan"),
            "max_aum": float("nan"),
            "breakeven_aum": float("nan"),
        }

    rets = returns.loc[common]
    vols = volumes.loc[common]

    # Gross alpha in bps (annualised)
    gross_daily = rets.mean()
    gross_annual = gross_daily * _TRADING_DAYS_PER_YEAR
    gross_bps = gross_annual * 10_000

    avg_daily_volume = vols.mean()

    # k calibrated to ~10 bps at 1% participation (empirical midcap proxy)
    k = 10.0 / np.sqrt(0.01)

    spread_cost = avg_spread_bps
    target_impact = max(gross_bps / 2 - spread_cost, 0)

    if target_impact <= 0 or avg_daily_volume <= 0:
        return {
            "gross_alpha_bps": round(float(gross_bps), 2),
            "estimated_impact_bps": float("nan"),
            "max_aum": 0.0,
            "breakeven_aum": 0.0,
        }

    # target_impact = k * sqrt(AUM * participation / avg_volume)
    # AUM = (target_impact / k)^2 * avg_volume / participation
    max_aum = (target_impact / k) ** 2 * avg_daily_volume / participation_rate

    breakeven_target = max(gross_bps - spread_cost, 0)
    breakeven_aum = (
        (breakeven_target / k) ** 2 * avg_daily_volume / participation_rate
        if breakeven_target > 0
        else 0.0
    )

    impact_bps = spread_cost + k * np.sqrt(participation_rate)

    return {
        "gross_alpha_bps": round(float(gross_bps), 2),
        "estimated_impact_bps": round(float(impact_bps), 2),
        "max_aum": round(float(max_aum), 0),
        "breakeven_aum": round(float(breakeven_aum), 0),
    }


# ---------------------------------------------------------------------------
# Additional utilities (preserved from original)
# ---------------------------------------------------------------------------


def regime_conditional_sharpe(
    returns: pd.Series,
    regime_labels: pd.Series,
    risk_free_rate: float = 0.0,
) -> Dict[str, float]:
    """Compute Sharpe ratio broken down by regime.

    Args:
        returns: Daily return series.
        regime_labels: Series of regime labels (e.g. "bull", "bear",
            "high_vol") aligned to the same index as returns.
        risk_free_rate: Annual risk-free rate.

    Returns:
        Dict of regime_label -> annualized Sharpe ratio.
    """
    aligned = pd.DataFrame({"returns": returns, "regime": regime_labels}).dropna()

    if aligned.empty:
        return {}

    daily_rf = risk_free_rate / _TRADING_DAYS_PER_YEAR
    results: Dict[str, float] = {}

    for label in aligned["regime"].unique():
        regime_rets = aligned.loc[aligned["regime"] == label, "returns"]

        if len(regime_rets) < 20:
            results[str(label)] = np.nan
            continue

        excess = regime_rets - daily_rf
        mu = excess.mean()
        sigma = excess.std()

        if sigma == 0:
            results[str(label)] = 0.0
        else:
            results[str(label)] = float((mu / sigma) * np.sqrt(_TRADING_DAYS_PER_YEAR))

    return results


def strategy_capacity_estimate(
    returns: pd.Series,
    avg_daily_volume: float,
    current_aum: float = 0.0,
    participation_rate: float = 0.10,
    impact_exponent: float = 0.5,
) -> float:
    """Estimate maximum AUM (scalar volume variant).

    Uses a simplified square-root market impact model.

    Args:
        returns: Daily return series of the strategy.
        avg_daily_volume: Average daily dollar volume of traded instruments.
        current_aum: Current AUM (for existing impact adjustment).
        participation_rate: Max fraction of ADV per day (default 10%).
        impact_exponent: Exponent for the market impact model (default 0.5).

    Returns:
        Estimated max AUM in dollars.
    """
    returns = pd.Series(returns, dtype=float).dropna()

    if len(returns) < 60:
        return 0.0

    annual_return = float(returns.mean() * _TRADING_DAYS_PER_YEAR)
    if annual_return <= 0:
        return 0.0

    daily_turnover_rate = float(returns.abs().mean())
    if daily_turnover_rate <= 0:
        daily_turnover_rate = 0.01

    k = 0.001

    ratio = annual_return / (k * _TRADING_DAYS_PER_YEAR)
    if ratio <= 0:
        return 0.0

    capacity = (avg_daily_volume / daily_turnover_rate) * (
        ratio ** (1 / impact_exponent)
    )

    return float(max(0.0, capacity))


def sharpe_decay_rate(
    rolling_sharpes: pd.Series,
    window: int = 63,
) -> pd.Series:
    """Compute the rolling rate of Sharpe change (first derivative).

    Negative values indicate the strategy is losing edge.

    Args:
        rolling_sharpes: Series of rolling Sharpe ratios.
        window: Window for computing the slope.

    Returns:
        Series of Sharpe change rates (units: Sharpe points per day).
    """
    sharpes = rolling_sharpes.dropna()
    if len(sharpes) < window:
        return pd.Series(dtype=float)

    def _slope(arr: np.ndarray) -> float:
        n = len(arr)
        if n < 10:
            return np.nan
        x = np.arange(n, dtype=float)
        x_mean = x.mean()
        y_mean = arr.mean()
        num = np.sum((x - x_mean) * (arr - y_mean))
        den = np.sum((x - x_mean) ** 2)
        if den == 0:
            return 0.0
        return num / den

    return sharpes.rolling(window, min_periods=window).apply(_slope, raw=True)


__all__ = [
    "rolling_sharpe",
    "strategy_half_life",
    "correlation_with_existing",
    "capacity_estimate",
    "regime_conditional_sharpe",
    "strategy_capacity_estimate",
    "sharpe_decay_rate",
]
