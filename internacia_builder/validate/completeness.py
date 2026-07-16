"""Shared completeness and includes-participation validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PRIORITY_TO_LEVEL = {
    "high": "IMPORTANT",
    "medium": "MEDIUM",
    "low": "LOW",
}


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_null_intblock_field(record: dict[str, Any], field: str) -> bool:
    if field == "includes" and record.get("membership_applicability") == "not_applicable":
        return False
    if field not in record:
        return True
    val = record[field]
    return val is None or val == "" or val == [] or val == {}


def field_rule(config: dict[str, Any], field: str) -> dict[str, Any]:
    return (config.get("fields") or {}).get(field) or {}


def field_priority(config: dict[str, Any], field: str, default: str = "medium") -> str:
    return str(field_rule(config, field).get("priority") or default)


def priority_level(config: dict[str, Any], field: str, default: str = "medium") -> str:
    return PRIORITY_TO_LEVEL.get(field_priority(config, field, default), "MEDIUM")


def load_includes_status_catalog(schemas_dir: Path) -> dict[str, dict[str, Any]]:
    path = schemas_dir / "includes_status.yaml"
    if not path.exists():
        return {}
    data = load_yaml(path) or {}
    raw = data.get("statuses") or {}
    return {str(k): v for k, v in raw.items() if isinstance(v, dict)}


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
        null_count = sum(1 for r in records if is_null_intblock_field(r, field))
        null_rate = null_count / n
        max_rate = float(rules.get("max_null_rate", 1.0))
        mode = rules.get("mode", "warn")
        report_fields[field] = {
            "null_count": null_count,
            "null_rate": round(null_rate, 4),
            "max_null_rate": max_rate,
            "mode": mode,
            "priority": rules.get("priority"),
            "requirement": rules.get("requirement"),
        }
        if null_rate > max_rate:
            msg = f"completeness: {field} null rate {null_rate:.2%} exceeds max {max_rate:.2%} ({null_count}/{n})"
            if mode == "error":
                errors.append(msg)
            else:
                warnings.append(msg)
    return errors, warnings, {"row_count": n, "fields": report_fields}


def validate_record_field_completeness(
    record: dict[str, Any], config: dict[str, Any]
) -> list[dict[str, Any]]:
    """Per-record missing-field issues for analyze-quality."""
    issues: list[dict[str, Any]] = []
    for field, rules in (config.get("fields") or {}).items():
        if not is_null_intblock_field(record, field):
            continue
        requirement = rules.get("requirement", "preferred")
        issue_type = "MISSING_MANDATORY_FIELD" if requirement == "mandatory" else "MISSING_PREFERRED_FIELD"
        issues.append({
            "issue_type": issue_type,
            "field": field,
            "current_value": None,
            "suggested_action": f"Populate {field} ({requirement})",
            "priority": PRIORITY_TO_LEVEL.get(str(rules.get("priority") or "medium"), "MEDIUM"),
        })
    return issues


def validate_membership_applicability(
    records: list[tuple[str, dict[str, Any]]], config: dict[str, Any]
) -> tuple[list[str], list[str]]:
    rule = (config.get("includes") or {}).get("membership_applicability") or {}
    if not rule.get("require_marker_when_empty"):
        return [], []

    mode = rule.get("mode", "warn")
    errors: list[str] = []
    warnings: list[str] = []
    for rel, rec in records:
        if not is_null_intblock_field(rec, "includes"):
            continue
        if rec.get("membership_applicability") == "not_applicable":
            continue
        msg = (
            f"{rel}: missing includes; set membership_applicability: not_applicable "
            "when membership is intentionally absent, or populate includes"
        )
        if mode == "error":
            errors.append(msg)
        else:
            warnings.append(msg)
    return errors, warnings


def validate_includes_status(
    records: list[tuple[str, dict[str, Any]]],
    catalog: dict[str, dict[str, Any]],
    config: dict[str, Any],
) -> tuple[list[str], list[str]]:
    rule = (config.get("includes") or {}).get("status") or {}
    if not catalog or not rule:
        return [], []

    allowed = set(catalog)
    mode = rule.get("mode", "error")
    errors: list[str] = []
    warnings: list[str] = []

    for rel, rec in records:
        for idx, inc in enumerate(rec.get("includes") or []):
            if not isinstance(inc, dict):
                continue
            status = inc.get("status")
            if status is None or status == "":
                msg = f"{rel}: includes[{idx}] missing status (see data/schemas/includes_status.yaml)"
                (errors if mode == "error" else warnings).append(msg)
                continue
            if str(status) not in allowed:
                msg = (
                    f"{rel}: includes[{idx}] has unknown status '{status}' "
                    f"(allowed: {sorted(allowed)})"
                )
                (errors if mode == "error" else warnings).append(msg)
    return errors, warnings
