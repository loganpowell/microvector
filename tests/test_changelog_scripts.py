#!/usr/bin/env python3
"""
Tests for changelog automation scripts.

Run with: python -m pytest tests/test_changelog_scripts.py -v
"""

import json
import pytest
from scripts import truncate_diff, update_changelog, prepare_benchmark_summary


class TestTruncateDiff:
    """Tests for truncate_diff.py"""

    def test_small_diff_not_truncated(self, tmp_path):
        """Test that small diffs are not truncated"""
        # Create a small diff
        input_file = tmp_path / "small_diff.txt"
        output_file = tmp_path / "output.txt"

        small_content = "diff --git a/test.py b/test.py\n" * 10
        input_file.write_text(small_content)

        stats = truncate_diff(input_file, output_file, max_tokens=1000)

        assert not stats["was_truncated"]
        assert stats["original_tokens"] == stats["truncated_tokens"]
        assert output_file.read_text() == small_content

    def test_large_diff_truncated(self, tmp_path):
        """Test that large diffs are truncated"""
        # Create a large diff
        input_file = tmp_path / "large_diff.txt"
        output_file = tmp_path / "output.txt"

        large_content = "diff --git a/test.py b/test.py\n" * 1000
        input_file.write_text(large_content)

        stats = truncate_diff(input_file, output_file, max_tokens=100)

        assert stats["was_truncated"]
        assert stats["truncated_tokens"] == 100
        assert stats["original_tokens"] > 100
        assert "(diff truncated for brevity)" in output_file.read_text()

    def test_missing_input_file(self, tmp_path):
        """Test handling of missing input file"""
        input_file = tmp_path / "missing.txt"
        output_file = tmp_path / "output.txt"

        stats = truncate_diff(input_file, output_file, max_tokens=1000)

        assert not stats["was_truncated"]
        assert stats["original_tokens"] > 0  # "No functional code changes" has tokens
        assert output_file.read_text() == "No functional code changes"

    def test_empty_diff(self, tmp_path):
        """Test handling of empty diff file"""
        input_file = tmp_path / "empty.txt"
        output_file = tmp_path / "output.txt"

        input_file.write_text("")

        stats = truncate_diff(input_file, output_file, max_tokens=1000)

        assert not stats["was_truncated"]
        assert output_file.read_text() == "No functional code changes"


class TestUpdateChangelog:
    """Tests for update_changelog.py"""

    def test_create_new_changelog(self, tmp_path):
        """Test creating a new CHANGELOG.md"""
        changelog = tmp_path / "CHANGELOG.md"
        entry = tmp_path / "entry.md"

        entry.write_text("## v1.0.0 - 2025-01-01\n\n### Added\n- New feature")

        result = update_changelog(
            changelog,
            entry,
            "v1.0.0",
            "https://github.com/test/repo",
            create_if_missing=True,
        )

        assert result is True
        assert changelog.exists()
        content = changelog.read_text()
        assert "# Changelog" in content
        assert "v1.0.0" in content
        assert "releases/tag/v1.0.0" in content

    def test_update_existing_changelog(self, tmp_path):
        """Test updating an existing CHANGELOG.md"""
        changelog = tmp_path / "CHANGELOG.md"
        entry = tmp_path / "entry.md"

        # Create existing changelog
        changelog.write_text(
            """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.0] - 2024-12-01

### Added
- Initial release
"""
        )

        # Create new entry
        entry.write_text("## v0.2.0 - 2025-01-01\n\n### Added\n- New feature")

        result = update_changelog(
            changelog, entry, "v0.2.0", "https://github.com/test/repo"
        )

        assert result is True
        content = changelog.read_text()

        # Verify new entry comes before old entry
        v2_pos = content.find("v0.2.0")
        v1_pos = content.find("v0.1.0")
        assert v2_pos < v1_pos
        assert "releases/tag/v0.2.0" in content

    def test_missing_entry_file(self, tmp_path):
        """Test handling of missing entry file"""
        changelog = tmp_path / "CHANGELOG.md"
        entry = tmp_path / "missing.md"

        changelog.write_text("# Changelog\n")

        result = update_changelog(
            changelog, entry, "v1.0.0", "https://github.com/test/repo"
        )

        assert result is False


class TestPrepareBenchmarks:
    """Tests for prepare_benchmarks.py"""

    def test_process_benchmark_metrics(self, tmp_path):
        """Test processing benchmark metrics"""
        benchmark_dir = tmp_path / "benchmarks"
        benchmark_dir.mkdir()
        output = tmp_path / "summary.txt"

        # Create sample benchmark data
        metrics = {
            "embedding_500_rate": 1234.5,
            "embedding_2000_rate": 1100.2,
            "search_500_time": 0.0123,
            "memory_delta_mb": 45.6,
        }

        metrics_file = benchmark_dir / "benchmark_metrics.json"
        metrics_file.write_text(json.dumps(metrics))

        stats = prepare_benchmark_summary(benchmark_dir, output)

        assert stats["has_benchmarks"] is True
        assert stats["files_found"] == 1
        assert stats["metrics_found"] == 4

        content = output.read_text()
        assert "Performance Metrics" in content
        assert "1234.5 docs/sec" in content
        assert "12.3ms" in content  # 0.0123 * 1000
        assert "45.6MB" in content

    def test_missing_benchmark_dir(self, tmp_path):
        """Test handling of missing benchmark directory"""
        benchmark_dir = tmp_path / "missing"
        output = tmp_path / "summary.txt"

        stats = prepare_benchmark_summary(benchmark_dir, output)

        assert stats["has_benchmarks"] is False
        assert stats["files_found"] == 0
        assert "No benchmark data available" in output.read_text()

    def test_empty_benchmark_dir(self, tmp_path):
        """Test handling of empty benchmark directory"""
        benchmark_dir = tmp_path / "empty"
        benchmark_dir.mkdir()
        output = tmp_path / "summary.txt"

        stats = prepare_benchmark_summary(benchmark_dir, output)

        assert stats["has_benchmarks"] is False
        assert stats["files_found"] == 0
        assert "No benchmark data available" in output.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
