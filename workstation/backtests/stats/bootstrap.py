"""Block bootstrap for time-series data.

Preserves autocorrelation structure by resampling contiguous blocks.
"""

from __future__ import annotations

from typing import Callable, List

import numpy as np


def block_bootstrap(
    data: np.ndarray,
    stat_func: Callable[[np.ndarray], float],
    n_bootstrap: int = 5000,
    block_size: int = 21,
    seed: int = 42,
) -> np.ndarray:
    """Circular block bootstrap for time series.

    Args:
        data: 1D array of observations (e.g. daily returns).
        stat_func: Function that computes a scalar statistic from data.
        n_bootstrap: Number of bootstrap replications.
        block_size: Size of contiguous blocks to resample.
        seed: Random seed for reproducibility.

    Returns:
        Array of n_bootstrap bootstrapped statistic values.
    """
    data = np.asarray(data, dtype=float)
    n = len(data)
    rng = np.random.RandomState(seed)

    if n < block_size:
        block_size = max(1, n // 2)

    n_blocks = int(np.ceil(n / block_size))
    results = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        # Random starting points for blocks (circular)
        starts = rng.randint(0, n, size=n_blocks)
        indices = np.concatenate([np.arange(s, s + block_size) % n for s in starts])[:n]
        boot_sample = data[indices]
        results[b] = stat_func(boot_sample)

    return results


def stationary_bootstrap(
    data: np.ndarray,
    stat_func: Callable[[np.ndarray], float],
    n_bootstrap: int = 5000,
    avg_block_size: float = 21.0,
    seed: int = 42,
) -> np.ndarray:
    """Stationary bootstrap (Politis & Romano, 1994).

    Block lengths are geometrically distributed, producing stationary
    resampled series.

    Args:
        data: 1D array of observations.
        stat_func: Statistic function.
        n_bootstrap: Number of replications.
        avg_block_size: Expected block length (geometric distribution).
        seed: Random seed.

    Returns:
        Array of bootstrapped statistic values.
    """
    data = np.asarray(data, dtype=float)
    n = len(data)
    rng = np.random.RandomState(seed)
    p = 1.0 / avg_block_size  # Probability of starting new block

    results = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        boot_sample = np.empty(n)
        idx = rng.randint(0, n)

        for i in range(n):
            boot_sample[i] = data[idx % n]
            if rng.random() < p:
                idx = rng.randint(0, n)  # Start new block
            else:
                idx += 1  # Continue current block

        results[b] = stat_func(boot_sample)

    return results
