"""LLM Verdict Module - Hybrid rule-based + LLM verdict for backtest rigor.

This module provides:
- Integration of rule-based BacktestReport with LLM verdict
- Convenience functions for generating hybrid verdicts
- Override policy enforcement (LLM can tighten, not loosen)
"""

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from backend.llm_client import VerdictExplanation
from backend.llm_client import generate_verdict as llm_generate_verdict

logger = logging.getLogger(__name__)


# ============================================================================
# Verdict Override Policy
# ============================================================================

# Map rule-based verdicts to severity levels for override policy
VERDICT_SEVERITY = {
    "ABANDON": 4,
    "NEEDS WORK": 3,
    "PROCEED WITH CAUTION": 2,
    "PROCEED": 1,
    "FAIL": 3,  # Treat FAIL like NEEDS WORK
    "FRAGILE": 3,
    "INCONSISTENT": 2,
    "CONSISTENT": 1,
    "PASS": 1,
    "EXPENSIVE BETA": 2,
    "MIXED": 2,
    "ALPHA": 1,
    "ROBUST": 1,
}


def _extract_final_verdict_severity(report: Any) -> int:
    """Extract severity from final verdict string."""
    verdict = report.final_verdict.upper()

    if "ABANDON" in verdict:
        return VERDICT_SEVERITY["ABANDON"]
    elif "NEEDS WORK" in verdict:
        return VERDICT_SEVERITY["NEEDS WORK"]
    elif "PROCEED WITH CAUTION" in verdict:
        return VERDICT_SEVERITY["PROCEED WITH CAUTION"]
    elif "PROCEED" in verdict:
        return VERDICT_SEVERITY["PROCEED"]

    return 2  # Default to middle severity


def _apply_override_policy(
    rule_based_verdict: str,
    llm_verdict: str,
    allow_loosening: bool = False,
) -> tuple[str, bool]:
    """Apply override policy to LLM verdict.

    By default, LLM can only tighten the verdict (make it more conservative).
    This prevents the LLM from incorrectly upgrading a FAIL to a PASS.

    Args:
        rule_based_verdict: The rule-based final verdict
        llm_verdict: The LLM's verdict
        allow_loosening: If True, allow LLM to loosen verdict (not recommended)

    Returns:
        Tuple of (final_verdict, was_overridden)
    """
    rule_severity = _get_verdict_severity(rule_based_verdict)
    llm_severity = _get_verdict_severity(llm_verdict)

    if llm_severity < rule_severity and not allow_loosening:
        # LLM tried to loosen - keep rule-based verdict
        logger.info(
            f"LLM verdict ({llm_verdict}) was overridden to preserve rule-based ({rule_based_verdict})"
        )
        return rule_based_verdict, True

    return llm_verdict, False


def _get_verdict_severity(verdict: str) -> int:
    """Get severity level for a verdict."""
    v = verdict.upper()

    for key, severity in VERDICT_SEVERITY.items():
        if key in v:
            return severity

    return 2  # Default


def _verdict_to_string(verdict: str) -> str:
    """Normalize verdict to standard string."""
    v = verdict.upper()

    if "ABANDON" in v:
        return "ABANDON"
    elif "NEEDS WORK" in v:
        return "NEEDS_WORK"
    elif "PROCEED WITH CAUTION" in v:
        return "PROCEED_WITH_CAUTION"
    elif "PROCEED" in v:
        return "PROCEED"

    return "NEEDS_WORK"  # Default to conservative


# ============================================================================
# Hybrid Verdict Generator
# ============================================================================


