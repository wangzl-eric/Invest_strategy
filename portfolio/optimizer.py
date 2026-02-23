"""Portfolio optimization (constraints, turnover, risk)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OptimizationConfig:
    risk_aversion: float = 1.0  # larger -> more risk penalty
    turnover_aversion: float = 0.0  # L1 turnover penalty
    max_weight: float = 0.10
    min_weight: float = -0.10  # allow modest shorting by default
    target_gross: Optional[float] = None  # if set, constrain sum(abs(w)) <= target_gross


def mean_variance_optimize(
    *,
    expected_returns: pd.Series,
    cov: pd.DataFrame,
    prev_weights: Optional[pd.Series] = None,
    cfg: Optional[OptimizationConfig] = None,
) -> pd.Series:
    """Solve a basic convex program:

    maximize   mu^T w - λ * w^T Σ w - γ * ||w - w_prev||_1
    subject to sum(w) == 1
               min_weight <= w_i <= max_weight
               (optional) sum(|w_i|) <= target_gross
    """

    cfg = cfg or OptimizationConfig()

    assets = expected_returns.index
    mu = expected_returns.astype(float).values
    Sigma = cov.reindex(index=assets, columns=assets).astype(float).values

    if prev_weights is None:
        w0 = np.zeros(len(assets))
    else:
        w0 = prev_weights.reindex(assets).fillna(0.0).astype(float).values

    try:
        import cvxpy as cp
    except Exception as e:  # pragma: no cover
        raise ImportError("cvxpy is required for portfolio optimization") from e

    w = cp.Variable(len(assets))

    # risk term (quadratic form). Add small ridge for numerical stability.
    Sigma_stable = Sigma + 1e-8 * np.eye(len(assets))
    risk = cp.quad_form(w, Sigma_stable)

    turnover = cp.norm1(w - w0)
    obj = cp.Maximize(mu @ w - float(cfg.risk_aversion) * risk - float(cfg.turnover_aversion) * turnover)

    constraints = [
        cp.sum(w) == 1.0,
        w <= float(cfg.max_weight),
        w >= float(cfg.min_weight),
    ]
    if cfg.target_gross is not None:
        constraints.append(cp.norm1(w) <= float(cfg.target_gross))

    prob = cp.Problem(obj, constraints)
    prob.solve(solver=cp.OSQP, verbose=False)

    if w.value is None:
        raise RuntimeError(f"Optimization failed (status={prob.status})")

    out = pd.Series(w.value, index=assets).astype(float)
    # Clean tiny numerical noise
    out[abs(out) < 1e-12] = 0.0
    return out


def weights_from_alpha(
    *,
    alpha: pd.Series,
    returns: pd.DataFrame,
    prev_weights: Optional[pd.Series] = None,
    cfg: Optional[OptimizationConfig] = None,
    cov_method: str = "ledoit_wolf",
) -> pd.Series:
    """Convenience: alpha -> mean-variance weights using a covariance estimate."""

    cfg = cfg or OptimizationConfig()

    # Build covariance
    if cov_method == "ledoit_wolf":
        from portfolio.risk import ledoit_wolf_cov

        cov = ledoit_wolf_cov(returns)
    elif cov_method == "sample":
        from portfolio.risk import sample_cov

        cov = sample_cov(returns)
    else:
        raise ValueError(f"Unknown cov_method: {cov_method}")

    mu = alpha.reindex(returns.columns).fillna(0.0)
    return mean_variance_optimize(expected_returns=mu, cov=cov, prev_weights=prev_weights, cfg=cfg)

