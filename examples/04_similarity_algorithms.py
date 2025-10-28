"""
Similarity Algorithms Example

Demonstrates different similarity metrics:
- cosine: Cosine similarity (default, good for semantic similarity)
- dot: Dot product (faster, works well with normalized vectors)
- euclidean: Euclidean distance (L2 distance)
- derrida: Derrida distance (specialized metric)
"""

from microvector import Client


def main():
    client = Client()

    # Sample documents
    documents = [
        {"text": "The cat sits on the mat", "id": "1"},
        {"text": "The dog lies on the rug", "id": "2"},
        {"text": "Python programming is fun", "id": "3"},
        {"text": "Machine learning with Python", "id": "4"},
    ]

    # Search query
    search_term = "cat on mat"

    # Test each algorithm
    algorithms = ["cosine", "dot", "euclidean", "derrida"]

    for algo in algorithms:
        print(f"\n{'='*60}")
        print(f"Algorithm: {algo.upper()}")
        print("=" * 60)

        # Save with specific algorithm
        partition_name = f"algo_{algo}"
        result = client.save(
            partition=partition_name,
            collection=documents,
            key="text",
            algo=algo,  # type: ignore
        )
        print(f"✓ Saved {result['documents_saved']} documents using {algo}")

        # Search with the same algorithm
        results = client.search(
            term=search_term,
            partition=partition_name,
            key="text",
            top_k=3,
        )

        # Display results
        print(f"\nTop 3 results for '{search_term}':")
        for i, doc in enumerate(results, 1):
            print(f"  {i}. Score: {doc['similarity_score']:.6f}")
            print(f"     Text: {doc['text']}")
            print(f"     ID: {doc['id']}")

    # Comparison summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    print("\nChoosing the right algorithm:")
    print("• cosine: Best for semantic similarity (default choice)")
    print("• dot: Faster, good for normalized vectors")
    print("• euclidean: Measures absolute distance between vectors")
    print("• derrida: Specialized distance metric")


if __name__ == "__main__":
    main()
