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

from internacia_builder import freshness
from internacia_builder.paths import project_root
from internacia_builder.validate import cross_rules, intblock_rules, registry
from internacia_builder.validate.completeness import (
    validate_completeness,
    validate_includes_status,
    validate_membership_applicability,
)
from internacia_builder.validate.identifiers import release_identifier_errors
from internacia_builder.validate.intblock_rules import TEMPLATED_DESC_RE as TEMPLATED_DESC
from internacia_builder.validate.output import emit_validation_result
from internacia_builder.validate.registry import (  # noqa: F401  (re-exported API)
    load_topic_aliases,
    load_topic_catalog,
    load_wikidata_exclusions,
)

app = typer.Typer(help="Validate internacia-db intblock data")

WIKIDATA = re.compile(r"^Q[1-9][0-9]*$")


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: Path) -> Any:
    return registry.load_yaml(path)


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


def validate_scope_category(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """Reject unknown categories, formal records without one, and non-formal IGOs."""
    return [f"{rel}: {issue['suggested_action']}" for rel, rec in records
            for issue in intblock_rules.check_intblock_scope_category(rec)
            if issue["issue_type"] != "SCOPE_CATEGORY_SEMANTIC_MISMATCH"]


def validate_scope_category_semantics(
    records: list[tuple[str, dict[str, Any]]],
) -> list[str]:
    """Reject blocktype/scope combinations with a known semantic contradiction."""
    return [f"{rel}: {issue['suggested_action']}" for rel, rec in records
            for issue in intblock_rules.check_intblock_scope_category(rec)
            if issue["issue_type"] == "SCOPE_CATEGORY_SEMANTIC_MISMATCH"]


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
        help="Treat warnings as errors, except the dated freshness warnings (age of last_verified "
        "and provenance dates), which only report",
    ),
    report: Path = typer.Option(
        None,
        "--report",
        help="Write JSON validation summary to this path",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit structured JSON result to stdout (for agents and automation)",
    ),
) -> None:
    """Run all intblock validation checks."""
    raise typer.Exit(
        run_validation(
            intblocks_dir=intblocks_dir,
            fail_on_warning=fail_on_warning,
            report=report,
            json_output=json_output,
        )
    )


def run_validation(
    intblocks_dir: Path | None = None,
    fail_on_warning: bool = False,
    report: Path | None = None,
    json_output: bool = False,
) -> int:
    """Run intblock validation; return process exit code (0 = success)."""
    root = project_root()
    ctx = registry.load_context(root, intblocks_dir=intblocks_dir)
    intblocks_dir = ctx.intblocks.directory
    completeness_cfg = ctx.intblocks_cfg
    if not ctx.intblocks.file_count:
        typer.echo(f"No YAML files in {intblocks_dir}", err=True)
        return 1

    errors: list[str] = [f"{rel}: {error}" for rel, error in ctx.intblocks.errors]
    warnings: list[str] = []
    all_records = ctx.intblocks.records
    records = list(zip(ctx.intblocks.paths, all_records, strict=True))

    # Dated warnings start firing as the calendar advances, so they report without failing
    # --fail-on-warning: a gate on them would turn CI red with no change to the data.
    rule_errors, rule_warnings, dated_warnings = registry.validator_messages(registry.INTBLOCKS, ctx)
    errors.extend(rule_errors)
    warnings.extend(rule_warnings)

    if intblocks_dir.resolve() == (root / "data" / "intblocks").resolve():
        errors.extend(
            f"data/watch/rosters.yaml: tier-1 id '{tier1_id}' is not an intblock"
            for tier1_id in freshness.load_tier1(root)
            if tier1_id not in ctx.intblock_ids
        )
        base_ref = freshness.comparison_base(root)
        if base_ref:
            errors.extend(
                freshness.check_changed_records(records, freshness.changed_base_records(root, base_ref), base_ref)
            )
        errors.extend(
            release_identifier_errors(
                root,
                "intblock",
                "data/intblocks",
                ctx.intblock_ids,
                ctx.alias_names,
                "data/intblocks_aliases.yaml",
            )
        )

    membership_errors, membership_warnings = validate_membership_applicability(records, completeness_cfg)
    errors.extend(membership_errors)
    warnings.extend(membership_warnings)

    status_errors, status_warnings = validate_includes_status(records, ctx.includes_status_catalog, completeness_cfg)
    errors.extend(status_errors)
    warnings.extend(status_warnings)

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
            "warning_count": len(warnings) + len(dated_warnings),
            "errors": errors,
            "warnings": warnings + dated_warnings,
            "completeness": completeness_report,
            "description_quality": description_report,
        }
        report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Wrote validation report: {report}")

    emit_validation_result(
        dataset="intblocks",
        validated=len(records),
        errors=errors,
        warnings=warnings + dated_warnings,
        json_output=json_output,
    )

    if errors or (fail_on_warning and warnings):
        return 1
    return 0


if __name__ == "__main__":
    app()
