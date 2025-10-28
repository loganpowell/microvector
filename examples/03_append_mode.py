"""
Append Mode Example

Demonstrates the difference between:
- append=False (default): Replace entire collection
- append=True: Add new documents to existing collection
"""

from microvector import Client


def main():
    client = Client()

    # Initial collection
    initial_docs = [
        {"text": "Python is a programming language", "category": "tech"},
        {"text": "JavaScript is used for web development", "category": "tech"},
    ]

    print("Step 1: Save initial collection (append=False)")
    print("-" * 50)
    result = client.save(
        partition="append_demo",
        collection=initial_docs,
        key="text",
        append=False,  # This is the default - replaces any existing data
    )
    print(f"✓ Saved {result['documents_saved']} documents")

    # Search to verify initial state
    results = client.search(
        term="programming",
        partition="append_demo",
        key="text",
        top_k=5,
    )
    print(f"✓ Collection has {len(results)} documents\n")

    # Add more documents with append=True
    additional_docs = [
        {"text": "Ruby is an elegant programming language", "category": "tech"},
        {"text": "Go is great for concurrent programming", "category": "tech"},
    ]

    print("Step 2: Add more documents (append=True)")
    print("-" * 50)
    result = client.save(
        partition="append_demo",
        collection=additional_docs,
        key="text",
        append=True,  # This adds to the existing collection
    )
    print(f"✓ Added {result['documents_saved']} documents")

    # Search to verify documents were appended
    results = client.search(
        term="programming",
        partition="append_demo",
        key="text",
        top_k=5,
    )
    print(f"✓ Collection now has {len(results)} documents")
    print("\nAll documents:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc['text']}")

    # Now demonstrate replace behavior (append=False)
    replacement_docs = [
        {"text": "Machine learning is a subset of AI", "category": "AI"},
        {"text": "Deep learning uses neural networks", "category": "AI"},
    ]

    print("\n\nStep 3: Replace collection (append=False)")
    print("-" * 50)
    result = client.save(
        partition="append_demo",
        collection=replacement_docs,
        key="text",
        append=False,  # This replaces the entire collection
    )
    print(f"✓ Replaced with {result['documents_saved']} documents")

    # Search to verify replacement
    results = client.search(
        term="AI machine learning",
        partition="append_demo",
        key="text",
        top_k=5,
    )
    print(f"✓ Collection now has {len(results)} documents")
    print("\nCurrent documents:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc['text']}")


if __name__ == "__main__":
    main()
