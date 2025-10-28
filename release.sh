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
git fetch origin
git rebase origin/main

# Check if rebase had conflicts
if [ $? -ne 0 ]; then
    echo "❌ Rebase failed - please resolve conflicts and try again"
    git rebase --abort
    exit 1
fi

# Get the previous release tag
PREV_TAG=$(git tag --sort=-version:refname | head -1)

if [ -z "$PREV_TAG" ]; then
    echo "📝 No previous releases found - this is the first release"
    # Get all commits for first release, excluding automated changelog commits
    COMMIT_MESSAGES=$(git log --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
else
    echo "📝 Previous release: $PREV_TAG"
    # Find the changelog commit for the previous release (added by CI after tag)
    CHANGELOG_COMMIT=$(git log --grep="Update CHANGELOG for ${PREV_TAG}" --format="%H" | head -1)
    
    if [ -n "$CHANGELOG_COMMIT" ]; then
        echo "📝 Changelog commit for ${PREV_TAG}: ${CHANGELOG_COMMIT:0:7}"
        # Get commits since the changelog commit for previous release
        COMMIT_MESSAGES=$(git log ${CHANGELOG_COMMIT}..HEAD --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
    else
        # Fallback to tag if no changelog commit found
        echo "📝 No changelog commit found, using tag as reference"
        COMMIT_MESSAGES=$(git log ${PREV_TAG}..HEAD --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
    fi
fi

# Build release notes
if [ -n "$CUSTOM_NOTES" ]; then
    # Use custom notes if provided
    NOTES="$CUSTOM_NOTES

## Changes since ${PREV_TAG:-initial commit}

$COMMIT_MESSAGES

📝 [View Release Changelog](https://github.com/loganpowell/microvector/blob/main/CHANGELOG.md#${VERSION//v/}---$(date +%Y-%m-%d))"
else
    # Use commit messages as notes
    NOTES="## Changes since ${PREV_TAG:-initial commit}

$COMMIT_MESSAGES

📝 [View Release Changelog](https://github.com/loganpowell/microvector/blob/main/CHANGELOG.md#${VERSION//v/}---$(date +%Y-%m-%d))"
fi

echo ""
echo "📋 Release notes preview:"
echo "---"
echo "$NOTES"
echo "---"
echo ""

# Run tests
echo "🧪 Running tests..."
uv run --with . pytest

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
