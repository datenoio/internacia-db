#!/usr/bin/env python3
"""Enrich intblock YAML records from Wikidata.

Three enrichment tracks (all on by default, individually skippable):
  - wikidata_id backfill (high-confidence matches only)
  - description replacement for templated boilerplate
  - multilingual other_names and acronym aliases
Every enriched field records a provenance entry.
"""

from __future__ import annotations

import re
import time
import unicodedata
import urllib.parse
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

from internacia_builder.http import fetch_json as _fetch_json

app = typer.Typer(help="Enrich intblock records from Wikidata")

ROOT = Path(__file__).resolve().parents[1]
INTBLOCKS_DIR = ROOT / "data" / "intblocks"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_URL = "https://www.wikidata.org/"
REQUEST_DELAY = 0.1
USER_AGENT = "Internacia-DB Intblocks Enricher/1.0"

# Languages backfilled into other_names (UN official languages + common extras).
UN_LANGS = ["en", "ar", "zh", "fr", "ru", "es", "de", "pt"]

# Boilerplate descriptions produced by earlier automated imports.
TEMPLATED_DESC = re.compile(
    r"^\s*(international (entity|organization) focused on|an? international (organization|entity)|"
    r"regional (organization|entity) focused on|international organization for)",
    re.IGNORECASE,
)

WD_LINK = re.compile(r"wikidata\.org/(?:wiki|entity)/(Q[1-9][0-9]*)")


def fetch_json(url: str) -> Any:
    return _fetch_json(url, user_agent=USER_AGENT, timeout=60)


