#!/usr/bin/env python3
"""One-off: walk the WTO RTA Information System into data/trade_agreements/ (catalogue level).

Input is the XLSX export of every RTA, https://rtais.wto.org/UI/ExportAllRTAList.aspx (sheet
``AllRTAs``: one row per RTA ID, goods and services dates side by side). The file is untrusted
data: keep it outside the repository and run this script with ``python -I``.

Each row gets one result, checked in this order:

- ``skipped``: ``SKIP`` (a party is not in data/countries), or an early announcement that no
  registry record matches (early announcements are out of scope for this pass);
- ``mapped``: a record whose ``wto_rta_id`` is the row's RTA ID; ``MAPPED`` (checked by hand);
  the one record, or the intblock a record links, that cites the row's RTA-IS ID card; or the
  one record with the same parties, a compatible type and a compatible status (``auto``);
- ``accession`` / ``same_instrument``: an accession to an agreement (``ACCESSION``) or another
  RTA ID of an instrument that already has one (``SAME_INSTRUMENT``); no ``wto_rta_id``;
- ``new``: a new record, linked to an existing intblock (``WTO_IS_INTBLOCK``, ``official``) or
  a ``verification: catalogue`` record with the parties WTO lists.

Mapped records get ``wto_rta_id``. A mapped ``catalogue`` record whose status WTO contradicts
(in force here, signed or negotiating in the record; inactive here, in force in the record)
takes the WTO status and dates. New catalogue records follow ``import_aric_ftas.py``: ids from
sorted alpha-2 codes, the EU as one ``intblock`` party, and the member states of a bloc WTO lists
as one party (EFTA, EAEU, GCC, MERCOSUR, SACU, ASEAN, Pacific Alliance) listed one by one, as
members at the date of signature, with the bloc id first in the record id. Older EC agreements
list the EC member states of the time; they become the ``EU`` party. See
``openspec/changes/add-trade-agreements-registry``.

Usage: python -I scripts/oneoff/import_wto_rtais.py EXPORT_XLSX [--write] [--report TSV]
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-22"
SOURCE = "WTO Regional Trade Agreements Information System"
CARD = "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid={}"
PARTY_STATUSES = {
    "member", "founding_member", "former_member", "participant", "associate", "associate_member",
    "associated", "contributor", "recipient",
}
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]

# WTO member names that differ from Internacia country names.
NAMES = {
    "Bahrain, Kingdom of": "BH", "Bolivia, Plurinational State of": "BO", "Korea, Republic of": "KR",
    "Kuwait, the State of": "KW", "Lebanese Republic": "LB", "Saudi Arabia, Kingdom of": "SA",
    "Moldova, Republic of": "MD", "Venezuela, Bolivarian Republic of": "VE", "Chinese Taipei": "TW",
    "Hong Kong, China": "HK", "Macao, China": "MO", "Kosovo (under UNSC res. 1244)": "XK", "The Gambia": "GM",
    "Sao Tomé and Principe": "ST", "Netherlands, Kingdom of, with respect to Aruba": "AW",
    "Netherlands Antilles": "AN", "Falkland Islands (Islas Malvinas)": "FK",
    "British Overseas Territory of Saint Helena, Ascension and Tristan da Cunha": "SH",
    "Wallis and Futuna Islands": "WF", "Virgin Islands, British": "VG", "Micronesia, Federated States of": "FM",
    "Korea, Democratic People's Republic of": "KP", "Iran": "IR", "Türkiye": "TR", "Kyrgyz Republic": "KG",
    "Lao People's Democratic Republic": "LA", "Slovak Republic": "SK", "Czech Republic": "CZ",
    "Russian Federation": "RU", "Syrian Arab Republic": "SY", "Viet Nam": "VN", "United Kingdom": "GB",
    "United States of America": "US", "Brunei Darussalam": "BN", "Egypt": "EG", "Eswatini": "SZ",
    "Tanzania": "TZ", "Côte d'Ivoire": "CI", "Cabo Verde": "CV", "Congo": "CG",
    "Democratic Republic of the Congo": "CD", "North Macedonia": "MK", "Palestine": "PS",
    "Saint Kitts and Nevis": "KN", "Yemen": "YE",
}
# Short names in RTA names, for early announcements that list no signatories.
TITLE_NAMES = {
    "EU": ["EU"], "US": ["US"], "Korea": ["KR"], "GCC": "GCC", "EFTA": "EFTA", "MERCOSUR": "MERCOSUR",
    "SACU": "SACU", "Russian Federation": ["RU"], "Belarus": ["BY"], "Kazakhstan": ["KZ"],
}
# The EC/EU member states and their date of accession (the United Kingdom left on 2020-01-31).
EC_JOINED = {
    **dict.fromkeys(["BE", "DE", "FR", "IT", "LU", "NL"], "1958-01-01"),
    **dict.fromkeys(["DK", "GB", "IE"], "1973-01-01"), "GR": "1981-01-01", "ES": "1986-01-01", "PT": "1986-01-01",
    **dict.fromkeys(["AT", "FI", "SE"], "1995-01-01"),
    **dict.fromkeys(["CY", "CZ", "EE", "HU", "LV", "LT", "MT", "PL", "SK", "SI"], "2004-05-01"),
    "BG": "2007-01-01", "RO": "2007-01-01", "HR": "2013-07-01",
}
# First words of country names that do not identify a country ("Republic of Austria").
GENERIC_WORDS = {
    "Republic", "Federal", "Kingdom", "United", "State", "Democratic", "Islamic", "People's", "Commonwealth",
    "Principality", "Grand", "Union", "Socialist", "Federation", "Independent", "Plurinational", "Bolivarian",
    "Oriental", "Hashemite", "Sultanate", "Swiss", "Confederation", "Special", "Great", "Federated", "Saint",
}
EC_NAME = re.compile(r"\b(EC|EU|EEC)\b|European (Union|Communit)")

# Blocs WTO lists as one party whose member states sign individually: (WTO name, prefix,
# [(state, joined, left)]). A record lists the members at the date of signature; a member
# that left the bloc later gets ``left``.
BLOCS = [
    ("ASEAN Free Trade Area (AFTA)", "ASEAN", [
        ("BN", "1984", None), ("ID", "1967", None), ("MY", "1967", None), ("PH", "1967", None),
        ("SG", "1967", None), ("TH", "1967", None), ("VN", "1995-07-28", None), ("LA", "1997-07-23", None),
        ("MM", "1997-07-23", None), ("KH", "1999-04-30", None)]),
    ("Eurasian Economic Union (EAEU)", "EAEU", [
        ("BY", "2015", None), ("KZ", "2015", None), ("RU", "2015", None), ("AM", "2015", None),
        ("KG", "2015", None)]),
    ("European Free Trade Association (EFTA)", "EFTA", [
        ("AT", "1960", "1995-01-01"), ("DK", "1960", "1973-01-01"), ("GB", "1960", "1973-01-01"),
        ("NO", "1960", None), ("PT", "1960", "1986-01-01"), ("SE", "1960", "1995-01-01"), ("CH", "1960", None),
        ("IS", "1970-03-01", None), ("FI", "1986-01-01", "1995-01-01"), ("LI", "1991-09-01", None)]),
    ("Gulf Cooperation Council (GCC)", "GCC", [(c, "1981", None) for c in ("BH", "KW", "OM", "QA", "SA", "AE")]),
    ("Southern Common Market (MERCOSUR)", "MERCOSUR", [(c, "1991", None) for c in ("AR", "BR", "PY", "UY")]),
    ("Southern African Customs Union (SACU)", "SACU", [(c, "1970", None) for c in ("BW", "LS", "NA", "SZ", "ZA")]),
    ("Pacific Alliance", "PACALL", [(c, "2011", None) for c in ("CL", "CO", "MX", "PE")]),
]
BLOC_BY_PREFIX = {b[1]: b for b in BLOCS}
LEFT_FOR_EU = "Left EFTA on joining the European Communities."

# RTA ID -> registry id, checked by hand (the parties or the name differ from the record's).
MAPPED = {
    4: "CEFTA", 16: "GAFTA", 35: "TNTR", 45: "SADCFTA", 94: "EAC", 120: "EUCU", 121: "COMESA", 124: "SAPTA",
    127: "CAN", 128: "ECOTA", 147: "PTN", 151: "CACM", 152: "EFTA", 582: "PICTA", 762: "CISFTA", 909: "EAEU",
    1086: "AfCFTA", 1276: "AUUAE", 732: "INNZ", 1103: "GBGE", 1117: "GBUA", 130: "MERCOSUR", 683: "PACERPLUS",
}
# Hand-mapped catalogue records that WTO shows in force although the record says abandoned:
# negotiations that were later resumed and concluded under the same name.
RESUMED = {732}
# RTA ID -> existing intblock: the row becomes a new registry record linked to it.
WTO_IS_INTBLOCK = {17: "CCASG", 36: "ECOWAS", 114: "EEA", 135: "ALADI", 141: "CARICOM"}
# Accessions: RTA ID -> registry id of the agreement acceded to.
ACCESSION = {
    6: "EUCU", 52: "EUCU", 123: "EUCU", 132: "EUCU", 137: "EUCU", 145: "EUCU", 869: "EUCU",
    46: "APTA", 54: "CEFTA-1992", 216: "CEFTA-1992", 217: "CEFTA-1992", 218: "CEFTA-1992", 149: "EFTA",
    838: "EAC", 878: "CACM", 907: "EUANDEAN", 910: "EAEU", 922: "EAEU", 948: "SADCFTA", 950: "EFTACRPA",
    966: "SAFTA", 983: "COMESA", 1009: "COMESA", 1026: "ALADI", 1075: "COMESA", 1093: "EUPACIFICEPA",
    1094: "EUPACIFICEPA", 1144: "UKPACIFICEPA", 1145: "UKPACIFICEPA", 1148: "EUESAEPA", 1218: "CPTPP",
}
# Another RTA ID of an instrument that already has one: RTA ID -> registry id.
SAME_INSTRUMENT: dict[int, str] = {}
# RTA ID -> reason for leaving the row out.
SFRY = "a party, the Socialist Federal Republic of Yugoslavia, is not in data/countries"
CSFR = "a party, Czechoslovakia (dissolved 1993), is not in data/countries"
SKIP = {
    150: SFRY, 284: SFRY, 287: CSFR, 306: CSFR,
    201: "WTO lists no signatories; the parties (North Borneo, Sarawak, Brunei) were colonial territories",
    308: "a party, the German Democratic Republic, is not in data/countries (WTO lists it as Germany)",
}
# Parties WTO leaves out of the signatory list (a predecessor state that is not in data/countries).
EXTRA_PARTIES = {
    335: [{"id": "RS", "type": "country", "note": "Signed by Serbia and Montenegro, whose legal personality Serbia continues."}],
    344: [{"id": "RS", "type": "country", "note": "Signed by Serbia and Montenegro, whose legal personality Serbia continues."}],
    277: [{"id": "SY", "type": "country", "note": "Missing from the WTO RTA-IS signatory list."}],
}
# RTA ID -> registry ids the auto-match must not use (same parties, another instrument).
NOT_SAME = {214: {"CACM"}, 857: {"TSOUZ", "EAEU"}, 873: {"INTH"}, 150: {"EGIN"}}
# Inactive RTA ID -> registry id of the agreement that replaced it (status superseded).
SUPERSEDED_BY = {
    20: "MXCENTRALAMERICA", 24: "MXCENTRALAMERICA", 25: "MXCENTRALAMERICA", 26: "MXCENTRALAMERICA",
    32: "MXCENTRALAMERICA", 122: "USMCA", 126: "AFTA", 129: "EFTATR", 214: "CACM", 316: "CCASG",
    324: "ALADI", 857: "EAEU", 694: "CAUA", 33: "EUCL", 61: "BATR", 117: "FOIS", 200: "ANZCERTA", 212: "NAFTA",
    213: "CARICOM", 366: "YAOUNDE-1969", 367: "LOME-1975", 368: "LOME-1979", 369: "LOME-1984", 1104: "GBISLINO",
}
# Hand-picked ids for new records whose parties do not give a short id.
IDS = {
    99: "CISFTA-1994", 126: "AFTA-CEPT", 148: "EUOCT", 190: "AFRICANCOMMONMARKET", 198: "ARABCOMMONMARKET",
    214: "CENTRALAMERICANFTA-1958", 215: "CEFTA-1992", 263: "EUOCT-1971", 313: "FINEFTA", 316: "GCCUEA",
    324: "LAFTA", 764: "DOCENTRALAMERICA", 857: "BYKZRU-CU", 863: "MXCENTRALAMERICA", 1098: "UKCENTRALAMERICA",
    106: "EURASEC", 213: "CARIFTA", 288: "EFTAEE", 298: "UDECAMEROON", 300: "BAFTA", 366: "YAOUNDE-1963",
    367: "YAOUNDE-1969", 368: "LOME-1975", 369: "LOME-1979", 370: "LOME-1984", 579: "CEZ", 1096: "UKANDEAN",
    1097: "UKCARIFORUM", 1101: "UKESA", 1171: "ATISA", 1241: "AETR-CEPA",
}
# EC agreements whose RTA name does not say EC (the EC member states become the EU party).
EC_ROWS = {199, 366, 367, 368, 369, 370}
# Agreement type when the WTO notification does not describe the instrument.
TYPE_FIX = {114: "fta", 368: "preference_scheme", 369: "preference_scheme", 370: "preference_scheme"}
# Notes for new records: legal facts from the RTA-IS remarks.
NOTES = {
    114: "WTO RTA-IS records the EEA Agreement under GATS Article V only; trade in goods between the EFTA States and the EU is notified under the earlier bilateral agreements.",
    20: "Ended when the Mexico-Central America Free Trade Agreement entered into force (WTO document WT/REG/GEN/N/7).",
    24: "Ended when the Mexico-Central America Free Trade Agreement entered into force (WTO document WT/REG/GEN/N/7).",
    25: "Ended when the Mexico-Central America Free Trade Agreement entered into force (WTO document WT/REG/GEN/N/7).",
    26: "Ended when the Mexico-Central America Free Trade Agreement entered into force (WTO document WT/REG/GEN/N/7).",
    32: "Ended when the Mexico-Central America Free Trade Agreement entered into force (WTO document WT/REG/GEN/N/7).",
    62: "Terminated on the accession of Croatia to the EU on 1 July 2013 (WTO document WT/REG/GEN/N/6).",
    67: "Terminated on the accession of Croatia to the EU on 1 July 2013 (WTO document WT/REG/GEN/N/6).",
    76: "Terminated on the accession of Croatia to the EU on 1 July 2013 (WTO document WT/REG/GEN/N/6).",
    368: "Non-reciprocal trade preferences of the EEC for the ACP States; WTO RTA-IS records it as an FTA.",
    369: "Non-reciprocal trade preferences of the EEC for the ACP States; WTO RTA-IS records it as an FTA.",
    370: "Non-reciprocal trade preferences of the EEC for the ACP States; WTO RTA-IS records it as an FTA.",
    126: "Agreement on the Common Effective Preferential Tariff (CEPT) Scheme for the ASEAN Free Trade Area; replaced by the ASEAN Trade in Goods Agreement.",
    579: "Ukraine's withdrawal took effect on 21 July 2023 (WTO RTA-IS).",
    671: "Suspended from 1 July 2022 (WTO documents WT/REG267/N/2 and S/C/N/500/Add.1).",
    694: "Ended when the modernized Canada-Ukraine Free Trade Agreement of 2023 entered into force (WTO document series WT/REG486).",
}

TYPES = {
    "FTA": "fta", "FTA & EIA": "fta", "CU": "customs_union", "CU & EIA": "customs_union", "PSA": "pta",
    "PSA & EIA": "pta", "EIA": "services",
}
# Registry agreement types a WTO row can map to.
COMPATIBLE = {
    "fta": {"fta", "customs_union", "pta"}, "customs_union": {"customs_union", "fta"},
    "pta": {"pta", "fta"}, "services": {"services", "fta"},
}


# --- input -----------------------------------------------------------------------------------

def read_export(path: Path) -> list[dict]:
    """Rows of the ``AllRTAs`` sheet as dicts, read with the standard library only."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    with zipfile.ZipFile(path) as z:
        shared = [
            "".join(t.text or "" for t in si.iter(f"{ns}t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{ns}si")
        ]
        targets = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheet = next(
            s for s in ET.fromstring(z.read("xl/workbook.xml")).find(f"{ns}sheets") if s.get("name") == "AllRTAs"
        )
        target = targets[sheet.get(rel)].lstrip("/")
        root = ET.fromstring(z.read(target if target.startswith("xl/") else f"xl/{target}"))
    table = []
    for row in root.iter(f"{ns}row"):
        cells = {}
        for c in row.findall(f"{ns}c"):
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            v = c.find(f"{ns}v")
            if c.get("t") == "s" and v is not None:
                cells[col - 1] = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                cells[col - 1] = "".join(t.text or "" for t in c.iter(f"{ns}t"))
            else:
                cells[col - 1] = v.text if v is not None else None
        table.append([cells.get(i) for i in range(max(cells) + 1)] if cells else [])
    header = table[0]
    return [dict(zip(header, (r + [None] * len(header))[: len(header)], strict=True)) for r in table[1:] if r]


def excel_date(value) -> str | None:
    if value in (None, ""):
        return None
    return (date(1899, 12, 30) + timedelta(days=int(float(value)))).isoformat()


def earliest(*values) -> str | None:
    dates = [d for d in (excel_date(v) for v in values) if d]
    return min(dates) if dates else None


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def ordered(record: dict) -> dict:
    """Schema field order; a linked record names its intblock right after its id."""
    keys = [k for k in FIELD_ORDER if k in record]
    if "intblock" in record:
        keys.remove("intblock")
        keys.insert(1, "intblock")
    return {k: record[k] for k in keys}


# --- registry --------------------------------------------------------------------------------

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
    names.update(NAMES)
    return names


def load_intblocks() -> dict[str, dict]:
    return {
        str(r["id"]): r
        for r in (yaml.safe_load(p.read_text(encoding="utf-8")) for p in (ROOT / "data" / "intblocks").rglob("*.yaml"))
        if isinstance(r, dict) and r.get("id")
    }


def load_registry() -> dict[str, dict]:
    return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(REGISTRY.glob("*.yaml"))}


