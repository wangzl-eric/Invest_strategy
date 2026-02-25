"""Flex Query & Portfolio Analyst CSV importers.

Import historical PnL/equity data into the pnl_history table.
Import trade history from Flex Query responses.

Usage:
    from backend.flex_importer import import_portfolio_analyst_csv, import_trades_from_flex
    rows = import_portfolio_analyst_csv("report.csv", "U1234567")
    
    # Import from Flex Query
    from backend.flex_query_client import FlexQueryClient
    client = FlexQueryClient(token="your_token")
    result = await client.fetch_statement(query_id="123456")
    count = import_trades_from_flex(result.trades)
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

import pandas as pd
from sqlalchemy import func

from backend.database import get_db_context
from backend.models import PnLHistory, Trade, Position

if TYPE_CHECKING:
    from backend.flex_query_client import FlexTrade, FlexPosition, FlexQueryResult

logger = logging.getLogger(__name__)


def calculate_and_update_returns(account_id: str, db) -> None:
    """
    Calculate cash-flow-adjusted daily_return and cumulative_return for all
    pnl_history records, excluding the effect of cash deposits / withdrawals.

    For Flex-imported records (total_cash IS NULL) the IBKR ``total_pnl``
    field already represents the day's investment P&L (realized + unrealized +
    dividends) and does *not* include cash flows, so:

        daily_return = total_pnl / prev_day_net_liquidation

    For live-API records (total_cash IS NOT NULL) ``total_pnl`` is a running
    all-time cumulative figure, so we fall back to NAV percentage change.
    """
    records = db.query(PnLHistory).filter(
        PnLHistory.account_id == account_id
    ).order_by(PnLHistory.date.asc()).all()

    if len(records) < 1:
        return

    data = []
    for record in records:
        data.append({
            'id': record.id,
            'date': record.date,
            'net_liquidation': record.net_liquidation,
            'total_pnl': record.total_pnl or 0.0,
            'total_cash': record.total_cash,
        })

    df = pd.DataFrame(data)
    df = df.sort_values('date')

    # Deduplicate: keep one record per calendar date (last entry wins)
    df['cal_date'] = pd.to_datetime(df['date']).dt.date
    df = df.drop_duplicates(subset=['cal_date'], keep='last')

    prev_nav = df['net_liquidation'].shift(1)

    # Flex records have total_cash = NULL; their total_pnl is the daily
    # investment P&L (excludes cash deposits/withdrawals).
    is_flex = df['total_cash'].isna()

    # PnL-based return for Flex records (cash-flow adjusted)
    pnl_return = df['total_pnl'] / prev_nav

    # NAV pct_change fallback for live-API records
    nav_return = df['net_liquidation'].pct_change()

    df['daily_return'] = pd.Series(dtype=float)
    df.loc[is_flex, 'daily_return'] = pnl_return[is_flex]
    df.loc[~is_flex, 'daily_return'] = nav_return[~is_flex]

    df['cumulative_return'] = (1 + df['daily_return'].fillna(0)).cumprod() - 1
    if len(df) > 0:
        df.loc[df.index[0], 'cumulative_return'] = 0.0

    for _, row in df.iterrows():
        record_id = row['id']
        daily_ret = row['daily_return'] if not pd.isna(row['daily_return']) else None
        cum_ret = row['cumulative_return'] if not pd.isna(row['cumulative_return']) else 0.0

        record = db.query(PnLHistory).filter(PnLHistory.id == record_id).first()
        if record:
            record.daily_return = float(daily_ret) if daily_ret is not None else None
            record.cumulative_return = float(cum_ret) if cum_ret is not None else 0.0

def import_mark_to_market_performance_csv(
    csv_path: str,
    account_id: Optional[str] = None,
) -> dict:
    """
    Import IBKR Flex Query 'mark-to-market performance' CSV into `pnl_history` as DAILY rows.

    This Flex export commonly comes as repeated 2-line blocks:
      - header line
      - data line
    where each block represents one day (FromDate == ToDate).

    We upsert by (account_id, date) where date is normalized to midnight.

    Returns:
        dict with imported / updated / skipped counts and date range.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    imported = 0
    updated = 0
    skipped = 0
    dates: list[datetime] = []

    def _parse_date_yyyymmdd(s: str) -> Optional[datetime]:
        s = str(s).strip().strip('"')
        if len(s) != 8 or not s.isdigit():
            return None
        try:
            dt = datetime.strptime(s, "%Y%m%d")
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        except Exception:
            return None

    def _to_float(s: str) -> Optional[float]:
        s = str(s).strip().strip('"')
        if s == "" or s.lower() == "nan":
            return None
        try:
            return float(s)
        except Exception:
            return None

    # Iterate header/data pairs
    i = 0
    account_ids_updated = set()
    with get_db_context() as db:
        while i < len(lines) - 1:
            header = lines[i]
            if not header.startswith('"ClientAccountID"'):
                i += 1
                continue

            data = lines[i + 1]
            # Parse using pandas' CSV parsing for quotes/commas
            try:
                cols = pd.read_csv(pd.io.common.StringIO(header), header=None).iloc[0].tolist()
                vals = pd.read_csv(pd.io.common.StringIO(data), header=None).iloc[0].tolist()
                row = {str(c).strip().strip('"'): str(v) for c, v in zip(cols, vals)}
            except Exception:
                i += 2
                continue

            row_account = row.get("ClientAccountID", "").strip().strip('"')
            acct = account_id or row_account
            if not acct:
                i += 2
                continue

            from_dt = _parse_date_yyyymmdd(row.get("FromDate", ""))
            to_dt = _parse_date_yyyymmdd(row.get("ToDate", ""))
            if not to_dt:
                i += 2
                continue

            # Only import daily rows; if FromDate/ToDate represent a range, skip here.
            if from_dt and from_dt != to_dt:
                skipped += 1
                i += 2
                continue

            starting = _to_float(row.get("StartingValue", ""))
            ending = _to_float(row.get("EndingValue", ""))
            mtm = _to_float(row.get("Mtm", "")) or 0.0
            realized = _to_float(row.get("Realized", "")) or 0.0
            change_unreal = _to_float(row.get("ChangeInUnrealized", "")) or 0.0
            dividends = _to_float(row.get("Dividends", "")) or 0.0
            interest = _to_float(row.get("Interest", "")) or 0.0
            broker_fees = _to_float(row.get("BrokerFees", "")) or 0.0
            advisor_fees = _to_float(row.get("AdvisorFees", "")) or 0.0
            client_fees = _to_float(row.get("ClientFees", "")) or 0.0

            # Total PnL is the sum of all components
            total_pnl = float(mtm + realized + change_unreal + dividends + interest + broker_fees + advisor_fees + client_fees)

            # Split between realized/unrealized only where meaningful.
            realized_pnl = float(realized)
            unrealized_pnl = float(total_pnl - realized_pnl)

            existing = db.query(PnLHistory).filter(
                PnLHistory.account_id == acct,
                PnLHistory.date == to_dt,
            ).first()

            if existing:
                existing.realized_pnl = realized_pnl
                existing.unrealized_pnl = unrealized_pnl
                existing.total_pnl = total_pnl
                existing.mtm = float(mtm)
                if ending is not None:
                    existing.net_liquidation = float(ending)
                updated += 1
            else:
                db.add(PnLHistory(
                    account_id=acct,
                    date=to_dt,
                    realized_pnl=realized_pnl,
                    unrealized_pnl=unrealized_pnl,
                    total_pnl=total_pnl,
                    mtm=float(mtm),
                    net_liquidation=float(ending) if ending is not None else None,
                    total_cash=None,
                ))
                imported += 1

            dates.append(to_dt)
            account_ids_updated.add(acct)
            i += 2
        
        # After importing all records, calculate and update returns for all affected accounts
        for acct in account_ids_updated:
            try:
                calculate_and_update_returns(acct, db)
                logger.info(f"Calculated returns for account {acct}")
            except Exception as e:
                logger.warning(f"Error calculating returns for account {acct}: {e}")
        
        db.commit()

    dates_sorted = sorted(set(dates))
    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "account_id": account_id,
        "min_date": dates_sorted[0].date().isoformat() if dates_sorted else None,
        "max_date": dates_sorted[-1].date().isoformat() if dates_sorted else None,
        "source_file": str(path),
    }


