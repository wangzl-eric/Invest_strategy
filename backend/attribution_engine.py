"""PnL Attribution Engine - generates LLM-powered explanations for PnL movements."""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal
from backend.llm_client import QwenLLMClient, AttributionExplanation
from backend.models import PnLAttribution, PnLHistory
from backend.news_service import NewsService
from backtests.strategies import get_signal_metadata, SIGNAL_METADATA

logger = logging.getLogger(__name__)

# Trigger thresholds
PORTFOLIO_PCT_THRESHOLD = 1.0  # 1% change triggers analysis
PORTFOLIO_DOLLAR_THRESHOLD = 5000  # $5K change triggers analysis
SIGNAL_PCT_THRESHOLD = 2.0  # 2% for individual signals


class AttributionEngine:
    """Engine for generating PnL attributions."""

    def __init__(
        self,
        db_session: Optional[Session] = None,
        news_service: Optional[NewsService] = None,
        llm_client: Optional[QwenLLMClient] = None,
    ):
        """Initialize attribution engine.

        Args:
            db_session: Database session (creates one if not provided)
            news_service: NewsService instance (creates one if not provided)
            llm_client: QwenLLMClient instance (creates one if not provided)
        """
        self._db = db_session
        self._news_service = news_service
        self._llm_client = llm_client

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    @property
    def news_service(self) -> NewsService:
        if self._news_service is None:
            self._news_service = NewsService()
        return self._news_service

    @property
    def llm_client(self) -> QwenLLMClient:
        if self._llm_client is None:
            self._llm_client = QwenLLMClient()
        return self._llm_client

    def should_trigger_attribution(
        self,
        scope: str,
        pnl_change_pct: float,
        pnl_change_dollar: float,
    ) -> bool:
        """Check if attribution should be triggered.

        Args:
            scope: 'portfolio' or 'signal'
            pnl_change_pct: Percent PnL change
            pnl_change_dollar: Dollar PnL change

        Returns:
            True if attribution should run
        """
        if scope == "portfolio":
            return (
                abs(pnl_change_pct) >= PORTFOLIO_PCT_THRESHOLD
                and abs(pnl_change_dollar) >= PORTFOLIO_DOLLAR_THRESHOLD
            )
        else:
            return abs(pnl_change_pct) >= SIGNAL_PCT_THRESHOLD

    def get_positions_for_signal(self, signal_name: str) -> List[str]:
        """Get position symbols for a signal/portfolio.

        Args:
            signal_name: Name of signal or portfolio

        Returns:
            List of position symbols
        """
        metadata = get_signal_metadata(signal_name)
        if metadata and metadata.get("positions"):
            return metadata["positions"]
        return []

    def get_previous_summaries(
        self,
        signal_name: str,
        days: int = 5,
    ) -> str:
        """Get previous attribution summaries for context.

        Args:
            signal_name: Name of signal or portfolio
            days: Number of days to look back

        Returns:
            Formatted string of previous summaries
        """
        cutoff = datetime.now() - timedelta(days=days)

        previous = (
            self.db.query(PnLAttribution)
            .filter(
                PnLAttribution.target_name == signal_name,
                PnLAttribution.analysis_date >= cutoff,
                PnLAttribution.status == "success",
            )
            .order_by(PnLAttribution.analysis_date.desc())
            .limit(days)
            .all()
        )

        if not previous:
            return ""

        formatted = []
        for attr in reversed(previous):  # Oldest first for context
            date = attr.analysis_date.strftime("%Y-%m-%d")
            try:
                explanation = json.loads(attr.explanation_json)
                narrative = explanation.get("narrative", "No narrative")[:100]
                sentiment = explanation.get("sentiment", "unknown")
            except (json.JSONDecodeError, TypeError):
                narrative = "Parse error"
                sentiment = "unknown"

            formatted.append(
                f"- {date}: {sentiment.upper()} - {narrative}..."
            )

        return "\n".join(formatted)

    def get_portfolio_pnl_change(
        self,
        account_id: str,
        date: datetime,
    ) -> Dict[str, float]:
        """Get portfolio PnL change for a date.

        Args:
            account_id: Account ID
            date: Date to analyze

        Returns:
            Dict with pnl_change_pct, pnl_change_dollar, previous_pnl, current_pnl
        """
        # Get today's and yesterday's PnL
        today = (
            self.db.query(PnLHistory)
            .filter(
                PnLHistory.account_id == account_id,
                PnLHistory.date <= date,
            )
            .order_by(PnLHistory.date.desc())
            .first()
        )

        yesterday = (
            self.db.query(PnLHistory)
            .filter(
                PnLHistory.account_id == account_id,
                PnLHistory.date < date,
            )
            .order_by(PnLHistory.date.desc())
            .first()
        )

        if not today or not yesterday:
            return {
                "pnl_change_pct": 0.0,
                "pnl_change_dollar": 0.0,
                "previous_pnl": 0.0,
                "current_pnl": 0.0,
            }

        current_pnl = today.total_pnl or 0.0
        previous_pnl = yesterday.total_pnl or 0.0
        pnl_change_dollar = current_pnl - previous_pnl

        # Calculate percent change
        if previous_pnl != 0:
            pnl_change_pct = (pnl_change_dollar / abs(previous_pnl)) * 100
        else:
            pnl_change_pct = 0.0

        return {
            "pnl_change_pct": pnl_change_pct,
            "pnl_change_dollar": pnl_change_dollar,
            "previous_pnl": previous_pnl,
            "current_pnl": current_pnl,
        }

    async def fetch_news_for_positions(
        self,
        symbols: List[str],
        date: datetime,
    ) -> List[Dict[str, Any]]:
        """Fetch news for position symbols.

        Args:
            symbols: List of position symbols
            date: Date to fetch news for

        Returns:
            List of news articles
        """
        all_articles = []

        # Connect to IBKR if not connected
        await self.news_service.connect()

        try:
            # Fetch news for each symbol (limit to avoid rate limits)
            for symbol in symbols[:10]:  # Max 10 symbols
                try:
                    articles = await self.news_service.get_equity_news(
                        symbol,
                        max_articles=3,
                    )
                    all_articles.extend(articles)
                except Exception as e:
                    logger.warning(f"Failed to get news for {symbol}: {e}")

        finally:
            await self.news_service.disconnect()

        return all_articles

    async def run_attribution(
        self,
        scope: str,
        target_name: str,
        account_id: Optional[str],
        date: datetime,
        pnl_change_pct: float,
        pnl_change_dollar: float,
        previous_pnl: float = 0.0,
        current_pnl: float = 0.0,
        positions: Optional[List[Dict[str, Any]]] = None,
        trigger_type: str = "manual",
    ) -> PnLAttribution:
        """Run full attribution for a signal/portfolio.

        Args:
            scope: 'portfolio' or 'signal'
            target_name: Name of target (e.g., 'main_portfolio', 'momentum_tech')
            account_id: Account ID (optional)
            date: Date being analyzed
            pnl_change_pct: Percent PnL change
            pnl_change_dollar: Dollar PnL change
            previous_pnl: Previous day's PnL
            current_pnl: Current day's PnL
            positions: List of position impacts (optional)
            trigger_type: What triggered this (threshold_portfolio, threshold_signal, manual)

        Returns:
            Saved PnLAttribution record
        """
        logger.info(
            f"Running attribution for {scope}/{target_name} on {date}: "
            f"${pnl_change_dollar:+.2f} ({pnl_change_pct:+.2f}%)"
        )

        # Get strategy metadata
        metadata = get_signal_metadata(target_name) or {}
        strategy_thesis = metadata.get("thesis", "No thesis available")
        expected_behavior = metadata.get("regime_preference", "normal")
        factor_exposure = metadata.get("factors", [])

        # Get position symbols
        position_symbols = positions or []
        if not position_symbols:
            position_symbols = self.get_positions_for_signal(target_name)

        # Fetch news
        news_articles = []
        news_sources = ""
        try:
            if position_symbols:
                news_articles = await self.fetch_news_for_positions(
                    position_symbols, date
                )
                news_sources = "ibkr"
        except Exception as e:
            logger.warning(f"Failed to fetch news: {e}")

        # Get previous summaries
        previous_summaries = self.get_previous_summaries(target_name)

        # Generate LLM attribution
        explanation = None
        status = "success"
        error_message = ""
        confidence = 0.0

        if self.llm_client.is_configured:
            try:
                news_str = self.llm_client.format_news_for_prompt(news_articles)
                positions_str = self.llm_client.format_positions_for_prompt(
                    positions or []
                )

                explanation = await self.llm_client.generate_attribution(
                    signal_name=target_name,
                    strategy_thesis=strategy_thesis,
                    expected_behavior=expected_behavior,
                    factor_exposure=factor_exposure,
                    previous_summaries=previous_summaries,
                    date=date,
                    market_regime="normal",  # Could add regime detection
                    market_moves="",  # Could add market moves
                    news_articles=news_str,
                    position_impacts=positions_str,
                    pnl_change_dollar=pnl_change_dollar,
                    pnl_change_pct=pnl_change_pct,
                )

                confidence = explanation.confidence

            except Exception as e:
                logger.error(f"LLM attribution failed: {e}")
                status = "failed"
                error_message = str(e)
        else:
            logger.warning("LLM not configured, skipping attribution")
            status = "skipped"
            error_message = "QWEN_API_KEY not configured"

        # Build explanation JSON
        if explanation:
            explanation_json = json.dumps({
                "sentiment": explanation.sentiment,
                "themes": explanation.themes,
                "catalysts": explanation.catalysts,
                "narrative": explanation.narrative,
                "strategy_specific_impact": explanation.strategy_specific_impact,
                "confidence": explanation.confidence,
            })
        else:
            explanation_json = "{}"

        # Build news articles JSON
        news_articles_json = json.dumps([
            {
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "timestamp": str(a.get("timestamp", "")),
                "summary": a.get("summary", ""),
            }
            for a in news_articles
        ])

        # Build position impacts JSON
        position_impacts_json = json.dumps(positions or [])

        # Save to database
        attribution = PnLAttribution(
            scope=scope,
            account_id=account_id,
            target_name=target_name,
            analysis_date=date,
            pnl_change_pct=pnl_change_pct,
            pnl_change_dollar=pnl_change_dollar,
            previous_pnl=previous_pnl,
            current_pnl=current_pnl,
            news_articles_json=news_articles_json,
            news_sources=news_sources,
            news_count=len(news_articles),
            explanation_json=explanation_json,
            position_impacts_json=position_impacts_json,
            confidence=confidence,
            status=status,
            error_message=error_message,
            trigger_type=trigger_type,
        )

        self.db.add(attribution)
        self.db.commit()
        self.db.refresh(attribution)

        logger.info(f"Attribution saved: ID={attribution.id}, status={status}")

        return attribution

    async def run_daily_attribution(
        self,
        account_id: str,
        date: Optional[datetime] = None,
    ) -> List[PnLAttribution]:
        """Run daily attribution for portfolio and all signals.

        Args:
            account_id: Account ID
            date: Date to analyze (defaults to today)

        Returns:
            List of created attribution records
        """
        date = date or datetime.now()

        results = []

        # Get portfolio PnL change
        pnl_data = self.get_portfolio_pnl_change(account_id, date)

        # Check portfolio threshold
        if self.should_trigger_attribution(
            "portfolio",
            pnl_data["pnl_change_pct"],
            pnl_data["pnl_change_dollar"],
        ):
            attr = await self.run_attribution(
                scope="portfolio",
                target_name="main_portfolio",
                account_id=account_id,
                date=date,
                pnl_change_pct=pnl_data["pnl_change_pct"],
                pnl_change_dollar=pnl_data["pnl_change_dollar"],
                previous_pnl=pnl_data["previous_pnl"],
                current_pnl=pnl_data["current_pnl"],
                trigger_type="threshold_portfolio",
            )
            results.append(attr)

        # Run attribution for each known signal
        for signal_name in SIGNAL_METADATA.keys():
            if signal_name == "main_portfolio":
                continue  # Already done

            # Get signal-specific PnL (placeholder - would need signal PnL tracking)
            # For now, use portfolio data as proxy
            signal_attr = await self.run_attribution(
                scope="signal",
                target_name=signal_name,
                account_id=account_id,
                date=date,
                pnl_change_pct=pnl_data["pnl_change_pct"],  # Would be signal-specific
                pnl_change_dollar=pnl_data["pnl_change_dollar"],  # Would be signal-specific
                previous_pnl=pnl_data["previous_pnl"],
                current_pnl=pnl_data["current_pnl"],
                trigger_type="threshold_signal",
            )
            results.append(signal_attr)

        return results


# Convenience function
async def run_attribution(
    signal_name: str,
    pnl_change_pct: float,
    pnl_change_dollar: float,
    date: Optional[datetime] = None,
    **kwargs,
) -> PnLAttribution:
    """Convenience function to run attribution.

    Args:
        signal_name: Name of signal/portfolio
        pnl_change_pct: Percent PnL change
        pnl_change_dollar: Dollar PnL change
        date: Date to analyze (defaults to today)
        **kwargs: Additional args for AttributionEngine.run_attribution

    Returns:
        Saved PnLAttribution record
    """
    engine = AttributionEngine()
    return await engine.run_attribution(
        scope="signal" if signal_name != "main_portfolio" else "portfolio",
        target_name=signal_name,
        account_id=kwargs.get("account_id"),
        date=date or datetime.now(),
        pnl_change_pct=pnl_change_pct,
        pnl_change_dollar=pnl_change_dollar,
        **kwargs,
    )
