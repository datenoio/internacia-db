"""Tests for validation JSON output formatting."""

import json

from internacia_builder.validate.output import (
    emit_validation_result,
    format_issues,
    lookup_fix_hint,
    parse_cli_message,
)


def test_parse_cli_message_splits_file_and_message():
    issue = parse_cli_message("data/countries/US.yaml: invalid field", severity="error")
    assert issue["file"] == "data/countries/US.yaml"
    assert issue["message"] == "invalid field"
    assert issue["severity"] == "error"


def test_parse_cli_message_without_file():
    issue = parse_cli_message("duplicate code 'AA'", severity="error")
    assert issue["file"] is None
    assert issue["message"] == "duplicate code 'AA'"


def test_lookup_fix_hint_borders():
    hint = lookup_fix_hint("borders must be a list of alpha-3 country codes")
    assert hint is not None
    assert "alpha-3" in hint


def test_format_issues_adds_fix_hint():
    issues = format_issues(
        ["data/intblocks/foo.yaml: missing includes; set membership_applicability: not_applicable"],
        "warning",
    )
    assert issues[0]["severity"] == "warning"
    assert "fix_hint" in issues[0]


def test_emit_validation_result_json(capsys):
    emit_validation_result(
        dataset="countries",
        validated=2,
        errors=["a.yaml: bad"],
        warnings=[],
        json_output=True,
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset"] == "countries"
    assert payload["validated"] == 2
    assert payload["error_count"] == 1
    assert payload["ok"] is False
    assert payload["errors"][0]["file"] == "a.yaml"
