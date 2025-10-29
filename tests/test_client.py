"""
Test suite for microvector Client API.
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from microvector import Client
from microvector.utils import EMBEDDING_MODEL, MODEL_CACHE_DIR, VECTOR_CACHE_DIR


@pytest.fixture
def temp_cache_dirs(shared_model_cache: str) -> Generator[tuple[str, str], None, None]:
    """Create temporary directories for testing caches."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use shared session-scoped model cache to avoid re-downloading
        model_cache = shared_model_cache
        vector_cache = os.path.join(tmpdir, "vectors")
        yield model_cache, vector_cache


@pytest.fixture
def sample_collection() -> list[dict[str, str]]:
    """Sample collection for testing."""
    return [
        {"text": "The quick brown fox jumps over the lazy dog", "category": "animals"},
        {"text": "Python is a high-level programming language", "category": "tech"},
        {"text": "Machine learning models learn from data", "category": "ai"},
        {"text": "The lazy dog sleeps under the tree", "category": "animals"},
        {"text": "JavaScript is used for web development", "category": "tech"},
    ]


@pytest.fixture
def client(temp_cache_dirs: tuple[str, str]) -> Client:
    """Create a test client with temporary cache directories."""
    model_cache, vector_cache = temp_cache_dirs
    return Client(
        model_cache=model_cache,
        vector_cache=vector_cache,
        embedding_model=EMBEDDING_MODEL,
    )


class TestClientInitialization:
    """Tests for Client initialization."""

    def test_client_init_default_paths(self) -> None:
        """Test client initialization with default paths."""
        client = Client()
        assert client.model_cache == MODEL_CACHE_DIR
        assert client.vector_cache == VECTOR_CACHE_DIR
        assert client.embedding_model == EMBEDDING_MODEL

    def test_client_init_custom_paths(self, temp_cache_dirs: tuple[str, str]) -> None:
        """Test client initialization with custom paths."""
        model_cache, vector_cache = temp_cache_dirs
        client = Client(
            model_cache=model_cache,
            vector_cache=vector_cache,
            embedding_model=EMBEDDING_MODEL,
        )
        assert client.model_cache == model_cache
        assert client.vector_cache == vector_cache
        assert os.path.exists(model_cache)
        assert os.path.exists(vector_cache)

    def test_client_creates_cache_directories(
        self, temp_cache_dirs: tuple[str, str]
    ) -> None:
        """Test that client creates cache directories if they don't exist."""
        model_cache, vector_cache = temp_cache_dirs
        # Model cache is now session-scoped and already exists
        assert os.path.exists(model_cache)
        # Vector cache should not exist yet
        assert not os.path.exists(vector_cache)

        Client(model_cache=model_cache, vector_cache=vector_cache)

        # Both should exist after Client initialization
        assert os.path.exists(model_cache)
        assert os.path.exists(vector_cache)


