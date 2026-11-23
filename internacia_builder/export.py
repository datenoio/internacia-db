"""Multi-format dataset writers: JSONL/YAML (zstd), Parquet, CSV, DuckDB."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import typer
import yaml
import zstandard as zstd
from tqdm import tqdm

from internacia_builder.contract import DUCKDB_STORAGE_COMPATIBILITY, TABLES, VIEWS, file_digest
from internacia_builder.doc_counts import documented_count
from internacia_builder.manifest import (
    dataset_metadata,
)
from internacia_builder.paths import project_root
from internacia_builder.schemas import (
    get_aliases_schema,
    get_attribute_migration_schema,
    get_border_status_schema,
    get_country_aliases_schema,
    get_memberships_schema,
    get_meta_schema,
    get_trade_agreement_instruments_schema,
    get_trade_agreement_parties_schema,
    get_trade_agreements_schema,
)
from internacia_builder.yaml_io import safe_load

RELEASE_ZSTD_LEVEL = 22
ZSTD_LEVEL_ENV = "INTERNACIA_ZSTD_LEVEL"


def zstd_level() -> int:
    """The zstd level of every compressed export (``*.zst`` and Parquet): 22 unless overridden.

    Releases always use 22. At 22 compression takes nearly half of a build; ``validate.yml`` sets
    ``INTERNACIA_ZSTD_LEVEL=3`` because a pull-request build is only tested, never published.
    The level changes the compressed bytes, not the data, so every check that a release runs
    passes at either level. Set it locally for a faster ``builder.py build`` too.
    """
    raw = os.environ.get(ZSTD_LEVEL_ENV, "").strip()
    if not raw:
        return RELEASE_ZSTD_LEVEL
    try:
        level = int(raw)
    except ValueError:
        level = 0
    if not 1 <= level <= RELEASE_ZSTD_LEVEL:
        raise ValueError(f"{ZSTD_LEVEL_ENV} must be an integer from 1 to {RELEASE_ZSTD_LEVEL}, not {raw!r}")
    return level


def load_intblock_aliases(project_root: Path) -> list[dict[str, Any]]:
    """Load the intblock identifier alias source (retired/renamed ids → current id)."""
    path = project_root / "data" / "intblocks_aliases.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = safe_load(f) or []
    aliases: list[dict[str, Any]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        aliases.append(
            {
                "alias": str(entry.get("alias") or ""),
                "target": str(entry["target"]) if entry.get("target") else None,
                "reason": str(entry.get("reason") or ""),
                "since": str(entry.get("since") or ""),
                "note": str(entry.get("note") or ""),
                "target_dataset": (
                    None if not entry.get("target") else str(entry.get("target_dataset") or "intblocks")
                ),
            }
        )
    return aliases

def load_country_aliases(project_root: Path) -> list[dict[str, Any]]:
    """Load country code alias source (retired/renamed codes → current code)."""
    path = project_root / "data" / "countries_aliases.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = safe_load(f) or []
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
        raw = safe_load(f) or []
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
            raw = safe_load(f) or []
        json_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        json_path.write_text(json.dumps(migrations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved attribute migrations: {json_path}")
    if write_parquet:
        table = pa.Table.from_pylist(migrations, schema=get_attribute_migration_schema())
        parquet_path = output_dir / "attribute_intblock_migrations.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=zstd_level())
        typer.echo(f"✓ Saved attribute migrations (parquet): {parquet_path}")

def load_border_status(project_root: Path) -> list[dict[str, Any]]:
    """Border status rows from data/borders/border_status.yaml, sorted by pair and start."""
    path = project_root / "data" / "borders" / "border_status.yaml"
    if not path.exists():
        return []
    document = safe_load(path.read_text(encoding="utf-8")) or {}
    rows: list[dict[str, Any]] = []
    for entry in document.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        pair = [str(code) for code in entry.get("countries") or []]
        rows.append(
            {
                "country_a": pair[0] if pair else None,
                "country_b": pair[1] if len(pair) > 1 else None,
                "status": entry.get("status"),
                "since": None if entry.get("since") is None else str(entry["since"]),
                "until": None if entry.get("until") is None else str(entry["until"]),
                "note": entry.get("note"),
                "last_verified": None if entry.get("last_verified") is None else str(entry["last_verified"]),
                "provenance": [
                    {
                        "source": p.get("source"),
                        "url": p.get("url"),
                        "retrieved_at": None if p.get("retrieved_at") is None else str(p["retrieved_at"]),
                        "license": p.get("license"),
                    }
                    for p in entry.get("provenance") or []
                    if isinstance(p, dict)
                ],
            }
        )
    rows.sort(key=lambda r: (str(r["country_a"]), str(r["country_b"]), str(r["since"] or "")))
    return rows

def save_border_status(rows: list[dict[str, Any]], output_dir: Path, write_parquet: bool = True) -> None:
    """Write the border status artifact as JSON and (optionally) Parquet."""
    json_path = output_dir / "border_status.json"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.echo(f"✓ Saved border status: {json_path}")
    if write_parquet:
        table = pa.Table.from_pylist(rows, schema=get_border_status_schema())
        parquet_path = output_dir / "border_status.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=zstd_level())
        typer.echo(f"✓ Saved border status (parquet): {parquet_path}")

def save_trade_agreements(
    agreements: list[dict[str, Any]],
    parties: list[dict[str, Any]],
    output_dir: Path,
    *,
    instruments: list[dict[str, Any]] | None = None,
    write_jsonl: bool = True,
    write_parquet: bool = True,
) -> None:
    """Write the trade agreements registry tables as JSONL and (optionally) Parquet."""
    for name, rows, schema in (
        ("trade_agreements", agreements, get_trade_agreements_schema()),
        ("trade_agreement_parties", parties, get_trade_agreement_parties_schema()),
        ("trade_agreement_instruments", instruments or [], get_trade_agreement_instruments_schema()),
    ):
        if write_jsonl:
            save_jsonl(rows, output_dir / f"{name}.jsonl")
        if write_parquet:
            table = pa.Table.from_pylist(rows, schema=schema)
            parquet_path = output_dir / f"{name}.parquet"
            pq.write_table(table, parquet_path, compression="zstd", compression_level=zstd_level())
            typer.echo(f"✓ Saved {name} (parquet): {parquet_path}")


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
        schema = get_country_aliases_schema() if basename == "countries_aliases" else get_aliases_schema()
        table = pa.Table.from_pylist(aliases, schema=schema)
        parquet_path = output_dir / f"{basename}.parquet"
        pq.write_table(table, parquet_path, compression="zstd", compression_level=zstd_level())
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
    design = rec.get("institutional_design") or {}
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
        "design_mandate": design.get("mandate") or "",
        "design_decision_rule": design.get("decision_rule") or "",
        "design_decision_force": design.get("decision_force") or "",
        "design_independent_organs": _join_list(design.get("independent_organs")),
        "design_enforcement": _join_list(design.get("enforcement")),
        "design_mutual_defence": design.get("mutual_defence"),
        "design_veto_holders": _join_list(design.get("veto_holders")),
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
    cctx = zstd.ZstdCompressor(level=zstd_level())
    output_file.write_bytes(cctx.compress(buf.getvalue().encode("utf-8")))
    typer.echo(f"✓ Saved CSV (zstd): {output_file}")

def save_json_array(data: list[dict[str, Any]], output_file: Path) -> None:
    """Save records as a Zstandard-compressed JSON array (``.json.zst``)."""
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    cctx = zstd.ZstdCompressor(level=zstd_level())
    output_file.write_bytes(cctx.compress(payload))
    typer.echo(f"✓ Saved JSON array (zstd): {output_file}")

def _table_schema_type(data_type: pa.DataType) -> str:
    if pa.types.is_string(data_type):
        return "string"
    if pa.types.is_boolean(data_type):
        return "boolean"
    if pa.types.is_integer(data_type):
        return "integer"
    if pa.types.is_floating(data_type):
        return "number"
    if pa.types.is_list(data_type):
        return "array"
    return "object"


def _parquet_table_schema(path: Path, table: str) -> dict[str, Any]:
    """Frictionless Table Schema for a Parquet resource, read from the written file."""
    fields = []
    for field in pq.read_schema(path):
        entry: dict[str, Any] = {"name": field.name, "type": _table_schema_type(field.type)}
        if not field.nullable:
            entry["constraints"] = {"required": True}
        fields.append(entry)
    table_schema: dict[str, Any] = {"fields": fields}
    primary_key = next((t["primary_key"] for t in TABLES if t["name"] == table), None)
    if primary_key and all(name in {f["name"] for f in fields} for name in primary_key):
        table_schema["primaryKey"] = primary_key
    return table_schema


def write_datapackage(output_dir: Path, version: str) -> None:
    """Emit a Frictionless Data Package descriptor for published resources.

    Call after every listed resource is written: resources carry their size and SHA-256."""
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
        ("border_status", "json", "border_status.json"),
        ("border_status", "parquet", "border_status.parquet"),
        ("trade_agreements", "jsonl", "trade_agreements.jsonl"),
        ("trade_agreements", "parquet", "trade_agreements.parquet"),
        ("trade_agreement_parties", "jsonl", "trade_agreement_parties.jsonl"),
        ("trade_agreement_parties", "parquet", "trade_agreement_parties.parquet"),
        ("trade_agreement_instruments", "jsonl", "trade_agreement_instruments.jsonl"),
        ("trade_agreement_instruments", "parquet", "trade_agreement_instruments.parquet"),
    ):
        file_path = output_dir / path
        if not file_path.exists():
            continue
        resources.append(
            {
                "name": f"{name}-{fmt}",
                "table": name,
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
        digest = file_digest(file_path)
        resources[-1]["bytes"] = digest["bytes"]
        resources[-1]["hash"] = f"sha256:{digest['sha256']}"
        if fmt == "parquet":
            resources[-1]["schema"] = _parquet_table_schema(file_path, name)
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


def write_dataset_card(output_dir: Path, counts: dict[str, int]) -> None:
    """Render the maintained distribution-card template with current counts.

    The card is committed, so it states the intblock count rounded down to the hundred
    (``documented_count``) and a new record does not change it."""
    template = project_root() / "templates" / "dataset-card.md"
    text = template.read_text(encoding="utf-8")
    for dataset, count in counts.items():
        text = text.replace("{{" + dataset + "_count}}", documented_count(dataset, count))
    (output_dir / "README.md").write_text(text, encoding="utf-8")

def load_yaml_files(directory: Path, desc: str = "Loading files") -> list[dict[str, Any]]:
    """Load all YAML files from a directory (including subdirectories).

    Raises RuntimeError if any file fails to parse, so a build can never
    silently ship with missing records.
    """
    yaml_files = sorted(directory.rglob("*.yaml"))
    data = []
    failures: list[str] = []

    for yaml_file in tqdm(yaml_files, desc=desc):
        try:
            with open(yaml_file, encoding="utf-8") as f:
                content = safe_load(f)
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
    cctx = zstd.ZstdCompressor(level=zstd_level())
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
    cctx = zstd.ZstdCompressor(level=zstd_level())
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(output_file, "wb") as f:
        f.write(cctx.compress(yaml_str.encode("utf-8")))
    typer.echo(f"✓ Saved YAML (zstd): {output_file}")

def fill_country_include_names(
    intblocks_data: list[dict[str, Any]], countries_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Set ``includes[].name`` of ``type: country`` entries to the country's ``name``.

    ``id`` is the join key; the label always comes from the country record, so a stale or
    missing source name never reaches an export. Other entry types keep their source name.
    """
    names = {str(c["code"]): c.get("name") for c in countries_data if c.get("code")}
    for record in intblocks_data:
        for inc in record.get("includes") or []:
            if isinstance(inc, dict) and inc.get("type") == "country":
                name = names.get(str(inc.get("id")))
                if name:
                    inc["name"] = name
    return intblocks_data


