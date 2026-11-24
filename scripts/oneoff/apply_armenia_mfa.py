"""Add Armenia's bilateral trade relations agreements (2026-11-24) to data/trade_agreements/.

One-off script. The facts come from the Armenian Ministry of Foreign Affairs list of bilateral
agreements in the sphere of trade and economy (as of 1 April 2008, columns signature,
ratification and entry into force) and from its bilateral relations pages. In that list a double
space between two dates means the ratification column is empty, so the second date is the entry
into force; two dates separated by one space are signature and ratification. The Latvian record
comes from the Latvian legal portal (likumi.lv), the Lithuanian entry-into-force date from WIPO
Lex.

Only agreements with a known entry-into-force date are written. Held, for want of one: the
agreements with Poland (1992), Estonia (1992 and 2002), China (1992 and 2013), North Korea and
Vietnam (1992), Iran (1992), Syria (1992), Egypt (1999), Iraq and the Republic of Korea (2005),
the trilateral Armenia-Iran-Turkmenistan agreement (1995), and the CIS-era agreements with
Belarus, Kyrgyzstan, Turkmenistan and Uzbekistan.

Usage: python scripts/oneoff/apply_armenia_mfa.py [--dry-run]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "trade_agreements"
TODAY = "2026-11-24"

FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "instruments", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "gptad_id", "dta_id", "unctad_iia_id", "unts_registration", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]

LIST = "Ministry of Foreign Affairs of Armenia, list of bilateral agreements in the sphere of trade and economy (as of 1 April 2008)"
LIST_URL = "https://www.mfa.am/filemanager/Statics/54_en.pdf"
PAGE = "Ministry of Foreign Affairs of Armenia, bilateral relations ({country})"


def page_url(code: str) -> str:
    return f"https://www.mfa.am/en/bilateral-relations/{code.lower()}"


def as_of(dates: str) -> str:
    return (
        f"The Armenian MFA list of 1 April 2008 gives {dates}; the status is the one that list gives, "
        "and no later termination was found."
    )


EU_NOTE = (
    " {country} joined the EU on {date}. Unlike the agreements with Estonia, Latvia, Lithuania and "
    "Poland, which it marks as terminated from 1 May 2004, the MFA list does not mark this one as terminated."
)

# id: (partner, name, signed, in_force, notes, page lists it, extra fields)
IN_FORCE = {
    "AMAT-TRA": ("AT", "Agreement between the Republic of Armenia and the Republic of Austria on bilateral foreign "
                 "economic relations", "1994-04-26", "1997-02-01",
                 as_of("signature on 26 April 1994, ratification on 11 October 1995 and entry into force on "
                       "1 February 1997") + " Austria was already an EU member state when the agreement entered "
                 "into force.", True),
    "AMCY-TRA": ("CY", "Trade Agreement between the Government of the Republic of Armenia and the Government of the "
                 "Republic of Cyprus", "1995-01-18", "1996-07-01",
                 as_of("signature on 18 January 1995, ratification on 12 June 1996 and entry into force on 1 July 1996")
                 + EU_NOTE.format(country="Cyprus", date="1 May 2004"), False),
    "AMBG-TRA": ("BG", "Agreement between the Government of the Republic of Armenia and the Government of the Republic "
                 "of Bulgaria on Trade and Economic Cooperation", "1994-04-25", "1998-12-16",
                 as_of("signature on 25 April 1994, ratification on 4 December 1998 and entry into force on "
                       "16 December 1998") + EU_NOTE.format(country="Bulgaria", date="1 January 2007"), False),
    "AMRO-TRA": ("RO", "Agreement between the Government of the Republic of Armenia and the Government of Romania on "
                 "Trade and Economic Relations and Scientific and Technological Cooperation", "1991-10-04",
                 "1992-11-26",
                 as_of("signature on 4 October 1991, ratification on 28 April 1992 and entry into force on "
                       "26 November 1992") + EU_NOTE.format(country="Romania", date="1 January 2007"), False),
    "AMIN-TRA": ("IN", "Agreement between the Government of the Republic of Armenia and the Government of the Republic "
                 "of India on Trade and Economic Cooperation", "1993-03-11", "1993-03-11",
                 as_of("signature and entry into force on 11 March 1993 and ratification by Armenia on 28 April 1993"),
                 False),
    "AMIR-TRA-1995": ("IR", "Trade Agreement between the Government of the Republic of Armenia and the Government of "
                      "the Islamic Republic of Iran", "1995-05-06", "1997-01-18",
                      as_of("signature on 6 May 1995, ratification on 26 March 1996 and entry into force on "
                            "18 January 1997") + " The earlier Agreement on Trade-Economic, Science and Technical "
                      "Cooperation of 17 March 1992 is not recorded: the list gives no entry-into-force date.", False),
    "AMLB-TRA": ("LB", "Agreement between the Government of the Republic of Armenia and the Government of the Lebanese "
                 "Republic on Commercial, Economic, Scientific and Technical Cooperation", "1995-05-01",
                 "1999-10-03",
                 as_of("signature on 1 May 1995, ratification on 14 November 1995 and entry into force on "
                       "3 October 1999"), False),
    "AEAM-TRA": ("AE", "Agreement between the Government of the Republic of Armenia and the Government of the United "
                 "Arab Emirates on Trade, Economic and Technical Cooperation", "2002-04-20", "2003-01-27",
                 as_of("signature on 20 April 2002, ratification on 8 August 2002 and entry into force on "
                       "27 January 2003"), True),
    "AMQA-TRA": ("QA", "Agreement between the Government of the Republic of Armenia and the Government of the State of "
                 "Qatar on Trade, Economic and Technical Cooperation", "2002-04-22", "2007-10-08",
                 as_of("signature on 22 April 2002, ratification on 8 August 2002 and entry into force on "
                       "8 October 2007"), True),
    "AMCU-TRA": ("CU", "Agreement between the Government of the Republic of Armenia and the Government of the Republic "
                 "of Cuba on Trade and Economic Cooperation", "2003-03-26", "2004-09-20",
                 as_of("signature on 26 March 2003 and entry into force on 20 September 2004"), True),
    "AMAR-TRA": ("AR", "Agreement on Trade and Economic Cooperation between the Government of the Republic of Armenia "
                 "and the Government of the Argentine Republic", "1994-05-03", "2004-01-15",
                 as_of("signature on 3 May 1994 and entry into force on 15 January 2004"), True),
}

LV_URL = "https://likumi.lv/ta/lv/starptautiskie-ligumi/id/26"
LV = "Latvian legal portal (likumi.lv), international agreements"
WIPO_LT_URL = "https://www.wipo.int/wipolex/en/treaties/parties/470"
WIPO = "WIPO Lex, contracting parties"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in sorted(codes)]


def prov(field: str, source: str, url: str) -> dict:
    return {"field": field, "source": source, "url": url, "retrieved_at": TODAY}


def ordered(record: dict) -> dict:
    extra = [k for k in record if k not in FIELD_ORDER]
    if extra:
        raise SystemExit(f"{record.get('id')}: unknown fields {extra}")
    return {k: record[k] for k in FIELD_ORDER if k in record}


def in_force_records() -> dict[str, dict]:
    out = {}
    for rid, (partner, name, signed, in_force, notes, on_page) in IN_FORCE.items():
        parties_source = (PAGE.format(country=partner), page_url(partner)) if on_page else (LIST, LIST_URL)
        out[rid] = {
            "id": rid,
            "name": name,
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": signed,
            "in_force": in_force,
            "parties": country("AM", partner),
            "notes": notes,
            "verification": "official",
            "last_verified": TODAY,
            "provenance": [
                prov("parties", *parties_source),
                prov("status", LIST, LIST_URL),
                prov("signed", LIST, LIST_URL),
                prov("in_force", LIST, LIST_URL),
            ],
        }
    return out


def terminated_records() -> dict[str, dict]:
    return {
        "AMLV-TRA": {
            "id": "AMLV-TRA",
            "name": "Agreement between the Government of the Republic of Latvia and the Government of the Republic of "
                    "Armenia on the Principles of Trade and Economic Cooperation",
            "other_names": [{
                "lang": "lv",
                "name": "Latvijas Republikas valdības un Armēnijas Republikas valdības nolīgums par tirdznieciski "
                        "ekonomiskās sadarbības principiem",
            }],
            "agreement_type": "trade_relations",
            "status": "terminated",
            "signed": "1993-06-15",
            "in_force": "1993-06-15",
            "ended": "2004-05-01",
            "parties": country("AM", "LV"),
            "links": [{"url": LV_URL, "type": "treaty_text"}],
            "notes": "Article 2 grants most-favoured-nation treatment. It lost force on 1 May 2004, when Latvia joined "
                     "the EU; the Armenian MFA list of 1 April 2008 also marks it as terminated from that date.",
            "verification": "official",
            "last_verified": TODAY,
            "provenance": [
                prov("parties", LV, LV_URL),
                prov("status", LV, LV_URL),
                prov("signed", LV, LV_URL),
                prov("in_force", LV, LV_URL),
                prov("ended", LV, LV_URL),
            ],
        },
        "AMLT-TRA": {
            "id": "AMLT-TRA",
            "name": "Agreement between the Government of the Republic of Lithuania and the Government of the Republic "
                    "of Armenia on Trade and Economic Cooperation",
            "agreement_type": "trade_relations",
            "status": "terminated",
            "signed": "1998-04-23",
            "in_force": "2003-01-29",
            "ended": "2004-05-01",
            "parties": country("AM", "LT"),
            "notes": "Signed in Moscow. The Armenian MFA list of 1 April 2008 gives ratification by Armenia on "
                     "21 March 2001 and marks the agreement as terminated from 1 May 2004, when Lithuania joined the "
                     "EU. Lithuania's Ministry of Foreign Affairs gives signature on 26 April 1998; WIPO Lex and the "
                     "Armenian list give 23 April 1998.",
            "verification": "official",
            "last_verified": TODAY,
            "provenance": [
                prov("parties", WIPO, WIPO_LT_URL),
                prov("status", LIST, LIST_URL),
                prov("signed", LIST, LIST_URL),
                prov("in_force", WIPO, WIPO_LT_URL),
                prov("ended", LIST, LIST_URL),
            ],
        },
    }


ROMANIA_PROTOCOL = {
    "id": "amendment-protocol-2006",
    "kind": "amending_protocol",
    "name": "Amendment Protocol to the Agreement on Trade and Economic Relations and Scientific and Technological "
            "Cooperation",
    "status": "signed",
    "signed": "2006-10-04",
    "notes": "In ratification as of the Armenian MFA list of 1 April 2008.",
    "provenance": [prov("instruments", LIST, LIST_URL)],
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    records = {**in_force_records(), **terminated_records()}
    records["AMRO-TRA"]["instruments"] = [ROMANIA_PROTOCOL]
    for rid, record in records.items():
        path = DATA / f"{rid}.yaml"
        if path.exists():
            raise SystemExit(f"{rid}: exists")
        text = yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120)
        if args.dry_run:
            print(text)
        else:
            path.write_text(text, encoding="utf-8")
    print(f"{len(records)} records")


if __name__ == "__main__":
    main()
