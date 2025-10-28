# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.16] - 2025-10-28

- HK: single consts for default model and vector cache dir
- hk
- fix? model name in job summary
- tries parsing model name from logs
- let's try again
- fix and added examples: 1. Fixed Bug in embed.py Problem: The filtering logic was checking for literal key names (e.g., metadata.author) instead of parsing the dot notation Solution: Added a has_nested_key() helper function that properly traverses nested dictionaries using dot notation

## [v0.2.15] - 2025-10-28

- No changes recorded

## [v0.2.14] - 2025-10-28

- No changes recorded

## [v0.2.13] - 2025-10-27

- adds append test and temporary append docs
- adds embedding model name from utils to job summary
- turns job output embedding model name to HF link

## [v0.2.12] - 2025-10-27

- updates docs
- fix client test with new parameter

## [v0.2.11] - 2025-10-27

- No changes recorded

## [v0.2.01] - 2025-10-27

- changes search 'partition_name' to 'partition'

## [v0.2.00] - 2025-10-27

- fix string formatting for correct release link
- adds append option and makes tests uv compliant
- fixes test
- test fix

## [v0.1.29] - 2025-10-23

- another 'fix' for benchmark action

## [v0.1.28] - 2025-10-23

- ensure we're rebased before we release
- appends to top of changelog
- fix: benchmark action not saving files

## [v0.1.27] - 2025-10-23

- update changelog link to github anchor format
- hk

## [v0.1.26] - 2025-10-23

- fix: CHANGELOG automation

## [v0.1.25] - 2025-10-23

- updates CHANGELOG gen model

## [v0.1.24] - 2025-10-23

- fix: uv instead of pip for gh action and adds action for automatic changelog maintanance

## [v0.1.23] - 2025-10-23

- performance improvements: - load embedding model from file (offline mode) - removes manual batching to delegate embeddings optimization to SentenceTransformer (much faster) - adds a github action to generate benchmark Job Summaries and benchmarking file histories - delegates logging specifics to consumer

## [v0.1.22] - 2025-10-23

- revert to original recipe for

## [v0.1.21] - 2025-10-23

- changes default model and safetensors
- reverts to string detection

## [v0.1.11] - 2025-10-22

- No changes recorded

## [v0.1.1] - 2025-10-22

- adds release script
- reverts to batches

## [v0.1.0] - 2025-10-22

- update readme
- adds publishing action for pypi

