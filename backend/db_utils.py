"""
Database Utilities for IBKR Analytics

This module provides easy-to-use functions for:
- Importing trades from Flex Query reports into the database
- Querying historical P&L data
- Managing trade records
- Future: Market data storage

Usage:
    from backend.db_utils import (
        import_trades_from_flex,
        get_trades_df,
        get_daily_pnl,
        get_trade_summary,
        query_trades
    )
    
    # Import trades from Flex Query files
    stats = import_trades_from_flex("data/flex_reports")
    
    # Query trades as DataFrame
    trades = get_trades_df(symbol="IAU", start_date="2025-01-01")
    
    # Get P&L summary
    pnl = get_daily_pnl(currency="USD")
"""
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import pandas as pd
import uuid

from sqlalchemy import func, desc, and_, or_, text
from sqlalchemy.orm import Session

from backend.database import get_db_context, init_db, engine
from backend.models import Trade, PnLHistory, Position, AccountSnapshot, PerformanceMetric, Base
from backend.flex_parser import FlexParser, load_all_flex_reports

logger = logging.getLogger(__name__)

# Default FX rate for USD to HKD (update as needed)
DEFAULT_USD_HKD_RATE = 7.78


# =============================================================================
# Import from FlexQueryResult (Direct from API)
# =============================================================================

def import_trades_from_flex_result(
    result,  # FlexQueryResult object
    base_currency: str = "HKD",
    default_fx_rate: float = DEFAULT_USD_HKD_RATE
) -> Dict[str, Any]:
    """
    Import trades directly from a FlexQueryResult object into the database.
    This is called automatically when fetching Flex Query data via the API.
    
    Args:
        result: FlexQueryResult object from FlexQueryClient
        base_currency: Base currency for the account (default: HKD)
        default_fx_rate: Default USD to base currency rate
        
    Returns:
        Dict with import statistics
    """
    if not result.trades:
        return {"status": "no_trades", "imported": 0, "skipped": 0, "source": "flex_api"}
    
    imported = 0
    skipped = 0
    errors = []
    
    with get_db_context() as db:
        for trade in result.trades:
            try:
                # Get exec_id from the trade object
                exec_id = trade.exec_id or trade.trade_id
                if not exec_id:
                    exec_id = f"flex_{uuid.uuid4().hex[:12]}"
                
                # Check if trade already exists
                existing = db.query(Trade).filter(Trade.exec_id == exec_id).first()
                if existing:
                    skipped += 1
                    continue
                
                # Get currency and FX rate
                currency = trade.currency or 'USD'
                # Use FX rates from result if available
                fx_rate = result.fx_rates.get(currency, default_fx_rate if currency == 'USD' else 1.0)
                realized_pnl = trade.realized_pnl or 0.0
                
                # Calculate P&L in base currency
                if currency == 'USD':
                    realized_pnl_base = realized_pnl * fx_rate
                elif currency == base_currency:
                    realized_pnl_base = realized_pnl
                else:
                    realized_pnl_base = realized_pnl
                
                # Create trade record
                db_trade = Trade(
                    account_id=trade.account_id or result.account_id or 'Unknown',
                    exec_id=exec_id,
                    exec_time=trade.trade_date or datetime.now(),
                    symbol=trade.symbol or '',
                    sec_type=trade.sec_type or 'STK',
                    currency=currency,
                    exchange=trade.exchange or None,
                    side=trade.side or '',
                    shares=abs(trade.quantity or 0),
                    price=trade.price or 0.0,
                    proceeds=trade.proceeds or 0.0,
                    commission=trade.commission or 0.0,
                    taxes=trade.tax or 0.0,
                    cost_basis=trade.cost_basis or 0.0,
                    realized_pnl=realized_pnl,
                    realized_pnl_base=realized_pnl_base,
                    mtm_pnl=0.0,  # Not available in FlexTrade
                    fx_rate_to_base=fx_rate,
                    base_currency=base_currency or result.base_currency or "HKD",
                    underlying=trade.underlying_symbol or None,
                    strike=None,  # Parse from trade if needed
                    expiry=None,
                    put_call=None,
                    multiplier=trade.multiplier or 1.0,
                    order_type=trade.order_type or None,
                    trade_id=trade.trade_id or None,
                )
                
                db.add(db_trade)
                imported += 1
                
            except Exception as e:
                errors.append(f"Error importing trade {trade.symbol}: {e}")
                logger.warning(f"Error importing trade: {e}")
                continue
        
        db.commit()
    
    logger.info(f"Imported {imported} trades, skipped {skipped} duplicates")
    
    return {
        "status": "success",
        "imported": imported,
        "skipped": skipped,
        "total_in_result": len(result.trades),
        "source": "flex_api",
        "errors": errors[:5] if errors else None,
    }


