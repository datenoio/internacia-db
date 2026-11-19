#!/usr/bin/env python3
"""Check that the committed data/datasets descriptors match a fresh build."""
import argparse
import sys
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.paths import project_root
from internacia_builder.snapshot import compare_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", type=Path, required=True, help="directory with a fresh build of the same commit")
    parser.add_argument("--committed", type=Path, default=project_root() / "data" / "datasets")
    args = parser.parse_args()
    problems = compare_snapshot(args.committed, args.fresh)
    if problems:
        print("Committed snapshot check FAILED:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("Committed snapshot OK: descriptors match the fresh build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
