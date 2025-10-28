#!/bin/bash
# Script to regenerate CHANGELOG.md with correct commit ranges
# This removes duplicate commits by using changelog commits as reference points

set -e

# Source shared release range utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/get_release_range.sh"

echo "🔧 Regenerating CHANGELOG.md..."
echo ""

# Backup current changelog
cp CHANGELOG.md CHANGELOG.md.backup
echo "💾 Backed up current changelog to CHANGELOG.md.backup"
echo ""

# Create new changelog header
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

EOF

# Get all tags sorted by version (newest first)
TAGS=$(git tag --sort=-version:refname)

echo "Processing releases in reverse chronological order..."
echo ""

# Process each tag
for TAG in $TAGS; do
    echo "Processing $TAG..."
    
    # Get commit range for this release using shared utility
    get_release_range "$TAG" "true"
    
    # Get the date of this tag
    TAG_DATE=$(get_tag_date "${TAG}")
    
    # Get commits, excluding automated changelog and benchmark commits
    COMMITS=$(get_commits_for_range "${LOWER_BOUND}" "${UPPER_BOUND}" "true")
    
    # Create section for this release
    echo "## [${TAG}] - ${TAG_DATE}" >> CHANGELOG.md
    echo "" >> CHANGELOG.md
    
    if [ -n "$COMMITS" ]; then
        echo "$COMMITS" >> CHANGELOG.md
    else
        echo "- No changes recorded" >> CHANGELOG.md
    fi
    
    echo "" >> CHANGELOG.md
    
    echo "  ✅ Added to changelog"
done

echo ""
echo "✅ CHANGELOG.md regenerated successfully!"
echo ""
echo "Review the changes:"
echo "  diff CHANGELOG.md.backup CHANGELOG.md"
echo ""
echo "If satisfied, commit the changes:"
echo "  git add CHANGELOG.md"
echo "  git commit -m '📝 Regenerate CHANGELOG with correct commit ranges'"
echo ""
echo "To restore backup if needed:"
echo "  mv CHANGELOG.md.backup CHANGELOG.md"
