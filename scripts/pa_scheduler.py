#!/usr/bin/env python3
"""Python scheduler for daily Portfolio Analyst automation.

Usage:
    python scripts/pa_scheduler.py --run-now          # Run once immediately
    python scripts/pa_scheduler.py --daemon           # Run daily at 09:00
    python scripts/pa_scheduler.py --daemon --time 21:00  # Custom time
"""
import sys
import logging
import time
import schedule
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.automate_pa_daily import automate_pa_daily
from dotenv import load_dotenv
load_dotenv()

# Setup logging
log_file = project_root / "pa_scheduler.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)s │ %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_file, mode="a")],
)
logger = logging.getLogger(__name__)


def run_job():
    """Execute PA automation job."""
    logger.info("=" * 50)
    logger.info(f"Scheduled PA automation starting: {datetime.now():%Y-%m-%d %H:%M}")
    logger.info("=" * 50)
    
    try:
        result = automate_pa_daily()
        status = "✓ Success" if result["success"] else f"✗ Failed: {result['error']}"
        logger.info(f"Result: {status}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="PA automation scheduler")
    parser.add_argument("--run-now", action="store_true", help="Run immediately and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--time", default="09:00", help="Daily run time (HH:MM)")
    
    args = parser.parse_args()
    
    if args.run_now:
        run_job()
        return 0
    
    if args.daemon:
        schedule.every().day.at(args.time).do(run_job)
        logger.info(f"Scheduler started: daily at {args.time}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Stopped")
            return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
