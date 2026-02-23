"""PnL chart component."""
from dash import dcc
import plotly.graph_objs as go
from datetime import datetime


def create_pnl_chart(pnl_data):
    """Create PnL chart from data."""
    if not pnl_data:
        from dash import html
        return html.Div([
            html.P("No PnL data available. Please fetch data first:", className="text-muted mb-2"),
            html.P("1. Go to http://localhost:8000/docs", className="text-muted mb-1"),
            html.P("2. Find the /api/fetch-data endpoint", className="text-muted mb-1"),
            html.P("3. Click 'Try it out' and 'Execute'", className="text-muted mb-1"),
            html.P("4. Refresh this page", className="text-muted"),
        ], style={'padding': '20px', 'textAlign': 'center'})
    
    # Parse dates and extract values
    dates = [datetime.fromisoformat(record['date'].replace('Z', '+00:00')) for record in pnl_data]
    dates.reverse()  # Show oldest to newest
    
    total_pnl = [record['total_pnl'] or 0 for record in reversed(pnl_data)]
    realized_pnl = [record['realized_pnl'] or 0 for record in reversed(pnl_data)]
    unrealized_pnl = [record['unrealized_pnl'] or 0 for record in reversed(pnl_data)]
    net_liquidation = [record['net_liquidation'] or 0 for record in reversed(pnl_data)]
    
    # Create traces
    traces = [
        go.Scatter(
            x=dates,
            y=net_liquidation,
            mode='lines',
            name='Net Liquidation',
            line=dict(color='blue', width=2),
        ),
        go.Scatter(
            x=dates,
            y=total_pnl,
            mode='lines',
            name='Total PnL',
            line=dict(color='green', width=2),
            yaxis='y2',
        ),
    ]
    
    layout = go.Layout(
        title='Account Value and PnL Over Time',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Net Liquidation ($)', side='left'),
        yaxis2=dict(title='PnL ($)', overlaying='y', side='right'),
        hovermode='x unified',
        legend=dict(x=0, y=1),
        height=400,
    )
    
    figure = go.Figure(data=traces, layout=layout)
    
    return dcc.Graph(figure=figure)

