#!/bin/bash
# Script to regenerate CHANGELOG.md with correct commit ranges
# This removes duplicate commits by using changelog commits as reference points

set -e

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
    
    # Find previous tag
    PREV_TAG=$(git tag --sort=-version:refname | grep -A1 "^${TAG}$" | tail -1)
    
    if [ "$PREV_TAG" = "$TAG" ]; then
        echo "  First release"
        PREV_COMMIT=$(git rev-list --max-parents=0 HEAD)
    else
        echo "  Using previous tag $PREV_TAG as reference"
        PREV_COMMIT="$PREV_TAG"
    fi
    
    # Find the changelog commit for THIS release (comes after the tag)
    CHANGELOG_COMMIT=$(git log --all --grep="Update CHANGELOG for ${TAG}" --format="%H" | head -1)
    
    if [ -n "$CHANGELOG_COMMIT" ]; then
        echo "  Using changelog commit ${CHANGELOG_COMMIT:0:7} as upper bound"
        UPPER_COMMIT="$CHANGELOG_COMMIT"
    else
        echo "  No changelog commit found, using tag ${TAG}"
        UPPER_COMMIT="$TAG"
    fi
    
    # Get the date of this tag
    TAG_DATE=$(git log -1 --format=%cd --date=format:%Y-%m-%d ${TAG})
    
    # Get commits, excluding automated changelog and benchmark commits
    COMMITS=$(git log ${PREV_COMMIT}..${UPPER_COMMIT} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG" | grep -v "^- 📊 Add benchmark results" || true)
    
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
