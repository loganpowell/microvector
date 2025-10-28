"""
Custom Cache Paths Example

Demonstrates how to use custom directories for:
- Model caching (embedding models)
- Vector caching (persisted vector stores)
"""

import tempfile
import os
from pathlib import Path
from microvector import Client


def main():
    # Create custom cache directories
    # In production, you'd use actual paths instead of temp directories
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_model_cache = os.path.join(temp_dir, "my_models")
        custom_vector_cache = os.path.join(temp_dir, "my_vectors")

        print(f"Model cache: {custom_model_cache}")
        print(f"Vector cache: {custom_vector_cache}")

        # Initialize client with custom paths
        # The directories will be created automatically if they don't exist
        client = Client(
            cache_models=custom_model_cache,
            cache_vectors=custom_vector_cache,
            embedding_model="avsolatorio/GIST-small-Embedding-v0",  # Default model
        )

        # Verify directories were created
        print(f"\n✓ Model cache exists: {os.path.exists(custom_model_cache)}")
        print(f"✓ Vector cache exists: {os.path.exists(custom_vector_cache)}")

        # Create and save a collection
        documents = [
            {"text": "Custom cache example document 1"},
            {"text": "Custom cache example document 2"},
            {"text": "Custom cache example document 3"},
        ]

        print("\nSaving documents...")
        client.save(
            partition="custom_cache_demo",
            collection=documents,
        )

        # Check that the vector cache file was created
        expected_file = Path(custom_vector_cache) / "custom_cache_demo.pickle.gz"
        print(f"\n✓ Vector cache file created: {expected_file.exists()}")
        print(f"  Location: {expected_file}")

        # Search the collection
        results = client.search(
            term="example",
            partition="custom_cache_demo",
            key="text",
            top_k=2,
        )

        print(f"\nSearch results: {len(results)} documents found")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['text']} (score: {result['similarity_score']:.4f})")


if __name__ == "__main__":
    main()
