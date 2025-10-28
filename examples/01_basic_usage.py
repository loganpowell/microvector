"""
Basic Usage Example

Demonstrates the fundamental operations of microvector:
- Initializing the Client
- Saving a collection
- Searching for similar documents
"""

from microvector import Client


def main():
    # Initialize the client with default settings
    # This will use default cache directories for models and vectors
    client = Client()

    # Create a sample collection of documents
    # Each document is a dictionary with at least a "text" field
    documents = [
        {"text": "The quick brown fox jumps over the lazy dog", "category": "animals"},
        {"text": "Python is a high-level programming language", "category": "tech"},
        {"text": "Machine learning models learn from data", "category": "ai"},
        {"text": "The lazy dog sleeps under the tree", "category": "animals"},
        {"text": "JavaScript is used for web development", "category": "tech"},
    ]

    # Save the collection to a named partition
    # This creates embeddings and persists them to disk
    print("Saving collection...")
    save_result = client.save(
        partition="example_documents",
        collection=documents,
        key="text",  # The field to vectorize (default is "text")
        algo="cosine",  # Similarity metric (default is "cosine")
    )

    print(f"✓ Saved {save_result['documents_saved']} documents")
    print(f"  Partition: {save_result['partition']}")
    print(f"  Algorithm: {save_result['algorithm']}")
    print(f"  Model: {save_result['embedding_model']}")

    # Search for similar documents
    print("\nSearching for 'programming languages'...")
    results = client.search(
        term="programming languages",
        partition="example_documents",
        key="text",
        top_k=3,  # Return top 3 most similar documents
    )

    # Display results
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity_score']:.4f}")
        print(f"   Text: {result['text']}")
        print(f"   Category: {result['category']}")

    # Search with a different query
    print("\n" + "=" * 60)
    print("\nSearching for 'dog'...")
    results = client.search(
        term="dog",
        partition="example_documents",
        key="text",
        top_k=2,
    )

    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity_score']:.4f}")
        print(f"   Text: {result['text']}")
        print(f"   Category: {result['category']}")


if __name__ == "__main__":
    main()
