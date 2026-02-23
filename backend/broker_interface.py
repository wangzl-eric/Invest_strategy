"""Abstract broker interface for multi-broker support."""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Standardized position data structure."""
    symbol: str
    quantity: float
    market_price: float
    market_value: float
    avg_cost: float
    unrealized_pnl: float
    currency: str
    sec_type: str
    exchange: Optional[str] = None


@dataclass
class Trade:
    """Standardized trade data structure."""
    symbol: str
    side: str  # BUY, SELL
    quantity: float
    price: float
    commission: float
    trade_date: datetime
    exec_id: str
    currency: str
    sec_type: str


@dataclass
class AccountSummary:
    """Standardized account summary."""
    account_id: str
    net_liquidation: float
    total_cash: float
    buying_power: float
    currency: str
    timestamp: datetime


class BrokerInterface(ABC):
    """Abstract interface for broker integrations."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the broker."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the broker."""
        pass
    
    @abstractmethod
    async def get_account_summary(self, account_id: Optional[str] = None) -> AccountSummary:
        """Get account summary."""
        pass
    
    @abstractmethod
    async def get_positions(self, account_id: Optional[str] = None) -> List[Position]:
        """Get current positions."""
        pass
    
    @abstractmethod
    async def get_trades(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trade]:
        """Get trade history."""
        pass
    
    @abstractmethod
    def get_broker_name(self) -> str:
        """Get the name of this broker."""
        pass


class IBKRBrokerAdapter(BrokerInterface):
    """Adapter for IBKR broker using existing IBKRClient."""
    
    def __init__(self, ibkr_client):
        self.ibkr_client = ibkr_client
    
    async def connect(self) -> bool:
        """Connect to IBKR."""
        return await self.ibkr_client.connect()
    
    async def disconnect(self):
        """Disconnect from IBKR."""
        await self.ibkr_client.disconnect()
    
    async def get_account_summary(self, account_id: Optional[str] = None) -> AccountSummary:
        """Get IBKR account summary."""
        account_data = await self.ibkr_client.get_account_summary(account_id)
        
        return AccountSummary(
            account_id=account_data.get('account', account_id or ''),
            net_liquidation=float(account_data.get('NetLiquidation', 0) or 0),
            total_cash=float(account_data.get('TotalCashValue', 0) or 0),
            buying_power=float(account_data.get('BuyingPower', 0) or 0),
            currency=account_data.get('currency', 'USD'),
            timestamp=datetime.utcnow()
        )
    
    async def get_positions(self, account_id: Optional[str] = None) -> List[Position]:
        """Get IBKR positions."""
        positions_data = await self.ibkr_client.get_positions(account_id)
        
        positions = []
        for pos_data in positions_data:
            positions.append(Position(
                symbol=pos_data['contract']['symbol'],
                quantity=float(pos_data['position']),
                market_price=float(pos_data.get('marketPrice', 0) or 0),
                market_value=float(pos_data.get('marketValue', 0) or 0),
                avg_cost=float(pos_data.get('avgCost', 0) or 0),
                unrealized_pnl=float(pos_data.get('unrealizedPnL', 0) or 0),
                currency=pos_data['contract'].get('currency', 'USD'),
                sec_type=pos_data['contract'].get('secType', 'STK'),
                exchange=pos_data['contract'].get('exchange')
            ))
        
        return positions
    
    async def get_trades(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trade]:
        """Get IBKR trades."""
        trades_data = await self.ibkr_client.get_trades(account_id)
        
        trades = []
        for trade_data in trades_data:
            exec_time_str = trade_data['execution'].get('time')
            exec_time = datetime.fromisoformat(exec_time_str) if exec_time_str else datetime.utcnow()
            
            # Filter by date if provided
            if start_date and exec_time < start_date:
                continue
            if end_date and exec_time > end_date:
                continue
            
            trades.append(Trade(
                symbol=trade_data['contract']['symbol'],
                side=trade_data['execution']['side'],
                quantity=float(trade_data['execution']['shares']),
                price=float(trade_data['execution']['price']),
                commission=float(trade_data.get('commission', 0) or 0),
                trade_date=exec_time,
                exec_id=trade_data['execution']['execId'],
                currency=trade_data['contract'].get('currency', 'USD'),
                sec_type=trade_data['contract'].get('secType', 'STK')
            ))
        
        return trades
    
    def get_broker_name(self) -> str:
        return "Interactive Brokers"


class BrokerManager:
    """Manages multiple broker connections."""
    
    def __init__(self):
        self.brokers: Dict[str, BrokerInterface] = {}
    
    def register_broker(self, broker_id: str, broker: BrokerInterface):
        """Register a broker adapter."""
        self.brokers[broker_id] = broker
        logger.info(f"Registered broker: {broker_id} ({broker.get_broker_name()})")
    
    def get_broker(self, broker_id: str) -> Optional[BrokerInterface]:
        """Get a broker by ID."""
        return self.brokers.get(broker_id)
    
    def list_brokers(self) -> List[str]:
        """List all registered broker IDs."""
        return list(self.brokers.keys())
    
    async def get_all_positions(self) -> Dict[str, List[Position]]:
        """Get positions from all brokers."""
        all_positions = {}
        
        for broker_id, broker in self.brokers.items():
            try:
                if await broker.connect():
                    positions = await broker.get_positions()
                    all_positions[broker_id] = positions
                    await broker.disconnect()
            except Exception as e:
                logger.error(f"Error getting positions from {broker_id}: {e}")
        
        return all_positions


# Global broker manager
broker_manager = BrokerManager()
