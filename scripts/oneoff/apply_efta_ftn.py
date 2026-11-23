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
  when EFTA (or Fedlex) states its parties and dates;
- creates records for the seven Joint Declarations on Cooperation with partners that have
  no other EFTA agreement (agreement_type framework), the signed modernised agreements
  with Ukraine (2025) and Chile (2024 amending protocol), and the EFTA-Algeria
  negotiations, which EFTA lists as on hold. Their texts were read from Wayback copies of
  the PDFs linked on the partner pages.

Run from the repository root: python scripts/oneoff/apply_efta_ftn.py. A second run
changes nothing.
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
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]
PARTY_ORDER = ["id", "type", "signed", "in_force", "provisional_application", "left", "note"]

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
    # The gov.uk review (PR 215) already moved in_force to 2022-09-01 and recorded the provisional
    # application dates that WTO RTA-IS gives as entry into force, so only EFTA's evidence is added here.
    "GBISLINO": {
        "slug": "united-kingdom",
        "parties": dates(("GB LI NO", "2022-09-01"), ("IS", "2023-02-01")),
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
        "set": {"status": "suspended"},  # status added by add-suspended-trade-agreement-status
        "notes": "EFTA lists the negotiations as suspended: launched in January 2011, 11 rounds held (page captured "
                 "2025-12-31).",
        "fields": ["status", "parties"], "official": True,
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
CHANGES["EFTAUA"]["notes"] = (
    "A modernised free trade agreement signed at Kyiv on 8 April 2025 (EFTAUA-2025) replaces this one for each "
    "EFTA State on its entry into force with Ukraine."
)
CHANGES["EFTACL"]["notes"] = (
    "A protocol signed at Geneva on 24 June 2024 (EFTACL-2024) amends this agreement into the modernised EFTA-Chile "
    "Free Trade Agreement; it was not yet in force when the EFTA page was captured on 2026-08-04."
)

# Amending protocols, revised agricultural agreements, review talks and official names, added
# as notes and other_names (EFTA pages; dates cross-checked on the WTO RTA-IS cards, titles
# on Fedlex).
FEDLEX_EC = "https://fedlex.data.admin.ch/eli/cc/2020/784/de"
FEDLEX_PS = "https://fedlex.data.admin.ch/eli/cc/2004/525/de"
FEDLEX_TITLE = "Fedlex, classified compilation (title of the agreement)"
LATER: dict[str, dict] = {
    "EFTAAL": {"notes": "An amending protocol signed on 18 September 2015 has been in force since 1 June 2017.",
               "extra": [("notes", WTO, CARD.format(600))]},
    "EFTARS": {"notes": "An amending protocol on trade and sustainable development signed on 20 May 2015 has been "
                        "in force since 1 February 2017.",
               "extra": [("notes", WTO, CARD.format(603))]},
    "EFTAME": {"notes": "An amending protocol signed on 14 July 2021 has been in force since 1 April 2022.",
               "extra": [("notes", WTO, CARD.format(765))]},
    "EFTABA": {"notes": "An amending protocol signed on 7 July 2022, with protocols amending the three bilateral "
                        "agricultural agreements, has been in force since 1 September 2023.",
               "extra": [("notes", WTO, CARD.format(740))]},
    "EFTAJO": {"notes": "Joint Committee Decision No. 1/2025 (adopted 10 June 2025, in force 1 February 2026) "
                        "modernised the rules of origin in Protocol B, with matching amendments to the three "
                        "bilateral agricultural agreements.",
               "extra": [("notes", WTO, CARD.format(75))]},
    "EFTATN": {"notes": "Joint Committee Decision No. 1/2024 (adopted 9 October 2024) introduced the modernised "
                        "Pan-Euro-Mediterranean rules of origin; WTO RTA-IS gives its entry into force as 1 March "
                        "2026, while the EFTA page captured 2026-02-19 still showed it as pending.",
               "extra": [("notes", WTO, CARD.format(37))]},
    "EFTAIL": {"notes": "Revised bilateral agricultural agreements, signed in Geneva on 22 November 2018, replaced the "
                        "original ones on 1 August 2021."},
    "EFTAMX": {"notes": "EFTA reports a fourth round of negotiations on a review of the agreement in June 2017 and "
                        "talks on its modernisation in February 2022 (page captured 2026-02-19)."},
    "EFTASACU": {"slug": "southern-african-customs-union-sacu",
                 "notes": "EFTA and SACU launched a review of the agreement in January 2018 to update and expand it; "
                          "negotiations were continuing in November 2021 (EFTA, page captured 2026-02-19)."},
    "EFTAPS": {"set": {"name": "EFTA-Palestine Interim Agreement"},
               "other_names": [
                   {"lang": "en", "name": "Interim Agreement between the EFTA States and the PLO for the benefit of "
                                          "the Palestinian Authority"},
                   {"lang": "en", "name": "EFTA - Palestine"}],
               "notes": "Concluded with the Palestine Liberation Organization (PLO) acting for the benefit of the "
                        "Palestinian Authority.",
               "extra": [("name", FEDLEX_TITLE, FEDLEX_PS)]},
    "EFTAEC": {"set": {"name": "EFTA-Ecuador Comprehensive Economic Partnership Agreement"},
               "other_names": [
                   {"lang": "en", "name": "Comprehensive Economic Partnership Agreement between the EFTA States and "
                                          "Ecuador"},
                   {"lang": "en", "name": "EFTA - Ecuador"}],
               "extra": [("name", FEDLEX_TITLE, FEDLEX_EC)]},
}
CAPTURES["southern-african-customs-union-sacu"] = "20260219082111"
for record_id, later in LATER.items():
    change = CHANGES.setdefault(record_id, {"slug": later.get("slug"), "fields": []})
    notes = change.get("notes")
    change["notes"] = ([notes] if isinstance(notes, str) else notes or []) + (
        [later["notes"]] if "notes" in later else [])
    change.setdefault("set", {}).update(later.get("set", {}))
    change.setdefault("other_names", []).extend(later.get("other_names", []))
    change.setdefault("extra", []).extend(later.get("extra", []))
    if "set" in later:
        change["fields"].append("name")
    if "notes" in later:
        change["fields"].append("notes")

EFTA_STATES = ["IS", "LI", "NO", "CH"]
TEXT = "EFTA, text of the instrument as published on efta.int (Wayback Machine copy)"
WB = "https://web.archive.org/web/{}/https://www.efta.int/sites/default/files/{}"


def jdc(code: str, slug: str, capture: str, name: str, title: str, day: str, text: str, notes: str,
        partners: list[str] | None = None) -> dict:
    """A Joint Declaration on Cooperation: effective on signature, no ratification clause."""
    return {
        "slug": slug, "capture": capture, "text": text,
        "record": {
            "id": f"EFTA{code}-JDC", "name": name, "other_names": [{"lang": "en", "name": title}],
            "agreement_type": "framework", "status": "in_force", "signed": day, "in_force": day,
            "parties": [{"id": c, "type": "country"} for c in (partners or [code]) + EFTA_STATES],
            "notes": notes,
        },
    }


# New records: slug and capture of the EFTA partner page, Wayback URL of the text read.
NEW: list[dict] = [
    jdc("DZ", "algeria", "20260214061541", "EFTA-Algeria Joint Declaration on Cooperation",
        "Declaration by the EFTA States and the People's Democratic Republic of Algeria", "2002-12-12",
        WB.format("20251225160523", "media/documents/legal-texts/free-trade-relations/algeria/algeria-jdc.pdf"),
        "Signed at Interlaken; establishes a Joint Committee. Free trade negotiations followed (EFTADZ)."),
    jdc("ASEAN", "asean", "20251225111051", "EFTA-ASEAN Joint Declaration on Economic Cooperation",
        "Joint Declaration on Economic Cooperation between the Association of Southeast Asian Nations (ASEAN) and "
        "the Member States of the European Free Trade Association (EFTA)", "2024-09-19",
        WB.format("20251226023404", "uploads/2024-09/ASEAN-EFTA%20JDC_190924.pdf"),
        "Adopted at Vientiane; comes into effect on the date of its adoption. The parties are the ten ASEAN Member "
        "States named in the text and the four EFTA States, not ASEAN as an organisation.",
        partners=["BN", "KH", "ID", "LA", "MY", "MM", "PH", "SG", "TH", "VN"]),
    jdc("MU", "mauritius", "20251225110855", "EFTA-Mauritius Joint Declaration on Cooperation",
        "Joint Declaration on Co-operation between the EFTA States and the Republic of Mauritius", "2009-06-09",
        WB.format("20251225164119", "media/documents/legal-texts/free-trade-relations/mauritius/mauritius-jdc.pdf"),
        "Signed at Geneva; establishes a Joint Committee."),
    jdc("MN", "mongolia", "20260210051008", "EFTA-Mongolia Joint Declaration on Cooperation",
        "Joint Declaration on Co-operation between the EFTA States and Mongolia", "2007-06-28",
        WB.format("20251226070538", "documents/legal-texts/free-trade-relations/mongolia/"
                  "Joint%20Declaration%20on%20Cooperation%20English%20English.pdf"),
        "Signed at Vaduz; establishes a Joint Committee."),
    jdc("MM", "myanmar", "20251225111136", "EFTA-Myanmar Joint Declaration on Cooperation",
        "Joint Declaration on Cooperation between Iceland, the Principality of Liechtenstein, the Kingdom of Norway "
        "and the Swiss Confederation and the Republic of the Union of Myanmar", "2013-06-24",
        WB.format("20251213172143", "media/documents/legal-texts/free-trade-relations/myanmar/myanmar-jdc.pdf"),
        "Signed at Trondheim; establishes a Joint Committee."),
    jdc("NG", "nigeria", "20251225110916", "EFTA-Nigeria Joint Declaration on Economic Cooperation",
        "Joint Declaration on Economic Cooperation between the Governments of the Member States of the European "
        "Free Trade Association (EFTA) and the Government of the Federal Republic of Nigeria", "2017-12-12",
        WB.format("20251225165052", "documents/legal-texts/free-trade-relations/nigeria/"
                  "EFTA-NIGERIA-JOINT-DECLARATION-ON-COOPERATION.pdf.PDF"),
        "Signed at Buenos Aires; comes into effect on signature and remains in effect unless either side "
        "terminates it with 180 days' notice. Establishes a Joint Committee."),
    jdc("PK", "pakistan", "20251225111143", "EFTA-Pakistan Joint Declaration on Cooperation",
        "Joint Declaration on Cooperation between the EFTA States and the Islamic Republic of Pakistan", "2012-11-12",
        WB.format("20251226070820", "media/documents/legal-texts/free-trade-relations/pakistan/"
                  "EFTA-Pakistan-Joint-Declaration-on-Cooperation.pdf"),
        "Signed at Geneva; establishes a Joint Committee."),
    {
        "slug": "ukraine", "capture": "20260807141948",
        "text": WB.format("20251226161247", "uploads/2025-04/EFTA-Ukraine%20-%20Main%20Agreement.pdf"),
        "record": {
            "id": "EFTAUA-2025", "name": "Modernised EFTA-Ukraine Free Trade Agreement",
            "other_names": [{"lang": "en", "name": "Free Trade Agreement between the EFTA States and Ukraine (2025)"}],
            "agreement_type": "fta", "status": "signed", "signed": "2025-04-08",
            "parties": [{"id": c, "type": "country"} for c in ["UA", *EFTA_STATES]],
            "notes": "Signed at Kyiv; negotiations launched in June 2023 and concluded on 2 December 2024. On its "
                     "entry into force between an EFTA State and Ukraine it replaces, for those Parties, the "
                     "agreement signed on 24 June 2010 (EFTAUA). Not in force when the EFTA page was captured on "
                     "2026-08-07.",
        },
    },
    {
        "slug": "chile", "capture": "20260804055322",
        "text": WB.format("20251225214542", "uploads/2024-06/Amending%20Protocol_0.pdf"),
        "record": {
            "id": "EFTACL-2024", "name": "Protocol Amending the EFTA-Chile Free Trade Agreement",
            "other_names": [{"lang": "en", "name": "Protocol Amending the Free Trade Agreement between the EFTA "
                                                  "States and the Republic of Chile"}],
            "agreement_type": "fta", "status": "signed", "signed": "2024-06-24",
            "parties": [{"id": c, "type": "country"} for c in ["CL", *EFTA_STATES]],
            "notes": "Signed at Geneva; negotiations launched in 2019 and concluded on 19 January 2024. The protocol "
                     "replaces whole chapters and annexes of the 2003 agreement (EFTACL); EFTA publishes the result "
                     "as the consolidated EFTA-Chile Free Trade Agreement 2024. Not in force when the EFTA page was "
                     "captured on 2026-08-04.",
        },
    },
    {
        "slug": "algeria", "capture": "20260214061541", "text": None,
        "record": {
            "id": "EFTADZ", "name": "EFTA-Algeria Free Trade Agreement",
            "agreement_type": "fta", "status": "suspended",
            "parties": [{"id": c, "type": "country"} for c in ["DZ", *EFTA_STATES]],
            "notes": "Four negotiation rounds were held in 2007 and 2008, after the 2002 declaration (EFTADZ-JDC). "
                     "EFTA lists the negotiations as on hold (page captured 2026-02-14).",
        },
    },
]

# Joint declarations that preceded an EFTA free trade agreement, linked from the partner pages.
# Texts read from Wayback copies of the PDFs; four are scans (Jordan, Montenegro, North
# Macedonia, Palestinian Authority) and were read from page images.
WAYBACK = "https://web.archive.org/web/"
PRECEDING_TEXTS = {
    "albania": "20251226113542/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
               "Albania/EFTA-Albania%20Joint%20Declaration%20on%20Cooperation.pdf",
    "panama": "20251225214246/http://www.efta.int/sites/default/files/media/documents/legal-texts/free-trade-relations/"
              "panama/panama-jdc.pdf",
    "colombia": "20251225220552/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
                "colombia/EFTA-Colombia%20Joint%20Declaration%20on%20Cooperation%20EN.pdf",
    "ecuador": "20251226020953/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
               "ecuador/EFTA-Ecuador%20Joint%20Declaration%20of%20Cooperation.pdf",
    "egypt": "20251225160844/http://www.efta.int/sites/default/files/media/documents/legal-texts/free-trade-relations/"
             "egypt/EFTA-Egypt%20Joint%20Declaration%20on%20Cooperation.pdf",
    "georgia": "20251226114631/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
               "free-trade-relations/georgia/efta-georgia-joint-declaration-on-cooperation.pdf",
    "gulf-cooperation-council-gcc": "20251225161604/http://www.efta.int/sites/default/files/media/documents/"
                                    "legal-texts/free-trade-relations/gulf-cooperation-council-GCC/"
                                    "EFTA-GCC%20Joint%20Declaration%20on%20Cooperation.pdf",
    "jordan": "20251225163336/http://www.efta.int/sites/default/files/media/documents/legal-texts/free-trade-relations/"
              "Jordan/EFTA-Jordan%20Joint%20Declaration%20on%20Cooperation.pdf",
    "kosovo": "20251226115127/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
              "kosovo/EFTA-Kosovo-Joint-Declaration-on-Cooperation.pdf",
    "lebanon": "20251225163951/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
               "free-trade-relations/lebanon/EFTA-Lebanon%20Joint%20Declaration%20on%20Cooperation.pdf",
    "malaysia": "20251226065435/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
                "free-trade-relations/malaysia/malaysia-jdc.pdf",
    "mercosur": "20251226021801/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
                "free-trade-relations/mercosur/Joint%20Declaration%20of%20Cooperation%20Mercosur.pdf",
    "moldova": "20251226115351/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
               "moldova/17-2684rev1.15%20EFTA-Moldova-Joint-Declaration-on-Cooperation.pdf",
    "serbia": "20260211135603/https://www.efta.int/sites/default/files/media/documents/legal-texts/"
              "free-trade-relations/serbia/EFTA-Serbia%20Joint%20Declaration%20on%20Cooperation.pdf",
    "morocco": "20251225164940/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
               "free-trade-relations/morocco/EFTA-Morocco%20Joint%20Declaration%20on%20Cooperation.pdf",
    "north-macedonia": "20251226121052/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
                       "free-trade-relations/macedonia/EFTA-Macedonia%20Joint%20Declaration%20on%20Cooperation.pdf",
    "palestinian-authority": "20251225211428/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
                             "free-trade-relations/palestinian-authority/"
                             "EFTA-Palestinian%20Authority%20%20Joint%20Declaration%20on%20Cooperation.pdf",
    "peru": "20251226023220/http://www.efta.int/sites/default/files/media/documents/legal-texts/free-trade-relations/"
            "peru/joint-declaration-of-cooperation/EFTA-Peru%20Joint%20Declaration%20on%20Cooperation%20EN.pdf",
    "philippines": "20251226071535/http://www.efta.int/sites/default/files/documents/legal-texts/"
                   "free-trade-relations/philippines/EFTA-Philippines%20Joint%20Declaration%20on%20Cooperation.pdf",
    "tunisia": "20251225212843/http://www.efta.int/sites/default/files/media/documents/legal-texts/"
               "free-trade-relations/tunisia/EFTA-Tunisia%20Joint%20Declaration%20on%20Cooperation.pdf",
    "ukraine": "20251226161240/http://www.efta.int/sites/default/files/documents/legal-texts/free-trade-relations/"
               "ukraine/joint-declaration-of-cooperation/EFTA-Ukraine%20Joint%20Declaration%20on%20Cooperation.pdf",
}
CAPTURES.update({"georgia": "20260831055342", "gulf-cooperation-council-gcc": "20251230211834",
                 "philippines": "20260209180017"})
LEFT_1995 = {"left": "1995-01-01", "note": "Left EFTA on joining the European Communities."}
JC = " Establishes a Joint Committee."

# (record id suffix, partner page slug, text key, name, title, signed, notes, partner codes)
PRECEDING = [
    ("AL", "albania", "albania", "EFTA-Albania Joint Declaration on Cooperation",
     "Declaration by the EFTA States and Albania", "1992-12-10",
     "Signed at Geneva by the seven EFTA States of the time." + JC + " Preceded the free trade agreement EFTAAL.",
     ["AL"]),
    ("PA", "central-american-states-costa-rica-guatemala-honduras-and-panama", "panama",
     "EFTA-Panama Joint Declaration on Cooperation",
     "Joint Declaration on Cooperation between the EFTA States and the Republic of Panama", "2010-07-20",
     "Signed at Geneva." + JC + " Preceded the EFTA-Central America free trade agreement EFTACRPA.", ["PA"]),
    ("CO", "colombia", "colombia", "EFTA-Colombia Joint Declaration on Cooperation",
     "Joint Declaration on Co-operation between the EFTA States and the Republic of Colombia", "2006-05-17",
     "Signed at Bern." + JC + " Preceded the free trade agreement EFTACO.", ["CO"]),
    ("EC", "ecuador", "ecuador", "EFTA-Ecuador Joint Declaration on Cooperation",
     "Joint Declaration on Cooperation between the Republic of Ecuador and the EFTA States", "2015-06-22",
     "Signed at Schaan." + JC + " Preceded the comprehensive economic partnership agreement EFTAEC.", ["EC"]),
    ("EG", "egypt", "egypt", "EFTA-Egypt Joint Declaration on Cooperation",
     "Declaration by the EFTA States and Egypt", "1995-12-08",
     "Signed at Zermatt." + JC + " Preceded the free trade agreement EFTAEG.", ["EG"]),
    ("GE", "georgia", "georgia", "EFTA-Georgia Joint Declaration on Cooperation",
     "Joint Declaration on Cooperation between Georgia and the EFTA States", "2012-06-28",
     "Signed at Gstaad." + JC + " Preceded the free trade agreement EFTAGE.", ["GE"]),
    ("GCC", "gulf-cooperation-council-gcc", "gulf-cooperation-council-gcc",
     "EFTA-GCC Joint Declaration on Cooperation", "Declaration by the EFTA States and the GCC Countries",
     "2000-05-23",
     "Signed at Brussels by the EFTA States and the governments of the six GCC member states." + JC
     + " Preceded the free trade agreement EFTAGCC.", ["AE", "BH", "SA", "OM", "QA", "KW"]),
    ("JO", "jordan", "jordan", "EFTA-Jordan Joint Declaration on Cooperation",
     "Declaration by the EFTA States and the Hashemite Kingdom of Jordan", "1997-06-19",
     "Signed at Geneva. Preceded the free trade agreement EFTAJO.", ["JO"]),
    ("XK", "kosovo", "kosovo", "EFTA-Kosovo Joint Declaration on Cooperation",
     "Joint Declaration on Cooperation between the EFTA States and the Republic of Kosovo", "2018-11-23",
     "Signed at Geneva." + JC + " Preceded the free trade agreement EFTAXK.", ["XK"]),
    ("LB", "lebanon", "lebanon", "EFTA-Lebanon Joint Declaration on Cooperation",
     "Declaration by the EFTA States and the Republic of Lebanon", "1997-06-19",
     "Signed at Geneva." + JC + " Preceded the free trade agreement EFTALB.", ["LB"]),
    ("MY", "malaysia", "malaysia", "EFTA-Malaysia Joint Declaration on Economic Cooperation",
     "Joint Declaration on Economic Cooperation between the Government of Malaysia and the Governments of the "
     "Member States of the European Free Trade Association (EFTA)", "2010-07-20",
     "Signed at Geneva; in force from signature unless terminated on six months' notice. Preceded the economic "
     "partnership agreement EFTAMY.", ["MY"]),
    ("MD", "moldova", "moldova", "EFTA-Moldova Joint Declaration on Cooperation",
     "Joint Declaration on Cooperation between the EFTA States and the Republic of Moldova", "2017-11-24",
     "Signed at Geneva." + JC + " Preceded the free trade agreement EFTAMD.", ["MD"]),
    ("MA", "morocco", "morocco", "EFTA-Morocco Joint Declaration on Cooperation",
     "Declaration by the EFTA States and Morocco", "1995-12-08",
     "Signed at Zermatt." + JC + " Preceded the free trade agreement EFTAMA.", ["MA"]),
    ("MK", "north-macedonia", "north-macedonia", "EFTA-North Macedonia Joint Declaration on Cooperation",
     "Declaration by the EFTA States' Governments and the Macedonian Government", "1996-03-29",
     "Signed at Vaduz. Preceded the free trade agreement EFTAMK.", ["MK"]),
    ("PS", "palestinian-authority", "palestinian-authority",
     "EFTA-Palestinian Authority Joint Declaration on Cooperation",
     "Declaration by the EFTA States and the Palestine Liberation Organization (PLO) for the benefit of the "
     "Palestinian Interim Self-Government Authority of the West Bank and Gaza Strip", "1996-12-16",
     "Signed at Geneva with the PLO. Preceded the interim agreement EFTAPS.", ["PS"]),
    ("PE", "peru", "peru", "EFTA-Peru Joint Declaration on Cooperation",
     "Joint Declaration on Co-operation between the EFTA States and the Republic of Peru", "2006-04-24",
     "Signed at Geneva." + JC + " Preceded the free trade agreement EFTAPE.", ["PE"]),
    ("TN", "tunisia", "tunisia", "EFTA-Tunisia Joint Declaration on Cooperation",
     "Declaration by the EFTA States and Tunisia", "1995-12-08",
     "Signed at Zermatt." + JC + " Preceded the free trade agreement EFTATN.", ["TN"]),
    ("UA", "ukraine", "ukraine", "EFTA-Ukraine Joint Declaration on Cooperation",
     "Declaration by the EFTA States and Ukraine", "2000-06-19",
     "Signed at Zurich." + JC + " Preceded the free trade agreement EFTAUA.", ["UA"]),
]
for suffix, slug, key, name, title, day, notes, partners in PRECEDING:
    entry = jdc(suffix, slug, CAPTURES[slug], name, title, day, WAYBACK + PRECEDING_TEXTS[key], notes, partners)
    if suffix == "AL":  # signed before Austria, Finland and Sweden joined the EC
        entry["record"]["parties"] = [{"id": "AL", "type": "country"}] + [
            {"id": c, "type": "country", **(LEFT_1995 if c in ("AT", "FI", "SE") else {})}
            for c in ["AT", "FI", "IS", "LI", "NO", "SE", "CH"]]
    NEW.append(entry)

mercosur = jdc("MERCOSUR", "mercosur", CAPTURES["mercosur"], "EFTA-MERCOSUR Joint Declaration on Cooperation",
               "Declaration on Trade and Investment Co-operation and Action Plan between the EFTA States and the "
               "MERCOSUR Member States", "2000-12-12", WAYBACK + PRECEDING_TEXTS["mercosur"],
               "Signed at Geneva by the EFTA States on 12 December 2000 and at Florianópolis by the MERCOSUR "
               "Member States on 15 December 2000; in effect from signature unless terminated on 180 days' "
               "notice." + JC + " Preceded the free trade agreement EFTAMERCOSUR.",
               ["AR", "BR", "PY", "UY"])
mercosur["record"]["in_force"] = "2000-12-15"
for party in mercosur["record"]["parties"][:4]:
    party["signed"] = "2000-12-15"
NEW.append(mercosur)

yugoslavia = jdc("YU", "serbia", CAPTURES["serbia"], "EFTA-Yugoslavia Joint Declaration on Cooperation",
                 "Declaration by the EFTA States and the Federal Republic of Yugoslavia", "2000-12-12",
                 WAYBACK + PRECEDING_TEXTS["serbia"],
                 "Signed at Geneva with the Federal Republic of Yugoslavia." + JC + " EFTA lists it on both its "
                 "Serbia and Montenegro pages; it preceded the free trade agreements EFTARS and EFTAME.",
                 ["RS", "ME"])
yugoslavia["record"]["parties"][0]["note"] = "Signed by the Federal Republic of Yugoslavia, which Serbia continues."
yugoslavia["record"]["parties"][1]["note"] = ("Part of the Federal Republic of Yugoslavia at signature; independent "
                                              "since 2006.")
NEW.append(yugoslavia)

philippines = jdc("PH", "philippines", CAPTURES["philippines"], "EFTA-Philippines Joint Declaration on Cooperation",
                  "Joint Declaration on Cooperation between the EFTA States (Iceland, the Principality of "
                  "Liechtenstein, the Kingdom of Norway and the Swiss Confederation) and the Republic of the "
                  "Philippines", "2014-06-23", WAYBACK + PRECEDING_TEXTS["philippines"],
                  "Signed at Vestmannaeyjar." + JC + " It takes effect when the Philippines notifies in writing "
                  "that its domestic requirements are met; EFTA does not publish that date, so the status stays "
                  "signed. Preceded the free trade agreement EFTAPH.", ["PH"])
philippines["record"]["status"] = "signed"
del philippines["record"]["in_force"]
NEW.append(philippines)


def create(entry: dict) -> dict:
    """Build a new record; dates, parties and name come from the text when it was read."""
    record = dict(entry["record"])
    record["links"] = [{"url": PAGE.format(entry["slug"]), "type": "website"}]
    record["verification"] = "official"
    record["last_verified"] = RETRIEVED
    page = SNAPSHOT.format(entry["capture"], entry["slug"])
    provenance = [{"field": "status", "source": EFTA, "url": page, "retrieved_at": RETRIEVED}]
    fields = [f for f in ("name", "signed", "in_force", "parties") if f in record]
    if not entry["text"]:
        fields.remove("name")  # a descriptive name for negotiations, not one a page states
    for field in fields:
        source, url = (TEXT, entry["text"]) if entry["text"] else (EFTA, page)
        provenance.append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})
    record["provenance"] = provenance
    return ordered(record, FIELD_ORDER)


