"""Performance metrics component."""
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go
from datetime import datetime


def create_performance_metrics(performance_data):
    """Create performance metrics display."""
    if not performance_data:
        return dbc.Alert("No performance data available", color="warning")
    
    # Get latest metrics
    latest = performance_data[0] if performance_data else {}
    
    # Metrics cards
    metrics_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Sharpe Ratio", className="card-title"),
                    html.H3(f"{latest.get('sharpe_ratio', 0):.2f}", className="text-primary"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Sortino Ratio", className="card-title"),
                    html.H3(f"{latest.get('sortino_ratio', 0):.2f}", className="text-info"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Max Drawdown", className="card-title"),
                    html.H3(f"{latest.get('max_drawdown', 0)*100:.2f}%", className="text-danger"),
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Win Rate", className="card-title"),
                    html.H3(f"{latest.get('win_rate', 0)*100:.1f}%", className="text-success"),
                ])
            ])
        ], width=3),
    ], className="mb-4")
    
    # Returns chart
    dates = [datetime.fromisoformat(record['date'].replace('Z', '+00:00')) for record in performance_data]
    dates.reverse()
    
    cumulative_returns = [record.get('cumulative_return', 0) * 100 for record in reversed(performance_data)]
    daily_returns = [record.get('daily_return', 0) * 100 for record in reversed(performance_data)]
    
    returns_chart = dcc.Graph(
        figure={
            'data': [
                go.Scatter(
                    x=dates,
                    y=cumulative_returns,
                    mode='lines',
                    name='Cumulative Return (%)',
                    line=dict(color='blue', width=2),
                ),
            ],
            'layout': go.Layout(
                title='Cumulative Returns Over Time',
                xaxis=dict(title='Date'),
                yaxis=dict(title='Return (%)'),
                height=400,
            )
        }
    )
    
    return html.Div([
        metrics_cards,
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        returns_chart,
                    ])
                ])
            ])
        ])
    ])

