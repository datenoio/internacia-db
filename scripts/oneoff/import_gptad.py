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
- ``new``: an agreement missing from the registry, written as a new record from ``NEW``.
  The facts in ``NEW`` (type, status, dates, parties at signature, successor) were checked
  against the GPTAD text and the sources each entry cites, because GPTAD statuses date from
  around 2010. A record linked to an existing intblock is ``official``; any other new
  record is ``catalogue``;
- ``unmatched``: no record, or more than one, or held back (``HELD``) because no source gives
  a date the status rules need. A record still proposed or under negotiation never matches,
  since GPTAD holds signed texts.

Mapped records get ``gptad_id`` and, when GPTAD has the full text, a ``treaty_text`` link to
the PDF; their status, dates, parties and verification level do not change. A new record
that an existing record superseded gives that record ``supersedes`` when it has none, and a
successor missing from the registry is written from ``EXTRA``. See
``openspec/changes/add-gptad-catalogue-links``.

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
LIBRARY = "https://wits.worldbank.org/gptad/library.aspx"
SOURCE = "World Bank Global Preferential Trade Agreements Database (GPTAD)"
RETRIEVED = "2026-11-23"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "gptad_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]

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

# GPTAD id -> a new record. ``parties`` (country codes, or dicts with party dates and notes)
# defaults to the GPTAD membership; ``sources`` lists (field, source, url) beyond the GPTAD row.
ASEAN = ["BN", "ID", "KH", "LA", "MM", "MY", "PH", "SG", "TH", "VN"]
ASEAN_CN_FA = ("https://asean.org/dialogue-partners/framework-agreement-on-comprehensive-economic-co-operation-"
               "between-asean-and-the-peoples-republic-of-china/")
ASEAN_IN_FA = ("https://asean.org/dialogue-partners/framework-agreement-on-comprehensive-economic-cooperation-"
               "between-the-association-of-southeast-asian-nations-and-the-republic-of-lndia/")
