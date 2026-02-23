"""Risk model utilities (covariance estimation, basic stress tests)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


def sample_cov(returns: pd.DataFrame) -> pd.DataFrame:
    r = returns.dropna(how="any")
    if r.empty:
        raise ValueError("returns empty after dropna")
    return r.cov()


def ledoit_wolf_cov(returns: pd.DataFrame) -> pd.DataFrame:
    """Shrinkage covariance (works well for noisy multi-asset signals)."""

    r = returns.dropna(how="any")
    if r.empty:
        raise ValueError("returns empty after dropna")

    try:
        from sklearn.covariance import LedoitWolf
    except Exception as e:  # pragma: no cover
        raise ImportError("scikit-learn required for LedoitWolf covariance") from e

    lw = LedoitWolf().fit(r.values)
    return pd.DataFrame(lw.covariance_, index=r.columns, columns=r.columns)


@dataclass(frozen=True)
class StressScenario:
    name: str
    shock: pd.Series  # per-asset return shock, indexed by asset


def apply_stress(weights: pd.Series, scenario: StressScenario) -> float:
    """Scenario P&L approximation (single-period)."""

    w = weights.reindex(scenario.shock.index).fillna(0.0)
    return float((w * scenario.shock).sum())

