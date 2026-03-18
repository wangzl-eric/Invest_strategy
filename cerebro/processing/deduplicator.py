"""Semantic deduplication for research papers.

Uses sentence-transformers embeddings and cosine similarity to detect
duplicate or near-duplicate papers across sources.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

from cerebro.config import cerebro_config
from cerebro.sources.base import RawPaper

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeduplicationResult:
    """Immutable result of deduplication check for a single paper.

    Attributes:
        paper: The paper being checked.
        is_duplicate: Whether the paper is a semantic duplicate.
        most_similar_id: Source ID of the most similar existing paper.
        similarity_score: Cosine similarity to the most similar paper (0-1).
    """

    paper: RawPaper
    is_duplicate: bool
    most_similar_id: Optional[str]
    similarity_score: float


class SemanticDeduplicator:
    """Detects duplicate papers using embedding cosine similarity.

    Uses sentence-transformers to compute embeddings of paper titles
    and abstracts, then compares incoming papers against a corpus of
    already-seen papers.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> None:
        """Initialize the deduplicator.

        The sentence-transformers model is loaded lazily on first use.

        Args:
            model_name: Sentence-transformers model name.
            threshold: Cosine similarity threshold for duplicate detection.
        """
        self._model_name = model_name or cerebro_config.storage.embedding_model
        self._threshold = threshold or cerebro_config.storage.dedup_threshold
        self._model = None
        self._corpus_embeddings: Optional[np.ndarray] = None
        self._corpus_ids: List[str] = []

    def _load_model(self) -> None:
        """Load the sentence-transformers model (lazy initialization)."""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            logger.info("Loaded sentence-transformers model: %s", self._model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    def _paper_text(self, paper: RawPaper) -> str:
        """Build the text representation of a paper for embedding.

        Combines title and abstract for a richer semantic signal.

        Args:
            paper: RawPaper instance.

        Returns:
            Combined text string.
        """
        parts = [paper.title]
        if paper.abstract:
            parts.append(paper.abstract[:500])
        return " ".join(parts)

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for a single text string.

        Args:
            text: Input text.

        Returns:
            Numpy array of shape (embedding_dim,).
        """
        self._load_model()
        return self._model.encode(text, normalize_embeddings=True)

    def _compute_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a batch of texts.

        Args:
            texts: List of input texts.

        Returns:
            Numpy array of shape (n_texts, embedding_dim).
        """
        self._load_model()
        return self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def add_to_corpus(self, papers: List[RawPaper]) -> None:
        """Add papers to the deduplication corpus.

        These papers will be checked against when deduplicating
        new incoming papers.

        Args:
            papers: List of already-known papers to add to corpus.
        """
        if not papers:
            return

        texts = [self._paper_text(p) for p in papers]
        new_embeddings = self._compute_embeddings_batch(texts)
        new_ids = [p.unique_key for p in papers]

        if self._corpus_embeddings is None:
            self._corpus_embeddings = new_embeddings
        else:
            self._corpus_embeddings = np.vstack(
                [self._corpus_embeddings, new_embeddings]
            )

        self._corpus_ids.extend(new_ids)
        logger.info(
            "Added %d papers to dedup corpus (total: %d)",
            len(papers),
            len(self._corpus_ids),
        )

    def check_duplicates(
        self,
        papers: List[RawPaper],
    ) -> List[DeduplicationResult]:
        """Check a list of papers for duplicates against the corpus.

        Args:
            papers: List of new papers to check.

        Returns:
            List of DeduplicationResult, one per input paper.
        """
        if not papers:
            return []

        # If corpus is empty, nothing can be a duplicate
        if self._corpus_embeddings is None or len(self._corpus_ids) == 0:
            return [
                DeduplicationResult(
                    paper=p,
                    is_duplicate=False,
                    most_similar_id=None,
                    similarity_score=0.0,
                )
                for p in papers
            ]

        texts = [self._paper_text(p) for p in papers]
        new_embeddings = self._compute_embeddings_batch(texts)

        # Cosine similarity (embeddings are already normalized)
        similarity_matrix = new_embeddings @ self._corpus_embeddings.T

        results: List[DeduplicationResult] = []
        for i, paper in enumerate(papers):
            sims = similarity_matrix[i]
            max_idx = int(np.argmax(sims))
            max_sim = float(sims[max_idx])

            is_dup = max_sim >= self._threshold

            results.append(
                DeduplicationResult(
                    paper=paper,
                    is_duplicate=is_dup,
                    most_similar_id=self._corpus_ids[max_idx],
                    similarity_score=round(max_sim, 4),
                )
            )

        return results

    def deduplicate_batch(
        self,
        papers: List[RawPaper],
    ) -> Tuple[List[RawPaper], List[DeduplicationResult]]:
        """Deduplicate a batch of papers, also checking within the batch.

        Returns the unique papers and full deduplication results.
        Papers that pass dedup are automatically added to the corpus.

        Args:
            papers: List of new papers to deduplicate.

        Returns:
            Tuple of (unique_papers, all_results).
        """
        if not papers:
            return [], []

        # First, check against existing corpus
        results = self.check_duplicates(papers)

        # Then check within the batch for inter-duplicates
        unique_papers: List[RawPaper] = []
        batch_texts: List[str] = []

        for result in results:
            if result.is_duplicate:
                logger.debug(
                    "Duplicate detected: '%s' (sim=%.3f to %s)",
                    result.paper.title[:60],
                    result.similarity_score,
                    result.most_similar_id,
                )
                continue

            # Check against papers already accepted in this batch
            if batch_texts:
                paper_text = self._paper_text(result.paper)
                paper_emb = self._compute_embedding(paper_text)
                batch_embs = self._compute_embeddings_batch(batch_texts)
                batch_sims = paper_emb @ batch_embs.T
                max_batch_sim = float(np.max(batch_sims))

                if max_batch_sim >= self._threshold:
                    logger.debug(
                        "Within-batch duplicate: '%s' (sim=%.3f)",
                        result.paper.title[:60],
                        max_batch_sim,
                    )
                    continue

            unique_papers.append(result.paper)
            batch_texts.append(self._paper_text(result.paper))

        # Add unique papers to corpus for future dedup
        if unique_papers:
            self.add_to_corpus(unique_papers)

        return unique_papers, results
