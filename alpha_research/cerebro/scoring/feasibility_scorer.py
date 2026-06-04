"""Feasibility scorer for research papers.

Assesses whether a paper's strategy can be implemented with our current
data sources, infrastructure, and capital constraints. Returns a binary
feasibility assessment with detailed reasons.
"""

import logging
from dataclasses import dataclass
from typing import FrozenSet, List, Tuple

from cerebro.config import cerebro_config
from cerebro.processing.structured_extractor import PaperSummary

logger = logging.getLogger(__name__)

# Infrastructure capabilities
SUPPORTED_ASSET_CLASSES: FrozenSet[str] = frozenset(
    {
        "Equities",
        "FX",
        "Crypto",
    }
)

PARTIALLY_SUPPORTED_CLASSES: FrozenSet[str] = frozenset(
    {
        "Commodities",
        "Rates",
        "Multi-Asset",
    }
)

# Strategies we cannot implement
INFEASIBLE_KEYWORDS: FrozenSet[str] = frozenset(
    {
        "high frequency",
        "hft",
        "market making",
        "co-location",
        "latency arbitrage",
        "tick-by-tick",
        "options writing",
        "selling volatility",
        "private equity",
        "venture capital",
        "real estate",
        "reits",
        "otc derivatives",
        "credit default swap",
        "corporate bond",
        "municipal bond",
    }
)

# Data we cannot access
UNAVAILABLE_DATA: FrozenSet[str] = frozenset(
    {
        "proprietary",
        "bloomberg terminal",
        "refinitiv",
        "capital iq",
        "compustat",
        "crsp",
        "institutional ownership 13f",
        "satellite imagery",
        "credit card data",
        "social media firehose",
    }
)


@dataclass(frozen=True)
class FeasibilityResult:
    """Immutable feasibility assessment result.

    Attributes:
        is_feasible: Whether the strategy can be implemented.
        confidence: Confidence in the assessment (0-1).
        blockers: Tuple of reasons why it is NOT feasible.
        enablers: Tuple of reasons why it IS feasible.
        missing_data: Tuple of data sources we would need but don't have.
        estimated_effort: Rough implementation effort (days).
    """

    is_feasible: bool
    confidence: float
    blockers: Tuple[str, ...]
    enablers: Tuple[str, ...]
    missing_data: Tuple[str, ...]
    estimated_effort: int


