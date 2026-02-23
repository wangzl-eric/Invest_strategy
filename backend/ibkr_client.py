"""IBKR API client wrapper with connection management and error handling."""
import logging
import asyncio
from typing import Optional, Dict, Any
from ib_insync import IB, Stock, Contract, AccountValue, Position, Trade
from ib_insync.objects import PortfolioItem
import time

from backend.config import settings

# Import circuit breaker if available
try:
    from backend.circuit_breaker import ibkr_circuit_breaker
except ImportError:
    # Fallback if circuit breaker not available
    ibkr_circuit_breaker = None

logger = logging.getLogger(__name__)


class IBKRClient:
    """IBKR API client with automatic reconnection and error handling."""
    
    def __init__(self):
        self.ib = IB()
        self.connected = False
        self.connection_attempts = 0
        self.max_retries = 5
        self.retry_delay = 5  # seconds
        self._handlers_setup = False
        self._setup_event_handlers()
        
    def _setup_event_handlers(self):
        """Set up event handlers for connection, disconnection, and errors."""
        if self._handlers_setup:
            return
            
        # Set up disconnect handler
        self.ib.disconnectedEvent += self._on_disconnect
        
        # Set up error handler to catch login/connection issues
        self.ib.errorEvent += self._on_error
        
        # Set up connected event handler
        self.ib.connectedEvent += self._on_connected
        
        self._handlers_setup = True
        
    def _on_connected(self):
        """Handle successful connection event."""
        logger.info("IBKR connection established - login notification should appear in TWS/Gateway")
        self.connected = True
        
    def _on_disconnect(self):
        """Handle disconnection event."""
        logger.warning("Disconnected from IBKR")
        self.connected = False
        
    def _on_error(self, reqId, errorCode, errorString, contract):
        """Handle error events from IBKR."""
        # Error code 502 = Couldn't connect to TWS. Valid id is -1.
        # Error code 504 = Not connected
        # Error code 1100 = Connectivity between IB and TWS has been lost
        # Error code 1101 = Connectivity between IB and TWS has been restored
        # Error code 1102 = Not connected
        # Error code 2119 = A socket connection was established to the server, but the login process failed
        # Error code 2104 = A market data farm is connected
        # Error code 2106 = A historical data farm connection is OK
        
        if errorCode in [502, 504, 1100, 1102]:
            logger.warning(f"IBKR connection error (code {errorCode}): {errorString}")
            self.connected = False
        elif errorCode == 2119:
            logger.error(f"IBKR login failed (code {errorCode}): {errorString}")
            logger.error("Please check TWS/Gateway and approve the connection request")
            self.connected = False
        elif errorCode == 1101:
            logger.info(f"IBKR connection restored (code {errorCode}): {errorString}")
            self.connected = True
        elif errorCode in [2104, 2106]:
            # These are informational messages, not errors
            logger.debug(f"IBKR info (code {errorCode}): {errorString}")
        elif errorCode > 2000:
            # Server errors (2000+) are usually informational
            logger.debug(f"IBKR server message (code {errorCode}): {errorString}")
        else:
            # Other errors
            logger.warning(f"IBKR error (code {errorCode}): {errorString}")
        
    async def connect(self) -> bool:
        """Connect to IBKR with circuit breaker protection."""
        def _connect():
            # This will be called by circuit breaker
            return self._connect_impl()
        
        try:
            if ibkr_circuit_breaker:
                return ibkr_circuit_breaker.call(_connect)
            else:
                # Fallback if circuit breaker not available
                return self._connect_impl()
        except Exception as e:
            logger.error(f"Circuit breaker prevented connection: {e}")
            return False
    
    async def _connect_impl(self) -> bool:
        """Connect to IBKR TWS/Gateway.
        
        Note: When connecting, TWS/Gateway will show a popup asking you to
        confirm the connection. You must approve this in TWS/Gateway for the
        connection to succeed.
        """
        if self.connected and self.ib.isConnected():
            return True
        
        # Ensure event handlers are set up
        self._setup_event_handlers()
        
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Attempting to connect to IBKR at {settings.ibkr.host}:{settings.ibkr.port} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                logger.info(
                    "NOTE: If this is the first connection, TWS/Gateway will show a popup. "
                    "Please approve the connection in TWS/Gateway."
                )
                
                await self.ib.connectAsync(
                    host=settings.ibkr.host,
                    port=settings.ibkr.port,
                    clientId=settings.ibkr.client_id,
                    timeout=settings.ibkr.timeout
                )
                
                # Wait a moment for connection to fully establish
                await asyncio.sleep(0.5)
                
                # Verify connection is actually established
                if self.ib.isConnected():
                    self.connected = True
                    self.connection_attempts = 0
                    logger.info("Successfully connected to IBKR")
                    return True
                else:
                    logger.warning("Connection call succeeded but connection not established")
                    self.connected = False
                    
            except Exception as e:
                self.connection_attempts += 1
                error_msg = str(e)
                
                # Check if error is related to login/connection
                if "login" in error_msg.lower() or "connection" in error_msg.lower():
                    logger.warning(
                        f"Connection attempt {attempt + 1} failed: {e}\n"
                        "This may be because:\n"
                        "1. TWS/Gateway is not running\n"
                        "2. The connection request was not approved in TWS/Gateway\n"
                        "3. The port number is incorrect\n"
                        "4. API access is not enabled in TWS/Gateway settings"
                    )
                else:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Failed to connect to IBKR after all retries")
                    return False
        
        return False
    
    async def ensure_connected(self) -> bool:
        """Ensure connection is active, reconnect if necessary."""
        # Check both our internal state and the actual IB connection status
        if not self.connected or not self.ib.isConnected():
            logger.info("Connection lost or not established, attempting to reconnect...")
            self.connected = False
            return await self.connect()
        return True
    
    async def disconnect(self):
        """Disconnect from IBKR."""
        if self.connected:
            try:
                self.ib.disconnect()
                self.connected = False
                logger.info("Disconnected from IBKR")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
    
    async def get_account_summary(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get account summary."""
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        try:
            account_values = self.ib.accountValues(account_id)
            
            summary = {}
            for av in account_values:
                if av.tag in ['TotalCashValue', 'NetLiquidation', 'BuyingPower', 
                             'GrossPositionValue', 'AvailableFunds', 'ExcessLiquidity']:
                    try:
                        summary[av.tag] = float(av.value)
                    except (ValueError, TypeError):
                        summary[av.tag] = av.value
            
            # Get account ID if not provided
            if account_id is None and account_values:
                summary['AccountId'] = account_values[0].account
            
            return summary
            
        except Exception as e:
            logger.error(f"Error fetching account summary: {e}")
            raise
    
    async def get_positions(self, account_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get current positions with market data using portfolio().
        
        Uses ib.portfolio() which returns PortfolioItem objects that already contain
        marketPrice, marketValue, and unrealizedPnL from IBKR.
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        try:
            # Use portfolio() which returns PortfolioItem with market data included
            portfolio_items = self.ib.portfolio(account_id)
            
            result = []
            for item in portfolio_items:
                position_data = {
                    'account': item.account,
                    'contract': {
                        'symbol': item.contract.symbol,
                        'secType': item.contract.secType,
                        'currency': item.contract.currency,
                        'exchange': item.contract.exchange or item.contract.primaryExchange,
                    },
                    'position': item.position,
                    'avgCost': float(item.averageCost) if item.averageCost else 0.0,
                    'marketPrice': float(item.marketPrice) if item.marketPrice else None,
                    'marketValue': float(item.marketValue) if item.marketValue else None,
                    'unrealizedPnL': float(item.unrealizedPNL) if item.unrealizedPNL else None,
                }
                
                logger.debug(
                    f"Position {item.contract.symbol}: "
                    f"qty={item.position}, avgCost={item.averageCost}, "
                    f"marketPrice={item.marketPrice}, marketValue={item.marketValue}, "
                    f"unrealizedPnL={item.unrealizedPNL}"
                )
                
                result.append(position_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    async def get_pnl(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get PnL information using portfolio data for accurate unrealized PnL.
        
        Uses ib.portfolio() to get accurate unrealized PnL from IBKR,
        and calculates realized PnL from the difference.
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        try:
            account_summary = await self.get_account_summary(account_id)
            
            # Use portfolio() which has accurate market data and unrealized PnL
            portfolio_items = self.ib.portfolio(account_id)
            
            # Calculate total unrealized PnL from portfolio items
            total_unrealized_pnl = sum(
                float(item.unrealizedPNL) if item.unrealizedPNL else 0.0
                for item in portfolio_items
            )
            
            net_liquidation = account_summary.get('NetLiquidation', 0)
            total_cash = account_summary.get('TotalCashValue', 0)
            gross_position_value = account_summary.get('GrossPositionValue', 0)
            
            # Calculate realized PnL
            # Realized PnL = NetLiquidation - TotalCash - GrossPositionValue + (GrossPositionValue - Cost basis)
            # Simplified: NetLiquidation - TotalCash - UnrealizedPnL gives approximately realized + cost basis
            # More accurate: use the difference between current value and cost
            total_cost_basis = sum(
                float(item.averageCost) * float(item.position) if item.averageCost else 0.0
                for item in portfolio_items
            )
            
            # Realized PnL = NetLiquidation - TotalCash - TotalCostBasis - UnrealizedPnL
            # This represents profits/losses from closed positions
            realized_pnl = net_liquidation - total_cash - total_cost_basis - total_unrealized_pnl
            
            # Total PnL = Realized + Unrealized
            total_pnl = realized_pnl + total_unrealized_pnl
            
            pnl = {
                'accountId': account_summary.get('AccountId') or account_id,
                'netLiquidation': net_liquidation,
                'totalCash': total_cash,
                'unrealizedPnL': total_unrealized_pnl,
                'realizedPnL': realized_pnl,
                'totalPnL': total_pnl,
                'timestamp': time.time(),
            }

            logger.info(
                f"Computed PnL snapshot: netLiq=${net_liquidation:,.2f}, "
                f"unrealizedPnL=${total_unrealized_pnl:,.2f}, "
                f"realizedPnL=${realized_pnl:,.2f}, totalPnL=${total_pnl:,.2f}"
            )

            return pnl
            
        except Exception as e:
            logger.error(f"Error fetching PnL: {e}")
            raise
    
    async def get_trades(self, account_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get trade history."""
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        try:
            fills = self.ib.fills()
            
            result = []
            for fill in fills:
                if account_id and fill.execution.account != account_id:
                    continue
                
                trade_data = {
                    'account': fill.execution.account,
                    'contract': {
                        'symbol': fill.contract.symbol,
                        'secType': fill.contract.secType,
                        'currency': fill.contract.currency,
                    },
                    'execution': {
                        'execId': fill.execution.execId,
                        'time': fill.execution.time.isoformat() if fill.execution.time else None,
                        'side': fill.execution.side,
                        'shares': float(fill.execution.shares),
                        'price': float(fill.execution.price),
                        'cumQty': float(fill.execution.cumQty),
                        'avgPrice': float(fill.execution.avgPrice),
                    },
                    'commission': float(fill.commissionReport.commission) if fill.commissionReport else 0.0,
                }
                result.append(trade_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            raise
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.connected:
            try:
                asyncio.create_task(self.disconnect())
            except:
                pass

