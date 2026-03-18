# Backtest Engine Guide

Single reference for the BacktestEngine: execution flow, data/action sequencing, position sizing, and optimizer integration.

## Table of Contents

1. [Execution Flow & Data Model](#1-execution-flow--data-model)
2. [Position Sizing](#2-position-sizing)
3. [Historical-Data-Based Sizing](#3-historical-data-based-sizing)
4. [Third-Party Optimizer Integration](#4-third-party-optimizer-integration)
5. [Custom Sizers & Examples](#5-custom-sizers--examples)
6. [Reference](#6-reference)

---

## 1. Execution Flow & Data Model

### Overview

The BacktestEngine uses Backtrader's Cerebro to run bar-by-bar. Each bar triggers a fixed sequence: data update → strategy → observers → broker. The Sizer is invoked only when the strategy places an order (no `next()` of its own).

### Execution Flow (Per Bar)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BAR N ARRIVES                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 1: Data Feeds                                                          │
│  • All data feeds advance to bar N                                           │
│  • data.close[0], data.high[0], etc. = current bar                           │
│  • data.close[-i] = bar N-i (historical)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 2: Strategy Wrapper (Position Tracking)                                 │
│  • next() called (prenext during warmup)                                     │
│  • _record_position() → append {date, position, portfolio_value, price}      │
│  • super().next() → delegate to wrapped strategy                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 3: Strategy (e.g. RegimeFilterStrategy)                                │
│  • Your trading logic runs                                                   │
│  • if signal: self.buy() or self.sell() or self.close()                      │
│  • When buy/sell called with size=None:                                      │
│      └─► Sizer._getsizing() invoked (NODE 3a)                               │
│  • Order created, queued for broker                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 4: Observers                                                           │
│  • PositionObserver.next() → lines.position, lines.portfolio_value           │
│  • TradeLogger.next() → detect position change, append to trade_log          │
│  • Broker observer (if added) → account value for plotting                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE 5: Broker                                                              │
│  • Process queued orders                                                     │
│  • Execute fills, update cash, position                                       │
│  • State ready for next bar                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            NEXT BAR (N+1)
```

### Component Roles

| Component | Has `next()`? | When Called | Purpose |
|-----------|---------------|-------------|---------|
| **Data Feed** | No | Before strategy | Provides bar N prices; `data.close[-i]` = historical |
| **Strategy Wrapper** | Yes | First | Records position/portfolio to `position_history` |
| **Strategy** | Yes | After wrapper | Trading logic; calls `buy()`/`sell()` |
| **Sizer** | No | On `buy()`/`sell()` | `_getsizing()` returns order size |
| **PositionObserver** | Yes | After strategy | Updates observer lines for plotting |
| **TradeLogger** | Yes | After strategy | Logs trades when position changes |
| **Broker** | No | After observers | Executes orders, updates account |

### State at Each Node

| Node | State Before | State After |
|------|--------------|-------------|
| After NODE 1 | — | Bar N loaded; `data.close[0]` = current |
| After NODE 2 | — | `position_history` has entry for bar N |
| After NODE 3 | — | Orders queued; Sizer may have been called |
| After NODE 4 | — | Observer lines updated; trade_log if position changed |
| After NODE 5 | — | Orders executed; cash/position updated |

### Data Flow Diagram

```
                    ┌──────────────┐
                    │  Data Feed   │
                    │  (prices)    │
                    └──────┬───────┘
                           │ data.close[0], data.close[-i]
                           ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Broker    │◄────│   Strategy   │────►│   Sizer     │
│ (cash, pos) │     │  (signals)   │     │ (_getsizing) │
└──────┬──────┘     └──────┬───────┘     └─────────────┘
       │                   │
       │                   │ buy()/sell()
       │                   ▼
       │            ┌──────────────┐
       │            │   Wrapper    │
       │            │ (records)    │
       │            └──────┬───────┘
       │                   │ position_history
       │                   ▼
       │            ┌──────────────┐
       └───────────►│  Observers   │
                    │ (lines, log) │
                    └──────────────┘
```

### Sizer Invocation

The Sizer does **not** have a `next()` method. It is invoked only when:

1. Strategy calls `self.buy()` or `self.sell()` **without** a `size` argument
2. Backtrader sees `size=None` and asks the strategy's Sizer
3. `Sizer._getsizing(comminfo, cash, data, isbuy)` is called
4. Return value becomes the order size

**Timing:** `_getsizing` runs **inside** the strategy's `next()`, at the moment `buy()` or `sell()` is called. It has access to:
- `data.close[-i]` — historical prices
- `self.strategy.broker.getvalue()` — portfolio value
- `len(self.strategy)` — number of bars processed

---

## 2. Position Sizing

### Quick Start

**Default (all-in):** Invest 100% of capital on BUY, 0% on SELL.

```python
from workstation.backtests.event_driven.backtest_engine import BacktestEngine

engine = BacktestEngine(cash=100000)
# sizer defaults to AllInSizer(100%) - no need to specify
```

**Fixed percentage:** Invest 50% of capital per trade.

```python
engine = BacktestEngine(cash=100000, sizer=50)
```

### Sizer Options

| `sizer` Value | Behavior |
|---------------|----------|
| `None` or `'allin'` | AllInSizer(percents=100) — invest 100% on BUY |
| `float` (0–100) | AllInSizer(percents=sizer) — e.g. `50` = half position |
| `bt.Sizer` class | Custom sizer with `sizer_params` passed as kwargs |

### Using `sizer_params` with a Custom Sizer Class

```python
engine = BacktestEngine(
    cash=100000,
    sizer=bt.sizers.AllInSizer,
    sizer_params={'percents': 75}
)
```

---

## 3. Historical-Data-Based Sizing

Size each trade using past price/volatility data. The Sizer has access to `data.close[-i]` (i bars ago) when `_getsizing` runs.

### Built-in Sizers

**VolatilitySizer** — Risk a fixed % of portfolio per unit of volatility. Higher vol → smaller position.

```python
from workstation.backtests.event_driven.backtest_engine import (
    BacktestEngine,
    VolatilitySizer,
)

engine = BacktestEngine(
    cash=100000,
    sizer=VolatilitySizer,
    sizer_params={
        'lookback': 20,       # bars for rolling volatility
        'target_risk': 0.02,  # 2% risk per trade
        'max_pct': 100,       # cap at 100% of portfolio
    }
)
```

**HistoricalPercentSizer** — Scale position by volatility ratio. When current vol is lower than reference vol → larger position.

```python
from workstation.backtests.event_driven.backtest_engine import (
    BacktestEngine,
    HistoricalPercentSizer,
)

engine = BacktestEngine(
    cash=100000,
    sizer=HistoricalPercentSizer,
    sizer_params={
        'lookback': 20,
        'base_pct': 100,   # base allocation
        'ref_vol': 0.02,   # reference vol (None = use rolling mean)
    }
)
```

### How It Works

At each `buy()` call, the Sizer's `_getsizing(comminfo, cash, data, isbuy)` runs. You have access to:

- `data.close[-i]` — close price i bars ago
- `self.strategy.broker.getvalue()` — portfolio value
- `len(self.strategy)` — number of bars processed so far

---

## 4. Third-Party Optimizer Integration

### 1. Optimizer Returns a Single Percentage

```python
def objective(trial):
    position_pct = trial.suggest_float('position_pct', 10, 100)
    engine = BacktestEngine(cash=100000, sizer=position_pct)
    # ... add data, strategy, run
    return -result['max_drawdown']

study = optuna.create_study()
study.optimize(objective, n_trials=50)
engine = BacktestEngine(cash=100000, sizer=study.best_params['position_pct'])
```

### 2. Optimizer Returns Multiple Parameters

```python
optimizer_result = {'position_pct': 45, 'risk_per_trade': 0.02}
engine = BacktestEngine(cash=100000, sizer=optimizer_result['position_pct'])
# Or with custom sizer:
engine = BacktestEngine(cash=100000, sizer=RiskBasedSizer,
    sizer_params={'risk_per_trade': optimizer_result['risk_per_trade']})
```

### 3. Optimizer as External Service/API

```python
params = requests.get("https://api/optimizer/sizing", params={...}).json()
engine = BacktestEngine(cash=100000, sizer=params['position_pct'])
```

### 4. Batch Optimization Loop

```python
for pct in [25, 50, 75, 100]:
    engine = BacktestEngine(cash=100000, sizer=pct)
    # ... run, collect results
best = max(results, key=lambda x: x['sharpe'])
engine = BacktestEngine(cash=100000, sizer=best['position_pct'])
```

---

## 5. Custom Sizers & Examples

### PercentRiskSizer

```python
class PercentRiskSizer(bt.Sizer):
    params = (('risk', 0.02),)
    def _getsizing(self, comminfo, cash, data, isbuy):
        if not isbuy:
            return abs(self.strategy.getposition(data).size)
        price = data.close[0]
        if price <= 0: return 0
        pv = self.strategy.broker.getvalue()
        return int(pv * self.params.risk / price)

engine = BacktestEngine(cash=100000, sizer=PercentRiskSizer,
    sizer_params={'risk': 0.02})
```

### ATR-like Sizer (Using High-Low Range)

```python
class ATRSizer(bt.Sizer):
    params = (('lookback', 20), ('risk_pct', 0.02))
    def _getsizing(self, comminfo, cash, data, isbuy):
        if not isbuy:
            return abs(self.strategy.getposition(data).size)
        price = float(data.close[0])
        ranges = []
        for i in range(1, min(self.params.lookback, len(self.strategy))):
            try:
                h, l = float(data.high[-i]), float(data.low[-i])
                if l > 0: ranges.append((h - l) / l)
            except (IndexError, TypeError): break
        atr_proxy = np.mean(ranges) if ranges else 0.02
        if atr_proxy < 1e-6: return int(cash / price)
        pv = self.strategy.broker.getvalue()
        risk_amt = pv * self.params.risk_pct
        size = int(risk_amt / (price * atr_proxy))
        return min(max(0, size), int(cash / price))
```

### Combining Historical Sizer with Optimizer

```python
def objective(trial):
    lookback = trial.suggest_int('lookback', 10, 60)
    target_risk = trial.suggest_float('target_risk', 0.01, 0.05)
    engine = BacktestEngine(cash=100000, sizer=VolatilitySizer,
        sizer_params={'lookback': lookback, 'target_risk': target_risk})
    # ... run backtest
    return result['sharpe_ratio']
```

---

## 6. Reference

- **Engine API:** `workstation/backtests/event_driven/backtest_engine.py` — `BacktestEngine.__init__(sizer=..., sizer_params=...)`
- **Backtrader Sizers:** https://www.backtrader.com/docu/sizers/sizers/
- **AllInSizer:** https://www.backtrader.com/docu/sizers-reference/
