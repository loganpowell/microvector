# microvector

Local vector database that persists to .pickle files.

> This is a small refactor and repackaging of [HyperDB](https://github.com/jdagdelen/hyperDB/tree/main) for easier installation and use in CPU-only environments and .

## Development Setup

This project is configured to automatically install CPU-only PyTorch for maximum compatibility across development environments.

### Quick Start

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Verify setup:**

   ```bash
   uv run setup_dev.py
   ```

3. **Run tests:**

   ```bash
   uv run pytest
   ```

4. **Type checking:**
   ```bash
   uv run pyright
   ```

### What gets installed

- **PyTorch (CPU-only)**: Automatically installed from the PyTorch CPU index
- **Transformers**: Hugging Face transformers library
- **Sentence Transformers**: For embeddings generation
- **NumPy**: Numerical computing

No special flags or manual PyTorch installation needed - just `uv sync` and you're ready to go!

### Dependencies

The project automatically configures:

- PyTorch CPU-only version (no CUDA dependencies)
- All required ML libraries for vector embeddings
- Development tools (pytest, pyright, ruff)

## Usage

```python
from microvector.store import Store

# Create a vector store
store = Store()

# Add documents
documents = [
    {"text": "Hello world", "category": "greeting"},
    {"text": "Machine learning is fun", "category": "tech"},
]
store.add_documents(documents)

# Query similar documents
results = store.query("AI and ML", top_k=5)
print(results)
```

## Features

- 🚀 **Simple API**: Easy to use vector storage and querying
- 💾 **Persistent**: Saves to pickle files
- 🔍 **Multiple similarity metrics**: Cosine, dot product, Euclidean
- 🎯 **Type safe**: Full type annotations with pyright
- ⚡ **CPU optimized**: Designed for CPU-only environments
