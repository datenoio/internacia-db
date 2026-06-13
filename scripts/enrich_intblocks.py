#!/usr/bin/env python3
"""Enrich intblock YAML records from Wikidata.

Three enrichment tracks (all on by default, individually skippable):
  - wikidata_id backfill (high-confidence matches only)
  - description replacement for templated boilerplate
  - multilingual other_names and acronym aliases
Every enriched field records a provenance entry.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

app = typer.Typer(help="Enrich intblock records from Wikidata")

ROOT = Path(__file__).resolve().parents[1]
INTBLOCKS_DIR = ROOT / "data" / "intblocks"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_URL = "https://www.wikidata.org/"
REQUEST_DELAY = 0.1

# Languages backfilled into other_names (UN official languages + common extras).
UN_LANGS = ["en", "ar", "zh", "fr", "ru", "es", "de", "pt"]

# Boilerplate descriptions produced by earlier automated imports.
TEMPLATED_DESC = re.compile(
    r"^\s*(international entity focused on|an? international (organization|entity)|"
    r"regional (organization|entity) focused on|international organization for)",
    re.IGNORECASE,
)

WD_LINK = re.compile(r"wikidata\.org/(?:wiki|entity)/(Q[1-9][0-9]*)")


def fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "Internacia-DB Intblocks Enricher/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


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


def wikidata_entities(qids: list[str], langs: list[str]) -> dict[str, dict[str, Any]]:
    if not qids:
        return {}
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": "labels|aliases|descriptions",
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


def enrich_descriptions(record: dict[str, Any], entity: dict[str, Any], *, force: bool) -> bool:
    current = str(record.get("description") or "")
    if not (force or is_templated(current) or not current):
        return False
    desc = ((entity.get("descriptions") or {}).get("en") or {}).get("value")
    if not desc or len(desc) < 12:
        return False
    new_desc = clean_description(desc)
    if new_desc == current:
        return False
    record["description"] = new_desc
    upsert_provenance(record, "description", "Wikidata", url=WIKIDATA_URL, license="CC0")
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


@app.command()
def enrich(
    id: str = typer.Option("", "--id", help="Single intblock id to enrich"),
    limit: int = typer.Option(0, "--limit", help="Process at most N files (0 = all)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print changes without writing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing descriptions"),
    skip_wikidata: bool = typer.Option(False, "--skip-wikidata", help="Skip wikidata_id backfill"),
    skip_descriptions: bool = typer.Option(False, "--skip-descriptions", help="Skip description enrichment"),
    skip_names: bool = typer.Option(False, "--skip-names", help="Skip multilingual name/acronym enrichment"),
) -> None:
    """Fetch Wikidata data and merge it into intblock YAML sources."""
    paths = sorted(INTBLOCKS_DIR.rglob("*.yaml"))
    records: list[tuple[Path, dict[str, Any]]] = []
    originals: dict[Path, str] = {}
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if id and str(data.get("id")) != id:
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
        if entity:
            if not skip_descriptions:
                enrich_descriptions(data, entity, force=force)
            if not skip_names:
                enrich_other_names(data, entity)
                enrich_acronyms(data, entity)
        after = yaml.dump(data, sort_keys=True, allow_unicode=True)
        if after == originals[path]:
            continue
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
