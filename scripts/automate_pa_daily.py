#!/usr/bin/env python3
"""Daily Portfolio Analyst automation: download CSV → import to database.

Usage:
    python scripts/automate_pa_daily.py [--account-id ID] [--no-cleanup]

Workflow:
    1. Download Portfolio Analyst report from IBKR
    2. Import CSV data into pnl_history table
    3. Cleanup old CSV files (>30 days)
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# LOGGING
# ============================================================================

def setup_logging() -> logging.Logger:
    """Setup logging to console and file."""
    log_file = project_root / "pa_automation.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# AUTOMATION
# ============================================================================

def automate_pa_daily(
    account_id: Optional[str] = None,
    download_dir: Optional[str] = None,
    date_column: str = "Date",
    equity_column: str = "Equity",
    return_column: Optional[str] = None,
    date_format: Optional[str] = None,
    cleanup_old: bool = True,
    keep_days: int = 30,
) -> dict:
    """
    Download PA report and import into database.
    
    Returns:
        dict with: success, csv_path, rows_imported, error
    """
    from scripts.download_portfolio_analyst import download_pa_report
    from backend.flex_importer import import_portfolio_analyst_csv
    
    account_id = account_id or os.getenv("IBKR_ACCOUNT_ID")
    if not account_id:
        raise ValueError("Set IBKR_ACCOUNT_ID environment variable")
    
    result = {
        "success": False,
        "csv_path": None,
        "rows_imported": 0,
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        # Step 1: Download
        logger.info("━" * 50)
        logger.info(f"PA Automation: {account_id}")
        logger.info("━" * 50)
        
        logger.info("[1/3] Downloading report...")
        csv_path = download_pa_report(account_id=account_id, download_dir=download_dir)
        result["csv_path"] = str(csv_path)
        logger.info(f"      Downloaded: {csv_path.name}")
        
        # Step 2: Import
        logger.info("[2/3] Importing to database...")
        rows = import_portfolio_analyst_csv(
            csv_path=str(csv_path),
            account_id=account_id,
            date_column=date_column,
            equity_column=equity_column,
            return_column=return_column,
            date_format=date_format,
        )
        result["rows_imported"] = rows
        logger.info(f"      Imported: {rows} rows")
        
        # Step 3: Cleanup
        if cleanup_old and csv_path.parent.exists():
            logger.info("[3/3] Cleaning up old files...")
            cutoff = datetime.now() - timedelta(days=keep_days)
            deleted = 0
            for f in csv_path.parent.glob("pa_report_*.csv"):
                if f.stat().st_mtime < cutoff.timestamp():
                    f.unlink()
                    deleted += 1
            if deleted:
                logger.info(f"      Deleted: {deleted} old files")
        
        result["success"] = True
        logger.info("━" * 50)
        logger.info("✓ PA Automation completed successfully")
        logger.info("━" * 50)
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"✗ PA Automation failed: {e}", exc_info=True)
    
    return result


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Portfolio Analyst automation")
    parser.add_argument("--account-id", help="Account ID (or IBKR_ACCOUNT_ID env)")
    parser.add_argument("--download-dir", help="Download directory")
    parser.add_argument("--date-column", default="Date", help="CSV date column")
    parser.add_argument("--equity-column", default="Equity", help="CSV equity column")
    parser.add_argument("--return-column", help="CSV return column (optional)")
    parser.add_argument("--date-format", help="Date format string (optional)")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep all CSV files")
    parser.add_argument("--keep-days", type=int, default=30, help="Days to keep files")
    
    args = parser.parse_args()
    
    result = automate_pa_daily(
        account_id=args.account_id,
        download_dir=args.download_dir,
        date_column=args.date_column,
        equity_column=args.equity_column,
        return_column=args.return_column,
        date_format=args.date_format,
        cleanup_old=not args.no_cleanup,
        keep_days=args.keep_days,
    )
    
    if result["success"]:
        print(f"✓ Imported {result['rows_imported']} rows from {result['csv_path']}")
        return 0
    else:
        print(f"✗ Error: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