def import_pnl_csv(
    csv_path: str,
    account_id: str,
    date_column: str = "date",
    net_liq_column: str = "net_liquidation",
    total_cash_column: Optional[str] = None,
    realized_column: Optional[str] = None,
    unrealized_column: Optional[str] = None,
    date_format: Optional[str] = None,
) -> int:
    """
    Import Flex-exported PnL CSV into database.
    
    Returns number of records imported/updated.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    logger.info(f"Importing PnL CSV: {path} → account {account_id}")

    df = pd.read_csv(path)
    if date_column not in df.columns:
        raise ValueError(f"Column '{date_column}' not found. Available: {list(df.columns)}")

    # Parse dates
    df["_date"] = pd.to_datetime(df[date_column], format=date_format) if date_format else pd.to_datetime(df[date_column])

    count = 0
    with get_db_context() as db:
        for _, row in df.iterrows():
            # Safely convert date (iterrows() returns scalar values)
            date_val = row["_date"]
            
            # Skip NA values
            try:
                if pd.isna(date_val):  # type: ignore
                    continue
            except (ValueError, TypeError):
                # If pd.isna fails, try direct check
                if date_val is None:
                    continue
            
            # Convert to datetime
            try:
                if isinstance(date_val, pd.Timestamp):
                    dt = date_val.to_pydatetime()
                elif isinstance(date_val, datetime):
                    dt = date_val
                else:
                    dt_val = pd.to_datetime(date_val)
                    if isinstance(dt_val, pd.Timestamp):
                        dt = dt_val.to_pydatetime()
                    else:
                        # Fallback: convert to string then parse
                        dt = pd.to_datetime(str(date_val)).to_pydatetime()
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Skipping row with invalid date: {date_val}, error: {e}")
                continue
            
            # Extract values with proper None handling
            net_liq = _safe_float(row, net_liq_column)
            total_cash = _safe_float(row, total_cash_column) if total_cash_column else None
            realized = _safe_float(row, realized_column) if realized_column else 0.0
            unrealized = _safe_float(row, unrealized_column) if unrealized_column else 0.0
            
            # Handle None values in arithmetic
            if realized is None:
                realized = 0.0
            if unrealized is None:
                unrealized = 0.0
            total_pnl = realized + unrealized

            # Upsert
            existing = db.query(PnLHistory).filter_by(account_id=account_id, date=dt).first()
            
            if existing:
                existing.realized_pnl = float(realized)  # type: ignore
                existing.unrealized_pnl = float(unrealized)  # type: ignore
                existing.total_pnl = float(total_pnl)  # type: ignore
                if net_liq is not None:
                    existing.net_liquidation = float(net_liq)  # type: ignore
                if total_cash is not None:
                    existing.total_cash = float(total_cash)  # type: ignore
            else:
                db.add(PnLHistory(
                    account_id=account_id, date=dt,
                    realized_pnl=float(realized), unrealized_pnl=float(unrealized),
                    total_pnl=float(total_pnl), 
                    net_liquidation=float(net_liq) if net_liq is not None else None, 
                    total_cash=float(total_cash) if total_cash is not None else None,
                ))
            count += 1

    logger.info(f"Imported {count} rows from {path}")
    return count


def import_portfolio_analyst_csv(
    csv_path: str,
    account_id: str,
    date_column: str = "Date",
    equity_column: str = "Equity",
    return_column: Optional[str] = None,
    net_liq_column: Optional[str] = None,
    date_format: Optional[str] = None,
) -> int:
    """
    Import Portfolio Analyst Custom Report CSV.
    
    Handles common PA report formats with equity/return columns.
    Calculates PnL from equity changes if return_column not provided.
    
    Returns number of records imported/updated.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    logger.info(f"Importing PA CSV: {path} → account {account_id}")

    df = pd.read_csv(path)
    
    # Validate columns
    net_liq_col = net_liq_column or equity_column
    for col, name in [(date_column, "date"), (net_liq_col, "equity")]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' ({name}) not found. Available: {list(df.columns)}")

    # Parse and sort by date
    df["_date"] = pd.to_datetime(df[date_column], format=date_format) if date_format else pd.to_datetime(df[date_column])
    df = df.sort_values("_date").reset_index(drop=True)
    
    # Calculate returns
    df["_equity"] = pd.to_numeric(df[net_liq_col], errors="coerce")
    if return_column and return_column in df.columns:
        df["_return_pct"] = pd.to_numeric(df[return_column], errors="coerce")
    else:
        df["_return_pct"] = df["_equity"].pct_change() * 100

    count = 0
    with get_db_context() as db:
        for idx, row in df.iterrows():
            # Safely convert date (iterrows() returns scalar values)
            date_val = row["_date"]
            
            # Skip NA values
            try:
                if pd.isna(date_val):  # type: ignore
                    continue
            except (ValueError, TypeError):
                # If pd.isna fails, try direct check
                if date_val is None:
                    continue
            
            # Convert to datetime
            try:
                if isinstance(date_val, pd.Timestamp):
                    dt = date_val.to_pydatetime()
                elif isinstance(date_val, datetime):
                    dt = date_val
                else:
                    dt_val = pd.to_datetime(date_val)
                    if isinstance(dt_val, pd.Timestamp):
                        dt = dt_val.to_pydatetime()
                    else:
                        # Fallback: convert to string then parse
                        dt = pd.to_datetime(str(date_val)).to_pydatetime()
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Skipping row with invalid date: {date_val}, error: {e}")
                continue
            
            net_liq = _safe_float(row, "_equity")
            
            # Calculate PnL from return
            unrealized_pnl = 0.0
            try:
                idx_int = int(idx) if isinstance(idx, (int, float, str)) else 0
                if idx_int > 0:
                    prev_idx = idx_int - 1
                    if prev_idx >= 0 and prev_idx < len(df):
                        prev_equity_val = df.loc[prev_idx, "_equity"]
                        return_pct_val = row.get("_return_pct", 0.0)
                        
                        # Check if values are valid (iterrows() returns scalars, but be safe)
                        try:
                            prev_equity_scalar = float(prev_equity_val) if not pd.isna(prev_equity_val) else None  # type: ignore
                            return_pct_scalar = float(return_pct_val) if not pd.isna(return_pct_val) else None  # type: ignore
                            
                            if prev_equity_scalar is not None and return_pct_scalar is not None:
                                unrealized_pnl = (return_pct_scalar / 100.0) * prev_equity_scalar
                        except (ValueError, TypeError, OverflowError):
                            unrealized_pnl = 0.0
            except (ValueError, TypeError, IndexError, KeyError):
                unrealized_pnl = 0.0

            # Ensure unrealized_pnl is a float
            unrealized_pnl = float(unrealized_pnl) if unrealized_pnl is not None else 0.0

            # Upsert
            existing = db.query(PnLHistory).filter_by(account_id=account_id, date=dt).first()
            
            if existing:
                if net_liq is not None:
                    existing.net_liquidation = float(net_liq)  # type: ignore[assignment]
                existing.unrealized_pnl = unrealized_pnl  # type: ignore[assignment]
                existing.total_pnl = unrealized_pnl  # type: ignore[assignment]
            else:
                db.add(PnLHistory(
                    account_id=account_id, date=dt,
                    realized_pnl=0.0, unrealized_pnl=unrealized_pnl,
                    total_pnl=unrealized_pnl, 
                    net_liquidation=float(net_liq) if net_liq is not None else None,  # type: ignore[arg-type]
                    total_cash=None,
                ))
            count += 1

    logger.info(f"Imported {count} rows from {path}")
    return count


