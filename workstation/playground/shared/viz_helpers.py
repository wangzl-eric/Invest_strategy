"""
Visualization helpers for playground studies.

Reusable plotting functions and chart templates used across all fields.
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set default style
sns.set_style("darkgrid")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10


def plot_time_series(
    data: pd.DataFrame,
    columns: List[str],
    title: str = "Time Series",
    ylabel: str = "Value",
    normalize: bool = False,
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Plot multiple time series on the same chart.

    Args:
        data: DataFrame with datetime index
        columns: List of column names to plot
        title: Chart title
        ylabel: Y-axis label
        normalize: If True, normalize to 100 at start
        figsize: Figure size tuple

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    for col in columns:
        series = data[col].dropna()
        if normalize:
            series = (series / series.iloc[0]) * 100
        ax.plot(series.index, series.values, label=col, linewidth=2)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_correlation_matrix(
    data: pd.DataFrame,
    title: str = "Correlation Matrix",
    figsize: Tuple[int, int] = (12, 10),
    annot: bool = True,
) -> plt.Figure:
    """
    Plot correlation matrix heatmap.

    Args:
        data: DataFrame with numeric columns
        title: Chart title
        figsize: Figure size tuple
        annot: If True, show correlation values

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    corr = data.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    sns.heatmap(
        corr,
        mask=mask,
        annot=annot,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    return fig


def plot_rolling_correlation(
    series1: pd.Series,
    series2: pd.Series,
    window: int = 60,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Plot rolling correlation between two series.

    Args:
        series1: First time series
        series2: Second time series
        window: Rolling window size (days)
        title: Chart title (auto-generated if None)
        figsize: Figure size tuple

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    rolling_corr = series1.rolling(window).corr(series2)

    ax.plot(rolling_corr.index, rolling_corr.values, linewidth=2, color="steelblue")
    ax.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.fill_between(rolling_corr.index, 0, rolling_corr.values, alpha=0.3)

    if title is None:
        title = f"{window}-Day Rolling Correlation: {series1.name} vs {series2.name}"

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("Correlation", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylim(-1, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_distribution(
    data: pd.Series,
    title: Optional[str] = None,
    bins: int = 50,
    figsize: Tuple[int, int] = (14, 6),
) -> plt.Figure:
    """
    Plot distribution with histogram and KDE.

    Args:
        data: Series to plot
        title: Chart title (auto-generated if None)
        bins: Number of histogram bins
        figsize: Figure size tuple

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Histogram with KDE
    ax1.hist(
        data.dropna(),
        bins=bins,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
        density=True,
    )
    data.dropna().plot.kde(ax=ax1, linewidth=2, color="darkred")
    ax1.axvline(
        data.mean(),
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {data.mean():.3f}",
    )
    ax1.axvline(
        data.median(),
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Median: {data.median():.3f}",
    )

    if title is None:
        title = f"Distribution: {data.name}"

    ax1.set_title(title, fontsize=12, fontweight="bold")
    ax1.set_xlabel("Value", fontsize=10)
    ax1.set_ylabel("Density", fontsize=10)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Q-Q plot
    from scipy import stats

    stats.probplot(data.dropna(), dist="norm", plot=ax2)
    ax2.set_title("Q-Q Plot (Normal)", fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_drawdown(
    prices: pd.Series, title: Optional[str] = None, figsize: Tuple[int, int] = (14, 10)
) -> plt.Figure:
    """
    Plot price series with drawdown chart.

    Args:
        prices: Price series
        title: Chart title (auto-generated if None)
        figsize: Figure size tuple

    Returns:
        matplotlib Figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # Price chart
    cummax = prices.cummax()
    ax1.plot(prices.index, prices.values, linewidth=2, label="Price", color="steelblue")
    ax1.plot(
        cummax.index,
        cummax.values,
        linewidth=1,
        linestyle="--",
        label="Peak",
        color="darkred",
        alpha=0.7,
    )

    if title is None:
        title = f"Price & Drawdown: {prices.name}"

    ax1.set_title(title, fontsize=14, fontweight="bold")
    ax1.set_ylabel("Price", fontsize=12)
    ax1.legend(loc="best")
    ax1.grid(True, alpha=0.3)

    # Drawdown chart
    drawdown = (prices / cummax - 1) * 100
    ax2.fill_between(drawdown.index, 0, drawdown.values, color="red", alpha=0.3)
    ax2.plot(drawdown.index, drawdown.values, linewidth=2, color="darkred")

    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()
    ax2.axhline(y=max_dd, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax2.text(
        max_dd_date,
        max_dd,
        f"Max DD: {max_dd:.2f}%",
        fontsize=10,
        ha="center",
        va="top",
    )

    ax2.set_ylabel("Drawdown (%)", fontsize=12)
    ax2.set_xlabel("Date", fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_regime_overlay(
    prices: pd.Series,
    regime: pd.Series,
    regime_labels: Optional[dict] = None,
    title: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Plot price series with regime background shading.

    Args:
        prices: Price series
        regime: Regime indicator (integer labels)
        regime_labels: Dict mapping regime values to names
        title: Chart title (auto-generated if None)
        figsize: Figure size tuple

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot prices
    ax.plot(
        prices.index,
        prices.values,
        linewidth=2,
        color="black",
        label="Price",
        zorder=10,
    )

    # Shade regimes
    colors = ["lightblue", "lightcoral", "lightgreen", "lightyellow"]
    unique_regimes = sorted(regime.unique())

    for i, reg in enumerate(unique_regimes):
        mask = regime == reg
        color = colors[i % len(colors)]
        label = (
            regime_labels.get(reg, f"Regime {reg}")
            if regime_labels
            else f"Regime {reg}"
        )

        # Find continuous segments
        segments = []
        start = None
        for idx, val in mask.items():
            if val and start is None:
                start = idx
            elif not val and start is not None:
                segments.append((start, idx))
                start = None
        if start is not None:
            segments.append((start, mask.index[-1]))

        # Shade segments
        for seg_start, seg_end in segments:
            ax.axvspan(
                seg_start,
                seg_end,
                alpha=0.3,
                color=color,
                label=label if segments.index((seg_start, seg_end)) == 0 else "",
            )

    if title is None:
        title = f"Price with Regime Overlay: {prices.name}"

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("Price", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)

    # Remove duplicate labels
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="best")

    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def save_figure(fig: plt.Figure, filepath: str, dpi: int = 300):
    """
    Save figure to file.

    Args:
        fig: matplotlib Figure object
        filepath: Output file path
        dpi: Resolution (dots per inch)
    """
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
    print(f"Figure saved to: {filepath}")
