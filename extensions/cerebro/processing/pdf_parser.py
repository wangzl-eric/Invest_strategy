"""PDF text extraction and section splitting.

Uses pymupdf (fitz) to extract text from PDFs and split into
logical sections (Abstract, Introduction, Methodology, Results, etc.).
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Common section headings in academic papers (case-insensitive patterns)
SECTION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("abstract", r"(?i)^(?:\d+\.?\s*)?abstract\b"),
    ("introduction", r"(?i)^(?:\d+\.?\s*)?introduction\b"),
    (
        "literature_review",
        r"(?i)^(?:\d+\.?\s*)?(?:literature\s+review|related\s+work|background)\b",
    ),
    ("data", r"(?i)^(?:\d+\.?\s*)?(?:data(?:\s+and\s+methodology)?|dataset)\b"),
    (
        "methodology",
        r"(?i)^(?:\d+\.?\s*)?(?:methodology|method|model|approach|framework)\b",
    ),
    ("results", r"(?i)^(?:\d+\.?\s*)?(?:results|empirical\s+results|findings)\b"),
    ("discussion", r"(?i)^(?:\d+\.?\s*)?(?:discussion|analysis)\b"),
    ("conclusion", r"(?i)^(?:\d+\.?\s*)?(?:conclusion|concluding\s+remarks|summary)\b"),
    ("references", r"(?i)^(?:\d+\.?\s*)?(?:references|bibliography)\b"),
    ("appendix", r"(?i)^(?:\d+\.?\s*)?(?:appendix|appendices)\b"),
)


@dataclass(frozen=True)
class ParsedPDF:
    """Immutable result of PDF parsing.

    Attributes:
        full_text: Complete extracted text.
        sections: Dict mapping section name to section text.
        page_count: Number of pages in the PDF.
        metadata: Extracted PDF metadata (title, author, etc.).
    """

    full_text: str
    sections: Dict[str, str]
    page_count: int
    metadata: Dict[str, str]


def extract_text_from_pdf(pdf_path: str) -> ParsedPDF:
    """Extract text from a PDF file and split into sections.

    Args:
        pdf_path: Path to the PDF file on disk.

    Returns:
        ParsedPDF with full text, sections, page count, and metadata.

    Raises:
        ImportError: If pymupdf is not installed.
        FileNotFoundError: If pdf_path does not exist.
        RuntimeError: If PDF cannot be opened or parsed.
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        raise ImportError("pymupdf not installed. Run: pip install pymupdf")

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF '{pdf_path}': {exc}")

    try:
        full_text = _extract_full_text(doc)
        sections = _split_into_sections(full_text)
        metadata = _extract_metadata(doc)
        page_count = doc.page_count

        return ParsedPDF(
            full_text=full_text,
            sections=sections,
            page_count=page_count,
            metadata=metadata,
        )
    finally:
        doc.close()


def extract_text_from_bytes(pdf_bytes: bytes) -> ParsedPDF:
    """Extract text from PDF bytes (e.g., downloaded content).

    Args:
        pdf_bytes: Raw PDF file content as bytes.

    Returns:
        ParsedPDF with full text, sections, page count, and metadata.

    Raises:
        ImportError: If pymupdf is not installed.
        RuntimeError: If PDF cannot be parsed.
    """
    try:
        import fitz
    except ImportError:
        raise ImportError("pymupdf not installed. Run: pip install pymupdf")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise RuntimeError(f"Failed to parse PDF from bytes: {exc}")

    try:
        full_text = _extract_full_text(doc)
        sections = _split_into_sections(full_text)
        metadata = _extract_metadata(doc)
        page_count = doc.page_count

        return ParsedPDF(
            full_text=full_text,
            sections=sections,
            page_count=page_count,
            metadata=metadata,
        )
    finally:
        doc.close()


def _extract_full_text(doc: "fitz.Document") -> str:
    """Extract full text from all pages of a PDF document.

    Args:
        doc: Open pymupdf Document object.

    Returns:
        Combined text from all pages.
    """
    pages_text: List[str] = []

    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text.strip():
                pages_text.append(text)
        except Exception as exc:
            logger.warning("Failed to extract text from page %d: %s", page_num, exc)

    return "\n\n".join(pages_text)


def _split_into_sections(text: str) -> Dict[str, str]:
    """Split extracted text into named sections based on heading patterns.

    Uses regex to detect common academic paper section headings and
    groups text between headings.

    Args:
        text: Full extracted text from the PDF.

    Returns:
        Dict mapping section name to section text content.
    """
    if not text.strip():
        return {}

    lines = text.split("\n")
    section_breaks: List[Tuple[int, str]] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 100:
            # Skip empty lines and very long lines (not headings)
            continue

        for section_name, pattern in SECTION_PATTERNS:
            if re.match(pattern, stripped):
                section_breaks.append((i, section_name))
                break

    if not section_breaks:
        # No sections detected; return full text as "body"
        return {"body": text.strip()}

    sections: Dict[str, str] = {}

    # Text before first section heading
    if section_breaks[0][0] > 0:
        preamble = "\n".join(lines[: section_breaks[0][0]]).strip()
        if preamble:
            sections["preamble"] = preamble

    # Extract each section
    for idx in range(len(section_breaks)):
        start_line = section_breaks[idx][0]
        section_name = section_breaks[idx][1]

        if idx + 1 < len(section_breaks):
            end_line = section_breaks[idx + 1][0]
        else:
            end_line = len(lines)

        section_text = "\n".join(lines[start_line + 1 : end_line]).strip()

        # If duplicate section name, append index
        key = section_name
        if key in sections:
            counter = 2
            while f"{key}_{counter}" in sections:
                counter += 1
            key = f"{key}_{counter}"

        sections[key] = section_text

    return sections


def _extract_metadata(doc: "fitz.Document") -> Dict[str, str]:
    """Extract PDF metadata (title, author, subject, etc.).

    Args:
        doc: Open pymupdf Document object.

    Returns:
        Dict of metadata key-value pairs (strings only).
    """
    raw_meta = doc.metadata or {}
    return {k: str(v).strip() for k, v in raw_meta.items() if v and str(v).strip()}
