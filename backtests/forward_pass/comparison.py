"""Comparison view: Side-by-side forward-pass vs post-trade attribution.

This module provides a unified view comparing:
1. Forward-pass: What the strategy predicted/saw at decision time
2. Post-trade: What actually happened (with hindsight)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class TradeComparison:
    """Single trade comparison: prediction vs actual."""
    
    # Trade ID
    trade_id: str
    
    # Timing
    entry_date: datetime
    exit_date: Optional[datetime]
    
    # Actual (outcome) - required fields first
    actual_direction: int  # 1, -1, 0
    actual_return: Optional[float]
    actual_pnl: Optional[float]
    
    # Forward-pass (prediction) - optional fields after
    predicted_direction: int = 0  # Default to 0 (flat)
    predicted_return: Optional[float] = None
    signal_confidence: Optional[float] = None
    entry_signals: Dict[str, float] = field(default_factory=dict)
    
    # Attribution (post-trade factors)
    factor_attribution: Dict[str, float] = field(default_factory=dict)
    sector_attribution: Dict[str, float] = field(default_factory=dict)
    news_sentiment: Optional[str] = None
    llm_explanation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
            "exit_date": self.exit_date.isoformat() if self.exit_date else None,
            # Forward-pass
            "predicted_direction": self.predicted_direction,
            "predicted_return": self.predicted_return,
            "signal_confidence": self.signal_confidence,
            "entry_signals": self.entry_signals,
            # Actual
            "actual_direction": self.actual_direction,
            "actual_return": self.actual_return,
            "actual_pnl": self.actual_pnl,
            # Attribution
            "factor_attribution": self.factor_attribution,
            "sector_attribution": self.sector_attribution,
            "news_sentiment": self.news_sentiment,
            "llm_explanation": self.llm_explanation,
            # Computed
            "prediction_correct": (
                np.sign(self.predicted_return or 0) == np.sign(self.actual_return or 0)
                if self.predicted_return and self.actual_return else None
            ),
            "prediction_error": (
                (self.actual_return or 0) - (self.predicted_return or 0)
                if self.predicted_return and self.actual_return else None
            ),
        }


class ComparisonView:
    """
    Unified view comparing forward-pass predictions vs post-trade attribution.
    
    Usage:
        comparison = ComparisonView(forward_tracker, attribution_results)
        df = comparison.to_dataframe()
        summary = comparison.get_summary()
    """
    
    def __init__(
        self,
        forward_pass_tracker: Any = None,
        attribution_results: Optional[pd.DataFrame] = None,
    ):
        """
        Args:
            forward_pass_tracker: ForwardPassTracker with trade predictions
            attribution_results: DataFrame with post-trade attribution
        """
        self.forward_tracker = forward_pass_tracker
        self.attribution = attribution_results
        self.comparisons: List[TradeComparison] = []
        
        if forward_pass_tracker and attribution_results is not None:
            self._build_comparisons()
    
    def _build_comparisons(self) -> None:
        """Build comparison records from trackers."""
        if self.forward_tracker is None:
            return
        
        # Get completed trades
        trades = self.forward_tracker.get_completed_trades()
        
        for trade in trades:
            # Find matching attribution
            attr = None
            if self.attribution is not None and not self.attribution.empty:
                # Match by date/ticker
                matches = self.attribution[
                    (self.attribution.get("ticker") == trade.ticker) |
                    (self.attribution.get("date") == trade.timestamp)
                ]
                if not matches.empty:
                    attr = matches.iloc[0]
            
            comp = TradeComparison(
                trade_id=trade.trade_id,
                entry_date=trade.timestamp,
                exit_date=None,  # Would be set from attribution
                predicted_direction=trade.direction,
                predicted_return=trade.predicted_return,
                signal_confidence=trade.signal_confidence,
                entry_signals=trade.entry_signals,
                actual_direction=trade.direction,  # Would be from actual
                actual_return=trade.get_actual_return(),
                actual_pnl=trade.get_pnl(),
            )
            
            # Add attribution if available
            if attr is not None:
                comp.factor_attribution = attr.get("factor_contribution", {})
                comp.sector_attribution = attr.get("sector_contribution", {})
                comp.news_sentiment = attr.get("news_sentiment")
                comp.llm_explanation = attr.get("llm_explanation")
            
            self.comparisons.append(comp)
    
    def add_comparison(self, comparison: TradeComparison) -> None:
        """Add a manual comparison record."""
        self.comparisons.append(comparison)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Export all comparisons to DataFrame."""
        if not self.comparisons:
            return pd.DataFrame()
        
        data = [c.to_dict() for c in self.comparisons]
        return pd.DataFrame(data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics comparing predictions vs actual."""
        if not self.comparisons:
            return {"error": "No comparisons available"}
        
        # Filter to completed trades with predictions
        valid = [
            c for c in self.comparisons 
            if c.predicted_return is not None and c.actual_return is not None
        ]
        
        if not valid:
            return {"error": "No valid predictions to compare"}
        
        # Direction accuracy
        correct_direction = sum(
            1 for c in valid if np.sign(c.predicted_return or 0) == np.sign(c.actual_return or 0)
        )
        direction_accuracy = correct_direction / len(valid)
        
        # Return prediction error
        errors = [(c.actual_return or 0) - (c.predicted_return or 0) for c in valid]
        
        # High confidence analysis
        high_conf = [c for c in valid if c.signal_confidence and c.signal_confidence > 0.7]
        low_conf = [c for c in valid if c.signal_confidence and c.signal_confidence <= 0.3]
        
        high_conf_acc = None
        low_conf_acc = None
        
        if high_conf:
            high_conf_acc = sum(
                1 for c in high_conf 
                if np.sign(c.predicted_return or 0) == np.sign(c.actual_return or 0)
            ) / len(high_conf)
        
        if low_conf:
            low_conf_acc = sum(
                1 for c in low_conf 
                if np.sign(c.predicted_return or 0) == np.sign(c.actual_return or 0)
            ) / len(low_conf)
        
        # Attribution analysis
        factor_impact = {}
        for c in valid:
            for factor, contrib in c.factor_attribution.items():
                if factor not in factor_impact:
                    factor_impact[factor] = []
                factor_impact[factor].append(contrib)
        
        factor_summary = {
            f: np.mean(v) for f, v in factor_impact.items()
        }
        
        # News sentiment accuracy
        sentiment_correct = sum(
            1 for c in valid 
            if c.news_sentiment and c.actual_return and (
                (c.news_sentiment == "positive" and c.actual_return > 0) or
                (c.news_sentiment == "negative" and c.actual_return < 0)
            )
        )
        sentiment_accuracy = sentiment_correct / len(valid) if valid else None
        
        return {
            "total_trades": len(valid),
            "direction_accuracy": direction_accuracy,
            "high_confidence_accuracy": high_conf_acc,
            "low_confidence_accuracy": low_conf_acc,
            "mean_predicted_return": np.mean([c.predicted_return for c in valid]),
            "mean_actual_return": np.mean([c.actual_return for c in valid]),
            "prediction_bias": np.mean(errors),
            "mae": np.mean(np.abs(errors)),
            "rmse": np.sqrt(np.mean(np.array(errors) ** 2)),
            "factor_impact": factor_summary,
            "news_sentiment_accuracy": sentiment_accuracy,
            # Win/loss breakdown
            "predicted_wins": sum(1 for c in valid if c.predicted_return and c.predicted_return > 0),
            "actual_wins": sum(1 for c in valid if c.actual_return and c.actual_return > 0),
            "predicted_losses": sum(1 for c in valid if c.predicted_return and c.predicted_return < 0),
            "actual_losses": sum(1 for c in valid if c.actual_return and c.actual_return < 0),
        }
    
    def get_prediction_quality_by_signal(self) -> pd.DataFrame:
        """Analyze prediction quality by individual signal."""
        if not self.comparisons:
            return pd.DataFrame()
        
        # Collect by signal
        signal_stats = {}
        
        for c in self.comparisons:
            for signal_name, signal_value in c.entry_signals.items():
                if signal_name not in signal_stats:
                    signal_stats[signal_name] = {
                        "count": 0,
                        "correct_direction": 0,
                        "total_error": [],
                    }
                
                stats = signal_stats[signal_name]
                stats["count"] += 1
                
                if c.actual_return is not None:
                    pred_sign = np.sign(signal_value)
                    actual_sign = np.sign(c.actual_return)
                    
                    if pred_sign == actual_sign:
                        stats["correct_direction"] += 1
                    
                    if c.predicted_return is not None:
                        stats["total_error"].append(c.actual_return - c.predicted_return)
        
        # Build DataFrame
        data = []
        for signal, stats in signal_stats.items():
            errors = stats["total_error"]
            data.append({
                "signal": signal,
                "count": stats["count"],
                "direction_accuracy": stats["correct_direction"] / stats["count"],
                "mean_error": np.mean(errors) if errors else None,
                "mae": np.mean(np.abs(errors)) if errors else None,
                "rmse": np.sqrt(np.mean(np.array(errors) ** 2)) if errors else None,
            })
        
        return pd.DataFrame(data).sort_values("direction_accuracy", ascending=False)
    
    def get_confusion_matrix(self) -> pd.DataFrame:
        """
        Build confusion matrix: predicted vs actual direction.
        
        Returns:
            DataFrame with predicted (rows) vs actual (columns)
        """
        if not self.comparisons:
            return pd.DataFrame()
        
        # Categories: Long (>0), Short (<0), Flat (0)
        predicted = []
        actual = []
        
        for c in self.comparisons:
            if c.predicted_return is None or c.actual_return is None:
                continue
            
            pred_cat = "long" if c.predicted_return > 0 else "short" if c.predicted_return < 0 else "flat"
            actual_cat = "long" if c.actual_return > 0 else "short" if c.actual_return < 0 else "flat"
            
            predicted.append(pred_cat)
            actual.append(actual_cat)
        
        # Build matrix
        matrix = pd.crosstab(
            pd.Series(predicted, name="predicted"),
            pd.Series(actual, name="actual"),
            margins=True
        )
        
        return matrix
    
    def get_llm_explanations(self) -> List[Dict[str, str]]:
        """Get all LLM-generated explanations."""
        return [
            {
                "trade_id": c.trade_id,
                "explanation": c.llm_explanation,
                "predicted": c.predicted_return,
                "actual": c.actual_return,
                "sentiment": c.news_sentiment,
            }
            for c in self.comparisons
            if c.llm_explanation
        ]


def create_comparison_view(
    forward_pass_path: str = None,
    attribution_path: str = None,
) -> ComparisonView:
    """
    Create comparison view from saved files.
    
    Args:
        forward_pass_path: Path to forward pass JSON
        attribution_path: Path to attribution CSV
        
    Returns:
        ComparisonView instance
    """
    from backtests.forward_pass.trade_tracker import ForwardPassTracker
    
    tracker = None
    attribution = None
    
    if forward_pass_path:
        # Load forward pass tracker
        import json
        with open(forward_pass_path) as f:
            data = json.load(f)
        
        # Would need to reconstruct tracker from saved data
        # For now, return empty
        pass
    
    if attribution_path:
        attribution = pd.read_csv(attribution_path)
    
    return ComparisonView(tracker, attribution)


__all__ = [
    "TradeComparison",
    "ComparisonView",
    "create_comparison_view",
]
