"""Alert evaluation scheduler integration."""
import logging
import asyncio
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.alert_engine import alert_engine

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


def start_alert_scheduler():
    """Start the alert evaluation scheduler."""
    if scheduler.running:
        logger.warning("Alert scheduler already running")
        return
    
    # Schedule alert evaluation every minute
    scheduler.add_job(
        evaluate_alerts,
        trigger=IntervalTrigger(minutes=1),
        id="alert_evaluation",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Alert scheduler started (evaluating every 1 minute)")


def stop_alert_scheduler():
    """Stop the alert evaluation scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Alert scheduler stopped")


async def evaluate_alerts():
    """Evaluate all alert rules."""
    try:
        alert_engine.evaluate_all_rules()
    except Exception as e:
        logger.error(f"Error in scheduled alert evaluation: {e}", exc_info=True)
