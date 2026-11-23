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
  record gives. ``datenoio/internacia-db#235`` adds 71 historical ALADI agreements with their
  successors, among them 33 that DESTA lists (``IN_PR_235``); the four records here are the
  historical agreements DESTA lists that #235 does not have, each ended on a fixed date. A
  successor that is only in an open pull request cannot be ``superseded_by`` yet; such a record
  would be ``terminated`` until it merges (``PENDING_SUCCESSORS``, empty now).
- Party governments: the UAE Ministry of Economy and Tourism and the Emirates News Agency
  (WAM), the Israeli Ministry of Foreign Affairs, the Kenyan National Assembly, the Serbian
  government and Ministry of Foreign Affairs, Jordan's export portal (Ministry of Industry,
  Trade and Supply), the Turkish Ministry of Trade, the Swiss State Secretariat for Economic
  Affairs, Monaco's official legal database (Legimonaco) and Latvia's official legal portal.
- The WTO: trade policy reviews of Malawi (2002, 2024), Mozambique (2017) and SACU (2009,
  2015), with the Zimbabwe Revenue Authority and Malawi's Ministry of Trade, for four southern
  African bilaterals; and trade policy reviews of Egypt (1999, 2005), Morocco (2003, 2016) and
  Tunisia (2016) for nine Arab bilaterals. The Egypt agreements are in force as of the 2005
  review, the latest that lists them.

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
DOL = "https://docsonline.wto.org/dol2fe/Pages/SS/directdoc.aspx?filename=Q%3A%2FWT%2FTPR%2F{}.pdf"
EG1999 = "WTO, Trade Policy Review of Egypt, WT/TPR/S/55 (1999), Chapter II"
EG2005 = "WTO, Trade Policy Review of Egypt, WT/TPR/S/150 (2005), Chapter II"
TN2016 = "WTO, Trade Policy Review of Tunisia, WT/TPR/S/341 (2016), Table 2.2"
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
    # The other 33 historical ALADI agreements DESTA lists are records of datenoio/internacia-db#235,
    # which is authoritative for them (IN_PR_235); these four are not in it.
    "ARCR-1983": aladi(37, "A25TM", 2, ["AR", "CR"], "504124eec8022bd6032578ed006a26d5", "1983-08-31",
                       "1983-08-31", "terminated", "1994-12-31",
                       in_force_note="In force from signature (Article 19).",
                       note="Article 19, as amended by the First Additional Protocol, set its term to 31 December "
                            "1994."),
    "ARSV-1983": aladi(42, "A25TM", 3, ["AR", "SV"], "01aeb2756bb5ee00032578ed006a7522", "1983-08-27",
                       "1983-10-27", "terminated", "1994-12-31",
                       note="Article 20, as amended by the First Additional Protocol, set its term to 31 December "
                            "1994."),
    "ARUY-1982": aladi(699, "ACE", 1, ["AR", "UY"], "1d5a040ec3cf305403256fbf006cc88d", "1982-12-20",
                       "1985-11-27", "terminated", "2003-05-01",
                       note="Expired on 1 May 2003 under Article 1 of its 28th Additional Protocol; ACE 57 (ARUY) "
                            "took effect the same day."),
    "MXNI-1985": aladi(610, "A25TM", 13, ["MX", "NI"], "2b6fd5c1956efdbb03256fbf006c1dbd", "1985-04-08",
                       "1986-08-12", "terminated", "1998-06-30",
                       note="The Fourth Additional Protocol extended it for the last time to 30 June 1998. The "
                            "Mexico - Nicaragua FTA (MXNI) took effect on 1 July 1998."),

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

    # --- Arab bilaterals: WTO trade policy reviews of Egypt, Morocco and Tunisia ----------------
    "EGSY": gov(413, [
        ("in_force", EG2005, DOL.format("S150-2")),
        ("status", EG2005, DOL.format("S150-2")),
    ], name="Trade Agreement between Egypt and Syria", agreement_type="pta", status="in_force",
        in_force="1991", parties=["EG", "SY"],
        notes="Egypt's 2005 trade policy review lists it among Egypt's bilateral trade agreements with Arab "
              "countries, in force since 1991; the authorities expected GAFTA to absorb its preferences."),
    "EGLY": gov(408, [
        ("in_force", EG2005, DOL.format("S150-2")),
        ("status", EG2005, DOL.format("S150-2")),
    ], name="Trade Agreement between Egypt and Libya", agreement_type="pta", status="in_force",
        in_force="1991", parties=["EG", "LY"],
        notes="Egypt's 2005 trade policy review lists it among Egypt's bilateral trade agreements with Arab "
              "countries, in force since 1991; the authorities expected GAFTA to absorb its preferences."),
    "EGLB": gov(407, [
        ("in_force", EG2005, DOL.format("S150-2")),
        ("status", EG2005, DOL.format("S150-2")),
    ], name="Trade Agreement between Egypt and Lebanon", agreement_type="pta", status="in_force",
        in_force="1999", parties=["EG", "LB"],
        notes="Duty-free access for a limited number of products (WTO, 1999). In force since 1999 (WTO, 2005)."),
    "EGIQ": gov(403, [
        ("in_force", EG2005, DOL.format("S150-2")),
        ("status", EG2005, DOL.format("S150-2")),
    ], name="Trade Agreement between Egypt and Iraq", agreement_type="pta", status="in_force",
        in_force="2001", parties=["EG", "IQ"],
        notes="Egypt's 2005 trade policy review lists it among Egypt's bilateral trade agreements with Arab "
              "countries, in force since 2001."),
    "EGMA": gov(410, [
        ("signed", EG1999, DOL.format("S55-2")),
        ("in_force", "WTO, Trade Policy Review of Morocco, WT/TPR/S/116 (2003), Chapter II",
         DOL.format("S116-2")),
        ("status", EG2005, DOL.format("S150-2")),
    ], name="Free Trade Agreement between Egypt and Morocco", agreement_type="fta", status="in_force",
        signed="1998", in_force="1999", parties=["EG", "MA"],
        notes="Creates a free trade area over 12 years for manufactures; agriculture was left for later. The four "
              "parties also signed the Agadir Agreement in 2004, in force on 27 March 2007; the WTO's 2005 "
              "review of Egypt says trade with Morocco was still governed by this agreement."),
    "EGTN": gov(414, [
        ("signed", EG1999, DOL.format("S55-2")),
        ("in_force", EG2005, DOL.format("S150-2")),
        ("status", TN2016, TPR + "s341_e.pdf"),
    ], name="Free Trade Agreement between Egypt and Tunisia", agreement_type="fta", status="in_force",
        signed="1997-12", in_force="1999", parties=["EG", "TN"],
        notes="Phases out duties: about 100 goods at once, tariffs below 20% over five years and the rest by 2007 "
              "(WTO, 1999). Egypt's 2005 review gives entry into force in 1999; Tunisia's 2016 review (Table "
              "2.2) gives 1998 and describes the preferences as partial."),
    "SYTN": gov(674, [
        ("in_force", TN2016, TPR + "s341_e.pdf"),
        ("status", TN2016, TPR + "s341_e.pdf"),
    ], name="Trade Agreement between Syria and Tunisia", agreement_type="pta", status="in_force",
        in_force="2005-03-10", parties=["SY", "TN"],
        notes="Partial tariff preferences that do not cover all trade in goods; not notified to the WTO (Tunisia's "
              "2016 trade policy review, which also dates the agreement 2003)."),
    "LYTN": gov(575, [
        ("in_force", TN2016, TPR + "s341_e.pdf"),
        ("status", TN2016, TPR + "s341_e.pdf"),
    ], name="Trade Agreement between Libya and Tunisia", agreement_type="pta", status="in_force",
        in_force="2002-02-19", parties=["LY", "TN"],
        notes="Partial tariff preferences that do not cover all trade in goods; not notified to the WTO (Tunisia's "
              "2016 trade policy review, which also dates the agreement 2001)."),
    "MATN": gov(625, [
        ("in_force", TN2016, TPR + "s341_e.pdf"),
        ("status", "WTO, Trade Policy Review of Morocco, WT/TPR/S/329 (2016), Table 2.2", TPR + "s329_e.pdf"),
    ], name="Free Trade Agreement between Morocco and Tunisia", agreement_type="fta", status="in_force",
        in_force="1999-03-16", parties=["MA", "TN"],
        notes="Lists of goods traded freely, at a single 17.5% duty or with tariffs dismantled to zero by "
              "1 January 2008 (WTO, 2003); Tunisia's 2016 review describes the preferences as partial. Both "
              "countries' 2016 reviews give entry into force on 16 March 1999."),
}

