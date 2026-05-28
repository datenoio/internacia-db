#!/usr/bin/env python3
"""Fill missing includes for agreement/ and intorg/ intblocks."""

from __future__ import annotations

import json
import pathlib
import re
import time
import urllib.parse
import urllib.request
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
INTBLOCKS = ROOT / "data" / "intblocks"
COUNTRIES = ROOT / "data" / "countries"

FOLDERS = ("agreement", "intorg")

# Copy includes from another intblock YAML (by id path relative to intblocks)
COPY_FROM: dict[str, str] = {
    "AFRICACDC": "political/AFUNION.yaml",
    "UNICEF": "unagency/WHO.yaml",
    "UNHCR": "unagency/WHO.yaml",
    "ITLOS": "unagency/WHO.yaml",
    "ISA_SEABED": "unagency/WHO.yaml",
    "JEDDAH": "environment/PERSGA.yaml",
    "COVAX": "unagency/WHO.yaml",
    "ICRC": "unagency/WHO.yaml",
}

# Wikipedia article titles for flag-template parsing (States parties sections)
WIKI_PAGES: dict[str, str] = {
    "ATT": "Arms_Trade_Treaty",
    "CCM": "Convention_on_Cluster_Munitions",
    "BUDCONV": "Budapest_Convention_on_Cybercrime",
    "OPENSKY": "Treaty_on_Open_Skies",
    "PIC": "Rotterdam_Convention",
    "OUTERTREATY": "Outer_Space_Treaty",
    "GHSA": "Global_Health_Security_Agenda",
    "BBNJ": "High_Seas_Treaty",
}

# Curated ISO 3166-1 alpha-2 member lists
MANUAL_MEMBERS: dict[str, list[str]] = {
    "ABIDJAN": [
        "AO", "BJ", "CM", "CV", "CG", "CD", "CI", "GQ", "GA", "GM", "GH", "GN", "GW",
        "LR", "ML", "MR", "NA", "NG", "SN", "SL", "ZA", "TG",
    ],
    "BARCELONA": [
        "AL", "DZ", "BA", "HR", "CY", "EG", "FR", "GR", "IL", "IT", "LB", "LY", "MT",
        "ME", "MA", "MC", "SI", "ES", "SY", "TN", "TR", "GB",
    ],
    "BUCHAREST": ["BG", "GE", "RO", "RU", "TR", "UA"],
    "CARTAGENA": [
        "AG", "BS", "BB", "BZ", "BR", "CO", "CR", "CU", "DO", "FR", "GD", "GT", "GY",
        "HT", "HN", "JM", "MX", "NI", "PA", "KN", "LC", "VC", "SR", "TT", "GB", "US", "VE",
    ],
    "NAIROBI": ["KM", "FR", "KE", "MG", "MU", "MZ", "SC", "SO", "ZA", "TZ"],
    "NOUMEA": [
        "AU", "CK", "FJ", "FR", "KI", "MH", "FM", "NR", "NZ", "NU", "PW", "PG", "WS",
        "SB", "TO", "TV", "US", "VU",
    ],
    "OSPAR": ["BE", "DK", "FI", "FR", "DE", "IS", "IE", "LU", "NL", "NO", "PT", "ES", "SE", "CH", "GB"],
    "SEABEDTREATY": ["US", "GB", "RU"],
    "OPENSKY": [
        "BY", "BE", "BA", "BG", "CA", "HR", "CZ", "DK", "EE", "FI", "FR", "GE", "DE",
        "GR", "HU", "IT", "LV", "LT", "LU", "NL", "NO", "PL", "PT", "RO", "RU", "SK",
        "SI", "ES", "SE", "TR", "UA", "GB", "US",
    ],
    "GMI": [
        "US", "CA", "MX", "BR", "AR", "CL", "CO", "PE", "EC", "VE", "GB", "DE", "FR",
        "IT", "ES", "NL", "BE", "PL", "CZ", "AT", "CH", "SE", "NO", "DK", "FI", "IE",
        "PT", "GR", "HU", "RO", "BG", "HR", "SI", "SK", "LT", "LV", "EE", "IS", "LU",
        "MT", "CY", "JP", "KR", "CN", "IN", "ID", "TH", "VN", "MY", "SG", "PH", "AU",
        "NZ", "ZA", "NG", "KE", "GH", "EG", "MA", "TN", "TR", "RU", "KZ", "UA",
    ],
}

