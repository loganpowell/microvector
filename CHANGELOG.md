# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.00](https://github.com/loganpowell/microvector/releases/tag/v0.3.00) - 2025-10-29

### Changed

- exits with 0 instead of 1 for diff truncation
- enable chanagelog gh action via manual trigger
- fix: enable chanagelog gh action via manual trigger
- pre-check valid tag before deploying changelog action
- fix changelog
- chore: update CHANGELOG for v0.2.18
- dedup changelog link in release notes
- chore: update CHANGELOG for v0.2.18
- chore: update CHANGELOG for v0.2.18
- attempts fix for overwriting changelog
- takes Release titles out of the LLMs hands
- Add PartitionStore class for managing cached vector store partitions…
- Export PartitionStore in package __init__…
- Refactor vector_cache to return PartitionStore instead of query function…
- Refactor Client to use PartitionStore and simplify API…
- Update vector_search to use PartitionStore interface…
- Refactor Store to simplify add/remove operations…
- Refactor append tests to use PartitionStore.add() pattern…
- Update benchmark tests to use PartitionStore pattern…
- Update Client tests for PartitionStore API and naming changes…
- Update dot notation tests for PartitionStore API…
- Add comprehensive tests for Store.remove_document()…
- Update README to document PartitionStore API and new patterns…
- filters out tests from changelog automation diffs

## [v0.2.18](https://github.com/loganpowell/microvector/releases/tag/v0.2.18) - 2025-10-28

### Added

- New scripts for changelog and benchmark preparation
- Tools for truncating diffs for LLM summaries
- Dynamic repository references in release update functions

### Fixed

- Corrected repository references in release update functionality

### Changed

- Truncates diff for LLM summary and modulates scripts for testing
- fixes repo references in release update fn

### Performance

- Added benchmark summary preparation for performance metrics in release notes

## [v0.2.17](https://github.com/loganpowell/microvector/releases/tag/v0.2.17) - 2025-10-28

- fixes automated changelog MGMT and adds scripts to fix ex-post
- DRYs up the inter-release commit detection and attempts to fix our gh-model release summary

## [v0.2.16](https://github.com/loganpowell/microvector/releases/tag/v0.2.16) - 2025-10-28

- HK: single consts for default model and vector cache dir
- hk
- fix? model name in job summary
- tries parsing model name from logs
- let's try again
- fix and added examples: 1. Fixed Bug in embed.py Problem: The filtering logic was checking for literal key names (e.g., metadata.author) instead of parsing the dot notation Solution: Added a has_nested_key() helper function that properly traverses nested dictionaries using dot notation

## [v0.2.15](https://github.com/loganpowell/microvector/releases/tag/v0.2.15) - 2025-10-28

- No changes recorded

## [v0.2.14](https://github.com/loganpowell/microvector/releases/tag/v0.2.14) - 2025-10-28

- No changes recorded

## [v0.2.13](https://github.com/loganpowell/microvector/releases/tag/v0.2.13) - 2025-10-27

- adds append test and temporary append docs
- adds embedding model name from utils to job summary
- turns job output embedding model name to HF link

## [v0.2.12](https://github.com/loganpowell/microvector/releases/tag/v0.2.12) - 2025-10-27

- updates docs
- fix client test with new parameter

## [v0.2.11](https://github.com/loganpowell/microvector/releases/tag/v0.2.11) - 2025-10-27

- No changes recorded

## [v0.2.01](https://github.com/loganpowell/microvector/releases/tag/v0.2.01) - 2025-10-27

- changes search 'partition_name' to 'partition'

## [v0.2.00](https://github.com/loganpowell/microvector/releases/tag/v0.2.00) - 2025-10-27

- fix string formatting for correct release link
- adds append option and makes tests uv compliant
- fixes test
- test fix

## [v0.1.29](https://github.com/loganpowell/microvector/releases/tag/v0.1.29) - 2025-10-23

- another 'fix' for benchmark action

## [v0.1.28](https://github.com/loganpowell/microvector/releases/tag/v0.1.28) - 2025-10-23

- ensure we're rebased before we release
- appends to top of changelog
- fix: benchmark action not saving files

## [v0.1.27](https://github.com/loganpowell/microvector/releases/tag/v0.1.27) - 2025-10-23

- update changelog link to github anchor format
- hk

## [v0.1.26](https://github.com/loganpowell/microvector/releases/tag/v0.1.26) - 2025-10-23

- fix: CHANGELOG automation

## [v0.1.25](https://github.com/loganpowell/microvector/releases/tag/v0.1.25) - 2025-10-23

- updates CHANGELOG gen model

## [v0.1.24](https://github.com/loganpowell/microvector/releases/tag/v0.1.24) - 2025-10-23

- fix: uv instead of pip for gh action and adds action for automatic changelog maintanance

## [v0.1.23](https://github.com/loganpowell/microvector/releases/tag/v0.1.23) - 2025-10-23

- performance improvements: - load embedding model from file (offline mode) - removes manual batching to delegate embeddings optimization to SentenceTransformer (much faster) - adds a github action to generate benchmark Job Summaries and benchmarking file histories - delegates logging specifics to consumer

## [v0.1.22](https://github.com/loganpowell/microvector/releases/tag/v0.1.22) - 2025-10-23

- revert to original recipe for

## [v0.1.21](https://github.com/loganpowell/microvector/releases/tag/v0.1.21) - 2025-10-23

- changes default model and safetensors
- reverts to string detection

## [v0.1.11](https://github.com/loganpowell/microvector/releases/tag/v0.1.11) - 2025-10-22

- No changes recorded

## [v0.1.1](https://github.com/loganpowell/microvector/releases/tag/v0.1.1) - 2025-10-22

- adds release script
- reverts to batches

## [v0.1.0](https://github.com/loganpowell/microvector/releases/tag/v0.1.0) - 2025-10-22

- update readme
- adds publishing action for pypi
