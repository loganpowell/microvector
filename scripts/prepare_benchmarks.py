#!/usr/bin/env python3
"""
Prepare benchmark summaries for changelog generation.

This script reads benchmark results from JSON files and creates
human-readable summaries for inclusion in release notes.
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def prepare_benchmark_summary(benchmark_dir: Path, output_path: Path) -> Dict[str, Any]:
    """
    Create a human-readable benchmark summary from JSON metrics.

    Args:
        benchmark_dir: Directory containing benchmark_metrics.json files
        output_path: Path to write the summary text file

    Returns:
        Dictionary with statistics about the benchmarks found
    """
    if not benchmark_dir.exists():
        summary = "No benchmark data available for this release."
        output_path.write_text(summary)
        return {"has_benchmarks": False, "files_found": 0, "metrics_found": 0}

    # Find all metric files
    metric_files = list(benchmark_dir.glob("benchmark_metrics.json"))

    if not metric_files:
        summary = "No benchmark data available for this release."
        output_path.write_text(summary)
        return {"has_benchmarks": False, "files_found": 0, "metrics_found": 0}

    # Read the first one (they should all be similar)
    with open(metric_files[0], "r") as f:
        metrics = json.load(f)

    # Create a human-readable summary
    summary_lines = ["## Performance Metrics\n"]
    metrics_count = 0

    if "embedding_500_rate" in metrics:
        summary_lines.append(
            f"- Embedding rate: {metrics['embedding_500_rate']} docs/sec (500 docs)"
        )
        metrics_count += 1

    if "embedding_2000_rate" in metrics:
        summary_lines.append(
            f"- Embedding rate: {metrics['embedding_2000_rate']} docs/sec (2000 docs)"
        )
        metrics_count += 1

    if "search_500_time" in metrics:
        search_ms = float(metrics["search_500_time"]) * 1000
        summary_lines.append(f"- Search latency: {search_ms:.1f}ms (500 docs)")
        metrics_count += 1

    if "memory_delta_mb" in metrics:
        summary_lines.append(f"- Memory usage: {metrics['memory_delta_mb']}MB delta")
        metrics_count += 1

    summary = "\n".join(summary_lines)

    # Write to file
    output_path.write_text(summary)

    return {
        "has_benchmarks": True,
        "files_found": len(metric_files),
        "metrics_found": metrics_count,
    }


def main():
    """Command-line interface for prepare_benchmark_summary."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Prepare benchmark summaries for changelog generation"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("./benchmark-data"),
        help="Directory containing benchmark results (default: ./benchmark-data)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark_summary.txt"),
        help="Output summary file path (default: benchmark_summary.txt)",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    # Prepare the summary
    stats = prepare_benchmark_summary(args.input, args.output)

    # Print statistics unless quiet
    if not args.quiet:
        if stats["has_benchmarks"]:
            print(f"✅ Benchmark summary created")
            print(f"   Files found: {stats['files_found']}")
            print(f"   Metrics found: {stats['metrics_found']}")
        else:
            print("⚠️  No benchmark data available")

    return 0 if stats["has_benchmarks"] else 1


if __name__ == "__main__":
    sys.exit(main())
