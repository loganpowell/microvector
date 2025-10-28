#!/usr/bin/env python3
"""
Update CHANGELOG.md with new release entries.

This script inserts new changelog entries at the top of CHANGELOG.md,
preserving the existing structure and adding release links.
"""

import re
import sys
from pathlib import Path
from typing import Optional


def update_changelog(
    changelog_path: Path,
    entry_path: Path,
    version: str,
    repo_url: str,
    create_if_missing: bool = True,
    force: bool = False,
) -> bool:
    """
    Update CHANGELOG.md with a new release entry.

    Args:
        changelog_path: Path to CHANGELOG.md
        entry_path: Path to the new changelog entry markdown file
        version: Version string (e.g., "v0.1.26")
        repo_url: GitHub repository URL (e.g., "https://github.com/owner/repo")
        create_if_missing: Create CHANGELOG.md if it doesn't exist
        force: Force regeneration even if version already exists

    Returns:
        True if changelog was updated, False otherwise
    """
    # Create changelog if it doesn't exist
    if not changelog_path.exists():
        if not create_if_missing:
            print(f"Error: {changelog_path} does not exist", file=sys.stderr)
            return False

        changelog_path.write_text(
            """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
        )

    # Read the changelog
    changelog = changelog_path.read_text()

    # Check if version already exists in changelog
    version_header_pattern = rf"## \[{re.escape(version)}\].*?(?=\n## \[|$)"
    existing_match = re.search(version_header_pattern, changelog, re.DOTALL)

    if existing_match and not force:
        print(f"⚠️  Version {version} already exists in CHANGELOG.md")
        print("Skipping duplicate entry (use --force to regenerate)")
        return True  # Not an error, just skip

    if existing_match and force:
        print(f"🔄 Regenerating entry for {version} (force mode)")
        # Remove the existing entry
        changelog = (
            changelog[: existing_match.start()] + changelog[existing_match.end() :]
        )

    # Read the new entry
    if not entry_path.exists():
        print(f"Error: Entry file {entry_path} does not exist", file=sys.stderr)
        return False

    new_entry = entry_path.read_text().strip()

    # Add release link to the changelog entry
    release_url = f"{repo_url.rstrip('/')}/releases/tag/{version}"

    # Modify the version header to include a link to the release
    # Pattern: ## [version] - date (or just ## version - date without brackets)
    version_pattern = rf"## (?:\[)?{re.escape(version)}(?:\])?"
    if re.search(version_pattern, new_entry):
        new_entry = re.sub(
            version_pattern, f"## [{version}]({release_url})", new_entry, count=1
        )

    # Find the end of the header (after the "Semantic Versioning" paragraph)
    # Then insert the new entry right after it
    header_pattern = r"(# Changelog.*?Semantic Versioning.*?\n)"

    match = re.search(header_pattern, changelog, re.DOTALL)
    if match:
        header_end = match.end()
        updated_changelog = (
            changelog[:header_end] + "\n" + new_entry + "\n" + changelog[header_end:]
        )
    else:
        # Fallback: just prepend after first line
        lines = changelog.split("\n", 1)
        updated_changelog = (
            lines[0] + "\n\n" + new_entry + "\n" + (lines[1] if len(lines) > 1 else "")
        )

    # Write back
    changelog_path.write_text(updated_changelog)

    return True


def main():
    """Command-line interface for update_changelog."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update CHANGELOG.md with new release entries"
    )
    parser.add_argument(
        "--changelog",
        type=Path,
        default=Path("CHANGELOG.md"),
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    parser.add_argument(
        "--entry", type=Path, required=True, help="Path to the new changelog entry file"
    )
    parser.add_argument(
        "--version", required=True, help="Version string (e.g., v0.1.26)"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)",
    )
    parser.add_argument(
        "--no-create",
        action="store_true",
        help="Do not create CHANGELOG.md if it does not exist",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if version already exists",
    )

    args = parser.parse_args()

    # Update the changelog
    success = update_changelog(
        args.changelog,
        args.entry,
        args.version,
        args.repo,
        create_if_missing=not args.no_create,
        force=args.force,
    )

    if success:
        print(f"✅ CHANGELOG.md updated successfully with {args.version}")
        return 0
    else:
        print("❌ Failed to update CHANGELOG.md", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
