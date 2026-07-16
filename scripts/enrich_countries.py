#!/usr/bin/env python3
"""Enrich country YAML records with population, area, gini, timezones, and native_names."""

from __future__ import annotations

import time
import urllib.parse
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import typer
import yaml

from internacia_builder.http import fetch_json as _fetch_json

app = typer.Typer(help="Enrich country profile fields from World Bank and Wikidata")

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES_DIR = ROOT / "data" / "countries"
ZONE1970 = Path(__file__).resolve().parent / "data" / "zone1970.tab"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
REQUEST_DELAY = 0.1

WB_INDICATORS = {
    "population": ("SP.POP.TOTL", "World Bank"),
    "area": ("AG.LND.TOTL.K2", "World Bank"),
    "gini": ("SI.POV.GINI", "World Bank"),
}

MANUAL_WIKIDATA: dict[str, str] = {
    "PT": "Q45",
    "CO": "Q739",
    "AN": "Q25228",
    "KV": "Q1246",
    "JG": "Q84804",
    "NI": "Q811",
}

MANUAL_TIMEZONES: dict[str, list[str]] = {
    "AN": ["America/Curacao"],
    "JG": ["Europe/Guernsey", "Europe/Jersey"],
    "KV": ["Europe/Belgrade"],
}

TIMEZONE_NOT_APPLICABLE = frozenset({"BV", "HM", "AQ"})

UNINHABITED = frozenset({"BV", "HM", "GS", "IO", "TF"})

M49_URL = "https://unstats.un.org/unsd/methodology/m49/"

ADMINREGION_BY_REGION: dict[str, dict[str, str]] = {
    "LCN": {"id": "LAC", "value": "Latin America & Caribbean (developing only)"},
    "ECS": {"id": "ECA", "value": "Europe & Central Asia (developing only)"},
    "EAS": {"id": "EAP", "value": "East Asia & Pacific (developing only)"},
    "MEA": {"id": "MEA", "value": "Middle East & North Africa (excluding high income)"},
    "SSF": {"id": "SSA", "value": "Sub-Saharan Africa (excluding high income)"},
}

WB_INDICATOR_URLS = {
    "SP.POP.TOTL": "https://data.worldbank.org/indicator/SP.POP.TOTL",
    "AG.LND.TOTL.K2": "https://data.worldbank.org/indicator/AG.LND.TOTL.K2",
    "SI.POV.GINI": "https://data.worldbank.org/indicator/SI.POV.GINI",
}

LANG3_TO2 = {
    "eng": "en",
    "por": "pt",
    "spa": "es",
    "fra": "fr",
    "deu": "de",
    "rus": "ru",
    "ara": "ar",
    "zho": "zh",
    "jpn": "ja",
    "kor": "ko",
    "nld": "nl",
    "ita": "it",
}


def fetch_json(url: str) -> Any:
    return _fetch_json(url, user_agent="Internacia-DB Country Enricher/1.0", timeout=120)


def fetch_world_bank(indicator_id: str) -> dict[str, dict[str, Any]]:
    """Return iso3 -> {value, year} for latest observation (paginated)."""
    return _fetch_world_bank_all(indicator_id)


def _fetch_world_bank_all(indicator_id: str) -> dict[str, dict[str, Any]]:
    """Bulk fetch using paginated country/all requests."""
    return _fetch_world_bank_paginated(indicator_id)


def _latest_wb_row(rows: list[dict[str, Any]], iso3: str) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for row in rows:
        val = row.get("value")
        if val is None:
            continue
        year = int(row.get("date") or 0)
        code3 = row.get("countryiso3code") or iso3
        if best is None or year > best["year"]:
            best = {"value": val, "year": year, "iso3": code3}
    return best


def _fetch_world_bank_by_countries(
    indicator_id: str,
    iso3_codes: list[str],
) -> dict[str, dict[str, Any]]:
    """Fetch indicator values per ISO3 code (reliable when bulk endpoints fail)."""
    out: dict[str, dict[str, Any]] = {}
    for iso3 in sorted({c for c in iso3_codes if c}):
        url = (
            f"https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator_id}"
            f"?format=json&per_page=50"
        )
        try:
            payload = fetch_json(url)
        except Exception:
            time.sleep(REQUEST_DELAY)
            continue
        rows = payload[1] if len(payload) > 1 and payload[1] else []
        best = _latest_wb_row(rows, iso3)
        if best:
            out[str(best["iso3"])] = {"value": best["value"], "year": best["year"]}
        time.sleep(REQUEST_DELAY)
    return out


