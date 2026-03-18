"""Tests for LLM verdict functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from backend.llm_verdict import (
    _apply_override_policy,
    _build_summary,
    _get_verdict_severity,
    generate_hybrid_verdict,
    run_verdict,
    verdict,
)

# ============================================================================
# Tests for Override Policy Functions
# ============================================================================


class TestVerdictSeverity:
    """Test verdict severity calculation."""

    def test_proceed_has_lowest_severity(self):
        assert _get_verdict_severity("PROCEED") == 1

    def test_proceed_with_caution_has_medium_severity(self):
        assert _get_verdict_severity("PROCEED WITH CAUTION") == 2

    def test_needs_work_has_high_severity(self):
        assert _get_verdict_severity("NEEDS WORK") == 3

    def test_abandon_has_highest_severity(self):
        assert _get_verdict_severity("ABANDON") == 4

    def test_fail_has_high_severity(self):
        assert _get_verdict_severity("FAIL") == 3

    def test_fragile_has_high_severity(self):
        assert _get_verdict_severity("FRAGILE") == 3

    def test_inconsistent_has_medium_severity(self):
        assert _get_verdict_severity("INCONSISTENT") == 2

    def test_consistent_has_low_severity(self):
        assert _get_verdict_severity("CONSISTENT") == 1

    def test_pass_has_low_severity(self):
        assert _get_verdict_severity("PASS") == 1

    def test_expensive_beta_has_medium_severity(self):
        assert _get_verdict_severity("EXPENSIVE BETA") == 2

    def test_mixed_has_medium_severity(self):
        assert _get_verdict_severity("MIXED") == 2

    def test_alpha_has_low_severity(self):
        assert _get_verdict_severity("ALPHA") == 1

    def test_robust_has_low_severity(self):
        assert _get_verdict_severity("ROBUST") == 1

    def test_unknown_verdict_defaults_to_medium(self):
        assert _get_verdict_severity("UNKNOWN") == 2

    def test_empty_string_defaults_to_medium(self):
        assert _get_verdict_severity("") == 2


class TestOverridePolicy:
    """Test override policy enforcement."""

    def test_llm_can_tighten_proceed_to_needs_work(self):
        result, overridden = _apply_override_policy(
            "PROCEED", "NEEDS_WORK", allow_loosening=False
        )
        assert result == "NEEDS_WORK"
        assert overridden is False

    def test_llm_can_tighten_to_proceed_with_caution(self):
        result, overridden = _apply_override_policy(
            "PROCEED", "PROCEED_WITH_CAUTION", allow_loosening=False
        )
        assert result == "PROCEED_WITH_CAUTION"
        assert overridden is False

    def test_llm_cannot_loosen_by_default(self):
        result, overridden = _apply_override_policy(
            "NEEDS_WORK", "PROCEED", allow_loosening=False
        )
        assert result == "NEEDS_WORK"
        assert overridden is True

    def test_llm_can_loosen_when_allowed(self):
        result, overridden = _apply_override_policy(
            "NEEDS_WORK", "PROCEED", allow_loosening=True
        )
        assert result == "PROCEED"
        assert overridden is False

    def test_same_verdict_no_override(self):
        result, overridden = _apply_override_policy(
            "PROCEED", "PROCEED", allow_loosening=False
        )
        assert result == "PROCEED"
        assert overridden is False

    def test_abandon_stays_abandon(self):
        # ABANDON (severity 4) vs NEEDS_WORK (severity 3)
        # LLM tries to loosen (4 -> 3), so it should be overridden
        result, overridden = _apply_override_policy(
            "ABANDON", "NEEDS_WORK", allow_loosening=False
        )
        assert result == "ABANDON"
        assert overridden is True  # LLM verdict was overridden


# ============================================================================
# Tests for Summary Building
# ============================================================================


class TestSummaryBuilding:
    """Test summary generation."""

    def test_build_summary_with_all_fields(self):
        result = {
            "rule_based": {
                "significance": {
                    "sharpe_ratio": 1.5,
                    "probabilistic_sharpe": 0.8,
                    "verdict": "PASS",
                },
                "walkforward": {
                    "win_rate": 0.6,
                    "n_windows": 5,
                    "verdict": "CONSISTENT",
                },
                "robustness": {"verdict": "ROBUST"},
                "beta": {"spy_correlation": 0.3, "verdict": "ALPHA"},
            },
            "llm": {"flags": ["flag1", "flag2"]},
        }
        summary = _build_summary(result)
        assert "Sharpe: 1.50" in summary
        assert "PSR: 80%" in summary
        assert "Walk-forward: 60% win rate" in summary

    def test_build_summary_with_missing_fields(self):
        result = {
            "rule_based": {},
            "llm": None,
        }
        summary = _build_summary(result)
        assert "Sharpe: 0.00" in summary
        assert "PSR: 0%" in summary


# ============================================================================
# Mock Report for Testing
# ============================================================================


def create_mock_report(
    sharpe=1.0,
    psr=0.7,
    deflated_sharpe=0.9,
    sig_verdict="PASS",
    win_rate=0.6,
    n_windows=5,
    wf_verdict="CONSISTENT",
    base_sharpe=1.0,
    costs_100_sharpe=0.5,
    slippage_25_sharpe=0.3,
    rob_verdict="ROBUST",
    spy_corr=0.3,
    qqq_corr=0.2,
    beta_verdict="ALPHA",
    n_iterations=10,
    landscape="FLAT",
    hypothesis_statement="Test hypothesis",
    who_loses="Test who",
    mechanism="Test mechanism",
):
    """Create a mock BacktestReport for testing."""
    mock_report = MagicMock()

    # Significance
    mock_significance = MagicMock()
    mock_significance.sharpe_ratio = sharpe
    mock_significance.probabilistic_sharpe = psr
    mock_significance.deflated_sharpe = deflated_sharpe
    mock_significance.verdict = sig_verdict

    # Walkforward
    mock_wf = MagicMock()
    mock_wf.win_rate = win_rate
    mock_wf.n_windows = n_windows
    mock_wf.mean_return = 0.1
    mock_wf.crisis_included = True
    mock_wf.verdict = wf_verdict

    # Robustness
    mock_rob = MagicMock()
    mock_rob.base_sharpe = base_sharpe
    mock_rob.costs_50_sharpe = 0.8
    mock_rob.costs_100_sharpe = costs_100_sharpe
    mock_rob.slippage_10_sharpe = 0.5
    mock_rob.slippage_25_sharpe = slippage_25_sharpe
    mock_rob.verdict = rob_verdict

    # Beta
    mock_beta = MagicMock()
    mock_beta.spy_correlation = spy_corr
    mock_beta.qqq_correlation = qqq_corr
    mock_beta.spy_verdict = beta_verdict

    # Hypothesis
    mock_hyp = MagicMock()
    mock_hyp.statement = hypothesis_statement
    mock_hyp.who_loses_money = who_loses
    mock_hyp.economic_mechanism = mechanism
    mock_hyp.noise_discrimination = "test noise"

    # Final verdict
    if wf_verdict == "INCONSISTENT" or rob_verdict == "FRAGILE":
        mock_report.final_verdict = "NEEDS WORK (walkforward, robustness)"
    elif beta_verdict == "EXPENSIVE BETA":
        mock_report.final_verdict = "PROCEED WITH CAUTION (beta heavy)"
    else:
        mock_report.final_verdict = "PROCEED"

    mock_report.significance = mock_significance
    mock_report.walkforward = mock_wf
    mock_report.robustness = mock_rob
    mock_report.beta = mock_beta
    mock_report.hypothesis = mock_hyp
    mock_report.n_iterations = n_iterations
    mock_report.optimization_landscape = landscape

    return mock_report


# ============================================================================
# Tests for Hybrid Verdict Generation
# ============================================================================


class TestGenerateHybridVerdict:
    """Test hybrid verdict generation."""

    @pytest.mark.asyncio
    async def test_generate_hybrid_verdict_rule_based_only(self):
        """Test with LLM disabled."""
        mock_report = create_mock_report()

        result = await generate_hybrid_verdict(
            report=mock_report,
            use_llm=False,
        )

        assert result["rule_based"]["significance"]["sharpe_ratio"] == 1.0
        assert result["llm"] is None
        assert "PROCEED" in result["final"]["verdict"]
        assert result["final"]["source"] == "rule_based"

    @pytest.mark.asyncio
    async def test_generate_hybrid_verdict_with_llm(self):
        """Test with LLM enabled (mocked)."""
        mock_report = create_mock_report()

        # Mock the LLM call
        with patch("backend.llm_verdict.llm_generate_verdict") as mock_llm:
            mock_llm_result = MagicMock()
            mock_llm_result.final_verdict = "PROCEED"
            mock_llm_result.reasoning = "Test reasoning"
            mock_llm_result.flags = []
            mock_llm_result.suggestions = []
            mock_llm_result.confidence = 0.8
            mock_llm.return_value = mock_llm_result

            result = await generate_hybrid_verdict(
                report=mock_report,
                use_llm=True,
            )

            assert result["llm"] is not None
            assert result["llm"]["final_verdict"] == "PROCEED"
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_override_policy_applied(self):
        """Test that override policy is applied correctly."""
        # Create a mock report that returns NEEDS WORK as final verdict
        mock_report = create_mock_report(
            wf_verdict="INCONSISTENT",  # This triggers NEEDS WORK
            rob_verdict="FRAGILE",  # This triggers NEEDS WORK
        )

        # LLM says PROCEED but should be overridden to NEEDS WORK
        with patch("backend.llm_verdict.llm_generate_verdict") as mock_llm:
            mock_llm_result = MagicMock()
            mock_llm_result.final_verdict = "PROCEED"  # Loosening
            mock_llm_result.reasoning = "Test"
            mock_llm_result.flags = []
            mock_llm_result.suggestions = []
            mock_llm_result.confidence = 0.8
            mock_llm.return_value = mock_llm_result

            result = await generate_hybrid_verdict(
                report=mock_report,
                use_llm=True,
                allow_loosening=False,
            )

            # Should keep NEEDS WORK (rule-based)
            assert "NEEDS" in result["final"]["verdict"]
            assert result["final"]["override_applied"] is True


# ============================================================================
# Tests for run_verdict and verdict functions
# ============================================================================


class TestRunVerdict:
    """Test the main run_verdict function."""

    @pytest.mark.asyncio
    async def test_run_verdict_with_numpy_arrays(self):
        """Test with numpy array inputs."""
        returns = np.random.randn(100) * 0.01
        benchmarks = {"SPY": np.random.randn(100) * 0.01}

        # Mock the LLM to avoid API call
        with patch("backend.llm_verdict.generate_hybrid_verdict") as mock_hybrid:
            mock_hybrid.return_value = {
                "rule_based": {
                    "significance": {
                        "sharpe_ratio": 1.0,
                        "probabilistic_sharpe": 0.7,
                        "deflated_sharpe": 0.8,
                        "verdict": "PASS",
                    },
                    "walkforward": {
                        "win_rate": 0.6,
                        "n_windows": 5,
                        "mean_return": 0.1,
                        "crisis_included": True,
                        "verdict": "CONSISTENT",
                    },
                    "robustness": {
                        "base_sharpe": 1.0,
                        "costs_50_sharpe": 0.8,
                        "costs_100_sharpe": 0.5,
                        "slippage_10_sharpe": 0.7,
                        "slippage_25_sharpe": 0.3,
                        "verdict": "ROBUST",
                    },
                    "beta": {
                        "spy_correlation": 0.3,
                        "qqq_correlation": 0.2,
                        "verdict": "ALPHA",
                    },
                    "optimization": {"n_iterations": 1, "landscape": "FLAT"},
                    "final_verdict": "PROCEED",
                },
                "llm": None,
                "final": {
                    "verdict": "PROCEED",
                    "source": "rule_based",
                    "override_applied": False,
                },
            }

            result = await run_verdict(
                returns=returns,
                benchmarks=benchmarks,
                hypothesis="Test hypothesis",
                use_llm=False,
                print_result=False,
            )

            assert result["verdict"] == "PROCEED"
            assert "summary" in result

    @pytest.mark.asyncio
    async def test_run_verdict_with_pandas_series(self):
        """Test with pandas Series inputs."""
        returns = pd.Series(np.random.randn(100) * 0.01)
        benchmarks = {"SPY": pd.Series(np.random.randn(100) * 0.01)}

        with patch("backend.llm_verdict.generate_hybrid_verdict") as mock_hybrid:
            mock_hybrid.return_value = {
                "rule_based": {
                    "significance": {
                        "sharpe_ratio": 1.0,
                        "probabilistic_sharpe": 0.7,
                        "deflated_sharpe": 0.8,
                        "verdict": "PASS",
                    },
                    "walkforward": {
                        "win_rate": 0.6,
                        "n_windows": 5,
                        "mean_return": 0.1,
                        "crisis_included": True,
                        "verdict": "CONSISTENT",
                    },
                    "robustness": {
                        "base_sharpe": 1.0,
                        "costs_50_sharpe": 0.8,
                        "costs_100_sharpe": 0.5,
                        "slippage_10_sharpe": 0.7,
                        "slippage_25_sharpe": 0.3,
                        "verdict": "ROBUST",
                    },
                    "beta": {
                        "spy_correlation": 0.3,
                        "qqq_correlation": 0.2,
                        "verdict": "ALPHA",
                    },
                    "optimization": {"n_iterations": 1, "landscape": "FLAT"},
                    "final_verdict": "PROCEED",
                },
                "llm": None,
                "final": {
                    "verdict": "PROCEED",
                    "source": "rule_based",
                    "override_applied": False,
                },
            }

            result = await run_verdict(
                returns=returns,
                benchmarks=benchmarks,
                hypothesis="Test hypothesis",
                use_llm=False,
                print_result=False,
            )

            assert result["verdict"] == "PROCEED"

    @pytest.mark.asyncio
    async def test_run_verdict_without_benchmarks(self):
        """Test without benchmark data."""
        returns = np.random.randn(100) * 0.01

        with patch("backend.llm_verdict.generate_hybrid_verdict") as mock_hybrid:
            mock_hybrid.return_value = {
                "rule_based": {
                    "significance": {
                        "sharpe_ratio": 1.0,
                        "probabilistic_sharpe": 0.7,
                        "deflated_sharpe": 0.8,
                        "verdict": "PASS",
                    },
                    "walkforward": {
                        "win_rate": 0.6,
                        "n_windows": 5,
                        "mean_return": 0.1,
                        "crisis_included": True,
                        "verdict": "CONSISTENT",
                    },
                    "robustness": {
                        "base_sharpe": 1.0,
                        "costs_50_sharpe": 0.8,
                        "costs_100_sharpe": 0.5,
                        "slippage_10_sharpe": 0.7,
                        "slippage_25_sharpe": 0.3,
                        "verdict": "ROBUST",
                    },
                    "beta": {
                        "spy_correlation": 0.0,
                        "qqq_correlation": 0.0,
                        "verdict": "MIXED",
                    },
                    "optimization": {"n_iterations": 1, "landscape": "FLAT"},
                    "final_verdict": "PROCEED",
                },
                "llm": None,
                "final": {
                    "verdict": "PROCEED",
                    "source": "rule_based",
                    "override_applied": False,
                },
            }

            result = await run_verdict(
                returns=returns,
                hypothesis="Test hypothesis",
                use_llm=False,
                print_result=False,
            )

            assert result["verdict"] == "PROCEED"


class TestVerdictSync:
    """Test the synchronous verdict wrapper."""

    def test_verdict_sync_wrapper(self):
        """Test that verdict() works as sync wrapper."""
        returns = np.random.randn(100) * 0.01

        with patch("backend.llm_verdict.run_verdict") as mock_run:
            mock_run.return_value = {
                "verdict": "PROCEED",
                "summary": "test",
                "details": {},
            }

            result = verdict(
                returns=returns,
                hypothesis="Test",
                use_llm=False,
                print_result=False,
            )

            assert result["verdict"] == "PROCEED"
            mock_run.assert_called_once()
