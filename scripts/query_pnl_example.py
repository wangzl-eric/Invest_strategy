#!/usr/bin/env python3
"""
Example script demonstrating how to query PnL data from the database.

Usage:
    python scripts/query_pnl_example.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.db_utils import (
    get_trades_df,
    get_daily_pnl,
    get_trade_summary,
    get_account_pnl_totals,
    query_trades
)
import pandas as pd


def main():
    print("=" * 80)
    print("PNL QUERY EXAMPLES")
    print("=" * 80)
    
    # 1. Get total P&L
    print("\n1. TOTAL P&L OVERVIEW")
    print("-" * 80)
    totals = get_account_pnl_totals()
    print(f"Total P&L (USD): ${totals['total_pnl_usd']:,.2f}")
    print(f"Total P&L (HKD): HK${totals['total_pnl_hkd']:,.2f}")
    print(f"Total Commissions: ${totals['total_commissions']:,.2f}")
    print(f"Total Trades: {totals['trade_count']}")
    
    # 2. Get daily P&L (last 10 days)
    print("\n2. DAILY P&L (Last 10 Days)")
    print("-" * 80)
    daily = get_daily_pnl()
    if not daily.empty:
        print(daily[['date', 'trade_count', 'realized_pnl', 'realized_pnl_hkd', 
                     'cumulative_pnl_usd']].tail(10).to_string(index=False))
    else:
        print("No daily P&L data available")
    
    # 3. Get trade summary by symbol
    print("\n3. P&L BY SYMBOL (Top 10)")
    print("-" * 80)
    summary = get_trade_summary()
    if not summary.empty:
        top_symbols = summary.head(10)
        print(top_symbols[['trade_count', 'realized_pnl_usd', 'realized_pnl_hkd']].to_string())
    else:
        print("No trade summary data available")
    
    # 4. Get recent trades
    print("\n4. RECENT TRADES (Last 5)")
    print("-" * 80)
    recent_trades = get_trades_df(limit=5)
    if not recent_trades.empty:
        print(recent_trades[['exec_time', 'symbol', 'side', 'shares', 
                            'price', 'realized_pnl']].to_string(index=False))
    else:
        print("No trades found")
    
    # 5. Monthly P&L summary (using SQL)
    print("\n5. MONTHLY P&L SUMMARY")
    print("-" * 80)
    monthly = query_trades("""
        SELECT 
            strftime('%Y-%m', exec_time) as month,
            COUNT(*) as trades,
            SUM(realized_pnl) as pnl_usd,
            SUM(realized_pnl_base) as pnl_hkd
        FROM trades 
        GROUP BY month 
        ORDER BY month DESC
        LIMIT 12
    """)
    if not monthly.empty:
        print(monthly.to_string(index=False))
    else:
        print("No monthly data available")
    
    # 6. Win/Loss statistics
    print("\n6. WIN/LOSS STATISTICS")
    print("-" * 80)
    win_loss = query_trades("""
        SELECT 
            CASE 
                WHEN realized_pnl > 0 THEN 'Win'
                WHEN realized_pnl < 0 THEN 'Loss'
                ELSE 'Breakeven'
            END as outcome,
            COUNT(*) as count,
            SUM(realized_pnl) as total_pnl,
            AVG(realized_pnl) as avg_pnl
        FROM trades 
        WHERE realized_pnl != 0
        GROUP BY outcome
    """)
    if not win_loss.empty:
        print(win_loss.to_string(index=False))
        
        # Calculate win rate
        total = win_loss['count'].sum()
        wins = win_loss[win_loss['outcome'] == 'Win']['count'].sum() if 'Win' in win_loss['outcome'].values else 0
        win_rate = (wins / total * 100) if total > 0 else 0
        print(f"\nWin Rate: {win_rate:.2f}%")
    else:
        print("No win/loss data available")
    
    print("\n" + "=" * 80)
    print("Done! Check docs/PNL_QUERY_GUIDE.md for more examples")
    print("=" * 80)


if __name__ == "__main__":
    main()
