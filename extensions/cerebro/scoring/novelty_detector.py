"""Novelty detector for research papers.

Uses embedding cosine similarity against a corpus of existing papers
to classify new papers as:
- NOVEL: Genuinely new approach (similarity < 0.5)
- INCREMENTAL: Builds on existing work (0.5 <= similarity < 0.7)
- REHASH: Very similar to existing papers (similarity >= 0.7)
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from cerebro.config import cerebro_config
from cerebro.processing.structured_extractor import PaperSummary

logger = logging.getLogger(__name__)


# Novelty classification thresholds
REHASH_THRESHOLD = 0.70  # Above = rehash of existing work
INCREMENTAL_THRESHOLD = 0.50  # Between = incremental contribution


@dataclass(frozen=True)
class NoveltyResult:
    """Immutable novelty detection result.

    Attributes:
        classification: NOVEL, INCREMENTAL, or REHASH.
        max_similarity: Highest similarity score against corpus.
        most_similar_title: Title of the most similar existing paper.
        most_similar_id: ID of the most similar existing paper.
        novelty_score: Inverted similarity (0 = rehash, 100 = completely novel).
        explanation: Human-readable explanation.
    """

    classification: str
    max_similarity: float
    most_similar_title: Optional[str]
    most_similar_id: Optional[str]
    novelty_score: float
    explanation: str


@dataclass(frozen=True)
class CorpusEntry:
    """Immutable entry in the novelty detection corpus.

    Attributes:
        paper_id: Unique identifier for the paper.
        title: Paper title.
        text: Combined text used for embedding.
    """

    paper_id: str
    title: str
    text: str


class NoveltyDetector:
    """Detects novelty of papers relative to an existing corpus.

    Uses sentence-transformers embeddings and cosine similarity to
    compare incoming papers against previously seen research.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        rehash_threshold: Optional[float] = None,
        incremental_threshold: Optional[float] = None,
    ) -> None:
        """Initialize the novelty detector.

        The embedding model is loaded lazily on first use.

        Args:
            model_name: Sentence-transformers model name.
            rehash_threshold: Similarity above which = rehash.
            incremental_threshold: Similarity above which = incremental.
        """
        self._model_name = model_name or cerebro_config.storage.embedding_model
        self._rehash_threshold = rehash_threshold or REHASH_THRESHOLD
        self._incremental_threshold = incremental_threshold or INCREMENTAL_THRESHOLD
        self._model = None
        self._corpus: List[CorpusEntry] = []
        self._corpus_embeddings: Optional[np.ndarray] = None

    def _load_model(self) -> None:
        """Load the sentence-transformers model (lazy)."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            logger.info(
                "Loaded embedding model for novelty detection: %s",
                self._model_name,
            )
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    def _summary_text(self, summary: PaperSummary) -> str:
        """Build text representation for embedding from PaperSummary.

        Combines title, methodology, signal description, and key findings
        for a rich semantic representation.

        Args:
            summary: PaperSummary instance.

        Returns:
            Combined text string.
        """
        parts = [summary.title]
        if summary.one_line:
            parts.append(summary.one_line)
        if summary.methodology and summary.methodology != "Not extracted":
            parts.append(summary.methodology)
        if (
            summary.signal_description
            and summary.signal_description != "No explicit signal"
        ):
            parts.append(summary.signal_description)
        if summary.key_findings:
            parts.extend(summary.key_findings[:3])

        return " ".join(parts)

    def add_to_corpus(
        self,
        paper_id: str,
        title: str,
        summary: PaperSummary,
    ) -> None:
        """Add a paper to the novelty detection corpus.

        Args:
            paper_id: Unique identifier for the paper.
            title: Paper title.
            summary: PaperSummary for text extraction.
        """
        text = self._summary_text(summary)
        entry = CorpusEntry(paper_id=paper_id, title=title, text=text)
        self._corpus.append(entry)

        # Recompute corpus embeddings
        self._load_model()
        new_embedding = self._model.encode(text, normalize_embeddings=True).reshape(
            1, -1
        )

        if self._corpus_embeddings is None:
            self._corpus_embeddings = new_embedding
        else:
            self._corpus_embeddings = np.vstack(
                [self._corpus_embeddings, new_embedding]
            )

    def add_corpus_batch(
        self,
        entries: List[Tuple[str, str, PaperSummary]],
    ) -> None:
        """Add multiple papers to the corpus at once.

        Args:
            entries: List of (paper_id, title, summary) tuples.
        """
        if not entries:
            return

        texts = []
        for paper_id, title, summary in entries:
            text = self._summary_text(summary)
            self._corpus.append(CorpusEntry(paper_id=paper_id, title=title, text=text))
            texts.append(text)

        self._load_model()
        new_embeddings = self._model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )

        if self._corpus_embeddings is None:
            self._corpus_embeddings = new_embeddings
        else:
            self._corpus_embeddings = np.vstack(
                [self._corpus_embeddings, new_embeddings]
            )

        logger.info(
            "Added %d papers to novelty corpus (total: %d)",
            len(entries),
            len(self._corpus),
        )

    def detect(self, summary: PaperSummary) -> NoveltyResult:
        """Detect the novelty of a paper against the existing corpus.

        Args:
            summary: PaperSummary to check for novelty.

        Returns:
            NoveltyResult with classification and similarity scores.
        """
        # Empty corpus = everything is novel
        if not self._corpus or self._corpus_embeddings is None:
            return NoveltyResult(
                classification="NOVEL",
                max_similarity=0.0,
                most_similar_title=None,
                most_similar_id=None,
                novelty_score=100.0,
                explanation="No existing papers in corpus for comparison.",
            )

        self._load_model()
        text = self._summary_text(summary)
        embedding = self._model.encode(text, normalize_embeddings=True).reshape(1, -1)

        # Cosine similarity (normalized embeddings)
        similarities = (embedding @ self._corpus_embeddings.T).flatten()

        max_idx = int(np.argmax(similarities))
        max_sim = float(similarities[max_idx])
        most_similar = self._corpus[max_idx]

        classification = self._classify(max_sim)
        novelty_score = round((1.0 - max_sim) * 100.0, 1)
        explanation = self._build_explanation(
            classification, max_sim, most_similar.title
        )

        return NoveltyResult(
            classification=classification,
            max_similarity=round(max_sim, 4),
            most_similar_title=most_similar.title,
            most_similar_id=most_similar.paper_id,
            novelty_score=max(0.0, novelty_score),
            explanation=explanation,
        )

    def _classify(self, similarity: float) -> str:
        """Classify novelty based on similarity score.

        Args:
            similarity: Cosine similarity value (0-1).

        Returns:
            Classification string: NOVEL, INCREMENTAL, or REHASH.
        """
        if similarity >= self._rehash_threshold:
            return "REHASH"
        elif similarity >= self._incremental_threshold:
            return "INCREMENTAL"
        else:
            return "NOVEL"

    def _build_explanation(
        self,
        classification: str,
        similarity: float,
        similar_title: str,
    ) -> str:
        """Build human-readable explanation of novelty result.

        Args:
            classification: NOVEL, INCREMENTAL, or REHASH.
            similarity: Cosine similarity score.
            similar_title: Title of most similar paper.

        Returns:
            Explanation string.
        """
        if classification == "REHASH":
            return (
                f"Very similar to existing paper (sim={similarity:.2f}): "
                f"'{similar_title}'. Likely a rehash or minor extension."
            )
        elif classification == "INCREMENTAL":
            return (
                f"Builds on existing work (sim={similarity:.2f}): "
                f"'{similar_title}'. May offer incremental improvements."
            )
        else:
            return (
                f"Appears novel (sim={similarity:.2f}). "
                f"Most similar existing paper: '{similar_title}'."
            )

    @property
    def corpus_size(self) -> int:
        """Return the number of papers in the corpus."""
        return len(self._corpus)
