"""
Offline Mode Example

Demonstrates saving and using models for offline use:
- Download and save models for offline use
- Use locally cached models without internet
- Useful for air-gapped environments or ensuring availability
"""

import tempfile
import os
from pathlib import Path
from microvector.embed import save_model_for_offline_use, get_embeddings
from microvector.utils import EMBEDDING_MODEL


def main():
    # Create a temporary directory for this example
    # In production, you'd use a permanent directory
    with tempfile.TemporaryDirectory() as temp_dir:
        offline_cache = os.path.join(temp_dir, "offline_models")

        print("Offline Model Setup Example")
        print("=" * 60)
        print(f"Model: {EMBEDDING_MODEL}")
        print(f"Cache directory: {offline_cache}")

        # Step 1: Save model for offline use
        print("\nStep 1: Downloading and saving model for offline use...")
        print("-" * 60)
        saved_path = save_model_for_offline_use(
            model_name=EMBEDDING_MODEL, cache_folder=offline_cache
        )

        print(f"✓ Model saved to: {saved_path}")
        print(f"✓ Directory exists: {saved_path.exists()}")

        # Verify the model files
        expected_files = [
            "config.json",
            "model.safetensors",
            "tokenizer.json",
            "config_sentence_transformers.json",
        ]

        print("\nVerifying model files:")
        for file_name in expected_files:
            file_path = saved_path / file_name
            exists = file_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file_name}")

        # Step 2: Use the offline model
        print("\n\nStep 2: Using the offline model...")
        print("-" * 60)

        # Now we can use the model from the offline cache
        test_documents = [
            "Machine learning is fascinating",
            "Python is a great programming language",
            "The weather is nice today",
        ]

        print(f"Generating embeddings for {len(test_documents)} documents...")
        embeddings = get_embeddings(
            chunks=test_documents, cache_folder=offline_cache  # Use the offline cache
        )

        print(f"\n✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0])}")

        # Verify embeddings are consistent
        print("\nEmbedding statistics:")
        for i, emb in enumerate(embeddings):
            print(f"  Document {i+1}: {len(emb)} dimensions")

        # Step 3: Use offline model again (should be faster)
        print("\n\nStep 3: Reusing offline model (should be instant)...")
        print("-" * 60)

        more_documents = [
            "Deep learning uses neural networks",
            "Cloud computing is transforming IT",
        ]

        embeddings2 = get_embeddings(chunks=more_documents, cache_folder=offline_cache)

        print(f"✓ Generated {len(embeddings2)} more embeddings")
        print(
            f"✓ All embeddings have same dimension: {len(embeddings2[0]) == len(embeddings[0])}"
        )

        print("\n" + "=" * 60)
        print("Summary:")
        print("  • Models are saved locally for offline use")
        print("  • No internet required after initial download")
        print("  • Useful for air-gapped or restricted environments")
        print("  • Models are reused across sessions")


if __name__ == "__main__":
    main()
