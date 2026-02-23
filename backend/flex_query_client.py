"""IBKR Flex Query Web Service Client.

Fetches historical trade data, positions, and account information
via IBKR's Flex Query Web Service API.

Supports both XML and CSV/TSV response formats.

Usage:
    from backend.flex_query_client import FlexQueryClient
    
    client = FlexQueryClient(token="your_flex_token")
    trades = await client.fetch_trades(query_id="123456")
"""
import logging
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from pathlib import Path
import os
import aiohttp
import pandas as pd

logger = logging.getLogger(__name__)


class FlexQueryStatus(Enum):
    """Status codes from Flex Query API."""
    SUCCESS = "Success"
    WARN = "Warn"
    FAIL = "Fail"


@dataclass
class FlexTrade:
    """Parsed trade from Flex Query response."""
    account_id: str
    trade_id: str
    exec_id: str
    symbol: str
    description: str
    sec_type: str  # STK, OPT, FUT, etc.
    currency: str
    exchange: str
    
    # Trade details
    trade_date: datetime
    settle_date: Optional[datetime]
    trade_time: Optional[str]
    side: str  # BUY, SELL
    quantity: float
    price: float
    proceeds: float  # Negative for buys, positive for sells
    
    # Cost and P&L
    commission: float
    tax: float
    cost_basis: float
    realized_pnl: float
    
    # Additional info
    order_type: Optional[str] = None
    asset_category: Optional[str] = None
    underlying_symbol: Optional[str] = None
    multiplier: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            'account_id': self.account_id,
            'exec_id': self.exec_id or self.trade_id,
            'exec_time': self.trade_date,
            'symbol': self.symbol,
            'sec_type': self.sec_type,
            'currency': self.currency,
            'side': self.side,
            'shares': abs(self.quantity),
            'price': self.price,
            'avg_price': self.price,
            'cum_qty': abs(self.quantity),
            'commission': self.commission,
            'realized_pnl': self.realized_pnl,
        }


@dataclass
class FlexPosition:
    """Parsed position from Flex Query response."""
    account_id: str
    symbol: str
    description: str
    sec_type: str
    currency: str
    
    quantity: float
    cost_basis_price: float
    cost_basis_money: float
    market_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    
    report_date: datetime
    asset_category: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'symbol': self.symbol,
            'sec_type': self.sec_type,
            'currency': self.currency,
            'quantity': self.quantity,
            'avg_cost': self.cost_basis_price,
            'market_price': self.market_price,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl,
        }


@dataclass
class FlexCashTransaction:
    """Parsed cash transaction from Flex Query response."""
    account_id: str
    transaction_id: str
    date: datetime
    currency: str
    amount: float
    transaction_type: str  # Deposits, Withdrawals, Dividends, etc.
    description: str
    symbol: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'transaction_id': self.transaction_id,
            'date': self.date,
            'currency': self.currency,
            'amount': self.amount,
            'type': self.transaction_type,
            'description': self.description,
            'symbol': self.symbol,
        }


@dataclass  
class FlexQueryResult:
    """Complete result from a Flex Query."""
    account_id: str
    from_date: datetime
    to_date: datetime
    generated_at: datetime
    
    trades: List[FlexTrade] = field(default_factory=list)
    positions: List[FlexPosition] = field(default_factory=list)
    cash_transactions: List[FlexCashTransaction] = field(default_factory=list)
    
    # Account summary
    net_liquidation: Optional[float] = None
    total_cash: Optional[float] = None
    
    # Raw response storage
    raw_xml: Optional[str] = None
    saved_file_path: Optional[str] = None  # Path where raw response was saved


