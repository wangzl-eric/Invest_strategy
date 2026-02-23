"""Positions table component."""
from dash import dash_table
import pandas as pd


def create_positions_table(positions_data):
    """Create positions table from data."""
    if not positions_data:
        return dash_table.DataTable(
            data=[],
            columns=[],
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(positions_data)
    
    # Format columns
    columns = [
        {'name': 'Symbol', 'id': 'symbol'},
        {'name': 'Quantity', 'id': 'quantity', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Avg Cost', 'id': 'avg_cost', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Market Price', 'id': 'market_price', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Market Value', 'id': 'market_value', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Unrealized PnL', 'id': 'unrealized_pnl', 'type': 'numeric', 'format': {'specifier': '.2f'}},
    ]
    
    # Style cells based on PnL
    def style_cell(value, column):
        if column == 'unrealized_pnl' and value is not None:
            if value > 0:
                return {'color': 'green', 'fontWeight': 'bold'}
            elif value < 0:
                return {'color': 'red', 'fontWeight': 'bold'}
        return {}
    
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=columns,
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{unrealized_pnl} > 0'},
                'backgroundColor': 'rgba(0, 255, 0, 0.1)',
            },
            {
                'if': {'filter_query': '{unrealized_pnl} < 0'},
                'backgroundColor': 'rgba(255, 0, 0, 0.1)',
            },
        ],
        sort_action='native',
        filter_action='native',
        page_action='native',
        page_size=20,
    )

