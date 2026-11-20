"""The committed text snapshot of ``data/datasets/`` and build reproducibility checks.

Binary and bulk exports are build outputs (see ``.gitignore``); only the descriptors
below are committed, so pull requests show which datasets changed without carrying
megabytes of regenerated files.
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
    "*.manifest.json",
    "contract.json",
    "datapackage.json",
    "README.md",
    "intblocks_aliases.json",
    "countries_aliases.json",
    "attribute_intblock_migrations.json",
    "border_status.json",
)

# Fields that identify one build rather than its content.
IDENTITY_FIELDS = ("build_date", "git_commit")

DUCKDB_FILE = "internacia.duckdb"


def is_committed(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in COMMITTED_PATTERNS)


def _normalized(path: Path) -> str:
    """File content with build identity removed from manifests."""
    text = path.read_text(encoding="utf-8")
    if not path.name.endswith(".manifest.json"):
        return text
    manifest = json.loads(text)
    for field in IDENTITY_FIELDS:
        manifest.pop(field, None)
    manifest["files"] = [f for f in manifest.get("files", []) if not f["path"].endswith(".meta.json")]
    return json.dumps(manifest, indent=2, sort_keys=True)


def compare_snapshot(committed_dir: Path, fresh_dir: Path) -> list[str]:
    """Compare the committed descriptors with a fresh build of the same sources.

    Manifests are compared without build identity (``build_date``, ``git_commit``) and
    without the checksums of ``.meta.json`` sidecars, which embed that identity."""
    problems: list[str] = []
    committed = {p.name for p in committed_dir.iterdir() if p.is_file() and is_committed(p.name)}
    fresh = {p.name for p in fresh_dir.iterdir() if p.is_file() and is_committed(p.name)}
    for name in sorted(fresh - committed):
        problems.append(f"{name}: produced by the build but not committed")
    for name in sorted(committed - fresh):
        problems.append(f"{name}: committed but no longer produced by the build")
    for name in sorted(committed & fresh):
        if _normalized(committed_dir / name) != _normalized(fresh_dir / name):
            problems.append(f"{name}: differs from a fresh build; run `python scripts/builder.py build` and commit")
    stray = sorted(
        p.name for p in committed_dir.iterdir() if p.is_file() and not is_committed(p.name) and _tracked(p)
    )
    problems.extend(f"{name}: generated binary/bulk export is tracked in git" for name in stray)
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
