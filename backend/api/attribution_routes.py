"""Attribution API routes for PnL attribution."""
import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.attribution_engine import AttributionEngine
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/attribution", tags=["attribution"])


# ============== Request/Response Models ==============


class AttributionRequest(BaseModel):
    """Request model for running attribution."""
    scope: str = "signal"  # 'portfolio' or 'signal'
    target_name: str  # e.g., 'main_portfolio', 'momentum_tech'
    account_id: Optional[str] = None
    date: Optional[str] = None  # ISO format date string
    pnl_change_pct: float
    pnl_change_dollar: float
    previous_pnl: float = 0.0
    current_pnl: float = 0.0
    positions: Optional[List[dict]] = None  # [{"symbol": "AAPL", "pnl_contribution": -500, "reason": "earnings_miss"}]
    trigger_type: str = "manual"


class AttributionResponse(BaseModel):
    """Response model for attribution."""
    id: int
    scope: str
    target_name: str
    analysis_date: str
    pnl_change_pct: float
    pnl_change_dollar: float
    news_count: int
    sentiment: Optional[str] = None
    themes: Optional[List[str]] = None
    catalysts: Optional[List[str]] = None
    narrative: Optional[str] = None
    strategy_specific_impact: Optional[str] = None
    confidence: Optional[float] = None
    status: str
    error_message: str = ""


class DailyAttributionRequest(BaseModel):
    """Request model for daily attribution run."""
    account_id: str
    date: Optional[str] = None  # ISO format date string


class AttributionHistoryRequest(BaseModel):
    """Request model for fetching attribution history."""
    target_name: Optional[str] = None
    start_date: Optional[str] = None  # ISO format
    end_date: Optional[str] = None  # ISO format
    limit: int = 50


class AttributionHistoryResponse(BaseModel):
    """Response model for attribution history."""
    attributions: List[AttributionResponse]
    total: int


class SignalListResponse(BaseModel):
    """Response model for available signals."""
    signals: dict  # {signal_name: metadata}


class LLMCreditsResponse(BaseModel):
    """Response model for LLM configuration status."""
    configured: bool
    model: str


# ============== API Endpoints ==============


@router.post("/run", response_model=AttributionResponse)
async def run_attribution(request: AttributionRequest):
    """Run attribution for a signal or portfolio.

    This endpoint triggers the full attribution pipeline:
    1. Fetches news for relevant positions
    2. Generates LLM explanation
    3. Stores result in database
    """
    try:
        # Parse date if provided
        date = None
        if request.date:
            date = datetime.fromisoformat(request.date)

        # Create engine and run attribution
        engine = AttributionEngine()

        attribution = await engine.run_attribution(
            scope=request.scope,
            target_name=request.target_name,
            account_id=request.account_id,
            date=date or datetime.now(),
            pnl_change_pct=request.pnl_change_pct,
            pnl_change_dollar=request.pnl_change_dollar,
            previous_pnl=request.previous_pnl,
            current_pnl=request.current_pnl,
            positions=request.positions,
            trigger_type=request.trigger_type,
        )

        # Parse explanation JSON
        try:
            explanation = json.loads(attribution.explanation_json)
        except (json.JSONDecodeError, TypeError):
            explanation = {}

        return AttributionResponse(
            id=attribution.id,
            scope=attribution.scope,
            target_name=attribution.target_name,
            analysis_date=attribution.analysis_date.isoformat(),
            pnl_change_pct=attribution.pnl_change_pct,
            pnl_change_dollar=attribution.pnl_change_dollar,
            news_count=attribution.news_count,
            sentiment=explanation.get("sentiment"),
            themes=explanation.get("themes"),
            catalysts=explanation.get("catalysts"),
            narrative=explanation.get("narrative"),
            strategy_specific_impact=explanation.get("strategy_specific_impact"),
            confidence=attribution.confidence,
            status=attribution.status,
            error_message=attribution.error_message,
        )

    except Exception as e:
        logger.error(f"Error running attribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily", response_model=List[AttributionResponse])
