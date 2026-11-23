#!/usr/bin/env python3
"""One-off: add ALADI partial-scope agreements missing from the registry, current and historical.

Input is the directory written by ``fetch_aladi.py`` (``index.json`` and ``docs/<code>.html``).
The pages are untrusted data: keep them outside the repository and run this script with
``python -I``.

A walk on 2026-11-23 compared ALADI's 90 current agreements with the registry by signatories
and date of signature. 15 carry no trade preferences (transport, tourism, waterway and
vehicle rules under Article 14, the agricultural health council), 25 already had a record
(the Mexico agreements from WTO RTA-IS, the GPTAD walk's ALADI records, and ACE 18, which is
MERCOSUR's Treaty of Asunción), and the 51 in ``SELECT`` had none. This script writes one
record for each of them. 16 of them were added from OAS SICE the same day (``import_sice.py``)
and merged by hand with the ALADI record under the SICE ids; the script skips existing files.

ALADI is the depositary, so the records are ``verification: official``. Signatories come
from ``Países signatarios``, the date of signature from ``Fecha de suscripción`` (US order,
``MM/DD/YY`` or ``MM/DD/YYYY``), and entry into force from ``Entrada en vigor`` (``DD/MM/YYYY``
or Spanish words); when it differs by pair of parties, each party gets the date of its
first pair. An agreement for which ALADI has no notice of entry into force is ``signed``.

Historical agreements (``HISTORY``) are the 118 terminated agreements missing from the
registry, read one by one. Their records give no end date field, but the ``Nota SG`` of the
secretariat says which agreement replaced them and from when. 62 are imported as
``superseded``: the end date is the one the note gives, else the successor's entry into
force between the same parties. 9 are imported as ``terminated``: the multilateral
commercial agreements (AAP.C), which ended pair by pair, some pairs replaced by a successor
and the others lapsing at their last extension, and ACE 26, which expired before its
successor.

A second pass over the 47 left out found the missing date for 19 in the validity clause of
the text, the secretariat's note, the protocols or the successor's text: 3 more
``superseded`` (ACE 8 of 1987, AAP.R 32, AAP.A25TM 14), 15 ``terminated`` (the 1982
sectoral commercial agreements that lapsed at their last extension, AAP.R 22, 34 and 35,
ACE 61) and one ``abandoned`` (AR.PREC 5, never in force). ``LEFT_OUT`` lists the other 28
with the reason: no official date of entry into force (the status rules need one), a
successor among those, incomplete pair-by-pair end dates, or a record in the DESTA walk.
See ``docs/intblock-sources.md``.

Usage: python -I scripts/oneoff/import_aladi.py ALADI_DIR [--write]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SOURCE = "ALADI, agreements database"
RECORD = "http://www2.aladi.org/nsfaladi/{}.nsf/0/{}?OpenDocument"

ES = {
    "argentina": "AR", "bolivia": "BO", "brasil": "BR", "chile": "CL", "colombia": "CO", "cuba": "CU",
    "ecuador": "EC", "méxico": "MX", "panamá": "PA", "paraguay": "PY", "perú": "PE", "uruguay": "UY",
    "venezuela": "VE", "costa rica": "CR", "el salvador": "SV", "guatemala": "GT", "honduras": "HN",
    "nicaragua": "NI", "trinidad y tobago": "TT", "guyana": "GY", "suriname": "SR",
    "san cristobal y nieves": "KN",
}
EN = {
    "AR": "Argentina", "BO": "Bolivia", "BR": "Brazil", "CL": "Chile", "CO": "Colombia", "CU": "Cuba",
    "EC": "Ecuador", "MX": "Mexico", "PA": "Panama", "PY": "Paraguay", "PE": "Peru", "UY": "Uruguay",
    "VE": "Venezuela", "CR": "Costa Rica", "SV": "El Salvador", "GT": "Guatemala", "HN": "Honduras",
    "NI": "Nicaragua", "TT": "Trinidad and Tobago", "GY": "Guyana", "SR": "Suriname", "KN": "Saint Kitts and Nevis",
}
MERCOSUR = {"AR", "BR", "PY", "UY"}
MONTHS = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
MONTHS["setiembre"] = 9
NO_DATE = "ALADI, the depositary, has no notice of its entry into force."

# ALADI code -> record id, agreement type and notes (checked by hand against the ALADI record).
# ``parties`` overrides the signatories ALADI lists; ``title`` overrides the generated name.
SELECT: dict[str, dict] = {
    "AAP.CE Nº 2": {"id": "BRUY", "type": "pta", "notes": "The Brazil - Uruguay Trade Expansion Protocol (PEC)."},
    "AAP.CE Nº 13": {"id": "ARPY", "type": "pta"},
    "AAP.CE Nº 14": {"id": "ARBR", "type": "fta",
                     "notes": "The Argentina - Brazil tariff elimination programme towards a common market, "
                              "taken up by MERCOSUR."},
    "AAP.CE Nº 16": {"id": "ARCL-1991", "type": "pta"},
    "AAP.CE Nº 40": {"id": "CUVE", "type": "pta"},
    "AAP.CE Nº 42": {"id": "CLCU", "type": "pta"},
    "AAP.CE Nº 46": {"id": "CUEC", "type": "pta"},
    "AAP.CE Nº 47": {"id": "BOCU", "type": "pta"},
    "AAP.CE Nº 49": {"id": "COCU", "type": "pta"},
    "AAP.CE Nº 50": {"id": "CUPE", "type": "pta"},
    "AAP.CE Nº 54": {"id": "MERCOSURMX", "type": "framework",
                     "notes": "Framework agreement for a free trade area between MERCOSUR and Mexico."},
    "AAP.CE Nº 55": {"id": "MERCOSURMX-AUTO", "type": "pta",
                     "notes": "Free trade in the automotive sector between MERCOSUR states and Mexico."},
    "AAP.CE Nº 57": {"id": "ARUY-AUTO", "type": "pta", "notes": "Trade in the automotive sector."},
    "AAP.CE Nº 62": {"id": "MERCOSURCU", "type": "pta"},
    "AAP.CE Nº 63": {"id": "UYVE", "type": "pta", "notes": "Venezuela grants duty-free access to listed goods."},
    "AAP.CE Nº 64": {"id": "PYVE", "type": "pta", "notes": "Venezuela grants duty-free access to listed goods."},
    "AAP.CE Nº 68": {"id": "ARVE", "type": "pta",
                     "notes": "Governs trade during Venezuela's accession to MERCOSUR."},
    "AAP.CE Nº 69": {"id": "BRVE", "type": "pta",
                     "notes": "Governs trade during Venezuela's accession to MERCOSUR."},
    "AAP.CE Nº 70": {"id": "ECOALBA", "type": "framework",
                     "title": "Economic Complementation Agreement No. 70: Framework Agreement for the Economic "
                              "Space of the Bolivarian Alliance for the Peoples of Our America - Peoples' Trade "
                              "Treaty (ECOALBA-TCP)"},
    "AAP.CE Nº 71": {"id": "CUPA", "type": "pta"},
    "AAP.CE Nº 72": {"id": "MERCOSURCO", "type": "fta",
                     "notes": "ALADI gives the dates of application between Colombia and each MERCOSUR state."},
    "AAP.CE Nº 73": {"id": "CLUY", "type": "fta"},
    "AAP.CE Nº 74": {"id": "BRPY", "type": "framework"},
    "AAP.CE Nº 75": {"id": "CLEC", "type": "fta"},
    "AAP.CE Nº 76": {"id": "MERCOSURPA", "type": "framework"},
    "AAP.A25TM Nº 6": {"id": "CONI", "type": "pta"},
    "AAP.A25TM Nº 7": {"id": "COCR-1984", "type": "pta",
                       "notes": "Not the 2013 Colombia - Costa Rica FTA (COCR)."},
    "AAP.A25TM Nº 16": {"id": "HNVE", "type": "pta"},
    "AAP.A25TM Nº 20": {"id": "TTVE", "type": "pta"},
    "AAP.A25TM Nº 22": {"id": "GYVE", "type": "pta"},
    "AAP.A25TM Nº 23": {"id": "GTVE", "type": "pta"},
    "AAP.A25TM Nº 25": {"id": "NIVE", "type": "pta"},
    "AAP.A25TM Nº 26": {"id": "CRVE", "type": "pta"},
    "AAP.A25TM Nº 27": {"id": "SVVE", "type": "pta"},
    "AAP.A25TM Nº 29": {"id": "COPA", "type": "pta"},
    "AAP.A25TM Nº 36": {"id": "CUGT", "type": "pta"},
    "AAP.A25TM Nº 37": {"id": "GTMXSV", "type": "other",
                        "parties": ["MX", "GT", {"id": "SV", "note": "Listed by ALADI as a party; the text is "
                                                                     "signed by Mexico and Guatemala."}],
                        "notes": "Trade in natural gas between Mexico and Guatemala: transport, distribution, "
                                 "storage, export and import."},
    "AAP.A25TM Nº 38": {"id": "BRGYKN", "type": "pta",
                        "parties": ["BR", "GY", {"id": "KN", "note": "Listed by ALADI as a party; the text is "
                                                                     "signed by Brazil and Guyana."}]},
    "AAP.A25TM Nº 41": {"id": "BRSR", "type": "pta", "notes": "Tariff preferences for rice."},
    "AAP.A25TM Nº 42": {"id": "ECGT", "type": "pta"},
    "AAP.A25TM Nº 44": {"id": "CUNI", "type": "pta"},
    "AAP.A25TM Nº 45": {"id": "ECNI", "type": "pta"},
    "AAP.A25TM Nº 47": {"id": "CUHN", "type": "pta"},
    "AAP.A25TM Nº 48": {"id": "BOSV", "type": "pta"},
    "AAP.A14TM Nº 12": {"id": "MERCOSURCACM", "type": "framework",
                        "parties": ["AR", "BR", "PY", "UY", "CR", "GT", "HN", "NI", "SV"],
                        "title": "Framework Agreement on Trade and Investment between MERCOSUR and the Central "
                                 "American Common Market"},
    "AAP.AG Nº 1": {"id": "ARUY-AG1", "type": "pta", "notes": "Preferential treatment for live cattle and meat."},
    "AAP.AG Nº 2": {"id": "ALADI-AG2", "type": "pta", "notes": "Liberalisation of trade in seeds."},
    "AR.AM Nº 1": {"id": "ALADI-AM1", "type": "preference_scheme", "beneficiary": "BO"},
    "AR.AM Nº 2": {"id": "ALADI-AM2", "type": "preference_scheme", "beneficiary": "EC"},
    "AR.AM Nº 3": {"id": "ALADI-AM3", "type": "preference_scheme", "beneficiary": "PY"},
    "AR.PAR Nº 4": {"id": "ALADI-PAR", "type": "pta",
                    "parties": ["AR", "BO", "BR", "CL", "CO", "EC", "MX", "PE", "PY", "UY", "VE",
                                {"id": "CU", "note": "Joined after acceding to ALADI in 1999."},
                                {"id": "PA", "note": "Joined after acceding to ALADI in 2012."}],
                    "title": "Regional Agreement No. 4 establishing the Regional Tariff Preference",
                    "notes": "A tariff preference that each member grants to the goods of the others, with "
                             "margins graded by level of development."},
}
# Historical agreements: ALADI code -> record id, type, the successor (``by``, its ALADI code
# or name, and ``sup``, its registry id) and the end date, read from the ``Nota SG`` of the
# record (else the successor's entry into force between the same parties, from its ALADI
# record). ``residual``: the note keeps in force the provisions on matters the successor does
# not cover; ``replaced`` words the replacement when it went pair by pair. ``in_force``
# overrides ALADI's date when the validity clause of the text contradicts it; ``why`` says so
# in the notes; ``parties`` gives party ``left`` dates. Without ``sup`` the record is ``terminated``.
AR_MX_1994 = "Argentina - Mexico on 30 December 1994, when ACE 6 (ARMX) took over"
HISTORY: dict[str, dict] = {
    "AAP.R Nº 1": {"id": "ARBR-AAPR1", "by": "AAP.CE Nº 14", "sup": "ARBR", "ended": "1990-12-20"},
    "AAP.R Nº 2": {"id": "ARBO-AAPR2", "by": "AAP.CE Nº 19", "sup": "ARBO-ACE19", "ended": "1992-04-28"},
    "AAP.R Nº 3": {"id": "BRCL-AAPR3", "by": "AAP.CE Nº 35", "sup": "MERCOSURCL", "ended": "1996-10-01",
                   "residual": True},
    "AAP.R Nº 4": {"id": "ARCO-AAPR4", "by": "AAP.CE Nº 11", "sup": "ARCO-ACE11", "ended": "1988-08-01"},
    "AAP.R Nº 6": {"id": "ARPE-AAPR6", "by": "AAP.CE Nº 9", "sup": "ARPE-ACE9", "ended": "1988-04-01"},
    "AAP.R Nº 7": {"id": "ARVE-AAPR7", "by": "AAP.CE Nº 10", "sup": "ARVE-ACE10", "ended": "1986-04-11"},
    "AAP.R Nº 8": {"id": "BOBR-AAPR8", "by": "AAP.CE Nº 26", "sup": "BOBR-ACE26", "ended": "1994-01-27"},
    "AAP.R Nº 9": {"id": "BRMX-AAPR9", "by": "AAP.CE Nº 53", "sup": "BRMX", "ended": "2003-05-02"},
    "AAP.R Nº 10": {"id": "BRCO-AAPR10", "by": "AAP.CE Nº 39", "sup": "BRCAN-ACE39", "ended": "1999-08-16",
                    "residual": True},
    "AAP.R Nº 11": {"id": "BREC-AAPR11", "by": "AAP.CE Nº 39", "sup": "BRCAN-ACE39", "ended": "1999-08-16",
                    "residual": True},
    "AAP.R Nº 12": {"id": "BRPE-AAPR12", "by": "AAP.CE Nº 25", "sup": "BRPE-ACE25", "ended": "1994-05-23",
                    "notes": "ALADI dates the end from 23 May 1994, when both parties had incorporated ACE 25 into "
                             "their law, and gives 28 September 1994 as the entry into force of ACE 25."},
    "AAP.R Nº 13": {"id": "BRVE-AAPR13", "by": "AAP.CE Nº 27", "sup": "BRVE-ACE27", "ended": "1995-01-31"},
    "AAP.R Nº 14": {"id": "CLCO-AAPR14", "by": "AAP.CE Nº 24", "sup": "CLCO-1993", "ended": "1993-12-06"},
    "AAP.R Nº 15": {"id": "CLEC-AAPR15", "by": "AAP.CE Nº 32", "sup": "CLEC-ACE32", "ended": "1994-12-20",
                    "in_force": "1983-04-30",
                    "why": "In force from signature under Article 27; ALADI's date of entry into force, 30 May "
                           "1983, does not match the text."},
    "AAP.R Nº 16": {"id": "CLVE-AAPR16", "by": "AAP.CE Nº 23", "sup": "CLVE", "ended": "1993-04-02"},
    "AAP.R Nº 17": {"id": "BOPY-AAPR17", "by": "AAP.CE Nº 29", "sup": "BOPY-ACE29", "ended": "1994-03-15"},
    "AAP.R Nº 18": {"id": "COPY-AAPR18", "by": "AAP.CE Nº 59", "sup": "MERCOSURCOECVE", "ended": "2005-04-19",
                    "residual": True,
                    "notes": "ALADI's transcription of the validity clause gives 10 June 1987 as the start date."},
    "AAP.R Nº 20": {"id": "PEPY-AAPR20", "by": "AAP.CE Nº 58", "sup": "MERCOSURPE", "ended": "2006-02-06",
                    "residual": True},
    "AAP.R Nº 21": {"id": "PYVE-AAPR21", "by": "AAP.CE Nº 59", "sup": "MERCOSURCOECVE", "ended": "2005-04-19",
                    "residual": True},
    "AAP.R Nº 23": {"id": "COUY-AAPR23", "by": "AAP.CE Nº 59", "sup": "MERCOSURCOECVE", "ended": "2005-02-01",
                    "residual": True},
    "AAP.R Nº 25": {"id": "UYVE-AAPR25", "by": "AAP.CE Nº 59", "sup": "MERCOSURCOECVE", "ended": "2005-01-05",
                    "residual": True},
    "AAP.R Nº 26": {"id": "ALADI-AAPR26", "by": "AAP.CE Nº 35", "sup": "MERCOSURCL", "ended": "1996-10-01",
                    "residual": True,
                    "notes": "The preferences between Argentina, Paraguay and Uruguay were last extended to 31 "
                             "December 1995, and those between Chile and Paraguay to 30 September 1995."},
    "AAP.R Nº 27": {"id": "BOCL-AAPR27", "by": "AAP.CE Nº 22", "sup": "BOCL", "ended": "1993-04-06"},
    "AAP.R Nº 28": {"id": "CLPE-AAPR28", "by": "AAP.CE Nº 38", "sup": "CLPE-1998", "ended": "1998-07-01"},
    "AAP.R Nº 30": {"id": "MXVE-AAPR30", "by": "AAP.CE Nº 33", "sup": "G-3", "ended": "1995-01-01"},
    "AAP.R Nº 31": {"id": "BOMX-AAPR31", "by": "AAP.CE Nº 31", "sup": "BOMX-ACE31", "ended": "1995-01-01"},
    "AAP.R Nº 33": {"id": "PEUY-AAPR33", "by": "AAP.CE Nº 58", "sup": "MERCOSURPE", "ended": "2006-01-02",
                    "residual": True},
    "AAP.R Nº 36": {"id": "ARMX-AAPR36", "by": "AAP.CE Nº 6", "sup": "ARMX", "ended": "1989-07-01",
                    "notes": "The parties ended it under Article 34 of ACE 6."},
    "AAP.R Nº 37": {"id": "CLMX-AAPR37", "by": "AAP.CE Nº 17", "sup": "CLMX-ACE17", "ended": "1991-09-22"},
    "AAP.R Nº 40": {"id": "COMX-AAPR40", "by": "AAP.CE Nº 33", "sup": "G-3", "ended": "1995-01-01"},
    "AAP.CE Nº 4": {"id": "CLUY-ACE4", "by": "AAP.CE Nº 35", "sup": "MERCOSURCL", "ended": "1996-10-01",
                    "residual": True},
    "AAP.CE Nº 5": {"id": "MXUY-ACE5", "by": "AAP.CE Nº 60", "sup": "MXUY", "ended": "2004-07-15"},
    "AAP.CE Nº 7": {"id": "ARBR-ACE7", "by": "AAP.CE Nº 14", "sup": "ARBR", "ended": "1990-12-20"},
    "AAP.CE Nº 9": {"id": "ARPE-ACE9", "by": "AAP.CE Nº 48", "sup": "ARCAN-ACE48", "ended": "2000-08-01",
                    "residual": True, "notes": "Last extended to 31 July 2000."},
    "AAP.CE Nº 10": {"id": "ARVE-ACE10", "by": "AAP.CE Nº 20", "sup": "ARVE-ACE20", "ended": "1995-08-06"},
    "AAP.CE Nº 11": {"id": "ARCO-ACE11", "by": "AAP.CE Nº 48", "sup": "ARCAN-ACE48", "ended": "2000-08-01",
                     "residual": True},
    "AAP.CE Nº 12": {"id": "ARBR-ACE12", "by": "AAP.CE Nº 14", "sup": "ARBR", "ended": "1990-12-20"},
    "AAP.CE Nº 15": {"id": "BOUY-ACE15", "by": "AAP.CE Nº 36", "sup": "MERCOSURBO", "ended": "1997-02-28",
                     "residual": True},
    "AAP.CE Nº 17": {"id": "CLMX-ACE17", "type": "fta", "by": "AAP.CE Nº 41", "sup": "CLMX", "ended": "1999-08-01"},
    "AAP.CE Nº 19": {"id": "ARBO-ACE19", "by": "AAP.CE Nº 36", "sup": "MERCOSURBO", "ended": "1997-02-28",
                     "residual": True, "in_force": "1992-04-28",
                     "why": "In force from signature under Article 33; ALADI's date of entry into force, 28 April "
                            "1982, is ten years before the signature."},
    "AAP.CE Nº 20": {"id": "ARVE-ACE20", "by": "AAP.CE Nº 48", "sup": "ARCAN-ACE48", "ended": "2000-08-01",
                     "residual": True},
    "AAP.CE Nº 25": {"id": "BRPE-ACE25", "by": "AAP.CE Nº 39", "sup": "BRCAN-ACE39", "ended": "1999-08-16",
                     "residual": True},
    "AAP.CE Nº 26": {"id": "BOBR-ACE26", "ended": "1995-12-31",
                     "notes": "Expired on 31 December 1995 under its Second Additional Protocol. From 28 February "
                              "1997 ACE 36 (MERCOSURBO) covers the trade between Bolivia and Brazil; the "
                              "provisions of ACE 26 outside its trade liberalisation programme stay in force "
                              "(Article 42 of ACE 36)."},
    "AAP.CE Nº 27": {"id": "BRVE-ACE27", "by": "AAP.CE Nº 39", "sup": "BRCAN-ACE39", "ended": "1999-08-16",
                     "residual": True},
    "AAP.CE Nº 29": {"id": "BOPY-ACE29", "by": "AAP.CE Nº 36", "sup": "MERCOSURBO", "ended": "1997-02-28",
                     "residual": True},
    "AAP.CE Nº 31": {"id": "BOMX-ACE31", "type": "fta", "by": "AAP.CE Nº 66", "sup": "BOMX", "ended": "2010-06-07",
                     "in_force": "1995-01-01",
                     "why": "Entry into force on 1 January 1995 under Article 21-04; ALADI gives no date.",
                     "notes": "Bolivia denounced it on 7 December 2009, with effect from 7 June 2010, the day "
                              "ACE 66 entered into force."},
    "AAP.CE Nº 32": {"id": "CLEC-ACE32", "type": "fta", "by": "AAP.CE Nº 65", "sup": "CLEC-ACE65",
                     "ended": "2010-01-25"},
    "AAP.CE Nº 34": {"id": "MERCOSURBO-ACE34", "by": "AAP.CE Nº 36", "sup": "MERCOSURBO", "ended": "1997-02-28",
                     "in_force": "1996-01-01",
                     "why": "In force from 1 January 1996 under Article 37; ALADI's date of entry into force, 1 "
                            "January 1994, is before the signature.",
                     "notes": "Kept the bilateral preferences between Bolivia and the MERCOSUR States in force "
                              "until ACE 36."},
    "AAP.CE Nº 43": {"id": "BRCU-ACE43", "by": "AAP.CE Nº 62", "sup": "MERCOSURCU", "ended": "2007-07-02",
                     "residual": True},
    "AAP.CE Nº 44": {"id": "CUUY-ACE44", "by": "AAP.CE Nº 62", "sup": "MERCOSURCU", "ended": "2008-09-03",
                     "residual": True},
    "AAP.CE Nº 45": {"id": "ARCU-ACE45", "by": "AAP.CE Nº 62", "sup": "MERCOSURCU", "ended": "2007-07-02",
                     "residual": True},
    "AAP.CE Nº 48": {"id": "ARCAN-ACE48", "by": "AAP.CE Nº 59", "sup": "MERCOSURCOECVE", "ended": "2006-01-02",
                     "parties": ["AR", {"id": "CO", "left": "2005-02-01"}, {"id": "EC", "left": "2005-04-01"},
                                 {"id": "PE", "left": "2006-01-02"}, {"id": "VE", "left": "2005-01-05"}],
                     "replaced": "Replaced pair by pair: by ACE 59 (MERCOSURCOECVE) for Venezuela on 5 January "
                                 "2005, Colombia on 1 February 2005 and Ecuador on 1 April 2005, and by ACE 58 "
                                 "(MERCOSURPE) for Peru on 2 January 2006, except for provisions on matters that they "
                                 "do not cover."},
    "AAP.CE Nº 52": {"id": "CUPY-ACE52", "by": "AAP.CE Nº 62", "sup": "MERCOSURCU", "ended": "2009-02-24",
                     "residual": True},
    "AAP.CE Nº 65": {"id": "CLEC-ACE65", "type": "fta", "by": "AAP.CE Nº 75", "sup": "CLEC", "ended": "2022-05-16",
                     "notes": "Certificates of origin under ACE 65 were accepted until 14 July 2022."},
    "AAP.A25TM Nº 1": {"id": "CRMX-A25TM1", "by": "the 1994 Costa Rica - Mexico FTA", "sup": "CRMX",
                       "ended": "1995-01-01"},
    "AAP.A25TM Nº 4": {"id": "ARCU-A25TM4", "by": "AAP.CE Nº 45", "sup": "ARCU-ACE45", "ended": "2000-01-01",
                       "notes": "Last extended to 31 December 1999."},
    "AAP.A25TM Nº 5": {"id": "COGT-A25TM5", "by": "the Colombia - Northern Triangle FTA", "sup": "COGTHNSV",
                       "ended": "2009-11-12"},
    "AAP.A25TM Nº 10": {"id": "GTMX-A25TM10", "by": "the Mexico - Northern Triangle FTA", "sup": "GTMX",
                        "ended": "2001-03-15"},
    "AAP.A25TM Nº 12": {"id": "CUMX-A25TM12", "by": "AAP.CE Nº 51", "sup": "CUMX", "ended": "2001-02-28"},
    "AAP.A25TM Nº 15": {"id": "MXSV-A25TM15", "by": "the Mexico - Northern Triangle FTA", "sup": "MXSV",
                        "ended": "2001-03-15"},
    "AAP.A25TM Nº 19": {"id": "COCU-A25TM19", "by": "AAP.A25TM Nº 33", "sup": "COCU-A25TM33", "ended": "1995-01-01"},
    "AAP.A25TM Nº 33": {"id": "COCU-A25TM33", "by": "AAP.CE Nº 49", "sup": "COCU", "ended": "2001-07-14"},
    "AAP.C Nº 24": {"id": "ARMX-AAPC24", "by": "AAP.CE Nº 6", "sup": "ARMX", "ended": "1994-12-30",
                    "notes": "The parties ended its preferences under Article 4 of the First Additional Protocol to "
                             "ACE 6."},
    "AAP.C Nº 10": {"id": "ALADI-AAPC10", "ended": "1997-12-31",
                    "notes": f"Ended pair by pair: {AR_MX_1994}, Argentina - Brazil on 30 September 1997 and Brazil - Mexico "
                             "on 31 December 1997, their last extensions."},
    "AAP.C Nº 15": {"id": "ALADI-AAPC15", "ended": "1997-12-31",
                    "notes": f"Ended pair by pair: {AR_MX_1994}, Argentina - Brazil on 30 September 1997 and Brazil - Mexico "
                             "on 31 December 1997, their last extensions."},
    "AAP.C Nº 22": {"id": "ALADI-AAPC22", "ended": "1997-12-31",
                    "notes": f"Ended pair by pair: {AR_MX_1994}, Argentina - Brazil on 30 September 1997 and Brazil - Mexico "
                             "on 31 December 1997, their last extensions."},
    "AAP.C Nº 26": {"id": "ALADI-AAPC26", "ended": "1997-12-31",
                    "notes": f"Ended pair by pair: {AR_MX_1994}, Argentina - Brazil on 30 September 1997 and Brazil - Mexico "
                             "on 31 December 1997, their last extensions."},
    "AAP.C Nº 13": {"id": "ALADI-AAPC13", "ended": "2005-01-05",
                    "notes": "Ended pair by pair: Argentina - Venezuela on 7 October 1993, under ACE 20; "
                             f"{AR_MX_1994}; Mexico - Venezuela on 1 January 1995 (G-3); Brazil - Venezuela on the "
                             "incorporation of its Eighth Additional Protocol, under ACE 27; Argentina - Brazil, "
                             "Argentina - Uruguay and Brazil - Uruguay on 31 December 1996, Brazil - Mexico on 31 "
                             "December 1997 and Mexico - Uruguay on 31 March 2001, their last extensions; Uruguay - "
                             "Venezuela on 5 January 2005, when ACE 59 (MERCOSURCOECVE) took over."},
    "AAP.C Nº 18": {"id": "ALADI-AAPC18", "ended": "2005-01-31",
                    "notes": "Ended pair by pair: Argentina - Venezuela on 7 October 1993, under ACE 20; "
                             f"{AR_MX_1994}; Mexico - Venezuela on 1 January 1995 (G-3); Brazil - Venezuela on the "
                             "incorporation of its Twentieth Additional Protocol, under ACE 27; Argentina - Brazil, "
                             "Argentina - Uruguay and Brazil - Uruguay on 30 September 1997, Brazil - Mexico on 31 "
                             "December 1997, Mexico - Uruguay on 31 March 2001 and Uruguay - Venezuela on 31 "
                             "January 2005, their last extensions."},
    "AAP.C Nº 19": {"id": "ALADI-AAPC19", "ended": "2001-03-31",
                    "notes": f"Ended pair by pair: {AR_MX_1994}; Argentina - Brazil, Argentina - Uruguay and Brazil - "
                             "Uruguay on 30 September 1997, Brazil - Mexico on 31 December 1997 and Mexico - "
                             "Uruguay on 31 March 2001, their last extensions."},
    "AAP.C Nº 21": {"id": "ALADI-AAPC21", "ended": "1997-12-31",
                    "notes": f"Ended pair by pair: Mexico - Uruguay on 31 December 1989, Brazil - Chile on 31 "
                             "December 1990, Argentina - Chile, Chile - Mexico and Chile - Uruguay on 31 December "
                             f"1991; {AR_MX_1994}; Argentina - Uruguay on 30 June 1995, Argentina - Brazil and Brazil - "
                             "Uruguay on 30 September 1997 and Brazil - Mexico on 31 December 1997, their last "
                             "extensions."},
    # Second pass over the left-out agreements: the dates come from the validity clause of the text,
    # the Secretariat's note, the protocols in the ALADI record, or the successor's text. ``signed``
    # overrides ALADI's date of signature, ``status`` the status, ``prov`` adds provenance entries.
    "AAP.CE Nº 8": {"id": "MXPE-ACE8", "by": "the Mexico - Peru Trade Integration Agreement", "sup": "MXPE",
                    "ended": "2012-02-01", "in_force": "1987-03-25",
                    "why": "In force from 25 March 1987 under Article 34; ALADI has no notice of its entry into force.",
                    "notes": "ALADI registers the 2011 agreement under the same number, ACE 8."},
    "AAP.R Nº 32": {"id": "MXPE-AAPR32", "by": "AAP.CE Nº 8", "sup": "MXPE-ACE8", "ended": "1987-03-25"},
    "AAP.A25TM Nº 14": {"id": "MXPA-A25TM14", "by": "the Mexico - Panama FTA", "sup": "MXPA", "ended": "2015-07-01",
                        "notes": "Article 20.7 of the FTA ended it on the FTA's entry into force and kept its tariff "
                                 "preferences for 30 days for certificates of origin issued before.",
                        "prov": [("ended", "Mexico - Panama Free Trade Agreement, Article 20.7 (OAS SICE copy)",
                                  "https://web.archive.org/web/20160914180105/http://sice.oas.org/TPD/MEX_PAN/"
                                  "Draft_MEX_PAN_FTA_s/33_disposiciones_finales_tlc_mex_pan_20140509.pdf")]},
    "AAP.CE Nº 61": {"id": "COMXVE-ACE61", "ended": "2005-12-31", "in_force": "2005-01-01",
                     "why": "In force from 1 January to 31 December 2005 under Article 11; ALADI's date of entry into "
                            "force, 1 January 1995, is ten years before the signature.",
                     "notes": "Free trade in the automotive sector, televisions, fertilisers and disposable razors "
                              "between the members of the Group of Three."},
    "AAP.R Nº 22": {"id": "BOUY-AAPR22", "ended": "1989-04-30",
                    "notes": "In force for six years from 1 May 1983 (Article 29), as the ALADI Secretariat notes; the "
                             "end date is the last day of that term. ACE 15 (BOUY-ACE15) and ACE 36 (MERCOSURBO) later "
                             "covered trade between Bolivia and Uruguay."},
    "AAP.C Nº 1": {"id": "ALADI-AAPC1", "ended": "1992-10-29",
                   "parties": ["AR", "BR", {"id": "CL", "left": "1991-11-28"}, "MX", {"id": "UY", "left": "1989-12-22"}],
                   "notes": "Statistical and similar machines. Uruguay's participation ended on 22 December 1989 (First "
                            "Additional Protocol) and Chile's on 28 November 1991 (Third Additional Protocol, signed by "
                            "Brazil, Chile and Mexico), which set its end at 29 October 1992.",
                   "prov": [("ended", "ALADI, Third Additional Protocol to AAP.C No. 1 (ALADI/AAP.C/1.3)",
                             "http://www2.aladi.org/biblioteca/publicaciones/aladi/acuerdos/ac/es/ac01/AC_001_003.pdf")]},
    "AAP.C Nº 2": {"id": "ALADI-AAPC2", "ended": "1984-12-27", "in_force": "1982-11-29",
                   "why": "In force from signature under Article 20; ALADI gives no date of entry into force.",
                   "notes": "Electronic valves. The First Additional Protocol ended it from 27 December 1984."},
    "AAP.C Nº 8": {"id": "ARMX-AAPC8", "ended": "1985-03-31", "in_force": "1982-12-29",
                   "why": "In force from signature under Article 21; ALADI gives no date of entry into force.",
                   "notes": "Glass industry. The Second Protocol extended its preferences for the last time to 31 "
                            "March 1985."},
    "AAP.C Nº 9": {"id": "BRMX-AAPC9", "ended": "1997-12-31", "in_force": "1982-11-29",
                   "why": "In force from signature under Article 22; ALADI gives no date of entry into force.",
                   "notes": "Electricity generation, transmission and distribution. Last extended to 31 December "
                            "1997 (ALADI/ACUERDOS COMERCIALES/Add.7 of 29 September 1997)."},
    "AAP.C Nº 12": {"id": "BRMX-AAPC12", "ended": "1997-12-31",
                    "notes": "Electronics and electrical communications. Last extended to 31 December 1997 "
                             "(ALADI/ACUERDOS COMERCIALES/Add.7 of 29 September 1997)."},
    "AAP.C Nº 14": {"id": "BRMX-AAPC14", "ended": "1991-11-28", "signed": "1982-11-29",
                    "why": "ALADI gives no date of signature; the agreement entered into force on signature (Article "
                           "21), on 29 November 1982.",
                    "notes": "Household electrical, mechanical and thermal appliances. The First Additional Protocol "
                             "ended it from 28 November 1991."},
    "AAP.C Nº 17": {"id": "ARBR-AAPC17", "ended": "1996-12-31",
                    "notes": "Refrigeration and air conditioning. Last extended to 31 December 1996 (ALADI/ACUERDOS "
                             "COMERCIALES/Add.2 of 12 January 1996)."},
    "AAP.C Nº 20": {"id": "ALADI-AAPC20", "ended": "1997-12-31",
                    "notes": "Dyes and pigments. Ended pair by pair: Argentina - Brazil and Argentina - Mexico on 31 "
                             "December 1989 (Seventh Additional Protocol), Brazil - Mexico on 31 December 1997, its last "
                             "extension. No preferences were registered between Chile and the other signatories."},
    "AAP.C Nº 23": {"id": "ARMX-AAPC23", "ended": "1991-11-28",
                    "notes": "Electricity generation, transmission and distribution. The Second Additional Protocol "
                             "ended it from 28 November 1991."},
    "AAP.C Nº 25": {"id": "ARMX-AAPC25", "ended": "1991-11-28",
                    "notes": "Lamps and lighting units. The Sixth Additional Protocol ended it from 28 November 1991."},
    "AAP.C Nº 27": {"id": "ALADI-AAPC27", "ended": "1997-12-31",
                    "notes": "Glass. Ended pair by pair: Mexico - Venezuela on 1 January 1995 (G-3); Brazil - Venezuela "
                             "once both had incorporated its Third Additional Protocol of 30 December 1994, under ACE 27 "
                             "(BRVE-ACE27, in force from 31 January 1995); Brazil - Mexico on 31 December 1997, its last "
                             "extension."},
    "AAP.R Nº 34": {"id": "BRPY-AAPR34", "ended": "1995-06-30",
                    "notes": "The Third Additional Protocol extended its preferences for the last time to 30 June 1995."},
    "AAP.R Nº 35": {"id": "BRUY-AAPR35", "ended": "1995-06-30",
                    "notes": "The Fifteenth Additional Protocol extended its preferences for the last time to 30 June "
                             "1995."},
    "AR.PREC Nº 5": {"id": "ALADI-PREC5", "status": "abandoned",
                     "title": "Regional Agreement No. 5 for the Recovery and Expansion of Intra-Regional Trade (PREC)",
                     "notes": "Never entered into force: Article 26 made it apply from 1 January 1989 if at least four "
                              "signatories had put it into force, a condition the ALADI Secretariat notes was not met."},
}
# Historical agreements that are left out, with the reason: 24 without an official date of entry
# into force or end, and the four that the DESTA walk (datenoio/internacia-db#229) adds.
# AAP.A14TM 2 (cultural and scientific cooperation) carries no trade preferences, ACE 39 has a
# record (BRCAN-ACE39), and the AAP.PC trade promotion agreements are not fetched.
NO_DATE_HIST = "ALADI has no date of entry into force, and the text makes it depend on notifications"
CUBA = "ALADI has no date of entry into force; the text makes it depend on notifications, and Cuba's is not on record"
IN_229 = "added by the DESTA walk (datenoio/internacia-db#229) as "
LEFT_OUT: dict[str, str] = {
    **{code: NO_DATE_HIST for code in ("AAP.CE Nº 21", "AAP.CE Nº 28", "AAP.CE Nº 30", "AAP.A25TM Nº 11")},
    **{code: CUBA for code in ("AAP.A25TM Nº 17", "AAP.A25TM Nº 21", "AAP.A25TM Nº 28", "AAP.A25TM Nº 30",
                               "AAP.A25TM Nº 32", "AAP.A25TM Nº 34", "AAP.A25TM Nº 35")},
    "AAP.CE Nº 56": "a framework that needed every signatory's notice; Uruguay never gave one (ACE 58 and 59 "
                    "replaced it), but ALADI does not say it never entered into force",
    "AAP.R Nº 5": "it ended when the First Additional Protocol to ACE 21 took effect, a date not on record",
    "AAP.CE Nº 3": "it ended when the First Additional Protocol to ACE 21 took effect, a date not on record",
    "AAP.R Nº 19": "its successor ACE 30 is left out",
    "AAP.R Nº 24": "its successor ACE 28 is left out",
    "AAP.A25TM Nº 18": "its successor AAP.A25TM 30 is left out",
    "AAP.R Nº 39": "no note: ALADI only lists ACE 5 and ACE 60 as later agreements, and neither text ends it",
    "AAP.C Nº 5": "the note gives no end date for several pairs",
    "AAP.C Nº 7": "the note gives 30 September 2007 as its last extension, citing a document of December 1996 that "
                  "extended the other sectoral agreements to 30 September 1997",
    "AAP.C Nº 16": "the note gives no end date for six pairs",
    "AAP.A14TM Nº 11": "a framework that ACE 58 and ACE 59 replaced pair by pair; no end date for the framework",
    "AAP.A25TM Nº 8": "no end date: the Colombia - Northern Triangle FTA keeps its preferences in force (Appendix 1 "
                      "to Annex 3.4)",
    "AAP.A25TM Nº 9": "no end date: the Colombia - Northern Triangle FTA keeps its preferences in force (Appendix 1 "
                      "to Annex 3.4)",
    "AAP.CE Nº 1": IN_229 + "ARUY-1982",
    "AAP.A25TM Nº 2": IN_229 + "ARCR-1983",
    "AAP.A25TM Nº 3": IN_229 + "ARSV-1983",
    "AAP.A25TM Nº 13": IN_229 + "MXNI-1985",
}
FIELD_ORDER = ["id", "name", "other_names", "agreement_type", "status", "signed", "in_force", "ended", "parties",
               "supersedes", "superseded_by", "notes", "verification", "last_verified", "provenance"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]


AFTER_PARTIES = ("superseded_by", "wto_rta_id", "aric_id", "gptad_id", "wikidata_id", "links", "description",
                 "notes", "verification")


def insert_before(text: str, line: str, keys: tuple[str, ...]) -> str:
    """Insert a top-level ``line`` before the first of ``keys`` present in the YAML text."""
    for key in keys:
        if f"\n{key}:" in text:
            return text.replace(f"\n{key}:", f"\n{line}\n{key}:", 1)
    raise ValueError(f"no anchor for {line!r}")


def words(date: str) -> str:
    year, month, day = date.split("-")
    return f"{int(day)} {MONTH_NAMES[int(month) - 1]} {year}"


def short(code: str) -> str:
    """``AAP.CE Nº 14`` -> ``ACE 14``; other codes keep the ALADI form with ``No.``."""
    return code.replace("AAP.CE Nº ", "ACE ").replace("Nº", "No.")


def page_text(path: Path) -> str:
    t = path.read_text(encoding="latin-1")
    t = re.sub(r"<(script|style).*?</\1>", "", t, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " | ", t))
    t = re.sub(r"(\s*\|\s*)+", " | ", t)
    return re.sub(r"\s+", " ", t)


def field(text: str, label: str) -> str:
    """A record field: ``label | : | value | ____``."""
    m = re.search(re.escape(label) + r" \| : \| (.*?) \| _{5,}", text)
    return m.group(1).strip() if m else ""


def signature_date(value: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})", value.strip())
    if not m:
        return None
    year = int(m.group(3))
    if year < 100:
        year += 1900 if year >= 60 else 2000
    return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


DATE = r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2} de [a-zé]+ de \d{4})"


def day_first(value: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{1,2}) de ([a-zé]+) de (\d{4})", value)
    if m and m.group(2) in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None


def codes(names: str) -> list[str]:
    """Country codes in a Spanish list such as ``Argentina, Brasil, Uruguay (MERCOSUR)``."""
    names = re.sub(r"\((MERCOSUR|MCCA|CARICOM)\)", "", names.lower())
    out = []
    for key in sorted(ES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(key)}\b", names):
            out.append(ES[key])
            names = re.sub(rf"\b{re.escape(key)}\b", " ", names)
    return sorted(out)


def entry_into_force(value: str) -> tuple[str | None, dict[str, str]]:
    """The earliest date and, when dates differ by pair, each party's first date."""
    per_party: dict[str, str] = {}
    pairs = re.findall(rf"(?:Entre|entre|Para)\s+([^:|]+?)\s*:\s*{DATE}", value)
    pairs += [(who, d) for who, d in re.findall(rf"para ([^|]+?) el (?:día )?{DATE}", value)]
    for who, raw in pairs:
        date = day_first(raw)
        for code in codes(who.replace("-", " y ")):
            if date and (code not in per_party or date < per_party[code]):
                per_party[code] = date
    dates = sorted({d for d in (day_first(x) for x in re.findall(DATE, value)) if d})
    first = dates[0] if dates else None
    return first, per_party if len(set(per_party.values())) > 1 else {}


