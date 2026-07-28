"""Validation result formatting for CLI and agent consumption."""

from __future__ import annotations

import json
from typing import Any

import typer

# Substring → fix hint for common agent/contributor mistakes.
FIX_HINTS: tuple[tuple[str, str], ...] = (
    (
        "borders must be a list of alpha-3",
        "Use ISO alpha-3 codes in borders (e.g. CAN, MEX), not alpha-2. See docs/ai-consumers.md.",
    ),
    (
        "missing includes; set membership_applicability",
        "Set membership_applicability: not_applicable or populate includes. "
        "See docs/agents/contribute.md.",
    ),
    (
        "population.year must not be 0",
        "Use year: null when the source year is unknown; never year: 0.",
    ),
    (
        "unknown blocktype",
        "Add the blocktype to data/blocktypes/blocktypes.yaml first, then re-validate.",
    ),
    (
        "filename must match record id",
        "Rename the YAML file so its stem matches the record id exactly (case-sensitive).",
    ),
    (
        "must not have code_status official_iso3166_1",
        "Non-ISO codes need code_status user_assigned or obsolete. See docs/country-code-policy.md.",
    ),
    (
        "must have code_status official_iso3166_1",
        "Standard ISO alpha-2 codes require code_status: official_iso3166_1.",
    ),
)


def lookup_fix_hint(message: str) -> str | None:
    for pattern, hint in FIX_HINTS:
        if pattern in message:
            return hint
    return None


def parse_cli_message(msg: str, *, severity: str) -> dict[str, Any]:
    file_path: str | None = None
    message = msg
    if ": " in msg:
        file_path, message = msg.split(": ", 1)
    issue: dict[str, Any] = {
        "file": file_path,
        "message": message,
        "severity": severity,
    }
    hint = lookup_fix_hint(message)
    if hint:
        issue["fix_hint"] = hint
    return issue


def format_issues(messages: list[str], severity: str) -> list[dict[str, Any]]:
    return [parse_cli_message(msg, severity=severity) for msg in messages]


def emit_validation_result(
    *,
    dataset: str,
    validated: int,
    errors: list[str],
    warnings: list[str],
    json_output: bool,
) -> None:
    if json_output:
        payload = {
            "dataset": dataset,
            "validated": validated,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "ok": len(errors) == 0,
            "errors": format_issues(errors, "error"),
            "warnings": format_issues(warnings, "warning"),
        }
        typer.echo(json.dumps(payload, indent=2))
        return

    for warning in warnings:
        typer.echo(f"WARN: {warning}", err=True)
    for error in errors:
        typer.echo(f"ERROR: {error}", err=True)
    typer.echo(f"Validated {validated} {dataset}: {len(errors)} error(s), {len(warnings)} warning(s)")
