"""LLM client for Qwen (DashScope) - generates PnL attribution explanations."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger(__name__)


class AttributionExplanation(BaseModel):
    """Structured LLM output for PnL attribution."""
    sentiment: str  # positive/negative/neutral
    themes: List[str]
    catalysts: List[str]
    narrative: str
    strategy_specific_impact: str
    confidence: float  # 0.0 - 1.0


class QwenLLMClient:
    """Client for Qwen LLM via DashScope API."""

    # Enhanced prompt template with strategy context
    PROMPT_TEMPLATE = """## Strategy Context
- Strategy Name: {signal_name}
- Strategy Thesis: {strategy_thesis}
- Expected Behavior: {expected_behavior}
- Primary Factors: {factor_exposure}

## Recent Attribution History (Last 5 Days)
{previous_summaries}

## Today's Market Context
- Date: {date}
- Market Regime: {market_regime}
- Key Market Moves: {market_moves}

## News Articles (Relevant to Positions)
{news_articles}

## Positions Impacted
{position_impacts}

## PnL Change
- Dollar Change: ${pnl_change_dollar:+.2f}
- Percent Change: {pnl_change_pct:+.2f}%

## Your Task
Generate a structured analysis explaining:
1. **What happened**: Brief description of the move
2. **Why it happened**: Root causes from news (cite specific articles)
3. **Strategy-specific impact**: How this affects {signal_name} given its thesis
4. **Previous context**: Connect to recent attribution history if relevant
5. **Themes & Catalysts**: Key themes and specific catalysts
6. **Narrative**: 2-3 sentence explanation a PM would use

