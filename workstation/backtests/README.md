# Backtests

Unified backtesting framework combining signal research, portfolio construction, and backtrader-based execution.

## Directory Structure

```
backtests/
├── __init__.py
├── core.py                 # Core utilities
├── metrics.py              # Performance metrics
├── walkforward.py          # Walk-forward analysis
│
├── strategies/             # Signal definitions (upstream)
│   ├── __init__.py
│   ├── signals.py         # Signal classes (Momentum, Carry, MeanReversion, etc.)
│   └── metadata.py        # Strategy metadata for PnL attribution
│
├── forward_pass/           # Dual-tracking: prediction vs actual
│   ├── __init__.py
│   ├── trade_tracker.py   # Track signal context per trade
│   └── comparison.py      # Side-by-side comparison view
│
├── builder.py             # Portfolio builder: signals → alpha → weights
│
├── event_driven/          # Event-driven framework
│   ├── __init__.py
│   ├── engine.py
│   └── events.py
│
└── runners/               # Experiment runners
    ├── __init__.py
    ├── momentum.py        # Momentum signal experiment
    └── portfolio_opt.py   # Portfolio optimization experiment
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  strategies/ │────►│   builder.py  │────►│  Backtrader  │────►│     IBKR     │
  │   signals.py │     │    (alpha)   │     │   engine.py  │     │   (live)     │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        │                     │                     │
        │                     │                     │
   "What to trade"       "How much"            "Execute"
   (signal scores)       (weights)           (Backtrader)
```

### Two Usage Modes

1. **Research Mode** - Pure pandas, no Backtrader dependency:
```python
from backtests.strategies import get_signal, MomentumSignal

signal = get_signal("momentum_60_21")
sig_values = signal.compute(prices)  # Returns pd.Series
positions = signal.to_positions(sig_values)
```

2. **Backtest Mode** - Native Backtrader integration:
```python
from backtests.strategies import create_signal_strategy, MomentumSignal

# Create Backtrader strategy from signal
StrategyClass = create_signal_strategy(MomentumSignal, {'lookback': 60, 'skip': 21})
cerebro.addstrategy(StrategyClass)
```

3. **Blended Signals** - Combine multiple signals:
```python
from backtests.strategies import create_blended_strategy, MomentumSignal, MeanReversionSignal

StrategyClass = create_blended_strategy(
    [MomentumSignal, MeanReversionSignal],
    [{'lookback': 60}, {'lookback': 30}],
    weights=[0.7, 0.3]
)
cerebro.addstrategy(StrategyClass)
```

### Detailed Flow

1. **Signals** (`strategies/signals.py`)
   - Define trading signals (Momentum, Carry, MeanReversion, etc.)
   - Each signal: `compute(prices) → signal_scores`
   - Registry: `get_signal(name)`, `register(signal)`

2. **Portfolio Builder** (`builder.py`)
   - Load price data for universe
   - Compute signals via `get_signal()`
   - Generate alpha scores (blend signals)
   - Optimize weights (mean-variance, risk-parity, etc.)

3. **Event-Driven Engine** (`event_driven/`)
   - Backtrader-based backtesting
   - Consistent logic between backtest and live

4. **Live Execution**
   - Connect to IBKR via `IBKRClient`
   - Same signals, same execution logic

## Usage

### 1. Using Signals Directly

```python
from backtests.strategies import get_signal, list_signals

# List available signals
print(list_signals())

# Get a signal
signal = get_signal("momentum_12_1")
sig_values = signal.compute(prices)
positions = signal.to_positions(sig_values)
```

### 2. Using Portfolio Builder

```python
from backtests.builder import PortfolioBuilder, PortfolioConfig

builder = PortfolioBuilder(
    PortfolioConfig(
        universe=["SPY", "TLT", "GLD"],
        signals=["momentum_60_21", "mean_reversion"],
        optimization="risk_parity",
    )
)

# Load data
import yfinance as yf
def loader(ticker, start, end):
    return yf.download(ticker, start=start, end=end, progress=False)

builder.load_data(loader, "2020-01-01", "2023-12-31")
builder.compute_signals()
builder.optimize_weights()

# Run backtest
results = builder.backtest()

# Get metrics
metrics = builder.get_portfolio_metrics()
print(metrics)
```

