"""
Test suite for dot notation key access functionality.

Tests the ability to use dot notation like "parent.child" to access
nested fields in documents for vectorization.
"""

import os
import tempfile
from collections.abc import Generator

import pytest

from microvector import Client
from microvector.embed import get_embeddings
from microvector.utils import EMBEDDING_MODEL


@pytest.fixture
def temp_cache_dirs(shared_model_cache: str) -> Generator[tuple[str, str], None, None]:
    """Create temporary directories for testing caches."""
    with tempfile.TemporaryDirectory() as tmpdir:
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
def nested_documents() -> list[dict]:
    """Sample documents with nested structure."""
    return [
        {
            "title": "Python Guide",
            "metadata": {
                "author": "Alice Smith",
                "year": 2024,
            },
        },
        {
            "title": "JavaScript Tutorial",
            "metadata": {
                "author": "Bob Johnson",
                "year": 2024,
            },
        },
        {
            "title": "ML Basics",
            "metadata": {
                "author": "Charlie Brown",
                "year": 2023,
            },
        },
    ]


@pytest.fixture
def deeply_nested_documents() -> list[dict]:
    """Sample documents with deep nesting."""
    return [
        {
            "id": "doc1",
            "content": {"metadata": {"tags": {"primary": "python programming"}}},
        },
        {
            "id": "doc2",
            "content": {
                "metadata": {"tags": {"primary": "javascript web development"}}
            },
        },
    ]


class TestDotNotationKeyAccess:
    """Tests for dot notation in key parameter."""

    def test_single_level_nested_key(
        self, client: Client, nested_documents: list[dict]
    ) -> None:
        """Test using dot notation for single level nesting."""
        result = client.save(
            partition="nested_single",
            collection=nested_documents,  # type: ignore
            key="metadata.author",
        )

        assert result["status"] == "success"
        assert result["documents_saved"] == 3
        assert result["key"] == "metadata.author"

    def test_multi_level_nested_key(
        self, client: Client, deeply_nested_documents: list[dict]
    ) -> None:
        """Test using dot notation for multi-level nesting."""
        result = client.save(
            partition="nested_deep",
            collection=deeply_nested_documents,  # type: ignore
            key="content.metadata.tags.primary",
        )

        assert result["status"] == "success"
        assert result["documents_saved"] == 2
        assert result["key"] == "content.metadata.tags.primary"

    def test_search_with_nested_key(
        self, client: Client, nested_documents: list[dict]
    ) -> None:
        """Test searching with a nested key."""
        client.save(
            partition="search_nested",
            collection=nested_documents,  # type: ignore
            key="metadata.author",
        )

        results = client.search(
            term="Alice",
            partition="search_nested",
            key="metadata.author",
            top_k=2,
        )

        assert results is not None
        assert len(results) > 0
        assert all("similarity_score" in r for r in results)
        # The top result should be Alice's document
        assert results[0]["metadata"]["author"] == "Alice Smith"

    def test_get_embeddings_with_nested_key(
        self, shared_model_cache: str, nested_documents: list[dict]
    ) -> None:
        """Test get_embeddings function with nested keys."""
        embeddings = get_embeddings(
            chunks=nested_documents,
            key="metadata.author",
            cache_folder=shared_model_cache,
        )

        assert len(embeddings) == 3
        assert all(len(emb) > 0 for emb in embeddings)
        # All embeddings should have the same dimension
        assert all(len(emb) == len(embeddings[0]) for emb in embeddings)

    def test_get_embeddings_with_deep_nested_key(
        self, shared_model_cache: str, deeply_nested_documents: list[dict]
    ) -> None:
        """Test get_embeddings with deeply nested key path."""
        embeddings = get_embeddings(
            chunks=deeply_nested_documents,
            key="content.metadata.tags.primary",
            cache_folder=shared_model_cache,
        )

        assert len(embeddings) == 2
        assert all(len(emb) > 0 for emb in embeddings)

    def test_missing_nested_key_filtered_out(
        self, client: Client, shared_model_cache: str
    ) -> None:
        """Test that documents missing the nested key are filtered out."""
        documents = [
            {"title": "Complete Doc", "metadata": {"author": "Alice"}},
            {"title": "Incomplete Doc", "metadata": {}},  # Missing 'author' key
            {
                "title": "No Metadata",
                # Missing 'metadata' entirely
            },
        ]

        embeddings = get_embeddings(
            chunks=documents,
            key="metadata.author",
            cache_folder=shared_model_cache,
        )

        # Only 1 document has the complete key path
        assert len(embeddings) == 1

    def test_different_nested_keys_same_collection(self, client: Client) -> None:
        """Test using different nested keys for different partitions."""
        documents = [
            {
                "name": "Product A",
                "specs": {"description": "High quality product"},
                "reviews": {"summary": "Excellent product"},
            },
            {
                "name": "Product B",
                "specs": {"description": "Budget friendly option"},
                "reviews": {"summary": "Good value for money"},
            },
        ]

        # Save using specs.description
        result1 = client.save(
            partition="by_specs",
            collection=documents,  # type: ignore
            key="specs.description",
        )

        # Save using reviews.summary
        result2 = client.save(
            partition="by_reviews",
            collection=documents,  # type: ignore
            key="reviews.summary",
        )

        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result1["key"] == "specs.description"
        assert result2["key"] == "reviews.summary"

    def test_nested_key_with_none_value(self, shared_model_cache: str) -> None:
        """Test that documents with None value in nested key are filtered."""
        documents = [
            {"metadata": {"author": "Alice"}},
            {"metadata": {"author": None}},  # Explicitly None
        ]

        embeddings = get_embeddings(
            chunks=documents,
            key="metadata.author",
            cache_folder=shared_model_cache,
        )

        # Only 1 document has a non-None value
        assert len(embeddings) == 1

    def test_append_with_nested_key(
        self, client: Client, nested_documents: list[dict]
    ) -> None:
        """Test appending documents with nested keys."""
        # Initial save
        client.save(
            partition="append_nested",
            collection=nested_documents[:2],  # type: ignore
            key="metadata.author",
            append=False,
        )

        # Append more
        result = client.save(
            partition="append_nested",
            collection=nested_documents[2:],  # type: ignore
            key="metadata.author",
            append=True,
        )

        assert result["status"] == "success"
        assert result["append"] is True

        # Verify all documents are searchable
        results = client.search(
            term="author",
            partition="append_nested",
            key="metadata.author",
            top_k=5,
        )

        assert results is not None
        assert len(results) == 3
