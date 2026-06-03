"""Structured paper summary extraction.

Defines the PaperSummary frozen dataclass and extraction logic that
converts raw LLM output into validated, structured data.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from cerebro.processing.llm_summarizer import CerebroLLMClient
from cerebro.sources.base import RawPaper

logger = logging.getLogger(__name__)

# Valid values for controlled fields
VALID_ASSET_CLASSES = frozenset(
    {
        "Equities",
        "FX",
        "Commodities",
        "Rates",
        "Crypto",
        "Multi-Asset",
    }
)

VALID_COMPLEXITIES = frozenset({"LOW", "MEDIUM", "HIGH"})


@dataclass(frozen=True)
class PaperSummary:
    """Immutable structured summary of a research paper.

    Produced by LLM extraction from a RawPaper. All fields are validated
    and normalized. Tuples are used instead of lists for immutability.

    Attributes:
        title: Paper title.
        one_line: One-sentence summary.
        methodology: Description of methodology (2-3 sentences).
        signal_description: Trading signal if proposed.
        asset_class: Tuple of asset classes covered.
        expected_sharpe: Annualized Sharpe if reported.
        data_requirements: Tuple of data sources needed.
        implementation_complexity: LOW / MEDIUM / HIGH.
        key_findings: Tuple of key findings.
        limitations: Tuple of limitations.
        novelty_claim: What is novel about this paper.
        backtest_period: Time period if backtested.
        sample_size: Number of assets/observations if reported.
        out_of_sample: Whether OOS testing was performed.
        transaction_costs_modeled: Whether costs were modeled.
        source_id: Unique ID from the source connector.
        source: Source name (arxiv, ssrn, etc.).
        extracted_at: Timestamp when extraction was performed.
    """

    title: str
    one_line: str
    methodology: str
    signal_description: str
    asset_class: Tuple[str, ...]
    expected_sharpe: Optional[float]
    data_requirements: Tuple[str, ...]
    implementation_complexity: str
    key_findings: Tuple[str, ...]
    limitations: Tuple[str, ...]
    novelty_claim: str
    backtest_period: Optional[str]
    sample_size: Optional[str]
    out_of_sample: bool
    transaction_costs_modeled: bool
    source_id: str = ""
    source: str = ""
    extracted_at: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Set extracted_at to now if not provided."""
        if self.extracted_at is None:
            object.__setattr__(self, "extracted_at", datetime.utcnow())


def _normalize_asset_classes(raw: Any) -> Tuple[str, ...]:
    """Normalize and validate asset class list from LLM output.

    Args:
        raw: Raw value from LLM JSON (list, string, or None).

    Returns:
        Tuple of validated asset class strings.
    """
    if raw is None:
        return ()
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return ()

    normalized: List[str] = []
    for item in raw:
        item_str = str(item).strip()
        # Try to match known asset classes (case-insensitive)
        for valid in VALID_ASSET_CLASSES:
            if item_str.lower() == valid.lower():
                normalized.append(valid)
                break
        else:
            # Accept unknown but log it
            if item_str:
                normalized.append(item_str)

    return tuple(normalized)


def _normalize_complexity(raw: Any) -> str:
    """Normalize implementation complexity to valid enum value.

    Args:
        raw: Raw value from LLM JSON.

    Returns:
        One of "LOW", "MEDIUM", "HIGH".
    """
    if raw is None:
        return "MEDIUM"
    raw_str = str(raw).upper().strip()
    if raw_str in VALID_COMPLEXITIES:
        return raw_str
    return "MEDIUM"


def _to_str_tuple(raw: Any) -> Tuple[str, ...]:
    """Convert a list/string to a tuple of strings.

    Args:
        raw: Raw value from LLM JSON.

    Returns:
        Tuple of non-empty strings.
    """
    if raw is None:
        return ()
    if isinstance(raw, str):
        return (raw,) if raw.strip() else ()
    if isinstance(raw, list):
        return tuple(str(item).strip() for item in raw if str(item).strip())
    return ()


def _safe_float(raw: Any) -> Optional[float]:
    """Safely convert to float or None.

    Args:
        raw: Raw value from LLM JSON.

    Returns:
        Float value or None.
    """
    if raw is None:
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def _safe_str(raw: Any, default: str = "") -> str:
    """Safely convert to string.

    Args:
        raw: Raw value from LLM JSON.
        default: Default value if None.

    Returns:
        String value.
    """
    if raw is None:
        return default
    return str(raw).strip()


def _safe_bool(raw: Any, default: bool = False) -> bool:
    """Safely convert to bool.

    Args:
        raw: Raw value from LLM JSON.
        default: Default value if None.

    Returns:
        Boolean value.
    """
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    raw_str = str(raw).lower().strip()
    return raw_str in ("true", "yes", "1")


def build_paper_summary(
    raw_paper: RawPaper,
    llm_output: Dict[str, Any],
) -> PaperSummary:
    """Build a validated PaperSummary from raw paper and LLM extraction output.

    Args:
        raw_paper: The original RawPaper from a source connector.
        llm_output: Dict of extracted fields from LLM summarization.

    Returns:
        Frozen PaperSummary dataclass with validated fields.
    """
    return PaperSummary(
        title=raw_paper.title,
        one_line=_safe_str(llm_output.get("one_line"), "No summary available"),
        methodology=_safe_str(llm_output.get("methodology"), "Not extracted"),
        signal_description=_safe_str(
            llm_output.get("signal_description"), "No explicit signal"
        ),
        asset_class=_normalize_asset_classes(llm_output.get("asset_class")),
        expected_sharpe=_safe_float(llm_output.get("expected_sharpe")),
        data_requirements=_to_str_tuple(llm_output.get("data_requirements")),
        implementation_complexity=_normalize_complexity(
            llm_output.get("implementation_complexity")
        ),
        key_findings=_to_str_tuple(llm_output.get("key_findings")),
        limitations=_to_str_tuple(llm_output.get("limitations")),
        novelty_claim=_safe_str(llm_output.get("novelty_claim"), "Not specified"),
        backtest_period=_safe_str(llm_output.get("backtest_period")) or None,
        sample_size=_safe_str(llm_output.get("sample_size")) or None,
        out_of_sample=_safe_bool(llm_output.get("out_of_sample")),
        transaction_costs_modeled=_safe_bool(
            llm_output.get("transaction_costs_modeled")
        ),
        source_id=raw_paper.source_id,
        source=raw_paper.source,
    )


async def extract_paper_summary(
    raw_paper: RawPaper,
    llm_client: Optional[CerebroLLMClient] = None,
) -> PaperSummary:
    """Extract a structured PaperSummary from a RawPaper via LLM.

    This is the main entry point for the extraction pipeline. It:
    1. Prepares the paper text (abstract + any available full text)
    2. Calls the LLM for structured extraction
    3. Validates and normalizes the output into a PaperSummary

    Args:
        raw_paper: RawPaper from a source connector.
        llm_client: Optional pre-configured LLM client.

    Returns:
        Validated PaperSummary dataclass.

    Raises:
        RuntimeError: If LLM extraction fails.
    """
    if llm_client is None:
        llm_client = CerebroLLMClient()

    authors_str = ", ".join(raw_paper.authors) if raw_paper.authors else "Unknown"

    llm_output = await llm_client.summarize_paper(
        title=raw_paper.title,
        authors=authors_str,
        source=raw_paper.source,
        text=raw_paper.abstract,
    )

    return build_paper_summary(raw_paper=raw_paper, llm_output=llm_output)
