#!/usr/bin/env python3
"""One-off: import the ADB ARIC FTA database into data/trade_agreements/ (catalogue level).

Inputs are a snapshot taken outside the repository (untrusted data; run with ``python -I``):

- ``LIST_JSON``: the rows of the ``arrayFTA`` object embedded in
  https://aric.adb.org/database/fta-all, as ``[{"id", "title", "status", "year"}]``;
- ``DETAIL_JSON``: per-row fields parsed from https://aric.adb.org/fta.php?id=N&ssid=3
  (``members``, ``dates`` as ``[status label, date]`` pairs, ``short``).

Rows that are already in the registry (``MAPPED``) only get ``aric_id``; every other row
becomes a ``verification: catalogue`` record. EU member states listed on an ARIC page are
replaced by the ``EU`` intblock party. See ``openspec/specs/trade-agreements/spec.md``.

Usage: python -I scripts/oneoff/import_aric_ftas.py LIST_JSON DETAIL_JSON [--write]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-22"
SOURCE = "Asia Regional Integration Center (ADB), FTA database"

# ARIC row id -> existing registry id (records moved from intblocks or linked to one).
MAPPED = {
    1: "AFTA", 3: "AIFTA", 11: "ACFTA", 12: "MSGTA", 13: "APTA", 14: "ANZCERTA", 21: "INDIAMERCOSURPTA",
    34: "PICTA", 41: "SPARTECA", 46: "TPSEP", 48: "USAU", 52: "USSG", 58: "AKFTA", 62: "ECOTA", 63: "AJCEP",
    76: "CHAFTA", 80: "AANZFTA", 83: "SAFTA", 103: "CISFTA", 105: "TPSOIC", 108: "EUPACIFICEPA", 125: "USKR",
    134: "D8PTA", 162: "CNKR", 199: "EUKR", 211: "INDIAEFTA", 242: "PACERPLUS", 250: "EUSG", 258: "TPP",
    259: "EUVN", 264: "KRCENTRALAMERICA", 286: "EUJP", 292: "RCEP", 293: "AHKFTA", 308: "EAEU", 311: "EUNZ",
    366: "AUUK", 367: "UKNZ", 384: "CPTPP", 414: "UKJP", 424: "INUAE", 428: "AUINDIA", 442: "AUUAE",
    448: "CNEC", 449: "CNNI", 450: "CNRS", 355: "UKIN",
    # Tier 2: imported as catalogue records first, then given intblocks with official rosters.
    20: "EFTAKR", 22: "EFTASG", 198: "EFTAID", 207: "GCCSG", 256: "EFTAHK", 269: "EAEUVN", 294: "EFTAPH",
    317: "EAEUIR", 336: "EFTAGE", 401: "EAEURS", 426: "UKPACIFICEPA", 471: "EFTATR-1991",
    # Signed candidates checked against official sources (ARIC statuses were out of date).
    153: "GCCPK", 201: "GCCNZ", 228: "GCCKR", 331: "EAEUSG", 369: "PACALLSG", 385: "EAEUCN", 387: "MERCOSURSG",
    434: "AZTMTR",
}

# ARIC member names that differ from Internacia country names.
NAMES = {
    "Bolivarian Republic of Venezuela": "VE", "Egypt": "EG", "Eswatini": "SZ", "Hong Kong, China": "HK",
    "Iran, Islamic Republic of": "IR", "Kyrgyz Republic": "KG", "Lao People's Democratic Republic": "LA",
    "Macau, China": "MO", "Micronesia": "FM", "Federated States of": None, "Naoero": "NR",
    "People's Republic of China": "CN", "Republic of Korea": "KR", "Republic of Moldova": "MD",
    "Russian Federation": "RU", "Slovak Republic": "SK", "Czech Republic": "CZ", "Syrian Arab Republic": "SY",
    "Taipei,China": "TW", "Tanzania": "TZ", "Türkiye": "TR", "Viet Nam": "VN", "United Kingdom": "GB",
    "United States": "US", "Brunei Darussalam": "BN", "Myanmar": "MM", "Kosovo": "XK", "Palestine": "PS",
    "Faroe Islands": "FO", "Bosnia and Herzegovina": "BA", "North Macedonia": "MK", "Macedonia": "MK",
    "Timor-Leste": "TL", "Democratic People's Republic of Korea": "KP",
}
EU27 = set("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE".split())
# Blocs whose member states sign individually; a record with all of them gets the bloc as id prefix.
PREFIX_BLOCS = [
    ("ASEAN", set("BN KH ID LA MY MM PH SG TH VN".split())),
    ("EAEU", set("AM BY KZ KG RU".split())),
    ("EFTA", set("IS LI NO CH".split())),
    ("GCC", set("BH KW OM QA SA AE".split())),
    ("MERCOSUR", set("AR BR PY UY".split())),
    ("SACU", set("BW LS NA SZ ZA".split())),
    ("PACALL", set("CL CO MX PE".split())),
]
# Names in agreement titles -> parties, for members the ARIC page leaves out (it often lists
# only the ADB members). Blocs whose states sign individually expand to those states.
TITLE_NAMES = {
    "United States of America": ["US"], "United States": ["US"], "US": ["US"], "UK": ["GB"],
    "United Kingdom": ["GB"], "Kosovo": ["XK"], "Macedonia": ["MK"], "Palestine": ["PS"],
    "Republic of Korea": ["KR"], "Korea": ["KR"], "Hong Kong": ["HK"], "Hong-Kong": ["HK"], "Macao": ["MO"],
    "Hong Kong, China": ["HK"], "Hong-Kong, China": ["HK"], "Macau, China": ["MO"], "Macao, China": ["MO"],
    "Taipei,China": ["TW"], "Taipei, China": ["TW"], "People's Republic of China": ["CN"],
    "Russia": ["RU"], "Iran": ["IR"], "Laos": ["LA"], "Moldova": ["MD"], "Kyrgyz Republic": ["KG"],
    "Bosnia-Herzegovina": ["BA"], "New Caledonia": ["NC"], "Faroe Islands": ["FO"], "Venezuela": ["VE"],
    "European Union": ["EU"], "EU": ["EU"], "EC": ["EU"],
    "European Free Trade Association": ["IS", "LI", "NO", "CH"], "EFTA": ["IS", "LI", "NO", "CH"],
    "Eurasian Economic Union": ["AM", "BY", "KZ", "KG", "RU"], "EEU": ["AM", "BY", "KZ", "KG", "RU"],
    "Gulf Cooperation Council": ["BH", "KW", "OM", "QA", "SA", "AE"], "GCC": ["BH", "KW", "OM", "QA", "SA", "AE"],
    "MERCOSUR": ["AR", "BR", "PY", "UY"], "Pacific Alliance": ["CL", "CO", "MX", "PE"],
    "Southern African Customs Union": ["BW", "LS", "NA", "SZ", "ZA"],
}

# Hand-picked ids for rows whose parties do not give a short mechanical id.
IDS = {
    69: "GUAMFTA", 381: "FTAAP", 221: "CEPEA", 136: "EAFTA", 181: "SCOFTA", 64: "BIMSTECFTA",
    161: "CNJPKR", 434: "AZTMTR", 189: "HNSVTW", 437: "EAEUIN-RU",
    441: "ASEANGCC", 346: "ASEANEAEU", 277: "EFTATSOUZ", 265: "TSOUZNZ",
}
STATUS = {
    "Signed and In Effect": "in_force",
    "Signed but not yet In Effect": "signed",
    "Negotiations launched": "negotiating",
    "Proposed/Under consultation and study": "proposed",
    "(FA) signed": "signed",
}
# Discontinued rows: ARIC id -> registry status.
DISCONTINUED = {189: "terminated"}


def clean_date(value: str) -> str | None:
    m = re.fullmatch(r"(\d{4})(?:-(\d{1,2})(?:-(\d{1,2}))?)?", value.strip())
    if not m:
        return None
    year, month, day = m.groups()
    if not month or int(month) == 0:
        return year
    if not day or int(day) == 0:
        return f"{year}-{int(month):02d}"
    return f"{year}-{int(month):02d}-{int(day):02d}"


def agreement_type(title: str, status: str) -> str:
    t = title.lower()
    if status == "(FA) signed" or "framework agreement" in t or "trade and investment framework" in t:
        return "framework"
    if "digital" in t:
        return "digital"
    if re.search(r"compact of free association|green economy|strategic partnership|initiative on 21st century"
                 r"|economic and trade agreement between the government|trade and economic cooperation", t):
        return "other"
    if re.search(r"free trade|economic partnership|closer economic|economic cooperation agreement|comprehensive "
                 r"economic|trade area|\bfta\b|\bcepa\b|economic union", t):
        return "fta"
    if re.search(r"preferential|treaty of trade|trade agreement|trading arrangement|trade development|tariff", t):
        return "pta"
    return "fta"


def load_country_names() -> dict[str, str]:
    names: dict[str, str] = {}
    for path in (ROOT / "data" / "countries").glob("*.yaml"):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        for key in ("name", "official_name"):
            if record.get(key):
                names[str(record[key])] = str(record["code"])
        for other in record.get("common_names") or []:
            if isinstance(other, str):
                names[other] = str(record["code"])
    names.update({k: v for k, v in NAMES.items() if v})
    return names


def resolve_members(members: list[str], names: dict[str, str], title: str = "") -> tuple[list[dict], list[str]]:
    codes, unknown = [], []
    for name in members:
        if name in NAMES and NAMES[name] is None:
            continue
        code = names.get(name)
        if code is None:
            unknown.append(name)
        elif code not in codes:
            codes.append(code)
    parties = []
    # ARIC pages list the EU member states of the time (often 2007-2013: with the United
    # Kingdom, without Croatia), so 20 or more of today's members stand for the EU.
    if len(EU27 & set(codes)) >= 20:
        codes = [c for c in codes if c not in EU27]
        # Older ARIC pages list the United Kingdom among the EU member states.
        if not re.search(r"United Kingdom|\bUK\b", title):
            codes = [c for c in codes if c != "GB"]
        parties.append({"id": "EU", "type": "intblock"})
    parties.extend({"id": c, "type": "country"} for c in codes)
    return parties, unknown


def title_codes(title: str, names: dict[str, str]) -> list[str]:
    """Parties named in an ARIC title, in order of appearance (longest names first)."""
    text = (title.replace("[, China]", "").replace("[Republic of] ", "Republic of ").replace("&uuml;", "ü")
            .replace("\u2019", "'"))
    lexicon: dict[str, list[str]] = {k: [v] for k, v in names.items() if len(k) >= 4 or k.isupper()}
    lexicon.update(TITLE_NAMES)
    found: list[tuple[int, list[str]]] = []
    taken = [False] * len(text)
    for name in sorted(lexicon, key=len, reverse=True):
        for m in re.finditer(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text):
            if any(taken[m.start():m.end()]):
                continue
            for k in range(m.start(), m.end()):
                taken[k] = True
            found.append((m.start(), lexicon[name]))
    codes: list[str] = []
    for _, group in sorted(found):
        codes.extend(c for c in group if c not in codes)
    return codes


def make_id(row_id: int, parties: list[dict], taken: set[str], suffix: str) -> str:
    if row_id in IDS:
        return IDS[row_id]
    ids = [p["id"] for p in parties]
    countries = set(ids) - {"EU"}
    prefix, rest = "", sorted(countries)
    for bloc, members in PREFIX_BLOCS:
        if members <= countries and (len(countries - members) >= 1 or "EU" in ids):
            prefix, rest = bloc, sorted(countries - members)
            break
    if "EU" in ids:
        prefix, rest = (prefix + "EU", rest) if prefix else ("EU", rest)
    base = prefix + "".join(rest)
    candidate = base
    if candidate in taken:
        candidate = f"{base}-{suffix}"
    n = 2
    while candidate in taken:
        candidate = f"{base}-{suffix}{n}"
        n += 1
    return candidate


SUFFIX = {"digital": "DIGITAL", "framework": "FRAMEWORK", "other": "OTHER", "pta": "PTA", "fta": "FTA"}


def main(argv: list[str]) -> int:
    rows = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    details = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    write = "--write" in argv
    names = load_country_names()
    intblock_ids = {p.stem for p in (ROOT / "data" / "intblocks").rglob("*.yaml")}
    existing = {p.stem for p in REGISTRY.glob("*.yaml")}
    taken = intblock_ids | existing
    problems = 0
    created: dict[str, dict] = {}
    for row in sorted(rows, key=lambda r: int(r["id"])):
        rid = int(row["id"])
        url = f"https://aric.adb.org/fta.php?id={rid}&ssid=3"
        if rid in MAPPED:
            target = REGISTRY / f"{MAPPED[rid]}.yaml"
            text = target.read_text(encoding="utf-8")
            if "aric_id:" not in text:
                text = text.replace("\nverification:", f"\naric_id: {rid}\nverification:", 1)
                if write:
                    target.write_text(text, encoding="utf-8")
            continue
        detail = details.get(str(rid)) or {}
        members = list(detail.get("members") or [])
        parties, unknown = resolve_members(members, names, row["title"])
        listed = {p["id"] for p in parties} | ({c for c in EU27} if any(p["id"] == "EU" for p in parties) else set())
        # The title fills in only when the page names fewer than two parties: the page is the
        # better source, and titles such as "(now GCC-Singapore FTA)" name later agreements.
        extra = [c for c in title_codes(row["title"], names) if c not in listed] if len(parties) < 2 else []
        if extra:
            unknown = [n for n in unknown if n not in ("Palestinian territories",)]
            codes = [p["id"] for p in parties if p["type"] == "country"] + [c for c in extra if c != "EU"]
            has_eu = "EU" in extra or any(p["id"] == "EU" for p in parties)
            parties = ([{"id": "EU", "type": "intblock"}] if has_eu else []) + [
                {"id": c, "type": "country"} for c in dict.fromkeys(codes) if not (has_eu and c in EU27)
            ]
        if unknown or len(parties) < 2:
            print(f"! {rid} {row['title']}: unknown members {unknown}, {len(parties)} parties")
            problems += 1
            continue
        # "[Republic of] Korea", "Hong Kong [, China]": keep the bracketed words, drop the brackets.
        title = re.sub(r"\s+", " ", re.sub(r"\[([^\]]*)\]", r"\1", row["title"])).replace(" ,", ",").strip()
        kind = agreement_type(title, row["status"])
        if row["status"] == "Discontinued":
            status = DISCONTINUED.get(rid, "abandoned")
        else:
            status = STATUS[row["status"]]
        dates = {label: clean_date(value) for label, value in detail.get("dates") or []}
        record: dict = {}
        tokens = re.findall(r"\b(CEPA|CECA|CEP|EPA|PTA|DEA|DTA|DPA|SPA|SPCA|TIFA|GEA)\b", f"{detail.get('short') or ''} {row['title']}")
        agreement_id = make_id(rid, parties, taken, tokens[0] if tokens else SUFFIX[kind])
        taken.add(agreement_id)
        record["id"] = agreement_id
        record["name"] = title
        short = detail.get("short")
        if short and re.fullmatch(r"[A-Z][A-Z0-9-]{1,14}", short):
            record["acronyms"] = [{"lang": "en", "value": short}]
        elif short and short != title:
            record["other_names"] = [{"lang": "en", "name": short}]
        record["agreement_type"] = kind
        record["status"] = status
        signed = dates.get("Signed but not yet In Effect") or dates.get("(FA) signed")
        in_force = dates.get("Signed and In Effect")
        # Some ARIC pages carry no dates; the list gives the year of the current status.
        year = clean_date(str(row.get("year") or "")) if row.get("year") else None
        if status == "in_force" and not in_force:
            in_force = year
        if status == "signed" and not signed:
            signed = year
        if status in ("signed", "in_force", "terminated", "abandoned") and signed:
            record["signed"] = signed
        if status in ("in_force", "terminated") and in_force:
            record["in_force"] = in_force
        if status == "terminated":
            record["ended"] = str(row.get("year") or "")
        record["parties"] = parties
        record["aric_id"] = rid
        history = [
            f"{label.lower()} {value}"
            for label, value in dates.items()
            if value and label in ("Proposed/Under consultation and study", "Negotiations launched")
        ]
        if history:
            record["notes"] = "ADB ARIC dates: " + "; ".join(history) + "."
        record["verification"] = "catalogue"
        record["last_verified"] = RETRIEVED
        record["provenance"] = [
            {"field": "parties", "source": SOURCE, "url": url, "retrieved_at": RETRIEVED},
            {"field": "status", "source": SOURCE, "url": url, "retrieved_at": RETRIEVED},
        ]
        created[agreement_id] = record
        if write:
            (REGISTRY / f"{agreement_id}.yaml").write_text(
                yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8"
            )
    print(f"created {len(created)}, mapped {len(MAPPED)}, problems {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
