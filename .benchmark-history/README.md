# Benchmarking System

This directory contains the benchmarking infrastructure for tracking performance over time.

## Overview

The benchmarking system automatically runs on every release and tracks:

- **Embedding performance** (documents/second for various dataset sizes)
- **Search performance** (query latency)
- **Memory usage** (total and delta)
- **Client workflow** (end-to-end save + search operations)

## Running Benchmarks Locally

### Run all benchmarks:

```bash
pytest tests/test_benchmarks.py -v -s
```

### Run specific benchmark:

```bash
pytest tests/test_benchmarks.py::TestEmbeddingPerformance::test_embedding_500_documents -v -s
```

### With detailed output:

```bash
pytest tests/test_benchmarks.py -v -s --tb=short
```

## Benchmark Tests

### Embedding Performance

- `test_embedding_50_documents` - Small dataset (50 docs)
- `test_embedding_500_documents` - Medium dataset (500 docs)
- `test_embedding_2000_documents` - Large dataset (2000 docs)

### Search Performance

- `test_search_in_500_documents` - Search in 500 doc collection
- `test_search_in_2000_documents` - Search in 2000 doc collection

### Client API Performance

- `test_client_save_and_search_workflow` - Full save + search workflow

### Memory Usage

- `test_memory_usage_large_collection` - Memory footprint for large collections

## CI/CD Integration

### GitHub Actions

The benchmarks run automatically on every release via `.github/workflows/benchmark-on-release.yml`:

1. **On Release**: Triggered when a new release is published
2. **Test Matrix**: Runs on Python 3.10, 3.11, and 3.12
3. **Artifacts**: Results stored for 90 days
4. **Job Summary**: Performance report in GitHub Actions UI
5. **History**: Committed to `.benchmark-history/` directory

### Manual Trigger

You can manually trigger benchmarks from the GitHub Actions tab:

1. Go to Actions → "Benchmark & Test on Release"
2. Click "Run workflow"
3. Select branch and run

## Viewing Results

### GitHub Actions UI

After each run, check the **Job Summary** tab for:

- Test pass/fail status
- Performance metrics table
- Performance insights
- Historical comparison

### Artifacts

Download artifacts from the Actions run:

- `benchmark-results-python-X.Y/` - Contains JSON metrics and raw output

### Local History

View benchmark history locally:

```bash
python scripts/visualize_benchmarks.py
```

This shows:

- All historical benchmark runs
- Version-to-version comparisons
- Performance trends

## Benchmark History

Benchmark results are automatically committed to `.benchmark-history/` on each release:

```
.benchmark-history/
├── benchmark_v0.1.0_py3.10_20250123_120000.json
├── benchmark_v0.1.0_py3.11_20250123_120100.json
├── benchmark_v0.1.1_py3.10_20250124_140000.json
└── ...
```

This provides:

- ✅ Permanent historical record
- ✅ Version-to-version tracking
- ✅ No expiration (unlike artifacts)
- ✅ Easy to analyze trends

## Metrics Collected

### Performance Metrics

| Metric                 | Description                       | Target         |
| ---------------------- | --------------------------------- | -------------- |
| `embedding_50_time`    | Time to embed 50 docs (seconds)   | < 0.5s         |
| `embedding_500_time`   | Time to embed 500 docs (seconds)  | < 2.0s         |
| `embedding_2000_time`  | Time to embed 2000 docs (seconds) | < 8.0s         |
| `embedding_*_rate`     | Documents per second              | > 100 docs/sec |
| `search_500_time`      | Query time in 500 docs (seconds)  | < 0.1s         |
| `search_2000_time`     | Query time in 2000 docs (seconds) | < 0.2s         |
| `client_workflow_time` | Save + search (seconds)           | < 3.0s         |

### Resource Metrics

| Metric            | Description                      |
| ----------------- | -------------------------------- |
| `memory_total_mb` | Total memory used (MB)           |
| `memory_delta_mb` | Memory increase during test (MB) |
| `cpu_percent`     | CPU utilization (%)              |

## Performance Targets

### Embedding (500 docs)

- ✅ **Excellent**: > 100 docs/sec
- ✅ **Good**: > 50 docs/sec
- ⚠️ **Below Target**: < 50 docs/sec

### Search Latency

- ✅ **Excellent**: < 50ms
- ✅ **Good**: < 100ms
- ⚠️ **Slow**: > 100ms

### Memory Efficiency

- ✅ **Efficient**: < 100MB delta
- ⚠️ **High**: > 100MB delta

## Adding New Benchmarks

1. **Add test to `tests/test_benchmarks.py`:**

```python
def test_my_new_benchmark(self, metrics_file: Path) -> None:
    """Benchmark: Description of what this tests."""
    metrics = PerformanceMetrics("my_benchmark_name")

    metrics.start()
    # Your code to benchmark
    result = some_operation()
    metrics.stop()

    # Verify correctness
    assert result is not None

    # Store metrics
    result = metrics.get_metrics()
    result["custom_metric"] = "value"

    TestEmbeddingPerformance._save_metrics(metrics_file, result)

    print(f"\n⏱️  My benchmark: {result['duration_seconds']}s")
```

2. **Update GitHub Action** (if needed) to parse and display new metrics

3. **Update targets** in this README

## Troubleshooting

### Benchmarks Failing

- Check if `psutil` is installed: `pip install psutil`
- Run with verbose output: `pytest tests/test_benchmarks.py -vvs`
- Check resource availability (CPU, memory)

### Missing Metrics

- Ensure test prints results in expected format
- Check `benchmark_results.txt` artifact
- Verify regex patterns in GitHub Action

### GitHub Action Not Running

- Verify release was published (not draft)
- Check workflow file syntax
- Look for errors in Actions tab

## Dependencies

- `pytest` - Test framework
- `psutil` - Resource monitoring (optional)
- `numpy` - Array operations
- `sentence-transformers` - Embedding model

## Best Practices

1. **Run locally first** before relying on CI
2. **Compare with previous runs** to detect regressions
3. **Check multiple Python versions** for compatibility
4. **Review memory usage** for large datasets
5. **Monitor trends** over time using history

## Questions?

- Check GitHub Actions logs for detailed output
- Review `.benchmark-history/` for historical data
- Run `python scripts/visualize_benchmarks.py` for analysis
