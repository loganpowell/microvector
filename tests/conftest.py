"""
Pytest configuration and shared fixtures for microvector tests.
"""

import logging
import tempfile
from pathlib import Path
from collections.abc import Generator

import pytest


# Configure logging for tests
logging.basicConfig(
    format="%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.WARNING,  # Less verbose during testing
    force=True,
)


@pytest.fixture(scope="session")
def shared_model_cache() -> Generator[str, None, None]:
    """
    Session-scoped model cache directory.

    This is shared across all tests to avoid re-downloading the HuggingFace
    model for every test. Uses a persistent cache directory so the model
    is downloaded once and reused across test runs.
    """
    # Use a persistent cache directory in the project
    cache_dir = Path(__file__).parent.parent / ".test_model_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    yield str(cache_dir)
    # Note: We don't clean up the cache directory to enable reuse across test runs


@pytest.fixture(scope="session")
def sample_documents():
    """Shared sample documents for testing."""
    return [
        {"text": "Machine learning is a subset of artificial intelligence"},
        {"text": "Python is a popular programming language"},
        {"text": "Neural networks can learn complex patterns"},
        {"text": "Data science involves analyzing large datasets"},
        {"text": "Cloud computing provides scalable infrastructure"},
    ]


def pytest_configure(config):  # type: ignore
    """Configure pytest with custom markers."""
    config.addinivalue_line(  # type: ignore
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")  # type: ignore
    config.addinivalue_line("markers", "benchmark: marks tests as performance benchmarks")  # type: ignore
