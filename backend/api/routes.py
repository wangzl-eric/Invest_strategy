"""API route handlers."""
import io
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import (
    AccountSnapshot, Position, PnLHistory, Trade, PerformanceMetric
)
from backend.auth import (
    get_current_user_or_api_key,
    get_user_accounts,
    get_user_primary_account,
    require_role,
)
from backend.api.schemas import (
    AccountSummaryResponse,
    PositionResponse,
    PnLResponse,
    TradeResponse,
    PerformanceMetricResponse,
    PnLTimeSeriesPoint,
)
from backend.data_fetcher import DataFetcher
from backend.data_processor import DataProcessor
from backend.cache import cache_manager, cached
import numpy as np
from backend.ibkr_client import IBKRClient
from backend.config import settings
from backend.flex_query_client import FlexQueryClient, FlexQueryError
from backend.flex_importer import (
    import_flex_query_result,
    import_trades_from_flex,
    import_mark_to_market_performance_csv,
)
from backend.db_utils import import_trades_from_flex_result, import_all_flex_data
from backend.export import (
    export_trades_excel,
    export_performance_excel,
    export_pnl_excel,
    export_combined_report,
    get_export_filename
)
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

data_processor = DataProcessor()


def model_to_dict(model_instance, exclude_fields: Optional[List[str]] = None):
    """Convert SQLAlchemy model to dict."""
    exclude_fields = exclude_fields or []
    result = {}
    for c in model_instance.__table__.columns:
        if c.name not in exclude_fields:
            value = getattr(model_instance, c.name)
            # Convert None to None (keep as is for Optional fields)
            result[c.name] = value
    return result


