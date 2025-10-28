"""
Real-World Use Cases

Demonstrates practical applications of microvector:
1. Semantic search over documentation
2. FAQ matching
3. Product recommendation
4. Content deduplication
"""

from microvector import Client


def documentation_search():
    """Example: Semantic search over technical documentation."""
    print("\nUse Case 1: Technical Documentation Search")
    print("=" * 60)

    client = Client()

    # Sample documentation entries
    docs = [
        {
            "title": "Getting Started with Installation",
            "content": "Install microvector using pip install microvector. Requires Python 3.9 or higher.",
            "category": "setup",
        },
        {
            "title": "Saving Your First Collection",
            "content": "Use client.save() to persist document collections with automatic vector generation.",
            "category": "tutorial",
        },
        {
            "title": "Searching Vector Stores",
            "content": "Use client.search() with a query term to find semantically similar documents.",
            "category": "tutorial",
        },
        {
            "title": "Choosing Similarity Metrics",
            "content": "microvector supports cosine, dot product, euclidean, and derrida distance metrics.",
            "category": "advanced",
        },
        {
            "title": "Troubleshooting Common Errors",
            "content": "If you encounter import errors, ensure all dependencies are installed correctly.",
            "category": "troubleshooting",
        },
    ]

    client.save(
        partition="documentation", collection=docs, key="content"  # type: ignore
    )

    # User query
    query = "How do I find similar documents?"
    print(f"\nUser query: '{query}'")

    results = client.search(
        term=query, partition="documentation", key="content", top_k=2
    )

    print("\nMost relevant documentation:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc['title']} ({doc['category']})")
        print(f"   {doc['content']}")
        print(f"   Relevance: {doc['similarity_score']:.4f}")


def faq_matching():
    """Example: FAQ question matching."""
    print("\n\nUse Case 2: FAQ Matching")
    print("=" * 60)

    client = Client()

    # FAQ database
    faqs = [
        {
            "question": "How do I reset my password?",
            "answer": "Click 'Forgot Password' on the login page and follow the email instructions.",
            "category": "account",
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept credit cards, PayPal, and bank transfers.",
            "category": "billing",
        },
        {
            "question": "How long does shipping take?",
            "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 days.",
            "category": "shipping",
        },
        {
            "question": "Can I cancel my subscription?",
            "answer": "Yes, you can cancel anytime from your account settings.",
            "category": "account",
        },
        {
            "question": "Do you offer refunds?",
            "answer": "We offer full refunds within 30 days of purchase.",
            "category": "billing",
        },
    ]

    client.save(partition="faqs", collection=faqs, key="question")  # type: ignore

    # User questions
    user_questions = [
        "I forgot my login password",
        "How fast is delivery?",
        "Can I get my money back?",
    ]

    for user_q in user_questions:
        print(f"\nUser: '{user_q}'")
        results = client.search(term=user_q, partition="faqs", key="question", top_k=1)

        if results:
            match = results[0]
            print(f"Matched FAQ: {match['question']}")
            print(f"Answer: {match['answer']}")
            print(f"Confidence: {match['similarity_score']:.4f}")


def product_recommendation():
    """Example: Product recommendation based on descriptions."""
    print("\n\nUse Case 3: Product Recommendation")
    print("=" * 60)

    client = Client()

    # Product catalog
    products = [
        {
            "name": "Wireless Headphones",
            "description": "Noise-canceling over-ear headphones with 30-hour battery life",
            "price": 299,
            "category": "audio",
        },
        {
            "name": "Laptop Stand",
            "description": "Ergonomic aluminum stand for laptops with adjustable height",
            "price": 49,
            "category": "accessories",
        },
        {
            "name": "USB-C Hub",
            "description": "7-in-1 USB-C adapter with HDMI, USB ports, and SD card reader",
            "price": 39,
            "category": "accessories",
        },
        {
            "name": "Mechanical Keyboard",
            "description": "RGB backlit mechanical keyboard with customizable switches",
            "price": 149,
            "category": "peripherals",
        },
        {
            "name": "Bluetooth Speaker",
            "description": "Portable waterproof speaker with 360-degree sound",
            "price": 79,
            "category": "audio",
        },
    ]

    client.save(
        partition="products", collection=products, key="description"  # type: ignore
    )

    # Customer search
    search_query = "I need something for better sound quality"
    print(f"\nCustomer search: '{search_query}'")

    results = client.search(
        term=search_query, partition="products", key="description", top_k=3
    )

    print("\nRecommended products:")
    for i, product in enumerate(results, 1):
        print(f"\n{i}. {product['name']} - ${product['price']}")
        print(f"   {product['description']}")
        print(f"   Match: {product['similarity_score']:.4f}")


def content_deduplication():
    """Example: Finding duplicate or similar content."""
    print("\n\nUse Case 4: Content Deduplication")
    print("=" * 60)

    client = Client()

    # Content submissions (some are duplicates)
    submissions = [
        {
            "id": "1",
            "text": "Python is a high-level programming language",
            "author": "Alice",
        },
        {"id": "2", "text": "JavaScript is used for web development", "author": "Bob"},
        {
            "id": "3",
            "text": "Python is a high level programming language",  # Near duplicate
            "author": "Charlie",
        },
        {
            "id": "4",
            "text": "Machine learning requires large datasets",
            "author": "David",
        },
        {
            "id": "5",
            "text": "JS is commonly used in web development",  # Similar to #2
            "author": "Eve",
        },
    ]

    print("Checking for duplicate content...")

    client.save(
        partition="submissions", collection=submissions, key="text"  # type: ignore
    )

    # Check each submission for similar content
    duplicates = []
    for submission in submissions:
        results = client.search(
            term=submission["text"],
            partition="submissions",
            key="text",
            top_k=2,  # Get top 2 (including self)
        )

        # Check if there's a high similarity match (other than itself)
        if len(results) > 1 and results[1]["similarity_score"] > 0.90:
            duplicates.append({"original": submission, "duplicate": results[1]})

    if duplicates:
        print(f"\nFound {len(duplicates)} potential duplicates:")
        for dup in duplicates:
            print(f"\n  ID {dup['original']['id']} by {dup['original']['author']}")
            print(
                f"  Similar to ID {dup['duplicate']['id']} (score: {dup['duplicate']['similarity_score']:.4f})"
            )
            print(f"  '{dup['original']['text']}'")
            print(f"  '{dup['duplicate']['text']}'")


def main():
    print("Real-World Use Cases for Microvector")
    print("=" * 60)

    documentation_search()
    faq_matching()
    product_recommendation()
    content_deduplication()

    print("\n" + "=" * 60)
    print("Summary: Microvector is useful for:")
    print("  • Semantic search over any text corpus")
    print("  • Question answering and FAQ matching")
    print("  • Product/content recommendation")
    print("  • Duplicate detection")
    print("  • Any task requiring semantic similarity")


if __name__ == "__main__":
    main()
