"""
Portfolio Builder: Connect Signals → Optimization → Execution
=============================================================
A unified pipeline for multi-asset quantitative strategy development.

Usage:
    from portfolio.builder import PortfolioBuilder
    
    builder = PortfolioBuilder()
    builder.set_universe(['SPY', 'TLT', 'GLD', 'UUP'])
    builder.set_signals(['momentum_60_21', 'mean_reversion'])
    builder.set_optimization('risk_parity')
    
    result = builder.run()
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class PortfolioConfig:
    """Configuration for portfolio construction."""
    
    # Universe
    universe: List[str] = field(default_factory=lambda: ['SPY', 'TLT', 'GLD'])
    
    # Signals to use
    signals: List[str] = field(default_factory=lambda: ['momentum_60_21'])
    
    # Optimization method
    optimization: str = 'mean_variance'  # mean_variance, risk_parity, black_litterman, equal_weight
    
    # Risk parameters
    risk_aversion: float = 1.0
    max_weight: float = 0.30
    min_weight: float = -0.10
    target_gross: float = 1.0
    
    # Rebalancing
    rebalance_frequency: str = 'monthly'  # daily, weekly, monthly
    turnover_penalty: float = 0.0
    
    # Backtest params
    initial_cash: float = 100000
    commission: float = 0.001


class PortfolioBuilder:
    """
    Unified portfolio construction pipeline.
    
    Flow:
    1. Load data for universe
    2. Compute signals for each asset
    3. Generate alpha (signal scores)
    4. Optimize weights
    5. Backtest and analyze
    """
    
    def __init__(self, config: Optional[PortfolioConfig] = None):
        self.config = config or PortfolioConfig()
        self.data: Dict[str, pd.DataFrame] = {}
        self.signals: Dict[str, pd.DataFrame] = {}
        self.weights: Optional[pd.Series] = None
        self.backtest_result: Optional[Dict] = None
        
    def load_data(
        self,
        data_loader: Callable[[str, str, str], pd.DataFrame],
        start_date: str,
        end_date: str,
    ) -> 'PortfolioBuilder':
        """
        Load price data for universe.
        
        Args:
            data_loader: Function(ticker, start, end) -> DataFrame
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        print(f"Loading data for {self.config.universe}...")
        
        close_prices = {}
        for ticker in self.config.universe:
            try:
                df = data_loader(ticker, start_date, end_date)
                if df is not None and len(df) > 0:
                    close_prices[ticker] = df['close']
                    self.data[ticker] = df
            except Exception as e:
                print(f"  Failed to load {ticker}: {e}")
        
        self.prices = pd.DataFrame(close_prices)
        print(f"  Loaded {len(self.prices)} days of data")
        
        return self
    
    def compute_signals(
        self,
        signal_config: Optional[Dict[str, Dict]] = None,
    ) -> 'PortfolioBuilder':
        """
        Compute signals for each asset.
        
        Args:
            signal_config: Dict of signal_name -> params
        """
        from research.signals import get_signal
        
        signal_config = signal_config or {}
        
        print(f"Computing signals: {self.config.signals}")
        
        for signal_name in self.config.signals:
            signal = get_signal(signal_name)
            if signal is None:
                print(f"  Signal {signal_name} not found, skipping")
                continue
            
            # Get params if any
            params = signal_config.get(signal_name, {})
            
            # Compute signal on price data
            sig = signal.compute(self.prices)
            self.signals[signal_name] = sig
            
        return self
    
    def generate_alpha(
        self,
        method: str = 'mean',
    ) -> pd.Series:
        """
        Generate alpha scores from signals.
        
        Methods:
        - mean: Simple average of all signals
        - weighted: Weighted average
        - best: Use best performing signal
        """
        if not self.signals:
            raise ValueError("No signals computed. Call compute_signals() first.")
        
        if method == 'mean':
            # Align signals
            aligned = []
            for sig_df in self.signals.values():
                if isinstance(sig_df, pd.DataFrame):
                    aligned.append(sig_df.mean(axis=1))
                else:
                    aligned.append(sig_df)
            
            alpha = pd.concat(aligned, axis=1).mean(axis=1)
            
        elif method == 'best':
            # Use most recent signal value
            alphas = []
            for sig_df in self.signals.values():
                if isinstance(sig_df, pd.DataFrame):
                    alphas.append(sig_df.iloc[-1])
                else:
                    alphas.append(sig_df.iloc[-1])
            alpha = pd.concat(alphas)
            
        else:
            raise ValueError(f"Unknown alpha method: {method}")
        
        # Normalize to weights
        self.alpha = alpha.dropna()
        return self.alpha
    
    def optimize_weights(
        self,
        method: Optional[str] = None,
    ) -> pd.Series:
        """
        Optimize portfolio weights.
        
        Methods:
        - mean_variance: Markowitz mean-variance
        - risk_parity: Equal risk contribution
        - equal_weight: 1/N allocation
        - black_litterman: Bayesian prior
        """
        from portfolio.optimizer import mean_variance_optimize, OptimizationConfig
        from portfolio.risk import sample_cov, ledoit_wolf_cov
        
        method = method or self.config.optimization
        
        # Get returns for covariance estimation
        returns = self.prices.pct_change().dropna()
        
        # Generate alpha if not exists
        if not hasattr(self, 'alpha'):
            self.generate_alpha()
        
        # Convert alpha to expected returns
        # Normalize alpha to annualized expected returns
        alpha_norm = (self.alpha - self.alpha.mean()) / self.alpha.std()
        expected_returns = alpha_norm * returns.std() * np.sqrt(252)  # Annualize
        
        # Handle missing assets
        common_assets = expected_returns.dropna().index.intersection(returns.columns)
        expected_returns = expected_returns[common_assets]
        
        if method == 'equal_weight':
            weights = pd.Series(1.0 / len(common_assets), index=common_assets)
            
        elif method == 'mean_variance':
            cfg = OptimizationConfig(
                risk_aversion=self.config.risk_aversion,
                turnover_aversion=self.config.turnover_penalty,
                max_weight=self.config.max_weight,
                min_weight=self.config.min_weight,
                target_gross=self.config.target_gross,
            )
            cov = ledoit_wolf_cov(returns[common_assets])
            weights = mean_variance_optimize(
                expected_returns=expected_returns,
                cov=cov,
                cfg=cfg,
            )
            
        elif method == 'risk_parity':
            weights = self._risk_parity_weights(returns[common_assets])
            
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        self.weights = weights.fillna(0)
        return self.weights
    
    def _risk_parity_weights(self, returns: pd.DataFrame) -> pd.Series:
        """Compute risk parity weights."""
        cov = returns.cov()
        vol = np.sqrt(np.diag(cov))
        
        # Inverse vol weights (simplified risk parity)
        inv_vol = 1 / vol
        weights = inv_vol / inv_vol.sum()
        
        return pd.Series(weights, index=returns.columns)
    
    def backtest(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Backtest the portfolio.
        """
        from backend.backtest_engine import BacktestEngine, IBKRDataFeed
        
        if self.weights is None:
            self.optimize_weights()
        
        # Determine backtest period
        if start_date is None:
            start_date = self.prices.index[100]  # Skip warmup
        if end_date is None:
            end_date = self.prices.index[-1]
        
        # For multi-asset, run individual strategy backtests
        results = {}
        
        for ticker in self.weights.index:
            if ticker not in self.data:
                continue
                
            df = self.data[ticker].copy()
            df = df.loc[start_date:end_date]
            
            if len(df) < 50:
                continue
            
            # Simple signal strategy
            engine = BacktestEngine(
                cash=self.config.initial_cash * self.weights[ticker],
                commission=self.config.commission,
            )
            
            df = df.reset_index(drop=True)
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            data_feed = IBKRDataFeed(dataname=df)
            engine.add_data(data_feed, name=ticker)
            
            # Use momentum strategy
            class SimpleMomentum(bt.Strategy):
                params = (('period', 50),)
                def __init__(self):
                    self.sma = bt.ind.SMA(self.data.close, period=self.params.period)
                def next(self):
                    if len(self) < self.params.period:
                        return
                    if self.data.close[-1] > self.sma[-1]:
                        if not self.position:
                            self.buy()
                    else:
                        if self.position:
                            self.sell()
            
            import backtrader as bt
            SimpleMomentum.__name__ = f'Momentum_{ticker}'
            
            engine.add_strategy(SimpleMomentum)
            
            try:
                result = engine.run_backtest()
                results[ticker] = result
            except Exception as e:
                print(f"  Backtest failed for {ticker}: {e}")
        
        self.backtest_result = results
        return results
    
    def get_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate portfolio-level metrics."""
        if not self.backtest_result:
            return {}
        
        # Combine equity curves
        equity_curves = []
        for ticker, result in self.backtest_result.items():
            eq = result.get('equity_curve')
            if eq is not None and len(eq) > 0:
                weight = self.weights.get(ticker, 0)
                eq['weighted_value'] = eq['portfolio_value'] * weight
                equity_curves.append(eq[['date', 'weighted_value']])
        
        if not equity_curves:
            return {}
        
        # Merge and sum
        portfolio = equity_curves[0]
        for eq in equity_curves[1:]:
            portfolio = portfolio.merge(eq, on='date', how='outer')
        
        portfolio = portfolio.sort_values('date')
        portfolio['total_value'] = portfolio[[c for c in portfolio.columns if c.endswith('_y') or c == 'weighted_value']].sum(axis=1)
        
        # Calculate metrics
        returns = portfolio['total_value'].pct_change().dropna()
        
        total_return = (1 + returns).prod() - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_dd = drawdown.min()
        
        return {
            'total_return': total_return,
            'annualized_return': (1 + total_return) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
        }
    
    def summary(self) -> pd.DataFrame:
        """Print portfolio summary."""
        print("\n" + "="*60)
        print("PORTFOLIO SUMMARY")
        print("="*60)
        
        print(f"\nUniverse: {self.config.universe}")
        print(f"Signals: {self.config.signals}")
        print(f"Optimization: {self.config.optimization}")
        
        print("\n--- Weights ---")
        if self.weights is not None:
            print(self.weights.sort_values(ascending=False).to_string())
        
        print("\n--- Performance ---")
        metrics = self.get_portfolio_metrics()
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"  {k}: {v*100:.2f}%" if 'return' in k or 'drawdown' in k else f"  {k}: {v:.2f}")
        
        print("="*60 + "\n")
        
        return self.weights


