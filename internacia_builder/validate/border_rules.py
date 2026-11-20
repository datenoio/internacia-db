"""Validation of land-border crossing status (``data/borders/border_status.yaml``).

The file is an edge dataset over ``countries.borders``: each entry names a sorted pair of
``iso3code`` values, a status and a period. These cross-record rules check the JSON Schema,
that both countries exist and border each other, and that a pair's periods do not conflict.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import jsonschema

BORDER_STATUS_FILE = "data/borders/border_status.yaml"


def _issue(issue_type: str, field: str, value: str, action: str) -> dict[str, Any]:
    return {
        "issue_type": issue_type,
        "file_path": BORDER_STATUS_FILE,
        "record_id": "border_status",
        "field": field,
        "current_value": value,
        "suggested_action": action,
    }


def _start(value: str | None) -> str:
    """Comparable period start."""
    if not value:
        return "0000-00-00"
    parts = str(value).split("-")
    return "-".join(parts + ["01"] * (3 - len(parts)))


def _end(value: str | None) -> str:
    """Comparable period end: missing means still current."""
    if not value:
        return "9999-99-99"
    parts = str(value).split("-")
    return "-".join(parts + (["12", "31"] if len(parts) == 1 else ["31"])[: 3 - len(parts)])


def border_status_entries(document: Any) -> list[dict[str, Any]]:
    """The ``entries`` list of the source document, or [] when absent or malformed."""
    if not isinstance(document, dict):
        return []
    return [e for e in document.get("entries") or [] if isinstance(e, dict)]


def check_border_status(
    document: Any, schema: dict[str, Any], countries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Schema, pair resolution, adjacency and period rules for border status entries."""
    if document is None:
        return []
    issues: list[dict[str, Any]] = []
    if schema:
        validator = jsonschema.validators.validator_for(schema)(schema)
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
            path = ".".join(str(p) for p in error.path) or "(root)"
            issues.append(_issue("SCHEMA_ERROR", path, "", error.message))
        if issues:
            return issues

    borders = {str(c.get("iso3code")): {str(b) for b in c.get("borders") or []} for c in countries if c.get("iso3code")}
    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for index, entry in enumerate(border_status_entries(document)):
        pair = [str(code) for code in entry.get("countries") or []]
        label = "-".join(pair)
        field = f"entries[{index}].countries"
        if len(pair) != 2 or pair[0] == pair[1] or pair != sorted(pair) or any(code not in borders for code in pair):
            issues.append(_issue(
                "UNRESOLVED_BORDER_STATUS_PAIR", field, label,
                "use two different existing iso3code values in sorted order",
            ))
            continue
        a, b = pair
        if b not in borders[a] or a not in borders[b]:
            issues.append(_issue(
                "BORDER_STATUS_NOT_ADJACENT", field, label,
                f"{a} and {b} must list each other in borders",
            ))
        since, until = entry.get("since"), entry.get("until")
        if until and not since:
            issues.append(_issue(
                "BORDER_STATUS_PERIOD_CONFLICT", f"entries[{index}].until", label,
                "an ended period needs a since date",
            ))
        if since and until and _start(since) > _end(until):
            issues.append(_issue(
                "BORDER_STATUS_PERIOD_CONFLICT", f"entries[{index}].since", label,
                f"since {since} is after until {until}",
            ))
        by_pair.setdefault((a, b), []).append(entry)

    for (a, b), entries in sorted(by_pair.items()):
        if len(entries) > 1:
            issues.append(_issue(
                "BORDER_STATUS_PERIOD_CONFLICT", "entries", f"{a}-{b}",
                "a border has one entry; when it closes again after reopening, replace the ended entry",
            ))
    return issues


def check_border_status_freshness(document: Any, max_age_months: int) -> list[dict[str, Any]]:
    """Warn when an entry's last_verified date is older than the freshness threshold."""
    if not max_age_months:
        return []
    today = date.today()
    issues: list[dict[str, Any]] = []
    for index, entry in enumerate(border_status_entries(document)):
        try:
            year, month, day = (int(p) for p in str(entry.get("last_verified") or "").split("-"))
            checked = date(year, month, day)
        except ValueError:
            continue
        age = (today.year - checked.year) * 12 + (today.month - checked.month)
        if age > max_age_months:
            issues.append(_issue(
                "STALE_BORDER_STATUS", f"entries[{index}].last_verified", str(entry.get("last_verified")),
                f"re-check the entry: last verified more than {max_age_months} months ago",
            ))
    return issues
