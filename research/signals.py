"""Signal registry: versioned, reusable signal components for research and deployment."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd


class BaseSignal(ABC):
    """Standard interface for signals in the registry.

    Each signal has: name, parameters, compute logic, and data dependencies.
    compute() returns signal scores (date x ticker) for use in blending and backtesting.
    """

    name: str = ""
    lookback: int = 252

    @abstractmethod
    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """Compute signal from price data.

        Args:
            prices: DataFrame with DatetimeIndex, ticker columns, close values.

        Returns:
            For single-asset (one column): pd.Series indexed by date.
            For multi-asset: pd.DataFrame with same index as prices, ticker columns.
        """
        ...

    def to_positions(self, signal: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
        """Convert raw signal scores to positions (-1..1 or 0/1).

        Default: sign of signal, clipped to [-1, 1].
        Override for custom position mapping.
        """
        if isinstance(signal, pd.Series):
            return np.sign(signal).clip(-1, 1).fillna(0.0)
        return signal.apply(lambda s: np.sign(s).clip(-1, 1).fillna(0.0))


class MomentumSignal(BaseSignal):
    """Momentum: return over lookback period, skipping recent skip days."""

    name = "momentum_12_1"
    lookback = 252
    skip = 21

    def __init__(self, lookback: Optional[int] = None, skip: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback
        if skip is not None:
            self.skip = skip
        self.name = f"momentum_{self.lookback}_{self.skip}"

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        ret = prices.pct_change(self.lookback - self.skip).shift(self.skip)
        return ret.iloc[:, 0] if ret.shape[1] == 1 else ret


class CarrySignal(BaseSignal):
    """Carry proxy: for rates/futures, (forward - spot) / spot.
    For equities without forward data: uses rolling return as carry proxy.
    """

    name = "carry_proxy"
    lookback = 21

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        # Simple carry proxy: expected forward return (rolling mean of past returns)
        rets = prices.pct_change()
        carry = rets.rolling(self.lookback, min_periods=1).mean()
        return carry.iloc[:, 0] if carry.shape[1] == 1 else carry


class MeanReversionSignal(BaseSignal):
    """Mean reversion: negative z-score of price vs moving average.
    When price > MA, signal is negative (expect reversion down).
    """

    name = "mean_reversion"
    lookback = 63

    def __init__(self, lookback: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        ma = prices.rolling(self.lookback, min_periods=self.lookback // 2).mean()
        z = (prices - ma) / prices.rolling(self.lookback, min_periods=self.lookback // 2).std()
        z = z.replace([np.inf, -np.inf], np.nan)
        # Negative so that high price -> short signal
        signal = -z
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_SIGNAL_REGISTRY: Dict[str, BaseSignal] = {}


def register(signal: BaseSignal) -> None:
    """Add a signal to the registry."""
    _SIGNAL_REGISTRY[signal.name] = signal


def get_signal(name: str) -> Optional[BaseSignal]:
    """Retrieve a signal by name."""
    return _SIGNAL_REGISTRY.get(name)


def list_signals() -> List[str]:
    """List all registered signal names."""
    return list(_SIGNAL_REGISTRY.keys())


# Register default signals
def _init_defaults():
    register(MomentumSignal())
    register(MomentumSignal(lookback=126, skip=21))
    register(CarrySignal())
    register(MeanReversionSignal())


_init_defaults()
