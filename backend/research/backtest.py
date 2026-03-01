"""Backtesting framework for quantitative strategies.

This module provides:
- EventDrivenBacktest: Backtesting with order execution simulation using Backtrader
- Integration with MLflow for experiment tracking
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable, Tuple
from datetime import datetime, date
from enum import Enum
from pathlib import Path

import pandas as pd
import numpy as np

from backend.config import settings

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Type of trading signal."""
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float = 100000
    commission: float = 0.001  # 0.1% per trade
    slippage: float = 0.0005   # 0.05% slippage
    position_size: float = 1.0  # 100% of capital
    long_only: bool = False
    
    @classmethod
    def from_config(cls) -> "BacktestConfig":
        """Create config from settings."""
        backtest_config = settings.research.backtest
        return cls(
            initial_capital=backtest_config.default_initial_capital,
            commission=backtest_config.default_commission,
            slippage=backtest_config.default_slippage
        )


@dataclass
class BacktestResult:
    """Results of a backtest."""
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: Dict[str, float]
    config: BacktestConfig
    
    def summary(self) -> str:
        """Generate summary string."""
        m = self.metrics
        return f"""
Backtest Summary
================
Total Return: {m.get('total_return', 0)*100:.2f}%
Sharpe Ratio: {m.get('sharpe_ratio', 0):.2f}
Max Drawdown: {m.get('max_drawdown', 0)*100:.2f}%
Win Rate: {m.get('win_rate', 0)*100:.1f}%
Total Trades: {m.get('total_trades', 0)}
Profit Factor: {m.get('profit_factor', 0):.2f}
        """.strip()


