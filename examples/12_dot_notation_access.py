"""
Dot Notation for Nested Keys Example

Demonstrates using dot notation to access nested fields in documents:
- Use "parent.child" notation in the 'key' parameter
- Vectorize deeply nested fields
- Search across nested document structures
"""

from microvector import Client


def main():
    print("Dot Notation for Nested Keys")
    print("=" * 60)

    client = Client()

    # Example 1: Basic nested field access
    print("\nExample 1: Vectorizing Nested Author Field")
    print("-" * 60)

    documents = [
        {
            "title": "Introduction to Python",
            "metadata": {
                "author": "Alice Smith",
                "year": 2024,
                "category": "programming",
            },
        },
        {
            "title": "Advanced JavaScript Techniques",
            "metadata": {
                "author": "Bob Johnson",
                "year": 2024,
                "category": "web development",
            },
        },
        {
            "title": "Machine Learning Basics",
            "metadata": {"author": "Charlie Brown", "year": 2023, "category": "AI"},
        },
    ]

    # Use dot notation to vectorize the nested 'author' field
    client.save(
        partition="nested_authors",
        collection=documents,  # type: ignore
        key="metadata.author",  # Dot notation for nested field!
    )

    print("✓ Saved documents using 'metadata.author' as the vectorization key")

    # Search by author name similarity
    results = client.search(
        term="Alice",
        partition="nested_authors",
        key="metadata.author",
        top_k=2,
    )

    print(f"\nSearch results for 'Alice':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Author: {result['metadata']['author']}")
        print(f"   Year: {result['metadata']['year']}")
        print(f"   Similarity: {result['similarity_score']:.4f}")

    # Example 2: Deeper nesting
    print("\n\n" + "=" * 60)
    print("Example 2: Multi-level Nested Fields")
    print("-" * 60)

    deep_docs = [
        {
            "id": "doc1",
            "content": {
                "metadata": {
                    "tags": {"primary": "python programming language tutorial"}
                }
            },
        },
        {
            "id": "doc2",
            "content": {
                "metadata": {
                    "tags": {"primary": "javascript web development framework"}
                }
            },
        },
        {
            "id": "doc3",
            "content": {
                "metadata": {
                    "tags": {"primary": "machine learning deep neural networks"}
                }
            },
        },
    ]

    # Use dot notation for deeply nested field
    client.save(
        partition="deep_nested",
        collection=deep_docs,  # type: ignore
        key="content.metadata.tags.primary",  # Multi-level dot notation!
    )

    print("✓ Saved documents using 'content.metadata.tags.primary' as key")

    results = client.search(
        term="web development",
        partition="deep_nested",
        key="content.metadata.tags.primary",
        top_k=2,
    )

    print(f"\nSearch results for 'web development':")
    for i, result in enumerate(results, 1):
        primary_tag = result["content"]["metadata"]["tags"]["primary"]
        print(f"\n{i}. ID: {result['id']}")
        print(f"   Primary tag: {primary_tag}")
        print(f"   Similarity: {result['similarity_score']:.4f}")

    # Example 3: Different nested fields in same collection
    print("\n\n" + "=" * 60)
    print("Example 3: Switching Between Nested Fields")
    print("-" * 60)

    products = [
        {
            "name": "Laptop Pro",
            "specs": {"description": "High-performance laptop with 16GB RAM"},
            "reviews": {"summary": "Excellent build quality and fast processor"},
        },
        {
            "name": "Wireless Mouse",
            "specs": {
                "description": "Ergonomic wireless mouse with precision tracking"
            },
            "reviews": {"summary": "Very comfortable and responsive"},
        },
    ]

    # Save and search using specs.description
    client.save(
        partition="product_specs",
        collection=products,  # type: ignore
        key="specs.description",
    )

    print("Searching by product specifications...")
    results = client.search(
        term="laptop computer",
        partition="product_specs",
        key="specs.description",
        top_k=1,
    )

    for result in results:
        print(f"  {result['name']}: {result['specs']['description']}")
        print(f"  Similarity: {result['similarity_score']:.4f}")

    # Save and search using reviews.summary
    client.save(
        partition="product_reviews",
        collection=products,  # type: ignore
        key="reviews.summary",
    )

    print("\nSearching by product reviews...")
    results = client.search(
        term="comfortable ergonomic",
        partition="product_reviews",
        key="reviews.summary",
        top_k=1,
    )

    for result in results:
        print(f"  {result['name']}: {result['reviews']['summary']}")
        print(f"  Similarity: {result['similarity_score']:.4f}")

    # Example 4: Practical use case - Blog posts
    print("\n\n" + "=" * 60)
    print("Example 4: Blog Posts with Nested Author Info")
    print("-" * 60)

    blog_posts = [
        {
            "title": "Getting Started with Python",
            "author": {
                "name": "Dr. Sarah Johnson",
                "bio": "AI researcher specializing in machine learning and Python",
            },
            "content": "Python is a versatile programming language...",
        },
        {
            "title": "Web Development Best Practices",
            "author": {
                "name": "Mike Developer",
                "bio": "Full-stack web developer with expertise in JavaScript frameworks",
            },
            "content": "Modern web development requires...",
        },
        {
            "title": "Deep Learning Tutorial",
            "author": {
                "name": "Dr. Sarah Johnson",
                "bio": "AI researcher specializing in machine learning and Python",
            },
            "content": "Neural networks are powerful tools...",
        },
    ]

    # Find posts by similar author bio
    client.save(
        partition="blog_authors",
        collection=blog_posts,  # type: ignore
        key="author.bio",
    )

    print("Finding posts by authors with AI/ML background...")
    results = client.search(
        term="artificial intelligence machine learning researcher",
        partition="blog_authors",
        key="author.bio",
        top_k=3,
    )

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Author: {result['author']['name']}")
        print(f"   Bio: {result['author']['bio']}")
        print(f"   Similarity: {result['similarity_score']:.4f}")

    print("\n" + "=" * 60)
    print("Summary:")
    print("  • Use dot notation like 'parent.child' in the key parameter")
    print("  • Works with any nesting depth: 'a.b.c.d'")
    print("  • Allows vectorizing specific nested fields")
    print("  • Great for structured documents with metadata")
    print("  • Each partition can use a different nested key")


if __name__ == "__main__":
    main()
