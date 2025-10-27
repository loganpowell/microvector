# Append Parameter Feature

## Overview

The `append` parameter allows you to incrementally update existing vector caches instead of replacing them entirely. This is useful when you want to add new documents to an existing vector store without re-processing all previously stored documents.

## Parameter Details

- **Name**: `append`
- **Type**: `bool`
- **Default**: `False`
- **Available in**: `Client.save()`, `Client.search()`, `vector_search()`, `vector_cache()`

## Behavior

### When `append=False` (Default)

- Creates a new vector store if one doesn't exist
- **Replaces** the entire existing vector store with new vectors if one already exists
- This is the original behavior - safe and predictable

### When `append=True`

- Creates a new vector store if one doesn't exist (same as `append=False`)
- **Adds** new vectors to the existing vector store if one already exists
- Existing vectors are preserved and new ones are added
- Useful for incremental updates

## Usage Examples

### Example 1: Using the Client API

```python
from microvector import Client

client = Client()

# Create initial vector store
client.save(
    partition="products",
    collection=[
        {"text": "laptop computer", "price": 999},
        {"text": "wireless mouse", "price": 29},
    ],
    key="text",
    append=False  # Default - creates new store
)

# Add more products to the existing store
client.save(
    partition="products",
    collection=[
        {"text": "mechanical keyboard", "price": 79},
        {"text": "USB-C cable", "price": 15},
    ],
    key="text",
    append=True  # Adds to existing store
)

# Now the store contains all 4 products
results = client.search(
    term="computer accessories",
    partition="products",
    key="text",
    top_k=5
)
```

### Example 2: Replace vs Append

```python
from microvector import Client

client = Client()

# Initial save
client.save(
    partition="docs",
    collection=[{"text": "Document 1"}, {"text": "Document 2"}],
    key="text"
)

# Append more documents (now has 4 total)
client.save(
    partition="docs",
    collection=[{"text": "Document 3"}, {"text": "Document 4"}],
    key="text",
    append=True
)

# Replace all documents (now has only 1 document)
client.save(
    partition="docs",
    collection=[{"text": "New Document"}],
    key="text",
    append=False  # Replaces everything
)
```

### Example 3: Using with search()

```python
from microvector import Client

client = Client()

# Search and optionally append new documents in one call
results = client.search(
    term="machine learning",
    partition="articles",
    key="text",
    collection=[
        {"text": "New article about deep learning"},
        {"text": "Another article about neural networks"}
    ],
    cache=True,
    append=True  # Adds these to existing cache
)
```

### Example 4: Low-level API

```python
from microvector.search import vector_search

# Search with append
results = vector_search(
    term="python programming",
    partition="tutorials",
    key="content",
    collection=new_tutorials,
    cache=True,
    append=True
)
```

### Example 5: Temporary Append (cache=False, append=True)

```python
from microvector import Client

client = Client()

# Create persistent cache
client.save(
    partition="products",
    collection=[
        {"text": "laptop computer", "price": 999},
        {"text": "wireless mouse", "price": 29},
    ],
    key="text"
)

# Temporarily add new products for a search without persisting
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

# This search will find results from all 4 products (2 original + 2 temporary)
# But the cache file still only contains the original 2 products

# Next search without new collection - only finds original 2
results = client.search(
    term="computer",
    partition="products",
    key="text",
    top_k=4
)
# Only returns the 2 original products
```

## Implementation Details

The `append` parameter modifies the behavior in `vector_cache()` function:

1. **When cache exists and `append=True`**:

   - Loads existing vector store from disk
   - Uses `Store.add_collection()` to add new vectors
   - Saves updated store back to disk
   - Preserves normalization state for cosine similarity

2. **When cache exists and `append=False`**:

   - Ignores existing cache
   - Creates new store with new collection
   - Overwrites cache file with new store

3. **When cache doesn't exist**:

   - Same behavior regardless of `append` value
   - Creates new cache with provided collection

4. **When cache exists and `append=True` with `cache=False`**:
   - Loads existing cache into memory
   - Appends new collection temporarily (in memory only)
   - Does NOT save changes back to disk
   - Original cache file remains unchanged

## Performance Considerations

- **Append mode**: Only processes embeddings for new documents
- **Replace mode**: Processes embeddings for all documents
- **Temporary append mode**: Loads existing cache + processes embeddings for new documents (no disk write)
- Appending is more efficient when adding small batches to large collections
- Replacing is simpler and ensures consistency when you have all documents available
- Temporary append is ideal for testing or temporary analysis without modifying stored data

## Use Cases

### Good use cases for `append=True`:

- Incremental data ingestion (e.g., daily updates)
- Adding new documents as they arrive
- Building up a corpus over time
- Batch processing with periodic updates

### Good use cases for `append=False`:

- Full rebuilds from source data
- When you want to ensure data consistency
- Deduplication or cleanup operations
- Initial setup or complete refresh

### Good use cases for `append=True` with `cache=False`:

- Testing new documents against existing corpus without committing
- "What-if" analysis - see how new documents would rank
- Temporary expansion of search space for a single query
- A/B testing different document sets
- Preview mode before permanent addition
- Analyzing candidate documents before ingestion

## Limitations

- Both append and replace operations require the same `key` field
- All vectors must have the same dimensionality (enforced by Store)
- The `algo` parameter should remain consistent for a partition
- No built-in deduplication - appending the same document twice will create duplicates
