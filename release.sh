#!/bin/bash
# Release script for microvector
# Usage: ./release.sh v0.1.0 "Release notes"

set -e

VERSION=$1
NOTES=${2:-"Release $VERSION"}

if [ -z "$VERSION" ]; then
    echo "Error: Version tag required"
    echo "Usage: ./release.sh v0.1.0 'Release notes'"
    exit 1
fi

# Ensure we're on main and up to date
echo "📦 Preparing release $VERSION..."
git checkout main
git pull origin main

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
