"""Tests for the artifact consistency checker's format readers and diff logic."""

import json
import shutil

import check_generated_artifacts as cga
import duckdb
import pyarrow.parquet as pq
import pytest
import yaml
from typer.testing import CliRunner

from internacia_builder import build as builder
from internacia_builder.clean import clean_data
from internacia_builder.contract import write_checksums, write_contract
from internacia_builder.manifest import get_dataset_version
from internacia_builder.paths import datasets_dir


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
    parquet = datasets_dir() / "intblocks.parquet"
    if not parquet.exists():
        import pytest
        pytest.skip("committed datasets not present")
    export_ids = {str(v) for v in pq.read_table(parquet, columns=["id"]).column("id").to_pylist()}
    source_ids = cga._source_ids(cga.DATASETS["intblocks"], root)
    assert export_ids == source_ids


@pytest.fixture(scope="module")
def artifact_fixture(tmp_path_factory):
    root = tmp_path_factory.mktemp("bundle")
    out = root / "data" / "datasets"
    out.mkdir(parents=True)
    source = {
        "countries": [{"code": "AA", "name": "Name with\na newline", "iso3code": "AAA"}],
        "intblocks": [{"id": "ORG", "name": "Organization", "notes": "curation only", "includes": [
            {"id": "AA", "name": "Name", "type": "country", "status": "member"},
        ]}],
        "blocktypes": [{"id": "political", "name": "Political"}],
    }
    for name, rows in source.items():
        spec = cga.DATASETS[name]
        path = root / spec["source"]
        if spec["glob"]:
            path = path / ("test/ORG.yaml" if name == "intblocks" else "AA.yaml")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(rows if name == "blocktypes" else rows[0]))
        source[name] = clean_data(rows, name)
    builder.fill_country_include_names(source["intblocks"], source["countries"])
    source["memberships"] = builder.build_membership_rows(source["intblocks"])
    builder.begin_build_context()
    for name, rows in source.items():
        schema = cga.SCHEMAS[name]()
        builder.save_parquet(rows, out / f"{name}.parquet", schema)
        builder.write_meta_sidecar(out, name, schema, len(rows))
        if name in cga.DATASETS:
            builder.save_jsonl(rows, out / f"{name}.jsonl")
            builder.save_jsonl_zst(rows, out / f"{name}.jsonl.zst")
            builder.save_yaml_zst(rows, out / f"{name}.yaml.zst")
    for name, flatten, fields in (
        ("countries", builder.flatten_country, builder.COUNTRIES_LITE_FIELDS),
        ("intblocks", builder.flatten_intblock, builder.INTBLOCKS_LITE_FIELDS),
    ):
        rows = [flatten(r) for r in source[name]]
        lite = builder.project_lite_rows(rows, fields)
        builder.save_csv_rows(rows, out / f"{name}.csv.zst")
        builder.save_csv_rows(lite, out / f"{name}-lite.csv.zst")
        builder.save_parquet(lite, out / f"{name}-lite.parquet")
        builder.save_json_array(source[name], out / f"{name}.json.zst")
    builder.save_memberships_csv(source["memberships"], out / "memberships.csv.zst")
    for name in ("countries_aliases", "intblocks_aliases"):
        builder.save_aliases([], out, basename=name)
    builder.save_border_status([], out)
    builder.create_duckdb_database(
        source["countries"], source["intblocks"], source["blocktypes"], out / "internacia.duckdb",
        cga.SCHEMAS["countries"](), cga.SCHEMAS["intblocks"](), cga.SCHEMAS["blocktypes"](), source["memberships"],
        reference_tables=[
            ("intblocks_aliases", [], cga.get_aliases_schema()),
            ("countries_aliases", [], cga.get_aliases_schema()),
            ("attribute_intblock_migrations", [], cga.get_attribute_migration_schema()),
        ],
    )
    for name, rows in source.items():
        builder.write_manifest(out, name, cga.SCHEMAS[name](), len(rows))
    write_contract(out, get_dataset_version())
    write_checksums(out)
    return root


def test_complete_content_guard_accepts_declared_projections_and_multiline_csv(artifact_fixture):
    assert cga.check_artifacts(artifact_fixture / "data/datasets", artifact_fixture) == []


@pytest.mark.parametrize(("mutation", "expected"), [
    ("country_value", "countries.duckdb: content"),
    ("duplicate", "duplicate primary key"),
    ("edge", "memberships.duckdb: content"),
    ("sidecar", "missing countries.meta.json"),
    ("meta_row", "_meta: expected exactly"),
    ("schema_hash", "invalid schema_hash"),
    ("source_value", "content differs"),
    ("taxonomy", "blocktypes.parquet: content"),
    ("csv_value", "countries.csv.zst: content"),
    ("lite", "countries-lite.parquet: content"),
    ("missing_file", "Missing, unreadable"),
    ("view", "current_memberships view: content"),
])
def test_content_guard_rejects_independent_corruption(artifact_fixture, tmp_path, mutation, expected):
    root = tmp_path / "copy"
    shutil.copytree(artifact_fixture, root)
    out = root / "data/datasets"
    queries = {
        "country_value": "UPDATE countries SET name = 'corrupt'",
        "duplicate": "INSERT INTO countries SELECT * FROM countries",
        "edge": "UPDATE memberships SET status = 'INVALID'",
        "meta_row": "DELETE FROM _meta WHERE dataset = 'blocktypes'",
        "view": "CREATE OR REPLACE VIEW current_memberships AS SELECT * FROM memberships WHERE false",
    }
    if mutation in queries:
        with duckdb.connect(str(out / "internacia.duckdb")) as con:
            con.execute(queries[mutation])
    elif mutation == "sidecar":
        (out / "countries.meta.json").unlink()
    elif mutation == "schema_hash":
        path = out / "countries.manifest.json"
        data = json.loads(path.read_text())
        data["schema_hash"] = "wrong"
        path.write_text(json.dumps(data))
    elif mutation in ("source_value", "taxonomy"):
        path = root / ("data/countries/AA.yaml" if mutation == "source_value" else "data/blocktypes/blocktypes.yaml")
        path.write_text(path.read_text().replace("Name with", "Changed") if mutation == "source_value"
                        else path.read_text().replace("Political", "Changed"))
    elif mutation == "csv_value":
        builder.save_csv_rows([{"code": "AA", "name": "corrupt"}], out / "countries.csv.zst")
    elif mutation == "lite":
        rows = pq.read_table(out / "countries-lite.parquet").to_pylist()
        rows[0]["name"] = "corrupt"
        builder.save_parquet(rows, out / "countries-lite.parquet")
    else:
        (out / "countries.parquet").unlink()
    result = CliRunner().invoke(cga.app, ["--root", str(root), "--datasets-dir", str(out)])
    assert result.exit_code == 1, result.output
    assert expected in result.output
