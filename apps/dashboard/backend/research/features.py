"""Feature registry for standardized signal definitions.

This module provides centralized feature definitions for quantitative research,
ensuring consistent signal calculations across backtests and production systems.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureCategory(str, Enum):
    """Feature category classification."""

    MOMENTUM = "momentum"
    VALUE = "value"
    VOLATILITY = "volatility"
    CARRY = "carry"
    QUALITY = "quality"
    GROWTH = "growth"
    MACRO = "macro"


@dataclass
class FeatureDefinition:
    """Definition of a quantitative feature."""

    name: str
    category: FeatureCategory
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_data: List[str] = field(default_factory=list)  # e.g., ["close", "volume"]

    def __repr__(self):
        return f"FeatureDefinition({self.name}, {self.category.value})"


class FeatureRegistry:
    """Registry for all quantitative features."""

    # Predefined feature definitions
    FEATURES: Dict[str, FeatureDefinition] = {
        # Momentum Features
        "momentum_20d": FeatureDefinition(
            name="momentum_20d",
            category=FeatureCategory.MOMENTUM,
            description="20-day price momentum (return)",
            parameters={"period": 20},
            required_data=["close"],
        ),
        "momentum_60d": FeatureDefinition(
            name="momentum_60d",
            category=FeatureCategory.MOMENTUM,
            description="60-day price momentum (return)",
            parameters={"period": 60},
            required_data=["close"],
        ),
        "momentum_120d": FeatureDefinition(
            name="momentum_120d",
            category=FeatureCategory.MOMENTUM,
            description="120-day price momentum (return)",
            parameters={"period": 120},
            required_data=["close"],
        ),
        "momentum_252d": FeatureDefinition(
            name="momentum_252d",
            category=FeatureCategory.MOMENTUM,
            description="252-day (1 year) price momentum",
            parameters={"period": 252},
            required_data=["close"],
        ),
        "momentum_12_1": FeatureDefinition(
            name="momentum_12_1",
            category=FeatureCategory.MOMENTUM,
            description="12-month minus 1-month momentum (Jagadeesh & Titman)",
            parameters={"period_long": 252, "period_short": 21},
            required_data=["close"],
        ),
        # Volatility Features
        "volatility_20d": FeatureDefinition(
            name="volatility_20d",
            category=FeatureCategory.VOLATILITY,
            description="20-day realized volatility (annualized)",
            parameters={"period": 20, "annualize": True},
            required_data=["close"],
        ),
        "volatility_60d": FeatureDefinition(
            name="volatility_60d",
            category=FeatureCategory.VOLATILITY,
            description="60-day realized volatility (annualized)",
            parameters={"period": 60, "annualize": True},
            required_data=["close"],
        ),
        "volatility_252d": FeatureDefinition(
            name="volatility_252d",
            category=FeatureCategory.VOLATILITY,
            description="252-day realized volatility (annualized)",
            parameters={"period": 252, "annualize": True},
            required_data=["close"],
        ),
        # Value Features
        "price_to_sma_50": FeatureDefinition(
            name="price_to_sma_50",
            category=FeatureCategory.VALUE,
            description="Price relative to 50-day simple moving average",
            parameters={"period": 50},
            required_data=["close"],
        ),
        "price_to_sma_200": FeatureDefinition(
            name="price_to_sma_200",
            category=FeatureCategory.VALUE,
            description="Price relative to 200-day simple moving average",
            parameters={"period": 200},
            required_data=["close"],
        ),
        # Carry Features (for FX, bonds, commodities)
        "carry_1y": FeatureDefinition(
            name="carry_1y",
            category=FeatureCategory.CARRY,
            description="1-year forward minus spot (carry)",
            parameters={"period": 252},
            required_data=["close", "forward"],
        ),
        # Quality Features
        "sharpe_ratio_60d": FeatureDefinition(
            name="sharpe_ratio_60d",
            category=FeatureCategory.QUALITY,
            description="60-day Sharpe ratio (annualized)",
            parameters={"period": 60, "risk_free": 0.0},
            required_data=["close"],
        ),
        "sortino_ratio_60d": FeatureDefinition(
            name="sortino_ratio_60d",
            category=FeatureCategory.QUALITY,
            description="60-day Sortino ratio (annualized, downside deviation)",
            parameters={"period": 60, "risk_free": 0.0},
            required_data=["close"],
        ),
        # Drawdown Features
        "max_drawdown_60d": FeatureDefinition(
            name="max_drawdown_60d",
            category=FeatureCategory.VOLATILITY,
            description="Maximum drawdown over 60-day window",
            parameters={"period": 60},
            required_data=["close"],
        ),
        "max_drawdown_252d": FeatureDefinition(
            name="max_drawdown_252d",
            category=FeatureCategory.VOLATILITY,
            description="Maximum drawdown over 252-day window",
            parameters={"period": 252},
            required_data=["close"],
        ),
        # Technical Indicator Features
        "zscore_20": FeatureDefinition(
            name="zscore_20",
            category=FeatureCategory.VOLATILITY,
            description="20-day z-score for mean reversion",
            parameters={"period": 20},
            required_data=["close"],
        ),
        "zscore_60": FeatureDefinition(
            name="zscore_60",
            category=FeatureCategory.VOLATILITY,
            description="60-day z-score for mean reversion",
            parameters={"period": 60},
            required_data=["close"],
        ),
        "rsi_14": FeatureDefinition(
            name="rsi_14",
            category=FeatureCategory.MOMENTUM,
            description="14-day Relative Strength Index",
            parameters={"period": 14},
            required_data=["close"],
        ),
        "atr_14": FeatureDefinition(
            name="atr_14",
            category=FeatureCategory.VOLATILITY,
            description="14-day Average True Range",
            parameters={"period": 14},
            required_data=["high", "low", "close"],
        ),
        "macd": FeatureDefinition(
            name="macd",
            category=FeatureCategory.MOMENTUM,
            description="MACD (12, 26, 9)",
            parameters={"fast": 12, "slow": 26, "signal": 9},
            required_data=["close"],
        ),
        "bollinger_bands": FeatureDefinition(
            name="bollinger_bands",
            category=FeatureCategory.VOLATILITY,
            description="Bollinger Bands (20, 2)",
            parameters={"period": 20, "std": 2},
            required_data=["close"],
        ),
        "stochastic": FeatureDefinition(
            name="stochastic",
            category=FeatureCategory.MOMENTUM,
            description="Stochastic Oscillator (14, 3, 3)",
            parameters={"k_period": 14, "k_smooth": 3, "d_period": 3},
            required_data=["high", "low", "close"],
        ),
    }

    def __init__(self):
        self._custom_features: Dict[str, FeatureDefinition] = {}

    def register(self, feature: FeatureDefinition):
        """Register a custom feature."""
        self._custom_features[feature.name] = feature
        logger.info(f"Registered custom feature: {feature.name}")

    def get(self, name: str) -> Optional[FeatureDefinition]:
        """Get feature definition by name."""
        return self.FEATURES.get(name) or self._custom_features.get(name)

    def list_features(
        self, category: Optional[FeatureCategory] = None
    ) -> List[FeatureDefinition]:
        """List all features, optionally filtered by category."""
        all_features = {**self.FEATURES, **self._custom_features}
        if category:
            return [f for f in all_features.values() if f.category == category]
        return list(all_features.values())

    def get_required_data(self, feature_names: List[str]) -> List[str]:
        """Get combined required data fields for multiple features."""
        required = set()
        for name in feature_names:
            feat = self.get(name)
            if feat:
                required.update(feat.required_data)
        return list(required)


# Global feature registry instance
_feature_registry = FeatureRegistry()


def get_feature_registry() -> FeatureRegistry:
    """Get the global feature registry."""
    return _feature_registry


# ----------------------------------------------------------------------
# Feature computation functions
# ----------------------------------------------------------------------


def compute_momentum(
    df: pd.DataFrame, period: int = 20, price_col: str = "close"
) -> pd.Series:
    """Compute momentum (return) over specified period.

    Args:
        df: DataFrame with price data
        period: Number of periods for momentum calculation
        price_col: Column name for price

    Returns:
        Series with momentum values
    """
    return df[price_col].pct_change(period)


def compute_volatility(
    df: pd.DataFrame, period: int = 20, price_col: str = "close", annualize: bool = True
) -> pd.Series:
    """Compute realized volatility.

    Args:
        df: DataFrame with price data
        period: Rolling window size
        price_col: Column name for price
        annualize: Whether to annualize (multiply by sqrt(252))

    Returns:
        Series with volatility values
    """
    returns = df[price_col].pct_change()
    vol = returns.rolling(window=period).std()
    if annualize:
        vol = vol * np.sqrt(252)
    return vol


def compute_sharpe_ratio(
    df: pd.DataFrame, period: int = 60, price_col: str = "close", risk_free: float = 0.0
) -> pd.Series:
    """Compute rolling Sharpe ratio.

    Args:
        df: DataFrame with price data
        period: Rolling window size
        price_col: Column name for price
        risk_free: Risk-free rate (annualized)

    Returns:
        Series with Sharpe ratio values
    """
    returns = df[price_col].pct_change()
    mean_return = returns.rolling(window=period).mean()
    std_return = returns.rolling(window=period).std()

    sharpe = (mean_return - risk_free / 252) / std_return
    sharpe = sharpe * np.sqrt(252)  # Annualize
    return sharpe


def compute_sortino_ratio(
    df: pd.DataFrame, period: int = 60, price_col: str = "close", risk_free: float = 0.0
) -> pd.Series:
    """Compute rolling Sortino ratio (downside deviation).

    Args:
        df: DataFrame with price data
        period: Rolling window size
        price_col: Column name for price
        risk_free: Risk-free rate (annualized)

    Returns:
        Series with Sortino ratio values
    """
    returns = df[price_col].pct_change()
    mean_return = returns.rolling(window=period).mean()

    # Downside returns only
    downside_returns = returns.copy()
    downside_returns[downside_returns > 0] = 0
    downside_std = downside_returns.rolling(window=period).std()

    sortino = (mean_return - risk_free / 252) / downside_std
    sortino = sortino * np.sqrt(252)  # Annualize
    return sortino


def compute_max_drawdown(
    df: pd.DataFrame, period: int = 60, price_col: str = "close"
) -> pd.Series:
    """Compute maximum drawdown over rolling window.

    Args:
        df: DataFrame with price data
        period: Rolling window size
        price_col: Column name for price

    Returns:
        Series with max drawdown values (negative)
    """
    rolling_max = df[price_col].rolling(window=period, min_periods=1).max()
    drawdown = (df[price_col] - rolling_max) / rolling_max
    return drawdown


def compute_price_to_sma(
    df: pd.DataFrame, period: int = 50, price_col: str = "close"
) -> pd.Series:
    """Compute price relative to simple moving average.

    Args:
        df: DataFrame with price data
        period: SMA period
        price_col: Column name for price

    Returns:
        Series with price/SMA ratio
    """
    sma = df[price_col].rolling(window=period).mean()
    return df[price_col] / sma


# ----------------------------------------------------------------------
# Technical Indicator Functions
# ----------------------------------------------------------------------


def compute_zscore(
    df: pd.DataFrame, period: int = 20, price_col: str = "close"
) -> pd.Series:
    """Compute z-score for mean reversion signals.

    Args:
        df: DataFrame with price data
        period: Rolling window for z-score calculation
        price_col: Column name for price

    Returns:
        Series with z-score values
    """
    rolling_mean = df[price_col].rolling(window=period).mean()
    rolling_std = df[price_col].rolling(window=period).std()
    zscore = (df[price_col] - rolling_mean) / rolling_std
    return zscore


def compute_volatility_regime(
    df: pd.DataFrame,
    lookback: int = 60,
    threshold: float = 1.0,
    price_col: str = "close",
) -> pd.Series:
    """Compute volatility regime (HIGH/LOW).

    Args:
        df: DataFrame with price data
        lookback: Period to compute historical volatility
        threshold: Number of std devs to classify regime
        price_col: Column name for price

    Returns:
        Series with regime values: 1 (HIGH), 0 (LOW)
    """
    returns = df[price_col].pct_change()
    vol = returns.rolling(window=lookback).std() * np.sqrt(252)

    # Use expanding window for first regime
    expanding_vol = returns.expanding().std() * np.sqrt(252)

    # Combine: use expanding for initial values, rolling for rest
    vol = vol.combine_first(expanding_vol)

    # Calculate running average volatility
    vol_ma = vol.rolling(window=lookback * 2, min_periods=lookback).mean()

    # Regime: 1 if vol > threshold * average, 0 otherwise
    regime = (vol > vol_ma * threshold).astype(int)
    return regime


def compute_rsi(
    df: pd.DataFrame, period: int = 14, price_col: str = "close"
) -> pd.Series:
    """Compute Relative Strength Index.

    Args:
        df: DataFrame with price data
        period: RSI period (typically 14)
        price_col: Column name for price

    Returns:
        Series with RSI values (0-100)
    """
    delta = df[price_col].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Use EMA for subsequent values
    avg_gain = avg_gain.combine_first(gain.ewm(span=period, adjust=False).mean())
    avg_loss = avg_loss.combine_first(loss.ewm(span=period, adjust=False).mean())

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_atr(
    df: pd.DataFrame,
    period: int = 14,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    """Compute Average True Range.

    Args:
        df: DataFrame with OHLC data
        period: ATR period (typically 14)
        high_col: Column name for high price
        low_col: Column name for low price
        close_col: Column name for close price

    Returns:
        Series with ATR values
    """
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]

    # True Range = max of:
    # 1. High - Low
    # 2. |High - Previous Close|
    # 3. |Low - Previous Close|
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()
    return atr


def compute_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_col: str = "close",
) -> pd.DataFrame:
    """Compute MACD (Moving Average Convergence Divergence).

    Args:
        df: DataFrame with price data
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        price_col: Column name for price

    Returns:
        DataFrame with macd, signal, and histogram columns
    """
    ema_fast = df[price_col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[price_col].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    result = pd.DataFrame(
        {"macd": macd_line, "macd_signal": signal_line, "macd_histogram": histogram},
        index=df.index,
    )

    return result


def compute_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2.0,
    price_col: str = "close",
) -> pd.DataFrame:
    """Compute Bollinger Bands.

    Args:
        df: DataFrame with price data
        period: Moving average period
        std_multiplier: Number of standard deviations for bands
        price_col: Column name for price

    Returns:
        DataFrame with bb_upper, bb_middle, bb_lower columns
    """
    middle = df[price_col].rolling(window=period).mean()
    std = df[price_col].rolling(window=period).std()

    upper = middle + (std * std_multiplier)
    lower = middle - (std * std_multiplier)

    # Position/bandwidth
    bandwidth = (upper - lower) / middle
    percent = (df[price_col] - lower) / (upper - lower)

    result = pd.DataFrame(
        {
            "bb_upper": upper,
            "bb_middle": middle,
            "bb_lower": lower,
            "bb_bandwidth": bandwidth,
            "bb_percent": percent,
        },
        index=df.index,
    )

    return result


def compute_stochastic(
    df: pd.DataFrame,
    k_period: int = 14,
    k_smooth: int = 3,
    d_period: int = 3,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.DataFrame:
    """Compute Stochastic Oscillator.

    Args:
        df: DataFrame with OHLC data
        k_period: %K period
        k_smooth: %K smoothing (typically 3)
        d_period: %D period (signal line)
        high_col: Column name for high price
        low_col: Column name for low price
        close_col: Column name for close price

    Returns:
        DataFrame with %K and %D columns
    """
    high_rolling = df[high_col].rolling(window=k_period).max()
    low_rolling = df[low_col].rolling(window=k_period).min()

    # %K = 100 * (Close - Lowest Low) / (Highest High - Lowest Low)
    k_raw = 100 * (df[close_col] - low_rolling) / (high_rolling - low_rolling)

    # Smooth %K
    k = k_raw.rolling(window=k_smooth).mean()

    # %D = SMA of %K
    d = k.rolling(window=d_period).mean()

    result = pd.DataFrame({"stoch_k": k, "stoch_d": d}, index=df.index)

    return result


class FeaturePipeline:
    """Reusable feature computation pipeline for any asset.

    This class provides a convenient way to compute multiple technical
    indicators and features from price data in a single call.

    Example:
        >>> pipeline = FeaturePipeline(features=['zscore_20', 'rsi_14', 'macd'])
        >>> features_df = pipeline.compute(price_df)
    """

    def __init__(
        self,
        features: Optional[List[str]] = None,
        price_col: str = "close",
        high_col: str = "high",
        low_col: str = "low",
    ):
        """Initialize the feature pipeline.

        Args:
            features: List of feature names to compute. If None, computes all available.
            price_col: Column name for close price
            high_col: Column name for high price
            low_col: Column name for low price
        """
        self.features = features or []
        self.price_col = price_col
        self.high_col = high_col
        self.low_col = low_col
        self.registry = get_feature_registry()

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute all configured features from price data.

        Args:
            df: DataFrame with OHLC price data

        Returns:
            DataFrame with original data + computed features
        """
        result = df.copy()

        for feature_name in self.features:
            if feature_name == "zscore_20":
                result["zscore_20"] = compute_zscore(
                    df, period=20, price_col=self.price_col
                )
            elif feature_name == "zscore_60":
                result["zscore_60"] = compute_zscore(
                    df, period=60, price_col=self.price_col
                )
            elif feature_name == "vol_regime":
                result["vol_regime"] = compute_volatility_regime(
                    df, price_col=self.price_col
                )
            elif feature_name == "rsi_14":
                result["rsi_14"] = compute_rsi(df, period=14, price_col=self.price_col)
            elif feature_name == "atr_14":
                result["atr_14"] = compute_atr(
                    df,
                    period=14,
                    high_col=self.high_col,
                    low_col=self.low_col,
                    close_col=self.price_col,
                )
            elif feature_name == "macd":
                macd_df = compute_macd(df, price_col=self.price_col)
                result = pd.concat([result, macd_df], axis=1)
            elif feature_name == "bollinger_bands":
                bb_df = compute_bollinger_bands(df, price_col=self.price_col)
                result = pd.concat([result, bb_df], axis=1)
            elif feature_name == "stochastic":
                stoch_df = compute_stochastic(
                    df,
                    high_col=self.high_col,
                    low_col=self.low_col,
                    close_col=self.price_col,
                )
                result = pd.concat([result, stoch_df], axis=1)
            else:
                # Try to compute from registry
                feat = self.registry.get(feature_name)
                if feat:
                    params = feat.parameters.copy()
                    params["df"] = df
                    params["price_col"] = self.price_col

                    if feature_name.startswith("momentum"):
                        result[feature_name] = compute_momentum(**params)
                    elif feature_name.startswith("volatility"):
                        result[feature_name] = compute_volatility(**params)
                    elif feature_name.startswith("sharpe"):
                        result[feature_name] = compute_sharpe_ratio(**params)
                    elif feature_name.startswith("sortino"):
                        result[feature_name] = compute_sortino_ratio(**params)
                    elif feature_name.startswith("max_drawdown"):
                        result[feature_name] = compute_max_drawdown(**params)
                    elif feature_name.startswith("price_to_sma"):
                        result[feature_name] = compute_price_to_sma(**params)
                else:
                    logger.warning(f"Unknown feature: {feature_name}")

        return result

    def list_available_features(self) -> List[str]:
        """List all available features.

        Returns:
            List of feature names
        """
        all_features = list(self.registry.FEATURES.keys())
        # Add technical indicators
        all_features.extend(
            [
                "zscore_20",
                "zscore_60",
                "vol_regime",
                "rsi_14",
                "atr_14",
                "macd",
                "bollinger_bands",
                "stochastic",
            ]
        )
        return sorted(set(all_features))


