"""Probabilistic Sharpe Ratio, Deflated Sharpe, and bootstrap confidence intervals.

References:
- Bailey & López de Prado (2012), "The Sharpe Ratio Efficient Frontier"
- Bailey & López de Prado (2014), "The Deflated Sharpe Ratio"
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy import stats


def probabilistic_sharpe_ratio(
    returns: np.ndarray,
    benchmark_sharpe: float = 0.0,
    risk_free_rate: float = 0.0,
) -> float:
    """Compute the Probabilistic Sharpe Ratio (PSR).

    PSR gives the probability that the observed Sharpe ratio exceeds a
    benchmark Sharpe, accounting for skewness and kurtosis of returns.

    Args:
        returns: Array of period returns (e.g. daily).
        benchmark_sharpe: Sharpe ratio to beat (annualized).
        risk_free_rate: Annual risk-free rate (subtracted from mean).

    Returns:
        PSR value in [0, 1].  Values > 0.95 are statistically significant.
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n < 10:
        return 0.0

    # Daily excess returns
    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf

    mu = np.mean(excess)
    sigma = np.std(excess, ddof=1)
    if sigma == 0:
        return 0.0

    # Observed Sharpe (annualized)
    sr_obs = (mu / sigma) * np.sqrt(252)

    # Skewness and excess kurtosis of returns
    skew = stats.skew(excess)
    kurt = stats.kurtosis(excess, fisher=True)  # excess kurtosis

    # Standard error of the Sharpe ratio (Lo 2002, adjusted for non-normality)
    sr_daily = mu / sigma
    se = np.sqrt((1 - skew * sr_daily + ((kurt - 1) / 4) * sr_daily**2) / (n - 1))

    if se == 0:
        return 0.0

    # PSR = Prob(SR > SR*) = Phi((SR_obs - SR*) / SE(SR))
    # Convert benchmark from annualized to daily-scale for comparison
    benchmark_daily_scale = benchmark_sharpe / np.sqrt(252)
    z = (sr_daily - benchmark_daily_scale) / se
    psr = stats.norm.cdf(z)

    return float(psr)


def deflated_sharpe_ratio(
    returns: np.ndarray,
    n_trials: int,
    risk_free_rate: float = 0.0,
) -> float:
    """Compute the Deflated Sharpe Ratio (DSR).

    Adjusts the observed Sharpe for multiple testing by estimating the
    expected maximum Sharpe from *n_trials* independent strategies under
    the null hypothesis of zero alpha.

    Args:
        returns: Array of period returns for the **best** strategy found.
        n_trials: Number of strategy variations / backtests tried.
        risk_free_rate: Annual risk-free rate.

    Returns:
        DSR in [0, 1].  Always <= PSR.  Values > 0.95 are significant.
    """
    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    n = len(returns)
    if n < 10 or n_trials < 1:
        return 0.0

    # Expected maximum Sharpe under the null (Euler-Mascheroni approx)
    euler_mascheroni = 0.5772156649
    e_max_sr = np.sqrt(2 * np.log(n_trials)) - (np.log(np.pi) + euler_mascheroni) / (
        2 * np.sqrt(2 * np.log(n_trials))
    )

    # Annualize the benchmark
    benchmark_sharpe = e_max_sr

    return probabilistic_sharpe_ratio(
        returns,
        benchmark_sharpe=benchmark_sharpe,
        risk_free_rate=risk_free_rate,
    )


def sharpe_confidence_interval(
    returns: np.ndarray,
    confidence: float = 0.95,
    n_bootstrap: int = 5000,
    block_size: int = 21,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap confidence interval for the annualized Sharpe ratio.

    Uses block bootstrap to preserve autocorrelation structure.

    Args:
        returns: Array of period returns.
        confidence: Confidence level (default 0.95).
        n_bootstrap: Number of bootstrap replications.
        block_size: Block size for block bootstrap (default 21 ≈ 1 month).
        seed: Random seed for reproducibility.

    Returns:
        (lower_bound, point_estimate, upper_bound) — all annualized.
    """
    from backtests.stats.bootstrap import block_bootstrap

    returns = np.asarray(returns, dtype=float)
    returns = returns[~np.isnan(returns)]
    if len(returns) < block_size * 2:
        sr = _annualized_sharpe(returns)
        return (sr, sr, sr)

    def sharpe_stat(r: np.ndarray) -> float:
        return _annualized_sharpe(r)

    boot_sharpes = block_bootstrap(
        returns,
        stat_func=sharpe_stat,
        n_bootstrap=n_bootstrap,
        block_size=block_size,
        seed=seed,
    )

    alpha = 1 - confidence
    lower = float(np.percentile(boot_sharpes, 100 * alpha / 2))
    upper = float(np.percentile(boot_sharpes, 100 * (1 - alpha / 2)))
    point = _annualized_sharpe(returns)

    return (lower, point, upper)


def _annualized_sharpe(returns: np.ndarray) -> float:
    """Helper: annualized Sharpe (assumes daily returns)."""
    if len(returns) == 0:
        return 0.0
    mu = np.mean(returns)
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    return float((mu / sigma) * np.sqrt(252))
