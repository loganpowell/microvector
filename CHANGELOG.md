# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.28](https://github.com/loganpowell/microvector/releases/tag/${version}) - 2025-10-23

### Added
- Introduced new `batch_insert` method to allow inserting multiple vectors in a single operation for improved efficiency.
- Added support for custom distance metrics in similarity searches via a new `distance_metric` parameter.

### Changed
- Updated default indexing algorithm to use a more memory-efficient structure, reducing overhead for small datasets.
- Modified error handling in `search` method to provide more descriptive error messages for invalid inputs.

### Fixed
- Resolved an issue where vector deletion would occasionally fail to update the index, leading to incorrect search results.
- Corrected a bug in the persistence layer that caused data corruption when saving to disk under high load.

### Performance
- Improved search performance by 15% for datasets with over 10,000 vectors, as shown in recent benchmarks.
- Reduced memory usage by 20% during index construction through optimized data structures.

<!-- New changes will be added here by the GitHub Action -->

## [v0.1.26](https://github.com/loganpowell/microvector/releases/tag/${version}) - 2025-10-23

### Added

- Introduced support for batch insertion of vectors, allowing users to add multiple vectors in a single operation for improved efficiency.
- Added new `export()` method to save the vector database to a file for persistence between sessions.

### Changed

- Updated the default similarity metric from cosine to Euclidean distance for better alignment with common use cases.
- Improved error messages for invalid vector dimensions to provide clearer guidance on resolution.

### Fixed

- Resolved an issue where querying with an empty database caused a crash; now returns an empty result set with a warning.
- Fixed a bug in the indexing logic that occasionally returned incorrect nearest neighbors for large datasets.

### Performance

- Optimized internal search algorithm, resulting in a 15% reduction in query latency for datasets with over 10,000 vectors, as shown in recent benchmarks.
- Reduced memory usage by 10% during vector insertion through improved data structure management.