async def generate_hybrid_verdict(
    report: Any,
    use_llm: bool = True,
    allow_loosening: bool = False,
) -> Dict[str, Any]:
    """Generate hybrid verdict combining rule-based and LLM analysis.

    Args:
        report: BacktestReport from BacktestResearcher.run_full_analysis()
        use_llm: Whether to call LLM for additional judgment
        allow_loosening: If True, allow LLM to loosen verdict (not recommended)

    Returns:
        Dict with:
        - rule_based: Original rule-based verdict and metrics
        - llm: LLM verdict (if use_llm=True)
        - final: The final verdict after applying override policy
    """
    # Extract rule-based verdict
    rule_based = {
        "final_verdict": report.final_verdict,
        "significance": {
            "sharpe_ratio": report.significance.sharpe_ratio,
            "probabilistic_sharpe": report.significance.probabilistic_sharpe,
            "deflated_sharpe": report.significance.deflated_sharpe,
            "verdict": report.significance.verdict,
        },
        "walkforward": {
            "n_windows": report.walkforward.n_windows,
            "win_rate": report.walkforward.win_rate,
            "mean_return": report.walkforward.mean_return,
            "crisis_included": report.walkforward.crisis_included,
            "verdict": report.walkforward.verdict,
        },
        "robustness": {
            "base_sharpe": report.robustness.base_sharpe,
            "costs_50_sharpe": report.robustness.costs_50_sharpe,
            "costs_100_sharpe": report.robustness.costs_100_sharpe,
            "slippage_10_sharpe": report.robustness.slippage_10_sharpe,
            "slippage_25_sharpe": report.robustness.slippage_25_sharpe,
            "verdict": report.robustness.verdict,
        },
        "beta": {
            "spy_correlation": report.beta.spy_correlation,
            "qqq_correlation": report.beta.qqq_correlation,
            "verdict": report.beta.spy_verdict,
        },
        "optimization": {
            "n_iterations": report.n_iterations,
            "landscape": report.optimization_landscape,
        },
    }

    result = {
        "rule_based": rule_based,
        "llm": None,
        "final": {
            "verdict": report.final_verdict,
            "source": "rule_based",
            "override_applied": False,
        },
    }

    # Call LLM if requested
    if use_llm:
        try:
            llm_result = await llm_generate_verdict(
                sharpe=report.significance.sharpe_ratio,
                psr=report.significance.probabilistic_sharpe,
                deflated_sharpe=report.significance.deflated_sharpe,
                sig_verdict=report.significance.verdict,
                n_windows=report.walkforward.n_windows,
                win_rate=report.walkforward.win_rate,
                mean_return=report.walkforward.mean_return,
                crisis_included=report.walkforward.crisis_included,
                wf_verdict=report.walkforward.verdict,
                base_sharpe=report.robustness.base_sharpe,
                costs_50_sharpe=report.robustness.costs_50_sharpe,
                costs_100_sharpe=report.robustness.costs_100_sharpe,
                slippage_10_sharpe=report.robustness.slippage_10_sharpe,
                slippage_25_sharpe=report.robustness.slippage_25_sharpe,
                rob_verdict=report.robustness.verdict,
                spy_correlation=report.beta.spy_correlation,
                qqq_correlation=report.beta.qqq_correlation,
                beta_verdict=report.beta.spy_verdict,
                n_iterations=report.n_iterations,
                landscape=report.optimization_landscape,
                turnover=0.5,  # Default - could be passed in
                hypothesis=report.hypothesis.statement,
                who_loses_money=report.hypothesis.who_loses_money,
                economic_mechanism=report.hypothesis.economic_mechanism,
                noise_discrimination=report.hypothesis.noise_discrimination,
            )

            # Apply override policy
            final_verdict, was_overridden = _apply_override_policy(
                report.final_verdict,
                llm_result.final_verdict,
                allow_loosening=allow_loosening,
            )

            result["llm"] = {
                "enabled": True,
                "final_verdict": llm_result.final_verdict,
                "reasoning": llm_result.reasoning,
                "flags": llm_result.flags,
                "suggestions": llm_result.suggestions,
                "confidence": llm_result.confidence,
            }

            result["final"] = {
                "verdict": final_verdict,
                "source": "llm" if not was_overridden else "rule_based",
                "override_applied": was_overridden,
                "reasoning": llm_result.reasoning,
                "flags": llm_result.flags,
                "suggestions": llm_result.suggestions,
            }

        except Exception as e:
            logger.error(f"LLM verdict failed: {e}")
            result["llm"] = {
                "enabled": True,
                "error": str(e),
            }
            # Fall back to rule-based

    return result


# ============================================================================
# Easy-to-Use Jupyter Interface
# ============================================================================


