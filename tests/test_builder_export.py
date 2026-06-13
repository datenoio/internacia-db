"""Integration tests for builder export paths using small fixture data."""

import json

import builder
import pyarrow.parquet as pq
import pytest

COUNTRY = {
    "code": "AA",
    "name": "Testland",
    "iso3code": "AAA",
    "numeric_code": "001",
    "entity_type": "sovereign_state",
    "code_status": "official_iso3166_1",
    "population": {"value": 100, "year": 2024, "source": "WB", "source_id": "S"},
    "borders": [],
}

INTBLOCK = {
    "id": "TESTORG",
    "name": "Test Organization",
    "blocktype": ["intorg"],
    "status": "formal",
    "includes": [{"id": "NO", "name": "Norway", "type": "country", "status": "member"}],
}

BLOCKTYPE = {"id": "intorg", "name": "International organization"}


def test_save_parquet_round_trip(tmp_path):
    data = builder.clean_data([COUNTRY], "countries")
    out = tmp_path / "countries.parquet"
    builder.save_parquet(data, out, schema=builder.get_countries_schema())
    table = pq.read_table(out)
    assert table.num_rows == 1
    row = table.to_pylist()[0]
    assert row["code"] == "AA"
    assert row["population"]["value"] == 100
    assert row["population"]["year"] == 2024


def test_save_parquet_raises_on_schema_mismatch(tmp_path):
    import pyarrow as pa

    bad = [{"code": 123, "population": "not-a-struct"}]
    with pytest.raises((pa.ArrowInvalid, pa.ArrowTypeError)):
        builder.save_parquet(bad, tmp_path / "bad.parquet", schema=builder.get_countries_schema())


def test_duckdb_export_creates_queryable_tables(tmp_path):
    import duckdb

    out = tmp_path / "test.duckdb"
    builder.create_duckdb_database(
        builder.clean_data([COUNTRY], "countries"),
        builder.clean_data([INTBLOCK], "intblocks"),
        builder.clean_data([BLOCKTYPE], "blocktypes"),
        out,
        countries_schema=builder.get_countries_schema(),
        intblocks_schema=builder.get_intblocks_schema(),
        blocktypes_schema=builder.get_blocktypes_schema(),
    )
    con = duckdb.connect(str(out))
    try:
        assert con.execute("SELECT COUNT(*) FROM countries").fetchone()[0] == 1
        assert con.execute("SELECT COUNT(*) FROM intblocks").fetchone()[0] == 1
        assert con.execute("SELECT COUNT(*) FROM blocktypes").fetchone()[0] == 1
        member = con.execute("SELECT m.id FROM intblocks, UNNEST(includes) AS t(m) LIMIT 1").fetchone()[0]
        assert member == "NO"
    finally:
        con.close()


def test_load_yaml_files_raises_on_parse_error(tmp_path):
    (tmp_path / "good.yaml").write_text("id: GOOD\n", encoding="utf-8")
    (tmp_path / "bad.yaml").write_text("id: [unclosed\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Failed to load 1 YAML file"):
        builder.load_yaml_files(tmp_path, "test")


def test_load_yaml_files_reads_subdirectories(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "a.yaml").write_text("id: A\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("id: B\n", encoding="utf-8")
    data = builder.load_yaml_files(tmp_path, "test")
    assert sorted(d["id"] for d in data) == ["A", "B"]


def test_manifest_fields_and_schema_hash_stability(tmp_path):
    schema = builder.get_countries_schema()
    builder.write_manifest(tmp_path, "countries", schema, 252)
    manifest = json.loads((tmp_path / "countries.manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset"] == "countries"
    assert manifest["row_count"] == 252
    assert set(manifest) == {
        "dataset",
        "version",
        "build_date",
        "git_commit",
        "row_count",
        "schema_hash",
        "data_license",
    }
    assert manifest["data_license"] == "CC-BY-4.0"
    # schema_hash must be deterministic for an unchanged schema
    assert manifest["schema_hash"] == builder.schema_hash(builder.get_countries_schema())
    assert len(manifest["schema_hash"]) == 16


def test_intblocks_manifest(tmp_path):
    schema = builder.get_intblocks_schema()
    builder.write_manifest(tmp_path, "intblocks", schema, 1057)
    manifest = json.loads((tmp_path / "intblocks.manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset"] == "intblocks"
    assert manifest["row_count"] == 1057


def test_duckdb_meta_table_is_queryable(tmp_path):
    import duckdb

    out = tmp_path / "test.duckdb"
    builder.create_duckdb_database(
        builder.clean_data([COUNTRY], "countries"),
        builder.clean_data([INTBLOCK], "intblocks"),
        builder.clean_data([BLOCKTYPE], "blocktypes"),
        out,
        countries_schema=builder.get_countries_schema(),
        intblocks_schema=builder.get_intblocks_schema(),
        blocktypes_schema=builder.get_blocktypes_schema(),
    )
    con = duckdb.connect(str(out))
    try:
        datasets = {row[0] for row in con.execute("SELECT dataset FROM _meta").fetchall()}
        assert datasets == {"countries", "intblocks", "blocktypes"}
        version, schema_hash, data_license = con.execute(
            "SELECT version, schema_hash, data_license FROM _meta WHERE dataset = 'countries'"
        ).fetchone()
        assert version == builder.get_dataset_version()
        assert schema_hash == builder.schema_hash(builder.get_countries_schema())
        assert data_license == "CC-BY-4.0"
    finally:
        con.close()


def test_meta_sidecar_matches_manifest(tmp_path):
    schema = builder.get_countries_schema()
    builder.write_manifest(tmp_path, "countries", schema, 252)
    builder.write_meta_sidecar(tmp_path, "countries", schema, 252)
    manifest = json.loads((tmp_path / "countries.manifest.json").read_text(encoding="utf-8"))
    sidecar = json.loads((tmp_path / "countries.meta.json").read_text(encoding="utf-8"))
    assert sidecar["version"] == manifest["version"]
    assert sidecar["schema_hash"] == manifest["schema_hash"]
    assert sidecar["row_count"] == manifest["row_count"] == 252
    assert sidecar["data_license"] == "CC-BY-4.0"


def test_save_aliases_writes_json_and_parquet(tmp_path):
    aliases = [
        {"alias": "ASF", "target": "FSA", "reason": "disambiguated", "since": "1.3.0", "note": ""},
    ]
    builder.save_aliases(aliases, tmp_path, write_parquet=True)
    data = json.loads((tmp_path / "intblocks_aliases.json").read_text(encoding="utf-8"))
    assert data[0]["alias"] == "ASF"
    assert data[0]["target"] == "FSA"
    table = pq.read_table(tmp_path / "intblocks_aliases.parquet")
    assert table.num_rows == 1
    assert table.to_pylist()[0]["reason"] == "disambiguated"


def test_load_intblock_aliases_reads_source(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "intblocks_aliases.yaml").write_text(
        "- alias: OLD\n  target: NEW\n  reason: renamed\n  since: '1.4.0'\n",
        encoding="utf-8",
    )
    aliases = builder.load_intblock_aliases(tmp_path)
    assert aliases == [{"alias": "OLD", "target": "NEW", "reason": "renamed", "since": "1.4.0", "note": ""}]
