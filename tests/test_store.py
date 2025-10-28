"""
Test suite for microvector Store class.
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from microvector.store import Store, unpack_results


class TestUnpackResults:
    """Tests for unpack_results utility function."""

    def test_unpack_results_basic(self):
        """Test unpacking results with basic documents."""
        results = [
            ({"text": "first document"}, np.float32(0.95)),
            ({"text": "second document"}, np.float32(0.80)),
        ]
        unpacked = unpack_results(results)  # type: ignore

        assert len(unpacked) == 2
        assert unpacked[0]["text"] == "first document"
        assert (
            abs(unpacked[0]["similarity_score"] - 0.95) < 0.01
        )  # Allow for floating point precision
        assert unpacked[1]["text"] == "second document"
        assert abs(unpacked[1]["similarity_score"] - 0.80) < 0.01

    def test_unpack_results_with_metadata(self):
        """Test unpacking results with complex documents."""
        results = [
            ({"text": "doc", "meta": {"source": "test"}}, np.float32(0.75)),
        ]
        unpacked = unpack_results(results)  # type: ignore

        assert unpacked[0]["text"] == "doc"
        assert unpacked[0]["meta"]["source"] == "test"
        assert unpacked[0]["similarity_score"] == 0.75


class TestStoreInitialization:
    """Tests for Store initialization."""

    def test_store_init_empty(self):
        """Test initializing an empty Store."""
        store = Store()
        assert store.collection == []
        assert store.vectors is None

    def test_store_init_with_collection(self):
        """Test initializing Store with a collection."""
        collection = ["doc1", "doc2", "doc3"]
        store = Store(collection=collection)

        assert len(store.collection) == 3
        assert store.vectors is not None
        assert store.vectors.shape[0] == 3

    def test_store_init_with_dict_collection(self):
        """Test initializing Store with dictionary collection."""
        collection = [
            {"text": "first doc"},
            {"text": "second doc"},
        ]
        store = Store(collection=collection, key="text")

        assert len(store.collection) == 2
        assert store.vectors is not None
        assert store.vectors.shape[0] == 2

    def test_store_init_with_custom_embedding_function(self):
        """Test initializing Store with custom embedding function."""

        def custom_embeddings(docs):  # type: ignore
            # Return random embeddings for testing
            return [np.random.rand(128).astype(np.float32) for _ in docs]  # type: ignore

        collection = ["doc1", "doc2"]
        store = Store(collection=collection, embedding_function=custom_embeddings)  # type: ignore

        assert len(store.collection) == 2
        assert store.vectors is not None
        assert store.vectors.shape == (2, 128)

    def test_store_init_with_different_algos(self):
        """Test initializing Store with different similarity algorithms."""
        collection = ["doc1", "doc2"]

        for algo in ["cosine", "dot", "euclidean", "derrida"]:
            store = Store(collection=collection, algo=algo)  # type: ignore
            assert store.collection == collection
            assert store.vectors is not None

    def test_store_init_invalid_algo_raises_error(self):
        """Test that invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Similarity metric not supported"):
            Store(collection=["doc"], algo="invalid_algo")  # type: ignore


class TestStoreAddOperations:
    """Tests for adding documents to Store."""

    def test_add_single_document(self):
        """Test adding a single document."""
        store = Store()
        store.add("new document")

        assert len(store.collection) == 1
        assert store.collection[0] == "new document"
        assert store.vectors is not None
        assert store.vectors.shape[0] == 1

    def test_add_multiple_documents(self):
        """Test adding multiple documents at once."""
        store = Store()
        docs = ["doc1", "doc2", "doc3"]
        store.add(docs)

        assert len(store.collection) == 3
        assert store.vectors is not None
        assert store.vectors.shape[0] == 3

    def test_add_document_to_existing_store(self):
        """Test adding documents to existing Store."""
        store = Store(collection=["initial doc"])
        initial_count = len(store.collection)

        store.add("new doc")

        assert len(store.collection) == initial_count + 1
        assert store.vectors is not None
        assert store.vectors.shape[0] == initial_count + 1

    def test_add_collection_incremental(self):
        """Test adding multiple collections incrementally."""
        store = Store()

        store.add_collection(["doc1", "doc2"])
        assert len(store.collection) == 2

        store.add_collection(["doc3", "doc4"])
        assert len(store.collection) == 4


class TestStoreRemoveOperations:
    """Tests for removing documents from Store."""

    def test_remove_document(self):
        """Test removing a document by index."""
        store = Store(collection=["doc1", "doc2", "doc3"])
        initial_count = len(store.collection)

        store.remove_document(1)

        assert len(store.collection) == initial_count - 1
        assert "doc2" not in store.collection
        assert store.vectors is not None
        assert store.vectors.shape[0] == initial_count - 1

    def test_remove_first_document(self):
        """Test removing the first document."""
        store = Store(collection=["doc1", "doc2", "doc3"])
        store.remove_document(0)

        assert store.collection[0] == "doc2"
        assert len(store.collection) == 2

    def test_remove_last_document(self):
        """Test removing the last document."""
        store = Store(collection=["doc1", "doc2", "doc3"])
        store.remove_document(2)

        assert len(store.collection) == 2
        assert "doc3" not in store.collection