def _fetch_world_bank_paginated(indicator_id: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    page = 1
    per_page = 250
    while True:
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/{indicator_id}"
            f"?format=json&per_page={per_page}"
        )
        if page > 1:
            url += f"&page={page}"
        try:
            payload = fetch_json(url)
        except Exception:
            break
        rows = payload[1] if len(payload) > 1 and payload[1] else []
        if not rows:
            break
        for row in rows:
            val = row.get("value")
            if val is None:
                continue
            iso3 = row.get("countryiso3code") or ""
            if not iso3:
                continue
            year = int(row.get("date") or 0)
            prev = out.get(iso3)
            if prev is None or year > prev["year"]:
                out[iso3] = {"value": val, "year": year}
        meta = payload[0] if payload else {}
        if page >= int(meta.get("pages") or 1):
            break
        page += 1
        time.sleep(REQUEST_DELAY)
    return out


def parse_zone1970(path: Path) -> dict[str, list[str]]:
    mapping: dict[str, set[str]] = {}
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        codes, _, zones = parts[0], parts[1], parts[2]
        zone_list = zones.split()
        for code in codes.split(","):
            code = code.strip()
            if not code:
                continue
            mapping.setdefault(code, set()).update(zone_list)
    return {k: sorted(v) for k, v in mapping.items()}


def wikidata_batch(qids: list[str], langs: list[str]) -> dict[str, dict[str, Any]]:
    if not qids:
        return {}
    params = {
        "action": "wbgetentities",
        "ids": "|".join(qids),
        "props": "labels|aliases|claims",
        "languages": "|".join(langs[:10]) if langs else "en",
        "format": "json",
    }
    url = f"{WIKIDATA_API}?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    return data.get("entities") or {}


def wikidata_numeric_claim(entity: dict[str, Any], prop: str) -> float | None:
    claims = entity.get("claims") or {}
    prop_claims = claims.get(prop) or []
    if not prop_claims:
        return None
    try:
        val = prop_claims[0]["mainsnak"]["datavalue"]["value"]["amount"]
        return float(val.lstrip("+"))
    except (KeyError, TypeError, ValueError):
        return None


