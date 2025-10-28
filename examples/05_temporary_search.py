"""
Temporary Search Example

Demonstrates searching without persisting to disk:
- Use cache=False to avoid saving to disk
- Useful for one-time searches or testing
- Collection is provided directly in the search call
"""

from microvector import Client


def main():
    client = Client()

    # Create a temporary collection (not saved to disk)
    temp_documents = [
        {"text": "cats are popular pets", "type": "animal", "popularity": "high"},
        {"text": "dogs are loyal companions", "type": "animal", "popularity": "high"},
        {"text": "birds can fly in the sky", "type": "animal", "popularity": "medium"},
        {"text": "fish live underwater", "type": "animal", "popularity": "medium"},
        {"text": "rabbits are gentle creatures", "type": "animal", "popularity": "low"},
    ]

    print("Searching temporary collection (not cached to disk)...")
    print("-" * 60)

    # Search without caching
    # The collection is provided in the search call itself
    results = client.search(
        term="pet animals",
        partition="temp_partition",  # Name doesn't matter for temporary searches
        key="text",
        top_k=3,
        collection=temp_documents,  # type: ignore
        cache=False,  # Don't save to disk
    )

    print(f"\nFound {len(results)} most relevant results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity_score']:.4f}")
        print(f"   Text: {result['text']}")
        print(f"   Type: {result['type']}")
        print(f"   Popularity: {result['popularity']}")

    # Another search on the same temporary collection
    print("\n" + "=" * 60)
    print("\nSearching for 'flying creatures'...")
    print("-" * 60)

    results = client.search(
        term="flying creatures",
        partition="temp_partition",
        key="text",
        top_k=2,
        collection=temp_documents,  # type: ignore
        cache=False,
    )

    print(f"\nFound {len(results)} most relevant results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity_score']:.4f}")
        print(f"   Text: {result['text']}")

    print("\n" + "=" * 60)
    print("\nNote: These searches were performed without creating any")
    print("cached files on disk. Useful for:")
    print("  • One-time searches")
    print("  • Testing queries")
    print("  • Dynamic collections")
    print("  • When you don't need persistence")


if __name__ == "__main__":
    main()
