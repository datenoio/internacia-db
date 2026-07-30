#!/usr/bin/env python3
"""Apply Manus 2026-06-15 roadmap migrations (topics, directories, centroids)."""

from __future__ import annotations

import json
import shutil
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(help="Apply Manus roadmap data migrations")

ROOT = Path(__file__).resolve().parents[1]
INTBLOCKS = ROOT / "data" / "intblocks"
COUNTRIES = ROOT / "data" / "countries"
TOPIC_ALIASES = ROOT / "data" / "schemas" / "topic_aliases.yaml"
BLOCKTYPES = ROOT / "data" / "blocktypes" / "blocktypes.yaml"

TOPIC_RENAMES: dict[str, str] = {
    "climate": "climate_change",
    "armscontrol": "arms_control",
    "humanitarian_aid": "humanitarian",
    "humanitarian_assistance": "humanitarian",
    "economic": "economy",
    "economic_cooperation": "economy",
    "legal": "law",
    "legal_development": "law",
    "counterterrorism": "counter_terrorism",
    "disaster": "disaster_relief",
    "scientific_research": "science",
    "transportation": "transport",
    "sustainability": "sustainable_development",
    "cooperation": "regional_cooperation",
    "international_cooperation": "regional_cooperation",
}

SPORTS_KEYS = {
    "football",
    "champions_league",
    "world_cup",
    "world_championships",
    "world_championship",
    "basketball",
    "volleyball",
    "beach_volleyball",
    "cricket",
    "tennis",
    "davis_cup",
    "billie_jean_king_cup",
    "weightlifting",
    "swimming",
    "athletics",
    "track_and_field",
    "olympic_games",
    "youth_sports",
}

ACRONYM_TOPICS: dict[str, tuple[str, str]] = {
    "PIGS": ("economy", "Economy"),
    "E7": ("economy", "Economy"),
    "G33": ("trade", "Trade"),
    "BRICS": ("economy", "Economy"),
    "CIVETS": ("economy", "Economy"),
    "FATFBLACKLIST": ("finance", "Finance"),
    "FATFGREYLIST": ("finance", "Finance"),
    "FAILEDS": ("economy", "Economy"),
    "BALTICSTATES": ("regional_cooperation", "Regional Cooperation"),
    "CORECOUNT": ("economy", "Economy"),
    "EAGLE": ("economy", "Economy"),
    "LLDC": ("development", "Development"),
    "MAR": ("economy", "Economy"),
    "MENA": ("regional_cooperation", "Regional Cooperation"),
    "MIDAMERICA": ("regional_cooperation", "Regional Cooperation"),
    "NIC": ("economy", "Economy"),
    "N11": ("economy", "Economy"),
    "PERIPHCOUNT": ("economy", "Economy"),
    "SEMIPERIPH": ("economy", "Economy"),
    "SOUTHERNCONE": ("regional_cooperation", "Regional Cooperation"),
    "TIMBI": ("economy", "Economy"),
    "VISTA": ("economy", "Economy"),
    "WIEMARTRIANGLE": ("regional_cooperation", "Regional Cooperation"),
}

DIR_RENAMES = {
    "taxation": "tax",
    "transportation": "transport",
    "unregionalblocks": "unregionalblock",
}

MANUAL_CENTROIDS: dict[str, dict[str, float]] = {
    "AN": {"lat": 12.1034, "lng": -68.9335},
    "JG": {"lat": 49.2144, "lng": -2.1312},
    "KV": {"lat": 42.6026, "lng": 20.9030},
}

DIR_DEFAULT_TOPICS: dict[str, tuple[str, str]] = {
    "intorg": ("economy", "Economy"),
    "unagency": ("diplomacy", "Diplomacy"),
    "agreement": ("law", "Law"),
    "maritime": ("maritime", "Maritime"),
    "transport": ("transport", "Transport"),
    "water": ("water", "Water"),
    "aviation": ("aviation", "Aviation"),
    "audit": ("governance", "Governance"),
    "fund": ("finance", "Finance"),
    "parliamentary": ("governance", "Governance"),
}

