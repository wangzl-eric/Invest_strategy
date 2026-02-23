"""Data processor for calculating performance metrics."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db_context
from backend.models import PnLHistory, Trade, PerformanceMetric, AccountSnapshot

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes historical data to calculate performance metrics."""
    
    def calculate_daily_returns(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Calculate daily returns from account snapshots."""
        with get_db_context() as db:
            query = db.query(AccountSnapshot).filter(
                AccountSnapshot.account_id == account_id
            ).order_by(AccountSnapshot.timestamp)
            
            if start_date:
                query = query.filter(AccountSnapshot.timestamp >= start_date)
            if end_date:
                query = query.filter(AccountSnapshot.timestamp <= end_date)
            
            snapshots = query.all()
            
            if len(snapshots) < 2:
                return pd.DataFrame()
            
            data = []
            for snapshot in snapshots:
                data.append({
                    'date': snapshot.timestamp,
                    'equity': snapshot.equity or snapshot.net_liquidation or 0.0,
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df['daily_return'] = df['equity'].pct_change()
            df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
            
            return df
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.0
    ) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        std_dev = excess_returns.std()
        if std_dev == 0 or np.isnan(std_dev) or np.isinf(std_dev):
            return 0.0
        
        mean_return = excess_returns.mean()
        if np.isnan(mean_return) or np.isinf(mean_return):
            return 0.0
        
        sharpe = np.sqrt(252) * mean_return / std_dev
        return float(sharpe) if not (np.isnan(sharpe) or np.isinf(sharpe)) else 0.0
    
    def calculate_sortino_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.0
    ) -> float:
        """Calculate Sortino ratio (downside deviation only)."""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return 0.0
        
        downside_std = downside_returns.std()
        if downside_std == 0 or np.isnan(downside_std) or np.isinf(downside_std):
            return 0.0
        
        mean_return = excess_returns.mean()
        if np.isnan(mean_return) or np.isinf(mean_return):
            return 0.0
        
        sortino = np.sqrt(252) * mean_return / downside_std
        return float(sortino) if not (np.isnan(sortino) or np.isinf(sortino)) else 0.0
    
    def calculate_max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(equity) < 2:
            return 0.0
        
        # Handle zero or negative starting equity
        if equity.iloc[0] == 0 or equity.iloc[0] < 0:
            # Use absolute values if starting equity is problematic
            equity_abs = equity.abs()
            if equity_abs.iloc[0] == 0:
                return 0.0
            cumulative = equity_abs / equity_abs.iloc[0]
        else:
            cumulative = equity / equity.iloc[0]
        
        running_max = cumulative.cummax()
        
        # Avoid division by zero - replace zeros in running_max with NaN, then fill
        # If running_max is 0, drawdown is 0 (no loss from peak)
        drawdown = (cumulative - running_max) / running_max.replace(0, np.nan)
        drawdown = drawdown.fillna(0.0)
        
        # Handle any remaining NaN or inf values
        drawdown = drawdown.replace([np.inf, -np.inf], 0.0)
        drawdown = drawdown.fillna(0.0)
        
        max_dd = drawdown.min()
        
        # Ensure result is valid
        if np.isnan(max_dd) or np.isinf(max_dd):
            return 0.0
        
        return float(max_dd)
    
    def calculate_trade_statistics(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate trade statistics."""
        with get_db_context() as db:
            query = db.query(Trade).filter(Trade.account_id == account_id)
            
            if start_date:
                query = query.filter(Trade.exec_time >= start_date)
            if end_date:
                query = query.filter(Trade.exec_time <= end_date)
            
            trades = query.order_by(Trade.exec_time).all()
            
            if not trades:
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                    'profit_factor': 0.0,
                }
            
            # Group trades by symbol and calculate PnL per trade
            # This is simplified - in reality, you'd need to track entry/exit pairs
            trade_pnls = []
            for trade in trades:
                # Simplified: assume we can calculate PnL from trade data
                # In practice, you'd need to match buy/sell pairs
                pass
            
            # For now, return basic statistics
            total_trades = len(trades)
            buy_trades = [t for t in trades if getattr(t, 'side', None) == 'BUY']
            sell_trades = [t for t in trades if getattr(t, 'side', None) == 'SELL']
            
            return {
                'total_trades': total_trades,
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'winning_trades': 0,  # Would need position tracking
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
            }
    
    def calculate_performance_metrics(
        self,
        account_id: str,
        date: Optional[datetime] = None
    ) -> PerformanceMetric:
        """Calculate and store performance metrics for a given date."""
        if date is None:
            date = datetime.utcnow()
        
        # Get date range (last 30 days for calculations)
        end_date = date
        start_date = date - timedelta(days=30)
        
        # Calculate returns
        returns_df = self.calculate_daily_returns(account_id, start_date, end_date)
        
        if returns_df.empty or len(returns_df) < 2:
            logger.warning(f"Insufficient data for performance metrics for {account_id}")
            # Return a default PerformanceMetric object to satisfy type checking
            return PerformanceMetric(
                account_id=account_id,
                date=date,
                daily_return=0.0,
                cumulative_return=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                max_drawdown=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
            )
        
        daily_returns = returns_df['daily_return'].dropna()
        cumulative_return = returns_df['cumulative_return'].iloc[-1] if len(returns_df) > 0 else 0.0
        equity = returns_df['equity']

        # Ensure we have valid Series for calculations
        if not isinstance(daily_returns, pd.Series):
            daily_returns = pd.Series(daily_returns).dropna()
        if not isinstance(equity, pd.Series):
            equity = pd.Series(equity)

        # Calculate metrics (handle empty series)
        if len(daily_returns) < 2:
            sharpe = 0.0
            sortino = 0.0
        else:
            sharpe = self.calculate_sharpe_ratio(daily_returns)
            sortino = self.calculate_sortino_ratio(daily_returns)
        
        if len(equity) < 2:
            max_drawdown = 0.0
        else:
            max_drawdown = self.calculate_max_drawdown(equity)

        trade_stats = self.calculate_trade_statistics(account_id, start_date, end_date)
        
        # Store metrics
        with get_db_context() as db:
            # Get daily return (last non-null value)
            daily_return = 0.0
            if len(daily_returns) > 0:
                try:
                    daily_return = float(daily_returns.iloc[-1])
                except (IndexError, ValueError, TypeError):
                    daily_return = 0.0
            
            metric = PerformanceMetric(
                account_id=account_id,
                date=date,
                daily_return=daily_return,
                cumulative_return=float(cumulative_return) if cumulative_return is not None else 0.0,
                sharpe_ratio=float(sharpe) if sharpe is not None else 0.0,
                sortino_ratio=float(sortino) if sortino is not None else 0.0,
                max_drawdown=float(max_drawdown) if max_drawdown is not None else 0.0,
                total_trades=trade_stats.get('total_trades', 0),
                winning_trades=trade_stats.get('winning_trades', 0),
                losing_trades=trade_stats.get('losing_trades', 0),
                win_rate=float(trade_stats.get('win_rate', 0.0)),
                avg_win=float(trade_stats.get('avg_win', 0.0)),
                avg_loss=float(trade_stats.get('avg_loss', 0.0)),
                profit_factor=float(trade_stats.get('profit_factor', 0.0)),
            )
            db.add(metric)
            db.flush()
            logger.info(f"Calculated and stored performance metrics for {account_id}")
            return metric
    
    def get_pnl_history(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get PnL history as DataFrame."""
        with get_db_context() as db:
            query = db.query(PnLHistory).filter(
                PnLHistory.account_id == account_id
            ).order_by(PnLHistory.date)
            
            if start_date:
                query = query.filter(PnLHistory.date >= start_date)
            if end_date:
                query = query.filter(PnLHistory.date <= end_date)
            
            pnl_records = query.all()
            
            if not pnl_records:
                return pd.DataFrame()
            
            data = []
            for record in pnl_records:
                data.append({
                    'date': record.date,
                    'realized_pnl': record.realized_pnl,
                    'unrealized_pnl': record.unrealized_pnl,
                    'total_pnl': record.total_pnl,
                    'net_liquidation': record.net_liquidation,
                    'total_cash': record.total_cash,
                })
            
            return pd.DataFrame(data)

    def get_pnl_time_series(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        freq: str = "raw",
    ) -> List[Dict[str, Any]]:
        """
        Get PnL history as a cleaned time series suitable for frontend charts.

        Args:
            account_id: IBKR account identifier.
            start_date: Optional start datetime for filtering.
            end_date: Optional end datetime for filtering.
            freq: Aggregation frequency. Supported values:
                - "raw": return raw snapshots from DB in time order
                - "D": aggregate to one row per calendar day using last snapshot

        Returns:
            A list of dicts sorted by timestamp with keys:
            - timestamp (ISO string)
            - realized_pnl
            - unrealized_pnl
            - total_pnl
            - net_liquidation
            - total_cash
        """
        df = self.get_pnl_history(account_id, start_date, end_date)

        if df.empty:
            logger.warning("No PnL history found", extra={"account_id": account_id})
            return []

        # Ensure datetime type and sort
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        if freq == "D":
            # Use last snapshot per calendar day
            df["calendar_date"] = df["date"].dt.date
            df = (
                df.sort_values("date")
                .groupby("calendar_date")
                .tail(1)
                .reset_index(drop=True)
            )

        # Build clean list of dicts with ISO timestamps
        series: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            series.append(
                {
                    "timestamp": pd.Timestamp(row["date"]).isoformat(),
                    "realized_pnl": float(row["realized_pnl"] or 0.0),
                    "unrealized_pnl": float(row["unrealized_pnl"] or 0.0),
                    "total_pnl": float(row["total_pnl"] or 0.0),
                    "net_liquidation": float(row["net_liquidation"] or 0.0)
                    if row["net_liquidation"] is not None
                    else None,
                    "total_cash": float(row["total_cash"] or 0.0)
                    if row["total_cash"] is not None
                    else None,
                }
            )

        return series

    def get_returns_series(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Get daily returns series from PnL history.
        
        Returns DataFrame with columns:
        - date
        - daily_return
        - cumulative_return
        - net_liquidation
        """
        df = self.get_pnl_history(account_id, start_date, end_date)
        
        if df.empty or len(df) < 2:
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
        
        # Calculate returns from net_liquidation
        df['daily_return'] = df['net_liquidation'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        return df[['date', 'daily_return', 'cumulative_return', 'net_liquidation', 'total_pnl']].dropna()

    def get_comprehensive_metrics(
        self,
        account_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics from PnL history.
        
        Returns dictionary with:
        - total_return
        - annualized_return
        - volatility
        - sharpe_ratio
        - sortino_ratio
        - max_drawdown
        - calmar_ratio
        - var_95
        - cvar_95
        """
        df = self.get_returns_series(account_id, start_date, end_date)
        
        if df.empty or len(df) < 2:
            return {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'max_drawdown': 0.0,
                'calmar_ratio': 0.0,
                'var_95': 0.0,
                'cvar_95': 0.0,
                'data_points': len(df),
            }
        
        returns = df['daily_return'].dropna()
        
        # Total and annualized return
        total_return = float((1 + returns).prod() - 1)
        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
        annualized_return = float((1 + total_return) ** (365 / max(days, 1)) - 1) if days > 0 else 0
        
        # Volatility
        volatility = float(returns.std() * np.sqrt(252))
        
        # Sharpe ratio
        sharpe = self.calculate_sharpe_ratio(returns)
        
        # Sortino ratio
        sortino = self.calculate_sortino_ratio(returns)
        
        # Max drawdown
        max_drawdown = self.calculate_max_drawdown(df['net_liquidation'])
        
        # Calmar ratio
        calmar = float(annualized_return / abs(max_drawdown)) if max_drawdown != 0 else 0
        
        # VaR and CVaR
        var_95 = float(np.percentile(returns, 5))
        cvar_95 = float(returns[returns <= var_95].mean()) if len(returns[returns <= var_95]) > 0 else var_95
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'data_points': len(df),
            'period_start': df['date'].iloc[0].strftime('%Y-%m-%d'),
            'period_end': df['date'].iloc[-1].strftime('%Y-%m-%d'),
        }

