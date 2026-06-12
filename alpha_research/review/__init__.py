"""One-call review pipeline: manifest -> rigor battery -> run artifacts -> pool.

The mandatory path from a strategy to the pool (EXECUTION_PLAN.md WP-1.4):

    python -m alpha_research.review run alpha_research/research/pool/<id>/manifest.yaml

Steps: manifest validation -> data QC preflight -> weights-contract backtest
-> walk-forward segments -> stats battery (PSR/DSR/MinBTL/bootstrap CI,
regime-conditional Sharpe) -> cost sensitivity (1x/2x/3x) -> parameter
sensitivity (+/-20%, +/-40%) -> correlation vs active pool -> gate evaluation
against the manifest's pre-committed promotion rules -> artifact bundle under
a reproducible run_id -> pool registration.
"""

from alpha_research.review.engine import (  # noqa: F401
    BacktestResult,
    run_weights_backtest,
)
from alpha_research.review.pipeline import run_review  # noqa: F401

__all__ = ["run_review", "run_weights_backtest", "BacktestResult"]