def infer_wb_classification(record: dict[str, Any]) -> dict[str, dict[str, str]] | None:
    """Infer World Bank-style region/income fields for entities the Bank does not classify."""
    sub = str(record.get("subregion") or "")
    continents = record.get("continents") or []
    cont = str(continents[0]) if continents else ""
    code = str(record.get("code", ""))

    if cont == "Antarctica" or code in {"AQ", "BV", "HM", "TF", "GS"}:
        return None

    lending: dict[str, str] = {"id": "NC", "value": "Not classified"}
    admin: dict[str, str] | None = None

    if sub == "Caribbean" or code in {"AI", "BL", "BQ", "GP", "MQ", "MS", "PM"}:
        region = {"id": "LCN", "value": "Latin America & Caribbean (all income levels)"}
        admin = {"id": "LAC", "value": "Latin America & Caribbean (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif sub in ("Northern Europe", "Southern Europe", "Western Europe", "Eastern Europe") or cont == "Europe":
        region = {"id": "ECS", "value": "Europe & Central Asia (all income levels)"}
        admin = {"id": "ECA", "value": "Europe & Central Asia (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif sub in ("Polynesia", "Australia and New Zealand", "Melanesia", "Micronesia") or cont == "Oceania":
        region = {"id": "EAS", "value": "East Asia & Pacific (all income levels)"}
        admin = {"id": "EAP", "value": "East Asia & Pacific (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif sub == "Eastern Asia" or code == "TW":
        region = {"id": "EAS", "value": "East Asia & Pacific (all income levels)"}
        admin = {"id": "EAP", "value": "East Asia & Pacific (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif sub in ("Northern Africa",) or code == "EH":
        region = {"id": "MEA", "value": "Middle East & North Africa (all income levels)"}
        admin = {"id": "MEA", "value": "Middle East & North Africa (excluding high income)"}
        income = {"id": "LMC", "value": "Lower middle income"}
    elif "Africa" in sub or cont == "Africa":
        region = {"id": "SSF", "value": "Sub-Saharan Africa (all income levels)"}
        admin = {"id": "SSA", "value": "Sub-Saharan Africa (excluding high income)"}
        income = {"id": "UMC", "value": "Upper middle income"} if code == "RE" else {"id": "LMC", "value": "Lower middle income"}
    elif sub == "South America" or cont == "South America":
        region = {"id": "LCN", "value": "Latin America & Caribbean (all income levels)"}
        admin = {"id": "LAC", "value": "Latin America & Caribbean (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"} if code == "GF" else {"id": "UMC", "value": "Upper middle income"}
    elif sub == "North America" or cont == "North America":
        region = {"id": "NAC", "value": "North America"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif sub == "Eastern Africa" or code == "IO":
        region = {"id": "MEA", "value": "Middle East & North Africa (all income levels)"}
        admin = {"id": "MEA", "value": "Middle East & North Africa (excluding high income)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif code == "UM":
        region = {"id": "EAS", "value": "East Asia & Pacific (all income levels)"}
        admin = {"id": "EAP", "value": "East Asia & Pacific (developing only)"}
        income = {"id": "NOC", "value": "High income: nonOECD"}
    elif code == "VA":
        region = {"id": "ECS", "value": "Europe & Central Asia (all income levels)"}
        admin = {"id": "ECA", "value": "Europe & Central Asia (developing only)"}
        income = {"id": "HIC", "value": "High income"}
    else:
        return None

    out: dict[str, dict[str, str]] = {"region": region, "incomeLevel": income, "lendingType": lending}
    if admin:
        out["adminregion"] = admin
    return out


def infer_adminregion_from_region(record: dict[str, Any]) -> dict[str, str] | None:
    """Map existing WB/M49 region to adminregion where the Bank omits it."""
    if record.get("adminregion"):
        return None
    if (record.get("incomeLevel") or {}).get("id") == "OEC":
        return None
    code = str(record.get("code", ""))
    if code in {"AQ", "BV", "HM", "TF", "GS"}:
        return None
    region_id = str((record.get("region") or {}).get("id") or "")
    return ADMINREGION_BY_REGION.get(region_id)


def classification_provenance_source(record: dict[str, Any], field: str) -> tuple[str, str]:
    prov = record.get("provenance") or []
    for entry in prov:
        if entry.get("field") == "region":
            src = str(entry.get("source") or "")
            if "M49" in src:
                return "UN M49 inference", M49_URL
    if field == "adminregion":
        return "World Bank regional complement", M49_URL
    return "World Bank", "https://data.worldbank.org/country"


def ensure_classification_provenance(record: dict[str, Any]) -> None:
    for field in ("region", "adminregion", "incomeLevel", "lendingType"):
        if not record.get(field):
            continue
        prov = record.get("provenance") or []
        if any(p.get("field") == field for p in prov):
            continue
        source, url = classification_provenance_source(record, field)
        upsert_provenance(record, field, source, url=url)


def build_native_names(entity: dict[str, Any], lang_codes: set[str]) -> dict[str, dict[str, str]]:
    labels = entity.get("labels") or {}
    aliases = entity.get("aliases") or {}
    native: dict[str, dict[str, str]] = {}
    for lang in sorted(lang_codes):
        label = (labels.get(lang) or {}).get("value")
        if not label:
            continue
        alias_list = aliases.get(lang) or []
        common = alias_list[0]["value"] if alias_list else label
        native[lang] = {"official": label, "common": common}
    if not native and labels.get("en"):
        en = labels["en"]["value"]
        native["en"] = {"official": en, "common": en}
    return native


def lang_codes_for_record(record: dict[str, Any]) -> set[str]:
    codes: set[str] = {"en"}
    for lang in record.get("languages") or []:
        if isinstance(lang, dict):
            c = str(lang.get("code", ""))
            codes.add(LANG3_TO2.get(c, c[:2] if len(c) >= 2 else c))
    for name in record.get("other_names") or []:
        if isinstance(name, dict) and name.get("id"):
            codes.add(str(name["id"]))
    return {c for c in codes if c and len(c) == 2}


def indicator_from_wb(
    wb_row: dict[str, Any] | None,
    source: str,
    source_id: str,
) -> dict[str, Any] | None:
    if not wb_row:
        return None
    val = wb_row["value"]
    if source_id == "SP.POP.TOTL":
        val = int(round(float(val)))
    else:
        val = float(val)
    return {
        "value": val,
        "year": wb_row["year"],
        "source": source,
        "source_id": source_id,
    }


def upsert_provenance(
    record: dict[str, Any],
    field: str,
    source: str,
    *,
    url: str = "",
    license: str = "",
    retrieved_at: str | None = None,
) -> None:
    retrieved_at = retrieved_at or date.today().isoformat()
    provenance = [p for p in (record.get("provenance") or []) if p.get("field") != field]
    entry: dict[str, str] = {
        "field": field,
        "source": source,
        "retrieved_at": retrieved_at,
    }
    if url:
        entry["url"] = url
    if license:
        entry["license"] = license
    provenance.append(entry)
    record["provenance"] = provenance


def sync_provenance_from_record(record: dict[str, Any]) -> None:
    today = date.today().isoformat()
    for field in ("population", "area", "gini"):
        ind = record.get(field)
        if not isinstance(ind, dict) or not ind.get("source"):
            continue
        src = str(ind["source"])
        sid = str(ind.get("source_id") or "")
        url = WB_INDICATOR_URLS.get(sid, "")
        if src == "Wikidata":
            url = "https://www.wikidata.org/"
        upsert_provenance(record, field, src, url=url, retrieved_at=today)

    if record.get("timezones") is not None:
        if record.get("timezone_status") == "not_applicable":
            upsert_provenance(record, "timezones", "not_applicable", retrieved_at=today)
        elif record.get("timezones"):
            upsert_provenance(
                record,
                "timezones",
                "IANA tzdata",
                url="https://data.iana.org/time-zones/tzdb/zone1970.tab",
                license="Public domain",
                retrieved_at=today,
            )

    if record.get("native_names"):
        upsert_provenance(
            record,
            "native_names",
            "Wikidata",
            url="https://www.wikidata.org/",
            license="CC0",
            retrieved_at=today,
        )


def enrich_record(
    record: dict[str, Any],
    wb: dict[str, dict[str, dict[str, Any]]],
    tz_map: dict[str, list[str]],
    wikidata_entities: dict[str, dict[str, Any]],
    *,
    force: bool = False,
) -> dict[str, Any]:
    code = record.get("code", "")
    iso3 = record.get("iso3code", "")
    qid = record.get("wikidata_id") or MANUAL_WIKIDATA.get(code, "")
    entity = wikidata_entities.get(qid, {}) if qid else {}

    if not record.get("wikidata_id") and qid:
        record["wikidata_id"] = qid

    if force or not record.get("population"):
        pop = indicator_from_wb(
            wb["population"].get(iso3),
            "World Bank",
            "SP.POP.TOTL",
        )
        if not pop and code in UNINHABITED:
            pop = {
                "value": 0,
                "year": 0,
                "source": "uninhabited",
                "source_id": "",
            }
        if not pop and entity:
            wd_pop = wikidata_numeric_claim(entity, "P1082")
            if wd_pop:
                pop = {
                    "value": int(wd_pop),
                    "year": 0,
                    "source": "Wikidata",
                    "source_id": "P1082",
                }
        if pop:
            record["population"] = pop

    if force or not record.get("area"):
        area = indicator_from_wb(
            wb["area"].get(iso3),
            "World Bank",
            "AG.LND.TOTL.K2",
        )
        if not area and entity:
            wd_area = wikidata_numeric_claim(entity, "P2046")
            if wd_area:
                area = {
                    "value": wd_area,
                    "year": 0,
                    "source": "Wikidata",
                    "source_id": "P2046",
                }
        if area:
            record["area"] = area

    if force or not record.get("gini"):
        gini = indicator_from_wb(
            wb["gini"].get(iso3),
            "World Bank",
            "SI.POV.GINI",
        )
        if gini:
            record["gini"] = gini

    if not record.get("region"):
        inferred = infer_wb_classification(record)
        if inferred:
            for field, value in inferred.items():
                if force or not record.get(field):
                    record[field] = value
            for field in inferred:
                source, url = ("UN M49 inference", M49_URL)
                upsert_provenance(record, field, source, url=url)

    admin = infer_adminregion_from_region(record)
    if admin and (force or not record.get("adminregion")):
        record["adminregion"] = admin
        source, url = classification_provenance_source(record, "adminregion")
        upsert_provenance(record, "adminregion", source, url=url)

    ensure_classification_provenance(record)

    if force or not record.get("timezones"):
        if code in TIMEZONE_NOT_APPLICABLE:
            record["timezones"] = []
            record["timezone_status"] = "not_applicable"
        elif code in MANUAL_TIMEZONES:
            record["timezones"] = MANUAL_TIMEZONES[code]
        else:
            zones = tz_map.get(code, [])
            record["timezones"] = zones
            if "timezone_status" in record and record["timezone_status"] == "not_applicable":
                del record["timezone_status"]

    if force or not record.get("native_names"):
        langs = lang_codes_for_record(record)
        if entity:
            record["native_names"] = build_native_names(entity, langs)

    if not record.get("common_names"):
        names: list[str] = []
        for candidate in (record.get("name"), record.get("official_name")):
            if candidate and candidate not in names:
                names.append(candidate)
        if entity:
            en_label = (entity.get("labels") or {}).get("en", {}).get("value")
            if en_label and en_label not in names:
                names.append(en_label)
        if names:
            record["common_names"] = names

    if record.get("borders") is None:
        record["borders"] = []

    if code == "UM":
        cc = record.setdefault("capital_city", {"name": "Washington DC"})
        cc.setdefault("lat", 38.8895)
        cc.setdefault("lng", -77.032)

    sync_provenance_from_record(record)
    return record


@app.command()
def enrich(
    code: str = typer.Option("", "--code", help="Single alpha-2 code to enrich"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print changes without writing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing enriched fields"),
) -> None:
    """Fetch external data and merge into country YAML sources."""
    typer.echo("Fetching World Bank indicators...")
    wb: dict[str, dict[str, dict[str, Any]]] = {}
    for key, (ind_id, _) in WB_INDICATORS.items():
        typer.echo(f"  {key} ({ind_id})...")
        try:
            wb[key] = fetch_world_bank(ind_id)
        except Exception as exc:
            typer.echo(f"  WARN: failed to fetch {ind_id}: {exc}", err=True)
            wb[key] = {}

    typer.echo("Loading IANA timezones...")
    tz_map = parse_zone1970(ZONE1970)

    paths = sorted(COUNTRIES_DIR.glob("*.yaml"))
    if code:
        paths = [COUNTRIES_DIR / f"{code.upper()}.yaml"]

    records: list[tuple[Path, dict[str, Any]]] = []
    qids: list[str] = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        qid = data.get("wikidata_id") or MANUAL_WIKIDATA.get(data.get("code", ""), "")
        if qid:
            qids.append(qid)
        records.append((path, data))

    typer.echo(f"Fetching Wikidata for {len(set(qids))} entities...")
    wikidata_entities: dict[str, dict[str, Any]] = {}
    unique_qids = sorted(set(qids))
    for i in range(0, len(unique_qids), 50):
        batch = unique_qids[i : i + 50]
        wikidata_entities.update(wikidata_batch(batch, ["en", "fr", "de", "es", "pt", "ru", "ar", "zh"]))
        time.sleep(REQUEST_DELAY)

    updated = 0
    for path, data in records:
        before = yaml.dump(data, sort_keys=True)
        data = enrich_record(
            data,
            wb,
            tz_map,
            wikidata_entities,
            force=force,
        )
        after = yaml.dump(data, sort_keys=True)
        if before == after:
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

    typer.echo(f"done: {updated} record(s) {'would be ' if dry_run else ''}updated")


@app.command("backfill-gini")
def backfill_gini(
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Fetch World Bank Gini for countries missing it."""
    missing_iso3: list[str] = []
    paths_by_iso3: dict[str, Path] = {}
    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if record.get("gini"):
            continue
        iso3 = str(record.get("iso3code") or "")
        if iso3:
            missing_iso3.append(iso3)
            paths_by_iso3[iso3] = path
    if not missing_iso3:
        typer.echo("done: 0 gini record(s) updated (none missing)")
        return
    typer.echo(f"Fetching World Bank gini for {len(missing_iso3)} countries...")
    wb_gini = _fetch_world_bank_by_countries("SI.POV.GINI", missing_iso3)
    typer.echo(f"  {len(wb_gini)} values returned")
    updated = 0
    for iso3, path in paths_by_iso3.items():
        record = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if record.get("gini"):
            continue
        gini = indicator_from_wb(wb_gini.get(iso3), "World Bank", "SI.POV.GINI")
        if not gini:
            continue
        record["gini"] = gini
        sync_provenance_from_record(record)
        updated += 1
        if dry_run:
            typer.echo(f"would update {path.relative_to(ROOT)}")
        else:
            path.write_text(
                yaml.dump(record, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
    typer.echo(f"done: {updated} gini record(s) {'would be ' if dry_run else ''}updated")


@app.command("backfill-classifications")
def backfill_classifications(
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Backfill adminregion and classification provenance without external fetches."""
    updated = 0
    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        before = yaml.dump(record, sort_keys=True)
        if not record.get("region"):
            inferred = infer_wb_classification(record)
            if inferred:
                for field, value in inferred.items():
                    if not record.get(field):
                        record[field] = value
                for field in inferred:
                    upsert_provenance(record, field, "UN M49 inference", url=M49_URL)
        admin = infer_adminregion_from_region(record)
        if admin:
            record["adminregion"] = admin
            source, url = classification_provenance_source(record, "adminregion")
            upsert_provenance(record, "adminregion", source, url=url)
        ensure_classification_provenance(record)
        after = yaml.dump(record, sort_keys=True)
        if before == after:
            continue
        updated += 1
        if dry_run:
            typer.echo(f"would update {path.relative_to(ROOT)}")
        else:
            path.write_text(
                yaml.dump(record, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
    typer.echo(f"done: {updated} classification record(s) {'would be ' if dry_run else ''}updated")


@app.command("backfill-provenance")
def backfill_provenance(
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Add provenance entries from existing enriched fields without re-fetching."""
    updated = 0
    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        before = yaml.dump(data.get("provenance"), sort_keys=True)
        sync_provenance_from_record(data)
        after = yaml.dump(data.get("provenance"), sort_keys=True)
        if before == after:
            continue
        updated += 1
        if dry_run:
            typer.echo(f"would update {path.relative_to(ROOT)}")
        else:
            path.write_text(
                yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
                encoding="utf-8",
            )
    typer.echo(f"done: {updated} provenance record(s) updated")


@app.command("check")
def check_enrichment(
    max_age_months: int = typer.Option(
        0,
        "--max-age-months",
        help="Stale provenance threshold in months (0 = read from countries_completeness.yaml)",
    ),
    fail_on_stale: bool = typer.Option(False, "--fail-on-stale", help="Exit 1 if any stale provenance"),
) -> None:
    """Report enrichment gaps and stale provenance (no network)."""
    import validate_countries as vc

    completeness_path = ROOT / "data" / "schemas" / "countries_completeness.yaml"
    cfg = yaml.safe_load(completeness_path.read_text(encoding="utf-8")) or {}
    threshold = max_age_months or int((cfg.get("provenance") or {}).get("max_age_months") or 12)

    stale = 0
    missing: dict[str, int] = defaultdict(int)
    track_fields = ("population", "area", "gini", "native_names", "centroid", "region", "adminregion")

    for path in sorted(COUNTRIES_DIR.glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rel = str(path.relative_to(ROOT))
        for w in vc.validate_provenance_freshness(record, rel, max_age_months=threshold):
            typer.echo(f"STALE: {w}")
            stale += 1
        for field in track_fields:
            if vc.is_null_field(record, field):
                missing[field] += 1

    total = len(list(COUNTRIES_DIR.glob("*.yaml")))
    typer.echo(f"provenance stale warnings: {stale} (threshold {threshold} months)")
    for field in track_fields:
        typer.echo(f"missing {field}: {missing[field]}/{total}")

    if fail_on_stale and stale:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
