"""LLM client for Qwen (DashScope) - generates PnL attribution explanations."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from backend.config import settings
from backend.token_tracker import get_token_tracker

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
            "messages": [{"role": "user", "content": prompt}],
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

                # Extract token usage from response
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                # Record token usage
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    endpoint="attribution",
                    success=True,
                )

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
                logger.error(
                    f"HTTP error calling Qwen API: {e.response.status_code} - {e.response.text}"
                )
                # Record failed request
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    endpoint="attribution",
                    success=False,
                    error=str(e),
                )
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
            summary = article.get("summary", article.get("description", ""))

            formatted.append(f"{i}. [{source}] {title}\n   {summary}")

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


# ============================================================================
# Market Movers News Summary
# ============================================================================


class MarketMoversSummary(BaseModel):
    """Structured LLM output for market movers news summary."""

    overall_market_sentiment: str  # bullish/bearish/mixed/neutral
    key_themes: List[str]
    top_mover_summaries: List[
        Dict[str, str]
    ]  # [{"ticker": "...", "summary": "...", "driver": "..."}]
    market_narrative: str  # 2-3 sentence summary
    notable_patterns: List[str]  # sector rotation, risk-on/off, etc.
    confidence: float  # 0.0 - 1.0


class MarketMoversLLMClient(QwenLLMClient):
    """Client for generating market movers news summaries."""

    # Prompt template for market movers summarization
    MOVERS_SUMMARY_PROMPT = """## Market Movers Analysis Task

You are a financial market analyst providing a quick summary of today's market movers.

## Date
{date}

## Market Context
- Overall Market Sentiment: {market_sentiment}
- Trading Volume: {volume_note}

## Top Movers Data
{movers_data}

## News Articles for Each Mover
{news_articles}

## Your Task
Analyze the top movers and their news to provide:

1. **Overall Market Sentiment**: Is the market bullish, bearish, mixed, or neutral today?
2. **Key Themes**: What are the dominant themes driving moves? (e.g., "tech earnings", "Fed pivot", "inflation concerns", "sector rotation")
3. **Per-Mover Summaries**: For each top mover, provide:
   - What happened (price move)
   - Why it happened (key news/driver)
   - Brief context
4. **Market Narrative**: 2-3 sentence summary of what's happening in markets today
5. **Notable Patterns**: Any patterns like sector rotation, risk-on/off, momentum shifts, etc.

Output in JSON format:
{{
  "overall_market_sentiment": "bullish/bearish/mixed/neutral",
  "key_themes": ["theme1", "theme2", "theme3"],
  "top_mover_summaries": [
    {{
      "ticker": "TICKER",
      "summary": "1-2 sentence summary of what's happening",
      "driver": "key driver/news"
    }}
  ],
  "market_narrative": "2-3 sentence market summary",
  "notable_patterns": ["pattern1", "pattern2"],
  "confidence": 0.0-1.0
}}

