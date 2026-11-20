#!/usr/bin/env python3
"""Verify a complete bundle's content, source freshness, uniqueness, and metadata.

Full JSON/YAML records are compared with cleaned sources; columnar and tabular
formats use their declared projections. The default directory is data/datasets
after a local `scripts/builder.py build`; CI passes its staging directory.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path

import _checkout  # noqa: F401  (this checkout's internacia_builder, not an installed one)
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import typer
import yaml
import zstandard

from internacia_builder.clean import clean_data
from internacia_builder.contract import CONTRACT_FILE, file_digest, render_contract, verify_checksums
from internacia_builder.export import (
    COUNTRIES_LITE_FIELDS,
    INTBLOCKS_LITE_FIELDS,
    build_membership_rows,
    fill_country_include_names,
    flatten_country,
    flatten_intblock,
    load_attribute_intblock_migrations,
    load_border_status,
    load_country_aliases,
    load_intblock_aliases,
    project_lite_rows,
)
from internacia_builder.manifest import dataset_files
from internacia_builder.schemas import (
    get_aliases_schema,
    get_attribute_migration_schema,
    get_blocktypes_schema,
    get_border_status_schema,
    get_countries_schema,
    get_intblocks_schema,
    get_memberships_schema,
    schema_hash,
)

app = typer.Typer(add_completion=False, help=__doc__)
ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "countries": {"key": "code", "source": "data/countries", "glob": "*.yaml"},
    "intblocks": {"key": "id", "source": "data/intblocks", "glob": "**/*.yaml"},
    "blocktypes": {"key": "id", "source": "data/blocktypes/blocktypes.yaml", "glob": None},
}
SCHEMAS = {
    "countries": get_countries_schema,
    "intblocks": get_intblocks_schema,
    "blocktypes": get_blocktypes_schema,
    "memberships": get_memberships_schema,
}


def _source_rows(spec: dict, root: Path) -> list[dict]:
    base = root / spec["source"]
    if spec["glob"] is None:
        rows = yaml.safe_load(base.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"{base}: expected a list")
        return rows
    paths = sorted(base.glob(spec["glob"]))
    if not paths:
        raise ValueError(f"{base}: no source records")
    rows = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths]
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{base}: expected object records")
    return rows


def _source_ids(spec: dict, root: Path) -> set[str]:
    return {str(r[spec["key"]]) for r in _source_rows(spec, root)}


def _decompress(path: Path) -> bytes:
    with path.open("rb") as stream, zstandard.ZstdDecompressor().stream_reader(stream) as reader:
        return reader.read()


def _jsonl_rows(path: Path) -> list[dict]:
    data = _decompress(path) if path.suffix == ".zst" else path.read_bytes()
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def _jsonl_ids(path: Path, key: str) -> set[str]:
    return {str(row[key]) for row in _jsonl_rows(path)}


def _yaml_zst_ids(path: Path, key: str) -> set[str]:
    return {str(row[key]) for row in yaml.safe_load(_decompress(path))}


def _parquet_ids(path: Path, key: str) -> set[str]:
    return {str(v) for v in pq.read_table(path, columns=[key]).column(key).to_pylist()}


def _canonical(row: dict) -> str:
    return json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _compare(rows: list[dict], expected: list[dict], label: str, problems: list[str], key: str | None = None):
    if key:
        keys = [row.get(key) for row in rows]
        if any(k is None or k == "" for k in keys) or len(set(keys)) != len(keys):
            problems.append(f"{label}: missing or duplicate primary key {key}")
    if len(rows) != len(expected):
        problems.append(f"{label}: row count {len(rows)} != source projection {len(expected)}")
    actual_set = Counter(_canonical(row) for row in rows)
    expected_set = Counter(_canonical(row) for row in expected)
    if actual_set != expected_set:
        problems.append(f"{label}: content differs from source projection")


def _csv_rows(path: Path) -> list[dict]:
    return list(csv.DictReader(io.StringIO(_decompress(path).decode("utf-8"), newline="")))


def _csv_expected(rows: list[dict]) -> list[dict]:
    return [{k: "" if v is None else str(v) for k, v in row.items()} for row in rows]


def _arrow_rows(rows: list[dict], schema: pa.Schema) -> list[dict]:
    return pa.Table.from_pylist(rows, schema=schema).to_pylist()


def _check_manifest_files(datasets_dir: Path, name: str, manifest: dict, problems: list[str]) -> None:
    listed = {entry.get("path"): entry for entry in manifest.get("files") or []}
    expected = {path.name for path in dataset_files(datasets_dir, name)}
    if set(listed) != expected:
        problems.append(f"{name}.manifest.json: files {sorted(listed)} != dataset files {sorted(expected)}")
    for file_name in sorted(set(listed) & expected):
        if {k: listed[file_name].get(k) for k in ("sha256", "bytes")} != file_digest(datasets_dir / file_name):
            problems.append(f"{name}.manifest.json: checksum or size of {file_name} does not match the file")


def _check_contract(datasets_dir: Path, version: str, problems: list[str]) -> None:
    path = datasets_dir / CONTRACT_FILE
    if not path.is_file():
        problems.append(f"{CONTRACT_FILE}: missing")
    elif path.read_text(encoding="utf-8") != render_contract(version):
        problems.append(f"{CONTRACT_FILE}: differs from the contract generated from the current schemas")


def _expected_views(source: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Rows each canonical view must return, computed independently of its SQL."""
    countries = _arrow_rows(source["countries"], get_countries_schema())
    current_status = {
        frozenset((row["country_a"], row["country_b"])): row["status"]
        for row in source.get("border_status") or [] if row.get("until") is None
    }
    ended = {
        row["id"] for row in source["intblocks"] if row.get("status") == "historical" or row.get("dissolved") is not None
    }
    memberships = _arrow_rows(source["memberships"], get_memberships_schema())
    return {
        "current_memberships": [
            m for m in memberships
            if m["status"] != "former_member" and m["left"] is None and m["intblock_id"] not in ended
        ],
        "country_currencies": [
            {"country_code": c["code"], "currency_code": x["code"], "currency_name": x["name"], "currency_symbol": x["symbol"]}
            for c in countries for x in c["currencies"] or []
        ],
        "country_languages": [
            {"country_code": c["code"], "language_code": x["code"], "language_name": x["name"], "official": x["official"]}
            for c in countries for x in c["languages"] or []
        ],
        "country_timezones": [{"country_code": c["code"], "timezone": tz} for c in countries for tz in c["timezones"] or []],
        "country_borders": [
            {
                "country_code": c["code"],
                "iso3code": c["iso3code"],
                "neighbor_iso3": b,
                "current_status": current_status.get(frozenset((c["iso3code"], b))),
            }
            for c in countries for b in c["borders"] or []
        ],
    }


