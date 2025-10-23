"""
Test suite for microvector Client API.
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from microvector import Client
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
    cache_models, cache_vectors = temp_cache_dirs
    return Client(
        cache_models=cache_models,
        cache_vectors=cache_vectors,
        embedding_model=EMBEDDING_MODEL,
    )


class TestClientInitialization:
    """Tests for Client initialization."""

    def test_client_init_default_paths(self) -> None:
        """Test client initialization with default paths."""
        client = Client()
        assert client.cache_models == "./.cached_models"
        assert client.cache_vectors == "./.vector_cache"
        assert client.embedding_model == EMBEDDING_MODEL

    def test_client_init_custom_paths(self, temp_cache_dirs: tuple[str, str]) -> None:
        """Test client initialization with custom paths."""
        cache_models, cache_vectors = temp_cache_dirs
        client = Client(
            cache_models=cache_models,
            cache_vectors=cache_vectors,
            embedding_model=EMBEDDING_MODEL,
        )
        assert client.cache_models == cache_models
        assert client.cache_vectors == cache_vectors
        assert os.path.exists(cache_models)
        assert os.path.exists(cache_vectors)

    def test_client_creates_cache_directories(
        self, temp_cache_dirs: tuple[str, str]
    ) -> None:
        """Test that client creates cache directories if they don't exist."""
        cache_models, cache_vectors = temp_cache_dirs
        # Model cache is now session-scoped and already exists
        assert os.path.exists(cache_models)
        # Vector cache should not exist yet
        assert not os.path.exists(cache_vectors)

        Client(cache_models=cache_models, cache_vectors=cache_vectors)

        # Both should exist after Client initialization
        assert os.path.exists(cache_models)
        assert os.path.exists(cache_vectors)


