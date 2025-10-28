# Changelog Automation Scripts

This directory contains reusable Python scripts for automating changelog generation and release management. These scripts are used by the GitHub Actions workflows but can also be run independently for testing and manual operations.

## Scripts

### `truncate_diff.py`

Truncates git diffs to a specified token limit using tiktoken, ensuring they fit within AI model constraints.

**Usage:**

```bash
# Basic usage
python scripts/truncate_diff.py input.diff output.diff

# Specify max tokens
python scripts/truncate_diff.py input.diff output.diff --max-tokens 3000

# Quiet mode (no output)
python scripts/truncate_diff.py input.diff output.diff --quiet
```

**Parameters:**

- `input`: Path to input diff file
- `output`: Path to output truncated diff file
- `--max-tokens`: Maximum number of tokens (default: 3000)
- `--encoding`: Tiktoken encoding name (default: cl100k_base)
- `--quiet`: Suppress output

**Example:**

```bash
# Generate a diff and truncate it
git diff v0.1.25..v0.1.26 > full_diff.txt
python scripts/truncate_diff.py full_diff.txt truncated.txt --max-tokens 2000

# For better results, filter to only functional code changes
# --diff-filter=ACM: Only Added, Copied, Modified (excludes Deleted, Renamed)
git diff --diff-filter=ACM v0.1.25..v0.1.26 -- \
  ':!*.md' ':!*.yml' ':!*.yaml' ':!*.sh' ':!*.json' \
  > functional_diff.txt
python scripts/truncate_diff.py functional_diff.txt truncated.txt --max-tokens 3000
```

### `update_changelog.py`

Updates CHANGELOG.md with new release entries, adding release links and preserving structure.

**Usage:**

```bash
python scripts/update_changelog.py \
  --entry changelog_entry.md \
  --version v0.1.26 \
  --repo https://github.com/owner/repo
```

**Parameters:**

- `--changelog`: Path to CHANGELOG.md (default: CHANGELOG.md)
- `--entry`: Path to the new changelog entry file (required)
- `--version`: Version string, e.g., v0.1.26 (required)
- `--repo`: GitHub repository URL (required)
- `--no-create`: Do not create CHANGELOG.md if it doesn't exist

**Example:**

```bash
# Create an entry file
cat > new_entry.md << EOF
## v0.1.26 - 2025-01-15

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug Z
EOF

# Update the changelog
python scripts/update_changelog.py \
  --entry new_entry.md \
  --version v0.1.26 \
  --repo https://github.com/loganpowell/microvector
```

### `prepare_benchmarks.py`

Processes benchmark JSON files and creates human-readable summaries for release notes.

**Usage:**

```bash
# Basic usage
python scripts/prepare_benchmarks.py

# Specify custom paths
python scripts/prepare_benchmarks.py \
  --input ./benchmark-results \
  --output summary.txt
```

**Parameters:**

- `--input`: Directory containing benchmark results (default: ./benchmark-data)
- `--output`: Output summary file path (default: benchmark_summary.txt)
- `--quiet`: Suppress output

**Example:**

```bash
# Process benchmarks from a specific directory
python scripts/prepare_benchmarks.py \
  --input ./my-benchmarks \
  --output perf_summary.txt
```

## Shell Scripts

### `get_release_range.sh`

Provides shared utilities for determining commit ranges between releases. This is sourced by other scripts.

**Functions:**

- `get_release_range()`: Determines upper and lower commit bounds for a release
- `get_commits_for_range()`: Gets filtered commits between bounds
- `get_commits_with_hash()`: Gets commits with short hash
- `get_tag_date()`: Gets the date of a tag
- `get_changelog_anchor()`: Creates GitHub anchor for changelog links

**Usage:**

```bash
# Source the utilities
source scripts/get_release_range.sh

# Get the commit range for v0.1.26
get_release_range "v0.1.26" "true"

# Now use the exported variables
echo "Previous tag: $PREV_TAG"
echo "Lower bound: $LOWER_BOUND"
echo "Upper bound: $UPPER_BOUND"
```

## Testing

Run the test suite to validate the scripts:

```bash
# Install test dependencies
uv pip install pytest

# Or with pip
pip install pytest

# Run tests
python -m pytest tests/test_changelog_scripts.py -v

# Run with coverage
uv pip install pytest-cov
python -m pytest tests/test_changelog_scripts.py -v --cov=scripts
```

## Dependencies

### Python Scripts

- **tiktoken**: For token counting and truncation

  ```bash
  # Using pip
  pip install tiktoken

  # Using uv (faster)
  uv pip install tiktoken
  ```

### Shell Scripts

- **git**: For commit history and diffs
- **gh** (GitHub CLI): For GitHub Models integration (optional, only for AI generation)

## Integration with GitHub Actions

These scripts are used in `.github/workflows/update-changelog.yml`:

1. **truncate_diff.py**: Limits diff size for AI model consumption
2. **prepare_benchmarks.py**: Creates performance summaries from benchmark data
3. **update_changelog.py**: Inserts new entries into CHANGELOG.md
4. **get_release_range.sh**: Determines correct commit ranges for releases

## Manual Workflow Example

Here's a complete example of manually generating a changelog for a release:

```bash
# 1. Get the commit range
source scripts/get_release_range.sh
get_release_range "v0.1.26" "false"

# 2. Generate the diff (filter non-functional files and deletions/renames)
# --diff-filter=ACM: Only Added, Copied, Modified (excludes Deleted, Renamed)
git diff --diff-filter=ACM ${LOWER_BOUND}..${UPPER_BOUND} -- \
  ':!*.md' ':!*.yml' ':!*.yaml' ':!*.sh' ':!*.json' \
  > functional_diff.txt

# 3. Truncate the diff
python scripts/truncate_diff.py \
  functional_diff.txt \
  truncated_diff.txt \
  --max-tokens 3000

# 4. Create a changelog entry (manually or with AI)
cat > entry.md << EOF
## v0.1.26 - 2025-01-15

### Added
- Feature description

### Fixed
- Bug fix description
EOF

# 5. Update CHANGELOG.md
python scripts/update_changelog.py \
  --entry entry.md \
  --version v0.1.26 \
  --repo https://github.com/loganpowell/microvector

# 6. Commit the changes
git add CHANGELOG.md
git commit -m "Update CHANGELOG for v0.1.26"
```

## Troubleshooting

### Import errors when running tests

Make sure you're running tests from the project root:

```bash
cd /path/to/microvector
python -m pytest tests/test_changelog_scripts.py -v
```

### Tiktoken not found

Install tiktoken:

```bash
# Using uv (recommended, faster)
uv pip install tiktoken

# Or using pip
pip install tiktoken
```

### Script fails with missing file

Check that you're running from the project root directory where the scripts expect to find files.