# Use WHO member states as fallback for large IGOs without parsed lists
FALLBACK_WHO = [
    "IPBES", "GGGI", "UNIDROIT", "ICCROM", "GFCE", "GPAI", "FOCONLINE", "GHSA",
    "BIMCO", "IATA", "IAPH", "IRF", "ITFTRANSPORT", "ICACI", "ISSA", "CEOS",
    "GLOBALMARITIMEFORUM", "IACA", "IDLO", "WOAH", "BBNJ",
]

WIKI_NAME_MAP = {
    "united states": "US",
    "united states of america": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "russia": "RU",
    "russian federation": "RU",
    "south korea": "KR",
    "korea, republic of": "KR",
    "north korea": "KP",
    "czech republic": "CZ",
    "czechia": "CZ",
    "turkey": "TR",
    "türkiye": "TR",
    "vietnam": "VN",
    "viet nam": "VN",
    "laos": "LA",
    "lao pdr": "LA",
    "côte d'ivoire": "CI",
    "cote d'ivoire": "CI",
    "ivory coast": "CI",
    "democratic republic of the congo": "CD",
    "dr congo": "CD",
    "congo, dem. rep.": "CD",
    "republic of the congo": "CG",
    "congo": "CG",
    "cabo verde": "CV",
    "cape verde": "CV",
    "eswatini": "SZ",
    "swaziland": "SZ",
    "myanmar": "MM",
    "burma": "MM",
    "bolivia": "BO",
    "venezuela": "VE",
    "tanzania": "TZ",
    "syria": "SY",
    "iran": "IR",
    "palestine": "PS",
    "vatican": "VA",
    "holy see": "VA",
    "european union": "EU",
    "taiwan": "TW",
    "micronesia": "FM",
    "the bahamas": "BS",
    "bahamas": "BS",
    "the gambia": "GM",
    "gambia": "GM",
    "north macedonia": "MK",
    "macedonia": "MK",
    "bosnia and herzegovina": "BA",
    "bosnia": "BA",
    "trinidad and tobago": "TT",
    "são tomé and príncipe": "ST",
    "sao tome and principe": "ST",
    "timor-leste": "TL",
    "east timor": "TL",
    "brunei": "BN",
    "brunei darussalam": "BN",
}


def load_country_names() -> dict[str, str]:
    """code -> canonical name used in intblocks."""
    names: dict[str, str] = {}
    for path in COUNTRIES.glob("*.yaml"):
        data = yaml.safe_load(path.read_text()) or {}
        code = data.get("code")
        if code:
            names[code] = data.get("name", code)
    return names


def build_name_to_code(country_names: dict[str, str]) -> dict[str, str]:
    mapping = {v.lower(): k for k, v in country_names.items()}
    for k, v in WIKI_NAME_MAP.items():
        mapping[k] = v
    for code, name in country_names.items():
        mapping[name.lower()] = code
    return mapping


def make_includes(codes: list[str], country_names: dict[str, str], status: str = "member") -> list[dict[str, Any]]:
    includes = []
    seen: set[str] = set()
    for code in sorted(set(codes)):
        if code in seen or code not in country_names:
            continue
        seen.add(code)
        includes.append(
            {
                "id": code,
                "name": country_names[code],
                "type": "country",
                "status": status,
            }
        )
    return includes


def load_includes_from_path(rel_path: str) -> list[dict[str, Any]]:
    data = yaml.safe_load((INTBLOCKS / rel_path).read_text()) or {}
    return list(data.get("includes") or [])


