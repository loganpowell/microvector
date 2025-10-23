# Microvector Tests

This directory contains the test suite for the microvector library.

## Test Structure

- **`test_client.py`**: Tests for the high-level `Client` API

  - Initialization and configuration
  - Save operations
  - Search operations
  - Edge cases and error handling
  - Integration tests

- **`test_store.py`**: Tests for the `Store` class

  - Document management (add, remove)
  - Persistence (save, load)
  - Querying and similarity search
  - Different similarity algorithms

- **`test_utils.py`**: Tests for utility functions

  - `stringify_nonstring_target_values` function
  - Type conversion and data transformation

- **`conftest.py`**: Shared pytest configuration and fixtures

## Running Tests

### Run all tests

```bash
uv run pytest
```

### Run specific test file

```bash
uv run pytest tests/test_client.py
```

### Run specific test class

```bash
uv run pytest tests/test_client.py::TestClientSearch
```

### Run specific test

```bash
uv run pytest tests/test_client.py::TestClientSearch::test_search_returns_results
```

### Run with coverage

```bash
uv run pytest --cov=microvector --cov-report=html
```

### Run with verbose output

```bash
uv run pytest -v
```

### Run tests matching a pattern

```bash
uv run pytest -k "search"
```

### Skip slow tests

```bash
uv run pytest -m "not slow"
```

## Test Coverage

The test suite covers:

- ✅ Client initialization with different configurations
- ✅ Saving collections to vector stores
- ✅ Searching with various parameters
- ✅ Temporary (non-cached) searches
- ✅ Different similarity algorithms (cosine, dot, euclidean, derrida)
- ✅ Persistence and loading from disk
- ✅ Edge cases (empty collections, missing keys, etc.)
- ✅ Multiple partitions
- ✅ Data type conversions
- ✅ Store operations (add, remove, query)

## Writing New Tests

When adding new tests:

1. Follow the existing structure with test classes
2. Use descriptive test names that explain what is being tested
3. Use fixtures from `conftest.py` for shared setup
4. Add docstrings to test functions
5. Mark slow tests with `@pytest.mark.slow`
6. Mark integration tests with `@pytest.mark.integration`

Example:

```python
class TestNewFeature:
    """Tests for new feature."""

    def test_feature_works(self, client, sample_collection):
        """Test that the feature works as expected."""
        # Arrange
        expected = "value"

        # Act
        result = client.new_feature()

        # Assert
        assert result == expected
```

## Continuous Integration

Tests are run automatically on:

- Every push to the repository
- Every pull request
- Before releases

All tests must pass before merging changes.
