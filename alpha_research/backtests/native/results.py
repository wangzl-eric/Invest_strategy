"""Result container for a native backtest run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import pandas as pd

from .objects import Trade


@dataclass
class BacktestResult:
    """Everything a native backtest produces, in analysis-ready form.

    Mirrors the field names of ``alpha_research.review.engine.BacktestResult``
    (``daily_returns`` / ``equity_curve`` / ``weights`` / ``metrics``) so the
    native engine is a drop-in for reporting code, plus the richer per-bar
    state an event-driven engine can expose (positions, trades, turnover).
    """

    daily_returns: pd.Series
    equity_curve: pd.DataFrame  # columns: date, portfolio_value
    weights: pd.DataFrame  # effective per-bar portfolio weights
    positions: pd.DataFrame  # per-bar share quantities
    turnover: pd.Series
    trades: List[Trade] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    analyzers: Dict[str, Any] = field(default_factory=dict)

    @property
    def trades_frame(self) -> pd.DataFrame:
        """Trade blotter as a DataFrame (empty frame when no trades)."""
        if not self.trades:
            return pd.DataFrame(
                columns=["dt", "symbol", "quantity", "price", "commission", "slippage"]
            )
        return pd.DataFrame(
            [
                {
                    "dt": t.dt,
                    "symbol": t.symbol,
                    "quantity": t.quantity,
                    "price": t.price,
                    "commission": t.commission,
                    "slippage": t.slippage,
                }
                for t in self.trades
            ]
        )

    def summary(self) -> str:
        """One-line-per-metric human summary."""
        lines = ["Native backtest summary", "=" * 40]
        for key, val in self.metrics.items():
            if isinstance(val, float):
                if any(tok in key for tok in ("return", "drawdown", "volatility")):
                    lines.append(f"  {key:24s}: {val * 100:8.2f}%")
                else:
                    lines.append(f"  {key:24s}: {val:8.3f}")
            else:
                lines.append(f"  {key:24s}: {val}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "analyzers": self.analyzers,
            "n_trades": len(self.trades),
            "n_days": int(len(self.daily_returns)),
        }


__all__ = ["BacktestResult"]
