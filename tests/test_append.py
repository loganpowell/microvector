"""
Test suite for the append parameter functionality.

Tests the ability to append new vectors to existing caches versus
replacing them entirely.
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
        cache_models = shared_model_cache
        cache_vectors = os.path.join(tmpdir, "vectors")
        yield cache_models, cache_vectors


@pytest.fixture
def client(temp_cache_dirs: tuple[str, str]) -> Client:
    """Create a test client with temporary cache directories."""
    cache_models, cache_vectors = temp_cache_dirs
    return Client(
        cache_models=cache_models,
        cache_vectors=cache_vectors,
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
    """Additional documents to append."""
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


class TestClientAppend:
    """Tests for Client.save() with append parameter."""

    def test_save_initial_append_false(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test creating initial vector store with append=False."""
        result = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=False,
        )

        assert result["status"] == "success"
        assert result["partition"] == "test_partition"
        assert result["documents_saved"] == 2
        assert result["append"] is False

        # Verify we can search the store
        results = client.search(
            term="programming",
            partition_name="test_partition",
            key="text",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_save_initial_append_true(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test creating initial vector store with append=True (should work same as False)."""
        result = client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=True,
        )

        assert result["status"] == "success"
        assert result["append"] is True

        # Verify we can search the store
        results = client.search(
            term="programming",
            partition_name="test_partition",
            key="text",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_append_to_existing_store(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test appending documents to existing vector store."""
        # Create initial store
        client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
            append=False,
        )

        # Append additional documents
        result = client.save(
            partition="test_partition",
            collection=additional_collection,
            key="text",
            append=True,
        )

        assert result["status"] == "success"
        assert result["documents_saved"] == 2
        assert result["append"] is True

        # Verify all 4 documents are searchable
        results = client.search(
            term="programming",
            partition_name="test_partition",
            key="text",
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

        # Replace with new documents
        result = client.save(
            partition="test_partition",
            collection=replacement_collection,
            key="text",
            append=False,
        )

        assert result["status"] == "success"
        assert result["documents_saved"] == 2
        assert result["append"] is False

        # Verify only new documents are searchable
        results = client.search(
            term="AI neural networks",
            partition_name="test_partition",
            key="text",
            top_k=4,
        )
        assert results is not None
        # Should only get 2 results (the replacement documents)
        assert len(results) == 2

        # Original documents should not be present
        texts = [r["text"] for r in results]
        assert not any("Python" in t or "JavaScript" in t for t in texts)
        assert any("Machine learning" in t or "Deep learning" in t for t in texts)

    def test_multiple_appends(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test multiple append operations."""
        # Create initial store
        client.save(
            partition="test_partition",
            collection=initial_collection,
            key="text",
        )

        # First append
        client.save(
            partition="test_partition",
            collection=additional_collection,
            key="text",
            append=True,
        )

        # Second append
        third_batch = [
            {"text": "Rust is a systems programming language", "category": "tech"},
        ]
        client.save(
            partition="test_partition",
            collection=third_batch,
            key="text",
            append=True,
        )

        # Verify all 5 documents are searchable
        results = client.search(
            term="programming",
            partition_name="test_partition",
            key="text",
            top_k=5,
        )
        assert results is not None
        assert len(results) == 5

    def test_append_with_different_similarity_metrics(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test append with different similarity algorithms."""
        for algo in ["cosine", "dot", "euclidean"]:
            partition = f"test_{algo}"

            # Initial save
            client.save(
                partition=partition,
                collection=initial_collection,
                key="text",
                algo=algo,  # type: ignore
            )

            # Append
            client.save(
                partition=partition,
                collection=[
                    {"text": "TypeScript adds types to JavaScript", "category": "tech"}
                ],
                key="text",
                algo=algo,  # type: ignore
                append=True,
            )

            # Verify search works
            results = client.search(
                term="programming",
                partition_name=partition,
                key="text",
                top_k=3,
                algo=algo,  # type: ignore
            )
            assert results is not None
            assert len(results) == 3


class TestClientSearchWithAppend:
    """Tests for Client.search() with append parameter."""

    def test_search_with_collection_append_false(self, client: Client) -> None:
        """Test search with collection parameter and append=False."""
        collection = [
            {"text": "First document about Python"},
            {"text": "Second document about JavaScript"},
        ]

        results = client.search(
            term="Python",
            partition_name="temp_search",
            key="text",
            collection=collection,
            cache=True,
            append=False,
            top_k=2,
        )

        assert results is not None
        assert len(results) == 2

    def test_search_with_collection_append_true(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test search that appends to existing cache."""
        # Create initial cache
        client.save(
            partition="search_append_test",
            collection=initial_collection,
            key="text",
        )

        # Search with additional collection and append=True
        new_docs = [{"text": "Kotlin is a modern JVM language"}]
        results = client.search(
            term="programming",
            partition_name="search_append_test",
            key="text",
            collection=new_docs,
            cache=True,
            append=True,
            top_k=3,
        )

        assert results is not None
        assert len(results) == 3  # 2 initial + 1 new


class TestVectorSearchAppend:
    """Tests for vector_search() function with append parameter."""

    def test_vector_search_append_false(
        self, temp_cache_dirs: tuple[str, str], initial_collection: list[dict[str, str]]
    ) -> None:
        """Test replacing with append=False using Client API."""
        cache_models, cache_vectors = temp_cache_dirs

        # Use Client API for both operations to ensure same cache paths
        client = Client(cache_models=cache_models, cache_vectors=cache_vectors)
        client.save(
            partition="vector_search_test",
            collection=initial_collection,
            key="text",
        )

        # Replace using client.search with collection
        new_collection = [{"text": "Completely new document"}]
        results = client.search(
            term="document",
            partition_name="vector_search_test",
            key="text",
            collection=new_collection,
            cache=True,
            append=False,
            top_k=2,
        )

        assert results is not None
        # Should only find the new document
        assert len(results) == 1
        assert "new document" in results[0]["text"]

    def test_vector_search_append_true(
        self, temp_cache_dirs: tuple[str, str], initial_collection: list[dict[str, str]]
    ) -> None:
        """Test vector_search with append=True using Client API."""
        cache_models, cache_vectors = temp_cache_dirs

        # Use Client API for both operations to ensure same cache paths
        client = Client(cache_models=cache_models, cache_vectors=cache_vectors)
        client.save(
            partition="vector_search_append",
            collection=initial_collection,
            key="text",
        )

        # Append using client.search with collection
        new_collection = [{"text": "Swift is used for iOS development"}]
        results = client.search(
            term="programming development",
            partition_name="vector_search_append",
            key="text",
            collection=new_collection,
            cache=True,
            append=True,
            top_k=3,
        )

        assert results is not None
        assert len(results) == 3  # 2 initial + 1 appended


class TestAppendEdgeCases:
    """Tests for edge cases with append functionality."""

    def test_append_empty_collection(
        self, client: Client, initial_collection: list[dict[str, str]]
    ) -> None:
        """Test appending an empty collection."""
        # Create initial store
        client.save(
            partition="test_empty_append",
            collection=initial_collection,
            key="text",
        )

        # Append empty collection - should not fail
        result = client.save(
            partition="test_empty_append",
            collection=[],
            key="text",
            append=True,
        )

        assert result["status"] == "success"
        assert result["documents_saved"] == 0

        # Original documents should still be there
        results = client.search(
            term="programming",
            partition_name="test_empty_append",
            key="text",
            top_k=2,
        )
        assert results is not None
        assert len(results) == 2

    def test_append_without_cache(self, client: Client) -> None:
        """Test that append parameter is ignored when cache=False."""
        collection = [{"text": "Document without cache"}]

        results = client.search(
            term="Document",
            partition_name="no_cache_test",
            key="text",
            collection=collection,
            cache=False,
            append=True,  # Should be ignored
            top_k=1,
        )

        assert results is not None
        assert len(results) == 1

    def test_replace_then_append(
        self,
        client: Client,
        initial_collection: list[dict[str, str]],
        replacement_collection: list[dict[str, str]],
        additional_collection: list[dict[str, str]],
    ) -> None:
        """Test replacing a store and then appending to the new version."""
        # Create initial
        client.save(
            partition="replace_append_test",
            collection=initial_collection,
            key="text",
        )

        # Replace
        client.save(
            partition="replace_append_test",
            collection=replacement_collection,
            key="text",
            append=False,
        )

        # Append to the replaced store
        client.save(
            partition="replace_append_test",
            collection=additional_collection,
            key="text",
            append=True,
        )

        # Should have replacement + additional (4 total)
        results = client.search(
            term="AI programming neural networks",
            partition_name="replace_append_test",
            key="text",
            top_k=5,
        )

        assert results is not None
        assert len(results) == 4

        texts = [r["text"] for r in results]
        # Should not have initial documents
        assert not any("Python" in t and "programming language" in t for t in texts)
        # Should have replacement documents
        assert any("Machine learning" in t or "Deep learning" in t for t in texts)
        # Should have appended documents
        assert any("Ruby" in t or "Go" in t for t in texts)