Output in JSON format:
{{
  "sentiment": "positive/negative/neutral",
  "themes": ["theme1", "theme2"],
  "catalysts": ["catalyst1", "catalyst2"],
  "narrative": "...",
  "strategy_specific_impact": "...",
  "confidence": 0.0-1.0
}}
"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize Qwen client.

        Args:
            api_key: Qwen/DashScope API key (defaults to config)
            model: Model name (defaults to config)
            base_url: API base URL (defaults to DashScope)
            max_tokens: Max tokens in response
            temperature: Sampling temperature
        """
        self._config = settings.llm
        self.api_key = api_key or self._config.qwen_api_key
        self.model = model or self._config.qwen_model
        self.base_url = base_url or self._config.qwen_base_url
        self.max_tokens = max_tokens or self._config.qwen_max_tokens
        self.temperature = temperature or self._config.qwen_temperature

    @property
    def is_configured(self) -> bool:
        return self._config.is_configured

    def _build_prompt(
        self,
        signal_name: str,
        strategy_thesis: str,
        expected_behavior: str,
        factor_exposure: List[str],
        previous_summaries: str,
        date: datetime,
        market_regime: str,
        market_moves: str,
        news_articles: str,
        position_impacts: str,
        pnl_change_dollar: float,
        pnl_change_pct: float,
    ) -> str:
        """Build the prompt with all context."""
        return self.PROMPT_TEMPLATE.format(
            signal_name=signal_name,
            strategy_thesis=strategy_thesis,
            expected_behavior=expected_behavior,
            factor_exposure=", ".join(factor_exposure),
            previous_summaries=previous_summaries or "No previous summaries available.",
            date=date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date),
            market_regime=market_regime,
            market_moves=market_moves,
            news_articles=news_articles,
            position_impacts=position_impacts,
            pnl_change_dollar=pnl_change_dollar,
            pnl_change_pct=pnl_change_pct,
        )

    async def generate_attribution(
        self,
        signal_name: str,
        strategy_thesis: str,
        expected_behavior: str = "normal",
        factor_exposure: Optional[List[str]] = None,
        previous_summaries: Optional[str] = None,
        date: Optional[datetime] = None,
        market_regime: str = "normal",
        market_moves: str = "",
        news_articles: str = "",
        position_impacts: str = "",
        pnl_change_dollar: float = 0.0,
        pnl_change_pct: float = 0.0,
    ) -> AttributionExplanation:
        """Generate attribution explanation from LLM.

        Args:
            signal_name: Name of signal/portfolio
            strategy_thesis: What the strategy tries to capture
            expected_behavior: Expected behavior in current regime
            factor_exposure: List of factor exposures
            previous_summaries: Previous attribution summaries
            date: Date being analyzed
            market_regime: Current market regime
            market_moves: Key market moves
            news_articles: News articles to analyze
            position_impacts: Position-level impacts
            pnl_change_dollar: Dollar PnL change
            pnl_change_pct: Percent PnL change

        Returns:
            AttributionExplanation with structured output

        Raises:
            ValueError: If API key not configured
            RuntimeError: If API call fails
        """
        if not self.is_configured:
            raise ValueError("QWEN_API_KEY not configured")

        factor_exposure = factor_exposure or []
        date = date or datetime.now()

        prompt = self._build_prompt(
            signal_name=signal_name,
            strategy_thesis=strategy_thesis,
            expected_behavior=expected_behavior,
            factor_exposure=factor_exposure,
            previous_summaries=previous_summaries or "",
            date=date,
            market_regime=market_regime,
            market_moves=market_moves,
            news_articles=news_articles,
            position_impacts=position_impacts,
            pnl_change_dollar=pnl_change_dollar,
            pnl_change_pct=pnl_change_pct,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return AttributionExplanation(
                    sentiment=parsed.get("sentiment", "neutral"),
                    themes=parsed.get("themes", []),
                    catalysts=parsed.get("catalysts", []),
                    narrative=parsed.get("narrative", ""),
                    strategy_specific_impact=parsed.get("strategy_specific_impact", ""),
                    confidence=parsed.get("confidence", 0.5),
                )

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling Qwen API: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Qwen API error: {e.response.status_code}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                raise RuntimeError(f"Invalid JSON from LLM: {e}")
            except Exception as e:
                logger.error(f"Unexpected error calling Qwen API: {e}")
                raise RuntimeError(f"Qwen API error: {e}")

    def format_news_for_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles for prompt.

        Args:
            articles: List of article dicts with title, source, timestamp, summary

        Returns:
            Formatted string for prompt
        """
        if not articles:
            return "No relevant news articles found."

        formatted = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            timestamp = article.get("timestamp", "")
            summary = article.get("summary", article.get("description", ""))

            formatted.append(
                f"{i}. [{source}] {title}\n   {summary}"
            )

        return "\n\n".join(formatted)

    def format_positions_for_prompt(self, positions: List[Dict[str, Any]]) -> str:
        """Format position impacts for prompt.

        Args:
            positions: List of position dicts with symbol, pnl_contribution, reason

        Returns:
            Formatted string for prompt
        """
        if not positions:
            return "No position data available."

        formatted = []
        for pos in positions:
            symbol = pos.get("symbol", "Unknown")
            pnl = pos.get("pnl_contribution", 0)
            reason = pos.get("reason", "Unknown reason")

            formatted.append(f"- {symbol}: ${pnl:+.2f} ({reason})")

        return "\n".join(formatted)


# Convenience function
async def generate_attribution(
    signal_name: str,
    strategy_thesis: str,
    news_articles: List[Dict[str, Any]],
    positions: List[Dict[str, Any]],
    pnl_change_dollar: float,
    pnl_change_pct: float,
    **kwargs,
) -> AttributionExplanation:
    """Convenience function to generate attribution.

    Args:
        signal_name: Name of signal/portfolio
        strategy_thesis: What the strategy tries to capture
        news_articles: List of news article dicts
        positions: List of position impact dicts
        pnl_change_dollar: Dollar PnL change
        pnl_change_pct: Percent PnL change
        **kwargs: Additional args passed to QwenLLMClient.generate_attribution

    Returns:
        AttributionExplanation
    """
    client = QwenLLMClient()

    news_str = client.format_news_for_prompt(news_articles)
    positions_str = client.format_positions_for_prompt(positions)

    return await client.generate_attribution(
        signal_name=signal_name,
        strategy_thesis=strategy_thesis,
        news_articles=news_str,
        position_impacts=positions_str,
        pnl_change_dollar=pnl_change_dollar,
        pnl_change_pct=pnl_change_pct,
        **kwargs,
    )