def check_artifacts(datasets_dir: Path, root: Path) -> list[str]:
    """Return actionable mismatches; the input bundle and sources are never changed."""
    problems: list[str] = []
    identities: dict[str, dict] = {}
    source = {name: clean_data(_source_rows(spec, root), name) for name, spec in DATASETS.items()}
    fill_country_include_names(source["intblocks"], source["countries"])
    source["memberships"] = build_membership_rows(source["intblocks"])
    source["border_status"] = load_border_status(root)
    con = duckdb.connect(str(datasets_dir / "internacia.duckdb"), read_only=True)
    try:
        meta = con.sql("SELECT * FROM _meta").to_arrow_table().to_pylist()
        if Counter(r["dataset"] for r in meta) != Counter(dict.fromkeys(SCHEMAS, 1)):
            problems.append("_meta: expected exactly one row per dataset")
        for name, schema_fn in SCHEMAS.items():
            schema = schema_fn()
            expected = _arrow_rows(source[name], schema)
            key = DATASETS[name]["key"] if name in DATASETS else None
            table = pq.read_table(datasets_dir / f"{name}.parquet")
            if not table.schema.equals(schema, check_metadata=False):
                problems.append(f"{name}.parquet: schema differs from declared export schema")
            _compare(table.to_pylist(), expected, f"{name}.parquet", problems, key)
            duck_rows = con.sql(f"SELECT * FROM {name}").to_arrow_table().to_pylist()
            _compare(duck_rows, expected, f"{name}.duckdb", problems, key)
            if name in DATASETS:
                _compare(source[name], source[name], f"{name}.source", problems, key)
                for ext, reader in (
                    ("jsonl.zst", _jsonl_rows),
                    ("jsonl", _jsonl_rows),
                    ("yaml.zst", lambda p: yaml.safe_load(_decompress(p))),
                ):
                    _compare(reader(datasets_dir / f"{name}.{ext}"), source[name], f"{name}.{ext}", problems, key)
                if (datasets_dir / f"{name}.jsonl").read_bytes() != _decompress(datasets_dir / f"{name}.jsonl.zst"):
                    problems.append(f"{name}: plain JSONL bytes differ from compressed JSONL")
            metadata = []
            for suffix in ("manifest.json", "meta.json"):
                path = datasets_dir / f"{name}.{suffix}"
                if not path.is_file():
                    problems.append(f"{name}: missing {path.name}")
                else:
                    metadata.append((path.name, json.loads(path.read_text(encoding="utf-8"))))
            metadata.extend((f"{name}._meta", row) for row in meta if row["dataset"] == name)
            if metadata and metadata[0][0] == f"{name}.manifest.json":
                _check_manifest_files(datasets_dir, name, metadata[0][1], problems)
            for label, record in metadata:
                for field, value in (("dataset", name), ("row_count", len(expected)), ("schema_hash", schema_hash(schema))):
                    if record.get(field) != value:
                        problems.append(f"{label}: invalid {field}: {record.get(field)!r}, expected {value!r}")
                identity = {
                    k: record.get(k) for k in ("version", "git_commit", "build_date", "data_license", "contract_version")
                }
                if any(not value for value in identity.values()):
                    problems.append(f"{label}: incomplete build identity")
                identities[label] = identity
        for name, flatten, fields in (
            ("countries", flatten_country, COUNTRIES_LITE_FIELDS),
            ("intblocks", flatten_intblock, INTBLOCKS_LITE_FIELDS),
        ):
            rows = [flatten(row) for row in source[name]]
            lite = project_lite_rows(rows, fields)
            for basename, expected in ((name, rows), (f"{name}-lite", lite)):
                _compare(_csv_rows(datasets_dir / f"{basename}.csv.zst"), _csv_expected(expected), f"{basename}.csv.zst", problems)
            _compare(pq.read_table(datasets_dir / f"{name}-lite.parquet").to_pylist(), lite, f"{name}-lite.parquet", problems)
            _compare(json.loads(_decompress(datasets_dir / f"{name}.json.zst")), source[name], f"{name}.json.zst", problems, DATASETS[name]["key"])
        _compare(_csv_rows(datasets_dir / "memberships.csv.zst"), _csv_expected(source["memberships"]), "memberships.csv.zst", problems)
        for name, loader in (("countries_aliases", load_country_aliases), ("intblocks_aliases", load_intblock_aliases)):
            expected = loader(root)
            _compare(json.loads((datasets_dir / f"{name}.json").read_text()), expected, f"{name}.json", problems, "alias")
            _compare(pq.read_table(datasets_dir / f"{name}.parquet").to_pylist(), expected, f"{name}.parquet", problems, "alias")
            duck = con.sql(f"SELECT * FROM {name}").to_arrow_table().to_pylist()
            _compare(duck, _arrow_rows(expected, get_aliases_schema()), f"{name}.duckdb", problems, "alias")
        border_status = source["border_status"]
        _compare(json.loads((datasets_dir / "border_status.json").read_text()), border_status, "border_status.json", problems)
        _compare(pq.read_table(datasets_dir / "border_status.parquet").to_pylist(),
                 _arrow_rows(border_status, get_border_status_schema()), "border_status.parquet", problems)
        duck = con.sql("SELECT * FROM border_status").to_arrow_table().to_pylist()
        _compare(duck, _arrow_rows(border_status, get_border_status_schema()), "border_status.duckdb", problems)
        migrations = _arrow_rows(load_attribute_intblock_migrations(root), get_attribute_migration_schema())
        duck = con.sql("SELECT * FROM attribute_intblock_migrations").to_arrow_table().to_pylist()
        _compare(duck, migrations, "attribute_intblock_migrations.duckdb", problems, "retired_id")
        for name, expected in _expected_views(source).items():
            duck = con.sql(f"SELECT * FROM {name}").to_arrow_table().to_pylist()
            _compare(duck, expected, f"{name} view", problems)
        if len({_canonical(i) for i in identities.values()}) != 1:
            problems.append("build identity differs across artifacts")
        versions = {identity["version"] for identity in identities.values()}
        if len(versions) == 1:
            _check_contract(datasets_dir, versions.pop(), problems)
        problems.extend(verify_checksums(datasets_dir))
    finally:
        con.close()
    return problems


@app.command()
def main(
    datasets_dir: Path = typer.Option(ROOT / "data" / "datasets", help="Dataset bundle to verify."),
    root: Path = typer.Option(ROOT, help="Repository root for source data."),
) -> None:
    try:
        problems = check_artifacts(datasets_dir.resolve(), root.resolve())
    except (OSError, ValueError, KeyError, TypeError, duckdb.Error, pa.ArrowException, yaml.YAMLError) as exc:
        problems = [f"Missing, unreadable, or invalid artifact/source: {exc}"]
    if problems:
        typer.echo("Artifact consistency check FAILED:")
        for problem in problems:
            typer.echo(f"  {problem}")
        raise typer.Exit(1)
    typer.echo("Artifact consistency OK: all source projections, values, row counts, keys, schemas, metadata, contract, and checksums agree")


if __name__ == "__main__":
    app()
