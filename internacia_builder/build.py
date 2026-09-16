#!/usr/bin/env python3
"""Dataset builder CLI for the Internacia project.

Implements the ``build``, ``info``, and ``analyze-quality`` commands. The
implementation lives in focused modules:

- :mod:`internacia_builder.schemas` — PyArrow schemas and schema hashing
- :mod:`internacia_builder.manifest` — build identity and manifest sidecars
- :mod:`internacia_builder.clean` — record normalization
- :mod:`internacia_builder.export` — multi-format writers and DuckDB export
- :mod:`internacia_builder.quality_report` — quality report generators

Public names are re-exported here for backward compatibility (``import
builder`` in tests, ``from internacia_builder.build import *`` in the
``scripts/builder.py`` shim). Prefer importing from the focused modules.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import typer
import yaml
from tqdm import tqdm

from internacia_builder.clean import (
    clean_data,
)
from internacia_builder.export import (
    COUNTRIES_LITE_FIELDS,
    INTBLOCKS_LITE_FIELDS,
    build_membership_rows,
    create_duckdb_database,
    flatten_country,
    flatten_intblock,
    load_attribute_intblock_migrations,
    load_country_aliases,
    load_intblock_aliases,
    load_yaml_files,
    project_lite_rows,
    save_aliases,
    save_attribute_intblock_migrations,
    save_csv_rows,
    save_json_array,
    save_jsonl,
    save_jsonl_zst,
    save_memberships_csv,
    save_parquet,
    save_yaml_zst,
    write_datapackage,
)
from internacia_builder.manifest import (
    begin_build_context,
    get_dataset_version,
    write_manifest,
    write_meta_sidecar,
)
from internacia_builder.paths import project_root as package_project_root
from internacia_builder.quality_report import (
    extract_country_codes,
    generate_country_reports,
    generate_full_report,
    generate_priority_reports,
    generate_rule_reports,
    get_priority_level,
)
from internacia_builder.schemas import (
    get_blocktypes_schema,
    get_countries_schema,
    get_intblocks_schema,
    get_memberships_schema,
    schema_hash,  # noqa: F401  (re-exported for tests and the scripts/builder.py shim)
)
from internacia_builder.validate.completeness import (
    is_null_intblock_field,
    load_includes_status_catalog,
)
from internacia_builder.validate.countries import run_validation as run_countries_validation
from internacia_builder.validate.country_rules import (
    check_country_borders,
    check_country_calling_codes,
    check_country_capital_distance,
    check_country_coordinates,
    check_country_currency_codes,
    check_country_duplicates,
    check_country_entity_flags,
    check_country_entity_status,
    check_country_filename,
    check_country_flag_emoji,
    check_country_indicator_values,
    check_country_indicator_years,
    check_country_landlocked,
    check_country_region_hierarchy,
    check_country_schema,
    check_country_text_encoding,
    check_country_timezones,
    check_country_tld,
    check_country_whitespace,
    check_provenance_count,
    check_provenance_freshness,
    check_provenance_integrity,
    validate_completeness,
    validate_official_iso_count,
)
from internacia_builder.validate.cross_rules import (
    check_border_reciprocity,
    check_border_resolution,
    check_duplicate_acronyms,
    check_duplicate_links,
    check_duplicate_wikidata_ids,
    check_historical_entity_members,
    check_hq_coordinates,
    check_hq_country,
    check_include_name_mismatch,
    check_org_refs,
    check_parent_entity_refs,
    check_partof_suborg_reciprocity,
    check_successor_reciprocity,
    load_border_reciprocity_allowlist,
    validate_aliases,
    validate_intblock_refs,
    validate_partof_refs,
)
from internacia_builder.validate.intblock_rules import (
    check_intblock_blocktypes,
    check_intblock_chronology,
    check_intblock_description_quality,
    check_intblock_directory_alignment,
    check_intblock_duplicates,
    check_intblock_filename,
    check_intblock_founding_members,
    check_intblock_include_dates,
    check_intblock_includes_contract,
    check_intblock_last_verified,
    check_intblock_lifecycle,
    check_intblock_links,
    check_intblock_membership_consistency,
    check_intblock_schema,
    check_intblock_text_encoding,
    check_intblock_topics,
)
from internacia_builder.validate.intblocks import load_topic_aliases, load_topic_catalog
from internacia_builder.validate.intblocks import run_validation as run_intblocks_validation

app = typer.Typer(help="Dataset builder for Internacia project")


def get_project_root() -> Path:
    """Get the project root directory."""
    return package_project_root()


def blocktypes_source_path(root: Path | None = None) -> Path:
    """Authoritative blocktypes taxonomy YAML (not generated)."""
    root = root or get_project_root()
    return root / "data" / "blocktypes" / "blocktypes.yaml"


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

    # Load country code aliases (retired/renamed codes → current code)
    country_aliases = load_country_aliases(project_root)
    typer.echo(f"   Loaded {len(country_aliases)} country alias(es)")

    attribute_migrations = load_attribute_intblock_migrations(project_root)
    typer.echo(f"   Loaded {len(attribute_migrations)} attribute intblock migration(s)")

    # Freeze one build identity for all manifests/sidecars/_meta rows.
    begin_build_context()

    # Get schemas
    countries_schema = get_countries_schema()
    intblocks_schema = get_intblocks_schema()
    blocktypes_schema = get_blocktypes_schema()

    # Flattened membership edges derived from country-coded includes entries.
    memberships_data = build_membership_rows(intblocks_data)
    typer.echo(f"   Derived {len(memberships_data)} membership edge(s)")

    # Generate datasets
    typer.echo("\n💾 Generating datasets...\n")

    # Generate for countries
    if "jsonl" in requested_formats:
        save_jsonl_zst(countries_data, output_dir / "countries.jsonl.zst")
        save_jsonl_zst(intblocks_data, output_dir / "intblocks.jsonl.zst")
        save_jsonl_zst(blocktypes_data, output_dir / "blocktypes.jsonl.zst")
        save_jsonl(countries_data, output_dir / "countries.jsonl")
        save_jsonl(intblocks_data, output_dir / "intblocks.jsonl")
        save_jsonl(blocktypes_data, output_dir / "blocktypes.jsonl")
        save_json_array(countries_data, output_dir / "countries.json.zst")
        save_json_array(intblocks_data, output_dir / "intblocks.json.zst")

    countries_csv_rows = [flatten_country(rec) for rec in countries_data]
    intblocks_csv_rows = [flatten_intblock(rec) for rec in intblocks_data]
    countries_lite_rows = project_lite_rows(countries_csv_rows, COUNTRIES_LITE_FIELDS)
    intblocks_lite_rows = project_lite_rows(intblocks_csv_rows, INTBLOCKS_LITE_FIELDS)
    save_csv_rows(countries_csv_rows, output_dir / "countries.csv.zst")
    save_csv_rows(intblocks_csv_rows, output_dir / "intblocks.csv.zst")
    save_csv_rows(countries_lite_rows, output_dir / "countries-lite.csv.zst")
    save_csv_rows(intblocks_lite_rows, output_dir / "intblocks-lite.csv.zst")

    if "yaml" in requested_formats:
        save_yaml_zst(countries_data, output_dir / "countries.yaml.zst")
        save_yaml_zst(intblocks_data, output_dir / "intblocks.yaml.zst")
        save_yaml_zst(blocktypes_data, output_dir / "blocktypes.yaml.zst")

    if "parquet" in requested_formats:
        save_parquet(countries_data, output_dir / "countries.parquet", schema=countries_schema)
        save_parquet(intblocks_data, output_dir / "intblocks.parquet", schema=intblocks_schema)
        save_parquet(blocktypes_data, output_dir / "blocktypes.parquet", schema=blocktypes_schema)
        save_parquet(memberships_data, output_dir / "memberships.parquet", schema=get_memberships_schema())
        save_parquet(countries_lite_rows, output_dir / "countries-lite.parquet")
        save_parquet(intblocks_lite_rows, output_dir / "intblocks-lite.parquet")
        save_memberships_csv(memberships_data, output_dir / "memberships.csv.zst")
        write_manifest(output_dir, "countries", countries_schema, len(countries_data))
        write_manifest(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
        write_manifest(output_dir, "blocktypes", blocktypes_schema, len(blocktypes_data))
        write_manifest(output_dir, "memberships", get_memberships_schema(), len(memberships_data))
        write_meta_sidecar(output_dir, "countries", countries_schema, len(countries_data))
        write_meta_sidecar(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
        write_meta_sidecar(output_dir, "blocktypes", blocktypes_schema, len(blocktypes_data))
        write_meta_sidecar(output_dir, "memberships", get_memberships_schema(), len(memberships_data))

    if "duckdb" in requested_formats:
        create_duckdb_database(
            countries_data,
            intblocks_data,
            blocktypes_data,
            output_dir / "internacia.duckdb",
            countries_schema=countries_schema,
            intblocks_schema=intblocks_schema,
            blocktypes_schema=blocktypes_schema,
            memberships_data=memberships_data,
        )
        if "parquet" not in requested_formats:
            write_manifest(output_dir, "countries", countries_schema, len(countries_data))
            write_manifest(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
            write_manifest(output_dir, "blocktypes", blocktypes_schema, len(blocktypes_data))
            write_manifest(output_dir, "memberships", get_memberships_schema(), len(memberships_data))

    # Always emit alias artifacts so consumers can remap retired ids/codes.
    save_aliases(intblock_aliases, output_dir, basename="intblocks_aliases", write_parquet="parquet" in requested_formats)
    save_aliases(country_aliases, output_dir, basename="countries_aliases", write_parquet="parquet" in requested_formats)
    save_attribute_intblock_migrations(
        attribute_migrations, output_dir, write_parquet="parquet" in requested_formats
    )

    write_datapackage(output_dir, get_dataset_version())

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

    started_at = time.monotonic()
    typer.echo("🔍 Scanning data sources...")
    typer.echo(f"  Countries: {countries_dir}")
    typer.echo(f"  Intblocks: {intblocks_dir}")
    typer.echo(f"  Output: {output_dir}")
    if check_http:
        typer.echo("  HTTP link checking: enabled (slow)")
    if check_wikidata:
        typer.echo("  Wikidata validation: enabled (slow)")

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
        raise typer.Exit(1) from e

    try:
        schema_intblocks = json.loads(schema_path_intblocks.read_text(encoding="utf-8"))
        completeness_cfg_intblocks = yaml.safe_load(completeness_path_intblocks.read_text(encoding="utf-8")) or {}
        includes_status_catalog = load_includes_status_catalog(project_root / "data" / "schemas")
    except Exception as e:
        typer.echo(f"Error loading intblock schema/config: {e}", err=True)
        raise typer.Exit(1) from e

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

    topic_aliases = load_topic_aliases(project_root / "data" / "schemas" / "topic_aliases.yaml")
    topic_catalog = load_topic_catalog(project_root / "data" / "schemas" / "topics.yaml")
    countries_prov_cfg = completeness_cfg_countries.get("provenance") or {}
    intblocks_prov_cfg = (completeness_cfg_intblocks.get("fields") or {}).get("provenance") or {}
    countries_prov_max_age = int(countries_prov_cfg.get("max_age_months") or 0)
    intblocks_prov_max_age = int(intblocks_prov_cfg.get("max_age_months") or 0)
    countries_prov_min_count = int(countries_prov_cfg.get("min_count") or 0)
    intblocks_prov_min_count = int(intblocks_prov_cfg.get("min_count") or 0)
    region_allowlist = {
        str(x) for x in ((completeness_cfg_countries.get("region_hierarchy") or {}).get("allowlist") or [])
    }
    last_verified_max_age = int(
        (completeness_cfg_intblocks.get("quality") or {}).get("last_verified_max_age_months") or 0
    )

    country_files = sorted(countries_dir.glob("*.yaml"))
    intblock_files = sorted(intblocks_dir.rglob("*.yaml"))
    typer.echo(f"  Found {len(country_files)} country files, {len(intblock_files)} intblock files\n")

    country_records = []
    country_rel_paths = []
    all_issues = []
    records_with_issues = {}
    total_records = 0
    parse_errors = 0

    for path in tqdm(country_files, desc="Checking countries", unit="record", mininterval=1.0):
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
            record_issues.extend(check_country_indicator_values(record))
            record_issues.extend(check_country_whitespace(record))
            record_issues.extend(check_country_entity_status(record))
            record_issues.extend(check_country_entity_flags(record))
            record_issues.extend(check_country_currency_codes(record))
            record_issues.extend(check_country_coordinates(record))
            record_issues.extend(check_country_filename(record, rel_path))
            record_issues.extend(check_country_tld(record))
            record_issues.extend(check_country_calling_codes(record))
            record_issues.extend(check_country_timezones(record))
            record_issues.extend(check_country_flag_emoji(record))
            record_issues.extend(check_country_landlocked(record))
            record_issues.extend(check_country_region_hierarchy(record, region_allowlist))
            record_issues.extend(check_country_capital_distance(record, completeness_cfg_countries))
            record_issues.extend(check_country_text_encoding(record))
            record_issues.extend(check_provenance_integrity(record))
            if countries_prov_max_age:
                record_issues.extend(check_provenance_freshness(record, max_age_months=countries_prov_max_age))
            if countries_prov_min_count:
                record_issues.extend(check_provenance_count(record, min_count=countries_prov_min_count))

            for issue in record_issues:
                issue["file_path"] = rel_path
                issue["record_id"] = record_id
                issue["priority"] = get_priority_level(issue["issue_type"], issue)

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
            parse_errors += 1

    country_issue_count = len(all_issues)

    intblock_records = []
    intblock_rel_paths = []
    known_country_codes = {str(r.get("code")) for r in country_records if r.get("code")}

    for path in tqdm(intblock_files, desc="Checking intblocks", unit="record", mininterval=1.0):
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
            record_issues.extend(check_intblock_filename(record, rel_path))
            record_issues.extend(check_intblock_directory_alignment(record, rel_path))
            record_issues.extend(check_intblock_topics(record, topic_aliases, topic_catalog))
            record_issues.extend(check_intblock_lifecycle(record))
            record_issues.extend(check_intblock_chronology(record))
            record_issues.extend(check_intblock_include_dates(record))
            record_issues.extend(check_intblock_founding_members(record, known_country_codes))
            record_issues.extend(check_intblock_membership_consistency(record, completeness_cfg_intblocks))
            record_issues.extend(check_intblock_description_quality(record))
            record_issues.extend(check_intblock_text_encoding(record))
            if last_verified_max_age:
                record_issues.extend(
                    check_intblock_last_verified(record, max_age_months=last_verified_max_age)
                )
            record_issues.extend(
                check_intblock_includes_contract(record, completeness_cfg_intblocks, includes_status_catalog)
            )
            record_issues.extend(check_intblock_links(record, check_http, check_wikidata))
            record_issues.extend(check_provenance_integrity(record))
            if intblocks_prov_max_age:
                record_issues.extend(check_provenance_freshness(record, max_age_months=intblocks_prov_max_age))
            if intblocks_prov_min_count:
                record_issues.extend(check_provenance_count(record, min_count=intblocks_prov_min_count))

            for issue in record_issues:
                issue["file_path"] = rel_path
                issue["record_id"] = record_id
                issue["priority"] = get_priority_level(issue["issue_type"], issue)

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
            parse_errors += 1

    intblock_issue_count = len(all_issues) - country_issue_count

    references_cfg = completeness_cfg_intblocks.get("references") or {}
    alias_names = {str(a.get("alias") or "") for a in aliases if isinstance(a, dict)} - {""}
    all_rel_paths = country_rel_paths + intblock_rel_paths
    all_records = country_records + intblock_records
    country_codes = known_country_codes
    countries_by_code = {str(r.get("code")): r for r in country_records if r.get("code")}

    cross_checks = [
        ("country duplicate identifiers", lambda: check_country_duplicates(country_records, country_rel_paths)),
        ("official ISO count", lambda: validate_official_iso_count(country_records)),
        ("country completeness", lambda: validate_completeness(country_records, completeness_cfg_countries)),
        ("intblock duplicate ids", lambda: check_intblock_duplicates(intblock_records, intblock_rel_paths)),
        ("partof references", lambda: validate_partof_refs(intblock_records, intblock_rel_paths)),
        (
            "alias integrity",
            lambda: validate_aliases(aliases, {str(r.get("id", "")) for r in intblock_records if r.get("id")}),
        ),
        (
            "intblock completeness",
            lambda: validate_completeness(
                intblock_records,
                completeness_cfg_intblocks,
                null_checker=is_null_intblock_field,
                attach_field_priority=True,
            ),
        ),
        (
            "country include resolution",
            lambda: validate_intblock_refs(
                countries_dir, intblock_records, intblock_rel_paths, completeness_cfg_countries
            ),
        ),
        ("duplicate links", lambda: check_duplicate_links(all_rel_paths, all_records)),
        ("border resolution", lambda: check_border_resolution(country_records, country_rel_paths)),
        (
            "border reciprocity",
            lambda: check_border_reciprocity(
                country_records,
                country_rel_paths,
                load_border_reciprocity_allowlist(completeness_cfg_countries),
            ),
        ),
        (
            "organizational references",
            lambda: check_org_refs(
                intblock_records,
                intblock_rel_paths,
                alias_names,
                {str(x) for x in (references_cfg.get("org_ref_allowlist") or [])},
            ),
        ),
        (
            "headquarters countries",
            lambda: check_hq_country(
                intblock_records,
                intblock_rel_paths,
                country_codes,
                set(completeness_cfg_countries.get("special_entity_allowlist") or []),
            ),
        ),
        (
            "wikidata id uniqueness",
            lambda: check_duplicate_wikidata_ids(
                all_rel_paths,
                all_records,
                {str(x) for x in (references_cfg.get("wikidata_duplicate_allowlist") or [])},
            ),
        ),
        (
            "include display names",
            lambda: check_include_name_mismatch(
                intblock_records,
                intblock_rel_paths,
                countries_by_code,
            ),
        ),
        (
            "parent entity references",
            lambda: check_parent_entity_refs(country_records, country_rel_paths),
        ),
        (
            "lineage reciprocity",
            lambda: check_successor_reciprocity(intblock_records, intblock_rel_paths),
        ),
        (
            "partof/suborganization reciprocity",
            lambda: check_partof_suborg_reciprocity(intblock_records, intblock_rel_paths),
        ),
        (
            "acronym uniqueness",
            lambda: check_duplicate_acronyms(
                intblock_records,
                intblock_rel_paths,
                {str(x) for x in (references_cfg.get("acronym_duplicate_allowlist") or [])},
            ),
        ),
        (
            "headquarters coordinates",
            lambda: check_hq_coordinates(
                intblock_records,
                intblock_rel_paths,
                countries_by_code,
                completeness_cfg_intblocks,
            ),
        ),
        (
            "historical entity members",
            lambda: check_historical_entity_members(
                intblock_records,
                intblock_rel_paths,
                countries_by_code,
            ),
        ),
    ]

    cross_issues = []
    with tqdm(cross_checks, desc="Cross-record checks", unit="check") as bar:
        for label, check in bar:
            bar.set_postfix_str(label)
            cross_issues.extend(check())

    for issue in cross_issues:
        issue.setdefault("file_path", "cross-record")
        issue.setdefault("record_id", "cross-record")
        issue["priority"] = get_priority_level(issue["issue_type"], issue)

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

    typer.echo("📝 Writing reports...")
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

    elapsed = time.monotonic() - started_at
    clean_records = total_records - len(records_with_issues)
    clean_pct = (clean_records / total_records * 100) if total_records else 0.0

    typer.echo(f"\n✅ Quality analysis completed in {elapsed:.1f}s")
    typer.echo(f"  Records analyzed: {total_records} ({len(country_files)} countries, {len(intblock_files)} intblocks)")
    if parse_errors:
        typer.echo(f"  ⚠️  YAML parse errors: {parse_errors}")
    typer.echo(f"  Records with issues: {len(records_with_issues)} ({clean_records} clean, {clean_pct:.1f}%)")
    typer.echo(f"  Total issues found: {len(all_issues)}")
    typer.echo(f"    from country checks: {country_issue_count}")
    typer.echo(f"    from intblock checks: {intblock_issue_count}")
    typer.echo(f"    from cross-record checks: {len(cross_issues)}")

    typer.echo("\nPriority breakdown:")
    for p in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        cnt = len(issues_by_priority.get(p, []))
        marker = "❌" if cnt and p in ("CRITICAL", "IMPORTANT") else "  "
        typer.echo(f"  {marker} {p}: {cnt}")
    if issues_by_priority.get("CRITICAL") or issues_by_priority.get("IMPORTANT"):
        typer.echo("  Note: CRITICAL/IMPORTANT issues fail the CI quality gate.")

    top_types = sorted(issues_by_type.items(), key=lambda kv: len(kv[1]), reverse=True)
    if top_types:
        typer.echo("\nTop issue types:")
        for issue_type, issues_list in top_types[:8]:
            priority = issues_list[0].get("priority", "MEDIUM")
            typer.echo(f"  {len(issues_list):5d}  {issue_type} [{priority}]")
        if len(top_types) > 8:
            rest = sum(len(v) for _, v in top_types[8:])
            typer.echo(f"        ... and {len(top_types) - 8} more issue type(s) ({rest} issues)")

    typer.echo(f"\nReports saved in: {output_dir}")
    typer.echo(f"  {output_dir / 'full_report.jsonl'} (machine-readable)")
    typer.echo(f"  {output_dir / 'full_report.txt'} (human-readable)")
    typer.echo(f"  {output_dir / 'priorities'}/ (per-priority), {output_dir / 'rules'}/ (per-rule), {output_dir / 'countries'}/ (per-country)")


def main() -> None:
    """Console entry point for the dataset builder CLI."""
    app()


if __name__ == "__main__":
    main()