### 3. Running Experiments

```bash
# Momentum signal experiment
python -m backtests.runners.momentum --ticker SPY --start 2020-01-01 --end 2023-12-31

# Portfolio optimization
python -m backtests.runners.portfolio_opt --returns_csv returns.csv --max_weight 0.2
```

## Strategy Metadata

Strategy metadata is defined in `strategies/metadata.py` for PnL attribution:

```python
from backtests.strategies import SIGNAL_METADATA, get_signal_metadata

metadata = get_signal_metadata("momentum_tech")
# {
#   "thesis": "Capture tech sector momentum...",
#   "factors": ["momentum", "size", "growth"],
#   "positions": ["AAPL", "MSFT", "GOOGL", ...]
# }
```

## Backtest Engine

The canonical event-driven backtest engine is in `workstation/backtests/event_driven/backtest_engine.py`.
Legacy imports from `backend.backtest_engine` still work through a compatibility shim:

```python
from backend.backtest_engine import BacktestEngine, IBKRDataFeed
import backtrader as bt

engine = BacktestEngine(cash=100000, commission=0.001)
engine.add_data(IBKRDataFeed(dataname=df), name="SPY")
engine.add_strategy(MyStrategy)
result = engine.run_backtest()
```

## Forward Pass: Dual Tracking

Track both **what the strategy predicted** (forward-pass) and **what actually happened** (post-trade) for attribution:

```python
from backtests.forward_pass import ForwardPassTracker, ComparisonView
from datetime import datetime

# 1. Track predictions during backtest
tracker = ForwardPassTracker()

# At each bar, update signals
tracker.update_signals(datetime.now(), {"momentum": 0.73, "mean_reversion": -0.2})

# When opening a trade
tracker.open_trade(
    timestamp=datetime.now(),
    ticker="AAPL",
    direction=1,  # Long
    quantity=100,
    price=150.25,
    predicted_return=0.05,  # What we expected
    confidence=0.8,          # Signal confidence
)

# When closing the trade
tracker.close_trade("AAPL", datetime.now(), price=155.00)

# 2. Compare with post-trade attribution
comparison = ComparisonView(tracker, attribution_df)

# Get summary
summary = comparison.get_summary()
# {
#   "direction_accuracy": 0.65,
#   "high_confidence_accuracy": 0.78,
#   "prediction_bias": -0.02,
#   "factor_impact": {"momentum": 0.015, "value": -0.003},
# }

# Get per-signal accuracy
signal_quality = comparison.get_prediction_quality_by_signal()

# Get confusion matrix
confusion = comparison.get_confusion_matrix()

# Get LLM explanations
explanations = comparison.get_llm_explanations()
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `SignalHistory` | Time series of signal values at each bar |
| `TradeRecord` | Single trade with entry/exit context |
| `ForwardPassTracker` | Aggregator for tracking predictions |
| `ComparisonView` | Side-by-side comparison with attribution |

### Look-Ahead Bias Prevention

When using forward-pass tracking, ensure signals are computed using only data available at time t:

```python
# ✅ Correct: Signal uses closed bar data
signal_value = momentum_signal.compute(prices)  # prices up to t, not t+1

# ❌ Wrong: Using future data
signal_value = prices['close'].shift(-1)  # Look-ahead!
```

The tracker records what was available at each timestamp, so you can later verify no look-ahead bias occurred.

### Use Cases

- **Signal quality analysis**: Are high-confidence signals actually more accurate?
- **Prediction bias detection**: Do we systematically over/under-predict?
- **Factor contribution**: Which signals drive actual returns?
- **LLM storytelling**: Compare what we predicted vs what actually happened

## Notes

- All paths use `backtests.` import prefix
- Signals are registered at module load time
- Portfolio builder uses backtrader internally for execution
- Live trading uses the same signals and execution logic
