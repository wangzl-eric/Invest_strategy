"""IBKR API client wrapper with connection management and error handling."""
import logging
import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ib_insync import IB, Stock, Contract, AccountValue, Position, Trade, Forex, Future
from ib_insync.objects import PortfolioItem
import pandas as pd
import time

from backend.config import settings

# Import circuit breaker if available
try:
    from backend.circuit_breaker import ibkr_circuit_breaker, CircuitState
except ImportError:
    ibkr_circuit_breaker = None
    CircuitState = None

logger = logging.getLogger(__name__)


# Valid durations for historical data requests
HISTORICAL_DURATIONS = [
    "1 D", "2 D", "3 D", "4 D", "5 D", "6 D", "7 D",
    "1 W", "2 W", "3 W", "4 W",
    "1 M", "2 M", "3 M", "4 M", "5 M", "6 M",
    "1 Y", "2 Y", "3 Y", "5 Y"
]

# Valid intervals for historical data
HISTORICAL_INTERVALS = [
    "1 secs", "5 secs", "10 secs", "15 secs", "30 secs",
    "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins",
    "1 hour", "2 hours", "3 hours", "4 hours", "8 hours",
    "1 day", "1 week", "1 month"
]


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
        try:
            if ibkr_circuit_breaker:
                # Check if circuit is open before attempting async connect
                if ibkr_circuit_breaker.state.value == "open":
                    from datetime import datetime as _dt
                    if ibkr_circuit_breaker.last_failure_time:
                        elapsed = (_dt.utcnow() - ibkr_circuit_breaker.last_failure_time).total_seconds()
                        if elapsed < ibkr_circuit_breaker.recovery_timeout:
                            logger.warning(f"Circuit breaker OPEN — retry in {int(ibkr_circuit_breaker.recovery_timeout - elapsed)}s")
                            return False
                        ibkr_circuit_breaker.state = CircuitState.HALF_OPEN

                result = await self._connect_impl()

                if ibkr_circuit_breaker:
                    if result:
                        ibkr_circuit_breaker.failure_count = 0
                        if ibkr_circuit_breaker.state.value == "half_open":
                            ibkr_circuit_breaker.success_count += 1
                            if ibkr_circuit_breaker.success_count >= 2:
                                ibkr_circuit_breaker.state = CircuitState.CLOSED
                    else:
                        ibkr_circuit_breaker.failure_count += 1
                        from datetime import datetime as _dt
                        ibkr_circuit_breaker.last_failure_time = _dt.utcnow()
                        if ibkr_circuit_breaker.failure_count >= ibkr_circuit_breaker.failure_threshold:
                            ibkr_circuit_breaker.state = CircuitState.OPEN
                            logger.warning(f"Circuit breaker OPEN after {ibkr_circuit_breaker.failure_count} failures")

                return result
            else:
                return await self._connect_impl()
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
                
                # Wait for connection + initial account data subscription
                await asyncio.sleep(1)
                
                # Verify connection is actually established
                if self.ib.isConnected():
                    self.connected = True
                    self.connection_attempts = 0
                    logger.info("Successfully connected to IBKR")

                    # Wait for account data to arrive (TWS streams it after connect)
                    for _wait in range(10):
                        if self.ib.accountValues():
                            logger.info("Account data is ready")
                            break
                        await asyncio.sleep(0.5)
                    else:
                        logger.warning("Account data not received within 5 s — queries may return empty results")

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
            
            # Fallback to configured account ID from env / config
            if 'AccountId' not in summary and account_id:
                summary['AccountId'] = account_id
            if 'AccountId' not in summary:
                env_acct = os.getenv('IBKR_ACCOUNT_ID', '') or getattr(settings.ibkr, 'account_id', '')
                if env_acct:
                    summary['AccountId'] = env_acct
                    logger.info(f"Using configured IBKR_ACCOUNT_ID: {env_acct}")
            
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

    # --------------------------------------------------------------------------
    # Historical Data Methods
    # --------------------------------------------------------------------------

    def _create_contract(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        expiry: Optional[str] = None,
        strike: Optional[float] = None,
        opt_type: Optional[str] = None
    ) -> Contract:
        """Create an IBKR contract object."""
        if sec_type == "STK":
            contract = Stock(symbol, exchange, currency)
        elif sec_type == "CASH":
            contract = Forex(symbol, exchange, currency)
        elif sec_type == "FUT":
            contract = Future(symbol, exchange, currency, expiry)
        elif sec_type in ["OPT", "FOP"]:
            contract = Stock(symbol, exchange, currency)  # Base for options
            # Note: Options require more complex contract specification
            # For options, use get_options_chain() instead
        else:
            contract = Stock(symbol, exchange, currency)
        
        return contract

    async def get_historical_data(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        duration: str = "1 Y",
        interval: str = "1 day",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        outside_rth: bool = False
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data from IBKR.
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL", "EUR/USD")
            sec_type: Security type - "STK" (stock), "CASH" (forex), "FUT" (future)
            exchange: Exchange (e.g., "SMART", "IDEALPRO" for forex, "CME" for futures)
            currency: Currency (e.g., "USD", "EUR")
            duration: How far back - "1 D", "1 W", "1 M", "1 Y", "2 Y", etc.
            interval: Bar size - "1 min", "5 mins", "1 hour", "1 day", etc.
            start_date: Start date for historical data (optional, overrides duration)
            end_date: End date for historical data (optional, defaults to now)
            outside_rth: Include data outside regular trading hours
            
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        # Validate duration and interval
        if duration not in HISTORICAL_DURATIONS:
            logger.warning(f"Invalid duration '{duration}', using '1 Y'. Valid: {HISTORICAL_DURATIONS}")
            duration = "1 Y"
        
        if interval not in HISTORICAL_INTERVALS:
            logger.warning(f"Invalid interval '{interval}', using '1 day'. Valid: {HISTORICAL_INTERVALS}")
            interval = "1 day"
        
        # Create contract
        contract = self._create_contract(symbol, sec_type, exchange, currency)
        
        # Add generic ticks to request
        # For stocks: whatToShow='TRADES', 'MIDPOINT', 'BID', 'ASK', 'BID_ASK'
        what_to_show = 'TRADES'
        if sec_type == 'CASH':
            what_to_show = 'MIDPOINT'  # Forex doesn't have trades in the same way
        
        try:
            # Use reqHistoricalDataAsync for historical data
            bars = await self.ib.reqHistoricalDataAsync(
                contract=contract,
                endDateTime=end_date.strftime('%Y%m%d %H:%M:%S') if end_date else '',
                durationStr=duration,
                barSizeSetting=interval,
                whatToShow=what_to_show,
                useRTH=not outside_rth,
                formatDate=2  # Unix timestamp format
            )
            
            if not bars:
                logger.warning(f"No historical data returned for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
            } for bar in bars])
            
            # Filter by date range if specified
            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]
            
            logger.info(f"Fetched {len(df)} bars for {symbol} ({sec_type})")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    async def get_realtime_bars(
        self,
        symbol: str,
        sec_type: str = "STK",
        exchange: str = "SMART",
        currency: str = "USD",
        duration: str = "5 D",
        interval: str = "1 min"
    ) -> pd.DataFrame:
        """Fetch real-time (live) bars from IBKR.
        
        This is similar to historical data but uses the real-time data farm.
        Useful for getting the most recent data quickly.
        
        Args:
            symbol: Ticker symbol
            sec_type: Security type
            exchange: Exchange
            currency: Currency
            duration: How far back
            interval: Bar size
            
        Returns:
            DataFrame with OHLCV data
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        contract = self._create_contract(symbol, sec_type, exchange, currency)
        
        try:
            bars = await self.ib.reqHistoricalDataAsync(
                contract=contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=interval,
                whatToShow='TRADES',
                useRTH=False,
                formatDate=2,
                keepUpToDate=True  # Request real-time updates
            )
            
            if not bars:
                return pd.DataFrame()
            
            df = pd.DataFrame([{
                'date': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
            } for bar in bars])
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching realtime bars for {symbol}: {e}")
            raise

    async def get_quote(self, symbol: str, sec_type: str = "STK", exchange: str = "SMART", currency: str = "USD") -> Dict[str, Any]:
        """Get current quote for a symbol.
        
        Args:
            symbol: Ticker symbol
            sec_type: Security type
            exchange: Exchange
            currency: Currency
            
        Returns:
            Dict with bid, ask, last, volume, etc.
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        contract = self._create_contract(symbol, sec_type, exchange, currency)
        
        # Request market data
        ticker = await self.ib.reqMktDataAsync(contract, '', False, False)
        
        # Wait briefly for data to arrive
        await asyncio.sleep(0.5)
        
        return {
            'symbol': symbol,
            'bid': ticker.bid,
            'ask': ticker.ask,
            'last': ticker.last,
            'bid_size': ticker.bidSize,
            'ask_size': ticker.askSize,
            'last_size': ticker.lastSize,
            'volume': ticker.volume,
            'close': ticker.close,
            'high': ticker.high,
            'low': ticker.low,
            'timestamp': datetime.now().isoformat()
        }

    async def search_symbols(self, symbol: str, exchange: str = "SMART") -> List[Dict[str, Any]]:
        """Search for symbols in IBKR database.
        
        Args:
            symbol: Search pattern (can be partial)
            exchange: Exchange to search in
            
        Returns:
            List of matching contracts with details
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        try:
            # Use IB's symbol search
            contracts = await self.ib.reqMatchingSymbolsAsync(symbol)
            
            results = []
            for contract in contracts:
                results.append({
                    'symbol': contract.symbol,
                    'sec_type': contract.secType,
                    'exchange': contract.exchange,
                    'currency': contract.currency,
                    'description': contract.description,
                    'contract_id': contract.conId
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching symbols for {symbol}: {e}")
            return []

    async def get_contract_details(self, symbol: str, exchange: str = "SMART", currency: str = "USD") -> List[Dict[str, Any]]:
        """Get detailed contract information.
        
        Args:
            symbol: Ticker symbol
            exchange: Exchange
            currency: Currency
            
        Returns:
            List of contract details (may include multiple contracts like options)
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        contract = Stock(symbol, exchange, currency)
        
        try:
            details = await self.ib.reqContractDetailsAsync(contract)
            
            results = []
            for detail in details:
                results.append({
                    'contract_id': detail.contract.conId,
                    'symbol': detail.contract.symbol,
                    'sec_type': detail.contract.secType,
                    'exchange': detail.contract.exchange,
                    'primary_exchange': detail.contract.primaryExchange,
                    'currency': detail.contract.currency,
                    'strike': detail.contract.strike,
                    'expiry': detail.contract.lastTradeDateOrContractMonth,
                    'right': detail.contract.right,
                    'multiplier': detail.contract.multiplier,
                    'market_name': detail.marketName,
                    'min_tick': detail.minTick,
                    'order_types': detail.orderTypes,
                    'valid_exchanges': detail.validExchanges,
                    'long_name': detail.longName,
                    'industry': detail.industry,
                    'category': detail.category,
                    'subcategory': detail.subcategory
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting contract details for {symbol}: {e}")
            return []

    async def get_options_chain(
        self,
        underlying_symbol: str,
        exchange: str = "SMART",
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get options chain for an underlying symbol.
        
        Args:
            underlying_symbol: Stock symbol (e.g., "AAPL")
            exchange: Exchange
            currency: Currency
            
        Returns:
            Dict with expiry dates and strikes for calls and puts
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        # Get contract details to find the contract ID
        details = await self.get_contract_details(underlying_symbol, exchange, currency)
        
        if not details:
            logger.warning(f"No contract details found for {underlying_symbol}")
            return {}
        
        contract_id = details[0]['contract_id']
        
        # Request options chains
        try:
            # Request security definition options parameters
            chains = await self.ib.reqSecDefOptParamsAsync(
                underlyingSymbol=underlying_symbol,
                exchange=exchange,
                secType='STK',
                underlyingConId=contract_id
            )
            
            if not chains:
                logger.warning(f"No options chain found for {underlying_symbol}")
                return {}
            
            result = {
                'underlying': underlying_symbol,
                'exchanges': [],
                'expirations': set(),
                'strikes': set(),
                'chains': []
            }
            
            for chain in chains:
                result['exchanges'].append(chain.exchange)
                
                for expiry in chain.expirations:
                    result['expirations'].add(expiry)
                
                for strike in chain.strikes:
                    result['strikes'].add(strike)
                
                result['chains'].append({
                    'exchange': chain.exchange,
                    'expirations': list(chain.expirations),
                    'strikes': list(chain.strikes),
                    'underlying_con_id': chain.underlyingConId,
                    'trading_class': chain.tradingClass
                })
            
            # Convert sets to sorted lists for JSON serialization
            result['expirations'] = sorted(list(result['expirations']))
            result['strikes'] = sorted([float(s) for s in result['strikes']])
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting options chain for {underlying_symbol}: {e}")
            return {}

    async def get_futures_chain(
        self,
        symbol: str,
        exchange: str = "CME",
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get futures chain for a symbol (e.g., "ES" for E-mini S&P 500).
        
        Args:
            symbol: Futures symbol (e.g., "ES", "CL", "GC")
            exchange: Exchange (e.g., "CME", "NYMEX", "COMEX")
            currency: Currency
            
        Returns:
            Dict with available contract months
        """
        if not await self.ensure_connected():
            raise ConnectionError("Not connected to IBKR")
        
        contract = Future(symbol, exchange, currency)
        
        try:
            details = await self.ib.reqContractDetailsAsync(contract)
            
            expirations = set()
            contracts = []
            
            for detail in details:
                if detail.contract.lastTradeDateOrContractMonth:
                    expirations.add(detail.contract.lastTradeDateOrContractMonth)
                    contracts.append({
                        'contract_id': detail.contract.conId,
                        'symbol': detail.contract.symbol,
                        'exchange': detail.contract.exchange,
                        'expiry': detail.contract.lastTradeDateOrContractMonth,
                        'multiplier': detail.contract.multiplier,
                        'long_name': detail.longName
                    })
            
            return {
                'symbol': symbol,
                'exchange': exchange,
                'currency': currency,
                'expirations': sorted(list(expirations)),
                'contracts': contracts
            }
            
        except Exception as e:
            logger.error(f"Error getting futures chain for {symbol}: {e}")
            return {}

    def __del__(self):
        """Cleanup on deletion."""
        if self.connected:
            try:
                asyncio.create_task(self.disconnect())
            except:
                pass

