# Automated Changelog Generation with GitHub Models

This repository uses GitHub Actions and GitHub Models (AI) to automatically generate and update the CHANGELOG.md file whenever a new release is published.

## How It Works

### Workflow Overview

When you publish a new release on GitHub, two workflows are triggered:

1. **Benchmark & Test on Release** (`.github/workflows/benchmark-on-release.yml`)

   - Runs comprehensive performance benchmarks
   - Generates Job Summaries with performance metrics
   - Saves benchmark data as artifacts

2. **Update Changelog** (`.github/workflows/update-changelog.yml`)
   - Analyzes git diff between the previous and current release
   - Downloads benchmark results from the benchmark workflow
   - Uses GitHub Models (GPT-4) to generate a human-readable changelog entry
   - Updates CHANGELOG.md and commits the changes
   - Appends the changelog to the GitHub release notes

### What Gets Analyzed

The AI-powered changelog generation considers:

1. **Git Diff**: All code changes between releases
2. **Commit Messages**: Individual commit descriptions
3. **File Change Statistics**: Which files were modified and how much
4. **Performance Benchmarks**: Key metrics like embedding speed, search latency, and memory usage

### Permissions Required

The changelog workflow requires the following permissions:

```yaml
permissions:
  contents: write # To commit changelog updates
  models: read # To access GitHub Models
```

## The Generated Changelog

The changelog follows the [Keep a Changelog](https://keepachangelog.com/) format with these sections:

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
- **Performance**: Performance improvements (when benchmarks show improvements)

## Triggering the Workflow

### Automatic (Recommended)

The changelog is automatically updated when you:

1. Create a new release using `./release.sh v0.x.x "Release notes"`
2. Or manually create a release through the GitHub UI

### Manual

You can also manually trigger the workflow:

1. Go to Actions → Update Changelog
2. Click "Run workflow"
3. Select the branch and run

## Example Changelog Entry

```markdown
## [v0.2.0] - 2025-10-23

### Added

- Support for custom similarity metrics (cosine, euclidean, dot product)
- Offline model caching to avoid repeated downloads

### Changed

- Improved embedding batching for better performance
- Updated dependencies to latest versions

### Fixed

- Memory leak in vector storage cleanup
- Race condition in concurrent access scenarios

### Performance

- Embedding performance: 152.3 docs/sec (500 docs)
- Search latency: 2.1ms (500 docs)
- Memory footprint: 85MB delta
```

## Technical Details

### GitHub Models Integration

The workflow uses two methods to interact with GitHub Models:

1. **gh-models extension**: The GitHub CLI extension for models

   ```bash
   gh extension install https://github.com/github/gh-models
   ```

2. **AI Inference**: Calling the GPT-4 model with carefully crafted prompts
   ```bash
   cat context.txt | gh models run gpt-4o "Your prompt here"
   ```

### Model Selection

Currently using: **gpt-4o** (GPT-4 Optimized)

This model provides:

- Excellent understanding of technical context
- High-quality natural language generation
- Good balance of speed and quality

You can switch to other models from the [GitHub Models catalog](https://github.com/marketplace?type=models) by changing the model name in the workflow.

### Prompt Engineering

The AI prompt is designed to:

1. Understand the technical context of a Python library
2. Categorize changes appropriately
3. Write user-facing descriptions (not just commit messages)
4. Include performance insights from benchmarks
5. Follow markdown formatting standards

### Error Handling

The workflow includes robust error handling:

- Continues if benchmark data is unavailable
- Handles first releases (no previous tag to compare)
- Gracefully handles missing or malformed data
- Won't fail if changelog update produces no changes

## Customization

### Change the AI Model

Edit `.github/workflows/update-changelog.yml`:

```yaml
gh models run anthropic/claude-3.5-sonnet \ # Instead of gpt-4o
```

Available models: https://github.com/marketplace?type=models

### Modify the Prompt

Edit the prompt in the "Generate changelog entry with AI" step to customize:

- The writing style
- Which sections to include
- How much detail to provide
- Technical vs. user-facing language

### Adjust Benchmark Integration

Modify `.github/workflows/benchmark-on-release.yml` to change which metrics are included in the changelog summary.

## Troubleshooting

### Workflow Fails: "Permission denied"

Ensure the workflow has the required permissions:

```yaml
permissions:
  contents: write
  models: read
```

### Benchmark Data Not Found

This is expected for the first run or if the benchmark workflow hasn't completed yet. The changelog will still be generated without performance metrics.

### AI-Generated Entry Needs Improvement

You can:

1. Manually edit CHANGELOG.md after it's generated
2. Adjust the AI prompt for future releases
3. Try a different AI model

### Changelog Not Committed

Check that:

- The workflow has `contents: write` permission
- There are actual changes to commit
- The git configuration is correct

## Best Practices

1. **Write Good Commit Messages**: The AI uses these to understand changes
2. **Run Benchmarks**: They provide valuable context for performance improvements
3. **Review Generated Entries**: While AI is good, human review ensures accuracy
4. **Keep Sections Organized**: Follow the Keep a Changelog format
5. **Be User-Focused**: Changelog is for users, not just developers

## Security Considerations

### Prompt Injection

The workflow is designed to minimize prompt injection risks:

- Limited permissions (no write access to issues/PRs)
- Input is from git history (controlled by repo maintainers)
- No external user input is used in prompts

### Token Usage

GitHub Models provides generous free tier usage. Monitor your usage at:
https://github.com/settings/models

## Future Enhancements

Potential improvements:

- Compare benchmarks between releases to auto-detect performance regressions
- Generate breaking change warnings based on API diff analysis
- Auto-categorize commits based on conventional commit format
- Create release notes in multiple languages
- Generate upgrade guides for major version bumps

## Resources

- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [GitHub Models in Actions Blog Post](https://github.blog/ai-and-ml/generative-ai/automate-your-project-with-github-models-in-actions/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