ALADI_A = "http://www2.aladi.org/nsfaladi/textacdos.nsf/4d5c18e55622e1040325749000756112/{}?OpenDocument"
ALADI_H = "http://www2.aladi.org/nsfaladi/histtextacdos.nsf/f88cf0ec27a4b651032576790064fc05/{}?OpenDocument"
ALADI_T = "http://www2.aladi.org/nsfaladi/textacdos.nsf/f648ed517f865e1883257d800057e111/{}?OpenDocument"
MICI_CA = "https://mici.gob.pa/wp-content/uploads/2022/06/3-Documento-Explicativo-TLC-Centroamerica.pdf"
JORDAN_FTAS = "https://jordanexportportal.gov.jo/menu-1/135-fta-insights"
JORDAN_CUSTOMS = "https://traderepository.customs.gov.jo/english/page8.html"
JOMA_TEXT = "https://services.customs.gov.jo/JCcits/Agreements/%d8%a7%d9%84%d9%85%d8%ba%d8%b1%d8%a8.pdf"
ACCESSION_2004 = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:12003T/AFI"
NEW: dict[int, dict] = {
    # Founding treaties of economic communities that are intblocks: linked records.
    352: {
        "id": "AEC", "intblock": "AEC", "agreement_type": "framework", "status": "in_force",
        "notes": "The Abuja Treaty sets out the African Economic Community in six stages, with a free trade area "
                 "and a customs union in each regional economic community; it carries no tariff commitments itself.",
        "sources": [("status", "African Union, OAU/AU treaties",
                     "https://au.int/en/treaties/treaty-establishing-african-economic-community")],
    },
    418: {
        "id": "ECCAS", "intblock": "ECCAS", "agreement_type": "framework", "status": "in_force",
        "signed": "1983-10-18", "in_force": "1984-12-18",
        "notes": "The treaty provides for a customs union of the member states in stages. The GPTAD library links "
                 "its text, but the PDF is missing on the server.",
        "sources": [("in_force", "WIPO Lex, Treaty Establishing the Economic Community of Central African States",
                     "https://www.wipo.int/wipolex/en/treaties/details/297")],
    },
    442: {
        "id": "MRU", "intblock": "MRU", "agreement_type": "customs_union", "status": "in_force",
        "in_force": "1973-10-03",
        "notes": "The Mano River Declaration, concluded at Malema, establishes a customs union between Liberia and "
                 "Sierra Leone and came into force on signature (UN Treaty Series No. 13608). Guinea and Côte "
                 "d'Ivoire joined the union later.",
        "sources": [("status", "Mano River Union Secretariat", "https://mru.int/")],
    },
    # ASEAN+1 and BIMST-EC framework agreements: the umbrella instruments of registry FTAs.
    349: {
        "id": "ACFTA-FA",
        "name": "Framework Agreement on Comprehensive Economic Co-operation between the Association of South East "
                "Asian Nations and the People's Republic of China",
        "agreement_type": "pta", "status": "in_force", "signed": "2002-11-04", "in_force": "2003-07-01",
        "parties": ASEAN + ["CN"],
        "notes": "Signed at Phnom Penh. The framework of the ASEAN-China FTA (ACFTA); its Early Harvest Programme "
                 "cut tariffs from 1 January 2004. Amended by protocols of 2003, 2006, 2012 and 2015.",
        "sources": [("status", "ASEAN Secretariat, legal instruments with external parties", ASEAN_CN_FA)],
    },
    405: {
        "id": "AIFTA-FA",
        "name": "Framework Agreement on Comprehensive Economic Cooperation between the Association of Southeast Asian "
                "Nations and the Republic of India",
        "agreement_type": "framework", "status": "in_force", "signed": "2003-10-08", "in_force": "2004-07-01",
        "parties": ASEAN + ["IN"],
        "notes": "Signed at Bali. The framework of the ASEAN-India FTA (AIFTA). The 2009 amending protocol dropped "
                 "the Early Harvest Programme, which was never applied.",
        "sources": [("status", "ASEAN Secretariat, legal instruments with external parties", ASEAN_IN_FA)],
    },
    452: {
        "id": "AKFTA-FA",
        "name": "Framework Agreement on Comprehensive Economic Cooperation among the Governments of the Member "
                "Countries of the Association of Southeast Asian Nations and the Republic of Korea",
        "agreement_type": "framework", "status": "in_force", "signed": "2005-12-13", "in_force": "2007-06-01",
        "parties": ASEAN + ["KR"], "link": False,
        "notes": "Signed at Kuala Lumpur. The framework of the ASEAN-Korea FTA (AKFTA). Korea's treaty database "
                 "gives entry into force on 1 June 2007; the ASEAN Secretariat lists it as not in force. The GPTAD "
                 "PDF holds the Agreement on Trade in Goods (AKFTA), so this record does not link it.",
        "sources": [("in_force", "Korea Ministry of Government Legislation, treaty No. 1850",
                     "https://www.law.go.kr/trtyInfoP.do?trtySeq=2120")],
    },
    454: {
        "id": "BIMSTECFTA-FA", "name": "Framework Agreement on the BIMST-EC Free Trade Area",
        "agreement_type": "framework", "status": "in_force", "signed": "2004-02-08", "in_force": "2004-06-30",
        "parties": [{"id": "BD", "signed": "2004-06-25",
                     "note": "Joined as a founding member by the Protocol signed at Bangkok on 25 June 2004."},
                    "BT", "IN", "LK", "MM", "NP", "TH"],
        "notes": "Signed at Phuket. The framework of the BIMSTEC Free Trade Area (BIMSTECFTA), whose agreements "
                 "are still under negotiation.",
        "sources": [("status", "BIMSTEC Secretariat, trade, investment and development",
                     "https://bimstec.org/trade-investment-and-development")],
    },
    # Predecessors of registry records.
    56: {
        "id": "AUPG-1976",
        "name": "Agreement on Trade and Commercial Relations between the Government of Australia and the Government "
                "of Papua New Guinea (PATCRA)",
        "agreement_type": "fta", "status": "superseded",
        "signed": "1976-11-06", "in_force": "1977-02-01", "ended": "1991-09-20", "superseded_by": "AUPG",
        "notes": "Signed at Port Moresby ([1977] ATS 7). Replaced by PATCRA II (AUPG), according to the Australian "
                 "treaty notes, which give no withdrawal date; the end date is the entry into force of PATCRA II.",
        "sources": [("in_force", "Australian Treaty Series [1977] ATS 7",
                     "http://www.austlii.edu.au/au/other/dfat/treaties/1977/7.html"),
                    ("status", "Australian Treaty Series [1977] ATS 7, treaty notes",
                     "http://www.austlii.edu.au/au/other/dfat/treaties/1977/7_notes.html")],
    },
    # ALADI economic complementation agreements (ACE), registered with ALADI, the depositary.
    164: {
        "id": "BRCAN-ACE39",
        "name": "Economic Complementation Agreement No. 39 between Colombia, Ecuador, Peru and Venezuela, member "
                "countries of the Andean Community, and Brazil",
        "other_names": [("es", "Acuerdo de Complementación Económica N° 39")],
        "agreement_type": "pta", "status": "superseded",
        "signed": "1999-08-12", "in_force": "1999-08-16", "ended": "2006-01-02", "superseded_by": "MERCOSURCOECVE",
        "parties": ["BR", "CO", "EC", "PE", "VE"],
        "notes": "Signed at Montevideo (the GPTAD text is an unsigned draft). Extended pair by pair until ACE 59 "
                 "(MERCOSURCOECVE) replaced it for Colombia and Venezuela on 1 February 2005 and for Ecuador on "
                 "1 April 2005, and ACE 58 (MERCOSURPE) for Peru on 2 January 2006.",
        "sources": [("status", "ALADI, historical agreements, AAP.CE 39", ALADI_H.format("a6ca2d28656bbbe1032573fa006b84ef"))],
    },
    166: {
        "id": "MERCOSURBO",
        "name": "Economic Complementation Agreement No. 36 between the MERCOSUR States Parties and Bolivia",
        "other_names": [("es", "Acuerdo de Complementación Económica N° 36 celebrado entre los Gobiernos de los "
                               "Estados Partes del MERCOSUR y el Gobierno de la República de Bolivia")],
        "agreement_type": "fta", "status": "in_force", "signed": "1996-12-17", "in_force": "1997-02-28",
        "parties": ["AR", "BO", "BR", "PY", "UY"],
        "notes": "Signed at Fortaleza. Still applied after Bolivia became a full MERCOSUR member in 2024.",
        "sources": [("status", "ALADI, AAP.CE 36", ALADI_A.format("e194fee5b3812afc032577ea00670dfe"))],
    },
    168: {
        "id": "MERCOSURCL",
        "name": "Economic Complementation Agreement No. 35 between the MERCOSUR States Parties and Chile",
        "other_names": [("es", "Acuerdo de Complementación Económica N° 35 celebrado entre los Gobiernos de los "
                               "Estados Partes del MERCOSUR y el Gobierno de la República de Chile")],
        "agreement_type": "fta", "status": "in_force", "signed": "1996-06-25", "in_force": "1996-10-01",
        "parties": ["AR", "BR", "CL", "PY", "UY"],
        "notes": "Signed at Potrero de los Funes. Later Chile - Argentina, Chile - Brazil and Chile - Paraguay "
                 "agreements were folded into it as additional protocols.",
        "sources": [("status", "ALADI, AAP.CE 35", ALADI_A.format("85868e7a6308d7d70325776d005ad45a"))],
    },
    170: {
        "id": "BOCL",
        "name": "Economic Complementation Agreement No. 22 between Bolivia and Chile",
        "other_names": [("es", "Acuerdo de Complementación Económica entre el Gobierno de la República de Bolivia "
                               "y el Gobierno de la República de Chile")],
        "agreement_type": "pta", "status": "in_force", "signed": "1993-04-06", "in_force": "1993-04-06",
        "notes": "Signed at Santa Cruz de la Sierra; in force on signature. Partial lists, with non-reciprocal "
                 "concessions from Chile.",
        "sources": [("status", "ALADI, AAP.CE 22", ALADI_A.format("22e99c149349183d032567ee007cef4f"))],
    },
    171: {
        "id": "CLCO-1993",
        "name": "Economic Complementation Agreement No. 24 for an Expanded Economic Area between Chile and Colombia",
        "other_names": [("es", "Acuerdo de Complementación Económica para el Establecimiento de un Espacio "
                               "Económico Ampliado entre Colombia y Chile")],
        "agreement_type": "fta", "status": "superseded",
        "signed": "1993-12-06", "in_force": "1993-12-06", "ended": "2009-05-08", "superseded_by": "CLCO",
        "notes": "Signed at Santiago. The 2006 Chile - Colombia FTA (CLCO), registered as the 9th additional "
                 "protocol to ACE 24, replaced most of its articles on 8 May 2009; ACE 24 remains the ALADI "
                 "vehicle of the FTA.",
        "sources": [("status", "ALADI, AAP.CE 24, 9th additional protocol", ALADI_A.format("d9ecf5a6860893e50325729c00480b3e"))],
    },
    172: {
        "id": "CLPE-1998",
        "name": "Economic Complementation Agreement No. 38 between Chile and Peru for a Free Trade Area",
        "other_names": [("es", "Acuerdo de Complementación Económica entre Chile y Perú para la Conformación de "
                               "una Zona de Libre Comercio")],
        "agreement_type": "fta", "status": "superseded",
        "signed": "1998-06-22", "in_force": "1998-07-01", "ended": "2009-03-01", "superseded_by": "CLPE",
        "notes": "Signed at Lima (GPTAD gives 20 June 1998). Replaced by the 2006 Chile - Peru FTA (CLPE), "
                 "registered as the 3rd additional protocol to ACE 38, on 1 March 2009.",
        "sources": [("status", "ALADI, AAP.CE 38, 3rd additional protocol", ALADI_A.format("b365f278d44f531803257a080052ab01"))],
    },
    173: {
        "id": "CLVE",
        "name": "Economic Complementation Agreement No. 23 between Chile and Venezuela for an Expanded Economic Area",
        "other_names": [("es", "Acuerdo de Complementación Económica Chile - Venezuela para el establecimiento de "
                               "un espacio económico ampliado")],
        "agreement_type": "fta", "status": "in_force", "signed": "1993-04-02", "in_force": "1993-04-02",
        "notes": "Signed at Santiago; in force on signature.",
        "sources": [("status", "ALADI, AAP.CE 23", ALADI_A.format("eabe6f976fe9c738032567ef004a0f2f"))],
    },
    # Panama free trade treaties replaced by the protocols to the Central America - Panama FTA.
    177: {
        "id": "PASV-1970",
        "name": "Treaty on Free Trade and Preferential Exchange between the Republics of Panama and El Salvador",
        "other_names": [("es", "Tratado de Libre Comercio y de Intercambio Preferencial entre las Repúblicas de "
                               "Panamá y El Salvador")],
        "agreement_type": "pta", "status": "superseded",
        "signed": "1970-06-02", "in_force": "1974", "ended": "2003-04-11", "superseded_by": "PASV",
        "notes": "Signed at San Salvador. Panama's trade ministry says it applied from 1974 and ended with the "
                 "El Salvador - Panama protocol to the Central America - Panama FTA (PASV); the end date is that "
                 "protocol's entry into force.",
        "sources": [("status", "Panama Ministry of Commerce and Industries, explanatory note on the Central "
                               "America - Panama FTA", MICI_CA),
                    ("ended", "Panama Ministry of Commerce and Industries, El Salvador protocol",
                     "https://intelcom.gob.pa/doc/otros/El%20Salvador.pdf")],
    },
    # CARICOM agreements: parties are the CARICOM member states the agreement covers.
    429: {
        "id": "CARICOMCO",
        "name": "Agreement on Trade, Economic and Technical Cooperation between the Caribbean Community (CARICOM) "
                "and the Government of the Republic of Colombia",
        "agreement_type": "pta", "status": "in_force", "signed": "1994-07-24", "in_force": "1995-01-01",
        "parties": ["CO", "AG", "BB", "BZ", "DM", "GD", "GY", "JM", "KN", "LC", "MS", "TT", "VC"],
        "notes": "Signed at Cartagena. It does not apply to the Bahamas (Article 23); Suriname and Haiti joined "
                 "CARICOM later. One-way preferences from Colombia at first; a 1998 protocol made them reciprocal "
                 "for the more developed CARICOM states.",
        "sources": [("status", "ALADI, AAP.A25TM 31", ALADI_T.format("2b69a8acdd946589032568250049b6da"))],
    },
    436: {
        "id": "CARICOMCR",
        "name": "Free Trade Agreement between the Caribbean Community (CARICOM) and the Government of the Republic "
                "of Costa Rica",
        "agreement_type": "fta", "status": "in_force", "signed": "2004-03-09", "in_force": "2005-11-15",
        "parties": [{"id": "CR", "in_force": "2005-11-15"}, {"id": "TT", "in_force": "2005-11-15"},
                    {"id": "GY", "in_force": "2006-04-30"}, {"id": "BB", "in_force": "2006-08-01"},
                    {"id": "BZ", "in_force": "2011-03-10"}, {"id": "JM", "in_force": "2015-06-01"},
                    "AG", "DM", "GD", "KN", "LC", "SR", "VC"],
        "notes": "Signed at Kingston. It enters into force pair by pair with Costa Rica; no entry into force was "
                 "found for Antigua and Barbuda, Dominica, Grenada, Saint Kitts and Nevis, Saint Lucia, Saint "
                 "Vincent and the Grenadines or Suriname.",
        "sources": [("in_force", "OAS SICE, CARICOM - Costa Rica (archived copy)",
                     "https://web.archive.org/web/20251217163236/http://www.sice.oas.org/TPD/CAR_CRI/CAR_CRI_e.asp")],
    },
    438: {
        "id": "CARICOMDO",
        "name": "Agreement establishing the Free Trade Area between the Caribbean Community and the Dominican "
                "Republic",
        "agreement_type": "fta", "status": "in_force", "signed": "1998-08-22", "in_force": "2001-12-01",
        "parties": [{"id": "DO", "in_force": "2002-02-05"}, {"id": "BB", "in_force": "2001-12-01"},
                    {"id": "JM", "in_force": "2001-12-01"}, {"id": "TT", "in_force": "2001-12-01"},
                    {"id": "GY", "in_force": "2004-10-06"}, {"id": "SR", "in_force": "2005-08"},
                    "AG", "BZ", "DM", "GD", "KN", "LC", "MS", "VC"],
        "notes": "Signed at Santo Domingo; implemented by a protocol of 28 April 2000. Reciprocal for the more "
                 "developed CARICOM states only; no entry into force was found for the less developed ones.",
        "sources": [("in_force", "OAS SICE, CARICOM - Dominican Republic (archived copy)",
                     "https://web.archive.org/web/20251114061705/https://sice.oas.org/TPD/CAR_DOM/CAR_DOM_e.asp")],
    },
    455: {
        "id": "CARICOMVE",
        "name": "Agreement between the Caribbean Community (CARICOM) and the Government of the Republic of "
                "Venezuela on Trade and Investment",
        "agreement_type": "pta", "status": "in_force", "signed": "1992-10-13", "in_force": "1993-01-01",
        "parties": ["VE", "AG", "BB", "BZ", "DM", "GD", "GY", "JM", "KN", "LC", "MS", "TT", "VC"],
        "notes": "One-way preferences from Venezuela; CARICOM grants most-favoured-nation treatment. The text names "
                 "no member states: the parties are the CARICOM members of 1992 that took part in its trade "
                 "agreements, and whether it covers the Bahamas is not settled. Jamaica describes it as dormant.",
        "sources": [("status", "ALADI, AAP.A25TM 24", ALADI_T.format("f92e0b44d87d2e6d03256825004459aa"))],
    },
    456: {
        "id": "CARICOMCU",
        "name": "Trade and Economic Co-operation Agreement between the Caribbean Community (CARICOM) and the "
                "Government of the Republic of Cuba",
        "agreement_type": "pta", "status": "in_force", "signed": "2000-07-05", "in_force": "2001-01-01",
        "parties": ["CU", "AG", "BB", "BZ", "DM", "GD", "GY", "JM", "KN", "LC", "MS", "SR", "TT", "VC"],
        "notes": "Signed at Canouan. Reciprocal between Cuba and the more developed CARICOM states. The member "
                 "states applied it at different dates (Trinidad and Tobago from 2006, Jamaica from 2015).",
        "sources": [("status", "ALADI, AAP.A25TM 40", ALADI_T.format("6b4f8ccd41885f5c03256cae0048432d"))],
    },
    # Arab bilaterals not notified to the WTO; GAFTA did not end them (Jordan Export Portal).
    176: {
        "id": "EGJO",
        "name": "Free Trade Agreement between the Government of the Hashemite Kingdom of Jordan and the Government "
                "of the Arab Republic of Egypt",
        "agreement_type": "fta", "status": "in_force", "signed": "1998-12-10", "in_force": "1999-12-28",
        "notes": "Signed at Amman. Replaced a free trade zone agreement of 8 May 1996 (Article 22). Applies in "
                 "parallel with GAFTA and the Agadir Agreement. Not notified to the WTO.",
        "sources": [("status", "Jordan Export Portal, FTA insights", JORDAN_FTAS),
                    ("in_force", "Jordan Export Portal, FTA insights", JORDAN_FTAS)],
    },
    416: {
        "id": "AEJO",
        "name": "Agreement for the Setting up of a Free Trade Zone between the Government of the Hashemite Kingdom "
                "of Jordan and the Government of the State of the United Arab Emirates",
        "agreement_type": "fta", "status": "in_force", "signed": "2000-05-21", "in_force": "2001-11-24",
        "notes": "Signed at Amman. The Jordan - UAE Comprehensive Economic Partnership Agreement (in force 2025) "
                 "does not terminate it. Not notified to the WTO.",
        "sources": [("status", "Jordan Export Portal, FTA insights", JORDAN_FTAS),
                    ("in_force", "Jordan Export Portal, FTA insights", JORDAN_FTAS)],
    },
    417: {
        "id": "ILJO",
        "name": "Agreement on Trade and Economic Cooperation between the Government of the State of Israel and the "
                "Government of the Hashemite Kingdom of Jordan",
        "agreement_type": "pta", "status": "in_force", "signed": "1995-10-25", "in_force": "1996-04-19",
        "notes": "Signed at Ein Bokek. Its protocol cuts duties on listed goods; renewed for three-year terms and "
                 "upgraded in 1996 and 2004. UN Treaty Series No. 41441. Not notified to the WTO.",
        "sources": [("in_force", "United Nations Treaty Series, vol. 2318, No. 41441",
                     "https://treaties.un.org/doc/Publication/UNTS/Volume%202318/v2318.pdf"),
                    ("status", "Jordan Customs, trade agreements repository", JORDAN_CUSTOMS)],
    },
    419: {
        "id": "IRPK-2004",
        "name": "Preferential Trade Agreement between the Islamic Republic of Pakistan and the Islamic Republic of Iran",
        "agreement_type": "pta", "status": "in_force", "signed": "2004-03-04", "in_force": "2006-09-01",
        "notes": "Signed at Islamabad. The free trade agreement under negotiation since 2016 is IRPK.",
        "sources": [("in_force", "Dawn, 27 August 2006", "https://www.dawn.com/news/207625"),
                    ("status", "Dawn, 27 March 2016", "https://www.dawn.com/news/1248109")],
    },
    424: {
        "id": "JOMA-1994", "name": "Trade Agreement between the Hashemite Kingdom of Jordan and the Kingdom of Morocco",
        "agreement_type": "pta", "status": "superseded", "signed": "1994-10-03", "in_force": "1994-10-03",
        "ended": "1999-10-03", "superseded_by": "JOMA",
        "notes": "Signed at Amman (GPTAD gives 10 March 1994, a day-month swap). Applied provisionally from "
                 "signature. Replaced by the 1998 Jordan - Morocco Free Trade Agreement on its entry into force "
                 "(Article 23 of that agreement).",
        "sources": [("status", "Jordan Customs, Jordan - Morocco Free Trade Agreement (Arabic text)", JOMA_TEXT)],
    },
    425: {
        "id": "BHJO",
        "name": "Economic Cooperation and Free Trade Agreement between the Government of the Hashemite Kingdom of "
                "Jordan and the Government of the State of Bahrain",
        "agreement_type": "fta", "status": "in_force", "signed": "2001-07-21", "in_force": "2005-05-29",
        "notes": "Signed at Manama (GPTAD gives 1 July 2001). Not notified to the WTO.",
        "sources": [("status", "Jordan Export Portal, FTA insights", JORDAN_FTAS),
                    ("in_force", "Jordan Export Portal, FTA insights", JORDAN_FTAS)],
    },
    427: {
        "id": "JOSY",
        "name": "Agreement Establishing a Free Trade Zone between the Government of the Hashemite Kingdom of Jordan "
                "and the Government of the Syrian Arab Republic",
        "agreement_type": "fta", "status": "in_force", "signed": "2001-10-08", "in_force": "2002",
        "notes": "Signed at Amman. Replaced the earlier Jordan - Syria trade agreements (Article 17). Little used "
                 "after 2011; a joint committee formed in 2025 to review it. Not notified to the WTO.",
        "sources": [("status", "Jordan Customs, trade agreements repository", JORDAN_CUSTOMS),
                    ("status", "Jordan News, 15 July 2025",
                     "https://www.jordannews.jo/Section-109/News/Bilateral-Committee-Formed-to-Review-Jordan-Syria-"
                     "Free-Trade-Agreement-43250")],
    },
    428: {
        "id": "JOTN",
        "name": "Agreement of Free Trade Zone between the Government of the Hashemite Kingdom of Jordan and the "
                "Government of the Tunisian Republic",
        "agreement_type": "fta", "status": "in_force", "signed": "1998-04-22", "in_force": "1999-06-16",
        "notes": "Signed at Tunis. Not notified to the WTO.",
        "sources": [("status", "Jordan Export Portal, FTA insights", JORDAN_FTAS),
                    ("in_force", "Jordan Export Portal, FTA insights", JORDAN_FTAS)],
    },
    441: {
        "id": "EGPS",
        "name": "Trade Agreement between the Government of the Arab Republic of Egypt and the Palestine Liberation "
                "Organization for the benefit of the Palestinian National Authority",
        "agreement_type": "pta", "status": "in_force", "signed": "1998-04-28", "in_force": "1999-12-28",
        "notes": "Signed at Gaza (GPTAD gives 19 February 1997, the date of the GAFTA resolution its preamble "
                 "cites). Two-year terms, renewed automatically; no source after 2000 confirms that it is applied. "
                 "The GPTAD library links its text, but the PDF is missing on the server.",
        "sources": [("in_force", "Egyptian Official Gazette No. 5 of 3 February 2000 (Decree 2/2000)",
                     "https://manshurat.org/node/39084")],
    },
    # Bilateral agreements.
    463: {
        "id": "HRLT", "name": "Free Trade Agreement between the Republic of Croatia and the Republic of Lithuania",
        "agreement_type": "fta", "status": "terminated",
        "signed": "2002-10-24", "in_force": "2003-05-01", "ended": "2004-05-01",
        "notes": "Signed in Zagreb. Ended when Lithuania joined the EU on 1 May 2004: under Article 6(10) of the 2003 "
                 "Act of Accession the new member states withdrew from their free trade agreements with third "
                 "countries. Not notified to the WTO.",
        "sources": [("in_force", "Ministry of Foreign Affairs of Lithuania, bilateral treaties with Croatia",
                     "https://www.urm.lt/en/treaties/bilateral/croatia/1239"),
                    ("status", "EUR-Lex, 2003 Act of Accession, Article 6(10)", ACCESSION_2004)],
    },
}
# GPTAD id -> why an agreement missing from the registry is not added yet: the status rules
# need a date that no source gives.
HELD: dict[int, str] = {
    165: "1998 CAN - MERCOSUR framework agreement: in force on signature, now historical at ALADI, end date unknown",
    174: "1973 Costa Rica - Panama treaty, replaced by CRPA on 2008-11-23: entry into force date unknown",
    178: "1973 Honduras - Panama treaty, replaced by HNPA on 2009-01-09: entry into force date unknown",
}
UNSIGNED = frozenset({"proposed", "negotiating"})
# Full-text PDFs the library links but the server does not have (HTTP 403, checked 2026-11-23).
MISSING_PDF = frozenset({
    "Japan-Switzerland.pdf", "Laos-Thailand.pdf", "PTN.pdf", "US-bahrain.pdf", "japan-vietnam.pdf",
    "ECCAS.pdf", "Egypt-Palestine.pdf",
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
    339: "1995 Armenia - Iran trade agreement: most-favoured-nation treatment, not preferential",
    431: "1984 India - China trade agreement: most-favoured-nation treatment, not preferential",
    433: "2006 India - Bangladesh trade agreement: cooperation and most-favoured-nation treatment, not preferential",
    460: "1981 India - Maldives trade agreement: most-favoured-nation treatment, not preferential",
    461: "1996 India - Mongolia trade and economic cooperation agreement: most-favoured-nation treatment",
    439: "IGAD agreement (1996): an organisation charter that aims at trade harmonisation, without trade commitments",
    430: "CEPGL convention (1976): an organisation charter for economic cooperation, without trade commitments",
    353: "ASEAN - Japan Framework (2003): a leaders' framework without entry into force; the agreement is AJCEP",
    423: "Arab Maghreb Union treaty (1989): an organisation charter that states aims, without trade commitments",
}

# Records that are not in GPTAD but that a new GPTAD record names as its successor.
ACE58 = ALADI_A.format("76bd2c93dc98a5850325789500538ef9")
ACE59 = ALADI_A.format("a87b9915768aab9b032578af004bcd49")
ACE_TEXT = "http://www2.aladi.org/biblioteca/publicaciones/aladi/acuerdos/ace/es/ace{0}/ACE_0{0}_Acuerdo_Texto.pdf"
EXTRA: list[dict] = [
    {
        "id": "MERCOSURPE",
        "name": "Economic Complementation Agreement No. 58 between the MERCOSUR States Parties and Peru",
        "other_names": [{"lang": "es", "name": "Acuerdo de Complementación Económica N° 58 suscrito entre los "
                                               "Gobiernos de los Estados Partes del MERCOSUR y el Gobierno de la "
                                               "República del Perú"}],
        "agreement_type": "fta", "status": "in_force", "signed": "2005-11-30", "in_force": "2006-01-02",
        "parties": [{"id": c, "type": "country", "in_force": d} for c, d in (
            ("AR", "2006-01-02"), ("BR", "2006-01-02"), ("PE", "2006-01-02"), ("PY", "2006-02-06"),
            ("UY", "2006-01-02"))],
        "notes": "Signed at Montevideo and deposited with ALADI. In force between Peru and Argentina, Brazil and "
                 "Uruguay from 2 January 2006 and Paraguay from 6 February 2006. Replaced ACE 39 (BRCAN-ACE39) "
                 "between Brazil and Peru. Not notified to the WTO.",
        "verification": "official", "last_verified": RETRIEVED,
        "provenance": [
            {"field": "parties", "source": "ALADI, AAP.CE 58", "url": ACE58, "retrieved_at": RETRIEVED},
            {"field": "in_force", "source": "ALADI, AAP.CE 58", "url": ACE58, "retrieved_at": RETRIEVED},
            {"field": "signed", "source": "ALADI, text of AAP.CE 58", "url": ACE_TEXT.format(58),
             "retrieved_at": RETRIEVED},
        ],
    },
    {
        "id": "MERCOSURCOECVE",
        "name": "Economic Complementation Agreement No. 59 between the MERCOSUR States Parties and Colombia, "
                "Ecuador and Venezuela, member countries of the Andean Community",
        "other_names": [{"lang": "es", "name": "Acuerdo de Complementación Económica N° 59 suscrito entre "
                                               "Argentina, Brasil, Paraguay y Uruguay, Estados Partes del MERCOSUR, y "
                                               "Colombia, Ecuador y Venezuela, Países Miembros de la CAN"}],
        "agreement_type": "fta", "status": "in_force", "signed": "2004-10-18", "in_force": "2005-01-05",
        "parties": [{"id": c, "type": "country", "in_force": d} for c, d in (
            ("AR", "2005-01-05"), ("BR", "2005-02-01"), ("CO", "2005-02-01"), ("EC", "2005-04-01"),
            ("PY", "2005-04-19"), ("UY", "2005-01-05"), ("VE", "2005-01-05"))],
        "supersedes": "BRCAN-ACE39",
        "notes": "Signed at Montevideo and deposited with ALADI. In force pair by pair: Venezuela with Argentina and "
                 "Uruguay from 5 January 2005 and with Brazil from 1 February 2005; Colombia with Argentina, Brazil "
                 "and Uruguay from 1 February 2005; Ecuador with them from 1 April 2005; Paraguay with all three "
                 "from 19 April 2005. ALADI still lists all seven signatories; Colombia and MERCOSUR also signed "
                 "ACE 72 in 2017, which is not in the registry. Not notified to the WTO.",
        "verification": "official", "last_verified": RETRIEVED,
        "provenance": [
            {"field": "parties", "source": "ALADI, AAP.CE 59", "url": ACE59, "retrieved_at": RETRIEVED},
            {"field": "in_force", "source": "ALADI, AAP.CE 59", "url": ACE59, "retrieved_at": RETRIEVED},
            {"field": "signed", "source": "ALADI, text of AAP.CE 59", "url": ACE_TEXT.format(59),
             "retrieved_at": RETRIEVED},
        ],
    },
    {
        "id": "JOMA",
        "name": "Free Trade Agreement between the Government of the Hashemite Kingdom of Jordan and the Government "
                "of the Kingdom of Morocco",
        "agreement_type": "fta", "status": "in_force", "signed": "1998-06-16", "in_force": "1999-10-03",
        "parties": [{"id": "JO", "type": "country"}, {"id": "MA", "type": "country"}],
        "supersedes": "JOMA-1994",
        "notes": "Signed at Rabat. Replaced the 1994 trade agreement (Article 23). Applies in parallel with GAFTA "
                 "and the Agadir Agreement. Not notified to the WTO.",
        "verification": "official", "last_verified": RETRIEVED,
        "provenance": [
            {"field": "parties", "source": "Jordan Customs, Jordan - Morocco Free Trade Agreement (Arabic text)",
             "url": JOMA_TEXT, "retrieved_at": RETRIEVED},
            {"field": "in_force", "source": "Jordan Export Portal, FTA insights", "url": JORDAN_FTAS,
             "retrieved_at": RETRIEVED},
        ],
    },
]


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


AFTER_PARTIES = ("superseded_by", "wto_rta_id", "aric_id", "gptad_id", "wikidata_id", "links", "description",
                 "notes", "verification")


def insert_before(text: str, line: str, keys: tuple[str, ...]) -> str:
    """Insert a top-level ``line`` before the first of ``keys`` present in the YAML text."""
    for key in keys:
        if f"\n{key}:" in text:
            return text.replace(f"\n{key}:", f"\n{line}\n{key}:", 1)
    raise ValueError(f"no anchor for {line!r}")


def new_record(gptad_id: int, spec: dict, pdf: str | None, parties: list[str]) -> dict:
    """A registry record for a GPTAD agreement missing from the registry."""
    record: dict = {"id": spec["id"]}
    if spec.get("intblock"):
        record["intblock"] = spec["intblock"]
    else:
        record["name"] = spec["name"]
    if spec.get("other_names"):
        record["other_names"] = [{"lang": lang, "name": name} for lang, name in spec["other_names"]]
    record["agreement_type"] = spec["agreement_type"]
    record["status"] = spec["status"]
    for key in ("signed", "in_force", "ended"):
        if spec.get(key):
            record[key] = spec[key]
    if not spec.get("intblock"):
        record["parties"] = [
            {"id": p, "type": "country"} if isinstance(p, str) else {"id": p["id"], "type": "country", **{
                k: v for k, v in p.items() if k != "id"}}
            for p in spec.get("parties") or parties
        ]
    for key in ("supersedes", "superseded_by"):
        if spec.get(key):
            record[key] = spec[key]
    record["gptad_id"] = gptad_id
    if pdf and spec.get("link", True):
        record["links"] = [{"url": pdf, "type": "treaty_text"}]
    if spec.get("notes"):
        record["notes"] = spec["notes"]
    record["verification"] = "official" if spec.get("intblock") else "catalogue"
    record["last_verified"] = RETRIEVED
    record["provenance"] = [
        {"field": "signed" if spec.get("intblock") else "parties", "source": SOURCE,
         "url": pdf if pdf and spec.get("link", True) else LIBRARY,
         "retrieved_at": RETRIEVED},
    ] + [{"field": f, "source": src, "url": url, "retrieved_at": RETRIEVED} for f, src, url in spec.get("sources", [])]
    keys = [k for k in FIELD_ORDER if k in record]
    if "intblock" in keys:
        keys.remove("intblock")
        keys.insert(1, "intblock")
    return {k: record[k] for k in keys}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("gptad_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write gptad_id, links and new records to data/trade_agreements/")
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
        elif gid in NEW:
            result.update(result="new", record=NEW[gid]["id"], how="NEW", detail="")
        elif gid in HELD:
            result.update(result="unmatched", record="", how="HELD", detail=HELD[gid])
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
            linked = NEW.get(r["gptad_id"], {}).get("link", True) and r["pdf"].startswith(PDF_PREFIX)
            new = insert_fields(text, r["gptad_id"], r["pdf"] if linked else None)
            if new != text:
                path.write_text(new, encoding="utf-8")
                written += 1
        created = 0
        for record in EXTRA:
            path = REGISTRY / f"{record['id']}.yaml"
            if not path.exists():
                path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
                created += 1
        for r in results:
            if r["result"] != "new":
                continue
            spec = NEW[r["gptad_id"]]
            path = REGISTRY / f"{spec['id']}.yaml"
            if path.exists() or spec["id"] in intblocks and spec.get("intblock") != spec["id"]:
                print(f"! {r['gptad_id']}: id {spec['id']} is taken")
                continue
            record = new_record(r["gptad_id"], spec, r["pdf"] or None, sorted(r["parties"].split(",")))
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
            created += 1
            successor = spec.get("superseded_by")
            if successor and spec.get("mark_successor", True):
                target = REGISTRY / f"{successor}.yaml"
                text = target.read_text(encoding="utf-8")
                if "\nsupersedes:" not in text:
                    target.write_text(insert_before(text, f"supersedes: {spec['id']}", AFTER_PARTIES), encoding="utf-8")
        print(f"wrote {written} records, created {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
