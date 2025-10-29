# microvector

Lightweight local vector database with persistence to disk, supporting multiple similarity metrics and an easy-to-use API.

> A refactor and repackaging of [HyperDB](https://github.com/jdagdelen/hyperDB/tree/main) optimized for CPU-only environments with improved type safety and developer experience.

## Features

- 🚀 **Simple API**: Clean, intuitive interface with `PartitionStore` pattern
- 💾 **Persistent Storage**: Automatically caches vector stores to `.pickle.gz` files
- 🔍 **Multiple Similarity Metrics**: Choose from cosine, dot product, Euclidean, or Derrida distance
- 🎯 **Type Safe**: Full type annotations with strict pyright compliance
- ⚡ **CPU Optimized**: Designed for CPU-only environments (no CUDA required)
- 🔄 **Flexible Caching**: Use persistent stores or create temporary in-memory collections
- 📦 **Easy Installation**: One-command setup with automatic PyTorch CPU configuration
- ✨ **Partition-level Operations**: Add, remove, and search documents through dedicated store objects

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

# Save a collection (by default, in-memory only)
store = client.save(
    partition="my_documents",
    collection=[
        {"text": "Python is a popular programming language", "category": "tech"},
        {"text": "Machine learning models learn from data", "category": "ai"},
        {"text": "The quick brown fox jumps over the lazy dog", "category": "example"},
    ],
    key="text"
)

# Search using the store
results = store.search(
    term="artificial intelligence and ML",
)

for result in results:
    print(f"Score: {result['similarity_score']:.4f} - {result['text']}")

# Add more documents (also in-memory by default)
store.add([
    {"text": "Deep learning uses neural networks", "category": "ai"}
])

# Search again with the updated store
results = store.search("neural networks", top_k=3)

# Persist to disk when ready
client.save(
    partition="my_documents",
    collection=store.to_dict(),
    cache=True  # Now save to disk
)
```

## API Reference

### Client

The main interface for creating and managing vector stores.

```python
Client(
    model_cache: str = "./.cached_models",
    vector_cache: str = "./.vector_cache",
    embedding_model: str = "avsolatorio/GIST-small-Embedding-v0",
    search_algo: str = "cosine"
)
```

**Parameters:**

| Parameter         | Description                                        | Default                                 |
| ----------------- | -------------------------------------------------- | --------------------------------------- |
| `model_cache`     | Directory for caching downloaded embedding models  | `"./.cached_models"`                    |
| `vector_cache`    | Directory for persisting vector stores             | `"./.vector_cache"`                     |
| `embedding_model` | HuggingFace model name for generating embeddings   | `"avsolatorio/GIST-small-Embedding-v0"` |
| `search_algo`     | `"cosine"`, `"dot"`, `"euclidean"`, or `"derrida"` | `"cosine"`                              |

**Note:** The `search_algo` is set at the client level and applies to all partitions created by that client. This ensures consistency and prevents issues with switching algorithms on already-normalized vectors.

### save()

Create or update a vector store and return a `PartitionStore` for operations.

```python
store = client.save(
    partition: str,
    collection: list[dict[str, Any]],
    key: str = "text",
    cache: bool = False,
    append: bool = False
) -> PartitionStore
```

**Parameters:**

| Parameter    | Description                                             | Default  |
| ------------ | ------------------------------------------------------- | -------- |
| `partition`  | Unique identifier for this vector store                 | -        |
| `collection` | List of documents (dictionaries) to vectorize           | -        |
| `key`        | Field name to use for embedding                         | `"text"` |
| `cache`      | If True, persist to disk; if False, keep in-memory only | `False`  |
| `append`     | If True, add to existing store; if False, replace       | `False`  |

**Returns:** `PartitionStore` object with methods for searching and managing documents

**Example:**

```python
store = client.save(
    partition="products",
    collection=[
        {"description": "Wireless headphones", "price": 99.99},
        {"description": "Smart watch", "price": 299.99},
    ],
    key="description",
    cache=True  # Persist to disk
)

print(f"Partition: {store.partition}")
print(f"Size: {store.size}")
print(f"Algorithm: {store.algo}")
```

### PartitionStore

A partition-specific interface for vector operations returned by `client.save()`.

**Attributes:**

| Attribute   | Type | Description                                                                      |
| ----------- | ---- | -------------------------------------------------------------------------------- |
| `partition` | str  | Name of the partition                                                            |
| `key`       | str  | Field being vectorized                                                           |
| `algo`      | str  | Similarity algorithm in use (`"cosine"`, `"dot"`, `"euclidean"`, or `"derrida"`) |
| `size`      | int  | Number of documents in the store (read-only property)                            |

**Methods:**

#### search()

Search this partition for similar documents.

```python
results = store.search(
    term: str,
    top_k: int = 5
) -> list[dict[str, Any]]
```

**Parameters:**

| Parameter | Description                         | Default |
| --------- | ----------------------------------- | ------- |
| `term`    | Search query string                 | -       |
| `top_k`   | Maximum number of results to return | `5`     |

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

**Example:**

```python
results = store.search("laptop computers", top_k=3)
for result in results:
    print(f"{result['similarity_score']:.3f} - {result['description']}")
```

#### add()

Add new documents to this partition.

```python
success = store.add(
    collection: list[dict[str, Any]] | dict[str, Any],
    cache: bool = False
) -> bool
```

**Parameters:**

| Parameter    | Description                                        | Default |
| ------------ | -------------------------------------------------- | ------- |
| `collection` | Single document or list of documents to add        | -       |
| `cache`      | If True, persist changes; if False, keep in-memory | `False` |

**Returns:** `True` if successful, `False` otherwise

**Example:**

```python
# Add a single document
store.add({"description": "USB-C cable", "price": 12.99})

# Add multiple documents
store.add([
    {"description": "Keyboard", "price": 79.99},
    {"description": "Mouse pad", "price": 19.99}
], cache=True)

print(f"Updated size: {store.size}")
```

#### remove()

Remove a document from this partition by index or content.

```python
success = store.remove(
    item: int | dict[str, Any],
    cache: bool = False
) -> bool
```

**Parameters:**

| Parameter | Description                                               | Default |
| --------- | --------------------------------------------------------- | ------- |
| `item`    | Document index (int) or document content (dict) to remove | -       |
| `cache`   | If True, persist changes; if False, keep in-memory        | `False` |

**Returns:** `True` if successful, `False` otherwise

**Example:**

```python
# Remove by index
store.remove(0)

# Remove by document content
store.remove({"description": "Wireless headphones", "price": 99.99})
```

#### delete()

Delete this partition's cache file from disk.

```python
success = store.delete() -> bool
```

**Returns:** `True` if successful, `False` otherwise

**Example:**

```python
if store.delete():
    print(f"Partition '{store.partition}' deleted from disk")
```

## Similarity Algorithms

| Algorithm   | Best For                          | Range                        |
| ----------- | --------------------------------- | ---------------------------- |
| `cosine`    | General text similarity (default) | 0-1 (higher is more similar) |
| `dot`       | When magnitude matters            | Unbounded                    |
| `euclidean` | Spatial distance                  | 0-∞ (lower is more similar)  |
| `derrida`   | Experimental alternative distance | 0-∞ (lower is more similar)  |

## Advanced Usage

### Using Different Algorithms

The similarity algorithm is set at the client level and applies to all partitions:

```python
# Create clients with different algorithms
cosine_client = Client(search_algo="cosine")
dot_client = Client(search_algo="dot")
euclidean_client = Client(search_algo="euclidean")

# Each client's partitions use its algorithm
cosine_store = cosine_client.save("docs_cosine", documents)
dot_store = dot_client.save("docs_dot", documents)

# Different algorithms, different results
cosine_results = cosine_store.search("query")
dot_results = dot_store.search("query")
```

**Why client-level?** Vectors are normalized based on the algorithm. Switching algorithms on existing vectors would produce incorrect results, so we lock the algorithm at creation time for consistency.

### Custom Embedding Models

Use any HuggingFace sentence-transformer model:

```python
client = Client(
    embedding_model="intfloat/e5-small-v2",
    search_algo="cosine"
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
    },
    {
        "product": {
            "name": "Mouse",
            "specs": {"cpu": None}
        }
    }
]

