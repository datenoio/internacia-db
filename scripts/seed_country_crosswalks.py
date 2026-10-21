#!/usr/bin/env python3
"""Validate and apply curated country crosswalk identifiers.

The curated CSV is the only value source. Source metadata is stored separately and
is copied into field-level provenance entries. The command is read-only by default.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = ROOT / "data" / "countries"
SEED = ROOT / "data" / "schemas" / "country_crosswalk_seed.csv"
SOURCES = ROOT / "data" / "schemas" / "country_crosswalk_sources.yaml"
POLICY = ROOT / "data" / "schemas" / "country_crosswalk_exclusions.yaml"
FIELDS = ("geonames_id", "ioc_code", "fifa_code", "fips_code")
FIELD_PATTERNS = {
    "geonames_id": re.compile(r"^[1-9][0-9]*$"),
    "ioc_code": re.compile(r"^[A-Z]{3}$"),
    "fifa_code": re.compile(r"^[A-Z]{3}$"),
    "fips_code": re.compile(r"^[A-Z]{2}$"),
}


class SeedValidationError(ValueError):
    """Raised when curated seed or source metadata is internally inconsistent."""


def load_seed(path: Path = SEED) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise SeedValidationError(f"curated seed does not exist: {path}")
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expected = ["code", *FIELDS]
        if reader.fieldnames != expected:
            raise SeedValidationError(
                f"seed columns must be {expected}, got {reader.fieldnames}"
            )
        rows: dict[str, dict[str, str]] = {}
        for line_no, row in enumerate(reader, start=2):
            code = (row.get("code") or "").strip().upper()
            if not re.fullmatch(r"[A-Z]{2}", code):
                raise SeedValidationError(f"line {line_no}: invalid country code {code!r}")
            if code in rows:
                raise SeedValidationError(f"line {line_no}: duplicate country code {code}")
            rows[code] = {field: (row.get(field) or "").strip() for field in FIELDS}
    validate_seed_values(rows)
    return rows


def validate_seed_values(rows: dict[str, dict[str, str]]) -> None:
    for field in FIELDS:
        seen: dict[str, str] = {}
        for code, row in rows.items():
            value = row.get(field, "")
            if not value:
                continue
            if not FIELD_PATTERNS[field].fullmatch(value):
                raise SeedValidationError(f"{code}: invalid {field} value {value!r}")
            if value in seen:
                raise SeedValidationError(
                    f"duplicate {field} value {value!r} for {seen[value]} and {code}"
                )
            seen[value] = code


def load_sources(path: Path = SOURCES) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise SeedValidationError(f"source metadata does not exist: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    retrieved_default = str(payload.get("retrieved_at") or "")
    sources = payload.get("fields") or {}
    result: dict[str, dict[str, str]] = {}
    for field in FIELDS:
        raw = sources.get(field) or {}
        source = str(raw.get("source") or "")
        url = str(raw.get("url") or "")
        retrieved_at = str(raw.get("retrieved_at") or retrieved_default)
        if not source or not url or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", retrieved_at):
            raise SeedValidationError(
                f"{field}: source, url and ISO retrieved_at are required"
            )
        result[field] = {
            "source": source,
            "url": url,
            "retrieved_at": retrieved_at,
            "license": str(raw.get("license") or ""),
        }
    return result


def load_policy(path: Path = POLICY) -> dict[str, Any]:
    if not path.exists():
        raise SeedValidationError(f"crosswalk policy does not exist: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def insert_or_replace_field(text: str, field: str, value: str, *, overwrite: bool) -> str:
    pattern = re.compile(rf"^{re.escape(field)}:\s*.*$", re.M)
    if pattern.search(text):
        if not overwrite:
            return text
        return pattern.sub(f"{field}: {yaml_scalar(value)}", text, count=1)

    lines = text.splitlines(keepends=True)
    anchors = [*FIELDS, "wikidata_id", "numeric_code", "iso3code"]
    insert_at = None
    for anchor in anchors:
        for idx, line in enumerate(lines):
            if re.match(rf"^{re.escape(anchor)}:\s*", line):
                insert_at = idx + 1
        if insert_at is not None:
            break
    rendered = f"{field}: {yaml_scalar(value)}\n"
    if insert_at is None:
        lines.insert(0, rendered)
    else:
        lines.insert(insert_at, rendered)
    return "".join(lines)


def provenance_fields(record: dict[str, Any]) -> set[str]:
    return {
        str(entry.get("field"))
        for entry in (record.get("provenance") or [])
        if isinstance(entry, dict) and entry.get("field")
    }


def render_provenance(field: str, source: dict[str, str]) -> str:
    fragment = (
        f"- field: {field}\n"
        f"  source: {yaml_scalar(source['source'])}\n"
        f"  url: {yaml_scalar(source['url'])}\n"
        f"  retrieved_at: {yaml_scalar(source['retrieved_at'])}\n"
    )
    if source.get("license"):
        fragment += f"  license: {yaml_scalar(source['license'])}\n"
    return fragment


def insert_provenance(
    text: str,
    field: str,
    source: dict[str, str],
    *,
    refresh: bool = False,
) -> str:
    record = yaml.safe_load(text) or {}
    if field in provenance_fields(record):
        if not refresh:
            return text
        pattern = re.compile(
            rf"^- field:\s*{re.escape(field)}\s*\n(?:^  .*\n)*",
            re.M,
        )
        if not pattern.search(text):
            raise SeedValidationError(
                f"cannot surgically refresh non-standard provenance block for {field}"
            )
        return pattern.sub(render_provenance(field, source), text, count=1)

    fragment = render_provenance(field, source)

    match = re.search(r"^provenance:\s*$", text, re.M)
    if not match:
        separator = "" if text.endswith("\n") else "\n"
        return f"{text}{separator}provenance:\n{fragment}"

    next_key = re.search(r"^[A-Za-z_][A-Za-z0-9_]*:\s*", text[match.end():], re.M)
    if next_key:
        insert_at = match.end() + next_key.start()
        return text[:insert_at] + fragment + text[insert_at:]
    separator = "" if text.endswith("\n") else "\n"
    return f"{text}{separator}{fragment}"


def reconcile_text(
    text: str,
    seed: dict[str, str],
    sources: dict[str, dict[str, str]],
    selected_fields: tuple[str, ...],
    *,
    allow_overwrite: bool = False,
    existing_only: bool = False,
    refresh_provenance: bool = False,
) -> tuple[str, list[dict[str, str]], list[dict[str, str]]]:
    original_record = yaml.safe_load(text) or {}
    original_provenance_fields = provenance_fields(original_record)
    updated = text
    actions: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []

    for field in selected_fields:
        target = seed.get(field, "")
        current = str(original_record.get(field) or "")
        if existing_only and not current:
            continue
        if not target:
            if current:
                conflicts.append({
                    "field": field,
                    "current": current,
                    "target": "",
                    "reason": "current value is absent from curated seed",
                })
            continue
        if current and current != target and not allow_overwrite:
            conflicts.append({
                "field": field,
                "current": current,
                "target": target,
                "reason": "current value differs from curated seed",
            })
            continue

        if not current:
            updated = insert_or_replace_field(updated, field, target, overwrite=False)
            actions.append({"field": field, "action": "added", "value": target})
        elif current != target:
            updated = insert_or_replace_field(updated, field, target, overwrite=True)
            actions.append({"field": field, "action": "updated", "value": target})

        before = updated
        updated = insert_provenance(
            updated,
            field,
            sources[field],
            refresh=refresh_provenance,
        )
        if updated != before:
            action = (
                "provenance_refreshed"
                if field in original_provenance_fields
                else "provenance_added"
            )
            actions.append({"field": field, "action": action, "value": target})

    return updated, actions, conflicts


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report required changes; default")
    mode.add_argument("--dry-run", action="store_true", help="show planned changes without writing")
    mode.add_argument("--apply", action="store_true", help="write validated changes")
    parser.add_argument("--allow-overwrite", action="store_true", help="accept curated values for conflicts")
    parser.add_argument(
        "--existing-only",
        action="store_true",
        help="repair provenance and conflicts only for already populated fields",
    )
    parser.add_argument(
        "--refresh-provenance",
        action="store_true",
        help="replace existing crosswalk provenance with current source metadata",
    )
    parser.add_argument("--field", action="append", choices=FIELDS, dest="fields")
    parser.add_argument("--report-json", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.allow_overwrite and not args.apply:
        raise SeedValidationError("--allow-overwrite requires --apply")

    selected_fields = tuple(args.fields or FIELDS)
    seed = load_seed()
    sources = load_sources()
    policy = load_policy()
    country_paths = {path.stem: path for path in sorted(COUNTRIES.glob("*.yaml"))}
    unknown = sorted(set(seed) - set(country_paths))
    missing = sorted(set(country_paths) - set(seed))
    if unknown or missing:
        raise SeedValidationError(
            f"seed/country code mismatch: unknown={unknown}, missing={missing}"
        )

    planned: list[tuple[Path, str]] = []
    report: dict[str, Any] = {
        "mode": "apply" if args.apply else "dry-run" if args.dry_run else "check",
        "fields": list(selected_fields),
        "actions": [],
        "conflicts": [],
        "unresolved": [],
        "summary": {},
    }
    summary: Counter[str] = Counter()
    for code, path in country_paths.items():
        text = path.read_text(encoding="utf-8")
        record = yaml.safe_load(text) or {}
        for field in selected_fields:
            current = str(record.get(field) or "")
            target = seed[code].get(field, "")
            if args.existing_only and not current:
                continue
            if target:
                if current == target:
                    summary["unchanged"] += 1
                elif current and args.allow_overwrite:
                    summary["updated"] += 1
                elif current:
                    summary["conflicts"] += 1
                else:
                    summary["added"] += 1
            elif current:
                summary["conflicts"] += 1
            else:
                exclusions = (
                    ((policy.get("fields") or {}).get(field) or {}).get("exclusions")
                    or {}
                )
                if code in exclusions:
                    summary["not_applicable"] += 1
                else:
                    summary["unresolved"] += 1
                    report["unresolved"].append({"code": code, "field": field})
        updated, actions, conflicts = reconcile_text(
            text,
            seed[code],
            sources,
            selected_fields,
            allow_overwrite=args.allow_overwrite,
            existing_only=args.existing_only,
            refresh_provenance=args.refresh_provenance,
        )
        for item in actions:
            report["actions"].append({"code": code, **item})
        for item in conflicts:
            report["conflicts"].append({"code": code, **item})
        if updated != text:
            planned.append((path, updated))

    report["summary"] = dict(sorted(summary.items()))
    print(f"summary={report['summary']}")
    if report["unresolved"]:
        for item in report["unresolved"]:
            print(f"UNRESOLVED {item['code']} {item['field']}")
        if args.report_json:
            args.report_json.parent.mkdir(parents=True, exist_ok=True)
            args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("No files written because undocumented nulls exist.")
        return 2

    if report["conflicts"]:
        for item in report["conflicts"]:
            print(
                f"CONFLICT {item['code']} {item['field']}: "
                f"{item['current']!r} -> {item['target']!r} ({item['reason']})"
            )
        if not args.allow_overwrite:
            if args.report_json:
                args.report_json.parent.mkdir(parents=True, exist_ok=True)
                args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print("No files written because unresolved conflicts exist.")
            return 2

    if args.apply:
        for path, updated in planned:
            path.write_text(updated, encoding="utf-8")

    counts = Counter(item["action"] for item in report["actions"])
    print(
        f"mode={report['mode']} files={len(planned)} actions={len(report['actions'])} "
        f"conflicts={len(report['conflicts'])} details={dict(sorted(counts.items()))}"
    )
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not args.apply and planned:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SeedValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
