"""Tests for LLM client verdict functionality."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.llm_client import VerdictExplanation, VerdictLLMClient, generate_verdict


class TestVerdictExplanation:
    """Test VerdictExplanation model."""

    def test_verdict_explanation_creation(self):
        """Test creating a VerdictExplanation."""
        exp = VerdictExplanation(
            final_verdict="PROCEED",
            confidence=0.8,
            reasoning="Test reasoning",
            flags=["flag1"],
            suggestions=["suggestion1"],
        )
        assert exp.final_verdict == "PROCEED"
        assert exp.confidence == 0.8
        assert exp.reasoning == "Test reasoning"
        assert exp.flags == ["flag1"]
        assert exp.suggestions == ["suggestion1"]

    def test_verdict_explanation_defaults(self):
        """Test default values."""
        exp = VerdictExplanation(
            final_verdict="NEEDS_WORK",
            confidence=0.5,
            reasoning="",
            flags=[],
            suggestions=[],
        )
        assert exp.flags == []
        assert exp.suggestions == []


class TestVerdictLLMClient:
    """Test VerdictLLMClient class."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""
        with patch("backend.llm_client.QwenLLMClient.__init__") as mock_init:
            mock_init.return_value = None
            client = VerdictLLMClient.__new__(VerdictLLMClient)  # Bypass __init__
            client.api_key = "test_key"
            client.model = "qwen-turbo"
            client.base_url = "https://api.qwen.com/v1"
            client.max_tokens = 1000
            client.temperature = 0.3
            # Use object.__setattr__ to set the property
            object.__setattr__(client, "_config", MagicMock())
            client._config.is_configured = True
            return client

    @pytest.mark.asyncio
    async def test_generate_verdict_success(self, mock_llm_client):
        """Test successful verdict generation."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "final_verdict": "PROCEED",
                                "confidence": 0.85,
                                "reasoning": "Strategy shows strong Sharpe and passes all tests",
                                "flags": ["high_turnover"],
                                "suggestions": ["Consider reducing turnover"],
                            }
                        )
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
            },
        }

        with patch("backend.llm_client.httpx.AsyncClient") as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            with patch("backend.llm_client.get_token_tracker") as mock_tracker:
                mock_tracker_instance = MagicMock()
                mock_tracker.return_value = mock_tracker_instance

                result = await mock_llm_client.generate_verdict(
                    sharpe=1.5,
                    psr=0.8,
                    deflated_sharpe=1.2,
                    sig_verdict="PASS",
                    n_windows=10,
                    win_rate=0.7,
                    mean_return=0.15,
                    crisis_included=True,
                    wf_verdict="CONSISTENT",
                    base_sharpe=1.5,
                    costs_50_sharpe=1.2,
                    costs_100_sharpe=0.9,
                    slippage_10_sharpe=1.3,
                    slippage_25_sharpe=1.1,
                    rob_verdict="ROBUST",
                    spy_correlation=0.25,
                    qqq_correlation=0.30,
                    beta_verdict="ALPHA",
                    n_iterations=5,
                    landscape="FLAT",
                    turnover=0.6,
                )

                assert result.final_verdict == "PROCEED"
                assert result.confidence == 0.85
                assert "Sharpe" in result.reasoning

    @pytest.mark.asyncio
    async def test_generate_verdict_not_configured(self):
        """Test error when client not configured."""
        with patch("backend.llm_client.QwenLLMClient.__init__") as mock_init:
            mock_init.return_value = None
            client = VerdictLLMClient.__new__(VerdictLLMClient)
            object.__setattr__(client, "_config", MagicMock())
            client._config.is_configured = False

            with pytest.raises(ValueError, match="QWEN_API_KEY not configured"):
                await client.generate_verdict(
                    sharpe=1.0,
                    psr=0.5,
                    deflated_sharpe=0.8,
                    sig_verdict="PASS",
                    n_windows=5,
                    win_rate=0.6,
                    mean_return=0.1,
                    crisis_included=False,
                    wf_verdict="CONSISTENT",
                    base_sharpe=1.0,
                    costs_50_sharpe=0.8,
                    costs_100_sharpe=0.5,
                    slippage_10_sharpe=0.9,
                    slippage_25_sharpe=0.7,
                    rob_verdict="ROBUST",
                    spy_correlation=0.3,
                    qqq_correlation=0.2,
                    beta_verdict="ALPHA",
                    n_iterations=1,
                    landscape="FLAT",
                    turnover=0.5,
                )

    @pytest.mark.asyncio
    async def test_generate_verdict_http_error(self, mock_llm_client):
        """Test handling of HTTP errors."""
        with patch("backend.llm_client.httpx.AsyncClient") as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 401
            mock_response_obj.text = "Unauthorized"
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post.side_effect = Exception("HTTP 401")
            mock_client.return_value = mock_async_client

            with pytest.raises(RuntimeError, match="Qwen API error"):
                await mock_llm_client.generate_verdict(
                    sharpe=1.0,
                    psr=0.5,
                    deflated_sharpe=0.8,
                    sig_verdict="PASS",
                    n_windows=5,
                    win_rate=0.6,
                    mean_return=0.1,
                    crisis_included=False,
                    wf_verdict="CONSISTENT",
                    base_sharpe=1.0,
                    costs_50_sharpe=0.8,
                    costs_100_sharpe=0.5,
                    slippage_10_sharpe=0.9,
                    slippage_25_sharpe=0.7,
                    rob_verdict="ROBUST",
                    spy_correlation=0.3,
                    qqq_correlation=0.2,
                    beta_verdict="ALPHA",
                    n_iterations=1,
                    landscape="FLAT",
                    turnover=0.5,
                )

    @pytest.mark.asyncio
    async def test_generate_verdict_invalid_json(self, mock_llm_client):
        """Test handling of invalid JSON response."""
        mock_response = {
            "choices": [{"message": {"content": "not valid json"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        }

        with patch("backend.llm_client.httpx.AsyncClient") as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
            mock_async_client.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.post.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            with pytest.raises(RuntimeError, match="Invalid JSON"):
                await mock_llm_client.generate_verdict(
                    sharpe=1.0,
                    psr=0.5,
                    deflated_sharpe=0.8,
                    sig_verdict="PASS",
                    n_windows=5,
                    win_rate=0.6,
                    mean_return=0.1,
                    crisis_included=False,
                    wf_verdict="CONSISTENT",
                    base_sharpe=1.0,
                    costs_50_sharpe=0.8,
                    costs_100_sharpe=0.5,
                    slippage_10_sharpe=0.9,
                    slippage_25_sharpe=0.7,
                    rob_verdict="ROBUST",
                    spy_correlation=0.3,
                    qqq_correlation=0.2,
                    beta_verdict="ALPHA",
                    n_iterations=1,
                    landscape="FLAT",
                    turnover=0.5,
                )


class TestGenerateVerdictConvenience:
    """Test the convenience function."""

    @pytest.mark.asyncio
    async def test_generate_verdict_function(self):
        """Test the generate_verdict convenience function."""
        with patch("backend.llm_client.VerdictLLMClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.generate_verdict = AsyncMock(
                return_value=VerdictExplanation(
                    final_verdict="PROCEED_WITH_CAUTION",
                    confidence=0.7,
                    reasoning="Test",
                    flags=["beta"],
                    suggestions=["Reduce beta"],
                )
            )
            MockClient.return_value = mock_instance

            result = await generate_verdict(
                sharpe=1.2,
                psr=0.6,
                deflated_sharpe=1.0,
                sig_verdict="PASS",
                n_windows=8,
                win_rate=0.55,
                mean_return=0.08,
                crisis_included=True,
                wf_verdict="CONSISTENT",
                base_sharpe=1.2,
                costs_50_sharpe=1.0,
                costs_100_sharpe=0.7,
                slippage_10_sharpe=1.1,
                slippage_25_sharpe=0.9,
                rob_verdict="ROBUST",
                spy_correlation=0.5,
                qqq_correlation=0.6,
                beta_verdict="MIXED",
                n_iterations=10,
                landscape="PEAKED",
                turnover=0.7,
            )

            assert result.final_verdict == "PROCEED_WITH_CAUTION"
            mock_instance.generate_verdict.assert_called_once()


class TestPromptBuilding:
    """Test prompt building in VerdictLLMClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        with patch("backend.llm_client.QwenLLMClient.__init__") as mock_init:
            mock_init.return_value = None
            c = VerdictLLMClient.__new__(VerdictLLMClient)
            c.api_key = "test"
            c.model = "qwen-turbo"
            c.base_url = "https://api.qwen.com/v1"
            c.max_tokens = 1000
            c.temperature = 0.3
            return c

    def test_prompt_contains_all_metrics(self, client):
        """Verify the prompt contains all expected metric placeholders."""
        prompt = client.VERDICT_PROMPT

        # Check for key placeholders - some have format specifiers like {:.1%}
        assert "{sharpe}" in prompt
        assert "psr:.1%" in prompt
        assert "{deflated_sharpe}" in prompt
        assert "{sig_verdict}" in prompt
        assert "{n_windows}" in prompt
        assert "win_rate:.1%" in prompt
        assert "{crisis_included}" in prompt
        assert "{wf_verdict}" in prompt
        assert "{base_sharpe}" in prompt
        assert "{costs_50_sharpe}" in prompt
        assert "{costs_100_sharpe}" in prompt
        assert "{slippage_10_sharpe}" in prompt
        assert "{slippage_25_sharpe}" in prompt
        assert "{rob_verdict}" in prompt
        assert "spy_correlation:.1%" in prompt
        assert "qqq_correlation:.1%" in prompt
        assert "{beta_verdict}" in prompt
        assert "{n_iterations}" in prompt
        assert "{landscape}" in prompt
        assert "turnover:.1%" in prompt
        assert "{hypothesis}" in prompt
        assert "{who_loses_money}" in prompt
        assert "{economic_mechanism}" in prompt

    def test_prompt_output_format(self, client):
        """Verify the prompt specifies JSON output format."""
        assert '"final_verdict":' in client.VERDICT_PROMPT
        assert '"confidence":' in client.VERDICT_PROMPT
        assert '"reasoning":' in client.VERDICT_PROMPT
        assert '"flags":' in client.VERDICT_PROMPT
        assert '"suggestions":' in client.VERDICT_PROMPT
