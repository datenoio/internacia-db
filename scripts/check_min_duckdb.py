#!/usr/bin/env python3
"""Check that internacia.duckdb opens and that every table and view reads on this DuckDB.

The builder pins a newer DuckDB than contract.json's ``min_duckdb``, so a view can build
and pass every other test yet fail to bind on the oldest DuckDB the release supports.
Run this check with that version, in an environment that has only duckdb installed:

    python -m venv /tmp/min-duckdb
    /tmp/min-duckdb/bin/pip install "duckdb==<min_duckdb from contract.json>"
    /tmp/min-duckdb/bin/python scripts/check_min_duckdb.py .ci-datasets

It imports nothing from internacia_builder, so that environment needs no other package.
"""
import argparse
import json
import sys
from pathlib import Path

import duckdb


def check(datasets: Path) -> list[str]:
    """Return one problem for each contract table or view that this DuckDB cannot read."""
    contract = json.loads((datasets / "contract.json").read_text(encoding="utf-8"))
    problems = []
    con = duckdb.connect(str(datasets / "internacia.duckdb"), read_only=True)
    try:
        for table in contract["tables"]:
            if not table.get("in_duckdb"):
                continue
            try:
                con.execute(f'SELECT * FROM "{table["name"]}"').fetchall()
            except duckdb.Error as exc:
                problems.append(f"{table.get('kind', 'table')} {table['name']}: {str(exc).splitlines()[0]}")
    finally:
        con.close()
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("datasets", type=Path, help="directory with internacia.duckdb and contract.json")
    args = parser.parse_args()
    declared = json.loads((args.datasets / "contract.json").read_text(encoding="utf-8"))["min_duckdb"]
    print(f"DuckDB {duckdb.__version__} (contract.json min_duckdb {declared})")
    problems = check(args.datasets)
    if problems:
        print("DuckDB compatibility check FAILED:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("Every table and view reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
