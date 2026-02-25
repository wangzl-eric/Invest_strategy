"""Research helpers: data loading, signal evaluation, and plotting for notebooks."""

from __future__ import annotations

from typing import List, Optional, Union

import pandas as pd
import numpy as np

from backend.market_data_store import market_data_store
from backtests.vectorized import run_vectorized_backtest, VectorizedBacktestConfig
from backtests.core import BacktestResult, CostModel, SlippageModel, VectorStrategy


def load_prices(
    asset_class: str,
    tickers: List[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Load price data from Parquet data lake, pivoted for signal computation.

    Returns a DataFrame with DatetimeIndex, ticker columns, and close values.
    Ready for use in signal computation (e.g. prices.pct_change(...)).

    Args:
        asset_class: One of "equities", "fx", "commodities", "rates_yf"
        tickers: List of ticker symbols
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)

    Returns:
        DataFrame with date index, ticker columns, close values.
        Empty DataFrame if no data.
    """
    df = market_data_store.query(
        asset_class=asset_class,
        tickers=tickers,
        start_date=start,
        end_date=end,
    )
    if df.empty or "close" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    pivoted = df.pivot(index="date", columns="ticker", values="close")
    pivoted.index = pd.DatetimeIndex(pivoted.index)
    return pivoted.sort_index()


def load_fred(
    category: str,
    series_ids: List[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Load FRED data from Parquet data lake, pivoted for analysis.

    Returns a DataFrame with DatetimeIndex, series_id columns, and values.

    Args:
        category: One of "treasury_yields", "macro_indicators", "fed_liquidity"
        series_ids: List of FRED series IDs
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)

    Returns:
        DataFrame with date index, series_id columns, values.
        Empty DataFrame if no data.
    """
    df = market_data_store.query(
        asset_class=category,
        tickers=series_ids,
        start_date=start,
        end_date=end,
    )
    if df.empty or "value" not in df.columns:
        return pd.DataFrame()

    id_col = "series_id" if "series_id" in df.columns else "ticker"
    df["date"] = pd.to_datetime(df["date"])
    pivoted = df.pivot(index="date", columns=id_col, values="value")
    pivoted.index = pd.DatetimeIndex(pivoted.index)
    return pivoted.sort_index()


class _SignalStrategy(VectorStrategy):
    """Adapter to run vectorized backtest from pre-computed position series."""

    def __init__(self, positions: pd.Series, name: str = "signal"):
        self._positions = positions
        self.name = name

    def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
        common = self._positions.index.intersection(bars.index)
        out = pd.Series(0.0, index=bars.index)
        out.loc[common] = self._positions.loc[common].values
        return out.reindex(bars.index).fillna(0.0)


def evaluate_signal(
    signal_series: pd.Series,
    price_series: pd.Series,
    cost_bps: float = 10.0,
    slippage_bps: float = 0.0,
) -> BacktestResult:
    """Run vectorized backtest on a pre-computed signal (position series).

    Args:
        signal_series: Target position series (e.g. -1..1 or 0/1), indexed by date
        price_series: Close price series, indexed by date
        cost_bps: Round-trip cost in basis points per unit turnover (default 10)
        slippage_bps: Slippage in bps per unit turnover (default 0)

    Returns:
        BacktestResult with equity, returns, positions, turnover, stats
    """
    # Align indices
    common_idx = signal_series.index.intersection(price_series.index)
    if len(common_idx) < 2:
        return BacktestResult(
            equity=pd.Series(dtype=float),
            returns=pd.Series(dtype=float),
            positions=pd.Series(dtype=float),
            turnover=pd.Series(dtype=float),
            stats={"total_return": 0.0, "sharpe": 0.0, "max_drawdown": 0.0},
            metadata={},
        )

    signal_aligned = signal_series.reindex(common_idx).fillna(0.0).sort_index()
    price_aligned = price_series.reindex(common_idx).ffill().bfill().sort_index()

    bars = pd.DataFrame({"close": price_aligned}, index=price_aligned.index)
    bars.index.name = "timestamp"

    cost_tps = cost_bps / 10000.0
    cfg = VectorizedBacktestConfig(
        cost_model=CostModel(cost_tps=cost_tps),
        slippage_model=SlippageModel(slippage_bps=slippage_bps),
    )
    strategy = _SignalStrategy(signal_aligned, name="signal")
    return run_vectorized_backtest(bars=bars, strategy=strategy, cfg=cfg)


def plot_backtest(result: BacktestResult) -> "plotly.graph_objects.Figure":
    """Create a standardized Plotly chart: equity, drawdown, rolling Sharpe.

    Args:
        result: BacktestResult from evaluate_signal or run_vectorized_backtest

    Returns:
        Plotly Figure with 3 subplots
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        raise ImportError("plotly is required for plot_backtest. pip install plotly")

    from backtests.metrics import annualized_sharpe

    equity = result.equity.dropna()
    if equity.empty or len(equity) < 2:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Rolling drawdown
    peak = equity.cummax()
    drawdown = (equity / peak) - 1.0

    # Rolling 63-day Sharpe (approx 3 months)
    roll_window = min(63, len(result.returns) // 2) if len(result.returns) > 1 else 1
    roll_window = max(1, roll_window)
    rolling_sharpe = (
        result.returns.rolling(roll_window, min_periods=roll_window)
        .apply(lambda x: annualized_sharpe(pd.Series(x), periods_per_year=252), raw=False)
        .fillna(0.0)
    )

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("Equity", "Drawdown", "Rolling Sharpe (63d)"),
        row_heights=[0.5, 0.25, 0.25],
    )

    fig.add_trace(
        go.Scatter(x=equity.index, y=equity.values, name="Equity", line=dict(color="#1f77b4")),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=drawdown.index, y=drawdown.values, name="Drawdown", fill="tozeroy", line=dict(color="#d62728")),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=rolling_sharpe.index, y=rolling_sharpe.values, name="Rolling Sharpe", line=dict(color="#2ca02c")),
        row=3,
        col=1,
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        margin=dict(t=40, b=40),
        template="plotly_white",
    )
    fig.update_yaxes(title_text="", row=1, col=1)
    fig.update_yaxes(title_text="", row=2, col=1)
    fig.update_yaxes(title_text="", row=3, col=1)
    return fig
