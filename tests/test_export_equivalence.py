"""Cross-format export equivalence and manifest consistency tests.

Round-trip tests exercise the compressed writers directly; the parity tests
assert that the committed dataset artifacts agree across JSONL, YAML, Parquet,
and DuckDB, and that manifests match the exported row counts.
"""

import io
import json

import builder
import duckdb
import pyarrow.parquet as pq
import pytest
import yaml
import zstandard

from internacia_builder.paths import project_root

DATASETS = {"countries": "code", "intblocks": "id", "blocktypes": "id"}
DATASETS_DIR = project_root() / "data" / "datasets"


def _read_jsonl_zst(path):
    dctx = zstandard.ZstdDecompressor()
    with path.open("rb") as f:
        text = io.TextIOWrapper(dctx.stream_reader(f), encoding="utf-8")
        return [json.loads(line) for line in text if line.strip()]


def _read_yaml_zst(path):
    dctx = zstandard.ZstdDecompressor()
    with path.open("rb") as f:
        return yaml.safe_load(dctx.stream_reader(f)) or []


def test_save_jsonl_zst_round_trip(tmp_path):
    rows = [{"id": "A", "n": 1}, {"id": "B", "n": 2}]
    out = tmp_path / "d.jsonl.zst"
    builder.save_jsonl_zst(rows, out)
    assert _read_jsonl_zst(out) == rows


def test_save_yaml_zst_round_trip(tmp_path):
    rows = [{"id": "A"}, {"id": "B"}]
    out = tmp_path / "d.yaml.zst"
    builder.save_yaml_zst(rows, out)
    assert _read_yaml_zst(out) == rows


@pytest.mark.parametrize("dataset,key", DATASETS.items())
def test_committed_formats_agree_on_primary_keys(dataset, key):
    if not (DATASETS_DIR / f"{dataset}.parquet").exists():
        pytest.skip("committed datasets not present")
    parquet_ids = {str(v) for v in pq.read_table(DATASETS_DIR / f"{dataset}.parquet", columns=[key]).column(key).to_pylist()}
    jsonl_ids = {str(r[key]) for r in _read_jsonl_zst(DATASETS_DIR / f"{dataset}.jsonl.zst")}
    yaml_ids = {str(r[key]) for r in _read_yaml_zst(DATASETS_DIR / f"{dataset}.yaml.zst")}
    con = duckdb.connect(str(DATASETS_DIR / "internacia.duckdb"), read_only=True)
    try:
        duck_ids = {str(r[0]) for r in con.execute(f"SELECT {key} FROM {dataset}").fetchall()}
    finally:
        con.close()
    assert jsonl_ids == parquet_ids
    assert yaml_ids == parquet_ids
    assert duck_ids == parquet_ids


@pytest.mark.parametrize("dataset,key", DATASETS.items())
def test_committed_manifest_row_count_matches(dataset, key):
    manifest_path = DATASETS_DIR / f"{dataset}.manifest.json"
    parquet_path = DATASETS_DIR / f"{dataset}.parquet"
    if not (manifest_path.exists() and parquet_path.exists()):
        pytest.skip("committed datasets not present")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    row_count = pq.read_table(parquet_path, columns=[key]).num_rows
    assert manifest["row_count"] == row_count
