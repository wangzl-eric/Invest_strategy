"""Signal registry: Backtrader-native signal components.

This module provides signals that work with Backtrader's event-driven framework.
Two usage modes:
1. Research mode: compute_signal_pandas() - pure pandas, no Backtrader
2. Backtest mode: use SignalStrategy class - native Backtrader integration
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union, Type

import numpy as np
import pandas as pd


class BaseSignal:
    """Standard interface for signals in the registry.

    Each signal has: name, parameters, compute logic, and data dependencies.
    compute() returns signal scores (date x ticker) for use in blending and backtesting.
    """

    name: str = ""
    lookback: int = 252

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """Compute signal from price data.

        Args:
            prices: DataFrame with DatetimeIndex, ticker columns, close values.

        Returns:
            For single-asset (one column): pd.Series indexed by date.
            For multi-asset: pd.DataFrame with same index as prices, ticker columns.
        """
        raise NotImplementedError("Subclasses must implement compute()")

    def to_positions(
        self, signal: Union[pd.Series, pd.DataFrame]
    ) -> Union[pd.Series, pd.DataFrame]:
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
        z = (prices - ma) / prices.rolling(
            self.lookback, min_periods=self.lookback // 2
        ).std()
        z = z.replace([np.inf, -np.inf], np.nan)
        # Negative so that high price -> short signal
        signal = -z
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal


class VolatilitySignal(BaseSignal):
    """Volatility signal: historical volatility over lookback.
    Lower vol = higher expected return (contrarian).
    """

    name = "volatility"
    lookback = 21

    def __init__(self, lookback: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        returns = prices.pct_change()
        vol = returns.rolling(self.lookback, min_periods=self.lookback // 2).std()
        # Invert: low vol = high signal (expect vol to expand)
        signal = -vol
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal

    def to_positions(
        self, signal: Union[pd.Series, pd.DataFrame]
    ) -> Union[pd.Series, pd.DataFrame]:
        """Inverse vol: buy when vol is low, sell when high."""
        if isinstance(signal, pd.Series):
            return (-np.sign(signal)).clip(-1, 1).fillna(0.0)
        return signal.apply(lambda s: (-np.sign(s)).clip(-1, 1).fillna(0.0))


class ATRSignal(BaseSignal):
    """Average True Range signal: normalized by price.
    High ATR = high volatility.
    """

    name = "atr"
    lookback = 14

    def __init__(self, lookback: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        # Need OHLC data - if only close, use close-based approximation
        returns = prices.pct_change().abs()
        atr = returns.rolling(self.lookback, min_periods=self.lookback // 2).mean()
        # Normalize by price
        atr_norm = atr / prices
        signal = -atr_norm  # Low ATR = buy
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal

    def to_positions(
        self, signal: Union[pd.Series, pd.DataFrame]
    ) -> Union[pd.Series, pd.DataFrame]:
        """Buy low volatility."""
        if isinstance(signal, pd.Series):
            return (-np.sign(signal)).clip(-1, 1).fillna(0.0)
        return signal.apply(lambda s: (-np.sign(s)).clip(-1, 1).fillna(0.0))


class RSISignal(BaseSignal):
    """Relative Strength Index: momentum oscillator [0, 100].
    RSI > 70 = overbought (sell), RSI < 30 = oversold (buy).
    """

    name = "rsi"
    lookback = 14

    def __init__(self, lookback: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback
        self.name = f"rsi_{self.lookback}"

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        delta = prices.diff()
        gain = (
            (delta.where(delta > 0, 0))
            .rolling(window=self.lookback, min_periods=self.lookback // 2)
            .mean()
        )
        loss = (
            (-delta.where(delta < 0, 0))
            .rolling(window=self.lookback, min_periods=self.lookback // 2)
            .mean()
        )

        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.replace([np.inf, -np.inf], np.nan)

        # Center around 50: high RSI = negative signal (sell), low RSI = positive (buy)
        signal = 50 - rsi
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal


class MACDSignal(BaseSignal):
    """MACD Signal: (EMA12 - EMA26) / EMA9.
    Positive = bullish momentum.
    """

    name = "macd"
    lookback = 26

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_line = signal
        self.name = f"macd_{fast}_{slow}_{signal}"

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        ema_fast = prices.ewm(span=self.fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_line, adjust=False).mean()
        histogram = macd_line - signal_line
        return histogram.iloc[:, 0] if histogram.shape[1] == 1 else histogram


class BollingerPositionSignal(BaseSignal):
    """Bollinger Band position: (close - lower) / (upper - lower).
    Values < 0 = below lower band, > 1 = above upper band.
    Mean reversion: sell when > 1, buy when < 0.
    """

    name = "bollinger_position"
    lookback = 20
    num_std = 2

    def __init__(self, lookback: Optional[int] = None, num_std: Optional[float] = None):
        if lookback is not None:
            self.lookback = lookback
        if num_std is not None:
            self.num_std = num_std

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        sma = prices.rolling(self.lookback, min_periods=self.lookback // 2).mean()
        std = prices.rolling(self.lookback, min_periods=self.lookback // 2).std()

        upper = sma + self.num_std * std
        lower = sma - self.num_std * std

        position = (prices - lower) / (upper - lower).replace(0, np.nan)
        position = position.replace([np.inf, -np.inf], np.nan)

        # Mean reversion: high position = sell signal
        signal = 0.5 - position
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal


class SMACrossoverSignal(BaseSignal):
    """SMA Crossover: fast SMA - slow SMA, normalized.
    Positive = bullish (fast above slow).
    """

    name = "sma_crossover"
    fast_period = 50
    slow_period = 200

    def __init__(self, fast: Optional[int] = None, slow: Optional[int] = None):
        if fast is not None:
            self.fast_period = fast
        if slow is not None:
            self.slow_period = slow
        self.name = f"sma_cross_{self.fast_period}_{self.slow_period}"

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        fast_sma = prices.rolling(
            self.fast_period, min_periods=self.fast_period // 2
        ).mean()
        slow_sma = prices.rolling(
            self.slow_period, min_periods=self.slow_period // 2
        ).mean()

        # Normalize by price
        signal = (fast_sma - slow_sma) / prices
        return signal.iloc[:, 0] if signal.shape[1] == 1 else signal


class VolumeSignal(BaseSignal):
    """Volume trend: volume relative to moving average.
    High volume = institutional interest.
    """

    name = "volume"
    lookback = 20

    def __init__(self, lookback: Optional[int] = None):
        if lookback is not None:
            self.lookback = lookback

    def compute(self, prices: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        # This requires volume data - if not available, return zeros
        # In practice, you'd pass volume as a separate DataFrame
        # For now, return neutral signal
        return pd.Series(0, index=prices.index)


# ---------------------------------------------------------------------------
# Signal Blending
# ---------------------------------------------------------------------------


class SignalBlender:
    """Blend multiple signals with weights."""

    def __init__(
        self, signals: List[BaseSignal], weights: Optional[List[float]] = None
    ):
        self.signals = signals
        self.weights = weights or [1.0 / len(signals)] * len(signals)

        if len(self.weights) != len(self.signals):
            raise ValueError("Number of weights must match number of signals")

    def compute(self, prices: pd.DataFrame) -> pd.Series:
        """Compute blended signal."""
        blended = None

        for signal, weight in zip(self.signals, self.weights):
            sig = signal.compute(prices)

            # Normalize to z-scores for fair blending
            sig_norm = (sig - sig.mean()) / sig.std() if sig.std() > 0 else sig

            if blended is None:
                blended = sig_norm * weight
            else:
                blended += sig_norm * weight

        return blended.fillna(0.0)


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
    # Original signals
    register(MomentumSignal())
    register(MomentumSignal(lookback=126, skip=21))
    register(CarrySignal())
    register(MeanReversionSignal())

    # New volatility/trend signals
    register(VolatilitySignal())
    register(VolatilitySignal(lookback=60))
    register(ATRSignal())
    register(RSISignal())
    register(RSISignal(lookback=7))  # Fast RSI
    register(MACDSignal())
    register(BollingerPositionSignal())
    register(BollingerPositionSignal(lookback=10, num_std=1.5))  # Tight bands
    register(SMACrossoverSignal(fast=50, slow=200))
    register(SMACrossoverSignal(fast=20, slow=50))


_init_defaults()


# ============================================================================
# Backtrader Integration - Create Strategy from Signal
# ============================================================================

def create_signal_strategy(
    signal_class: Type[BaseSignal],
    signal_params: Optional[Dict] = None,
    threshold: float = 0.0,
) -> type:
    """
    Create a Backtrader Strategy class from a signal class.
    
    This provides native Backtrader compatibility while using our signal system.
    
    Args:
        signal_class: Signal class (e.g., MomentumSignal)
        signal_params: Parameters for the signal
        threshold: Signal threshold for entry/exit
        
    Returns:
        Backtrader Strategy class
        
    Example:
        from backtests.strategies import create_signal_strategy, MomentumSignal
        
        StrategyClass = create_signal_strategy(MomentumSignal, {'lookback': 60, 'skip': 21})
        cerebro.addstrategy(StrategyClass)
    """
    import backtrader as bt
    
    signal_params = signal_params or {}
    
    class SignalStrategy(bt.Strategy):
        params = (
            ('threshold', threshold),
        )
        
        def __init__(self):
            # Create signal instance
            self.signal = signal_class(**signal_params)
            self.order = None
            # Store price history for signal computation
            self._price_history = []
            
        def notify_order(self, order):
            if order.status in [order.Completed]:
                self.order = None
                
        def next(self):
            if self.order:
                return
                
            # Get current close
            close = self.data.close[0]
            self._price_history.append(close)
            
            # Keep only lookback period
            lookback = getattr(self.signal, 'lookback', 60)
            if len(self._price_history) > lookback + 20:
                self._price_history.pop(0)
                
            # Need enough data
            if len(self._price_history) < lookback:
                return
                
            # Compute signal using pandas
            prices_df = pd.DataFrame({'close': self._price_history})
            sig_values = self.signal.compute(prices_df)
            
            # Get latest signal value
            if isinstance(sig_values, pd.Series):
                sig = sig_values.iloc[-1]
            else:
                sig = sig_values
                
            # Convert to position
            position = np.sign(sig) if not pd.isna(sig) else 0
            
            # Execute based on signal
            if position > self.params.threshold:
                if not self.position:
                    self.order = self.buy()
            elif position < -self.params.threshold:
                if self.position:
                    self.order = self.sell()
            elif position == 0:
                if self.position:
                    self.order = self.close()
    
    # Set strategy name
    SignalStrategy.__name__ = f"Signal_{signal_class.__name__}"
    return SignalStrategy


def create_blended_strategy(
    signal_classes: List[Type[BaseSignal]],
    signal_params: Optional[List[Dict]] = None,
    weights: Optional[List[float]] = None,
    threshold: float = 0.0,
) -> type:
    """
    Create a Backtrader Strategy class from multiple blended signals.
    
    Args:
        signal_classes: List of signal classes
        signal_params: List of parameter dicts for each signal
        weights: Weights for blending
        threshold: Signal threshold for entry/exit
        
    Returns:
        Backtrader Strategy class
    """
    import backtrader as bt
    
    signal_params = signal_params or [{}] * len(signal_classes)
    weights = weights or [1.0 / len(signal_classes)] * len(signal_classes)
    
    class BlendedSignalStrategy(bt.Strategy):
        params = (
            ('threshold', threshold),
        )
        
        def __init__(self):
            # Create signal instances
            self.signals = [
                sig_class(**params) 
                for sig_class, params in zip(signal_classes, signal_params)
            ]
            self.weights = weights
            self.order = None
            self._price_history = []
            
        def notify_order(self, order):
            if order.status in [order.Completed]:
                self.order = None
                
        def next(self):
            if self.order:
                return
                
            # Get current close
            close = self.data.close[0]
            self._price_history.append(close)
            
            # Keep only lookback period
            lookback = max(getattr(s, 'lookback', 60) for s in self.signals)
            if len(self._price_history) > lookback + 20:
                self._price_history.pop(0)
                
            if len(self._price_history) < lookback:
                return
                
            # Compute blended signal
            blended = 0
            prices_df = pd.DataFrame({'close': self._price_history})
            
            for sig, weight in zip(self.signals, self.weights):
                sig_values = sig.compute(prices_df)
                if isinstance(sig_values, pd.Series):
                    sig_val = sig_values.iloc[-1]
                else:
                    sig_val = sig_values
                    
                # Normalize
                if not pd.isna(sig_val):
                    blended += sig_val * weight
                    
            # Convert to position
            position = np.sign(blended) if not pd.isna(blended) else 0
            
            # Execute
            if position > self.params.threshold:
                if not self.position:
                    self.order = self.buy()
            elif position < -self.params.threshold:
                if self.position:
                    self.order = self.sell()
            elif position == 0:
                if self.position:
                    self.order = self.close()
    
    BlendedSignalStrategy.__name__ = "BlendedSignalStrategy"
    return BlendedSignalStrategy


# ============================================================================
# Signal Research Utilities
# ============================================================================


def run_signal_research(
    prices: pd.DataFrame,
    signal_names: List[str] = None,
    metric: str = "sharpe",
) -> pd.DataFrame:
    """
    Run research on multiple signals.

    Args:
        prices: Price data (DataFrame with 'close' column)
        signal_names: List of signal names to test (None = all)
        metric: Metric to optimize ('sharpe', 'return', 'calmar')

    Returns:
        DataFrame with signal research results
    """
    if signal_names is None:
        signal_names = list_signals()

    results = []

    for sig_name in signal_names:
        signal = get_signal(sig_name)
        if signal is None:
            continue

        # Compute signal
        sig = signal.compute(prices[["close"]])
        positions = signal.to_positions(sig)

        # Simple return calculation
        returns = prices["close"].pct_change()
        signal_returns = positions.shift(1) * returns

        # Remove NaN
        valid = ~(positions.isna() | returns.isna())
        signal_returns = signal_returns[valid]

        if len(signal_returns) == 0:
            continue

        # Calculate metrics
        total_return = (1 + signal_returns).prod() - 1
        volatility = signal_returns.std() * np.sqrt(252)
        sharpe = (signal_returns.mean() * 252) / volatility if volatility > 0 else 0

        # Drawdown
        cumulative = (1 + signal_returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_dd = drawdown.min()

        # Win rate
        wins = (signal_returns > 0).sum()
        total = len(signal_returns)
        win_rate = wins / total if total > 0 else 0

        results.append(
            {
                "signal": sig_name,
                "total_return": total_return,
                "sharpe": sharpe,
                "max_drawdown": max_dd,
                "win_rate": win_rate,
                "n_trades": total,
            }
        )

    return pd.DataFrame(results)


__all__ = [
    "BaseSignal",
    "MomentumSignal",
    "CarrySignal",
    "MeanReversionSignal",
    "VolatilitySignal",
    "ATRSignal",
    "RSISignal",
    "MACDSignal",
    "BollingerPositionSignal",
    "SMACrossoverSignal",
    "VolumeSignal",
    "SignalBlender",
    "register",
    "get_signal",
    "list_signals",
    "run_signal_research",
    "create_signal_strategy",
    "create_blended_strategy",
]