def record_parties(record: dict, intblocks: dict[str, dict]) -> frozenset[str]:
    if record.get("intblock"):
        block = intblocks.get(str(record["intblock"])) or {}
        return frozenset(
            str(i["id"]) for i in block.get("includes") or []
            if isinstance(i, dict) and i.get("status") in PARTY_STATUSES
        )
    return frozenset(str(p["id"]) for p in record.get("parties") or [])


def cited_rta_ids(record: dict, intblocks: dict[str, dict]) -> set[int]:
    texts = [yaml.safe_dump(record)]
    if record.get("intblock") and record["intblock"] in intblocks:
        texts.append(yaml.safe_dump(intblocks[record["intblock"]]))
    return {int(n) for t in texts for n in re.findall(r"rtaid=(\d+)", t)}


# --- parties ---------------------------------------------------------------------------------

def bloc_states(prefix: str, signed: str | None) -> list[dict]:
    parties = []
    for state, joined, left in BLOC_BY_PREFIX[prefix][2]:
        if signed and (joined > signed or (left and left <= signed)):
            continue
        party = {"id": state, "type": "country"}
        if left:
            party["left"] = left
            if prefix == "EFTA" and EC_JOINED.get(state) == left:
                party["note"] = LEFT_FOR_EU
        parties.append(party)
    return parties


