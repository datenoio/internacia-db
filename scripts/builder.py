#!/usr/bin/env python3
"""
Dataset builder for Internacia project.

This script generates datasets from data/countries and data/intblocks directories
in multiple formats: JSONL (zstd), YAML (zstd), Parquet (zstd), and DuckDB database.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import jsonschema
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import typer
import yaml
import zstandard as zstd
from tqdm import tqdm

from internacia_builder.paths import project_root as package_project_root
from internacia_builder.validate.countries import run_validation as run_countries_validation
from internacia_builder.validate.intblocks import run_validation as run_intblocks_validation

app = typer.Typer(help="Dataset builder for Internacia project")


def get_project_root() -> Path:
    """Get the project root directory."""
    return package_project_root()


def blocktypes_source_path(root: Path | None = None) -> Path:
    """Authoritative blocktypes taxonomy YAML (not generated)."""
    root = root or get_project_root()
    return root / "data" / "blocktypes" / "blocktypes.yaml"


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=get_project_root(),
            check=True,
        )
        return result.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_dataset_version() -> str:
    changelog = get_project_root() / "CHANGELOG.md"
    if not changelog.exists():
        return "unknown"
    text = changelog.read_text(encoding="utf-8")
    dated = re.findall(r"## \[([^\]]+)\] - \d{4}-\d{2}-\d{2}", text)
    if dated:
        return dated[0]
    match = re.search(r"## \[([^\]]+)\]", text)
    return match.group(1) if match else "unknown"


# SPDX identifier for the dataset (data) license; see DATA_LICENSE / ATTRIBUTION.md.
DATA_LICENSE_SPDX = "CC-BY-4.0"


def schema_hash(schema: pa.Schema) -> str:
    digest = hashlib.sha256(schema.serialize().to_pybytes()).hexdigest()
    return digest[:16]


def dataset_metadata(
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> dict[str, Any]:
    """Build the canonical metadata record shared by manifests, the DuckDB
    ``_meta`` table, and Parquet ``.meta.json`` sidecars."""
    return {
        "dataset": dataset,
        "version": get_dataset_version(),
        "build_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": get_git_commit(),
        "row_count": row_count,
        "schema_hash": schema_hash(schema),
        "data_license": DATA_LICENSE_SPDX,
    }


def write_manifest(
    output_dir: Path,
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> None:
    manifest = dataset_metadata(dataset, schema, row_count)
    path = output_dir / f"{dataset}.manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved manifest: {path}")


def write_meta_sidecar(
    output_dir: Path,
    dataset: str,
    schema: pa.Schema,
    row_count: int,
) -> None:
    """Write a ``<dataset>.meta.json`` sidecar next to the Parquet export so
    Parquet-only consumers can read version info without the full manifest."""
    meta = dataset_metadata(dataset, schema, row_count)
    path = output_dir / f"{dataset}.meta.json"
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved meta sidecar: {path}")


def get_meta_schema() -> pa.Schema:
    """Schema for the embedded DuckDB ``_meta`` table."""
    return pa.schema(
        [
            ("dataset", pa.string()),
            ("version", pa.string()),
            ("build_date", pa.string()),
            ("git_commit", pa.string()),
            ("row_count", pa.int64()),
            ("schema_hash", pa.string()),
            ("data_license", pa.string()),
        ]
    )


def _indicator_struct(value_type: pa.DataType) -> pa.DataType:
    return pa.struct(
        [
            ("value", value_type),
            ("year", pa.int64()),
            ("source", pa.string()),
            ("source_id", pa.string()),
        ]
    )


def get_countries_schema() -> pa.Schema:
    """Define explicit PyArrow schema for countries."""
    return pa.schema(
        [
            ("code", pa.string()),
            ("name", pa.string()),
            ("iso3code", pa.string()),
            ("capital_city", pa.struct([("name", pa.string()), ("lng", pa.float64()), ("lat", pa.float64())])),
            ("region", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("adminregion", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("incomeLevel", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("lendingType", pa.struct([("id", pa.string()), ("value", pa.string())])),
            ("numeric_code", pa.string()),
            ("wikidata_id", pa.string()),
            ("official_name", pa.string()),
            (
                "languages",
                pa.list_(pa.struct([("code", pa.string()), ("name", pa.string()), ("official", pa.bool_())])),
            ),
            (
                "currencies",
                pa.list_(pa.struct([("code", pa.string()), ("name", pa.string()), ("symbol", pa.string())])),
            ),
            ("un_member", pa.bool_()),
            ("independent", pa.bool_()),
            ("entity_type", pa.string()),
            ("code_status", pa.string()),
            (
                "recognition_status",
                pa.struct(
                    [
                        ("status", pa.string()),
                        ("un_member", pa.bool_()),
                        ("notes", pa.string()),
                    ]
                ),
            ),
            (
                "parent_entity",
                pa.struct(
                    [
                        ("code", pa.string()),
                        ("name", pa.string()),
                    ]
                ),
            ),
            ("subregion", pa.string()),
            ("continents", pa.list_(pa.string())),
            ("borders", pa.list_(pa.string())),
            ("landlocked", pa.bool_()),
            ("tld", pa.string()),
            ("calling_codes", pa.list_(pa.string())),
            ("flag_emoji", pa.string()),
            ("car_side", pa.string()),
            ("start_of_week", pa.string()),
            ("demonyms", pa.struct([("female", pa.string()), ("male", pa.string())])),
            ("m49_code", pa.string()),
            ("population", _indicator_struct(pa.int64())),
            ("area", _indicator_struct(pa.float64())),
            ("gini", _indicator_struct(pa.float64())),
            ("centroid", pa.struct([("lat", pa.float64()), ("lng", pa.float64())])),
            ("timezones", pa.list_(pa.string())),
            ("timezone_status", pa.string()),
            ("native_names", pa.map_(pa.string(), pa.struct([("official", pa.string()), ("common", pa.string())]))),
            ("other_names", pa.list_(pa.struct([("id", pa.string()), ("name", pa.string())]))),
            ("common_names", pa.list_(pa.string())),
            (
                "provenance",
                pa.list_(
                    pa.struct(
                        [
                            ("field", pa.string()),
                            ("source", pa.string()),
                            ("url", pa.string()),
                            ("retrieved_at", pa.string()),
                            ("license", pa.string()),
                        ]
                    )
                ),
            ),
        ]
    )


def get_intblocks_schema() -> pa.Schema:
    """Define explicit PyArrow schema for intblocks."""
    return pa.schema(
        [
            ("id", pa.string()),
            ("blocktype", pa.list_(pa.string())),
            ("status", pa.string()),
            ("name", pa.string()),
            ("languages", pa.list_(pa.string())),
            ("links", pa.list_(pa.struct([("url", pa.string()), ("type", pa.string())]))),
            ("translations", pa.list_(pa.struct([("lang", pa.string()), ("name", pa.string())]))),
            ("founded", pa.string()),
            ("geographic_scope", pa.string()),
            ("regions", pa.list_(pa.string())),
            (
                "includes",
                pa.list_(
                    pa.struct(
                        [
                            ("id", pa.string()),
                            ("name", pa.string()),
                            ("type", pa.string()),
                            ("status", pa.string()),
                            ("joined", pa.string()),
                            ("role", pa.string()),
                            ("note", pa.string()),
                        ]
                    )
                ),
            ),
            ("membership_count", pa.int64()),
            ("wikidata_id", pa.string()),
            ("legal_status", pa.string()),
            ("description", pa.string()),
            ("tags", pa.list_(pa.string())),
            ("topics", pa.list_(pa.struct([("key", pa.string()), ("name", pa.string())]))),
            (
                "headquarters",
                pa.struct(
                    [
                        ("city", pa.string()),
                        ("country", pa.string()),
                        ("coordinates", pa.struct([("lat", pa.float64()), ("lng", pa.float64())])),
                    ]
                ),
            ),
            ("acronyms", pa.list_(pa.struct([("lang", pa.string()), ("value", pa.string())]))),
            ("partof", pa.list_(pa.string())),  # Normalized to list of strings
            ("dissolved", pa.string()),
            ("predecessor", pa.string()),
            ("successor", pa.string()),
            ("other_names", pa.list_(pa.struct([("id", pa.string()), ("name", pa.string())]))),
            (
                "provenance",
                pa.list_(
                    pa.struct(
                        [
                            ("field", pa.string()),
                            ("source", pa.string()),
                            ("url", pa.string()),
                            ("retrieved_at", pa.string()),
                            ("license", pa.string()),
                        ]
                    )
                ),
            ),
        ]
    )


def get_blocktypes_schema() -> pa.Schema:
    """Define explicit PyArrow schema for blocktypes."""
    return pa.schema(
        [
            ("id", pa.string()),
            ("name", pa.string()),
            ("other_names", pa.list_(pa.struct([("lang", pa.string()), ("name", pa.string())]))),
        ]
    )


def clean_data(data: list[dict[str, Any]], dataset_type: str) -> list[dict[str, Any]]:
    """
    Clean data to ensure consistency with schema.

    Fixes known issues:
    - Boolean 'lang' values (from 'no' parsed as False) -> converted to "no"
    - Inconsistent 'partof' field -> normalized to list of strings
    - Boolean values in string fields -> converted to strings
    - None values in required string fields -> converted to empty strings
    """
    cleaned_data = []

    # String fields that should never be None or bool
    string_fields = {
        "id",
        "status",
        "name",
        "founded",
        "geographic_scope",
        "wikidata_id",
        "legal_status",
        "description",
        "dissolved",
        "predecessor",
        "successor",
    }

    for item in data:
        # Deep copy to avoid modifying original if needed, but for now just modifying dict
        cleaned_item = item.copy()

        if dataset_type == "intblocks":
            # Fix boolean languages in translations
            if "translations" in cleaned_item:
                new_translations = []
                for t in cleaned_item["translations"]:
                    if isinstance(t, dict):
                        new_t = t.copy()
                        if "lang" in new_t and isinstance(new_t["lang"], bool):
                            new_t["lang"] = "no" if new_t["lang"] is False else "yes"
                        if "name" in new_t and isinstance(new_t["name"], bool):
                            new_t["name"] = "no" if new_t["name"] is False else "yes"
                        new_translations.append(new_t)
                cleaned_item["translations"] = new_translations

            # Fix boolean languages list
            if "languages" in cleaned_item:
                new_languages = []
                for lang in cleaned_item["languages"]:
                    if isinstance(lang, bool):
                        new_languages.append("no" if lang is False else "yes")
                    else:
                        new_languages.append(str(lang))
                cleaned_item["languages"] = new_languages

            # Normalize partof to list of strings
            if "partof" in cleaned_item:
                partof = cleaned_item["partof"]
                if partof is None:
                    cleaned_item["partof"] = []
                elif isinstance(partof, str):
                    cleaned_item["partof"] = [partof]
                elif isinstance(partof, dict):
                    # If it's a dict, it might be an ID->Name map or similar
                    # For now, let's just take keys if they look like IDs
                    cleaned_item["partof"] = list(partof.keys())
                elif isinstance(partof, list):
                    # Ensure all items are strings
                    cleaned_item["partof"] = [str(p) for p in partof]

            # Fix boolean values in string fields
            for field in string_fields:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""

            # Ensure includes fields are strings
            if "includes" in cleaned_item:
                for member in cleaned_item["includes"]:
                    if isinstance(member, dict):
                        for key in ["id", "name", "type", "status", "joined", "role", "note"]:
                            if key in member:
                                if isinstance(member[key], bool):
                                    member[key] = "yes" if member[key] else "no"
                                elif member[key] is None:
                                    member[key] = ""

            # Ensure links fields are strings
            if "links" in cleaned_item:
                for link in cleaned_item["links"]:
                    if isinstance(link, dict):
                        for key in ["url", "type"]:
                            if key in link:
                                if isinstance(link[key], bool):
                                    link[key] = "yes" if link[key] else "no"
                                elif link[key] is None:
                                    link[key] = ""

            # Ensure other_names fields are strings
            if "other_names" in cleaned_item:
                for name in cleaned_item["other_names"]:
                    if isinstance(name, dict):
                        for key in ["id", "name"]:
                            if key in name:
                                if isinstance(name[key], bool):
                                    name[key] = "yes" if name[key] else "no"
                                elif name[key] is None:
                                    name[key] = ""

            # Ensure acronyms fields are strings
            if "acronyms" in cleaned_item:
                for acronym in cleaned_item["acronyms"]:
                    if isinstance(acronym, dict):
                        for key in ["lang", "value"]:
                            if key in acronym:
                                if isinstance(acronym[key], bool):
                                    acronym[key] = "yes" if acronym[key] else "no"
                                elif acronym[key] is None:
                                    acronym[key] = ""

            # Ensure headquarters fields are strings/floats
            if "headquarters" in cleaned_item:
                hq = cleaned_item["headquarters"]
                if isinstance(hq, dict):
                    for key in ["city", "country"]:
                        if key in hq:
                            if isinstance(hq[key], bool):
                                hq[key] = "yes" if hq[key] else "no"
                            elif hq[key] is None:
                                hq[key] = ""
                    if "coordinates" in hq and isinstance(hq["coordinates"], dict):
                        for key in ["lat", "lng"]:
                            if key in hq["coordinates"]:
                                if isinstance(hq["coordinates"][key], bool):
                                    hq["coordinates"][key] = 0.0
                                elif hq["coordinates"][key] is None:
                                    hq["coordinates"][key] = 0.0

            # Ensure topics fields are strings
            if "topics" in cleaned_item:
                for topic in cleaned_item["topics"]:
                    if isinstance(topic, dict):
                        for key in ["key", "name"]:
                            if key in topic:
                                if isinstance(topic[key], bool):
                                    topic[key] = "yes" if topic[key] else "no"
                                elif topic[key] is None:
                                    topic[key] = ""

            # Normalize provenance entries (None -> [], None subfields -> "")
            prov = cleaned_item.get("provenance")
            if prov is None:
                cleaned_item["provenance"] = []
            elif isinstance(prov, list):
                for entry in prov:
                    if isinstance(entry, dict):
                        for key in ("field", "source", "url", "retrieved_at", "license"):
                            if key in entry and entry[key] is None:
                                entry[key] = ""

        if dataset_type == "countries":
            sub = cleaned_item.get("subregion")
            if isinstance(sub, str):
                cleaned_item["subregion"] = sub.strip()
            for key in ("region", "adminregion"):
                obj = cleaned_item.get(key)
                if isinstance(obj, dict) and isinstance(obj.get("value"), str):
                    obj["value"] = obj["value"].strip()

            if cleaned_item.get("borders") is None:
                cleaned_item["borders"] = []

            for field in ("population", "area", "gini"):
                val = cleaned_item.get(field)
                if isinstance(val, (int, float)) and field == "population":
                    cleaned_item[field] = {
                        "value": int(val),
                        "year": None,
                        "source": "legacy",
                        "source_id": "",
                    }
                elif isinstance(val, (int, float)) and field == "area":
                    cleaned_item[field] = {
                        "value": float(val),
                        "year": None,
                        "source": "legacy",
                        "source_id": "",
                    }
                elif isinstance(val, dict):
                    raw_year = val.get("year")
                    cleaned_item[field] = {
                        "value": val.get("value"),
                        # Unknown years export as null, never a fabricated 0.
                        "year": int(raw_year) if raw_year else None,
                        "source": str(val.get("source") or ""),
                        "source_id": str(val.get("source_id") or ""),
                    }

            cc = cleaned_item.get("capital_city")
            if isinstance(cc, dict):
                for coord in ("lat", "lng"):
                    if coord in cc and cc[coord] is not None:
                        try:
                            cc[coord] = float(cc[coord])
                        except (TypeError, ValueError):
                            cc[coord] = 0.0
                    elif coord not in cc:
                        cc[coord] = 0.0

            prov = cleaned_item.get("provenance")
            if prov is None:
                cleaned_item["provenance"] = []
            elif isinstance(prov, list):
                for entry in prov:
                    if isinstance(entry, dict):
                        for key in ("field", "source", "url", "retrieved_at", "license"):
                            if key in entry and entry[key] is None:
                                entry[key] = ""

        if dataset_type == "blocktypes":
            # Ensure other_names fields are strings
            if "other_names" in cleaned_item:
                if cleaned_item["other_names"] is None:
                    cleaned_item["other_names"] = []
                elif isinstance(cleaned_item["other_names"], list):
                    for name in cleaned_item["other_names"]:
                        if isinstance(name, dict):
                            for key in ["lang", "name"]:
                                if key in name:
                                    if isinstance(name[key], bool):
                                        name[key] = "yes" if name[key] else "no"
                                    elif name[key] is None:
                                        name[key] = ""
            # Ensure id and name are strings
            for field in ["id", "name"]:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""

        cleaned_data.append(cleaned_item)

    return cleaned_data


def get_aliases_schema() -> pa.Schema:
    """Schema for the intblock identifier alias artifact."""
    return pa.schema(
        [
            ("alias", pa.string()),
            ("target", pa.string()),
            ("reason", pa.string()),
            ("since", pa.string()),
            ("note", pa.string()),
        ]
    )


def load_intblock_aliases(project_root: Path) -> list[dict[str, Any]]:
    """Load the intblock identifier alias source (retired/renamed ids → current id)."""
    path = project_root / "data" / "intblocks_aliases.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []
    aliases: list[dict[str, Any]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        aliases.append(
            {
                "alias": str(entry.get("alias") or ""),
                "target": str(entry.get("target") or ""),
                "reason": str(entry.get("reason") or ""),
                "since": str(entry.get("since") or ""),
                "note": str(entry.get("note") or ""),
            }
        )
    return aliases


def save_aliases(aliases: list[dict[str, Any]], output_dir: Path, write_parquet: bool = True) -> None:
    """Write the intblock alias artifact as JSON and (optionally) Parquet."""
    json_path = output_dir / "intblocks_aliases.json"
    json_path.write_text(json.dumps(aliases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved alias map: {json_path}")
    if write_parquet:
        table = pa.Table.from_pylist(aliases, schema=get_aliases_schema())
        parquet_path = output_dir / "intblocks_aliases.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=22)
        typer.echo(f"✓ Saved alias map (parquet): {parquet_path}")


def load_yaml_files(directory: Path, desc: str = "Loading files") -> list[dict[str, Any]]:
    """Load all YAML files from a directory (including subdirectories).

    Raises RuntimeError if any file fails to parse, so a build can never
    silently ship with missing records.
    """
    yaml_files = list(directory.rglob("*.yaml"))
    data = []
    failures: list[str] = []

    for yaml_file in tqdm(yaml_files, desc=desc):
        try:
            with open(yaml_file, encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if content:
                    data.append(content)
        except Exception as e:
            typer.echo(f"Error loading {yaml_file}: {e}", err=True)
            failures.append(str(yaml_file))

    if failures:
        raise RuntimeError(f"Failed to load {len(failures)} YAML file(s): {', '.join(failures)}")

    return data


def save_jsonl_zst(data: list[dict[str, Any]], output_file: Path):
    """Save data as Zstandard-compressed JSONL file."""
    cctx = zstd.ZstdCompressor(level=22)
    with open(output_file, "wb") as f:
        with cctx.stream_writer(f) as compressor:
            for item in data:
                line = json.dumps(item, ensure_ascii=False) + "\n"
                compressor.write(line.encode("utf-8"))
    typer.echo(f"✓ Saved JSONL (zstd): {output_file}")


def save_yaml_zst(data: list[dict[str, Any]], output_file: Path):
    """Save data as Zstandard-compressed YAML file."""
    cctx = zstd.ZstdCompressor(level=22)
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(output_file, "wb") as f:
        f.write(cctx.compress(yaml_str.encode("utf-8")))
    typer.echo(f"✓ Saved YAML (zstd): {output_file}")


def save_parquet(data: list[dict[str, Any]], output_file: Path, schema: pa.Schema | None = None):
    """Save data as Parquet file using explicit schema and Zstd compression.

    Schema mismatches raise instead of silently falling back to pandas
    inference, so schema drift fails the build loudly.
    """
    table = pa.Table.from_pylist(data, schema=schema)
    pq.write_table(table, output_file, compression="zstd", compression_level=22)
    typer.echo(f"✓ Saved Parquet (zstd): {output_file}")


def create_duckdb_database(
    countries_data: list[dict[str, Any]],
    intblocks_data: list[dict[str, Any]],
    blocktypes_data: list[dict[str, Any]],
    output_file: Path,
    countries_schema: pa.Schema,
    intblocks_schema: pa.Schema,
    blocktypes_schema: pa.Schema,
):
    """Create DuckDB database with countries, intblocks, and blocktypes tables."""
    # Remove existing database if it exists
    if output_file.exists():
        output_file.unlink()

    # Connect to DuckDB
    con = duckdb.connect(str(output_file))

    try:
        tables = [
            ("countries", countries_data, countries_schema),
            ("intblocks", intblocks_data, intblocks_schema),
            ("blocktypes", blocktypes_data, blocktypes_schema),
        ]
        counts = {}
        for name, data, schema in tables:
            typer.echo(f"Creating {name} table...")
            arrow_table = pa.Table.from_pylist(data, schema=schema)
            # Explicit registration: do not rely on DuckDB's implicit
            # replacement scan of local Python variables.
            con.register("arrow_source", arrow_table)
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM arrow_source")
            con.unregister("arrow_source")
            counts[name] = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]

        # Embed a self-describing _meta table (one row per dataset) so the
        # database file carries its own version/schema info.
        meta_rows = [dataset_metadata(name, schema, len(data)) for name, data, schema in tables]
        meta_table = pa.Table.from_pylist(meta_rows, schema=get_meta_schema())
        con.register("arrow_source", meta_table)
        con.execute("CREATE TABLE _meta AS SELECT * FROM arrow_source")
        con.unregister("arrow_source")

        typer.echo(f"✓ Saved DuckDB: {output_file}")
        typer.echo(f"  - Countries: {counts['countries']} rows")
        typer.echo(f"  - Intblocks: {counts['intblocks']} rows")
        typer.echo(f"  - Blocktypes: {counts['blocktypes']} rows")

    finally:
        con.close()


@app.command()
def build(
    output_dir: Path = typer.Option(
        None, "--output-dir", "-o", help="Output directory for datasets (default: data/datasets)"
    ),
    formats: str = typer.Option(
        "jsonl,yaml,parquet,duckdb",
        "--formats",
        "-f",
        help="Comma-separated list of formats to generate (jsonl, yaml, parquet, duckdb)",
    ),
):
    """
    Build datasets from data/countries, data/intblocks, and data/blocktypes/blocktypes.yaml.

    Generates datasets in multiple formats:
    - JSONL: Zstd-compressed line-delimited JSON
    - YAML: Zstd-compressed YAML
    - Parquet: Zstd-compressed Parquet with explicit schema
    - DuckDB: Database with countries, intblocks, and blocktypes tables
    """
    project_root = get_project_root()

    # Set default output directory
    if output_dir is None:
        output_dir = project_root / "data" / "datasets"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse formats
    requested_formats = [f.strip().lower() for f in formats.split(",")]
    valid_formats = {"jsonl", "yaml", "parquet", "duckdb"}
    invalid_formats = set(requested_formats) - valid_formats

    if invalid_formats:
        typer.echo(f"Error: Invalid formats: {', '.join(invalid_formats)}", err=True)
        typer.echo(f"Valid formats: {', '.join(valid_formats)}")
        raise typer.Exit(1)

    typer.echo("\n🚀 Building datasets...")
    typer.echo(f"Output directory: {output_dir}\n")

    # Load countries data
    countries_dir = project_root / "data" / "countries"
    if not countries_dir.exists():
        typer.echo(f"Error: Countries directory not found: {countries_dir}", err=True)
        raise typer.Exit(1)

    for dataset, run_fn in (
        ("countries", run_countries_validation),
        ("intblocks", run_intblocks_validation),
    ):
        typer.echo(f"📁 Validating {dataset} data...")
        if run_fn() != 0:
            typer.echo(f"{dataset} validation failed; aborting build.", err=True)
            raise typer.Exit(1)

    typer.echo("📁 Loading countries data...")
    try:
        countries_data = load_yaml_files(countries_dir, "Loading countries")
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    typer.echo(f"   Loaded {len(countries_data)} countries")

    countries_data = clean_data(countries_data, "countries")

    # Load intblocks data
    intblocks_dir = project_root / "data" / "intblocks"
    if not intblocks_dir.exists():
        typer.echo(f"Error: Intblocks directory not found: {intblocks_dir}", err=True)
        raise typer.Exit(1)

    typer.echo("📁 Loading intblocks data...")
    try:
        intblocks_data = load_yaml_files(intblocks_dir, "Loading intblocks")
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    typer.echo(f"   Loaded {len(intblocks_data)} intblocks")

    # Clean intblocks data
    typer.echo("🧹 Cleaning data...")
    intblocks_data = clean_data(intblocks_data, "intblocks")

    # Load blocktypes data
    blocktypes_file = blocktypes_source_path(project_root)
    if not blocktypes_file.exists():
        typer.echo(f"Error: Blocktypes source not found: {blocktypes_file}", err=True)
        raise typer.Exit(1)

    typer.echo("📁 Loading blocktypes data...")
    try:
        with open(blocktypes_file, encoding="utf-8") as f:
            blocktypes_data = yaml.safe_load(f)
            if blocktypes_data is None:
                blocktypes_data = []
            elif not isinstance(blocktypes_data, list):
                typer.echo(f"Warning: blocktypes.yaml should contain a list, got {type(blocktypes_data)}", err=True)
                blocktypes_data = []
    except Exception as e:
        typer.echo(f"Error loading {blocktypes_file}: {e}", err=True)
        raise typer.Exit(1) from e

    typer.echo(f"   Loaded {len(blocktypes_data)} blocktypes")

    # Clean blocktypes data
    blocktypes_data = clean_data(blocktypes_data, "blocktypes")

    blocktypes_yaml_out = output_dir / "blocktypes.yaml"
    blocktypes_yaml_out.write_text(
        yaml.dump(blocktypes_data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )

    # Load intblock identifier aliases (retired/renamed ids → current id)
    intblock_aliases = load_intblock_aliases(project_root)
    typer.echo(f"   Loaded {len(intblock_aliases)} intblock alias(es)")

    # Get schemas
    countries_schema = get_countries_schema()
    intblocks_schema = get_intblocks_schema()
    blocktypes_schema = get_blocktypes_schema()

    # Generate datasets
    typer.echo("\n💾 Generating datasets...\n")

    # Generate for countries
    if "jsonl" in requested_formats:
        save_jsonl_zst(countries_data, output_dir / "countries.jsonl.zst")
        save_jsonl_zst(intblocks_data, output_dir / "intblocks.jsonl.zst")
        save_jsonl_zst(blocktypes_data, output_dir / "blocktypes.jsonl.zst")

    if "yaml" in requested_formats:
        save_yaml_zst(countries_data, output_dir / "countries.yaml.zst")
        save_yaml_zst(intblocks_data, output_dir / "intblocks.yaml.zst")
        save_yaml_zst(blocktypes_data, output_dir / "blocktypes.yaml.zst")

    if "parquet" in requested_formats:
        save_parquet(countries_data, output_dir / "countries.parquet", schema=countries_schema)
        save_parquet(intblocks_data, output_dir / "intblocks.parquet", schema=intblocks_schema)
        save_parquet(blocktypes_data, output_dir / "blocktypes.parquet", schema=blocktypes_schema)
        write_manifest(output_dir, "countries", countries_schema, len(countries_data))
        write_manifest(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
        write_meta_sidecar(output_dir, "countries", countries_schema, len(countries_data))
        write_meta_sidecar(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
        write_meta_sidecar(output_dir, "blocktypes", blocktypes_schema, len(blocktypes_data))

    if "duckdb" in requested_formats:
        create_duckdb_database(
            countries_data,
            intblocks_data,
            blocktypes_data,
            output_dir / "internacia.duckdb",
            countries_schema=countries_schema,
            intblocks_schema=intblocks_schema,
            blocktypes_schema=blocktypes_schema,
        )
        if "parquet" not in requested_formats:
            write_manifest(output_dir, "countries", countries_schema, len(countries_data))
            write_manifest(output_dir, "intblocks", intblocks_schema, len(intblocks_data))

    # Always emit the intblock alias artifact so consumers can remap retired ids.
    save_aliases(intblock_aliases, output_dir, write_parquet="parquet" in requested_formats)

    typer.echo("\n✅ All datasets generated successfully!")
    typer.echo(f"📂 Output location: {output_dir}")


@app.command()
def info():
    """Display information about the builder and available data sources."""
    project_root = get_project_root()

    typer.echo("\n📊 Internacia Dataset Builder\n")
    typer.echo("Data sources:")

    countries_dir = project_root / "data" / "countries"
    if countries_dir.exists():
        country_files = list(countries_dir.rglob("*.yaml"))
        typer.echo(f"  • Countries: {len(country_files)} files in {countries_dir}")
    else:
        typer.echo(f"  • Countries: ❌ Not found at {countries_dir}")

    intblocks_dir = project_root / "data" / "intblocks"
    if intblocks_dir.exists():
        intblock_files = list(intblocks_dir.rglob("*.yaml"))
        subdirs = [d for d in intblocks_dir.iterdir() if d.is_dir()]
        typer.echo(f"  • Intblocks: {len(intblock_files)} files in {intblocks_dir}")
        typer.echo(f"    Categories: {', '.join([d.name for d in subdirs])}")
    else:
        typer.echo(f"  • Intblocks: ❌ Not found at {intblocks_dir}")

    typer.echo("\nSupported formats:")
    typer.echo("  • JSONL - Zstd-compressed line-delimited JSON")
    typer.echo("  • YAML - Zstd-compressed YAML")
    typer.echo("  • Parquet - Zstd-compressed columnar format")
    typer.echo("  • DuckDB - Relational database with SQL support")
    typer.echo()
# ==============================================================================
# Data Quality Analysis and Reporting
# ==============================================================================

# Priority mapping for issue types
ISSUE_PRIORITY_MAP = {
    "CRITICAL": [
        "SCHEMA_ERROR",
        "DUPLICATE_IDENTIFIER",
        "DUPLICATE_INTBLOCK_ID",
    ],
    "IMPORTANT": [
        "INVALID_BORDER_REFERENCE",
        "INVALID_INDICATOR_YEAR",
        "INVALID_ENTITY_TYPE",
        "INVALID_CODE_STATUS",
        "INVALID_ISO_COUNT",
        "UNKNOWN_BLOCKTYPE",
        "ALIAS_INTEGRITY_ERROR",
        "UNRESOLVED_COUNTRY_INCLUDE",
        "COMPLETENESS_ERROR",
    ],
    "MEDIUM": [
        "UNRESOLVED_PARTOF_REF",
        "LIFECYCLE_INCONSISTENCY",
        "TEMPLATED_DESCRIPTION",
        "COMPLETENESS_WARN",
        "INVALID_URL",
        "INVALID_ID",
    ],
    "LOW": [
        "WHITESPACE_IN_CATEGORICAL_FIELD",
        "DUPLICATE_LINK",
    ],
}

RULE_DESCRIPTIONS = {
    "SCHEMA_ERROR": "YAML source does not validate against its JSON Schema definition.",
    "DUPLICATE_IDENTIFIER": "Multiple countries share the same code, ISO3 code, or numeric code.",
    "DUPLICATE_INTBLOCK_ID": "Multiple intblocks share the same ID.",
    "INVALID_BORDER_REFERENCE": "Country borders list references a non-existent or invalid alpha-3 code.",
    "INVALID_INDICATOR_YEAR": "Population, area, or Gini index contains a zero or negative year.",
    "INVALID_ENTITY_TYPE": "Country record has an invalid or missing entity type classification.",
    "INVALID_CODE_STATUS": "Country record has an invalid or missing ISO code status classification.",
    "INVALID_ISO_COUNT": "Total count of official ISO 3166-1 country records does not match the expected count (249).",
    "UNKNOWN_BLOCKTYPE": "An intblock references a blocktype not defined in the taxonomy.",
    "UNRESOLVED_PARTOF_REF": "An intblock's partof references a non-existent intblock ID.",
    "LIFECYCLE_INCONSISTENCY": "Historical intblock uses non-standard ended key or has status mismatch.",
    "ALIAS_INTEGRITY_ERROR": "Acronym alias targets an unresolved ID or is misconfigured.",
    "TEMPLATED_DESCRIPTION": "An intblock uses templated boilerplate description.",
    "UNRESOLVED_COUNTRY_INCLUDE": "An intblock's includes references a non-existent country code.",
    "COMPLETENESS_ERROR": "Completeness validation failed (error mode) due to too many missing values.",
    "COMPLETENESS_WARN": "Completeness validation warned (warn mode) due to missing values.",
    "WHITESPACE_IN_CATEGORICAL_FIELD": "Leading/trailing whitespace found in categorical text fields.",
    "DUPLICATE_LINK": "Multiple records share the same external URL.",
    "INVALID_URL": "A URL in the intblock is invalid or inaccessible.",
    "INVALID_ID": "A Wikidata Q-ID is invalid or doesn't match the record's name.",
}

EXPECTED_OFFICIAL_ISO_COUNT = 249


def get_priority_level(issue_type: str) -> str:
    for priority, issue_types in ISSUE_PRIORITY_MAP.items():
        if issue_type in issue_types:
            return priority
    return "MEDIUM"


def is_null_field(record: dict[str, Any], field: str) -> bool:
    if field == "timezones" and record.get("timezone_status") == "not_applicable":
        return False
    if field not in record:
        return True
    val = record[field]
    if val is None:
        return True
    if val == "" or val == [] or val == {}:
        return True
    return False


def extract_country_codes(record: dict[str, Any], dataset_type: str) -> list[str]:
    codes = []
    if dataset_type == "countries":
        code = record.get("code")
        if code:
            codes.append(str(code).upper())
    elif dataset_type == "intblocks":
        # Headquarters country
        hq = record.get("headquarters") or {}
        hq_country = hq.get("country")
        if hq_country and len(str(hq_country)) == 2:
            codes.append(str(hq_country).upper())
        
        # Includes countries
        for inc in record.get("includes") or []:
            if isinstance(inc, dict) and inc.get("type") == "country":
                cid = inc.get("id")
                if cid and len(str(cid)) == 2:
                    c_upper = str(cid).upper()
                    if c_upper not in codes:
                        codes.append(c_upper)
    return codes if codes else ["UNKNOWN"]


# Country Checker Functions
def check_country_schema(record: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(record), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append({
            "issue_type": "SCHEMA_ERROR",
            "field": path,
            "current_value": str(err.instance),
            "suggested_action": f"Fix schema error: {err.message}"
        })
    return errors


def check_country_borders(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    borders = record.get("borders")
    if borders is None:
        return errors
    if not isinstance(borders, list):
        errors.append({
            "issue_type": "INVALID_BORDER_REFERENCE",
            "field": "borders",
            "current_value": str(borders),
            "suggested_action": "borders must be a list of alpha-3 country codes"
        })
        return errors
    for b in borders:
        if not isinstance(b, str) or not re.match(r"^[A-Z]{3}$", b):
            errors.append({
                "issue_type": "INVALID_BORDER_REFERENCE",
                "field": "borders",
                "current_value": str(b),
                "suggested_action": f"border '{b}' must be ISO alpha-3 uppercase"
            })
    return errors


def check_country_indicator_years(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    for field in ("population", "area", "gini"):
        val = record.get(field)
        if not isinstance(val, dict):
            continue
        year = val.get("year")
        if year is None:
            continue
        if not isinstance(year, int) or isinstance(year, bool) or year <= 0:
            errors.append({
                "issue_type": "INVALID_INDICATOR_YEAR",
                "field": f"{field}.year",
                "current_value": str(year),
                "suggested_action": f"{field}.year must be a positive integer or omitted"
            })
    return errors


def check_country_whitespace(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    sub = record.get("subregion")
    if isinstance(sub, str) and sub != sub.strip():
        errors.append({
            "issue_type": "WHITESPACE_IN_CATEGORICAL_FIELD",
            "field": "subregion",
            "current_value": sub,
            "suggested_action": "Strip leading/trailing whitespace"
        })
    for key in ("region", "adminregion"):
        obj = record.get(key)
        if isinstance(obj, dict):
            val = obj.get("value")
            if isinstance(val, str) and val != val.strip():
                errors.append({
                    "issue_type": "WHITESPACE_IN_CATEGORICAL_FIELD",
                    "field": f"{key}.value",
                    "current_value": val,
                    "suggested_action": "Strip leading/trailing whitespace"
                })
    return errors


def check_country_entity_status(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    code = str(record.get("code", ""))
    entity_type = record.get("entity_type")
    code_status = record.get("code_status")

    entity_types = {
        "sovereign_state",
        "dependent_territory",
        "special_administrative_region",
        "disputed_territory",
        "historical_entity",
        "supranational_grouping",
        "statistical_area",
    }
    code_statuses = {
        "official_iso3166_1",
        "user_assigned",
        "obsolete",
        "exceptionally_reserved",
    }
    non_iso_alpha2 = {"AN", "JG", "KV"}

    if not entity_type:
        errors.append({
            "issue_type": "INVALID_ENTITY_TYPE",
            "field": "entity_type",
            "current_value": None,
            "suggested_action": "Specify entity_type"
        })
    elif entity_type not in entity_types:
        errors.append({
            "issue_type": "INVALID_ENTITY_TYPE",
            "field": "entity_type",
            "current_value": entity_type,
            "suggested_action": f"entity_type must be one of {sorted(entity_types)}"
        })

    if not code_status:
        errors.append({
            "issue_type": "INVALID_CODE_STATUS",
            "field": "code_status",
            "current_value": None,
            "suggested_action": "Specify code_status"
        })
    elif code_status not in code_statuses:
        errors.append({
            "issue_type": "INVALID_CODE_STATUS",
            "field": "code_status",
            "current_value": code_status,
            "suggested_action": f"code_status must be one of {sorted(code_statuses)}"
        })

    if code in non_iso_alpha2:
        if code_status == "official_iso3166_1":
            errors.append({
                "issue_type": "INVALID_CODE_STATUS",
                "field": "code_status",
                "current_value": code_status,
                "suggested_action": f"non-ISO code '{code}' must not have code_status official_iso3166_1"
            })
    elif code_status and code_status != "official_iso3166_1":
        if re.match(r"^[A-Z]{2}$", code) and code not in {"XA", "XS", "XT", "XN"}:
            errors.append({
                "issue_type": "INVALID_CODE_STATUS",
                "field": "code_status",
                "current_value": code_status,
                "suggested_action": f"ISO-style code '{code}' must have code_status official_iso3166_1"
            })

    return errors


def check_country_duplicates(records: list[dict[str, Any]], rel_paths: list[str]) -> list[dict[str, Any]]:
    errors = []
    by_code = {}
    by_iso3 = {}
    by_numeric = {}

    for path, rec in zip(rel_paths, records):
        record_id = rec.get("code", "unknown")
        for field, mapping in (
            ("code", by_code),
            ("iso3code", by_iso3),
            ("numeric_code", by_numeric),
        ):
            val = str(rec.get(field, ""))
            if not val:
                continue
            if val in mapping and mapping[val][0] != path:
                errors.append({
                    "issue_type": "DUPLICATE_IDENTIFIER",
                    "field": field,
                    "current_value": val,
                    "suggested_action": f"Duplicate {field} '{val}' found in both {path} and {mapping[val][0]}",
                    "file_path": path,
                    "record_id": record_id
                })
            else:
                mapping[val] = (path, record_id)
    return errors


def validate_official_iso_count(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    count = sum(1 for r in records if r.get("code_status") == "official_iso3166_1")
    if count != EXPECTED_OFFICIAL_ISO_COUNT:
        errors.append({
            "issue_type": "INVALID_ISO_COUNT",
            "field": "code_status",
            "current_value": str(count),
            "suggested_action": f"Expected exactly {EXPECTED_OFFICIAL_ISO_COUNT} official_iso3166_1 records, but found {count}"
        })
    return errors


def validate_completeness(records: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    n = len(records)
    if n == 0:
        return errors
    fields_cfg = config.get("fields", {})
    for field, rules in fields_cfg.items():
        null_count = sum(1 for r in records if is_null_field(r, field))
        null_rate = null_count / n
        max_rate = float(rules.get("max_null_rate", 1.0))
        mode = rules.get("mode", "warn")
        if null_rate > max_rate:
            issue_type = "COMPLETENESS_ERROR" if mode == "error" else "COMPLETENESS_WARN"
            errors.append({
                "issue_type": issue_type,
                "field": field,
                "current_value": f"{null_rate:.2%} null rate ({null_count}/{n})",
                "suggested_action": f"Ensure {field} is populated (max null rate allowed: {max_rate:.2%})"
            })
    return errors


# Intblocks Checker Functions
def check_intblock_schema(record: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(record), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append({
            "issue_type": "SCHEMA_ERROR",
            "field": path,
            "current_value": str(err.instance),
            "suggested_action": f"Fix schema error: {err.message}"
        })
    return errors


def check_intblock_duplicates(records: list[dict[str, Any]], rel_paths: list[str]) -> list[dict[str, Any]]:
    errors = []
    seen = {}
    for path, rec in zip(rel_paths, records):
        rid = str(rec.get("id", ""))
        if not rid:
            continue
        if rid in seen and seen[rid][0] != path:
            errors.append({
                "issue_type": "DUPLICATE_INTBLOCK_ID",
                "field": "id",
                "current_value": rid,
                "suggested_action": f"Duplicate intblock ID '{rid}' found in both {path} and {seen[rid][0]}",
                "file_path": path,
                "record_id": rid
            })
        else:
            seen[rid] = (path, rid)
    return errors


def check_intblock_blocktypes(record: dict[str, Any], taxonomy: set[str]) -> list[dict[str, Any]]:
    errors = []
    for bt in record.get("blocktype") or []:
        if str(bt) not in taxonomy:
            errors.append({
                "issue_type": "UNKNOWN_BLOCKTYPE",
                "field": "blocktype",
                "current_value": str(bt),
                "suggested_action": f"blocktype '{bt}' must exist in the blocktypes taxonomy"
            })
    return errors


def check_intblock_lifecycle(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    if "ended" in record:
        errors.append({
            "issue_type": "LIFECYCLE_INCONSISTENCY",
            "field": "ended",
            "current_value": str(record.get("ended")),
            "suggested_action": "Use the standard 'dissolved' field instead of 'ended'"
        })
    if record.get("dissolved") and record.get("status") not in ("historical", None):
        errors.append({
            "issue_type": "LIFECYCLE_INCONSISTENCY",
            "field": "status",
            "current_value": str(record.get("status")),
            "suggested_action": f"Record has a dissolved date but status is '{record.get('status')}', expected 'historical'"
        })
    return errors


def check_intblock_description_quality(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    desc = str(record.get("description") or "")
    templated_desc_re = re.compile(
        r"^\s*(international entity focused on|an? international (organization|entity)|"
        r"regional (organization|entity) focused on|international organization for)",
        re.IGNORECASE,
    )
    if templated_desc_re.match(desc):
        errors.append({
            "issue_type": "TEMPLATED_DESCRIPTION",
            "field": "description",
            "current_value": desc,
            "suggested_action": "Rewrite description to avoid templated boilerplate"
        })
    return errors


def check_intblock_links(
    record: dict[str, Any],
    check_http: bool = False,
    check_wikidata: bool = False,
) -> list[dict[str, Any]]:
    errors = []
    entity_name = record.get("name", "")
    links = record.get("links", [])
    wikidata_ids_in_links = []

    try:
        import sys
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        from validate_links import validate_url, validate_wikidata_entity, extract_wikidata_id, REQUEST_DELAY
    except ImportError:
        def extract_wikidata_id(url: str) -> str | None:
            match = re.search(r"Q\d+", url)
            return match.group(0) if match else None

        def validate_url(url: str, timeout: int = 10) -> tuple[bool, str, int]:
            return True, "", 200

        def validate_wikidata_entity(qid: str, entity_name: str) -> tuple[bool, str]:
            return True, ""
        
        REQUEST_DELAY = 0.0

    for i, link in enumerate(links):
        if not isinstance(link, dict):
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}]",
                "current_value": str(link),
                "suggested_action": "Link must be a dictionary"
            })
            continue

        url = link.get("url", "")
        link_type = link.get("type", "")

        if not url:
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}].url",
                "current_value": None,
                "suggested_action": "Missing URL"
            })
            continue

        if not link_type:
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}].type",
                "current_value": None,
                "suggested_action": "Missing type"
            })
            continue

        if link_type == "wikidata":
            qid = extract_wikidata_id(url)
            if qid:
                wikidata_ids_in_links.append(qid)
            else:
                errors.append({
                    "issue_type": "INVALID_URL",
                    "field": f"links[{i}].url",
                    "current_value": url,
                    "suggested_action": "Could not extract Q-number from Wikidata URL"
                })

        if check_http:
            is_valid, error_msg, _ = validate_url(url)
            if not is_valid:
                errors.append({
                    "issue_type": "INVALID_URL",
                    "field": f"links[{i}].url",
                    "current_value": url,
                    "suggested_action": f"URL check failed: {error_msg}"
                })
            time.sleep(REQUEST_DELAY)

    wikidata_id = record.get("wikidata_id")
    if wikidata_id:
        if not re.match(r"^Q\d+$", str(wikidata_id)):
            errors.append({
                "issue_type": "INVALID_ID",
                "field": "wikidata_id",
                "current_value": str(wikidata_id),
                "suggested_action": "wikidata_id has invalid format (must be Q followed by digits)"
            })
        else:
            if wikidata_ids_in_links and wikidata_id not in wikidata_ids_in_links:
                errors.append({
                    "issue_type": "INVALID_ID",
                    "field": "wikidata_id",
                    "current_value": str(wikidata_id),
                    "suggested_action": f"wikidata_id does not match any wikidata link Q-numbers: {wikidata_ids_in_links}"
                })

            if check_wikidata and entity_name:
                is_valid, error_msg = validate_wikidata_entity(wikidata_id, entity_name)
                if not is_valid:
                    errors.append({
                        "issue_type": "INVALID_ID",
                        "field": "wikidata_id",
                        "current_value": str(wikidata_id),
                        "suggested_action": f"Wikidata validation failed: {error_msg}"
                    })
                time.sleep(REQUEST_DELAY)

    if wikidata_ids_in_links and not wikidata_id:
        errors.append({
            "issue_type": "INVALID_ID",
            "field": "wikidata_id",
            "current_value": None,
            "suggested_action": f"Record has wikidata link(s) but missing wikidata_id field. Found: {wikidata_ids_in_links}"
        })

    return errors


def validate_partof_refs(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    errors = []
    known_ids = {str(rec.get("id", "")) for rec in records if rec.get("id")}
    for path, rec in zip(rel_paths, records):
        record_id = rec.get("id", "unknown")
        partof = rec.get("partof")
        if partof is None:
            continue
        if isinstance(partof, str):
            refs = [partof]
        elif isinstance(partof, dict):
            refs = [str(partof.get("id", ""))]
        elif isinstance(partof, list):
            refs = [str(p.get("id", "")) if isinstance(p, dict) else str(p) for p in partof]
        else:
            continue
        for ref in refs:
            if ref and ref not in known_ids:
                errors.append({
                    "issue_type": "UNRESOLVED_PARTOF_REF",
                    "field": "partof",
                    "current_value": ref,
                    "suggested_action": f"partof reference '{ref}' does not match any known intblock id",
                    "file_path": path,
                    "record_id": record_id
                })
    return errors


def validate_aliases(
    aliases: list[dict[str, Any]],
    known_ids: set[str],
) -> list[dict[str, Any]]:
    errors = []
    seen_aliases = set()
    for entry in aliases:
        if not isinstance(entry, dict):
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": str(entry),
                "suggested_action": "Alias entry must be a dictionary"
            })
            continue
        alias = str(entry.get("alias") or "")
        target = str(entry.get("target") or "")
        reason = str(entry.get("reason") or "")
        if not alias or not target:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": f"alias={alias}, target={target}",
                "suggested_action": "Alias entry must contain non-empty alias and target fields"
            })
            continue
        if alias in seen_aliases:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": alias,
                "suggested_action": f"Duplicate alias entry for '{alias}'"
            })
        seen_aliases.add(alias)
        if reason not in {"renamed", "merged", "disambiguated"}:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": reason,
                "suggested_action": f"Alias '{alias}': invalid reason '{reason}' (must be renamed, merged, or disambiguated)"
            })
        if target not in known_ids:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": target,
                "suggested_action": f"Alias '{alias}' target '{target}' does not match any existing intblock id"
            })
        if alias in known_ids and reason != "disambiguated":
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": alias,
                "suggested_action": f"Alias '{alias}' collides with a current intblock id; mark reason 'disambiguated'"
            })
    return errors


def validate_intblock_refs(
    countries_dir: Path,
    intblocks_records: list[dict[str, Any]],
    intblocks_paths: list[str],
    completeness_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    errors = []
    allowlist = set(completeness_cfg.get("special_entity_allowlist") or [])
    mode = (completeness_cfg.get("unresolved_country_includes") or {}).get("mode", "warn")
    issue_type = "UNRESOLVED_COUNTRY_INCLUDE"

    for path, data in zip(intblocks_paths, intblocks_records):
        record_id = data.get("id", "unknown")
        for inc in data.get("includes") or []:
            if not isinstance(inc, dict) or inc.get("type") != "country":
                continue
            raw_id = inc.get("id", "")
            if isinstance(raw_id, bool):
                continue
            cid = str(raw_id).strip()
            if not re.match(r"^[A-Z]{2}$", cid):
                continue
            country_file = countries_dir / f"{cid}.yaml"
            if country_file.exists() or cid in allowlist:
                continue

            errors.append({
                "issue_type": issue_type,
                "field": "includes",
                "current_value": cid,
                "suggested_action": f"Country include '{cid}' does not match any valid country file",
                "file_path": path,
                "record_id": record_id
            })
    return errors


# Report Writers
def generate_full_report(issues: list[dict[str, Any]], records_with_issues: dict[str, Any], total_records: int, output_path: Path) -> None:
    report_lines = []
    report_lines.append("DATA QUALITY ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Records Analyzed: {total_records}")
    report_lines.append(f"Total Issues Found: {len(issues)}")
    report_lines.append(f"Records with Issues: {len(records_with_issues)}")
    report_lines.append("")
    
    issues_by_type = {}
    for issue in issues:
        issue_type = issue["issue_type"]
        issues_by_type.setdefault(issue_type, []).append(issue)
    
    report_lines.append("=== ISSUES BY TYPE ===")
    report_lines.append("")
    
    for issue_type in sorted(issues_by_type.keys()):
        issues_list = issues_by_type[issue_type]
        report_lines.append(f"[{issue_type}]")
        report_lines.append(f"Count: {len(issues_list)}")
        report_lines.append(f"Priority: {issues_list[0].get('priority', 'MEDIUM')}")
        report_lines.append("")
        
        for issue in issues_list[:50]:
            report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
            report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
            report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Issue: {issue_type}")
            report_lines.append(f"Field: {issue.get('field', 'unknown')}")
            report_lines.append(f"Current Value: {issue.get('current_value')}")
            report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
            report_lines.append("")
        
        if len(issues_list) > 50:
            n = len(issues_list) - 50
            report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
            report_lines.append("")
            
    report_lines.append("")
    report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
    report_lines.append("")
    for issue_type in sorted(issues_by_type.keys()):
        count = len(issues_by_type[issue_type])
        priority = issues_by_type[issue_type][0].get("priority", "MEDIUM") if issues_by_type[issue_type] else "MEDIUM"
        report_lines.append(f"{issue_type} ({priority}): {count} issue" + ("s" if count != 1 else ""))
        
    report_lines.append("")
    report_lines.append("=== SUMMARY BY PRIORITY ===")
    report_lines.append("")
    issues_by_priority = {}
    for issue in issues:
        priority = issue.get("priority", "MEDIUM")
        issues_by_priority.setdefault(priority, []).append(issue)
        
    for priority in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        if priority in issues_by_priority:
            count = len(issues_by_priority[priority])
            report_lines.append(f"{priority}: {count} issue" + ("s" if count != 1 else ""))
            
    report_lines.append("")
    report_lines.append("=== RECORDS WITH MULTIPLE ISSUES (3+) ===")
    report_lines.append("")
    
    multi_issue_records = {
        rid: data for rid, data in records_with_issues.items() if len(data["issues"]) >= 3
    }
    
    if multi_issue_records:
        for record_id, data in sorted(multi_issue_records.items(), key=lambda x: len(x[1]["issues"]), reverse=True)[:100]:
            report_lines.append(f"Record ID: {record_id}")
            report_lines.append(f"File: {data.get('file_path', 'unknown')}")
            report_lines.append(f"Country: {data.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Issue Count: {len(data['issues'])}")
            report_lines.append("Issues:")
            for issue in data["issues"]:
                report_lines.append(f"  - {issue['issue_type']} ({issue.get('priority', 'MEDIUM')}): {issue['field']}")
            report_lines.append("")
    else:
        report_lines.append("No records found with 3+ issues")
        
    output_path.write_text("\n".join(report_lines), encoding="utf-8")


def generate_country_reports(issues_by_country: dict[str, list[dict[str, Any]]], records_by_country: dict[str, dict[str, Any]], output_dir: Path) -> None:
    countries_dir = output_dir / "countries"
    countries_dir.mkdir(parents=True, exist_ok=True)
    
    countries_with_issues = {c for c, issues in issues_by_country.items() if issues}
    if countries_dir.exists():
        for f in countries_dir.iterdir():
            if f.is_file() and f.name.endswith(".txt"):
                country_code = f.name[:-4]
                if country_code not in countries_with_issues:
                    f.unlink()

    for country_code, country_issues in issues_by_country.items():
        if not country_issues:
            continue
            
        country_records = records_by_country.get(country_code, {})
        report_lines = []
        report_lines.append(f"DATA QUALITY REPORT - COUNTRY: {country_code}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Country Code: {country_code}")
        report_lines.append(f"Total Records with Issues: {len(country_records)}")
        report_lines.append(f"Total Issues Found: {len(country_issues)}")
        report_lines.append("")
        
        issues_by_type = {}
        for issue in country_issues:
            issue_type = issue["issue_type"]
            issues_by_type.setdefault(issue_type, []).append(issue)
            
        report_lines.append("=== ISSUES BY TYPE ===")
        report_lines.append("")
        
        for issue_type in sorted(issues_by_type.keys()):
            issues_list = issues_by_type[issue_type]
            report_lines.append(f"[{issue_type}]")
            report_lines.append(f"Count: {len(issues_list)}")
            report_lines.append(f"Priority: {issues_list[0].get('priority', 'MEDIUM')}")
            report_lines.append("")
            
            for issue in issues_list[:100]:
                report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
                report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
                report_lines.append(f"Issue: {issue_type}")
                report_lines.append(f"Field: {issue.get('field', 'unknown')}")
                report_lines.append(f"Current Value: {issue.get('current_value')}")
                report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
                report_lines.append("")
                
            if len(issues_list) > 100:
                n = len(issues_list) - 100
                report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
                report_lines.append("")
                
        report_lines.append("")
        report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
        report_lines.append("")
        for issue_type in sorted(issues_by_type.keys()):
            count = len(issues_by_type[issue_type])
            report_lines.append(f"{issue_type}: {count} issue" + ("s" if count != 1 else ""))
            
        multi_issue_records = {
            rid: data for rid, data in country_records.items() if len(data["issues"]) >= 3
        }
        
        if multi_issue_records:
            report_lines.append("")
            report_lines.append("=== RECORDS WITH MULTIPLE ISSUES (3+) ===")
            report_lines.append("")
            for record_id, data in sorted(multi_issue_records.items(), key=lambda x: len(x[1]["issues"]), reverse=True)[:50]:
                report_lines.append(f"Record ID: {record_id}")
                report_lines.append(f"File: {data.get('file_path', 'unknown')}")
                report_lines.append(f"Issue Count: {len(data['issues'])}")
                report_lines.append("Issues:")
                for issue in data["issues"]:
                    report_lines.append(f"  - {issue['issue_type']}: {issue['field']}")
                report_lines.append("")
                
        country_file = countries_dir / f"{country_code}.txt"
        country_file.write_text("\n".join(report_lines), encoding="utf-8")


def generate_priority_reports(issues_by_priority: dict[str, list[dict[str, Any]]], output_dir: Path) -> None:
    priorities_dir = output_dir / "priorities"
    priorities_dir.mkdir(parents=True, exist_ok=True)
    
    for priority in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        priority_issues = issues_by_priority.get(priority, [])
        report_lines = []
        if not priority_issues:
            report_lines.append(f"DATA QUALITY REPORT - PRIORITY: {priority}")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Priority Level: {priority}")
            report_lines.append("Total Issues Found: 0")
            report_lines.append("")
            report_lines.append("No issues at this priority level.")
            priority_file = priorities_dir / f"{priority}.txt"
            priority_file.write_text("\n".join(report_lines), encoding="utf-8")
            continue
            
        report_lines.append(f"DATA QUALITY REPORT - PRIORITY: {priority}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Priority Level: {priority}")
        report_lines.append(f"Total Issues Found: {len(priority_issues)}")
        report_lines.append("")
        
        issues_by_type = {}
        for issue in priority_issues:
            issue_type = issue["issue_type"]
            issues_by_type.setdefault(issue_type, []).append(issue)
            
        report_lines.append("=== ISSUES BY TYPE ===")
        report_lines.append("")
        
        for issue_type in sorted(issues_by_type.keys()):
            issues_list = issues_by_type[issue_type]
            report_lines.append(f"[{issue_type}]")
            report_lines.append(f"Count: {len(issues_list)}")
            report_lines.append("")
            
            for issue in issues_list[:100]:
                report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
                report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
                report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
                report_lines.append(f"Issue: {issue_type}")
                report_lines.append(f"Field: {issue.get('field', 'unknown')}")
                report_lines.append(f"Current Value: {issue.get('current_value')}")
                report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
                report_lines.append("")
                
            if len(issues_list) > 100:
                n = len(issues_list) - 100
                report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
                report_lines.append("")
                
        report_lines.append("")
        report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
        report_lines.append("")
        for issue_type in sorted(issues_by_type.keys()):
            count = len(issues_by_type[issue_type])
            report_lines.append(f"{issue_type}: {count} issue" + ("s" if count != 1 else ""))
            
        report_lines.append("")
        report_lines.append("=== SUMMARY BY COUNTRY ===")
        report_lines.append("")
        issues_by_country = {}
        for issue in priority_issues:
            country_code = issue.get("country_code", "UNKNOWN")
            issues_by_country.setdefault(country_code, []).append(issue)
            
        for country_code in sorted(issues_by_country.keys()):
            count = len(issues_by_country[country_code])
            report_lines.append(f"{country_code}: {count} issue" + ("s" if count != 1 else ""))
            
        priority_file = priorities_dir / f"{priority}.txt"
        priority_file.write_text("\n".join(report_lines), encoding="utf-8")


def generate_rule_reports(issues_by_type: dict[str, list[dict[str, Any]]], output_dir: Path) -> None:
    rules_dir = output_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    known_issue_types = []
    for issue_types in ISSUE_PRIORITY_MAP.values():
        known_issue_types.extend(issue_types)
        
    for issue_type in known_issue_types:
        if not issues_by_type.get(issue_type):
            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", issue_type)
            rule_file = rules_dir / f"{safe_name}.txt"
            if rule_file.exists():
                rule_file.unlink()

    for issue_type, issues_list in issues_by_type.items():
        if not issues_list:
            continue
            
        priority = issues_list[0].get("priority", "MEDIUM")
        report_lines = []
        report_lines.append(f"DATA QUALITY REPORT - RULE: {issue_type}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Issue Type: {issue_type}")
        report_lines.append(f"Priority: {priority}")
        report_lines.append(f"Total Issues Found: {len(issues_list)}")
        
        rule_desc = RULE_DESCRIPTIONS.get(issue_type)
        if rule_desc:
            report_lines.append("")
            report_lines.append(f"Description: {rule_desc}")
            
        report_lines.append("")
        report_lines.append("=== AFFECTED RECORDS ===")
        report_lines.append("")
        
        for issue in issues_list[:100]:
            report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
            report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
            report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Field: {issue.get('field', 'unknown')}")
            report_lines.append(f"Current Value: {issue.get('current_value')}")
            report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
            report_lines.append("")
            
        if len(issues_list) > 100:
            n = len(issues_list) - 100
            report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
            report_lines.append("")
            
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", issue_type)
        rule_file = rules_dir / f"{safe_name}.txt"
        rule_file.write_text("\n".join(report_lines), encoding="utf-8")


@app.command()
def analyze_quality(
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for quality reports (default: dataquality)",
    ),
    check_http: bool = typer.Option(
        False,
        "--check-http",
        help="Enable HTTP accessibility checking for links (slow)",
    ),
    check_wikidata: bool = typer.Option(
        False,
        "--check-wikidata",
        help="Enable Wikidata API validation for wikidata_id (slow)",
    ),
) -> None:
    """
    Analyze countries and intblocks records for missing values and data quality issues,
    generating organized reports.
    """
    project_root = get_project_root()
    countries_dir = project_root / "data" / "countries"
    intblocks_dir = project_root / "data" / "intblocks"
    
    if not countries_dir.exists():
        typer.echo(f"Error: Countries directory not found at {countries_dir}", err=True)
        raise typer.Exit(1)
        
    if not intblocks_dir.exists():
        typer.echo(f"Error: Intblocks directory not found at {intblocks_dir}", err=True)
        raise typer.Exit(1)

    if output is None:
        output_dir = project_root / "dataquality"
    else:
        output_dir = output

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "countries").mkdir(exist_ok=True)
    (output_dir / "priorities").mkdir(exist_ok=True)
    (output_dir / "rules").mkdir(exist_ok=True)

    typer.echo("🔍 Scanning data sources...")
    typer.echo(f"  Countries: {countries_dir}")
    typer.echo(f"  Intblocks: {intblocks_dir}")
    typer.echo(f"  Output: {output_dir}")

    schema_path_countries = project_root / "data" / "schemas" / "countries.schema.json"
    completeness_path_countries = project_root / "data" / "schemas" / "countries_completeness.yaml"
    schema_path_intblocks = project_root / "data" / "schemas" / "intblocks.schema.json"
    completeness_path_intblocks = project_root / "data" / "schemas" / "intblocks_completeness.yaml"
    blocktypes_path = blocktypes_source_path(project_root)
    aliases_path = project_root / "data" / "intblocks_aliases.yaml"

    try:
        schema_countries = json.loads(schema_path_countries.read_text(encoding="utf-8"))
        completeness_cfg_countries = yaml.safe_load(completeness_path_countries.read_text(encoding="utf-8")) or {}
    except Exception as e:
        typer.echo(f"Error loading country schema/config: {e}", err=True)
        raise typer.Exit(1)

    try:
        schema_intblocks = json.loads(schema_path_intblocks.read_text(encoding="utf-8"))
        completeness_cfg_intblocks = yaml.safe_load(completeness_path_intblocks.read_text(encoding="utf-8")) or {}
    except Exception as e:
        typer.echo(f"Error loading intblock schema/config: {e}", err=True)
        raise typer.Exit(1)

    taxonomy = set()
    if blocktypes_path.exists():
        try:
            bt_data = yaml.safe_load(blocktypes_path.read_text(encoding="utf-8")) or []
            taxonomy = {str(b.get("id", "")) for b in bt_data if isinstance(b, dict)}
        except Exception as e:
            typer.echo(f"Warning: could not load blocktypes taxonomy: {e}", err=True)

    aliases = []
    if aliases_path.exists():
        try:
            aliases = yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or []
        except Exception as e:
            typer.echo(f"Warning: could not load aliases: {e}", err=True)

    country_files = sorted(countries_dir.glob("*.yaml"))
    country_records = []
    country_rel_paths = []
    all_issues = []
    records_with_issues = {}
    total_records = 0

    for path in country_files:
        total_records += 1
        rel_path = str(path.relative_to(project_root))
        try:
            with open(path, encoding="utf-8") as f:
                record = yaml.safe_load(f)
            if not record:
                continue
            country_records.append(record)
            country_rel_paths.append(rel_path)
            
            record_id = record.get("code", "unknown")
            record_issues = []
            
            record_issues.extend(check_country_schema(record, schema_countries))
            record_issues.extend(check_country_borders(record))
            record_issues.extend(check_country_indicator_years(record))
            record_issues.extend(check_country_whitespace(record))
            record_issues.extend(check_country_entity_status(record))
            
            for issue in record_issues:
                issue["file_path"] = rel_path
                issue["record_id"] = record_id
                issue["priority"] = get_priority_level(issue["issue_type"])
                
            all_issues.extend(record_issues)
            if record_issues:
                records_with_issues[record_id] = {
                    "file_path": rel_path,
                    "issues": record_issues,
                }
        except Exception as e:
            all_issues.append({
                "issue_type": "SCHEMA_ERROR",
                "field": "(root)",
                "current_value": str(e),
                "suggested_action": f"YAML parse error: {e}",
                "file_path": rel_path,
                "record_id": path.stem,
                "priority": "CRITICAL"
            })
            records_with_issues[path.stem] = {
                "file_path": rel_path,
                "issues": [all_issues[-1]]
            }

    intblock_files = sorted(intblocks_dir.rglob("*.yaml"))
    intblock_records = []
    intblock_rel_paths = []

    for path in intblock_files:
        total_records += 1
        rel_path = str(path.relative_to(project_root))
        try:
            with open(path, encoding="utf-8") as f:
                record = yaml.safe_load(f)
            if not record:
                continue
            intblock_records.append(record)
            intblock_rel_paths.append(rel_path)
            
            record_id = record.get("id", "unknown")
            record_issues = []
            
            record_issues.extend(check_intblock_schema(record, schema_intblocks))
            record_issues.extend(check_intblock_blocktypes(record, taxonomy))
            record_issues.extend(check_intblock_lifecycle(record))
            record_issues.extend(check_intblock_description_quality(record))
            record_issues.extend(check_intblock_links(record, check_http, check_wikidata))
            
            for issue in record_issues:
                issue["file_path"] = rel_path
                issue["record_id"] = record_id
                issue["priority"] = get_priority_level(issue["issue_type"])
                
            all_issues.extend(record_issues)
            if record_issues:
                records_with_issues[record_id] = {
                    "file_path": rel_path,
                    "issues": record_issues,
                }
        except Exception as e:
            all_issues.append({
                "issue_type": "SCHEMA_ERROR",
                "field": "(root)",
                "current_value": str(e),
                "suggested_action": f"YAML parse error: {e}",
                "file_path": rel_path,
                "record_id": path.stem,
                "priority": "CRITICAL"
            })
            records_with_issues[path.stem] = {
                "file_path": rel_path,
                "issues": [all_issues[-1]]
            }

    cross_issues = []
    cross_issues.extend(check_country_duplicates(country_records, country_rel_paths))
    cross_issues.extend(validate_official_iso_count(country_records))
    cross_issues.extend(validate_completeness(country_records, completeness_cfg_countries))
    
    cross_issues.extend(check_intblock_duplicates(intblock_records, intblock_rel_paths))
    cross_issues.extend(validate_partof_refs(intblock_records, intblock_rel_paths))
    cross_issues.extend(validate_aliases(aliases, {str(r.get("id", "")) for r in intblock_records if r.get("id")}))
    cross_issues.extend(validate_completeness(intblock_records, completeness_cfg_intblocks))
    cross_issues.extend(validate_intblock_refs(countries_dir, intblock_records, intblock_rel_paths, completeness_cfg_countries))

    link_to_records = {}
    for path, rec in zip(country_rel_paths + intblock_rel_paths, country_records + intblock_records):
        rid = rec.get("code") or rec.get("id") or "unknown"
        urls = []
        tld = rec.get("tld")
        if tld:
            urls.append(f"http://{tld}")
        for link in rec.get("links") or []:
            if isinstance(link, dict) and link.get("url"):
                urls.append(link["url"])
        for u in urls:
            link_to_records.setdefault(u, []).append((path, rid))
            
    for url, metas in link_to_records.items():
        if url and len(metas) > 1:
            for path, rid in metas:
                cross_issues.append({
                    "issue_type": "DUPLICATE_LINK",
                    "field": "links",
                    "current_value": url,
                    "suggested_action": f"Duplicate link '{url}' found in multiple records: {metas}",
                    "file_path": path,
                    "record_id": rid
                })

    for issue in cross_issues:
        issue.setdefault("file_path", "cross-record")
        issue.setdefault("record_id", "cross-record")
        issue["priority"] = get_priority_level(issue["issue_type"])
        
    all_issues.extend(cross_issues)

    for issue in all_issues:
        rec_id = issue.get("record_id", "unknown")
        dataset_type = "countries" if issue["file_path"].startswith("data/countries") else "intblocks"
        if issue["file_path"] == "cross-record":
            issue["country_code"] = "UNKNOWN"
            continue
            
        record_found = None
        if dataset_type == "countries":
            for r in country_records:
                if r.get("code") == rec_id:
                    record_found = r
                    break
        else:
            for r in intblock_records:
                if r.get("id") == rec_id:
                    record_found = r
                    break
                    
        if record_found:
            codes = extract_country_codes(record_found, dataset_type)
            issue["country_code"] = codes[0] if codes else "UNKNOWN"
            issue["all_country_codes"] = codes
        else:
            issue["country_code"] = "UNKNOWN"
            issue["all_country_codes"] = ["UNKNOWN"]

    records_with_issues = {}
    for issue in all_issues:
        path = issue.get("file_path", "unknown")
        rid = issue.get("record_id", "unknown")
        if path == "cross-record" or rid == "cross-record":
            continue
        if rid not in records_with_issues:
            records_with_issues[rid] = {
                "file_path": path,
                "country_code": issue.get("country_code", "UNKNOWN"),
                "all_country_codes": issue.get("all_country_codes", ["UNKNOWN"]),
                "issues": []
            }
        records_with_issues[rid]["issues"].append(issue)

    issues_by_country = {}
    records_by_country = {}
    for rid, data in records_with_issues.items():
        for code in data.get("all_country_codes", ["UNKNOWN"]):
            issues_by_country.setdefault(code, [])
            records_by_country.setdefault(code, {})
            
            c_issues = [iss for iss in data["issues"] if iss.get("country_code") == code or code in iss.get("all_country_codes", [])]
            issues_by_country[code].extend(c_issues)
            records_by_country[code][rid] = {
                "file_path": data["file_path"],
                "issues": c_issues,
            }

    issues_by_priority = {}
    for issue in all_issues:
        priority = issue.get("priority", "MEDIUM")
        issues_by_priority.setdefault(priority, []).append(issue)

    issues_by_type = {}
    for issue in all_issues:
        issue_type = issue["issue_type"]
        issues_by_type.setdefault(issue_type, []).append(issue)

    generate_full_report(all_issues, records_with_issues, total_records, output_dir / "full_report.txt")
    
    full_jsonl = output_dir / "full_report.jsonl"
    with open(full_jsonl, "w", encoding="utf-8") as f:
        for issue in all_issues:
            clean_issue = {
                "issue_type": issue.get("issue_type"),
                "field": issue.get("field"),
                "current_value": issue.get("current_value"),
                "suggested_action": issue.get("suggested_action"),
                "file_path": issue.get("file_path"),
                "record_id": issue.get("record_id"),
                "priority": issue.get("priority"),
                "country_code": issue.get("country_code"),
            }
            f.write(json.dumps(clean_issue, ensure_ascii=False) + "\n")

    primary_jsonl = output_dir / "primary_priority.jsonl"
    filtered_records = [
        (rid, data) for rid, data in records_with_issues.items() if len(data["issues"]) >= 3
    ]
    sorted_records = sorted(
        filtered_records,
        key=lambda x: (
            len(x[1]["issues"]),
            sum(1 for iss in x[1]["issues"] if iss.get("priority") == "CRITICAL"),
            sum(1 for iss in x[1]["issues"] if iss.get("priority") == "IMPORTANT"),
        ),
        reverse=True
    )
    with open(primary_jsonl, "w", encoding="utf-8") as f:
        for rid, data in sorted_records:
            priority_counts = {}
            for iss in data["issues"]:
                p = iss.get("priority", "MEDIUM")
                priority_counts[p] = priority_counts.get(p, 0) + 1
            clean_rec = {
                "record_id": rid,
                "file_path": data["file_path"],
                "country_code": data.get("country_code", "UNKNOWN"),
                "all_country_codes": data.get("all_country_codes", []),
                "total_issues": len(data["issues"]),
                "priority_counts": priority_counts,
                "issues": [
                    {
                        "issue_type": iss.get("issue_type"),
                        "field": iss.get("field"),
                        "priority": iss.get("priority"),
                        "current_value": iss.get("current_value"),
                        "suggested_action": iss.get("suggested_action"),
                    }
                    for iss in data["issues"]
                ]
            }
            f.write(json.dumps(clean_rec, ensure_ascii=False) + "\n")

    generate_country_reports(issues_by_country, records_by_country, output_dir)
    generate_priority_reports(issues_by_priority, output_dir)
    generate_rule_reports(issues_by_type, output_dir)

    typer.echo(f"\n✅ Quality analysis completed!")
    typer.echo(f"  Total records analyzed: {total_records}")
    typer.echo(f"  Total issues found: {len(all_issues)}")
    typer.echo(f"  Records with issues: {len(records_with_issues)}")
    typer.echo(f"  Reports saved in: {output_dir}")
    
    typer.echo("\nPriority breakdown:")
    for p in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        cnt = len(issues_by_priority.get(p, []))
        typer.echo(f"  {p}: {cnt}")


if __name__ == "__main__":
    app()
