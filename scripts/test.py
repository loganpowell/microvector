#!/usr/bin/env python
"""Test runner script for uv run compatibility."""
import sys
import pytest


def main():
    """Entry point for test runner."""
    sys.exit(pytest.main(sys.argv[1:]))


if __name__ == "__main__":
    main()
