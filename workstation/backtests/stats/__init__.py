"""Statistical tests and anti-overfitting tools for backtesting."""

from backtests.stats.bootstrap import block_bootstrap
from backtests.stats.cross_validation import (
    cpcv_split,
    purged_kfold_split,
    walk_forward_split,
)
from backtests.stats.decay_analysis import (
    correlation_with_existing,
    regime_conditional_sharpe,
    rolling_sharpe,
    sharpe_decay_rate,
    strategy_capacity_estimate,
    strategy_half_life,
)
from backtests.stats.minimum_backtest import minimum_backtest_length
from backtests.stats.multiple_testing import (
    bonferroni_correction,
    fdr_correction,
    whites_reality_check,
)
from backtests.stats.sharpe_tests import (
    deflated_sharpe_ratio,
    probabilistic_sharpe_ratio,
    sharpe_confidence_interval,
)

__all__ = [
    "probabilistic_sharpe_ratio",
    "deflated_sharpe_ratio",
    "sharpe_confidence_interval",
    "bonferroni_correction",
    "fdr_correction",
    "whites_reality_check",
    "cpcv_split",
    "purged_kfold_split",
    "walk_forward_split",
    "block_bootstrap",
    "minimum_backtest_length",
    # Decay analysis
    "rolling_sharpe",
    "strategy_half_life",
    "correlation_with_existing",
    "regime_conditional_sharpe",
    "strategy_capacity_estimate",
    "sharpe_decay_rate",
]
