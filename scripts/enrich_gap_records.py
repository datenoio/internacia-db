#!/usr/bin/env python3
"""Enrich gap-analysis intblock records with standard metadata fields."""

from __future__ import annotations

import pathlib
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
INTBLOCKS = ROOT / "data" / "intblocks"

NEW_IDS = {
    "AMRO",
    "IPBES",
    "GGGI",
    "ICCROM",
    "UNIDROIT",
    "ESM",
    "ASEANPLUS3",
    "WARSAWPACT",
    "SEATO",
    "CENTO",
    "IPEF",
    "DANUBECOM",
    "PERSGA",
    "SACEP",
    "NDPHS",
    "AACB",
    "SEACEN",
    "CILSS",
    "LCBC",
    "CICOS",
    "OMVG",
    "OMVS",
    "OKACOM",
    "VBA",
    "ZAMCOM",
    "MGC",
    "C5PLUS1",
    "BBNJ",
    "EASTASIASUMMIT",
    "FIPIC",
    "V20",
    "SIDS",
    "COVAX",
    "AFRICACDC",
    "GHSA",
    "ATT",
    "CCM",
    "BUDCONV",
    "JCPOA",
    "OPENSKY",
    "GPAI",
    "FOCONLINE",
    "GFCE",
    "UNIGF",
}

