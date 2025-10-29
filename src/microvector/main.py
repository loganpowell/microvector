"""
Main Client API for microvector library.

Provides a simple interface for creating, saving, and searching vector stores.
"""

import logging
from pathlib import Path
from typing import Any

from microvector.cache import vector_cache
from microvector.partition import PartitionStore
from microvector.utils import (
    EMBEDDING_MODEL,
    MODEL_CACHE_DIR,
    VECTOR_CACHE_DIR,
    SimilarityMetrics,
)

# Get logger - let the library consumer configure logging
logger = logging.getLogger(__name__)


class Client:
    """
    Main client for microvector operations.

    Provides a high-level interface for managing vector stores with
    automatic caching and persistence. The similarity algorithm is set
    at the client level and applies to all partitions created by this client.

    Args:
        model_cache: Path to directory for caching embedding models.
            Defaults to MODEL_CACHE_DIR ("./.cached_models")
        vector_cache: Path to directory for caching vector stores.
            Defaults to VECTOR_CACHE_DIR ("./.vector_cache")
        embedding_model: HuggingFace embedding model name.
            Defaults to "avsolatorio/GIST-small-Embedding-v0"
        search_algo: Similarity metric for all partitions created by this client.
            One of: "cosine" (default), "dot", "euclidean", "derrida"

    Example:
        >>> client = Client(search_algo="cosine")
        >>> store = client.save(
        ...     partition="my_data",
        ...     collection=[
        ...         {"text": "hello world", "metadata": {"source": "test"}},
        ...         {"text": "goodbye world", "metadata": {"source": "test"}},
        ...     ]
        ... )
        >>> results = store.search("hello", top_k=5)
    """

    def __init__(
        self,
        model_cache: str = MODEL_CACHE_DIR,
        vector_cache: str = VECTOR_CACHE_DIR,
        embedding_model: str = EMBEDDING_MODEL,
        search_algo: SimilarityMetrics = "cosine",
    ):
        self.model_cache: str = model_cache
        self.vector_cache: str = vector_cache
        self.embedding_model: str = embedding_model
        self.search_algo: SimilarityMetrics = search_algo

        # Ensure cache directories exist
        Path(self.model_cache).mkdir(parents=True, exist_ok=True)
        Path(self.vector_cache).mkdir(parents=True, exist_ok=True)

        logger.info("Initialized Client with model: %s", self.embedding_model)
        logger.info("Search algorithm: %s", self.search_algo)
        logger.info("Model cache: %s", self.model_cache)
        logger.info("Vector cache: %s", self.vector_cache)

    def save(
        self,
        partition: str,
        collection: list[dict[str, Any]],
        key: str = "text",
        cache: bool = False,
        append: bool = False,
    ) -> PartitionStore:
        """
        Save a collection to the vector store and return a PartitionStore.

        Creates embeddings for the collection and optionally persists them to disk.
        Uses the client's search_algo for all operations.

        Args:
            partition: Name of the partition to save to
            collection: List of documents to save. Each document should be a dict
                containing at least the field specified by `key`
            key: The field name in each document to vectorize. Defaults to "text"
            cache: If True, persist the vector store to disk.
                   If False (default), create an in-memory only store.
            append: If True, adds new vectors to existing cache. If False (default),
                replaces existing cache with new vectors

        Returns:
            PartitionStore instance for this partition

        Example:
            >>> client = Client(search_algo="cosine")
            >>> store = client.save(
            ...     partition="products",
            ...     collection=[
            ...         {"text": "laptop computer", "price": 999},
            ...         {"text": "wireless mouse", "price": 29},
            ...     ],
            ...     key="text"
            ... )
            >>> results = store.search("computer", top_k=5)
            >>>
            >>> # Append more documents to existing partition
            >>> store = client.save(
            ...     partition="products",
            ...     collection=[{"text": "keyboard", "price": 79}],
            ...     key="text",
            ...     cache=True,
            ...     append=True
            ... )
        """
        logger.info(
            "Saving collection to partition: %s (cache=%s, append=%s)",
            partition,
            cache,
            append,
        )

        # Use vector_cache to create and save the vector store
        # Returns a PartitionStore instance
        store = vector_cache(
            partition=partition,
            key=key,
            collection=collection,
            cache=cache,
            model=self.embedding_model,
            algo=self.search_algo,
            cache_vectors=self.vector_cache,
            cache_models=self.model_cache,
            append=append,
        )

        return store
