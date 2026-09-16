"""Multi-format dataset writers: JSONL/YAML (zstd), Parquet, CSV, DuckDB."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import typer
import yaml
import zstandard as zstd
from tqdm import tqdm

from internacia_builder.manifest import (
    dataset_metadata,
)
from internacia_builder.paths import project_root
from internacia_builder.schemas import (
    get_aliases_schema,
    get_attribute_migration_schema,
    get_memberships_schema,
    get_meta_schema,
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

def load_country_aliases(project_root: Path) -> list[dict[str, Any]]:
    """Load country code alias source (retired/renamed codes → current code)."""
    path = project_root / "data" / "countries_aliases.yaml"
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

def load_attribute_intblock_migrations(project_root: Path) -> list[dict[str, Any]]:
    """Load retired attribute-partition intblock → country field mappings."""
    path = project_root / "data" / "attribute_intblock_migrations.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []
    rows: list[dict[str, Any]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        value = entry.get("country_value")
        rows.append(
            {
                "retired_id": str(entry.get("retired_id") or ""),
                "country_field": str(entry.get("country_field") or ""),
                "country_value": "" if value is None else str(value),
                "country_value_id": str(entry.get("country_value_id") or ""),
                "disposition": str(entry.get("disposition") or ""),
                "vocab": str(entry.get("vocab") or ""),
                "vocab_id": str(entry.get("vocab_id") or ""),
                "since": str(entry.get("since") or ""),
                "note": str(entry.get("note") or ""),
            }
        )
    return rows

def save_attribute_intblock_migrations(
    migrations: list[dict[str, Any]],
    output_dir: Path,
    *,
    write_parquet: bool = True,
) -> None:
    """Write attribute migration artifact as JSON and optional Parquet."""
    json_path = output_dir / "attribute_intblock_migrations.json"
    # Prefer source-shaped JSON (richer types) when available at data/
    source = project_root() / "data" / "attribute_intblock_migrations.yaml"
    if source.exists():
        with open(source, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or []
        json_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        json_path.write_text(json.dumps(migrations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved attribute migrations: {json_path}")
    if write_parquet:
        table = pa.Table.from_pylist(migrations, schema=get_attribute_migration_schema())
        parquet_path = output_dir / "attribute_intblock_migrations.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=22)
        typer.echo(f"✓ Saved attribute migrations (parquet): {parquet_path}")

def save_aliases(
    aliases: list[dict[str, Any]],
    output_dir: Path,
    basename: str = "intblocks_aliases",
    write_parquet: bool = True,
) -> None:
    """Write an alias artifact as JSON and (optionally) Parquet."""
    json_path = output_dir / f"{basename}.json"
    json_path.write_text(json.dumps(aliases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved alias map: {json_path}")
    if write_parquet:
        table = pa.Table.from_pylist(aliases, schema=get_aliases_schema())
        parquet_path = output_dir / f"{basename}.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=22)
        typer.echo(f"✓ Saved alias map (parquet): {parquet_path}")

def _join_list(values: list[Any] | None, sep: str = ";") -> str:
    if not values:
        return ""
    return sep.join(str(v) for v in values)

def _indicator_cols(prefix: str, indicator: dict[str, Any] | None) -> dict[str, Any]:
    indicator = indicator or {}
    return {
        f"{prefix}_value": indicator.get("value"),
        f"{prefix}_year": indicator.get("year"),
        f"{prefix}_source": indicator.get("source") or "",
    }

def flatten_country(rec: dict[str, Any]) -> dict[str, Any]:
    """Flatten one country record to scalar CSV columns."""
    cap = rec.get("capital_city") or {}
    region = rec.get("region") or {}
    adminregion = rec.get("adminregion") or {}
    income = rec.get("incomeLevel") or {}
    lending = rec.get("lendingType") or {}
    rec_status = rec.get("recognition_status") or {}
    parent = rec.get("parent_entity") or {}
    demonyms = rec.get("demonyms") or {}
    centroid = rec.get("centroid") or {}
    row: dict[str, Any] = {
        "code": rec.get("code") or "",
        "name": rec.get("name") or "",
        "iso3code": rec.get("iso3code") or "",
        "numeric_code": rec.get("numeric_code") or "",
        "wikidata_id": rec.get("wikidata_id") or "",
        "geonames_id": rec.get("geonames_id") or "",
        "ioc_code": rec.get("ioc_code") or "",
        "fifa_code": rec.get("fifa_code") or "",
        "fips_code": rec.get("fips_code") or "",
        "official_name": rec.get("official_name") or "",
        "capital_city_name": cap.get("name") or "",
        "capital_city_lat": cap.get("lat"),
        "capital_city_lng": cap.get("lng"),
        "region_id": region.get("id") or "",
        "region_value": region.get("value") or "",
        "adminregion_id": adminregion.get("id") or "",
        "adminregion_value": adminregion.get("value") or "",
        "incomeLevel_id": income.get("id") or "",
        "incomeLevel_value": income.get("value") or "",
        "lendingType_id": lending.get("id") or "",
        "lendingType_value": lending.get("value") or "",
        "un_member": rec.get("un_member"),
        "un_status": rec.get("un_status") or "",
        "independent": rec.get("independent"),
        "entity_type": rec.get("entity_type") or "",
        "code_status": rec.get("code_status") or "",
        "recognition_status": rec_status.get("status") or "",
        "recognition_un_member": rec_status.get("un_member"),
        "recognition_notes": rec_status.get("notes") or "",
        "parent_entity_code": parent.get("code") or "",
        "parent_entity_name": parent.get("name") or "",
        "subregion": rec.get("subregion") or "",
        "continents": _join_list(rec.get("continents")),
        "borders": _join_list(rec.get("borders")),
        "landlocked": rec.get("landlocked"),
        "tld": rec.get("tld") or "",
        "flag_emoji": rec.get("flag_emoji") or "",
        "m49_code": rec.get("m49_code") or "",
        "centroid_lat": centroid.get("lat"),
        "centroid_lng": centroid.get("lng"),
        "timezones": _join_list(rec.get("timezones")),
        "demonyms_female": demonyms.get("female") or "",
        "demonyms_male": demonyms.get("male") or "",
        "common_names": _join_list(rec.get("common_names"), "|"),
    }
    row.update(_indicator_cols("population", rec.get("population")))
    row.update(_indicator_cols("area", rec.get("area")))
    row.update(_indicator_cols("gini", rec.get("gini")))
    return row

def flatten_intblock(rec: dict[str, Any]) -> dict[str, Any]:
    """Flatten one intblock record to scalar CSV columns."""
    hq = rec.get("headquarters") or {}
    coords = hq.get("coordinates") or {}
    return {
        "id": rec.get("id") or "",
        "name": rec.get("name") or "",
        "status": rec.get("status") or "",
        "wikidata_id": rec.get("wikidata_id") or "",
        "founded": rec.get("founded") or "",
        "geographic_scope": rec.get("geographic_scope") or "",
        "scope_category": rec.get("scope_category") or "",
        "legal_status": rec.get("legal_status") or "",
        "membership_count": rec.get("membership_count"),
        "membership_count_type": rec.get("membership_count_type") or "",
        "blocktype": _join_list(rec.get("blocktype")),
        "regions": _join_list(rec.get("regions")),
        "partof": _join_list(rec.get("partof")),
        "languages": _join_list(rec.get("languages")),
        "hq_city": hq.get("city") or "",
        "hq_country": hq.get("country") or "",
        "hq_lat": coords.get("lat"),
        "hq_lng": coords.get("lng"),
        "dissolved": rec.get("dissolved") or "",
        "successor": rec.get("successor") or "",
        "description": rec.get("description") or "",
    }


COUNTRIES_LITE_FIELDS = (
    "code",
    "name",
    "iso3code",
    "wikidata_id",
    "entity_type",
    "code_status",
    "un_status",
    "independent",
    "region_id",
    "subregion",
    "ioc_code",
    "fifa_code",
)

INTBLOCKS_LITE_FIELDS = (
    "id",
    "name",
    "status",
    "wikidata_id",
    "geographic_scope",
    "scope_category",
    "blocktype",
    "membership_count",
    "legal_status",
)

def project_lite_rows(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    return [{field: row.get(field) for field in fields} for row in rows]

def save_csv_rows(rows: list[dict[str, Any]], output_file: Path) -> None:
    """Save flattened rows as a Zstandard-compressed CSV file (``.csv.zst``)."""
    import csv
    import io

    buf = io.StringIO(newline="")
    if rows:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    cctx = zstd.ZstdCompressor(level=22)
    output_file.write_bytes(cctx.compress(buf.getvalue().encode("utf-8")))
    typer.echo(f"✓ Saved CSV (zstd): {output_file}")

def save_json_array(data: list[dict[str, Any]], output_file: Path) -> None:
    """Save records as a Zstandard-compressed JSON array (``.json.zst``)."""
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    cctx = zstd.ZstdCompressor(level=22)
    output_file.write_bytes(cctx.compress(payload))
    typer.echo(f"✓ Saved JSON array (zstd): {output_file}")

def write_datapackage(output_dir: Path, version: str) -> None:
    """Emit a Frictionless Data Package descriptor for published resources."""
    resources: list[dict[str, Any]] = []
    for name, fmt, path in (
        ("countries", "csv", "countries.csv.zst"),
        ("countries-lite", "csv", "countries-lite.csv.zst"),
        ("countries", "parquet", "countries.parquet"),
        ("countries-lite", "parquet", "countries-lite.parquet"),
        ("countries", "json", "countries.json.zst"),
        ("countries", "jsonl", "countries.jsonl"),
        ("intblocks", "csv", "intblocks.csv.zst"),
        ("intblocks-lite", "csv", "intblocks-lite.csv.zst"),
        ("intblocks", "parquet", "intblocks.parquet"),
        ("intblocks-lite", "parquet", "intblocks-lite.parquet"),
        ("intblocks", "json", "intblocks.json.zst"),
        ("intblocks", "jsonl", "intblocks.jsonl"),
        ("blocktypes", "parquet", "blocktypes.parquet"),
        ("memberships", "csv", "memberships.csv.zst"),
        ("memberships", "parquet", "memberships.parquet"),
        ("intblocks_aliases", "json", "intblocks_aliases.json"),
        ("countries_aliases", "json", "countries_aliases.json"),
        ("attribute_intblock_migrations", "json", "attribute_intblock_migrations.json"),
    ):
        file_path = output_dir / path
        if not file_path.exists():
            continue
        resources.append(
            {
                "name": name,
                "path": path,
                "format": fmt,
                "mediatype": {
                    "csv": "text/csv",
                    "parquet": "application/vnd.apache.parquet",
                    "json": "application/json",
                    "jsonl": "application/x-ndjson",
                }.get(fmt, "application/octet-stream"),
                "compression": "zstd" if path.endswith(".zst") else None,
            }
        )
        if resources[-1]["compression"] is None:
            del resources[-1]["compression"]
    package = {
        "name": "internacia-datasets",
        "title": "Internacia reference datasets",
        "version": version,
        "licenses": [{"name": "CC-BY-4.0", "title": "Creative Commons Attribution 4.0"}],
        "resources": resources,
    }
    out = output_dir / "datapackage.json"
    out.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved datapackage: {out}")

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

def save_jsonl(data: list[dict[str, Any]], output_file: Path):
    """Save data as plain (uncompressed) JSONL file.

    Row content is identical to the ``.jsonl.zst`` variant so consumers
    without a zstd codec can read the same data.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    typer.echo(f"✓ Saved JSONL: {output_file}")

