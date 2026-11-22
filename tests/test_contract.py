"""Consumer contract, canonical schema_hash, and bundle checksums."""
import hashlib
import json

import pyarrow as pa
import pytest

from internacia_builder.contract import (
    build_contract,
    contract_version,
    verify_checksums,
    write_checksums,
)
from internacia_builder.manifest import dataset_files
from internacia_builder.schemas import get_countries_schema, logical_type, schema_columns, schema_hash


@pytest.mark.parametrize(
    ("data_type", "expected"),
    [
        (pa.string(), "string"),
        (pa.int32(), "int32"),
        (pa.list_(pa.struct([("id", pa.string()), ("primary", pa.bool_())])), "list<struct<id:string,primary:boolean>>"),
        (pa.map_(pa.string(), pa.struct([("official", pa.string())])), "map<string,struct<official:string>>"),
    ],
)
def test_logical_type_grammar(data_type, expected):
    assert logical_type(data_type) == expected


def test_logical_type_rejects_unmapped_types():
    with pytest.raises(ValueError):
        logical_type(pa.date32())


def test_schema_hash_is_sha256_of_canonical_columns():
    schema = get_countries_schema()
    canonical = json.dumps(schema_columns(schema), separators=(",", ":"), ensure_ascii=False)
    assert schema_hash(schema) == hashlib.sha256(canonical.encode()).hexdigest()
    assert schema_columns(schema)[0] == ["code", "string", False]


def test_schema_hash_ignores_arrow_metadata_and_tracks_columns():
    schema = pa.schema([pa.field("id", pa.string(), nullable=False), ("n", pa.int64())])
    assert schema_hash(schema.with_metadata({"writer": "any pyarrow"})) == schema_hash(schema)
    assert schema_hash(schema.append(pa.field("extra", pa.string()))) != schema_hash(schema)
    assert schema_hash(pa.schema([("id", pa.string()), ("n", pa.int64())])) != schema_hash(schema)


def test_contract_tables_keys_and_open_enums():
    contract = build_contract("3.2.1")
    assert contract["contract_version"] == "3.2"
    assert contract["dataset_version"] == "3.2.1"
    tables = {t["name"]: t for t in contract["tables"]}
    assert all(t["in_duckdb"] for t in tables.values())
    assert {name for name, t in tables.items() if t["kind"] == "view"} == {
        "current_memberships", "country_currencies", "country_languages", "country_timezones",
        "country_borders", "country_trade_agreements",
    }
    assert "FROM memberships" in tables["current_memberships"]["definition"]
    assert tables["memberships"]["primary_key"] == ["intblock_id", "country_code"]
    assert tables["countries"]["schema_hash"] == schema_hash(get_countries_schema())
    for table in tables.values():
        columns = {c["name"]: c for c in table["columns"]}
        assert all(not columns[key]["nullable"] for key in table["primary_key"])
    enums = {(e["table"], e["column"]): e for e in contract["enums"]}
    assert all(e["open"] for e in enums.values())
    assert "igo" in enums[("intblocks", "scope_category")]["values"]
    assert enums[("memberships", "status")]["values"] == enums[("intblocks", "includes[].status")]["values"]


def test_contract_version_is_major_minor():
    assert contract_version("3.0.0") == "3.0"
    assert contract_version("unknown") == "unknown"


def test_checksums_detect_unlisted_missing_and_changed_files(tmp_path):
    (tmp_path / "a.parquet").write_bytes(b"a")
    (tmp_path / "b.json").write_text("{}")
    write_checksums(tmp_path)
    assert verify_checksums(tmp_path) == []
    assert (tmp_path / "SHA256SUMS").read_text().splitlines()[0].endswith("  a.parquet")
    (tmp_path / "a.parquet").write_bytes(b"changed")
    (tmp_path / "c.csv").write_text("x")
    (tmp_path / "b.json").unlink()
    problems = verify_checksums(tmp_path)
    assert any("a.parquet does not match" in p for p in problems)
    assert any("c.csv is not listed" in p for p in problems)
    assert any("b.json is listed but missing" in p for p in problems)


def test_dataset_files_excludes_manifest_and_other_datasets(tmp_path):
    for name in ("countries.parquet", "countries-lite.csv.zst", "countries.manifest.json", "countries_aliases.json"):
        (tmp_path / name).write_text("x")
    assert [p.name for p in dataset_files(tmp_path, "countries")] == ["countries-lite.csv.zst", "countries.parquet"]
