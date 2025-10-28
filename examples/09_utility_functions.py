"""
Utility Functions Example

Demonstrates helper utilities from microvector.utils:
- stringify_nonstring_target_values: Convert non-string values to strings
- Useful for ensuring all vectorized fields are strings
"""

from microvector import Client
from microvector.utils import stringify_nonstring_target_values


def main():
    print("Utility Functions Example")
    print("=" * 60)

    # Example 1: Converting integer values
    print("\nExample 1: Converting product IDs (integers) to strings")
    print("-" * 60)

    products = [
        {"name": "Widget A", "product_id": 12345},
        {"name": "Widget B", "product_id": 67890},
        {"name": "Widget C", "product_id": 11111},
    ]

    print("Original data:")
    for p in products:
        print(
            f"  {p['name']}: ID={p['product_id']} (type: {type(p['product_id']).__name__})"
        )

    # Convert product_id to strings
    converted = stringify_nonstring_target_values(products, "product_id")

    print("\nAfter conversion:")
    for p in converted:
        print(
            f"  {p['name']}: ID={p['product_id']} (type: {type(p['product_id']).__name__})"
        )

    # Example 2: Converting boolean values
    print("\n\nExample 2: Converting boolean flags to strings")
    print("-" * 60)

    items = [
        {"item": "Task A", "completed": True},
        {"item": "Task B", "completed": False},
        {"item": "Task C", "completed": True},
    ]

    print("Original data:")
    for item in items:
        print(
            f"  {item['item']}: {item['completed']} (type: {type(item['completed']).__name__})"
        )

    converted = stringify_nonstring_target_values(items, "completed")

    print("\nAfter conversion:")
    for item in converted:
        print(
            f"  {item['item']}: {item['completed']} (type: {type(item['completed']).__name__})"
        )

    # Example 3: Converting float values
    print("\n\nExample 3: Converting prices (floats) to strings")
    print("-" * 60)

    products_with_prices = [
        {"item": "Laptop", "price": 999.99},
        {"item": "Mouse", "price": 29.50},
        {"item": "Keyboard", "price": 79.00},
    ]

    print("Original data:")
    for p in products_with_prices:
        print(f"  {p['item']}: ${p['price']} (type: {type(p['price']).__name__})")

    converted = stringify_nonstring_target_values(products_with_prices, "price")

    print("\nAfter conversion:")
    for p in converted:
        print(f"  {p['item']}: ${p['price']} (type: {type(p['price']).__name__})")

    # Example 4: Nested dictionaries
    print("\n\nExample 4: Converting values in nested structures")
    print("-" * 60)

    nested_data = [
        {"header": "Item 1", "metadata": {"count": 100}},
        {"header": "Item 2", "metadata": {"count": 250}},
    ]

    print("Original nested data:")
    for item in nested_data:
        print(
            f"  {item['header']}: count={item['metadata']['count']} (type: {type(item['metadata']['count']).__name__})"
        )

    converted = stringify_nonstring_target_values(nested_data, "count")

    print("\nAfter conversion:")
    for item in converted:
        print(
            f"  {item['header']}: count={item['metadata']['count']} (type: {type(item['metadata']['count']).__name__})"
        )

    # Example 5: Using with Client for vectorization
    print("\n\nExample 5: Practical use with Client API")
    print("-" * 60)

    # When you have documents with numeric IDs but want to search by ID
    documents = [
        {"description": "Product documentation", "version": 1.5},
        {"description": "API reference guide", "version": 2.0},
        {"description": "Tutorial for beginners", "version": 1.0},
    ]

    # Convert version numbers to strings for vectorization
    converted_docs = stringify_nonstring_target_values(documents, "version")

    client = Client()

    # Now we can vectorize the version field
    client.save(
        partition="versioned_docs",
        collection=converted_docs,  # type: ignore
        key="version",  # Now this field contains strings
    )

    print("✓ Saved documents with stringified version numbers")

    # Search by version
    results = client.search(
        term="2.0",
        partition="versioned_docs",
        key="version",
        top_k=1,
    )

    print(f"\nSearch for version '2.0':")
    for result in results:
        print(f"  {result['description']} (v{result['version']})")
        print(f"  Similarity: {result['similarity_score']:.4f}")

    print("\n" + "=" * 60)
    print("Summary: stringify_nonstring_target_values")
    print("  • Converts integers, floats, booleans to strings")
    print("  • Works with nested dictionaries")
    print("  • Preserves other fields unchanged")
    print("  • Useful before vectorizing non-text fields")


if __name__ == "__main__":
    main()
