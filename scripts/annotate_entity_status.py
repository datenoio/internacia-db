#!/usr/bin/env python3
"""Annotate country records with entity_type and code_status."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(help="Annotate country entity status fields")

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES_DIR = ROOT / "data" / "countries"

SPECIAL_ADMIN = frozenset({"HK", "MO"})
DISPUTED_TERRITORY = frozenset({"EH"})

POLICY_OVERRIDES: dict[str, dict[str, Any]] = {
    "AN": {
        "entity_type": "historical_entity",
        "code_status": "obsolete",
        "recognition_status": {
            "status": "dissolved",
            "notes": "Former ISO 3166-1 code; successors include CW, SX, and BQ.",
        },
    },
    "JG": {
        "entity_type": "supranational_grouping",
        "code_status": "user_assigned",
        "recognition_status": {
            "status": "collective_grouping",
            "notes": "Not a current ISO 3166-1 alpha-2 code; use GG and JE for constituent territories.",
        },
    },
    "KV": {
        "entity_type": "disputed_territory",
        "code_status": "user_assigned",
        "recognition_status": {
            "status": "disputed_or_partially_recognized",
            "un_member": False,
            "notes": "User-assigned alpha-2 code KV; not an official ISO 3166-1 assignment.",
        },
    },
}


def infer_entity_type(record: dict[str, Any]) -> str:
    code = record.get("code", "")
    if code in SPECIAL_ADMIN:
        return "special_administrative_region"
    if code in DISPUTED_TERRITORY:
        return "disputed_territory"
    if record.get("independent") is True:
        return "sovereign_state"
    return "dependent_territory"


def annotate_record(record: dict[str, Any]) -> dict[str, Any]:
    code = record.get("code", "")
    override = POLICY_OVERRIDES.get(code)
    if override:
        record.update(override)
        return record

    record["code_status"] = "official_iso3166_1"
    record["entity_type"] = infer_entity_type(record)
    return record


@app.command()
def main(
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Set entity_type and code_status on all country YAML sources."""
    updated = 0
    official = 0

    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        before = yaml.dump(data, sort_keys=True)
        data = annotate_record(data)
        after = yaml.dump(data, sort_keys=True)

        if data.get("code_status") == "official_iso3166_1":
            official += 1

        if before != after:
            updated += 1
            if dry_run:
                typer.echo(f"would update {path.relative_to(ROOT)}")
            else:
                path.write_text(
                    yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
                    encoding="utf-8",
                )
                typer.echo(f"updated {path.relative_to(ROOT)}")

    typer.echo(f"done: {updated} updated, {official} with code_status=official_iso3166_1")


if __name__ == "__main__":
    app()