HIGH_PROFILE_METADATA: dict[str, dict[str, Any]] = {
    "NATO": {
        "legal_status": "treaty",
        "geographic_scope": "regional",
        "headquarters": {"city": "Brussels", "country": "BE"},
    },
    "EU": {
        "legal_status": "treaty",
        "geographic_scope": "regional",
        "headquarters": {"city": "Brussels", "country": "BE"},
    },
    "AU": {
        "legal_status": "treaty",
        "geographic_scope": "regional",
        "headquarters": {"city": "Addis Ababa", "country": "ET"},
    },
    "ASEAN": {
        "legal_status": "treaty",
        "geographic_scope": "regional",
        "headquarters": {"city": "Jakarta", "country": "ID"},
    },
    "WHO": {
        "legal_status": "intergovernmental",
        "geographic_scope": "global",
        "headquarters": {"city": "Geneva", "country": "CH"},
    },
    "UNDP": {
        "legal_status": "intergovernmental",
        "geographic_scope": "global",
        "headquarters": {"city": "New York", "country": "US"},
    },
}


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path: Path, data: Any) -> None:
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def canonical_topic_key(key: str, blocktype: list[str] | None = None) -> str:
    if key in SPORTS_KEYS:
        return "sports_governance" if blocktype and "sports" in blocktype else "sports"
    return TOPIC_RENAMES.get(key, key)


def migrate_topics() -> int:
    changed = 0
    for path in sorted(INTBLOCKS.rglob("*.yaml")):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        blocktype = record.get("blocktype") or []
        topics = record.get("topics")
        if topics is None and record.get("id") in ACRONYM_TOPICS:
            key, name = ACRONYM_TOPICS[str(record["id"])]
            record["topics"] = [{"key": key, "name": name}]
            dump_yaml(path, record)
            changed += 1
            continue
        if not isinstance(topics, list):
            continue
        if topics == [] and record.get("id") in ACRONYM_TOPICS:
            key, name = ACRONYM_TOPICS[str(record["id"])]
            record["topics"] = [{"key": key, "name": name}]
            dump_yaml(path, record)
            changed += 1
            continue
        new_topics: list[dict[str, str]] = []
        seen: set[str] = set()
        for topic in topics:
            if not isinstance(topic, dict):
                continue
            key = canonical_topic_key(str(topic.get("key", "")), blocktype)
            if key in seen:
                continue
            seen.add(key)
            name = str(topic.get("name") or key.replace("_", " ").title())
            if key == "sports":
                name = "Sports"
            elif key == "sports_governance":
                name = "Sports Governance"
            elif key in TOPIC_RENAMES.values():
                name = key.replace("_", " ").title()
            new_topics.append({"key": key, "name": name})
        if new_topics != topics:
            record["topics"] = new_topics
            dump_yaml(path, record)
            changed += 1
    return changed


def rename_directories() -> None:
    for old, new in DIR_RENAMES.items():
        src = INTBLOCKS / old
        dst = INTBLOCKS / new
        if src.exists() and not dst.exists():
            src.rename(dst)
        elif src.exists() and dst.exists():
            for item in src.iterdir():
                target = dst / item.name
                if target.exists():
                    continue
                shutil.move(str(item), str(target))
            if not any(src.iterdir()):
                src.rmdir()


def update_blocktypes_taxonomy() -> None:
    entries = load_yaml(BLOCKTYPES) or []
    if not isinstance(entries, list):
        return
    filtered = [e for e in entries if isinstance(e, dict) and e.get("id") != "unregionalblocks"]
    if not any(e.get("id") == "audit" for e in filtered):
        filtered.append(
            {
                "id": "audit",
                "name": "Supreme Audit Institution",
                "other_names": [
                    {"lang": "en", "name": "Supreme Audit Institution"},
                    {"lang": "fr", "name": "Institution supérieure de contrôle"},
                ],
            }
        )
    dump_yaml(BLOCKTYPES, filtered)


def assign_audit_blocktype() -> int:
    changed = 0
    audit_dir = INTBLOCKS / "audit"
    if not audit_dir.exists():
        return 0
    for path in audit_dir.glob("*.yaml"):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        bts = list(record.get("blocktype") or [])
        if "audit" not in bts:
            record["blocktype"] = ["audit"] + [b for b in bts if b != "audit"]
            dump_yaml(path, record)
            changed += 1
    return changed