def build_membership_rows(intblocks_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten country-coded includes entries into one membership edge per row.

    Organization-type entries are excluded: their ids reference intblocks,
    not countries. Country/territory entries join against ``countries.code``;
    historical-country entries may use the explicit historical registry instead.
    Use a left join when preserving historical membership edges.
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
                    "role": inc.get("role"),
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
    cctx = zstd.ZstdCompressor(level=zstd_level())
    output_file.write_bytes(cctx.compress(buf.getvalue().encode("utf-8")))
    typer.echo(f"✓ Saved CSV (zstd): {output_file}")

def save_parquet(data: list[dict[str, Any]], output_file: Path, schema: pa.Schema | None = None):
    """Save data as Parquet file using explicit schema and Zstd compression.

    Schema mismatches raise instead of silently falling back to pandas
    inference, so schema drift fails the build loudly.
    """
    table = pa.Table.from_pylist(data, schema=schema)
    pq.write_table(table, output_file, compression="zstd", compression_level=zstd_level())
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
    reference_tables: list[tuple[str, list[dict[str, Any]], pa.Schema]] | None = None,
):
    """Create DuckDB database with countries, intblocks, blocktypes, and memberships tables,
    the alias/migration reference tables, and the canonical views from the contract."""
    # Remove existing database if it exists
    if output_file.exists():
        output_file.unlink()

    con = duckdb.connect(str(output_file), config={"storage_compatibility_version": DUCKDB_STORAGE_COMPATIBILITY})

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
            counts[name] = con.execute(f"SELECT COUNT(*) FROM {name}").fetchall()[0][0]

        # Embed a self-describing _meta table (one row per dataset) so the
        # database file carries its own version/schema info.
        meta_rows = [dataset_metadata(name, schema, len(data)) for name, data, schema in tables]
        meta_table = pa.Table.from_pylist(meta_rows, schema=get_meta_schema())
        con.register("arrow_source", meta_table)
        con.execute("CREATE TABLE _meta AS SELECT * FROM arrow_source")
        con.unregister("arrow_source")

        reference_tables = list(reference_tables or [])
        present = {name for name, _, _ in reference_tables}
        # Views read these tables; an empty table keeps a view valid.
        for name, schema_fn in (
            ("border_status", get_border_status_schema),
            ("trade_agreements", get_trade_agreements_schema),
            ("trade_agreement_parties", get_trade_agreement_parties_schema),
            ("trade_agreement_instruments", get_trade_agreement_instruments_schema),
        ):
            if name not in present:
                reference_tables.append((name, [], schema_fn()))
        for name, data, schema in reference_tables:
            con.register("arrow_source", pa.Table.from_pylist(data, schema=schema))
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM arrow_source")
            con.unregister("arrow_source")

        for view in VIEWS:
            if view["name"] in ("current_memberships", "country_trade_agreements") and memberships_data is None:
                continue
            con.execute(f"CREATE VIEW {view['name']} AS {view['sql']}")

        typer.echo(f"✓ Saved DuckDB: {output_file}")
        typer.echo(f"  - Countries: {counts['countries']} rows")
        typer.echo(f"  - Intblocks: {counts['intblocks']} rows")
        typer.echo(f"  - Blocktypes: {counts['blocktypes']} rows")
        if "memberships" in counts:
            typer.echo(f"  - Memberships: {counts['memberships']} rows")

    finally:
        con.close()
