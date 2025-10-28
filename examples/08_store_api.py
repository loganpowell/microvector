"""
Store API Example

Demonstrates the lower-level Store class for advanced use cases:
- Direct vector store manipulation
- Custom embedding functions
- In-memory vector operations without Client abstraction
"""

from microvector.store import Store
import numpy as np


def main():
    print("Store API - Advanced Usage")
    print("=" * 60)

    # Example 1: Basic Store initialization
    print("\nExample 1: Basic Store with simple strings")
    print("-" * 60)

    documents = [
        "Python is a programming language",
        "JavaScript runs in browsers",
        "Machine learning requires data",
    ]

    # Create a store with default settings
    store = Store(collection=documents)

    print(f"✓ Created store with {len(store.collection)} documents")
    print(f"✓ Vectors shape: {store.vectors.shape}")
    print(f"✓ Embedding dimension: {store.vectors.shape[1]}")

    # Search the store
    results = store.query("web development", top_k=2)
    print(f"\nSearch results for 'web development':")
    for doc, score in results:
        print(f"  Score: {score:.4f} | Document: {doc}")

    # Example 2: Store with dictionary documents
    print("\n\nExample 2: Store with dictionary documents")
    print("-" * 60)

    dict_documents = [
        {"text": "The quick brown fox", "category": "animals"},
        {"text": "Python programming tutorial", "category": "tech"},
        {"text": "Machine learning basics", "category": "ai"},
    ]

    store2 = Store(collection=dict_documents, key="text")

    results = store2.query("coding tutorial", top_k=2)
    print(f"\nSearch results for 'coding tutorial':")
    for doc, score in results:
        print(f"  Score: {score:.4f}")
        print(f"  Text: {doc['text']}")
        print(f"  Category: {doc['category']}")

    # Example 3: Different similarity algorithms
    print("\n\nExample 3: Comparing similarity algorithms")
    print("-" * 60)

    test_docs = ["cats and dogs", "programming languages", "machine learning models"]

    query = "pets animals"

    for algo in ["cosine", "dot", "euclidean"]:
        store_algo = Store(collection=test_docs, algo=algo)  # type: ignore
        results = store_algo.query(query, top_k=1)
        top_doc, top_score = results[0]
        print(f"{algo:12} | Score: {top_score:8.4f} | Doc: {top_doc}")

    # Example 4: Custom embedding function
    print("\n\nExample 4: Custom embedding function")
    print("-" * 60)

    def simple_random_embeddings(documents):
        """Simple random embeddings for demonstration."""
        # In practice, you'd use a real embedding model
        return [np.random.rand(128).astype(np.float32) for _ in documents]

    store_custom = Store(
        collection=["doc1", "doc2", "doc3"],
        embedding_function=simple_random_embeddings,  # type: ignore
    )

    print(f"✓ Created store with custom embeddings")
    print(f"✓ Vectors shape: {store_custom.vectors.shape}")
    print(f"✓ Custom dimension: {store_custom.vectors.shape[1]}")

    # Example 5: Adding documents to existing store
    print("\n\nExample 5: Extending a store")
    print("-" * 60)

    initial_docs = ["first document", "second document"]
    store5 = Store(collection=initial_docs)
    print(f"Initial store size: {len(store5.collection)} documents")

    # Add more documents
    additional_docs = ["third document", "fourth document"]
    store5.add_vectors(additional_docs)
    print(f"After adding: {len(store5.collection)} documents")
    print(f"New vectors shape: {store5.vectors.shape}")

    # Example 6: Empty store initialization
    print("\n\nExample 6: Empty store")
    print("-" * 60)

    empty_store = Store()
    print(f"Empty store collection: {empty_store.collection}")
    print(f"Empty store vectors: {empty_store.vectors}")

    # Add documents later
    empty_store.add_vectors(["first doc", "second doc"])
    print(f"After adding: {len(empty_store.collection)} documents")

    print("\n" + "=" * 60)
    print("Summary: Store API provides:")
    print("  • Direct vector manipulation")
    print("  • Custom embedding functions")
    print("  • Different similarity metrics")
    print("  • In-memory operations")
    print("  • Lower-level control vs Client API")


if __name__ == "__main__":
    main()
