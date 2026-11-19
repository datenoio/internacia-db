#!/usr/bin/env python3
"""Validate distribution resources and optional tag-version consistency."""
import argparse
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.distribution import check_release_version, validate_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--version")
    args = parser.parse_args()
    validate_bundle(args.directory)
    if args.version:
        check_release_version(args.version, args.directory)
    print("Release bundle OK")


if __name__ == "__main__":
    main()