# ============================================================================
# Multi-Asset Strategy Examples
# ============================================================================

class MultiAssetStrategy:
    """
    Example multi-asset strategies that use the portfolio builder.
    """
    
    @staticmethod
    def trend_following(universe: List[str], start: str, end: str) -> PortfolioBuilder:
        """Trend-following strategy using momentum signals."""
        
        builder = PortfolioBuilder(PortfolioConfig(
            universe=universe,
            signals=['momentum_60_21'],
            optimization='mean_variance',
            risk_aversion=2.0,
        ))
        
        import yfinance as yf
        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)
        
        builder.load_data(loader, start, end)
        builder.compute_signals()
        builder.optimize_weights()
        
        return builder
    
    @staticmethod
    def risk_parity_strategy(universe: List[str], start: str, end: str) -> PortfolioBuilder:
        """Risk parity strategy."""
        
        builder = PortfolioBuilder(PortfolioConfig(
            universe=universe,
            signals=[],  # No signals, pure risk parity
            optimization='risk_parity',
        ))
        
        import yfinance as yf
        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)
        
        builder.load_data(loader, start, end)
        builder.optimize_weights()
        
        return builder
    
    @staticmethod
    def blended_strategy(universe: List[str], start: str, end: str) -> PortfolioBuilder:
        """Blended momentum + risk parity strategy."""
        
        builder = PortfolioBuilder(PortfolioConfig(
            universe=universe,
            signals=['momentum_60_21', 'mean_reversion'],
            optimization='mean_variance',
            risk_aversion=1.5,
            max_weight=0.25,
        ))
        
        import yfinance as yf
        def loader(ticker, start, end):
            return yf.download(ticker, start=start, end=end, progress=False)
        
        builder.load_data(loader, start, end)
        builder.compute_signals()
        builder.generate_alpha(method='mean')
        builder.optimize_weights()
        
        return builder


__all__ = [
    'PortfolioBuilder',
    'PortfolioConfig',
    'MultiAssetStrategy',
]
