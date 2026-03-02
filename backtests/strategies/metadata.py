"""Strategy metadata for PnL attribution.

Each strategy/signal gets context for LLM-powered explanations.
"""

from typing import Dict, Optional

# Metadata for PnL attribution - each signal/portfolio gets context for LLM explanations
SIGNAL_METADATA: Dict[str, dict] = {
    # Example: momentum_tech strategy
    "momentum_tech": {
        "thesis": "Capture tech sector momentum using 12-1 price return",
        "factors": ["momentum", "size", "growth"],
        "regime_preference": "risk_on",
        "description": "Long/short tech stocks with strongest 12M momentum, rebalancing monthly",
        "positions": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD"],
    },
    # Example: carry_g10 strategy
    "carry_g10": {
        "thesis": "Capture carry in G10 currencies via high-yield target",
        "factors": ["carry", "volatility"],
        "regime_preference": "low_vol",
        "description": "Long high-yield G10 FX (AUD, NZD, CAD), short low-yield (JPY, CHF, EUR)",
        "positions": ["EURUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"],
    },
    # Example: mean_reversion strategy
    "mean_reversion": {
        "thesis": "Mean revert short-term dislocations in SPX constituents",
        "factors": ["mean_reversion", "liquidity"],
        "regime_preference": "high_vol",
        "description": "Buy oversold, sell overbought based on 63-day z-score",
        "positions": ["SPY", "QQQ", "IWM"],
    },
    # Default portfolio-level
    "main_portfolio": {
        "thesis": "Diversified multi-strategy portfolio",
        "factors": ["momentum", "carry", "volatility", "value"],
        "regime_preference": "all",
        "description": "Combined portfolio across all strategies",
        "positions": [],  # Will be populated from actual holdings
    },
}


def get_signal_metadata(signal_name: str) -> Optional[dict]:
    """Get metadata for a signal/portfolio.

    Args:
        signal_name: Name of signal or portfolio

    Returns:
        Metadata dict with thesis, factors, etc., or None if not found
    """
    return SIGNAL_METADATA.get(signal_name)


__all__ = ["SIGNAL_METADATA", "get_signal_metadata"]