store = client.save(
    partition="products",
    collection=collection,
    key="product.name"  # Extract "Laptop", "Mouse" from nested structure
)

# Search works on the nested field
results = store.search("computer", top_k=1)
print(results[0]["product"]["name"])  # "Laptop"
```

### Working with Multiple Partitions

Organize different datasets in separate partitions:

```python
# Create stores for different content types
news_store = client.save("news_articles", news_data, key="content")
review_store = client.save("product_reviews", review_data, key="review_text")
ticket_store = client.save("support_tickets", tickets, key="description")

# Search each independently
news_results = news_store.search("economy")
review_results = review_store.search("quality")
ticket_results = ticket_store.search("login issue")
```

### Incremental Updates

Add new documents to existing stores without replacing them:

```python
# Create initial store (in-memory by default)
store = client.save(
    partition="knowledge_base",
    collection=[
        {"text": "Python is a programming language"},
        {"text": "JavaScript runs in browsers"},
    ]
)

print(f"Initial size: {store.size}")  # 2

# Add more documents using the store's add() method
store.add([
    {"text": "TypeScript adds types to JavaScript"},
    {"text": "Rust is memory-safe"},
])

print(f"Updated size: {store.size}")  # 4

# Or use save() with append=True
client.save(
    partition="knowledge_base",
    collection=[{"text": "Go is designed for concurrency"}],
    append=True
)