class FlexQueryError(Exception):
    """Exception raised for Flex Query errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FlexQueryClient:
    """Client for IBKR Flex Query Web Service.
    
    The Flex Query process has two steps:
    1. Send request with token and query ID → get reference code
    2. Fetch statement using reference code → get XML data
    """
    
    BASE_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService"
    
    # Retry settings
    MAX_RETRIES = 15  # Increased for CSV format (may take longer to generate)
    RETRY_DELAY = 3  # seconds between retries
    CSV_RETRY_DELAY = 6  # Longer delay when waiting for CSV format
    STATEMENT_READY_WAIT = 5  # seconds to wait before first fetch attempt
    
    def __init__(self, token: str, timeout: int = 60):
        """Initialize Flex Query client.
        
        Args:
            token: Flex Web Service token from IBKR Account Management
            timeout: Request timeout in seconds
        """
        self.token = token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def _send_request(
        self, 
        query_id: str,
        session: aiohttp.ClientSession
    ) -> str:
        """Step 1: Send request to generate report.
        
        Returns:
            Reference code to fetch the statement
        """
        url = f"{self.BASE_URL}.SendRequest"
        params = {
            't': self.token,
            'q': query_id,
            'v': '3'  # API version
        }
        
        logger.info(f"Sending Flex Query request for query_id={query_id}")
        
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            xml_text = await response.text()
        
        # Parse response XML
        root = ET.fromstring(xml_text)
        
        status = root.find('Status')
        if status is None or status.text != 'Success':
            error_code = root.find('ErrorCode')
            error_msg = root.find('ErrorMessage')
            raise FlexQueryError(
                f"Flex Query request failed: {error_msg.text if error_msg is not None else 'Unknown error'}",
                error_code.text if error_code is not None else None
            )
        
        reference_code = root.find('ReferenceCode')
        if reference_code is None or not reference_code.text:
            raise FlexQueryError("No reference code in response")
        
        logger.info(f"Got reference code: {reference_code.text}")
        return reference_code.text
    
    async def _get_statement(
        self,
        reference_code: str,
        session: aiohttp.ClientSession,
        prefer_csv: bool = True
    ) -> str:
        """Step 2: Fetch the generated statement.
        
        Args:
            reference_code: Reference code from SendRequest
            session: aiohttp session
            prefer_csv: If True, try to request CSV format (if supported by API)
        
        Returns:
            Statement data (XML or CSV format)
        """
        url = f"{self.BASE_URL}.GetStatement"
        params = {
            't': self.token,
            'q': reference_code,
            'v': '3'
        }
        
        # Try to request CSV format if supported (some IBKR API versions support 'type' parameter)
        if prefer_csv:
            params['type'] = 'CSV'  # Request CSV format
        
        for attempt in range(self.MAX_RETRIES):
            logger.info(f"Fetching statement (attempt {attempt + 1}/{self.MAX_RETRIES})")
            
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                response_text = await response.text()
            
            # Check if response is CSV format (starts with column headers in quotes or comma-separated)
            # CSV can be tab-separated (TSV) or comma-separated
            is_csv = (
                (response_text.startswith('"') and ('\t' in response_text[:200] or ',' in response_text[:200])) or
                (len(response_text) > 100 and ',' in response_text[:200] and not response_text.strip().startswith('<'))
            )
            
            if is_csv:
                logger.info("Statement retrieved successfully (CSV format)")
                return response_text
            
            # Check if statement is XML format
            if response_text.startswith('<FlexQueryResponse') or response_text.startswith('<FlexStatementResponse'):
                # IMPORTANT: XML responses can be either the final report OR a small status payload
                # like: <Status>Warn</Status><ErrorCode>1019</ErrorCode> (still generating).
                root = ET.fromstring(response_text)

                status = root.find('.//Status') or root.find('Status')
                error_code = root.find('.//ErrorCode') or root.find('ErrorCode')
                error_msg = root.find('.//ErrorMessage') or root.find('ErrorMessage')

                # Hard failure
                if status is not None and status.text == 'Fail':
                    raise FlexQueryError(
                        f"Statement fetch failed: {error_msg.text if error_msg is not None else 'Unknown error'}",
                        error_code.text if error_code is not None else None
                    )

                # Still generating
                if status is not None and status.text == 'Warn' and error_code is not None and error_code.text == '1019':
                    wait_time = self.CSV_RETRY_DELAY if prefer_csv else self.RETRY_DELAY
                    logger.info(
                        f"Statement still generating (XML Warn 1019; waiting for report), waiting {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                    continue

                # Otherwise: treat as final XML report
                logger.info("Statement retrieved successfully (XML format)")
                return response_text
            
            # Check if still generating (small XML response with status)
            try:
                root = ET.fromstring(response_text)
                status = root.find('Status')
                if status is not None and status.text == 'Warn':
                    error_code = root.find('ErrorCode')
                    if error_code is not None and error_code.text == '1019':
                        # Statement still being generated - wait longer if we prefer CSV
                        wait_time = self.CSV_RETRY_DELAY if prefer_csv else self.RETRY_DELAY
                        logger.info(f"Statement still generating (waiting for CSV format), waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    # Other warning - log it
                    error_msg = root.find('ErrorMessage')
                    logger.warning(f"Flex Query warning: {error_msg.text if error_msg is not None else 'Unknown'}")
                elif status is not None and status.text == 'Fail':
                    error_msg = root.find('ErrorMessage')
                    raise FlexQueryError(
                        f"Statement fetch failed: {error_msg.text if error_msg is not None else 'Unknown error'}"
                    )
            except ET.ParseError:
                # Not XML - might be CSV or other format
                # If it's a substantial response (not a small error message), accept it
                if len(response_text) > 500:
                    logger.info(f"Statement retrieved (non-XML format, {len(response_text)} bytes)")
                    return response_text
            
            # Unexpected response
            logger.warning(f"Unexpected response ({len(response_text)} bytes), retrying in {self.RETRY_DELAY}s...")
            await asyncio.sleep(self.RETRY_DELAY)
        
        raise FlexQueryError(f"Failed to fetch statement after {self.MAX_RETRIES} attempts")
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from Flex Query."""
        if not date_str:
            return None
        
        # Try different formats
        formats = [
            '%Y%m%d',           # 20231215
            '%Y-%m-%d',         # 2023-12-15
            '%Y%m%d;%H%M%S',    # 20231215;143052
            '%Y-%m-%d %H:%M:%S' # 2023-12-15 14:30:52
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _parse_float(self, value: Optional[str]) -> float:
        """Parse float value, handling empty strings."""
        if not value or value.strip() == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_trades(self, root: ET.Element, account_id: str) -> List[FlexTrade]:
        """Parse trades from Flex Query XML."""
        trades = []
        
        # Find all Trade elements (may be nested under Trades or directly under FlexStatement)
        for trade_elem in root.findall('.//Trade'):
            try:
                # Get trade attributes
                attrs = trade_elem.attrib
                
                # Skip if not a trade execution
                level_of_detail = attrs.get('levelOfDetail', '')
                if level_of_detail and level_of_detail not in ['EXECUTION', 'ORDER']:
                    continue
                
                trade = FlexTrade(
                    account_id=attrs.get('accountId', account_id),
                    trade_id=attrs.get('tradeID', ''),
                    exec_id=attrs.get('ibExecID', attrs.get('tradeID', '')),
                    symbol=attrs.get('symbol', ''),
                    description=attrs.get('description', ''),
                    sec_type=attrs.get('assetCategory', 'STK'),
                    currency=attrs.get('currency', 'USD'),
                    exchange=attrs.get('exchange', ''),
                    trade_date=self._parse_date(attrs.get('tradeDate')) or datetime.now(),
                    settle_date=self._parse_date(attrs.get('settleDateTarget')),
                    trade_time=attrs.get('tradeTime'),
                    side='BUY' if self._parse_float(attrs.get('quantity', '0')) > 0 else 'SELL',
                    quantity=self._parse_float(attrs.get('quantity', '0')),
                    price=self._parse_float(attrs.get('tradePrice', '0')),
                    proceeds=self._parse_float(attrs.get('proceeds', '0')),
                    commission=self._parse_float(attrs.get('ibCommission', '0')),
                    tax=self._parse_float(attrs.get('taxes', '0')),
                    cost_basis=self._parse_float(attrs.get('cost', '0')),
                    realized_pnl=self._parse_float(attrs.get('fifoPnlRealized', '0')),
                    order_type=attrs.get('orderType'),
                    asset_category=attrs.get('assetCategory'),
                    underlying_symbol=attrs.get('underlyingSymbol'),
                    multiplier=self._parse_float(attrs.get('multiplier', '1')) or 1.0,
                )
                
                # Combine trade date and time if available
                if trade.trade_time and trade.trade_date:
                    try:
                        time_parts = trade.trade_time.split(':')
                        if len(time_parts) >= 2:
                            trade.trade_date = trade.trade_date.replace(
                                hour=int(time_parts[0]),
                                minute=int(time_parts[1]),
                                second=int(time_parts[2]) if len(time_parts) > 2 else 0
                            )
                    except (ValueError, IndexError):
                        pass
                
                trades.append(trade)
                
            except Exception as e:
                logger.warning(f"Error parsing trade element: {e}")
                continue
        
        logger.info(f"Parsed {len(trades)} trades from Flex Query")
        return trades
    
    def _parse_positions(self, root: ET.Element, account_id: str) -> List[FlexPosition]:
        """Parse positions from Flex Query XML."""
        positions = []
        
        for pos_elem in root.findall('.//OpenPosition'):
            try:
                attrs = pos_elem.attrib
                
                position = FlexPosition(
                    account_id=attrs.get('accountId', account_id),
                    symbol=attrs.get('symbol', ''),
                    description=attrs.get('description', ''),
                    sec_type=attrs.get('assetCategory', 'STK'),
                    currency=attrs.get('currency', 'USD'),
                    quantity=self._parse_float(attrs.get('position', '0')),
                    cost_basis_price=self._parse_float(attrs.get('costBasisPrice', '0')),
                    cost_basis_money=self._parse_float(attrs.get('costBasisMoney', '0')),
                    market_price=self._parse_float(attrs.get('markPrice', '0')),
                    market_value=self._parse_float(attrs.get('positionValue', '0')),
                    unrealized_pnl=self._parse_float(attrs.get('fifoPnlUnrealized', '0')),
                    realized_pnl=self._parse_float(attrs.get('fifoPnlRealized', '0')),
                    report_date=self._parse_date(attrs.get('reportDate')) or datetime.now(),
                    asset_category=attrs.get('assetCategory'),
                )
                
                positions.append(position)
                
            except Exception as e:
                logger.warning(f"Error parsing position element: {e}")
                continue
        
        logger.info(f"Parsed {len(positions)} positions from Flex Query")
        return positions
    
    def _parse_cash_transactions(self, root: ET.Element, account_id: str) -> List[FlexCashTransaction]:
        """Parse cash transactions from Flex Query XML."""
        transactions = []
        
        for trans_elem in root.findall('.//CashTransaction'):
            try:
                attrs = trans_elem.attrib
                
                transaction = FlexCashTransaction(
                    account_id=attrs.get('accountId', account_id),
                    transaction_id=attrs.get('transactionID', ''),
                    date=self._parse_date(attrs.get('dateTime') or attrs.get('reportDate')) or datetime.now(),
                    currency=attrs.get('currency', 'USD'),
                    amount=self._parse_float(attrs.get('amount', '0')),
                    transaction_type=attrs.get('type', ''),
                    description=attrs.get('description', ''),
                    symbol=attrs.get('symbol'),
                )
                
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Error parsing cash transaction element: {e}")
                continue
        
        logger.info(f"Parsed {len(transactions)} cash transactions from Flex Query")
        return transactions
    
    def _parse_account_info(self, root: ET.Element) -> Dict[str, Any]:
        """Parse account information from Flex Query XML."""
        info = {}
        
        # Look for EquitySummaryInBase or similar elements
        equity_elem = root.find('.//EquitySummaryInBase')
        if equity_elem is not None:
            attrs = equity_elem.attrib
            info['net_liquidation'] = self._parse_float(attrs.get('total', '0'))
            info['cash'] = self._parse_float(attrs.get('cash', '0'))
        
        # Also check AccountInformation
        account_elem = root.find('.//AccountInformation')
        if account_elem is not None:
            attrs = account_elem.attrib
            info['account_id'] = attrs.get('accountId', '')
            info['account_type'] = attrs.get('accountType', '')
            info['currency'] = attrs.get('currency', 'USD')
        
        return info
    
    def _is_csv_format(self, text: str) -> bool:
        """Check if the response is in CSV/TSV format."""
        # CSV/TSV format typically starts with column headers
        # XML format starts with <?xml or <FlexQueryResponse or <FlexStatementResponse
        text = text.strip()
        return not (text.startswith('<?xml') or 
                   text.startswith('<FlexQueryResponse') or 
                   text.startswith('<FlexStatementResponse') or
                   text.startswith('<FlexStatement'))
    
    def _parse_csv_trades(self, df: pd.DataFrame, account_id: str) -> List[FlexTrade]:
        """Parse trades from CSV DataFrame."""
        trades = []
        
        # Find rows that look like trades (have TradeID or Symbol columns)
        trade_cols = ['Symbol', 'TradeID', 'IBExecID', 'Buy/Sell', 'Quantity', 'TradePrice']
        
        # Check if this looks like a trade section
        if not any(col in df.columns for col in ['Symbol', 'TradeID']):
            return trades
        
        for _, row in df.iterrows():
            try:
                # Skip rows without essential trade data
                symbol = str(row.get('Symbol', '')).strip()
                if not symbol or symbol == 'nan' or symbol == 'Symbol':
                    continue
                
                # Parse trade date
                trade_date_str = str(row.get('TradeDate', row.get('DateTime', row.get('Date', ''))))
                trade_date = self._parse_date(trade_date_str) or datetime.now()
                
                # Determine side from Buy/Sell or quantity sign
                buy_sell = str(row.get('Buy/Sell', '')).upper()
                quantity = self._parse_float(str(row.get('Quantity', '0')))
                if buy_sell in ['BUY', 'B']:
                    side = 'BUY'
                elif buy_sell in ['SELL', 'S']:
                    side = 'SELL'
                else:
                    side = 'BUY' if quantity > 0 else 'SELL'
                
                trade = FlexTrade(
                    account_id=str(row.get('ClientAccountID', row.get('AccountId', account_id))),
                    trade_id=str(row.get('TradeID', '')),
                    exec_id=str(row.get('IBExecID', row.get('ExecID', row.get('TradeID', '')))),
                    symbol=symbol,
                    description=str(row.get('Description', '')),
                    sec_type=str(row.get('AssetClass', row.get('AssetCategory', 'STK'))),
                    currency=str(row.get('CurrencyPrimary', row.get('Currency', 'USD'))),
                    exchange=str(row.get('Exchange', row.get('ListingExchange', ''))),
                    trade_date=trade_date,
                    settle_date=self._parse_date(str(row.get('SettleDateTarget', ''))),
                    trade_time=str(row.get('TradeTime', '')),
                    side=side,
                    quantity=quantity,
                    price=self._parse_float(str(row.get('TradePrice', row.get('Price', '0')))),
                    proceeds=self._parse_float(str(row.get('Proceeds', '0'))),
                    commission=self._parse_float(str(row.get('IBCommission', row.get('Commission', row.get('Commissions', '0'))))),
                    tax=self._parse_float(str(row.get('Taxes', '0'))),
                    cost_basis=self._parse_float(str(row.get('CostBasis', row.get('Cost', '0')))),
                    realized_pnl=self._parse_float(str(row.get('FifoPnlRealized', row.get('RealizedPnl', '0')))),
                    asset_category=str(row.get('AssetClass', row.get('AssetCategory', ''))),
                    multiplier=self._parse_float(str(row.get('Multiplier', '1'))) or 1.0,
                )
                
                trades.append(trade)
                
            except Exception as e:
                logger.warning(f"Error parsing CSV trade row: {e}")
                continue
        
        logger.info(f"Parsed {len(trades)} trades from CSV")
        return trades
    
    def _parse_csv_positions(self, df: pd.DataFrame, account_id: str) -> List[FlexPosition]:
        """Parse positions from CSV DataFrame."""
        positions = []
        
        # Check for position-related columns
        position_indicators = ['CloseQuantity', 'Position', 'Quantity', 'ClosePrice']
        if not any(col in df.columns for col in position_indicators):
            return positions
        
        for _, row in df.iterrows():
            try:
                symbol = str(row.get('Symbol', '')).strip()
                if not symbol or symbol == 'nan' or symbol == 'Symbol':
                    continue
                
                quantity = self._parse_float(str(row.get('CloseQuantity', row.get('Position', row.get('Quantity', '0')))))
                if quantity == 0:
                    continue
                
                position = FlexPosition(
                    account_id=str(row.get('ClientAccountID', row.get('AccountId', account_id))),
                    symbol=symbol,
                    description=str(row.get('Description', '')),
                    sec_type=str(row.get('AssetClass', row.get('AssetCategory', 'STK'))),
                    currency=str(row.get('CurrencyPrimary', row.get('Currency', 'USD'))),
                    quantity=quantity,
                    cost_basis_price=self._parse_float(str(row.get('CostBasisPrice', '0'))),
                    cost_basis_money=self._parse_float(str(row.get('CostBasisMoney', '0'))),
                    market_price=self._parse_float(str(row.get('ClosePrice', row.get('MarkPrice', '0')))),
                    market_value=self._parse_float(str(row.get('PositionValue', row.get('Value', '0')))),
                    unrealized_pnl=self._parse_float(str(row.get('FifoPnlUnrealized', row.get('UnrealizedPnl', '0')))),
                    realized_pnl=self._parse_float(str(row.get('FifoPnlRealized', row.get('RealizedPnl', '0')))),
                    report_date=self._parse_date(str(row.get('ReportDate', ''))) or datetime.now(),
                    asset_category=str(row.get('AssetClass', row.get('AssetCategory', ''))),
                )
                
                positions.append(position)
                
            except Exception as e:
                logger.warning(f"Error parsing CSV position row: {e}")
                continue
        
        logger.info(f"Parsed {len(positions)} positions from CSV")
        return positions
    
    def _parse_csv_statement(self, csv_text: str) -> FlexQueryResult:
        """Parse CSV/TSV format Flex Query response.
        
        The CSV format may contain multiple sections (tables) separated by headers.
        """
        trades = []
        positions = []
        cash_transactions = []
        account_id = ''
        from_date = datetime.now()
        to_date = datetime.now()
        net_liquidation = None
        total_cash = None
        
        # Split by double newlines or detect section breaks
        # IBKR CSV often has multiple tables concatenated
        lines = csv_text.strip().split('\n')
        
        current_section_lines = []
        sections = []
        
        for line in lines:
            # Detect new section (new header row)
            if line.startswith('"') and '\t"' in line and current_section_lines:
                # Check if this looks like a new header
                if current_section_lines and not current_section_lines[-1].startswith('"ClientAccountID'):
                    # Save current section
                    if current_section_lines:
                        sections.append('\n'.join(current_section_lines))
                    current_section_lines = []
            current_section_lines.append(line)
        
        # Don't forget the last section
        if current_section_lines:
            sections.append('\n'.join(current_section_lines))
        
        # If no clear sections, treat the whole thing as one
        if not sections:
            sections = [csv_text]
        
        # Parse each section
        for section_text in sections:
            try:
                # Try to read as TSV first, then CSV
                try:
                    df = pd.read_csv(StringIO(section_text), sep='\t', dtype=str)
                except:
                    df = pd.read_csv(StringIO(section_text), dtype=str)
                
                if df.empty:
                    continue
                
                # Extract account ID from first row if available
                if 'ClientAccountID' in df.columns and not account_id:
                    first_account = df['ClientAccountID'].dropna().iloc[0] if len(df) > 0 else ''
                    if first_account and str(first_account) != 'nan':
                        account_id = str(first_account)
                
                # Extract date range
                if 'FromDate' in df.columns and 'ToDate' in df.columns:
                    from_date_str = df['FromDate'].dropna().iloc[0] if len(df['FromDate'].dropna()) > 0 else ''
                    to_date_str = df['ToDate'].dropna().iloc[0] if len(df['ToDate'].dropna()) > 0 else ''
                    from_date = self._parse_date(str(from_date_str)) or from_date
                    to_date = self._parse_date(str(to_date_str)) or to_date
                
                # Extract net liquidation if available
                if 'EndingValue' in df.columns:
                    ending_val = df['EndingValue'].dropna().iloc[0] if len(df['EndingValue'].dropna()) > 0 else '0'
                    net_liquidation = self._parse_float(str(ending_val))
                
                # Parse trades from this section
                section_trades = self._parse_csv_trades(df, account_id)
                trades.extend(section_trades)
                
                # Parse positions from this section  
                section_positions = self._parse_csv_positions(df, account_id)
                positions.extend(section_positions)
                
            except Exception as e:
                logger.warning(f"Error parsing CSV section: {e}")
                continue
        
        result = FlexQueryResult(
            account_id=account_id,
            from_date=from_date,
            to_date=to_date,
            generated_at=datetime.now(),
            trades=trades,
            positions=positions,
            cash_transactions=cash_transactions,
            net_liquidation=net_liquidation,
            total_cash=total_cash,
            raw_xml=csv_text,
        )
        
        logger.info(f"Parsed CSV statement: {len(trades)} trades, {len(positions)} positions")
        return result
    
    def parse_statement(self, response_text: str) -> FlexQueryResult:
        """Parse complete Flex Query statement (XML or CSV format).
        
        Args:
            response_text: Raw response from Flex Query (XML or CSV)
            
        Returns:
            FlexQueryResult with all parsed data
        """
        # Detect format and parse accordingly
        if self._is_csv_format(response_text):
            logger.info("Detected CSV/TSV format response")
            return self._parse_csv_statement(response_text)
        
        # Parse as XML
        logger.info("Detected XML format response")
        root = ET.fromstring(response_text)
        
        # Get statement info
        statement = root.find('.//FlexStatement') or root
        attrs = statement.attrib if hasattr(statement, 'attrib') else {}
        
        account_id = attrs.get('accountId', '')
        from_date = self._parse_date(attrs.get('fromDate')) or datetime.now()
        to_date = self._parse_date(attrs.get('toDate')) or datetime.now()
        generated_at = self._parse_date(attrs.get('whenGenerated')) or datetime.now()
        
        # Parse all sections
        trades = self._parse_trades(root, account_id)
        positions = self._parse_positions(root, account_id)
        cash_transactions = self._parse_cash_transactions(root, account_id)
        account_info = self._parse_account_info(root)
        
        result = FlexQueryResult(
            account_id=account_id or account_info.get('account_id', ''),
            from_date=from_date,
            to_date=to_date,
            generated_at=generated_at,
            trades=trades,
            positions=positions,
            cash_transactions=cash_transactions,
            net_liquidation=account_info.get('net_liquidation'),
            total_cash=account_info.get('cash'),
            raw_xml=response_text,
        )
        
        return result
    
    def _save_raw_response(
        self, 
        response_text: str, 
        query_id: str,
        query_name: str = "",
        query_type: str = "activity"
    ) -> Optional[Path]:
        """Save the raw Flex Query response to a file.
        
        Files are organized by: data/flex_reports/{YYYY-MM-DD}/{type}/{name}_{timestamp}.ext
        
        Args:
            response_text: The raw response from Flex Query (XML or CSV)
            query_id: The query ID for naming the file
            query_name: Human-readable name for the query (e.g., "Activity Statement")
            query_type: Category for organization (e.g., "trades", "positions", "activity")
            
        Returns:
            Path to the saved file, or None if saving failed
        """
        try:
            # Determine project root and data directory
            project_root = Path(__file__).parent.parent
            
            # Organize by date and type: data/flex_reports/2026-01-10/activity/
            today = datetime.now().strftime("%Y-%m-%d")
            data_dir = project_root / "data" / "flex_reports" / today / query_type
            
            # Create directory if it doesn't exist
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            
            # Sanitize query name for filename (replace spaces/special chars)
            safe_name = query_name.replace(" ", "_").replace("/", "-") if query_name else query_id
            safe_name = "".join(c for c in safe_name if c.isalnum() or c in "_-")
            
            # Determine file extension based on content
            if response_text.strip().startswith('"') or '\t' in response_text[:100]:
                ext = "csv"
            elif response_text.strip().startswith('<'):
                ext = "xml"
            else:
                ext = "txt"
            
            filename = f"{safe_name}_{timestamp}.{ext}"
            filepath = data_dir / filename
            
            # Save the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            logger.info(f"Saved Flex Query response to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.warning(f"Failed to save Flex Query response: {e}")
            return None
    
    async def fetch_statement(
        self, 
        query_id: str, 
        query_name: str = "",
        query_type: str = "activity",
        save_raw: bool = True
    ) -> FlexQueryResult:
        """Fetch and parse a Flex Query statement.
        
        Args:
            query_id: The Flex Query ID from IBKR Account Management
            query_name: Human-readable name for the query (for file naming)
            query_type: Category for file organization (trades, positions, activity, etc.)
            save_raw: If True, save the raw response to data/flex_reports/
            
        Returns:
            FlexQueryResult with all parsed data
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            # Step 1: Request the report
            reference_code = await self._send_request(query_id, session)
            
            # Wait a bit before fetching
            # For mark-to-market queries, wait longer as CSV generation may take more time
            wait_time = self.STATEMENT_READY_WAIT * 2 if query_type == "mark-to-market" else self.STATEMENT_READY_WAIT
            logger.info(f"Waiting {wait_time}s for statement generation (query_type={query_type})...")
            await asyncio.sleep(wait_time)
            
            # Step 2: Fetch the statement (prefer CSV format, especially for mark-to-market)
            prefer_csv = query_type == "mark-to-market"  # Always prefer CSV for mark-to-market queries
            response_text = await self._get_statement(reference_code, session, prefer_csv=prefer_csv)
            
            # Step 3: Save the raw response if requested
            saved_path = None
            if save_raw:
                saved_path = self._save_raw_response(
                    response_text, 
                    query_id,
                    query_name=query_name,
                    query_type=query_type
                )
            
            # Step 4: Parse the statement
            result = self.parse_statement(response_text)
            
            # Add the saved file path to the result if available
            if save_raw and saved_path:
                result.saved_file_path = str(saved_path)
            
            return result
    
    async def fetch_trades(self, query_id: str) -> List[FlexTrade]:
        """Convenience method to fetch only trades.
        
        Args:
            query_id: Flex Query ID configured for trade data
            
        Returns:
            List of FlexTrade objects
        """
        result = await self.fetch_statement(query_id)
        return result.trades
    
    async def fetch_positions(self, query_id: str) -> List[FlexPosition]:
        """Convenience method to fetch only positions.
        
        Args:
            query_id: Flex Query ID configured for position data
            
        Returns:
            List of FlexPosition objects
        """
        result = await self.fetch_statement(query_id)
        return result.positions


# Synchronous wrapper for non-async contexts
def fetch_flex_statement_sync(token: str, query_id: str) -> FlexQueryResult:
    """Synchronous wrapper for fetching Flex Query statement.
    
    Args:
        token: Flex Web Service token
        query_id: Flex Query ID
        
    Returns:
        FlexQueryResult with all parsed data
    """
    client = FlexQueryClient(token=token)
    return asyncio.run(client.fetch_statement(query_id))
