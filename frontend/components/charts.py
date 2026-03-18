"""Reusable chart components."""
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc

# Professional lightweight palette for charts
BLUE = "#4da6ff"
RED = "#f87171"
GREEN = "#34d399"
MUTED = "#9094a1"
BG_CARD = "#181b1f"


def create_returns_chart(
    dates: List[str],
    portfolio_returns: List[float],
    benchmark_returns: Optional[List[float]] = None,
    title: str = "Cumulative Returns",
) -> dcc.Graph:
    """Create a cumulative returns chart."""
    fig = go.Figure()

    # Portfolio line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_returns,
            mode="lines",
            name="Portfolio",
            line=dict(color=BLUE, width=2),
            fill="tozeroy",
            fillcolor="rgba(77, 166, 255, 0.1)",
        )
    )

    # Benchmark line (if provided)
    if benchmark_returns and len(benchmark_returns) == len(dates):
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=benchmark_returns,
                mode="lines",
                name="Benchmark",
                line=dict(color=RED, width=2, dash="dash"),
            )
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=title,
        xaxis=dict(
            gridcolor="rgba(42, 46, 53, 0.5)",
            tickfont=dict(color=MUTED),
            titlefont=dict(color=MUTED),
            linecolor="#2a2e35",
            zerolinecolor="#2a2e35",
        ),
        yaxis=dict(
            gridcolor="rgba(42, 46, 53, 0.5)",
            tickfont=dict(color=MUTED),
            titlefont=dict(color=MUTED),
            linecolor="#2a2e35",
            zerolinecolor="#2a2e35",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=MUTED),
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=350,
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def create_heatmap(
    data: pd.DataFrame, title: str = "Heatmap", colorscale: str = "Viridis"
) -> dcc.Graph:
    """Create a heatmap chart."""
    fig = px.imshow(
        data,
        aspect="auto",
        color_continuous_scale=colorscale,
        labels=dict(x="X", y="Y", color="Value"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=title,
        xaxis=dict(tickfont=dict(color=MUTED)),
        yaxis=dict(tickfont=dict(color=MUTED)),
        coloraxis_colorbar=dict(tickfont=dict(color=MUTED)),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def create_correlation_matrix(
    returns_df: pd.DataFrame, title: str = "Correlation Matrix"
) -> dcc.Graph:
    """Create a correlation matrix heatmap."""
    corr_matrix = returns_df.corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale="RdBu",
            zmid=0,
            text=corr_matrix.values,
            texttemplate="%{text:.2f}",
            textfont={"size": 10},
            colorbar=dict(title="Correlation", tickfont=dict(color=MUTED)),
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=title,
        xaxis=dict(tickfont=dict(color=MUTED)),
        yaxis=dict(tickfont=dict(color=MUTED)),
        height=400,
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False})
