#!/bin/bash
# Script to fix release notes for existing releases
# This regenerates release notes using the correct logic (excluding duplicates)

set -e

# Get all tags sorted by version
TAGS=$(git tag --sort=-version:refname)

echo "🔧 Fixing release notes for all releases..."
echo ""

# Process each tag
for TAG in $TAGS; do
    echo "Processing $TAG..."
    
    # Find previous tag
    PREV_TAG=$(git tag --sort=-version:refname | grep -A1 "^${TAG}$" | tail -1)
    
    if [ "$PREV_TAG" = "$TAG" ]; then
        echo "  ℹ️  First release, skipping..."
        continue
    fi
    
    # Find the changelog commit for the previous release
    CHANGELOG_COMMIT=$(git log --grep="Update CHANGELOG for ${PREV_TAG}" --format="%H" | head -1)
    
    if [ -n "$CHANGELOG_COMMIT" ]; then
        echo "  📝 Using changelog commit ${CHANGELOG_COMMIT:0:7} as reference"
        # Get commits between changelog and this tag, excluding automated commits
        COMMIT_MESSAGES=$(git log ${CHANGELOG_COMMIT}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
    else
        echo "  📝 No changelog found, using previous tag as reference"
        # Fallback to previous tag
        COMMIT_MESSAGES=$(git log ${PREV_TAG}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
    fi
    
    # Build new release notes
    NEW_NOTES="## Changes since ${PREV_TAG}

$COMMIT_MESSAGES

📝 [View Release Changelog](https://github.com/loganpowell/microvector/blob/main/CHANGELOG.md#${TAG//./}---$(git log -1 --format=%cd --date=format:%Y-%m-%d ${TAG}))"
    
    echo "  📋 New notes preview:"
    echo "$NEW_NOTES" | head -10
    echo ""
    
    # Ask for confirmation
    read -p "  Update release notes for $TAG? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh release edit "$TAG" --notes "$NEW_NOTES"
        echo "  ✅ Updated $TAG"
    else
        echo "  ⏭️  Skipped $TAG"
    fi
    
    echo ""
done

echo "✅ Done!"
