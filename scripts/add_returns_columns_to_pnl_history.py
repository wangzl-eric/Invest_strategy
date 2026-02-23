#!/usr/bin/env python3
"""
Migration script to add daily_return and cumulative_return columns to pnl_history table.

This script:
1. Checks if columns already exist
2. Adds columns if they don't exist
3. Optionally calculates returns for existing data
"""
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database import get_db_context
from backend.models import PnLHistory
from sqlalchemy import text

def migrate_pnl_history_table():
    """Add daily_return and cumulative_return columns to pnl_history table."""
    db_path = project_root / "ibkr_analytics.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    print(f"Migrating pnl_history table in {db_path}...")
    
    with get_db_context() as db:
        # Check if columns already exist
        result = db.execute(text("PRAGMA table_info(pnl_history)"))
        columns = [row[1] for row in result.fetchall()]
        
        has_daily_return = 'daily_return' in columns
        has_cumulative_return = 'cumulative_return' in columns
        
        if has_daily_return and has_cumulative_return:
            print("✓ Columns daily_return and cumulative_return already exist")
            return True
        
        # Add columns if they don't exist
        if not has_daily_return:
            print("Adding daily_return column...")
            db.execute(text("ALTER TABLE pnl_history ADD COLUMN daily_return FLOAT"))
            print("✓ Added daily_return column")
        
        if not has_cumulative_return:
            print("Adding cumulative_return column...")
            db.execute(text("ALTER TABLE pnl_history ADD COLUMN cumulative_return FLOAT"))
            print("✓ Added cumulative_return column")
        
        db.commit()
        print("✓ Migration completed successfully")
        
        # Check and add mtm column if needed
        result = db.execute(text("PRAGMA table_info(pnl_history)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'mtm' not in columns:
            print("Adding mtm column...")
            db.execute(text("ALTER TABLE pnl_history ADD COLUMN mtm FLOAT DEFAULT 0.0"))
            db.commit()
            print("✓ Added mtm column")
        else:
            print("✓ Column 'mtm' already exists")
        
        # Optionally calculate returns for existing data
        print("\nCalculating returns for existing data...")
        from backend.flex_importer import calculate_and_update_returns
        
        # Get all unique account IDs
        account_ids = db.query(PnLHistory.account_id).distinct().all()
        account_ids = [row[0] for row in account_ids]
        
        for account_id in account_ids:
            try:
                calculate_and_update_returns(account_id, db)
                print(f"  ✓ Calculated returns for account {account_id}")
            except Exception as e:
                print(f"  ✗ Error calculating returns for account {account_id}: {e}")
        
        db.commit()
        print("\n✓ Return calculation completed")
        
        return True

if __name__ == "__main__":
    try:
        success = migrate_pnl_history_table()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
