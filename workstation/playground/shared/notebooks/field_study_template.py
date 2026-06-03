"""
Example notebook demonstrating playground field workflow.

This notebook shows how to:
1. Refresh local data when needed
2. Load data using shared helpers
3. Create visualizations
4. Analyze a specific field topic
5. Document findings

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
from datetime import datetime
from pathlib import Path

import pandas as pd


def _find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "workstation").exists() and (candidate / "apps").exists():
            return candidate
    raise RuntimeError("Could not find repo root. Start Jupyter from the repository.")


PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import shared helpers
from playground.data_helpers import (  # noqa: E402
    calculate_volatility,
    get_prices,
    refresh_prices,
)
from playground.shared.viz_helpers import (  # noqa: E402
    plot_distribution,
    plot_regime_overlay,
    plot_rolling_correlation,
    plot_time_series,
)

START_DATE = "2020-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
PRICE_DATASET = "equities"  # Use "ibkr_equities" if you want IBKR-backed local data
REFRESH_LOCAL_CACHE = False

# %% [markdown]
# ## 1. Load Data
#
# The playground now follows the same local-first flow as the main research stack:
# 1. Optionally refresh the local database from the source API
# 2. Read analysis data from the local cache through one shared helper layer

# %% Optional refresh job
# Turn this on when the local cache is empty or stale.
if REFRESH_LOCAL_CACHE:
    refresh_prices(
        ["SPY", "TLT"],
        start=START_DATE,
        end=END_DATE,
        dataset=PRICE_DATASET,
    )

# %% Load local data
spy = get_prices("SPY", start=START_DATE, end=END_DATE, dataset=PRICE_DATASET)
tlt = get_prices("TLT", start=START_DATE, end=END_DATE, dataset=PRICE_DATASET)

# Combine into DataFrame
data = pd.DataFrame(
    {
        "SPY": spy.set_index("date")["close"],
        "TLT": tlt.set_index("date")["close"],
    }
).dropna()

if data.empty:
    raise RuntimeError(
        "No local price data found for SPY/TLT. "
        "Set REFRESH_LOCAL_CACHE = True to refresh the local cache, "
        "or change PRICE_DATASET to a dataset with cached data."
    )

print(f"Data range: {data.index[0]} to {data.index[-1]}")
print(f"Observations: {len(data)}")

# %% [markdown]
# ## 2. Exploratory Analysis

# %% Time series plot
fig = plot_time_series(
    data=data, columns=["SPY", "TLT"], title="SPY vs TLT", normalize=True
)
# fig.savefig('charts/spy_tlt_timeseries.png', dpi=300)

# %% Calculate returns
returns = data.pct_change().dropna()
returns.columns = ["SPY_ret", "TLT_ret"]

# %% Distribution analysis
fig = plot_distribution(returns["SPY_ret"], title="SPY Returns Distribution")

# %% [markdown]
# ## 3. Correlation Analysis

# %% Rolling correlation
fig = plot_rolling_correlation(
    data["SPY"], data["TLT"], window=60, title="SPY-TLT 60-Day Rolling Correlation"
)

# %% [markdown]
# ## 4. Regime Analysis (Optional)

# %% Define realized-volatility regimes from local price data
realized_vol = calculate_volatility(returns["SPY_ret"], window=20).dropna()
regime_names = ["Low Vol", "Mid Vol", "High Vol"]
if realized_vol.nunique() < 2:
    regimes = pd.Series(0, index=realized_vol.index, dtype="int64")
else:
    regime_count = min(3, realized_vol.nunique())
    regimes = pd.qcut(
        realized_vol.rank(method="first"),
        q=regime_count,
        labels=list(range(regime_count)),
    )
regime_labels = {
    idx: regime_names[idx] for idx in sorted(pd.unique(regimes.astype(int)))
}
aligned_spy = data["SPY"].reindex(realized_vol.index)

# %% Plot with regime overlay
fig = plot_regime_overlay(
    aligned_spy,
    regimes,
    regime_labels=regime_labels,
    title="SPY with Realized-Volatility Regimes",
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
