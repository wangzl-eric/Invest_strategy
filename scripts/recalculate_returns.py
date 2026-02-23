#!/usr/bin/env python3
"""
Script to recalculate daily_return and cumulative_return for all existing pnl_history records.

This script:
1. Fetches all accounts with pnl_history records
2. Recalculates returns using the new method: daily_return = total_pnl / previous_net_liquidation
3. Updates all records in the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database import get_db_context
from backend.models import PnLHistory
from backend.flex_importer import calculate_and_update_returns

def recalculate_all_returns():
    """Recalculate returns for all accounts in the database."""
    db_path = project_root / "ibkr_analytics.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    print(f"Recalculating returns for all accounts in {db_path}...")
    print("=" * 60)
    
    with get_db_context() as db:
        # Get all unique account IDs
        account_ids = db.query(PnLHistory.account_id).distinct().all()
        account_ids = [row[0] for row in account_ids]
        
        if not account_ids:
            print("No accounts found in pnl_history table")
            return False
        
        print(f"Found {len(account_ids)} account(s): {', '.join(account_ids)}")
        print()
        
        total_records = 0
        for account_id in account_ids:
            try:
                # Count records for this account
                count = db.query(PnLHistory).filter(
                    PnLHistory.account_id == account_id
                ).count()
                
                print(f"Account: {account_id}")
                print(f"  Records: {count}")
                print(f"  Recalculating returns...", end=" ")
                
                # Recalculate returns
                calculate_and_update_returns(account_id, db)
                
                print("✓")
                total_records += count
                
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Commit all changes
        db.commit()
        print()
        print("=" * 60)
        print(f"✓ Successfully recalculated returns for {total_records} records across {len(account_ids)} account(s)")
        print()
        print("New calculation method:")
        print("  daily_return = total_pnl / previous_day_net_liquidation")
        print("  cumulative_return = (1 + r1) × (1 + r2) × ... - 1")
        
        return True

if __name__ == "__main__":
    try:
        success = recalculate_all_returns()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
