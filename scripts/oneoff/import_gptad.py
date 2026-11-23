#!/usr/bin/env python3
"""One-off: map World Bank GPTAD agreements to trade agreement records (ids and text links).

Input is the directory written by ``fetch_gptad.py`` (``library.html``, ``ids.json``,
``detail/<id>.html``). The pages are untrusted data: keep them outside the repository and
run this script with ``python -I``.

Each GPTAD agreement id gets one result, checked in this order:

- ``skipped``: ``SKIP`` (checked by hand): a duplicate of another GPTAD id for the same
  instrument, an accession or enlargement protocol (recorded as party dates, not as an
  agreement), or an agreement outside the registry scope;
- ``mapped``: the record that already has the ``gptad_id``; ``MAPPED`` (checked by hand);
  or the one record whose parties equal the GPTAD membership and whose date of signature
  (entry into force when GPTAD has no signature date) is within ``DAYS`` days of the GPTAD
  date, or the only record with those parties when there is no pair of dates to compare
  (``auto``). Parties are compared with the EU
  as one party and the member states of EFTA, ASEAN, MERCOSUR, CARICOM, SACU, the Andean
  Community and the GCC folded into the bloc, because GPTAD lists a bloc's members of
  around 2010 and the registry its members at the date of signature;
- ``unmatched``: no record, more than one, or an older instrument than the record with the
  same parties (``NOT_IN_REGISTRY``); listed in the report for the change that adds the
  missing agreements. A record still proposed or under negotiation never matches, since
  GPTAD holds signed texts.

Mapped records get ``gptad_id`` and, when GPTAD has the full text, a ``treaty_text`` link to
the PDF. No record is added, and no status, date, party or verification level changes:
GPTAD was last updated around 2010. See ``openspec/changes/add-gptad-catalogue-links``.

Usage: python -I scripts/oneoff/import_gptad.py GPTAD_DIR [--write] [--report TSV]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.parse
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
DAYS = 366
PDF_PREFIX = "https://wits.worldbank.org/GPTAD/PDF/archive/"

# GPTAD member names that data/countries does not list (misspellings, French, old names).
NAMES = {
    "Lao": "LA", "Luxemburg": "LU", "Luxembourt": "LU", "The Netherlands": "NL", "Buglaria": "BG",
    "Republic of Georgia": "GE", "Kyrgyz": "KG", "Kyrgyz Republic": "KG", "the Philippines": "PH",
    "Lichtenstein": "LI", "Antigua": "AG", "St. Kitts-Nevis-Anguilla": "KN", "St. Kitts": "KN",
    "Nevis": "KN", "Saint Kitts": "KN", "St. Vincent": "VC", "Saint Vincent": "VC",
    "St. Lucia": "LC", "Trinidad": "TT", "Tobago": "TT", "Barbuda": "AG", "Principe": "ST",
    "Sao Tome": "ST", "Cameroun": "CM", "Centrafricaine": "CF", "Gabonaise": "GA",
    "Guinée Équatoriale": "GQ", "China (Taiwan)": "TW", "Chinese Taipei": "TW", "Taiwan": "TW",
    "Bosnia": "BA", "Herzegovina": "BA", "Bosnia & Herzegovina": "BA", "Jordon": "JO",
    "United Arab Emirates (UAE)": "AE", "UAE": "AE", "Fiji Islands": "FJ", "Western Samoa": "WS",
    "Palestine Liberation Organization": "PS", "Palestine Authority": "PS", "Palestinian Authority": "PS",
    "United Republic of Cameroon": "CM", "People’s Republic of the Congo": "CG",
    "Republic of Sao Tome and Principe": "ST", "Republic of Zaire": "CD", "Zaire": "CD",
    "Bolivarian Republic of Venezuela": "VE", "The Republic of Korea": "KR", "Korea": "KR",
    "Former Yugoslav Republic of Macedonia": "MK", "FYROM": "MK", "Macedonia": "MK",
    "Macedonia(Former Yugoslav Republic of Macedonia)": "MK", "Northern Ireland": "GB",
    "Tchad": "TD", "Swaziland": "SZ", "Libyan Arab Jamahiriya": "LY", "Sahrawi": "EH",
    "Cape Verde": "CV", "Guinea Bissau": "GW", "Cote d'Ivoire": "CI", "Iran": "IR", "Syria": "SY",
    "Russia": "RU", "Vietnam": "VN", "Moldova": "MD", "Brunei": "BN", "Tanzania": "TZ",
    "Bolivia": "BO", "Venezuela": "VE", "Hong Kong": "HK", "Hong Kong, China": "HK", "USA": "US",
    "United States": "US", "UK": "GB", "Czech Republic": "CZ", "Slovak Republic": "SK",
    "Gambia": "GM", "Bahamas": "BS", "Faeroe Islands": "FO", "Micronesia": "FM", "Burma": "MM",
    "East Timor": "TL", "Turkey": "TR", "Netherlands Antilles": "AN",
    "Serbia and Montenegro": "RS", "Yugoslavia": "RS", "Congo": "CG", "Viet Nam": "VN", "Macao": "MO",
    "Macau": "MO", "Republic of Sao Tome": "ST",
    "Belgique": "BE", "Danemark": "DK", "Finlande": "FI", "Allemagne": "DE", "Grèce": "GR",
    "Irelande": "IE", "Italie": "IT", "Pays-Bas": "NL", "Espagne": "ES", "Suède": "SE",
    "Royaume-Uni": "GB", "Malte": "MT", "Autriche": "AT", "UNMIK": "XK",
    "Falkland Islands (Islas Malvinas)": "FK", "Wallis and Futuna Islands": "WF",
}
EC_NAMES = r"European Communit(?:y|ies|iy)|Communauté européenne|\bEC\b|\bEU\b|European Union"
# Groupings GPTAD writes before a list of their member states, not folded into one party.
LABELS = r"\bCEFTA\b|BIMST-EC|European Economic Area|CARIFORUM|Overseas Countries and Territories"
# Blocs whose member states the registry lists one by one: (pattern in a name, intblock id,
# former members to fold as well).
BLOCS = {
    "EFTA": (r"(?<!C)EFTA|European Free Trade", "EFTA", {"AT", "FI", "SE", "PT", "GB", "DK"}),
    "ASEAN": (r"ASEAN|AFTA", "ASEAN", set()),
    "MERCOSUR": (r"MERCOSUR", "MERCOSUR", {"VE"}),
    "CARICOM": (r"CARICOM|Caribbean Community", "CARICOM", set()),
    "SACU": (r"SACU|Southern African Customs", "SACU", set()),
    "CAN": (r"Andean", "CAN", {"VE", "CL"}),
    "GCC": (r"GCC|Gulf Cooperation", "CCASG", set()),
}

# GPTAD id -> registry id, checked by hand against the official name of the GPTAD text
# where the automatic rule finds no record, several, or another instrument with the same
# parties and date (GPTAD dates sometimes belong to an older agreement than its text).
MAPPED: dict[int, str] = {
    # EC agreements: the text is the instrument named, whatever the date GPTAD gives.
    3: "EUDZ",  # Euro-Mediterranean Association Agreement (2002); GPTAD date is the 1976 one
    4: "EUBG",  # Europe Agreement, not the Interim Agreement of the same day
    8: "EUCZ",  # Europe Agreement
    9: "EUEG-1977",  # Cooperation Agreement of 1977, not the 1972 agreement
    12: "EUHU",  # Europe Agreement
    17: "EULB-1977",  # Cooperation Agreement of 1977
    20: "EUMT",  # English text; 21 is the French one
    22: "EUMX",  # FTA decision under the 1997 Global Agreement
    25: "EUOCT",
    27: "EUPL",  # Europe Agreement
    28: "EURO",  # Europe Agreement
    29: "EUSK",  # Europe Agreement
    30: "EUSI-1996-2",  # Interim Agreement of 1996
    33: "EUSY",  # Cooperation Agreement of 1977
    34: "EUMK",  # Stabilisation and Association Agreement
    144: "EUCU",  # Treaty establishing the European Community
    336: "EUCARIFORUMEPA",
    445: "EUSM",  # GPTAD lists the EU member states as parties
    # Plurilateral agreements: the registry reads the roster from an intblock.
    149: "AFTA-CEPT",  # CEPT Agreement of 1992
    150: "APTA",  # Bangkok Agreement of 1975
    151: "CAN",  # codified Cartagena Agreement
    152: "COMESA",
    154: "ALADI",
    155: "SPARTECA",
    159: "CEFTA-1992",
    161: "CISFTA-1994",
    250: "CAFTADR",  # with the Dominican Republic; 211 is the May 2004 Central America text
    262: "SADCFTA",  # SADC Protocol on Trade
    270: "CACM",
    284: "MSGTA",
    288: "GSTP",
    294: "ECOWAS",  # Revised Treaty
    300: "UEMOA",
    306: "SAFTA",
    315: "EEA",
    351: "PICTA",
    381: "CEFTA",  # CEFTA 2006
    401: "EAC",
    402: "ECOTA",
    421: "SACU",  # 2002 SACU Agreement
    449: "PTN",
    # Agreements with blocs or parties the automatic rule does not fold.
    82: "EEFO",  # Denmark signs for the Faroe Islands
    90: "FOPL",
    91: "CHFOLI",
    375: "FOIS",
    252: "CLCR",  # Chile - Central America FTA, Costa Rica protocol (English; 160 is Spanish)
    214: "CLSV",  # Chile - Central America FTA, El Salvador protocol
    169: "MXSV",  # Mexico - Northern Triangle; WTO has one RTA ID per Central American party
    299: "GTMX",
    303: "HNMX",
    253: "RORS",
    254: "BARO",
    260: "MDRS",
    322: "AKFTA",  # Agreement on Trade in Goods; 452 is the 2005 framework agreement
    364: "INDIAMERCOSURPTA",
    387: "CLCN",  # the 2005 FTA text; GPTAD gives a 1996 date
    426: "INTH-2003",  # framework agreement with the early harvest scheme
    437: "INKR",  # no membership in GPTAD
    446: "NITW",  # Taiwan (Republic of China) - Nicaragua
    459: "AFIN",  # 450 and 466 repeat the same text
    # GPTAD duplicates: the id with the WTO document symbol or annexes is kept.
    58: "BAHR",
    104: "ILTR",
    124: "NZSG",
}

# GPTAD id -> an older instrument than the record with the same parties, left for the change
# that adds predecessor agreements.
NOT_IN_REGISTRY: dict[int, str] = {
    174: "1973 Costa Rica - Panama free trade treaty; CRPA is the 2007 protocol to the Central America - Panama FTA",
}
UNSIGNED = frozenset({"proposed", "negotiating"})
# Full-text PDFs the library links but the server does not have (HTTP 403, checked 2026-11-23).
MISSING_PDF = frozenset({
    "Japan-Switzerland.pdf", "Laos-Thailand.pdf", "PTN.pdf", "US-bahrain.pdf", "japan-vietnam.pdf",
})

# GPTAD id -> reason it maps to no record.
SKIP: dict[int, str] = {
    21: "French text of the EC - Malta agreement (20)",
    160: "Spanish text of the Chile - Central America FTA (252)",
    211: "United States - Central America text of May 2004; CAFTA-DR (250) adds the Dominican Republic",
    265: "duplicate of 58 (Bosnia and Herzegovina - Croatia)",
    275: "duplicate of 104 (Israel - Turkey)",
    269: "duplicate of 124 (New Zealand - Singapore)",
    443: "duplicate of 364 (MERCOSUR - India)",
    450: "duplicate of 459 (Afghanistan - India)",
    466: "duplicate of 459 (Afghanistan - India), labelled FTA",
    293: "duplicate of 299 (Mexico - Northern Triangle, same PDF)",
    403: "duplicate of 242 (accession of Croatia to CEFTA)",
    1: "accession of Romania to CEFTA; party dates of CEFTA-1992",
    133: "accession of Bulgaria to CEFTA; party dates of CEFTA-1992",
    134: "accession of Slovenia to CEFTA; party dates of CEFTA-1992",
    242: "accession of Croatia to CEFTA; party dates of CEFTA-1992",
    292: "accession of China to the Bangkok Agreement; party dates of APTA",
    411: "accession of Iceland to EFTA; party dates of EFTA",
    247: "EU enlargement treaty; membership dates of the EU intblock",
    256: "EU enlargement treaty; membership dates of the EU intblock",
    296: "EU enlargement treaty; membership dates of the EU intblock",
    301: "EU enlargement decision; membership dates of the EU intblock",
    308: "EU enlargement treaty; membership dates of the EU intblock",
    408: "EU enlargement treaty; membership dates of the EU intblock",
    156: "BAFTA protocol on agricultural goods; part of BAFTA",
    158: "BAFTA agreement on non-tariff barriers; part of BAFTA",
    259: "amendment of the Croatia - Serbia and Montenegro FTA, not its text",
    263: "amendment of the SADC Protocol on Trade (262)",
    414: "GUUAM charter, not the 2002 GUAM FTA",
    434: "1958 India - Japan agreement on commerce: most-favoured-nation treatment, not preferential",
    470: "United States - Albania trade relations agreement: most-favoured-nation treatment, not preferential",
    471: "United States - Vietnam bilateral trade agreement: most-favoured-nation treatment, not preferential",
}


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def cell_text(fragment: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment)).replace("\\r\\n", "\n")
    return re.sub(r"[ \t\r\f\v]+", " ", text).strip()


def us_date(value: str) -> str | None:
    """GPTAD dates are MM/DD/YYYY; 'N/A' and 1899 placeholders mean no date."""
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", value.strip())
    if not m or m.group(3) < "1900":
        return None
    return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"


def read_library(path: Path) -> list[dict]:
    """Rows of the library table."""
    page = path.read_text(encoding="utf-8")
    body = page.split('<div id="DataDiv">', 1)[1].split("</tbody>", 1)[0]
    rows = []
    for row in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        pdf = re.search(r"href='([^']+\.pdf)'", cells[0], re.I)
        annex = re.search(r"openannexwindow\((\d+)\)", row)
        rows.append({
            "name": cell_text(cells[0]),
            "pdf": pdf.group(1) if pdf else None,
            "members": cell_text(cells[1]),
            "type": cell_text(cells[2]),
            "signed": us_date(cell_text(cells[3])),
            "in_force": us_date(cell_text(cells[4])),
            "notified": cell_text(cells[5]),
            "status": cell_text(cells[6]),
            "annex_id": int(annex.group(1)) if annex else None,
        })
    return rows


def read_detail(path: Path) -> dict:
    """Indexed provisions of one agreement: {provision label: text}, plus the PDF link."""
    page = re.sub(r"<script.*?</script>", "", path.read_text(encoding="utf-8"), flags=re.S)
    fields: dict[str, str] = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [cell_text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(cells) >= 2 and re.match(r"^[IV]+(\.\d+)* ", cells[0]):
            label = re.sub(r"^[IV]+(\.\d+)* ", "", cells[0]).strip().lower()
            fields[label] = cells[1]
    pdf = re.search(r"href='([^']+/PDF/archive/[^']+\.pdf)'", page, re.I)
    fields["pdf"] = pdf.group(1) if pdf else None
    return fields


def country_names() -> dict[str, str]:
    names: dict[str, str] = {}
    for path in sorted((ROOT / "data" / "countries").glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        candidates = [record.get("name"), record.get("official_name")]
        candidates += [o.get("name") for o in record.get("other_names") or [] if o.get("id") == "en"]
        for name in candidates:
            if name:
                names.setdefault(norm(name), record["code"])
    for name, code in NAMES.items():
        names[norm(name)] = code
    return names


def load_intblocks() -> dict[str, dict]:
    out = {}
    for path in (ROOT / "data" / "intblocks").rglob("*.yaml"):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("id"):
            out[str(record["id"])] = record
    return out


def roster(intblock: dict | None) -> set[str]:
    return {
        str(i["id"]) for i in (intblock or {}).get("includes") or []
        if isinstance(i, dict) and i.get("type") == "country"
    }


def gptad_parties(name: str, members: str, names: dict[str, str]) -> tuple[set[str], list[str]]:
    """Party codes of a GPTAD membership string (the EC as ``EU``) and the names not resolved."""
    text = members.replace("\n", " ")
    parties: set[str] = set()
    if re.search(EC_NAMES, text) or re.search(EC_NAMES, name):
        parties.add("EU")
        text = re.sub(rf"(?:{EC_NAMES})\s*\(+[^()]*\)+", " ", text)
        text = re.sub(EC_NAMES, " ", text)
    # A bloc label before a list of member states: the states are the parties.
    for pattern in [p for p, _, _ in BLOCS.values()] + [LABELS]:
        text = re.sub(rf"(?:{pattern})(?: States)?\s*(?=\()", " ", text)
    text = re.sub(r"\bSAARC \(South Asian Association for Regional Cooperation\)", " ", text)
    unresolved = []
    for chunk in re.split(r"[,;()]", text):
        chunk = chunk.strip(" .")
        # "Trinidad and Tobago" is one name, "Bulgaria and Romania" two.
        for token in [chunk] if lookup(chunk, names) else re.split(r"\band\b| - ", chunk):
            token = token.strip(" .")
            if not token:
                continue
            code = lookup(token, names)
            bloc = next((b for b, (pattern, _, _) in BLOCS.items() if re.fullmatch(f"(?:{pattern}).*", token)), None)
            if code:
                parties.add(code)
            elif bloc:
                parties.add(bloc)  # the bloc named as one party, without its member states
            elif not re.fullmatch(r"European (?:Atomic Energy|Coal|Steel) Community|Steel Community|BIMST-", token):
                unresolved.append(token)
    return parties, unresolved


def lookup(name: str, names: dict[str, str]) -> str | None:
    key = norm(name)
    return names.get(key) or names.get(re.sub(r"^the ", "", key))


def fold(label: str, parties: set[str], members: dict[str, set[str]]) -> frozenset[str]:
    """Fold a bloc's member states into the bloc when the agreement is named after it."""
    out = set(parties)
    for bloc, (pattern, _, _) in BLOCS.items():
        if re.search(pattern, label) and len(out & members[bloc]) >= 2:
            out = (out - members[bloc]) | {bloc}
    return frozenset(out)


