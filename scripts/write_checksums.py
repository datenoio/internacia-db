#!/usr/bin/env python3
"""Write or verify SHA256SUMS for a dataset bundle directory."""
import argparse
import sys
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)

from internacia_builder.contract import CHECKSUMS_FILE, verify_checksums, write_checksums


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--check", action="store_true", help="verify instead of writing")
    args = parser.parse_args()
    if not args.check:
        write_checksums(args.directory)
    problems = verify_checksums(args.directory)
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"{args.directory / CHECKSUMS_FILE}: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
