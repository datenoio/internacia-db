#!/usr/bin/env python3
"""One-off: add the U.S. trade and investment framework agreements to data/trade_agreements/.

The table below was checked by hand on 2026-11-23 against three official sources:

- USTR's list of Trade & Investment Framework Agreements and the agreement texts it links
  (https://ustr.gov/trade-agreements/trade-investment-framework-agreements); scanned texts were
  read with OCR;
- the State Department's Treaties in Force 2026 (TIF), bilateral part and the multilateral
  "Trade & Investment" section;
- USTR press releases where neither gives the date (WAEMU, the 2012 South Africa amendment).

EDIT (edit.wti.org, World Trade Institute) served only as a candidate list: the 51 U.S. rows that
the EDIT walk (docs/history/edit-match-2026-11-23.csv, PR 246) left as "missing", plus the
Central Asia TIFA. Each record links its EDIT document page when EDIT has the text, and its notes
say where EDIT's dates differ.

Held, not written: TIFAs that enter into force on an exchange of notifications and that TIF does
not list, so no official source gives the date of entry into force: Algeria (2001), Angola
(2009), Armenia (2015), ECOWAS (2014), GCC (2012), Iceland (2009), Lebanon (2006), Myanmar (2013),
Qatar (2004), Turkey (1999) and Ukraine (2008). PKUS and BRUS-TRA (Brazil ATEC) already exist and
are left unchanged.

Ids: ``<pair>-TIFA`` with the alpha-2 codes in alphabetical order (``PKUS`` style), or the bloc
name before ``US`` (``ASEANUS-TIFA``); an earlier agreement of the same pair takes its year.

Usage: python -I scripts/oneoff/import_us_tifas.py [--write]
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-11-23"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "links", "description", "notes", "instruments", "verification", "last_verified", "provenance",
]
TIF_SOURCE = "U.S. Department of State, Treaties in Force 2026"
TIF_URL = "https://www.state.gov/wp-content/uploads/2026/06/Treaties-in-Force-2026.pdf#page={page}"
USTR_LIST_SOURCE = "Office of the United States Trade Representative, Trade & Investment Framework Agreements"
USTR_LIST_URL = "https://ustr.gov/trade-agreements/trade-investment-framework-agreements"
USTR_TEXT_SOURCE = "Office of the United States Trade Representative, text of the agreement"
EDIT_SOURCE = "World Trade Institute, Electronic Database of Investment Treaties (EDIT)"
EDIT_URL = "https://edit.wti.org/document/show/{uuid}"
U = "https://ustr.gov/sites/default/files/"
WAEMU_PRESS = ("https://ustr.gov/archive/Document_Library/Press_Releases/2002/April/"
               "United_States_West_African_Nations_Sign_Agreement_Promoting_Trade.html")
USTR_AFRICA_INDEX = "https://ustr.gov/archive/World_Regions/Africa/Africa_TIFAs/Section_Index.html"
ZA_PRESS = ("https://ustr.gov/about-us/policy-offices/press-office/press-releases/2012/june/"
            "ustr-south-africa-sign-trade-agreement")

ASEAN = ["BN", "KH", "ID", "LA", "MY", "MM", "PH", "SG", "TH", "VN"]
SIGN = "enters into force on signature"


def c(*ids):
    return [(i, "country") for i in ids]


def b(bloc):
    return [(bloc, "intblock"), ("US", "country")]


# id, name, USTR label (or other English name), parties, signed, in_force, TIF page,
# USTR text URL, text_dated (the USTR text shows the date of signature), text_eif (the text
# enters into force on signature), EDIT uuid, notes, extra provenance, instruments.
R = [
    dict(id="AFUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Transitional Islamic State of Afghanistan concerning the Development of Trade and Investment Relations",
         label="U.S.-Afghanistan TIFA", parties=c("AF", "US"), signed="2004-09-21", in_force="2004-09-21", tif=11,
         text=U + "uploads/agreements/tifa/asset_upload_file642_9850.pdf", text_dated=False, text_eif=True,
         edit="217a8c40-d196-4f7d-925c-d1097893a989",
         notes="Signed at Kabul; enters into force on signature. The copy USTR posts leaves the place and date of "
               "signature blank. EDIT gives 2004-06-26 as the date of signature and entry into force."),
    dict(id="ANDEANUS-TIFA", name="Agreement between the Governments of Bolivia, Colombia, Ecuador, Peru and Venezuela, "
         "Member Countries of the Andean Community, and the Government of the United States of America relating to the "
         "Establishment of a Council on Trade and Investment",
         label="Andean Community-United States Council on Trade and Investment",
         parties=c("BO", "CO", "EC", "PE", "VE", "US"), signed="1998-10-30", in_force="1998-10-30", tif=15,
         edit="052952aa-4c1d-4acc-887f-2be11187a33f",
         notes="Signed at Washington; takes effect on signature. The five Andean governments sign as one Party; Treaties "
               "in Force files the agreement under the Andean Community. USTR's current TIFA list does not include it."),
    dict(id="ARUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Argentine Republic",
         label="U.S.-Argentina TIFA", parties=c("AR", "US"), signed="2016-03-23", in_force="2016-03-23", tif=22,
         text=U + "files/agreements/tifa/TIFA%20US%20ARG%20ENGLISH.PDF", text_dated=True, text_eif=True,
         edit="2b081f48-b60a-4331-a087-87849ca4ced6",
         notes="Signed at Buenos Aires; enters into force on signature. Separate from the 2026 Agreement on Reciprocal "
               "Trade and Investment (ARUS-ART)."),
    dict(id="ASEANUS-TIFA", name="Trade and Investment Framework Arrangement between the United States of America and "
         "the Association of Southeast Asian Nations",
         label="U.S.-ASEAN TIFA", parties=c(*ASEAN, "US"), signed="2006-08-25", in_force="2006-08-25", tif=548,
         text=U + "uploads/agreements/tifa/asset_upload_file932_9760.pdf", text_dated=True, text_eif=False,
         edit="f0737e96-4060-44b2-a42a-f6ce8e6fbbd4",
         notes="Signed at Kuala Lumpur by the United States and the ten ASEAN Member Countries, not by ASEAN as an "
               "organisation. Treaties in Force gives entry into force on signature and lists the parties without "
               "Brunei Darussalam, whose minister signed the text USTR posts."),
    dict(id="BDUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "People's Republic of Bangladesh on a Trade and Investment Cooperation Forum",
         label="U.S.-Bangladesh TICFA", parties=c("BD", "US"), signed="2013-11-25", in_force="2014-01-30", tif=37,
         text=U + "files/agreements/tifa/US-BangladeshTICFA.pdf", text_dated=False, text_eif=False,
         edit="18355f72-d69a-4467-bff3-b7562f53bc81",
         notes="Signed at Washington; enters into force when the Parties have notified each other by exchange of "
               "letters that they have completed their internal procedures."),
    dict(id="BHUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Kingdom of Bahrain concerning the Development of Trade and Investment Relations",
         label="U.S.-Bahrain TIFA", parties=c("BH", "US"), signed="2002-06-18", in_force="2002-06-18",
         text=U + "uploads/agreements/tifa/asset_upload_file168_7735.pdf", text_dated=True, text_eif=True,
         edit="48f02c1b-fa65-4d78-a879-77cab41d0b60",
         notes="Signed at Washington; effective from the date of signature. Treaties in Force 2026 does not list it. "
               "Predates the 2004 free trade agreement (USBH)."),
    dict(id="BNUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of Brunei Darussalam",
         label="U.S.-Brunei TIFA", parties=c("BN", "US"), signed="2002-12-16", in_force="2002-12-16", tif=59,
         text=U + "uploads/agreements/tifa/asset_upload_file720_10024.pdf", text_dated=True, text_eif=False,
         edit="36d7399b-0253-4038-8f21-947077384650", notes="Signed at Washington."),
    dict(id="BOUS-TIFA", name="Agreement concerning a United States-Bolivia Council on Trade and Investment",
         label="United States-Bolivia Council on Trade and Investment", parties=c("BO", "US"),
         signed="1990-05-08", in_force="1990-05-08", tif=50,
         notes="Signed at Washington. USTR's current TIFA list does not include it."),
    dict(id="CARICOMUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States "
         "of America and the Caribbean Community",
         label="U.S.-CARICOM TIFA", parties=b("CARICOM"), signed="2013-05-28", in_force="2013-05-28", tif=81,
         text=U + "US%20CARICOM%20TIFA%20US.pdf", text_dated=True, text_eif=True,
         edit="223bdc55-d6ff-4f0f-95d2-390d7f9a55c6",
         notes="Signed at Port of Spain; enters into force on signature. CARICOM signs as one Party. Follows the 1991 "
               "agreement on a CARICOM-United States Council on Trade and Investment (CARICOMUS-TIFA-1991), which "
               "Treaties in Force 2026 still lists."),
    dict(id="CARICOMUS-TIFA-1991", name="Agreement concerning a CARICOM-United States Council on Trade and Investment",
         label="CARICOM-United States Council on Trade and Investment", parties=b("CARICOM"),
         signed="1991-07-22", in_force="1991-07-22", tif=81,
         notes="Signed at Washington. Treaties in Force files it under the Caribbean Community. The 2013 TIFA "
               "(CARICOMUS-TIFA) refers to it in its preamble."),
    dict(id="CENTRALAMERICAUS-TIFA", name="Agreement concerning a Central American-United States Regional Trade and "
         "Investment Council",
         label="Central American-United States Regional Trade and Investment Council",
         parties=c("CR", "DO", "SV", "GT", "HN", "NI", "US"), signed="1998-03-20", in_force="1998-03-20", tif=547,
         notes="Signed at San Jose. Treaties in Force lists it among the multilateral trade and investment agreements, "
               "with Costa Rica, the Dominican Republic, El Salvador, Guatemala, Honduras and Nicaragua as parties."),
    dict(id="CENTRALASIAUS-TIFA", name="Framework Agreement between the Government of the United States of America, the "
         "Government of the Republic of Kazakhstan, the Government of the Kyrgyz Republic, the Government of the Republic "
         "of Tajikistan, the Government of Turkmenistan, and the Government of the Republic of Uzbekistan concerning the "
         "Development of Trade and Investment Relations",
         label="U.S.-Central Asian TIFA", parties=c("KZ", "KG", "TJ", "TM", "UZ", "US"),
         signed="2004-06-01", in_force="2004-06-01", tif=547,
         text=U + "uploads/agreements/tifa/asset_upload_file683_7722.pdf", text_dated=True, text_eif=True,
         edit="2687a56b-a709-4d96-9e90-1f25e6193671",
         notes="Signed at Washington; enters into force on signature. The United States is depositary. EDIT gives 2024-06-01 as the date of "
               "signature and entry into force."),
    dict(id="CHUS-TIFA", name="Agreement between the Government of the United States of America and the Government of "
         "the Swiss Confederation establishing a Trade and Investment Cooperation Forum",
         label="U.S.-Switzerland TICF", parties=c("CH", "US"), signed="2006-05-25", in_force="2006-05-25",
         text=U + "US-Switzerland%20TIFA.pdf", text_dated=True, text_eif=True,
         edit="f0629ebf-ad12-4c7b-b181-0df95f352d0b",
         notes="Signed at Washington; enters into force upon signature. Treaties in Force 2026 does not list it. "
               "Separate from the 2025 framework with Switzerland and Liechtenstein (CHLIUS-FRAMEWORK)."),
    dict(id="CLUS-TIFA", name="Agreement concerning a United States-Chile Council on Trade and Investment",
         label="United States-Chile Council on Trade and Investment", parties=c("CL", "US"),
         signed="1990-10-01", in_force="1990-10-01", tif=87,
         notes="Signed at Washington. Predates the 2003 free trade agreement (USCL); Treaties in Force 2026 still lists "
               "it."),
    dict(id="COMESAUS-TIFA", name="Agreement between the Government of the United States of America and the Common Market "
         "for Eastern and Southern Africa concerning the Development of Trade and Investment Relations",
         label="U.S.-COMESA TIFA", parties=b("COMESA"), signed="2001-10-29", in_force="2001-10-29",
         text=U + "uploads/agreements/tifa/asset_upload_file367_7725.pdf", text_dated=True, text_eif=True,
         edit="725c6213-cba0-46b1-ac7c-5e477a64468e",
         notes="Signed at Washington; enters into force on signature. COMESA signs as one Party. Treaties in Force "
               "2026 does not list it.",
         extra=[("signed", "Office of the United States Trade Representative, Africa TIFAs index (archive)",
                 USTR_AFRICA_INDEX)]),
    dict(id="EACUS-TIFA", name="Trade and Investment Framework Agreement between the East African Community and the "
         "Government of the United States of America",
         label="U.S.-East African Community TIFA", parties=b("EAC"), signed="2008-07-16", in_force="2008-07-16",
         tif=126, text=U + "uploads/agreements/tifa/asset_upload_file413_15020.pdf", text_dated=True, text_eif=True,
         edit="1fc50f63-dc82-4608-8f76-c0127421776e",
         notes="Signed at Washington; enters into force upon signature. The East African Community signs as one Party."),
    dict(id="ECUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Republic of Ecuador concerning a United States-Ecuador Council on Trade and Investment",
         label="U.S.-Ecuador TIC", parties=c("EC", "US"), signed="1990-07-23", in_force="1990-07-23", tif=130,
         text=U + "files/agreements/tifa/9-4-2009%20US-Ecuador%20TIC%20Agreement%20-%20English.pdf",
         text_dated=True, text_eif=True,
         notes="Signed at Washington; enters into force on signature. USTR also posts a Protocol relating to Trade "
               "Rules and Transparency, which enters into force the day after the last notification; the copy is "
               "undated, so it is not recorded as an instrument. Separate from the 2026 Agreement on Reciprocal Trade "
               "(ECUS-ART)."),
    dict(id="EEUS-TIFA", name="Agreement concerning the Development of Trade and Investment Relations between the United "
         "States of America and Estonia",
         label="United States-Estonia Agreement concerning the Development of Trade and Investment Relations",
         parties=c("EE", "US"), signed="1992-09-17", in_force="1992-09-17", tif=140,
         notes="Signed at Washington. Treaties in Force 2026 lists it; USTR's current TIFA list does not."),
    dict(id="EGUS-TIFA", name="Agreement between the Government of the United States of America and the Arab Republic of "
         "Egypt concerning the Development of Trade and Investment Relations",
         label="U.S.-Egypt TIFA", parties=c("EG", "US"), signed="1999-07-01", in_force="1999-07-01", tif=133,
         text=U + "U.S.%20-%20Egypt%20TIFA.pdf", text_dated=False, text_eif=True,
         edit="5e6751d4-dc64-42fa-bd57-b72f28cbc8ab",
         notes="Signed at Washington; enters into force on signature."),
    dict(id="FJUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Fiji",
         label="U.S.-Fiji TIFA", parties=c("FJ", "US"), signed="2020-10-15", in_force="2020-10-15",
         text=U + "files/agreements/tifa/Final%20Signed%20US-Fiji%20TIFA.pdf", text_dated=True, text_eif=True,
         edit="a3df21bc-2222-437c-ab3d-83d031e3640d",
         notes="Signed for Fiji at Suva on 13 October 2020 and for the United States at Washington on 15 October 2020; "
               "enters into force on the date of its signature by both Parties. Treaties in Force 2026 does not list it."),
    dict(id="GEUS-TIFA", name="Trade and Investment Framework Agreement between the United States of America and Georgia",
         label="U.S.-Georgia TIFA", parties=c("GE", "US"), signed="2007-06-20", in_force="2007-06-20", tif=164,
         text=U + "U.S-Georgia%20TIFA%20%28English%29.pdf", text_dated=False, text_eif=True,
         edit="d9c22487-6a00-4c4d-ab39-9804138e05c7", notes="Signed at Washington; enters into force on signature."),
    dict(id="GHUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Republic of Ghana concerning the Development of Trade and Investment Relations",
         label="U.S.-Ghana TIFA", parties=c("GH", "US"), signed="1999-02-26", in_force="1999-02-26",
         text=U + "uploads/agreements/tifa/asset_upload_file126_7726.pdf", text_dated=True, text_eif=True,
         edit="a94b1d42-247c-4dda-9e1d-95c2a32c4c10",
         notes="Signed at Washington; effective on signature. Treaties in Force 2026 does not list it.",
         extra=[("signed", "Office of the United States Trade Representative, Africa TIFAs index (archive)",
                 USTR_AFRICA_INDEX)]),
    dict(id="GTUS-TIFA", name="Agreement concerning a United States-Guatemala Council on Trade and Investment",
         label="United States-Guatemala Council on Trade and Investment", parties=c("GT", "US"),
         signed="1991-10-02", in_force="1991-10-02", tif=185,
         notes="Signed at Washington. USTR's current TIFA list does not include it."),
    dict(id="HNUS-TIFA", name="Agreement concerning a United States-Honduras Council on Trade and Investment",
         label="United States-Honduras Council on Trade and Investment", parties=c("HN", "US"),
         signed="1990-11-01", in_force="1990-11-01", tif=195,
         notes="Signed at Washington. USTR's current TIFA list does not include it."),
    dict(id="IDUS-TIFA", name="Memorandum of Understanding between the Government of the United States of America and "
         "the Government of the Republic of Indonesia concerning the Establishment of the Council on Trade and Investment",
         label="U.S.-Indonesia TIFA", parties=c("ID", "US"), signed="1996-07-16", in_force="1996-07-16", tif=209,
         text=U + "uploads/agreements/tifa/asset_upload_file10_10199.pdf", text_dated=True, text_eif=True,
         notes="Signed at Christchurch; enters into force on signature. Separate from the 2026 Agreement on Reciprocal "
               "Trade (IDUS-ART)."),
    dict(id="IQUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Iraq concerning the Development of Trade and Investment Relations",
         label="U.S.-Iraq TIFA", parties=c("IQ", "US"), signed="2005-07-11", in_force="2013-05-31", tif=215,
         text=U + "uploads/agreements/tifa/asset_upload_file836_13617.pdf", text_dated=False, text_eif=False,
         edit="6de6e9f3-f3fc-481e-ad26-e05f77f83d65",
         notes="Signed at Amman; enters into force when Iraq notifies the United States that its legal requirements "
               "are met. USTR posts only the Arabic text."),
    dict(id="JOUS-TIFA", name="Agreement concerning the Development of Trade and Investment Relations between the United "
         "States of America and Jordan",
         label="United States-Jordan Agreement concerning the Development of Trade and Investment Relations",
         parties=c("JO", "US"), signed="1999-03-15", in_force="1999-03-15", tif=244,
         notes="Signed at Washington. Predates the 2000 free trade agreement (USJO); Treaties in Force 2026 still lists "
               "it."),
    dict(id="KHUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Royal Government of Cambodia",
         label="U.S.-Cambodia TIFA", parties=c("KH", "US"), signed="2006-07-14", in_force="2006-07-14", tif=66,
         text=U + "uploads/agreements/tifa/asset_upload_file152_9651.pdf", text_dated=True, text_eif=False,
         edit="cfd0be90-76a1-4918-8838-9b8c18f78645", notes="Signed at Washington."),
    dict(id="KWUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "State of Kuwait concerning the Development of Trade and Investment Relations",
         label="U.S.-Kuwait TIFA", parties=c("KW", "US"), signed="2004-02-06", in_force="2004-08-07", tif=259,
         text=U + "uploads/agreements/tifa/asset_upload_file909_7733.pdf", text_dated=True, text_eif=False,
         edit="f917181c-3694-4d76-828f-b5e65b865189",
         notes="Signed at Washington; effective on the date the Parties exchange notes that their domestic procedures "
               "are complete."),
    dict(id="LAUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Lao People's Democratic Republic",
         label="U.S.-Laos TIFA", parties=c("LA", "US"), signed="2016-02-17", in_force="2016-02-17",
         text=U + "US-Laos-TIFA-signed.pdf", text_dated=True, text_eif=True,
         edit="ffd472ee-719b-450d-b405-b718592e1eef",
         notes="Signed at San Francisco; enters into force upon signature. Treaties in Force 2026 does not list it."),
    dict(id="LKUS-TIFA", name="Trade and Investment Framework Agreement between the United States of America and the "
         "Democratic Socialist Republic of Sri Lanka",
         label="U.S.-Sri Lanka TIFA", parties=c("LK", "US"), signed="2002-07-25", in_force="2002-07-25",
         text=U + "US-Sri%20Lanka%20TIFA.pdf", text_dated=True, text_eif=True,
         edit="0f0a6c11-ba38-4565-a14d-b0c0334e2cef",
         notes="Signed at Washington; effective from the date of signature by both Parties. Treaties in Force 2026 does "
               "not list it. EDIT gives 2022-07-25 as the date of signature and entry into force."),
    dict(id="LRUS-TIFA", name="Trade and Investment Framework Agreement between the United States of America and the "
         "Republic of Liberia",
         label="U.S.-Liberia TIFA", parties=c("LR", "US"), signed="2007-02-15", in_force="2007-02-15", tif=269,
         text=U + "uploads/agreements/tifa/asset_upload_file278_10544.pdf", text_dated=True, text_eif=True,
         edit="87c77f7c-d4a8-4a98-ba46-3a43203986ee", notes="Signed at Washington; enters into force on signature."),
    dict(id="LTUS-TIFA", name="Agreement concerning the Development of Trade and Investment Relations between the United "
         "States of America and Lithuania",
         label="United States-Lithuania Agreement concerning the Development of Trade and Investment Relations",
         parties=c("LT", "US"), signed="1992-07-06", in_force="1992-11-12", tif=273,
         notes="Signed at Washington. Treaties in Force 2026 lists it; USTR's current TIFA list does not."),
    dict(id="LYUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the State of Libya and "
         "the Government of the United States of America",
         label="U.S.-Libya TIFA", parties=c("LY", "US"), signed="2013-12-18", in_force="2019-11-05", tif=270,
         edit="561258d2-0fd3-464c-9648-aaff845fd52e",
         notes="Signed at Tripoli; enters into force when the Parties have notified each other that their legal "
               "requirements are met. The English and Arabic texts on USTR's TIFA page are of an earlier agreement, "
               "signed at Tripoli on 20 May 2010 with the Great Socialist People's Libyan Arab Jamahiriya, which "
               "Treaties in Force 2026 does not list."),
    dict(id="MAUS-TIFA", name="Agreement concerning the Development of Trade and Investment Relations between the United "
         "States of America and Morocco",
         label="United States-Morocco Agreement concerning the Development of Trade and Investment Relations",
         parties=c("MA", "US"), signed="1995-03-16", in_force="1995-03-16", tif=308,
         notes="Signed at Washington. Predates the 2004 free trade agreement (USMA); Treaties in Force 2026 still lists "
               "it."),
    dict(id="MNUS-TIFA", name="Agreement between the Government of the United States of America and the Government of "
         "Mongolia concerning the Development of Trade and Investment Relations",
         label="U.S.-Mongolia TIFA", parties=c("MN", "US"), signed="2004-07-15", in_force="2004-07-15", tif=304,
         text=U + "US-Mongolia%20TIFA%20English%20Version.pdf", text_dated=False, text_eif=True,
         edit="c6d9663a-b089-446a-9880-a3820356625f", notes="Signed at Washington; enters into force on signature."),
    dict(id="MUUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Mauritius",
         label="U.S.-Mauritius TIFA", parties=c("MU", "US"), signed="2006-09-18", in_force="2006-09-18",
         text=U + "uploads/agreements/tifa/asset_upload_file789_9937.pdf", text_dated=True, text_eif=True,
         edit="39bf7e3c-14c8-4c19-ab64-e011ed5bc0ef",
         notes="Signed at Washington; enters into force on signature. Treaties in Force 2026 does not list it."),
    dict(id="MVUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of Maldives",
         label="U.S.-Maldives TIFA", parties=c("MV", "US"), signed="2009-10-17", in_force="2009-10-17", tif=281,
         text=U + "US-Maldives%20TIFA.pdf", text_dated=True, text_eif=True,
         edit="ace1dfcf-17f0-43d4-96c0-53f595f9032c", notes="Signed at Male; enters into force on signature."),
    dict(id="MXUS-TIFA", name="Understanding between the United States of America and Mexico concerning a Framework of "
         "Principles and Procedures for Consultations regarding Trade and Investment Relations",
         label="United States-Mexico Framework Understanding on Trade and Investment",
         parties=c("MX", "US"), signed="1987-11-06", in_force="1987-11-06", tif=299,
         notes="Signed at Mexico, with an agenda. Predates NAFTA and USMCA; Treaties in Force 2026 still lists it."),
    dict(id="MYUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of Malaysia",
         label="U.S.-Malaysia TIFA", parties=c("MY", "US"), signed="2004-05-10", in_force="2004-05-10", tif=280,
         text=U + "US-Malaysia%20TIFA.pdf", text_dated=False, text_eif=False,
         edit="7f8f7107-698b-4066-bbed-d6a5f0e380c3",
         notes="Signed at Washington. Separate from the 2025 Agreement on Reciprocal Trade (MYUS-ART)."),
    dict(id="MZUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Mozambique concerning the Development of Trade and Investment "
         "Relations",
         label="U.S.-Mozambique TIFA", parties=c("MZ", "US"), signed="2005-06-21", in_force="2005-06-21", tif=310,
         text=U + "uploads/agreements/tifa/asset_upload_file304_7806.pdf", text_dated=True, text_eif=True,
         edit="16d97663-ce3b-48af-9d92-4df9b9912a5d", notes="Signed at Washington; enters into force on signature."),
    dict(id="NGUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Federal Republic of Nigeria concerning the Development of Trade and Investment Relations",
         label="U.S.-Nigeria TIFA", parties=c("NG", "US"), signed="2000-02-16", in_force="2000-02-16", tif=328,
         text=U + "uploads/agreements/tifa/asset_upload_file172_7727.pdf", text_dated=True, text_eif=True,
         edit="06895db9-b640-480a-b1c8-9da42e0a5303", notes="Signed at Washington; effective on signature."),
    dict(id="NPUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of Nepal",
         label="U.S.-Nepal TIFA", parties=c("NP", "US"), signed="2011-04-15", in_force="2011-04-15",
         text=U + "uploads/Countries%20Regions/africa/agreements/tifa/"
                  "Final%20Signed%20TIFA%20April%2015%2C%202011%20US%20version.pdf", text_dated=True, text_eif=True,
         edit="17866449-c928-41dc-9b18-3ef3ccd1f069",
         notes="Signed at Washington; enters into force on signature. Treaties in Force 2026 does not list it."),
    dict(id="NZUS-TIFA", name="Agreement between the Government of the United States of America and the Government of "
         "New Zealand concerning a Framework of Principles and Procedures for Consultations regarding Trade and "
         "Investment Relations",
         label="U.S.-New Zealand TIFA", parties=c("NZ", "US"), signed="1992-10-02", in_force="1992-10-02", tif=321,
         text=U + "US-New%20Zealand%20TIFA.pdf", text_dated=False, text_eif=True,
         edit="45183ac6-6158-4718-bf85-a9da774c4521", notes="Signed at Washington; enters into force on signature."),
    dict(id="OMUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Sultanate of Oman concerning the Development of Trade and Investment Relations",
         label="U.S.-Oman TIFA", parties=c("OM", "US"), signed="2004-07-07", in_force="2004-07-07", tif=337,
         text=U + "US-Oman%20TIFA.pdf", text_dated=True, text_eif=True,
         notes="Signed at Washington; enters into force on signature. Predates the 2006 free trade agreement (USOM)."),
    dict(id="PAUS-TIFA", name="Agreement concerning a United States-Panama Council on Trade and Investment",
         label="United States-Panama Council on Trade and Investment", parties=c("PA", "US"),
         signed="1991-06-27", in_force="1991-06-27", tif=348,
         notes="Signed at Washington. Predates the 2007 trade promotion agreement (USPA); Treaties in Force 2026 still "
               "lists it."),
    dict(id="PHUS-TIFA", name="Understanding between the Government of the United States of America and the Government of "
         "the Republic of the Philippines concerning a Framework of Principles and Procedures and the Establishment of a "
         "Consultative Mechanism for the Expansion of Trade and Investment Flows between the Two Countries",
         label="U.S.-Philippines TIFA", parties=c("PH", "US"), signed="1989-11-09", in_force="1989-11-09", tif=363,
         text=U + "US-Philippines%20TIFA.pdf", text_dated=True, text_eif=False,
         notes="Signed at Washington. USTR also posts a Protocol concerning Customs Administration and Trade "
               "Facilitation, which enters into force on signature; the posted copy carries no date of signature, so "
               "it is not recorded as an instrument."),
    dict(id="PYUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Paraguay",
         label="U.S.-Paraguay TIFA", parties=c("PY", "US"), signed="2017-01-13", in_force="2021-03-17", tif=352,
         text=U + "files/agreements/tifa/US-PY%20TIFAeng.pdf", text_dated=True, text_eif=False,
         edit="ee783492-b07e-4708-b65b-5d3989145329",
         notes="Signed at Washington; enters into force on the date of the last notification that the Parties' "
               "internal procedures are complete. On entry into force it supersedes the earlier agreement signed at "
               "Washington on 26 September 2003, which has no record here."),
    dict(id="RWUS-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Republic of Rwanda concerning the Development of Trade and Investment "
         "Relations",
         label="U.S.-Rwanda TIFA", parties=c("RW", "US"), signed="2006-06-07", in_force="2006-06-07", tif=381,
         text=U + "US-Rwanda%20TIFA.pdf", text_dated=True, text_eif=True,
         edit="39d9876f-6eb6-4f8f-992e-cc3a690c2591", notes="Signed at Washington; enters into force on signature."),
    dict(id="SACUUS-TIFA", name="Cooperative Agreement between the United States of America and the Southern African "
         "Customs Union to Foster Trade, Investment and Development",
         label="U.S.-SACU Trade, Investment and Development Cooperative Agreement (TIDCA)",
         parties=c("BW", "LS", "NA", "ZA", "SZ", "US"), signed="2008-07-16", in_force="2008-07-16", tif=548,
         edit="cb653ab6-b8a6-44c8-959a-1d45f083350b",
         notes="Signed at Washington by the governments of the five SACU Member States and the United States. USTR "
               "names it the Trade, Investment, and Development Cooperative Agreement (TIDCA) on its TIFA page but "
               "links no text; Treaties in Force lists it among the multilateral trade and investment agreements."),
    dict(id="SAUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Kingdom of Saudi Arabia concerning the Development of Trade and Investment Relations",
         label="U.S.-Saudi Arabia TIFA", parties=c("SA", "US"), signed="2003-07-31", in_force="2003-07-31", tif=390,
         text=U + "uploads/agreements/tifa/asset_upload_file304_7740.pdf", text_dated=True, text_eif=True,
         edit="0dd2be90-b6ac-4ffe-a694-cef56494116d",
         notes="Signed at Washington; enters into force on signature. EDIT gives 2024-03-15 as the date of signature."),
    dict(id="SGUS-TIFA", name="Agreement between the United States of America and Singapore concerning a Framework of "
         "Principles and Procedures for Consultations regarding Trade and Investment Relations",
         label="United States-Singapore Framework Agreement on Trade and Investment",
         parties=c("SG", "US"), signed="1991-10-11", in_force="1991-10-11", tif=399,
         notes="Signed at Singapore. Predates the 2003 free trade agreement (USSG); Treaties in Force 2026 still lists "
               "it."),
    dict(id="SRUS-TIFA", name="Agreement concerning a United States-Suriname Council on Trade and Investment",
         label="United States-Suriname Council on Trade and Investment", parties=c("SR", "US"),
         signed="1993-10-08", in_force="1993-10-08", tif=417, notes="Signed at Washington, with an annex."),
    dict(id="THUS-TIFA", name="Trade and Investment Framework Agreement between the United States of America and the "
         "Kingdom of Thailand",
         label="U.S.-Thailand TIFA", parties=c("TH", "US"), signed="2002-10-23", in_force="2002-10-23", tif=429,
         text=U + "US--Thailand%20TIFA.pdf", text_dated=False, text_eif=False,
         edit="e88cfde0-2780-4bd9-b6a2-6c0a58fed155",
         notes="Signed at Los Cabos. The copy USTR posts leaves the place and date of signature blank. Separate from "
               "the 2004 FTA negotiations (THUS) and the 2025 framework (THUS-FRAMEWORK)."),
    dict(id="TNUS-TIFA", name="Agreement between the Government of the United States of America and the Government of "
         "Tunisia concerning the Development of Trade and Investment Relations",
         label="U.S.-Tunisia TIFA", parties=c("TN", "US"), signed="2002-10-02", in_force="2002-10-02",
         text=U + "uploads/agreements/tifa/asset_upload_file459_9936.pdf", text_dated=True, text_eif=True,
         notes="Signed at Washington; enters into force on signature. Treaties in Force 2026 does not list it."),
    dict(id="AEUS-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "United Arab Emirates concerning the Development of Trade and Investment Relations",
         label="U.S.-United Arab Emirates TIFA", parties=c("AE", "US"), signed="2004-03-15", in_force="2006-11-01",
         tif=453, text=U + "uploads/agreements/tifa/asset_upload_file305_7741.pdf", text_dated=True, text_eif=False,
         edit="7d416795-8c02-40dd-98d5-ef4ecd0f629b",
         notes="Signed at Washington; enters into force when the Parties exchange notes that their domestic "
               "procedures are complete."),
    dict(id="UEMOAUS-TIFA", name="Agreement between the Government of the United States of America and the West African "
         "Economic and Monetary Union concerning the Development of Trade and Investment Relations",
         label="U.S.-West African Economic and Monetary Union (WAEMU) TIFA", parties=b("UEMOA"),
         signed="2002-04-24", in_force="2002-04-24",
         text=U + "uploads/agreements/tifa/asset_upload_file935_7730.pdf", text_dated=False, text_eif=True,
         edit="49d7a8a0-6f22-4579-a244-18371ca2bab8",
         notes="Signed at Washington; enters into force on signature. WAEMU signs as one Party. The copy USTR posts "
               "leaves the place and date of signature blank; USTR's press release of 24 April 2002 gives the date. "
               "Treaties in Force 2026 does not list it.",
         extra=[("signed", "Office of the United States Trade Representative, press release of 24 April 2002",
                 WAEMU_PRESS),
                ("signed", "Office of the United States Trade Representative, Africa TIFAs index (archive)",
                 USTR_AFRICA_INDEX)]),
    dict(id="USUY-TIFA", name="Trade and Investment Framework Agreement between the United States of America and the "
         "Oriental Republic of Uruguay",
         label="U.S.-Uruguay TIFA", parties=c("UY", "US"), signed="2007-01-25", in_force="2007-01-25", tif=468,
         text=U + "uploads/agreements/tifa/asset_upload_file566_15163.pdf", text_dated=True, text_eif=True,
         edit="4ba4441d-5711-4e20-b5a2-28884e4fb4b1", notes="Signed at Montevideo; enters into force on signature.",
         instruments=[
             dict(id="protocol-environment-2008", kind="supplementary_agreement",
                  name="Protocol to the 2007 Trade and Investment Framework Agreement between the United States of "
                       "America and the Oriental Republic of Uruguay concerning Trade and Environment Public "
                       "Participation",
                  status="in_force", signed="2008-10-02", in_force="2008-10-02",
                  notes="Signed at Washington; enters into force on signature.",
                  url=U + "uploads/agreements/tifa/asset_upload_file665_15166.pdf"),
             dict(id="protocol-trade-facilitation-2008", kind="supplementary_agreement",
                  name="Protocol to the 2007 Trade and Investment Framework Agreement between the United States of "
                       "America and the Oriental Republic of Uruguay concerning Trade Facilitation",
                  status="in_force", signed="2008-10-02", in_force="2008-10-02",
                  notes="Signed at Washington; enters into force on signature.",
                  url=U + "uploads/agreements/tifa/asset_upload_file190_15165.pdf"),
         ]),
    dict(id="USVE-TIFA", name="Agreement concerning a United States-Venezuela Council on Trade and Investment",
         label="United States-Venezuela Council on Trade and Investment", parties=c("VE", "US"),
         signed="1991-04-08", in_force="1991-04-08", tif=473,
         notes="Signed at Washington, with an annex. USTR's current TIFA list does not include it."),
    dict(id="USVN-TIFA", name="Trade and Investment Framework Agreement between the Government of the United States of "
         "America and the Government of the Socialist Republic of Vietnam",
         label="U.S.-Vietnam TIFA", parties=c("VN", "US"), signed="2007-06-21", in_force="2007-06-21", tif=476,
         text=U + "uploads/agreements/tifa/asset_upload_file81_12935.pdf", text_dated=False, text_eif=True,
         edit="2866ab0e-434e-4132-8269-cab747fb8fc2",
         notes="Signed at Washington; enters into force on signature. Separate from the 2025 framework "
               "(USVN-FRAMEWORK)."),
    dict(id="USYE-TIFA", name="Agreement between the Government of the United States of America and the Government of the "
         "Republic of Yemen concerning the Development of Trade and Investment Relations",
         label="U.S.-Yemen TIFA", parties=c("YE", "US"), signed="2004-02-06", in_force="2004-02-06", tif=479,
         text=U + "uploads/agreements/tifa/asset_upload_file638_7743.pdf", text_dated=True, text_eif=True,
         edit="c0eca61d-3418-451f-a886-733b1a2971f6", notes="Signed at Washington; enters into force on signature."),
    dict(id="USZA-TIFA", name="Agreement concerning the Development of Trade and Investment between the Government of the "
         "Republic of South Africa and the Government of the United States of America",
         label="U.S.-South Africa TIFA", parties=c("ZA", "US"), signed="1999-02-18", in_force="1999-02-18",
         text=U + "uploads/agreements/tifa/asset_upload_file224_7728.pdf", text_dated=True, text_eif=True,
         notes="Signed at Cape Town; enters into force on signature. Treaties in Force 2026 lists the agreement with "
               "the date of the 2012 amending agreement (signed and in force at Washington on 18 June 2012).",
         extra=[("signed", "Office of the United States Trade Representative, Africa TIFAs index (archive)",
                 USTR_AFRICA_INDEX)],
         instruments=[
             dict(id="amendment-2012", kind="amending_protocol",
                  name="Trade and Investment Framework Agreement of 18 June 2012 amending the 1999 Agreement "
                       "concerning the Development of Trade and Investment",
                  status="in_force", signed="2012-06-18", in_force="2012-06-18",
                  notes="Signed at Washington. USTR's release says it amends the TIFA signed in 1999; Treaties in Force "
                        "2026 gives signature and entry into force on 18 June 2012.",
                  url=ZA_PRESS, source="Office of the United States Trade Representative, press release of 18 June 2012",
                  tif=406),
         ]),
]


def prov(field, source, url):
    return {"field": field, "source": source, "url": url, "retrieved_at": TODAY}


def build(r: dict) -> dict:
    tif = TIF_URL.format(page=r["tif"]) if r.get("tif") else None
    text = r.get("text")
    links = []
    if text:
        links.append({"url": text, "type": "treaty_text"})
    if r.get("edit"):
        links.append({"url": EDIT_URL.format(uuid=r["edit"]), "type": "treaty_text"})
    on_ustr_list = text is not None or r["id"] in {"SACUUS-TIFA", "LYUS-TIFA"}
    if on_ustr_list:
        links.append({"url": USTR_LIST_URL, "type": "website"})
    p = []
    if tif:
        for f in ("parties", "signed", "in_force", "status"):
            p.append(prov(f, TIF_SOURCE, tif))
    if text:
        p.append(prov("name", USTR_TEXT_SOURCE, text))
        if not tif:
            p.append(prov("parties", USTR_TEXT_SOURCE, text))
        if r.get("text_dated"):
            p.append(prov("signed", USTR_TEXT_SOURCE, text))
        if r.get("text_eif"):
            p.append(prov("in_force", USTR_TEXT_SOURCE, text))
    elif tif:
        p.append(prov("name", TIF_SOURCE, tif))
    if r.get("edit") and not text:
        p.append(prov("name", EDIT_SOURCE, EDIT_URL.format(uuid=r["edit"])))
    for field, source, url in r.get("extra", []):
        p.append(prov(field, source, url))
    if on_ustr_list:
        p.append(prov("status", USTR_LIST_SOURCE, USTR_LIST_URL))
    if r.get("edit") and "EDIT gives" in r.get("notes", ""):
        p.append(prov("notes", EDIT_SOURCE, EDIT_URL.format(uuid=r["edit"])))
    # Every record needs an official source for each date it sets.
    fields = {x["field"] for x in p if x["source"] != EDIT_SOURCE}
    for f in ("parties", "signed", "in_force", "status"):
        assert f in fields, (r["id"], f)
    record = {
        "id": r["id"],
        "name": r["name"],
        "other_names": [{"lang": "en", "name": r["label"]}],
        "agreement_type": "framework",
        "status": "in_force",
        "signed": r["signed"],
        "in_force": r["in_force"],
        "parties": [{"id": i, "type": t} for i, t in r["parties"]],
        "links": links,
        "notes": r["notes"],
        "verification": "official",
        "last_verified": TODAY,
        "provenance": p,
    }
    if r.get("instruments"):
        items = []
        for ins in r["instruments"]:
            ip = [prov("signed", ins.get("source", USTR_TEXT_SOURCE), ins["url"]),
                  prov("in_force", ins.get("source", USTR_TEXT_SOURCE), ins["url"])]
            if ins.get("tif"):
                ip.append(prov("in_force", TIF_SOURCE, TIF_URL.format(page=ins["tif"])))
            items.append({k: ins[k] for k in ("id", "kind", "name", "status", "signed", "in_force", "notes")}
                         | {"provenance": ip})
        record["instruments"] = items
    return {k: record[k] for k in FIELD_ORDER if k in record}


def dump(record: dict) -> str:
    return yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)


def main(argv: list[str]) -> int:
    write = "--write" in argv
    out = ROOT / "data" / "trade_agreements"
    ids = [r["id"] for r in R]
    assert len(ids) == len(set(ids))
    for r in R:
        path = out / f"{r['id']}.yaml"
        if path.exists():
            print(f"exists, skipped: {r['id']}")
            continue
        text = dump(build(r))
        if write:
            path.write_text(text, encoding="utf-8")
        print(f"{'wrote' if write else 'would write'} {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
