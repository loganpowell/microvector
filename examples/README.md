# Microvector Examples

This directory contains comprehensive examples demonstrating various features and use cases of microvector.

## Quick Start

Run any example with:

```bash
python examples/01_basic_usage.py
```

## Example Overview

### Basic Features

1. **`01_basic_usage.py`** - Getting Started

   - Initialize the Client
   - Save a collection
   - Perform semantic search
   - Best starting point for new users

2. **`02_custom_paths.py`** - Custom Cache Directories

   - Configure custom model cache paths
   - Configure custom vector cache paths
   - Verify directory creation
   - Useful for production deployments

3. **`03_append_mode.py`** - Append vs Replace
   - `append=False` - Replace entire collection (default)
   - `append=True` - Add to existing collection
   - Practical use cases for each mode

### Advanced Features

4. **`04_similarity_algorithms.py`** - Similarity Metrics

   - Compare cosine, dot product, euclidean, and derrida metrics
   - Understand when to use each algorithm
   - See how results differ by metric

5. **`05_temporary_search.py`** - Non-Persistent Search

   - Search without saving to disk (`cache=False`)
   - Useful for one-time queries
   - Good for testing and dynamic collections

6. **`06_custom_key_fields.py`** - Custom Document Fields
   - Use fields other than "text" for vectorization
   - Handle product descriptions, titles, etc.
   - Work with nested document structures

### Special Topics

7. **`07_offline_mode.py`** - Offline Model Usage

   - Download and save models for offline use
   - Use cached models without internet
   - Essential for air-gapped environments

8. **`08_store_api.py`** - Low-Level Store API

   - Direct vector store manipulation
   - Custom embedding functions
   - In-memory operations
   - Advanced users only

9. **`09_utility_functions.py`** - Helper Utilities
   - `stringify_nonstring_target_values()` - Convert non-strings
   - Handle numeric IDs, booleans, floats
   - Prepare data for vectorization

### Performance & Applications

10. **`10_benchmarking.py`** - Performance Benchmarks

    - Measure embedding generation time
    - Track save and search performance
    - Monitor memory usage
    - Compare append vs replace operations

11. **`11_real_world_use_cases.py`** - Practical Applications

    - Documentation search
    - FAQ matching
    - Product recommendation
    - Content deduplication

12. **`12_dot_notation_access.py`** - Nested Field Access
    - Use dot notation in key parameter: `"parent.child"`
    - Vectorize deeply nested fields
    - Multi-level nesting: `"a.b.c.d"`
    - Switch between different nested keys

## Running Examples

### Prerequisites

Ensure microvector is installed:

```bash
pip install microvector
```

Or for development:

```bash
git clone https://github.com/loganpowell/microvector.git
cd microvector
uv sync
```

### Running Individual Examples

```bash
# Basic usage
python examples/01_basic_usage.py

# Try append mode
python examples/03_append_mode.py

# Compare similarity algorithms
python examples/04_similarity_algorithms.py

# Real-world applications
python examples/11_real_world_use_cases.py
```

### Running All Examples

```bash
# Run all examples sequentially
for f in examples/*.py; do
    echo "Running $f..."
    python "$f"
    echo "---"
done
```

## Example Categories

### For Beginners

- Start with `01_basic_usage.py`
- Then try `03_append_mode.py`
- Move to `06_custom_key_fields.py`

### For Production Use

- `02_custom_paths.py` - Configure cache locations
- `07_offline_mode.py` - Offline model setup
- `10_benchmarking.py` - Performance testing

### For Advanced Users

- `08_store_api.py` - Low-level API
- `04_similarity_algorithms.py` - Algorithm selection
- `09_utility_functions.py` - Helper utilities

### For Specific Use Cases

- `11_real_world_use_cases.py` - Complete applications
- `05_temporary_search.py` - Ad-hoc searches

## Common Patterns

### Pattern 1: Basic Save & Search

```python
from microvector import Client

client = Client()
client.save(partition="docs", collection=[{"text": "..."}])
results = client.search(term="query", partition="docs", key="text")
```

### Pattern 2: Custom Configuration

```python
client = Client(
    cache_models="/path/to/models",
    cache_vectors="/path/to/vectors",
    embedding_model="model-name"
)
```

### Pattern 3: Append to Collection

```python
# Initial save
client.save(partition="data", collection=docs1, append=False)
# Add more later
client.save(partition="data", collection=docs2, append=True)
```

### Pattern 4: Temporary Search

```python
results = client.search(
    term="query",
    partition="temp",
    key="text",
    collection=documents,
    cache=False
)
```

## Tips

- **First-time run**: Model download may take a few minutes
- **Cache location**: Default is `~/.cache/microvector/`
- **Embedding model**: Default is `avsolatorio/GIST-small-Embedding-v0`
- **Top_k**: Adjust based on how many results you need
- **Similarity score**: Higher is better (0.0 to 1.0+ range)

## Troubleshooting

### Import Errors

```bash
pip install microvector --upgrade
```

### Model Download Issues

- Check internet connection
- Ensure sufficient disk space (~500MB for model)
- Try using offline mode after first successful download

### Performance Issues

- Reduce dataset size for testing
- Use `cache=True` to persist vector stores
- Consider using `dot` algorithm for faster searches

## Contributing

Have a great example? Submit a PR! Good examples:

- Demonstrate a specific feature clearly
- Include helpful comments
- Show practical use cases
- Are self-contained and runnable

## License

Same as microvector - see LICENSE file in repository root.
