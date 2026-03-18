# Feature Registry Guide

This document describes the standardized features available in the research platform for signal generation and backtesting.

## Overview

The Feature Registry provides centralized definitions for quantitative features used in:
- Signal research and hypothesis testing
- Factor-based strategies
- Backtesting and performance evaluation

## Available Features

### Momentum Features

| Feature Name | Description | Parameters |
|--------------|-------------|------------|
| `momentum_20d` | 20-day price momentum (return) | `period: 20` |
| `momentum_60d` | 60-day price momentum | `period: 60` |
| `momentum_120d` | 120-day price momentum | `period: 120` |
| `momentum_252d` | 252-day (1 year) momentum | `period: 252` |
| `momentum_12_1` | 12-month minus 1-month momentum (Jagadeesh & Titman) | `period_long: 252`, `period_short: 21` |

### Volatility Features

| Feature Name | Description | Parameters |
|--------------|-------------|------------|
| `volatility_20d` | 20-day realized volatility (annualized) | `period: 20`, `annualize: True` |
| `volatility_60d` | 60-day realized volatility | `period: 60`, `annualize: True` |
| `volatility_252d` | 252-day realized volatility | `period: 252`, `annualize: True` |
| `max_drawdown_60d` | Maximum drawdown over 60-day window | `period: 60` |
| `max_drawdown_252d` | Maximum drawdown over 252-day window | `period: 252` |

### Value Features

| Feature Name | Description | Parameters |
|--------------|-------------|------------|
| `price_to_sma_50` | Price relative to 50-day SMA | `period: 50` |
| `price_to_sma_200` | Price relative to 200-day SMA | `period: 200` |

### Quality Features

| Feature Name | Description | Parameters |
|--------------|-------------|------------|
| `sharpe_ratio_60d` | 60-day Sharpe ratio (annualized) | `period: 60`, `risk_free: 0.0` |
| `sortino_ratio_60d` | 60-day Sortino ratio (downside deviation) | `period: 60`, `risk_free: 0.0` |

### Carry Features

| Feature Name | Description | Parameters |
|--------------|-------------|------------|
| `carry_1y` | 1-year forward minus spot (carry) | `period: 252` |

## Using Features in Python

```python
from backend.research.features import compute_features, get_feature_registry

# Get registry
registry = get_feature_registry()

# List all features
features = registry.list_features()
print(f"Total features: {len(features)}")

# List by category
momentum_features = registry.list_features(FeatureCategory.MOMENTUM)

# Compute features from price data
import pandas as pd
df = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', ...],
    'close': [100.0, 101.0, ...]
})

# Compute specific features
result = compute_features(df, ['momentum_20d', 'volatility_60d'], price_col='close')
```

## Using Features via API

```bash
# List all features
curl http://localhost:8000/api/research/features

# List momentum features
curl "http://localhost:8000/api/research/features?category=momentum"

# Compute features
curl -X POST "http://localhost:8000/api/research/features/compute" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"date": "2024-01-01", "close": 100},
      {"date": "2024-01-02", "close": 101}
    ],
    "feature_names": ["momentum_20d", "volatility_60d"],
    "price_col": "close"
  }'
```

## Adding Custom Features

```python
from backend.research.features import FeatureRegistry, FeatureDefinition, FeatureCategory

# Create custom feature
custom_feature = FeatureDefinition(
    name="my_custom_momentum",
    category=FeatureCategory.MOMENTUM,
    description="Custom 30-day momentum",
    parameters={"period": 30},
    required_data=["close"]
)

# Register
registry = get_feature_registry()
registry.register(custom_feature)
```

## Feature Categories

- **MOMENTUM**: Price momentum and trend features
- **VOLATILITY**: Risk and volatility measures
- **VALUE**: Valuation and mean-reversion indicators
- **QUALITY**: Risk-adjusted performance metrics
- **CARRY**: Forward/spot spread features
- **GROWTH**: Growth rate features
- **MACRO**: Macroeconomic indicators