def align_primary_blocktype() -> tuple[int, int]:
    moved = 0
    reordered = 0
    for path in sorted(list(INTBLOCKS.rglob("*.yaml"))):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        bts = record.get("blocktype") or []
        if not bts:
            continue
        dir_name = path.parent.name
        primary = str(bts[0])
        if primary == dir_name:
            continue
        if dir_name in [str(b) for b in bts]:
            record["blocktype"] = [dir_name] + [b for b in bts if str(b) != dir_name]
            dump_yaml(path, record)
            reordered += 1
            continue
        target_dir = INTBLOCKS / primary
        if target_dir.is_dir():
            target = target_dir / path.name
            if not target.exists():
                shutil.move(str(path), str(target))
                moved += 1
    return moved, reordered


def fix_exemplar_records() -> None:
    wto_old = INTBLOCKS / "unagency" / "WTO.yaml"
    wto_new = INTBLOCKS / "trade" / "WTO.yaml"
    if wto_old.exists() and not wto_new.exists():
        record = load_yaml(wto_old)
        if isinstance(record, dict):
            bts = [b for b in (record.get("blocktype") or []) if str(b) != "unagency"]
            if "trade" not in bts:
                bts = ["trade"] + bts
            else:
                bts = ["trade"] + [b for b in bts if b != "trade"]
            record["blocktype"] = bts
            dump_yaml(wto_new, record)
            wto_old.unlink()

    g20 = INTBLOCKS / "political" / "G-20.yaml"
    if g20.exists():
        record = load_yaml(g20)
        if isinstance(record, dict):
            bts = list(record.get("blocktype") or [])
            for bt in ("economic", "forum"):
                if bt not in bts:
                    bts.append(bt)
            record["blocktype"] = bts
            topics = list(record.get("topics") or [])
            keys = {t.get("key") for t in topics if isinstance(t, dict)}
            for key, name in (("economy", "Economy"), ("finance", "Finance")):
                if key not in keys:
                    topics.append({"key": key, "name": name})
            record["topics"] = topics
            dump_yaml(g20, record)


def backfill_high_profile_metadata() -> int:
    changed = 0
    today = date.today().isoformat()
    for iid, meta in HIGH_PROFILE_METADATA.items():
        matches = list(INTBLOCKS.rglob(f"{iid}.yaml"))
        if not matches:
            continue
        path = matches[0]
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        updated = False
        for field, value in meta.items():
            if is_empty(record.get(field)):
                record[field] = value
                updated = True
                upsert_intblock_provenance(record, field, "official charter", today)
        if updated:
            dump_yaml(path, record)
            changed += 1
    return changed


def official_source_url(record: dict[str, Any]) -> str:
    for link in record.get("links") or []:
        if isinstance(link, dict) and link.get("type") == "website" and link.get("url"):
            return str(link["url"])
    for link in record.get("links") or []:
        if isinstance(link, dict) and link.get("url"):
            return str(link["url"])
    return ""


def upsert_intblock_provenance(
    record: dict[str, Any],
    field: str,
    source: str,
    retrieved_at: str | None = None,
) -> None:
    retrieved_at = retrieved_at or date.today().isoformat()
    provenance = [p for p in (record.get("provenance") or []) if p.get("field") != field]
    entry: dict[str, str] = {"field": field, "source": source, "retrieved_at": retrieved_at}
    url = official_source_url(record)
    if url:
        entry["url"] = url
    provenance.append(entry)
    record["provenance"] = provenance


def backfill_context_field_provenance() -> int:
    """Add provenance for legal_status, geographic_scope, headquarters when present."""
    changed = 0
    today = date.today().isoformat()
    for path in sorted(INTBLOCKS.rglob("*.yaml")):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        before = yaml.dump(record.get("provenance"), sort_keys=True)
        for field in ("legal_status", "geographic_scope", "headquarters"):
            if is_empty(record.get(field)):
                continue
            prov = record.get("provenance") or []
            if any(p.get("field") == field for p in prov):
                continue
            upsert_intblock_provenance(record, field, "official sources", today)
        after = yaml.dump(record.get("provenance"), sort_keys=True)
        if before != after:
            dump_yaml(path, record)
            changed += 1
    return changed


