"""Automated portfolio rebalancing with risk controls."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Callable
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from portfolio.optimizer import OptimizationConfig, weights_from_alpha
from execution.runner import ExecutionRunner, RunnerConfig
from execution.risk import RiskEngine, RiskLimits
from execution.broker import Broker
from execution.types import OrderRequest

logger = logging.getLogger(__name__)


PriceGetter = Callable[[str], float]


@dataclass
class RebalanceConfig:
    """Configuration for automated rebalancing."""
    account_id: str
    mode: str = "paper"  # paper/live/sim
    rebalance_threshold: float = 0.02  # Rebalance if drift > 2%
    min_rebalance_interval_days: int = 1  # Minimum days between rebalances
    max_position_weight: float = 0.10
    min_position_weight: float = -0.10
    risk_aversion: float = 1.0
    cost_aware: bool = True
    dry_run: bool = True  # If True, only simulate, don't execute


class PortfolioRebalancer:
    """Automated portfolio rebalancer."""
    
    def __init__(
        self,
        *,
        broker: Broker,
        price_getter: PriceGetter,
        get_current_positions: Callable[[str], Dict[str, float]],
        get_net_liquidation: Callable[[str], float],
        risk_engine: Optional[RiskEngine] = None,
        config: Optional[RebalanceConfig] = None
    ):
        self.broker = broker
        self.price_getter = price_getter
        self.get_current_positions = get_current_positions
        self.get_net_liquidation = get_net_liquidation
        self.risk_engine = risk_engine or RiskEngine(RiskLimits())
        self.config = config or RebalanceConfig(account_id="")
        
        runner_config = RunnerConfig(
            mode=self.config.mode,
            account_id=self.config.account_id
        )
        self.execution_runner = ExecutionRunner(
            broker=broker,
            price_getter=price_getter,
            risk_engine=self.risk_engine,
            cfg=runner_config
        )
        
        self.last_rebalance_time: Optional[datetime] = None
    
    def calculate_target_weights(
        self,
        alpha: pd.Series,
        returns: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """Calculate target portfolio weights from alpha signals.
        
        Args:
            alpha: Alpha scores per asset
            returns: Optional returns DataFrame for covariance estimation
        
        Returns:
            Target weights as Series
        """
        opt_config = OptimizationConfig(
            risk_aversion=self.config.risk_aversion,
            max_weight=self.config.max_position_weight,
            min_weight=self.config.min_position_weight
        )
        
        if returns is not None:
            weights = weights_from_alpha(
                alpha=alpha,
                returns=returns,
                cfg=opt_config
            )
        else:
            # Simple normalization if no returns data
            # Normalize to sum to 1 and apply bounds
            weights = alpha.copy()
            weights = weights.fillna(0.0)
            
            # Apply bounds
            weights = weights.clip(
                lower=self.config.min_position_weight,
                upper=self.config.max_position_weight
            )
            
            # Normalize to sum to 1
            total = weights.sum()
            if total != 0:
                weights = weights / total
            else:
                weights = pd.Series(0.0, index=weights.index)
        
        return weights
    
    def calculate_current_weights(
        self,
        positions: Dict[str, float],
        prices: Dict[str, float],
        net_liquidation: float
    ) -> pd.Series:
        """Calculate current portfolio weights from positions.
        
        Args:
            positions: Dictionary of symbol -> quantity
            prices: Dictionary of symbol -> price
            net_liquidation: Net liquidation value (equity)
        
        Returns:
            Current weights as Series
        """
        if net_liquidation == 0:
            return pd.Series(dtype=float)
        
        weights = {}
        for symbol, quantity in positions.items():
            price = prices.get(symbol, 0.0)
            notional = quantity * price
            weight = notional / net_liquidation
            weights[symbol] = weight
        
        return pd.Series(weights)
    
    def calculate_rebalance_orders(
        self,
        target_weights: pd.Series,
        current_weights: pd.Series,
        net_liquidation: float,
        prices: Dict[str, float]
    ) -> list[OrderRequest]:
        """Calculate orders needed to rebalance portfolio.
        
        Args:
            target_weights: Target weights per asset
            current_weights: Current weights per asset
            net_liquidation: Net liquidation value
            prices: Current prices per asset
        
        Returns:
            List of OrderRequest objects
        """
        orders = []
        
        # Union of all symbols
        all_symbols = set(target_weights.index) | set(current_weights.index)
        
        for symbol in all_symbols:
            target_weight = target_weights.get(symbol, 0.0)
            current_weight = current_weights.get(symbol, 0.0)
            
            # Calculate target and current notional
            target_notional = target_weight * net_liquidation
            current_notional = current_weight * net_liquidation
            
            # Calculate target and current quantities
            price = prices.get(symbol, 0.0)
            if price == 0:
                logger.warning(f"Price not available for {symbol}, skipping")
                continue
            
            target_qty = target_notional / price
            current_qty = current_notional / price
            
            # Calculate trade quantity
            trade_qty = target_qty - current_qty
            
            # Apply threshold - don't trade if difference is too small
            if abs(trade_qty * price / net_liquidation) < self.config.rebalance_threshold:
                continue
            
            # Round to reasonable precision
            trade_qty = round(trade_qty, 2)
            
            if abs(trade_qty) < 0.01:  # Minimum trade size
                continue
            
            # Determine side
            side = "BUY" if trade_qty > 0 else "SELL"
            quantity = abs(trade_qty)
            
            order = OrderRequest(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type="MKT",
                sec_type="STK",
                currency="USD"
            )
            
            orders.append(order)
        
        return orders
    
    def should_rebalance(self) -> bool:
        """Check if enough time has passed since last rebalance."""
        if self.last_rebalance_time is None:
            return True
        
        min_interval = timedelta(days=self.config.min_rebalance_interval_days)
        time_since_rebalance = datetime.utcnow() - self.last_rebalance_time
        
        return time_since_rebalance >= min_interval
    
    def rebalance(
        self,
        target_weights: pd.Series,
        returns: Optional[pd.DataFrame] = None
    ) -> Dict[str, any]:
        """Execute portfolio rebalancing.
        
        Args:
            target_weights: Target weights per asset (or alpha scores)
            returns: Optional returns DataFrame for optimization
        
        Returns:
            Dictionary with rebalance results
        """
        if not self.should_rebalance():
            return {
                "status": "skipped",
                "reason": "Minimum interval not met",
                "last_rebalance": self.last_rebalance_time.isoformat() if self.last_rebalance_time else None
            }
        
        # Get current positions and prices
        positions = self.get_current_positions(self.config.account_id)
        net_liquidation = self.get_net_liquidation(self.config.account_id)
        
        # Get prices for all symbols
        all_symbols = set(target_weights.index) | set(positions.keys())
        prices = {}
        for symbol in all_symbols:
            try:
                prices[symbol] = self.price_getter(symbol)
            except Exception as e:
                logger.warning(f"Could not get price for {symbol}: {e}")
                continue
        
        # Calculate target weights if alpha was provided
        if returns is not None or len(target_weights) > 0:
            # Check if target_weights sum to ~1 (already weights) or need optimization
            if abs(target_weights.sum() - 1.0) < 0.1:
                # Already weights
                final_target_weights = target_weights
            else:
                # Alpha scores, need optimization
                final_target_weights = self.calculate_target_weights(target_weights, returns)
        else:
            return {
                "status": "error",
                "error": "No target weights or alpha provided"
            }
        
        # Calculate current weights
        current_weights = self.calculate_current_weights(positions, prices, net_liquidation)
        
        # Calculate rebalance orders
        orders = self.calculate_rebalance_orders(
            final_target_weights,
            current_weights,
            net_liquidation,
            prices
        )
        
        if not orders:
            return {
                "status": "skipped",
                "reason": "No rebalancing needed",
                "target_weights": final_target_weights.to_dict(),
                "current_weights": current_weights.to_dict()
            }
        
        # Execute orders (or simulate if dry_run)
        if self.config.dry_run:
            result = {
                "status": "simulated",
                "orders_count": len(orders),
                "orders": [
                    {
                        "symbol": o.symbol,
                        "side": o.side,
                        "quantity": o.quantity,
                        "order_type": o.order_type
                    }
                    for o in orders
                ],
                "target_weights": final_target_weights.to_dict(),
                "current_weights": current_weights.to_dict()
            }
        else:
            order_ids = self.execution_runner.submit_orders(orders)
            result = {
                "status": "executed",
                "orders_count": len(orders),
                "order_ids": order_ids,
                "target_weights": final_target_weights.to_dict(),
                "current_weights": current_weights.to_dict()
            }
        
        self.last_rebalance_time = datetime.utcnow()
        
        return result
