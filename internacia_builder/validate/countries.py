#!/usr/bin/env python3
"""Validate country YAML sources, completeness, and intblock cross-references.

Rule logic lives in :mod:`internacia_builder.validate.country_rules` and
:mod:`internacia_builder.validate.cross_rules`; this module adapts the shared
issue dicts to CLI error/warning messages and drives the validation run.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import typer
import yaml

from internacia_builder.paths import project_root
from internacia_builder.validate import country_rules, cross_rules, registry
from internacia_builder.validate.country_rules import (  # noqa: F401 (re-exported API)
    CODE_STATUSES,
    ENTITY_TYPES,
    EXPECTED_OFFICIAL_ISO_COUNT,
    NON_ISO_ALPHA2,
    is_null_field,
)
from internacia_builder.validate.identifiers import release_identifier_errors
from internacia_builder.validate.output import emit_validation_result

app = typer.Typer(help="Validate internacia-db country data")

ALPHA2 = re.compile(r"^[A-Z]{2}$")
ALPHA3 = re.compile(r"^[A-Z]{3}$")
NUMERIC3 = re.compile(r"^\d{3}$")
ISO4217 = re.compile(r"^[A-Z]{3}$")
WIKIDATA = re.compile(r"^Q[1-9][0-9]*$")
DEFERRED_COUNTRY_IDS = frozenset()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> dict[str, Any]:
    return registry.load_yaml(path) or {}


def _messages(issues: list[dict[str, Any]], rel_path: str) -> list[str]:
    return [f"{rel_path}: {issue['suggested_action']}" for issue in issues]


def validate_schema(record: dict[str, Any], schema: dict[str, Any], rel_path: str) -> list[str]:
    return [
        f"{rel_path}: {issue['field']}: {issue['message']}"
        for issue in country_rules.check_country_schema(record, schema)
    ]


def validate_entity_status(record: dict[str, Any], rel_path: str) -> tuple[list[str], list[str]]:
    return _messages(country_rules.check_country_entity_status(record), rel_path), []


def validate_currency_codes(record: dict[str, Any], rel_path: str) -> list[str]:
    return _messages(country_rules.check_country_currency_codes(record), rel_path)


def validate_provenance_freshness(
    record: dict[str, Any],
    rel_path: str,
    *,
    max_age_months: int,
) -> list[str]:
    return _messages(
        country_rules.check_provenance_freshness(record, max_age_months=max_age_months),
        rel_path,
    )


def validate_official_iso_count(records: list[dict[str, Any]]) -> list[str]:
    return [
        f"entity policy: {issue['suggested_action']}"
        for issue in country_rules.validate_official_iso_count(records)
    ]


def check_duplicates(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    rel_paths = [rel for rel, _ in records]
    recs = [rec for _, rec in records]
    return [
        f"duplicate {issue['field']} '{issue['current_value']}' in {issue['file_path']} and {issue['other_path']}"
        for issue in country_rules.check_country_duplicates(recs, rel_paths)
    ]


def validate_borders(record: dict[str, Any], rel_path: str) -> list[str]:
    return _messages(country_rules.check_country_borders(record), rel_path)


def validate_indicator_years(record: dict[str, Any], rel_path: str) -> list[str]:
    return _messages(country_rules.check_country_indicator_years(record), rel_path)


def validate_completeness(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    report_fields: dict[str, Any] = {}
    n = len(records)
    if n == 0:
        return errors, warnings, {"row_count": 0, "fields": report_fields}

    fields_cfg = config.get("fields", {})
    for field, rules in fields_cfg.items():
        null_count = sum(1 for r in records if is_null_field(r, field))
        null_rate = null_count / n
        max_rate = float(rules.get("max_null_rate", 1.0))
        mode = rules.get("mode", "warn")
        report_fields[field] = {
            "null_count": null_count,
            "null_rate": round(null_rate, 4),
            "max_null_rate": max_rate,
            "mode": mode,
        }
        if null_rate > max_rate:
            msg = f"completeness: {field} null rate {null_rate:.2%} exceeds max {max_rate:.2%} ({null_count}/{n})"
            if mode == "error":
                errors.append(msg)
            else:
                warnings.append(msg)
    return errors, warnings, {"row_count": n, "fields": report_fields}


def validate_intblock_refs(
    countries_dir: Path,
    intblocks_dir: Path,
    config: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    mode = (config.get("unresolved_country_includes") or {}).get("mode", "warn")

    unresolved: dict[str, list[str]] = defaultdict(list)

    records, paths = [], []
    for yaml_path in sorted(intblocks_dir.rglob("*.yaml")):
        rel = str(yaml_path.relative_to(intblocks_dir.parent.parent))
        try:
            data = load_yaml(yaml_path)
        except yaml.YAMLError as exc:
            errors.append(f"{rel}: invalid intblock YAML: {exc}")
            continue
        records.append(data)
        paths.append(rel)
    for issue in cross_rules.validate_intblock_refs(countries_dir, records, paths, config):
        if issue["issue_type"] != "UNRESOLVED_COUNTRY_INCLUDE":
            errors.append(f"{issue['file_path']}: {issue['suggested_action']}")
        else:
            unresolved[issue["current_value"]].append(issue["file_path"])

    deferred = {k: v for k, v in unresolved.items() if k in DEFERRED_COUNTRY_IDS}
    other = {k: v for k, v in unresolved.items() if k not in DEFERRED_COUNTRY_IDS}

    for cid, sources in sorted(deferred.items()):
        warnings.append(
            f"cross-dataset (deferred policy): country include '{cid}' "
            f"unresolved in {len(sources)} file(s), e.g. {sources[0]}"
        )

    for cid, sources in sorted(other.items()):
        msg = f"cross-dataset: country include '{cid}' unresolved ({len(sources)} references, e.g. {sources[0]})"
        if mode == "error":
            errors.append(msg)
        else:
            warnings.append(msg)

    if deferred:
        warnings.append(f"cross-dataset summary: {len(deferred)} deferred id(s): " + ", ".join(sorted(deferred)))
    if other:
        warnings.append(f"cross-dataset summary: {len(other)} unexpected unresolved id(s)")

    return errors, warnings


@app.command()
def main(
    countries_dir: Path = typer.Option(
        None,
        "--countries-dir",
        help="Path to data/countries",
    ),
    fail_on_warning: bool = typer.Option(
        False,
        "--fail-on-warning",
        help="Treat warnings as errors, except the dated freshness warnings (age of last_verified "
        "and provenance dates), which only report",
    ),
    report: Path = typer.Option(
        None,
        "--report",
        help="Write JSON completeness and validation summary to this path",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit structured JSON result to stdout (for agents and automation)",
    ),
) -> None:
    """Run all country validation checks."""
    raise typer.Exit(
        run_validation(
            countries_dir=countries_dir,
            fail_on_warning=fail_on_warning,
            report=report,
            json_output=json_output,
        )
    )


def run_validation(
    countries_dir: Path | None = None,
    fail_on_warning: bool = False,
    report: Path | None = None,
    json_output: bool = False,
) -> int:
    """Run country validation; return process exit code (0 = success)."""
    root = project_root()
    countries_dir = countries_dir or root / "data" / "countries"
    intblocks_dir = root / "data" / "intblocks"
    ctx = registry.load_context(root, countries_dir=countries_dir, datasets=(registry.COUNTRIES,))
    completeness_cfg = ctx.countries_cfg
    if not ctx.countries.file_count:
        typer.echo(f"No YAML files in {countries_dir}", err=True)
        return 1

    errors: list[str] = [f"{rel}: {error}" for rel, error in ctx.countries.errors]
    warnings: list[str] = []
    all_records = ctx.countries.records

    # Dated warnings start firing as the calendar advances, so they report without failing
    # --fail-on-warning: a gate on them would turn CI red with no change to the data.
    rule_errors, rule_warnings, dated_warnings = registry.validator_messages(registry.COUNTRIES, ctx)
    errors.extend(rule_errors)
    warnings.extend(rule_warnings)

    comp_errors, comp_warnings, completeness_report = validate_completeness(all_records, completeness_cfg)
    errors.extend(comp_errors)
    warnings.extend(comp_warnings)

    if intblocks_dir.exists():
        xref_errors, xref_warnings = validate_intblock_refs(countries_dir, intblocks_dir, completeness_cfg)
        errors.extend(xref_errors)
        warnings.extend(xref_warnings)

    if countries_dir.resolve() == (root / "data" / "countries").resolve():
        aliases = load_yaml(root / "data" / "countries_aliases.yaml") if (root / "data" / "countries_aliases.yaml").exists() else []
        errors.extend(
            release_identifier_errors(
                root,
                "country",
                "data/countries",
                {str(record.get("code")) for record in all_records if record.get("code")},
                {str(a.get("alias")) for a in aliases or [] if isinstance(a, dict) and a.get("alias")},
                "data/countries_aliases.yaml",
            )
        )

    # Write the report only after every check (including cross-dataset
    # references) has contributed its findings.
    if report:
        summary = {
            "countries_validated": len(all_records),
            "error_count": len(errors),
            "warning_count": len(warnings) + len(dated_warnings),
            "errors": errors,
            "warnings": warnings + dated_warnings,
            "completeness": completeness_report,
        }
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation report: {report}")

    emit_validation_result(
        dataset="countries",
        validated=len(all_records),
        errors=errors,
        warnings=warnings + dated_warnings,
        json_output=json_output,
    )

    if errors or (fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    app()
