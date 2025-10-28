"""
Custom Key Fields Example

Demonstrates using different fields for vectorization:
- Default is "text" field
- You can specify any field name with the 'key' parameter
- Useful when your documents have custom structures
"""

from microvector import Client


def main():
    client = Client()

    # Example 1: Product descriptions
    print("Example 1: E-commerce Products")
    print("=" * 60)

    products = [
        {
            "name": "Laptop",
            "description": "High-performance laptop with 16GB RAM and SSD",
            "category": "Electronics",
            "price": 999,
        },
        {
            "name": "Mouse",
            "description": "Wireless ergonomic mouse with precision tracking",
            "category": "Electronics",
            "price": 29,
        },
        {
            "name": "Keyboard",
            "description": "Mechanical keyboard with RGB backlighting",
            "category": "Electronics",
            "price": 79,
        },
    ]

    # Save using "description" field instead of "text"
    client.save(
        partition="products",
        collection=products,  # type: ignore
        key="description",  # Vectorize the description field
    )

    # Search using the same key
    results = client.search(
        term="computer peripherals",
        partition="products",
        key="description",
        top_k=2,
    )

    print("\nSearch results for 'computer peripherals':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']} - ${result['price']}")
        print(f"   Description: {result['description']}")
        print(f"   Similarity: {result['similarity_score']:.4f}")

    # Example 2: Blog posts with titles
    print("\n\n" + "=" * 60)
    print("Example 2: Blog Posts (using title field)")
    print("=" * 60)

    blog_posts = [
        {
            "title": "Introduction to Machine Learning",
            "author": "Alice",
            "tags": ["AI", "ML", "Python"],
        },
        {
            "title": "Web Development Best Practices",
            "author": "Bob",
            "tags": ["Web", "JavaScript", "HTML"],
        },
        {
            "title": "Deep Learning with Neural Networks",
            "author": "Charlie",
            "tags": ["AI", "Deep Learning", "TensorFlow"],
        },
    ]

    # Save using "title" field
    client.save(
        partition="blog_posts",
        collection=blog_posts,  # type: ignore
        key="title",  # Vectorize the title field
    )

    # Search using the title key
    results = client.search(
        term="artificial intelligence",
        partition="blog_posts",
        key="title",
        top_k=2,
    )

    print("\nSearch results for 'artificial intelligence':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Author: {result['author']}")
        print(f"   Tags: {', '.join(result['tags'])}")
        print(f"   Similarity: {result['similarity_score']:.4f}")

    # Example 3: Custom nested field (needs preprocessing)
    print("\n\n" + "=" * 60)
    print("Example 3: Documents with Multiple Text Fields")
    print("=" * 60)

    # When you have multiple fields, combine them or choose one
    documents = [
        {
            "headline": "Climate Change Impact",
            "summary": "Study shows rising temperatures affecting ecosystems",
            "combined": "Climate Change Impact Study shows rising temperatures affecting ecosystems",
        },
        {
            "headline": "Tech Startup Raises Funding",
            "summary": "AI company secures $50M in Series B funding",
            "combined": "Tech Startup Raises Funding AI company secures $50M in Series B funding",
        },
    ]

    # Use the combined field for vectorization
    client.save(
        partition="news",
        collection=documents,  # type: ignore
        key="combined",
    )

    results = client.search(
        term="technology investment",
        partition="news",
        key="combined",
        top_k=1,
    )

    print("\nSearch results for 'technology investment':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['headline']}")
        print(f"   Summary: {result['summary']}")
        print(f"   Similarity: {result['similarity_score']:.4f}")


if __name__ == "__main__":
    main()