@router.get("/account/summary", response_model=AccountSummaryResponse)
async def get_account_summary(
    account_id: Optional[str] = Query(None, description="Account ID"),
    current_user: Optional = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get latest account summary."""
    try:
        # If user is authenticated, filter by their accounts
        if current_user:
            user_accounts = get_user_accounts(current_user, db)
            user_account_ids = [acc.account_id for acc in user_accounts]
            
            if account_id:
                # Verify user has access to this account
                if account_id not in user_account_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied to this account"
                    )
            else:
                # Use primary account or first account
                primary = get_user_primary_account(current_user, db)
                account_id = primary.account_id if primary else (user_account_ids[0] if user_account_ids else None)
        
        query = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp))
        
        if account_id:
            query = query.filter(AccountSnapshot.account_id == account_id)
        
        snapshot = query.first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="No account snapshot found")
        
        return AccountSummaryResponse(**model_to_dict(snapshot))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    account_id: Optional[str] = Query(None, description="Account ID"),
    db: Session = Depends(get_db)
):
    """Get current positions."""
    try:
        query = db.query(Position).order_by(desc(Position.timestamp))
        
        if account_id:
            query = query.filter(Position.account_id == account_id)
        
        # Get latest position for each symbol
        positions = query.all()
        
        # Group by symbol and get latest
        latest_positions = {}
        for pos in positions:
            key = f"{pos.account_id}_{pos.symbol}"
            if key not in latest_positions or pos.timestamp > latest_positions[key].timestamp:
                latest_positions[key] = pos
        
        result = list(latest_positions.values())
        
        return [PositionResponse(**model_to_dict(p)) for p in result]
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pnl", response_model=List[PnLResponse])
async def get_pnl(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get PnL history."""
    try:
        logger.info(
            "Handling /pnl request",
            extra={
                "account_id": account_id,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit": limit,
            },
        )

        query = db.query(PnLHistory).order_by(desc(PnLHistory.date))
        
        if account_id:
            query = query.filter(PnLHistory.account_id == account_id)
        if start_date:
            query = query.filter(PnLHistory.date >= start_date)
        if end_date:
            query = query.filter(PnLHistory.date <= end_date)
        
        pnl_records = query.limit(limit).all()

        logger.info(
            "Fetched PnL records",
            extra={
                "record_count": len(pnl_records),
                "first_date": pnl_records[0].date.isoformat() if pnl_records else None,
                "last_date": pnl_records[-1].date.isoformat() if pnl_records else None,
            },
        )

        response = [PnLResponse(**model_to_dict(p)) for p in pnl_records]

        # Log a small preview of the series for debugging (first/last item only)
        if response:
            first = response[0]
            last = response[-1]
            logger.debug(
                "PnL response preview",
                extra={
                    "first": {
                        "date": first.date.isoformat(),
                        "total_pnl": first.total_pnl,
                        "net_liquidation": first.net_liquidation,
                    },
                    "last": {
                        "date": last.date.isoformat(),
                        "total_pnl": last.total_pnl,
                        "net_liquidation": last.net_liquidation,
                    },
                },
            )
        else:
            logger.warning("No PnL records found for query")

        return response
        
    except Exception as e:
        logger.error(f"Error fetching PnL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pnl/history", response_model=List[PnLTimeSeriesPoint])
async def get_pnl_history(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    freq: str = Query(
        "raw",
        description='Aggregation frequency: "raw" for all snapshots, "D" for one point per day (last snapshot)',
    ),
):
    """
    Get cleaned PnL/equity time series for charts.

    This endpoint wraps `DataProcessor.get_pnl_time_series` and returns a
    normalized time series that the frontend can consume directly.
    """
    try:
        if not account_id:
            # Fallback: try to infer latest account_id from snapshots
            with next(get_db()) as db:
                latest_snapshot = (
                    db.query(AccountSnapshot)
                    .order_by(desc(AccountSnapshot.timestamp))
                    .first()
                )
                if latest_snapshot:
                    account_id = latest_snapshot.account_id

        if not account_id:
            raise HTTPException(
                status_code=400,
                detail="account_id is required and could not be inferred from data",
            )

        series = data_processor.get_pnl_time_series(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            freq=freq,
        )

        # Convert dicts to PnLTimeSeriesPoint models
        result: List[PnLTimeSeriesPoint] = []
        for point in series:
            result.append(
                PnLTimeSeriesPoint(
                    timestamp=datetime.fromisoformat(point["timestamp"]),
                    realized_pnl=point["realized_pnl"],
                    unrealized_pnl=point["unrealized_pnl"],
                    total_pnl=point["total_pnl"],
                    net_liquidation=point.get("net_liquidation"),
                    total_cash=point.get("total_cash"),
                )
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching PnL history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=List[PerformanceMetricResponse])
async def get_performance(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get performance metrics."""
    try:
        query = db.query(PerformanceMetric).order_by(desc(PerformanceMetric.date))
        
        if account_id:
            query = query.filter(PerformanceMetric.account_id == account_id)
        if start_date:
            query = query.filter(PerformanceMetric.date >= start_date)
        if end_date:
            query = query.filter(PerformanceMetric.date <= end_date)
        
        metrics = query.limit(limit).all()
        
        return [PerformanceMetricResponse(**model_to_dict(m)) for m in metrics]
        
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    account_id: Optional[str] = Query(None, description="Account ID"),
    symbol: Optional[str] = Query(None, description="Symbol filter"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get trade history."""
    try:
        query = db.query(Trade).order_by(desc(Trade.exec_time))
        
        if account_id:
            query = query.filter(Trade.account_id == account_id)
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        if start_date:
            query = query.filter(Trade.exec_time >= start_date)
        if end_date:
            query = query.filter(Trade.exec_time <= end_date)
        
        trades = query.limit(limit).all()
        
        return [TradeResponse(**model_to_dict(t)) for t in trades]
        
    except Exception as e:
        logger.error(f"Error fetching trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-data")
async def fetch_data_now(
    account_id: Optional[str] = Query(None, description="Account ID to fetch data for"),
    store_pnl: bool = Query(False, description="If True, store PnL records in database. If False, fetch but don't store (for display only)")
):
    """Manually trigger data fetch from IBKR. By default, fetches fresh data but doesn't store PnL records."""
    try:
        logger.info(f"Manual data fetch triggered for account: {account_id} (store_pnl={store_pnl})")
        
        # Create IBKR client and data fetcher
        ibkr_client = IBKRClient()
        data_fetcher = DataFetcher(ibkr_client)
        
        # Connect to IBKR
        if not await ibkr_client.connect():
            import socket
            # Check if port is accessible
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            port_check = sock.connect_ex((settings.ibkr.host, settings.ibkr.port))
            sock.close()
            
            if port_check != 0:
                detail = (
                    f"Failed to connect to IBKR TWS/Gateway on {settings.ibkr.host}:{settings.ibkr.port}. "
                    f"Port is not accessible.\n\n"
                    f"Troubleshooting steps:\n"
                    f"1. Make sure TWS/Gateway is running and you're logged in\n"
                    f"2. Enable API in TWS/Gateway: Configure → API → Settings\n"
                    f"3. Enable 'Enable ActiveX and Socket Clients'\n"
                    f"4. Set Socket port to {settings.ibkr.port} (7497 for paper, 7496 for live)\n"
                    f"5. Add '127.0.0.1' to 'Trusted IPs'\n"
                    f"6. Restart TWS/Gateway after changing settings\n"
                    f"7. Run 'python test_ibkr_connection.py' for detailed diagnostics"
                )
            else:
                detail = (
                    f"Failed to connect to IBKR TWS/Gateway on {settings.ibkr.host}:{settings.ibkr.port}. "
                    f"Port is open but connection was refused.\n\n"
                    f"Possible issues:\n"
                    f"1. API might not be enabled in TWS/Gateway\n"
                    f"2. '127.0.0.1' might not be in Trusted IPs\n"
                    f"3. TWS/Gateway needs to be restarted after enabling API\n"
                    f"4. Run 'python test_ibkr_connection.py' for detailed diagnostics"
                )
            
            raise HTTPException(status_code=503, detail=detail)
        
        # Fetch all data (don't store PnL by default)
        result = await data_fetcher.fetch_all(account_id, store_pnl=store_pnl)
        
        # Disconnect
        await ibkr_client.disconnect()
        
        message = "Data fetched successfully" if not store_pnl else "Data fetched and stored successfully"
        return {
            "status": "success",
            "message": message,
            "account_id": result['account_id'],
            "positions_count": len(result['positions']),
            "trades_count": len(result['trades']),
            "pnl_fetched": True,
            "pnl_stored": store_pnl,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data from IBKR: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


# =============================================================================
# Flex Query Endpoints
# =============================================================================

@router.get("/flex-query/status")
async def get_flex_query_status():
    """Check if Flex Query is configured and ready to use."""
    is_configured = settings.flex_query.is_configured
    queries = settings.flex_query.get_all_queries()
    
    return {
        "configured": is_configured,
        "has_token": bool(settings.flex_query.token),
        "query_count": len(queries),
        "queries": [
            {
                "id": q.id,
                "name": q.name,
                "type": q.type,
                "description": q.description,
            }
            for q in queries
        ],
        "message": (
            f"Flex Query is configured with {len(queries)} report(s)" if is_configured
            else "Flex Query not configured. Please set token and queries in config/app_config.yaml"
        )
    }


@router.post("/flex-query/fetch-all-reports")
async def fetch_all_flex_query_reports(
    auto_import: bool = Query(
        True,
        description="Automatically import new trades to database (deduplicates existing records)"
    )
):
    """Fetch ALL configured Flex Query reports at once.
    
    This endpoint fetches data from every Flex Query defined in app_config.yaml,
    saves the raw responses organized by date/type, and automatically imports
    new trades to the database (with deduplication).
    
    Files are saved to: data/flex_reports/{YYYY-MM-DD}/{type}/{name}_{timestamp}.csv
    New trades are automatically appended to the database (duplicates are skipped).
    """
    try:
        flex_token = settings.flex_query.token
        queries = settings.flex_query.get_all_queries()
        
        if not flex_token:
            logger.warning("Flex Query fetch rejected: token not configured")
            raise HTTPException(
                status_code=400,
                detail="Flex Web Service token not configured in config/app_config.yaml"
            )
        
        if not queries:
            logger.warning("Flex Query fetch rejected: no queries configured")
            raise HTTPException(
                status_code=400,
                detail="No Flex Queries configured. Add queries to flex_query.queries in config/app_config.yaml"
            )
        
        logger.info(f"Fetching {len(queries)} Flex Query reports...")
        
        client = FlexQueryClient(token=flex_token)
        results = []
        errors = []
        total_imported = 0
        total_skipped = 0
        
        for query in queries:
            try:
                logger.info(f"Fetching '{query.name}' (ID: {query.id}, Type: {query.type})")
                
                result = await client.fetch_statement(
                    query_id=query.id,
                    query_name=query.name,
                    query_type=query.type,
                    save_raw=True
                )
                
                # Auto-import ALL data to database (trades, positions, PnL, snapshots)
                import_stats = {
                    "trades": {"imported": 0, "skipped": 0},
                    "positions": {"imported": 0, "skipped": 0},
                    "pnl": {"imported": 0, "skipped": 0},
                    "account_snapshots": {"imported": 0, "skipped": 0},
                    "total_imported": 0,
                    "total_skipped": 0,
                }
                
                if auto_import:
                    # For mark-to-market performance, the daily series lives in the saved CSV.
                    # Import that directly into pnl_history as one row per day.
                    csv_file_path = None
                    
                    # Check if saved file is CSV
                    if result.saved_file_path and str(result.saved_file_path).endswith(".csv"):
                        csv_file_path = result.saved_file_path
                    # Fallback: If XML was returned but CSV might exist, check the directory
                    elif query.type == "mark-to-market" and result.saved_file_path:
                        from pathlib import Path
                        saved_path = Path(result.saved_file_path)
                        # Look for CSV files in the same directory with similar name (performance*.csv)
                        # Try multiple patterns to find CSV files
                        patterns = [
                            f"{saved_path.stem.split('_')[0]}*.csv",  # performance*.csv
                            "performance*.csv",  # Any performance CSV
                            "*.csv",  # Any CSV in directory
                        ]
                        csv_files = []
                        for pattern in patterns:
                            csv_files.extend(list(saved_path.parent.glob(pattern)))
                            if csv_files:
                                break
                        
                        if csv_files:
                            # Use the most recent CSV file
                            csv_file_path = str(max(csv_files, key=lambda p: p.stat().st_mtime))
                            logger.info(f"Found CSV file in directory (fallback): {csv_file_path}")
                            # Update result.saved_file_path to point to CSV for consistency
                            result.saved_file_path = csv_file_path
                    
                    if csv_file_path and query.type == "mark-to-market":
                        logger.info(f"Importing mark-to-market daily series from CSV: {csv_file_path}")
                        perf_stats = import_mark_to_market_performance_csv(
                            csv_file_path,
                            account_id=result.account_id or None,
                        )
                        # Count as imported/updated/skipped under pnl
                        import_stats["pnl"]["imported"] += int(perf_stats.get("imported", 0))
                        import_stats["pnl"]["skipped"] += int(perf_stats.get("skipped", 0))
                        # treat updates as "imported" for summary purposes
                        import_stats["pnl"]["imported"] += int(perf_stats.get("updated", 0))
                        import_stats["total_imported"] += int(perf_stats.get("imported", 0)) + int(perf_stats.get("updated", 0))
                        import_stats["total_skipped"] += int(perf_stats.get("skipped", 0))
                        total_imported += int(perf_stats.get("imported", 0)) + int(perf_stats.get("updated", 0))
                        total_skipped += int(perf_stats.get("skipped", 0))
                    else:
                        logger.info(f"Auto-importing all data from '{query.name}' to database...")
                        full_import_stats = import_all_flex_data(result)
                        import_stats = full_import_stats.get("stats", import_stats)
                        import_stats["total_imported"] = full_import_stats.get("total_imported", 0)
                        import_stats["total_skipped"] = full_import_stats.get("total_skipped", 0)
                        total_imported += import_stats["total_imported"]
                        total_skipped += import_stats["total_skipped"]
                
                results.append({
                    "query_id": query.id,
                    "query_name": query.name,
                    "query_type": query.type,
                    "status": "success",
                    "account_id": result.account_id,
                    "from_date": result.from_date.isoformat() if result.from_date else None,
                    "to_date": result.to_date.isoformat() if result.to_date else None,
                    "trades_count": len(result.trades),
                    "positions_count": len(result.positions),
                    "saved_to": result.saved_file_path,
                    "db_import": {
                        "trades": import_stats["trades"],
                        "positions": import_stats["positions"],
                        "pnl": import_stats["pnl"],
                        "account_snapshots": import_stats["account_snapshots"],
                        "total_imported": import_stats["total_imported"],
                        "total_skipped": import_stats["total_skipped"],
                    },
                })
                
            except FlexQueryError as e:
                logger.error(f"Error fetching '{query.name}': {e.message}")
                errors.append({
                    "query_id": query.id,
                    "query_name": query.name,
                    "status": "error",
                    "error": e.message,
                })
            except Exception as e:
                logger.error(f"Unexpected error fetching '{query.name}': {e}")
                errors.append({
                    "query_id": query.id,
                    "query_name": query.name,
                    "status": "error",
                    "error": str(e),
                })
        
        return {
            "status": "completed",
            "message": f"Fetched {len(results)} of {len(queries)} reports successfully",
            "total_queries": len(queries),
            "successful": len(results),
            "failed": len(errors),
            "database": {
                "auto_import": auto_import,
                "total_new_records": total_imported,
                "total_duplicates_skipped": total_skipped,
                "note": "Includes trades, positions, PnL history, and account snapshots",
            },
            "results": results,
            "errors": errors if errors else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Flex Query reports: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/flex-query/fetch-trades")
async def fetch_trades_from_flex_query(
    query_id: Optional[str] = Query(
        None, 
        description="Flex Query ID (uses config trade_query_id if not provided)"
    ),
    token: Optional[str] = Query(
        None,
        description="Flex Web Service token (uses config token if not provided)"
    )
):
    """Fetch historical trade data from IBKR Flex Query Web Service.
    
    This endpoint fetches trade history that goes beyond the current TWS session,
    allowing you to import historical trades into the database.
    
    Prerequisites:
    1. Create a Flex Query in IBKR Account Management (Performance & Reports → Flex Queries)
    2. Configure the query to include Trade data
    3. Get a Flex Web Service token (Flex Queries → Configure Flex Web Service)
    4. Either configure in app_config.yaml or pass as parameters
    """
    try:
        # Use provided values or fall back to config
        flex_token = token or settings.flex_query.token
        flex_query_id = query_id or settings.flex_query.trade_query_id or settings.flex_query.activity_query_id
        
        if not flex_token:
            logger.warning("Flex Query fetch-trades rejected: token not configured")
            raise HTTPException(
                status_code=400,
                detail=(
                    "Flex Web Service token not configured.\n\n"
                    "To configure:\n"
                    "1. Log into IBKR Account Management\n"
                    "2. Go to: Performance & Reports → Flex Queries\n"
                    "3. Click 'Configure Flex Web Service'\n"
                    "4. Generate a token and add it to config/app_config.yaml"
                )
            )
        
        if not flex_query_id:
            logger.warning("Flex Query fetch-trades rejected: query ID not provided")
            raise HTTPException(
                status_code=400,
                detail=(
                    "Flex Query ID not provided.\n\n"
                    "To create a query:\n"
                    "1. Log into IBKR Account Management\n"
                    "2. Go to: Performance & Reports → Flex Queries → Activity Flex Query\n"
                    "3. Create a new query with 'Trades' section enabled\n"
                    "4. Note the Query ID and add it to config/app_config.yaml"
                )
            )
        
        logger.info(f"Fetching trades from Flex Query ID: {flex_query_id}")
        
        # Create client and fetch data
        client = FlexQueryClient(token=flex_token)
        result = await client.fetch_statement(flex_query_id)
        
        # Import trades into database
        import_result = import_flex_query_result(result)
        
        return {
            "status": "success",
            "message": "Trade history fetched and imported successfully",
            **import_result,
            "total_trades_in_response": len(result.trades),
            "total_positions_in_response": len(result.positions),
            "raw_data_saved_to": result.saved_file_path,
        }
        
    except FlexQueryError as e:
        logger.error(f"Flex Query error: {e.message}")
        raise HTTPException(
            status_code=502,
            detail=f"Flex Query error: {e.message}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching from Flex Query: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/flex-query/portfolio-summary")
async def get_flex_portfolio_summary(
    query_id: Optional[str] = Query(
        None,
        description="Flex Query ID (uses config activity_query_id if not provided)"
    )
):
    """Get real-time portfolio summary from Flex Query.
    
    Returns account summary, positions, and P&L data from the latest Flex Query fetch.
    This data includes historical context not available from real-time TWS API.
    """
    try:
        flex_token = settings.flex_query.token
        flex_query_id = query_id or settings.flex_query.activity_query_id or settings.flex_query.trade_query_id
        
        if not flex_token or not flex_query_id:
            logger.warning("Flex Query portfolio-summary rejected: token or query_id not configured")
            raise HTTPException(
                status_code=400,
                detail="Flex Query not configured. Set token and query_id in config/app_config.yaml"
            )
        
        logger.info(f"Fetching portfolio summary from Flex Query ID: {flex_query_id}")
        
        client = FlexQueryClient(token=flex_token)
        result = await client.fetch_statement(flex_query_id)
        
        # Parse positions by asset class
        positions_by_class = {}
        for pos in result.positions:
            asset_class = pos.sec_type or 'OTHER'
            if asset_class not in positions_by_class:
                positions_by_class[asset_class] = []
            positions_by_class[asset_class].append({
                'symbol': pos.symbol,
                'description': pos.description,
                'quantity': pos.quantity,
                'market_price': pos.market_price,
                'market_value': pos.market_value,
                'cost_basis': pos.cost_basis_money,
                'unrealized_pnl': pos.unrealized_pnl,
                'realized_pnl': pos.realized_pnl,
                'currency': pos.currency,
            })
        
        return {
            "status": "success",
            "account_id": result.account_id,
            "from_date": result.from_date.isoformat() if result.from_date else None,
            "to_date": result.to_date.isoformat() if result.to_date else None,
            "generated_at": result.generated_at.isoformat() if result.generated_at else None,
            "summary": {
                "net_liquidation": result.net_liquidation,
                "total_cash": result.total_cash,
                "total_positions": len(result.positions),
                "total_trades": len(result.trades),
            },
            "positions_by_class": positions_by_class,
            "positions": [
                {
                    'symbol': pos.symbol,
                    'description': pos.description,
                    'sec_type': pos.sec_type,
                    'quantity': pos.quantity,
                    'market_price': pos.market_price,
                    'market_value': pos.market_value,
                    'cost_basis': pos.cost_basis_money,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'realized_pnl': pos.realized_pnl,
                    'currency': pos.currency,
                }
                for pos in result.positions
            ],
            "recent_trades": [
                {
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'quantity': trade.quantity,
                    'price': trade.price,
                    'trade_date': trade.trade_date.isoformat() if trade.trade_date else None,
                    'commission': trade.commission,
                    'realized_pnl': trade.realized_pnl,
                }
                for trade in result.trades[:20]  # Last 20 trades
            ],
            "raw_data_saved_to": result.saved_file_path,
        }
        
    except FlexQueryError as e:
        logger.error(f"Flex Query error: {e.message}")
        raise HTTPException(status_code=502, detail=f"Flex Query error: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/flex-query/fetch-all")
async def fetch_all_from_flex_query(
    query_id: Optional[str] = Query(
        None,
        description="Flex Query ID (uses config activity_query_id if not provided)"
    ),
    token: Optional[str] = Query(
        None,
        description="Flex Web Service token (uses config token if not provided)"
    )
):
    """Fetch all available data from IBKR Flex Query (trades, positions, cash transactions).
    
    This is a comprehensive fetch that imports all data from the Flex Query response.
    Use this when you want to sync your entire account history.
    """
    try:
        flex_token = token or settings.flex_query.token
        flex_query_id = query_id or settings.flex_query.activity_query_id or settings.flex_query.trade_query_id
        
        if not flex_token or not flex_query_id:
            logger.warning("Flex Query fetch-all rejected: token or query_id not configured")
            raise HTTPException(
                status_code=400,
                detail="Flex Query not configured. Set token and query_id in config or pass as parameters."
            )
        
        logger.info(f"Fetching all data from Flex Query ID: {flex_query_id}")
        
        client = FlexQueryClient(token=flex_token)
        result = await client.fetch_statement(flex_query_id)
        
        # Import all data
        import_result = import_flex_query_result(result)
        
        return {
            "status": "success",
            "message": "All data fetched and imported successfully",
            **import_result,
            "summary": {
                "trades_in_response": len(result.trades),
                "positions_in_response": len(result.positions),
                "cash_transactions_in_response": len(result.cash_transactions),
                "net_liquidation": result.net_liquidation,
                "total_cash": result.total_cash,
            },
            "raw_data_saved_to": result.saved_file_path,
        }
        
    except FlexQueryError as e:
        logger.error(f"Flex Query error: {e.message}")
        raise HTTPException(status_code=502, detail=f"Flex Query error: {e.message}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching from Flex Query: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =============================================================================
# Risk Analytics Endpoints
# =============================================================================

@router.get("/risk/metrics")
async def get_risk_metrics(
    account_id: Optional[str] = Query(None, description="Account ID"),
    confidence_level: float = Query(0.95, ge=0.0, le=1.0, description="Confidence level for VaR/CVaR"),
    start_date: Optional[datetime] = Query(None, description="Start date for returns calculation"),
    end_date: Optional[datetime] = Query(None, description="End date for returns calculation"),
):
    """Get comprehensive risk metrics including VaR, CVaR, beta, and more."""
    try:
        from portfolio.risk_analytics import portfolio_metrics
        
        # Get returns data
        returns_df = data_processor.calculate_daily_returns(account_id, start_date, end_date)
        
        if returns_df.empty or len(returns_df) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for risk metrics calculation"
            )
        
        returns = returns_df['daily_return'].dropna()
        
        # Calculate risk metrics (without benchmark for now)
        metrics = portfolio_metrics(
            returns=returns,
            confidence_level=confidence_level,
            benchmark_returns=None
        )
        
        # Add additional metrics
        if len(returns) > 0:
            metrics['volatility'] = float(returns.std() * np.sqrt(252))  # Annualized
            metrics['mean_return'] = float(returns.mean())
        
        return {
            "account_id": account_id,
            "confidence_level": confidence_level,
            "metrics": metrics,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "data_points": len(returns)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating risk metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/risk/var")
async def get_var(
    account_id: Optional[str] = Query(None, description="Account ID"),
    confidence_level: float = Query(0.95, ge=0.0, le=1.0, description="Confidence level"),
    method: str = Query("historical", regex="^(historical|parametric)$", description="VaR calculation method"),
):
    """Calculate Value at Risk (VaR) for the portfolio."""
    try:
        from portfolio.risk_analytics import historical_var, parametric_var
        
        returns_df = data_processor.calculate_daily_returns(account_id)
        
        if returns_df.empty or len(returns_df) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for VaR calculation"
            )
        
        returns = returns_df['daily_return'].dropna()
        
        if method == "historical":
            var = historical_var(returns, confidence_level)
        else:
            var = parametric_var(returns, confidence_level)
        
        return {
            "account_id": account_id,
            "var": var,
            "confidence_level": confidence_level,
            "method": method,
            "var_percent": var * 100 if var != 0 else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating VaR: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/risk/cvar")
async def get_cvar(
    account_id: Optional[str] = Query(None, description="Account ID"),
    confidence_level: float = Query(0.95, ge=0.0, le=1.0, description="Confidence level"),
):
    """Calculate Conditional VaR (CVaR) / Expected Shortfall."""
    try:
        from portfolio.risk_analytics import conditional_var
        
        returns_df = data_processor.calculate_daily_returns(account_id)
        
        if returns_df.empty or len(returns_df) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for CVaR calculation"
            )
        
        returns = returns_df['daily_return'].dropna()
        cvar = conditional_var(returns, confidence_level)
        
        return {
            "account_id": account_id,
            "cvar": cvar,
            "confidence_level": confidence_level,
            "cvar_percent": cvar * 100 if cvar != 0 else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating CVaR: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/risk/stress-test")
async def get_stress_test(
    account_id: Optional[str] = Query(None, description="Account ID"),
    scenarios: Optional[str] = Query(None, description="Comma-separated list of shock percentages (e.g., -0.05,-0.10)"),
):
    """Perform stress testing with various shock scenarios."""
    try:
        import numpy as np
        
        returns_df = data_processor.calculate_daily_returns(account_id)
        
        if returns_df.empty or len(returns_df) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for stress testing"
            )
        
        returns = returns_df['daily_return'].dropna()
        
        # Parse scenarios
        if scenarios:
            scenario_list = [float(s.strip()) for s in scenarios.split(',')]
        else:
            scenario_list = [-0.01, -0.05, -0.10, -0.20]  # Default scenarios
        
        # Perform stress test
        mean_return = returns.mean()
        results = {}
        for shock in scenario_list:
            shocked_return = mean_return + shock
            results[f"{shock*100:.0f}%"] = float(shocked_return)
        
        return {
            "account_id": account_id,
            "scenarios": results,
            "data_points": len(returns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing stress test: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =============================================================================
# Export Endpoints
# =============================================================================

@router.get("/export/trades")
async def export_trades(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
):
    """Export trades to Excel format."""
    try:
        data = export_trades_excel(account_id, start_date, end_date)
        filename = get_export_filename("trades", account_id)
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting trades: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/export/performance")
async def export_performance(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
):
    """Export performance metrics to Excel format."""
    try:
        data = export_performance_excel(account_id, start_date, end_date)
        filename = get_export_filename("performance", account_id)
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting performance: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/export/pnl")
async def export_pnl(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
):
    """Export PnL history to Excel format."""
    try:
        data = export_pnl_excel(account_id, start_date, end_date)
        filename = get_export_filename("pnl", account_id)
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PnL: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/export/report")
async def export_report(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
):
    """Export combined report with multiple sheets (trades, performance, PnL)."""
    try:
        data = export_combined_report(account_id, start_date, end_date)
        filename = get_export_filename("report", account_id)
        
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =============================================================================
# Performance Analytics Endpoints
# =============================================================================

@router.get("/performance/analytics")
async def get_performance_analytics(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    include_benchmark: bool = Query(True, description="Include S&P 500 benchmark comparison"),
    rolling_window: int = Query(30, description="Rolling window for metrics (days)"),
    db: Session = Depends(get_db)
):
    """Get comprehensive performance analytics including returns, metrics, and benchmark comparison."""
    # Try to get from cache first
    cache_key = f"performance:analytics:{account_id}:{start_date}:{end_date}:{include_benchmark}:{rolling_window}"
    cached_result = cache_manager.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    from backend.benchmark_service import (
        get_benchmark_comparison,
        calculate_rolling_metrics,
        get_returns_distribution
    )
    from backend.api.schemas import (
        PerformanceAnalyticsResponse,
        ReturnsDistributionResponse,
        RollingMetricsResponse,
        BenchmarkComparisonResponse,
        BenchmarkTimeSeriesData,
        HistogramData,
        DistributionStatistics,
    )
    import pandas as pd
    
    try:
        # Get account_id if not provided
        if not account_id:
            latest_snapshot = (
                db.query(AccountSnapshot)
                .order_by(desc(AccountSnapshot.timestamp))
                .first()
            )
            if latest_snapshot:
                account_id = latest_snapshot.account_id
        
        if not account_id:
            raise HTTPException(
                status_code=400,
                detail="account_id is required and could not be inferred from data"
            )
        
        # Get PnL history from database
        query = db.query(PnLHistory).filter(
            PnLHistory.account_id == account_id
        ).order_by(PnLHistory.date)
        
        if start_date:
            query = query.filter(PnLHistory.date >= start_date)
        if end_date:
            query = query.filter(PnLHistory.date <= end_date)
        
        pnl_records = query.all()
        
        if len(pnl_records) < 2:
            return PerformanceAnalyticsResponse(
                account_id=account_id,
                data_points=len(pnl_records),
                error="Insufficient data for analytics calculation"
            )
        
        # Build DataFrame from PnL history (use stored returns if available)
        df = pd.DataFrame([{
            'date': r.date,
            'net_liquidation': r.net_liquidation or 0,
            'total_pnl': r.total_pnl or 0,
            'realized_pnl': r.realized_pnl or 0,
            'unrealized_pnl': r.unrealized_pnl or 0,
            'daily_return': r.daily_return,  # Use stored value
            'cumulative_return': r.cumulative_return,  # Use stored value
        } for r in pnl_records])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        df = df.set_index('date')
        
        # Use stored daily_return if available, otherwise calculate from net_liquidation
        if df['daily_return'].isna().all():
            logger.info("No stored daily_return found, calculating from net_liquidation")
            df['daily_return'] = df['net_liquidation'].pct_change()
        
        df = df.dropna(subset=['daily_return'])
        
        if len(df) < 2:
            return PerformanceAnalyticsResponse(
                account_id=account_id,
                data_points=len(df),
            )
        
        returns = df['daily_return']
        
        # Calculate summary metrics
        # Use stored cumulative_return for total_return if available
        if 'cumulative_return' in df.columns and not df['cumulative_return'].isna().all():
            # Use the last cumulative_return value as total_return
            total_return = float(df['cumulative_return'].iloc[-1]) if len(df) > 0 else 0.0
        else:
            # Fallback: calculate from daily returns
            total_return = float((1 + returns).prod() - 1)
        
        days = (df.index[-1] - df.index[0]).days
        annualized_return = float((1 + total_return) ** (365 / max(days, 1)) - 1) if days > 0 else 0
        volatility = float(returns.std() * np.sqrt(252))
        sharpe = float(np.sqrt(252) * returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino = float(np.sqrt(252) * returns.mean() / downside_std) if downside_std > 0 else 0
        
        # Max drawdown
        # Use stored cumulative_return if available, otherwise calculate
        if 'cumulative_return' in df.columns and not df['cumulative_return'].isna().all():
            # Convert cumulative_return to growth factor (1 + cumulative_return)
            cumulative = 1 + df['cumulative_return'].fillna(0)
        else:
            # Fallback: calculate from daily returns
            cumulative = (1 + returns).cumprod()
        
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = float(drawdown.min())
        
        # Calmar ratio
        calmar = float(annualized_return / abs(max_drawdown)) if max_drawdown != 0 else 0
        
        # Build returns series for frontend (use stored cumulative_return if available)
        returns_series = []
        for idx, row in df.iterrows():
            # Use stored cumulative_return if available, otherwise calculate
            if 'cumulative_return' in row and not pd.isna(row['cumulative_return']):
                cum_return = float(row['cumulative_return'])
            else:
                # Fallback: calculate from daily returns
                cum_return = float((1 + returns.loc[:idx]).prod() - 1)
            
            returns_series.append({
                'date': idx.strftime('%Y-%m-%d'),
                'daily_return': float(row['daily_return']) if not pd.isna(row['daily_return']) else 0,
                'cumulative_return': cum_return,
            })
        
        # Build equity series
        equity_series = []
        for idx, row in df.iterrows():
            equity_series.append({
                'date': idx.strftime('%Y-%m-%d'),
                'net_liquidation': float(row['net_liquidation']),
                'total_pnl': float(row['total_pnl']),
            })
        
        # Get distribution
        dist_data = get_returns_distribution(returns)
        distribution = ReturnsDistributionResponse(
            histogram=HistogramData(
                bins=dist_data['histogram']['bins'],
                counts=dist_data['histogram']['counts']
            ),
            statistics=DistributionStatistics(**dist_data['statistics']),
            percentiles=dist_data['percentiles']
        )
        
        # Get rolling metrics
        rolling_data = calculate_rolling_metrics(returns, window=rolling_window)
        rolling_metrics = RollingMetricsResponse(**rolling_data)
        
        # Get benchmark comparison
        benchmark_comparison = None
        if include_benchmark:
            benchmark_data = get_benchmark_comparison(
                returns,
                start_date=df.index[0].to_pydatetime(),
                end_date=df.index[-1].to_pydatetime()
            )
            
            if 'error' not in benchmark_data or benchmark_data.get('time_series'):
                time_series_data = benchmark_data.get('time_series', {})
                benchmark_comparison = BenchmarkComparisonResponse(
                    portfolio_sharpe=benchmark_data.get('portfolio_sharpe'),
                    benchmark_sharpe=benchmark_data.get('benchmark_sharpe'),
                    beta=benchmark_data.get('beta'),
                    alpha=benchmark_data.get('alpha'),
                    information_ratio=benchmark_data.get('information_ratio'),
                    tracking_error=benchmark_data.get('tracking_error'),
                    correlation=benchmark_data.get('correlation'),
                    data_points=benchmark_data.get('data_points', 0),
                    portfolio_cumulative_return=benchmark_data.get('portfolio_cumulative_return'),
                    benchmark_cumulative_return=benchmark_data.get('benchmark_cumulative_return'),
                    time_series=BenchmarkTimeSeriesData(
                        dates=time_series_data.get('dates', []),
                        portfolio_cumulative=time_series_data.get('portfolio_cumulative', []),
                        benchmark_cumulative=time_series_data.get('benchmark_cumulative', []),
                    ) if time_series_data else None,
                    error=benchmark_data.get('error'),
                )
        
        result = PerformanceAnalyticsResponse(
            account_id=account_id,
            period_start=df.index[0].strftime('%Y-%m-%d'),
            period_end=df.index[-1].strftime('%Y-%m-%d'),
            data_points=len(df),
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar,
            returns_series=returns_series,
            equity_series=equity_series,
            distribution=distribution,
            rolling_metrics=rolling_metrics,
            benchmark_comparison=benchmark_comparison,
        )
        
        # Cache the result for 60 seconds
        try:
            cache_manager.set(cache_key, result.dict(), ttl=60)
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating performance analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/benchmark/sp500")
async def get_sp500_benchmark(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    days: int = Query(365, description="Number of days of data (if dates not specified)"),
):
    """Get S&P 500 benchmark data for comparison charts."""
    from backend.benchmark_service import get_sp500_data
    from backend.api.schemas import SP500DataResponse, SP500DataPoint
    
    try:
        # Set default date range
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=days)
        
        # Fetch data
        df = get_sp500_data(start_date, end_date)
        
        if df.empty:
            return SP500DataResponse(
                data=[],
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
            )
        
        # Build response
        data_points = []
        for _, row in df.iterrows():
            data_points.append(SP500DataPoint(
                date=row['date'].strftime('%Y-%m-%d'),
                close=float(row['close']),
                daily_return=float(row['daily_return']) if not pd.isna(row['daily_return']) else None,
                cumulative_return=float(row['cumulative_return']) if not pd.isna(row['cumulative_return']) else None,
            ))
        
        # Calculate total and annualized return
        total_return = float(df['cumulative_return'].iloc[-1]) if len(df) > 0 else None
        days_in_data = (df['date'].iloc[-1] - df['date'].iloc[0]).days if len(df) > 1 else 0
        annualized_return = float((1 + total_return) ** (365 / max(days_in_data, 1)) - 1) if total_return and days_in_data > 0 else None
        
        return SP500DataResponse(
            symbol="^GSPC",
            name="S&P 500",
            data=data_points,
            start_date=df['date'].iloc[0].strftime('%Y-%m-%d') if len(df) > 0 else None,
            end_date=df['date'].iloc[-1].strftime('%Y-%m-%d') if len(df) > 0 else None,
            total_return=total_return,
            annualized_return=annualized_return,
        )
        
    except Exception as e:
        logger.error(f"Error fetching S&P 500 data: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

