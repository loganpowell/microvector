"""
Example usage of the microvector Client API.

This demonstrates the API described in docs/ARCH.md
"""

from microvector import Client

# Initialize the client
mv_client = Client(
    cache_models="./cached_models",
    cache_vectors="./vector_cache",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # default
)

# Sample data
sample_collection = [
    {
        "text": "The quick brown fox jumps over the lazy dog",
        "metadata": {"source": "classic"},
    },
    {
        "text": "Python is a high-level programming language",
        "metadata": {"source": "tech"},
    },
    {"text": "Machine learning models learn from data", "metadata": {"source": "ai"}},
    {"text": "The lazy dog sleeps under the tree", "metadata": {"source": "story"}},
    {"text": "JavaScript is used for web development", "metadata": {"source": "tech"}},
]

# Example 1: Save data to vector store
print("Example 1: Saving data to vector store")
print("=" * 50)
result = mv_client.save(
    partition_name="example_partition",
    collection=sample_collection,
)
print(f"Save result: {result}\n")

# Example 2: Search existing data in vector store
print("Example 2: Searching existing data")
print("=" * 50)
search_results = mv_client.search(
    term="programming languages",
    partition_name="example_partition",
    key="text",
    top_k=3,
    algo="cosine",
)
print("Search results for 'programming languages':")
for i, result in enumerate(search_results or [], 1):
    print(f"{i}. {result.get('text', 'N/A')}")
    print(f"   Similarity: {result.get('similarity_score', 0):.4f}")
    print(f"   Metadata: {result.get('metadata', {})}\n")

# Example 3: Create and search freshly minted vector store (temporary, no caching)
print("Example 3: Temporary in-memory search (no caching)")
print("=" * 50)
temp_collection = [
    {"text": "cats are popular pets", "metadata": {"category": "animals"}},
    {"text": "dogs are loyal companions", "metadata": {"category": "animals"}},
    {"text": "birds can fly in the sky", "metadata": {"category": "animals"}},
]

temp_results = mv_client.search(
    term="pet animals",
    partition_name="temp_partition",
    key="text",
    top_k=2,
    collection=temp_collection,
    cache=False,  # do not persist to disk
    algo="cosine",
)
print("Temporary search results for 'pet animals':")
for i, result in enumerate(temp_results or [], 1):
    print(f"{i}. {result.get('text', 'N/A')}")
    print(f"   Similarity: {result.get('similarity_score', 0):.4f}\n")

print("Example completed successfully!")
