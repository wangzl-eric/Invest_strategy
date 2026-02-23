"""Blend signals/strategies into a unified expected return (alpha) estimate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Signal:
    name: str
    score: pd.Series  # per-asset signal score
    weight: float = 1.0


def zscore(s: pd.Series) -> pd.Series:
    x = s.astype(float)
    std = x.std()
    if std == 0 or np.isnan(std):
        return x * 0.0
    return (x - x.mean()) / std


def blend_signals(signals: list[Signal], *, zscore_each: bool = True) -> pd.Series:
    """Weighted sum of signals -> alpha score per asset."""

    if not signals:
        return pd.Series(dtype=float)

    # Align universe
    idx = signals[0].score.index
    for s in signals[1:]:
        idx = idx.union(s.score.index)

    alpha = pd.Series(0.0, index=idx)
    for s in signals:
        x = s.score.reindex(idx)
        x = zscore(x) if zscore_each else x.astype(float)
        alpha = alpha + (float(s.weight) * x.fillna(0.0))
    return alpha