async def run_verdict(
    returns: Union[List[float], np.ndarray, pd.Series],
    benchmarks: Optional[Dict[str, Union[List[float], np.ndarray, pd.Series]]] = None,
    hypothesis: Optional[str] = None,
    who_loses_money: Optional[str] = None,
    economic_mechanism: Optional[str] = None,
    noise_discrimination: Optional[str] = None,
    n_iterations: int = 1,
    avg_turnover: float = 0.5,
    use_llm: bool = True,
    allow_loosening: bool = False,
    print_result: bool = True,
) -> Dict[str, Any]:
    """Easy-to-use verdict function for Jupyter notebooks.

    This is the main function you'll call from Jupyter. It runs the full
    backtest rigor analysis and returns a verdict with explanations.

    Args:
        returns: Daily returns as list, numpy array, or pandas Series
        benchmarks: Optional dict of benchmark returns, e.g. {'SPY': [...]}
        hypothesis: Your strategy hypothesis (what are you trying to capture?)
        who_loses_money: Who loses money when your trade works?
        economic_mechanism: What's the economic mechanism behind the edge?
        noise_discrimination: How does your strategy separate signal from noise?
        n_iterations: Number of parameter optimizations tried (for deflated Sharpe)
        avg_turnover: Average portfolio turnover (0.0 to 1.0)
        use_llm: Whether to get LLM verdict (default: True)
        allow_loosening: Allow LLM to loosen verdict? (default: False, recommended)
        print_result: Print a nice summary? (default: True)

    Returns:
        Dict with:
        - verdict: Final verdict string (PROCEED, PROCEED_WITH_CAUTION, NEEDS_WORK, ABANDON)
        - summary: Short summary of the result
        - details: Full details including rule_based and llm analysis

    Example:
        >>> returns = [...]  # your daily returns
        >>> result = await run_verdict(
        ...     returns,
        ...     benchmarks={'SPY': spy_returns},
        ...     hypothesis='Momentum continues after earnings',
        ...     who_loses_money='Slow traders',
        ...     economic_mechanism='Information diffusion'
        ... )
        >>> print(result['verdict'])
    """
    # Import from skill
    import sys
    from pathlib import Path

    skill_path = (
        Path(__file__).parent.parent / ".cursor" / "skills" / "quant-backtest-research"
    )
    if str(skill_path) not in sys.path:
        sys.path.insert(0, str(skill_path))
    from researcher import BacktestResearcher

    # Convert returns to pandas Series
    if isinstance(returns, (list, np.ndarray)):
        returns_series = pd.Series(returns)
    else:
        returns_series = returns

    # Convert benchmarks
    benchmark_series = {}
    if benchmarks:
        for ticker, rets in benchmarks.items():
            if isinstance(rets, (list, np.ndarray)):
                benchmark_series[ticker] = pd.Series(rets)
            else:
                benchmark_series[ticker] = rets

    # Build hypothesis dict if provided
    hypothesis_dict = {}
    if hypothesis:
        hypothesis_dict["statement"] = hypothesis
    if who_loses_money:
        hypothesis_dict["who_loses_money"] = who_loses_money
    if economic_mechanism:
        hypothesis_dict["economic_mechanism"] = economic_mechanism
    if noise_discrimination:
        hypothesis_dict["noise_discrimination"] = noise_discrimination

    # Run full analysis
    researcher = BacktestResearcher(
        returns=returns_series,
        benchmark_returns=benchmark_series,
        hypothesis=hypothesis_dict.get("statement", ""),
        who_loses_money=hypothesis_dict.get("who_loses_money", ""),
        economic_mechanism=hypothesis_dict.get("economic_mechanism", ""),
        noise_discrimination=hypothesis_dict.get("noise_discrimination", ""),
        n_optimization_iterations=n_iterations,
        avg_turnover=avg_turnover,
    )

    report = researcher.run_full_analysis()

    # Generate hybrid verdict
    result = await generate_hybrid_verdict(
        report=report,
        use_llm=use_llm,
        allow_loosening=allow_loosening,
    )

    # Build user-friendly output
    output = {
        "verdict": result["final"]["verdict"],
        "summary": _build_summary(result),
        "details": result,
    }

    if print_result:
        _print_result(output)

    return output


def _build_summary(result: Dict[str, Any]) -> str:
    """Build a short summary string."""
    parts = []

    # Rule-based summary
    rb = result.get("rule_based", {})
    sig = rb.get("significance", {})
    wf = rb.get("walkforward", {})
    rob = rb.get("robustness", {})
    beta = rb.get("beta", {})

    parts.append(f"Sharpe: {sig.get('sharpe_ratio', 0):.2f}")
    parts.append(f"PSR: {sig.get('probabilistic_sharpe', 0):.0%}")
    parts.append(f"Walk-forward: {wf.get('win_rate', 0):.0%} win rate")
    parts.append(f"Robustness: {rob.get('verdict', 'N/A')}")
    parts.append(f"Beta: {beta.get('verdict', 'N/A')}")

    # LLM summary if available
    if result.get("llm") and result["llm"].get("flags"):
        parts.append(f"\nLLM Flags: {', '.join(result['llm']['flags'][:2])}")

    return " | ".join(parts)


