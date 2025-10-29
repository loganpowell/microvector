"""
Test suite for PartitionStore.add() functionality.

Tests the ability to add new documents to existing stores versus
replacing them entirely, and the persistence behavior with cache parameter.
"""

import os
import tempfile
from collections.abc import Generator

import pytest

from microvector import Client
from microvector.search import vector_search
from microvector.utils import EMBEDDING_MODEL


@pytest.fixture
def temp_cache_dirs(shared_model_cache: str) -> Generator[tuple[str, str], None, None]:
    """Create temporary directories for testing caches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use shared session-scoped model cache to avoid re-downloading
        model_cache = shared_model_cache
        vector_cache = os.path.join(tmpdir, "vectors")
        yield model_cache, vector_cache


@pytest.fixture
def client(temp_cache_dirs: tuple[str, str]) -> Client:
    """Create a test client with temporary cache directories."""
    model_cache, vector_cache = temp_cache_dirs
    return Client(
        model_cache=model_cache,
        vector_cache=vector_cache,
        embedding_model=EMBEDDING_MODEL,
    )


@pytest.fixture
def initial_collection() -> list[dict[str, str]]:
    """Initial collection of documents."""
    return [
        {"text": "Python is a programming language", "category": "tech"},
        {"text": "JavaScript is used for web development", "category": "tech"},
    ]


@pytest.fixture
def additional_collection() -> list[dict[str, str]]:
    """Additional documents to add."""
    return [
        {"text": "Ruby is an elegant programming language", "category": "tech"},
        {"text": "Go is great for concurrent programming", "category": "tech"},
    ]


@pytest.fixture
def replacement_collection() -> list[dict[str, str]]:
    """Documents to replace existing collection."""
    return [
        {"text": "Machine learning is a subset of AI", "category": "AI"},
        {"text": "Deep learning uses neural networks", "category": "AI"},
    ]


class TestPartitionStoreAdd:
    """Tests for PartitionStore.add() method."""

    def test_save_initial_append_false(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test creating initial vector store with append=False."""
        store = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=False,
        )

        assert store.partition == "test_partition"
        assert store.size == 2
        assert store.key == "text"

        # Verify we can search the store
        results = store.search(
            term="programming",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_save_initial_append_true(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test creating initial vector store with append=True (should work same as False)."""
        store = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=True,
        )

        assert store.size == 2
        assert store.key == "text"

        # Verify we can search the store
        results = store.search(
            term="programming",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_add_to_existing_store(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test adding documents to existing vector store using PartitionStore.add()."""
        # Create initial store
        store = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=False,
        )

        assert store.size == 2

        # Add additional documents using the add() method
        success = store.add(additional_collection, cache=True)

        assert success is True
        assert store.size == 4

        # Verify all 4 documents are searchable
        results = store.search(
            term="programming",
            top_k=4,
        )
        assert results is not None
        assert len(results) == 4

        # Check that we can find documents from both batches
        texts = [r["text"] for r in results]
        assert any("Python" in t for t in texts)
        assert any("Ruby" in t or "Go" in t for t in texts)

    def test_replace_existing_store(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        replacement_collection: list[dict[str, str]],
    ) -> None:
        """Test replacing existing vector store with append=False."""
        # Create initial store
        client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=False,
        )

        # Replace with new documents using save with append=False
        store = client.save(
            partition="test_partition",
            collection=replacement_collection,
            key="text",
            append=False,
        )

        assert store.size == 2

        # Verify only new documents are searchable
        results = store.search(
            term="AI neural networks",
            top_k=4,
        )
        assert results is not None
        # Should only get 2 results (the replacement documents)
        assert len(results) == 2

        # Original documents should not be present
        texts = [r["text"] for r in results]
        assert not any("Python" in t or "JavaScript" in t for t in texts)
        assert any("Machine learning" in t or "Deep learning" in t for t in texts)

    def test_multiple_adds(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test multiple add operations using PartitionStore.add()."""
        # Create initial store
        store = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
        )

        # First add
        store.add(additional_collection, cache=True)

        # Second add
        third_batch = [
            {"text": "Rust is a systems programming language", "category": "tech"},
        ]
        store.add(third_batch, cache=True)

        # Verify all 5 documents are searchable
        results = store.search(
            term="programming",
            top_k=5,
        )
        assert results is not None
        assert len(results) == 5

    def test_add_with_different_similarity_metrics(
        self, initial_collection: list[dict[str, str]], temp_cache_dirs: tuple[str, str]
    ) -> None:
        """Test add() with different similarity algorithms."""
        model_cache, vector_cache = temp_cache_dirs

        for algo in ["cosine", "dot", "euclidean"]:  # type: ignore
            partition = f"test_{algo}"

            # Create client with specific algorithm
            test_client = Client(
                model_cache=model_cache,
                vector_cache=vector_cache,
                search_algo=algo,  # type: ignore
            )

            # Initial save
            store = test_client.save(
                partition=partition,
                collection=initial_collection,
                key="text",
            )

            # Add using PartitionStore.add()
            store.add(
                [{"text": "TypeScript adds types to JavaScript", "category": "tech"}],
                cache=True,
            )

            # Verify search works
            results = store.search(
                term="programming",
                top_k=3,
            )
            assert results is not None
            assert len(results) == 3


class TestPartitionStoreSearchAndAdd:
    """Tests for combining PartitionStore.search() and add() operations."""

    def test_save_and_search(self, client: Client) -> None:
        """Test saving then searching with PartitionStore."""
        collection = [
            {"text": "First document about Python"},
            {"text": "Second document about JavaScript"},
        ]

        store = client.save(
            partition="temp_search",
            collection=collection,
            cache=True,
        )

        results = store.search(
            term="Python",
            top_k=2,
        )

        assert results is not None
        assert len(results) == 2

    def test_add_then_search(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test adding to existing store then searching."""
        # Create initial cache
        store = client.save(
            partition="search_add_test",
            collection=initial_collection,
            key="text",
        )

        # Add additional documents
        new_docs = [{"text": "Kotlin is a modern JVM language"}]
        store.add(new_docs, cache=True)

        # Search should find all documents
        results = store.search(
            term="programming",
            top_k=3,
        )

        assert results is not None
        assert len(results) == 3  # 2 initial + 1 new


class TestVectorSearchWithPartitionStore:
    """Tests for vector_search() function with PartitionStore."""

    def test_vector_search_save_replace(
        self, temp_cache_dirs: tuple[str, str], initial_collection: list[dict[str, str]]
    ) -> None:
        """Test replacing with append=False using Client API."""
        model_cache, vector_cache = temp_cache_dirs

        # Use Client API for both operations to ensure same cache paths
        client = Client(model_cache=model_cache, vector_cache=vector_cache)
        client.save(
            partition="vector_search_test",
            collection=initial_collection,
            key="text",
        )

        # Replace using save with append=False
        new_collection = [{"text": "Completely new document"}]
        store = client.save(
            partition="vector_search_test",
            collection=new_collection,
        )

        # Search the replaced store
        results = store.search(
            term="document",
            top_k=2,
        )

        assert results is not None
        # Should only find the new document
        assert len(results) == 1
        assert "new document" in results[0]["text"]

    def test_vector_search_with_add(
        self, temp_cache_dirs: tuple[str, str], initial_collection: list[dict[str, str]]
    ) -> None:
        """Test using PartitionStore.add() to append documents."""
        model_cache, vector_cache = temp_cache_dirs

        # Use Client API to create initial store
        client = Client(model_cache=model_cache, vector_cache=vector_cache)
        store = client.save(
            partition="vector_search_add",
            collection=initial_collection,
            key="text",
        )

        # Add using PartitionStore.add()
        new_collection = [{"text": "Swift is used for iOS development"}]
        store.add(new_collection, cache=True)

        # Search should find all documents
        results = store.search(
            term="programming development",
            top_k=3,
        )

        assert results is not None
        assert len(results) == 3  # 2 initial + 1 added


class TestPartitionStoreEdgeCases:
    """Tests for edge cases with PartitionStore.add() functionality."""

    def test_add_without_cache(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test adding to store without persisting (cache=False)."""
        # Create persistent cache
        store = client.save(
            partition="temp_add_test",
            collection=initial_collection,
            key="text",
            cache=True,  # Create persistent cache
        )

        # Verify initial cache has 2 documents
        results = store.search(
            term="programming",
            top_k=5,
        )
        assert results is not None
        assert len(results) == 2

        # Add without persisting
        additional_docs = [
            {"text": "Ruby is an elegant programming language", "category": "tech"},
            {"text": "Go is great for concurrent programming", "category": "tech"},
        ]

        store.add(additional_docs, cache=False)  # Don't persist

        # Should have all 4 documents in memory
        results = store.search(
            term="programming",
            top_k=5,
        )

        assert results is not None
        assert len(results) == 4

        texts = [r["text"] for r in results]
        assert any("Python" in t for t in texts)
        assert any("Ruby" in t or "Go" in t for t in texts)

        # Reload the store to verify only original 2 documents were persisted
        new_store = client.save(
            partition="temp_add_test",
            collection=[],  # Load existing
            cache=True,  # Load from cache
        )

        results = new_store.search(
            term="programming",
            top_k=5,
        )
        assert results is not None
        assert len(results) == 2

        texts = [r["text"] for r in results]
        assert any("Python" in t for t in texts)
        assert not any("Ruby" in t or "Go" in t for t in texts)

    def test_add_empty_collection(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test adding an empty collection."""
        # Create initial store
        store = client.save(
            partition="test_empty_add",
            collection=initial_collection,
            key="text",
        )

        initial_size = store.size

        # Add empty collection - should not fail
        success = store.add([], cache=True)

        assert success is True
        assert store.size == initial_size

        # Original documents should still be there
        results = store.search(
            term="programming",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_add_without_existing_cache(self, client: Client) -> None:
        """Test that creating a non-cached store works."""
        collection = [{"text": "Document without cache"}]

        store = client.save(
            partition="no_cache_test",
            collection=collection,
            cache=False,
        )

        results = store.search(
            term="Document",
            top_k=1,
        )

        assert results is not None
        assert len(results) == 1

    def test_replace_then_add(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        replacement_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test replacing a store and then adding to the new version."""
        # Create initial
        client.save(
            partition="replace_add_test",
            collection=initial_collection,
            key="text",
        )

        # Replace with new store
        store = client.save(
            partition="replace_add_test",
            collection=replacement_collection,
            key="text",
            append=False,
        )

        # Add to the replaced store
        store.add(additional_collection, cache=True)

        # Should have replacement + additional (4 total)
        results = store.search(
            term="AI programming neural networks",
            top_k=5,
        )

        assert results is not None
        assert len(results) == 4

        texts = [r["text"] for r in results]
        # Should not have initial documents
        assert not any("Python" in t and "programming language" in t for t in texts)
        # Should have replacement documents
        assert any("Machine learning" in t or "Deep learning" in t for t in texts)
        # Should have added documents
        assert any("Ruby" in t or "Go" in t for t in texts)
