"""
IBKR Flex Query Parser

Parses IBKR Flex Query CSV/TSV and XML reports into structured DataFrames
for trade history, performance analysis, and P&L recording.

Usage:
    from backend.flex_parser import FlexParser
    
    parser = FlexParser()
    
    # Parse a single file
    result = parser.parse_file("data/flex_reports/2026-01-10/trades/Historical_Trades.csv")
    
    # Parse all files in a directory
    all_data = parser.parse_directory("data/flex_reports")
    
    # Access DataFrames
    trades_df = result.trades
    positions_df = result.positions
    performance_df = result.performance
"""
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from io import StringIO
import glob
import re

logger = logging.getLogger(__name__)


@dataclass
class FlexParseResult:
    """Result of parsing a Flex Query file."""
    file_path: str
    account_id: str = ""
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    
    # Main DataFrames
    trades: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    positions: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    performance: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    account_summary: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    cash_transactions: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    
    # Metadata
    parse_errors: List[str] = field(default_factory=list)
    sections_found: List[str] = field(default_factory=list)


class FlexParser:
    """Parser for IBKR Flex Query reports (CSV/TSV and XML formats)."""
    
    # Column mappings for different section types
    ACCOUNT_SUMMARY_COLS = [
        'ClientAccountID', 'CurrencyPrimary', 'FromDate', 'ToDate',
        'StartingValue', 'Mtm', 'Realized', 'Dividends', 'Interest',
        'Commissions', 'EndingValue', 'TWR'
    ]
    
    POSITION_MTM_COLS = [
        'ClientAccountID', 'AssetClass', 'Symbol', 'Description', 'Conid',
        'CloseQuantity', 'ClosePrice', 'TransactionMtmPnl', 'PriorOpenMtmPnl',
        'Commissions', 'Total'
    ]
    
    TRADE_COLS = [
        'ClientAccountID', 'AssetClass', 'Symbol', 'Description', 'Conid',
        'TradeID', 'TradeDate', 'DateTime', 'Buy/Sell', 'Quantity',
        'TradePrice', 'Proceeds', 'Commissions', 'IBCommission',
        'CostBasis', 'FifoPnlRealized', 'MtmPnl', 'LevelOfDetail'
    ]
    
    def __init__(self):
        self.results: List[FlexParseResult] = []
    
    def parse_file(self, file_path: str) -> FlexParseResult:
        """Parse a single Flex Query file (CSV/TSV or XML)."""
        path = Path(file_path)
        result = FlexParseResult(file_path=str(path))
        
        if not path.exists():
            result.parse_errors.append(f"File not found: {file_path}")
            return result
        
        try:
            content = path.read_text(encoding='utf-8')
            
            # Detect format
            if content.strip().startswith('<'):
                return self._parse_xml(content, result)
            else:
                return self._parse_csv(content, result)
                
        except Exception as e:
            result.parse_errors.append(f"Error reading file: {str(e)}")
            logger.error(f"Error parsing {file_path}: {e}")
            return result
    
    def parse_directory(self, directory: str, pattern: str = "**/*.csv") -> List[FlexParseResult]:
        """Parse all matching files in a directory."""
        results = []
        dir_path = Path(directory)
        
        for file_path in dir_path.glob(pattern):
            result = self.parse_file(str(file_path))
            results.append(result)
        
        # Also try XML files
        for file_path in dir_path.glob("**/*.xml"):
            result = self.parse_file(str(file_path))
            results.append(result)
        
        self.results = results
        return results
    
    def get_consolidated_trades(self) -> pd.DataFrame:
        """Get all trades from parsed results as a single DataFrame."""
        all_trades = []
        for result in self.results:
            if not result.trades.empty:
                trades_copy = result.trades.copy()
                trades_copy['source_file'] = result.file_path
                all_trades.append(trades_copy)
        
        if not all_trades:
            return pd.DataFrame()
        
        df = pd.concat(all_trades, ignore_index=True)
        
        # Remove duplicates based on exec_id or trade_id
        dedup_cols = []
        if 'exec_id' in df.columns:
            dedup_cols.append('exec_id')
        elif 'trade_id' in df.columns:
            dedup_cols.append('trade_id')
        
        if dedup_cols:
            # Filter out empty/null values before deduplication
            df = df[df[dedup_cols[0]].notna() & (df[dedup_cols[0]] != '')]
            df = df.drop_duplicates(subset=dedup_cols, keep='last')
        
        # Sort by date
        if 'trade_date' in df.columns:
            df = df.sort_values('trade_date', ascending=False)
        
        return df.reset_index(drop=True)
    
    def get_consolidated_performance(self) -> pd.DataFrame:
        """Get all performance data from parsed results as a single DataFrame."""
        all_perf = []
        for result in self.results:
            if not result.performance.empty:
                perf_copy = result.performance.copy()
                perf_copy['source_file'] = result.file_path
                all_perf.append(perf_copy)
        
        if not all_perf:
            return pd.DataFrame()
        
        df = pd.concat(all_perf, ignore_index=True)
        
        # Remove header rows that got parsed as data
        if 'symbol' in df.columns:
            df = df[df['symbol'].notna() & (df['symbol'] != '') & (df['symbol'] != 'Symbol')]
        
        # Remove duplicates by symbol (keep latest)
        if 'symbol' in df.columns:
            df = df.drop_duplicates(subset=['symbol'], keep='last')
        
        # Sort by total P&L
        if 'total_pnl' in df.columns:
            df = df.sort_values('total_pnl', ascending=False)
        
        return df.reset_index(drop=True)
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse various date formats from IBKR."""
        if pd.isna(date_str) or date_str == '' or date_str is None:
            return None
        
        date_str = str(date_str).strip()
        
        formats = [
            '%Y%m%d',
            '%Y-%m-%d',
            '%Y%m%d;%H%M%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y%m%d;%H%M%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.split(';')[0] if ';' in date_str else date_str, fmt.split(';')[0])
            except ValueError:
                continue
        
        return None
    
    def _parse_float(self, value: Any) -> float:
        """Safely parse float value."""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_csv(self, content: str, result: FlexParseResult) -> FlexParseResult:
        """Parse CSV/TSV format Flex Query report."""
        lines = content.strip().split('\n')
        
        # Identify sections by header rows
        sections = self._identify_sections(lines)
        result.sections_found = list(sections.keys())
        
        # Parse each section
        for section_name, (start_line, end_line) in sections.items():
            section_content = '\n'.join(lines[start_line:end_line])
            
            try:
                df = pd.read_csv(StringIO(section_content), sep='\t', dtype=str)
                df = df.replace(['', 'nan', 'NaN'], np.nan)
                
                if section_name == 'account_summary':
                    result.account_summary = self._process_account_summary(df, result)
                elif section_name == 'position_mtm':
                    result.performance = self._process_position_mtm(df, result)
                elif section_name == 'trades':
                    result.trades = self._process_trades(df, result)
                elif section_name == 'positions':
                    result.positions = self._process_positions(df, result)
                    
            except Exception as e:
                result.parse_errors.append(f"Error parsing section {section_name}: {str(e)}")
                logger.warning(f"Error parsing section {section_name}: {e}")
        
        return result
    
    def _identify_sections(self, lines: List[str]) -> Dict[str, Tuple[int, int]]:
        """Identify different sections in the CSV by their header patterns."""
        sections = {}
        current_section = None
        section_start = 0
        
        for i, line in enumerate(lines):
            # Account summary section
            if 'StartingValue' in line and 'EndingValue' in line:
                if current_section:
                    sections[current_section] = (section_start, i)
                current_section = 'account_summary'
                section_start = i
            
            # Position MTM section (has CloseQuantity, ClosePrice, TransactionMtmPnl)
            elif 'CloseQuantity' in line and 'TransactionMtmPnl' in line:
                if current_section:
                    sections[current_section] = (section_start, i)
                current_section = 'position_mtm'
                section_start = i
            
            # Trades section (has TradeID, Buy/Sell, TradePrice)
            elif 'TradeID' in line and 'Buy/Sell' in line and 'TradePrice' in line:
                if current_section:
                    sections[current_section] = (section_start, i)
                current_section = 'trades'
                section_start = i
            
            # Asset summary (has Prior Period Value, Transactions)
            elif 'Prior Period Value' in line and 'Transactions' in line:
                if current_section:
                    sections[current_section] = (section_start, i)
                current_section = 'asset_summary'
                section_start = i
        
        # Close last section
        if current_section:
            sections[current_section] = (section_start, len(lines))
        
        return sections
    
    def _process_account_summary(self, df: pd.DataFrame, result: FlexParseResult) -> pd.DataFrame:
        """Process account summary section."""
        if df.empty:
            return df
        
        # Extract account ID and date range
        if 'ClientAccountID' in df.columns:
            result.account_id = str(df['ClientAccountID'].iloc[0])
        if 'FromDate' in df.columns:
            result.from_date = self._parse_date(df['FromDate'].iloc[0])
        if 'ToDate' in df.columns:
            result.to_date = self._parse_date(df['ToDate'].iloc[0])
        
        # Convert numeric columns
        numeric_cols = ['StartingValue', 'Mtm', 'Realized', 'Dividends', 
                       'Interest', 'Commissions', 'EndingValue', 'TWR']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(self._parse_float)
        
        return df
    
    def _process_position_mtm(self, df: pd.DataFrame, result: FlexParseResult) -> pd.DataFrame:
        """Process position-level mark-to-market section."""
        if df.empty:
            return df
        
        # Filter out summary rows
        if 'Symbol' in df.columns:
            df = df[df['Symbol'].notna() & (df['Symbol'] != '')]
        
        # Standardize column names
        rename_map = {
            'ClientAccountID': 'account_id',
            'AssetClass': 'asset_class',
            'Symbol': 'symbol',
            'Description': 'description',
            'Conid': 'conid',
            'CloseQuantity': 'quantity',
            'ClosePrice': 'close_price',
            'TransactionMtmPnl': 'mtm_pnl',
            'PriorOpenMtmPnl': 'prior_mtm_pnl',
            'Commissions': 'commissions',
            'Total': 'total_pnl',
            'TotalWithAccruals': 'total_pnl_with_accruals',
            'CurrencyPrimary': 'currency',
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        
        # Convert numeric columns
        numeric_cols = ['quantity', 'close_price', 'mtm_pnl', 'prior_mtm_pnl', 
                       'commissions', 'total_pnl', 'total_pnl_with_accruals']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(self._parse_float)
        
        return df
    
    def _process_trades(self, df: pd.DataFrame, result: FlexParseResult) -> pd.DataFrame:
        """Process trades section into clean trade history DataFrame."""
        if df.empty:
            return df
        
        # Filter to EXECUTION level only (actual fills)
        if 'LevelOfDetail' in df.columns:
            executions = df[df['LevelOfDetail'] == 'EXECUTION'].copy()
        else:
            executions = df.copy()
        
        if executions.empty:
            return pd.DataFrame()
        
        # Standardize column names
        rename_map = {
            'ClientAccountID': 'account_id',
            'AssetClass': 'asset_class',
            'SubCategory': 'sub_category',
            'Symbol': 'symbol',
            'Description': 'description',
            'Conid': 'conid',
            'TradeID': 'trade_id',
            'IBExecID': 'exec_id',
            'TradeDate': 'trade_date_str',
            'DateTime': 'datetime_str',
            'Buy/Sell': 'side',
            'Quantity': 'quantity',
            'TradePrice': 'price',
            'TradeMoney': 'trade_value',
            'Proceeds': 'proceeds',
            'IBCommission': 'commission',
            'Taxes': 'taxes',
            'CostBasis': 'cost_basis',
            'FifoPnlRealized': 'realized_pnl',
            'MtmPnl': 'mtm_pnl',
            'Exchange': 'exchange',
            'CurrencyPrimary': 'currency',
            'FXRateToBase': 'fx_rate',
            'Multiplier': 'multiplier',
            'Strike': 'strike',
            'Expiry': 'expiry',
            'Put/Call': 'put_call',
            'UnderlyingSymbol': 'underlying',
            'OrderType': 'order_type',
        }
        executions = executions.rename(columns={k: v for k, v in rename_map.items() if k in executions.columns})
        
        # Parse dates
        if 'datetime_str' in executions.columns:
            executions['trade_datetime'] = executions['datetime_str'].apply(self._parse_datetime_with_time)
        if 'trade_date_str' in executions.columns:
            executions['trade_date'] = executions['trade_date_str'].apply(self._parse_date)
        
        # If trade_date is missing, extract from trade_datetime
        if 'trade_date' not in executions.columns and 'trade_datetime' in executions.columns:
            executions['trade_date'] = executions['trade_datetime'].apply(
                lambda x: x.date() if x else None
            )
        
        # Convert numeric columns
        numeric_cols = ['quantity', 'price', 'trade_value', 'proceeds', 'commission',
                       'taxes', 'cost_basis', 'realized_pnl', 'mtm_pnl', 'fx_rate',
                       'multiplier', 'strike']
        for col in numeric_cols:
            if col in executions.columns:
                executions[col] = executions[col].apply(self._parse_float)
        
        # Calculate net value
        if 'proceeds' in executions.columns and 'commission' in executions.columns:
            executions['net_proceeds'] = executions['proceeds'] + executions['commission']
        
        # Select key columns for output
        output_cols = [
            'account_id', 'trade_date', 'trade_datetime', 'symbol', 'description',
            'asset_class', 'side', 'quantity', 'price', 'trade_value', 'proceeds',
            'commission', 'taxes', 'cost_basis', 'realized_pnl', 'mtm_pnl',
            'currency', 'exchange', 'trade_id', 'exec_id', 'order_type',
            'underlying', 'strike', 'expiry', 'put_call', 'multiplier'
        ]
        available_cols = [c for c in output_cols if c in executions.columns]
        
        return executions[available_cols].reset_index(drop=True)
    
    def _parse_datetime_with_time(self, dt_str: Any) -> Optional[datetime]:
        """Parse datetime string that includes time (e.g., '20250110;103601')."""
        if pd.isna(dt_str) or dt_str == '' or dt_str is None:
            return None
        
        dt_str = str(dt_str).strip()
        
        formats = [
            '%Y%m%d;%H%M%S',
            '%Y%m%d;%H%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d;%H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        # Fallback: try just date
        return self._parse_date(dt_str)
    
    def _process_positions(self, df: pd.DataFrame, result: FlexParseResult) -> pd.DataFrame:
        """Process current positions from the data."""
        # This would process OpenPosition data if available
        return df
    
    def _parse_xml(self, content: str, result: FlexParseResult) -> FlexParseResult:
        """Parse XML format Flex Query report."""
        try:
            # Check for error response
            if '<ErrorCode>' in content:
                root = ET.fromstring(content)
                error_msg = root.find('.//ErrorMessage')
                if error_msg is not None:
                    result.parse_errors.append(f"XML Error: {error_msg.text}")
                return result
            
            root = ET.fromstring(content)
            
            # Get statement info
            statement = root.find('.//FlexStatement')
            if statement is not None:
                result.account_id = statement.get('accountId', '')
                result.from_date = self._parse_date(statement.get('fromDate'))
                result.to_date = self._parse_date(statement.get('toDate'))
            
            # Parse trades
            trades_data = []
            for trade in root.findall('.//Trade'):
                attrs = trade.attrib
                if attrs.get('levelOfDetail') != 'EXECUTION':
                    continue
                
                trades_data.append({
                    'account_id': attrs.get('accountId', result.account_id),
                    'trade_id': attrs.get('tradeID', ''),
                    'exec_id': attrs.get('ibExecID', ''),
                    'symbol': attrs.get('symbol', ''),
                    'description': attrs.get('description', ''),
                    'asset_class': attrs.get('assetCategory', ''),
                    'side': 'BUY' if self._parse_float(attrs.get('quantity', '0')) > 0 else 'SELL',
                    'quantity': abs(self._parse_float(attrs.get('quantity', '0'))),
                    'price': self._parse_float(attrs.get('tradePrice', '0')),
                    'proceeds': self._parse_float(attrs.get('proceeds', '0')),
                    'commission': self._parse_float(attrs.get('ibCommission', '0')),
                    'realized_pnl': self._parse_float(attrs.get('fifoPnlRealized', '0')),
                    'trade_date': self._parse_date(attrs.get('tradeDate')),
                    'currency': attrs.get('currency', 'USD'),
                    'exchange': attrs.get('exchange', ''),
                })
            
            if trades_data:
                result.trades = pd.DataFrame(trades_data)
                result.sections_found.append('trades')
            
            # Parse positions
            positions_data = []
            for pos in root.findall('.//OpenPosition'):
                attrs = pos.attrib
                positions_data.append({
                    'account_id': attrs.get('accountId', result.account_id),
                    'symbol': attrs.get('symbol', ''),
                    'description': attrs.get('description', ''),
                    'asset_class': attrs.get('assetCategory', ''),
                    'quantity': self._parse_float(attrs.get('position', '0')),
                    'cost_basis': self._parse_float(attrs.get('costBasisMoney', '0')),
                    'market_value': self._parse_float(attrs.get('positionValue', '0')),
                    'unrealized_pnl': self._parse_float(attrs.get('fifoPnlUnrealized', '0')),
                    'currency': attrs.get('currency', 'USD'),
                })
            
            if positions_data:
                result.positions = pd.DataFrame(positions_data)
                result.sections_found.append('positions')
            
        except ET.ParseError as e:
            result.parse_errors.append(f"XML Parse Error: {str(e)}")
        except Exception as e:
            result.parse_errors.append(f"Error parsing XML: {str(e)}")
        
        return result


# ============================================================================
# Utility Functions
# ============================================================================

def load_all_flex_reports(data_dir: str = "data/flex_reports") -> Dict[str, pd.DataFrame]:
    """
    Load all Flex Query reports and return consolidated DataFrames.
    
    Returns:
        Dict with 'trades', 'performance', 'positions' DataFrames
    """
    parser = FlexParser()
    parser.parse_directory(data_dir)
    
    return {
        'trades': parser.get_consolidated_trades(),
        'performance': parser.get_consolidated_performance(),
        'results': parser.results,
    }


def get_trade_summary(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of trades by symbol.
    
    Returns DataFrame with columns:
    - symbol, total_trades, total_quantity, total_value, realized_pnl, commissions
    """
    if trades_df.empty:
        return pd.DataFrame()
    
    summary = trades_df.groupby('symbol').agg({
        'trade_id': 'count',
        'quantity': 'sum',
        'proceeds': 'sum',
        'commission': 'sum',
        'realized_pnl': 'sum',
    }).rename(columns={
        'trade_id': 'trade_count',
        'quantity': 'total_quantity',
        'proceeds': 'total_proceeds',
        'commission': 'total_commission',
        'realized_pnl': 'total_realized_pnl',
    })
    
    return summary.sort_values('total_realized_pnl', ascending=False)


