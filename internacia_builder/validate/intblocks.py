#!/usr/bin/env python3
"""Validate intblock YAML sources: schema, taxonomy, references, completeness.

Rule logic lives in :mod:`internacia_builder.validate.intblock_rules` and
:mod:`internacia_builder.validate.cross_rules`; this module adapts the shared
issue dicts to CLI error/warning messages and drives the validation run.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import typer
import yaml

from internacia_builder.paths import project_root
from internacia_builder.validate import cross_rules, intblock_rules
from internacia_builder.validate.completeness import (
    load_includes_status_catalog,
    validate_completeness,
    validate_includes_status,
    validate_membership_applicability,
)
from internacia_builder.validate.intblock_rules import TEMPLATED_DESC_RE as TEMPLATED_DESC

app = typer.Typer(help="Validate internacia-db intblock data")

WIKIDATA = re.compile(r"^Q[1-9][0-9]*$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_schema(record: dict[str, Any], schema: dict[str, Any], rel_path: str) -> list[str]:
    return [
        f"{rel_path}: {issue['field']}: {issue['message']}"
        for issue in intblock_rules.check_intblock_schema(record, schema)
    ]


def check_duplicate_ids(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    rel_paths = [rel for rel, _ in records]
    recs = [rec for _, rec in records]
    return [
        f"duplicate id '{issue['current_value']}' in {issue['file_path']} and {issue['other_path']}"
        for issue in intblock_rules.check_intblock_duplicates(recs, rel_paths)
    ]


def validate_blocktypes(records: list[tuple[str, dict[str, Any]]], taxonomy: set[str]) -> list[str]:
    """Every blocktype value must exist in the blocktypes taxonomy."""
    errors: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_blocktypes(rec, taxonomy):
            errors.append(f"{rel}: unknown blocktype '{issue['current_value']}'")
    return errors


def validate_filename_ids(records: list[tuple[str, dict[str, Any]]]) -> list[str]:
    """The YAML filename stem must match the record id exactly, including case."""
    errors: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_filename(rec, rel):
            errors.append(f"{rel}: {issue['suggested_action']}")
    return errors


def validate_directory_alignment(records: list[tuple[str, dict[str, Any]]]) -> list[str]:
    """The parent category directory name must appear in the record's blocktype list."""
    errors: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_directory_alignment(rec, rel):
            errors.append(f"{rel}: {issue['suggested_action']}")
    return errors