Be concise and actionable. Focus on the most important information.
"""

    async def generate_movers_summary(
        self,
        movers: List[Dict[str, Any]],
        news_articles_by_ticker: Dict[str, List[Dict[str, Any]]],
        market_sentiment: str = "mixed",
        volume_note: str = "",
    ) -> MarketMoversSummary:
        """Generate a summary of market movers and their news.

        Args:
            movers: List of mover dicts with ticker, name, return_pct, direction, etc.
            news_articles_by_ticker: Dict mapping ticker to list of news articles
            market_sentiment: Overall market sentiment
            volume_note: Any note about trading volume

        Returns:
            MarketMoversSummary with structured output
        """
        if not self.is_configured:
            raise ValueError("QWEN_API_KEY not configured")

        # Format movers data for prompt
        movers_data = self._format_movers_for_prompt(movers)

        # Format news articles
        news_articles = self._format_news_articles_for_prompt(news_articles_by_ticker)

        prompt = self.MOVERS_SUMMARY_PROMPT.format(
            date=datetime.now().strftime("%Y-%m-%d"),
            market_sentiment=market_sentiment,
            volume_note=volume_note or "Normal trading volume",
            movers_data=movers_data,
            news_articles=news_articles,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
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

                # Extract token usage from response
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                # Record token usage
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    endpoint="mover-news",
                    success=True,
                )

                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return MarketMoversSummary(
                    overall_market_sentiment=parsed.get(
                        "overall_market_sentiment", "neutral"
                    ),
                    key_themes=parsed.get("key_themes", []),
                    top_mover_summaries=parsed.get("top_mover_summaries", []),
                    market_narrative=parsed.get("market_narrative", ""),
                    notable_patterns=parsed.get("notable_patterns", []),
                    confidence=parsed.get("confidence", 0.5),
                )

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error calling Qwen API: {e.response.status_code} - {e.response.text}"
                )
                # Record failed request
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    endpoint="mover-news",
                    success=False,
                    error=str(e),
                )
                raise RuntimeError(f"Qwen API error: {e.response.status_code}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                raise RuntimeError(f"Invalid JSON from LLM: {e}")
            except Exception as e:
                logger.error(f"Unexpected error calling Qwen API: {e}")
                raise RuntimeError(f"Qwen API error: {e}")

    def _format_movers_for_prompt(self, movers: List[Dict[str, Any]]) -> str:
        """Format movers data for prompt."""
        if not movers:
            return "No significant movers today."

        formatted = []
        for m in movers[:10]:  # Top 10 movers
            ticker = m.get("ticker", "")
            name = m.get("name", ticker)
            ret = m.get("return_pct", 0)
            direction = m.get("direction", "")
            z = m.get("z_score", 0)
            asset_class = m.get("asset_class", "")

            formatted.append(
                f"- {ticker} ({name}): {ret:+.2f}% ({direction}), z-score: {z:.2f}, asset class: {asset_class}"
            )

        return "\n".join(formatted)

    def _format_news_articles_for_prompt(
        self, news_by_ticker: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Format news articles by ticker for prompt."""
        if not news_by_ticker:
            return "No news articles available for analysis."

        formatted = []
        for ticker, articles in news_by_ticker.items():
            formatted.append(f"\n## {ticker} News:")
            if not articles:
                formatted.append("  - No news available")
                continue

            for i, article in enumerate(articles[:3], 1):  # Top 3 articles per ticker
                title = article.get("title", "No title")
                source = article.get("source", "Unknown")
                summary = article.get("summary", article.get("description", ""))
                formatted.append(f"  {i}. [{source}] {title}")
                if summary:
                    formatted.append(f"     {summary[:200]}...")

        return "\n".join(formatted)


# Convenience function
async def generate_movers_news_summary(
    movers: List[Dict[str, Any]],
    news_articles_by_ticker: Dict[str, List[Dict[str, Any]]],
    market_sentiment: str = "mixed",
    **kwargs,
) -> MarketMoversSummary:
    """Convenience function to generate market movers summary.

    Args:
        movers: List of mover dicts
        news_articles_by_ticker: Dict mapping ticker to news articles
        market_sentiment: Overall market sentiment
        **kwargs: Additional args passed to MarketMoversLLMClient

    Returns:
        MarketMoversSummary
    """
    client = MarketMoversLLMClient()
    return await client.generate_movers_summary(
        movers=movers,
        news_articles_by_ticker=news_articles_by_ticker,
        market_sentiment=market_sentiment,
        **kwargs,
    )


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


# ============================================================================
# Backtest Rigor Verdict
# ============================================================================

from pydantic import BaseModel


class VerdictExplanation(BaseModel):
    """Structured LLM output for backtest rigor verdict."""

    final_verdict: str  # PROCEED | PROCEED_WITH_CAUTION | NEEDS_WORK | ABANDON
    confidence: float  # 0.0 - 1.0
    reasoning: str  # Natural language explanation
    flags: List[str]  # Specific concerns identified
    suggestions: List[str]  # Actionable improvements


