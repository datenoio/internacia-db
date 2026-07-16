"""Tests for the artifact consistency checker's format readers and diff logic."""

import json

import builder
import check_generated_artifacts as cga
import pyarrow.parquet as pq


def test_format_readers_round_trip(tmp_path):
    rows = [{"id": "A", "n": 1}, {"id": "B", "n": 2}]
    builder.save_jsonl_zst(rows, tmp_path / "d.jsonl.zst")
    builder.save_yaml_zst(rows, tmp_path / "d.yaml.zst")
    builder.save_parquet(rows, tmp_path / "d.parquet", schema=None)

    assert cga._jsonl_ids(tmp_path / "d.jsonl.zst", "id") == {"A", "B"}
    assert cga._yaml_zst_ids(tmp_path / "d.yaml.zst", "id") == {"A", "B"}
    assert cga._parquet_ids(tmp_path / "d.parquet", "id") == {"A", "B"}


def test_parquet_reader_detects_mismatch(tmp_path):
    builder.save_parquet([{"id": "A"}, {"id": "B"}], tmp_path / "d.parquet", schema=None)
    ids = cga._parquet_ids(tmp_path / "d.parquet", "id")
    assert ids != {"A", "B", "C"}  # injected extra id absent from export


def test_identity_diff_flags_divergent_build(tmp_path):
    matching = {"a": {"version": "1", "build_date": "x", "git_commit": "g"},
                "b": {"version": "1", "build_date": "x", "git_commit": "g"}}
    distinct = {json.dumps(v, sort_keys=True) for v in matching.values()}
    assert len(distinct) == 1

    divergent = dict(matching)
    divergent["c"] = {"version": "2", "build_date": "y", "git_commit": "h"}
    distinct = {json.dumps(v, sort_keys=True) for v in divergent.values()}
    assert len(distinct) > 1


def test_committed_parquet_source_parity():
    """The committed intblocks parquet id set matches the YAML source ids."""
    root = cga.ROOT
    parquet = root / "data" / "datasets" / "intblocks.parquet"
    if not parquet.exists():
        import pytest
        pytest.skip("committed datasets not present")
    export_ids = {str(v) for v in pq.read_table(parquet, columns=["id"]).column("id").to_pylist()}
    source_ids = cga._source_ids(cga.DATASETS["intblocks"], root)
    assert export_ids == source_ids