def normalize(text: str) -> str:
    """Casefold, strip diacritics and punctuation, collapse whitespace for matching."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text)
    return " ".join(text.lower().split())


def is_acronym(value: str) -> bool:
    v = value.strip()
    return 2 <= len(v) <= 12 and v == v.upper() and any(c.isalpha() for c in v) and " " not in v


def is_templated(description: str) -> bool:
    return bool(TEMPLATED_DESC.match(description or ""))


def wikidata_search(name: str, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "uselang": "en",
        "format": "json",
        "limit": limit,
        "type": "item",
    }
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    try:
        data = fetch_json(url)
    except Exception:
        return []
    return data.get("search") or []


def wikidata_entities(qids: list[str], langs: list[str], *, with_claims: bool = False) -> dict[str, dict[str, Any]]:
    if not qids:
        return {}
    props = "labels|aliases|descriptions"
    if with_claims:
        props += "|claims"
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": props,
        "languages": "|".join(langs),
        "format": "json",
    }
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    try:
        data = fetch_json(url)
    except Exception:
        return {}
    return data.get("entities") or {}


def record_qid_from_links(record: dict[str, Any]) -> str | None:
    for link in record.get("links") or []:
        if isinstance(link, dict):
            m = WD_LINK.search(str(link.get("url", "")))
            if m:
                return m.group(1)
    return None


def record_acronyms(record: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for acr in record.get("acronyms") or []:
        if isinstance(acr, dict) and acr.get("value"):
            out.add(str(acr["value"]))
    rid = str(record.get("id") or "")
    if rid:
        out.add(rid)
    return out


def resolve_wikidata_id(record: dict[str, Any]) -> str | None:
    """High-confidence wikidata_id resolution: existing link, then exact-match search."""
    qid = record_qid_from_links(record)
    if qid:
        return qid

    name = str(record.get("name") or "")
    if not name:
        return None
    norm_name = normalize(name)
    norm_acronyms = {normalize(a) for a in record_acronyms(record)}

    for cand in wikidata_search(name):
        label = normalize(str(cand.get("label") or ""))
        match_text = normalize(str((cand.get("match") or {}).get("text") or ""))
        aliases = {normalize(str(a)) for a in (cand.get("aliases") or [])}
        cand_names = {label, match_text} | aliases
        cand_names.discard("")
        if norm_name in cand_names:
            return str(cand.get("id"))
        # Acronym match only when it is a genuine acronym (avoids generic collisions)
        if norm_acronyms & cand_names and any(is_acronym(a) for a in record_acronyms(record)):
            # require the candidate full label to share a word with the record name
            if norm_name and label and (set(norm_name.split()) & set(label.split())):
                return str(cand.get("id"))
    return None


def upsert_provenance(record: dict[str, Any], field: str, source: str, *, url: str = "", license: str = "") -> None:
    provenance = [p for p in (record.get("provenance") or []) if p.get("field") != field]
    entry: dict[str, str] = {"field": field, "source": source, "retrieved_at": date.today().isoformat()}
    if url:
        entry["url"] = url
    if license:
        entry["license"] = license
    provenance.append(entry)
    record["provenance"] = provenance


def clean_description(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


DESC_LANGS = ["en", "fr", "de", "es", "pt", "ru", "ar"]


def pick_wikidata_description(entity: dict[str, Any], min_len: int = 8) -> str | None:
    descriptions = entity.get("descriptions") or {}
    for lang in DESC_LANGS:
        desc = (descriptions.get(lang) or {}).get("value")
        if desc and len(desc.strip()) >= min_len:
            return str(desc).strip()
    return None


def grouping_fallback_description(record: dict[str, Any]) -> str | None:
    """Build a specific description when Wikidata has no usable text."""
    if not is_templated(str(record.get("description") or "")):
        return None
    name = str(record.get("name") or record.get("id") or "").strip()
    if not name:
        return None
    blocktypes = [str(b) for b in (record.get("blocktype") or [])]
    regions = record.get("regions") or []
    region_part = f" in {regions[0]}" if regions else ""
    members = record.get("membership_count") or len(record.get("includes") or [])

    if "geographic" in blocktypes:
        if members:
            return f"{name} is a regional grouping of {members} countries{region_part}."
        return f"{name} is a geographic region{region_part}."

    primary = blocktypes[0] if blocktypes else "organization"
    if members:
        return f"{name} is an international {primary} body with {members} members."
    return f"{name} is an international {primary} organization."


def infer_description(record: dict[str, Any], entity: dict[str, Any]) -> str | None:
    desc = pick_wikidata_description(entity)
    if desc:
        return clean_description(desc)
    fallback = grouping_fallback_description(record)
    if fallback:
        return fallback
    labels = entity.get("labels") or {}
    for lang in DESC_LANGS:
        label = (labels.get(lang) or {}).get("value")
        if label and len(label) >= 3:
            name = str(record.get("name") or record.get("id") or label)
            if normalize(label) != normalize(name):
                return f"{name} ({label})."
            break
    return None


def enrich_descriptions(record: dict[str, Any], entity: dict[str, Any], *, force: bool) -> bool:
    current = str(record.get("description") or "")
    if not (force or is_templated(current) or not current):
        return False
    new_desc = infer_description(record, entity) if entity else None
    if not new_desc and is_templated(current):
        new_desc = grouping_fallback_description(record)
    if not new_desc or new_desc == current:
        return False
    record["description"] = new_desc
    source = "Wikidata" if entity and pick_wikidata_description(entity) else "inferred grouping"
    url = WIKIDATA_URL if source == "Wikidata" else ""
    license = "CC0" if source == "Wikidata" else ""
    upsert_provenance(record, "description", source, url=url, license=license)
    return True


def enrich_other_names(record: dict[str, Any], entity: dict[str, Any]) -> bool:
    labels = entity.get("labels") or {}
    existing = record.get("other_names") or []
    have = {str(n.get("id")) for n in existing if isinstance(n, dict)}
    added = False
    for lang in UN_LANGS:
        if lang in have:
            continue
        label = (labels.get(lang) or {}).get("value")
        if not label:
            continue
        existing.append({"id": lang, "name": label})
        have.add(lang)
        added = True
    if added:
        existing.sort(key=lambda n: str(n.get("id")))
        record["other_names"] = existing
        upsert_provenance(record, "other_names", "Wikidata", url=WIKIDATA_URL, license="CC0")
    return added


def enrich_acronyms(record: dict[str, Any], entity: dict[str, Any]) -> bool:
    aliases = entity.get("aliases") or {}
    existing = record.get("acronyms") or []
    have = {(str(a.get("lang")), str(a.get("value"))) for a in existing if isinstance(a, dict)}
    added = False
    for lang in UN_LANGS:
        for alias in aliases.get(lang) or []:
            value = str(alias.get("value") or "")
            if not is_acronym(value):
                continue
            key = (lang, value)
            if key in have:
                continue
            existing.append({"lang": lang, "value": value})
            have.add(key)
            added = True
    if added:
        record["acronyms"] = existing
        upsert_provenance(record, "acronyms", "Wikidata", url=WIKIDATA_URL, license="CC0")
    return added


def wikidata_inception_date(entity: dict[str, Any]) -> str | None:
    claims = entity.get("claims") or {}
    for prop in ("P571", "P580", "P1619"):  # inception, start time, date of official opening
        for stmt in claims.get(prop) or []:
            try:
                time_val = str(stmt["mainsnak"]["datavalue"]["value"]["time"])
            except (KeyError, TypeError, ValueError):
                continue
            match = re.match(r"([+-]?)(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", time_val)
            if not match:
                continue
            year = match.group(2)
            month = match.group(3)
            day = match.group(4)
            if month and day:
                return f"{year}-{month}-{day}"
            if month:
                return f"{year}-{month}"
            return year
    return None


def enrich_founded(record: dict[str, Any], entity: dict[str, Any]) -> bool:
    if record.get("founded"):
        return False
    founded = wikidata_inception_date(entity)
    if not founded:
        return False
    record["founded"] = founded
    qid = str(record.get("wikidata_id") or "")
    upsert_provenance(
        record,
        "founded",
        "Wikidata",
        url=f"{WIKIDATA_URL}wiki/{qid}" if qid else WIKIDATA_URL,
        license="CC0",
    )
    return True


def stamp_last_verified(record: dict[str, Any]) -> None:
    """Record the date this record was last touched by enrichment/verification."""
    record["last_verified"] = date.today().isoformat()


def wikidata_coordinates(entity: dict[str, Any]) -> tuple[float, float] | None:
    """Read a coordinate-location (P625) claim as (lat, lng)."""
    for stmt in (entity.get("claims") or {}).get("P625") or []:
        try:
            value = stmt["mainsnak"]["datavalue"]["value"]
            return float(value["latitude"]), float(value["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
    return None


def wikidata_hq_qid(entity: dict[str, Any]) -> str | None:
    """Read the headquarters-location (P159) claim as a Q-id."""
    for stmt in (entity.get("claims") or {}).get("P159") or []:
        try:
            return str(stmt["mainsnak"]["datavalue"]["value"]["id"])
        except (KeyError, TypeError):
            continue
    return None


def enrich_headquarters(
    record: dict[str, Any],
    entity: dict[str, Any],
    city_entities: dict[str, dict[str, Any]] | None = None,
) -> bool:
    """Fill ``headquarters`` (city + coordinates) from Wikidata P159/P625 claims.

    Never overwrites an existing hand-curated ``headquarters`` value.
    """
    if record.get("headquarters"):
        return False
    hq: dict[str, Any] = {}
    coords = wikidata_coordinates(entity)
    hq_qid = wikidata_hq_qid(entity)
    if hq_qid and city_entities and hq_qid in city_entities:
        city = city_entities[hq_qid]
        label = (city.get("labels") or {}).get("en", {}).get("value")
        if label:
            hq["city"] = str(label)
        if coords is None:
            coords = wikidata_coordinates(city)
    if coords is not None:
        hq["coordinates"] = {"lat": coords[0], "lng": coords[1]}
    if not hq:
        return False
    record["headquarters"] = hq
    qid = str(record.get("wikidata_id") or "")
    upsert_provenance(
        record,
        "headquarters",
        "Wikidata",
        url=f"{WIKIDATA_URL}wiki/{qid}" if qid else WIKIDATA_URL,
        license="CC0",
    )
    return True


@app.command("backfill-structural")
def backfill_structural(
    subdir: str = typer.Option("", "--subdir", help="Restrict to intblocks subdirectory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report changes without writing"),
    limit: int = typer.Option(0, "--limit", help="Max records to process (0 = all)"),
) -> None:
    """Backfill ``headquarters`` (P159/P625) and ``founded`` (P571) from Wikidata.

    Only records with a ``wikidata_id`` and an empty target field are touched;
    each filled field gets a provenance entry and the record is stamped with
    ``last_verified``.
    """
    search_dir = INTBLOCKS_DIR / subdir if subdir else INTBLOCKS_DIR
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(search_dir.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not data.get("wikidata_id"):
            continue
        if data.get("headquarters") and data.get("founded"):
            continue
        records.append((path, data))
    if limit:
        records = records[:limit]
    typer.echo(f"Backfilling structural metadata for {len(records)} record(s)...")

    qids = sorted({str(d["wikidata_id"]) for _, d in records})
    entities: dict[str, dict[str, Any]] = {}
    for i in range(0, len(qids), 50):
        entities.update(wikidata_entities(qids[i : i + 50], ["en"], with_claims=True))
        time.sleep(REQUEST_DELAY)

    # Resolve headquarters city entities (P159 targets) for labels + coordinates.
    hq_qids = sorted({q for e in entities.values() if (q := wikidata_hq_qid(e))})
    city_entities: dict[str, dict[str, Any]] = {}
    for i in range(0, len(hq_qids), 50):
        city_entities.update(wikidata_entities(hq_qids[i : i + 50], ["en"], with_claims=True))
        time.sleep(REQUEST_DELAY)

    updated = 0
    for path, data in records:
        entity = entities.get(str(data.get("wikidata_id") or ""), {})
        changed = False
        changed |= enrich_headquarters(data, entity, city_entities)
        changed |= enrich_founded(data, entity)
        if not changed:
            continue
        stamp_last_verified(data)
        updated += 1
        rel = path.relative_to(ROOT)
        if dry_run:
            typer.echo(f"would update {rel} -> hq={data.get('headquarters')} founded={data.get('founded')}")
        else:
            path.write_text(
                yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
            typer.echo(f"updated {rel}")
    typer.echo(f"done: {updated} record(s) {'would be ' if dry_run else ''}updated")


@app.command("backfill-founded")
def backfill_founded(
    subdir: str = typer.Option("", "--subdir", help="Restrict to intblocks subdirectory"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    limit: int = typer.Option(0, "--limit", help="Max records to process (0 = all)"),
) -> None:
    """Backfill founded dates from Wikidata P571/P580 for records with wikidata_id."""
    search_dir = INTBLOCKS_DIR / subdir if subdir else INTBLOCKS_DIR
    paths = sorted(search_dir.rglob("*.yaml"))
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if data.get("founded") or not data.get("wikidata_id"):
            continue
        records.append((path, data))
    if limit:
        records = records[:limit]
    typer.echo(f"Backfilling founded for {len(records)} record(s)...")
    qids = sorted({str(d["wikidata_id"]) for _, d in records})
    entities: dict[str, dict[str, Any]] = {}
    for i in range(0, len(qids), 50):
        entities.update(wikidata_entities(qids[i : i + 50], ["en"], with_claims=True))
        time.sleep(REQUEST_DELAY)
    updated = 0
    for path, data in records:
        entity = entities.get(str(data.get("wikidata_id") or ""), {})
        if not enrich_founded(data, entity):
            continue
        stamp_last_verified(data)
        updated += 1
        if dry_run:
            typer.echo(f"would update {path.relative_to(ROOT)} -> founded={data['founded']}")
        else:
            path.write_text(
                yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
    typer.echo(f"done: {updated} founded field(s) {'would be ' if dry_run else ''}updated")


@app.command()
def enrich(
    id: str = typer.Option("", "--id", help="Single intblock id to enrich"),
    ids: str = typer.Option("", "--ids", help="Comma-separated intblock ids"),
    subdir: str = typer.Option("", "--subdir", help="Restrict to a subdirectory of data/intblocks (e.g. political)"),
    limit: int = typer.Option(0, "--limit", help="Process at most N files (0 = all)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print changes without writing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing descriptions"),
    skip_wikidata: bool = typer.Option(False, "--skip-wikidata", help="Skip wikidata_id backfill"),
    skip_descriptions: bool = typer.Option(False, "--skip-descriptions", help="Skip description enrichment"),
    skip_names: bool = typer.Option(False, "--skip-names", help="Skip multilingual name/acronym enrichment"),
    templated_only: bool = typer.Option(
        False,
        "--templated-only",
        help="Only process records with templated boilerplate descriptions",
    ),
) -> None:
    """Fetch Wikidata data and merge it into intblock YAML sources."""
    search_dir = INTBLOCKS_DIR / subdir if subdir else INTBLOCKS_DIR
    if not search_dir.is_dir():
        raise typer.BadParameter(f"subdir not found: {search_dir}")
    id_filter = {s.strip() for s in ids.split(",") if s.strip()} if ids else set()
    if id:
        matches = sorted(search_dir.rglob(f"{id.upper()}.yaml"))
        paths = matches or sorted(search_dir.rglob("*.yaml"))
    else:
        paths = sorted(search_dir.rglob("*.yaml"))
    records: list[tuple[Path, dict[str, Any]]] = []
    originals: dict[Path, str] = {}
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rid = str(data.get("id") or "")
        if id and rid != id.upper():
            continue
        if id_filter and rid not in id_filter:
            continue
        if templated_only and not is_templated(str(data.get("description") or "")):
            continue
        records.append((path, data))
        originals[path] = yaml.dump(data, sort_keys=True, allow_unicode=True)
    if limit and not id:
        records = records[:limit]

    typer.echo(f"Loaded {len(records)} intblock record(s)")

    resolved = 0
    if not skip_wikidata:
        missing = [(p, d) for p, d in records if not d.get("wikidata_id")]
        typer.echo(f"Resolving wikidata_id for {len(missing)} record(s) without one...")
        for _, data in missing:
            qid = resolve_wikidata_id(data)
            if qid:
                data["wikidata_id"] = qid
                upsert_provenance(data, "wikidata_id", "Wikidata", url=WIKIDATA_URL, license="CC0")
                resolved += 1
            time.sleep(REQUEST_DELAY)
        typer.echo(f"  resolved {resolved} new wikidata_id(s)")

    entities: dict[str, dict[str, Any]] = {}
    if not (skip_descriptions and skip_names):
        qids = sorted({str(d["wikidata_id"]) for _, d in records if d.get("wikidata_id")})
        typer.echo(f"Fetching {len(qids)} Wikidata entities...")
        for i in range(0, len(qids), 50):
            entities.update(wikidata_entities(qids[i : i + 50], UN_LANGS))
            time.sleep(REQUEST_DELAY)

    updated = 0
    for path, data in records:
        entity = entities.get(str(data.get("wikidata_id") or ""), {})
        if not skip_descriptions:
            enrich_descriptions(data, entity, force=force)
        if entity and not skip_names:
                enrich_other_names(data, entity)
                enrich_acronyms(data, entity)
        after = yaml.dump(data, sort_keys=True, allow_unicode=True)
        if after == originals[path]:
            continue
        stamp_last_verified(data)
        updated += 1
        rel = path.relative_to(ROOT)
        if dry_run:
            typer.echo(f"would update {rel}")
        else:
            path.write_text(
                yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
            typer.echo(f"updated {rel}")

    typer.echo(f"done: {updated} record(s) {'would be ' if dry_run else ''}updated; {resolved} wikidata_id(s) resolved")


if __name__ == "__main__":
    app()
