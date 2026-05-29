#!/usr/bin/env python3
"""Validate country YAML sources, completeness, and intblock cross-references."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import jsonschema
import typer
import yaml

app = typer.Typer(help="Validate internacia-db country data")

ALPHA2 = re.compile(r"^[A-Z]{2}$")
ALPHA3 = re.compile(r"^[A-Z]{3}$")
NUMERIC3 = re.compile(r"^\d{3}$")
WIKIDATA = re.compile(r"^Q[1-9][0-9]*$")
DEFERRED_COUNTRY_IDS = frozenset({"XA", "XS", "XT", "XN"})
NON_ISO_ALPHA2 = frozenset({"AN", "JG", "KV"})

ENTITY_TYPES = frozenset({
    "sovereign_state",
    "dependent_territory",
    "special_administrative_region",
    "disputed_territory",
    "historical_entity",
    "supranational_grouping",
    "statistical_area",
})

CODE_STATUSES = frozenset({
    "official_iso3166_1",
    "user_assigned",
    "obsolete",
    "exceptionally_reserved",
})

EXPECTED_OFFICIAL_ISO_COUNT = 249


def project_root() -> Path:
    return Path(__file__).parent.parent


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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


def validate_schema(
    record: dict[str, Any], schema: dict[str, Any], rel_path: str
) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(record), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{rel_path}: {path}: {err.message}")
    return errors


def validate_entity_status(
    record: dict[str, Any], rel_path: str
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    code = str(record.get("code", ""))
    entity_type = record.get("entity_type")
    code_status = record.get("code_status")

    if not entity_type:
        errors.append(f"{rel_path}: missing entity_type")
    elif entity_type not in ENTITY_TYPES:
        errors.append(f"{rel_path}: invalid entity_type '{entity_type}'")

    if not code_status:
        errors.append(f"{rel_path}: missing code_status")
    elif code_status not in CODE_STATUSES:
        errors.append(f"{rel_path}: invalid code_status '{code_status}'")

    if code in NON_ISO_ALPHA2:
        if code_status == "official_iso3166_1":
            errors.append(
                f"{rel_path}: non-ISO code '{code}' must not have code_status official_iso3166_1"
            )
    elif code_status != "official_iso3166_1":
        errors.append(
            f"{rel_path}: ISO-style code '{code}' must have code_status official_iso3166_1"
        )

    return errors, warnings


def validate_official_iso_count(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    count = sum(
        1 for r in records if r.get("code_status") == "official_iso3166_1"
    )
    if count != EXPECTED_OFFICIAL_ISO_COUNT:
        errors.append(
            f"entity policy: expected {EXPECTED_OFFICIAL_ISO_COUNT} "
            f"official_iso3166_1 records, found {count}"
        )
    return errors


def check_duplicates(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    by_code: dict[str, str] = {}
    by_iso3: dict[str, str] = {}
    by_numeric: dict[str, str] = {}

    for rel, rec in records:
        for field, mapping in (
            ("code", by_code),
            ("iso3code", by_iso3),
            ("numeric_code", by_numeric),
        ):
            val = str(rec.get(field, ""))
            if not val:
                continue
            if val in mapping and mapping[val] != rel:
                errors.append(
                    f"duplicate {field} '{val}' in {rel} and {mapping[val]}"
                )
            else:
                mapping[val] = rel
    return errors


def validate_borders(record: dict[str, Any], rel_path: str) -> list[str]:
    errors: list[str] = []
    borders = record.get("borders")
    if borders is None:
        return errors
    if not isinstance(borders, list):
        errors.append(f"{rel_path}: borders must be a list")
        return errors
    for b in borders:
        if not isinstance(b, str) or not ALPHA3.match(b):
            errors.append(f"{rel_path}: border '{b}' must be ISO alpha-3 uppercase")
    return errors


def audit_whitespace(record: dict[str, Any], rel_path: str) -> list[str]:
    warnings: list[str] = []
    sub = record.get("subregion")
    if isinstance(sub, str) and sub != sub.strip():
        warnings.append(f"{rel_path}: subregion has leading/trailing whitespace")
    for key in ("region", "adminregion"):
        obj = record.get(key)
        if isinstance(obj, dict):
            val = obj.get("value")
            if isinstance(val, str) and val != val.strip():
                warnings.append(f"{rel_path}: {key}.value has leading/trailing whitespace")
    return warnings


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
            msg = (
                f"completeness: {field} null rate {null_rate:.2%} "
                f"exceeds max {max_rate:.2%} ({null_count}/{n})"
            )
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
    allowlist = set(config.get("special_entity_allowlist") or [])
    mode = (config.get("unresolved_country_includes") or {}).get("mode", "warn")

    unresolved: dict[str, list[str]] = defaultdict(list)

    for yaml_path in sorted(intblocks_dir.rglob("*.yaml")):
        data = load_yaml(yaml_path)
        rel = str(yaml_path.relative_to(intblocks_dir.parent.parent))
        for inc in data.get("includes") or []:
            if not isinstance(inc, dict):
                continue
            if inc.get("type") != "country":
                continue
            raw_id = inc.get("id", "")
            if isinstance(raw_id, bool):
                continue
            cid = str(raw_id).strip()
            if not ALPHA2.match(cid):
                continue
            country_file = countries_dir / f"{cid}.yaml"
            if country_file.exists():
                continue
            if cid in allowlist:
                continue
            unresolved[cid].append(rel)

    deferred = {k: v for k, v in unresolved.items() if k in DEFERRED_COUNTRY_IDS}
    other = {k: v for k, v in unresolved.items() if k not in DEFERRED_COUNTRY_IDS}

    for cid, sources in sorted(deferred.items()):
        warnings.append(
            f"cross-dataset (deferred policy): country include '{cid}' "
            f"unresolved in {len(sources)} file(s), e.g. {sources[0]}"
        )

    for cid, sources in sorted(other.items()):
        msg = (
            f"cross-dataset: country include '{cid}' unresolved "
            f"({len(sources)} references, e.g. {sources[0]})"
        )
        if mode == "error":
            errors.append(msg)
        else:
            warnings.append(msg)

    if deferred:
        warnings.append(
            f"cross-dataset summary: {len(deferred)} deferred id(s): "
            + ", ".join(sorted(deferred))
        )
    if other:
        warnings.append(
            f"cross-dataset summary: {len(other)} unexpected unresolved id(s)"
        )

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
        help="Treat warnings as errors",
    ),
    report: Path = typer.Option(
        None,
        "--report",
        help="Write JSON completeness and validation summary to this path",
    ),
) -> None:
    """Run all country validation checks."""
    root = project_root()
    countries_dir = countries_dir or root / "data" / "countries"
    intblocks_dir = root / "data" / "intblocks"
    schema_path = root / "data" / "schemas" / "countries.schema.json"
    completeness_path = root / "data" / "schemas" / "countries_completeness.yaml"

    schema = load_json(schema_path)
    completeness_cfg = load_yaml(completeness_path)

    errors: list[str] = []
    warnings: list[str] = []
    records: list[tuple[str, dict[str, Any]]] = []
    all_records: list[dict[str, Any]] = []

    yaml_files = sorted(countries_dir.glob("*.yaml"))
    if not yaml_files:
        typer.echo(f"No YAML files in {countries_dir}", err=True)
        raise typer.Exit(1)

    for path in yaml_files:
        rel = str(path.relative_to(root))
        try:
            record = load_yaml(path)
        except yaml.YAMLError as e:
            errors.append(f"{rel}: YAML parse error: {e}")
            continue
        records.append((rel, record))
        all_records.append(record)
        errors.extend(validate_schema(record, schema, rel))
        errors.extend(validate_borders(record, rel))
        warnings.extend(audit_whitespace(record, rel))
        ent_errors, ent_warnings = validate_entity_status(record, rel)
        errors.extend(ent_errors)
        warnings.extend(ent_warnings)

    errors.extend(check_duplicates(records))
    errors.extend(validate_official_iso_count(all_records))

    comp_errors, comp_warnings, completeness_report = validate_completeness(
        all_records, completeness_cfg
    )
    errors.extend(comp_errors)
    warnings.extend(comp_warnings)

    if report:
        summary = {
            "countries_validated": len(records),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "completeness": completeness_report,
        }
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation report: {report}")

    if intblocks_dir.exists():
        xref_errors, xref_warnings = validate_intblock_refs(
            countries_dir, intblocks_dir, completeness_cfg
        )
        errors.extend(xref_errors)
        warnings.extend(xref_warnings)

    for w in warnings:
        typer.echo(f"WARN: {w}", err=True)
    for e in errors:
        typer.echo(f"ERROR: {e}", err=True)

    typer.echo(
        f"Validated {len(records)} countries: "
        f"{len(errors)} error(s), {len(warnings)} warning(s)"
    )

    if errors or (fail_on_warning and warnings):
        raise typer.Exit(1)
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
