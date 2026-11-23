#!/usr/bin/env python3
"""Apply the EFTA free trade network review of 2026-11-23 to data/trade_agreements/.

efta.int is behind a Cloudflare challenge, so the 46 partner pages under
https://www.efta.int/trade-relations/free-trade-network were read from Wayback Machine
captures (December 2025 to November 2026). Conflicts were checked against the WTO RTA-IS
ID cards ("Specific dates of entry into force") and, for Lebanon, the Fedlex
scope-of-application table.

The facts are written out below rather than parsed, because several partner pages carry
the date of a joint declaration or an older agreement in their "Key facts" box. The
script:

- updates stale statuses (Thailand and Malaysia signed, the Singapore DEA in force for two
  parties), the UK agreement's entry into force (the WTO date is provisional application),
  and adds notes on suspended or concluded negotiations;
- adds per-state entry-into-force dates (parties[].in_force) where the agreement entered
  into force on different dates for different EFTA States;
- adds the EFTA partner page as a link and as provenance, and marks a record official
  when EFTA (or Fedlex) states its parties and dates.

Run once from the repository root: python scripts/oneoff/apply_efta_ftn.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
EFTA = "EFTA, free trade network partner page (Wayback Machine copy)"
WTO = "WTO Regional Trade Agreements Information System"
FEDLEX = "Fedlex, scope of application (Geltungsbereich) of the agreement"
PAGE = "https://www.efta.int/trade-relations/free-trade-network/{}"
SNAPSHOT = "https://web.archive.org/web/{}/https://www.efta.int/trade-relations/free-trade-network/{}"
CARD = "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid={}"
FEDLEX_LB = (
    "https://fedlex.data.admin.ch/filestore/fedlex.data.admin.ch/eli/cc/2007/199/20130501/de/html/"
    "fedlex-data-admin-ch-eli-cc-2007-199-20130501-de-html-3.html"
)
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]
PARTY_ORDER = ["id", "type", "signed", "in_force", "left", "note"]

# Wayback capture used for each partner page (slug -> timestamp).
CAPTURES = {
    "albania": "20260219191342", "bosnia-and-herzegovina": "20260809220243", "canada": "20261006234116",
    "central-american-states-costa-rica-guatemala-honduras-and-panama": "20260215215152",
    "chile": "20260804055322", "colombia": "20260219151530", "ecuador": "20260219175907",
    "egypt": "20260824034607", "israel": "20261012014947", "jordan": "20260219180225",
    "kosovo": "20260214031834", "lebanon": "20260813161625", "malaysia": "20260822044736",
    "mercosur": "20261115205235", "mexico": "20260219130415", "moldova": "20261012233214",
    "montenegro": "20261003125033", "morocco": "20260219204501", "north-macedonia": "20260219100659",
    "palestinian-authority": "20260219200705", "peru": "20260219175300",
    "russia-belarus-kazakhstan": "20251231033445", "serbia": "20261012100714",
    "singapore": "20261008071746", "thailand": "20260211110931", "tunisia": "20260219084850",
    "ukraine": "20260807141948", "united-kingdom": "20251225062440", "viet-nam": "20260714005424",
}


def dates(*groups: tuple[str, str]) -> dict[str, dict]:
    """("AL LI CH", "2010-11-01"), ... -> per-party in_force updates."""
    out: dict[str, dict] = {}
    for codes, day in groups:
        for code in codes.split():
            out[code] = {"in_force": day}
    return out


# Records whose signature and entry-into-force dates the EFTA page states and the registry
# already has: they only gain the link, provenance and official verification.
CONFIRMED = {
    "EFTABA": "bosnia-and-herzegovina", "EFTACA": "canada", "EFTACL": "chile", "EFTAEC": "ecuador",
    "EFTAEG": "egypt", "EFTAIL": "israel", "EFTAJO": "jordan", "EFTAMX": "mexico", "EFTAMA": "morocco",
    "EFTAMK": "north-macedonia", "EFTAPS": "palestinian-authority", "EFTAUA": "ukraine",
}

# Records with changes. Keys: slug, set (top-level fields), parties (code -> fields),
# notes (appended), fields (provenance fields read from the EFTA page), extra (other
# provenance entries), official (verification), replace (provenance fields whose old
# catalogue entries the new source replaces).
CHANGES: dict[str, dict] = {
    "EFTAAL": {
        "slug": "albania",
        "parties": dates(("AL LI CH", "2010-11-01"), ("NO", "2011-08-01"), ("IS", "2011-10-01")),
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTACO": {
        "slug": "colombia",
        "parties": dates(("CO LI CH", "2011-07-01"), ("NO", "2014-09-01"), ("IS", "2014-10-01")),
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTAME": {
        "slug": "montenegro",
        "parties": dates(("ME LI CH", "2012-09-01"), ("IS", "2012-10-01"), ("NO", "2012-11-01")),
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTARS": {
        "slug": "serbia",
        "parties": dates(("RS LI CH", "2010-10-01"), ("NO", "2011-06-01"), ("IS", "2011-10-01")),
        "notes": "The EFTA page gives Iceland's date without the year; the WTO RTA-IS card gives 2011-10-01.",
        "fields": ["signed", "in_force", "parties"], "extra": [("parties", WTO, CARD.format(603))],
        "official": True,
    },
    "EFTATN": {
        "slug": "tunisia",
        "parties": dates(("LI CH", "2005-06-01"), ("NO", "2005-08-01"), ("IS", "2006-03-01")),
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTAPE": {
        "slug": "peru",
        "parties": {
            **dates(("LI CH", "2011-07-01"), ("IS", "2011-10-01"), ("NO", "2012-07-01")),
            "PE": {"signed": "2010-07-14", "in_force": "2011-07-01"},
        },
        "notes": "The EFTA States signed in Reykjavik on 24 June 2010; Peru signed in Lima on 14 July 2010.",
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTACRPA": {
        "slug": "central-american-states-costa-rica-guatemala-honduras-and-panama",
        "parties": {
            **dates(("CR PA NO", "2014-08-19"), ("LI CH", "2014-08-29"), ("IS", "2014-09-05")),
            "GT": {"note": "Accession protocol signed in Schaan on 22 June 2015; entry into force pending (EFTA, "
                           "page captured 2026-02-15)."},
        },
        "notes": "Honduras took part in the first five negotiation rounds; EFTA lists its accession talks as on hold.",
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTAMD": {
        "slug": "moldova",
        "parties": dates(("MD IS", "2024-09-01"), ("NO", "2024-11-01"), ("LI CH", "2025-04-01")),
        "notes": "The EFTA page's key facts give 24 November 2017, the date of the Joint Declaration on Cooperation; "
                 "the signature date is from WTO RTA-IS.",
        "fields": ["in_force", "parties"],
    },
    "EFTATH": {
        "slug": "thailand",
        "set": {"status": "signed", "signed": "2025-01-23"},
        "notes": "Negotiations relaunched in June 2022 and concluded on 29 November 2024; signed in Davos on "
                 "23 January 2025, entry into force pending (EFTA, page captured 2026-02-11).",
        "fields": ["status", "signed"], "replace": ["status"], "official": True,
    },
    "EFTAMY": {
        "slug": "malaysia",
        "set": {
            "name": "EFTA-Malaysia Economic Partnership Agreement",
            "acronyms": [{"lang": "en", "value": "MEEPA"}],
            "status": "signed", "signed": "2025-06-23",
        },
        "other_names": [{"lang": "en", "name": "Malaysia-European Free Trade Association Free Trade Agreement"}],
        "notes": "Negotiations paused from 2017 to 2020 and concluded on 11 April 2025; signed in Tromsø on "
                 "23 June 2025 together with a Memorandum of Understanding on Cooperation and Capacity Building, "
                 "entry into force pending (EFTA, page captured 2026-08-22).",
        "fields": ["name", "status", "signed"], "replace": ["status"], "official": True,
    },
    "EFTASG-DEA": {
        "slug": "singapore",
        "set": {"status": "in_force", "signed": "2025-09-25", "in_force": "2026-03-01"},
        "parties": {
            "SG": {"in_force": "2026-03-01"}, "NO": {"in_force": "2026-03-01"},
            "IS": {"note": "Ratification pending."}, "LI": {"note": "Ratification pending."},
            "CH": {"note": "Ratification pending."},
        },
        "notes": "Negotiations concluded on 10 July 2025; signed on 25 September 2025; in force for Norway and "
                 "Singapore since 1 March 2026 (EFTA, page captured 2026-10-08).",
        "fields": ["status", "signed", "in_force", "parties"], "replace": ["status"], "official": True,
    },
    "GBISLINO": {
        "slug": "united-kingdom",
        "set": {"in_force": "2022-09-01"},
        "parties": dates(("GB LI NO", "2022-09-01"), ("IS", "2023-02-01")),
        "notes": "WTO RTA-IS gives 2021-12-01 as the date of entry into force; its remarks show that date as the "
                 "start of provisional application between the UK and Norway (Liechtenstein 2022-01-01, Iceland "
                 "2022-09-01).",
        "fields": ["signed", "in_force", "parties"], "extra": [("parties", WTO, CARD.format(1173))],
        "official": True,
    },
    "EFTALB": {
        "slug": "lebanon",
        "notes": "The EFTA page (captured 2026-08-13) gives 1 July 2007 as the date of entry into force; the Fedlex "
                 "scope-of-application table and WTO RTA-IS give 1 January 2007 for all five parties.",
        "fields": ["signed"], "extra": [("in_force", FEDLEX, FEDLEX_LB), ("parties", FEDLEX, FEDLEX_LB)],
        "official": True,
    },
    "EFTAMERCOSUR": {
        "slug": "mercosur",
        "parties": {
            **dates(("BR IS", "2026-10-01"), ("UY NO", "2026-11-01")),
            **{c: {"note": "Entry into force pending."} for c in ("AR", "PY", "LI", "CH")},
        },
        "notes": "In force between Brazil and Iceland from 1 October 2026, and for Uruguay and Norway from "
                 "1 November 2026; pending for Argentina, Paraguay, Liechtenstein and Switzerland (EFTA, page "
                 "captured 2026-11-15; WTO RTA-IS).",
        "fields": ["signed", "in_force", "parties"], "official": True,
    },
    "EFTAXK": {
        "slug": "kosovo",
        "parties": dates(("XK IS NO", "2026-09-01"), ("LI CH", "2026-10-01")),
        "notes": "Negotiations launched in June 2022 and concluded on 26 September 2024; signed in Davos on "
                 "22 January 2025 (EFTA). The per-party dates are from WTO RTA-IS; the EFTA page captured "
                 "2026-02-14 still showed entry into force as pending.",
        "fields": ["signed"], "extra": [("parties", WTO, CARD.format(1056))],
    },
    "EFTATSOUZ": {
        "slug": "russia-belarus-kazakhstan",
        "notes": "EFTA lists the negotiations as suspended: launched in January 2011, 11 rounds held (page captured "
                 "2025-12-31).",
        "fields": ["status"],
    },
    "EFTAVN": {
        "slug": "viet-nam",
        "notes": "Negotiations launched in July 2012 and concluded on 2 July 2026; not yet signed (EFTA, page "
                 "captured 2026-07-14).",
        "fields": ["status"], "replace": ["status"], "official": True,
    },
}
for record_id, slug in CONFIRMED.items():
    CHANGES[record_id] = {"slug": slug, "fields": ["signed", "in_force", "parties"], "official": True}


def ordered(mapping: dict, order: list[str]) -> dict:
    return {k: mapping[k] for k in order if k in mapping}


def apply(record: dict, change: dict) -> dict:
    slug = change["slug"]
    record.update(change.get("set", {}))
    if "other_names" in change:
        names = record.setdefault("other_names", [])
        names.extend(n for n in change["other_names"] if n not in names)

    by_code = {p["id"]: p for p in record["parties"]}
    for code, fields in change.get("parties", {}).items():
        by_code[code].update(fields)
    record["parties"] = [ordered(p, PARTY_ORDER) for p in record["parties"]]

    if change.get("notes"):
        record["notes"] = f"{record['notes']} {change['notes']}" if record.get("notes") else change["notes"]

    link = {"url": PAGE.format(slug), "type": "website"}
    links = record.setdefault("links", [])
    if link not in links:
        links.insert(0, link)

    replaced = set(change.get("replace", [])) | set(change.get("set", {}))
    provenance = [p for p in record["provenance"] if p["field"] not in replaced]
    snapshot = SNAPSHOT.format(CAPTURES[slug], slug)
    entries = [(field, EFTA, snapshot) for field in change["fields"]] + change.get("extra", [])
    for field, source, url in entries:
        provenance = [p for p in provenance if not (p["field"] == field and p["source"] == source)]
        provenance.append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})
    record["provenance"] = provenance

    if change.get("official"):
        record["verification"] = "official"
    record["last_verified"] = RETRIEVED
    return ordered(record, FIELD_ORDER)


def main() -> int:
    for record_id, change in sorted(CHANGES.items()):
        path = REGISTRY / f"{record_id}.yaml"
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        record = apply(record, change)
        path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
        print(f"{record_id}: {record['status']}, {record['verification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
