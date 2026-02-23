"""Vectorized backtesting on bar data (fast iteration for alpha research)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from backtests.core import BacktestResult, CostModel, SlippageModel, VectorStrategy, ensure_datetime_index
from backtests.metrics import annualized_sharpe, max_drawdown, total_return


@dataclass(frozen=True)
class VectorizedBacktestConfig:
    # Execution convention: positions decided at t and applied to return t->t+1
    shift_positions_by: int = 1
    periods_per_year: int = 252

    cost_model: CostModel = CostModel(cost_tps=0.0)
    slippage_model: SlippageModel = SlippageModel(slippage_bps=0.0)


def _simple_turnover(pos: pd.Series) -> pd.Series:
    p = pos.fillna(0.0)
    return p.diff().abs().fillna(0.0)


def run_vectorized_backtest(
    *,
    bars: pd.DataFrame,
    strategy: VectorStrategy,
    cfg: Optional[VectorizedBacktestConfig] = None,
    price_col: str = "close",
) -> BacktestResult:
    cfg = cfg or VectorizedBacktestConfig()
    b = ensure_datetime_index(bars)

    if price_col not in b.columns:
        raise ValueError(f"bars missing '{price_col}' column")

    price = b[price_col].astype(float)
    raw_pos = strategy.generate_positions(b).astype(float)
    raw_pos = raw_pos.reindex(price.index).fillna(0.0)

    # Apply execution delay
    pos = raw_pos.shift(cfg.shift_positions_by).fillna(0.0)
    turn = _simple_turnover(pos)

    # Gross returns (simple close-to-close)
    rets = price.pct_change().fillna(0.0)
    gross = pos * rets

    net = cfg.cost_model.apply(gross, turnover=turn)
    net = cfg.slippage_model.apply(net, turnover=turn)

    equity = (1.0 + net).cumprod()

    stats = {
        "total_return": total_return(equity),
        "sharpe": annualized_sharpe(net, periods_per_year=cfg.periods_per_year),
        "max_drawdown": max_drawdown(equity),
        "avg_daily_return": float(net.mean()),
        "vol_daily": float(net.std()),
    }
    # Defensive NaN cleanup
    stats = {k: (0.0 if (np.isnan(v) or np.isinf(v)) else float(v)) for k, v in stats.items()}

    return BacktestResult(
        equity=equity,
        returns=net,
        positions=pos,
        turnover=turn,
        stats=stats,
        metadata={"strategy": strategy.name, "price_col": price_col},
    )

