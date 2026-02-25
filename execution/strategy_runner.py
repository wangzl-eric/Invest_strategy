"""Strategy runner: evaluate signals, optimize weights, generate and submit paper orders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

import pandas as pd

from execution.audit import record_order, record_risk_event
from execution.broker import Broker
from execution.risk import RiskEngine, RiskLimits, RiskState
from execution.runner import ExecutionRunner, RunnerConfig
from execution.types import OrderRequest
from portfolio.blend import Signal, blend_signals
from portfolio.optimizer import weights_from_alpha


PriceGetter = Callable[[str], float]


@dataclass
class StrategyRunnerConfig:
    """Configuration for the strategy runner."""

    asset_class: str = "equities"
    tickers: List[str] = None
    signals: List = None
    signal_weights: Optional[List[float]] = None
    portfolio_value: float = 100_000.0
    account_id: str = ""
    lookback_days: int = 252

    def __post_init__(self):
        if self.tickers is None:
            self.tickers = []
        if self.signals is None:
            self.signals = []


def _load_prices(
    asset_class: str,
    tickers: List[str],
    lookback_days: int,
) -> pd.DataFrame:
    """Load prices from data lake or yfinance fallback."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    try:
        from backend.market_data_store import market_data_store

        df = market_data_store.query(
            asset_class=asset_class,
            tickers=tickers,
            start_date=start_str,
            end_date=end_str,
        )
    except Exception:
        df = pd.DataFrame()

    if df.empty or "close" not in df.columns:
        try:
            import yfinance as yf

            data = yf.download(tickers, start=start_str, end=end_str, progress=False, threads=True)
            if data.empty:
                return pd.DataFrame()
            if isinstance(data.columns, pd.MultiIndex):
                records = []
                for ticker in tickers:
                    if ticker in data["Close"].columns:
                        close = data["Close"][ticker]
                        for idx, val in close.items():
                            records.append({"date": idx.date().isoformat(), "ticker": ticker, "close": float(val)})
                df = pd.DataFrame(records)
            else:
                df = data.reset_index()
                df = df.rename(columns={"Date": "date", "Close": "close"})
                df["ticker"] = tickers[0] if len(tickers) == 1 else "UNKNOWN"
                df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        except Exception:
            return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    pivoted = df.pivot(index="date", columns="ticker", values="close")
    pivoted.index = pd.DatetimeIndex(pivoted.index)
    return pivoted.sort_index()


def _get_current_positions_from_db(account_id: str) -> Dict[str, float]:
    """Get current positions (symbol -> quantity) from database."""
    try:
        from backend.database import get_db_context
        from backend.models import Position
        from sqlalchemy import desc

        with get_db_context() as db:
            query = db.query(Position).filter(Position.account_id == account_id).order_by(desc(Position.timestamp))
            positions = query.all()
            latest = {}
            for p in positions:
                if p.symbol not in latest or p.timestamp > latest[p.symbol].timestamp:
                    latest[p.symbol] = p
            return {p.symbol: float(p.quantity) for p in latest.values()}
    except Exception:
        return {}


def _compute_target_weights(
    prices: pd.DataFrame,
    signals: List,
    signal_weights: Optional[List[float]],
) -> Optional[pd.Series]:
    """Compute target portfolio weights from signals."""
    if not signals or prices.empty:
        return None

    n = len(signals)
    weights = signal_weights if signal_weights else [1.0 / n] * n
    blend_inputs = []

    for sig, w in zip(signals, weights):
        try:
            scores = sig.compute(prices)
            if isinstance(scores, pd.DataFrame):
                row = scores.dropna(how="all").iloc[-1] if not scores.empty else pd.Series(dtype=float)
            else:
                row = scores.reindex(prices.columns).fillna(0.0)
            if not row.dropna().empty:
                blend_inputs.append(Signal(name=sig.name, score=row, weight=w))
        except Exception:
            continue

    if not blend_inputs:
        return None

    alpha = blend_signals(blend_inputs, zscore_each=True)
    alpha = alpha.reindex(prices.columns).fillna(0.0)
    returns = prices.pct_change().dropna(how="all")

    if len(returns) < 63:
        return None

    try:
        w = weights_from_alpha(alpha=alpha, returns=returns, cov_method="ledoit_wolf")
    except Exception:
        try:
            w = weights_from_alpha(alpha=alpha, returns=returns, cov_method="sample")
        except Exception:
            n = len(prices.columns)
            w = pd.Series(1.0 / n, index=prices.columns)
    return w


def run_strategy(
    *,
    broker: Broker,
    price_getter: PriceGetter,
    config: StrategyRunnerConfig,
    risk_engine: Optional[RiskEngine] = None,
) -> List[OrderRequest]:
    """Evaluate signals, compute target weights, generate orders. Does NOT submit.

    Returns the list of OrderRequest that would be submitted.
    Caller can inspect/modify before passing to ExecutionRunner.submit_orders().
    """
    if not config.tickers or not config.signals:
        return []

    prices = _load_prices(config.asset_class, config.tickers, config.lookback_days)
    if prices.empty or len(prices) < 63:
        record_risk_event(
            severity="WARNING",
            event_type="STRATEGY_NO_DATA",
            message="Insufficient price data for strategy",
            context={"tickers": config.tickers},
        )
        return []

    target_weights = _compute_target_weights(prices, config.signals, config.signal_weights)
    if target_weights is None:
        return []

    current_positions = _get_current_positions_from_db(config.account_id) if config.account_id else {}
    portfolio_value = config.portfolio_value

    orders: List[OrderRequest] = []
    for symbol in target_weights.index:
        weight = float(target_weights.get(symbol, 0.0))
        if abs(weight) < 1e-6:
            weight = 0.0

        price = price_getter(symbol)
        if price is None or price <= 0:
            continue

        target_dollar = weight * portfolio_value
        target_qty = target_dollar / price
        current_qty = current_positions.get(symbol, 0.0)
        delta_qty = target_qty - current_qty

        if abs(delta_qty) < 0.01:
            continue

        side = "BUY" if delta_qty > 0 else "SELL"
        orders.append(
            OrderRequest(
                symbol=symbol,
                side=side,
                quantity=abs(round(delta_qty, 2)),
            )
        )

    return orders


def run_and_submit(
    *,
    broker: Broker,
    price_getter: PriceGetter,
    config: StrategyRunnerConfig,
    risk_engine: Optional[RiskEngine] = None,
    runner_cfg: Optional[RunnerConfig] = None,
) -> List[int]:
    """Run strategy, generate orders, and submit via ExecutionRunner with risk checks.

    Returns list of order row IDs that were submitted to the broker.
    """
    orders = run_strategy(broker=broker, price_getter=price_getter, config=config, risk_engine=risk_engine)
    if not orders:
        return []

    runner = ExecutionRunner(
        broker=broker,
        price_getter=price_getter,
        risk_engine=risk_engine or RiskEngine(RiskLimits()),
        cfg=runner_cfg or RunnerConfig(mode="paper", account_id=config.account_id),
    )
    return runner.submit_orders(orders)
