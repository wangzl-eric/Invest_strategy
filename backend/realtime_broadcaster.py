"""Real-time data broadcaster that monitors changes and sends updates via WebSocket."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db_context
from backend.models import Position, PnLHistory, AccountSnapshot, Trade
from backend.websocket_manager import manager
from backend.data_fetcher import DataFetcher
from backend.ibkr_client import IBKRClient

logger = logging.getLogger(__name__)


class RealtimeBroadcaster:
    """Monitors data changes and broadcasts updates via WebSocket."""
    
    def __init__(self, update_interval_seconds: float = 1.0):
        self.update_interval = update_interval_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.last_positions: Dict[str, Dict[str, Any]] = {}
        self.last_pnl: Dict[str, float] = {}
        self.last_account_snapshot: Dict[str, Dict[str, Any]] = {}
        self.ibkr_client: Optional[IBKRClient] = None
        self.data_fetcher: Optional[DataFetcher] = None
    
    async def start(self):
        """Start the broadcaster."""
        if self.running:
            logger.warning("Broadcaster is already running")
            return
        
        self.running = True
        self.ibkr_client = IBKRClient()
        self.data_fetcher = DataFetcher(self.ibkr_client)
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info("Real-time broadcaster started")
    
    async def stop(self):
        """Stop the broadcaster."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self.ibkr_client:
            await self.ibkr_client.disconnect()
        
        logger.info("Real-time broadcaster stopped")
    
    async def _broadcast_loop(self):
        """Main broadcasting loop."""
        while self.running:
            try:
                await self._check_and_broadcast_updates()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(self.update_interval)
    
    async def _check_and_broadcast_updates(self):
        """Check for data changes and broadcast updates."""
        try:
            # Check positions
            await self._broadcast_position_updates()
            
            # Check P&L
            await self._broadcast_pnl_updates()
            
            # Check account snapshots
            await self._broadcast_account_updates()
            
        except Exception as e:
            logger.error(f"Error checking updates: {e}", exc_info=True)
    
    async def _broadcast_position_updates(self):
        """Broadcast position updates."""
        try:
            with get_db_context() as db:
                # Get latest positions grouped by account_id
                latest_positions_query = db.query(Position).order_by(
                    desc(Position.timestamp)
                ).all()
                
                # Group by account_id and get latest per symbol
                positions_by_account: Dict[str, Dict[str, Dict[str, Any]]] = {}
                for pos in latest_positions_query:
                    account_id = pos.account_id
                    symbol = pos.symbol
                    
                    if account_id not in positions_by_account:
                        positions_by_account[account_id] = {}
                    
                    key = f"{account_id}_{symbol}"
                    if key not in positions_by_account[account_id] or \
                       pos.timestamp > positions_by_account[account_id][key]['timestamp']:
                        positions_by_account[account_id][symbol] = {
                            'symbol': pos.symbol,
                            'sec_type': pos.sec_type,
                            'currency': pos.currency,
                            'quantity': pos.quantity,
                            'avg_cost': pos.avg_cost,
                            'market_price': pos.market_price,
                            'market_value': pos.market_value,
                            'unrealized_pnl': pos.unrealized_pnl,
                            'timestamp': pos.timestamp.isoformat() if pos.timestamp else None,
                        }
                
                # Compare with last known state and broadcast changes
                for account_id, positions in positions_by_account.items():
                    channel = f"positions:{account_id}"
                    current_state = positions
                    last_state = self.last_positions.get(account_id, {})
                    
                    # Check for changes
                    has_changes = False
                    for symbol, pos_data in current_state.items():
                        last_pos = last_state.get(symbol)
                        if last_pos is None or \
                           pos_data['quantity'] != last_pos.get('quantity', 0) or \
                           pos_data['market_price'] != last_pos.get('market_price') or \
                           pos_data['unrealized_pnl'] != last_pos.get('unrealized_pnl'):
                            has_changes = True
                            break
                    
                    # Also check for removed positions
                    if not has_changes:
                        for symbol in last_state:
                            if symbol not in current_state:
                                has_changes = True
                                break
                    
                    if has_changes:
                        message = {
                            'type': 'positions_update',
                            'account_id': account_id,
                            'timestamp': datetime.utcnow().isoformat(),
                            'positions': list(current_state.values()),
                        }
                        await manager.broadcast_to_channel(message, channel)
                        self.last_positions[account_id] = current_state
                        
        except Exception as e:
            logger.error(f"Error broadcasting position updates: {e}", exc_info=True)
    
    async def _broadcast_pnl_updates(self):
        """Broadcast P&L updates."""
        try:
            with get_db_context() as db:
                # Get latest P&L for each account
                latest_pnl_query = db.query(PnLHistory).order_by(
                    desc(PnLHistory.date)
                ).all()
                
                pnl_by_account: Dict[str, Dict[str, Any]] = {}
                for pnl in latest_pnl_query:
                    account_id = pnl.account_id
                    # Compare datetime objects, not strings
                    existing_date = pnl_by_account.get(account_id, {}).get('_date_obj')
                    if account_id not in pnl_by_account or \
                       (pnl.date and existing_date and pnl.date > existing_date) or \
                       (pnl.date and not existing_date):
                        pnl_by_account[account_id] = {
                            '_date_obj': pnl.date,  # Keep datetime for comparison
                            'date': pnl.date.isoformat() if pnl.date else None,
                            'realized_pnl': pnl.realized_pnl,
                            'unrealized_pnl': pnl.unrealized_pnl,
                            'total_pnl': pnl.total_pnl,
                            'net_liquidation': pnl.net_liquidation,
                            'total_cash': pnl.total_cash,
                        }
                
                # Broadcast changes
                for account_id, pnl_data in pnl_by_account.items():
                    channel = f"pnl:{account_id}"
                    current_total_pnl = pnl_data.get('total_pnl', 0) or 0
                    last_total_pnl = self.last_pnl.get(account_id, 0)
                    
                    if abs(current_total_pnl - last_total_pnl) > 0.01:  # Threshold to avoid noise
                        message = {
                            'type': 'pnl_update',
                            'account_id': account_id,
                            'timestamp': datetime.utcnow().isoformat(),
                            **pnl_data,
                        }
                        await manager.broadcast_to_channel(message, channel)
                        self.last_pnl[account_id] = current_total_pnl
                        
        except Exception as e:
            logger.error(f"Error broadcasting P&L updates: {e}", exc_info=True)
    
    async def _broadcast_account_updates(self):
        """Broadcast account snapshot updates."""
        try:
            with get_db_context() as db:
                # Get latest account snapshots
                latest_snapshots_query = db.query(AccountSnapshot).order_by(
                    desc(AccountSnapshot.timestamp)
                ).all()
                
                snapshots_by_account: Dict[str, Dict[str, Any]] = {}
                for snapshot in latest_snapshots_query:
                    account_id = snapshot.account_id
                    # Compare datetime objects, not strings
                    existing_timestamp = snapshots_by_account.get(account_id, {}).get('_timestamp_obj')
                    if account_id not in snapshots_by_account or \
                       (snapshot.timestamp and existing_timestamp and snapshot.timestamp > existing_timestamp) or \
                       (snapshot.timestamp and not existing_timestamp):
                        snapshots_by_account[account_id] = {
                            '_timestamp_obj': snapshot.timestamp,  # Keep datetime for comparison
                            'timestamp': snapshot.timestamp.isoformat() if snapshot.timestamp else None,
                            'net_liquidation': snapshot.net_liquidation,
                            'total_cash_value': snapshot.total_cash_value,
                            'buying_power': snapshot.buying_power,
                            'gross_position_value': snapshot.gross_position_value,
                            'available_funds': snapshot.available_funds,
                            'excess_liquidity': snapshot.excess_liquidity,
                            'equity': snapshot.equity,
                        }
                
                # Broadcast changes
                for account_id, snapshot_data in snapshots_by_account.items():
                    channel = f"account:{account_id}"
                    current_net_liq = snapshot_data.get('net_liquidation', 0) or 0
                    last_snapshot = self.last_account_snapshot.get(account_id, {})
                    last_net_liq = last_snapshot.get('net_liquidation', 0) or 0
                    
                    if abs(current_net_liq - last_net_liq) > 0.01:  # Threshold
                        message = {
                            'type': 'account_update',
                            'account_id': account_id,
                            'timestamp': datetime.utcnow().isoformat(),
                            **snapshot_data,
                        }
                        await manager.broadcast_to_channel(message, channel)
                        self.last_account_snapshot[account_id] = snapshot_data
                        
        except Exception as e:
            logger.error(f"Error broadcasting account updates: {e}", exc_info=True)
    
    async def trigger_manual_update(self, account_id: Optional[str] = None):
        """Manually trigger an update fetch and broadcast."""
        try:
            if not self.ibkr_client or not self.data_fetcher:
                self.ibkr_client = IBKRClient()
                self.data_fetcher = DataFetcher(self.ibkr_client)
            
            # Connect if needed
            if not await self.ibkr_client.ensure_connected():
                logger.warning("Cannot trigger manual update: IBKR not connected")
                return
            
            # Fetch fresh data (don't store PnL)
            await self.data_fetcher.fetch_all(account_id, store_pnl=False)
            
            # Wait a moment for DB to update
            await asyncio.sleep(0.5)
            
            # Broadcast updates
            await self._check_and_broadcast_updates()
            
        except Exception as e:
            logger.error(f"Error in manual update trigger: {e}", exc_info=True)


# Global broadcaster instance
broadcaster = RealtimeBroadcaster(update_interval_seconds=1.0)