# Curated metadata: wikidata_id, headquarters (city/country), acronyms, legal_status, topics
ENRICHMENT: dict[str, dict[str, Any]] = {
    "AMRO": {
        "wikidata_id": "Q28162743",
        "headquarters": {"city": "Singapore", "country": "SG"},
        "acronyms": [{"lang": "en", "value": "AMRO"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "economy", "name": "Economy"},
            {"key": "finance", "name": "Finance"},
        ],
    },
    "IPBES": {
        "wikidata_id": "Q3156270",
        "headquarters": {"city": "Bonn", "country": "DE"},
        "acronyms": [{"lang": "en", "value": "IPBES"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "environment", "name": "Environment"},
            {"key": "science", "name": "Science"},
        ],
    },
    "GGGI": {
        "wikidata_id": "Q5533568",
        "headquarters": {"city": "Seoul", "country": "KR"},
        "acronyms": [{"lang": "en", "value": "GGGI"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "environment", "name": "Environment"},
            {"key": "development", "name": "Development"},
        ],
    },
    "ICCROM": {
        "wikidata_id": "Q748789",
        "headquarters": {"city": "Rome", "country": "IT"},
        "acronyms": [{"lang": "en", "value": "ICCROM"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "culture", "name": "Culture"},
            {"key": "heritage", "name": "Heritage"},
        ],
    },
    "UNIDROIT": {
        "wikidata_id": "Q376658",
        "headquarters": {"city": "Rome", "country": "IT"},
        "acronyms": [{"lang": "en", "value": "UNIDROIT"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "law", "name": "Law"}],
    },
    "ESM": {
        "wikidata_id": "Q2040462",
        "headquarters": {"city": "Luxembourg", "country": "LU"},
        "acronyms": [{"lang": "en", "value": "ESM"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "finance", "name": "Finance"},
            {"key": "economy", "name": "Economy"},
        ],
    },
    "ASEANPLUS3": {
        "wikidata_id": "Q483654",
        "headquarters": {"city": "Jakarta", "country": "ID"},
        "acronyms": [{"lang": "en", "value": "ASEAN+3"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "political", "name": "Political"},
            {"key": "economy", "name": "Economy"},
        ],
    },
    "WARSAWPACT": {
        "wikidata_id": "Q41644",
        "headquarters": {"city": "Moscow", "country": "RU"},
        "acronyms": [{"lang": "en", "value": "Warsaw Pact"}],
        "legal_status": "treaty_organization",
        "topics": [
            {"key": "military", "name": "Military"},
            {"key": "political", "name": "Political"},
        ],
    },
    "SEATO": {
        "wikidata_id": "Q544296",
        "headquarters": {"city": "Bangkok", "country": "TH"},
        "acronyms": [{"lang": "en", "value": "SEATO"}],
        "legal_status": "treaty_organization",
        "topics": [{"key": "military", "name": "Military"}],
    },
    "CENTO": {
        "wikidata_id": "Q849092",
        "headquarters": {"city": "Ankara", "country": "TR"},
        "acronyms": [{"lang": "en", "value": "CENTO"}],
        "legal_status": "treaty_organization",
        "topics": [{"key": "military", "name": "Military"}],
    },
    "IPEF": {
        "wikidata_id": "Q115203763",
        "acronyms": [{"lang": "en", "value": "IPEF"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "trade", "name": "Trade"},
            {"key": "economy", "name": "Economy"},
        ],
    },
    "DANUBECOM": {
        "wikidata_id": "Q1194391",
        "headquarters": {"city": "Budapest", "country": "HU"},
        "acronyms": [{"lang": "en", "value": "DC"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "transport", "name": "Transport"},
            {"key": "water", "name": "Water"},
        ],
    },
    "PERSGA": {
        "wikidata_id": "Q3355622",
        "headquarters": {"city": "Jeddah", "country": "SA"},
        "acronyms": [{"lang": "en", "value": "PERSGA"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "environment", "name": "Environment"},
            {"key": "ocean", "name": "Ocean"},
        ],
    },
    "SACEP": {
        "wikidata_id": "Q7402525",
        "headquarters": {"city": "Colombo", "country": "LK"},
        "acronyms": [{"lang": "en", "value": "SACEP"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "environment", "name": "Environment"}],
    },
    "NDPHS": {
        "wikidata_id": "Q17021727",
        "headquarters": {"city": "Stockholm", "country": "SE"},
        "acronyms": [{"lang": "en", "value": "NDPHS"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "health", "name": "Health"}],
    },
    "AACB": {
        "wikidata_id": "Q4680743",
        "headquarters": {"city": "Dakar", "country": "SN"},
        "acronyms": [{"lang": "en", "value": "AACB"}],
        "legal_status": "association",
        "topics": [{"key": "finance", "name": "Finance"}],
    },
    "SEACEN": {
        "wikidata_id": "Q7569008",
        "headquarters": {"city": "Kuala Lumpur", "country": "MY"},
        "acronyms": [{"lang": "en", "value": "SEACEN"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "finance", "name": "Finance"},
            {"key": "research", "name": "Research"},
        ],
    },
    "CILSS": {
        "wikidata_id": "Q1419931",
        "headquarters": {"city": "Ouagadougou", "country": "BF"},
        "acronyms": [{"lang": "en", "value": "CILSS"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "food", "name": "Food"},
            {"key": "environment", "name": "Environment"},
        ],
    },
    "LCBC": {
        "wikidata_id": "Q1424268",
        "headquarters": {"city": "N'Djamena", "country": "TD"},
        "acronyms": [{"lang": "en", "value": "LCBC"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "CICOS": {
        "wikidata_id": "Q6042588",
        "headquarters": {"city": "Kinshasa", "country": "CD"},
        "acronyms": [{"lang": "en", "value": "CICOS"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "OMVG": {
        "wikidata_id": "Q3348668",
        "headquarters": {"city": "Dakar", "country": "SN"},
        "acronyms": [{"lang": "en", "value": "OMVG"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "OMVS": {
        "wikidata_id": "Q1326517",
        "headquarters": {"city": "Dakar", "country": "SN"},
        "acronyms": [{"lang": "en", "value": "OMVS"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "OKACOM": {
        "wikidata_id": "Q1424753",
        "headquarters": {"city": "Maun", "country": "BW"},
        "acronyms": [{"lang": "en", "value": "OKACOM"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "VBA": {
        "wikidata_id": "Q1634950",
        "headquarters": {"city": "Ouagadougou", "country": "BF"},
        "acronyms": [{"lang": "en", "value": "VBA"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "ZAMCOM": {
        "wikidata_id": "Q8073817",
        "headquarters": {"city": "Harare", "country": "ZW"},
        "acronyms": [{"lang": "en", "value": "ZAMCOM"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "water", "name": "Water"}],
    },
    "MGC": {
        "wikidata_id": "Q6808399",
        "acronyms": [{"lang": "en", "value": "MGC"}],
        "legal_status": "intergovernmental",
        "topics": [
            {"key": "political", "name": "Political"},
            {"key": "culture", "name": "Culture"},
        ],
    },
    "C5PLUS1": {
        "wikidata_id": "Q28158938",
        "acronyms": [{"lang": "en", "value": "C5+1"}],
        "legal_status": "diplomatic_platform",
        "topics": [{"key": "political", "name": "Political"}],
    },
    "BBNJ": {
        "wikidata_id": "Q120432689",
        "headquarters": {"city": "New York", "country": "US"},
        "acronyms": [{"lang": "en", "value": "BBNJ"}],
        "legal_status": "treaty",
        "topics": [
            {"key": "environment", "name": "Environment"},
            {"key": "ocean", "name": "Ocean"},
        ],
    },
    "EASTASIASUMMIT": {
        "wikidata_id": "Q618666",
        "headquarters": {"city": "Jakarta", "country": "ID"},
        "acronyms": [{"lang": "en", "value": "EAS"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "political", "name": "Political"}],
    },
    "FIPIC": {
        "wikidata_id": "Q21006981",
        "acronyms": [{"lang": "en", "value": "FIPIC"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "political", "name": "Political"}],
    },
    "V20": {
        "wikidata_id": "Q30943971",
        "acronyms": [{"lang": "en", "value": "V20"}],
        "legal_status": "coalition",
        "topics": [
            {"key": "climate", "name": "Climate"},
            {"key": "finance", "name": "Finance"},
        ],
    },
    "SIDS": {
        "wikidata_id": "Q170424",
        "headquarters": {"city": "New York", "country": "US"},
        "acronyms": [{"lang": "en", "value": "SIDS"}],
        "legal_status": "un_grouping",
        "topics": [
            {"key": "development", "name": "Development"},
            {"key": "climate", "name": "Climate"},
        ],
    },
    "COVAX": {
        "wikidata_id": "Q101437219",
        "headquarters": {"city": "Geneva", "country": "CH"},
        "acronyms": [{"lang": "en", "value": "COVAX"}],
        "legal_status": "partnership",
        "topics": [{"key": "health", "name": "Health"}],
    },
    "AFRICACDC": {
        "wikidata_id": "Q55384745",
        "headquarters": {"city": "Addis Ababa", "country": "ET"},
        "acronyms": [{"lang": "en", "value": "Africa CDC"}],
        "legal_status": "intergovernmental",
        "topics": [{"key": "health", "name": "Health"}],
    },
    "GHSA": {
        "wikidata_id": "Q22022249",
        "headquarters": {"city": "Washington", "country": "US"},
        "acronyms": [{"lang": "en", "value": "GHSA"}],
        "legal_status": "partnership",
        "topics": [{"key": "health", "name": "Health"}],
    },
    "ATT": {
        "wikidata_id": "Q546247",
        "headquarters": {"city": "Geneva", "country": "CH"},
        "acronyms": [{"lang": "en", "value": "ATT"}],
        "legal_status": "treaty",
        "topics": [
            {"key": "armscontrol", "name": "Arms Control"},
            {"key": "law", "name": "Law"},
        ],
    },
    "CCM": {
        "wikidata_id": "Q844393",
        "headquarters": {"city": "Geneva", "country": "CH"},
        "acronyms": [{"lang": "en", "value": "CCM"}],
        "legal_status": "treaty",
        "topics": [{"key": "armscontrol", "name": "Arms Control"}],
    },
    "BUDCONV": {
        "wikidata_id": "Q223800",
        "headquarters": {"city": "Strasbourg", "country": "FR"},
        "acronyms": [{"lang": "en", "value": "Budapest Convention"}],
        "legal_status": "treaty",
        "topics": [
            {"key": "law", "name": "Law"},
            {"key": "cybersecurity", "name": "Cybersecurity"},
        ],
    },
    "JCPOA": {
        "wikidata_id": "Q18785272",
        "headquarters": {"city": "Vienna", "country": "AT"},
        "acronyms": [{"lang": "en", "value": "JCPOA"}],
        "legal_status": "treaty",
        "topics": [{"key": "armscontrol", "name": "Arms Control"}],
    },
    "OPENSKY": {
        "wikidata_id": "Q622799",
        "headquarters": {"city": "Vienna", "country": "AT"},
        "acronyms": [{"lang": "en", "value": "Open Skies"}],
        "legal_status": "treaty",
        "topics": [{"key": "armscontrol", "name": "Arms Control"}],
    },
    "GPAI": {
        "wikidata_id": "Q97185282",
        "headquarters": {"city": "Paris", "country": "FR"},
        "acronyms": [{"lang": "en", "value": "GPAI"}],
        "legal_status": "partnership",
        "topics": [{"key": "technology", "name": "Technology"}],
    },
    "FOCONLINE": {
        "wikidata_id": "Q5504594",
        "headquarters": {"city": "The Hague", "country": "NL"},
        "acronyms": [{"lang": "en", "value": "FOC"}],
        "legal_status": "coalition",
        "topics": [{"key": "digital", "name": "Digital"}],
    },
    "GFCE": {
        "wikidata_id": "Q30337375",
        "headquarters": {"city": "The Hague", "country": "NL"},
        "acronyms": [{"lang": "en", "value": "GFCE"}],
        "legal_status": "partnership",
        "topics": [{"key": "cybersecurity", "name": "Cybersecurity"}],
    },
    "UNIGF": {
        "wikidata_id": "Q1194395",
        "headquarters": {"city": "Geneva", "country": "CH"},
        "acronyms": [{"lang": "en", "value": "IGF"}],
        "legal_status": "un_process",
        "topics": [{"key": "digital", "name": "Digital"}],
    },
}


def _wikidata_link(qid: str) -> dict[str, str]:
    return {"url": f"https://www.wikidata.org/wiki/{qid}", "type": "wikidata"}


EXTRA_BLOCKTYPES: dict[str, list[str]] = {
    "IPBES": ["biodiversity"],
    "BBNJ": ["biodiversity", "ocean"],
    "BUDCONV": ["cybersecurity"],
    "UNIGF": ["digital"],
    "GFCE": ["cybersecurity"],
    "GPAI": ["technology"],
    "FOCONLINE": ["digital"],
    "AFRICACDC": ["health"],
    "COVAX": ["health"],
    "GHSA": ["health"],
    "NDPHS": ["health"],
    "V20": ["climate"],
    "SIDS": ["climate"],
}

FIELD_ORDER = [
    "id",
    "blocktype",
    "status",
    "languages",
    "links",
    "name",
    "founded",
    "dissolved",
    "headquarters",
    "geographic_scope",
    "regions",
    "partof",
    "includes",
    "membership_count",
    "wikidata_id",
    "legal_status",
    "acronyms",
    "description",
    "tags",
    "topics",
    "other_names",
    "official_documents",
    "social_media",
]


def _order_fields(data: dict[str, Any]) -> dict[str, Any]:
    ordered: dict[str, Any] = {}
    for key in FIELD_ORDER:
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def enrich_record(data: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    block_id = data["id"]
    data.setdefault("languages", ["en"])

    qid = meta.get("wikidata_id")
    if qid:
        data["wikidata_id"] = qid
        links = list(data.get("links") or [])
        if not any(l.get("type") == "wikidata" for l in links if isinstance(l, dict)):
            links.append(_wikidata_link(qid))
        data["links"] = links

    for field in ("headquarters", "acronyms", "legal_status", "topics"):
        if field in meta:
            data[field] = meta[field]

    blocktypes = list(data.get("blocktype") or [])
    for bt in EXTRA_BLOCKTYPES.get(block_id, []):
        if bt not in blocktypes:
            blocktypes.append(bt)
    data["blocktype"] = blocktypes

    tags = set(data.get("tags") or [])
    tags.add(block_id)
    for ac in meta.get("acronyms") or []:
        tags.add(ac["value"])
    for topic in meta.get("topics") or []:
        tags.add(topic["key"])
    data["tags"] = sorted(tags)

    return _order_fields(data)


def main() -> None:
    updated = 0
    for path in INTBLOCKS.rglob("*.yaml"):
        data = yaml.safe_load(path.read_text()) or {}
        block_id = data.get("id")
        if block_id not in NEW_IDS:
            continue
        meta = ENRICHMENT.get(block_id)
        if not meta:
            print(f"WARN: no enrichment for {block_id}")
            continue
        data = enrich_record(data, meta)
        path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False))
        updated += 1
        print(f"updated {path.relative_to(ROOT)}")
    print(f"done: {updated} records")


if __name__ == "__main__":
    main()
