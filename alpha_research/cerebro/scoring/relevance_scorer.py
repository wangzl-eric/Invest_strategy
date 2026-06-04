"""Relevance scorer for research papers.

Scores 0-100 based on:
- Asset class match (30 points): Does the paper cover our asset classes?
- Signal complementarity (25 points): Does it complement our existing signals?
- Data availability (25 points): Can we replicate with our data sources?
- Infrastructure fit (20 points): Does it fit our backtesting/execution stack?
"""

import logging
from dataclasses import dataclass
from typing import FrozenSet, Optional, Tuple

from cerebro.config import cerebro_config
from cerebro.processing.structured_extractor import PaperSummary

logger = logging.getLogger(__name__)

# Our existing signal types (from backtests/strategies/signals.py)
EXISTING_SIGNALS: FrozenSet[str] = frozenset(
    {
        "momentum",
        "carry",
        "mean_reversion",
        "volatility",
        "atr",
        "rsi",
        "macd",
        "bollinger",
        "sma_crossover",
        "volume",
    }
)

# Signal keywords that map to our existing signals
SIGNAL_KEYWORD_MAP = {
    "momentum": {"momentum", "trend", "time-series momentum", "tsmom"},
    "carry": {"carry", "yield", "interest rate differential"},
    "mean_reversion": {"mean reversion", "reversal", "contrarian", "revert"},
    "volatility": {"volatility", "vol", "variance", "vix", "garch"},
    "value": {"value", "fundamental", "book-to-market", "earnings"},
    "quality": {"quality", "profitability", "accruals"},
    "size": {"size", "small cap", "market cap"},
    "sentiment": {"sentiment", "news", "nlp", "text"},
    "machine_learning": {
        "machine learning",
        "deep learning",
        "neural",
        "random forest",
    },
    "microstructure": {"microstructure", "order flow", "bid-ask", "market making"},
    "factor_timing": {"factor timing", "regime", "tactical"},
    "risk_parity": {"risk parity", "risk budgeting", "equal risk"},
    "pairs_trading": {"pairs", "cointegration", "statistical arbitrage"},
    "options": {"options", "implied volatility", "skew", "greeks"},
    "alternative_data": {
        "alternative data",
        "satellite",
        "web scraping",
        "social media",
    },
}


@dataclass(frozen=True)
class RelevanceScore:
    """Immutable relevance score breakdown.

    Attributes:
        total: Composite score 0-100.
        asset_class_score: Score for asset class match (0-30).
        signal_complementarity_score: Score for signal novelty (0-25).
        data_availability_score: Score for data replicability (0-25).
        infra_fit_score: Score for infrastructure fit (0-20).
        details: Human-readable breakdown.
    """

    total: float
    asset_class_score: float
    signal_complementarity_score: float
    data_availability_score: float
    infra_fit_score: float
    details: str


