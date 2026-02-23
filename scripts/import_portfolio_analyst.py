#!/usr/bin/env python3
"""Import Portfolio Analyst CSV into the database.

Usage:
    python scripts/import_portfolio_analyst.py <csv_file> <account_id>
    
Example:
    python scripts/import_portfolio_analyst.py data/pa_reports/report.csv U1234567
"""
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.flex_importer import import_portfolio_analyst_csv


def main():
    parser = argparse.ArgumentParser(description="Import Portfolio Analyst CSV to database")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("account_id", help="IBKR account ID (e.g., U1234567)")
    parser.add_argument("--date-column", default="Date", help="Date column name")
    parser.add_argument("--equity-column", default="Equity", help="Equity column name")
    parser.add_argument("--return-column", help="Return column name (optional)")
    parser.add_argument("--date-format", help="Date format (e.g., %%Y-%%m-%%d)")
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"✗ File not found: {args.csv_file}")
        return 1
    
    print(f"Importing: {args.csv_file}")
    print(f"Account:   {args.account_id}")
    
    try:
        rows = import_portfolio_analyst_csv(
            csv_path=str(csv_path),
            account_id=args.account_id,
            date_column=args.date_column,
            equity_column=args.equity_column,
            return_column=args.return_column,
            date_format=args.date_format,
        )
        
        print(f"✓ Imported {rows} rows")
        print(f"  Database: {project_root / 'ibkr_analytics.db'}")
        print(f"  API: http://localhost:8000/api/pnl/history?account_id={args.account_id}")
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