def import_all_flex_data(
    result,  # FlexQueryResult object
    base_currency: str = "HKD",
    default_fx_rate: float = DEFAULT_USD_HKD_RATE
) -> Dict[str, Any]:
    """
    Import ALL data from a FlexQueryResult into the database:
    - Trades
    - Positions
    - PnL History
    - Account Snapshots (if available)
    
    This function handles deduplication for all data types.
    
    Args:
        result: FlexQueryResult object from FlexQueryClient
        base_currency: Base currency for the account (default: HKD)
        default_fx_rate: Default USD to base currency rate
        
    Returns:
        Dict with comprehensive import statistics
    """
    stats = {
        "trades": {"imported": 0, "skipped": 0},
        "positions": {"imported": 0, "skipped": 0},
        "pnl": {"imported": 0, "skipped": 0},
        "account_snapshots": {"imported": 0, "skipped": 0},
    }
    
    account_id = result.account_id or 'Unknown'
    
    # Import trades
    if result.trades:
        trade_stats = import_trades_from_flex_result(result, base_currency, default_fx_rate)
        stats["trades"] = {
            "imported": trade_stats.get("imported", 0),
            "skipped": trade_stats.get("skipped", 0),
        }
    
    # Import positions
    if result.positions:
        with get_db_context() as db:
            for pos in result.positions:
                try:
                    # Check if position already exists (by account_id, symbol, and date)
                    pos_date = result.to_date.date() if result.to_date else datetime.now().date()
                    existing = db.query(Position).filter(
                        Position.account_id == (pos.account_id or account_id),
                        Position.symbol == (pos.symbol or ''),
                        func.date(Position.timestamp) == pos_date
                    ).first()
                    
                    if existing:
                        stats["positions"]["skipped"] += 1
                        continue
                    
                    # Create position record
                    db_position = Position(
                        account_id=pos.account_id or account_id,
                        symbol=pos.symbol or '',
                        sec_type=pos.sec_type or 'STK',
                        currency=pos.currency or 'USD',
                        quantity=pos.quantity or 0.0,
                        avg_cost=pos.avg_cost or 0.0,
                        market_price=pos.market_price or 0.0,
                        market_value=pos.market_value or 0.0,
                        unrealized_pnl=pos.unrealized_pnl or 0.0,
                        timestamp=result.to_date or datetime.now(),
                    )
                    db.add(db_position)
                    stats["positions"]["imported"] += 1
                    
                except Exception as e:
                    logger.warning(f"Error importing position {pos.symbol}: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"Imported {stats['positions']['imported']} positions, skipped {stats['positions']['skipped']} duplicates")
    
    # Import PnL History
    pnl_imported = False
    if result.net_liquidation is not None and result.to_date:
        with get_db_context() as db:
            try:
                # Check if PnL record already exists for this date
                pnl_date = result.to_date.replace(hour=0, minute=0, second=0, microsecond=0)
                existing = db.query(PnLHistory).filter(
                    PnLHistory.account_id == account_id,
                    func.date(PnLHistory.date) == pnl_date.date()
                ).first()
                
                if existing:
                    stats["pnl"]["skipped"] += 1
                else:
                    # Calculate total PnL from trades if available
                    realized_pnl = 0.0
                    if result.trades:
                        realized_pnl = sum(t.realized_pnl or 0.0 for t in result.trades)
                    
                    # Calculate unrealized PnL from positions if available
                    unrealized_pnl = 0.0
                    if result.positions:
                        unrealized_pnl = sum(p.unrealized_pnl or 0.0 for p in result.positions)
                    
                    pnl_record = PnLHistory(
                        account_id=account_id,
                        date=pnl_date,
                        realized_pnl=realized_pnl,
                        unrealized_pnl=unrealized_pnl,
                        total_pnl=realized_pnl + unrealized_pnl,
                        net_liquidation=result.net_liquidation,
                        total_cash=result.total_cash,
                    )
                    db.add(pnl_record)
                    stats["pnl"]["imported"] += 1
                    pnl_imported = True
                    db.commit()
                    
            except Exception as e:
                logger.warning(f"Error importing PnL: {e}")
                db.rollback()
    
    # Calculate and update returns after importing PnL data
    if pnl_imported:
        from backend.flex_importer import calculate_and_update_returns
        with get_db_context() as db:
            try:
                calculate_and_update_returns(account_id, db)
                db.commit()
                logger.info(f"Calculated returns for account {account_id}")
            except Exception as e:
                logger.warning(f"Error calculating returns for account {account_id}: {e}")
    
    # Import Account Snapshot (if we have net liquidation data)
    if result.net_liquidation is not None and result.to_date:
        with get_db_context() as db:
            try:
                snapshot_time = result.to_date
                # Check if snapshot already exists (within same minute)
                # Use a time window approach instead of extract
                time_window_start = snapshot_time.replace(second=0, microsecond=0)
                time_window_end = time_window_start.replace(second=59)
                existing = db.query(AccountSnapshot).filter(
                    AccountSnapshot.account_id == account_id,
                    AccountSnapshot.timestamp >= time_window_start,
                    AccountSnapshot.timestamp <= time_window_end
                ).first()
                
                if existing:
                    stats["account_snapshots"]["skipped"] += 1
                else:
                    snapshot = AccountSnapshot(
                        account_id=account_id,
                        timestamp=snapshot_time,
                        net_liquidation=result.net_liquidation,
                        total_cash=result.total_cash,
                        equity=result.net_liquidation,  # Use net liquidation as equity
                    )
                    db.add(snapshot)
                    stats["account_snapshots"]["imported"] += 1
                    db.commit()
                    
            except Exception as e:
                logger.warning(f"Error importing account snapshot: {e}")
                db.rollback()
    
    total_imported = (
        stats["trades"]["imported"] +
        stats["positions"]["imported"] +
        stats["pnl"]["imported"] +
        stats["account_snapshots"]["imported"]
    )
    total_skipped = (
        stats["trades"]["skipped"] +
        stats["positions"]["skipped"] +
        stats["pnl"]["skipped"] +
        stats["account_snapshots"]["skipped"]
    )
    
    logger.info(
        f"Flex Query import complete: {total_imported} new records, {total_skipped} duplicates skipped"
    )
    
    return {
        "status": "success",
        "account_id": account_id,
        "from_date": result.from_date.isoformat() if result.from_date else None,
        "to_date": result.to_date.isoformat() if result.to_date else None,
        "stats": stats,
        "total_imported": total_imported,
        "total_skipped": total_skipped,
    }


# =============================================================================
# Database Initialization
# =============================================================================

def init_database():
    """Initialize database tables. Run this once to create all tables."""
    init_db()
    print("✓ Database initialized successfully")
    print(f"  Tables: trades, positions, pnl_history, account_snapshots, performance_metrics")


def reset_trades_table():
    """Drop and recreate the trades table (WARNING: deletes all trade data!)."""
    Trade.__table__.drop(engine, checkfirst=True)
    Trade.__table__.create(engine, checkfirst=True)
    print("✓ Trades table reset")

def reset_pnl_history_table():
    """Drop and recreate the pnl_history table (WARNING: deletes all PnL history!)."""
    PnLHistory.__table__.drop(engine, checkfirst=True)
    PnLHistory.__table__.create(engine, checkfirst=True)
    print("✓ PnL history table reset")


# =============================================================================
# Import from Flex Query
# =============================================================================

def import_trades_from_flex(
    data_dir: str = "data/flex_reports",
    base_currency: str = "HKD",
    default_fx_rate: float = DEFAULT_USD_HKD_RATE
) -> Dict[str, Any]:
    """
    Import trades from Flex Query CSV/XML files into the database.
    
    Args:
        data_dir: Directory containing Flex Query files
        base_currency: Base currency for the account (default: HKD)
        default_fx_rate: Default USD to base currency rate
        
    Returns:
        Dict with import statistics
    """
    # Parse all flex query files
    data = load_all_flex_reports(data_dir)
    trades_df = data['trades']
    
    if trades_df.empty:
        return {"status": "no_trades", "imported": 0, "skipped": 0}
    
    imported = 0
    skipped = 0
    errors = []
    
    with get_db_context() as db:
        for _, row in trades_df.iterrows():
            try:
                # Generate exec_id if missing
                exec_id = row.get('exec_id') or row.get('trade_id')
                if not exec_id or pd.isna(exec_id) or exec_id == '':
                    exec_id = f"flex_{uuid.uuid4().hex[:12]}"
                
                # Check if trade already exists
                existing = db.query(Trade).filter(Trade.exec_id == exec_id).first()
                if existing:
                    skipped += 1
                    continue
                
                # Parse values
                currency = str(row.get('currency', 'USD'))
                fx_rate = float(row.get('fx_rate', default_fx_rate)) if pd.notna(row.get('fx_rate')) else default_fx_rate
                realized_pnl = float(row.get('realized_pnl', 0)) if pd.notna(row.get('realized_pnl')) else 0.0
                
                # Calculate P&L in base currency
                if currency == 'USD':
                    realized_pnl_base = realized_pnl * fx_rate
                elif currency == base_currency:
                    realized_pnl_base = realized_pnl
                else:
                    realized_pnl_base = realized_pnl  # Keep as is for other currencies
                
                # Parse trade date
                trade_date = row.get('trade_datetime') or row.get('trade_date')
                if isinstance(trade_date, str):
                    trade_date = pd.to_datetime(trade_date)
                elif pd.isna(trade_date):
                    trade_date = datetime.now()
                
                # Create trade record
                trade = Trade(
                    account_id=str(row.get('account_id', 'U13798787')),
                    exec_id=exec_id,
                    exec_time=trade_date,
                    symbol=str(row.get('symbol', '')),
                    sec_type=str(row.get('asset_class', 'STK')),
                    currency=currency,
                    exchange=str(row.get('exchange', '')) if pd.notna(row.get('exchange')) else None,
                    side=str(row.get('side', '')),
                    shares=abs(float(row.get('quantity', 0))),
                    price=float(row.get('price', 0)) if pd.notna(row.get('price')) else 0.0,
                    proceeds=float(row.get('proceeds', 0)) if pd.notna(row.get('proceeds')) else 0.0,
                    commission=float(row.get('commission', 0)) if pd.notna(row.get('commission')) else 0.0,
                    taxes=float(row.get('taxes', 0)) if pd.notna(row.get('taxes')) else 0.0,
                    cost_basis=float(row.get('cost_basis', 0)) if pd.notna(row.get('cost_basis')) else 0.0,
                    realized_pnl=realized_pnl,
                    realized_pnl_base=realized_pnl_base,
                    mtm_pnl=float(row.get('mtm_pnl', 0)) if pd.notna(row.get('mtm_pnl')) else 0.0,
                    fx_rate_to_base=fx_rate,
                    base_currency=base_currency,
                    underlying=str(row.get('underlying', '')) if pd.notna(row.get('underlying')) else None,
                    strike=float(row.get('strike', 0)) if pd.notna(row.get('strike')) else None,
                    expiry=str(row.get('expiry', '')) if pd.notna(row.get('expiry')) else None,
                    put_call=str(row.get('put_call', '')) if pd.notna(row.get('put_call')) else None,
                    multiplier=float(row.get('multiplier', 1)) if pd.notna(row.get('multiplier')) else 1.0,
                    order_type=str(row.get('order_type', '')) if pd.notna(row.get('order_type')) else None,
                    trade_id=str(row.get('trade_id', '')) if pd.notna(row.get('trade_id')) else None,
                )
                
                db.add(trade)
                imported += 1
                
            except Exception as e:
                errors.append(f"Error importing trade: {e}")
                logger.warning(f"Error importing trade: {e}")
                continue
        
        db.commit()
    
    return {
        "status": "success",
        "imported": imported,
        "skipped": skipped,
        "total_in_files": len(trades_df),
        "errors": errors[:5] if errors else None,
    }


# =============================================================================
# Query Functions
# =============================================================================

def get_trades_df(
    symbol: Optional[str] = None,
    start_date: Optional[Union[str, datetime, date]] = None,
    end_date: Optional[Union[str, datetime, date]] = None,
    side: Optional[str] = None,
    currency: Optional[str] = None,
    limit: int = 1000,
) -> pd.DataFrame:
    """
    Query trades from database and return as DataFrame.
    
    Args:
        symbol: Filter by symbol (supports LIKE pattern with %)
        start_date: Filter trades on or after this date
        end_date: Filter trades on or before this date
        side: Filter by BUY or SELL
        currency: Filter by currency
        limit: Maximum rows to return
        
    Returns:
        DataFrame with trade records
    """
    with get_db_context() as db:
        query = db.query(Trade)
        
        if symbol:
            if '%' in symbol:
                query = query.filter(Trade.symbol.like(symbol))
            else:
                query = query.filter(Trade.symbol == symbol)
        
        if start_date:
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            query = query.filter(Trade.exec_time >= start_date)
        
        if end_date:
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            query = query.filter(Trade.exec_time <= end_date)
        
        if side:
            query = query.filter(Trade.side == side.upper())
        
        if currency:
            query = query.filter(Trade.currency == currency.upper())
        
        query = query.order_by(desc(Trade.exec_time)).limit(limit)
        
        trades = query.all()
        
        if not trades:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for t in trades:
            data.append({
                'id': t.id,
                'exec_time': t.exec_time,
                'symbol': t.symbol,
                'sec_type': t.sec_type,
                'side': t.side,
                'shares': t.shares,
                'price': t.price,
                'currency': t.currency,
                'commission': t.commission,
                'realized_pnl': t.realized_pnl,
                'realized_pnl_hkd': t.realized_pnl_base,
                'fx_rate': t.fx_rate_to_base,
                'exchange': t.exchange,
                'exec_id': t.exec_id,
            })
        
        return pd.DataFrame(data)


def get_daily_returns(
    account_id: Optional[str] = None,
    start_date: Optional[Union[str, datetime, date]] = None,
    end_date: Optional[Union[str, datetime, date]] = None,
    use_pnl_history: bool = True,
) -> pd.DataFrame:
    """
    Get daily returns series from PnL History or Account Snapshots.
    
    Args:
        account_id: Filter by account ID
        start_date: Start date for returns
        end_date: End date for returns
        use_pnl_history: If True, use PnL History net_liquidation values.
                        If False, use AccountSnapshot equity values.
        
    Returns:
        DataFrame with all columns from pnl_history table:
        - date, account_id
        - realized_pnl, unrealized_pnl, total_pnl
        - net_liquidation, total_cash
        - daily_return, cumulative_return
    """
    if use_pnl_history:
        # Get returns from PnL History (use stored daily_return and cumulative_return if available)
        with get_db_context() as db:
            query = db.query(PnLHistory).order_by(PnLHistory.date)
            
            if account_id:
                query = query.filter(PnLHistory.account_id == account_id)
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(PnLHistory.date >= start_date)
            if end_date:
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(PnLHistory.date <= end_date)
            
            pnl_records = query.all()
            
            if len(pnl_records) < 1:
                return pd.DataFrame(columns=[
                    'date', 'account_id', 
                    'realized_pnl', 'unrealized_pnl', 'total_pnl', 'mtm',
                    'net_liquidation', 'total_cash',
                    'daily_return', 'cumulative_return'
                ])
            
            data = []
            for record in pnl_records:
                data.append({
                    'date': record.date,
                    'account_id': record.account_id,
                    'net_liquidation': record.net_liquidation,
                    'total_cash': record.total_cash,
                    'realized_pnl': record.realized_pnl,
                    'unrealized_pnl': record.unrealized_pnl,
                    'total_pnl': record.total_pnl,
                    'mtm': record.mtm,  # Mark-to-Market PnL
                    'daily_return': record.daily_return,  # Use stored value (may be None)
                    'cumulative_return': record.cumulative_return,  # Use stored value (may be None)
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Check if stored returns are available (not all NULL)
            has_stored_returns = not (df['daily_return'].isna().all() and df['cumulative_return'].isna().all())
            
            if has_stored_returns:
                # Use stored values, but fill in any missing ones by calculation
                missing_mask = df['daily_return'].isna()
                if missing_mask.any():
                    logger.info("Some returns are missing in pnl_history, calculating from net_liquidation")
                    # Calculate for missing rows
                    calculated_returns = df['net_liquidation'].pct_change()
                    calculated_cumulative = (1 + calculated_returns).cumprod() - 1
                    # Fill missing values
                    df.loc[missing_mask, 'daily_return'] = calculated_returns[missing_mask]
                    df.loc[missing_mask, 'cumulative_return'] = calculated_cumulative[missing_mask]
            else:
                # No stored returns available, calculate from scratch
                logger.info("No stored returns found in pnl_history, calculating from net_liquidation")
                df['daily_return'] = df['net_liquidation'].pct_change()
                df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
                # Set first record's cumulative_return to 0
                if len(df) > 0:
                    df.loc[df.index[0], 'cumulative_return'] = 0.0
            
            # Drop rows where daily_return is still NaN (first row typically)
            df = df.dropna(subset=['daily_return'])
            
            # Return all columns from pnl_history table
            return df
    else:
        # Calculate returns from Account Snapshots (equity values)
        from backend.data_processor import DataProcessor
        processor = DataProcessor()
        
        if not account_id:
            # Try to get account_id from database
            with get_db_context() as db:
                first_snapshot = db.query(AccountSnapshot).first()
                if first_snapshot:
                    account_id = first_snapshot.account_id
                else:
                    return pd.DataFrame(columns=['date', 'daily_return', 'cumulative_return', 'equity'])
        
        start_dt = None
        end_dt = None
        if start_date:
            if isinstance(start_date, str):
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_dt = start_date
        if end_date:
            if isinstance(end_date, str):
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_dt = end_date
        
        return processor.calculate_daily_returns(account_id, start_dt, end_dt)


def get_daily_pnl(
    start_date: Optional[Union[str, datetime, date]] = None,
    end_date: Optional[Union[str, datetime, date]] = None,
    group_by_currency: bool = False,
) -> pd.DataFrame:
    """
    Get daily P&L summary from trades.
    
    Args:
        start_date: Start date filter
        end_date: End date filter
        group_by_currency: If True, show P&L by currency
        
    Returns:
        DataFrame with daily P&L (in both USD and HKD)
    """
    trades = get_trades_df(start_date=start_date, end_date=end_date, limit=10000)
    
    if trades.empty:
        return pd.DataFrame()
    
    trades['date'] = pd.to_datetime(trades['exec_time']).dt.date
    
    if group_by_currency:
        daily = trades.groupby(['date', 'currency']).agg({
            'id': 'count',
            'realized_pnl': 'sum',
            'realized_pnl_hkd': 'sum',
            'commission': 'sum',
        }).rename(columns={'id': 'trade_count'})
    else:
        daily = trades.groupby('date').agg({
            'id': 'count',
            'realized_pnl': 'sum',
            'realized_pnl_hkd': 'sum',
            'commission': 'sum',
        }).rename(columns={'id': 'trade_count'})
    
    daily = daily.reset_index()
    daily['cumulative_pnl_usd'] = daily['realized_pnl'].cumsum()
    daily['cumulative_pnl_hkd'] = daily['realized_pnl_hkd'].cumsum()
    
    return daily


def get_trade_summary(
    start_date: Optional[Union[str, datetime, date]] = None,
    end_date: Optional[Union[str, datetime, date]] = None,
) -> pd.DataFrame:
    """
    Get P&L summary grouped by symbol.
    
    Returns:
        DataFrame with columns: symbol, trade_count, total_quantity, 
        realized_pnl_usd, realized_pnl_hkd, commissions
    """
    trades = get_trades_df(start_date=start_date, end_date=end_date, limit=10000)
    
    if trades.empty:
        return pd.DataFrame()
    
    summary = trades.groupby('symbol').agg({
        'id': 'count',
        'shares': 'sum',
        'realized_pnl': 'sum',
        'realized_pnl_hkd': 'sum',
        'commission': 'sum',
    }).rename(columns={
        'id': 'trade_count',
        'shares': 'total_shares',
        'realized_pnl': 'realized_pnl_usd',
        'realized_pnl_hkd': 'realized_pnl_hkd',
        'commission': 'total_commission',
    })
    
    return summary.sort_values('realized_pnl_usd', ascending=False)


def get_account_pnl_totals() -> Dict[str, float]:
    """
    Get total P&L across all trades.
    
    Returns:
        Dict with total_pnl_usd, total_pnl_hkd, total_commissions
    """
    with get_db_context() as db:
        result = db.query(
            func.sum(Trade.realized_pnl).label('total_usd'),
            func.sum(Trade.realized_pnl_base).label('total_hkd'),
            func.sum(Trade.commission).label('total_commission'),
            func.count(Trade.id).label('trade_count'),
        ).first()
        
        return {
            'total_pnl_usd': result.total_usd or 0.0,
            'total_pnl_hkd': result.total_hkd or 0.0,
            'total_commissions': result.total_commission or 0.0,
            'trade_count': result.trade_count or 0,
        }


def query_trades(sql: str) -> pd.DataFrame:
    """
    Execute raw SQL query on the trades table.
    
    Args:
        sql: SQL query string (e.g., "SELECT * FROM trades WHERE symbol = 'IAU'")
        
    Returns:
        DataFrame with query results
    """
    return pd.read_sql(sql, engine)


# =============================================================================
# P&L Recording
# =============================================================================

def record_daily_pnl(
    account_id: str,
    date: datetime,
    realized_pnl: float,
    unrealized_pnl: float,
    net_liquidation: float,
    total_cash: float,
) -> PnLHistory:
    """
    Record daily P&L snapshot to database.
    
    Args:
        account_id: Account identifier
        date: Date of the snapshot
        realized_pnl: Realized P&L
        unrealized_pnl: Unrealized P&L
        net_liquidation: Net liquidation value
        total_cash: Total cash
        
    Returns:
        Created PnLHistory record
    """
    with get_db_context() as db:
        pnl = PnLHistory(
            account_id=account_id,
            date=date,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            total_pnl=realized_pnl + unrealized_pnl,
            net_liquidation=net_liquidation,
            total_cash=total_cash,
        )
        db.add(pnl)
        db.commit()
        db.refresh(pnl)
        return pnl


# =============================================================================
# Print/Display Functions
# =============================================================================

def print_trade_summary():
    """Print formatted trade summary to console."""
    summary = get_trade_summary()
    totals = get_account_pnl_totals()
    
    print("\n" + "=" * 70)
    print("TRADE SUMMARY BY SYMBOL")
    print("=" * 70)
    
    if summary.empty:
        print("No trades found in database.")
        return
    
    print(f"\n{'Symbol':<25} {'Trades':>8} {'P&L (USD)':>14} {'P&L (HKD)':>14}")
    print("-" * 70)
    
    for symbol, row in summary.iterrows():
        print(f"{symbol:<25} {row['trade_count']:>8} {row['realized_pnl_usd']:>14,.2f} {row['realized_pnl_hkd']:>14,.2f}")
    
    print("-" * 70)
    print(f"{'TOTAL':<25} {totals['trade_count']:>8} {totals['total_pnl_usd']:>14,.2f} {totals['total_pnl_hkd']:>14,.2f}")
    print(f"{'Commissions':<25} {'':>8} {totals['total_commissions']:>14,.2f}")
    print("=" * 70)


def print_daily_pnl():
    """Print formatted daily P&L to console."""
    daily = get_daily_pnl()
    
    print("\n" + "=" * 80)
    print("DAILY P&L")
    print("=" * 80)
    
    if daily.empty:
        print("No trades found in database.")
        return
    
    print(f"\n{'Date':<12} {'Trades':>8} {'Daily USD':>14} {'Daily HKD':>14} {'Cumul USD':>14} {'Cumul HKD':>14}")
    print("-" * 80)
    
    for _, row in daily.iterrows():
        print(f"{str(row['date']):<12} {row['trade_count']:>8} "
              f"{row['realized_pnl']:>14,.2f} {row['realized_pnl_hkd']:>14,.2f} "
              f"{row['cumulative_pnl_usd']:>14,.2f} {row['cumulative_pnl_hkd']:>14,.2f}")
    
    print("=" * 80)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("""
IBKR Database Utility

Usage:
    python -m backend.db_utils <command>

Commands:
    init        - Initialize database tables
    import      - Import trades from Flex Query files
    summary     - Show trade summary by symbol
    daily       - Show daily P&L
    totals      - Show total P&L
    reset       - Reset trades table (WARNING: deletes data!)
    reset-pnl   - Reset pnl_history table (WARNING: deletes data!)
    query <sql> - Run SQL query
        """)
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        init_database()
    
    elif command == "import":
        print("Importing trades from Flex Query files...")
        result = import_trades_from_flex()
        print(f"✓ Imported: {result['imported']}, Skipped: {result['skipped']}")
        if result.get('errors'):
            print(f"  Errors: {result['errors']}")
    
    elif command == "summary":
        print_trade_summary()
    
    elif command == "daily":
        print_daily_pnl()
    
    elif command == "totals":
        totals = get_account_pnl_totals()
        print(f"\nTotal P&L (USD): ${totals['total_pnl_usd']:,.2f}")
        print(f"Total P&L (HKD): HK${totals['total_pnl_hkd']:,.2f}")
        print(f"Total Commissions: ${totals['total_commissions']:,.2f}")
        print(f"Total Trades: {totals['trade_count']}")
    
    elif command == "reset":
        confirm = input("Are you sure you want to reset the trades table? (yes/no): ")
        if confirm.lower() == "yes":
            reset_trades_table()
        else:
            print("Cancelled.")

    elif command == "reset-pnl":
        confirm = input("Are you sure you want to reset the pnl_history table? (yes/no): ")
        if confirm.lower() == "yes":
            reset_pnl_history_table()
        else:
            print("Cancelled.")
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("Please provide a SQL query")
        else:
            sql = " ".join(sys.argv[2:])
            result = query_trades(sql)
            print(result.to_string())
    
    else:
        print(f"Unknown command: {command}")
