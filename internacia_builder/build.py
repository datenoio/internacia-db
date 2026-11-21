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
from internacia_builder.contract import write_checksums, write_contract
from internacia_builder.export import (
    COUNTRIES_LITE_FIELDS,
    INTBLOCKS_LITE_FIELDS,
    build_membership_rows,
    create_duckdb_database,
    fill_country_include_names,
    flatten_country,
    flatten_intblock,
    load_attribute_intblock_migrations,
    load_border_status,
    load_country_aliases,
    load_intblock_aliases,
    load_yaml_files,
    project_lite_rows,
    save_aliases,
    save_attribute_intblock_migrations,
    save_border_status,
    save_csv_rows,
    save_json_array,
    save_jsonl,
    save_jsonl_zst,
    save_memberships_csv,
    save_parquet,
    save_yaml_zst,
    write_datapackage,
    write_dataset_card,
)
from internacia_builder.freshness import last_verified_kpi, load_tier1
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
    get_aliases_schema,
    get_attribute_migration_schema,
    get_blocktypes_schema,
    get_border_status_schema,
    get_countries_schema,
    get_intblocks_schema,
    get_memberships_schema,
    schema_hash,  # noqa: F401  (re-exported for tests and the scripts/builder.py shim)
)
from internacia_builder.validate.countries import run_validation as run_countries_validation
from internacia_builder.validate.cross_rules import check_duplicate_links  # noqa: F401  (re-exported for tests)
from internacia_builder.validate.intblocks import run_validation as run_intblocks_validation
from internacia_builder.validate.registry import (
    COUNTRIES,
    COUNTRY_RULES,
    INTBLOCK_RULES,
    INTBLOCKS,
    Rule,
    load_context,
    run_rules,
)
from internacia_builder.yaml_io import safe_load

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
    intblocks_data = fill_country_include_names(intblocks_data, countries_data)

    # Load blocktypes data
    blocktypes_file = blocktypes_source_path(project_root)
    if not blocktypes_file.exists():
        typer.echo(f"Error: Blocktypes source not found: {blocktypes_file}", err=True)
        raise typer.Exit(1)

    typer.echo("📁 Loading blocktypes data...")
    try:
        with open(blocktypes_file, encoding="utf-8") as f:
            blocktypes_data = safe_load(f)
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

    border_status = load_border_status(project_root)
    typer.echo(f"   Loaded {len(border_status)} border status entr{'y' if len(border_status) == 1 else 'ies'}")

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
            reference_tables=[
                ("intblocks_aliases", intblock_aliases, get_aliases_schema()),
                ("countries_aliases", country_aliases, get_aliases_schema()),
                ("attribute_intblock_migrations", attribute_migrations, get_attribute_migration_schema()),
                ("border_status", border_status, get_border_status_schema()),
            ],
        )

    # Always emit alias artifacts so consumers can remap retired ids/codes.
    save_aliases(intblock_aliases, output_dir, basename="intblocks_aliases", write_parquet="parquet" in requested_formats)
    save_aliases(country_aliases, output_dir, basename="countries_aliases", write_parquet="parquet" in requested_formats)
    save_attribute_intblock_migrations(
        attribute_migrations, output_dir, write_parquet="parquet" in requested_formats
    )
    save_border_status(border_status, output_dir, write_parquet="parquet" in requested_formats)

    # Manifests list the checksums of their dataset's files, so they follow every data file.
    if {"parquet", "duckdb"} & set(requested_formats):
        write_manifest(output_dir, "countries", countries_schema, len(countries_data))
        write_manifest(output_dir, "intblocks", intblocks_schema, len(intblocks_data))
        write_manifest(output_dir, "blocktypes", blocktypes_schema, len(blocktypes_data))
        write_manifest(output_dir, "memberships", get_memberships_schema(), len(memberships_data))

    write_datapackage(output_dir, get_dataset_version())
    write_dataset_card(output_dir, {"countries": len(countries_data), "intblocks": len(intblocks_data), "blocktypes": len(blocktypes_data)})
    write_contract(output_dir, get_dataset_version())
    typer.echo(f"✓ Saved contract: {output_dir / 'contract.json'}")
    write_checksums(output_dir)
    typer.echo(f"✓ Saved checksums: {output_dir / 'SHA256SUMS'}")

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

    try:
        ctx = load_context(project_root, check_http=check_http, check_wikidata=check_wikidata)
    except Exception as e:
        typer.echo(f"Error loading schemas and rule configuration: {e}", err=True)
        raise typer.Exit(1) from e
    country_records, intblock_records = ctx.countries.records, ctx.intblocks.records
    completeness_cfg_intblocks = ctx.intblocks_cfg
    total_records = ctx.countries.file_count + ctx.intblocks.file_count
    typer.echo(f"  Found {ctx.countries.file_count} country files, {ctx.intblocks.file_count} intblock files\n")

    all_issues = []
    parse_errors = 0
    for dataset in (ctx.countries, ctx.intblocks):
        for rel_path, error in dataset.errors:
            all_issues.append({
                "issue_type": "SCHEMA_ERROR",
                "field": "(root)",
                "current_value": error,
                "suggested_action": error,
                "file_path": rel_path,
                "record_id": Path(rel_path).stem,
                "priority": get_priority_level("SCHEMA_ERROR"),
            })
            parse_errors += 1

    issue_counts = {COUNTRIES: 0, INTBLOCKS: 0, "cross-record": 0}
    rules = [rule for rule in (*COUNTRY_RULES, *INTBLOCK_RULES) if rule.enabled(ctx)]
    with tqdm(total=len(rules), desc="Running rules", unit="rule") as bar:

        def advance(rule: Rule) -> None:
            bar.set_postfix_str(f"{rule.dataset}: {rule.name}")
            bar.update(1)

        for rule, issue in run_rules(rules, ctx, on_rule=advance):
            issue["priority"] = get_priority_level(issue["issue_type"], issue)
            issue_counts["cross-record" if rule.cross else rule.dataset] += 1
            all_issues.append(issue)

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

    quality_cfg = completeness_cfg_intblocks.get("quality") or {}
    kpi = last_verified_kpi(
        intblock_records,
        load_tier1(project_root),
        max_age_months=int(quality_cfg.get("last_verified_max_age_months") or 12),
        tier1_max_age_months=int(quality_cfg.get("last_verified_tier1_max_age_months") or 6),
    )
    (output_dir / "last_verified_kpi.json").write_text(json.dumps(kpi, indent=2) + "\n", encoding="utf-8")
    typer.echo(
        f"  last_verified: {kpi['all']['missing']} of {kpi['all']['total']} never verified, "
        f"{kpi['all']['stale']} overdue; tier 1: {kpi['tier1']['missing']} never verified, "
        f"{kpi['tier1']['stale']} overdue"
    )

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
    typer.echo(
        f"  Records analyzed: {total_records} "
        f"({ctx.countries.file_count} countries, {ctx.intblocks.file_count} intblocks)"
    )
    if parse_errors:
        typer.echo(f"  ⚠️  YAML parse errors: {parse_errors}")
    typer.echo(f"  Records with issues: {len(records_with_issues)} ({clean_records} clean, {clean_pct:.1f}%)")
    typer.echo(f"  Total issues found: {len(all_issues)}")
    typer.echo(f"    from country checks: {issue_counts[COUNTRIES]}")
    typer.echo(f"    from intblock checks: {issue_counts[INTBLOCKS]}")
    typer.echo(f"    from cross-record checks: {issue_counts['cross-record']}")

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
