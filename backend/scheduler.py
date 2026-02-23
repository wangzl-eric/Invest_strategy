"""Background scheduler to periodically fetch PnL snapshots from IBKR."""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from backend.config import settings
from backend.data_fetcher import DataFetcher
from backend.ibkr_client import IBKRClient

logger = logging.getLogger(__name__)


class PnLScheduler:
    """Simple asyncio-based scheduler for periodic PnL snapshots."""

    def __init__(self, account_id: Optional[str] = None):
        self.account_id = account_id
        self._task: Optional[asyncio.Task] = None
        self._stopped = asyncio.Event()

    async def _run_loop(self):
        """Internal loop that runs forever until stopped."""
        interval_minutes = settings.app.update_interval_minutes
        interval_seconds = max(interval_minutes, 1) * 60

        logger.info(
            "Starting PnL scheduler loop",
            extra={
                "interval_minutes": interval_minutes,
                "interval_seconds": interval_seconds,
            },
        )

        while not self._stopped.is_set():
            start_ts = datetime.utcnow().isoformat()
            try:
                logger.info(
                    "PnL scheduler tick: fetching data",
                    extra={"timestamp": start_ts, "account_id": self.account_id},
                )

                ibkr_client = IBKRClient()
                data_fetcher = DataFetcher(ibkr_client)

                # Connect, fetch account snapshot AND PnL, then disconnect
                if await ibkr_client.connect():
                    # Update AccountSnapshot so frontend Net Liquidation card updates
                    await data_fetcher.fetch_and_store_account_snapshot(self.account_id)
                    # Update PnLHistory for historical tracking
                    await data_fetcher.fetch_and_store_pnl(self.account_id)
                    await ibkr_client.disconnect()
                else:
                    logger.warning("PnL scheduler could not connect to IBKR")

            except Exception as e:
                logger.error(f"PnL scheduler error during fetch: {e}")

            # Wait for next interval or stop
            try:
                await asyncio.wait_for(self._stopped.wait(), timeout=interval_seconds)
                # If we get here, stop was requested
                break
            except asyncio.TimeoutError:
                # Normal wake-up for next tick - loop continues
                logger.debug(f"Scheduler waiting for next tick in {interval_seconds}s")
                continue

        logger.info("PnL scheduler loop stopped")

    def start(self):
        """Start the background scheduler task."""
        if self._task is not None and not self._task.done():
            logger.warning("PnL scheduler task already running")
            return

        try:
            # Try to get the running event loop (works in FastAPI context)
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Fallback to get_event_loop if no loop is running
            loop = asyncio.get_event_loop()
        
        self._stopped.clear()
        self._task = loop.create_task(self._run_loop())
        logger.info(
            "PnL scheduler task started",
            extra={"interval_minutes": settings.app.update_interval_minutes}
        )

    async def stop(self):
        """Stop the background scheduler task."""
        if self._task is None:
            return

        self._stopped.set()
        try:
            await self._task
        except Exception:
            # Swallow exceptions on shutdown
            pass
        logger.info("PnL scheduler task cancelled")

"""Scheduled jobs for data updates."""
import logging
import asyncio
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import settings
from backend.data_fetcher import DataFetcher
from backend.data_processor import DataProcessor

logger = logging.getLogger(__name__)


class Scheduler:
    """Scheduler for periodic data updates."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.data_fetcher = DataFetcher()
        self.data_processor = DataProcessor()
        self.running = False
    
    async def update_data_job(self, account_id: Optional[str] = None):
        """Job to fetch and store account data."""
        try:
            logger.info("Starting scheduled data update...")
            
            # Fetch all data
            result = await self.data_fetcher.fetch_all(account_id)
            account_id = result['account_id']
            
            # Calculate performance metrics
            await asyncio.to_thread(
                self.data_processor.calculate_performance_metrics,
                account_id
            )
            
            # Evaluate alert rules after data update
            try:
                from backend.alert_scheduler import alert_scheduler
                await alert_scheduler.evaluate_and_notify(account_id)
            except Exception as e:
                logger.error(f"Error evaluating alerts: {e}", exc_info=True)
            
            logger.info("Completed scheduled data update")
            
        except Exception as e:
            logger.error(f"Error in scheduled data update: {e}")
    
    def start(self, account_id: Optional[str] = None):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        interval_minutes = settings.app.update_interval_minutes
        
        # Add job to scheduler
        self.scheduler.add_job(
            self.update_data_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[account_id],
            id='update_data',
            name='Update IBKR account data',
            replace_existing=True,
        )
        
        self.scheduler.start()
        self.running = True
        logger.info(f"Scheduler started with {interval_minutes} minute interval")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            return
        
        self.scheduler.shutdown()
        self.running = False
        logger.info("Scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()


# Global scheduler instance
scheduler = Scheduler()

