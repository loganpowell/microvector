"""
PartitionStore: Represents a cached vector store partition with add/remove/search operations.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional, Union

from microvector.store import Store
from microvector.utils import SimilarityMetrics

logger = logging.getLogger(__name__)


class PartitionStore:
    """
    Represents a cached vector store partition.

    Provides methods to search, add, remove documents, and manage persistence.
    The similarity algorithm is locked to the client that created this store.

    Args:
        store: The underlying Store instance
        partition: Name of this partition
        key: The field name that was vectorized
        cache_path: Path to the cache file (None for in-memory only)
        algo: Similarity algorithm (locked from client)

    Example:
        >>> client = Client(search_algo="cosine")
        >>> store = client.save("products", collection=[...], key="text")
        >>> results = store.search("laptop", top_k=5)
        >>> store.add([{"text": "new item"}])
        >>> store.remove(0)
    """

    def __init__(
        self,
        store: Store,
        partition: str,
        key: str,
        cache_path: Optional[str],
        algo: SimilarityMetrics,
    ):
        self._store = store
        self.partition = partition
        self.key = key
        self._cache_path = cache_path
        self.algo = algo

    def search(self, term: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Search this partition for similar documents.

        Args:
            term: Search query string
            top_k: Number of top results to return (default: 5)

        Returns:
            List of matching documents with similarity scores

        Example:
            >>> results = store.search("laptop computer", top_k=3)
            >>> for r in results:
            ...     print(f"{r['text']}: {r['similarity_score']}")
        """
        logger.info(
            "Searching partition '%s' for term: '%s' (top_k=%d, algo=%s)",
            self.partition,
            term,
            top_k,
            self.algo,
        )

        if not term or term.strip() == "":
            logger.error("Search term is empty")
            return []

        results = self._store.query(term, top_k=top_k)
        logger.info("Found %d results", len(results))
        return results

    def add(self, collection: Union[Any, list[Any]], cache: bool = False) -> bool:
        """
        Add documents to this partition.

        Args:
            collection: Single document or list of documents to add
            cache: If True, persist changes to disk. If False (default), keep in-memory only.

        Returns:
            True if successful, False otherwise

        Example:
            >>> # Add single document
            >>> store.add({"text": "new product"}, cache=True)
            True
            >>> # Add multiple documents
            >>> store.add([{"text": "item1"}, {"text": "item2"}], cache=True)
            True
        """
        try:
            logger.info(
                "Adding documents to partition '%s' (cache=%s)", self.partition, cache
            )

            # Store.add() handles both single items and lists
            self._store.add(collection)

            # Persist if requested and we have a cache path
            if cache and self._cache_path:
                self._store.save(self._cache_path)
                logger.info("Changes persisted to %s", self._cache_path)
            elif cache and not self._cache_path:
                logger.warning(
                    "Cannot persist - partition '%s' was created without cache",
                    self.partition,
                )

            return True
        except Exception as e:
            logger.error("Failed to add documents: %s", e)
            return False

    def remove(self, item: Union[int, Any], cache: bool = False) -> bool:
        """
        Remove a document from this partition.

        Args:
            item: Either an integer index or the document itself.
                  If an integer, removes the document at that index.
                  If not an integer, searches for the document and removes it if found.
            cache: If True, persist changes to disk. If False (default), keep in-memory only.

        Returns:
            True if document was found and removed, False otherwise

        Raises:
            IndexError: If integer index is out of range

        Example:
            >>> # Remove by index
            >>> store.remove(0, cache=True)
            True
            >>> # Remove by document content
            >>> store.remove({"text": "old product"}, cache=True)
            True
        """
        try:
            logger.info(
                "Removing document from partition '%s' (cache=%s)",
                self.partition,
                cache,
            )

            # Store.remove_document() handles both index and document
            result = self._store.remove_document(item)

            if not result:
                logger.warning("Document not found in partition '%s'", self.partition)
                return False

            # Persist if requested and we have a cache path
            if cache and self._cache_path:
                self._store.save(self._cache_path)
                logger.info("Changes persisted to %s", self._cache_path)
            elif cache and not self._cache_path:
                logger.warning(
                    "Cannot persist - partition '%s' was created without cache",
                    self.partition,
                )

            return True
        except IndexError as e:
            logger.error("Invalid index: %s", e)
            raise
        except Exception as e:
            logger.error("Failed to remove document: %s", e)
            return False

    def delete(self) -> bool:
        """
        Delete this partition's cache file from disk.

        Returns:
            True if cache file was deleted, False if no cache file exists or deletion failed

        Example:
            >>> store.delete()
            True
        """
        if not self._cache_path:
            logger.warning(
                "Cannot delete - partition '%s' has no cache file", self.partition
            )
            return False

        try:
            if os.path.exists(self._cache_path):
                os.remove(self._cache_path)
                logger.info("Deleted cache file: %s", self._cache_path)
                return True
            else:
                logger.warning("Cache file does not exist: %s", self._cache_path)
                return False
        except Exception as e:
            logger.error("Failed to delete cache file: %s", e)
            return False

    @property
    def size(self) -> int:
        """
        Number of documents in this partition.

        Returns:
            Count of documents

        Example:
            >>> print(f"Store has {store.size} documents")
            Store has 42 documents
        """
        return len(self._store.collection)

    def to_dict(self, vectors: bool = False) -> list[dict[str, Any]]:
        """
        Export partition contents as a list of dictionaries.

        Args:
            vectors: If True, include vector embeddings in the output (default: False)

        Returns:
            List of documents with their indices (and optionally vectors)

        Example:
            >>> docs = store.to_dict()
            >>> for doc in docs:
            ...     print(f"Index {doc['index']}: {doc['document']}")
        """
        return self._store.to_dict(vectors=vectors)

    def __repr__(self) -> str:
        """String representation of this partition store."""
        cache_status = "cached" if self._cache_path else "in-memory"
        return (
            f"PartitionStore(partition='{self.partition}', "
            f"key='{self.key}', algo='{self.algo}', "
            f"size={self.size}, {cache_status})"
        )
