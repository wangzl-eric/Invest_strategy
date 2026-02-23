"""Export functionality for reports and data."""
import io
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from backend.database import get_db_context
from backend.models import Trade, Position, PnLHistory, PerformanceMetric
from backend.data_processor import DataProcessor

logger = logging.getLogger(__name__)


def export_trades_excel(
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bytes:
    """Export trades to Excel format.
    
    Args:
        account_id: Optional account ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        Excel file as bytes
    """
    with get_db_context() as db:
        query = db.query(Trade).order_by(Trade.exec_time.desc())
        
        if account_id:
            query = query.filter(Trade.account_id == account_id)
        if start_date:
            query = query.filter(Trade.exec_time >= start_date)
        if end_date:
            query = query.filter(Trade.exec_time <= end_date)
        
        trades = query.all()
    
    if not trades:
        raise HTTPException(status_code=404, detail="No trades found")
    
    # Convert to DataFrame
    data = []
    for trade in trades:
        data.append({
            "Exec Time": trade.exec_time.isoformat() if trade.exec_time else None,
            "Symbol": trade.symbol,
            "Side": trade.side,
            "Shares": trade.shares,
            "Price": trade.price,
            "Avg Price": trade.avg_price,
            "Commission": trade.commission or 0.0,
            "Taxes": trade.taxes or 0.0,
            "Proceeds": trade.proceeds,
            "Cost Basis": trade.cost_basis,
            "Realized PnL": trade.realized_pnl,
            "Currency": trade.currency,
            "Exchange": trade.exchange,
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Trades', index=False)
    
    output.seek(0)
    return output.getvalue()


def export_performance_excel(
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bytes:
    """Export performance metrics to Excel format.
    
    Args:
        account_id: Optional account ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        Excel file as bytes
    """
    with get_db_context() as db:
        query = db.query(PerformanceMetric).order_by(PerformanceMetric.date.desc())
        
        if account_id:
            query = query.filter(PerformanceMetric.account_id == account_id)
        if start_date:
            query = query.filter(PerformanceMetric.date >= start_date)
        if end_date:
            query = query.filter(PerformanceMetric.date <= end_date)
        
        metrics = query.all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No performance metrics found")
    
    # Convert to DataFrame
    data = []
    for metric in metrics:
        data.append({
            "Date": metric.date.isoformat() if metric.date else None,
            "Daily Return": metric.daily_return,
            "Cumulative Return": metric.cumulative_return,
            "Sharpe Ratio": metric.sharpe_ratio,
            "Sortino Ratio": metric.sortino_ratio,
            "Max Drawdown": metric.max_drawdown,
            "Total Trades": metric.total_trades,
            "Winning Trades": metric.winning_trades,
            "Losing Trades": metric.losing_trades,
            "Win Rate": metric.win_rate,
            "Avg Win": metric.avg_win,
            "Avg Loss": metric.avg_loss,
            "Profit Factor": metric.profit_factor,
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Performance', index=False)
    
    output.seek(0)
    return output.getvalue()


def export_pnl_excel(
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bytes:
    """Export PnL history to Excel format.
    
    Args:
        account_id: Optional account ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        Excel file as bytes
    """
    processor = DataProcessor()
    df = processor.get_pnl_history(account_id, start_date, end_date)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No PnL history found")
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='PnL History', index=False)
    
    output.seek(0)
    return output.getvalue()


def export_combined_report(
    account_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> bytes:
    """Export combined report with multiple sheets (trades, performance, PnL).
    
    Args:
        account_id: Optional account ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        Excel file as bytes with multiple sheets
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Trades sheet
        try:
            trades_data = export_trades_excel(account_id, start_date, end_date)
            trades_df = pd.read_excel(io.BytesIO(trades_data))
            trades_df.to_excel(writer, sheet_name='Trades', index=False)
        except HTTPException as e:
            if e.status_code != 404:
                raise
            # Create empty sheet if no trades
            pd.DataFrame().to_excel(writer, sheet_name='Trades', index=False)
        
        # Performance sheet
        try:
            perf_data = export_performance_excel(account_id, start_date, end_date)
            perf_df = pd.read_excel(io.BytesIO(perf_data))
            perf_df.to_excel(writer, sheet_name='Performance', index=False)
        except HTTPException as e:
            if e.status_code != 404:
                raise
            pd.DataFrame().to_excel(writer, sheet_name='Performance', index=False)
        
        # PnL History sheet
        try:
            pnl_data = export_pnl_excel(account_id, start_date, end_date)
            pnl_df = pd.read_excel(io.BytesIO(pnl_data))
            pnl_df.to_excel(writer, sheet_name='PnL History', index=False)
        except HTTPException as e:
            if e.status_code != 404:
                raise
            pd.DataFrame().to_excel(writer, sheet_name='PnL History', index=False)
    
    output.seek(0)
    return output.getvalue()


def get_export_filename(export_type: str, account_id: Optional[str] = None) -> str:
    """Generate filename for export.
    
    Args:
        export_type: Type of export (trades, performance, pnl, report)
        account_id: Optional account ID
    
    Returns:
        Filename string
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    account_suffix = f"_{account_id}" if account_id else ""
    return f"{export_type}{account_suffix}_{timestamp}.xlsx"