def get_daily_pnl(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate daily P&L summary from trades.
    
    Returns DataFrame with columns:
    - date, trade_count, realized_pnl, commissions
    """
    if trades_df.empty or 'trade_date' not in trades_df.columns:
        return pd.DataFrame()
    
    # Ensure trade_date is datetime
    trades_df = trades_df.copy()
    trades_df['date'] = pd.to_datetime(trades_df['trade_date'])
    
    daily = trades_df.groupby('date').agg({
        'trade_id': 'count',
        'realized_pnl': 'sum',
        'commission': 'sum',
    }).rename(columns={
        'trade_id': 'trade_count',
        'realized_pnl': 'daily_realized_pnl',
        'commission': 'daily_commission',
    })
    
    daily['cumulative_pnl'] = daily['daily_realized_pnl'].cumsum()
    
    return daily.sort_index()


# ============================================================================
# Main entry point for testing
# ============================================================================

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Default to data/flex_reports
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/flex_reports"
    
    print(f"\n{'='*60}")
    print(f"IBKR Flex Query Parser")
    print(f"{'='*60}\n")
    
    # Parse all files
    data = load_all_flex_reports(data_dir)
    
    # Report results
    print(f"Parsed {len(data['results'])} files\n")
    
    for result in data['results']:
        print(f"📄 {result.file_path}")
        print(f"   Account: {result.account_id}")
        print(f"   Period: {result.from_date} to {result.to_date}")
        print(f"   Sections: {', '.join(result.sections_found)}")
        print(f"   Trades: {len(result.trades)}")
        print(f"   Performance rows: {len(result.performance)}")
        if result.parse_errors:
            print(f"   ⚠️ Errors: {result.parse_errors}")
        print()
    
    # Show consolidated trades
    trades = data['trades']
    if not trades.empty:
        print(f"\n{'='*60}")
        print(f"CONSOLIDATED TRADES: {len(trades)} executions")
        print(f"{'='*60}\n")
        
        # Summary by symbol
        summary = get_trade_summary(trades)
        print("Trade Summary by Symbol:")
        print(summary.to_string())
        print()
        
        # Daily P&L
        daily_pnl = get_daily_pnl(trades)
        if not daily_pnl.empty:
            print("\nDaily P&L:")
            print(daily_pnl.tail(10).to_string())
            print(f"\nTotal Realized P&L: ${daily_pnl['cumulative_pnl'].iloc[-1]:,.2f}")
    
    # Show performance data
    perf = data['performance']
    if not perf.empty:
        print(f"\n{'='*60}")
        print(f"POSITION PERFORMANCE: {len(perf)} positions")
        print(f"{'='*60}\n")
        
        display_cols = ['symbol', 'asset_class', 'quantity', 'close_price', 
                       'mtm_pnl', 'total_pnl', 'commissions']
        available = [c for c in display_cols if c in perf.columns]
        print(perf[available].to_string())
