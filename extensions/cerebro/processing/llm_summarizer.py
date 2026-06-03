"""LLM summarizer for research papers.

Extends the QwenLLMClient pattern from backend/llm_client.py to
summarize academic papers and extract structured information.
Uses Qwen-Turbo for bulk summarization (cost-efficient).
"""

import json
import logging
from typing import Any, Dict, Optional

import httpx

from cerebro.config import cerebro_config

logger = logging.getLogger(__name__)


# Prompt for paper summarization and structured extraction
SUMMARIZE_PROMPT = """You are a quantitative finance research analyst. Analyze the following
research paper/article and extract structured information.

## Paper Title
{title}

## Authors
{authors}

## Source
{source}

## Full Text / Abstract
{text}

## Your Task
Extract the following information. Be precise and factual. If information is not
available in the text, use null.

Output ONLY valid JSON with these fields:
{{
  "one_line": "One-sentence summary of the paper's contribution",
  "methodology": "Description of the methodology used (2-3 sentences)",
  "signal_description": "If a trading signal is proposed, describe it. Otherwise 'No explicit signal'",
  "asset_class": ["List of asset classes: Equities, FX, Commodities, Rates, Crypto, Multi-Asset"],
  "expected_sharpe": null or float (annualized Sharpe ratio if reported),
  "data_requirements": ["List of data sources needed to replicate"],
  "implementation_complexity": "LOW or MEDIUM or HIGH",
  "key_findings": ["List of 2-4 key findings"],
  "limitations": ["List of 1-3 limitations noted by authors or obvious"],
  "novelty_claim": "What is novel about this paper vs existing literature",
  "backtest_period": "Start-End period if backtested, e.g., '2000-2023'. null if not reported",
  "sample_size": "Number of assets/observations if reported. null if not",
  "out_of_sample": true/false (did they test out-of-sample?),
  "transaction_costs_modeled": true/false (did they model transaction costs?)
}}

Be concise. Do not invent information not present in the text.
"""


class CerebroLLMClient:
    """LLM client for Cerebro paper summarization and extraction.

    Follows the QwenLLMClient pattern from backend/llm_client.py.
    Uses the same DashScope API endpoint and token tracking.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> None:
        """Initialize Cerebro LLM client.

        Falls back to backend LLM config for API key and base URL,
        but uses Cerebro-specific model and parameters.

        Args:
            api_key: Qwen/DashScope API key.
            model: Model name for summarization.
            base_url: API base URL.
            max_tokens: Max tokens in response.
            temperature: Sampling temperature.
        """
        # Import backend config for API key (shared across platform)
        try:
            from backend.config import settings as backend_settings

            self._api_key = api_key or backend_settings.llm.qwen_api_key
            self._base_url = base_url or backend_settings.llm.qwen_base_url
        except ImportError:
            import os

            self._api_key = api_key or os.getenv("QWEN_API_KEY", "")
            self._base_url = base_url or (
                "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            )

        self._model = model or cerebro_config.llm.bulk_model
        self._max_tokens = max_tokens or cerebro_config.llm.max_tokens
        self._temperature = temperature or cerebro_config.llm.temperature

    @property
    def is_configured(self) -> bool:
        """Check if the LLM client has a valid API key."""
        return bool(self._api_key)

    async def summarize_paper(
        self,
        title: str,
        authors: str,
        source: str,
        text: str,
    ) -> Dict[str, Any]:
        """Summarize a paper and extract structured fields via LLM.

        Args:
            title: Paper title.
            authors: Comma-separated author names.
            source: Source name (e.g., "arxiv", "ssrn").
            text: Full text or abstract to analyze.

        Returns:
            Dict with extracted fields matching PaperSummary schema.

        Raises:
            ValueError: If API key is not configured.
            RuntimeError: If API call fails or response is invalid.
        """
        if not self.is_configured:
            raise ValueError(
                "QWEN_API_KEY not configured. Set it in .env or environment."
            )

        # Truncate text to avoid token limits (keep first ~6000 chars)
        truncated_text = text[:6000] if len(text) > 6000 else text

        prompt = SUMMARIZE_PROMPT.format(
            title=title,
            authors=authors,
            source=source,
            text=truncated_text,
        )

        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Make an LLM API call and parse JSON response.

        Args:
            prompt: Full prompt text.

        Returns:
            Parsed JSON dict from LLM response.

        Raises:
            RuntimeError: If API call fails or JSON is invalid.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                # Track token usage if tracker is available
                self._record_usage(data)

                content = data["choices"][0]["message"]["content"]
                return json.loads(content)

            except httpx.HTTPStatusError as exc:
                logger.error(
                    "HTTP error calling LLM API: %s - %s",
                    exc.response.status_code,
                    exc.response.text[:500],
                )
                self._record_failure(str(exc))
                raise RuntimeError(f"LLM API error: {exc.response.status_code}")
            except json.JSONDecodeError as exc:
                logger.error("Failed to parse LLM JSON response: %s", exc)
                raise RuntimeError(f"Invalid JSON from LLM: {exc}")
            except Exception as exc:
                logger.error("Unexpected LLM error: %s", exc)
                self._record_failure(str(exc))
                raise RuntimeError(f"LLM API error: {exc}")

    def _record_usage(self, response_data: Dict[str, Any]) -> None:
        """Record token usage to the shared tracker.

        Args:
            response_data: Full API response JSON.
        """
        try:
            from backend.token_tracker import get_token_tracker

            usage = response_data.get("usage", {})
            tracker = get_token_tracker()
            tracker.record_usage(
                model=self._model,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                endpoint="cerebro-summarize",
                success=True,
            )
        except ImportError:
            pass  # Token tracker not available outside backend context

    def _record_failure(self, error: str) -> None:
        """Record a failed API call to the shared tracker.

        Args:
            error: Error message string.
        """
        try:
            from backend.token_tracker import get_token_tracker

            tracker = get_token_tracker()
            tracker.record_usage(
                model=self._model,
                prompt_tokens=0,
                completion_tokens=0,
                endpoint="cerebro-summarize",
                success=False,
                error=error,
            )
        except ImportError:
            pass
