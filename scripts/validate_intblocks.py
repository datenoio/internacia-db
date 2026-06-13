#!/usr/bin/env python3
"""Validate intblock YAML sources: schema, taxonomy, references, completeness."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import typer
import yaml

app = typer.Typer(help="Validate internacia-db intblock data")

WIKIDATA = re.compile(r"^Q[1-9][0-9]*$")


def project_root() -> Path:
    return Path(__file__).parent.parent


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_null_field(record: dict[str, Any], field: str) -> bool:
    if field not in record:
        return True
    val = record[field]
    return val is None or val == "" or val == [] or val == {}


def validate_schema(record: dict[str, Any], schema: dict[str, Any], rel_path: str) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(record), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{rel_path}: {path}: {err.message}")
    return errors


def check_duplicate_ids(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for rel, rec in records:
        rid = str(rec.get("id", ""))
        if not rid:
            continue
        if rid in seen and seen[rid] != rel:
            errors.append(f"duplicate id '{rid}' in {rel} and {seen[rid]}")
        else:
            seen[rid] = rel
    return errors


def validate_blocktypes(records: list[tuple[str, dict[str, Any]]], taxonomy: set[str]) -> list[str]:
    """Every blocktype value must exist in the blocktypes taxonomy."""
    errors: list[str] = []
    for rel, rec in records:
        for bt in rec.get("blocktype") or []:
            if str(bt) not in taxonomy:
                errors.append(f"{rel}: unknown blocktype '{bt}'")
    return errors


def validate_partof_refs(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """partof references should resolve to existing intblock ids (warn-only)."""
    warnings: list[str] = []
    known_ids = {str(rec.get("id", "")) for _, rec in records}
    for rel, rec in records:
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
                warnings.append(f"{rel}: partof '{ref}' does not match any intblock id")
    return warnings


def validate_lifecycle(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """Historical entities must use the standard dissolved field, not ad-hoc keys."""
    warnings: list[str] = []
    for rel, rec in records:
        if "ended" in rec:
            warnings.append(f"{rel}: uses non-standard 'ended'; use 'dissolved'")
        if rec.get("dissolved") and rec.get("status") not in ("historical", None):
            warnings.append(f"{rel}: has dissolved date but status is '{rec.get('status')}', expected 'historical'")
    return warnings


def validate_aliases(
    aliases: list[dict[str, Any]],
    known_ids: set[str],
) -> list[str]:
    """Alias integrity: every target must resolve to an existing intblock id, and
    an alias that collides with a current id must be marked ``disambiguated``."""
    errors: list[str] = []
    seen_aliases: set[str] = set()
    for entry in aliases:
        if not isinstance(entry, dict):
            errors.append(f"alias entry is not a mapping: {entry!r}")
            continue
        alias = str(entry.get("alias") or "")
        target = str(entry.get("target") or "")
        reason = str(entry.get("reason") or "")
        if not alias or not target:
            errors.append(f"alias entry missing alias/target: {entry!r}")
            continue
        if alias in seen_aliases:
            errors.append(f"duplicate alias '{alias}'")
        seen_aliases.add(alias)
        if reason not in {"renamed", "merged", "disambiguated"}:
            errors.append(f"alias '{alias}': invalid reason '{reason}'")
        if target not in known_ids:
            errors.append(f"alias '{alias}': target '{target}' does not match any intblock id")
        if alias in known_ids and reason != "disambiguated":
            errors.append(
                f"alias '{alias}' collides with a current intblock id; "
                f"mark reason 'disambiguated' if the acronym was reassigned"
            )
    return errors


def validate_completeness(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    report_fields: dict[str, Any] = {}
    n = len(records)
    if n == 0:
        return errors, warnings, {"row_count": 0, "fields": report_fields}

    for field, rules in (config.get("fields") or {}).items():
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
    root = project_root()
    intblocks_dir = intblocks_dir or root / "data" / "intblocks"
    schema_path = root / "data" / "schemas" / "intblocks.schema.json"
    completeness_path = root / "data" / "schemas" / "intblocks_completeness.yaml"
    blocktypes_path = root / "data" / "datasets" / "blocktypes.yaml"
    aliases_path = root / "data" / "intblocks_aliases.yaml"

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
        raise typer.Exit(1)

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
    if taxonomy:
        errors.extend(validate_blocktypes(records, taxonomy))
    warnings.extend(validate_partof_refs(records))
    warnings.extend(validate_lifecycle(records))

    if aliases_path.exists():
        known_ids = {str(rec.get("id", "")) for _, rec in records if rec.get("id")}
        aliases = load_yaml(aliases_path) or []
        errors.extend(validate_aliases(aliases, known_ids))

    all_records = [rec for _, rec in records]
    comp_errors, comp_warnings, completeness_report = validate_completeness(all_records, completeness_cfg)
    errors.extend(comp_errors)
    warnings.extend(comp_warnings)

    if report:
        summary = {
            "intblocks_validated": len(records),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "completeness": completeness_report,
        }
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation report: {report}")

    for w in warnings:
        typer.echo(f"WARN: {w}", err=True)
    for e in errors:
        typer.echo(f"ERROR: {e}", err=True)

    typer.echo(f"Validated {len(records)} intblocks: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (fail_on_warning and warnings):
        raise typer.Exit(1)
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