class VerdictLLMClient(QwenLLMClient):
    """Client for generating backtest rigor verdicts."""

    # Prompt template for verdict generation
    VERDICT_PROMPT = """## Task
You are a quantitative research expert evaluating a trading strategy backtest. You provide nuanced judgments that complement rule-based checks.

## Rule-Based Analysis Results
### Significance
- Sharpe (annualized): {sharpe}
- Probabilistic Sharpe: {psr:.1%}
- Deflated Sharpe: {deflated_sharpe}
- VERDICT: {sig_verdict}

### Walk-Forward Analysis
- Number of windows: {n_windows}
- Win Rate: {win_rate:.1%}
- Mean Return: {mean_return:.2%}
- Crisis Period Included: {crisis_included}
- VERDICT: {wf_verdict}

### Robustness Stress Test
- Base Sharpe: {base_sharpe}
- Costs +50% Sharpe: {costs_50_sharpe}
- Costs +100% Sharpe: {costs_100_sharpe}
- Slippage 10bps Sharpe: {slippage_10_sharpe}
- Slippage 25bps Sharpe: {slippage_25_sharpe}
- VERDICT: {rob_verdict}

### Beta Correlation
- SPY Correlation: {spy_correlation:.1%}
- QQQ Correlation: {qqq_correlation:.1%}
- VERDICT: {beta_verdict}

### Parameter Sensitivity
- Optimization iterations: {n_iterations}
- Optimization landscape: {landscape}
- Average turnover: {turnover:.1%}

## Hypothesis (if provided)
- Statement: {hypothesis}
- Who loses money: {who_loses_money}
- Economic mechanism: {economic_mechanism}
- Noise discrimination: {noise_discrimination}

## Your Task
1. Review the rule-based analysis results above
2. Provide a nuanced judgment considering:
   - Is the hypothesis economically plausible?
   - Are metrics borderline (close to thresholds) or clear-cut?
   - Are there any red flags not captured by the rules?
   - Does the strategy make economic sense?
3. Output a final verdict and actionable suggestions

## Verdict Guidelines
- PROCEED: Strong all-around, passes all tests clearly
- PROCEED_WITH_CAUTION: Good but has minor concerns (e.g., borderline metrics, beta heavy)
- NEEDS_WORK: Significant issues that need addressing before deployment
- ABANDON: Fundamental problems, likely no economic edge

## Override Policy
You may tighten the verdict (e.g., PROCEED → NEEDS_WORK) but should not loosen it unless the rule-based analysis is clearly wrong.

Output in JSON format:
{{
  "final_verdict": "PROCEED|PROCEED_WITH_CAUTION|NEEDS_WORK|ABANDON",
  "confidence": 0.0-1.0,
  "reasoning": "2-3 sentence explanation of your reasoning",
  "flags": ["specific concern 1", "specific concern 2"],
  "suggestions": ["actionable suggestion 1", "actionable suggestion 2"]
}}

Be concise and actionable.
"""

    async def generate_verdict(
        self,
        sharpe: float,
        psr: float,
        deflated_sharpe: float,
        sig_verdict: str,
        n_windows: int,
        win_rate: float,
        mean_return: float,
        crisis_included: bool,
        wf_verdict: str,
        base_sharpe: float,
        costs_50_sharpe: float,
        costs_100_sharpe: float,
        slippage_10_sharpe: float,
        slippage_25_sharpe: float,
        rob_verdict: str,
        spy_correlation: float,
        qqq_correlation: float,
        beta_verdict: str,
        n_iterations: int,
        landscape: str,
        turnover: float,
        hypothesis: str = "",
        who_loses_money: str = "",
        economic_mechanism: str = "",
        noise_discrimination: str = "",
    ) -> VerdictExplanation:
        """Generate a verdict for backtest rigor analysis.

        Args:
            sharpe: Sharpe ratio (annualized)
            psr: Probabilistic Sharpe Ratio
            deflated_sharpe: Deflated Sharpe Ratio
            sig_verdict: Rule-based significance verdict
            n_windows: Number of walk-forward windows
            win_rate: Walk-forward win rate
            mean_return: Walk-forward mean return
            crisis_included: Whether crisis period was included
            wf_verdict: Rule-based walk-forward verdict
            base_sharpe: Base Sharpe ratio
            costs_50_sharpe: Sharpe with 50% more costs
            costs_100_sharpe: Sharpe with 100% more costs
            slippage_10_sharpe: Sharpe with 10bps slippage
            slippage_25_sharpe: Sharpe with 25bps slippage
            rob_verdict: Rule-based robustness verdict
            spy_correlation: SPY correlation
            qqq_correlation: QQQ correlation
            beta_verdict: Rule-based beta verdict
            n_iterations: Number of optimization iterations
            landscape: Optimization landscape (FLAT/PEAKED)
            turnover: Average portfolio turnover
            hypothesis: Strategy hypothesis statement
            who_loses_money: Who loses money in this trade
            economic_mechanism: Economic mechanism
            noise_discrimination: How strategy discriminates noise

        Returns:
            VerdictExplanation with structured output
        """
        if not self.is_configured:
            raise ValueError("QWEN_API_KEY not configured")

        prompt = self.VERDICT_PROMPT.format(
            sharpe=sharpe,
            psr=psr,
            deflated_sharpe=deflated_sharpe,
            sig_verdict=sig_verdict,
            n_windows=n_windows,
            win_rate=win_rate,
            mean_return=mean_return,
            crisis_included=crisis_included,
            wf_verdict=wf_verdict,
            base_sharpe=base_sharpe,
            costs_50_sharpe=costs_50_sharpe,
            costs_100_sharpe=costs_100_sharpe,
            slippage_10_sharpe=slippage_10_sharpe,
            slippage_25_sharpe=slippage_25_sharpe,
            rob_verdict=rob_verdict,
            spy_correlation=spy_correlation,
            qqq_correlation=qqq_correlation,
            beta_verdict=beta_verdict,
            n_iterations=n_iterations,
            landscape=landscape,
            turnover=turnover,
            hypothesis=hypothesis or "[Not provided]",
            who_loses_money=who_loses_money or "[Not provided]",
            economic_mechanism=economic_mechanism or "[Not provided]",
            noise_discrimination=noise_discrimination or "[Not provided]",
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
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

                # Extract token usage
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                # Record token usage
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    endpoint="verdict",
                    success=True,
                )

                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return VerdictExplanation(
                    final_verdict=parsed.get("final_verdict", "NEEDS_WORK"),
                    confidence=parsed.get("confidence", 0.5),
                    reasoning=parsed.get("reasoning", ""),
                    flags=parsed.get("flags", []),
                    suggestions=parsed.get("suggestions", []),
                )

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error calling Qwen API: {e.response.status_code} - {e.response.text}"
                )
                token_tracker = get_token_tracker()
                token_tracker.record_usage(
                    model=self.model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    endpoint="verdict",
                    success=False,
                    error=str(e),
                )
                raise RuntimeError(f"Qwen API error: {e.response.status_code}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                raise RuntimeError(f"Invalid JSON from LLM: {e}")
            except Exception as e:
                logger.error(f"Unexpected error calling Qwen API: {e}")
                raise RuntimeError(f"Qwen API error: {e}")


# Convenience function
async def generate_verdict(
    sharpe: float,
    psr: float,
    deflated_sharpe: float,
    sig_verdict: str,
    n_windows: int,
    win_rate: float,
    mean_return: float,
    crisis_included: bool,
    wf_verdict: str,
    base_sharpe: float,
    costs_50_sharpe: float,
    costs_100_sharpe: float,
    slippage_10_sharpe: float,
    slippage_25_sharpe: float,
    rob_verdict: str,
    spy_correlation: float,
    qqq_correlation: float,
    beta_verdict: str,
    n_iterations: int,
    landscape: str,
    turnover: float,
    **kwargs,
) -> VerdictExplanation:
    """Convenience function to generate backtest verdict.

    Args:
        All metrics from the backtest analysis
        **kwargs: Additional args passed to VerdictLLMClient.generate_verdict

    Returns:
        VerdictExplanation
    """
    client = VerdictLLMClient()
    return await client.generate_verdict(
        sharpe=sharpe,
        psr=psr,
        deflated_sharpe=deflated_sharpe,
        sig_verdict=sig_verdict,
        n_windows=n_windows,
        win_rate=win_rate,
        mean_return=mean_return,
        crisis_included=crisis_included,
        wf_verdict=wf_verdict,
        base_sharpe=base_sharpe,
        costs_50_sharpe=costs_50_sharpe,
        costs_100_sharpe=costs_100_sharpe,
        slippage_10_sharpe=slippage_10_sharpe,
        slippage_25_sharpe=slippage_25_sharpe,
        rob_verdict=rob_verdict,
        spy_correlation=spy_correlation,
        qqq_correlation=qqq_correlation,
        beta_verdict=beta_verdict,
        n_iterations=n_iterations,
        landscape=landscape,
        turnover=turnover,
        **kwargs,
    )