# Persist all changes to disk when ready
store.add([], cache=True)  # Flush to disk
```

### Persistent Storage

Enable caching to persist vector stores to disk:

```python
# Save directly to disk
store = client.save(
    partition="permanent_docs",
    collection=documents,
    cache=True  # Persist immediately
)

# Add documents and persist
store.add(new_documents, cache=True)

# Remove documents and persist
store.remove(0, cache=True)

# Later, load from cache
loaded_store = client.save(
    partition="permanent_docs",
    collection=[],  # Empty collection loads from cache
    cache=True
)
```

### In-Memory Operations

Work with documents without persisting to disk (default behavior):

```python
# Create a temporary store (cache=False is the default)
temp_store = client.save(
    partition="temp_analysis",
    collection=documents
)

# Add documents without caching (default behavior)
temp_store.add(more_documents)

# Search as normal
results = temp_store.search("query")

# Since cache=False (default), changes aren't persisted
```

### Document Management

```python
# Create store (in-memory by default)
store = client.save("products", initial_products)

# Add new products (in-memory)
store.add([
    {"name": "New Product", "price": 49.99}
])

# Remove by index (in-memory)
store.remove(0)

# Remove by content (in-memory)
store.remove({"name": "Old Product", "price": 19.99})

# Check current size
print(f"Current inventory: {store.size} items")

# Persist changes to disk
store.add([], cache=True)

# Or delete entire partition from disk
if store.delete():
    print("Partition deleted")
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
├── main.py              # Client API
├── partition_store.py   # PartitionStore class for partition operations
├── store.py             # Vector storage and similarity search
├── cache.py             # Persistence layer
├── embed.py             # Embedding generation
├── search.py            # Search utilities
├── algos.py             # Similarity algorithms
└── utils.py             # Helper functions
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Based on [HyperDB](https://github.com/jdagdelen/hyperDB) by John Dagdelen.
Refactored and maintained by Logan Powell.