def _safe_float(row, col: str) -> Optional[float]:
    """Safely extract float from row."""
    if col not in row.index:
        return None
    val = row[col]
    if pd.isna(val):
        return None
    try:
        result = float(val)
        # Check for NaN or Inf
        if pd.isna(result) or (isinstance(result, float) and (result == float('inf') or result == float('-inf'))):
            return None
        return result
    except (ValueError, TypeError, OverflowError):
        return None


def import_trades_from_flex(trades: List["FlexTrade"]) -> int:
    """Import trades from Flex Query response into database.
    
    Args:
        trades: List of FlexTrade objects from FlexQueryClient
        
    Returns:
        Number of trades imported (excludes duplicates)
    """
    if not trades:
        logger.info("No trades to import")
        return 0
    
    count = 0
    with get_db_context() as db:
        for flex_trade in trades:
            # Generate a unique exec_id if not provided
            exec_id = flex_trade.exec_id or flex_trade.trade_id
            if not exec_id or exec_id.strip() == '' or exec_id == 'nan':
                # Generate exec_id from trade details
                exec_id = f"{flex_trade.symbol}_{flex_trade.trade_date.strftime('%Y%m%d%H%M%S')}_{flex_trade.side}_{abs(flex_trade.quantity)}"
            
            # Skip trades with no meaningful data
            if not flex_trade.symbol or flex_trade.symbol == 'nan':
                logger.debug(f"Skipping trade with no symbol")
                continue
            
            # Skip trades with zero quantity and zero price (summary rows)
            if flex_trade.quantity == 0 and flex_trade.price == 0:
                logger.debug(f"Skipping summary row for {flex_trade.symbol}")
                continue
            
            # Check if trade already exists by exec_id
            existing = db.query(Trade).filter(
                Trade.exec_id == exec_id
            ).first()
            
            if existing:
                logger.debug(f"Trade {exec_id} already exists, skipping")
                continue
            
            # Create new trade record
            trade = Trade(
                account_id=flex_trade.account_id,
                exec_id=exec_id,
                exec_time=flex_trade.trade_date,
                symbol=flex_trade.symbol,
                sec_type=flex_trade.sec_type,
                currency=flex_trade.currency,
                side=flex_trade.side,
                shares=abs(flex_trade.quantity),
                price=flex_trade.price,
                avg_price=flex_trade.price,
                cum_qty=abs(flex_trade.quantity),
                commission=abs(flex_trade.commission),
            )
            
            db.add(trade)
            count += 1
        
        db.flush()
    
    logger.info(f"Imported {count} new trades from Flex Query")
    return count


