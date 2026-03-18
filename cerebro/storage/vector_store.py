"""ChromaDB vector store for paper embeddings.

Uses ChromaDB with sentence-transformers for local embeddings.
Stores paper embeddings for semantic search and novelty detection.
No API cost — all embeddings computed locally.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cerebro.config import cerebro_config

logger = logging.getLogger(__name__)


class CerebroVectorStore:
    """ChromaDB-backed vector store for research paper embeddings.

    Provides semantic search over papers and embedding storage
    for novelty detection and deduplication.
    """

    COLLECTION_NAME = "cerebro_papers"

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ) -> None:
        """Initialize the vector store.

        ChromaDB client and embedding function are created lazily
        on first use.

        Args:
            persist_directory: Path to ChromaDB persistence directory.
            embedding_model: Sentence-transformers model name.
        """
        self._persist_dir = persist_directory or str(cerebro_config.chromadb_abs_path)
        self._embedding_model = (
            embedding_model or cerebro_config.storage.embedding_model
        )
        self._client = None
        self._collection = None

    def _ensure_initialized(self) -> None:
        """Initialize ChromaDB client and collection on first use."""
        if self._collection is not None:
            return

        try:
            import chromadb
            from chromadb.utils import embedding_functions
        except ImportError:
            raise ImportError("chromadb not installed. Run: pip install chromadb")

        # Ensure persistence directory exists
        persist_path = Path(self._persist_dir)
        persist_path.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=str(persist_path))

        # Use sentence-transformers for local embeddings
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self._embedding_model
        )

        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=ef,
            metadata={"description": "Cerebro research paper embeddings"},
        )

        logger.info(
            "Initialized ChromaDB at '%s' with model '%s' (%d documents)",
            self._persist_dir,
            self._embedding_model,
            self._collection.count(),
        )

    def add_paper(
        self,
        paper_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a single paper embedding to the store.

        Args:
            paper_id: Unique identifier for the paper.
            text: Text to embed (title + abstract + methodology).
            metadata: Optional metadata dict to store alongside embedding.
        """
        self._ensure_initialized()

        safe_metadata = self._sanitize_metadata(metadata or {})

        try:
            self._collection.upsert(
                ids=[paper_id],
                documents=[text],
                metadatas=[safe_metadata],
            )
        except Exception as exc:
            logger.error("Failed to add paper '%s' to vector store: %s", paper_id, exc)
            raise

    def add_papers_batch(
        self,
        paper_ids: List[str],
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add multiple papers to the store in a batch.

        Args:
            paper_ids: List of unique identifiers.
            texts: List of texts to embed.
            metadatas: Optional list of metadata dicts.
        """
        if not paper_ids:
            return

        self._ensure_initialized()

        safe_metadatas = [
            self._sanitize_metadata(m) for m in (metadatas or [{} for _ in paper_ids])
        ]

        try:
            # ChromaDB has batch size limits; chunk if needed
            batch_size = 100
            for i in range(0, len(paper_ids), batch_size):
                end = min(i + batch_size, len(paper_ids))
                self._collection.upsert(
                    ids=paper_ids[i:end],
                    documents=texts[i:end],
                    metadatas=safe_metadatas[i:end],
                )

            logger.info("Added %d papers to vector store", len(paper_ids))
        except Exception as exc:
            logger.error("Failed to batch-add papers to vector store: %s", exc)
            raise

    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search for papers matching a query.

        Args:
            query: Search query text.
            n_results: Max number of results to return.
            where: Optional ChromaDB where filter.

        Returns:
            List of result dicts with id, text, metadata, and distance.
        """
        self._ensure_initialized()

        try:
            kwargs: Dict[str, Any] = {
                "query_texts": [query],
                "n_results": min(n_results, self._collection.count() or 1),
            }
            if where:
                kwargs["where"] = where

            results = self._collection.query(**kwargs)

            # Flatten ChromaDB results into list of dicts
            output: List[Dict[str, Any]] = []
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for idx in range(len(ids)):
                output.append(
                    {
                        "id": ids[idx],
                        "text": documents[idx] if idx < len(documents) else "",
                        "metadata": metadatas[idx] if idx < len(metadatas) else {},
                        "distance": distances[idx] if idx < len(distances) else 0.0,
                    }
                )

            return output
        except Exception as exc:
            logger.error("Vector store search failed: %s", exc)
            return []

    def get_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific paper by ID.

        Args:
            paper_id: Unique paper identifier.

        Returns:
            Dict with id, text, and metadata, or None if not found.
        """
        self._ensure_initialized()

        try:
            result = self._collection.get(ids=[paper_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0] if result["documents"] else "",
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                }
        except Exception as exc:
            logger.error(
                "Failed to get paper '%s' from vector store: %s", paper_id, exc
            )

        return None

    def delete_paper(self, paper_id: str) -> None:
        """Delete a paper from the vector store.

        Args:
            paper_id: Unique paper identifier.
        """
        self._ensure_initialized()

        try:
            self._collection.delete(ids=[paper_id])
        except Exception as exc:
            logger.error(
                "Failed to delete paper '%s' from vector store: %s", paper_id, exc
            )

    @property
    def count(self) -> int:
        """Return the number of papers in the store."""
        self._ensure_initialized()
        return self._collection.count()

    @staticmethod
    def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata for ChromaDB (only str/int/float/bool allowed).

        Args:
            metadata: Raw metadata dict.

        Returns:
            Dict with only ChromaDB-compatible value types.
        """
        sanitized: Dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = ""
            elif isinstance(value, (list, tuple)):
                sanitized[key] = ", ".join(str(v) for v in value)
            else:
                sanitized[key] = str(value)
        return sanitized