def listing(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def name_for(code: str, spec: dict, parties: list[str], signed: str | None) -> tuple[str, str]:
    kind, number = code.split(" Nº ")
    if spec.get("title"):
        english = spec["title"]
    else:
        # MERCOSUR dates from the Treaty of Asunción (26 March 1991).
        if set(parties) > MERCOSUR and (signed or "") >= "1991-03-26":
            between = "the MERCOSUR States Parties and " + listing([EN[c] for c in parties if c not in MERCOSUR])
        else:
            between = listing([EN[c] for c in parties])
        english = {
            "AAP.CE": f"Economic Complementation Agreement No. {number} between {between}",
            "AAP.A25TM": f"Partial Scope Agreement No. {number} between {between} "
                         "(Article 25 of the 1980 Montevideo Treaty)",
            "AAP.AG": f"Agricultural Partial Scope Agreement No. {number} between {between}",
            "AAP.R": f"Partial Scope Renegotiation Agreement No. {number} between {between}",
            "AAP.C": f"Partial Scope Commercial Agreement No. {number} between {between}",
        }.get(kind) or (f"Regional Market Opening Agreement No. {number} in favour of {EN[spec['beneficiary']]}"
                        if kind == "AR.AM" else f"{kind} No. {number}")
    spanish = {
        "AAP.CE": f"Acuerdo de Complementación Económica N° {number}",
        "AAP.A25TM": f"Acuerdo de Alcance Parcial N° {number} (Artículo 25 del Tratado de Montevideo 1980)",
        "AAP.A14TM": f"Acuerdo de Alcance Parcial N° {number} (Artículo 14 del Tratado de Montevideo 1980)",
        "AAP.AG": f"Acuerdo de Alcance Parcial Agropecuario N° {number}",
        "AAP.R": f"Acuerdo de Alcance Parcial de Renegociación N° {number}",
        "AAP.C": f"Acuerdo de Alcance Parcial Comercial N° {number}",
        "AR.AM": f"Acuerdo Regional de Apertura de Mercados N° {number}",
        "AR.PAR": f"Acuerdo Regional N° {number} - Preferencia Arancelaria Regional",
        "AR.PREC": f"Acuerdo Regional N° {number} - Recuperación y Expansión del Comercio Intrarregional (PREC)",
    }[kind]
    return english, spanish


def history_notes(spec: dict) -> list[str]:
    """Notes of a historical record: date corrections, then the successor, then the record's own notes."""
    notes = [spec["why"]] if spec.get("why") else []
    if spec.get("sup"):
        by = short(spec["by"]) if spec["by"].startswith("AAP.") else spec["by"]
        replaced = f"Replaced by {by} ({spec['sup']}) from {words(spec['ended'])}"
        notes.append(spec.get("replaced") or replaced + (
            f", except for provisions on matters that {by} does not cover." if spec.get("residual") else "."))
    if spec.get("notes"):
        notes.append(spec["notes"])
    return notes


def build(code: str, spec: dict, agreement: dict, text: str) -> dict:
    hist = agreement["db"] == "hist"
    listed = codes(field(text, "Países signatarios"))
    signed = spec.get("signed") or signature_date(field(text, "Fecha de suscripción"))
    first, per_party = entry_into_force(field(text, "Entrada en vigor"))
    if hist and spec.get("in_force"):
        first, per_party = spec["in_force"], {}
    abandoned = spec.get("status") == "abandoned"
    if abandoned:
        first, per_party = None, {}
    raw_parties = spec.get("parties") or listed
    ids = [p if isinstance(p, str) else p["id"] for p in raw_parties]
    english, spanish = name_for(code, spec, ids, signed)
    parties = []
    for p in raw_parties:
        party = {"id": p, "type": "country"} if isinstance(p, str) else {"id": p["id"], "type": "country",
                                                                         **{k: v for k, v in p.items() if k != "id"}}
        if party["id"] == spec.get("beneficiary"):
            party["note"] = "Beneficiary: the other members grant duty-free access to listed goods without reciprocity."
        if party["id"] in per_party:
            party = {"id": party["id"], "type": "country", "in_force": per_party[party["id"]],
                     **{k: v for k, v in party.items() if k not in ("id", "type")}}
        parties.append(party)
    notes = [f"Registered with ALADI as {code.replace('Nº', 'No.')}."]
    if hist:
        notes += history_notes(spec)
    elif spec.get("notes"):
        notes.append(spec["notes"])
    if not first and not abandoned:
        notes.append(NO_DATE)
    if hist:
        status = spec.get("status") or ("superseded" if spec.get("sup") else "terminated")
    else:
        status = "in_force" if first else "signed"
    record = {
        "id": spec["id"], "name": english, "other_names": [{"lang": "es", "name": spanish}],
        "agreement_type": spec.get("type", "pta"), "status": status, "signed": signed,
    }
    if first:
        record["in_force"] = first
    if hist and not abandoned:
        record["ended"] = spec["ended"]
    record["parties"] = parties
    if spec.get("supersedes"):
        record["supersedes"] = spec["supersedes"]
    if spec.get("sup"):
        record["superseded_by"] = spec["sup"]
    record["notes"] = " ".join(notes)
    record["verification"] = "official"
    record["last_verified"] = RETRIEVED
    url = RECORD.format("histtextacdos" if hist else "textacdos", agreement["main"])
    if abandoned:
        fields = ("parties", "signed", "status")
    elif hist:
        fields = ("parties", "signed", "in_force", "ended")
    else:
        fields = ("parties", "signed", "in_force" if first else "status")
    record["provenance"] = [{"field": f, "source": SOURCE, "url": url, "retrieved_at": RETRIEVED} for f in fields]
    record["provenance"] += [{"field": f, "source": source, "url": link, "retrieved_at": RETRIEVED}
                             for f, source, link in spec.get("prov", [])]
    overridden = {p["id"] for p in raw_parties if isinstance(p, dict)}
    problems = sorted(set(ids) - set(listed) - overridden)
    if problems:
        print(f"! {code}: parties {problems} are not among the ALADI signatories {listed}")
    return {k: record[k] for k in FIELD_ORDER if k in record}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("aladi_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write the records to data/trade_agreements/")
    args = parser.parse_args(argv)
    index = json.loads((args.aladi_dir / "index.json").read_text(encoding="utf-8"))
    assert not set(HISTORY) & set(LEFT_OUT), set(HISTORY) & set(LEFT_OUT)
    existing = {path.stem: yaml.safe_load(path.read_text(encoding="utf-8")) for path in REGISTRY.glob("*.yaml")}
    # A successor with exactly one predecessor and no ``supersedes`` gets one.
    predecessors: dict[str, list[str]] = {}
    for rid, record in existing.items():
        if record.get("superseded_by") and rid not in {s["id"] for s in HISTORY.values()}:
            predecessors.setdefault(record["superseded_by"], []).append(rid)
    for spec in HISTORY.values():
        if spec.get("sup"):
            predecessors.setdefault(spec["sup"], []).append(spec["id"])
    single = {succ: pred[0] for succ, pred in predecessors.items() if len(pred) == 1}
    new_ids = {s["id"] for s in HISTORY.values()} | {s["id"] for s in SELECT.values()}
    written = 0
    for code, spec in [*SELECT.items(), *HISTORY.items()]:
        agreement = index[code]
        expected = "hist" if code in HISTORY else "cur"
        if agreement["db"] != expected:
            print(f"! {code} is not a {expected} agreement")
            continue
        if spec["id"] in single and not (existing.get(spec["id"]) or {}).get("supersedes"):
            spec = {**spec, "supersedes": single[spec["id"]]}
        text = page_text(args.aladi_dir / "docs" / (code.replace(" ", "_").replace("º", "") + ".html"))
        record = build(code, spec, agreement, text)
        path = REGISTRY / f"{record['id']}.yaml"
        print(f"{code:18} {record['id']:18} {record['status']:10} {record['signed']} {record.get('in_force', '-'):10} "
              f"{record.get('ended', '-'):10} {record.get('superseded_by', '-'):15} "
              f"{','.join(p['id'] for p in record['parties'])}")
        successor = record.get("superseded_by")
        if successor and successor not in existing and successor not in new_ids:
            print(f"! {code}: successor {successor} is not in the registry")
        if args.write and not path.exists():
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
            written += 1
    linked = 0
    for successor, predecessor in sorted(single.items()):
        path = REGISTRY / f"{successor}.yaml"
        # Also links the SELECT records that were already in the registry (the 16 merged with SICE).
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "\nsupersedes:" not in text and predecessor in {s["id"] for s in HISTORY.values()}:
            print(f"  {successor} supersedes {predecessor}")
            if args.write:
                path.write_text(insert_before(text, f"supersedes: {predecessor}", AFTER_PARTIES), encoding="utf-8")
            linked += 1
    print(f"{len(SELECT)} current and {len(HISTORY)} historical agreements, wrote {written}, "
          f"{linked} existing successors get supersedes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