async def run_daily_attribution(request: DailyAttributionRequest):
    """Run daily attribution for portfolio and all signals.

    This endpoint:
    1. Checks if portfolio PnL crosses threshold
    2. If yes, runs attribution for portfolio
    3. Runs attribution for each known signal
    """
    try:
        # Parse date if provided
        date = None
        if request.date:
            date = datetime.fromisoformat(request.date)

        # Create engine and run daily attribution
        engine = AttributionEngine()

        attributions = await engine.run_daily_attribution(
            account_id=request.account_id,
            date=date,
        )

        results = []
        for attr in attributions:
            try:
                explanation = json.loads(attr.explanation_json)
            except (json.JSONDecodeError, TypeError):
                explanation = {}

            results.append(
                AttributionResponse(
                    id=attr.id,
                    scope=attr.scope,
                    target_name=attr.target_name,
                    analysis_date=attr.analysis_date.isoformat(),
                    pnl_change_pct=attr.pnl_change_pct,
                    pnl_change_dollar=attr.pnl_change_dollar,
                    news_count=attr.news_count,
                    sentiment=explanation.get("sentiment"),
                    themes=explanation.get("themes"),
                    catalysts=explanation.get("catalysts"),
                    narrative=explanation.get("narrative"),
                    strategy_specific_impact=explanation.get("strategy_specific_impact"),
                    confidence=attr.confidence,
                    status=attr.status,
                    error_message=attr.error_message,
                )
            )

        return results

    except Exception as e:
        logger.error(f"Error running daily attribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=AttributionHistoryResponse)
async def get_attribution_history(
    target_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
):
    """Get attribution history."""
    try:
        from backend.database import SessionLocal
        from backend.models import PnLAttribution

        db = SessionLocal()
        try:
            query = db.query(PnLAttribution)

            # Apply filters
            if target_name:
                query = query.filter(PnLAttribution.target_name == target_name)

            if start_date:
                start = datetime.fromisoformat(start_date)
                query = query.filter(PnLAttribution.analysis_date >= start)

            if end_date:
                end = datetime.fromisoformat(end_date)
                query = query.filter(PnLAttribution.analysis_date <= end)

            # Order by date descending
            query = query.order_by(PnLAttribution.analysis_date.desc())

            # Get total count
            total = query.count()

            # Apply limit
            attributions = query.limit(limit).all()

            results = []
            for attr in attributions:
                try:
                    explanation = json.loads(attr.explanation_json)
                except (json.JSONDecodeError, TypeError):
                    explanation = {}

                results.append(
                    AttributionResponse(
                        id=attr.id,
                        scope=attr.scope,
                        target_name=attr.target_name,
                        analysis_date=attr.analysis_date.isoformat(),
                        pnl_change_pct=attr.pnl_change_pct,
                        pnl_change_dollar=attr.pnl_change_dollar,
                        news_count=attr.news_count,
                        sentiment=explanation.get("sentiment"),
                        themes=explanation.get("themes"),
                        catalysts=explanation.get("catalysts"),
                        narrative=explanation.get("narrative"),
                        strategy_specific_impact=explanation.get("strategy_specific_impact"),
                        confidence=attr.confidence,
                        status=attr.status,
                        error_message=attr.error_message,
                    )
                )

            return AttributionHistoryResponse(
                attributions=results,
                total=total,
            )

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error fetching attribution history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals", response_model=SignalListResponse)
async def get_available_signals():
    """Get list of available signals with their metadata."""
    from backtests.strategies import SIGNAL_METADATA

    return SignalListResponse(
        signals=SIGNAL_METADATA
    )


@router.get("/config/status", response_model=LLMCreditsResponse)
async def get_llm_status():
    """Check if LLM is configured."""
    from backend.llm_client import QwenLLMClient

    client = QwenLLMClient()

    return LLMCreditsResponse(
        configured=client.is_configured,
        model=settings.llm.qwen_model if client.is_configured else "",
    )


@router.get("/health")
async def health_check():
    """Health check for attribution service."""
    from backend.llm_client import QwenLLMClient
    from backtests.strategies import SIGNAL_METADATA

    client = QwenLLMClient()

    return {
        "status": "healthy",
        "llm_configured": client.is_configured,
        "available_signals": len(SIGNAL_METADATA),
    }
