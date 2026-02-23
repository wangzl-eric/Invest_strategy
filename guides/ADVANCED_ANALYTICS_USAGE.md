# Advanced Analytics Usage Guide

This guide explains how to use the advanced analytics features including portfolio optimization, factor analysis, attribution, and Monte Carlo simulations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Portfolio Optimization](#portfolio-optimization)
3. [Factor Analysis](#factor-analysis)
4. [Attribution Analysis](#attribution-analysis)
5. [Monte Carlo Simulations](#monte-carlo-simulations)
6. [Python Client Examples](#python-client-examples)
7. [Frontend Integration](#frontend-integration)

## Quick Start

### 1. Start the Application

```bash
./start.sh
```

The API will be available at `http://localhost:8000`

### 2. Access API Documentation

Open your browser to: `http://localhost:8000/docs`

You'll see all available endpoints including the new advanced analytics endpoints under `/api/analytics/`.

### 3. Get Your Account ID

First, you need to know your account ID. You can get it from:

```bash
curl http://localhost:8000/api/account/summary
```

Or check the latest account snapshot in your database.

---

## Portfolio Optimization

### Markowitz Mean-Variance Optimization

Optimizes portfolio weights to maximize Sharpe ratio or minimize variance.

**Endpoint:** `POST /api/analytics/optimization/markowitz`

**Parameters:**
- `account_id` (optional): Your IBKR account ID (auto-detected if not provided)
- `risk_free_rate` (default: 0.0): Risk-free rate for Sharpe calculation
- `target_return` (optional): Target return - if provided, minimizes variance for this return
- `max_weight` (default: 1.0): Maximum weight per asset
- `min_weight` (default: 0.0): Minimum weight per asset
- `long_only` (default: true): If true, no short positions allowed
- `start_date` (optional): Start date for returns calculation
- `end_date` (optional): End date for returns calculation

**Example Request (curl):**

```bash
curl -X POST "http://localhost:8000/api/analytics/optimization/markowitz?account_id=U1234567&risk_free_rate=0.02&long_only=true"
```

**Example Request (Python):**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analytics/optimization/markowitz",
    params={
        "account_id": "U1234567",
        "risk_free_rate": 0.02,
        "max_weight": 0.20,  # Max 20% per asset
        "long_only": True,
    }
)

result = response.json()
print(f"Expected Return: {result['expected_return']:.2%}")
print(f"Expected Volatility: {result['expected_volatility']:.2%}")
print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
print("\nOptimal Weights:")
for weight in result['weights']:
    print(f"  {weight['asset']}: {weight['weight']:.2%}")
```

**Example Response:**

```json
{
  "method": "markowitz",
  "weights": [
    {"asset": "AAPL", "weight": 0.25},
    {"asset": "MSFT", "weight": 0.20},
    {"asset": "GOOGL", "weight": 0.15}
  ],
  "expected_return": 0.12,
  "expected_volatility": 0.18,
  "sharpe_ratio": 0.67,
  "constraints_satisfied": true,
  "optimization_status": "optimal"
}
```

### Black-Litterman Optimization

Combines market equilibrium with investor views.

**Endpoint:** `POST /api/analytics/optimization/black-litterman`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `risk_aversion` (default: 3.0): Risk aversion parameter (typically 2-4)
- `risk_free_rate` (default: 0.0): Risk-free rate
- `tau` (default: 0.05): Uncertainty scaling factor
- `views` (optional): JSON string of `{"ASSET": expected_return}` views
- `view_confidences` (optional): JSON string of `{"ASSET": confidence}` (0-1)
- `start_date` (optional): Start date for returns calculation
- `end_date` (optional): End date for returns calculation

**Example Request (Python):**

```python
import requests
import json

views = {
    "AAPL": 0.15,  # Expect 15% return
    "MSFT": 0.12   # Expect 12% return
}

confidences = {
    "AAPL": 0.8,   # 80% confident
    "MSFT": 0.6    # 60% confident
}

response = requests.post(
    "http://localhost:8000/api/analytics/optimization/black-litterman",
    params={
        "account_id": "U1234567",
        "risk_aversion": 3.0,
        "risk_free_rate": 0.02,
        "tau": 0.05,
        "views": json.dumps(views),
        "view_confidences": json.dumps(confidences),
    }
)

result = response.json()
print(f"Optimal Weights: {result['weights']}")
```

### Risk Parity Optimization

Equal risk contribution from each asset.

**Endpoint:** `POST /api/analytics/optimization/risk-parity`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `target_risk` (optional): Target portfolio volatility
- `start_date` (optional): Start date for returns calculation
- `end_date` (optional): End date for returns calculation

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/analytics/optimization/risk-parity?account_id=U1234567&target_risk=0.15"
```

---

## Factor Analysis

### Fama-French Factor Analysis

Decomposes portfolio returns into market, value (HML), size (SMB), and momentum (UMD) factors.

**Endpoint:** `GET /api/analytics/factor-analysis/fama-french`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `start_date` (optional): Start date for analysis
- `end_date` (optional): End date for analysis

**Example Request (Python):**

```python
import requests
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

response = requests.get(
    "http://localhost:8000/api/analytics/factor-analysis/fama-french",
    params={
        "account_id": "U1234567",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
)

result = response.json()

print("Factor Loadings:")
for loading in result['factor_loadings']:
    print(f"  {loading['asset']} - {loading['factor']}: {loading['loading']:.4f}")

print("\nFactor Returns:")
for factor, ret in result['factor_returns'].items():
    print(f"  {factor}: {ret:.4%}")

print("\nR-squared (explained variance):")
for asset, r2 in result['r_squared'].items():
    print(f"  {asset}: {r2:.2%}")
```

**Example Response:**

```json
{
  "factor_loadings": [
    {"asset": "AAPL", "factor": "Market", "loading": 1.2},
    {"asset": "AAPL", "factor": "HML", "loading": 0.3},
    {"asset": "MSFT", "factor": "Market", "loading": 1.1}
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

### Style Analysis

Decomposes portfolio returns into style benchmark exposures.

**Endpoint:** `GET /api/analytics/factor-analysis/style`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `start_date` (optional): Start date for analysis
- `end_date` (optional): End date for analysis
- `constraint_long_only` (default: true): Long-only constraint

**Example Request:**

```bash
curl "http://localhost:8000/api/analytics/factor-analysis/style?account_id=U1234567"
```

**Example Response:**

```json
{
  "style_weights": {
    "Market": 0.75,
    "Growth": 0.15,
    "Value": 0.10
  },
  "r_squared": 0.88,
  "tracking_error": 0.05
}
```

---

## Attribution Analysis

### Factor Attribution

Attributes portfolio returns to factor exposures.

**Endpoint:** `GET /api/analytics/attribution/factor`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `start_date` (optional): Start date for analysis
- `end_date` (optional): End date for analysis

**Example Request (Python):**

```python
import requests

response = requests.get(
    "http://localhost:8000/api/analytics/attribution/factor",
    params={
        "account_id": "U1234567",
    }
)

result = response.json()

print(f"Total Attribution: {result['total_attribution']:.2%}")
print("\nFactor Contributions:")
if result['factor_attribution']:
    for factor, contrib in result['factor_attribution'].items():
        print(f"  {factor}: {contrib:.2%}")
```

**Example Response:**

```json
{
  "total_attribution": 0.12,
  "factor_attribution": {
    "Market": 0.08,
    "HML": 0.02,
    "SMB": 0.01,
    "UMD": 0.01
  },
  "sector_attribution": null,
  "region_attribution": null,
  "security_attribution": null
}
```

---

## Monte Carlo Simulations

### Simple Monte Carlo Simulation

Simulates future portfolio value using geometric Brownian motion.

**Endpoint:** `GET /api/analytics/monte-carlo/simple`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `initial_value` (optional): Starting portfolio value (auto-detected if not provided)
- `n_simulations` (default: 10000): Number of simulation paths
- `n_periods` (default: 252): Number of days to simulate
- `start_date` (optional): Start date for parameter estimation
- `end_date` (optional): End date for parameter estimation
- `random_seed` (optional): Random seed for reproducibility

**Example Request (Python):**

```python
import requests

response = requests.get(
    "http://localhost:8000/api/analytics/monte-carlo/simple",
    params={
        "account_id": "U1234567",
        "initial_value": 100000,
        "n_simulations": 10000,
        "n_periods": 252,  # 1 year
        "random_seed": 42,
    }
)

result = response.json()

print(f"Initial Value: ${result['initial_value']:,.2f}")
print(f"Expected Final Value: ${result['expected_final_value']:,.2f}")
print(f"Probability of Loss: {result['probability_of_loss']:.2%}")
print(f"VaR (95%): ${result['var_95']:,.2f}")
print(f"CVaR (95%): ${result['cvar_95']:,.2f}")
print("\nPercentiles:")
percentiles = result['percentiles']
print(f"  5th: ${percentiles['p5']:,.2f}")
print(f"  25th: ${percentiles['p25']:,.2f}")
print(f"  50th (median): ${percentiles['p50']:,.2f}")
print(f"  75th: ${percentiles['p75']:,.2f}")
print(f"  95th: ${percentiles['p95']:,.2f}")
```

**Example Response:**

```json
{
  "initial_value": 100000.0,
  "expected_final_value": 112000.0,
  "percentiles": {
    "p5": 85000.0,
    "p25": 98000.0,
    "p50": 110000.0,
    "p75": 125000.0,
    "p95": 145000.0
  },
  "probability_of_loss": 0.15,
  "var_95": 15000.0,
  "cvar_95": 18000.0,
  "n_simulations": 10000,
  "n_periods": 252
}
```

### Portfolio Monte Carlo Simulation

Multi-asset portfolio simulation with rebalancing.

**Endpoint:** `GET /api/analytics/monte-carlo/portfolio`

**Parameters:**
- `account_id` (optional): Your IBKR account ID
- `initial_value` (optional): Starting portfolio value
- `n_simulations` (default: 10000): Number of simulation paths
- `n_periods` (default: 252): Number of days to simulate
- `rebalance_frequency` (default: 21): Rebalance every N days (0 = no rebalancing)
- `start_date` (optional): Start date for parameter estimation
- `end_date` (optional): End date for parameter estimation
- `random_seed` (optional): Random seed for reproducibility

**Example Request:**

```bash
curl "http://localhost:8000/api/analytics/monte-carlo/portfolio?account_id=U1234567&n_simulations=10000&rebalance_frequency=21"
```

---

## Python Client Examples

### Complete Example: Portfolio Optimization Workflow

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"
ACCOUNT_ID = "U1234567"

# 1. Get current positions
positions = requests.get(f"{BASE_URL}/positions", params={"account_id": ACCOUNT_ID}).json()
print(f"Current positions: {len(positions)}")

# 2. Run Markowitz optimization
opt_result = requests.post(
    f"{BASE_URL}/analytics/optimization/markowitz",
    params={
        "account_id": ACCOUNT_ID,
        "risk_free_rate": 0.02,
        "max_weight": 0.25,  # Max 25% per asset
        "long_only": True,
    }
).json()

print(f"\nOptimal Portfolio:")
print(f"  Expected Return: {opt_result['expected_return']:.2%}")
print(f"  Expected Volatility: {opt_result['expected_volatility']:.2%}")
print(f"  Sharpe Ratio: {opt_result['sharpe_ratio']:.2f}")
print(f"\n  Recommended Weights:")
for w in opt_result['weights']:
    print(f"    {w['asset']}: {w['weight']:.2%}")

# 3. Run factor analysis
factor_result = requests.get(
    f"{BASE_URL}/analytics/factor-analysis/fama-french",
    params={"account_id": ACCOUNT_ID}
).json()

print(f"\nFactor Analysis:")
print(f"  Factors: {', '.join(factor_result['factor_names'])}")
for asset in set(loading['asset'] for loading in factor_result['factor_loadings']):
    asset_loadings = [l for l in factor_result['factor_loadings'] if l['asset'] == asset]
    print(f"\n  {asset}:")
    for loading in asset_loadings:
        print(f"    {loading['factor']}: {loading['loading']:.4f}")

# 4. Run Monte Carlo simulation
mc_result = requests.get(
    f"{BASE_URL}/analytics/monte-carlo/simple",
    params={
        "account_id": ACCOUNT_ID,
        "n_simulations": 10000,
        "n_periods": 252,
    }
).json()

print(f"\nMonte Carlo Simulation (1 year):")
print(f"  Expected Value: ${mc_result['expected_final_value']:,.2f}")
print(f"  Probability of Loss: {mc_result['probability_of_loss']:.2%}")
print(f"  VaR (95%): ${mc_result['var_95']:,.2f}")
```

### Example: Factor Attribution Analysis

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"
ACCOUNT_ID = "U1234567"

# Get attribution
attribution = requests.get(
    f"{BASE_URL}/analytics/attribution/factor",
    params={
        "account_id": ACCOUNT_ID,
        "start_date": (datetime.now() - timedelta(days=365)).isoformat(),
        "end_date": datetime.now().isoformat(),
    }
).json()

print("Performance Attribution:")
print(f"  Total: {attribution['total_attribution']:.2%}")
if attribution['factor_attribution']:
    print("\n  By Factor:")
    for factor, contrib in sorted(attribution['factor_attribution'].items(), 
                                   key=lambda x: abs(x[1]), reverse=True):
        print(f"    {factor}: {contrib:.2%}")
```

---

## Frontend Integration

### Using in Dash/React Frontend

```python
# In your Dash frontend (frontend/app.py or similar)
import dash
from dash import dcc, html, Input, Output
import requests

# Add a callback for optimization
@app.callback(
    Output('optimization-results', 'children'),
    Input('optimize-button', 'n_clicks'),
    State('account-id', 'value')
)
def run_optimization(n_clicks, account_id):
    if n_clicks is None:
        return ""
    
    try:
        response = requests.post(
            "http://localhost:8000/api/analytics/optimization/markowitz",
            params={"account_id": account_id, "risk_free_rate": 0.02}
        )
        result = response.json()
        
        # Display results
        return html.Div([
            html.H4("Optimal Portfolio"),
            html.P(f"Expected Return: {result['expected_return']:.2%}"),
            html.P(f"Expected Volatility: {result['expected_volatility']:.2%}"),
            html.P(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}"),
            html.Ul([
                html.Li(f"{w['asset']}: {w['weight']:.2%}")
                for w in result['weights']
            ])
        ])
    except Exception as e:
        return html.Div(f"Error: {str(e)}", style={"color": "red"})
```

### JavaScript/React Example

```javascript
// In your React component
async function runOptimization(accountId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/analytics/optimization/markowitz?account_id=${accountId}&risk_free_rate=0.02`,
      { method: 'POST' }
    );
    
    const result = await response.json();
    
    console.log('Optimal Portfolio:', result);
    console.log('Expected Return:', result.expected_return);
    console.log('Sharpe Ratio:', result.sharpe_ratio);
    
    return result;
  } catch (error) {
    console.error('Optimization error:', error);
    throw error;
  }
}
```

---

## Common Use Cases

### 1. Rebalancing Recommendation

```python
# Get current weights vs optimal weights
current_positions = requests.get(f"{BASE_URL}/positions", params={"account_id": ACCOUNT_ID}).json()
optimal_weights = requests.post(f"{BASE_URL}/analytics/optimization/markowitz", 
                                params={"account_id": ACCOUNT_ID}).json()

# Calculate rebalancing trades needed
# (implementation depends on your trade execution system)
```

### 2. Risk Assessment

```python
# Run Monte Carlo to assess downside risk
mc = requests.get(f"{BASE_URL}/analytics/monte-carlo/simple",
                  params={"account_id": ACCOUNT_ID, "n_periods": 252}).json()

if mc['probability_of_loss'] > 0.20:
    print("Warning: High probability of loss!")
if mc['var_95'] > initial_value * 0.10:
    print("Warning: High VaR!")
```

### 3. Factor Exposure Analysis

```python
# Understand what factors drive your returns
factors = requests.get(f"{BASE_URL}/analytics/factor-analysis/fama-french",
                       params={"account_id": ACCOUNT_ID}).json()

# Check if you're overexposed to market risk
market_loadings = [l['loading'] for l in factors['factor_loadings'] if l['factor'] == 'Market']
avg_market_beta = sum(market_loadings) / len(market_loadings)
if avg_market_beta > 1.2:
    print("Warning: High market exposure (beta > 1.2)")
```

---

## Troubleshooting

### "Insufficient data for optimization"

**Solution:** Make sure you have:
1. Historical position data or trade data
2. At least 30-60 days of data for meaningful statistics
3. Multiple positions (optimization needs at least 2 assets)

**Check your data:**
```bash
curl "http://localhost:8000/api/positions?account_id=YOUR_ACCOUNT_ID"
curl "http://localhost:8000/api/trades?account_id=YOUR_ACCOUNT_ID&limit=10"
```

### "account_id is required"

**Solution:** Either:
1. Provide account_id as a query parameter
2. Make sure you have at least one account snapshot in the database
3. The API will auto-detect from the latest snapshot if not provided

### Optimization returns empty weights

**Possible causes:**
1. Not enough historical data
2. All assets have zero or negative expected returns
3. Constraints are too restrictive (e.g., max_weight too low)

**Solution:** Try relaxing constraints or using a longer time period for returns estimation.

---

## Next Steps

1. **Integrate with Frontend**: Add optimization and analytics widgets to your dashboard
2. **Automate Rebalancing**: Use optimization results to trigger rebalancing trades
3. **Risk Monitoring**: Set up alerts based on Monte Carlo VaR/CVaR thresholds
4. **Factor Tilting**: Use factor analysis to adjust portfolio toward desired factor exposures

For more information, see:
- API Documentation: `http://localhost:8000/docs`
- Source code: `portfolio/advanced_analytics.py`
- API routes: `backend/api/advanced_analytics_routes.py`
