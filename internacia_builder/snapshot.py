"""The committed text snapshot of ``data/datasets/`` and build reproducibility checks.

Exports and build descriptors are build outputs (see ``.gitignore``). Only the descriptors
below are committed: they change with the schema or with rare source edits. Build
manifests and ``datapackage.json`` carry per-build checksums, sizes, row counts and build
identity, which every data change rewrites; committing them made every pair of open data
pull requests conflict, so they ship only in builds and GitHub Releases.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path

import duckdb

from internacia_builder.contract import CHECKSUMS_FILE, file_digest

# Keep in sync with the ``data/datasets/`` negations in .gitignore.
COMMITTED_PATTERNS = (
    "contract.json",
    "README.md",
    "intblocks_aliases.json",
    "countries_aliases.json",
    "attribute_intblock_migrations.json",
    "border_status.json",
)

DUCKDB_FILE = "internacia.duckdb"


def is_committed(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in COMMITTED_PATTERNS)


def compare_snapshot(committed_dir: Path, fresh_dir: Path) -> list[str]:
    """Compare the committed descriptors with a fresh build of the same sources."""
    problems: list[str] = []
    committed = {p.name for p in committed_dir.iterdir() if p.is_file() and is_committed(p.name)}
    fresh = {p.name for p in fresh_dir.iterdir() if p.is_file() and is_committed(p.name)}
    for name in sorted(fresh - committed):
        problems.append(f"{name}: produced by the build but not committed")
    for name in sorted(committed - fresh):
        problems.append(f"{name}: committed but no longer produced by the build")
    for name in sorted(committed & fresh):
        if (committed_dir / name).read_bytes() != (fresh_dir / name).read_bytes():
            problems.append(f"{name}: differs from a fresh build; run `python scripts/builder.py build` and commit")
    stray = sorted(
        p.name for p in committed_dir.iterdir() if p.is_file() and not is_committed(p.name) and _tracked(p)
    )
    problems.extend(
        f"{name}: build output is tracked in git; run `git rm --cached data/datasets/{name}`" for name in stray
    )
    return problems


def _tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path.name],
        cwd=path.parent,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def duckdb_content_digest(path: Path) -> dict[str, str]:
    """SHA-256 per table/view of its column definitions and rows in stored order."""
    digests: dict[str, str] = {}
    con = duckdb.connect(str(path), read_only=True)
    try:
        names = [
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY table_name"
            ).fetchall()
        ]
        for name in names:
            digest = hashlib.sha256()
            columns = con.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = 'main' AND table_name = ? ORDER BY ordinal_position",
                [name],
            ).fetchall()
            digest.update(json.dumps(columns).encode())
            for row in con.execute(f'SELECT * FROM "{name}"').fetchall():
                digest.update(json.dumps(row, default=str, ensure_ascii=False).encode())
                digest.update(b"\n")
            digests[name] = digest.hexdigest()
    finally:
        con.close()
    return digests


def compare_builds(first: Path, second: Path) -> list[str]:
    """Two builds of the same commit: every file is byte-identical except the DuckDB
    file (and ``SHA256SUMS``, which lists it), whose tables must have identical content."""
    problems: list[str] = []
    names_a = {p.name for p in first.iterdir() if p.is_file()}
    names_b = {p.name for p in second.iterdir() if p.is_file()}
    for name in sorted(names_a ^ names_b):
        problems.append(f"{name}: present in only one build")
    for name in sorted(names_a & names_b - {DUCKDB_FILE, CHECKSUMS_FILE}):
        if file_digest(first / name) != file_digest(second / name):
            problems.append(f"{name}: bytes differ between builds")
    if DUCKDB_FILE in names_a & names_b:
        a, b = duckdb_content_digest(first / DUCKDB_FILE), duckdb_content_digest(second / DUCKDB_FILE)
        if a.keys() != b.keys():
            problems.append(f"{DUCKDB_FILE}: tables differ: {sorted(a.keys() ^ b.keys())}")
        problems.extend(f"{DUCKDB_FILE}: content of {name} differs" for name in sorted(a.keys() & b.keys()) if a[name] != b[name])
    return problems
