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

    if observed_sharpe <= 0 or n_trials < 1:
        return int(1e6)  # Effectively infinite — strategy has no edge

    z_alpha = stats.norm.ppf(confidence)

    # Expected maximum Sharpe under the null (same as DSR calculation)
    if n_trials > 1:
        euler_mascheroni = 0.5772156649
        e_max_sr = np.sqrt(2 * np.log(n_trials)) - (
            np.log(np.pi) + euler_mascheroni
        ) / (2 * np.sqrt(2 * np.log(n_trials)))
    else:
        e_max_sr = 0.0

    # If observed Sharpe doesn't beat the expected max, need infinite data
    if observed_sharpe <= e_max_sr:
        return int(1e6)

    # Excess kurtosis
    excess_kurt = kurtosis - 3.0

    # MinBTL formula (from Bailey & López de Prado)
    # n >= (z_alpha / (SR - SR*))^2 * (1 - skew*SR + (kurt-1)/4 * SR^2)
    # where SR is annualized Sharpe per sqrt(period)
    sr = observed_sharpe
    sr_star = e_max_sr

    adjustment = 1 - skewness * sr + (excess_kurt / 4) * sr**2
    if adjustment <= 0:
        adjustment = 1.0

    min_n = (z_alpha / (sr - sr_star)) ** 2 * adjustment

    # Convert from "Sharpe periods" to daily observations
    # The formula gives min observations in annualized units; scale to daily
    min_daily = min_n * 252

    return int(np.ceil(min_daily))


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
