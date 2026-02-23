#!/usr/bin/env python3
"""Start the IBKR data scheduler to automatically fetch account data."""
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.scheduler import scheduler
from backend.ibkr_client import IBKRClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the scheduler."""
    account_id = None
    
    # Get account ID from command line if provided
    if len(sys.argv) > 1:
        account_id = sys.argv[1]
        logger.info(f"Using account ID: {account_id}")
    else:
        logger.info("No account ID provided. Will auto-detect from IBKR.")
    
    # Create and connect IBKR client
    ibkr_client = IBKRClient()
    
    logger.info("Connecting to IBKR TWS/Gateway...")
    if not await ibkr_client.connect():
        logger.error("Failed to connect to IBKR. Make sure TWS/Gateway is running and API is enabled.")
        sys.exit(1)
    
    logger.info("Successfully connected to IBKR!")
    
    # Get account ID if not provided
    if not account_id:
        try:
            account_summary = await ibkr_client.get_account_summary()
            account_id = account_summary.get('AccountId')
            if account_id:
                logger.info(f"Auto-detected account ID: {account_id}")
            else:
                logger.warning("Could not auto-detect account ID. Please provide it as an argument.")
        except Exception as e:
            logger.warning(f"Could not auto-detect account ID: {e}")
    
    if not account_id:
        logger.error("Account ID is required. Usage: python start_scheduler.py <ACCOUNT_ID>")
        await ibkr_client.disconnect()
        sys.exit(1)
    
    # Start scheduler
    logger.info(f"Starting scheduler for account: {account_id}")
    scheduler.start(account_id=account_id)
    
    logger.info("=" * 60)
    logger.info("Scheduler started successfully!")
    logger.info(f"Account ID: {account_id}")
    logger.info("Data will be fetched automatically at configured intervals.")
    logger.info("Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("\nStopping scheduler...")
        scheduler.stop()
        await ibkr_client.disconnect()
        logger.info("Scheduler stopped. Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)

