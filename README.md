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
    partition_name="my_documents",
    collection=[
        {"text": "Python is a popular programming language", "category": "tech"},
        {"text": "Machine learning models learn from data", "category": "ai"},
        {"text": "The quick brown fox jumps over the lazy dog", "category": "example"},
    ]
)

# Search the persisted collection
results = client.search(
    term="artificial intelligence and ML",
    partition_name="my_documents",
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
    embedding_model: str = "infgrad/stella-base-en-v2"
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
    partition_name: str,
    collection: list[dict[str, Any]],
    key: str = "text",
    algo: str = "cosine"
) -> dict[str, Any]
```

**Parameters:**

- `partition_name`: Unique identifier for this vector store
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
    "algorithm": "cosine"
}
```

**Example:**

```python
result = client.save(
    partition_name="products",
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
    partition_name: str,
    key: str = "text",
    top_k: int = 5,
    collection: Optional[list[dict[str, Any]]] = None,
    cache: bool = True,
    algo: str = "cosine"
) -> list[dict[str, Any]]
```

**Parameters:**

- `term`: Search query string
- `partition_name`: Name of the vector store to query
- `key`: Field name that was used for embedding
- `top_k`: Maximum number of results to return
- `collection`: Optional temporary collection (for non-persistent search)
- `cache`: If True, persist the collection; if False, keep in-memory only
- `algo`: Similarity metric to use

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
    partition_name="products",
    key="description",
    top_k=3
)
```

**Example - Temporary search (no persistence):**

```python
results = client.search(
    term="budget phones",
    partition_name="temp_search",
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
    embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
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
    partition_name="products",
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
