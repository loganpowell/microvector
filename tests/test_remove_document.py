"""Tests for Store.remove_document() with both index and document-based removal."""

import pytest
import numpy as np
from microvector.store import Store


def test_remove_by_index():
    """Test removing a document by integer index."""
    collection = [
        {"text": "first document"},
        {"text": "second document"},
        {"text": "third document"},
    ]

    store = Store(collection=collection)

    # Verify initial size
    assert len(store.collection) == 3
    assert store.vectors is not None
    assert store.vectors.shape[0] == 3

    # Remove middle document by index
    result = store.remove_document(1)

    assert result is True
    assert len(store.collection) == 2
    assert store.vectors.shape[0] == 2
    assert store.collection[0]["text"] == "first document"
    assert store.collection[1]["text"] == "third document"


def test_remove_by_document_dict():
    """Test removing a document by providing the actual document (dict)."""
    doc1 = {"text": "first document", "id": 1}
    doc2 = {"text": "second document", "id": 2}
    doc3 = {"text": "third document", "id": 3}
    collection = [doc1, doc2, doc3]

    store = Store(collection=collection)

    # Remove by document reference
    result = store.remove_document(doc2)

    assert result is True
    assert len(store.collection) == 2
    assert store.vectors is not None
    assert store.vectors.shape[0] == 2
    assert doc2 not in store.collection
    assert store.collection[0] == doc1
    assert store.collection[1] == doc3


def test_remove_by_document_string():
    """Test removing a document when collection contains strings."""
    collection = ["first doc", "second doc", "third doc"]

    store = Store(collection=collection)

    # Remove by string value
    result = store.remove_document("second doc")

    assert result is True
    assert len(store.collection) == 2
    assert store.vectors is not None
    assert store.vectors.shape[0] == 2
    assert "second doc" not in store.collection
    assert store.collection == ["first doc", "third doc"]


def test_remove_nonexistent_document():
    """Test that removing a non-existent document returns False."""
    collection = [
        {"text": "first document"},
        {"text": "second document"},
    ]

    store = Store(collection=collection)

    # Try to remove a document that doesn't exist
    result = store.remove_document({"text": "nonexistent"})

    assert result is False
    assert len(store.collection) == 2  # Collection unchanged


def test_remove_invalid_index():
    """Test that removing with an invalid index raises IndexError."""
    collection = [
        {"text": "first document"},
        {"text": "second document"},
    ]

    store = Store(collection=collection)

    # Try to remove with out-of-range index
    with pytest.raises(IndexError, match="Index 5 out of range"):
        store.remove_document(5)

    # Try with negative out-of-range index
    with pytest.raises(IndexError, match="Index -1 out of range"):
        store.remove_document(-1)


def test_remove_all_documents_sequentially():
    """Test removing all documents one by one."""
    collection = [
        {"text": "doc1"},
        {"text": "doc2"},
        {"text": "doc3"},
    ]

    store = Store(collection=collection)

    # Remove all documents by index (always remove index 0)
    store.remove_document(0)
    assert len(store.collection) == 2

    store.remove_document(0)
    assert len(store.collection) == 1

    store.remove_document(0)
    assert len(store.collection) == 0
    assert store.vectors is not None
    assert store.vectors.shape[0] == 0


def test_remove_by_document_with_duplicates():
    """Test that remove_document only removes the first occurrence."""
    collection = [
        {"text": "duplicate"},
        {"text": "unique"},
        {"text": "duplicate"},
    ]

    store = Store(collection=collection)

    # Remove first occurrence of duplicate
    result = store.remove_document({"text": "duplicate"})

    assert result is True
    assert len(store.collection) == 2
    assert store.collection[0]["text"] == "unique"
    assert store.collection[1]["text"] == "duplicate"


def test_remove_preserves_query_functionality():
    """Test that removal doesn't break query functionality."""
    collection = [
        {"text": "python programming"},
        {"text": "javascript coding"},
        {"text": "java development"},
    ]

    store = Store(collection=collection)

    # Remove middle document
    store.remove_document(1)

    # Query should still work
    results = store.query("programming languages", top_k=2)

    assert len(results) == 2
    assert all("similarity_score" in r for r in results)
    # Should only return the remaining documents
    assert all(r["text"] in ["python programming", "java development"] for r in results)


def test_remove_and_add_cycle():
    """Test removing and adding documents in cycles."""
    initial = [{"text": "doc1"}, {"text": "doc2"}]

    store = Store(collection=initial)
    assert len(store.collection) == 2

    # Remove one
    store.remove_document(0)
    assert len(store.collection) == 1

    # Add one back
    store.add({"text": "doc3"})
    assert len(store.collection) == 2
    assert store.collection[1]["text"] == "doc3"

    # Remove by document
    store.remove_document({"text": "doc2"})
    assert len(store.collection) == 1
    assert store.collection[0]["text"] == "doc3"
