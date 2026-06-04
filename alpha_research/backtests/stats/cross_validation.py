"""Cross-validation methods for time-series backtesting.

References:
- López de Prado (2018), "Advances in Financial Machine Learning", Ch. 7 & 12
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def purged_kfold_split(
    dates: pd.DatetimeIndex,
    n_splits: int = 5,
    embargo_pct: float = 0.01,
    label_end_times: Optional[pd.Series] = None,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Purged K-Fold cross-validation for time series.

    Two-step contamination removal per López de Prado Ch. 7:

    1. **Purge**: Remove training observations whose label outcome period
       overlaps with the test period. An observation entered at t0 whose
       label resolves at t1 is contaminated if t1 >= test_start_date.
       Requires ``label_end_times`` (t1 for each t0).

    2. **Embargo**: After the test fold ends, drop the next ``embargo_size``
       observations from training. This prevents leakage from features that
       carry test-period information into subsequent training data.

    Args:
        dates: Sorted DatetimeIndex of observation dates (entry times t0).
        n_splits: Number of folds.
        embargo_pct: Fraction of total observations to embargo after each
            test fold. Default 0.01 (1%).
        label_end_times: pd.Series indexed by entry date (t0), values are
            exit/outcome dates (t1). Used for purging. When None, only
            the embargo step is applied.

    Returns:
        List of (train_indices, test_indices) tuples.
    """
    n = len(dates)
    embargo_size = max(int(n * embargo_pct), 1)
    fold_size = n // n_splits

    # Build a date-indexed Series of end times for fast lookup
    end_times_by_date: Optional[pd.Series] = None
    if label_end_times is not None:
        end_times_by_date = pd.Series(
            index=dates, data=np.full(n, pd.NaT), dtype="datetime64[ns]"
        )
        # Align provided end times onto the full date index
        common = label_end_times.index.intersection(dates)
        end_times_by_date.loc[common] = pd.to_datetime(
            label_end_times.loc[common].values
        )

    splits = []
    for i in range(n_splits):
        test_start = i * fold_size
        test_end = min((i + 1) * fold_size, n)

        test_idx = np.arange(test_start, test_end)

        # Embargo: exclude observations immediately after test fold
        embargo_end = min(test_end + embargo_size, n)

        # Initial training set: before test start and after embargo
        train_before = np.arange(0, test_start)
        train_after = np.arange(embargo_end, n)

        # Purge: drop training obs whose label outcome overlaps the test period
        if end_times_by_date is not None and len(train_before) > 0:
            test_start_date = dates[test_start]
            ends = end_times_by_date.iloc[train_before]
            # Keep obs whose outcome resolves before the test period starts,
            # or whose end time is unknown (NaT) — those are safe.
            keep = ends.isna() | (ends < test_start_date)
            train_before = train_before[keep.values]

        train_idx = np.concatenate([train_before, train_after])

        if len(train_idx) > 0 and len(test_idx) > 0:
            splits.append((train_idx, test_idx))

    return splits


def cpcv_split(
    dates: pd.DatetimeIndex,
    n_splits: int = 6,
    n_test_groups: int = 2,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Combinatorial Purged Cross-Validation (CPCV).

    Generates all C(n_splits, n_test_groups) combinations of test groups.
    Each combination uses n_test_groups groups as test and the rest as train.

    This produces many more paths than standard K-fold, enabling backtest
    overfitting analysis.

    Args:
        dates: Sorted DatetimeIndex.
        n_splits: Number of groups to split data into.
        n_test_groups: Number of groups to use as test in each combination.

    Returns:
        List of (train_indices, test_indices) tuples.
    """
    n = len(dates)
    fold_size = n // n_splits

    # Create group boundaries
    groups = []
    for i in range(n_splits):
        start = i * fold_size
        end = min((i + 1) * fold_size, n)
        if i == n_splits - 1:
            end = n  # Last group gets remainder
        groups.append(np.arange(start, end))

    # Generate all combinations of test groups
    splits = []
    for test_group_indices in combinations(range(n_splits), n_test_groups):
        test_idx = np.concatenate([groups[i] for i in test_group_indices])
        train_group_indices = [
            i for i in range(n_splits) if i not in test_group_indices
        ]
        train_idx = np.concatenate([groups[i] for i in train_group_indices])

        if len(train_idx) > 0 and len(test_idx) > 0:
            splits.append((train_idx, test_idx))

    return splits


def walk_forward_split(
    dates: pd.DatetimeIndex,
    train_window: int,
    test_window: int,
    step: Optional[int] = None,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Walk-forward (rolling window) cross-validation.

    Args:
        dates: Sorted DatetimeIndex.
        train_window: Number of observations in training window.
        test_window: Number of observations in test window.
        step: Step size for rolling (default: test_window = non-overlapping).

    Returns:
        List of (train_indices, test_indices) tuples.
    """
    n = len(dates)
    if step is None:
        step = test_window

    splits = []
    start = 0

    while start + train_window + test_window <= n:
        train_idx = np.arange(start, start + train_window)
        test_idx = np.arange(
            start + train_window,
            min(start + train_window + test_window, n),
        )

        if len(test_idx) > 0:
            splits.append((train_idx, test_idx))

        start += step

    return splits
