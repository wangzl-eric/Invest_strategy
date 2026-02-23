"""API routes for report generation and scheduling."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.reporting import report_generator, scheduled_report_service
from backend.auth import get_current_user_or_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/reports/performance")
async def generate_performance_report(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Generate and download a performance report PDF."""
    try:
        if not account_id:
            from backend.models import AccountSnapshot
            from sqlalchemy import desc
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        pdf_buffer = report_generator.generate_performance_report(
            account_id, start_date, end_date
        )
        
        filename = f"performance_report_{account_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating performance report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/trades")
async def generate_trade_report(
    account_id: Optional[str] = Query(None, description="Account ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user = Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Generate and download a trade history report PDF."""
    try:
        if not account_id:
            from backend.models import AccountSnapshot
            from sqlalchemy import desc
            latest = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.timestamp)).first()
            if latest:
                account_id = latest.account_id
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        pdf_buffer = report_generator.generate_trade_report(
            account_id, start_date, end_date
        )
        
        filename = f"trade_report_{account_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating trade report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/schedule")
async def schedule_report(
    account_id: str,
    report_type: str = Query(..., description="Type: performance, trades, or combined"),
    frequency: str = Query(..., description="Frequency: daily, weekly, monthly"),
    recipient_email: str = Query(..., description="Email address to send report"),
    report_time: str = Query("09:00", description="Time to send report (HH:MM)"),
    current_user = Depends(get_current_user_or_api_key),
):
    """Schedule a recurring report."""
    try:
        if report_type not in ["performance", "trades", "combined"]:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        if frequency not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="Invalid frequency")
        
        # Schedule the report
        scheduled_report_service.schedule_daily_report(
            account_id, recipient_email, report_time
        )
        
        return {
            "status": "scheduled",
            "account_id": account_id,
            "report_type": report_type,
            "frequency": frequency,
            "recipient": recipient_email,
            "report_time": report_time
        }
    except Exception as e:
        logger.error(f"Error scheduling report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
