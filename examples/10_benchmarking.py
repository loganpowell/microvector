"""
Benchmarking Example

Demonstrates how to measure performance of microvector operations:
- Embedding generation time
- Save operation performance
- Search operation performance
- Memory usage tracking
"""

import time
import psutil
import os
from microvector import Client
from microvector.embed import get_embeddings


class PerformanceTracker:
    """Simple performance tracking utility."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = 0.0
        self.end_time = 0.0
        self.process = psutil.Process(os.getpid())
        self.start_memory = 0

    def start(self):
        """Start tracking."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        print(f"▶ Starting: {self.operation_name}")

    def stop(self):
        """Stop tracking and report."""
        self.end_time = time.time()
        end_memory = self.process.memory_info().rss

        duration = self.end_time - self.start_time
        memory_delta = (end_memory - self.start_memory) / 1024 / 1024  # MB

        print(f"✓ Completed: {self.operation_name}")
        print(f"  Duration: {duration:.3f} seconds")
        print(f"  Memory delta: {memory_delta:+.2f} MB")
        return duration


def main():
    print("Microvector Performance Benchmarking")
    print("=" * 60)

    client = Client()

    # Benchmark 1: Small dataset (50 documents)
    print("\nBenchmark 1: Small Dataset (50 documents)")
    print("-" * 60)

    small_dataset = [
        {"text": f"Document {i} with content about topic {i % 10}", "id": str(i)}
        for i in range(50)
    ]

    tracker = PerformanceTracker("Save 50 documents")
    tracker.start()
    client.save(
        partition="bench_small",
        collection=small_dataset,
    )
    save_time_small = tracker.stop()

    tracker = PerformanceTracker("Search 50 documents")
    tracker.start()
    results = client.search(
        term="topic content",
        partition="bench_small",
        key="text",
        top_k=10,
    )
    search_time_small = tracker.stop()

    print(f"  Docs/sec (save): {50 / save_time_small:.2f}")
    print(f"  Results found: {len(results)}")

    # Benchmark 2: Medium dataset (500 documents)
    print("\n\nBenchmark 2: Medium Dataset (500 documents)")
    print("-" * 60)

    medium_dataset = [
        {
            "text": f"Document {i} with detailed content about topic {i % 50}",
            "id": str(i),
        }
        for i in range(500)
    ]

    tracker = PerformanceTracker("Save 500 documents")
    tracker.start()
    client.save(
        partition="bench_medium",
        collection=medium_dataset,
    )
    save_time_medium = tracker.stop()

    tracker = PerformanceTracker("Search 500 documents")
    tracker.start()
    results = client.search(
        term="topic content",
        partition="bench_medium",
        key="text",
        top_k=10,
    )
    search_time_medium = tracker.stop()

    print(f"  Docs/sec (save): {500 / save_time_medium:.2f}")
    print(f"  Results found: {len(results)}")

    # Benchmark 3: Direct embedding performance
    print("\n\nBenchmark 3: Direct Embedding Generation")
    print("-" * 60)

    test_texts = [f"Test document {i} for embedding benchmark" for i in range(100)]

    tracker = PerformanceTracker("Generate 100 embeddings")
    tracker.start()
    embeddings = get_embeddings(test_texts)
    embed_time = tracker.stop()

    print(f"  Embeddings/sec: {100 / embed_time:.2f}")
    print(f"  Embedding dimension: {len(embeddings[0])}")

    # Benchmark 4: Append vs Replace
    print("\n\nBenchmark 4: Append vs Replace Performance")
    print("-" * 60)

    initial_docs = [{"text": f"Initial doc {i}", "id": str(i)} for i in range(100)]

    tracker = PerformanceTracker("Initial save (100 docs)")
    tracker.start()
    client.save(
        partition="bench_append",
        collection=initial_docs,
        append=False,
    )
    tracker.stop()

    additional_docs = [
        {"text": f"Additional doc {i}", "id": str(i + 100)} for i in range(50)
    ]

    tracker = PerformanceTracker("Append 50 docs")
    tracker.start()
    client.save(
        partition="bench_append",
        collection=additional_docs,
        append=True,
    )
    append_time = tracker.stop()

    tracker = PerformanceTracker("Replace with 50 docs")
    tracker.start()
    client.save(
        partition="bench_append",
        collection=additional_docs,
        append=False,
    )
    replace_time = tracker.stop()

    print(f"\n  Append time: {append_time:.3f}s")
    print(f"  Replace time: {replace_time:.3f}s")

    # Summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    print(f"Small dataset (50 docs):   {50 / save_time_small:.2f} docs/sec")
    print(f"Medium dataset (500 docs): {500 / save_time_medium:.2f} docs/sec")
    print(f"Embedding generation:      {100 / embed_time:.2f} embeddings/sec")
    print(f"\nSearch is generally fast and scales well with dataset size.")
    print("Append operations preserve existing data and add new vectors.")


if __name__ == "__main__":
    main()