def record_parties(record: dict, intblocks: dict[str, dict]) -> set[str]:
    if record.get("intblock"):
        return roster(intblocks.get(str(record["intblock"])))
    return {str(p["id"]) for p in record.get("parties") or []}


def record_date(record: dict, intblocks: dict[str, dict], field: str) -> str | None:
    """The record's ``signed`` or ``in_force`` date, else its linked intblock's."""
    if record.get(field):
        return str(record[field])
    intblock = intblocks.get(str(record.get("intblock"))) if record.get("intblock") else None
    if intblock is None:
        return None
    value = intblock.get("founded") if field == "signed" else (intblock.get("active_period") or {}).get("start")
    return str(value) if value else None


def distance(row: dict, record: dict, intblocks: dict[str, dict]) -> int | None:
    """Days between the GPTAD and registry signatures, or entries into force when GPTAD has no signature."""
    if row.get("signed"):
        return days_apart(row["signed"], record_date(record, intblocks, "signed"))
    return days_apart(row.get("in_force"), record_date(record, intblocks, "in_force"))


def days_apart(a: str | None, b: str | None) -> int | None:
    if not a or not b or len(a) < 4 or len(b) < 4:
        return None
    def as_date(value: str) -> date:
        parts = [int(x) for x in value.split("-")] + [1, 1]
        return date(parts[0], parts[1], parts[2])
    return abs((as_date(a) - as_date(b)).days)


