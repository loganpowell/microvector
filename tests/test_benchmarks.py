"""
Benchmark tests for microvector performance tracking.

These tests measure performance metrics over time to track improvements
and detect regressions. Results are logged and can be used for CI/CD
reporting.
"""

import time
import os
from typing import Any, Generator
from pathlib import Path
import json
from datetime import datetime

import pytest

import psutil

from microvector import Client
from microvector.store import Store
from microvector.embed import get_embeddings
from microvector.utils import EMBEDDING_MODEL


class PerformanceMetrics:
    """Helper class to capture and store performance metrics."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = 0.0
        self.end_time = 0.0
        self.start_cpu = 0.0
        self.end_cpu = 0.0
        self.start_memory = 0
        self.end_memory = 0
        self.process = psutil.Process(os.getpid())

    def start(self) -> None:
        """Start measuring performance."""
        self.start_time = time.time()
        self.start_cpu = self.process.cpu_percent()
        self.start_memory = self.process.memory_info().rss

    def stop(self) -> None:
        """Stop measuring performance."""
        self.end_time = time.time()
        self.end_cpu = self.process.cpu_percent()
        self.end_memory = self.process.memory_info().rss

    def get_metrics(self) -> dict[str, Any]:
        """Get collected metrics."""
        metrics: dict[str, Any] = {
            "test_name": self.test_name,
            "duration_seconds": round(self.end_time - self.start_time, 3),
            "timestamp": datetime.now().isoformat(),
        }

        metrics.update(
            {
                "cpu_percent": round(self.end_cpu, 2),
                "memory_mb": round(self.end_memory / 1024 / 1024, 2),
                "memory_delta_mb": round((self.end_memory - self.start_memory) / 1024 / 1024, 2),
            }
        )

        return metrics


@pytest.fixture
def benchmark_data_small() -> list[dict[str, str]]:
    """Small dataset for benchmarking (50 documents)."""
    return [{"text": f"Document {i} about topic {i % 10} with some content", "id": str(i)} for i in range(50)]


@pytest.fixture
def benchmark_data_medium() -> list[dict[str, str]]:
    """Medium dataset for benchmarking (500 documents)."""
    return [
        {
            "text": f"Document {i} about topic {i % 50} with detailed content",
            "id": str(i),
        }
        for i in range(500)
    ]


@pytest.fixture
def benchmark_data_large() -> list[dict[str, str]]:
    """Large dataset for benchmarking (2000 documents)."""
    return [
        {
            "text": f"Document {i} about topic {i % 100} with extensive content",
            "id": str(i),
        }
        for i in range(2000)
    ]


@pytest.fixture
def metrics_file(tmp_path: Path) -> Path:
    """Create a temporary file for storing benchmark metrics."""
    return tmp_path / "benchmark_metrics.json"


class TestEmbeddingPerformance:
    """Benchmark tests for embedding generation."""

    @pytest.mark.benchmark
    def test_embedding_50_documents(
        self,
        benchmark_data_small: list[dict[str, str]],
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Generate embeddings for 50 documents."""
        metrics = PerformanceMetrics("embedding_50_docs")

        texts = [doc["text"] for doc in benchmark_data_small]

        metrics.start()
        embeddings = get_embeddings(texts, cache_folder=shared_model_cache)
        metrics.stop()

        # Verify correctness
        assert len(embeddings) == 50

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 50
        result["embeddings_per_second"] = round(50 / result["duration_seconds"], 2)

        self._save_metrics(metrics_file, result)

        # Print for visibility
        print(f"\n⏱️  Embedding 50 docs: {result['duration_seconds']}s ({result['embeddings_per_second']} docs/sec)")

    @pytest.mark.benchmark
    def test_embedding_500_documents(
        self,
        benchmark_data_medium: list[dict[str, str]],
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Generate embeddings for 500 documents."""
        metrics = PerformanceMetrics("embedding_500_docs")

        texts = [doc["text"] for doc in benchmark_data_medium]

        metrics.start()
        embeddings = get_embeddings(texts, cache_folder=shared_model_cache)
        metrics.stop()

        # Verify correctness
        assert len(embeddings) == 500

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 500
        result["embeddings_per_second"] = round(500 / result["duration_seconds"], 2)

        self._save_metrics(metrics_file, result)

        print(f"\n⏱️  Embedding 500 docs: {result['duration_seconds']}s ({result['embeddings_per_second']} docs/sec)")

    @pytest.mark.benchmark
    def test_embedding_2000_documents(
        self,
        benchmark_data_large: list[dict[str, str]],
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Generate embeddings for 2000 documents."""
        metrics = PerformanceMetrics("embedding_2000_docs")

        texts = [doc["text"] for doc in benchmark_data_large]

        metrics.start()
        embeddings = get_embeddings(texts, cache_folder=shared_model_cache)
        metrics.stop()

        # Verify correctness
        assert len(embeddings) == 2000

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 2000
        result["embeddings_per_second"] = round(2000 / result["duration_seconds"], 2)

        self._save_metrics(metrics_file, result)

        print(f"\n⏱️  Embedding 2000 docs: {result['duration_seconds']}s ({result['embeddings_per_second']} docs/sec)")

    @staticmethod
    def _save_metrics(metrics_file: Path, result: dict[str, Any]) -> None:
        """Append metrics to file."""
        metrics_list = []
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                metrics_list = json.load(f)

        metrics_list.append(result)

        with open(metrics_file, "w") as f:
            json.dump(metrics_list, f, indent=2)


class TestSearchPerformance:
    """Benchmark tests for search operations."""

    @pytest.mark.benchmark
    def test_search_in_500_documents(
        self,
        benchmark_data_medium: list[dict[str, str]],
        tmp_path: Path,
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Search in 500 document collection."""
        metrics = PerformanceMetrics("search_500_docs")

        # Setup: Create store with 500 documents using shared cache
        embedding_fn = lambda docs: get_embeddings(docs, key="text", cache_folder=shared_model_cache)
        store = Store(
            collection=benchmark_data_medium,
            key="text",
            algo="cosine",
            embedding_function=embedding_fn,
        )

        query = "document about topic"

        # Measure search performance
        metrics.start()
        results = store.query(query, top_k=10)
        metrics.stop()

        # Verify correctness
        assert len(results) == 10

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 500
        result["top_k"] = 10
        result["searches_per_second"] = round(1 / result["duration_seconds"], 2)

        TestEmbeddingPerformance._save_metrics(metrics_file, result)

        print(f"\n🔍 Search in 500 docs: {result['duration_seconds']}s")

    @pytest.mark.benchmark
    def test_search_in_2000_documents(
        self,
        benchmark_data_large: list[dict[str, str]],
        tmp_path: Path,
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Search in 2000 document collection."""
        metrics = PerformanceMetrics("search_2000_docs")

        # Setup: Create store with 2000 documents using shared cache
        embedding_fn = lambda docs: get_embeddings(docs, key="text", cache_folder=shared_model_cache)
        store = Store(
            collection=benchmark_data_large,
            key="text",
            algo="cosine",
            embedding_function=embedding_fn,
        )

        query = "document about topic"

        # Measure search performance
        metrics.start()
        results = store.query(query, top_k=10)
        metrics.stop()

        # Verify correctness
        assert len(results) == 10

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 2000
        result["top_k"] = 10
        result["searches_per_second"] = round(1 / result["duration_seconds"], 2)

        TestEmbeddingPerformance._save_metrics(metrics_file, result)

        print(f"\n🔍 Search in 2000 docs: {result['duration_seconds']}s")


class TestClientPerformance:
    """Benchmark tests for Client API operations."""

    @pytest.mark.benchmark
    def test_client_save_and_search_workflow(
        self,
        benchmark_data_medium: list[dict[str, str]],
        tmp_path: Path,
        shared_model_cache: str,
        metrics_file: Path,
    ) -> None:
        """Benchmark: Complete save and search workflow with Client."""
        metrics = PerformanceMetrics("client_workflow_500_docs")

        cache_models = shared_model_cache
        cache_vectors = str(tmp_path / "vectors")

        client = Client(
            cache_models=cache_models,
            cache_vectors=cache_vectors,
            embedding_model=EMBEDDING_MODEL,
        )

        metrics.start()

        # Save collection
        client.save(
            partition_name="benchmark_test",
            collection=benchmark_data_medium,
        )

        # Perform search
        results = client.search(
            term="document about topic",
            partition_name="benchmark_test",
            key="text",
            top_k=10,
        )

        metrics.stop()

        # Verify correctness
        assert results is not None
        assert len(results) == 10

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 500
        result["operations"] = "save + search"

        TestEmbeddingPerformance._save_metrics(metrics_file, result)

        print(f"\n💾 Client workflow (500 docs): {result['duration_seconds']}s")


class TestMemoryUsage:
    """Benchmark tests for memory efficiency."""

    @pytest.mark.benchmark
    def test_memory_usage_large_collection(
        self,
        benchmark_data_large: list[dict[str, str]],
        metrics_file: Path,
        shared_model_cache: str,
    ) -> None:
        """Benchmark: Memory usage with large collection."""
        metrics = PerformanceMetrics("memory_usage_2000_docs")

        metrics.start()

        # Create store with shared cache to avoid model reloading
        embedding_fn = lambda docs: get_embeddings(docs, key="text", cache_folder=shared_model_cache)
        store = Store(
            collection=benchmark_data_large,
            key="text",
            algo="cosine",
            embedding_function=embedding_fn,
        )

        # Perform a query to ensure everything is loaded
        _ = store.query("test query", top_k=5)

        metrics.stop()

        # Store metrics
        result = metrics.get_metrics()
        result["documents"] = 2000

        TestEmbeddingPerformance._save_metrics(metrics_file, result)

        print(f"\n💾 Memory usage (2000 docs): {result['memory_mb']} MB (delta: {result['memory_delta_mb']} MB)")


@pytest.fixture(scope="session", autouse=True)
def save_final_metrics(request: Any, tmp_path_factory: Any) -> Generator[None, None, None]:
    """Save all collected metrics to a file for CI/CD reporting."""
    # This will run after all tests complete
    yield

    # Get the benchmark metrics file path
    # Note: tmp_path_factory creates session-scoped temp directories
    metrics_dir = tmp_path_factory.getbasetemp() / "benchmark_results"
    metrics_dir.mkdir(exist_ok=True)

    final_metrics_file = metrics_dir / "final_benchmark_metrics.json"

    # If running in CI, also save to a known location
    if os.getenv("CI"):
        ci_metrics_file = Path("benchmark_results.json")
        ci_metrics_file.parent.mkdir(exist_ok=True)

        print(f"\n📊 Benchmark metrics saved to: {ci_metrics_file}")
