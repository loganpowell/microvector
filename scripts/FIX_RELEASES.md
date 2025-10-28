# Fix Release Notes

## Quick fix for a single release

Update a single release's notes:

```bash
TAG="v0.2.16"
PREV_TAG="v0.2.15"

# Find the changelog commit for the previous release
CHANGELOG_COMMIT=$(git log --grep="Update CHANGELOG for ${PREV_TAG}" --format="%H" | head -1)

# Get commits since changelog (or since prev tag if no changelog)
if [ -n "$CHANGELOG_COMMIT" ]; then
    COMMITS=$(git log ${CHANGELOG_COMMIT}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
else
    COMMITS=$(git log ${PREV_TAG}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
fi

# Update the release
gh release edit "$TAG" --notes "## Changes since ${PREV_TAG}

$COMMITS"
```

## Batch fix all releases

Run the script to interactively fix all releases:

```bash
./scripts/fix_release_notes.sh
```

This will:

1. Loop through all tags
2. Calculate correct commits for each release
3. Show you a preview
4. Ask for confirmation before updating

## Non-interactive batch update

To update all releases without prompts:

```bash
for TAG in $(git tag --sort=-version:refname); do
    PREV_TAG=$(git tag --sort=-version:refname | grep -A1 "^${TAG}$" | tail -1)

    if [ "$PREV_TAG" != "$TAG" ]; then
        CHANGELOG_COMMIT=$(git log --grep="Update CHANGELOG for ${PREV_TAG}" --format="%H" | head -1)

        if [ -n "$CHANGELOG_COMMIT" ]; then
            COMMITS=$(git log ${CHANGELOG_COMMIT}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
        else
            COMMITS=$(git log ${PREV_TAG}..${TAG} --pretty=format:"- %s" --reverse | grep -v "^- 📝 Update CHANGELOG")
        fi

        echo "Updating $TAG..."
        gh release edit "$TAG" --notes "## Changes since ${PREV_TAG}

$COMMITS"
    fi
done
```
