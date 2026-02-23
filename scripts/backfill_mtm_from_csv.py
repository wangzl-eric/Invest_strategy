#!/usr/bin/env python3
"""
Backfill mtm values from existing Flex Query CSV files.

This script:
1. Finds all mark-to-market performance CSV files
2. Re-imports them to update mtm values in the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.flex_importer import import_mark_to_market_performance_csv

def backfill_mtm_from_csv():
    """Backfill mtm values from CSV files."""
    data_dir = project_root / "data" / "flex_reports"
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return False
    
    print(f"Searching for mark-to-market CSV files in {data_dir}...")
    print("=" * 60)
    
    # Find all mark-to-market performance CSV files
    csv_files = list(data_dir.glob("**/mark-to-market/*.csv"))
    
    if not csv_files:
        print("No mark-to-market CSV files found")
        return False
    
    print(f"Found {len(csv_files)} CSV file(s)")
    print()
    
    total_imported = 0
    total_updated = 0
    
    for csv_file in sorted(csv_files):
        try:
            print(f"Processing: {csv_file.name}")
            result = import_mark_to_market_performance_csv(
                str(csv_file),
                account_id=None,  # Will be extracted from CSV
            )
            
            imported = result.get("imported", 0)
            updated = result.get("updated", 0)
            
            total_imported += imported
            total_updated += updated
            
            print(f"  ✓ Imported: {imported}, Updated: {updated}")
            if result.get("min_date") and result.get("max_date"):
                print(f"  Date range: {result['min_date']} to {result['max_date']}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print()
    print("=" * 60)
    print(f"✓ Backfill completed")
    print(f"  Total imported: {total_imported}")
    print(f"  Total updated: {total_updated}")
    print()
    print("Note: Updated records now have mtm values from CSV files")
    
    return True

if __name__ == "__main__":
    try:
        success = backfill_mtm_from_csv()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
