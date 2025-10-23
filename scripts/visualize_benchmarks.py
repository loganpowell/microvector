#!/usr/bin/env python3
"""
Visualize benchmark history from stored results.

Usage:
    python scripts/visualize_benchmarks.py
"""

import json
from pathlib import Path
from typing import Any
from datetime import datetime


def load_benchmark_history() -> list[dict[str, Any]]:
    """Load all benchmark history files."""
    history_dir = Path(".benchmark-history")

    if not history_dir.exists():
        print("⚠️  No benchmark history found")
        return []

    benchmarks = []
    for file in sorted(history_dir.glob("benchmark_*.json")):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                benchmarks.append(data)
        except Exception as e:
            print(f"⚠️  Error loading {file}: {e}")

    return benchmarks


def print_benchmark_summary(benchmarks: list[dict[str, Any]]) -> None:
    """Print a summary of benchmark results."""
    if not benchmarks:
        print("No benchmarks to display")
        return

    print("\n" + "=" * 80)
    print("📊 BENCHMARK HISTORY SUMMARY")
    print("=" * 80 + "\n")

    # Sort by timestamp
    benchmarks.sort(key=lambda x: x.get("metadata", {}).get("timestamp", ""))

    print(f"Total benchmark runs: {len(benchmarks)}\n")

    # Table header
    print(f"{'Version':<12} {'Python':<8} {'Embed 500':<12} {'Search 500':<12} {'Memory':<10}")
    print("-" * 80)

    for bench in benchmarks:
        metadata = bench.get("metadata", {})
        version = metadata.get("version", "unknown")[:11]
        python_ver = metadata.get("python_version", "N/A")

        embed_time = bench.get("embedding_500_time", "N/A")
        search_time = bench.get("search_500_time", "N/A")
        memory = bench.get("memory_delta_mb", "N/A")

        embed_str = f"{embed_time}s" if embed_time != "N/A" else "N/A"
        search_str = f"{search_time}s" if search_time != "N/A" else "N/A"
        memory_str = f"{memory}MB" if memory != "N/A" else "N/A"

        print(f"{version:<12} {python_ver:<8} {embed_str:<12} {search_str:<12} {memory_str:<10}")

    print("\n" + "=" * 80)

    # Calculate improvements
    if len(benchmarks) >= 2:
        latest = benchmarks[-1]
        previous = benchmarks[-2]

        print("\n📈 LATEST CHANGES (vs previous run):\n")

        if "embedding_500_time" in latest and "embedding_500_time" in previous:
            latest_time = float(latest["embedding_500_time"])
            prev_time = float(previous["embedding_500_time"])
            improvement = ((prev_time - latest_time) / prev_time) * 100

            if improvement > 0:
                print(f"  ✅ Embedding (500 docs): {improvement:+.1f}% faster")
            elif improvement < 0:
                print(f"  ⚠️  Embedding (500 docs): {abs(improvement):.1f}% slower")
            else:
                print(f"  ⚖️  Embedding (500 docs): no change")

        if "search_500_time" in latest and "search_500_time" in previous:
            latest_time = float(latest["search_500_time"])
            prev_time = float(previous["search_500_time"])
            improvement = ((prev_time - latest_time) / prev_time) * 100

            if improvement > 0:
                print(f"  ✅ Search (500 docs): {improvement:+.1f}% faster")
            elif improvement < 0:
                print(f"  ⚠️  Search (500 docs): {abs(improvement):.1f}% slower")
            else:
                print(f"  ⚖️  Search (500 docs): no change")

        print()


def main() -> None:
    """Main entry point."""
    benchmarks = load_benchmark_history()
    print_benchmark_summary(benchmarks)

    if benchmarks:
        print("\n💡 Tip: Benchmark history is stored in .benchmark-history/")
        print("💡 Each release automatically commits new benchmark data\n")


if __name__ == "__main__":
    main()