def import_positions_from_flex(positions: List["FlexPosition"]) -> int:
    """Import positions from Flex Query response into database.
    
    Args:
        positions: List of FlexPosition objects from FlexQueryClient
        
    Returns:
        Number of positions imported/updated
    """
    if not positions:
        logger.info("No positions to import")
        return 0
    
    count = 0
    with get_db_context() as db:
        for flex_pos in positions:
            # Create new position snapshot (positions are point-in-time)
            position = Position(
                account_id=flex_pos.account_id,
                timestamp=flex_pos.report_date,
                symbol=flex_pos.symbol,
                sec_type=flex_pos.sec_type,
                currency=flex_pos.currency,
                exchange='',  # Not provided in Flex Query
                quantity=flex_pos.quantity,
                avg_cost=flex_pos.cost_basis_price,
                market_price=flex_pos.market_price,
                market_value=flex_pos.market_value,
                unrealized_pnl=flex_pos.unrealized_pnl,
            )
            
            db.add(position)
            count += 1
        
        db.flush()
    
    logger.info(f"Imported {count} positions from Flex Query")
    return count


def import_flex_query_result(result: "FlexQueryResult") -> dict:
    """Import all data from a Flex Query result.
    
    Args:
        result: FlexQueryResult from FlexQueryClient
        
    Returns:
        Dictionary with counts of imported items
    """
    trades_count = import_trades_from_flex(result.trades)
    positions_count = import_positions_from_flex(result.positions)
    
    # Also update PnL history if we have account info
    pnl_count = 0
    if result.net_liquidation is not None:
        with get_db_context() as db:
            # Check if we already have a PnL record for this date
            existing = db.query(PnLHistory).filter(
                PnLHistory.account_id == result.account_id,
                PnLHistory.date >= result.to_date.replace(hour=0, minute=0, second=0),
                PnLHistory.date <= result.to_date.replace(hour=23, minute=59, second=59),
            ).first()
            
            if not existing:
                pnl_record = PnLHistory(
                    account_id=result.account_id,
                    date=result.to_date,
                    realized_pnl=0.0,  # Not directly available from summary
                    unrealized_pnl=0.0,
                    total_pnl=0.0,
                    net_liquidation=result.net_liquidation,
                    total_cash=result.total_cash,
                )
                db.add(pnl_record)
                db.flush()
                pnl_count = 1
    
    return {
        'trades_imported': trades_count,
        'positions_imported': positions_count,
        'pnl_records_imported': pnl_count,
        'account_id': result.account_id,
        'from_date': result.from_date.isoformat(),
        'to_date': result.to_date.isoformat(),
    }
