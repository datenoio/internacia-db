#!/usr/bin/env python3
"""One-off: check Norway's trade agreements against Lovdata's treaty register.

Lovdata publishes "Norges traktater", the treaty register kept by the treaty unit of the
Norwegian Ministry of Foreign Affairs (``https://lovdata.no/register/traktater``). Each
treaty page (``https://lovdata.no/dokument/TRAKTAT/traktat/<id>``) gives the signature date,
the entry into force for Norway and, where Norway keeps the treaty, a party table with each
party's signature, ratification, entry into force and withdrawal (the last day of
application). Norway is the depositary of the EFTA Convention (since 17 November 1995) and of
the EFTA free trade agreements, so those tables are the depositary's record.

This pass covers:

- ``FIXES``: dates and statuses that Lovdata contradicts (the EFTA-Viet Nam signature, the
  provisional application of the 2020 UK-Iceland-Norway goods agreement and of the EFTA-
  Slovenia agreement, the first entry into force of three EFTA agreements, two investment
  treaty dates and the termination of the investment treaty with Slovakia);
- ``PARTIES``: each party's own entry into force of the EFTA agreements Norway keeps, where it
  differs from the agreement's; Switzerland's dates are also checked against Fedlex;
- ``OFFICIAL``: records whose dates Lovdata confirms, which move to ``verification: official``;
- ``NOTES``: conflicts and staggered dates kept as notes, on records whose parties come from
  an intblock or where Lovdata's party table is not reliable;
- ``INSTRUMENTS``: Norway's bilateral agreements on agriculture under the EFTA agreements and
  their amendments, the supplementary protocols to the 1973 EEC-Norway agreement, the
  instruments of the Faroe Islands-Norway agreement and two further EFTA instruments;
- ``EFTA_MEMBERS``: the EFTA Convention's membership dates, former members included, on the
  EFTA intblock.

``fetch CACHE_DIR``
    Download every Lovdata page the plan uses (one request a second), query Fedlex for the
    Swiss dates, check every planned value and write ``CACHE_DIR/lovdata.json``; exits non-zero
    if a page or a value does not match.

``apply CACHE_DIR [--write]``
    Print, and with ``--write`` make, the changes. Running it again changes nothing.

Lovdata pages are untrusted data: keep the cache outside the repository and run with
``python -I``.
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
EFTA_INTBLOCK = ROOT / "data" / "intblocks" / "fta" / "EFTA.yaml"
RETRIEVED = "2026-11-23"
LOVDATA = "https://lovdata.no/dokument/TRAKTAT/traktat/"
SOURCE = "Lovdata, Norges traktater (treaty register of the Norwegian Ministry of Foreign Affairs)"
FEDLEX = "Fedlex (Swiss federal law platform)"
SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
USER_AGENT = "internacia-db one-off (trade agreements registry)"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "unctad_iia_id", "gptad_id", "dta_id", "wikidata_id", "links", "description",
    "notes", "instruments", "verification", "last_verified", "provenance",
]
# Lovdata party names -> registry ids.
PARTY_NAMES = {
    "Norge": "NO", "Island": "IS", "Liechtenstein": "LI", "Sveits": "CH", "Østerrike": "AT",
    "Finland": "FI", "Sverige": "SE", "Danmark": "DK", "Storbritannia": "GB", "Portugal": "PT",
}

# Record fixes: the new values and the Lovdata page that gives them. ``checks`` say where on
# the page each value is: ``signed``, ``norway`` (entry into force for Norway), ``first``
# (the earliest entry into force in the party table), ``note`` (a phrase of the remark) or
# ``end`` (the entry into force of the termination agreement ``end_doc``).
FIXES: dict[str, dict] = {
    "EFTAVN": {"doc": "2026-10-18-22", "set": {"status": "signed", "signed": "2026-10-18"},
               "checks": {"signed": "signed"}},
    "GBISNO": {"doc": "2020-12-08-15", "set": {"provisional_application": "2021-01-01", "in_force": "2021-02-22"},
               "checks": {"provisional_application": ("note", "anvendt midlertidig fra 1. januar 2021"),
                          "in_force": "norway"}},
    "EFTASI": {"doc": "1995-06-13-2", "set": {"provisional_application": "1995-07-01", "in_force": "1998-09-01"},
               "checks": {"provisional_application": ("note", "midlertidig anvendt fra 01-07-1995"),
                          "in_force": "first"}},
    "EFTAEE": {"doc": "1995-12-07-8", "set": {"in_force": "1997-10-01"}, "checks": {"in_force": "first"}},
    "EFTALT": {"doc": "1995-12-07-6", "set": {"in_force": "1997-01-01"}, "checks": {"in_force": "first"}},
    "EFTAPL": {"doc": "1992-12-10-3", "set": {"in_force": "1994-09-01"}, "checks": {"in_force": "first"}},
    "EFTAHR": {"doc": "2001-06-21-1", "set": {"ended": "2013-07-01"},
               "checks": {"ended": ("note", "opphørte den 1. juli 2013")}},
    "NOPE-BIT": {"doc": "1995-03-10-1", "set": {"signed": "1995-03-10"}, "checks": {"signed": "signed"}},
    "LTNO-BIT": {"doc": "1992-06-16-2", "set": {"in_force": "1992-12-19"}, "checks": {"in_force": "norway"}},
    "NOSK-BIT": {"doc": "1991-05-21-2", "end_doc": "2024-08-19-8", "set": {"status": "terminated", "ended": "2024-10-01"},
                 "checks": {"ended": "end"}},
}

# Each party's own entry into force (and provisional application) of EFTA agreements whose
# records list their parties. Switzerland's dates are checked against Fedlex too.
PARTIES: dict[str, dict] = {
    "EFTABG": {"doc": "1993-03-29-3", "in_force": {"NO": "1994-01-01", "IS": "1994-06-01", "CH": "1994-06-01",
                                                   "LI": "1994-10-01", "AT": "1993-09-01", "FI": "1994-07-01"}},
    "EFTACZ": {"doc": "1992-03-20-1", "in_force": {"IS": "1993-01-01", "CH": "1992-12-01", "LI": "1997-01-01",
                                                   "AT": "1992-12-01", "FI": "1992-12-01"}},
    "EFTAHU": {"doc": "1993-03-29-1", "in_force": {"CH": "1994-06-01", "IS": "1994-06-01", "LI": "1994-10-01",
                                                   "FI": "1994-03-01"}},
    "EFTAIL": {"doc": "1992-09-17-1", "in_force": {"CH": "1993-07-01", "IS": "1993-08-01", "LI": "1994-05-01"}},
    "EFTAHR": {"doc": "2001-06-21-1", "in_force": {"IS": "2002-08-01", "CH": "2002-09-01", "LI": "2002-09-01"}},
    "EFTARO": {"doc": "1992-12-10-1", "in_force": {"NO": "1993-07-01", "CH": "1994-02-01", "LI": "1994-05-01",
                                                   "AT": "1993-08-01", "IS": "1994-06-01", "FI": "1993-10-01"},
               "provisional": {"CH": "1993-05-01"}},
    "EFTAEE": {"doc": "1995-12-07-8", "in_force": {"NO": "1997-10-01", "LI": "1998-01-01"}},
    "EFTALT": {"doc": "1995-12-07-6", "in_force": {"LI": "1998-01-01"},
               "provisional": {"CH": "1997-01-01", "LI": "1997-01-01"}},
    "EFTALV": {"doc": "1995-12-07-5", "in_force": {"LI": "1998-01-01"},
               "provisional": {"CH": "1996-06-01", "LI": "1996-06-01"}},
    "EFTAMK": {"doc": "2000-06-19-1", "in_force": {"IS": "2002-08-01"}},
    "EFTAMX": {"doc": "2000-11-27-1", "in_force": {"IS": "2001-10-01"}},
    "EFTAPS": {"doc": "1998-11-30-5", "in_force": {"IS": "2000-11-01"}},
    "EFTATR-1991": {"doc": "1991-12-10-1", "in_force": {"AT": "1992-10-01", "SE": "1992-04-15", "FI": "1992-05-01"}},
}
# Swiss entry into force on Fedlex, found by signature date and "EFTA" in the German title.
FEDLEX_CH: dict[str, tuple[str, str]] = {
    "EFTABG": ("1993-03-29", "Bulgarien"), "EFTACZ": ("1992-03-20", "Tschechischen"),
    "EFTAHU": ("1993-03-29", "Ungarn"), "EFTAIL": ("1992-09-17", "Israel"), "EFTAHR": ("2001-06-21", "Kroatien"),
    "EFTARO": ("1992-12-10", "Rumänien"), "EFTAPL": ("1992-12-10", "Polen"), "EFTASI": ("1995-06-13", "Slowenien"),
    "EFTAGE": ("2016-06-27", "Georgien"), "EFTAMD": ("2023-06-27", "Moldau"), "EFTAXK": ("2025-01-22", "Kosovo"),
    "EFTAHK-LABOUR": ("2011-06-21", "Arbeitsstandards"),
}

# Records whose dates Lovdata confirms (record id -> Lovdata page, and for terminated
# investment treaties the termination agreement).
OFFICIAL: dict[str, dict] = {
    "EFTAEE": {"doc": "1995-12-07-8"}, "EFTALT": {"doc": "1995-12-07-6"}, "EFTALV": {"doc": "1995-12-07-5"},
    "EFTABG": {"doc": "1993-03-29-3"}, "EFTACZ": {"doc": "1992-03-20-1"}, "EFTAHU": {"doc": "1993-03-29-1"},
    "EFTARO": {"doc": "1992-12-10-1"}, "EFTAPL": {"doc": "1992-12-10-3"}, "EFTASI": {"doc": "1995-06-13-2"},
    "EFTAHR": {"doc": "2001-06-21-1"}, "EFTAMD": {"doc": "2023-06-27-4"}, "EFTAXK": {"doc": "2025-01-22-5"},
    "FONO": {"doc": "1992-08-28-1"}, "GBISNO": {"doc": "2020-12-08-15"},
    "MGNO-BIT": {"doc": "1966-05-13-1"}, "CNNO-BIT": {"doc": "1984-11-21-1"}, "LKNO-BIT": {"doc": "1985-06-13-1"},
    "NOPL-BIT": {"doc": "1990-06-05-1", "end_doc": "2023-07-18-3"},
    "HUNO-BIT": {"doc": "1991-04-08-1", "end_doc": "2022-07-14-13"},
    "NOSK-BIT": {"doc": "1991-05-21-2", "end_doc": "2024-08-19-8"},
    "CZNO-BIT": {"doc": "1991-05-21-3"},
    "NORO-BIT": {"doc": "1991-06-11-1", "end_doc": "2022-07-07-14"},
    "IDNO-BIT-1991": {"doc": "1991-11-26-2"},
    "EENO-BIT": {"doc": "1992-06-15-1", "end_doc": "2022-04-06-16"},
    "LVNO-BIT": {"doc": "1992-06-16-1", "end_doc": "2022-07-27-15"},
    "LTNO-BIT": {"doc": "1992-06-16-2", "end_doc": "2022-05-12-17"},
    "CLNO-BIT": {"doc": "1993-06-01-1"}, "NOPE-BIT": {"doc": "1995-03-10-1"}, "NORU-BIT": {"doc": "1995-10-04-3"},
}
# Dates Lovdata gives differently from a record that keeps its own (checked, then noted).
KEEP: dict[str, str] = {
    "CZNO-BIT": "Lovdata lists the treaty with the Czech Republic as in force from 1 January 1993, the date the Czech "
                "Republic succeeded Czechoslovakia.",
    "NOSK-BIT": "Lovdata lists the treaty with Slovakia as in force from 1 January 1993, the date Slovakia succeeded "
                "Czechoslovakia.",
    "IDNO-BIT-1991": "Lovdata records the termination by a decision of the Ministry of Foreign Affairs of 31 March 2004.",
}

NOTES: dict[str, dict] = {
    "EFTACO": {"doc": "2008-11-25-47", "check": ("norway", "2014-10-01"),
               "note": "Lovdata gives the entry into force for Norway as 1 October 2014, but 1 September 2014 for "
                       "Norway's agreement on agriculture with Colombia, which entered into force with the free trade "
                       "agreement; the registry keeps 1 September 2014."},
    "EFTATH": {"doc": "2025-01-23-6", "check": ("first", "2027-01-01"),
               "note": "Lovdata (Norway is the depositary) records every party's ratification by October 2026 and "
                       "gives 1 January 2027 as the entry into force for all parties."},
    "EFTAHK": {"doc": "2011-06-21-35", "check": ("norway", "2012-11-01"),
               "note": "In force between Hong Kong, Iceland, Liechtenstein and Switzerland since 1 October 2012 and "
                       "for Norway since 1 November 2012 (Lovdata)."},
    "EFTAGE": {"doc": "2016-06-27-18", "check": ("party", "CH", "2018-05-01"),
               "note": "In force for Switzerland and Liechtenstein since 1 May 2018 (Lovdata; Fedlex SR 0.632.313.601 "
                       "for Switzerland)."},
    "EFTAPH": {"doc": "2016-04-28-19", "check": ("party", "IS", "2020-01-01"),
               "note": "In force for Iceland since 1 January 2020 (Lovdata)."},
    "EFTAMD": {"doc": "2023-06-27-4", "check": ("party", "LI", "2024-04-01"),
               "note": "Lovdata's party table gives 1 November 2024 for Moldova and 1 April 2024 for Liechtenstein; "
                       "the registry keeps 1 September 2024 for Moldova, the date the agreement entered into force "
                       "for Iceland, and 1 April 2025 for Liechtenstein, the date Fedlex gives for Switzerland."},
    "EFTAHR": {"doc": "2001-06-21-1", "check": ("party", "CH", "2002-09-01"),
               "note": "Lovdata notes provisional application by Switzerland from 1 January 2002."},
}

AGRI = "supplementary_agreement"
AMEND = "amending_protocol"
LETTERS = "exchange_of_letters"
# Instruments: (record, instrument id, Lovdata page, kind, overrides). Name, signature and
# entry into force come from the page; ``ended`` is required for an instrument that ended.
INSTRUMENTS: list[tuple[str, str, str, str, dict]] = [
    ("EFTATR-1991", "agriculture-norway", "1991-12-10-2", AGRI,
     {"notes": "Still in force: amended by an instrument of 25 June 2018 that entered into force with the 2018 "
               "EFTA-Türkiye agreement (`EFTATR`)."}),
    ("EFTATR", "agriculture-norway-amendment-2018", "2018-06-25-14", AMEND,
     {"notes": "Amends the 1991 agricultural protocol between Norway and Türkiye (`EFTATR-1991`)."}),
    ("EFTACZ", "agriculture-norway", "1992-04-08-1", AGRI,
     {"ended": "2004-05-01", "notes": "Continued the protocol of 8 April 1992 with Czechoslovakia; ended when the Czech "
                                       "Republic joined the EU."}),
    ("EFTASK", "agriculture-norway", "1992-04-08-2", AGRI,
     {"ended": "2004-05-01", "notes": "Continued the protocol of 8 April 1992 with Czechoslovakia; ended when Slovakia "
                                       "joined the EU."}),
    ("EFTAIL", "agriculture-norway", "1992-09-16-1", AGRI,
     {"ended": "2021-08-01", "notes": "In force on 16 March 1993 with effect from 1 January 1993. Lovdata marks it as "
                                       "ended; it was replaced by the agreement on agricultural products of 2018, in "
                                       "force on 1 August 2021."}),
    ("EFTAIL", "agriculture-norway-2018", "2018-11-22-27", AGRI, {}),
    ("EFTARO", "agriculture-norway", "1992-12-10-2", AGRI,
     {"ended": "2007-01-01", "notes": "Ended when Romania joined the EU."}),
    ("EFTAPL", "agriculture-norway", "1992-12-10-4", AGRI,
     {"ended": "2004-05-01", "notes": "Ended with the free trade agreement when Poland joined the EU."}),
    ("EFTAHU", "agriculture-norway", "1993-03-29-2", AGRI,
     {"ended": "2004-05-01", "notes": "Ended with the free trade agreement when Hungary joined the EU."}),
    ("EFTABG", "agriculture-norway", "1993-03-29-4", AGRI,
     {"ended": "2007-01-01", "notes": "Applied provisionally from 1 July 1993; ended when Bulgaria joined the EU."}),
    ("EFTASI", "agriculture-norway", "1995-06-13-3", AGRI,
     {"ended": "2004-05-01", "notes": "Applied provisionally from 1 July 1995; ended when Slovenia joined the EU."}),
    ("EFTAEE", "agriculture-norway", "1996-03-27-1", AGRI,
     {"ended": "2004-05-01", "notes": "Ended when Estonia joined the EU."}),
    ("EFTALV", "agriculture-norway", "1996-04-23-1", AGRI,
     {"ended": "2004-05-01", "notes": "Ended with the free trade agreement when Latvia joined the EU."}),
    ("EFTALT", "agriculture-norway", "1996-05-22-1", AGRI,
     {"signed": "1996-05-22", "ended": "2004-05-01",
      "notes": "Lovdata gives 22 May 1995 as the signature date, before the free trade agreement of 7 December 1995; "
               "the registry uses 22 May 1996, the date in Lovdata's identifier. Ended with the free trade agreement "
               "when Lithuania joined the EU."}),
    ("EFTAMA", "agriculture-norway", "1997-06-19-3", AGRI, {}),
    ("EFTAPS", "agriculture-norway", "1998-11-30-4", AGRI, {}),
    ("EFTAPS", "agriculture-norway-2026", "2026-06-22-11", AGRI, {}),
    ("EFTAMK", "agriculture-norway", "2000-06-19-2", AGRI, {}),
    ("EFTAMK", "agriculture-norway-amendment-2021", "2021-07-14-10", AMEND,
     {"notes": "Signed by Norway on 14 July 2021 and by North Macedonia on 23 July 2021."}),
    ("EFTAMX", "agriculture-norway", "2000-11-27-2", AGRI, {}),
    ("EFTAMX", "agriculture-norway-amendment-2011", "2011-10-11-42", AMEND, {}),
    ("EFTAHR", "agriculture-norway", "2001-06-21-2", AGRI, {"ended": "2013-07-01", "notes": "Ended on 1 July 2013."}),
    ("EFTAJO", "agriculture-norway", "2001-06-21-5", AGRI, {}),
    ("EFTAJO", "agriculture-norway-amendment-2025", "2025-06-10-20", AMEND, {}),
    ("EFTASG", "agriculture-norway", "2002-06-26-2", AGRI, {}),
    ("EFTACL", "agriculture-norway", "2003-06-26-34", AGRI, {}),
    ("EFTALB", "agriculture-norway", "2004-06-24-11", AGRI, {}),
    ("EFTATN", "agriculture-norway", "2004-12-17-64", AGRI, {}),
    ("EFTATN", "agriculture-norway-amendment-2024", "2024-10-09-17", AMEND, {}),
    ("EFTAKR", "agriculture-norway", "2005-12-15-61", AGRI, {}),
    ("EFTASACU", "agriculture-norway", "2006-06-26-25", AGRI,
     {"notes": "Signed by Norway at Höfn on 26 June 2006 and by the SACU states on later dates."}),
    ("EFTAEG", "agriculture-norway", "2007-01-27-3", AGRI, {}),
    ("EFTACA", "agriculture-norway", "2008-01-26-1", AGRI, {}),
    ("EFTACO", "agriculture-norway", "2008-11-25-34", AGRI, {}),
    ("EFTAGCC", "agriculture-norway", "2009-06-22-18", AGRI, {}),
    ("EFTAAL", "agriculture-norway", "2009-12-17-49", AGRI, {}),
    ("EFTAAL", "agriculture-norway-amendment-2021", "2021-07-08-6", AMEND, {}),
    ("EFTARS", "agriculture-norway", "2009-12-17-50", AGRI, {}),
    ("EFTARS", "agriculture-norway-amendment-2021", "2021-09-13-12", AMEND, {}),
    ("EFTAUA", "agriculture-norway", "2010-06-24-26", AGRI, {}),
    ("EFTAUA-2025", "agriculture-norway-amendment-2025", "2025-04-08-10", AMEND,
     {"notes": "Amends the agreement on agriculture between Norway and Ukraine of 24 June 2010, signed with the "
               "modernised free trade agreement."}),
    ("EFTAPE", "agriculture-norway", "2010-06-24-31", AGRI, {}),
    ("EFTAHK", "agriculture-norway", "2011-06-21-23", AGRI, {}),
    ("EFTAHK", "labour", "2011-06-21-24", AGRI,
     {"signed": "2011-06-21", "coverage": [],
      "notes": "Signed on 17 and 21 June 2011. In force for Switzerland since 1 October 2012 (Fedlex SR "
               "0.632.314.161.2) and for Norway since 1 November 2012 (Lovdata)."}),
    ("EFTAME", "agriculture-norway", "2011-11-14-53", AGRI, {}),
    ("EFTAME", "agriculture-norway-amendment-2021", "2021-07-14-9", AMEND, {}),
    ("EFTABA", "agriculture-norway", "2013-06-24-11", AGRI, {}),
    ("FONO", "agriculture", "1992-08-27-1", AGRI,
     {"name": "Protocol between Norway and Denmark and the Faroe Islands on trade in agricultural products",
      "notes": "Concluded by an exchange of letters."}),
    ("FONO", "origin-letters-1994", "1994-02-16-1", LETTERS,
     {"name": "Exchange of letters between Norway and Denmark and the Faroe Islands amending the rules of origin"}),
    ("FONO", "origin-letters-2005", "2005-11-30-53", LETTERS,
     {"name": "Exchange of letters between Norway and Denmark and the Faroe Islands amending the rules of origin "
              "(Annex 3)"}),
    ("EUNO", "additional-protocol-1980", "1980-11-06-1", AMEND,
     {"notes": "Concluded on the accession of Greece to the European Communities."}),
    ("EUNO", "cheese-arrangement-1983", "1983-04-11-1", "other",
     {"name": "Interim arrangement in the form of agreed rules between Norway and the European Economic Community on "
              "reciprocal trade in cheese"}),
    ("EUNO", "additional-protocol-1986", "1986-07-14-1", AMEND,
     {"notes": "Concluded on the accession of Spain and Portugal to the European Communities."}),
    ("EUNO", "second-additional-protocol-1989", "1989-04-19-1", AMEND,
     {"notes": "Removed Norwegian duties of 2 % and lower on imports from Spain."}),
    ("EUNO", "third-additional-protocol-1989", "1989-06-09-1", AMEND,
     {"notes": "Completed the removal of duties in trade with Spain."}),
    ("EUNO", "supplementary-protocol-1989", "1989-07-26-1", AMEND,
     {"notes": "Removed quantitative restrictions on exports and measures having equivalent effect."}),
    ("EUNO", "additional-protocol-1995", "1995-07-25-1", AMEND,
     {"notes": "Concluded on the accession of Austria, Finland and Sweden to the EU, with tariff quotas for fish; in "
               "force on 1 September 1995 with effect from 1 July 1995."}),
    ("EUNO", "cheese-letters-1995", "1995-12-20-1", LETTERS, {"notes": "With effect from 1 January 1995."}),
    ("EUNO", "customs-cooperation-1997", "1997-04-10-1", AGRI, {}),
    ("EUNO", "protocol-2-agreement-2002", "2002-11-27-1", AMEND,
     {"ended": "2005-01-01",
      "notes": "Amended the import rules for certain processed agricultural products (Protocol 2). Lovdata marks it as "
               "ended; it was replaced by the exchange of letters of 13 December 2004, in force on 1 January 2005."}),
    ("EUNO", "additional-protocol-2003", "2003-10-14-70", AMEND,
     {"notes": "Concluded on the accession of ten states to the EU in 2004; applied provisionally from 1 May 2004."}),
    ("EUNO", "protocol-2-letters-2004", "2004-12-13-50", LETTERS,
     {"notes": "Amended the import rules for certain processed agricultural products (Protocol 2)."}),
    ("EUNO", "additional-protocol-2007", "2007-07-25-21", AMEND,
     {"in_force": "2011-11-09",
      "notes": "Concluded on the accession of Bulgaria and Romania to the EU; applied provisionally from 1 September "
               "2007."}),
    ("EUNO", "additional-protocol-2010", "2010-07-28-42", AMEND,
     {"in_force": "2011-05-01", "notes": "On trade in fish; applied provisionally from 1 March 2011."}),
    ("EUNO", "additional-protocol-2014", "2014-04-11-9", AMEND,
     {"in_force": "2025-02-19",
      "notes": "Concluded on the accession of Croatia to the EU; applied provisionally from 1 August 2014."}),
    ("EUNO", "additional-protocol-2016", "2016-05-03-9", AMEND,
     {"notes": "Applied provisionally from 1 September 2016."}),
    ("EUNO", "additional-protocol-2024", "2024-09-12-14", AMEND,
     {"notes": "Applied provisionally from 1 January 2025."}),
]

# EFTA Convention membership (Lovdata, depositary Norway since 17 November 1995). ``left`` is
# the first day without membership, the day after Lovdata's last day.
EFTA_DOC = "1960-01-04-1"
EFTA_MEMBERS: list[tuple[str, str, str, str, str | None]] = [
    ("AT", "Austria", "former_member", "1960-05-03", "1995-01-01"),
    ("DK", "Denmark", "former_member", "1960-05-03", "1973-01-01"),
    ("FI", "Finland", "former_member", "1986-01-01", "1995-01-01"),
    ("IS", "Iceland", "member", "1970-03-01", None),
    ("LI", "Liechtenstein", "member", "1991-09-01", None),
    ("NO", "Norway", "founding_member", "1960-05-03", None),
    ("PT", "Portugal", "former_member", "1960-05-03", "1986-01-01"),
    ("SE", "Sweden", "former_member", "1960-05-03", "1995-01-01"),
    ("CH", "Switzerland", "founding_member", "1960-05-03", None),
    ("GB", "United Kingdom", "former_member", "1960-05-03", "1973-01-01"),
]
EFTA_NAMES = {"AT": "Østerrike", "DK": "Danmark", "FI": "Finland", "IS": "Island", "LI": "Liechtenstein",
              "NO": "Norge", "PT": "Portugal", "SE": "Sverige", "CH": "Sveits", "GB": "Storbritannia"}


# --- Lovdata pages ---------------------------------------------------------------------------

def get(url: str) -> str:
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read().decode("utf-8", "replace")
        except OSError as error:
            print(f"retry {url}: {error}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"cannot fetch {url}")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def iso(text: str | None) -> str | None:
    """The first DD-MM-YYYY date of a Lovdata value, as YYYY-MM-DD."""
    match = re.search(r"(\d{2})-(\d{2})-(\d{4})", text or "")
    return f"{match.group(3)}-{match.group(2)}-{match.group(1)}" if match else None


def parse(page: str) -> dict:
    meta = {name: value for name, value in re.findall(r'id="metaField_(\w+)">(.*?)</td>', page, flags=re.S)}
    parties = []
    for block in re.split(r"<strong>Part:</strong>", meta.pop("parter", ""))[1:]:
        fields = re.split(r"<strong>([^<]+?):</strong>", "<strong>Part:</strong>" + block)
        parties.append({k.strip(): clean(v) for k, v in zip(fields[1::2], fields[2::2], strict=True)})
    out = {name: clean(value) for name, value in meta.items()}
    out["parties"] = parties
    return out


def docs_used() -> list[str]:
    docs = {EFTA_DOC}
    for table in (FIXES, PARTIES, OFFICIAL, NOTES):
        for spec in table.values():
            docs.update(d for d in (spec.get("doc"), spec.get("end_doc")) if d)
    docs.update(entry[2] for entry in INSTRUMENTS)
    return sorted(docs)


def party_dates(page: dict) -> dict[str, dict]:
    out = {}
    for party in page["parties"]:
        code = PARTY_NAMES.get(party.get("Part", ""))
        if code:
            out[code] = {"in_force": iso(party.get("Ikrafttredelsesdato")),
                         "last_day": iso(party.get("Fratredelsesdato")), "note": party.get("Merknad", "")}
    return out


def lovdata_value(pages: dict, doc: str, where, end_doc: str | None = None) -> str | None:
    page = pages[doc]
    if where == "signed":
        return iso(page.get("undertegningsdato"))
    if where == "norway":
        return iso(page.get("ikraftNorge") or page.get("ikraft"))
    if where == "first":
        dates = [iso(p.get("Ikrafttredelsesdato")) for p in page["parties"]]
        return min((d for d in dates if d), default=iso(page.get("ikraft")))
    if where == "end":
        return iso(pages[end_doc].get("ikraft"))
    raise ValueError(where)


def fedlex_ch(signed: str, fragment: str) -> str | None:
    query = f'''PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
SELECT DISTINCT ?eif WHERE {{
  ?a a jolux:ConsolidationAbstract ; jolux:dateDocument "{signed}"^^<http://www.w3.org/2001/XMLSchema#date> ;
     jolux:isRealizedBy ?e ; jolux:dateEntryInForce ?eif .
  ?e jolux:language <http://publications.europa.eu/resource/authority/language/DEU> ; jolux:title ?t .
  FILTER(CONTAINS(?t, "EFTA") && CONTAINS(?t, "{fragment}")) }}'''
    request = urllib.request.Request(SPARQL + "?" + urllib.parse.urlencode({"query": query}),
                                     headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        rows = json.load(response)["results"]["bindings"]
    values = {r["eif"]["value"] for r in rows}
    return values.pop() if len(values) == 1 else None


def fetch(cache: Path) -> int:
    pages_dir = cache / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    pages = {}
    for doc in docs_used():
        path = pages_dir / f"{doc}.html"
        if not path.exists():
            path.write_text(get(LOVDATA + doc), encoding="utf-8")
            time.sleep(1)
        pages[doc] = parse(path.read_text(encoding="utf-8"))
    problems: list[str] = []

    def expect(label: str, got, want) -> None:
        if got != want:
            problems.append(f"{label}: Lovdata {got} != planned {want}")

    for rid, spec in FIXES.items():
        for field, where in spec["checks"].items():
            if isinstance(where, tuple):
                if where[1] not in pages[spec["doc"]].get("merknad", ""):
                    problems.append(f"{rid}.{field}: remark lacks {where[1]!r}")
            else:
                expect(f"{rid}.{field}", lovdata_value(pages, spec["doc"], where, spec.get("end_doc")),
                       spec["set"][field])
    for rid, spec in PARTIES.items():
        table = party_dates(pages[spec["doc"]])
        for code, value in spec["in_force"].items():
            expect(f"{rid} {code}", (table.get(code) or {}).get("in_force"), value)
        for code, value in spec.get("provisional", {}).items():
            note = (table.get(code) or {}).get("note", "")
            if f"fra {value[8:10]}-{value[5:7]}-{value[:4]}" not in note:
                problems.append(f"{rid} {code}: no provisional application from {value} in {note!r}")
    fedlex = {}
    for key, (signed, fragment) in FEDLEX_CH.items():
        fedlex[key] = fedlex_ch(signed, fragment)
    for rid, spec in PARTIES.items():
        if "CH" in spec["in_force"]:
            expect(f"{rid} CH (Fedlex)", fedlex.get(rid), spec["in_force"]["CH"])
    expect("EFTAPL CH (Fedlex)", fedlex["EFTAPL"], "1994-09-01")
    expect("EFTASI CH (Fedlex)", fedlex["EFTASI"], "1998-09-01")
    expect("EFTAGE CH (Fedlex)", fedlex["EFTAGE"], "2018-05-01")
    expect("EFTAMD CH (Fedlex)", fedlex["EFTAMD"], "2025-04-01")
    expect("EFTAHK labour CH (Fedlex)", fedlex["EFTAHK-LABOUR"], "2012-10-01")
    for rid, spec in OFFICIAL.items():
        record = load(rid)
        page = pages[spec["doc"]]
        if record.get("agreement_type") == "investment":
            if rid not in KEEP:
                expect(f"{rid}.in_force", lovdata_value(pages, spec["doc"], "norway"),
                       FIXES.get(rid, {}).get("set", {}).get("in_force", record.get("in_force")))
            expect(f"{rid}.signed", iso(page.get("undertegningsdato")),
                   FIXES.get(rid, {}).get("set", {}).get("signed", record.get("signed")))
            if spec.get("end_doc"):
                expect(f"{rid}.ended", lovdata_value(pages, spec["doc"], "end", spec["end_doc"]),
                       FIXES.get(rid, {}).get("set", {}).get("ended", record.get("ended")))
        elif rid not in FIXES or "signed" not in FIXES[rid]["set"]:
            expect(f"{rid}.signed", iso(page.get("undertegningsdato")), record.get("signed"))
    for rid, spec in NOTES.items():
        where, *rest = spec["check"]
        if where == "party":
            expect(f"{rid} {rest[0]}", (party_dates(pages[spec["doc"]]).get(rest[0]) or {}).get("in_force"), rest[1])
        else:
            expect(f"{rid}.{where}", lovdata_value(pages, spec["doc"], where), rest[0])
    efta = party_dates(pages[EFTA_DOC])
    for code, _name, _status, joined, left in EFTA_MEMBERS:
        row = efta.get(code) or {}
        expect(f"EFTA {code} joined", row.get("in_force"), joined)
        expect(f"EFTA {code} left", row.get("last_day") and day_after(row["last_day"]), left)
    for rid, iid, doc, _kind, extra in INSTRUMENTS:
        page = pages[doc]
        status = page.get("status", "")
        if "opphørt" in status and not extra.get("ended"):
            problems.append(f"{rid}/{iid}: Lovdata marks it ended; no ended date planned")
        if not (extra.get("name") or page.get("tittelOrginal")):
            problems.append(f"{rid}/{iid}: no English title")
    (cache / "lovdata.json").write_text(json.dumps({"pages": pages, "fedlex": fedlex}, indent=1, ensure_ascii=False),
                                        encoding="utf-8")
    for line in problems:
        print(line, file=sys.stderr)
    print(f"{len(pages)} Lovdata pages, {len(problems)} problem(s)", file=sys.stderr)
    return 1 if problems else 0


# --- Registry changes ------------------------------------------------------------------------

def day_after(iso_date: str) -> str:
    return (date.fromisoformat(iso_date) + timedelta(days=1)).isoformat()


def load(rid: str) -> dict:
    return yaml.safe_load((REGISTRY / f"{rid}.yaml").read_text(encoding="utf-8"))


def ordered(record: dict) -> dict:
    out = {k: record[k] for k in FIELD_ORDER if k in record}
    out.update({k: v for k, v in record.items() if k not in out})
    return out


def cite(record: dict, field: str, url: str, source: str = SOURCE) -> None:
    for p in record.setdefault("provenance", []):
        if p.get("field") == field and p.get("url") == url:
            p["retrieved_at"] = RETRIEVED
            return
    record["provenance"].append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})


def link(record: dict, url: str) -> None:
    links = record.setdefault("links", [])
    if all(entry.get("url") != url for entry in links):
        links.insert(0, {"url": url, "type": "website"})


def add_note(record: dict, note: str) -> None:
    if note not in (record.get("notes") or ""):
        record["notes"] = ((record.get("notes") or "").rstrip() + " " + note).strip()


def human(iso_date: str) -> str:
    d = date.fromisoformat(iso_date)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def previous_source(record: dict, field: str) -> str:
    for p in record.get("provenance") or []:
        if p.get("field") == field and p.get("source") != SOURCE:
            return p["source"]
    for p in record.get("provenance") or []:
        if p.get("source") != SOURCE:
            return p["source"]
    return "An earlier source"


LABELS = {"in_force": "the entry into force as", "signed": "the signature date as", "ended": "the end date as"}


def apply(cache: Path, write: bool) -> int:
    data = json.loads((cache / "lovdata.json").read_text(encoding="utf-8"))
    pages = data["pages"]
    records: dict[str, dict] = {}

    def get_record(rid: str) -> dict:
        if rid not in records:
            records[rid] = load(rid)
        return records[rid]

    for rid, spec in FIXES.items():
        record = get_record(rid)
        url = LOVDATA + spec["doc"]
        for field, value in spec["set"].items():
            old = record.get(field)
            if str(old or "") == value:
                continue
            print(f"{rid}: {field} {old} -> {value}")
            if old and field in LABELS:
                add_note(record, f"{previous_source(record, field)} gives {LABELS[field]} {human(str(old))}.")
            record[field] = value
            if field != "status":
                cite(record, field, url)
        if spec.get("end_doc"):
            cite(record, "ended", LOVDATA + spec["end_doc"])
            cite(record, "status", LOVDATA + spec["end_doc"])
        else:
            cite(record, "status", url)
        if rid == "EFTAVN":
            add_note(record, "Signed on 18 October 2026 (Lovdata; Norway is the depositary).")
        if rid == "GBISNO":
            add_note(record, "Applied provisionally from 1 January 2021 and in force from 22 February 2021 (Lovdata).")

    for rid, spec in PARTIES.items():
        record = get_record(rid)
        url = LOVDATA + spec["doc"]
        parties = record["parties"]
        for code, value in spec["in_force"].items():
            party = next((p for p in parties if p["id"] == code), None)
            if party is None:
                party = {"id": code, "type": "country"}
                parties.append(party)
                print(f"{rid}: {code} added as a party")
            if party.get("in_force") != value:
                print(f"{rid}: {code} in_force {party.get('in_force')} -> {value}")
                party["in_force"] = value
        for code, value in spec.get("provisional", {}).items():
            party = next(p for p in parties if p["id"] == code)
            if party.get("provisional_application") != value:
                print(f"{rid}: {code} provisional_application -> {value}")
                party["provisional_application"] = value
        for party in parties:
            # Keep the registry's key order for a party: id, type, dates, left, note.
            keys = ["id", "type", "signed", "provisional_application", "in_force", "left", "note"]
            ordered_party = {k: party[k] for k in keys if k in party}
            ordered_party.update({k: v for k, v in party.items() if k not in ordered_party})
            party.clear()
            party.update(ordered_party)
        cite(record, "parties", url)
        note = "The parties' own entry into force dates are from Lovdata, the treaty register of Norway, the depositary"
        add_note(record, note + ("; Fedlex confirms Switzerland's." if "CH" in spec["in_force"] else "."))

    eftaee = get_record("EFTAEE")
    stale = ("The Fedlex title names the EFTA States as parties; Norway, an EFTA State at signature, is not listed "
             "here and was not checked.")
    if stale in (eftaee.get("notes") or ""):
        eftaee["notes"] = eftaee["notes"].replace(stale, "").strip()

    for rid, spec in OFFICIAL.items():
        record = get_record(rid)
        url = LOVDATA + spec["doc"]
        link(record, url)
        for field in ("signed", "in_force") if rid not in KEEP else ("signed",):
            if record.get(field):
                cite(record, field, url)
        cite(record, "parties", url)
        if spec.get("end_doc"):
            cite(record, "ended", LOVDATA + spec["end_doc"])
        if rid in KEEP:
            add_note(record, KEEP[rid])
        if record.get("verification") != "official":
            print(f"{rid}: verification {record.get('verification')} -> official")
        record["verification"] = "official"

    for rid, spec in NOTES.items():
        record = get_record(rid)
        add_note(record, spec["note"])
        link(record, LOVDATA + spec["doc"])
        cite(record, "notes", LOVDATA + spec["doc"])

    for rid, iid, doc, kind, extra in INSTRUMENTS:
        record = get_record(rid)
        page = pages[doc]
        status_text = page.get("status", "")
        in_force = extra.get("in_force") or iso(page.get("ikraftNorge") or page.get("ikraft"))
        item = {"id": iid, "kind": kind, "name": extra.get("name") or page.get("tittelOrginal")}
        item["other_names"] = [{"lang": "no", "name": page["tittel"]}]
        if extra.get("ended"):
            item["status"] = "terminated"
        elif "ikke" in status_text or not in_force:
            item["status"] = "signed"
        else:
            item["status"] = "in_force"
        item["signed"] = extra.get("signed") or iso(page.get("undertegningsdato"))
        if item["status"] != "signed":
            item["in_force"] = in_force
        if extra.get("ended"):
            item["ended"] = extra["ended"]
        coverage = extra.get("coverage", ["goods"])
        if coverage:
            item["coverage"] = coverage
        if extra.get("notes"):
            item["notes"] = extra["notes"]
        item["provenance"] = [{"field": "instruments", "source": SOURCE, "url": LOVDATA + doc,
                               "retrieved_at": RETRIEVED}]
        if iid == "labour":
            item["provenance"].append({"field": "instruments", "source": FEDLEX,
                                       "url": "https://fedlex.data.admin.ch/sparqlendpoint",
                                       "retrieved_at": RETRIEVED})
        items = record.setdefault("instruments", [])
        existing = next((i for i in items if i.get("id") == iid), None)
        if existing is None:
            items.append(item)
            print(f"{rid}: + instrument {iid} ({item['status']} {item['signed']} / {item.get('in_force')})")
        elif existing != item:
            existing.clear()
            existing.update(item)
            print(f"{rid}: ~ instrument {iid}")
    for record in records.values():
        if record.get("instruments"):
            record["instruments"].sort(key=lambda i: (str(i.get("signed") or "9999"), i["id"]))

    for rid, record in records.items():
        record["last_verified"] = RETRIEVED
        if record.get("notes"):
            record["notes"] = re.sub(r"\s{2,}", " ", record["notes"]).strip()
        if write:
            (REGISTRY / f"{rid}.yaml").write_text(
                yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    print(f"{len(records)} records")
    apply_efta_intblock(write)
    return 0


def apply_efta_intblock(write: bool) -> None:
    """Rewrite the EFTA intblock's includes with the Convention's membership dates."""
    text = EFTA_INTBLOCK.read_text(encoding="utf-8")
    lines = ["includes:"]
    for code, name, status, joined, left in EFTA_MEMBERS:
        quoted = f"'{code}'" if code == "NO" else code
        lines += [f"- id: {quoted}", f"  name: {name}", "  type: country", f"  status: {status}", f"  joined: '{joined}'"]
        if left:
            lines.append(f"  left: '{left}'")
    block = "\n".join(lines) + "\n"
    new = re.sub(r"^includes:\n(?:[- ].*\n)+", block, text, count=1, flags=re.M)
    entry = (f"- field: includes\n  source: \"{SOURCE}\"\n  retrieved_at: \"{RETRIEVED}\"\n"
             f"  url: \"{LOVDATA}{EFTA_DOC}\"\n")
    if entry not in new:
        new = new.replace("provenance:\n", "provenance:\n" + entry, 1)
    new = re.sub(r"^last_verified: .*$", f"last_verified: '{RETRIEVED}'", new, count=1, flags=re.M)
    if new != text:
        print("EFTA intblock: includes with membership dates and former members")
        if write:
            EFTA_INTBLOCK.write_text(new, encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"fetch", "apply"}:
        print(__doc__)
        return 2
    cache = Path(argv[1])
    if argv[0] == "fetch":
        return fetch(cache)
    return apply(cache, "--write" in argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