class FeasibilityScorer:
    """Assesses whether a paper's strategy is implementable."""

    def __init__(self) -> None:
        self._available_sources = set(
            s.lower() for s in cerebro_config.scoring.available_data_sources
        )

    def assess(self, summary: PaperSummary) -> FeasibilityResult:
        """Assess feasibility of implementing a paper's strategy.

        Args:
            summary: Structured PaperSummary from extraction.

        Returns:
            FeasibilityResult with blockers and enablers.
        """
        blockers: List[str] = []
        enablers: List[str] = []
        missing_data: List[str] = []

        # Check asset class support
        self._check_asset_class(summary, blockers, enablers)

        # Check for infeasible strategy types
        self._check_infeasible_keywords(summary, blockers)

        # Check data requirements
        self._check_data_requirements(summary, blockers, enablers, missing_data)

        # Check implementation complexity
        self._check_complexity(summary, blockers, enablers)

        # Determine feasibility
        is_feasible = len(blockers) == 0
        confidence = self._compute_confidence(blockers, enablers, summary)
        effort = self._estimate_effort(summary, missing_data)

        return FeasibilityResult(
            is_feasible=is_feasible,
            confidence=round(confidence, 2),
            blockers=tuple(blockers),
            enablers=tuple(enablers),
            missing_data=tuple(missing_data),
            estimated_effort=effort,
        )

    def _check_asset_class(
        self,
        summary: PaperSummary,
        blockers: List[str],
        enablers: List[str],
    ) -> None:
        """Check if asset classes are supported.

        Args:
            summary: Paper summary.
            blockers: List to append blockers to.
            enablers: List to append enablers to.
        """
        if not summary.asset_class:
            enablers.append("No specific asset class required")
            return

        paper_classes = set(summary.asset_class)
        supported = paper_classes & SUPPORTED_ASSET_CLASSES
        partial = paper_classes & PARTIALLY_SUPPORTED_CLASSES
        unsupported = (
            paper_classes - SUPPORTED_ASSET_CLASSES - PARTIALLY_SUPPORTED_CLASSES
        )

        if supported:
            enablers.append(f"Fully supported asset classes: {', '.join(supported)}")

        if partial:
            enablers.append(f"Partially supported: {', '.join(partial)}")

        if unsupported and not supported and not partial:
            blockers.append(f"Unsupported asset classes: {', '.join(unsupported)}")

    def _check_infeasible_keywords(
        self,
        summary: PaperSummary,
        blockers: List[str],
    ) -> None:
        """Check for keywords indicating infeasible strategies.

        Args:
            summary: Paper summary.
            blockers: List to append blockers to.
        """
        combined = (
            f"{summary.methodology} {summary.signal_description} " f"{summary.one_line}"
        ).lower()

        for keyword in INFEASIBLE_KEYWORDS:
            if keyword in combined:
                blockers.append(
                    f"Strategy requires '{keyword}' which is not in our infrastructure"
                )
                return  # One blocker is enough

    def _check_data_requirements(
        self,
        summary: PaperSummary,
        blockers: List[str],
        enablers: List[str],
        missing_data: List[str],
    ) -> None:
        """Check if required data sources are available.

        Args:
            summary: Paper summary.
            blockers: List to append blockers to.
            enablers: List to append enablers to.
            missing_data: List to append missing data to.
        """
        if not summary.data_requirements:
            enablers.append("No specific data requirements identified")
            return

        for req in summary.data_requirements:
            req_lower = req.lower()

            # Check for unavailable data
            for unavail in UNAVAILABLE_DATA:
                if unavail in req_lower:
                    blockers.append(f"Requires unavailable data: {req}")
                    missing_data.append(req)
                    break
            else:
                # Check if any of our sources can provide it
                if any(src in req_lower for src in self._available_sources):
                    enablers.append(f"Data available: {req}")
                elif self._is_common_market_data(req_lower):
                    enablers.append(f"Standard market data: {req}")
                else:
                    missing_data.append(req)

        # Missing data is a blocker only if critical mass is missing
        if missing_data and len(missing_data) > len(summary.data_requirements) / 2:
            blockers.append(
                f"Majority of data requirements unavailable: "
                f"{', '.join(missing_data)}"
            )

    def _check_complexity(
        self,
        summary: PaperSummary,
        blockers: List[str],
        enablers: List[str],
    ) -> None:
        """Check implementation complexity constraints.

        Args:
            summary: Paper summary.
            blockers: List to append blockers to.
            enablers: List to append enablers to.
        """
        if summary.implementation_complexity == "LOW":
            enablers.append("Low implementation complexity")
        elif summary.implementation_complexity == "MEDIUM":
            enablers.append("Moderate implementation complexity")
        elif summary.implementation_complexity == "HIGH":
            # HIGH is not a blocker, just a concern
            enablers.append("High complexity - requires significant effort")

    def _compute_confidence(
        self,
        blockers: List[str],
        enablers: List[str],
        summary: PaperSummary,
    ) -> float:
        """Compute confidence in the feasibility assessment.

        Args:
            blockers: List of blocking reasons.
            enablers: List of enabling reasons.
            summary: Paper summary.

        Returns:
            Confidence score 0-1.
        """
        # More information = higher confidence
        info_score = 0.0

        if summary.asset_class:
            info_score += 0.2
        if summary.data_requirements:
            info_score += 0.2
        if summary.implementation_complexity != "MEDIUM":  # Non-default
            info_score += 0.1
        if summary.methodology != "Not extracted":
            info_score += 0.2
        if summary.signal_description != "No explicit signal":
            info_score += 0.2

        # Clear verdict = higher confidence
        total_reasons = len(blockers) + len(enablers)
        if total_reasons > 0:
            info_score += 0.1

        return min(1.0, info_score)

    def _estimate_effort(
        self,
        summary: PaperSummary,
        missing_data: List[str],
    ) -> int:
        """Estimate implementation effort in person-days.

        Args:
            summary: Paper summary.
            missing_data: List of missing data sources.

        Returns:
            Estimated effort in days.
        """
        base_effort = {
            "LOW": 3,
            "MEDIUM": 7,
            "HIGH": 15,
        }

        effort = base_effort.get(summary.implementation_complexity, 7)

        # Add time for data acquisition
        effort += len(missing_data) * 2

        # OOS already tested = less validation needed
        if summary.out_of_sample:
            effort = max(1, effort - 2)

        return effort

    @staticmethod
    def _is_common_market_data(req: str) -> bool:
        """Check if a data requirement is standard market data.

        Args:
            req: Lowercase data requirement string.

        Returns:
            True if this is commonly available market data.
        """
        common_terms = {
            "price",
            "return",
            "volume",
            "ohlc",
            "close",
            "market cap",
            "index",
            "benchmark",
            "s&p",
            "exchange rate",
            "interest rate",
            "yield curve",
        }
        return any(term in req for term in common_terms)