class TestClientSave:
    """Tests for Client.save() method."""

    def test_save_returns_success_info(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that save returns a PartitionStore with proper attributes."""
        store = client.save(
            partition="test_partition",
            collection=sample_collection,
        )

        assert store.partition == "test_partition"
        assert store.size == len(sample_collection)
        assert store.key == "text"
        assert store.algo == "cosine"

    def test_save_creates_pickle_file(
        self,
        client: Client,
        sample_collection: list[dict[str, str]],
        temp_cache_dirs: tuple[str, str],
    ) -> None:
        """Test that save creates a pickle file in the cache directory."""
        _, vector_cache = temp_cache_dirs
        client.save(
            partition="test_partition",
            collection=sample_collection,
            cache=True,  # Need to persist to disk
        )

        expected_file = Path(vector_cache) / "test_partition.pickle.gz"
        assert expected_file.exists()

    def test_save_with_custom_key(self, client: Client) -> None:
        """Test saving with a custom key field."""
        collection = [
            {"description": "First item", "value": 1},
            {"description": "Second item", "value": 2},
        ]
        store = client.save(
            partition="custom_key_test",
            collection=collection,  # type: ignore
            key="description",
        )

        assert store.key == "description"

    def test_save_with_different_algorithms(
        self, sample_collection: list[dict[str, str]], temp_cache_dirs: tuple[str, str]
    ) -> None:
        """Test saving with different similarity algorithms."""
        model_cache, vector_cache = temp_cache_dirs
        algorithms: list = ["cosine", "dot", "euclidean", "derrida"]  # type: ignore

        for algo in algorithms:
            # Create client with specific algorithm
            client = Client(
                model_cache=model_cache,
                vector_cache=vector_cache,
                search_algo=algo,  # type: ignore
            )
            store = client.save(
                partition=f"test_{algo}",
                collection=sample_collection,
            )
            assert store.algo == algo


class TestClientSearch:
    """Tests for Client.search() method."""

    def test_search_returns_results(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that search returns relevant results."""
        # Save the collection and get store
        store = client.save(
            partition="search_test",
            collection=sample_collection,
        )

        # Search the store
        results = store.search(
            term="programming languages",
            top_k=3,
        )

        assert results is not None
        assert len(results) <= 3
        assert all("similarity_score" in r for r in results)
        assert all("text" in r for r in results)

    def test_search_relevance(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that search returns relevant results in order."""
        store = client.save(
            partition="relevance_test",
            collection=sample_collection,
        )

        results = store.search(
            term="dog",
            top_k=2,
        )

        assert results is not None
        assert len(results) == 2
        # Results should be sorted by similarity
        assert results[0]["similarity_score"] >= results[1]["similarity_score"]
        # Should contain references to dogs
        assert any("dog" in r["text"].lower() for r in results)

    def test_search_top_k_limit(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that top_k parameter limits results."""
        store = client.save(
            partition="topk_test",
            collection=sample_collection,
        )

        for k in [1, 2, 3, 5]:
            results = store.search(
                term="technology",
                top_k=k,
            )
            assert results is not None
            assert len(results) <= k

    def test_search_temporary_collection(self, client: Client) -> None:
        """Test searching with a temporary (non-cached) collection."""
        temp_collection = [
            {"text": "cats are popular pets", "type": "animal"},
            {"text": "dogs are loyal companions", "type": "animal"},
            {"text": "birds can fly in the sky", "type": "animal"},
        ]

        store = client.save(
            partition="temp_partition",
            collection=temp_collection,  # type: ignore
            cache=False,
        )

        results = store.search(
            term="pet animals",
            top_k=2,
        )

        assert results is not None
        assert len(results) <= 2

    def test_search_with_different_algorithms(
        self, sample_collection: list[dict[str, str]], temp_cache_dirs: tuple[str, str]
    ) -> None:
        """Test searching with different similarity algorithms."""
        model_cache, vector_cache = temp_cache_dirs
        algorithms: list = ["cosine", "dot", "euclidean"]  # type: ignore

        for algo in algorithms:
            # Create client with specific algorithm
            test_client = Client(
                model_cache=model_cache,
                vector_cache=vector_cache,
                search_algo=algo,  # type: ignore
            )

            store = test_client.save(
                partition=f"algo_test_{algo}",
                collection=sample_collection,
            )

            results = store.search(
                term="programming",
                top_k=3,
            )

            assert results is not None
            assert len(results) > 0

    def test_search_cached_partition_persists(
        self,
        client: Client,
        sample_collection: list[dict[str, str]],
        temp_cache_dirs: tuple[str, str],
    ) -> None:
        """Test that cached partitions persist across client instances."""
        _, vector_cache = temp_cache_dirs

        # Save with first client
        client.save(
            partition="persistent_test",
            collection=sample_collection,
            cache=True,  # Persist to disk
        )

        # Create new client instance with same cache directory AND same model
        new_client = Client(
            model_cache=client.model_cache,
            vector_cache=vector_cache,
            embedding_model=client.embedding_model,  # Use same model to avoid dimension mismatch
        )

        # Load the existing partition by calling save with no collection
        store = new_client.save(
            partition="persistent_test",
            collection=[],  # Empty collection loads existing cache
            cache=True,  # Load from cache
        )

        # Should be able to search the loaded partition
        results = store.search(
            term="programming",
            top_k=2,
        )

        assert results is not None
        assert len(results) > 0

    def test_search_empty_term_returns_none(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that searching with empty term returns empty list."""
        store = client.save(
            partition="empty_term_test",
            collection=sample_collection,
        )

        results = store.search(
            term="",
        )

        assert results == []

    def test_search_jurisdiction_collection(self, client: Client) -> None:
        """Test searching jurisdiction data by name."""
        collection = [
            {
                "jurisdictionName": "AFGHANISTAN",
                "jurType": "COUNTRY",
                "countryJurisdictionId": None,
                "countryName": None,
                "stateJurisdictionId": None,
                "stateName": None,
                "hasImpositionIndicator": True,
                "jurisdictionId": 80334,
            },
            {
                "jurisdictionName": "ALAND ISLANDS",
                "jurType": "COUNTRY",
                "countryJurisdictionId": None,
                "countryName": None,
                "stateJurisdictionId": None,
                "stateName": None,
                "hasImpositionIndicator": True,
                "jurisdictionId": 80335,
            },
        ]

        store = client.save(
            partition="Country",
            collection=collection,
            key="jurisdictionName",
        )

        results = store.search(
            term="US",
            top_k=5,
        )

        assert results is not None
        assert len(results) <= 5
        # Verify all required fields are present
        for result in results:
            assert "similarity_score" in result
            assert "jurisdictionName" in result
            assert "jurisdictionId" in result
            assert "jurType" in result


class TestClientEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_save_empty_collection(self, client: Client) -> None:
        """Test saving an empty collection."""
        store = client.save(
            partition="empty_collection",
            collection=[],
        )
        assert store.size == 0

    def test_partition_normalization(
        self,
        client: Client,
        sample_collection: list[dict[str, str]],
        temp_cache_dirs: tuple[str, str],
    ) -> None:
        """Test that partition names are normalized (lowercase, underscores)."""
        _, vector_cache = temp_cache_dirs

        client.save(
            partition="Test Partition Name",
            collection=sample_collection,
            cache=True,  # Persist to disk
        )

        # Should create file with normalized name
        expected_file = Path(vector_cache) / "test_partition_name.pickle.gz"
        assert expected_file.exists()

    def test_search_with_collection_and_cache(self, client: Client) -> None:
        """Test searching with both collection and cache=True."""
        collection = [
            {"text": "first document"},
            {"text": "second document"},
        ]

        # Should save the collection when cache=True
        store = client.save(
            partition="cache_test",
            collection=collection,  # type: ignore
            cache=True,
        )

        results = store.search(
            term="document",
        )

        assert results is not None

        # Should be able to load and search again
        store2 = client.save(
            partition="cache_test",
            collection=[],  # Empty collection loads existing cache
            cache=True,  # Load from cache
        )

        results2 = store2.search(
            term="document",
        )

        assert results2 is not None


class TestClientIntegration:
    """Integration tests for full workflows."""

    def test_full_workflow(self, client: Client) -> None:
        """Test complete save and search workflow."""
        # Create collection
        collection = [
            {"text": "Neural networks are powerful machine learning models"},
            {"text": "Deep learning requires large datasets"},
            {"text": "Python is great for data science"},
            {"text": "JavaScript runs in web browsers"},
            {"text": "Machine learning transforms industries"},
        ]

        # Save collection and get store
        store = client.save(
            partition="ml_docs",
            collection=collection,
        )
        assert store.size == len(collection)

        # Search for ML-related content
        ml_results = store.search(
            term="artificial intelligence and machine learning",
            top_k=3,
        )

        assert ml_results is not None
        assert len(ml_results) <= 3
        # Should find ML-related documents
        assert any("learning" in r["text"].lower() for r in ml_results)

        # Search for programming content
        prog_results = store.search(
            term="programming languages",
            top_k=2,
        )

        assert prog_results is not None
        assert len(prog_results) <= 2

    def test_multiple_partitions(self, client: Client) -> None:
        """Test working with multiple partitions."""
        animals = [
            {"text": "cats meow"},
            {"text": "dogs bark"},
        ]
        tech = [
            {"text": "Python programming"},
            {"text": "JavaScript coding"},
        ]

        # Save to different partitions
        animal_store = client.save(partition="animals", collection=animals)
        tech_store = client.save(partition="tech", collection=tech)

        # Search each partition
        animal_results = animal_store.search(
            term="pet sounds",
            top_k=2,
        )
        tech_results = tech_store.search(
            term="software development",
            top_k=2,
        )

        assert animal_results is not None
        assert tech_results is not None
        assert len(animal_results) <= 2
        assert len(tech_results) <= 2