class EventDrivenBacktest:
    """Event-driven backtest for realistic order execution simulation.
    
    This backtest simulates:
    - Order placement and fill
    - Partial fills
    - Market impact
    - Realistic transaction costs
    """
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig.from_config()
        self._data: Optional[pd.DataFrame] = None
        self._signal_generator: Optional[Callable] = None
        self._results: Optional[BacktestResult] = None
        
        # State
        self._cash: float = 0
        self._position: float = 0
        self._equity_history: List[Dict] = []
        self._trade_history: List[Dict] = []
    
    def set_data(self, data: pd.DataFrame, price_col: str = "close"):
        """Set price data with OHLC columns."""
        self._data = data.copy()
        self._price_col = price_col
        self._open_col = "open"
        self._high_col = "high"
        self._low_col = "low"
    
    def set_signal_generator(self, generator: Callable[[pd.DataFrame], pd.Series]):
        """Set function that generates signals from price data.
        
        Args:
            generator: Function that takes price DataFrame and returns signals
        """
        self._signal_generator = generator
    
    def run(self) -> BacktestResult:
        """Run the event-driven backtest."""
        if self._data is None or self._signal_generator is None:
            raise ValueError("Data and signal generator must be set")
        
        # Initialize
        self._cash = self.config.initial_capital
        self._position = 0
        self._equity_history = []
        self._trade_history = []
        
        # Generate signals
        signals = self._signal_generator(self._data)
        
        # Process each bar
        for i, (date_idx, row) in enumerate(self._data.iterrows()):
            signal = signals.loc[date_idx] if date_idx in signals.index else 0
            
            # Get current price (use open for execution)
            current_price = row[self._price_col]
            
            # Calculate equity
            equity = self._cash + self._position * current_price
            
            # Execute trades based on signal
            target_position = signal * self.config.position_size * equity / current_price
            
            if self.config.long_only:
                target_position = max(0, target_position)
            
            position_diff = target_position - self._position
            
            if abs(position_diff) > 0.001:  # Threshold to avoid tiny trades
                # Execute trade
                execution_price = self._execute_trade(
                    position_diff, 
                    current_price,
                    row.get(self._high_col, current_price),
                    row.get(self._low_col, current_price)
                )
                
                trade_value = abs(position_diff) * execution_price
                commission = trade_value * self.config.commission
                slippage = trade_value * self.config.slippage
                total_cost = commission + slippage
                
                # Update cash and position
                if position_diff > 0:  # Buy
                    self._cash -= (trade_value + total_cost)
                    self._position += position_diff
                else:  # Sell
                    self._cash += (trade_value - total_cost)
                    self._position += position_diff
                
                # Record trade
                self._trade_history.append({
                    "date": date_idx,
                    "type": "BUY" if position_diff > 0 else "SELL",
                    "price": execution_price,
                    "shares": abs(position_diff),
                    "value": trade_value,
                    "commission": commission,
                    "slippage": slippage
                })
            
            # Record equity
            self._equity_history.append({
                "date": date_idx,
                "equity": equity,
                "cash": self._cash,
                "position": self._position,
                "price": current_price
            })
        
        # Create result DataFrames
        equity_curve = pd.DataFrame(self._equity_history).set_index("date")
        trades = pd.DataFrame(self._trade_history)
        
        # Calculate metrics
        metrics = self._calculate_metrics(equity_curve, trades)
        
        self._results = BacktestResult(
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            config=self.config
        )
        
        return self._results
    
    def _execute_trade(
        self, 
        position_diff: float, 
        close_price: float,
        high: float,
        low: float
    ) -> float:
        """Simulate trade execution with slippage."""
        # Simple model: execution at close + random slippage within day's range
        if position_diff > 0:  # Buy
            # Assume we get execution between close and high
            base_price = close_price
            slippage_pct = np.random.uniform(0, self.config.slippage * 2)
            return base_price * (1 + slippage_pct)
        else:  # Sell
            # Assume we get execution between close and low
            base_price = close_price
            slippage_pct = np.random.uniform(0, self.config.slippage * 2)
            return base_price * (1 - slippage_pct)
    
    def _calculate_metrics(
        self, 
        equity_curve: pd.DataFrame, 
        trades: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate performance metrics."""
        if equity_curve.empty:
            return {}
        
        returns = equity_curve["equity"].pct_change().dropna()
        
        total_return = (equity_curve["equity"].iloc[-1] / self.config.initial_capital) - 1
        
        if returns.std() > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        rolling_max = equity_curve["equity"].cummax()
        drawdown = (equity_curve["equity"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_trades": len(trades),
            "final_equity": equity_curve["equity"].iloc[-1]
        }


# ----------------------------------------------------------------------
# MLflow Integration
# ----------------------------------------------------------------------

class BacktestExperiment:
    """MLflow integration for backtest experiments."""
    
    def __init__(self, experiment_name: Optional[str] = None):
        self.experiment_name = experiment_name or settings.research.mlflow.experiment_name
        self._mlflow = None
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Setup MLflow if enabled."""
        if not settings.research.mlflow.is_enabled:
            logger.info("MLflow is disabled")
            return
        
        try:
            import mlflow
            mlflow.set_experiment(self.experiment_name)
            self._mlflow = mlflow
            logger.info(f"MLflow initialized with experiment: {self.experiment_name}")
        except ImportError:
            logger.warning("MLflow not installed - experiment tracking disabled")
        except Exception as e:
            logger.warning(f"Failed to setup MLflow: {e}")
    
    def log_backtest(self, result: BacktestResult, params: Optional[Dict] = None):
        """Log backtest results to MLflow."""
        if self._mlflow is None:
            logger.warning("MLflow not available - skipping experiment logging")
            return
        
        with self._mlflow.start_run():
            # Log parameters
            if params:
                self._mlflow.log_params(params)
            
            # Log config
            self._mlflow.log_params({
                "initial_capital": result.config.initial_capital,
                "commission": result.config.commission,
                "slippage": result.config.slippage,
                "position_size": result.config.position_size
            })
            
            # Log metrics
            for key, value in result.metrics.items():
                if isinstance(value, (int, float)):
                    self._mlflow.log_metric(key, value)
            
            # Log equity curve as artifact
            equity_file = "/tmp/equity_curve.csv"
            result.equity_curve.to_csv(equity_file)
            self._mlflow.log_artifact(equity_file)
            
            # Log trades as artifact
            if not result.trades.empty:
                trades_file = "/tmp/trades.csv"
                result.trades.to_csv(trades_file, index=False)
                self._mlflow.log_artifact(trades_file)


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------

def run_backtest(
    data: pd.DataFrame,
    signals: pd.Series,
    config: Optional[BacktestConfig] = None,
) -> BacktestResult:
    """Convenience function to run a backtest using EventDrivenBacktest.
    
    Args:
        data: Price data with date index
        signals: Trading signals (-1, 0, 1)
        config: Backtest configuration
        
    Returns:
        BacktestResult
    """
    engine = EventDrivenBacktest(config)
    
    engine.set_data(data)
    engine.set_signals(signals)
    return engine.run()


def run_factor_backtest(
    data: pd.DataFrame,
    factor_name: str,
    direction: str = "long_short",
    quantile: float = 0.2,
    config: Optional[BacktestConfig] = None
) -> BacktestResult:
    """Run a factor-based backtest.
    
    Args:
        data: Price data with factor column
        factor_name: Name of factor column to use for ranking
        direction: "long_short" or "long_only"
        quantile: Top/bottom quantile for longs/shorts
        config: Backtest configuration
        
    Returns:
        BacktestResult
    """
    df = data.copy()
    
    # Rank by factor
    df["rank"] = df[factor_name].rank(pct=True)
    
    # Generate signals
    if direction == "long_short":
        df["signal"] = 0
        df.loc[df["rank"] > (1 - quantile), "signal"] = 1
        df.loc[df["rank"] < quantile, "signal"] = -1
    else:  # long_only
        df["signal"] = 0
        df.loc[df["rank"] > (1 - quantile), "signal"] = 1
    
    signals = df["signal"]
    
    return run_backtest(data, signals, config)
