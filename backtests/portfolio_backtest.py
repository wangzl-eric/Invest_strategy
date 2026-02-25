"""Portfolio-level backtester: blend signals, optimize weights, simulate daily rebalancing."""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd

from backtests.core import BacktestResult, CostModel
from backtests.metrics import annualized_sharpe, max_drawdown, total_return
from portfolio.blend import Signal, blend_signals
from portfolio.optimizer import weights_from_alpha


def _get_signal_scores(signal, prices: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    """Get cross-sectional signal scores as of a given date."""
    scores = signal.compute(prices.loc[:date])
    if isinstance(scores, pd.DataFrame):
        # Take latest row
        valid = scores.dropna(how="all")
        if valid.empty:
            return pd.Series(dtype=float)
        return valid.iloc[-1]
    return scores.reindex(prices.columns).fillna(0.0)


def run_portfolio_backtest(
    *,
    prices: pd.DataFrame,
    signals: List,
    signal_weights: Optional[List[float]] = None,
    cost_bps: float = 10.0,
    rebalance_freq: int = 1,
    min_history: int = 63,
) -> BacktestResult:
    """Run portfolio backtest: blend signals, optimize weights, simulate rebalancing.

    Args:
        prices: DataFrame with DatetimeIndex, ticker columns, close values
        signals: List of BaseSignal instances (e.g. MomentumSignal, MeanReversionSignal)
        signal_weights: Weights for each signal in blend (default: equal)
        cost_bps: Round-trip cost in bps per unit turnover
        rebalance_freq: Rebalance every N days (1 = daily)
        min_history: Minimum return history for covariance estimation

    Returns:
        BacktestResult with equity, returns, positions (gross), turnover, stats
    """
    if prices.empty or prices.shape[1] == 0:
        return BacktestResult(
            equity=pd.Series(dtype=float),
            returns=pd.Series(dtype=float),
            positions=pd.Series(dtype=float),
            turnover=pd.Series(dtype=float),
            stats={"total_return": 0.0, "sharpe": 0.0, "max_drawdown": 0.0},
            metadata={},
        )

    prices = prices.sort_index()
    returns = prices.pct_change().dropna(how="all")
    if returns.empty or len(returns) < min_history:
        return BacktestResult(
            equity=pd.Series(dtype=float),
            returns=pd.Series(dtype=float),
            positions=pd.Series(dtype=float),
            turnover=pd.Series(dtype=float),
            stats={"total_return": 0.0, "sharpe": 0.0, "max_drawdown": 0.0},
            metadata={},
        )

    n_sigs = len(signals)
    weights = signal_weights if signal_weights is not None else [1.0 / max(1, n_sigs)] * n_sigs
    cost_tps = cost_bps / 10000.0
    cost_model = CostModel(cost_tps=cost_tps)

    # Ensure min_history covers signal lookbacks
    lookbacks = [getattr(s, "lookback", 63) for s in signals]
    min_history = max(min_history, max(lookbacks, default=63))

    dates = returns.index
    prev_weights = None
    portfolio_rets = []
    turnover_series = []
    for i in range(min_history, len(dates) - 1):
        t = dates[i]
        t_next = dates[i + 1]
        hist_returns = returns.loc[:t]
        if len(hist_returns) < min_history:
            continue

        # Build blended alpha from signals at t
        blend_inputs = []
        for sig, w in zip(signals, weights):
            try:
                score = _get_signal_scores(sig, prices, t)
                if score is not None and not score.dropna().empty:
                    blend_inputs.append(Signal(name=sig.name, score=score, weight=w))
            except Exception:
                continue

        if not blend_inputs:
            continue

        alpha = blend_signals(blend_inputs, zscore_each=True)
        alpha = alpha.reindex(returns.columns).fillna(0.0)

        try:
            w = weights_from_alpha(
                alpha=alpha,
                returns=hist_returns,
                prev_weights=prev_weights,
                cov_method="ledoit_wolf",
            )
        except Exception:
            try:
                w = weights_from_alpha(
                    alpha=alpha,
                    returns=hist_returns,
                    prev_weights=prev_weights,
                    cov_method="sample",
                )
            except Exception:
                # Fallback: equal weight when optimization fails
                n = len(returns.columns)
                w = pd.Series(1.0 / n, index=returns.columns)

        # Gross return: w @ ret_{t+1} (weights at t earn return t->t+1)
        ret_next = returns.loc[t_next].reindex(w.index).fillna(0.0)
        gross = float((w * ret_next).sum())

        # Turnover
        if prev_weights is not None:
            turn = float((w - prev_weights.reindex(w.index).fillna(0.0)).abs().sum())
        else:
            turn = float(w.abs().sum())

        net = cost_model.apply(pd.Series([gross]), turnover=pd.Series([turn])).iloc[0]
        portfolio_rets.append((t_next, net))
        turnover_series.append((t_next, turn))
        prev_weights = w

    if not portfolio_rets:
        return BacktestResult(
            equity=pd.Series(dtype=float),
            returns=pd.Series(dtype=float),
            positions=pd.Series(dtype=float),
            turnover=pd.Series(dtype=float),
            stats={"total_return": 0.0, "sharpe": 0.0, "max_drawdown": 0.0},
            metadata={},
        )

    idx = pd.DatetimeIndex([x[0] for x in portfolio_rets])
    portfolio_rets = pd.Series([x[1] for x in portfolio_rets], index=idx)
    turnover_series = pd.Series([x[1] for x in turnover_series], index=idx)
    equity = (1.0 + portfolio_rets).cumprod()

    stats = {
        "total_return": total_return(equity),
        "sharpe": annualized_sharpe(portfolio_rets, periods_per_year=252),
        "max_drawdown": max_drawdown(equity),
        "avg_daily_return": float(portfolio_rets.mean()),
        "vol_daily": float(portfolio_rets.std()),
    }
    stats = {k: (0.0 if (np.isnan(v) or np.isinf(v)) else float(v)) for k, v in stats.items()}

    # Positions: use gross exposure as proxy (portfolio-level)
    gross_exp = pd.Series(1.0, index=idx)

    return BacktestResult(
        equity=equity,
        returns=portfolio_rets,
        positions=gross_exp,
        turnover=turnover_series,
        stats=stats,
        metadata={"strategy": "portfolio_blend", "signals": ",".join(s.name for s in signals)},
    )