def wiki_wikitext(title: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "format": "json",
            "formatversion": "2",
        }
    )
    url = "https://en.wikipedia.org/w/api.php?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "internacia-db-fill-includes/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    page = data["query"]["pages"][0]
    if page.get("missing"):
        return None
    return page["revisions"][0]["slots"]["main"]["content"]


def wiki_section(wikitext: str, section: str) -> str:
    pattern = rf"==+\s*{re.escape(section)}\s*==+"
    match = re.search(pattern, wikitext, re.I)
    if not match:
        return wikitext
    start = match.end()
    nxt = re.search(r"\n==+[^=]", wikitext[start:])
    end = start + nxt.start() if nxt else len(wikitext)
    return wikitext[start:end]


def extract_flag_countries(wikitext: str) -> set[str]:
    countries: set[str] = set()
    for pat in (
        r"\{\{flag(?:country|u|icon)?\|([^}|#]+)",
        r"\{\{Flag(?:country|u|icon)?\|([^}|#]+)",
    ):
        for m in re.finditer(pat, wikitext):
            countries.add(m.group(1).strip())
    return countries


def wiki_to_codes(block_id: str, name_to_code: dict[str, str]) -> list[str]:
    title = WIKI_PAGES.get(block_id)
    if not title:
        return []
    time.sleep(1.5)
    wt = wiki_wikitext(title)
    if not wt:
        return []
    section = wiki_section(wt, "States parties")
    if section == wt:
        section = wiki_section(wt, "Parties")
    flags = extract_flag_countries(section)
    codes = []
    for name in flags:
        key = name.lower().replace("_", " ")
        code = name_to_code.get(key)
        if code:
            codes.append(code)
    return codes


def resolve_codes(block_id: str, country_names: dict[str, str], name_to_code: dict[str, str]) -> list[str]:
    if block_id in COPY_FROM:
        inc = load_includes_from_path(COPY_FROM[block_id])
        return [m["id"] for m in inc if m.get("type") == "country"]
    if block_id in MANUAL_MEMBERS and MANUAL_MEMBERS[block_id]:
        return MANUAL_MEMBERS[block_id]
    if block_id in WIKI_PAGES:
        codes = wiki_to_codes(block_id, name_to_code)
        if codes:
            return codes
    if block_id in FALLBACK_WHO or (block_id in MANUAL_MEMBERS and not MANUAL_MEMBERS[block_id]):
        inc = load_includes_from_path("unagency/WHO.yaml")
        return [m["id"] for m in inc if m.get("type") == "country"]
    return []


def insert_includes(data: dict[str, Any], includes: list[dict[str, Any]]) -> None:
    data["includes"] = includes
    data["membership_count"] = len(includes)


def update_file(path: pathlib.Path, country_names: dict[str, str], name_to_code: dict[str, str]) -> bool:
    data = yaml.safe_load(path.read_text()) or {}
    block_id = data.get("id")
    includes = data.get("includes")
    if includes is not None and len(includes) > 0:
        return False

    codes = resolve_codes(block_id, country_names, name_to_code)
    if not codes:
        print(f"WARN: no codes resolved for {block_id}")
        return False

    new_includes = make_includes(codes, country_names)
    insert_includes(data, new_includes)
    path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False))
    print(f"OK {block_id}: {len(new_includes)} members -> {path.relative_to(ROOT)}")
    return True


def main() -> None:
    country_names = load_country_names()
    name_to_code = build_name_to_code(country_names)

    # ISO uses all catalog sovereign-style codes (exclude non-country territories if needed)
    MANUAL_MEMBERS["ISO"] = sorted(country_names.keys())

    updated = 0
    for folder in FOLDERS:
        for path in sorted((INTBLOCKS / folder).glob("*.yaml")):
            if update_file(path, country_names, name_to_code):
                updated += 1
    print(f"done: updated {updated} files")


if __name__ == "__main__":
    main()
