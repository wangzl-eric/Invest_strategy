"""
Example notebook demonstrating playground field workflow.

This notebook shows how to:
1. Load data using shared helpers
2. Create visualizations
3. Analyze a specific field topic
4. Document findings

Copy this to your field's notebooks/ directory and customize.
"""

# %% [markdown]
# # Field Study Template
#
# **Field:** [volatility/momentum/carry/macro/correlation/options/fx/crypto/portfolio]
# **Date:** YYYY-MM-DD
# **Hypothesis:** [What are you testing?]

# %% Setup
import sys
sys.path.append('/Users/zelin/Desktop/PA Investment/Invest_strategy')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import shared helpers
from playground.shared.data_helpers import load_market_data, load_fred_data
from playground.shared.viz_helpers import (
    plot_time_series,
    plot_correlation_matrix,
    plot_rolling_correlation,
    plot_distribution,
    plot_drawdown,
    plot_regime_overlay
)

# %% [markdown]
# ## 1. Load Data

# %% Load data
# Example: Load equity and volatility data
spy = load_market_data('SPY')
vix = load_fred_data('VIXCLS')

# Combine into DataFrame
data = pd.DataFrame({
    'SPY': spy,
    'VIX': vix
}).dropna()

print(f"Data range: {data.index[0]} to {data.index[-1]}")
print(f"Observations: {len(data)}")

# %% [markdown]
# ## 2. Exploratory Analysis

# %% Time series plot
fig = plot_time_series(
    data=data,
    columns=['SPY', 'VIX'],
    title='SPY vs VIX',
    normalize=True
)
# fig.savefig('charts/spy_vix_timeseries.png', dpi=300)

# %% Calculate returns
returns = data.pct_change().dropna()
returns.columns = ['SPY_ret', 'VIX_ret']

# %% Distribution analysis
fig = plot_distribution(
    returns['SPY_ret'],
    title='SPY Returns Distribution'
)

# %% [markdown]
# ## 3. Correlation Analysis

# %% Rolling correlation
fig = plot_rolling_correlation(
    data['SPY'],
    data['VIX'],
    window=60,
    title='SPY-VIX 60-Day Rolling Correlation'
)

# %% [markdown]
# ## 4. Regime Analysis (Optional)

# %% Define regimes
regimes = pd.cut(data['VIX'], bins=[0, 15, 25, 100], labels=[0, 1, 2])
regime_labels = {0: 'Low Vol', 1: 'Medium Vol', 2: 'High Vol'}

# %% Plot with regime overlay
fig = plot_regime_overlay(
    data['SPY'],
    regimes,
    regime_labels=regime_labels,
    title='SPY with Volatility Regimes'
)

# %% [markdown]
# ## 5. Key Findings
#
# Document your observations here:
# - Finding 1
# - Finding 2
# - Finding 3

# %% [markdown]
# ## 6. Next Steps
#
# - [ ] Follow-up analysis 1
# - [ ] Follow-up analysis 2
# - [ ] Consider for formal research?
