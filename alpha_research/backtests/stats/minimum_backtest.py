"""Minimum Backtest Length (MinBTL).

Reference:
- Bailey & López de Prado (2014), "The Deflated Sharpe Ratio"
- Bailey, Borwein, López de Prado & Zhu (2016), "The Probability of Backtest Overfitting"
"""

from __future__ import annotations

import numpy as np


def minimum_backtest_length(
    observed_sharpe: float,
    n_trials: int,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    confidence: float = 0.95,
) -> int:
    """Estimate the minimum number of observations needed for a valid backtest.

    Given an observed Sharpe ratio and the number of trials conducted,
    computes the minimum sample size required for the Sharpe to be
    statistically significant at the given confidence level.

    Args:
        observed_sharpe: Annualized Sharpe ratio of the strategy.
        n_trials: Number of strategy configurations tested.
        skewness: Skewness of the return distribution.
        kurtosis: Kurtosis of the return distribution (3 = normal).
        confidence: Required confidence level (e.g. 0.95).

    Returns:
        Minimum number of daily observations (trading days) required.
    """
    from scipy import stats

    from alpha_research.backtests.stats.sharpe_tests import expected_max_z

    if observed_sharpe <= 0 or n_trials < 1:
        return int(1e6)  # Effectively infinite — strategy has no edge

    z_alpha = stats.norm.ppf(confidence)

    # Expected maximum of n_trials standard normals — z-score units.
    # Under the null, the max-trial Sharpe estimate over n periods is
    # ~ e_max_z / sqrt(n), so comparisons must use the per-period Sharpe.
    e_max_z = expected_max_z(n_trials)

    # Daily (per-period) Sharpe from the annualized input
    sr_daily = observed_sharpe / np.sqrt(252)

    # Excess kurtosis; non-normality adjustment on the SR standard error
    # (Lo 2002 / Bailey & López de Prado), evaluated at the daily SR.
    excess_kurt = kurtosis - 3.0
    adjustment = 1 - skewness * sr_daily + (excess_kurt / 4) * sr_daily**2
    if adjustment <= 0:
        adjustment = 1.0

    # Require the observed daily SR to clear the expected max-trial null
    # by z_alpha standard errors:
    #   sr_daily >= (e_max_z + z_alpha * sqrt(adjustment)) / sqrt(n)
    min_daily = ((e_max_z + z_alpha * np.sqrt(adjustment)) / sr_daily) ** 2

    return int(np.ceil(min(min_daily, 1e6)))


def min_track_record_length(
    observed_sharpe: float,
    benchmark_sharpe: float = 0.0,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    confidence: float = 0.95,
    frequency: int = 252,
) -> float:
    """Minimum Track Record Length (MinTRL) in years.

    Simplified version: given an observed annualized Sharpe and a benchmark,
    how many years of data do we need?

    Args:
        observed_sharpe: Observed annualized Sharpe.
        benchmark_sharpe: Benchmark annualized Sharpe to beat.
        skewness: Return skewness.
        kurtosis: Return kurtosis.
        confidence: Confidence level.
        frequency: Observations per year (252 for daily).

    Returns:
        Minimum track record in years.
    """
    min_days = minimum_backtest_length(
        observed_sharpe=observed_sharpe,
        n_trials=1,
        skewness=skewness,
        kurtosis=kurtosis,
        confidence=confidence,
    )

    return min_days / frequency