def join_library(ids: dict[int, str], details: dict[int, dict], library: list[dict]) -> dict[int, dict]:
    """The library row of each GPTAD id: by annex id, then by name, PDF, status and notification."""
    out: dict[int, dict] = {}
    used: set[int] = set()
    for n, row in enumerate(library):
        if row["annex_id"] in ids:
            out[row["annex_id"]] = row
            used.add(n)
    for gid in sorted(ids):
        if gid in out:
            continue
        detail = details.get(gid, {})
        key = (norm(ids[gid]), detail.get("pdf"), detail.get("in force status", ""), detail.get("notified to wto", ""))
        for n, row in enumerate(library):
            if n in used:
                continue
            if (norm(row["name"]), row["pdf"], row["status"], row["notified"]) == key:
                out[gid] = row
                used.add(n)
                break
        else:
            for n, row in enumerate(library):
                if n not in used and norm(row["name"]) == key[0]:
                    out[gid] = row
                    used.add(n)
                    break
    return out


def insert_fields(text: str, gptad_id: int, pdf: str | None) -> str:
    """Add ``gptad_id`` after the other catalogue ids and a ``treaty_text`` link, keeping layout."""
    if "\ngptad_id:" not in text:
        for anchor in ("\nwikidata_id:", "\nlinks:", "\ndescription:", "\nnotes:", "\nverification:"):
            if anchor in text:
                text = text.replace(anchor, f"\ngptad_id: {gptad_id}{anchor}", 1)
                break
    if pdf and pdf not in text:
        item = f"- url: {pdf}\n  type: treaty_text\n"
        if "\nlinks:\n" in text:
            head, tail = text.split("\nlinks:\n", 1)
            lines = tail.splitlines(keepends=True)
            n = 0
            while n < len(lines) and (lines[n].startswith("- ") or lines[n].startswith("  ")):
                n += 1
            text = head + "\nlinks:\n" + "".join(lines[:n]) + item + "".join(lines[n:])
        else:
            for anchor in ("\ndescription:", "\nnotes:", "\nverification:"):
                if anchor in text:
                    text = text.replace(anchor, f"\nlinks:\n{item.rstrip()}{anchor}", 1)
                    break
    return text


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("gptad_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write gptad_id and links to data/trade_agreements/")
    parser.add_argument("--report", type=Path, help="TSV with one row per GPTAD id")
    args = parser.parse_args(argv)

    ids = {int(k): v for k, v in json.loads((args.gptad_dir / "ids.json").read_text(encoding="utf-8")).items()}
    details = {
        int(p.stem): read_detail(p) for p in (args.gptad_dir / "detail").glob("*.html") if p.stem.isdigit()
    }
    library = read_library(args.gptad_dir / "library.html")
    rows = join_library(ids, details, library)
    names = country_names()
    intblocks = load_intblocks()
    members = {bloc: roster(intblocks.get(ib)) | extra for bloc, (_, ib, extra) in BLOCS.items()}
    registry = {
        p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(REGISTRY.glob("*.yaml"))
    }
    by_gptad = {int(r["gptad_id"]): rid for rid, r in registry.items() if r.get("gptad_id")}
    folded = {}
    for rid, record in registry.items():
        label = " ".join([rid, str(record.get("name") or (intblocks.get(str(record.get("intblock"))) or {}).get("name") or "")])
        folded[rid] = fold(label, record_parties(record, intblocks), members)

    results: list[dict] = []
    for gid in sorted(ids):
        row = rows.get(gid) or {}
        detail = details.get(gid, {})
        name = ids[gid]
        membership = detail.get("membership") or row.get("members") or ""
        parties, unresolved = gptad_parties(name, membership, names)
        key = fold(f"{name} {membership}", parties, members)
        signed = row.get("signed")
        pdf = detail.get("pdf") or row.get("pdf")
        if pdf and pdf.rsplit("/", 1)[-1] in MISSING_PDF:
            pdf = None
        pdf = urllib.parse.quote(pdf, safe=":/()") if pdf else None  # some file names have spaces
        result = {"gptad_id": gid, "name": name, "signed": signed or "", "status": row.get("status", ""),
                  "parties": ",".join(sorted(key)), "unresolved": "; ".join(unresolved), "pdf": pdf or "",
                  "official_name": (detail.get("official name") or "").replace("\n", " ")[:200],
                  "wto_symbol": (detail.get("wto document symbol") or "").replace("\n", " ")[:120]}
        if gid in SKIP:
            result.update(result="skipped", record="", how="SKIP", detail=SKIP[gid])
        elif gid in by_gptad:
            result.update(result="mapped", record=by_gptad[gid], how="gptad_id", detail="")
        elif gid in MAPPED:
            result.update(result="mapped", record=MAPPED[gid], how="MAPPED", detail="")
        elif gid in NOT_IN_REGISTRY:
            result.update(result="unmatched", record="", how="NOT_IN_REGISTRY", detail=NOT_IN_REGISTRY[gid])
        else:
            # GPTAD holds signed texts, so a record still proposed or under negotiation is no match.
            same = [rid for rid, fp in folded.items() if fp == key and registry[rid].get("status") not in UNSIGNED]
            near = [rid for rid in same if (d := distance(row, registry[rid], intblocks)) is not None and d <= DAYS]
            if len(near) == 1:
                result.update(result="mapped", record=near[0], how="auto",
                              detail=f"{distance(row, registry[near[0]], intblocks)} days")
            elif len(same) == 1 and distance(row, registry[same[0]], intblocks) is None:
                # One record with these parties, and no pair of dates to compare.
                result.update(result="mapped", record=same[0], how="auto", detail="no dates")
            else:
                cands = near or same
                result.update(result="unmatched", record="", how="",
                              detail=" ".join(f"{rid}({record_date(registry[rid], intblocks, 'signed')})" for rid in cands[:6]))
        results.append(result)

    # A record takes one GPTAD id; a second claim is a conflict to settle in MAPPED or SKIP.
    claims: dict[str, list[int]] = {}
    for r in results:
        if r["result"] == "mapped":
            claims.setdefault(r["record"], []).append(r["gptad_id"])
    conflicts = {rid: gids for rid, gids in claims.items() if len(gids) > 1}
    for r in results:
        if r["result"] == "mapped" and r["record"] in conflicts and r["how"] == "auto":
            r.update(result="unmatched", detail=f"{r['record']} also claimed by {conflicts[r['record']]}", record="", how="")

    counts: dict[str, int] = {}
    for r in results:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    print(" ".join(f"{k}={v}" for k, v in sorted(counts.items())), f"conflicts={len(conflicts)}")

    if args.report:
        cols = ["gptad_id", "result", "how", "record", "detail", "name", "signed", "status", "parties",
                "unresolved", "official_name", "wto_symbol", "pdf"]
        with args.report.open("w", encoding="utf-8") as out:
            out.write("\t".join(cols) + "\n")
            for r in results:
                out.write("\t".join(str(r.get(c, "")).replace("\t", " ") for c in cols) + "\n")

    if args.write:
        written = 0
        for r in results:
            if r["result"] != "mapped":
                continue
            path = REGISTRY / f"{r['record']}.yaml"
            text = path.read_text(encoding="utf-8")
            new = insert_fields(text, r["gptad_id"], r["pdf"] if r["pdf"].startswith(PDF_PREFIX) else None)
            if new != text:
                path.write_text(new, encoding="utf-8")
                written += 1
        print(f"wrote {written} records")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