def save_yaml_zst(data: list[dict[str, Any]], output_file: Path):
    """Save data as Zstandard-compressed YAML file."""
    cctx = zstd.ZstdCompressor(level=22)
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(output_file, "wb") as f:
        f.write(cctx.compress(yaml_str.encode("utf-8")))
    typer.echo(f"✓ Saved YAML (zstd): {output_file}")

def build_membership_rows(intblocks_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten country-coded includes entries into one membership edge per row.

    Organization-type entries are excluded: their ids reference intblocks,
    not countries. country / territory / historical-country entries all join
    against ``countries.code``.
    """
    rows: list[dict[str, Any]] = []
    for record in intblocks_data:
        for inc in record.get("includes") or []:
            if not isinstance(inc, dict) or inc.get("type") == "organization":
                continue
            rows.append(
                {
                    "intblock_id": record.get("id"),
                    "country_code": inc.get("id"),
                    "include_type": inc.get("type"),
                    "status": inc.get("status"),
                    "joined": inc.get("joined"),
                    "left": inc.get("left"),
                }
            )
    rows.sort(key=lambda r: (str(r["intblock_id"]), str(r["country_code"])))
    return rows

def save_memberships_csv(rows: list[dict[str, Any]], output_file: Path):
    """Save membership edges as a Zstandard-compressed CSV file (``.csv.zst``)."""
    import csv
    import io

    buf = io.StringIO(newline="")
    fieldnames = get_memberships_schema().names
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    cctx = zstd.ZstdCompressor(level=22)
    output_file.write_bytes(cctx.compress(buf.getvalue().encode("utf-8")))
    typer.echo(f"✓ Saved CSV (zstd): {output_file}")

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
    memberships_data: list[dict[str, Any]] | None = None,
):
    """Create DuckDB database with countries, intblocks, blocktypes, and memberships tables."""
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
        if memberships_data is not None:
            tables.append(("memberships", memberships_data, get_memberships_schema()))
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
        if "memberships" in counts:
            typer.echo(f"  - Memberships: {counts['memberships']} rows")

    finally:
        con.close()
