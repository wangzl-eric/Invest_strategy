"""Quality scorer for research papers.

Scores 0-100 based on:
- Publication venue (20 points): Academic journal, working paper, blog post
- Out-of-sample testing (25 points): Did they test OOS?
- Transaction costs modeled (20 points): Are costs realistic?
- Sample size adequacy (15 points): Enough data for reliable conclusions?
- Statistical rigor (20 points): Proper methodology and reporting
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from cerebro.processing.structured_extractor import PaperSummary

logger = logging.getLogger(__name__)

# Publication venue quality tiers
VENUE_SCORES = {
    # Top-tier journals
    "journal of finance": 20.0,
    "journal of financial economics": 20.0,
    "review of financial studies": 20.0,
    "journal of portfolio management": 18.0,
    "financial analysts journal": 18.0,
    "quantitative finance": 17.0,
    "journal of empirical finance": 16.0,
    "journal of banking & finance": 15.0,
    # Working papers / preprints
    "arxiv": 12.0,
    "ssrn": 12.0,
    "nber": 14.0,
    # Industry research
    "aqr": 15.0,
    "man institute": 14.0,
    "two sigma": 14.0,
    "alpha architect": 13.0,
    "research affiliates": 14.0,
    # Blogs / community
    "quantocracy": 8.0,
    "reddit": 5.0,
    "kaggle": 10.0,
    "blog": 7.0,
}


@dataclass(frozen=True)
class QualityScore:
    """Immutable quality score breakdown.

    Attributes:
        total: Composite score 0-100.
        venue_score: Publication venue quality (0-20).
        oos_score: Out-of-sample testing (0-25).
        costs_score: Transaction cost modeling (0-20).
        sample_score: Sample size adequacy (0-15).
        rigor_score: Statistical rigor (0-20).
        details: Human-readable breakdown.
    """

    total: float
    venue_score: float
    oos_score: float
    costs_score: float
    sample_score: float
    rigor_score: float
    details: str


class QualityScorer:
    """Scores paper quality based on methodological rigor."""

    def score(self, summary: PaperSummary) -> QualityScore:
        """Score a paper summary for quality.

        Args:
            summary: Structured PaperSummary from extraction.

        Returns:
            QualityScore with breakdown.
        """
        venue = self._score_venue(summary)
        oos = self._score_oos(summary)
        costs = self._score_costs(summary)
        sample = self._score_sample_size(summary)
        rigor = self._score_rigor(summary)

        total = venue + oos + costs + sample + rigor

        details = (
            f"Venue: {venue:.0f}/20 | "
            f"OOS: {oos:.0f}/25 | "
            f"Costs: {costs:.0f}/20 | "
            f"Sample: {sample:.0f}/15 | "
            f"Rigor: {rigor:.0f}/20"
        )

        return QualityScore(
            total=round(total, 1),
            venue_score=round(venue, 1),
            oos_score=round(oos, 1),
            costs_score=round(costs, 1),
            sample_score=round(sample, 1),
            rigor_score=round(rigor, 1),
            details=details,
        )

    def _score_venue(self, summary: PaperSummary) -> float:
        """Score publication venue quality (0-20).

        Args:
            summary: Paper summary.

        Returns:
            Score 0-20.
        """
        source_lower = summary.source.lower()

        # Check direct source match
        for venue_key, score in VENUE_SCORES.items():
            if venue_key in source_lower:
                return score

        # Check title/methodology for venue mentions
        combined = f"{summary.title} {summary.one_line}".lower()
        for venue_key, score in VENUE_SCORES.items():
            if venue_key in combined:
                return min(score, 15.0)  # Mentioned but not confirmed

        return 8.0  # Unknown venue, moderate default

    def _score_oos(self, summary: PaperSummary) -> float:
        """Score out-of-sample testing (0-25).

        Papers with proper OOS testing are significantly more reliable.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-25.
        """
        if summary.out_of_sample:
            # Check for additional OOS quality indicators
            methodology_lower = summary.methodology.lower()

            # Walk-forward or expanding window = best practice
            if any(
                term in methodology_lower
                for term in [
                    "walk-forward",
                    "expanding window",
                    "rolling",
                    "walk forward",
                    "time-series cv",
                ]
            ):
                return 25.0

            # Simple train/test split
            if any(
                term in methodology_lower
                for term in ["train/test", "holdout", "validation set"]
            ):
                return 20.0

            # Generic OOS
            return 18.0

        # No OOS testing
        methodology_lower = summary.methodology.lower()
        if "in-sample" in methodology_lower or "full sample" in methodology_lower:
            return 3.0  # Explicitly in-sample only

        return 5.0  # Unknown, assume no OOS

    def _score_costs(self, summary: PaperSummary) -> float:
        """Score transaction cost modeling (0-20).

        Papers that model realistic transaction costs are more credible.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-20.
        """
        if summary.transaction_costs_modeled:
            # Check sophistication of cost modeling
            combined = f"{summary.methodology} {summary.limitations}".lower()

            # Market impact / Almgren-Chriss = best
            if any(
                term in combined
                for term in [
                    "market impact",
                    "almgren",
                    "price impact",
                    "execution cost",
                ]
            ):
                return 20.0

            # Proportional costs
            if any(
                term in combined
                for term in ["basis points", "bps", "commission", "proportional"]
            ):
                return 16.0

            # Generic cost mention
            return 14.0

        # No cost modeling
        return 3.0

    def _score_sample_size(self, summary: PaperSummary) -> float:
        """Score sample size adequacy (0-15).

        Larger and longer datasets provide more reliable conclusions.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-15.
        """
        score = 5.0  # Default for unknown

        # Parse backtest period for length
        if summary.backtest_period:
            years = self._estimate_period_years(summary.backtest_period)
            if years is not None:
                if years >= 20:
                    score = 15.0
                elif years >= 10:
                    score = 12.0
                elif years >= 5:
                    score = 8.0
                elif years >= 3:
                    score = 5.0
                else:
                    score = 3.0

        # Parse sample size for cross-sectional breadth
        if summary.sample_size:
            n = self._parse_sample_size(summary.sample_size)
            if n is not None:
                if n >= 1000:
                    score = min(15.0, score + 3.0)
                elif n >= 100:
                    score = min(15.0, score + 1.0)

        return score

    def _score_rigor(self, summary: PaperSummary) -> float:
        """Score statistical rigor (0-20).

        Based on methodology description and key findings.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-20.
        """
        score = 5.0
        combined = (
            f"{summary.methodology} {' '.join(summary.key_findings)} "
            f"{summary.novelty_claim}"
        ).lower()

        # Statistical testing indicators
        rigor_terms = {
            "t-statistic": 3.0,
            "p-value": 3.0,
            "confidence interval": 3.0,
            "bootstrap": 3.0,
            "sharpe ratio": 2.0,
            "information ratio": 2.0,
            "maximum drawdown": 2.0,
            "calmar": 1.0,
            "sortino": 1.0,
            "regression": 2.0,
            "fama-macbeth": 3.0,
            "newey-west": 3.0,
            "heteroskedasticity": 2.0,
            "autocorrelation": 2.0,
            "stationarity": 2.0,
            "cointegration": 2.0,
            "cross-validation": 3.0,
            "multiple testing": 3.0,
            "bonferroni": 3.0,
            "false discovery": 3.0,
        }

        for term, bonus in rigor_terms.items():
            if term in combined:
                score += bonus

        # Check for acknowledged limitations (sign of honest reporting)
        if summary.limitations and len(summary.limitations) >= 2:
            score += 2.0

        return min(20.0, score)

    @staticmethod
    def _estimate_period_years(period_str: str) -> Optional[float]:
        """Estimate the number of years in a backtest period string.

        Args:
            period_str: Period string like "2000-2023" or "Jan 2010 - Dec 2022".

        Returns:
            Estimated number of years, or None if unparsable.
        """
        # Match patterns like "2000-2023", "2000 - 2023", "2000 to 2023"
        match = re.search(r"(\d{4})\s*[-–—to]+\s*(\d{4})", period_str)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            if 1900 <= start_year <= 2030 and start_year < end_year:
                return float(end_year - start_year)

        # Match "N years" pattern
        match = re.search(r"(\d+)\s*years?", period_str, re.IGNORECASE)
        if match:
            return float(match.group(1))

        return None

    @staticmethod
    def _parse_sample_size(sample_str: str) -> Optional[int]:
        """Parse a sample size description to a number.

        Args:
            sample_str: Sample size string like "500 stocks" or "1,234".

        Returns:
            Parsed integer, or None if unparsable.
        """
        # Remove commas and extract first number
        cleaned = sample_str.replace(",", "")
        match = re.search(r"(\d+)", cleaned)
        if match:
            return int(match.group(1))
        return None