class TestStorePersistence:
    """Tests for saving and loading Store."""

    def test_save_and_load_pickle(self):
        """Test saving and loading Store as pickle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test_store.pickle")

            # Create and save store
            original_store = Store(collection=["doc1", "doc2", "doc3"])
            original_store.save(filepath)

            # Load into new store
            loaded_store = Store()
            loaded_store.load(filepath)

            assert len(loaded_store.collection) == len(original_store.collection)
            assert loaded_store.collection == original_store.collection
            assert loaded_store.vectors is not None
            assert np.array_equal(loaded_store.vectors, original_store.vectors)  # type: ignore

    def test_save_and_load_gzip(self):
        """Test saving and loading Store as gzipped pickle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test_store.pickle.gz")

            # Create and save store
            collection = [
                {"text": "first doc", "meta": "data1"},
                {"text": "second doc", "meta": "data2"},
            ]
            original_store = Store(collection=collection, key="text")
            original_store.save(filepath)

            # Load into new store
            loaded_store = Store(key="text")
            loaded_store.load(filepath)

            assert len(loaded_store.collection) == len(original_store.collection)
            assert loaded_store.collection == original_store.collection
            assert loaded_store.vectors is not None
            assert np.array_equal(loaded_store.vectors, original_store.vectors)  # type: ignore

    def test_save_creates_file(self):
        """Test that save actually creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.pickle"

            store = Store(collection=["doc"])
            store.save(str(filepath))

            assert filepath.exists()


class TestStoreQuery:
    """Tests for querying Store."""

    def test_query_returns_results(self):
        """Test basic query functionality."""
        collection = [
            {"text": "dogs are loyal pets"},
            {"text": "cats are independent"},
            {"text": "birds can fly"},
        ]
        store = Store(collection=collection, key="text")

        results = store.query("pet animals", top_k=2)

        assert len(results) <= 2
        assert all("similarity_score" in r for r in results)
        assert all("text" in r for r in results)

    def test_query_top_k_limit(self):
        """Test that top_k limits number of results."""
        collection = [f"document {i}" for i in range(10)]
        store = Store(collection=collection)

        for k in [1, 3, 5]:
            results = store.query("document", top_k=k)
            assert len(results) == k

    def test_query_results_sorted(self):
        """Test that results are sorted by similarity."""
        collection = [
            {"text": "machine learning algorithms"},
            {"text": "deep neural networks"},
            {"text": "cooking recipes"},
        ]
        store = Store(collection=collection, key="text")

        results = store.query("artificial intelligence", top_k=3)

        # Results should be in descending order of similarity
        for i in range(len(results) - 1):
            assert results[i]["similarity_score"] >= results[i + 1]["similarity_score"]

    def test_query_empty_store_raises_error(self):
        """Test querying empty Store raises ValueError."""
        store = Store()

        with pytest.raises(ValueError, match="No vectors available"):
            store.query("test query")

    def test_query_with_different_algos(self):
        """Test querying with different similarity algorithms."""
        collection = ["doc1", "doc2", "doc3"]

        for algo in ["cosine", "dot", "euclidean"]:
            store = Store(collection=collection, algo=algo)  # type: ignore
            results = store.query("doc", top_k=2)
            assert len(results) == 2


class TestStoreToDict:
    """Tests for Store.to_dict() method."""

    def test_to_dict_without_vectors(self):
        """Test converting Store to dict without vectors."""
        collection = ["doc1", "doc2"]
        store = Store(collection=collection)

        dict_repr = store.to_dict(vectors=False)

        assert len(dict_repr) == 2
        assert all("document" in item for item in dict_repr)
        assert all("index" in item for item in dict_repr)
        assert all("vector" not in item for item in dict_repr)

    def test_to_dict_with_vectors(self):
        """Test converting Store to dict with vectors."""
        collection = ["doc1", "doc2"]
        store = Store(collection=collection)

        dict_repr = store.to_dict(vectors=True)

        assert len(dict_repr) == 2
        assert all("document" in item for item in dict_repr)
        assert all("index" in item for item in dict_repr)
        assert all("vector" in item for item in dict_repr)
        # Check that vectors are lists and have the expected structure
        for item in dict_repr:
            assert isinstance(item["vector"], list)
            assert len(item["vector"]) > 0  # type: ignore  # Vector should have some dimensions

    def test_to_dict_indices_correct(self):
        """Test that indices in dict representation are correct."""
        collection = ["doc1", "doc2", "doc3"]
        store = Store(collection=collection)

        dict_repr = store.to_dict()

        for i, item in enumerate(dict_repr):
            assert item["index"] == i
            assert item["document"] == collection[i]
