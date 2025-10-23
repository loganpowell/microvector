"""
Main Client API for microvector library.

Provides a simple interface for creating, saving, and searching vector stores.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from microvector.cache import vector_cache
from microvector.utils import EMBEDDING_MODEL, SimilarityMetrics

logging.basicConfig(
    format="%(levelname)-1s [%(name)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
    force=True,
)

logger = logging.getLogger(__name__)


class Client:
    """
    Main client for microvector operations.

    Provides a high-level interface for managing vector stores with
    automatic caching and persistence.

    Args:
        cache_models: Path to directory for caching embedding models.
            Defaults to "./.cached_models"
        cache_vectors: Path to directory for caching vector stores.
            Defaults to "./.vector_cache"
        embedding_model: HuggingFace embedding model name.
            Defaults to "sentence-transformers/all-MiniLM-L6-v2"

    Example:
        >>> client = Client()
        >>> client.save(
        ...     partition_name="my_data",
        ...     collection=[
        ...         {"text": "hello world", "metadata": {"source": "test"}},
        ...         {"text": "goodbye world", "metadata": {"source": "test"}},
        ...     ]
        ... )
        >>> results = client.search(
        ...     term="hello",
        ...     partition_name="my_data",
        ...     key="text",
        ...     top_k=5
        ... )
    """

    def __init__(
        self,
        cache_models: str = "./.cached_models",
        cache_vectors: str = "./.vector_cache",
        embedding_model: str = EMBEDDING_MODEL,
    ):
        self.cache_models = cache_models
        self.cache_vectors = cache_vectors
        self.embedding_model = embedding_model

        # Ensure cache directories exist
        Path(self.cache_models).mkdir(parents=True, exist_ok=True)
        Path(self.cache_vectors).mkdir(parents=True, exist_ok=True)

        logger.info("Initialized Client with model: %s", self.embedding_model)
        logger.info("Model cache: %s", self.cache_models)
        logger.info("Vector cache: %s", self.cache_vectors)

    def save(
        self,
        partition_name: str,
        collection: list[dict[str, Any]],
        key: str = "text",
        algo: SimilarityMetrics = "cosine",
    ) -> dict[str, Any]:
        """
        Save a collection to the vector store.

        Creates embeddings for the collection and persists them to disk.

        Args:
            partition_name: Name of the partition to save to
            collection: List of documents to save. Each document should be a dict
                containing at least the field specified by `key`
            key: The field name in each document to vectorize. Defaults to "text"
            algo: Similarity metric to use. One of: "cosine", "dot", "euclidean", "derrida"

        Returns:
            Dictionary with status information about the save operation

        Example:
            >>> client.save(
            ...     partition_name="products",
            ...     collection=[
            ...         {"text": "laptop computer", "price": 999},
            ...         {"text": "wireless mouse", "price": 29},
            ...     ],
            ...     key="text"
            ... )
        """
        logger.info("Saving collection to partition: %s", partition_name)

        # Use vector_cache to create and save the vector store
        _ = vector_cache(
            partition=partition_name,
            key=key,
            collection=collection,
            cache=True,
            model=self.embedding_model,
            algo=algo,
            cache_vectors=self.cache_vectors,
            cache_models=self.cache_models,
        )

        return {
            "status": "success",
            "partition": partition_name,
            "documents_saved": len(collection),
            "key": key,
            "algorithm": algo,
        }

    def search(
        self,
        term: str,
        partition_name: str,
        key: str = "text",
        top_k: int = 5,
        collection: Optional[list[dict[str, Any]]] = None,
        cache: bool = True,
        algo: SimilarityMetrics = "cosine",
    ) -> Optional[list[dict[str, Any]]]:
        """
        Search for similar documents in a vector store.

        Can search existing cached vectors or create a new temporary vector store
        from a provided collection.

        Args:
            term: Search query string
            partition_name: Name of the partition to search
            key: The field name in documents that was vectorized. Defaults to "text"
            top_k: Number of top results to return. Defaults to 5
            collection: Optional collection to create a new vector store from.
                If provided with cache=False, creates a temporary in-memory store
            cache: Whether to persist the vector store to disk. Defaults to True
            algo: Similarity metric to use. One of: "cosine", "dot", "euclidean", "derrida"

        Returns:
            List of matching documents with similarity scores, or None if no results

        Example:
            >>> # Search existing cached vectors
            >>> results = client.search(
            ...     term="laptop",
            ...     partition_name="products",
            ...     key="text",
            ...     top_k=3
            ... )
            >>>
            >>> # Create and search temporary vector store
            >>> results = client.search(
            ...     term="laptop",
            ...     partition_name="temp",
            ...     key="text",
            ...     collection=[{"text": "laptop computer"}, {"text": "desktop PC"}],
            ...     cache=False
            ... )
        """
        logger.info("Searching partition '%s' for term: '%s'", partition_name, term)

        # Check for empty search term
        if not term or term.strip() == "":
            logger.error("Search term is empty")
            return None

        # Use vector_cache to get the querier function
        querier = vector_cache(
            partition=partition_name,
            key=key,
            collection=collection,
            cache=cache,
            model=self.embedding_model,
            algo=algo,
            cache_vectors=self.cache_vectors,
            cache_models=self.cache_models,
        )

        if querier is None:
            logger.error("Failed to create querier for partition '%s'", partition_name)
            return None

        # Execute the query
        results = querier(term, top_k)
        logger.info("Found %d results", len(results) if results else 0)

        return results