def is_empty(val: Any) -> bool:
    return val is None or val == "" or val == [] or val == {}


def fetch_country_centroids() -> dict[str, dict[str, float]]:
    url = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Internacia-DB/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        rows = json.loads(resp.read().decode("utf-8"))
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        cca2 = row.get("cca2")
        latlng = row.get("latlng") or []
        if cca2 and len(latlng) == 2:
            out[str(cca2)] = {"lat": float(latlng[0]), "lng": float(latlng[1])}
    return out


def populate_centroids(dry_run: bool = False) -> int:
    centroids = fetch_country_centroids()
    changed = 0
    today = date.today().isoformat()
    for path in sorted(COUNTRIES.glob("*.yaml")):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        code = str(record.get("code") or path.stem)
        if not is_empty(record.get("centroid")):
            record.pop("latitude", None)
            record.pop("longitude", None)
            continue
        c = centroids.get(code) or MANUAL_CENTROIDS.get(code)
        if not c:
            continue
        record["centroid"] = c
        record.pop("latitude", None)
        record.pop("longitude", None)
        provenance = [p for p in (record.get("provenance") or []) if p.get("field") != "centroid"]
        provenance.append(
            {
                "field": "centroid",
                "source": "mledoze/countries",
                "url": "https://github.com/mledoze/countries",
                "retrieved_at": today,
            }
        )
        record["provenance"] = provenance
        if not dry_run:
            dump_yaml(path, record)
        changed += 1
    return changed


def assign_default_topics() -> int:
    changed = 0
    for path in sorted(INTBLOCKS.rglob("*.yaml")):
        record = load_yaml(path)
        if not isinstance(record, dict):
            continue
        topics = record.get("topics")
        if topics not in (None, []):
            continue
        dir_name = path.parent.name
        primary = str((record.get("blocktype") or [dir_name])[0])
        key, name = DIR_DEFAULT_TOPICS.get(dir_name) or DIR_DEFAULT_TOPICS.get(primary, ("governance", "Governance"))
        record["topics"] = [{"key": key, "name": name}]
        dump_yaml(path, record)
        changed += 1
    return changed


def copy_un_includes(target_id: str, out_path: Path) -> None:
    un_path = INTBLOCKS / "political" / "UN.yaml"
    un = load_yaml(un_path)
    record = load_yaml(out_path) if out_path.exists() else {}
    if isinstance(un, dict) and isinstance(record, dict):
        record["includes"] = un.get("includes") or []
        record["membership_count"] = len(record["includes"])
        dump_yaml(out_path, record)


@app.command("topics")
def cmd_topics() -> None:
    n = migrate_topics()
    m = assign_default_topics()
    typer.echo(f"Migrated topics in {n} files; assigned defaults in {m} files")


@app.command("directories")
def cmd_directories() -> None:
    rename_directories()
    update_blocktypes_taxonomy()
    n = assign_audit_blocktype()
    fix_exemplar_records()
    moved, reordered = align_primary_blocktype()
    typer.echo(f"Directories renamed; audit blocktype on {n} files; moved {moved}, reordered {reordered}")


@app.command("metadata")
def cmd_metadata() -> None:
    n = backfill_high_profile_metadata()
    p = backfill_context_field_provenance()
    typer.echo(f"Backfilled metadata on {n} high-profile records; provenance on {p} records")


@app.command("provenance")
def cmd_provenance() -> None:
    p = backfill_context_field_provenance()
    typer.echo(f"Added context-field provenance on {p} intblock records")


@app.command("centroids")
def cmd_centroids(dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    n = populate_centroids(dry_run=dry_run)
    typer.echo(f"Populated centroid on {n} country records")


@app.command("all")
def cmd_all() -> None:
    cmd_directories()
    cmd_topics()
    cmd_metadata()
    cmd_centroids()


if __name__ == "__main__":
    app()
