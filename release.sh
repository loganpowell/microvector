#!/bin/bash
# Release script for microvector
# Usage: ./release.sh v0.1.0 ["Optional custom release notes"]

set -e

VERSION=$1
CUSTOM_NOTES=$2

if [ -z "$VERSION" ]; then
    echo "Error: Version tag required"
    echo "Usage: ./release.sh v0.1.0 ['Optional custom release notes']"
    exit 1
fi

# Ensure we're on main and up to date
echo "📦 Preparing release $VERSION..."
git checkout main
git pull origin main

# Get the previous release tag
PREV_TAG=$(git tag --sort=-version:refname | head -1)

if [ -z "$PREV_TAG" ]; then
    echo "📝 No previous releases found - this is the first release"
    # Get all commits for first release
    COMMIT_MESSAGES=$(git log --pretty=format:"- %s" --reverse)
else
    echo "📝 Previous release: $PREV_TAG"
    # Get commits since last release
    COMMIT_MESSAGES=$(git log ${PREV_TAG}..HEAD --pretty=format:"- %s" --reverse)
fi

# Build release notes
if [ -n "$CUSTOM_NOTES" ]; then
    # Use custom notes if provided
    NOTES="$CUSTOM_NOTES

## Changes since ${PREV_TAG:-initial commit}

$COMMIT_MESSAGES"
else
    # Use commit messages as notes
    NOTES="## Changes since ${PREV_TAG:-initial commit}

$COMMIT_MESSAGES"
fi

echo ""
echo "📋 Release notes preview:"
echo "---"
echo "$NOTES"
echo "---"
echo ""

# Run tests
echo "🧪 Running tests..."
uv run pytest

# Build the package
echo "🔨 Building package..."
rm -rf dist/
uv build

echo "✅ Build successful!"
echo ""
echo "📋 Files in dist/:"
ls -lh dist/

# Create the release on GitHub
echo ""
echo "🚀 Creating GitHub release..."

if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not installed"
    echo "Install with: brew install gh"
    echo ""
    echo "Then run manually:"
    echo "  git tag $VERSION"
    echo "  git push origin $VERSION"
    echo "  gh release create $VERSION --title '$VERSION' --notes '$NOTES'"
    exit 1
fi

gh release create "$VERSION" \
    --title "$VERSION" \
    --notes "$NOTES" \
    --latest

echo ""
echo "✅ Release created successfully!"
echo "🎉 GitHub Actions will automatically publish to PyPI"
echo ""
echo "Monitor the workflow at:"
echo "https://github.com/loganpowell/microvector/actions"
