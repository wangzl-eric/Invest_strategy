# ML Features Usage Guide

This guide explains how to use the machine learning and advanced analytics features in the platform, including regime detection, anomaly detection, stress testing, and factor analysis.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Regime Detection](#regime-detection)
3. [Anomaly Detection](#anomaly-detection)
4. [Stress Testing](#stress-testing)
5. [Factor Analysis (ML-based)](#factor-analysis-ml-based)
6. [Portfolio Optimization (ML-based)](#portfolio-optimization-ml-based)
7. [Python Examples](#python-examples)
8. [Integration Examples](#integration-examples)

## Quick Start

All ML features are available via the `/api/analytics/` endpoints. Start by accessing the API documentation:

```bash
# Open in browser
http://localhost:8000/docs
```

Navigate to the **"advanced-analytics"** section to see all available ML endpoints.

---

## Regime Detection

Detects current market regime (bull/bear/neutral) using statistical analysis of recent returns.

### Endpoint

`GET /api/analytics/regime-detection`

### Parameters

- `account_id` (optional): Your IBKR account ID (auto-detected if not provided)
- `lookback_window` (default: 60): Number of days to analyze
- `start_date` (optional): Start date for analysis
- `end_date` (optional): End date for analysis

### Example Request (curl)

```bash
curl "http://localhost:8000/api/analytics/regime-detection?account_id=U1234567&lookback_window=90"
```

### Example Request (Python)

```python
import requests
from datetime import datetime, timedelta

response = requests.get(
    "http://localhost:8000/api/analytics/regime-detection",
    params={
        "account_id": "U1234567",
        "lookback_window": 90,  # Analyze last 90 days
    }
)

result = response.json()

print(f"Current Regime: {result['regime'].upper()}")
print(f"Mean Return: {result['mean_return']:.4%}")
print(f"Volatility: {result['volatility']:.4%}")
print(f"Confidence: {result['confidence']:.2f}")

# Regime can be: "bull", "bear", or "neutral"
if result['regime'] == 'bull':
    print("✅ Bull market detected - consider increasing exposure")
elif result['regime'] == 'bear':
    print("⚠️ Bear market detected - consider defensive positioning")
else:
    print("➡️ Neutral market - maintain current strategy")
```

### Example Response

```json
{
  "regime": "bull",
  "mean_return": 0.0015,
  "volatility": 0.015,
  "confidence": 0.10
}
```

### Use Cases

1. **Dynamic Asset Allocation**: Adjust portfolio weights based on detected regime
2. **Risk Management**: Reduce exposure during bear markets
3. **Strategy Selection**: Switch between aggressive and defensive strategies

---

## Anomaly Detection

Detects anomalous returns using statistical methods (Z-score analysis).

### Endpoint

`GET /api/analytics/anomaly-detection`

### Parameters

- `account_id` (optional): Your IBKR account ID
- `threshold_sigma` (default: 3.0): Number of standard deviations for anomaly threshold
- `start_date` (optional): Start date for analysis
- `end_date` (optional): End date for analysis

### Example Request (Python)

```python
import requests

response = requests.get(
    "http://localhost:8000/api/analytics/anomaly-detection",
    params={
        "account_id": "U1234567",
        "threshold_sigma": 3.0,  # Flag returns > 3 standard deviations
    }
)

result = response.json()

print(f"Anomalies Detected: {result['num_anomalies']}")
print(f"Threshold: {result['threshold_sigma']}σ")
print(f"Mean Return: {result['mean']:.4%}")
print(f"Std Dev: {result['std']:.4%}")

if result['num_anomalies'] > 0:
    print("\n⚠️ Anomalous Returns Found:")
    for date, value in zip(result['anomaly_dates'], result['anomaly_values']):
        print(f"  {date}: {value:.4%}")
else:
    print("✅ No anomalies detected")
```

### Example Response

```json
{
  "num_anomalies": 3,
  "anomaly_dates": [
    "2024-01-15T00:00:00",
    "2024-03-22T00:00:00",
    "2024-06-10T00:00:00"
  ],
  "anomaly_values": [0.085, -0.092, 0.078],
  "threshold_sigma": 3.0,
  "mean": 0.0012,
  "std": 0.015
}
```

### Use Cases

1. **Risk Monitoring**: Flag unusual trading days that may indicate errors or market events
2. **Data Quality**: Identify data anomalies that need investigation
3. **Event Detection**: Detect significant market events or news impacts

---

## Stress Testing

Tests portfolio performance under various stress scenarios (market crashes, volatility spikes, etc.).

### Endpoint

`POST /api/analytics/stress-test`

### Parameters

- `account_id` (optional): Your IBKR account ID
- `scenarios` (optional): JSON array of scenario objects (uses defaults if not provided)
- `start_date` (optional): Start date for historical data
- `end_date` (optional): End date for historical data

### Scenario Format

Each scenario is a dictionary with:
- `name`: Scenario name
- `market_shock`: Market return shock (e.g., -0.20 for -20%)
- `volatility_multiplier`: Volatility multiplier (e.g., 2.0 for 2x volatility)

### Example Request (Python)

```python
import requests
import json

# Custom scenarios
scenarios = [
    {
        "name": "2008 Financial Crisis",
        "market_shock": -0.38,  # -38% market drop
        "volatility_multiplier": 3.0
    },
    {
        "name": "COVID-19 March 2020",
        "market_shock": -0.34,  # -34% drop
        "volatility_multiplier": 2.5
    },
    {
        "name": "Moderate Correction",
        "market_shock": -0.10,  # -10% correction
        "volatility_multiplier": 1.5
    }
]

response = requests.post(
    "http://localhost:8000/api/analytics/stress-test",
    params={
        "account_id": "U1234567",
        "scenarios": json.dumps(scenarios),
    }
)

result = response.json()

print("Stress Test Results:")
print("=" * 50)
for scenario_name, scenario_result in result.items():
    print(f"\n{scenario_name}:")
    print(f"  Final Value: ${scenario_result['final_value']:,.2f}")
    print(f"  Return Impact: {scenario_result['return_impact']:.2%}")
    print(f"  Volatility Impact: {scenario_result['volatility_impact']:.2%}")
    print(f"  Estimated Drawdown: {scenario_result['drawdown_estimate']:.2%}")
```

### Example Response

```json
{
  "2008 Financial Crisis": {
    "final_value": 62000.0,
    "return_impact": -0.38,
    "volatility_impact": 0.45,
    "drawdown_estimate": 0.38
  },
  "COVID-19 March 2020": {
    "final_value": 66000.0,
    "return_impact": -0.34,
    "volatility_impact": 0.375,
    "drawdown_estimate": 0.34
  },
  "Moderate Correction": {
    "final_value": 90000.0,
    "return_impact": -0.10,
    "volatility_impact": 0.225,
    "drawdown_estimate": 0.10
  }
}
```

### Use Cases

1. **Risk Assessment**: Understand portfolio behavior under extreme conditions
2. **Capital Planning**: Determine capital requirements for stress scenarios
3. **Regulatory Compliance**: Meet stress testing requirements

---

## Factor Analysis (ML-based)

Uses linear regression (ML) to decompose portfolio returns into factor exposures.

### Endpoint

`GET /api/analytics/factor-analysis/fama-french`

This uses **Fama-French factor model** which applies linear regression to decompose returns into:
- **Market factor** (beta)
- **HML** (High minus Low - value factor)
- **SMB** (Small minus Big - size factor)
- **UMD** (Up minus Down - momentum factor, if available)

### Example Request (Python)

```python
import requests

response = requests.get(
    "http://localhost:8000/api/analytics/factor-analysis/fama-french",
    params={
        "account_id": "U1234567",
    }
)

result = response.json()

print("Factor Loadings (ML Regression Results):")
print("=" * 50)

# Group by asset
assets = {}
for loading in result['factor_loadings']:
    asset = loading['asset']
    if asset not in assets:
        assets[asset] = {}
    assets[asset][loading['factor']] = loading['loading']

for asset, factors in assets.items():
    print(f"\n{asset}:")
    print(f"  R² (Explained Variance): {result['r_squared'][asset]:.2%}")
    for factor, loading in factors.items():
        print(f"  {factor}: {loading:.4f}")

print("\nFactor Returns:")
for factor, ret in result['factor_returns'].items():
    print(f"  {factor}: {ret:.4%}")
```

### Example Response

```json
{
  "factor_loadings": [
    {"asset": "AAPL", "factor": "Market", "loading": 1.15},
    {"asset": "AAPL", "factor": "HML", "loading": 0.32},
    {"asset": "MSFT", "factor": "Market", "loading": 1.08}
  ],
  "factor_returns": {
    "Market": 0.10,
    "HML": 0.02,
    "SMB": -0.01
  },
  "r_squared": {
    "AAPL": 0.85,
    "MSFT": 0.82
  },
  "factor_names": ["Market", "HML", "SMB"]
}
```

### Understanding the Results

- **Factor Loadings**: Regression coefficients showing sensitivity to each factor
  - Market loading > 1.0 = higher volatility than market
  - HML > 0 = value tilt
  - SMB > 0 = small-cap tilt
- **R²**: Percentage of return variance explained by factors (higher = better model fit)
- **Factor Returns**: Historical returns of each factor

---

## Portfolio Optimization (ML-based)

Uses optimization algorithms (Markowitz, Black-Litterman, Risk Parity) to find optimal portfolio weights.

### Markowitz Optimization

**Endpoint:** `POST /api/analytics/optimization/markowitz`

Uses mean-variance optimization to maximize Sharpe ratio.

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analytics/optimization/markowitz",
    params={
        "account_id": "U1234567",
        "risk_free_rate": 0.02,
        "max_weight": 0.25,  # Max 25% per asset
        "long_only": True,
    }
)

result = response.json()

print("Optimal Portfolio (ML Optimization):")
print(f"  Expected Return: {result['expected_return']:.2%}")
print(f"  Expected Volatility: {result['expected_volatility']:.2%}")
print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
print("\n  Recommended Weights:")
for w in result['weights']:
    print(f"    {w['asset']}: {w['weight']:.2%}")
```

### Black-Litterman Optimization

**Endpoint:** `POST /api/analytics/optimization/black-litterman`

Combines market equilibrium with your views using Bayesian inference.

```python
import requests
import json

# Your views on expected returns
views = {
    "AAPL": 0.15,  # Expect 15% return
    "MSFT": 0.12   # Expect 12% return
}

# Your confidence in each view (0-1)
confidences = {
    "AAPL": 0.8,   # 80% confident
    "MSFT": 0.6    # 60% confident
}

response = requests.post(
    "http://localhost:8000/api/analytics/optimization/black-litterman",
    params={
        "account_id": "U1234567",
        "risk_aversion": 3.0,
        "views": json.dumps(views),
        "view_confidences": json.dumps(confidences),
    }
)

result = response.json()
# Same format as Markowitz
```

---

## Python Examples

### Complete ML Analysis Workflow

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/analytics"
ACCOUNT_ID = "U1234567"

# 1. Detect current market regime
print("1. Market Regime Detection")
regime = requests.get(
    f"{BASE_URL}/regime-detection",
    params={"account_id": ACCOUNT_ID, "lookback_window": 90}
).json()
print(f"   Regime: {regime['regime']}")
print(f"   Confidence: {regime['confidence']:.2f}")

# 2. Check for anomalies
print("\n2. Anomaly Detection")
anomalies = requests.get(
    f"{BASE_URL}/anomaly-detection",
    params={"account_id": ACCOUNT_ID, "threshold_sigma": 3.0}
).json()
print(f"   Anomalies Found: {anomalies['num_anomalies']}")

# 3. Factor analysis
print("\n3. Factor Analysis")
factors = requests.get(
    f"{BASE_URL}/factor-analysis/fama-french",
    params={"account_id": ACCOUNT_ID}
).json()
print(f"   Factors: {factors['factor_names']}")
avg_r2 = sum(factors['r_squared'].values()) / len(factors['r_squared'])
print(f"   Average R²: {avg_r2:.2%}")

# 4. Stress testing
print("\n4. Stress Testing")
scenarios = [
    {"name": "Market Crash", "market_shock": -0.20, "volatility_multiplier": 2.0}
]
stress = requests.post(
    f"{BASE_URL}/stress-test",
    params={"account_id": ACCOUNT_ID, "scenarios": json.dumps(scenarios)}
).json()
print(f"   Crash Scenario Impact: {stress['Market Crash']['return_impact']:.2%}")

# 5. Portfolio optimization
print("\n5. Portfolio Optimization")
opt = requests.post(
    f"{BASE_URL}/optimization/markowitz",
    params={"account_id": ACCOUNT_ID, "risk_free_rate": 0.02}
).json()
print(f"   Optimal Sharpe: {opt['sharpe_ratio']:.2f}")
```

### Automated Risk Monitoring

```python
import requests
import time
from datetime import datetime

def monitor_risk(account_id, check_interval=3600):
    """Monitor portfolio risk using ML features."""
    
    while True:
        try:
            # Check regime
            regime = requests.get(
                "http://localhost:8000/api/analytics/regime-detection",
                params={"account_id": account_id}
            ).json()
            
            if regime['regime'] == 'bear':
                print(f"⚠️ BEAR MARKET DETECTED at {datetime.now()}")
                print(f"   Mean Return: {regime['mean_return']:.4%}")
                # Trigger alerts, reduce exposure, etc.
            
            # Check anomalies
            anomalies = requests.get(
                "http://localhost:8000/api/analytics/anomaly-detection",
                params={"account_id": account_id, "threshold_sigma": 3.5}
            ).json()
            
            if anomalies['num_anomalies'] > 0:
                print(f"🚨 ANOMALIES DETECTED: {anomalies['num_anomalies']}")
                for date, value in zip(anomalies['anomaly_dates'], anomalies['anomaly_values']):
                    print(f"   {date}: {value:.4%}")
            
            time.sleep(check_interval)
            
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(60)

# Run monitoring
# monitor_risk("U1234567")
```

---

## Integration Examples

### Dash Frontend Integration

```python
# In your Dash app (frontend/app.py)
import dash
from dash import dcc, html, Input, Output, callback
import requests

@app.callback(
    Output('regime-display', 'children'),
    Input('refresh-regime', 'n_clicks'),
    State('account-id', 'value')
)
def update_regime(n_clicks, account_id):
    if n_clicks is None:
        return ""
    
    try:
        response = requests.get(
            "http://localhost:8000/api/analytics/regime-detection",
            params={"account_id": account_id}
        )
        result = response.json()
        
        regime_color = {
            "bull": "green",
            "bear": "red",
            "neutral": "gray"
        }.get(result['regime'], "gray")
        
        return html.Div([
            html.H4(f"Market Regime: {result['regime'].upper()}"),
            html.P(f"Confidence: {result['confidence']:.2f}"),
            html.P(f"Mean Return: {result['mean_return']:.4%}"),
        ], style={"color": regime_color})
    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
```

### JavaScript/React Integration

```javascript
// React component for regime detection
async function getMarketRegime(accountId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/analytics/regime-detection?account_id=${accountId}`
    );
    const result = await response.json();
    
    return {
      regime: result.regime,
      confidence: result.confidence,
      meanReturn: result.mean_return,
      volatility: result.volatility
    };
  } catch (error) {
    console.error('Error fetching regime:', error);
    throw error;
  }
}

// Use in component
function RegimeIndicator({ accountId }) {
  const [regime, setRegime] = useState(null);
  
  useEffect(() => {
    getMarketRegime(accountId).then(setRegime);
  }, [accountId]);
  
  if (!regime) return <div>Loading...</div>;
  
  const color = {
    bull: 'green',
    bear: 'red',
    neutral: 'gray'
  }[regime.regime];
  
  return (
    <div style={{ color }}>
      <h3>Market Regime: {regime.regime.toUpperCase()}</h3>
      <p>Confidence: {regime.confidence.toFixed(2)}</p>
    </div>
  );
}
```

---

## Best Practices

### 1. Data Requirements

- **Minimum Data**: At least 30-60 days of historical data for meaningful results
- **More Data = Better**: Longer history improves ML model accuracy
- **Data Quality**: Ensure clean, accurate data for best results

### 2. Parameter Tuning

- **Regime Detection**: Adjust `lookback_window` based on your strategy timeframe
  - Short-term: 30-60 days
  - Medium-term: 60-120 days
  - Long-term: 120+ days

- **Anomaly Detection**: Adjust `threshold_sigma` based on your risk tolerance
  - Conservative: 2.5σ (more anomalies flagged)
  - Standard: 3.0σ
  - Aggressive: 3.5σ (fewer anomalies)

### 3. Combining ML Features

Use multiple ML features together for comprehensive analysis:

```python
# Comprehensive risk assessment
def comprehensive_risk_analysis(account_id):
    # Regime check
    regime = get_regime(account_id)
    
    # Anomaly check
    anomalies = get_anomalies(account_id)
    
    # Stress test
    stress = stress_test(account_id)
    
    # Factor exposure
    factors = get_factors(account_id)
    
    # Risk score
    risk_score = 0
    if regime['regime'] == 'bear':
        risk_score += 30
    if anomalies['num_anomalies'] > 5:
        risk_score += 20
    if stress['Market Crash']['return_impact'] < -0.30:
        risk_score += 30
    if factors['factor_loadings'][0]['loading'] > 1.5:  # High beta
        risk_score += 20
    
    return {
        "risk_score": risk_score,
        "recommendation": "reduce_exposure" if risk_score > 50 else "maintain"
    }
```

---

## Troubleshooting

### "Insufficient data" Error

**Solution**: Ensure you have enough historical data
- Check: `GET /api/pnl?account_id=YOUR_ID&limit=100`
- Minimum: 30 days for basic analysis
- Recommended: 90+ days for reliable ML results

### Regime Always "neutral"

**Possible causes**:
1. Not enough data
2. Returns are truly neutral
3. Lookback window too short

**Solution**: Increase `lookback_window` to 90-120 days

### No Anomalies Detected

**Possible causes**:
1. Threshold too high
2. Data is clean (good!)
3. Not enough data

**Solution**: Lower `threshold_sigma` to 2.5 or check data quality

---

## Next Steps

1. **Automate Monitoring**: Set up scheduled checks for regime and anomalies
2. **Build Alerts**: Integrate with alert system to notify on regime changes
3. **Strategy Adaptation**: Use regime detection to automatically adjust strategies
4. **Risk Limits**: Use stress test results to set position limits

For more information:
- API Documentation: `http://localhost:8000/docs`
- Advanced Analytics Guide: `docs/ADVANCED_ANALYTICS_USAGE.md`
- Source Code: `backend/advanced_analytics.py`
