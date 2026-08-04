#!/usr/bin/env python3
"""Invert attribute-partition intblocks into country fields.

Reads data/intblocks/{writingdirection,writingsystem,dvdregion,teleregion,
lawsystem,railgauge,traffichand}/, maps legacy ids via data/vocabs/*/legacy_intblock_ids,
and writes country YAML fields. Also emits data/attribute_intblock_migrations.yaml.

Does not add government_form to countries (scope guardrail); govform intblocks
are listed as vocab_only retirements in the migration artifact.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTBLOCKS = ROOT / "data" / "intblocks"
COUNTRIES = ROOT / "data" / "countries"
VOCABS = ROOT / "data" / "vocabs"
MIGRATION_OUT = ROOT / "data" / "attribute_intblock_migrations.yaml"

SINCE = "Unreleased"

# blocktype dir -> (country_field, kind)
# kind: list_id | list_rail | scalar_dvd | car_side
FIELD_SPECS: dict[str, tuple[str, str]] = {
    "writingdirection": ("writing_directions", "list_id"),
    "writingsystem": ("writing_systems", "list_id"),
    "dvdregion": ("dvd_region", "scalar_dvd"),
    "teleregion": ("broadcast_systems", "list_id"),
    "lawsystem": ("legal_systems", "list_id"),
    "railgauge": ("rail_gauges", "list_rail"),
    "traffichand": ("car_side", "car_side"),
}

TRAFFIC_VALUE = {"LHTRAFFIC": "left", "RHTRAFFIC": "right"}


def _load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dump_yaml(path: Path, data: Any) -> None:
    path.write_text(
        yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )


def load_legacy_maps() -> tuple[dict[str, dict[str, Any]], dict[str, int], dict[str, int]]:
    """legacy_id -> vocab entry; dvd region ints; rail gauge_mm by vocab id."""
    legacy: dict[str, dict[str, Any]] = {}
    dvd_regions: dict[str, int] = {}
    gauge_mm: dict[str, int] = {}
    for path in VOCABS.glob("*.yaml"):
        entries = _load_yaml(path) or []
        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("id"):
                continue
            for lid in entry.get("legacy_intblock_ids") or []:
                legacy[str(lid)] = entry
            if path.name == "dvd_regions.yaml" and entry.get("region") is not None:
                dvd_regions[str(entry["id"])] = int(entry["region"])
                for lid in entry.get("legacy_intblock_ids") or []:
                    dvd_regions[str(lid)] = int(entry["region"])
            if path.name == "rail_gauges.yaml" and entry.get("gauge_mm") is not None:
                gauge_mm[str(entry["id"])] = int(entry["gauge_mm"])
    return legacy, dvd_regions, gauge_mm


def country_members(record: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for inc in record.get("includes") or []:
        if isinstance(inc, dict) and inc.get("type") == "country" and inc.get("id"):
            out.append(str(inc["id"]).upper())
    return out


def mark_primary(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(items) == 1:
        items[0] = {**items[0], "primary": True}
    elif len(items) > 1 and not any(i.get("primary") for i in items):
        items[0] = {**items[0], "primary": True}
    return items


def build_country_updates(
    legacy: dict[str, dict[str, Any]],
    dvd_regions: dict[str, int],
    gauge_mm: dict[str, int],
) -> tuple[dict[str, dict[str, Any]], list[str], list[dict[str, Any]]]:
    """Return per-code field updates, conflict lines, migration rows."""
    # code -> field -> ordered unique values
    lists: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    dvd: dict[str, int] = {}
    traffic: dict[str, str] = {}
    conflicts: list[str] = []
    migrations: list[dict[str, Any]] = []
    seen_retired: set[str] = set()

    for blocktype, (field, kind) in FIELD_SPECS.items():
        directory = INTBLOCKS / blocktype
        if not directory.is_dir():
            conflicts.append(f"missing directory: {directory}")
            continue
        for path in sorted(directory.glob("*.yaml")):
            rec = _load_yaml(path) or {}
            rid = str(rec.get("id") or path.stem)
            members = country_members(rec)

            if rid not in seen_retired:
                seen_retired.add(rid)
                if kind == "car_side":
                    migrations.append(
                        {
                            "retired_id": rid,
                            "country_field": "car_side",
                            "country_value": TRAFFIC_VALUE.get(rid, ""),
                            "since": SINCE,
                            "note": f"Prefer countries.car_side = '{TRAFFIC_VALUE.get(rid, '')}'",
                        }
                    )
                elif kind == "scalar_dvd":
                    region = dvd_regions.get(rid)
                    migrations.append(
                        {
                            "retired_id": rid,
                            "country_field": "dvd_region",
                            "country_value": region,
                            "since": SINCE,
                            "note": f"Prefer countries.dvd_region = {region}",
                        }
                    )
                else:
                    vocab = legacy.get(rid, {})
                    vid = str(vocab.get("id") or "")
                    migrations.append(
                        {
                            "retired_id": rid,
                            "country_field": field,
                            "country_value_id": vid,
                            "since": SINCE,
                            "note": f"Prefer countries.{field} containing id '{vid}'",
                        }
                    )

            if kind == "car_side":
                value = TRAFFIC_VALUE.get(rid)
                if not value:
                    conflicts.append(f"unknown traffichand id {rid}")
                    continue
                for code in members:
                    if code in traffic and traffic[code] != value:
                        conflicts.append(f"{code}: traffichand conflict {traffic[code]} vs {value}")
                    traffic[code] = value
                continue

            if kind == "scalar_dvd":
                region = dvd_regions.get(rid)
                if region is None:
                    conflicts.append(f"unknown dvdregion id {rid}")
                    continue
                for code in members:
                    if code in dvd and dvd[code] != region:
                        conflicts.append(f"{code}: dvd_region conflict {dvd[code]} vs {region}")
                    dvd[code] = region
                continue

            vocab = legacy.get(rid)
            if not vocab:
                conflicts.append(f"no vocab mapping for {rid}")
                continue
            vid = str(vocab["id"])
            for code in members:
                bucket = lists[code][field]
                if vid not in bucket:
                    bucket.append(vid)

    # govform vocab-only retirements
    gov_dir = INTBLOCKS / "govform"
    if gov_dir.is_dir():
        gov_legacy = {
            lid: e
            for e in (_load_yaml(VOCABS / "government_forms.yaml") or [])
            for lid in (e.get("legacy_intblock_ids") or [])
        }
        for path in sorted(gov_dir.glob("*.yaml")):
            rec = _load_yaml(path) or {}
            rid = str(rec.get("id") or path.stem)
            if rid in seen_retired:
                continue
            seen_retired.add(rid)
            vocab = gov_legacy.get(rid, {})
            migrations.append(
                {
                    "retired_id": rid,
                    "disposition": "vocab_only",
                    "vocab": "government_forms",
                    "vocab_id": vocab.get("id"),
                    "since": SINCE,
                    "note": "Government form not stored on countries; see data/vocabs/government_forms.yaml",
                }
            )

    updates: dict[str, dict[str, Any]] = defaultdict(dict)
    for code, fields in lists.items():
        for field, ids in fields.items():
            if field == "rail_gauges":
                items = [{"id": i, **({"gauge_mm": gauge_mm[i]} if i in gauge_mm else {})} for i in ids]
                updates[code][field] = mark_primary(items)
            else:
                items = [{"id": i} for i in ids]
                if field in ("writing_directions", "writing_systems"):
                    updates[code][field] = mark_primary(items)
                else:
                    updates[code][field] = items

    for code, region in dvd.items():
        updates[code]["dvd_region"] = region

    # car_side: reconcile with existing YAML; prefer existing car_side on conflict
    for path in COUNTRIES.glob("*.yaml"):
        code = path.stem.upper()
        data = _load_yaml(path) or {}
        existing = data.get("car_side")
        inverted = traffic.get(code)
        if inverted and existing and existing != inverted:
            conflicts.append(
                f"{code}: car_side={existing} vs traffichand={inverted} (keeping car_side)"
            )
        # Do not overwrite car_side from traffichand; car_side is already source of truth.
        # Only note missing car_side when traffichand has a value.
        if inverted and not existing:
            updates[code]["car_side"] = inverted
            conflicts.append(f"{code}: car_side missing; set from traffichand={inverted}")

    return updates, conflicts, migrations


def apply_updates(updates: dict[str, dict[str, Any]], *, dry_run: bool) -> int:
    changed = 0
    for code, fields in sorted(updates.items()):
        path = COUNTRIES / f"{code}.yaml"
        if not path.exists():
            print(f"SKIP missing country file: {code}")
            continue
        data = _load_yaml(path) or {}
        before = yaml.dump(data, sort_keys=True)
        for key, value in fields.items():
            data[key] = value
        # Light provenance for migrated attribute fields
        prov = list(data.get("provenance") or [])
        for key in fields:
            if key == "car_side":
                continue
            if any(isinstance(p, dict) and p.get("field") == key for p in prov):
                continue
            prov.append(
                {
                    "field": key,
                    "source": "Internacia attribute-intblock migration",
                    "retrieved_at": "2026-08-03",
                    "url": "https://github.com/datenoio/internacia-db",
                    "license": "CC-BY-4.0",
                }
            )
        data["provenance"] = prov
        after = yaml.dump(data, sort_keys=True)
        if before == after:
            continue
        changed += 1
        if not dry_run:
            _dump_yaml(path, data)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write-migration-only", action="store_true")
    args = parser.parse_args()

    legacy, dvd_regions, gauge_mm = load_legacy_maps()
    updates, conflicts, migrations = build_country_updates(legacy, dvd_regions, gauge_mm)

    print(f"Countries to update: {len(updates)}")
    print(f"Migration entries: {len(migrations)}")
    if conflicts:
        print(f"Conflicts / notes ({len(conflicts)}):")
        for line in conflicts:
            print(f"  - {line}")

    if not args.write_migration_only:
        n = apply_updates(updates, dry_run=args.dry_run)
        print(f"{'Would update' if args.dry_run else 'Updated'} {n} country files")

    if not args.dry_run:
        _dump_yaml(MIGRATION_OUT, migrations)
        print(f"Wrote {MIGRATION_OUT}")


if __name__ == "__main__":
    main()
