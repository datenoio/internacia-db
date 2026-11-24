"""Apply the Turkish Ministry of Trade country-page walk (2026-11-24) to data/trade_agreements/.

One-off script. The Ministry of Trade publishes, for each country, a table of the agreements "that form the
basis of trade between the two countries" (iki ülke arasında ticaretin altyapısını oluşturan anlaşma ve
protokoller) with the date of signature and of Türkiye's approval in the Resmî Gazete, but not the date of
entry into force. Trade relations agreements from those tables are written here only when an official source
gives their entry into force (or provisional application): the UN Treaty Series, a partner government's
treaty list, the Resmî Gazete decrees fixing the entry-into-force dates of agreements, or the agreement text
published in the Resmî Gazete. Agreements with current EU member states, and those without such a date, are
reported in the pull request and not written. See docs/intblock-sources.md (Türkiye's trade relations row).

Usage: python scripts/oneoff/apply_turkey_trade_relations.py [--dry-run]
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

MOT = "Turkish Ministry of Trade, bilateral agreements with"
UNTS = "United Nations Treaty Collection, United Nations Treaty Series"
RG = "Resmî Gazete (Official Gazette of the Republic of Türkiye)"
LISTED = ("The Turkish Ministry of Trade lists it among the agreements that form the basis of trade between "
          "the two countries.")


def mot(region: str, country: str, slug: str = "iki-ulke-arasinda-ticaretin-altyapisini-olusturan-anlasma-ve-"
                                               "protokoller") -> str:
    return f"https://ticaret.gov.tr/yurtdisi-teskilati/{region}/{country}/ikili-anlasmalar/{slug}"


def unts(objid: str) -> str:
    return f"https://treaties.un.org/Pages/showDetails.aspx?objid={objid}&clang=_en"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in codes]


def tr_name(name: str) -> list[dict]:
    return [{"lang": "tr", "name": name}]


def ministry_prov(country_name: str, url: str, fields=("parties", "signed")) -> list[tuple[str, str, str]]:
    return [(f, f"{MOT} {country_name}", url) for f in fields]


NEW: dict[str, dict] = {
    "ARTR-TRA": {
        "set": {
            "name": "Economic and Trade Cooperation Agreement between the Argentine Republic and the Republic of "
                    "Turkey",
            "other_names": [{"lang": "es", "name": "Convenio de Cooperación Económica y Comercial entre la "
                                                  "República Argentina y la República de Turquía"}]
                           + tr_name("Türkiye Cumhuriyeti Hükümeti ile Arjantin Cumhuriyeti Hükümeti Arasında "
                                     "Ticari ve Ekonomik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "1992-05-09", "in_force": "1994-09-01", "parties": country("AR", "TR"),
            "notes": "Türkiye approved it in the Resmî Gazete No. 21299 of 29 July 1992 and Argentina by Law "
                     "24.326 of 11 May 1994. Argentina's treaty library lists it as in force; it runs for five "
                     "years and is renewed for one-year periods until denounced. " + LISTED,
        },
        "links": [("https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKSmmA==", "website")],
        "prov": ministry_prov("Argentina", mot("guney-amerika", "arjantin")) + [
            ("in_force", "Argentine Ministry of Foreign Affairs, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKSmmA=="),
            ("status", "Argentine Ministry of Foreign Affairs, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKSmmA=="),
            ("notes", "Argentine Ministry of Foreign Affairs, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKSmmA=="),
        ],
    },
    "BJTR-TRA": {
        "set": {
            "name": "Agreement on Economic, Trade and Technical Cooperation between the Government of the Republic "
                    "of Türkiye and the Government of the Republic of Benin",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Benin Cumhuriyeti Hükümeti Arasında "
                                   "Ekonomik, Ticari ve Teknik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "2012-07-09", "in_force": "2017-11-17", "parties": country("BJ", "TR"),
            "notes": "Signed in Ankara. Türkiye approved it in the Resmî Gazete No. 29988 of 23 February 2017; the "
                     "decree of 2018 fixing the entry-into-force dates of agreements (No. 2018/11380) gives "
                     "17 November 2017. " + LISTED,
        },
        "prov": ministry_prov("Benin", mot("afrika", "benin")) + [
            ("in_force", f"{RG}, decree No. 2018/11380 of 17 March 2018 fixing agreements' entry-into-force dates",
             "https://www.resmigazete.gov.tr/eskiler/2018/03/20180317-10.pdf"),
            ("status", f"{RG}, decree No. 2018/11380", "https://www.resmigazete.gov.tr/eskiler/2018/03/20180317-10.pdf"),
            ("notes", f"{RG}, No. 29988 of 23 February 2017",
             "https://www.resmigazete.gov.tr/eskiler/2017/02/20170223-2.pdf"),
        ],
    },
    "BRTR-TRA": {
        "set": {
            "name": "Agreement on trade, economic and industrial cooperation between the Government of the Federative "
                    "Republic of Brazil and the Government of the Republic of Turkey",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Brezilya Federatif Cumhuriyeti Hükümeti "
                                   "Arasında Ticaret, Ekonomik ve Sınai İşbirliği Anlaşması"),
            "status": "in_force", "signed": "1995-04-10", "in_force": "1997-03-19", "parties": country("BR", "TR"),
            "unts_registration": "I-34809",
            "notes": "Signed in Brasília; in force on the exchange of the instruments of ratification (Article IX). "
                     "Türkiye approved it in the Resmî Gazete No. 22296 of 28 May 1995. " + LISTED,
        },
        "links": [(unts("080000028009f74e"), "website")],
        "prov": ministry_prov("Brazil", mot("guney-amerika", "brezilya")) + [
            ("in_force", UNTS, unts("080000028009f74e")), ("unts_registration", UNTS, unts("080000028009f74e")),
            ("status", f"{MOT} Brazil", mot("guney-amerika", "brezilya")),
            ("notes", UNTS, unts("080000028009f74e")),
        ],
    },
    "BYTR-TRA": {
        "set": {
            "name": "Agreement on trade and economic cooperation between the Government of the Republic of Belarus "
                    "and the Government of the Republic of Turkey",
            "other_names": [{"lang": "ru", "name": "Соглашение между Правительством Республики Беларусь и "
                                                  "Правительством Турецкой Республики о торговом и экономическом "
                                                  "сотрудничестве"}] + tr_name("Ticaret ve Ekonomik İşbirliği "
                                                                             "Anlaşması"),
            "status": "in_force", "signed": "1993-09-08", "in_force": "1993-12-01", "parties": country("BY", "TR"),
            "notes": "Türkiye approved it in the Resmî Gazete No. 21754 of 10 November 1993. " + LISTED,
        },
        "prov": ministry_prov("Belarus", mot("avrupa", "belarus")) + [
            ("in_force", "Embassy of Belarus in Türkiye, bilateral agreements",
             "https://turkey.mfa.gov.by/ru/bilateral_relations/agreements/"),
            ("status", f"{MOT} Belarus", mot("avrupa", "belarus")),
            ("notes", f"{MOT} Belarus", mot("avrupa", "belarus")),
        ],
    },
    "CGTR-TRA": {
        "set": {
            "name": "Agreement on trade, economic and technical cooperation between the Government of the Republic "
                    "of Turkey and the Government of the Republic of the Congo",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Kongo Cumhuriyeti Arasında Ticaret, Ekonomik "
                                   "ve Teknik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "2000-09-28", "in_force": "2007-05-11", "parties": country("CG", "TR"),
            "unts_registration": "I-45064",
            "notes": "In force by notification (Article XII). Türkiye's decree No. 2007/12723 (Resmî Gazete No. 26701 "
                     "of 15 November 2007) corrected the entry-into-force date, first fixed as 23 February 2007, to "
                     "11 May 2007, the date the UNTS gives. " + LISTED,
        },
        "links": [(unts("08000002801efc74"), "website")],
        "prov": ministry_prov("the Republic of the Congo", mot("afrika", "kongo")) + [
            ("in_force", UNTS, unts("08000002801efc74")), ("unts_registration", UNTS, unts("08000002801efc74")),
            ("status", f"{MOT} the Republic of the Congo", mot("afrika", "kongo")),
            ("notes", f"{RG}, decree No. 2007/12723", "https://www.resmigazete.gov.tr/eskiler/2007/11/20071115-5.htm"),
        ],
    },
    "DZTR-TRA": {
        "set": {
            "name": "Trade Agreement between the Republic of Turkey and the People's Democratic Republic of Algeria",
            "other_names": tr_name("Ticaret Anlaşması"),
            "status": "in_force", "signed": "1979-05-09", "provisional_application": "1979-05-09",
            "parties": country("DZ", "TR"),
            "notes": "Article 12 applies it provisionally from signature and definitively from the exchange of the "
                     "instruments of approval, whose date was not found. It replaced the trade agreement of "
                     "27 July 1967. Türkiye approved it in the Resmî Gazete No. 16824 of 29 November 1979. " + LISTED,
        },
        "prov": ministry_prov("Algeria", mot("afrika", "cezayir")) + [
            ("provisional_application", f"{RG}, No. 16824 of 29 November 1979 (text of the agreement, Article 12)",
             "https://www.resmigazete.gov.tr/arsiv/16824.pdf"),
            ("status", f"{MOT} Algeria", mot("afrika", "cezayir")),
            ("notes", f"{RG}, No. 16824 of 29 November 1979", "https://www.resmigazete.gov.tr/arsiv/16824.pdf"),
        ],
    },
    "JOTR-TRA": {
        "set": {
            "name": "Agreement on Trade and Economic Cooperation between the Government of the Republic of Türkiye "
                    "and the Government of the Hashemite Kingdom of Jordan",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Haşimi Ürdün Krallığı Hükümeti Arasında "
                                   "Ticari ve Ekonomik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "2019-10-01", "in_force": "2021-09-21", "parties": country("JO", "TR"),
            "notes": "Signed in Ankara after the Türkiye-Jordan free trade agreement (JOTR) ended in 2018. Türkiye "
                     "approved it by Law No. 7300 (Resmî Gazete of 20 March 2021); Presidential Decision No. 5027 "
                     "(Resmî Gazete No. 31705 of 30 December 2021) fixes its entry into force on 21 September 2021. "
                     "The Ministry of Trade's country page still shows it as in internal approval.",
        },
        "prov": ministry_prov("Jordan", mot("orta-dogu-ve-korfez", "urdun")) + [
            ("in_force", f"{RG}, Presidential Decision No. 5027 fixing agreements' entry-into-force dates",
             "https://www.resmigazete.gov.tr/eskiler/2021/12/20211230-9.pdf"),
            ("status", f"{RG}, Presidential Decision No. 5027",
             "https://www.resmigazete.gov.tr/eskiler/2021/12/20211230-9.pdf"),
            ("notes", f"{RG}, Presidential Decision No. 5027",
             "https://www.resmigazete.gov.tr/eskiler/2021/12/20211230-9.pdf"),
        ],
    },
    "KRTR-TRA": {
        "set": {
            "name": "Agreement on trade promotion and economic and technical cooperation between the Government of "
                    "the Republic of Korea and the Government of the Republic of Turkey",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Kore Cumhuriyeti Hükümeti Arasında "
                                   "Ticaretin Geliştirilmesi ve Ekonomik ve Teknik İşbirliği Hakkında Anlaşma"),
            "status": "in_force", "signed": "1977-05-05", "provisional_application": "1977-05-05",
            "in_force": "1977-12-06", "parties": country("KR", "TR"), "unts_registration": "I-49762",
            "notes": "Signed in Ankara; applied provisionally from signature and in force definitively by "
                     "notification (Article X). Türkiye approved it in the Resmî Gazete No. 16131 of 6 December "
                     "1977. The Ministry of Trade's table gives 1997 as the year of signature, a typing error. "
                     + LISTED,
        },
        "links": [(unts("0800000280330f49"), "website")],
        "prov": ministry_prov("the Republic of Korea", mot("dogu-asya", "guney-kore-cumhuriyeti",
                                                        "iki-ulke-arasinda-ticaretin-altyapisini-olusturan-"
                                                        "anlasmalar-ve-protokoller"), ("parties",)) + [
            ("signed", UNTS, unts("0800000280330f49")), ("in_force", UNTS, unts("0800000280330f49")),
            ("provisional_application", UNTS, unts("0800000280330f49")),
            ("unts_registration", UNTS, unts("0800000280330f49")),
            ("status", f"{MOT} the Republic of Korea",
             mot("dogu-asya", "guney-kore-cumhuriyeti",
                 "iki-ulke-arasinda-ticaretin-altyapisini-olusturan-anlasmalar-ve-protokoller")),
            ("notes", UNTS, unts("0800000280330f49")),
        ],
    },
    "KZTR-TRA": {
        "set": {
            "name": "Agreement on trade, economic and technical cooperation between the Government of the Republic "
                    "of Kazakhstan and the Government of the Republic of Turkey",
            "other_names": [{"lang": "ru", "name": "Соглашение о торгово-экономическом и техническом "
                                                  "сотрудничестве"}] + tr_name("Ticaret ve Ekonomik Teknik "
                                                                             "İşbirliği Anlaşması"),
            "status": "in_force", "signed": "1997-09-10", "in_force": "2000-05-22", "parties": country("KZ", "TR"),
            "notes": "Signed in Almaty. Türkiye approved it in the Resmî Gazete No. 23360 of 2 June 1998. " + LISTED,
        },
        "prov": ministry_prov("Kazakhstan", mot("orta-asya", "kazakistan")) + [
            ("in_force", "Embassy of Kazakhstan in Türkiye, treaty base",
             "https://www.gov.kz/memleket/entities/mfa-ankara/press/article/details/149589?lang=ru"),
            ("status", f"{MOT} Kazakhstan", mot("orta-asya", "kazakistan")),
            ("notes", f"{MOT} Kazakhstan", mot("orta-asya", "kazakistan")),
        ],
    },
    "KZTR-TRA-2003": {
        "set": {
            "name": "Agreement on long-term trade and economic cooperation between the Government of the Republic "
                    "of Kazakhstan and the Government of the Republic of Turkey",
            "other_names": [{"lang": "ru", "name": "Соглашение о долгосрочном торгово-экономическом "
                                                  "сотрудничестве"}] + tr_name("Uzun Vadeli Ticari ve Ekonomik "
                                                                             "İşbirliği Anlaşması"),
            "status": "in_force", "signed": "2003-05-22", "in_force": "2003-10-03", "parties": country("KZ", "TR"),
            "notes": "Signed in Ankara. The Ministry of Trade's table gives no Resmî Gazete publication. " + LISTED,
        },
        "prov": ministry_prov("Kazakhstan", mot("orta-asya", "kazakistan")) + [
            ("in_force", "Embassy of Kazakhstan in Türkiye, treaty base",
             "https://www.gov.kz/memleket/entities/mfa-ankara/press/article/details/149589?lang=ru"),
            ("status", f"{MOT} Kazakhstan", mot("orta-asya", "kazakistan")),
            ("notes", f"{MOT} Kazakhstan", mot("orta-asya", "kazakistan")),
        ],
    },
    "MATR-TRA": {
        "set": {
            "name": "Trade Agreement between the Republic of Turkey and the Kingdom of Morocco",
            "other_names": tr_name("Ticaret Anlaşması"),
            "status": "in_force", "signed": "1972-05-16", "provisional_application": "1972-05-16",
            "parties": country("MA", "TR"),
            "notes": "Article 8 applies it provisionally from signature and definitively from the exchange of the "
                     "instruments of ratification, whose date was not found. Türkiye approved it in the Resmî "
                     "Gazete No. 14297 of 5 September 1972. The 2004 free trade agreement (MATR) does not refer to "
                     "it. " + LISTED,
        },
        "prov": ministry_prov("Morocco", mot("afrika", "fas")) + [
            ("provisional_application", f"{RG}, No. 14297 of 5 September 1972 (text of the agreement, Article 8)",
             "https://www.resmigazete.gov.tr/arsiv/14297.pdf"),
            ("status", f"{MOT} Morocco", mot("afrika", "fas")),
            ("notes", f"{RG}, No. 14297 of 5 September 1972", "https://www.resmigazete.gov.tr/arsiv/14297.pdf"),
        ],
    },
    "MDTR-TRA": {
        "set": {
            "name": "Agreement on trade and economic cooperation between the Republic of Moldova and the Republic of "
                    "Turkey",
            "other_names": [{"lang": "ro", "name": "Acord privind cooperarea comercial-economică dintre Republica "
                                                  "Moldova şi Republica Turcia"}] + tr_name("Ticaret ve Ekonomik "
                                                                                          "İşbirliği Anlaşması"),
            "status": "in_force", "signed": "1994-02-14", "in_force": "1994-06-07", "parties": country("MD", "TR"),
            "notes": "Signed in Ankara. Türkiye approved it in the Resmî Gazete No. 21952 of 6 June 1994. Moldova's "
                     "list of bilateral treaties (entry B00246) gives no end date. " + LISTED,
        },
        "prov": ministry_prov("Moldova", mot("avrupa", "moldova")) + [
            ("in_force", "Ministry of Foreign Affairs of the Republic of Moldova, list of bilateral treaties (2026)",
             "https://mfa.gov.md/sites/default/files/lista_tratatelor_bilaterale_2026.pdf"),
            ("status", "Ministry of Foreign Affairs of the Republic of Moldova, list of bilateral treaties (2026)",
             "https://mfa.gov.md/sites/default/files/lista_tratatelor_bilaterale_2026.pdf"),
            ("notes", "Ministry of Foreign Affairs of the Republic of Moldova, list of bilateral treaties (2026)",
             "https://mfa.gov.md/sites/default/files/lista_tratatelor_bilaterale_2026.pdf"),
        ],
    },
    "MXTR-TRA": {
        "set": {
            "name": "Agreement on trade and economic cooperation between the Government of the United Mexican "
                    "States and the Government of the Republic of Turkey",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ile Meksika Birleşik Devletleri Hükümeti "
                                   "Arasında Ticaret ve Ekonomik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "1998-09-28", "in_force": "2001-02-02", "parties": country("MX", "TR"),
            "unts_registration": "I-37766",
            "notes": "In force on the exchange of the instruments of ratification (Article VII). Türkiye approved it "
                     "in the Resmî Gazete No. 23559 of 20 December 1998. " + LISTED,
        },
        "links": [(unts("0800000280087c1f"), "website")],
        "prov": ministry_prov("Mexico", mot("orta-amerika", "meksika")) + [
            ("in_force", UNTS, unts("0800000280087c1f")), ("unts_registration", UNTS, unts("0800000280087c1f")),
            ("status", f"{MOT} Mexico", mot("orta-amerika", "meksika")),
            ("notes", UNTS, unts("0800000280087c1f")),
        ],
    },
    "NOTR-TRA": {
        "set": {
            "name": "Commercial Agreement between Norway and Turkey",
            "other_names": tr_name("Ticaret ve Ödeme Anlaşması"),
            "status": "in_force", "signed": "1949-02-24", "in_force": "1949-03-07", "parties": country("NO", "TR"),
            "unts_registration": "I-433",
            "notes": "Signed in Ankara together with a payments agreement (UNTS I-453). The Ministry of Trade's "
                     "table dates it 24 January 1949 and records Türkiye's approval in the Resmî Gazete No. 7391 of "
                     "28 December 1949. Lovdata's register of Norwegian treaties does not list it, and no "
                     "termination was found. " + LISTED,
        },
        "links": [(unts("0800000280162c50"), "website")],
        "prov": ministry_prov("Norway", mot("avrupa", "norvec", "ikili-anlasmalar-tablosu"), ("parties",)) + [
            ("signed", UNTS, unts("0800000280162c50")), ("in_force", UNTS, unts("0800000280162c50")),
            ("unts_registration", UNTS, unts("0800000280162c50")),
            ("status", f"{MOT} Norway", mot("avrupa", "norvec", "ikili-anlasmalar-tablosu")),
            ("notes", f"{MOT} Norway", mot("avrupa", "norvec", "ikili-anlasmalar-tablosu")),
        ],
    },
    "NOTR-TRA-1978": {
        "set": {
            "name": "Agreement between Norway and Turkey on trade, economic, industrial and technical cooperation",
            "other_names": tr_name("Ticari, Ekonomik, Sınai ve Teknik İş birliği Anlaşması"),
            "status": "in_force", "signed": "1978-02-10", "in_force": "1978-02-10", "parties": country("NO", "TR"),
            "notes": "In force on signature. Türkiye approved it in the Resmî Gazete No. 16308 of 6 June 1978. "
                     + LISTED,
        },
        "links": [("https://lovdata.no/dokument/TRAKTAT/traktat/1978-02-10-1", "website")],
        "prov": ministry_prov("Norway", mot("avrupa", "norvec", "ikili-anlasmalar-tablosu")) + [
            ("in_force", "Lovdata, Norges traktater", "https://lovdata.no/dokument/TRAKTAT/traktat/1978-02-10-1"),
            ("status", f"{MOT} Norway", mot("avrupa", "norvec", "ikili-anlasmalar-tablosu")),
            ("notes", "Lovdata, Norges traktater", "https://lovdata.no/dokument/TRAKTAT/traktat/1978-02-10-1"),
        ],
    },
    "SATR-TRA": {
        "set": {
            "name": "Trade Agreement between the Republic of Turkey and the Kingdom of Saudi Arabia",
            "other_names": tr_name("Ticaret Anlaşması"),
            "status": "in_force", "signed": "1974-05-01", "in_force": "1974-05-01", "parties": country("SA", "TR"),
            "notes": "Article 7 puts it into force from signature, subject to final approval, for one year, renewed "
                     "from year to year. Türkiye approved it in the Resmî Gazete No. 14959 of 28 July 1974. " + LISTED,
        },
        "prov": ministry_prov("Saudi Arabia", mot("orta-dogu-ve-korfez", "suudi-arabistan")) + [
            ("in_force", f"{RG}, No. 14959 of 28 July 1974 (text of the agreement, Article 7)",
             "https://www.resmigazete.gov.tr/arsiv/14959.pdf"),
            ("status", f"{MOT} Saudi Arabia", mot("orta-dogu-ve-korfez", "suudi-arabistan")),
            ("notes", f"{RG}, No. 14959 of 28 July 1974", "https://www.resmigazete.gov.tr/arsiv/14959.pdf"),
        ],
    },
    "TNTR-TRA": {
        "set": {
            "name": "Trade, Economic and Technical Cooperation Agreement between the Republic of Turkey and the "
                    "Republic of Tunisia",
            "other_names": tr_name("Ticaret, Ekonomik ve Teknik İşbirliği Anlaşması"),
            "status": "superseded", "signed": "1992-07-15", "provisional_application": "1992-07-15",
            "ended": "2005-07-01", "superseded_by": "TNTR", "parties": country("TN", "TR"),
            "notes": "Article XIV applies it provisionally from signature and definitively from the exchange of the "
                     "instruments of approval, whose date was not found. Türkiye approved it in the Resmî Gazete "
                     "No. 21506 of 24 February 1993. The Türkiye-Tunisia free trade agreement (TNTR) replaced it on "
                     "1 July 2005; the Ministry of Trade's country page still lists it.",
        },
        "prov": ministry_prov("Tunisia", mot("afrika", "tunus")) + [
            ("provisional_application", f"{RG}, No. 21506 of 24 February 1993 (text of the agreement, Article XIV)",
             "https://www.resmigazete.gov.tr/arsiv/21506.pdf"),
            ("status", "Turkish Ministry of Trade (English site), Tunisia",
             "https://www.trade.gov.tr/free-trade-agreements/tunisia"),
            ("ended", "Turkish Ministry of Trade (English site), Tunisia",
             "https://www.trade.gov.tr/free-trade-agreements/tunisia"),
            ("superseded_by", "Turkish Ministry of Trade (English site), Tunisia",
             "https://www.trade.gov.tr/free-trade-agreements/tunisia"),
            ("notes", f"{RG}, No. 21506 of 24 February 1993", "https://www.resmigazete.gov.tr/arsiv/21506.pdf"),
        ],
    },
    "TRUY-TRA": {
        "set": {
            "name": "Agreement on Trade, Economic and Technical Cooperation between the Government of the Republic "
                    "of Turkey and the Government of the Oriental Republic of Uruguay",
            "other_names": tr_name("Türkiye Cumhuriyeti Hükümeti ve Uruguay Doğu Cumhuriyeti Hükümeti Arasında "
                                   "Ticari, Ekonomik ve Teknik İşbirliği Anlaşması"),
            "status": "in_force", "signed": "2009-04-30", "in_force": "2011-10-25", "parties": country("TR", "UY"),
            "unts_registration": "I-49548",
            "notes": "In force on the exchange of the instruments of ratification (Article VIII). Türkiye approved "
                     "it in the Resmî Gazete of 28 May 2011. " + LISTED,
        },
        "links": [(unts("0800000280324f71"), "website")],
        "prov": ministry_prov("Uruguay", mot("guney-amerika", "uruguay")) + [
            ("in_force", UNTS, unts("0800000280324f71")), ("unts_registration", UNTS, unts("0800000280324f71")),
            ("status", f"{MOT} Uruguay", mot("guney-amerika", "uruguay")),
            ("notes", UNTS, unts("0800000280324f71")),
        ],
    },
}

# UNTS catalogue records that the Ministry of Trade lists: status from a party government.
UPGRADE = {
    "COTR-TRA": ("Colombia", mot("guney-amerika", "kolombiya"), "No. 27271 of 27 June 2009"),
    "GYTR-TRA": ("Guyana", mot("guney-amerika", "guyana"), "No. 27630 of 3 July 2010"),
    "MUTR-TRA": ("Mauritius", mot("afrika", "morityus"), None),
    "PYTR-TRA": ("Paraguay", mot("guney-amerika", "paraguay"), "No. 27848 of 16 February 2011"),
    "TRZA-TRA": ("South Africa", mot("afrika", "guney-afrika-cumhuriyeti"), "No. 26629 of 31 August 2007"),
}


def ordered(record: dict) -> dict:
    extra = [k for k in record if k not in FIELD_ORDER]
    if extra:
        raise SystemExit(f"{record.get('id')}: unknown fields {extra}")
    return {k: record[k] for k in FIELD_ORDER if k in record}


def prov_entry(field: str, source: str, url: str) -> dict:
    return {"field": field, "source": source, "url": url, "retrieved_at": TODAY}


def build_new(rid: str, change: dict) -> dict:
    if (DATA / f"{rid}.yaml").exists():
        raise SystemExit(f"{rid}: exists, but marked new")
    record = {"id": rid, "agreement_type": "trade_relations", **change["set"],
              "verification": "official", "last_verified": TODAY}
    if change.get("links"):
        record["links"] = [{"url": u, "type": t} for u, t in change["links"]]
    record["provenance"] = [prov_entry(*p) for p in change["prov"]]
    return ordered(record)


def upgrade(rid: str, country_name: str, url: str, rg: str | None) -> dict:
    record = yaml.safe_load((DATA / f"{rid}.yaml").read_text(encoding="utf-8"))
    approval = f" Türkiye approved it in the Resmî Gazete {rg}." if rg else ""
    record["notes"] = ("Dates from the UN Treaty Series registration. " + LISTED + approval)
    record["verification"] = "official"
    record["last_verified"] = TODAY
    keep = [p for p in record["provenance"] if p["field"] not in ("status", "notes")]
    keep += [prov_entry("status", f"{MOT} {country_name}", url), prov_entry("notes", f"{MOT} {country_name}", url)]
    record["provenance"] = keep
    return ordered(record)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    out = {rid: build_new(rid, change) for rid, change in NEW.items()}
    out.update({rid: upgrade(rid, *args_) for rid, args_ in UPGRADE.items()})
    tntr = yaml.safe_load((DATA / "TNTR.yaml").read_text(encoding="utf-8"))
    if tntr.get("supersedes") not in (None, "TNTR-TRA"):
        raise SystemExit(f"TNTR already supersedes {tntr['supersedes']}")
    tntr["supersedes"] = "TNTR-TRA"
    tntr["provenance"] = [p for p in tntr["provenance"] if p["field"] != "supersedes"] + [
        prov_entry("supersedes", "Turkish Ministry of Trade (English site), Tunisia",
                   "https://www.trade.gov.tr/free-trade-agreements/tunisia")]
    tntr["last_verified"] = TODAY
    out["TNTR"] = ordered(tntr)
    for rid, record in out.items():
        text = yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)
        if args.dry_run:
            print(text)
        else:
            (DATA / f"{rid}.yaml").write_text(text, encoding="utf-8")
    print(f"{len(NEW)} new, {len(UPGRADE)} upgraded, TNTR supersedes TNTR-TRA")


if __name__ == "__main__":
    main()
