"""Data fetching module to retrieve account data from IBKR and store in database."""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.ibkr_client import IBKRClient
from backend.database import get_db_context
from backend.models import (
    AccountSnapshot, Position, PnLHistory, Trade, PerformanceMetric
)

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches data from IBKR and stores it in the database."""
    
    def __init__(self, ibkr_client: Optional[IBKRClient] = None):
        self.ibkr_client = ibkr_client or IBKRClient()
    
    def _model_to_dict(self, model_instance, exclude_fields: Optional[List[str]] = None):
        """Convert SQLAlchemy model to dict."""
        exclude_fields = exclude_fields or []
        return {
            c.name: getattr(model_instance, c.name)
            for c in model_instance.__table__.columns
            if c.name not in exclude_fields
        }
    
    async def fetch_and_store_account_snapshot(
        self, 
        account_id: Optional[str] = None
    ) -> AccountSnapshot:
        """Fetch account summary and store as snapshot."""
        try:
            account_summary = await self.ibkr_client.get_account_summary(account_id)
            account_id = account_id or account_summary.get('AccountId')
            
            if not account_id:
                raise ValueError("Account ID not found")
            
            with get_db_context() as db:
                snapshot = AccountSnapshot(
                    account_id=account_id,
                    timestamp=datetime.utcnow(),
                    total_cash_value=account_summary.get('TotalCashValue'),
                    net_liquidation=account_summary.get('NetLiquidation'),
                    buying_power=account_summary.get('BuyingPower'),
                    gross_position_value=account_summary.get('GrossPositionValue'),
                    available_funds=account_summary.get('AvailableFunds'),
                    excess_liquidity=account_summary.get('ExcessLiquidity'),
                    equity=account_summary.get('NetLiquidation'),
                )
                db.add(snapshot)
                db.flush()
                # Expunge from session so it can be used after session closes
                db.expunge(snapshot)
                logger.info(f"Stored account snapshot for {account_id}")
                return snapshot
                
        except Exception as e:
            logger.error(f"Error fetching/storing account snapshot: {e}")
            raise
    
    async def fetch_and_store_positions(
        self,
        account_id: Optional[str] = None
    ) -> List[Position]:
        """Fetch positions and store in database."""
        try:
            positions_data = await self.ibkr_client.get_positions(account_id)
            
            if not positions_data:
                return []
            
            account_id = account_id or positions_data[0].get('account')
            
            stored_positions = []
            with get_db_context() as db:
                for pos_data in positions_data:
                    position = Position(
                        account_id=pos_data.get('account', account_id),
                        timestamp=datetime.utcnow(),
                        symbol=pos_data['contract']['symbol'],
                        sec_type=pos_data['contract'].get('secType'),
                        currency=pos_data['contract'].get('currency'),
                        exchange=pos_data['contract'].get('exchange'),
                        quantity=float(pos_data['position']),
                        avg_cost=pos_data.get('avgCost'),
                        market_price=pos_data.get('marketPrice'),
                        market_value=pos_data.get('marketValue'),
                        unrealized_pnl=pos_data.get('unrealizedPnL'),
                    )
                    db.add(position)
                    stored_positions.append(position)
                
                db.flush()
                # Expunge all positions from session
                for pos in stored_positions:
                    db.expunge(pos)
                logger.info(f"Stored {len(stored_positions)} positions for {account_id}")
                return stored_positions
                
        except Exception as e:
            logger.error(f"Error fetching/storing positions: {e}")
            raise
    
    async def fetch_and_store_pnl(
        self,
        account_id: Optional[str] = None
    ) -> PnLHistory:
        """Fetch PnL data and store in database."""
        try:
            pnl_data = await self.ibkr_client.get_pnl(account_id)
            logger.info(
                "Fetched raw PnL from IBKR",
                extra={
                    "account_id_param": account_id,
                    "raw_pnl": {
                        "accountId": pnl_data.get("accountId"),
                        "netLiquidation": pnl_data.get("netLiquidation"),
                        "totalCash": pnl_data.get("totalCash"),
                        "unrealizedPnL": pnl_data.get("unrealizedPnL"),
                        "realizedPnL": pnl_data.get("realizedPnL"),
                        "totalPnL": pnl_data.get("totalPnL"),
                        "timestamp": pnl_data.get("timestamp"),
                    },
                },
            )
            account_id = account_id or pnl_data.get('accountId')
            
            if not account_id:
                raise ValueError("Account ID not found")
            
            with get_db_context() as db:
                pnl_record = PnLHistory(
                    account_id=account_id,
                    date=datetime.utcnow(),
                    realized_pnl=pnl_data.get('realizedPnL', 0.0),
                    unrealized_pnl=pnl_data.get('unrealizedPnL', 0.0),
                    total_pnl=pnl_data.get('totalPnL', 0.0),
                    net_liquidation=pnl_data.get('netLiquidation'),
                    total_cash=pnl_data.get('totalCash'),
                )
                db.add(pnl_record)
                db.flush()
                # Expunge from session
                db.expunge(pnl_record)
                logger.info(
                    "Stored PnL record",
                    extra={
                        "account_id": account_id,
                        "date": pnl_record.date.isoformat(),
                        "realized_pnl": pnl_record.realized_pnl,
                        "unrealized_pnl": pnl_record.unrealized_pnl,
                        "total_pnl": pnl_record.total_pnl,
                        "net_liquidation": pnl_record.net_liquidation,
                        "total_cash": pnl_record.total_cash,
                    },
                )
                return pnl_record
                
        except Exception as e:
            logger.error(f"Error fetching/storing PnL: {e}")
            raise
    
    async def fetch_and_store_trades(
        self,
        account_id: Optional[str] = None
    ) -> List[Trade]:
        """Fetch trades and store in database."""
        try:
            trades_data = await self.ibkr_client.get_trades(account_id)
            
            if not trades_data:
                return []
            
            stored_trades = []
            with get_db_context() as db:
                for trade_data in trades_data:
                    # Check if trade already exists
                    existing = db.query(Trade).filter(
                        Trade.exec_id == trade_data['execution']['execId']
                    ).first()
                    
                    if existing:
                        continue
                    
                    exec_time_str = trade_data['execution'].get('time')
                    exec_time = datetime.fromisoformat(exec_time_str) if exec_time_str else datetime.utcnow()
                    
                    trade = Trade(
                        account_id=trade_data.get('account', account_id),
                        exec_id=trade_data['execution']['execId'],
                        exec_time=exec_time,
                        symbol=trade_data['contract']['symbol'],
                        sec_type=trade_data['contract'].get('secType'),
                        currency=trade_data['contract'].get('currency'),
                        side=trade_data['execution']['side'],
                        shares=float(trade_data['execution']['shares']),
                        price=float(trade_data['execution']['price']),
                        avg_price=float(trade_data['execution'].get('avgPrice', trade_data['execution']['price'])),
                        cum_qty=float(trade_data['execution'].get('cumQty', trade_data['execution']['shares'])),
                        commission=float(trade_data.get('commission', 0.0)),
                    )
                    db.add(trade)
                    stored_trades.append(trade)
                
                db.flush()
                # Expunge all trades from session
                for trade in stored_trades:
                    db.expunge(trade)
                logger.info(f"Stored {len(stored_trades)} new trades")
                return stored_trades
                
        except Exception as e:
            logger.error(f"Error fetching/storing trades: {e}")
            raise
    
    def _model_to_dict(self, model_instance, exclude_fields: Optional[List[str]] = None):
        """Convert SQLAlchemy model to dict."""
        exclude_fields = exclude_fields or []
        return {
            c.name: getattr(model_instance, c.name)
            for c in model_instance.__table__.columns
            if c.name not in exclude_fields
        }
    
    async def fetch_all(
        self,
        account_id: Optional[str] = None,
        store_pnl: bool = False
    ) -> Dict[str, Any]:
        """Fetch all account data and optionally store in database.
        
        Args:
            account_id: Account ID to fetch data for
            store_pnl: If False, fetch PnL but don't store it in database (for display only)
        """
        try:
            logger.info(f"Starting full data fetch (store_pnl={store_pnl})...")
            
            # Fetch account summary first to get account_id if not provided
            snapshot = await self.fetch_and_store_account_snapshot(account_id)
            # Extract account_id from snapshot before it becomes detached
            account_id = snapshot.account_id if hasattr(snapshot, 'account_id') else account_id
            
            # Fetch other data
            positions = await self.fetch_and_store_positions(account_id)
            
            # Fetch PnL (but only store if store_pnl=True)
            if store_pnl:
                pnl = await self.fetch_and_store_pnl(account_id)
            else:
                # Fetch PnL but don't store it
                pnl_data = await self.ibkr_client.get_pnl(account_id)
                # Convert to dict format for return (but don't store in DB)
                pnl = pnl_data if isinstance(pnl_data, dict) else self._model_to_dict(pnl_data) if hasattr(pnl_data, '__dict__') else {}
                logger.info("Fetched PnL for display (not stored in database)")
            
            trades = await self.fetch_and_store_trades(account_id)
            
            logger.info("Completed full data fetch")
            
            # Convert SQLAlchemy models to dicts (objects are expunged so this should work)
            snapshot_dict = self._model_to_dict(snapshot)
            positions_list = [self._model_to_dict(p) for p in positions]
            pnl_dict = pnl if isinstance(pnl, dict) else self._model_to_dict(pnl)
            trades_list = [self._model_to_dict(t) for t in trades]
            
            return {
                'account_id': account_id,
                'snapshot': snapshot_dict,
                'positions': positions_list,
                'pnl': pnl_dict,
                'trades': trades_list,
            }
            
        except Exception as e:
            logger.error(f"Error in full data fetch: {e}")
            raise

