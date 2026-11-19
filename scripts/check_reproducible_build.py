#!/usr/bin/env python3
"""Check that two builds of the same commit are reproducible.

Every file must be byte-identical except internacia.duckdb, whose tables must have
identical columns and rows.
"""
import argparse
import sys
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.snapshot import compare_builds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    problems = compare_builds(args.first, args.second)
    if problems:
        print("Reproducible build check FAILED:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("Reproducible build OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
