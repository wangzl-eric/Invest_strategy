"""Reusable chart components."""
from dash import dcc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from typing import Optional, List, Dict


def create_returns_chart(
    dates: List[str],
    portfolio_returns: List[float],
    benchmark_returns: Optional[List[float]] = None,
    title: str = "Cumulative Returns"
) -> dcc.Graph:
    """Create a cumulative returns chart."""
    fig = go.Figure()
    
    # Portfolio line
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_returns,
        mode='lines',
        name='Portfolio',
        line=dict(color='#58a6ff', width=2),
        fill='tozeroy',
        fillcolor='rgba(88, 166, 255, 0.1)',
    ))
    
    # Benchmark line (if provided)
    if benchmark_returns and len(benchmark_returns) == len(dates):
        fig.add_trace(go.Scatter(
            x=dates,
            y=benchmark_returns,
            mode='lines',
            name='Benchmark',
            line=dict(color='#f85149', width=2, dash='dash'),
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title,
        xaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
        ),
        yaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            ticksuffix='%',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#c9d1d9'),
        ),
        margin=dict(t=40, b=40, l=60, r=20),
        height=350,
        hovermode='x unified',
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_heatmap(
    data: pd.DataFrame,
    title: str = "Heatmap",
    colorscale: str = "Viridis"
) -> dcc.Graph:
    """Create a heatmap chart."""
    fig = px.imshow(
        data,
        aspect="auto",
        color_continuous_scale=colorscale,
        labels=dict(x="X", y="Y", color="Value")
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title,
        xaxis=dict(tickfont=dict(color='#8b949e')),
        yaxis=dict(tickfont=dict(color='#8b949e')),
        coloraxis_colorbar=dict(tickfont=dict(color='#8b949e')),
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_correlation_matrix(
    returns_df: pd.DataFrame,
    title: str = "Correlation Matrix"
) -> dcc.Graph:
    """Create a correlation matrix heatmap."""
    corr_matrix = returns_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation", tickfont=dict(color='#8b949e')),
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=title,
        xaxis=dict(tickfont=dict(color='#8b949e')),
        yaxis=dict(tickfont=dict(color='#8b949e')),
        height=400,
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})
