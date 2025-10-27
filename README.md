# microvector

Lightweight local vector database with persistence to disk, supporting multiple similarity metrics and an easy-to-use API.

> A refactor and repackaging of [HyperDB](https://github.com/jdagdelen/hyperDB/tree/main) optimized for CPU-only environments with improved type safety and developer experience.

## Features

- 🚀 **Simple API**: Clean, intuitive interface with just two main methods: `save()` and `search()`
- 💾 **Persistent Storage**: Automatically caches vector stores to `.pickle.gz` files
- 🔍 **Multiple Similarity Metrics**: Choose from cosine, dot product, Euclidean, or Derrida distance
- 🎯 **Type Safe**: Full type annotations with strict pyright compliance
- ⚡ **CPU Optimized**: Designed for CPU-only environments (no CUDA required)
- 🔄 **Flexible Caching**: Use persistent stores or create temporary in-memory collections
- 📦 **Easy Installation**: One-command setup with automatic PyTorch CPU configuration

## Installation

```bash
pip install microvector
```

Or for development:

```bash
git clone https://github.com/loganpowell/microvector.git
cd microvector
uv sync
```

## Quick Start

```python
from microvector import Client

# Initialize the client
client = Client()

# Save a collection with automatic persistence
client.save(
    partition="my_documents",
    collection=[
        {"text": "Python is a popular programming language", "category": "tech"},
        {"text": "Machine learning models learn from data", "category": "ai"},
        {"text": "The quick brown fox jumps over the lazy dog", "category": "example"},
    ]
)

# Search the persisted collection
results = client.search(
    term="artificial intelligence and ML",
    partition="my_documents",
    key="text",
    top_k=5
)

for result in results:
    print(f"Score: {result['similarity_score']:.4f} - {result['text']}")
```

## API Reference

### Client

The main interface for all vector operations.

```python
Client(
    cache_models: str = "./.cached_models",
    cache_vectors: str = "./.vector_cache",
    embedding_model: str = "avsolatorio/GIST-small-Embedding-v0"
)
```

**Parameters:**

- `cache_models`: Directory for caching downloaded embedding models
- `cache_vectors`: Directory for persisting vector stores
- `embedding_model`: HuggingFace model name for generating embeddings

### save()

Save a collection to a persistent vector store.

```python
client.save(
    partition: str,
    collection: list[dict[str, Any]],
    key: str = "text",
    algo: str = "cosine"
) -> dict[str, Any]
```

**Parameters:**

- `partition`: Unique identifier for this vector store
- `collection`: List of documents (dictionaries) to vectorize
- `key`: Field name to use for embedding (default: "text")
- `algo`: Similarity metric - `"cosine"`, `"dot"`, `"euclidean"`, or `"derrida"`

**Returns:**

```python
{
    "status": "success",
    "partition": "my_documents",
    "documents_saved": 42,
    "key": "text",
    "algorithm": "cosine",
    "append": False,
    "embedding_model": "avsolatorio/GIST-small-Embedding-v0"
}
```

**Example:**

```python
result = client.save(
    partition="products",
    collection=[
        {"description": "Wireless headphones", "price": 99.99},
        {"description": "Smart watch", "price": 299.99},
    ],
    key="description",
    algo="cosine"
)
```

### search()

Search a vector store with semantic similarity.

```python
client.search(
    term: str,
    partition: str,
    key: str = "text",
    top_k: int = 5,
    collection: Optional[list[dict[str, Any]]] = None,
    cache: bool = True,
    algo: str = "cosine",
    append: bool = False
) -> list[dict[str, Any]]
```

**Parameters:**

- `term`: Search query string
- `partition`: Name of the vector store to query
- `key`: property within each item in the collection to search against (vectorized field)
- `top_k`: Maximum number of results to return
- `collection`: Optional temporary collection (for non-persistent search)
- `cache`: If True, persist the collection; if False, keep in-memory only
- `algo`: Similarity metric to use
- `append`: If True, append to existing store; if False (default), replace existing store

**Returns:** List of documents with similarity scores

```python
[
    {
        "text": "Machine learning is awesome",
        "category": "ai",
        "similarity_score": 0.923
    },
    ...
]
```

**Example - Search existing store:**

```python
results = client.search(
    term="laptop computers",
    partition="products",
    key="description",
    top_k=3
)
```

**Example - Temporary search (no persistence):**

```python
results = client.search(
    term="budget phones",
    partition="temp_search",
    key="description",
    top_k=5,
    collection=[
        {"description": "iPhone 15 Pro", "price": 999},
        {"description": "Samsung Galaxy S24", "price": 899},
    ],
    cache=False  # Don't save to disk
)
```

## Similarity Algorithms

| Algorithm   | Best For                          | Range                        |
| ----------- | --------------------------------- | ---------------------------- |
| `cosine`    | General text similarity (default) | 0-1 (higher is more similar) |
| `dot`       | When magnitude matters            | Unbounded                    |
| `euclidean` | Spatial distance                  | 0-∞ (lower is more similar)  |
| `derrida`   | Experimental alternative distance | 0-∞ (lower is more similar)  |

## Advanced Usage

### Custom Embedding Models

Use any HuggingFace sentence-transformer model:

```python
client = Client(
    embedding_model="intfloat/e5-small-v2"
)
```

### Nested Key Paths

Access nested fields using dot notation:

```python
collection = [
    {
        "product": {
            "name": "Laptop",
            "specs": {"cpu": "Intel i7"}
        }
    }
]

client.save(
    partition="products",
    collection=collection,
    key="product.name"
)
```

### Working with Multiple Partitions

Organize different datasets in separate partitions:

```python
# Save different content types
client.save("news_articles", news_data, key="content")
client.save("product_reviews", review_data, key="review_text")
client.save("support_tickets", tickets, key="description")

# Search each independently
news_results = client.search("economy", "news_articles", key="content")
review_results = client.search("quality", "product_reviews", key="review_text")
```

### Incremental Updates with Append

Add new documents to existing vector stores without replacing them:

```python
# Create initial store
client.save(
    partition="knowledge_base",
    key="text",
    collection=[
        {"text": "Python is a programming language"},
        {"text": "JavaScript runs in browsers"},
    ]
)

# Append more documents later
client.save(
    partition="knowledge_base",
    key="text",
    collection=[
        {"text": "TypeScript adds types to JavaScript"},
        {"text": "Rust is memory-safe"},
    ],
    append=True  # Adds to existing store instead of replacing
)

# Now the store contains all 4 documents
```

### Temporary Append

Test new documents against existing corpus without persisting changes:

```python
# Create persistent store
client.save(
    partition="products",
    key="text",
    collection=[
        {"text": "laptop computer", "price": 999},
        {"text": "wireless mouse", "price": 29},
    ]
)

# Temporarily add documents for a single search
results = client.search(
    term="computer accessories",
    partition="products",
    key="text",
    collection=[
        {"text": "USB-C hub", "price": 49},
        {"text": "laptop stand", "price": 39},
    ],
    cache=False,  # Don't persist
    append=True,  # But load existing cache and append temporarily
    top_k=4
)
# Returns 4 results (2 original + 2 temporary)

# Next search only finds the 2 original products
results = client.search(
    term="computer",
    partition="products",
    key="text",
    top_k=4
)
# Returns 2 results (temporary documents weren't persisted)
```

## Development Setup

This project uses `uv` for dependency management and automatically configures CPU-only PyTorch.

### Quick Start

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Verify setup:**

   ```bash
   uv run python setup_dev.py
   ```

3. **Run tests:**

   ```bash
   uv run pytest
   ```

4. **Type checking:**
   ```bash
   uv run pyright
   ```

### What Gets Installed

- **PyTorch (CPU-only)**: Automatically from PyTorch CPU index
- **Transformers**: HuggingFace transformers library
- **Sentence Transformers**: For embedding generation
- **NumPy**: Numerical computing

No special flags or manual PyTorch installation needed - just `uv sync` and go!

## Performance Tips

1. **Reuse Client instances** - Model loading is expensive
2. **Use persistent caching** - Vector computation is cached automatically
3. **Batch your saves** - Save collections together when possible
4. **Choose the right algorithm** - Cosine is fastest for most use cases
5. **Adjust top_k** - Lower values are faster

## Architecture

```
microvector/
├── main.py          # Client API
├── store.py         # Vector storage and similarity search
├── cache.py         # Persistence layer
├── embed.py         # Embedding generation
├── algos.py         # Similarity algorithms
└── utils.py         # Helper functions
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Based on [HyperDB](https://github.com/jdagdelen/hyperDB) by John Dagdelen.
Refactored and maintained by Logan Powell.