# Records whose successor is not in the registry yet (set by ``build``): ``terminated`` for now,
# ``superseded`` with ``superseded_by`` once the successor merges.
PENDING_SUCCESSORS: dict[str, str] = {}

# Successors whose only predecessor is added here (none: #235 sets ``supersedes`` on CLMX, CRMX, CUMX,
# MXUY, BOMX and BRMX with its own ids).
MAIN_SUPERSEDES: dict[str, str] = {}

# DESTA historical ALADI agreements that are records of datenoio/internacia-db#235 (DESTA number ->
# #235 record id). The walk first wrote them here; the duplicates were dropped on 2026-11-23.
IN_PR_235: dict[int, str] = {
    31: "ARBO-ACE19", 32: "ARBR-ACE7", 33: "ARBR-ACE12", 36: "ARCO-ACE11", 38: "ARCU-A25TM4", 39: "ARCU-ACE45",
    46: "ARPE-ACE9", 48: "ARVE-ACE10", 49: "ARVE-ACE20", 118: "BOBR-ACE26", 124: "BOMX-ACE31", 125: "BOPY-ACE29",
    126: "BOUY-ACE15", 139: "BRCU-ACE43", 712: "BRMX-AAPR9", 142: "BRPE-ACE25", 145: "BRVE-ACE27",
    203: "CLEC-ACE32", 204: "CLEC-ACE65", 211: "CLMX-ACE17", 214: "CLPE-AAPR28", 217: "CLUY-ACE4",
    231: "COCU-A25TM19", 232: "COCU-A25TM33", 236: "COGT-A25TM5", 247: "CRMX-A25TM1", 268: "CUMX-A25TM12",
    467: "GTMX-A25TM10", 417: "MXSV-A25TM15", 615: "MXUY-ACE5", 270: "CUPY-ACE52", 275: "CUUY-ACE44",
    24: "ARCAN-ACE48",
}


def build(rid: str, spec: dict, ids: set[str]) -> dict:
    spec = dict(spec)
    desta = spec.pop("_desta")
    prov = spec.pop("_prov")
    if spec.get("superseded_by") and spec["superseded_by"] not in ids:
        # The successor is in an open pull request (#209 or #226): until it merges the record is
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