def validate_topics(
    records: list[tuple[str, dict[str, Any]]],
    aliases: dict[str, str],
    catalog: set[str] | None = None,
) -> list[str]:
    """Warn on empty topics, deprecated topic keys, and keys missing from the
    canonical catalog."""
    warnings: list[str] = []
    for rel, rec in records:
        topics = rec.get("topics")
        if topics is None or topics == []:
            warnings.append(f"{rel}: missing topics")
            continue
        for issue in intblock_rules.check_intblock_topics(rec, aliases, catalog):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def load_topic_aliases(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = load_yaml(path) or {}
    raw = data.get("aliases") or {}
    return {str(k): str(v.get("canonical", "")) for k, v in raw.items() if isinstance(v, dict)}


def load_topic_catalog(path: Path) -> set[str]:
    """Canonical topic keys from data/schemas/topics.yaml."""
    if not path.exists():
        return set()
    data = load_yaml(path) or {}
    return {str(k) for k in (data.get("topics") or {})}


def validate_partof_refs(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """partof references should resolve to existing intblock ids (warn-only)."""
    rel_paths = [rel for rel, _ in records]
    recs = [rec for _, rec in records]
    return [
        f"{issue['file_path']}: partof '{issue['current_value']}' does not match any intblock id"
        for issue in cross_rules.validate_partof_refs(recs, rel_paths)
    ]


def validate_org_refs(
    records: list[tuple[str, dict[str, Any]]],
    alias_names: set[str],
    allowlist: set[str],
) -> list[str]:
    """predecessor/successor/suborganizations references should resolve (warn-only)."""
    rel_paths = [rel for rel, _ in records]
    recs = [rec for _, rec in records]
    return [
        f"{issue['file_path']}: {issue['suggested_action']}"
        for issue in cross_rules.check_org_refs(recs, rel_paths, alias_names, allowlist)
    ]


def validate_lifecycle(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """Historical entities must use the standard dissolved field, not ad-hoc keys,
    and lifecycle status must be consistent with the dissolved date."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_lifecycle(rec):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_chronology(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """founded/dissolved must parse, be ordered, and not lie in the future."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_chronology(rec):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_membership_consistency(
    records: list[tuple[str, dict[str, Any]]],
    config: dict[str, Any],
) -> list[str]:
    """Duplicate includes, membership_count mismatches, contradictory markers."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_membership_consistency(rec, config):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_include_dates(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """includes[].joined/left date parsing, ordering, and dissolution bounds."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_include_dates(rec):
            warnings.append(f"{rel}: {issue['field']}: {issue['suggested_action']}")
    return warnings


def validate_founding_members(
    records: list[tuple[str, dict[str, Any]]],
    country_codes: set[str],
) -> list[str]:
    """founding_members must resolve to countries and appear in includes."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_founding_members(rec, country_codes):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_last_verified(
    records: list[tuple[str, dict[str, Any]]],
    config: dict[str, Any],
) -> list[str]:
    """Advisory when last_verified is older than the configured maximum age."""
    max_age = int((config.get("quality") or {}).get("last_verified_max_age_months") or 0)
    if max_age <= 0:
        return []
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_last_verified(rec, max_age_months=max_age):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_text_encoding(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """Mojibake and control-character detection in name/description."""
    warnings: list[str] = []
    for rel, rec in records:
        for issue in intblock_rules.check_intblock_text_encoding(rec):
            warnings.append(f"{rel}: {issue['suggested_action']}")
    return warnings


def validate_aliases(
    aliases: list[dict[str, Any]],
    known_ids: set[str],
) -> list[str]:
    """Alias integrity: every target must resolve to an existing intblock id, and
    an alias that collides with a current id must be marked ``disambiguated``."""
    return [issue["suggested_action"] for issue in cross_rules.validate_aliases(aliases, known_ids)]


def validate_description_quality(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, Any]]:
    """Measure the share of records using templated boilerplate descriptions."""
    errors: list[str] = []
    warnings: list[str] = []
    n = len(records)
    rule = (config.get("quality") or {}).get("templated_description") or {}
    templated = sum(1 for r in records if TEMPLATED_DESC.match(str(r.get("description") or "")))
    rate = templated / n if n else 0.0
    report = {"templated_count": templated, "templated_rate": round(rate, 4)}
    if not rule:
        return errors, warnings, report
    max_rate = float(rule.get("max", 1.0))
    mode = rule.get("mode", "warn")
    report["max"] = max_rate
    report["mode"] = mode
    if rate > max_rate:
        msg = f"description quality: templated rate {rate:.2%} exceeds max {max_rate:.2%} ({templated}/{n})"
        (errors if mode == "error" else warnings).append(msg)
    return errors, warnings, report


@app.command()
def main(
    intblocks_dir: Path = typer.Option(
        None,
        "--intblocks-dir",
        help="Path to data/intblocks",
    ),
    fail_on_warning: bool = typer.Option(
        False,
        "--fail-on-warning",
        help="Treat warnings as errors",
    ),
    report: Path = typer.Option(
        None,
        "--report",
        help="Write JSON validation summary to this path",
    ),
) -> None:
    """Run all intblock validation checks."""
    raise typer.Exit(
        run_validation(
            intblocks_dir=intblocks_dir,
            fail_on_warning=fail_on_warning,
            report=report,
        )
    )


def run_validation(
    intblocks_dir: Path | None = None,
    fail_on_warning: bool = False,
    report: Path | None = None,
) -> int:
    """Run intblock validation; return process exit code (0 = success)."""
    root = project_root()
    intblocks_dir = intblocks_dir or root / "data" / "intblocks"
    countries_dir = root / "data" / "countries"
    schema_path = root / "data" / "schemas" / "intblocks.schema.json"
    completeness_path = root / "data" / "schemas" / "intblocks_completeness.yaml"
    countries_completeness_path = root / "data" / "schemas" / "countries_completeness.yaml"
    schemas_dir = root / "data" / "schemas"
    blocktypes_path = root / "data" / "blocktypes" / "blocktypes.yaml"
    aliases_path = root / "data" / "intblocks_aliases.yaml"
    topic_aliases_path = root / "data" / "schemas" / "topic_aliases.yaml"

    schema = load_json(schema_path)
    completeness_cfg = load_yaml(completeness_path) or {}
    taxonomy: set[str] = set()
    if blocktypes_path.exists():
        taxonomy = {str(b.get("id", "")) for b in (load_yaml(blocktypes_path) or []) if isinstance(b, dict)}

    errors: list[str] = []
    warnings: list[str] = []
    records: list[tuple[str, dict[str, Any]]] = []

    yaml_files = sorted(intblocks_dir.rglob("*.yaml"))
    if not yaml_files:
        typer.echo(f"No YAML files in {intblocks_dir}", err=True)
        return 1

    for path in yaml_files:
        rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        try:
            record = load_yaml(path)
        except yaml.YAMLError as e:
            errors.append(f"{rel}: YAML parse error: {e}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{rel}: expected a mapping at the document root")
            continue
        records.append((rel, record))
        errors.extend(validate_schema(record, schema, rel))

    errors.extend(check_duplicate_ids(records))
    errors.extend(validate_filename_ids(records))
    if taxonomy:
        errors.extend(validate_blocktypes(records, taxonomy))
    errors.extend(validate_directory_alignment(records))
    topic_aliases = load_topic_aliases(topic_aliases_path)
    topic_catalog = load_topic_catalog(schemas_dir / "topics.yaml")
    warnings.extend(validate_topics(records, topic_aliases, topic_catalog))
    warnings.extend(validate_partof_refs(records))
    warnings.extend(validate_lifecycle(records))
    warnings.extend(validate_chronology(records))
    warnings.extend(validate_include_dates(records))
    warnings.extend(validate_membership_consistency(records, completeness_cfg))
    warnings.extend(validate_last_verified(records, completeness_cfg))
    warnings.extend(validate_text_encoding(records))

    rel_paths_all = [rel for rel, _ in records]
    recs_all = [rec for _, rec in records]
    warnings.extend(
        f"{issue['file_path']}: {issue['suggested_action']}"
        for issue in cross_rules.check_successor_reciprocity(recs_all, rel_paths_all)
    )
    warnings.extend(
        f"{issue['file_path']}: {issue['suggested_action']}"
        for issue in cross_rules.check_partof_suborg_reciprocity(recs_all, rel_paths_all)
    )

    references_cfg = completeness_cfg.get("references") or {}
    alias_names: set[str] = set()
    if aliases_path.exists():
        known_ids = {str(rec.get("id", "")) for _, rec in records if rec.get("id")}
        aliases = load_yaml(aliases_path) or []
        errors.extend(validate_aliases(aliases, known_ids))
        alias_names = {str(a.get("alias") or "") for a in aliases if isinstance(a, dict)} - {""}

    warnings.extend(
        validate_org_refs(
            records,
            alias_names,
            {str(x) for x in (references_cfg.get("org_ref_allowlist") or [])},
        )
    )

    if countries_dir.exists():
        countries_cfg = load_yaml(countries_completeness_path) or {}
        country_codes = {p.stem for p in countries_dir.glob("*.yaml")}
        countries_by_code: dict[str, dict[str, Any]] = {}
        for country_path in sorted(countries_dir.glob("*.yaml")):
            try:
                country = load_yaml(country_path)
            except yaml.YAMLError:
                continue  # parse errors are reported by validate_countries
            if isinstance(country, dict) and country.get("code"):
                countries_by_code[str(country["code"])] = country
        rel_paths = [rel for rel, _ in records]
        recs = [rec for _, rec in records]
        warnings.extend(
            f"{issue['file_path']}: {issue['suggested_action']}"
            for issue in cross_rules.check_hq_country(
                recs,
                rel_paths,
                country_codes,
                set(countries_cfg.get("special_entity_allowlist") or []),
            )
        )
        warnings.extend(validate_founding_members(records, country_codes))
        warnings.extend(
            f"{issue['file_path']}: {issue['suggested_action']}"
            for issue in cross_rules.check_hq_coordinates(
                recs, rel_paths, countries_by_code, completeness_cfg
            )
        )
        warnings.extend(
            f"{issue['file_path']}: {issue['suggested_action']}"
            for issue in cross_rules.check_historical_entity_members(
                recs, rel_paths, countries_by_code
            )
        )

    rel_paths = [rel for rel, _ in records]
    recs = [rec for _, rec in records]
    warnings.extend(
        f"{issue['file_path']}: {issue['suggested_action']}"
        for issue in cross_rules.check_duplicate_wikidata_ids(
            rel_paths,
            recs,
            {str(x) for x in (references_cfg.get("wikidata_duplicate_allowlist") or [])},
        )
    )
    warnings.extend(
        f"{issue['file_path']}: {issue['suggested_action']}"
        for issue in cross_rules.check_duplicate_acronyms(
            recs,
            rel_paths,
            {str(x) for x in (references_cfg.get("acronym_duplicate_allowlist") or [])},
        )
    )

    includes_status_catalog = load_includes_status_catalog(schemas_dir)
    membership_errors, membership_warnings = validate_membership_applicability(records, completeness_cfg)
    errors.extend(membership_errors)
    warnings.extend(membership_warnings)

    status_errors, status_warnings = validate_includes_status(records, includes_status_catalog, completeness_cfg)
    errors.extend(status_errors)
    warnings.extend(status_warnings)

    all_records = [rec for _, rec in records]
    comp_errors, comp_warnings, completeness_report = validate_completeness(all_records, completeness_cfg)
    errors.extend(comp_errors)
    warnings.extend(comp_warnings)

    desc_errors, desc_warnings, description_report = validate_description_quality(all_records, completeness_cfg)
    errors.extend(desc_errors)
    warnings.extend(desc_warnings)

    if report:
        summary = {
            "intblocks_validated": len(records),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "completeness": completeness_report,
            "description_quality": description_report,
        }
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation report: {report}")

    for w in warnings:
        typer.echo(f"WARN: {w}", err=True)
    for e in errors:
        typer.echo(f"ERROR: {e}", err=True)

    typer.echo(f"Validated {len(records)} intblocks: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    app()
