#!/usr/bin/env python3
"""
Truncate git diffs to a specified token limit using tiktoken.

This script is used to prepare code diffs for AI model consumption,
ensuring they stay within token limits while preserving as much
context as possible.
"""

import sys
from pathlib import Path
from typing import Optional

import tiktoken


def truncate_diff(
    input_path: Path,
    output_path: Path,
    max_tokens: int = 3000,
    encoding_name: str = "cl100k_base",
) -> dict:
    """
    Truncate a diff file to a maximum number of tokens.

    Args:
        input_path: Path to the input diff file
        output_path: Path to write the truncated diff
        max_tokens: Maximum number of tokens to keep (default: 3000)
        encoding_name: Tiktoken encoding to use (default: cl100k_base for GPT-4)

    Returns:
        Dictionary with statistics: original_tokens, truncated_tokens, was_truncated
    """
    # Read the input diff
    if not input_path.exists():
        diff_content = "No functional code changes"
        original_tokens = 0
    else:
        diff_content = input_path.read_text()

        # Handle empty diffs
        if not diff_content.strip():
            diff_content = "No functional code changes"

    # Initialize tokenizer
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(diff_content)
    original_tokens = len(tokens)

    # Truncate if necessary
    if original_tokens > max_tokens:
        truncated_tokens = tokens[:max_tokens]
        truncated_diff = encoding.decode(truncated_tokens)
        truncated_diff += "\n\n... (diff truncated for brevity)"
        was_truncated = True
        final_tokens = max_tokens
    else:
        truncated_diff = diff_content
        was_truncated = False
        final_tokens = original_tokens

    # Write the output
    output_path.write_text(truncated_diff)

    # Return statistics
    return {
        "original_tokens": original_tokens,
        "truncated_tokens": final_tokens,
        "was_truncated": was_truncated,
        "encoding": encoding_name,
    }


def main():
    """Command-line interface for truncate_diff."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Truncate git diffs to token limits using tiktoken"
    )
    parser.add_argument("input", type=Path, help="Input diff file path")
    parser.add_argument("output", type=Path, help="Output truncated diff file path")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=3000,
        help="Maximum number of tokens (default: 3000)",
    )
    parser.add_argument(
        "--encoding",
        default="cl100k_base",
        help="Tiktoken encoding name (default: cl100k_base)",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    # Truncate the diff
    stats = truncate_diff(
        args.input, args.output, max_tokens=args.max_tokens, encoding_name=args.encoding
    )

    # Print statistics unless quiet
    if not args.quiet:
        print(f"Diff tokens: {stats['truncated_tokens']}/{stats['original_tokens']}")
        if stats["was_truncated"]:
            print(f"⚠️  Diff was truncated to {args.max_tokens} tokens")
        else:
            print("✅ Diff fits within token limit")

    return 0 if not stats["was_truncated"] else 1


if __name__ == "__main__":
    sys.exit(main())
