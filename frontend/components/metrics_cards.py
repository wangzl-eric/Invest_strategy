"""Reusable metrics cards component."""
from dash import html
import dash_bootstrap_components as dbc


def create_metrics_row(metrics: list, cols_per_row: int = 4):
    """
    Create a responsive row of metric cards.
    
    Args:
        metrics: List of dicts with keys: label, value, value_class, prefix, suffix
        cols_per_row: Number of columns per row (default 4)
    """
    rows = []
    for i in range(0, len(metrics), cols_per_row):
        row_metrics = metrics[i:i + cols_per_row]
        cols = []
        
        for metric in row_metrics:
            col_width = 12 // cols_per_row
            cols.append(
                dbc.Col([
                    create_metric_card(
                        metric.get('label', ''),
                        metric.get('value', 'N/A'),
                        metric.get('value_class', 'neutral'),
                        metric.get('prefix', ''),
                        metric.get('suffix', '')
                    )
                ], xs=12, sm=6, md=col_width)
            )
        
        rows.append(dbc.Row(cols, className="mb-3"))
    
    return html.Div(rows)


def create_metric_card(label: str, value: str, value_class: str = "neutral", prefix: str = "", suffix: str = ""):
    """Create a styled metric card."""
    return html.Div([
        html.P(label, className="metric-label"),
        html.P(f"{prefix}{value}{suffix}", className=f"metric-value {value_class}"),
    ], className="metric-card")
