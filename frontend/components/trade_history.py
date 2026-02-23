"""Trade history table component."""
from dash import dash_table
import pandas as pd


def create_trade_history(trades_data):
    """Create trade history table from data."""
    if not trades_data:
        return dash_table.DataTable(
            data=[],
            columns=[],
            style_cell={'textAlign': 'left'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        )
    
    # Convert to DataFrame
    df = pd.DataFrame(trades_data)
    
    # Format columns
    columns = [
        {'name': 'Time', 'id': 'exec_time'},
        {'name': 'Symbol', 'id': 'symbol'},
        {'name': 'Side', 'id': 'side'},
        {'name': 'Shares', 'id': 'shares', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Price', 'id': 'price', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Avg Price', 'id': 'avg_price', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Commission', 'id': 'commission', 'type': 'numeric', 'format': {'specifier': '.2f'}},
    ]
    
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
                'if': {'filter_query': '{side} = BUY'},
                'backgroundColor': 'rgba(0, 255, 0, 0.1)',
            },
            {
                'if': {'filter_query': '{side} = SELL'},
                'backgroundColor': 'rgba(255, 0, 0, 0.1)',
            },
        ],
        sort_action='native',
        filter_action='native',
        page_action='native',
        page_size=20,
    )

