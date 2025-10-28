#!/bin/bash
# Script to fix release notes for existing releases
# This regenerates release notes using the correct logic (excluding duplicates)

set -e

# Source shared release range utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/get_release_range.sh"

# Get all tags sorted by version
TAGS=$(git tag --sort=-version:refname)

echo "🔧 Fixing release notes for all releases..."
echo ""

# Process each tag
for TAG in $TAGS; do
    echo "Processing $TAG..."
    
    # Get commit range for this release using shared utility
    get_release_range "$TAG" "true"
    
    # Check if this is the first release
    if [ "$LOWER_BOUND" = "$(git rev-list --max-parents=0 HEAD)" ]; then
        echo "  ℹ️  First release, skipping..."
        continue
    fi
    
    # Get commits for this release
    COMMIT_MESSAGES=$(get_commits_for_range "${LOWER_BOUND}" "${UPPER_BOUND}" "true")
    
    # Get tag date and create changelog anchor
    TAG_DATE=$(get_tag_date "${TAG}")
    CHANGELOG_ANCHOR=$(get_changelog_anchor "${TAG}" "${TAG_DATE}")
    
    # Build new release notes
    NEW_NOTES="## Changes since ${PREV_TAG}

$COMMIT_MESSAGES

📝 [View Release Changelog](https://github.com/loganpowell/microvector/blob/main/CHANGELOG.md#${CHANGELOG_ANCHOR})"
    
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
