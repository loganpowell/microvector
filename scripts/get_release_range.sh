#!/bin/bash
# Utility script to get correct commit range for a release
# This provides consistent logic across all scripts and GitHub Actions
#
# Usage:
#   source scripts/get_release_range.sh
#   get_release_range "v0.2.16"
#
# Returns: Sets variables LOWER_BOUND and UPPER_BOUND

get_release_range() {
    local TAG="$1"
    local USE_CHANGELOG_UPPER="${2:-true}"  # Whether to use changelog commit as upper bound
    
    # Find previous tag
    PREV_TAG=$(git tag --sort=-version:refname | grep -A1 "^${TAG}$" | tail -1)
    
    if [ "$PREV_TAG" = "$TAG" ]; then
        # First release - from initial commit to this tag
        LOWER_BOUND=$(git rev-list --max-parents=0 HEAD)
        echo "  First release, using initial commit as lower bound" >&2
    else
        # Use previous tag as lower bound
        LOWER_BOUND="$PREV_TAG"
        echo "  Using previous tag $PREV_TAG as lower bound" >&2
    fi
    
    # Determine upper bound
    if [ "$USE_CHANGELOG_UPPER" = "true" ]; then
        # Look for changelog commit that comes after this tag
        CHANGELOG_COMMIT=$(git log --all --grep="Update CHANGELOG for ${TAG}" --format="%H" | head -1)
        
        if [ -n "$CHANGELOG_COMMIT" ]; then
            UPPER_BOUND="$CHANGELOG_COMMIT"
            echo "  Using changelog commit ${CHANGELOG_COMMIT:0:7} as upper bound" >&2
        else
            UPPER_BOUND="$TAG"
            echo "  No changelog commit found, using tag as upper bound" >&2
        fi
    else
        # Just use the tag itself
        UPPER_BOUND="$TAG"
        echo "  Using tag as upper bound" >&2
    fi
    
    # Export for use by caller
    export LOWER_BOUND
    export UPPER_BOUND
    export PREV_TAG
}

get_commits_for_range() {
    local LOWER="$1"
    local UPPER="$2"
    local EXCLUDE_AUTOMATED="${3:-true}"
    
    if [ "$EXCLUDE_AUTOMATED" = "true" ]; then
        # Exclude automated changelog and benchmark commits
        git log ${LOWER}..${UPPER} --pretty=format:"- %s" --reverse \
            | grep -v "Update CHANGELOG" \
            | grep -v "Add benchmark results" \
            || true
    else
        # Include all commits
        git log ${LOWER}..${UPPER} --pretty=format:"- %s" --reverse
    fi
}

get_commits_with_hash() {
    local LOWER="$1"
    local UPPER="$2"
    local EXCLUDE_AUTOMATED="${3:-true}"
    
    if [ "$EXCLUDE_AUTOMATED" = "true" ]; then
        # Exclude automated changelog and benchmark commits
        git log ${LOWER}..${UPPER} --pretty=format:"- %s (%h)" --reverse \
            | grep -v "Update CHANGELOG" \
            | grep -v "Add benchmark results" \
            || true
    else
        # Include all commits
        git log ${LOWER}..${UPPER} --pretty=format:"- %s (%h)" --reverse
    fi
}

# Helper to get tag date
get_tag_date() {
    local TAG="$1"
    git log -1 --format=%cd --date=format:%Y-%m-%d ${TAG}
}

# Helper to create changelog anchor link
get_changelog_anchor() {
    local TAG="$1"
    local DATE="$2"
    local VERSION_ANCHOR=$(echo "$TAG" | sed 's/\.//g')
    echo "${VERSION_ANCHOR}---${DATE}"
}