def _print_result(result: Dict[str, Any]) -> None:
    """Print a nice formatted result."""
    verdict = result["verdict"]
    details = result["details"]

    # Color codes for terminal
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    # Pick color based on verdict
    if "PROCEED" in verdict and "CAUTION" not in verdict:
        color = GREEN
    elif "PROCEED WITH CAUTION" in verdict:
        color = YELLOW
    else:
        color = RED

    print("\n" + "=" * 60)
    print(f"{color}  VERDICT: {verdict}{RESET}")
    print("=" * 60)
    print()

    # Rule-based summary
    rb = details.get("rule_based", {})
    print("📊 RULE-BASED ANALYSIS")
    print("-" * 40)

    sig = rb.get("significance", {})
    print(f"  Sharpe:           {sig.get('sharpe_ratio', 0):.2f}")
    print(f"  Probabilistic:    {sig.get('probabilistic_sharpe', 0):.1%}")
    print(f"  Deflated:         {sig.get('deflated_sharpe', 0):.2f}")
    print(f"  Significance:     {sig.get('verdict', 'N/A')}")
    print()

    wf = rb.get("walkforward", {})
    print(
        f"  Walk-forward:     {wf.get('win_rate', 0):.1%} win rate ({wf.get('n_windows', 0)} windows)"
    )
    print(f"  Walk-forward:    {wf.get('verdict', 'N/A')}")
    print()

    rob = rb.get("robustness", {})
    print(f"  Costs +100%:      Sharpe {rob.get('costs_100_sharpe', 0):.2f}")
    print(f"  Slippage 25bps:   Sharpe {rob.get('slippage_25_sharpe', 0):.2f}")
    print(f"  Robustness:       {rob.get('verdict', 'N/A')}")
    print()

    beta = rb.get("beta", {})
    print(f"  SPY Correlation: {beta.get('spy_correlation', 0):.1%}")
    print(f"  Beta Type:       {beta.get('verdict', 'N/A')}")
    print()

    # LLM verdict if available
    llm = details.get("llm")
    if llm and not llm.get("error"):
        print("🧠 LLM VERDICT")
        print("-" * 40)
        print(f"  Verdict:    {llm.get('final_verdict', 'N/A')}")
        print(f"  Confidence: {llm.get('confidence', 0):.0%}")
        print()

        if llm.get("reasoning"):
            print(f"  Reasoning:")
            print(f"    {llm['reasoning'][:200]}...")
            print()

        if llm.get("flags"):
            print(f"  Flags:")
            for flag in llm["flags"]:
                print(f"    • {flag}")
            print()

        if llm.get("suggestions"):
            print(f"  Suggestions:")
            for suggestion in llm["suggestions"]:
                print(f"    → {suggestion}")
            print()

        if details.get("final", {}).get("override_applied"):
            print(f"  ⚠️  LLM verdict overridden (kept rule-based)")
            print()

    print("=" * 60)


# ============================================================================
# Sync Wrapper for Easy Use
# ============================================================================


def verdict(
    returns: Union[List[float], np.ndarray, pd.Series],
    benchmarks: Optional[Dict[str, Union[List[float], np.ndarray, pd.Series]]] = None,
    hypothesis: Optional[str] = None,
    who_loses_money: Optional[str] = None,
    economic_mechanism: Optional[str] = None,
    noise_discrimination: Optional[str] = None,
    n_iterations: int = 1,
    avg_turnover: float = 0.5,
    use_llm: bool = True,
    allow_loosening: bool = False,
    print_result: bool = True,
) -> Dict[str, Any]:
    """Synchronous wrapper for run_verdict.

    Use this in Jupyter notebooks for simplest interface:

    >>> result = verdict(returns, hypothesis="...")
    >>> print(result['verdict'])

    Args:
        Same as run_verdict()

    Returns:
        Same as run_verdict()
    """
    import asyncio

    import nest_asyncio

    # Allow nested event loops (needed for Jupyter)
    nest_asyncio.apply()

    return asyncio.run(
        run_verdict(
            returns=returns,
            benchmarks=benchmarks,
            hypothesis=hypothesis,
            who_loses_money=who_loses_money,
            economic_mechanism=economic_mechanism,
            noise_discrimination=noise_discrimination,
            n_iterations=n_iterations,
            avg_turnover=avg_turnover,
            use_llm=use_llm,
            allow_loosening=allow_loosening,
            print_result=print_result,
        )
    )


__all__ = [
    "run_verdict",
    "verdict",
    "generate_hybrid_verdict",
    "generate_verdict_from_metrics",
    "VerdictExplanation",
]


# Backwards compatibility alias
generate_verdict_from_metrics = run_verdict