class TestClientSave:
    """Tests for Client.save() method."""

    def test_save_returns_success_info(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that save returns proper status information."""
        result = client.save(
            partition_name="test_partition",
            collection=sample_collection,
        )

        assert result["status"] == "success"
        assert result["partition"] == "test_partition"
        assert result["documents_saved"] == len(sample_collection)
        assert result["key"] == "text"
        assert result["algorithm"] == "cosine"

    def test_save_creates_pickle_file(
        self,
        client: Client,
        sample_collection: list[dict[str, str]],
        temp_cache_dirs: tuple[str, str],
    ) -> None:
        """Test that save creates a pickle file in the cache directory."""
        _, cache_vectors = temp_cache_dirs
        client.save(
            partition_name="test_partition",
            collection=sample_collection,
        )

        expected_file = Path(cache_vectors) / "test_partition.pickle.gz"
        assert expected_file.exists()

    def test_save_with_custom_key(self, client: Client) -> None:
        """Test saving with a custom key field."""
        collection = [
            {"description": "First item", "value": 1},
            {"description": "Second item", "value": 2},
        ]
        result = client.save(
            partition_name="custom_key_test",
            collection=collection,  # type: ignore
            key="description",
        )

        assert result["status"] == "success"
        assert result["key"] == "description"

    def test_save_with_different_algorithms(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test saving with different similarity algorithms."""
        algorithms = ["cosine", "dot", "euclidean", "derrida"]

        for algo in algorithms:
            result = client.save(
                partition_name=f"test_{algo}",
                collection=sample_collection,
                algo=algo,  # type: ignore
            )
            assert result["status"] == "success"
            assert result["algorithm"] == algo


class TestClientSearch:
    """Tests for Client.search() method."""

    def test_search_returns_results(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that search returns relevant results."""
        # First save the collection
        client.save(
            partition_name="search_test",
            collection=sample_collection,
        )

        # Then search
        results = client.search(
            term="programming languages",
            partition_name="search_test",
            key="text",
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
        client.save(
            partition_name="relevance_test",
            collection=sample_collection,
        )

        results = client.search(
            term="dog",
            partition_name="relevance_test",
            key="text",
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
        client.save(
            partition_name="topk_test",
            collection=sample_collection,
        )

        for k in [1, 2, 3, 5]:
            results = client.search(
                term="technology",
                partition_name="topk_test",
                key="text",
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

        results = client.search(
            term="pet animals",
            partition_name="temp_partition",
            key="text",
            top_k=2,
            collection=temp_collection,  # type: ignore
            cache=False,
        )

        assert results is not None
        assert len(results) <= 2

    def test_search_with_different_algorithms(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test searching with different similarity algorithms."""
        algorithms = ["cosine", "dot", "euclidean"]

        for algo in algorithms:
            client.save(
                partition_name=f"algo_test_{algo}",
                collection=sample_collection,
                algo=algo,  # type: ignore
            )

            results = client.search(
                term="programming",
                partition_name=f"algo_test_{algo}",
                key="text",
                top_k=3,
                algo=algo,  # type: ignore
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
        _, cache_vectors = temp_cache_dirs

        # Save with first client
        client.save(
            partition_name="persistent_test",
            collection=sample_collection,
        )

        # Create new client instance with same cache directory AND same model
        new_client = Client(
            cache_models=client.cache_models,
            cache_vectors=cache_vectors,
            embedding_model=client.embedding_model,  # Use same model to avoid dimension mismatch
        )

        # Should be able to search without providing collection again
        results = new_client.search(
            term="programming",
            partition_name="persistent_test",
            key="text",
            top_k=2,
        )

        assert results is not None
        assert len(results) > 0

    def test_search_empty_term_returns_none(
        self, client: Client, sample_collection: list[dict[str, str]]
    ) -> None:
        """Test that searching with empty term returns None."""
        client.save(
            partition_name="empty_term_test",
            collection=sample_collection,
        )

        results = client.search(
            term="",
            partition_name="empty_term_test",
            key="text",
        )

        assert results is None

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

        client.save(
            partition_name="Country",
            collection=collection,
            key="jurisdictionName",
        )

        results = client.search(
            term="US",
            partition_name="Country",
            key="jurisdictionName",
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
        result = client.save(
            partition_name="empty_collection",
            collection=[],
        )
        assert result["status"] == "success"
        assert result["documents_saved"] == 0

    def test_partition_name_normalization(
        self,
        client: Client,
        sample_collection: list[dict[str, str]],
        temp_cache_dirs: tuple[str, str],
    ) -> None:
        """Test that partition names are normalized (lowercase, underscores)."""
        _, cache_vectors = temp_cache_dirs

        client.save(
            partition_name="Test Partition Name",
            collection=sample_collection,
        )

        # Should create file with normalized name
        expected_file = Path(cache_vectors) / "test_partition_name.pickle.gz"
        assert expected_file.exists()

    def test_search_with_collection_and_cache(self, client: Client) -> None:
        """Test searching with both collection and cache=True."""
        collection = [
            {"text": "first document"},
            {"text": "second document"},
        ]

        # Should save the collection when cache=True
        results = client.search(
            term="document",
            partition_name="cache_test",
            key="text",
            collection=collection,  # type: ignore
            cache=True,
        )

        assert results is not None

        # Should be able to search again without collection
        results2 = client.search(
            term="document",
            partition_name="cache_test",
            key="text",
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

        # Save collection
        save_result = client.save(
            partition_name="ml_docs",
            collection=collection,
        )
        assert save_result["status"] == "success"

        # Search for ML-related content
        ml_results = client.search(
            term="artificial intelligence and machine learning",
            partition_name="ml_docs",
            key="text",
            top_k=3,
        )

        assert ml_results is not None
        assert len(ml_results) <= 3
        # Should find ML-related documents
        assert any("learning" in r["text"].lower() for r in ml_results)

        # Search for programming content
        prog_results = client.search(
            term="programming languages",
            partition_name="ml_docs",
            key="text",
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
        client.save(partition_name="animals", collection=animals)
        client.save(partition_name="tech", collection=tech)

        # Search each partition
        animal_results = client.search(
            term="pet sounds",
            partition_name="animals",
            key="text",
            top_k=2,
        )
        tech_results = client.search(
            term="software development",
            partition_name="tech",
            key="text",
            top_k=2,
        )

        assert animal_results is not None
        assert tech_results is not None
        assert len(animal_results) <= 2
        assert len(tech_results) <= 2
