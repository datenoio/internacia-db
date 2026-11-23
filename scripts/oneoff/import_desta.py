#!/usr/bin/env python3
"""One-off: add trade agreements that DESTA lists and the registry lacks, with official dates.

DESTA (Design of Trade Agreements, https://www.designoftradeagreements.org/downloads/) is an
academic catalogue of preferential trade agreements. Its list of treaties v2.3 has 903 base
treaties. ``match_desta.py`` matched them to the registry on 2026-11-23 (report:
``docs/history/desta-match-2026-11-23.md``). Most of the agreements it found missing are
bilateral and were never notified to the WTO.

DESTA gives a year of signature and a year of entry into force, not a status. Like the GPTAD
walk, a record created from DESTA does not take its status or dates from DESTA: every record
below cites a depositary or a party government for them, and DESTA only for the fact that
it lists the agreement (provenance field ``desta_id``, the DESTA ``number``; see the OpenSpec
change ``add-desta-catalogue-links``). Agreements with no such source are held and listed in
the pull request.

Sources:

- ALADI, the depositary of the partial scope agreements of the 1980 Montevideo Treaty. Its
  historical agreements database (``histtextacdos.nsf``) gives the date of signature, the
  entry into force clause, the date of entry into force and a Secretariat note on how the
  agreement ended: on a fixed date ("rigió hasta", "caducó"), or when a later agreement took
  effect between the same parties, whose date the note gives or the later agreement's ALADI
  record gives. ``datenoio/internacia-db#226`` added the current ALADI agreements and left
  out the historical ones because their records give no end date; the records here are the
  historical agreements DESTA lists whose end date ALADI states or derives from a successor.
  A successor that is only in an open pull request (#209, #218 or #226) cannot be ``superseded_by``
  yet, so those records are ``terminated`` until it merges (``PENDING_SUCCESSORS``).
- Party governments: the UAE Ministry of Economy and Tourism and the Emirates News Agency
  (WAM), the Israeli Ministry of Foreign Affairs, the Kenyan National Assembly, the Serbian
  government and Ministry of Foreign Affairs, Jordan's export portal (Ministry of Industry,
  Trade and Supply), the Turkish Ministry of Trade, the Swiss State Secretariat for Economic
  Affairs, Monaco's official legal database (Legimonaco) and Latvia's official legal portal.
- The WTO: trade policy reviews of Malawi (2002, 2024), Mozambique (2017) and SACU (2009,
  2015), with the Zimbabwe Revenue Authority and Malawi's Ministry of Trade, for four southern
  African bilaterals.

Records are ``verification: official``: their status and dates come from the depositary or a
party government.

Usage: python -I scripts/oneoff/import_desta.py [--write]
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
DESTA = "Design of Trade Agreements (DESTA) v2.3, list of treaties, number {}"
DESTA_URL = "https://www.designoftradeagreements.org/downloads/"
TPR = "https://www.wto.org/english/tratop_e/tpr_e/"
ALADI = "ALADI, historical agreements database"
ALADI_URL = "http://www2.aladi.org/nsfaladi/histtextacdos.nsf/f88cf0ec27a4b651032576790064fc05/{}?OpenDocument"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "gptad_id", "wikidata_id",
    "links", "description", "notes", "verification", "last_verified", "provenance",
]
EN = {
    "AR": "Argentina", "BO": "Bolivia", "BR": "Brazil", "CL": "Chile", "CO": "Colombia", "CU": "Cuba",
    "EC": "Ecuador", "MX": "Mexico", "PE": "Peru", "PY": "Paraguay", "UY": "Uruguay", "VE": "Venezuela",
    "CR": "Costa Rica", "SV": "El Salvador", "GT": "Guatemala", "NI": "Nicaragua",
}
KIND = {
    # ALADI code prefix -> (English title, Spanish title, ALADI short code)
    "ACE": ("Economic Complementation Agreement No. {n} between {p}",
            "Acuerdo de Complementación Económica N° {n}", "AAP.CE No. {n}"),
    "A25TM": ("Partial Scope Agreement No. {n} between {p} (Article 25 of the 1980 Montevideo Treaty)",
              "Acuerdo de Alcance Parcial N° {n} (Artículo 25 del Tratado de Montevideo 1980)",
              "AAP.A25TM No. {n}"),
    "R": ("Partial Scope Renegotiation Agreement No. {n} between {p}",
          "Acuerdo de Alcance Parcial de Renegociación N° {n}", "AAP.R No. {n}"),
}


def joined(parties: list[str]) -> str:
    names = [EN[p] for p in parties]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def aladi(desta: int, kind: str, n: int, parties: list[str], doc: str, signed: str, in_force: str,
          status: str, ended: str, superseded_by: str | None = None, agreement_type: str = "pta",
          note: str = "", party_left: dict[str, str] | None = None, in_force_note: str = "",
          ended_from: str | None = None) -> dict:
    """A historical ALADI agreement. ``ended_from`` names the record whose ALADI entry gives the end date."""
    en, es, short = KIND[kind]
    record = {
        "name": en.format(n=n, p=joined(parties)),
        "other_names": [{"lang": "es", "name": es.format(n=n)}],
        "agreement_type": agreement_type,
        "status": status,
        "signed": signed,
        "in_force": in_force,
        "ended": ended,
        "parties": [{"id": p, "type": "country", **({"left": party_left[p]} if party_left and p in party_left else {})}
                    for p in parties],
        "notes": " ".join(x for x in (f"Registered with ALADI as {short.format(n=n)}.", in_force_note, note) if x),
        "_desta": desta,
        "_prov": [(f, ALADI, ALADI_URL.format(doc)) for f in ("parties", "signed", "in_force", "status", "ended")],
    }
    if superseded_by:
        record["superseded_by"] = superseded_by
    if ended_from:
        record["_prov"].append(("ended", f"ALADI record of the successor agreement ({ended_from})", None))
    return record


def gov(desta: int, prov: list[tuple[str, str, str]], **fields) -> dict:
    fields["_desta"] = desta
    fields["_prov"] = prov
    fields["parties"] = [{"id": p, "type": "country"} for p in fields["parties"]]
    return fields


RECORDS: dict[str, dict] = {
    # --- ALADI historical agreements ---------------------------------------------------------
    # Argentina
    "ARBO-1992": aladi(31, "ACE", 19, ["AR", "BO"], "292e7c2463fd9c71032576ee00610021", "1992-04-28",
                       "1992-04-28", "superseded", "1997-02-28", "MERCOSURBO",
                       in_force_note="In force from signature (Article 33); ALADI's entry into force field reads "
                                     "28/04/1982.",
                       note="Under Article 42 of ACE 36 (MERCOSURBO, in force 28 February 1997) the provisions "
                            "of ACE 19 not concerning the trade liberalisation programme stay in force between "
                            "the two countries.", ended_from="MERCOSURBO"),
    "ARBR-1986": aladi(32, "ACE", 7, ["AR", "BR"], "7728a25ad8f932fc03256fbf006d13e0", "1986-12-10",
                       "1987-01-01", "superseded", "1990-12-20", "ARBR",
                       note="Ended when ACE 14 (ARBR) took effect on 20 December 1990 (Article 31 of ACE 14)."),
    "ARBR-1988": aladi(33, "ACE", 12, ["AR", "BR"], "a76125106886345d032576e70054a2d9", "1988-09-09",
                       "1988-09-01", "superseded", "1990-12-20", "ARBR",
                       in_force_note="Article 16 sets entry into force on 1 September 1988, before signature.",
                       note="Ended when ACE 14 (ARBR) took effect (Article 31 of ACE 14).", ended_from="ARBR"),
    "ARCO-1988": aladi(36, "ACE", 11, ["AR", "CO"], "20a695cadb141640032576e30050638a", "1988-04-28",
                       "1988-08-01", "superseded", "2000-08-01", "ARCAN-ACE48",
                       note="Its tariff preferences ended when ACE 48 took effect on 1 August 2000 (Article 27 "
                            "of ACE 48); provisions on matters ACE 48 does not cover stay in force."),
    "ARCR-1983": aladi(37, "A25TM", 2, ["AR", "CR"], "504124eec8022bd6032578ed006a26d5", "1983-08-31",
                       "1983-08-31", "terminated", "1994-12-31",
                       in_force_note="In force from signature (Article 19).",
                       note="Article 19, as amended by the First Additional Protocol, set its term to 31 December "
                            "1994."),
    "ARCU-1984": aladi(38, "A25TM", 4, ["AR", "CU"], "f948202744e6d42e03256fbf006bafcc", "1984-03-16",
                       "1984-05-16", "superseded", "2000-01-01", "ARCU-1999",
                       note="Replaced by ACE 45 (Article 21 of ACE 45), in force 1 January 2000.",
                       ended_from="ARCU-1999"),
    "ARCU-1999": aladi(39, "ACE", 45, ["AR", "CU"], "41051094785864d1032578920051e498", "1999-12-30",
                       "2000-01-01", "superseded", "2007-07-02", "MERCOSURCU",
                       note="Its tariff preferences ended when ACE 62 (MERCOSURCU) took effect between Argentina "
                            "and Cuba on 2 July 2007 (Article 29 of ACE 62)."),
    "ARSV-1983": aladi(42, "A25TM", 3, ["AR", "SV"], "01aeb2756bb5ee00032578ed006a7522", "1983-08-27",
                       "1983-10-27", "terminated", "1994-12-31",
                       note="Article 20, as amended by the First Additional Protocol, set its term to 31 December "
                            "1994."),
    "ARPE-1988": aladi(46, "ACE", 9, ["AR", "PE"], "99c5a3ec454ff45403256fbf006d2f05", "1988-03-11",
                       "1988-04-01", "superseded", "2000-08-01", "ARCAN-ACE48",
                       note="Its tariff preferences ended when ACE 48 took effect (Article 27 of ACE 48); "
                            "provisions on matters ACE 48 does not cover stay in force.", ended_from="ARCAN-ACE48"),
    "ARVE-1986": aladi(48, "ACE", 10, ["AR", "VE"], "40e0dfac298bb0900325763300602b8e", "1986-04-11",
                       "1986-04-11", "superseded", "1995-08-06", "ARVE-1992",
                       note="Its preferences ended when ACE 20 took effect (transitional provision 2 of ACE 20).",
                       ended_from="ARVE-1992"),
    "ARVE-1992": aladi(49, "ACE", 20, ["AR", "VE"], "08a82bb885f0af720325763300640940", "1992-10-06",
                       "1995-08-06", "superseded", "2000-08-01", "ARCAN-ACE48",
                       note="Its tariff preferences ended when ACE 48 took effect on 1 August 2000 (Article 27 "
                            "of ACE 48); provisions on matters ACE 48 does not cover stay in force."),
    "ARUY-1982": aladi(699, "ACE", 1, ["AR", "UY"], "1d5a040ec3cf305403256fbf006cc88d", "1982-12-20",
                       "1985-11-27", "terminated", "2003-05-01",
                       note="Expired on 1 May 2003 under Article 1 of its 28th Additional Protocol; ACE 57 (ARUY) "
                            "took effect the same day."),
    "ARCAN-ACE48": aladi(24, "ACE", 48, ["AR", "CO", "EC", "PE", "VE"], "3d13638d02617fdb032573fa006c2ffb",
                         "2000-06-29", "2000-08-01", "superseded", "2006-01-02", "MERCOSURCOECVE",
                         party_left={"CO": "2005-02-01", "EC": "2005-04-01", "VE": "2005-01-05", "PE": "2006-01-02"},
                         note="Signed by Argentina and the member countries of the Andean Community. Its tariff "
                              "preferences ended when ACE 59 (MERCOSURCOECVE) took effect between Argentina and "
                              "Colombia (1 February 2005), Ecuador (1 April 2005) and Venezuela (5 January 2005), "
                              "and ACE 58 (MERCOSURPE) between Argentina and Peru (2 January 2006); the party "
                              "left dates are those dates.", ended_from="MERCOSURPE"),
    # Bolivia
    "BOBR-1994": aladi(118, "ACE", 26, ["BO", "BR"], "a787ebeaceba1e180325770400669cd1", "1994-01-27",
                       "1994-01-27", "terminated", "1995-12-31",
                       note="Expired on 31 December 1995 under the sole article of its Second Additional "
                            "Protocol. ACE 36 (MERCOSURBO) followed in 1997."),
    "BOMX-1994": aladi(124, "ACE", 31, ["BO", "MX"], "ac1ece6c2b39eaae03257762005e9426", "1994-09-10",
                       "1995-01-01", "superseded", "2010-06-07", "BOMX", agreement_type="fta",
                       in_force_note="Article 21-04 sets entry into force on 1 January 1995.",
                       note="The Bolivia - Mexico Free Trade Treaty. Bolivia denounced it on 7 December 2009 and "
                            "the denunciation took effect on 7 June 2010 (Article 21-07), the day ACE 66 (BOMX) "
                            "took effect."),
    "BOPY-1994": aladi(125, "ACE", 29, ["BO", "PY"], "0fabed1dd29835530325776800522237", "1994-03-15",
                       "1994-03-15", "superseded", "1997-02-28", "MERCOSURBO",
                       note="Under Article 42 of ACE 36 (MERCOSURBO, in force 28 February 1997) its provisions not "
                            "concerning the trade liberalisation programme stay in force.", ended_from="MERCOSURBO"),
    "BOUY-1991": aladi(126, "ACE", 15, ["BO", "UY"], "5c093576df5ae5f80325757d005c092f", "1991-04-12",
                       "1991-04-12", "superseded", "1997-02-28", "MERCOSURBO",
                       note="Under Article 42 of ACE 36 (MERCOSURBO, in force 28 February 1997) its provisions not "
                            "concerning the trade liberalisation programme stay in force.", ended_from="MERCOSURBO"),
    # Brazil
    "BRCU-1999": aladi(139, "ACE", 43, ["BR", "CU"], "66370cd713fc22dc032573470067cf4a", "1999-12-22",
                       "2000-01-01", "superseded", "2007-07-02", "MERCOSURCU",
                       note="Its tariff preferences ended when ACE 62 (MERCOSURCU) took effect between Brazil and "
                            "Cuba on 2 July 2007 (Article 29 of ACE 62)."),
    "BRMX-1983": aladi(712, "R", 9, ["BR", "MX"], "bbc1af103751db40032581b6006b345c", "1983-04-30",
                       "1984-01-01", "superseded", "2003-05-02", "BRMX",
                       note="All its provisions and preferences ended when ACE 53 (BRMX) took effect (Article "
                            "XVIII-3 of ACE 53).", ended_from="BRMX"),
    "BRPE-1993": aladi(142, "ACE", 25, ["BR", "PE"], "73c1494893b866e7032576f000518364", "1993-12-31",
                       "1994-09-28", "superseded", "1999-08-16", "BRCAN-ACE39",
                       note="Its tariff preferences ended when ACE 39 took effect on 16 August 1999 (Article 27 "
                            "of ACE 39)."),
    "BRVE-1994": aladi(145, "ACE", 27, ["BR", "VE"], "60c5a80571fcaafd03256fc000451f98", "1994-07-15",
                       "1995-01-31", "superseded", "1999-08-16", "BRCAN-ACE39",
                       note="Its tariff preferences ended when ACE 39 took effect (Article 27 of ACE 39).",
                       ended_from="BRCAN-ACE39"),
    # Chile
    "CLEC-1994": aladi(203, "ACE", 32, ["CL", "EC"], "4b9689cfa1c0ecd2032576ef004ff1fc", "1994-12-20",
                       "1994-12-20", "superseded", "2010-01-25", "CLEC-2008", agreement_type="fta",
                       note="Establishes an expanded economic area. Ended when ACE 65 took effect on 25 January "
                            "2010 (Article 16-7 of ACE 65)."),
    "CLEC-2008": aladi(204, "ACE", 65, ["CL", "EC"], "69ea9e71d08d3db0032588b1005dc665", "2008-03-10",
                       "2010-01-25", "superseded", "2022-05-16", "CLEC", agreement_type="fta",
                       note="Replaced by ACE 75 (CLEC) from 16 May 2022; certificates under ACE 65 were accepted "
                            "until 14 July 2022."),
    "CLMX-1991": aladi(211, "ACE", 17, ["CL", "MX"], "063833b627a9a27803256fbf006d6ab6", "1991-09-22",
                       "1991-09-22", "superseded", "1999-08-01", "CLMX", agreement_type="fta",
                       note="Ended when ACE 41 (CLMX) took effect (Article 20-10 of ACE 41).", ended_from="CLMX"),
    "CLPE-1983": aladi(214, "R", 28, ["CL", "PE"], "f52314b6805d2f5b03256fc00047dc2f", "1983-04-30",
                       "1983-05-01", "superseded", "1998-07-01", "CLPE-1998",
                       note="Ended when ACE 38 (CLPE-1998) took effect (Article 34 of ACE 38).",
                       ended_from="CLPE-1998"),
    "CLUY-1985": aladi(217, "ACE", 4, ["CL", "UY"], "e60e11c9b2b21ca0032575d2005832c0", "1985-02-01",
                       "1985-02-01", "superseded", "1996-10-01", "MERCOSURCL",
                       note="Its tariff preferences ended when ACE 35 (MERCOSURCL) took effect on 1 October 1996 "
                            "(Article 48 of ACE 35); provisions compatible with ACE 35 stay in force."),
    # Colombia
    "COCU-1988": aladi(231, "A25TM", 19, ["CO", "CU"], "c2493cf75844dbfd03256fbf006c4007", "1988-12-12",
                       "1989-11-21", "superseded", "1995-01-01", "COCU-1994",
                       note="Replaced by AAP.A25TM No. 33 (Article 38 of that agreement).", ended_from="COCU-1994"),
    "COCU-1994": aladi(232, "A25TM", 33, ["CO", "CU"], "6137105e891da69d03256fbf006c689b", "1994-07-08",
                       "1995-01-01", "superseded", "2001-07-14", "COCU",
                       note="Replaced by ACE 49 (COCU; Article 33 of ACE 49).", ended_from="COCU"),
    "COGT-1984": aladi(236, "A25TM", 5, ["CO", "GT"], "bc4948c0e567ee69032576be00446a2d", "1984-03-01",
                       "1985-09-02", "superseded", "2009-11-12", "COGTHNSV",
                       note="Ended when the free trade agreement of Colombia with El Salvador, Guatemala and "
                            "Honduras (COGTHNSV) took effect between Colombia and Guatemala on 12 November 2009 "
                            "(Article 21.3 of that agreement)."),
    # Mexico
    "CRMX-1982": aladi(247, "A25TM", 1, ["CR", "MX"], "6080b50291e5ef2503256fbf006b578c", "1982-07-22",
                       "1984-06-15", "superseded", "1995-01-01", "CRMX",
                       in_force_note="Applied provisionally from signature; definitive entry into force on the "
                                     "exchange of ratifications.",
                       note="ALADI notes that the Costa Rica - Mexico FTA of 5 April 1994 (CRMX, in force "
                            "1 January 1995) superseded it.", ended_from="CRMX"),
    "CUMX-1985": aladi(268, "A25TM", 12, ["CU", "MX"], "399569e751ffc10a03256fbf006c1309", "1985-03-11",
                       "1986-05-28", "superseded", "2001-02-28", "CUMX",
                       note="Ended when ACE 51 (CUMX) took effect (Article 25 of ACE 51).", ended_from="CUMX"),
    "GTMX-1984": aladi(467, "A25TM", 10, ["GT", "MX"], "18c6e19065bdb24c03256fbf006bf0c9", "1984-09-04",
                       "1985-06-07", "superseded", "2001-03-15", "GTMX",
                       note="The 18th Additional Protocol extended it to 31 March 2001 or the entry into force of "
                            "the Mexico - El Salvador, Guatemala and Honduras FTA, whichever came first; that "
                            "agreement (GTMX) took effect for Guatemala on 15 March 2001.", ended_from="GTMX"),
    "MXSV-1986": aladi(417, "A25TM", 15, ["MX", "SV"], "c669bf6b1aa3326503256fbf006c26e9", "1986-02-06",
                       "1987-06-11", "superseded", "2001-03-15", "MXSV",
                       note="The 12th Additional Protocol extended it to 31 March 2001 or the entry into force of "
                            "the Mexico - El Salvador, Guatemala and Honduras FTA, whichever came first; that "
                            "agreement (MXSV) took effect for El Salvador on 15 March 2001.", ended_from="MXSV"),
    "MXNI-1985": aladi(610, "A25TM", 13, ["MX", "NI"], "2b6fd5c1956efdbb03256fbf006c1dbd", "1985-04-08",
                       "1986-08-12", "terminated", "1998-06-30",
                       note="The Fourth Additional Protocol extended it for the last time to 30 June 1998. The "
                            "Mexico - Nicaragua FTA (MXNI) took effect on 1 July 1998."),
    "MXUY-1986": aladi(615, "ACE", 5, ["MX", "UY"], "a0942a89c163c90a0325767f00553f98", "1986-05-07",
                       "1986-06-01", "superseded", "2004-07-15", "MXUY",
                       note="Ended when ACE 60 (MXUY) took effect on 15 July 2004 (Article 20-09 of ACE 60)."),
    # Cuba
    "CUPY-2000": aladi(270, "ACE", 52, ["CU", "PY"], "a594dcb1616661bb03257633006862dc", "2000-11-20",
                       "2001-04-25", "superseded", "2009-02-24", "MERCOSURCU",
                       note="Its tariff preferences ended when ACE 62 (MERCOSURCU) took effect between Cuba and "
                            "Paraguay on 24 February 2009 (Article 29 of ACE 62)."),
    "CUUY-1999": aladi(275, "ACE", 44, ["CU", "UY"], "44213f8f9067d3170325763300684570", "1999-12-23",
                       "2000-01-01", "superseded", "2008-09-03", "MERCOSURCU",
                       note="Its tariff preferences ended when ACE 62 (MERCOSURCU) took effect between Cuba and "
                            "Uruguay on 3 September 2008 (Article 29 of ACE 62)."),

    # --- party governments ---------------------------------------------------------------------
    "AEIL": gov(1096, [
        ("signed", "Israeli Ministry of Foreign Affairs, Consulate General in Dubai, bilateral relations",
         "https://embassies.gov.il/dubai/en/the-consulate/bilateral-relations"),
        ("in_force", "Israeli Ministry of Foreign Affairs, Embassy in Abu Dhabi, economic department",
         "https://embassies.gov.il/united-arab-emirates/en/the-embassy/departments/economic-department"),
        ("status", "Israeli Ministry of Foreign Affairs, Consulate General in Dubai, bilateral relations",
         "https://embassies.gov.il/dubai/en/the-consulate/bilateral-relations"),
    ], name="UAE-Israel Comprehensive Economic Partnership Agreement",
        acronyms=[{"lang": "en", "value": "UAE-Israel CEPA"}], agreement_type="fta", status="in_force",
        signed="2022-05-31", in_force="2023-04-01", parties=["AE", "IL"],
        notes="Signed in Dubai. A customs agreement signed on 26 March 2023 allowed it to take effect."),
    "AERS": gov(1129, [
        ("signed", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/uae-serbia-cepa"),
        ("in_force", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/uae-serbia-cepa"),
        ("status", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/uae-serbia-cepa"),
    ], name="UAE-Serbia Comprehensive Economic Partnership Agreement",
        acronyms=[{"lang": "en", "value": "UAE-Serbia CEPA"}], agreement_type="fta", status="in_force",
        signed="2024-10-05", in_force="2025-06-01", parties=["AE", "RS"],
        notes="The first UAE CEPA with a country that is not a WTO member."),
    "AEMU": gov(1132, [
        ("signed", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/cepa_mauritius"),
        ("in_force", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/cepa_mauritius"),
        ("status", "UAE Ministry of Economy and Tourism", "https://www.moet.gov.ae/en/cepa_mauritius"),
    ], name="UAE-Mauritius Comprehensive Economic Partnership Agreement",
        acronyms=[{"lang": "en", "value": "UAE-Mauritius CEPA"}], agreement_type="fta", status="in_force",
        signed="2024-07-22", in_force="2025-04-01", parties=["AE", "MU"],
        notes="The first UAE CEPA with an African country."),
    "AEKE": gov(1124, [
        ("signed", "Emirates News Agency (WAM)",
         "https://www.wam.ae/en/article/bhopav3-presidents-uae-kenya-take-part-comprehensive"),
        ("status", "Kenya National Assembly, Hansard, 18 November 2025",
         "https://www.parliament.go.ke/sites/default/files/2025-11/Hansard%20Report%20-%20Tuesday,%2018th%20November%202025%20(P).pdf"),
    ], name="UAE-Kenya Comprehensive Economic Partnership Agreement",
        acronyms=[{"lang": "en", "value": "UAE-Kenya CEPA"}], agreement_type="fta", status="signed",
        signed="2025-01-14", parties=["AE", "KE"],
        notes="Signed in Abu Dhabi. The Kenyan National Assembly approved ratification in November 2025 with a "
              "reservation on Article 13.33 (protection of undisclosed test data for pharmaceutical products). No "
              "entry into force was found on 2026-11-23."),
    "AECF": gov(1122, [
        ("signed", "Emirates News Agency (WAM)",
         "https://www.wam.ae/article/bij2epa-uae-president-central-african-republic-president"),
        ("status", "Emirates News Agency (WAM)",
         "https://www.wam.ae/article/bij2epa-uae-president-central-african-republic-president"),
    ], name="UAE-Central African Republic Comprehensive Economic Partnership Agreement",
        acronyms=[{"lang": "en", "value": "UAE-CAR CEPA"}], agreement_type="fta", status="signed",
        signed="2025-03-06", parties=["AE", "CF"],
        notes="Signed in Abu Dhabi. No entry into force was found on 2026-11-23."),
    "EGRS": gov(1130, [
        ("signed", "Government of the Republic of Serbia",
         "https://www.srbija.gov.rs/vest/en/227032/serbia-egypt-sign-free-trade-agreement.php"),
        ("in_force", "Serbian Ministry of Foreign Affairs, Embassy in Cairo",
         "https://cairo.mfa.gov.rs/en/press-service/activities/free-trade-agreement-between-government-republic-serbia-and-government-arab-republic-egypt"),
        ("status", "Serbian Ministry of Foreign Affairs, Embassy in Cairo",
         "https://cairo.mfa.gov.rs/en/press-service/activities/free-trade-agreement-between-government-republic-serbia-and-government-arab-republic-egypt"),
    ], name="Free Trade Agreement between the Government of the Republic of Serbia and the Government of the "
            "Arab Republic of Egypt", agreement_type="fta", status="in_force",
        signed="2024-07-13", in_force="2025-09-01", parties=["EG", "RS"],
        notes="Signed in Cairo. Covers trade in goods; services may follow in later negotiations."),
    "LBTR": gov(1101, [
        ("signed", "Turkish Ministry of Trade, FTAs in ratification",
         "https://ticaret.gov.tr/dis-iliskiler/serbest-ticaret-anlasmalari/onay-sureci-devam-eden-stalar/lubnan"),
        ("status", "Turkish Ministry of Trade, FTAs in ratification",
         "https://ticaret.gov.tr/dis-iliskiler/serbest-ticaret-anlasmalari/onay-sureci-devam-eden-stalar/lubnan"),
    ], name="Agreement Establishing an Association Establishing a Free Trade Area between the Republic of "
            "Türkiye and the Lebanese Republic", agreement_type="fta", status="signed",
        signed="2010-11-24", parties=["LB", "TR"],
        notes="Signed in Beirut. Türkiye completed ratification in 2013 (Law No. 6388); it takes effect once "
              "Lebanon completes its procedures."),
    "JOKW": gov(524, [
        ("in_force", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
        ("status", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
    ], name="Jordan - Kuwait Agreement", agreement_type="fta", status="in_force", in_force="2005",
        parties=["JO", "KW"], notes="Jordan lists it as a bilateral FTA-style agreement in force since 2005."),
    "JOSD": gov(535, [
        ("in_force", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
        ("status", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
    ], name="Jordan - Sudan Agreement", agreement_type="fta", status="in_force", in_force="2003",
        parties=["JO", "SD"], notes="Jordan lists it as a bilateral agreement in force since 2003."),
    "DZJO": gov(18, [
        ("signed", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
        ("in_force", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
        ("status", "Jordan Export Portal (Ministry of Industry, Trade and Supply), FTA insights",
         "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"),
    ], name="Jordan - Algeria Agreement", agreement_type="fta", status="in_force", signed="1997",
        in_force="1999", parties=["DZ", "JO"],
        notes="Jordan lists it as a bilateral agreement of 1997, in force since 1999."),
    "CHFO": gov(443, [
        ("signed", "Swiss State Secretariat for Economic Affairs (SECO), SR 0.632.313.141",
         "https://www.seco.admin.ch/de/freihandelsabkommen-faeroeer-inseln"),
        ("in_force", "Swiss State Secretariat for Economic Affairs (SECO), SR 0.632.313.141",
         "https://www.seco.admin.ch/de/freihandelsabkommen-faeroeer-inseln"),
        ("status", "Swiss State Secretariat for Economic Affairs (SECO), SR 0.632.313.141",
         "https://www.seco.admin.ch/de/freihandelsabkommen-faeroeer-inseln"),
    ], name="Agreement between the Government of Switzerland and the Government of Denmark and the Home "
            "Government of the Faroe Islands on Free Trade between Switzerland and the Faroe Islands",
        other_names=[{"lang": "de", "name": "Abkommen zwischen der Schweizerischen Regierung einerseits und der "
                                            "Regierung von Dänemark und der Landesregierung der Färöer "
                                            "andererseits über den Freihandel zwischen der Schweiz und den Färöern"}],
        agreement_type="fta", status="in_force", signed="1994-01-12", in_force="1995-03-01",
        parties=["CH", "FO"], notes="Swiss classified compilation SR 0.632.313.141."),
    "FRMC": gov(452, [
        ("signed", "Legimonaco, Convention douanière du 18 mai 1963",
         "https://legimonaco.mc/tai/convention/1963/05-18-tai1l000236@2023-.05-.01-/"),
        ("in_force", "Legimonaco, Convention douanière du 18 mai 1963",
         "https://legimonaco.mc/tai/convention/1963/05-18-tai1l000236@2023-.05-.01-/"),
        ("status", "Legimonaco, Convention douanière du 18 mai 1963",
         "https://legimonaco.mc/tai/convention/1963/05-18-tai1l000236@2023-.05-.01-/"),
    ], name="Customs Convention between the Government of the Principality of Monaco and the Government of the "
            "French Republic", other_names=[{"lang": "fr", "name": "Convention douanière entre le Gouvernement "
                                                                     "de la Principauté de Monaco et le "
                                                                     "Gouvernement de la République française"}],
        agreement_type="customs_union", status="in_force", signed="1963-05-18", in_force="1963-09-01",
        parties=["FR", "MC"],
        notes="Signed in Paris. Made enforceable in Monaco by Sovereign Ordinance No. 3.038 of 19 August 1963; "
              "amended by an exchange of letters of 8 November 1994 and an amendment of 25 October 2001."),
    "LVUA": gov(571, [
        ("signed", "Latvian official legal portal (likumi.lv)",
         "https://likumi.lv/ta/lv/starptautiskie-ligumi/id/978"),
        ("in_force", "Latvian official legal portal (likumi.lv)",
         "https://likumi.lv/ta/lv/starptautiskie-ligumi/id/978"),
        ("ended", "Latvian official legal portal (likumi.lv)",
         "https://likumi.lv/ta/lv/starptautiskie-ligumi/id/978"),
        ("status", "Latvian official legal portal (likumi.lv)",
         "https://likumi.lv/ta/lv/starptautiskie-ligumi/id/978"),
    ], name="Free Trade Agreement between the Republic of Latvia and Ukraine",
        other_names=[{"lang": "lv", "name": "Latvijas Republikas un Ukrainas brīvās tirdzniecības līgums"}],
        agreement_type="fta", status="terminated", signed="1995-11-22", in_force="1997-01-15",
        ended="2004-05-01", parties=["LV", "UA"],
        notes="Signed in Kyiv. Ended on Latvia's accession to the European Union."),

    # --- southern African bilaterals: WTO trade policy reviews, party governments --------------
    "MWMZ": gov(595, [
        ("signed", "WTO, Trade Policy Review of Mozambique, WT/TPR/S/354 (2017), Table 2.3 (RTAs in force, 2016)",
         TPR + "s354_e.pdf"),
        ("in_force", "WTO, Trade Policy Review of Mozambique, WT/TPR/S/354 (2017), Table 2.3 (RTAs in force, 2016)",
         TPR + "s354_e.pdf"),
        ("status", "WTO, Trade Policy Review of Malawi, report by the Government, WT/TPR/G/460 (2024)",
         TPR + "g460_e.pdf"),
    ], name="Preferential Trade Agreement between the Government of the Republic of Malawi and the Government "
            "of the Republic of Mozambique", agreement_type="pta", status="in_force", signed="2005-12-28",
        in_force="2006-09-20", parties=["MW", "MZ"],
        notes="Duty-free trade in originating goods except an exclusion list (sugar, beer, branded soft drinks, "
              "refined edible oil, dressed chickens, eggs, unmanufactured tobacco and others). Replaced the colonial "
              "arrangement of the 1959 trade agreement between Portugal and the Federation of Rhodesia and "
              "Nyasaland. Not notified to the WTO."),
    "MZZW": gov(629, [
        ("signed", "WTO, Trade Policy Review of Mozambique, WT/TPR/S/354 (2017), Table 2.3 (RTAs in force, 2016)",
         TPR + "s354_e.pdf"),
        ("in_force", "WTO, Trade Policy Review of Mozambique, WT/TPR/S/354 (2017), Table 2.3 (RTAs in force, 2016)",
         TPR + "s354_e.pdf"),
        ("status", "Zimbabwe Revenue Authority (ZIMRA), origin and preference",
         "https://www.zimra.co.zw/customs/origin-and-preference/origin-and-preference"),
    ], name="Trade Agreement between the Government of the Republic of Mozambique and the Government of the "
            "Republic of Zimbabwe", agreement_type="pta", status="in_force", signed="2004-01-09",
        in_force="2004-03-01", parties=["MZ", "ZW"],
        notes="Duty-free trade in all goods except sugar, branded soft drinks, firearms, ammunition and explosives, "
              "motor vehicles, beer and manufactured tobacco. The WTO gives entry into force on 1 March 2004; "
              "Zimbabwe implements it by Statutory Instrument 33 of 2005. Not notified to the WTO."),
    "BWZW": gov(137, [
        ("signed", "WTO, Trade Policy Review of SACU, WT/TPR/S/222 (2009), Annex 1 (Botswana)",
         TPR + "s222-01_e.doc"),
        ("in_force", "Zimbabwe Revenue Authority (ZIMRA), origin and preference: Statutory Instrument 192 of 1988",
         "https://www.zimra.co.zw/customs/origin-and-preference/origin-and-preference"),
        ("status", "WTO, Trade Policy Review of SACU, WT/TPR/S/324 (2015), Annex 1 (Botswana)",
         TPR + "s324-00_e.pdf"),
    ], name="Trade Agreement between Botswana and Zimbabwe", agreement_type="fta", status="in_force",
        signed="1988", in_force="1988", parties=["BW", "ZW"],
        notes="Reciprocal duty-free trade in goods wholly produced in either country or with at least 25% local "
              "content. First signed in 1956 between the Bechuanaland Protectorate and the Federation of Rhodesia "
              "and Nyasaland, and amended in 1988 and 2010 (WTO); Zimbabwe gave effect to the 1988 text by "
              "Statutory Instrument 192 of 1988."),
    "MWZA": gov(762, [
        ("in_force", "WTO, Trade Policy Review of Malawi, WT/TPR/S/96 (2002), Chapter II",
         "https://docsonline.wto.org/dol2fe/Pages/SS/directdoc.aspx?filename=Q%3A%2FWT%2FTPR%2FS96-2.pdf"),
        ("status", "WTO, Trade Policy Review of Malawi, report by the Government, WT/TPR/G/460 (2024)",
         TPR + "g460_e.pdf"),
        ("notes", "Malawi Trade Portal (trade.gov.mw), guide to Malawi's preferential trade agreements",
         "https://portal.trade.gov.mw/en-gb/site/display/120"),
    ], name="Trade Agreement between Malawi and South Africa", agreement_type="pta", status="in_force",
        in_force="1990", parties=["MW", "ZA"],
        notes="A revision, in 1990, of the trade agreement the two countries signed in 1967 (Malawi Trade "
              "Portal); the WTO says the agreement was formed in 1990. Non-reciprocal: South Africa admits goods "
              "grown, produced or manufactured in Malawi duty free with at least 25% local content, with quotas "
              "for some goods such as tea, and Malawi grants South African goods most-favoured-nation treatment. "
              "Either party may end it with 12 months' notice."),
}

# Records whose successor is not in the registry yet (set by ``build``): ``terminated`` for now,
# ``superseded`` with ``superseded_by`` once the successor merges.
PENDING_SUCCESSORS: dict[str, str] = {}

# Successors whose only predecessor is added here.
MAIN_SUPERSEDES: dict[str, str] = {
    "CLMX": "CLMX-1991", "CRMX": "CRMX-1982", "CUMX": "CUMX-1985", "MXUY": "MXUY-1986", "BOMX": "BOMX-1994",
    "BRMX": "BRMX-1983",
}


def build(rid: str, spec: dict, ids: set[str]) -> dict:
    spec = dict(spec)
    desta = spec.pop("_desta")
    prov = spec.pop("_prov")
    if spec.get("superseded_by") and spec["superseded_by"] not in ids:
        # The successor is in an open pull request (#209, #218 or #226): until it merges the record is
        # ``terminated``; its notes name the successor. See PENDING_SUCCESSORS.
        PENDING_SUCCESSORS[rid] = spec.pop("superseded_by")
        spec["status"] = "terminated"
    record = {"id": rid, **{k: v for k, v in spec.items() if v not in (None, "", [])}}
    record["verification"] = "official"
    record["last_verified"] = RETRIEVED
    record["provenance"] = [
        {"field": f, "source": s, **({"url": u} if u else {}), "retrieved_at": RETRIEVED} for f, s, u in prov
        if f in record or f == "status"
    ] + [{"field": "desta_id", "source": DESTA.format(desta), "url": DESTA_URL, "retrieved_at": RETRIEVED}]
    return {k: record[k] for k in FIELD_ORDER if k in record}


def dump(record: dict) -> str:
    return yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)


def main(argv: list[str]) -> int:
    write = "--write" in argv
    existing = {p.stem for p in REGISTRY.glob("*.yaml")}
    clash = [rid for rid in RECORDS if rid in existing]
    if clash and not write:
        print("already in the registry:", ", ".join(clash))
    ids = existing | set(RECORDS)
    for rid, spec in RECORDS.items():
        record = build(rid, spec, ids)
        path = REGISTRY / f"{rid}.yaml"
        if write:
            path.write_text(dump(record), encoding="utf-8")
        else:
            print(dump(record))
    for successor, predecessor in MAIN_SUPERSEDES.items():
        path = REGISTRY / f"{successor}.yaml"
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if record.get("supersedes") and record["supersedes"] != predecessor:
            print(f"{successor}: already supersedes {record['supersedes']}", file=sys.stderr)
            continue
        record["supersedes"] = predecessor
        record = {k: record[k] for k in FIELD_ORDER if k in record} | {k: v for k, v in record.items()
                                                                     if k not in FIELD_ORDER}
        if write:
            path.write_text(dump(record), encoding="utf-8")
    for rid, target in PENDING_SUCCESSORS.items():
        print(f"{rid}: terminated until {target} is in the registry", file=sys.stderr)
    print(f"{len(RECORDS)} records{' written' if write else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