def compute_features(
    df: pd.DataFrame, feature_names: List[str], price_col: str = "close"
) -> pd.DataFrame:
    """Compute multiple features from price data.

    Args:
        df: DataFrame with price data (must have date index or column)
        feature_names: List of feature names to compute
        price_col: Column name for price

    Returns:
        DataFrame with computed features
    """
    result = df.copy()

    registry = get_feature_registry()

    for feature_name in feature_names:
        feat = registry.get(feature_name)
        if feat is None:
            logger.warning(f"Unknown feature: {feature_name}")
            continue

        params = feat.parameters.copy()
        params["df"] = result
        params["price_col"] = price_col

        # Dispatch to computation function
        if feature_name.startswith("momentum"):
            period = params.get("period", 20)
            result[feature_name] = compute_momentum(period=period, **params)
        elif feature_name.startswith("volatility"):
            period = params.get("period", 20)
            annualize = params.get("annualize", True)
            result[feature_name] = compute_volatility(
                period=period, annualize=annualize, **params
            )
        elif feature_name.startswith("sharpe_ratio"):
            result[feature_name] = compute_sharpe_ratio(**params)
        elif feature_name.startswith("sortino_ratio"):
            result[feature_name] = compute_sortino_ratio(**params)
        elif feature_name.startswith("max_drawdown"):
            period = params.get("period", 60)
            result[feature_name] = compute_max_drawdown(period=period, **params)
        elif feature_name.startswith("price_to_sma"):
            period = params.get("period", 50)
            result[feature_name] = compute_price_to_sma(period=period, **params)
        else:
            logger.warning(f"No computation function for feature: {feature_name}")

    return result


# ----------------------------------------------------------------------
# Macro features (from FRED data)
# ----------------------------------------------------------------------


def compute_macro_features(
    prices_df: pd.DataFrame,
    fred_df: pd.DataFrame,
    feature_config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Compute macro-linked features.

    Args:
        prices_df: DataFrame with price data
        fred_df: DataFrame with FRED series (wide format: date, series_id, value)
        feature_config: Optional configuration for which macro features to compute

    Returns:
        DataFrame with macro features merged
    """
    if feature_config is None:
        feature_config = {}

    result = prices_df.copy()

    # Merge macro data
    if not fred_df.empty:
        # Pivot FRED data to wide format
        fred_wide = fred_df.pivot(index="date", columns="series_id", values="value")
        fred_wide = fred_wide.reset_index()

        # Forward fill missing values
        fred_wide = fred_wide.ffill()

        # Merge with prices
        result = result.merge(fred_wide, on="date", how="left")
        result = result.ffill()

    return result