class RelevanceScorer:
    """Scores paper relevance to our portfolio and infrastructure."""

    def __init__(self) -> None:
        self._target_classes = set(
            c.lower() for c in cerebro_config.scoring.target_asset_classes
        )
        self._available_sources = set(
            s.lower() for s in cerebro_config.scoring.available_data_sources
        )

    def score(self, summary: PaperSummary) -> RelevanceScore:
        """Score a paper summary for relevance.

        Args:
            summary: Structured PaperSummary from extraction.

        Returns:
            RelevanceScore with breakdown.
        """
        ac_score = self._score_asset_class(summary)
        sig_score = self._score_signal_complementarity(summary)
        data_score = self._score_data_availability(summary)
        infra_score = self._score_infra_fit(summary)

        total = ac_score + sig_score + data_score + infra_score

        details = (
            f"Asset class: {ac_score:.0f}/30 | "
            f"Signal complementarity: {sig_score:.0f}/25 | "
            f"Data availability: {data_score:.0f}/25 | "
            f"Infra fit: {infra_score:.0f}/20"
        )

        return RelevanceScore(
            total=round(total, 1),
            asset_class_score=round(ac_score, 1),
            signal_complementarity_score=round(sig_score, 1),
            data_availability_score=round(data_score, 1),
            infra_fit_score=round(infra_score, 1),
            details=details,
        )

    def _score_asset_class(self, summary: PaperSummary) -> float:
        """Score asset class match (0-30 points).

        Full score if paper covers our primary asset classes.
        Partial score for Multi-Asset or adjacent classes.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-30.
        """
        if not summary.asset_class:
            return 5.0  # Unknown asset class gets minimal score

        paper_classes = set(c.lower() for c in summary.asset_class)

        # Direct match with target classes
        direct_matches = paper_classes & self._target_classes
        if direct_matches:
            # Full score for direct match, bonus if covers multiple
            return min(30.0, 20.0 + len(direct_matches) * 5.0)

        # Multi-asset is partially relevant
        if "multi-asset" in paper_classes:
            return 20.0

        # Adjacent asset classes (commodities, rates, crypto)
        adjacent = {"commodities", "rates", "crypto"}
        if paper_classes & adjacent:
            return 10.0

        return 5.0

    def _score_signal_complementarity(self, summary: PaperSummary) -> float:
        """Score signal complementarity (0-25 points).

        Higher score for signals that complement (not duplicate)
        our existing signal set.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-25.
        """
        signal_text = (
            f"{summary.signal_description} {summary.methodology} "
            f"{summary.novelty_claim}"
        ).lower()

        if "no explicit signal" in signal_text and not summary.key_findings:
            return 5.0  # Theoretical paper, low complementarity

        # Check which signal categories this paper touches
        covered_categories: set = set()
        novel_categories: set = set()

        for category, keywords in SIGNAL_KEYWORD_MAP.items():
            if any(kw in signal_text for kw in keywords):
                covered_categories.add(category)
                if category not in EXISTING_SIGNALS:
                    novel_categories.add(category)

        if not covered_categories:
            return 10.0  # Cannot determine, give moderate score

        # Novel signal types get highest score
        if novel_categories:
            return min(25.0, 15.0 + len(novel_categories) * 5.0)

        # Existing signal types with new methodology
        if "novel" in signal_text or "new" in signal_text:
            return 15.0

        # Pure overlap with existing signals
        return 8.0

    def _score_data_availability(self, summary: PaperSummary) -> float:
        """Score data availability (0-25 points).

        Higher score if we can replicate with our existing data sources.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-25.
        """
        if not summary.data_requirements:
            return 12.0  # Unknown requirements, moderate score

        # Map common data requirement descriptions to our sources
        DATA_REQUIREMENT_MAP = {
            "price": {"yfinance", "stooq", "ibkr", "binance"},
            "equity": {"yfinance", "stooq", "ibkr"},
            "stock": {"yfinance", "stooq", "ibkr"},
            "fx": {"yfinance", "ibkr", "ecb_fx"},
            "forex": {"yfinance", "ibkr", "ecb_fx"},
            "interest rate": {"fred"},
            "yield": {"fred"},
            "treasury": {"fred"},
            "macro": {"fred"},
            "economic": {"fred"},
            "gdp": {"fred"},
            "inflation": {"fred"},
            "cpi": {"fred"},
            "crypto": {"binance"},
            "bitcoin": {"binance"},
            "volume": {"yfinance", "stooq", "ibkr", "binance"},
            "option": {"ibkr"},
            "futures": {"ibkr"},
            "intraday": {"ibkr", "polygon"},
            "tick": {"ibkr", "polygon"},
        }

        reqs_text = " ".join(summary.data_requirements).lower()
        total_reqs = len(summary.data_requirements)
        matched_reqs = 0

        for req in summary.data_requirements:
            req_lower = req.lower()
            for keyword, sources in DATA_REQUIREMENT_MAP.items():
                if keyword in req_lower:
                    if sources & self._available_sources:
                        matched_reqs += 1
                        break
            else:
                # Check if requirement text mentions any of our sources directly
                if any(src in req_lower for src in self._available_sources):
                    matched_reqs += 1

        if total_reqs == 0:
            return 12.0

        coverage = matched_reqs / total_reqs
        return round(coverage * 25.0, 1)

    def _score_infra_fit(self, summary: PaperSummary) -> float:
        """Score infrastructure fit (0-20 points).

        Higher score for papers that fit our backtesting and execution stack.

        Args:
            summary: Paper summary.

        Returns:
            Score 0-20.
        """
        score = 10.0  # Base score

        # Lower complexity is better for our small team
        complexity_bonus = {
            "LOW": 6.0,
            "MEDIUM": 3.0,
            "HIGH": 0.0,
        }
        score += complexity_bonus.get(summary.implementation_complexity, 2.0)

        # Already backtested = easier to validate
        if summary.backtest_period:
            score += 2.0

        # Transaction costs modeled = more realistic
        if summary.transaction_costs_modeled:
            score += 2.0

        return min(20.0, score)
