"""Multiple testing corrections for backtesting.

References:
- White (2000), "A Reality Check for Data Snooping"
- Hansen (2005), "A Test for Superior Predictive Ability"
- Benjamini & Hochberg (1995), FDR control
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np


def bonferroni_correction(
    p_values: np.ndarray, alpha: float = 0.05
) -> Tuple[np.ndarray, np.ndarray]:
    """Bonferroni correction for multiple testing.

    Args:
        p_values: Array of p-values from individual tests.
        alpha: Family-wise error rate.

    Returns:
        (reject_mask, adjusted_p_values) — boolean array and adjusted p-values.
    """
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    adjusted = np.minimum(p_values * n, 1.0)
    reject = adjusted < alpha
    return reject, adjusted


def fdr_correction(
    p_values: np.ndarray, alpha: float = 0.05
) -> Tuple[np.ndarray, np.ndarray]:
    """Benjamini-Hochberg False Discovery Rate correction.

    Controls the expected proportion of false positives among rejected hypotheses.

    Args:
        p_values: Array of p-values.
        alpha: Target FDR level.

    Returns:
        (reject_mask, adjusted_p_values).
    """
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    if n == 0:
        return np.array([], dtype=bool), np.array([], dtype=float)

    # Sort p-values
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]

    # BH thresholds: (rank / n) * alpha
    ranks = np.arange(1, n + 1)
    thresholds = (ranks / n) * alpha

    # Find largest k where p_(k) <= threshold
    reject_sorted = sorted_p <= thresholds
    if reject_sorted.any():
        max_reject_idx = np.max(np.where(reject_sorted))
        reject_sorted[:] = False
        reject_sorted[: max_reject_idx + 1] = True
    else:
        reject_sorted[:] = False

    # Adjusted p-values (Benjamini-Hochberg method)
    adjusted = np.empty(n)
    adjusted[sorted_idx[-1]] = sorted_p[-1]
    for i in range(n - 2, -1, -1):
        adjusted[sorted_idx[i]] = min(
            adjusted[sorted_idx[i + 1]], sorted_p[i] * n / (i + 1)
        )
    adjusted = np.minimum(adjusted, 1.0)

    # Unsort reject mask
    reject = np.zeros(n, dtype=bool)
    reject[sorted_idx] = reject_sorted

    return reject, adjusted


def whites_reality_check(
    strategy_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    n_bootstrap: int = 1000,
    block_size: int = 21,
    seed: int = 42,
) -> Tuple[float, float]:
    """White's Reality Check for data snooping.

    Tests whether the best strategy is genuinely better than the benchmark,
    accounting for the number of strategies tested.

    Args:
        strategy_returns: 2D array (n_days, n_strategies) of strategy returns.
        benchmark_returns: 1D array of benchmark returns (e.g. buy-and-hold).
        n_bootstrap: Number of bootstrap replications.
        block_size: Block size for circular block bootstrap.
        seed: Random seed.

    Returns:
        (test_statistic, p_value).  Reject null if p_value < alpha.
    """
    strategy_returns = np.asarray(strategy_returns)
    benchmark_returns = np.asarray(benchmark_returns)

    if strategy_returns.ndim == 1:
        strategy_returns = strategy_returns.reshape(-1, 1)

    n_days = len(benchmark_returns)
    n_strategies = strategy_returns.shape[1]

    # Excess performance of each strategy over benchmark
    excess = strategy_returns - benchmark_returns.reshape(-1, 1)

    # Observed test statistic: max of mean excess returns
    mean_excess = np.mean(excess, axis=0)
    observed_stat = np.max(mean_excess) * np.sqrt(n_days)

    # Bootstrap distribution under the null
    rng = np.random.RandomState(seed)
    boot_stats = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        # Circular block bootstrap indices
        indices = _circular_block_indices(n_days, block_size, rng)
        boot_excess = excess[indices, :]

        # Center to impose the null hypothesis (zero expected excess return)
        boot_mean = np.mean(boot_excess, axis=0) - mean_excess
        boot_stats[b] = np.max(boot_mean) * np.sqrt(n_days)

    # p-value: fraction of bootstrap stats >= observed stat
    p_value = float(np.mean(boot_stats >= observed_stat))

    return float(observed_stat), p_value


def _circular_block_indices(
    n: int, block_size: int, rng: np.random.RandomState
) -> np.ndarray:
    """Generate circular block bootstrap indices."""
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.randint(0, n, size=n_blocks)
    indices = np.concatenate([np.arange(s, s + block_size) % n for s in starts])
    return indices[:n]
