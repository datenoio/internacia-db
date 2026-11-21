"""Committed descriptor snapshot (D3) and reproducible-build checks."""
import shutil

import duckdb
import pytest

from internacia_builder.paths import project_root
from internacia_builder.snapshot import COMMITTED_PATTERNS, compare_builds, compare_snapshot, is_committed


@pytest.fixture
def dirs(tmp_path):
    committed, fresh = tmp_path / "committed", tmp_path / "fresh"
    for directory in (committed, fresh):
        directory.mkdir()
        (directory / "contract.json").write_text("{}")
        (directory / "countries.parquet").write_bytes(b"binary")
        (directory / "countries.manifest.json").write_text("{}")
    return committed, fresh


def test_build_only_files_are_not_compared(dirs):
    committed, fresh = dirs
    (fresh / "countries.manifest.json").write_text('{"row_count": 2}')
    (fresh / "datapackage.json").write_text("{}")
    assert compare_snapshot(committed, fresh) == []


def test_content_change_and_missing_descriptor_are_reported(dirs):
    committed, fresh = dirs
    (fresh / "contract.json").write_text('{"changed": true}')
    (fresh / "countries_aliases.json").write_text("[]")
    problems = compare_snapshot(committed, fresh)
    assert any("contract.json: differs" in p for p in problems)
    assert any("countries_aliases.json: produced by the build but not committed" in p for p in problems)


def test_committed_patterns_match_gitignore():
    lines = (project_root() / ".gitignore").read_text().splitlines()
    negated = {line.removeprefix("!/data/datasets/") for line in lines if line.startswith("!/data/datasets/")}
    assert negated == set(COMMITTED_PATTERNS)
    assert is_committed("contract.json")
    assert not is_committed("intblocks.manifest.json")
    assert not is_committed("datapackage.json")
    assert not is_committed("internacia.duckdb")
    assert not is_committed("countries.meta.json")


def _duckdb(path, value):
    with duckdb.connect(str(path)) as con:
        con.execute(f"CREATE TABLE t AS SELECT {value} AS v")


def test_compare_builds(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    first.mkdir()
    (first / "x.jsonl").write_text("{}\n")
    _duckdb(first / "internacia.duckdb", 1)
    shutil.copytree(first, second, ignore=shutil.ignore_patterns("internacia.duckdb"))
    _duckdb(second / "internacia.duckdb", 1)
    assert compare_builds(first, second) == []
    (second / "x.jsonl").write_text("{\"changed\": 1}\n")
    (second / "internacia.duckdb").unlink()
    _duckdb(second / "internacia.duckdb", 2)
    problems = compare_builds(first, second)
    assert "x.jsonl: bytes differ between builds" in problems
    assert "internacia.duckdb: content of t differs" in problems