def ordered(mapping: dict, order: list[str]) -> dict:
    keys = [k for k in order if k in mapping]
    if "intblock" in keys:  # a linked record names its intblock right after its id
        keys.remove("intblock")
        keys.insert(1, "intblock")
    return {k: mapping[k] for k in keys}


def apply(record: dict, change: dict) -> dict:
    slug = change["slug"]
    record.update(change.get("set", {}))
    if change.get("other_names"):
        names = record.setdefault("other_names", [])
        names.extend(n for n in change["other_names"] if n not in names)

    if "parties" in record:  # a record linked to an intblock reads its parties from there
        by_code = {p["id"]: p for p in record["parties"]}
        for code, fields in change.get("parties", {}).items():
            by_code[code].update(fields)
        record["parties"] = [ordered(p, PARTY_ORDER) for p in record["parties"]]

    notes = change.get("notes") or []
    for note in [notes] if isinstance(notes, str) else notes:
        if note not in record.get("notes", ""):
            record["notes"] = f"{record['notes']} {note}" if record.get("notes") else note

    if "intblock" not in record:  # a linked record takes its links from the intblock
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
    for entry in NEW:
        record = create(entry)
        path = REGISTRY / f"{record['id']}.yaml"
        path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
        print(f"{record['id']}: new, {record['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
