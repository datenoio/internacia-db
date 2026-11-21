"""Tests for the oldest-supported-DuckDB check (CI runs it with contract.json min_duckdb)."""

import json

import check_min_duckdb
import duckdb

from internacia_builder.paths import datasets_dir


def test_built_database_reads():
    assert check_min_duckdb.check(datasets_dir()) == []


def test_view_that_does_not_bind_is_reported(tmp_path):
    con = duckdb.connect(str(tmp_path / "internacia.duckdb"))
    con.execute("CREATE TABLE t AS SELECT 1 AS x")
    con.execute("CREATE VIEW v AS SELECT x FROM t")
    con.execute("DROP TABLE t")
    con.close()
    tables = [{"name": "v", "kind": "view", "in_duckdb": True}, {"name": "absent", "kind": "table", "in_duckdb": False}]
    (tmp_path / "contract.json").write_text(json.dumps({"min_duckdb": "0", "tables": tables}), encoding="utf-8")

    problems = check_min_duckdb.check(tmp_path)

    assert len(problems) == 1
    assert problems[0].startswith("view v: ")