def named_in(code: str, rta_name: str, names: dict[str, str]) -> bool:
    """Whether the RTA name names the country (its name, or the first word of it)."""
    for name, c in names.items():
        if c != code:
            continue
        first = name.split()[0]
        words = [name] + ([first] if len(first) >= 4 and first not in GENERIC_WORDS else [])
        if any(re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", rta_name) for w in words):
            return True
    return False


def resolve(field: str | None, names: dict[str, str], signed: str | None, applied: str | None,
            rta_name: str, ec_row: bool = False) -> tuple[list[dict], list[str], list[str]]:
    """Parties of a signatory list, the blocs WTO names in it, and unknown names."""
    expanded: list[dict] = []
    blocs: list[str] = []
    unknown: list[str] = []
    codes: list[str] = []
    for raw in (field or "").split(";"):
        name = clean(raw)
        if not name:
            continue
        if name == "European Union":
            codes.append("EU")
            continue
        bloc = next((b for b in BLOCS if b[0] == name), None)
        if bloc:
            blocs.append(bloc[1])
            expanded.extend(bloc_states(bloc[1], signed))
            continue
        code = names.get(name)
        if code is None:
            unknown.append(name)
        else:
            codes.append(code)
    # Older EC agreements list EC member states (often those of a later date) instead of the
    # EC: every EC state that the RTA name does not name as the partner becomes the EU party.
    members = {c for c in codes if c in EC_JOINED and not named_in(c, rta_name, names)}
    if len(members) >= 5 and (ec_row or EC_NAME.search(rta_name)):
        codes = ["EU"] + [c for c in codes if c not in members and c != "EU"]
    # Older EFTA agreements list the EFTA States one by one.
    efta_left: dict[str, str] = {}
    if not blocs and signed and re.search(r"\bEFTA\b", rta_name):
        states = BLOC_BY_PREFIX["EFTA"][2]
        at_signature = {st for st, joined, left in states if joined <= signed and not (left and left <= signed)}
        if at_signature <= set(codes):
            blocs.append("EFTA")
            efta_left = {st: left for st, _, left in states if st in at_signature and left}
    parties: list[dict] = []
    seen: set[str] = set()
    for code in codes:
        if code not in seen:
            seen.add(code)
            party = {"id": code, "type": "intblock" if code == "EU" else "country"}
            if code in efta_left:
                party["left"] = efta_left[code]
                if EC_JOINED.get(code) == efta_left[code]:
                    party["note"] = LEFT_FOR_EU
            parties.append(party)
    for party in expanded:
        if party["id"] not in seen:
            seen.add(party["id"])
            parties.append(party)
    parties.sort(key=lambda p: p["type"] != "intblock")
    return parties, blocs, unknown


def title_parties(rta_name: str, names: dict[str, str]) -> frozenset[str]:
    """Parties named in an RTA name ("EU - India"), for rows that list no signatories."""
    ids: set[str] = set()
    for part in re.split(r"\s+-\s+|\s*/\s*", rta_name):
        part = clean(part)
        hit = TITLE_NAMES.get(part) or ([names[part]] if part in names else None)
        if hit is None:
            return frozenset()
        ids.update(m["id"] for m in bloc_states(hit, None)) if isinstance(hit, str) else ids.update(hit)
    return frozenset(ids)


def make_id(parties: list[dict], blocs: list[str], taken: set[str], year: str | None) -> str:
    ids = [p["id"] for p in parties]
    countries = {i for i in ids if i != "EU"}
    prefix = "EU" if "EU" in ids else ""
    for bloc in sorted(set(blocs), key=lambda b: [x[1] for x in BLOCS].index(b)):
        prefix += bloc
        countries -= {m[0] for m in BLOC_BY_PREFIX[bloc][2]}
    base = prefix + "".join(sorted(countries))
    if base not in taken:
        return base
    candidate = f"{base}-{year}" if year else f"{base}-WTO"
    n = 2
    while candidate in taken:
        candidate = f"{base}-{year}-{n}"
        n += 1
    return candidate


# --- main ------------------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    rows = read_export(Path(argv[1]))
    write = "--write" in argv
    report_path = Path(argv[argv.index("--report") + 1]) if "--report" in argv else None
    names = load_country_names()
    intblocks = load_intblocks()
    registry = load_registry()
    aliases = yaml.safe_load((ROOT / "data" / "intblocks_aliases.yaml").read_text(encoding="utf-8")) or []
    taken = set(intblocks) | set(registry) | {str(a.get("alias")) for a in aliases if isinstance(a, dict)}
    by_rta = {int(r["wto_rta_id"]): rid for rid, r in registry.items() if r.get("wto_rta_id")}
    cited: dict[int, set[str]] = {}
    for rid, record in registry.items():
        for n in cited_rta_ids(record, intblocks):
            cited.setdefault(n, set()).add(rid)
    party_index: dict[frozenset[str], list[str]] = {}
    for rid, record in registry.items():
        party_index.setdefault(record_parties(record, intblocks), []).append(rid)

    report: list[list[str]] = []
    counts: dict[str, int] = {}
    created: dict[str, dict] = {}
    add_rta: dict[str, int] = {}
    corrected: dict[str, dict] = {}
    accessions: dict[str, list[tuple[int, dict]]] = {}
    problems = 0

    def note(kind: str, row: dict, target: str = "", detail: str = "") -> None:
        counts[kind] = counts.get(kind, 0) + 1
        report.append([str(row["RTA ID"]), kind, target, clean(row["Status"]), clean(row["RTA Name"]), detail])

    def correct(target: str, row: dict, status_wto: str, signed: str | None, in_force: str | None,
                ended: str | None, kind: str | None) -> str:
        """WTO status, type and full dates for a mapped catalogue record (ADB ARIC lags and often
        gives only a year). Official records and records linked to an intblock are not changed."""
        record = registry[target]
        old = record.get("status")
        if record.get("verification") != "catalogue" or record.get("intblock"):
            return ""
        new = dict(record)
        changes = []
        reopened = int(row["RTA ID"]) in RESUMED and old == "abandoned"
        if status_wto == "Inactive" and old == "in_force":
            new.update(status="terminated", ended=ended)
        elif status_wto.startswith("In ") and (old in ("signed", "negotiating", "proposed") or reopened):
            new["status"] = "in_force"
        if new["status"] != old:
            changes.append(f"status {old} -> {new['status']}")
        if kind and record.get("agreement_type") in ("other", "framework"):
            new["agreement_type"] = kind
            changes.append(f"type {record['agreement_type']} -> {kind}")
        # A date the record gives as a year (or year and month) of the WTO date, or one only
        # WTO gives, takes the WTO date; a different date is reported and left alone.
        dated = []
        for key, value in (("signed", signed), ("in_force", in_force)):
            if not value or (key == "in_force" and new["status"] not in ("in_force", "terminated", "superseded")):
                continue
            mine = str(record.get(key) or "")
            if mine == value:
                continue
            if not mine or (len(mine) < 10 and value.startswith(mine)) or new["status"] != old:
                new[key] = value
                dated.append(key)
            else:
                changes.append(f"{key} {mine} != WTO {value} (kept)")
        if not dated and new == record:
            return "; ".join(changes)
        if dated:
            changes.append("dates from WTO: " + ", ".join(dated))
        url = CARD.format(row["RTA ID"])
        fields = {"status"} if new["status"] != old else set()
        fields |= set(dated) | ({"agreement_type"} if new["agreement_type"] != record.get("agreement_type") else set())
        new["provenance"] = [p for p in record["provenance"] if p.get("field") not in fields] + [
            {"field": f, "source": SOURCE, "url": url, "retrieved_at": RETRIEVED} for f in sorted(fields)
        ]
        if new["status"] != old:
            new["notes"] = clean(f"{record.get('notes') or ''} WTO RTA-IS lists it as {status_wto.lower()}; ADB ARIC gave {old.replace('_', ' ')}.")
        corrected[target] = new
        return "; ".join(changes)

    # In-force rows first, so they get the base id when an inactive row has the same parties.
    order = {"In Force": 0, "In force for at least one Party": 0, "Inactive": 1}
    rows.sort(key=lambda r: (order.get(clean(r["Status"]), 2), int(r["RTA ID"])))
    for row in rows:
        rta = int(row["RTA ID"])
        status_wto = clean(row["Status"])
        signed = earliest(row["Date of Signature (G)"], row["Date of Signature (S)"])
        in_force = earliest(row["Date of Entry into Force (G)"], row["Date of Entry into Force (S)"])
        ended = excel_date(row["Inactive Date"])
        ec_row = rta in EC_ROWS
        current, blocs_c, unknown_c = resolve(row["Current signatories"], names, signed, in_force, row["RTA Name"], ec_row)
        original, blocs_o, unknown_o = resolve(row["Original signatories"], names, signed, in_force, row["RTA Name"], ec_row)
        parties = [dict(p) for p in current or original] + [dict(p) for p in EXTRA_PARTIES.get(rta, [])]
        blocs = blocs_c or blocs_o
        party_set = frozenset(p["id"] for p in parties)
        detail = ",".join(sorted(party_set))
        kind = TYPE_FIX.get(rta) or TYPES.get(clean(row["Type"]))

        if rta in SKIP:
            note("skipped", row, "", SKIP[rta])
            continue
        if rta in by_rta:
            note("mapped", row, by_rta[rta], "wto_rta_id")
            continue
        if rta in MAPPED:
            target = MAPPED[rta]
            if target not in registry:
                print(f"! {rta}: MAPPED target {target} is not a registry record")
                problems += 1
                continue
            add_rta[target] = rta
            note("mapped", row, target, " ".join(x for x in ("hand", correct(target, row, status_wto, signed, in_force, ended, kind)) if x))
            continue
        if rta in ACCESSION:
            accessions.setdefault(ACCESSION[rta], []).append((rta, row))
            note("accession", row, ACCESSION[rta], detail)
            continue
        if rta in SAME_INSTRUMENT:
            note("same_instrument", row, SAME_INSTRUMENT[rta], detail)
            continue
        hits = sorted(cited.get(rta, set()) - set(by_rta.values()) - set(add_rta))
        if len(hits) == 1:
            add_rta[hits[0]] = rta
            note("mapped", row, hits[0], " ".join(x for x in ("card cited", correct(hits[0], row, status_wto, signed, in_force, ended, kind)) if x))
            continue
        if not party_set and status_wto.startswith("Early"):
            party_set = title_parties(clean(row["RTA Name"]), names)
        keys = {party_set, frozenset(p["id"] for p in original)} if original else {party_set}
        candidates = sorted({
            c for k in keys for c in party_index.get(k, [])
            if c not in by_rta.values() and c not in add_rta and c not in NOT_SAME.get(rta, set())
        })
        inactive = status_wto == "Inactive"
        early = status_wto.startswith("Early")

        def fits(c: str, kind: str | None = kind, early: bool = early, inactive: bool = inactive) -> bool:
            rec = registry[c]
            if kind and rec.get("agreement_type") not in COMPATIBLE.get(kind, set()):
                return False
            if early:
                return True
            if rec.get("status") in ("proposed", "negotiating", "abandoned"):
                return False
            # A catalogue record's status may lag; an official record's status must agree.
            ended_record = rec.get("status") in ("terminated", "superseded")
            return ended_record == inactive or rec.get("verification") == "catalogue"

        fitting = [c for c in candidates if fits(c)]
        if early:
            if len(fitting) == 1:
                add_rta[fitting[0]] = rta
                note("mapped", row, fitting[0], "auto (early announcement)")
            else:
                note("skipped", row, ";".join(candidates), "early announcement with no registry record; out of scope for this pass")
            continue
        if len(fitting) == 1:
            add_rta[fitting[0]] = rta
            note("mapped", row, fitting[0], " ".join(x for x in ("auto", correct(fitting[0], row, status_wto, signed, in_force, ended, kind)) if x))
            continue
        if fitting or (candidates and rta not in NOT_SAME):
            note("review", row, ";".join(candidates), detail)
            problems += 1
            continue
        if unknown_c or unknown_o:
            note("review", row, "", f"unknown parties {unknown_c + unknown_o}")
            problems += 1
            continue
        if kind is None:
            note("review", row, "", f"type {row['Type']}")
            problems += 1
            continue
        if rta in WTO_IS_INTBLOCK:
            record = {"id": WTO_IS_INTBLOCK[rta], "intblock": WTO_IS_INTBLOCK[rta]}
        else:
            if len(parties) < 2:
                note("review", row, "", f"{len(parties)} parties")
                problems += 1
                continue
            year = (signed or in_force or "")[:4] or None
            record = {"id": IDS.get(rta) or make_id(parties, blocs, taken, year), "name": clean(row["RTA Name"])}
        if record["id"] in taken and rta not in WTO_IS_INTBLOCK:
            print(f"! {rta}: id {record['id']} is taken")
            problems += 1
            continue
        if record["id"] in registry or record["id"] in created:
            print(f"! {rta}: registry already has {record['id']}")
            problems += 1
            continue
        taken.add(record["id"])
        record["agreement_type"] = kind
        if inactive:
            record["status"] = "superseded" if rta in SUPERSEDED_BY else "terminated"
        else:
            record["status"] = "in_force"
        record["signed"] = signed
        record["in_force"] = in_force
        if inactive:
            record["ended"] = ended
        if "intblock" not in record:
            listed = {p["id"] for p in parties}
            for p in original if current else []:
                if p["id"] not in listed:
                    p = dict(p)
                    p.setdefault("note", "Listed by WTO RTA-IS as an original signatory, not a current one.")
                    parties.append(p)
            record["parties"] = parties
        if rta in SUPERSEDED_BY:
            record["superseded_by"] = SUPERSEDED_BY[rta]
        record["wto_rta_id"] = rta
        facts = []
        g = excel_date(row["Date of Entry into Force (G)"])
        s = excel_date(row["Date of Entry into Force (S)"])
        if g and s and g != s:
            facts.append(f"WTO RTA-IS gives entry into force on {g} for goods and on {s} for services.")
        if status_wto == "In force for at least one Party":
            facts.append("WTO RTA-IS lists it as in force for at least one party.")
        if rta in NOTES:
            facts.append(NOTES[rta])
        if facts:
            record["notes"] = " ".join(facts)
        record["verification"] = "official" if "intblock" in record else "catalogue"
        record["last_verified"] = RETRIEVED
        url = CARD.format(rta)
        record["provenance"] = [
            {"field": f, "source": SOURCE, "url": url, "retrieved_at": RETRIEVED}
            for f in (("status",) if "intblock" in record else ("parties", "status"))
        ]
        created[record["id"]] = record
        note("new", row, record["id"], detail)

    # Accessions to a new record add the acceding parties; other accessions are reported only.
    for target, items in accessions.items():
        if target not in registry and target not in created:
            print(f"! accession target {target} is neither a registry record nor a new one")
            problems += 1
            continue
        record = created.get(target)
        if record is None or "parties" not in record:
            continue
        listed = {p["id"] for p in record["parties"]}
        ids = []
        for rta, row in sorted(items, key=lambda i: i[1]["Date of Entry into Force (G)"] or ""):
            ids.append(str(rta))
            joined = earliest(row["Date of Signature (G)"], row["Date of Signature (S)"])
            applied = earliest(row["Date of Entry into Force (G)"], row["Date of Entry into Force (S)"])
            acceding, _, _ = resolve(row["Original signatories"] or row["Current signatories"], names, joined,
                                     applied, row["RTA Name"])
            for party in acceding:
                if party["id"] in listed:
                    continue
                listed.add(party["id"])
                party = dict(party)
                if applied:
                    party["in_force"] = applied
                else:
                    party["signed"] = joined
                    party["note"] = "Accession signed, not in force (WTO RTA-IS early announcement)."
                if row["Inactive Date"]:
                    party["left"] = excel_date(row["Inactive Date"])
                record["parties"].append(party)
        record["notes"] = clean(f"{record.get('notes') or ''} WTO RTA-IS lists {'the accession' if len(ids) == 1 else 'the accessions'} separately (RTA {'ID' if len(ids) == 1 else 'IDs'} {', '.join(ids)}).")

    unresolved_supersession = [r for r in SUPERSEDED_BY.values() if r not in registry and r not in created]
    for ref in sorted(set(unresolved_supersession)):
        print(f"! superseded_by {ref} is neither a registry record nor a new one")
        problems += 1

    if write:
        for target, rta in add_rta.items():
            if target in corrected:
                corrected[target]["wto_rta_id"] = rta
                continue
            path = REGISTRY / f"{target}.yaml"
            text = path.read_text(encoding="utf-8")
            anchor = "\naric_id:" if "\naric_id:" in text else "\nverification:"
            text = text.replace(anchor, f"\nwto_rta_id: {rta}{anchor}", 1)
            path.write_text(text, encoding="utf-8")
        for agreement_id, record in {**corrected, **created}.items():
            record = ordered({k: v for k, v in record.items() if v is not None})
            (REGISTRY / f"{agreement_id}.yaml").write_text(
                yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8"
            )
    if report_path:
        report.sort(key=lambda r: int(r[0]))
        report_path.write_text(
            "\n".join("\t".join(r) for r in [["rta_id", "result", "record", "wto_status", "wto_name", "detail"], *report])
            + "\n",
            encoding="utf-8",
        )
    print(", ".join(f"{k} {v}" for k, v in sorted(counts.items())), f"(rows {len(rows)}, corrected {len(corrected)}, problems {problems})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
