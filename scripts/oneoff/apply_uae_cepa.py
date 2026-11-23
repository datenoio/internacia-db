"""Apply the UAE CEPA walk (2026-11-23) to data/trade_agreements/.

One-off script. The facts come from the UAE Ministry of Foreign Trade (trade.gov.ae), which took
over the CEPA pages from the Ministry of Economy and Tourism, from the Emirates News Agency (WAM),
and from each partner government. See docs/intblock-sources.md (UAE CEPA programme row) and the
pull request body for conflicts and held items.

Usage: python scripts/oneoff/apply_uae_cepa.py [--dry-run]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "trade_agreements"
TODAY = "2026-11-23"

FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id",
    "aric_id", "gptad_id", "dta_id", "unctad_iia_id", "unts_registration", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]

MOFT = "UAE Ministry of Foreign Trade"
WAM = "Emirates News Agency (WAM)"
EDIT = "EDIT - Electronic Database of Investment Treaties (World Trade Institute)"


def moft(slug: str) -> str:
    return f"https://www.trade.gov.ae/{slug}"


def wam(slug: str) -> str:
    return f"https://www.wam.ae/en/article/{slug}"


def edit(uuid: str) -> str:
    return f"https://edit.wti.org/document/show/{uuid}"


ARIC = "Asia Regional Integration Center (ADB), FTA database"
RTAIS = "WTO Regional Trade Agreements Information System"
SICE = "OAS Foreign Trade Information System (SICE)"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in codes]


def cepa_name(partner: str) -> str:
    return f"UAE-{partner} Comprehensive Economic Partnership Agreement"


def acr(value: str) -> list[dict]:
    return [{"lang": "en", "value": value}]


# Record id -> changes. Keys:
#   set: fields to set (None removes the field)
#   prov: list of (field, source, url) provenance entries; they replace existing entries for the same fields
#   drop_prov: further provenance fields to drop (catalogue entries the new ones replace)
#   links: links to add (url, type)
#   new: True for a new record (set must hold every required field)
CHANGES: dict[str, dict] = {
    # --- in force, upgraded or rechecked -------------------------------------------------------------
    "INUAE": {
        "links": [(moft("documents/d/guest/final_agreement_uae_india_cepa"), "treaty_text")],
        "prov": [
            ("status", MOFT, moft("uae-india-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AEIL": {
        "links": [(moft("documents/d/guest/israel_uae_cepa_eng"), "treaty_text")],
        "prov": [
            ("in_force", MOFT, moft("uae-israel-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AEID": {
        "set": {
            "name": cepa_name("Indonesia"),
            "acronyms": acr("IUAE-CEPA"),
            "other_names": [{"lang": "en", "name": "Indonesia-UAE Comprehensive Economic Partnership Agreement"}],
            "notes": "Signed in Abu Dhabi. Indonesia ratified it by Presidential Regulation (Perpres) No. 43 of 2023 "
                     "on 12 July 2023.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae_indonesia_cepa_eng"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("wto_rta_id", RTAIS, "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid=1229"),
            ("signed", "Indonesian Ministry of Trade, Directorate General of International Trade Negotiations",
             "https://ditjenppi.kemendag.go.id/bilateral/afrika-timurtengah/uniemiratarab"),
            ("in_force", "Indonesian Ministry of Trade, press release of 8 August 2026",
             "https://www.kemendag.go.id/berita/siaran-pers/bertemu-menteri-perdagangan-uea-mendag-busan-bahas-optimalisasi-pemanfaatan-iuae-cepa"),
            ("status", MOFT, moft("uae-indonesia-comprehensive-economic-partnership-agreement")),
            ("notes", "Indonesian Ministry of Trade, Directorate General of International Trade Negotiations",
             "https://ditjenppi.kemendag.go.id/bilateral/afrika-timurtengah/uniemiratarab"),
        ],
    },
    "AETR-CEPA": {
        "set": {
            "name": cepa_name("Türkiye"),
            "acronyms": acr("UAE-Türkiye CEPA"),
            "notes": "Türkiye approved it by Decision No. 7180, published in the Resmî Gazete No. 32173 "
                     "of 27 April 2023.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae_turkey_cepa_eng"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("wto_rta_id", RTAIS, "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid=1241"),
            ("signed", "Turkish Ministry of Trade, free trade agreements in force",
             "https://ticaret.gov.tr/dis-iliskiler/serbest-ticaret-anlasmalari/yururlukte-bulunan-stalar/birlesik-arap-emirlikleri"),
            ("in_force", "Turkish Ministry of Trade, free trade agreements in force",
             "https://ticaret.gov.tr/dis-iliskiler/serbest-ticaret-anlasmalari/yururlukte-bulunan-stalar/birlesik-arap-emirlikleri"),
            ("status", MOFT, moft("the-uae-t%C3%BCrkiye-cepa")),
            ("notes", "Turkish Ministry of Trade, free trade agreements in force",
             "https://ticaret.gov.tr/dis-iliskiler/serbest-ticaret-anlasmalari/yururlukte-bulunan-stalar/birlesik-arap-emirlikleri"),
        ],
    },
    "AEKH": {
        "set": {
            "name": cepa_name("Cambodia"),
            "acronyms": acr("UAE-Cambodia CEPA"),
            "other_names": [{"lang": "en", "name": "Cambodia-United Arab Emirates Comprehensive Economic Partnership Agreement"}],
            "in_force": "2024-01-31",
            "notes": "Signed in Phnom Penh. ADB ARIC gives only the year of entry into force (2024), and an older "
                     "UAE timeline graphic gives 25 January 2024; the UAE Ministry of Foreign Trade and the Cambodian "
                     "Ministry of Commerce give 31 January 2024.",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=443&ssid=3"),
            ("signed", MOFT, moft("uae-cambodia-cepa")),
            ("in_force", "Cambodian Ministry of Commerce, FTA portal", "https://ftaportal.moc.gov.kh/"),
            ("status", MOFT, moft("uae-cambodia-cepa")),
            ("notes", MOFT, moft("uae-cambodia-cepa")),
        ],
    },
    "AEGE": {
        "set": {
            "name": cepa_name("Georgia"),
            "acronyms": acr("UAE-Georgia CEPA"),
            "other_names": [{"lang": "en", "name": "Georgia-United Arab Emirates Economic Partnership Agreement"}],
            "signed": "2023-10-10",
            "in_force": "2024-06-27",
            "notes": "The Parliament of Georgia ratified it on 15 May 2024. Georgia's Legislative Herald and the UAE "
                     "Ministry of Foreign Trade give entry into force on 27 June 2024; ADB ARIC gives 26 June 2024, the "
                     "date of the WAM announcement.",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=444&ssid=3"),
            ("signed", "Legislative Herald of Georgia (matsne.gov.ge)", "https://matsne.gov.ge/ka/document/view/6208065"),
            ("in_force", "Legislative Herald of Georgia (matsne.gov.ge)", "https://matsne.gov.ge/ka/document/view/6208065"),
            ("status", MOFT, moft("uae-georgia-cepa")),
            ("notes", "Legislative Herald of Georgia (matsne.gov.ge), ratification resolution",
             "https://matsne.gov.ge/ka/document/view/6165534"),
        ],
        "links": [(moft("documents/d/guest/uae_georgia_cepa-pdf"), "treaty_text")],
    },
    "AECR": {
        "set": {
            "notes": "Signed in San José; approved by Costa Rica's Law No. 10618 (La Gaceta, Alcance No. 202, "
                     "12 December 2024). The SICE agreements table gives 2025-01-04 for entry into force, a day/month "
                     "swap. COMEX and the UAE Ministry of Foreign Trade give 2025-04-01; WAM announced it on "
                     "2 April 2025 as coming into force that day.",
        },
        "links": [(moft("documents/d/guest/uae_costa_rica_cepa_eng"), "treaty_text")],
        "prov": [
            ("signed", "Imprenta Nacional, La Gaceta, Alcance No. 202 (Law No. 10618)",
             "https://www.imprentanacional.go.cr/pub/2024/12/12/ALCA202_12_12_2024.pdf"),
            ("in_force", "Costa Rica Ministry of Foreign Trade (COMEX)",
             "https://www.comex.go.cr/tratados/emiratos-%C3%A1rabes-unidos/"),
            ("status", MOFT, moft("uae-costa-rica-cepa")),
            ("notes", "Costa Rica Ministry of Foreign Trade (COMEX)",
             "https://www.comex.go.cr/tratados/emiratos-%C3%A1rabes-unidos/"),
        ],
    },
    "AEMU": {
        "set": {
            "notes": "The first UAE CEPA with an African country. WAM announced it on 2 April 2025 as coming into "
                     "force that day; the Mauritius Revenue Authority and the Mauritian Ministry of Foreign Affairs "
                     "give 1 April 2025.",
        },
        "links": [(moft("documents/d/guest/uae_mauritius_cepa_eng"), "treaty_text")],
        "prov": [
            ("signed", MOFT, moft("uae-mauritius-cepa")),
            ("in_force", "Mauritius Revenue Authority, notice of 30 March 2025",
             "https://mra.mu/download/NoticeCEPA300325.pdf"),
            ("status", "Mauritius Ministry of Foreign Affairs, Regional Integration and International Trade",
             "https://www.mauritiustrade.mu/en/trade-agreements/uae"),
            ("notes", WAM, wam("15hwwqg-uae%E2%80%99s-comprehensive-economic-partnership")),
        ],
    },
    "AECL": {
        "set": {
            "notes": "Signed in Abu Dhabi. Chile promulgated it by Decree No. 142 of 2 October 2025 (Diario Oficial "
                     "No. 44.330, 22 December 2025), which gives entry into force on 24 November 2025. LeyChile shows "
                     "the publication date, 22 December 2025, as the start of validity, and the SICE Trade Policy "
                     "Developments index (May 2026 snapshot) still lists it as signed but not in force.",
        },
        "prov": [
            ("signed", "Diario Oficial de la República de Chile, Decree No. 142 of 2025",
             "https://www.diariooficial.interior.gob.cl/publicaciones/2025/12/22/44330/01/2743367.pdf"),
            ("in_force", "Diario Oficial de la República de Chile, Decree No. 142 of 2025",
             "https://www.diariooficial.interior.gob.cl/publicaciones/2025/12/22/44330/01/2743367.pdf"),
            ("status", "Undersecretariat of International Economic Relations (SUBREI)",
             "https://www.subrei.gob.cl/acuerdos-comerciales/acuerdos-comerciales-vigentes/emiratos-arabes-unidos"),
            ("notes", "Diario Oficial de la República de Chile, Decree No. 142 of 2025",
             "https://www.diariooficial.interior.gob.cl/publicaciones/2025/12/22/44330/01/2743367.pdf"),
        ],
    },
    "AERS": {
        "set": {
            "notes": "Signed in Belgrade. The first UAE CEPA with a country that is not a WTO member. Serbia ratified "
                     "it by law (Službeni glasnik RS – Međunarodni ugovori No. 2/2025).",
        },
        "prov": [
            ("signed", "Serbian Ministry of Internal and Foreign Trade, ratification law",
             "https://must.gov.rs/extfile/sr/14451/Закон о потврђивању ССEП.pdf"),
            ("in_force", "Serbian Ministry of Internal and Foreign Trade", "https://must.gov.rs/tekst/sr/14394/"),
            ("status", MOFT, moft("uae-serbia-comprehensive-economic-partnership-agreement")),
            ("notes", "Serbian Ministry of Internal and Foreign Trade, ratification law",
             "https://must.gov.rs/extfile/sr/14451/Закон о потврђивању ССEП.pdf"),
        ],
    },
    "AEJO-CEPA": {
        "new": True,
        "set": {
            "name": cepa_name("Jordan"),
            "acronyms": acr("UAE-Jordan CEPA"),
            "agreement_type": "fta",
            "status": "in_force",
            "signed": "2024-10-06",
            "in_force": "2025-05-15",
            "parties": country("AE", "JO"),
            "notes": "Signed in Jordan; the Arabic text is authentic. Article 1.5 affirms the parties' rights and "
                     "obligations under other agreements, including the Greater Arab Free Trade Area, and no provision "
                     "terminates the 2000 free trade zone agreement (AEJO); the Jordan Export Portal lists both. "
                     "The first UAE CEPA with an Arab country.",
            "verification": "official",
        },
        "links": [
            (moft("documents/d/guest/uae-jordan-cepa"), "treaty_text"),
            (edit("fc01ff2f-be2e-47a0-9d20-cfbe90138a1e"), "treaty_text"),
        ],
        "prov": [
            ("parties", MOFT, moft("uae-jordan-cepa")),
            ("signed", "Jordan News Agency (Petra), statement of the Minister of Industry, Trade and Supply",
             "https://petra.gov.jo/dotcleen/index.php/en/news/jordan-uae-push-to-expand-trade-boost-economic-partnership"),
            ("in_force", MOFT, moft("uae-jordan-cepa")),
            ("status", "Jordan Export Portal, FTA matrix",
             "https://jordanexportportal.gov.jo/menu-1/82-fta-matrix---jordan-trade-agreements"),
            ("notes", EDIT, edit("fc01ff2f-be2e-47a0-9d20-cfbe90138a1e")),
        ],
    },
    "AEJO": {
        "set": {
            "notes": "Signed at Amman. Not notified to the WTO. The UAE-Jordan CEPA (AEJO-CEPA, in force 2025-05-15) "
                     "does not terminate it: its Article 1.5 affirms the parties' other agreements, and the Jordan "
                     "Export Portal lists both.",
        },
        "prov": [
            ("notes", "Jordan Export Portal, FTA matrix",
             "https://jordanexportportal.gov.jo/menu-1/82-fta-matrix---jordan-trade-agreements"),
        ],
    },
    "AEVN": {
        "set": {
            "name": "UAE-Viet Nam Comprehensive Economic Partnership Agreement",
            "acronyms": acr("UAE-Viet Nam CEPA"),
            "other_names": [{"lang": "en", "name": "Viet Nam-United Arab Emirates Economic Partnership Agreement"}],
            "status": "in_force",
            "in_force": "2026-02-03",
            "notes": "Signed in Dubai. Viet Nam's Decree No. 143/2026/ND-CP implements it from 3 February 2026.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae_vn_cepa"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=461&ssid=3"),
            ("signed", "Vietnamese Ministry of Industry and Trade",
             "https://moit.gov.vn/tin-tuc/hoat-dong/hoat-dong-cua-lanh-dao-dang-nha-nuoc/viet-nam-va-uae-ky-hiep-dinh-doi-tac-kinh-te-toan-dien-cepa-.html"),
            ("in_force", "Official Gazette of Viet Nam (Công báo), Decree No. 143/2026/ND-CP",
             "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-143-2026-nd-cp-469481.htm"),
            ("status", WAM, wam("byjzfby-uae-vietnam-comprehensive-economic-partnership")),
            ("notes", "Official Gazette of Viet Nam (Công báo), Decree No. 143/2026/ND-CP",
             "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-143-2026-nd-cp-469481.htm"),
        ],
    },
    "AUUAE": {
        "prov": [
            ("status", MOFT, moft("uae-australia-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AENZ": {
        "set": {
            "name": cepa_name("New Zealand"),
            "acronyms": acr("UAE-New Zealand CEPA"),
            "notes": "WAM announced the entry into force on 27 August 2025; the New Zealand Customs Service, MFAT and "
                     "the UAE Ministry of Foreign Trade give 28 August 2025.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae_newzealand_cepa_eng"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("wto_rta_id", RTAIS, "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid=1252"),
            ("signed", "New Zealand Customs Service",
             "https://www.customs.govt.nz/information-releases-and-legislation/legislation/international-agreements/free-trade-agreements/new-zealand-united-arab-emirates-comprehensive-economic-partnership-agreement"),
            ("in_force", "New Zealand Ministry of Foreign Affairs and Trade",
             "https://www.mfat.govt.nz/en/trade/free-trade-agreements/free-trade-agreements-in-force/new-zealand-united-arab-emirates-free-trade-agreement/overview"),
            ("status", MOFT, moft("uae-new-zealand-comprehensive-economic-partnership-agreement")),
            ("notes", WAM, wam("blentn3-uae-new-zealand-comprehensive-economic-partnership")),
        ],
    },
    "AEMY": {
        "set": {
            "acronyms": acr("MY-UAE CEPA"),
            "signed": "2025-01-14",
            "in_force": "2025-10-01",
            "notes": "Signed in Abu Dhabi. ADB ARIC gives 2024-01-14 for entry into force; MITI and the UAE Ministry "
                     "of Foreign Trade give 2025-10-01.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae_malaysia_cepa_eng"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=459&ssid=3"),
            ("signed", "Malaysian Ministry of Investment, Trade and Industry (MITI)",
             "https://www.miti.gov.my/miti/resources/Media%20Release/PERJANJIAN_CEPA_MALAYSIA-UAE_SASARAN_PENINGKATAN_PERDAGANGAN.pdf"),
            ("in_force", "Malaysian Ministry of Investment, Trade and Industry (MITI), notice of 29 September 2025",
             "https://www.miti.gov.my/miti/resources/Preferential%20Certificate%20of%20Origin/Announcement/Notice_MY_UAE_CEPA_2025.pdf"),
            ("status", MOFT, moft("uae-malaysia-comprehensive-economic-partnership-agreement")),
            ("notes", MOFT, moft("uae-malaysia-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AEUA": {
        "set": {
            "name": cepa_name("Ukraine"),
            "acronyms": acr("UAE-Ukraine CEPA"),
            "notes": "Signed in Abu Dhabi. Ukraine ratified it by Law No. 4802-IX of 26 February 2026.",
            "verification": "official",
        },
        "links": [(moft("documents/d/guest/uae-ukraine-cepa_eng_fully-executed-1"), "treaty_text")],
        "drop_prov": ["parties"],
        "prov": [
            ("wto_rta_id", RTAIS, "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid=1251"),
            ("signed", "Ministry of Economy of Ukraine",
             "https://me.gov.ua/News/Print/e22aa263-c7ef-4c43-a81d-7787e0968d4b?lang=uk-UA"),
            ("in_force", "State Customs Service of Ukraine", "https://t.me/UkraineCustoms/6275"),
            ("status", MOFT, moft("uae-ukraine-cepa")),
            ("notes", "Verkhovna Rada of Ukraine, Law No. 4802-IX (Wayback Machine capture)",
             "http://web.archive.org/web/20260331151315/https://zakon.rada.gov.ua/laws/show/4802-20"),
        ],
    },
    "AEKR": {
        "set": {
            "name": "UAE-Republic of Korea Comprehensive Economic Partnership Agreement",
            "acronyms": acr("UAE-Korea CEPA"),
            "other_names": [{"lang": "en", "name": "Republic of Korea-United Arab Emirates Comprehensive Economic Partnership Agreement"}],
            "status": "in_force",
            "signed": "2024-05-29",
            "in_force": "2026-05-01",
            "notes": "Signed in Seoul. The Korean National Assembly consented on 31 March 2026 and the two sides set "
                     "entry into force for 1 May 2026.",
            "verification": "official",
        },
        "links": [
            (moft("documents/d/guest/uae-korea-cepa_english-2"), "treaty_text"),
            (edit("8d3b42e0-ffdd-4581-9981-cc0be90524ea"), "treaty_text"),
        ],
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=452&ssid=3"),
            ("signed", "Korea FTA portal (fta.go.kr), Ministry of Trade, Industry and Resources",
             "https://www.fta.go.kr/ftamain/kfta/lov5/ucp/1/2/"),
            ("in_force", "Korean Ministry of Trade, Industry and Resources, press release of 3 April 2026",
             "https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/171693/view"),
            ("status", MOFT, moft("uae-korea-cepa")),
            ("notes", "Korean Ministry of Trade, Industry and Resources, press release of 3 April 2026",
             "https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/171693/view"),
        ],
    },
    "AEAZ": {
        "new": True,
        "set": {
            "name": cepa_name("Azerbaijan"),
            "acronyms": acr("UAE-Azerbaijan CEPA"),
            "agreement_type": "fta",
            "status": "in_force",
            "signed": "2025-07-09",
            "in_force": "2026-04-15",
            "parties": country("AE", "AZ"),
            "notes": "Signed in Abu Dhabi. Azerbaijan approved it by Law No. 268-VIIQ of 17 October 2025. The UAE "
                     "Ministry of Foreign Trade and WAM give entry into force on 15 April 2026; the Azerbaijani Ministry "
                     "of Economy announced on 26 May 2026 that it had entered into force, without a date.",
            "verification": "official",
        },
        "links": [
            (moft("documents/d/guest/uae_azerbaijan_cepa"), "treaty_text"),
            (edit("4f86a275-298c-4e78-8bab-b37c87b2b99d"), "treaty_text"),
        ],
        "prov": [
            ("parties", MOFT, moft("uae-azerbaijan-cepa")),
            ("signed", "Ministry of Economy of the Republic of Azerbaijan",
             "https://economy.gov.az/en/page/iqtisadi-sazisler/herterefli-ticaret-sazisleri"),
            ("in_force", MOFT, moft("uae-azerbaijan-cepa")),
            ("status", "Ministry of Economy of the Republic of Azerbaijan, news of 26 May 2026",
             "https://economy.gov.az/az/post/3414/birlesmis-ereb-emirlikleri-ile-imzalanmis-herterefli-iqtisadi-terefdasliq-sazisi-quvveye-minib"),
            ("notes", WAM, wam("bzq977o-uae-azerbaijan-cepa-officially-enters-into-force")),
        ],
    },
    "AECD": {
        "new": True,
        "set": {
            "name": "UAE-Democratic Republic of the Congo Comprehensive Economic Partnership Agreement",
            "acronyms": acr("UAE-DRC CEPA"),
            "agreement_type": "fta",
            "status": "in_force",
            "signed": "2026-02-02",
            "in_force": "2026-10-30",
            "parties": country("AE", "CD"),
            "notes": "Signed at Qasr Al Shati in Abu Dhabi. The DRC Senate and National Assembly approved ratification "
                     "in July 2026 (Congolese Press Agency); no DRC government notice of entry into force was found.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("byje0mb-uae-democratic-republic-congo-strengthen-economic")),
            ("signed", WAM, wam("byje0mb-uae-democratic-republic-congo-strengthen-economic")),
            ("in_force", WAM, wam("c3051gr-uae%E2%80%99s-comprehensive-economic-partnership-agreement")),
            ("status", WAM, wam("c3051gr-uae%E2%80%99s-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AERU": {
        "new": True,
        "set": {
            "name": "Agreement on Trade in Services and Investment between the United Arab Emirates and the Russian Federation",
            "acronyms": acr("TISIA"),
            "agreement_type": "services",
            "status": "in_force",
            "signed": "2025-08-07",
            "in_force": "2026-08-23",
            "parties": country("AE", "RU"),
            "notes": "Covers trade in services and investment; trade in goods is covered by the EAEU-UAE Economic "
                     "Partnership Agreement (EAEUAE). Signed in Moscow; Russia ratified it by Federal Law No. 140-FZ "
                     "of 25 May 2026. The Russian official publication gives entry into force on 23 August 2026; WAM "
                     "reported it on 22 August 2026 and gives 8 August 2025 for the signature.",
            "verification": "official",
        },
        "links": [(edit("ded80636-0fdc-4857-a075-99c5b4129d2d"), "treaty_text")],
        "prov": [
            ("parties", "Official Internet Portal of Legal Information (publication.pravo.gov.ru)",
             "http://publication.pravo.gov.ru/document/0001202608240005"),
            ("signed", "Official Internet Portal of Legal Information (publication.pravo.gov.ru)",
             "http://publication.pravo.gov.ru/document/0001202608240005"),
            ("in_force", "Official Internet Portal of Legal Information (publication.pravo.gov.ru)",
             "http://publication.pravo.gov.ru/document/0001202608240005"),
            ("status", WAM, wam("c1v24ya-uae-russia-trade-services-and-investment-agreement")),
            ("notes", WAM, wam("c1v24ya-uae-russia-trade-services-and-investment-agreement")),
        ],
    },
    "AEBY": {
        "new": True,
        "set": {
            "name": "Agreement on Trade in Services and Investment between the United Arab Emirates and the Republic of Belarus",
            "acronyms": acr("TISIA"),
            "agreement_type": "services",
            "status": "in_force",
            "signed": "2025-06-27",
            "in_force": "2026-10-07",
            "parties": country("AE", "BY"),
            "notes": "Covers trade in services and investment; trade in goods is covered by the EAEU-UAE Economic "
                     "Partnership Agreement (EAEUAE). Signed in Minsk; Belarus signed its ratification law on "
                     "10 December 2025. No Belarusian notice of entry into force was found.",
            "verification": "official",
        },
        "links": [(edit("ea910bb2-9b11-45f5-bd7d-29c697c2d15e"), "treaty_text")],
        "prov": [
            ("parties", "National Legal Internet Portal of the Republic of Belarus (pravo.by)",
             "https://pravo.by/novosti/obshchestvenno-politicheskie-i-v-oblasti-prava/2025/june/89278/"),
            ("signed", "National Legal Internet Portal of the Republic of Belarus (pravo.by)",
             "https://pravo.by/novosti/obshchestvenno-politicheskie-i-v-oblasti-prava/2025/june/89278/"),
            ("in_force", WAM, wam("c2mg1zn-uae-belarus-trade-services-and-investment")),
            ("status", WAM, wam("c2mg1zn-uae-belarus-trade-services-and-investment")),
            ("notes", "National Legal Internet Portal of the Republic of Belarus (pravo.by)",
             "https://pravo.by/novosti/obshchestvenno-politicheskie-i-v-oblasti-prava/2025/december/91318/"),
        ],
    },
    # --- signed, not in force ---------------------------------------------------------------------------
    "AECO": {
        "set": {
            "name": cepa_name("Colombia"),
            "acronyms": acr("UAE-Colombia CEPA"),
            "other_names": [{"lang": "es", "name": "Acuerdo Integral de Asociación Económica entre la República de Colombia y los Emiratos Árabes Unidos"}],
            "notes": "The Colombian approval bill gives Bogotá as the place of signature; WAM reported it from Abu Dhabi "
                     "in a report dated 19 April 2024. Not in force: the approval bill (Proyecto "
                     "de Ley 266 de 2026 Senado, filed 28 September 2026) passed the Senate's Second Committee on "
                     "4 November 2026. The Colombian Foreign Ministry's bilateral page gives 5 December 2023, the date "
                     "negotiations concluded, as the date of signature.",
            "verification": "official",
        },
        "prov": [
            ("signed", "Congress of Colombia, Gaceta del Congreso No. 1428 of 2026 (Proyecto de Ley 266 de 2026 Senado; copy on redjurista.com)",
             "https://www.redjurista.com/Compilaciones2018/gacetasCongreso/2026/gc_1428_2026.pdf"),
            ("status", "Senate of Colombia, press release of 4 November 2026",
             "https://www.senado.gov.co/index.php/el-senado/noticias/7700-productos-colombianos-entrarian-sin-aranceles-a-emiratos-arabes-unidos"),
            ("notes", WAM, wam("13vg51t-uae-and-colombian-presidents-witness-signing")),
        ],
    },
    "AEKE": {
        "set": {
            "notes": "Signed at Qasr Al Bahr in Abu Dhabi. The Kenyan National Assembly approved ratification on "
                     "27 November 2025, after deleting the reservations on Articles 13.33 and 2.13 that the motion "
                     "first carried. Goods market access is left to negotiations within the East African Community "
                     "(Article 2.19). Not in force on 2026-11-23: it is not among the 20 CEPAs that the UAE counted "
                     "in force on 30 October 2026.",
        },
        "prov": [
            ("signed", "Kenya National Assembly, memorandum on the ratification of the Kenya-UAE CEPA (March 2025)",
             "https://parliament.go.ke/sites/default/files/2025-03/Memorandum%20to%20the%20National%20Assembly%20to%20Commence%20the%20Ratification%20Process%20of%20%20the%20Kenya%20-United%20Arab%20Emirates%20Comprehensive%20Economic%20Partnership%20Agreement%20.pdf"),
            ("status", "Kenya National Assembly, Hansard, 27 November 2025",
             "https://www.parliament.go.ke/sites/default/files/2025-11/Hansard%20Report%20-%20Thursday%2C%2027th%20November%202025%20%28P%29.pdf"),
            ("notes", "Kenya National Assembly, Hansard, 27 November 2025",
             "https://www.parliament.go.ke/sites/default/files/2025-11/Hansard%20Report%20-%20Thursday%2C%2027th%20November%202025%20%28P%29.pdf"),
        ],
    },
    "AECF": {
        "set": {
            "notes": "Signed in Abu Dhabi. Not in force on 2026-11-23: it is not among the 20 CEPAs that the UAE "
                     "counted in force on 30 October 2026.",
        },
        "prov": [
            ("notes", WAM, wam("c3051gr-uae%E2%80%99s-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AECG": {
        "new": True,
        "set": {
            "name": "UAE-Republic of the Congo Comprehensive Economic Partnership Agreement",
            "acronyms": acr("UAE-Congo CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2025-04-08",
            "parties": country("AE", "CG"),
            "notes": "Signed at Qasr Al Bahr in Abu Dhabi; negotiations concluded in December 2023. Not in force on "
                     "2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("bj2pq0o-uae-president-president-republic-the-congo-witness")),
            ("signed", WAM, wam("bj2pq0o-uae-president-president-republic-the-congo-witness")),
            ("status", "UAE Presidential Court (mohamedbinzayed.ae)",
             "https://www.mohamedbinzayed.ae/en/latest-news-listing/2025/04/UAE-President-President-of-Republic-of-the-Congo-witness-signing-of-Comprehensive-Agreement"),
        ],
    },
    "AEAO": {
        "new": True,
        "set": {
            "name": cepa_name("Angola"),
            "acronyms": acr("UAE-Angola CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2025-08-25",
            "parties": country("AE", "AO"),
            "notes": "Signed at the Presidential Palace in Luanda during the UAE President's state visit. Not in force "
                     "on 2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("bldgylh-uae-angolan-presidents-witness-exchange")),
            ("signed", "Angolan Ministry of Industry and Commerce (MINDCOM)",
             "https://mindcom.gov.ao/web/noticias/angola-e-emirados-arabes-unidos-assinam-dois-instrumentos-juridicos-de-cooperacao-no-sector-da-industria-e-comercio"),
            ("status", WAM, wam("bldgylh-uae-angolan-presidents-witness-exchange")),
        ],
    },
    "AEPH": {
        "new": True,
        "set": {
            "name": cepa_name("Philippines"),
            "acronyms": acr("PH-UAE CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2026-01-13",
            "parties": country("AE", "PH"),
            "notes": "Signed in Abu Dhabi during Abu Dhabi Sustainability Week. The timeline on the Department of Trade "
                     "and Industry's FTA portal gives November 2025 for the signature. Not in force: it was not on the "
                     "Philippine Senate's list of treaties submitted for concurrence on 26 May 2026.",
            "verification": "official",
        },
        "prov": [
            ("parties", MOFT, moft("w/uae-philippines-begin-new-chapter-of-trade-investment-cooperation-with-signing-of-cepa")),
            ("signed", WAM, wam("by7hbpm-uae-philippines-begin-new-chapter-trade-investment")),
            ("status", "Senate of the Philippines, treaties submitted for concurrence (20th Congress, 26 May 2026)",
             "https://senate.gov.ph/hq/uploads/stand_alone/pdfs/3f32e381-a096-4e59-982a-933424dd3283.pdf"),
        ],
    },
    "AENG": {
        "new": True,
        "set": {
            "name": cepa_name("Nigeria"),
            "acronyms": acr("UAE-Nigeria CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2026-01-13",
            "parties": country("AE", "NG"),
            "notes": "Signed in Abu Dhabi during Abu Dhabi Sustainability Week. Not in force on 2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("by7hbym-uae-nigeria-forge-stronger-economic-ties-with")),
            ("signed", "State House, Federal Republic of Nigeria",
             "https://statehouse.gov.ng/nigerias-trade-deal-with-the-uae-minister-jumoke-oduwole-explains-what-nigeria-stands-to-gain-from-cepa/"),
            ("status", WAM, wam("c3051gr-uae%E2%80%99s-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AESL": {
        "new": True,
        "set": {
            "name": cepa_name("Sierra Leone"),
            "acronyms": acr("UAE-Sierra Leone CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2026-02-02",
            "parties": country("AE", "SL"),
            "notes": "Signed at Qasr Al Shati in Abu Dhabi. Not in force on 2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("byje04h-uae-sierra-leone-enhance-economic-relations")),
            ("signed", "State House of Sierra Leone, UAE-Sierra Leone joint statement",
             "https://statehouse.gov.sl/wp-content/uploads/2026/02/JOINT-STATEMENT-BETWEEN-THE-UNITED-ARAB-EMIRATES-AND-THE-REPUBLIC-OF-SIERRA-LEONE-final-edition.pdf"),
            ("status", WAM, wam("c3051gr-uae%E2%80%99s-comprehensive-economic-partnership-agreement")),
        ],
    },
    "AEGA": {
        "new": True,
        "set": {
            "name": cepa_name("Gabon"),
            "acronyms": acr("UAE-Gabon CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2026-02-06",
            "parties": country("AE", "GA"),
            "notes": "Signed in Abu Dhabi. Not in force on 2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("bylrqy5-uae-and-gabon-sign-comprehensive-economic")),
            ("signed", WAM, wam("bylrqy5-uae-and-gabon-sign-comprehensive-economic")),
            ("status", MOFT, moft("w/cepa-with-gabon-strengthens-uae-presence-in-west-africa-minister-of-foreign-trade")),
        ],
    },
    "AEEC": {
        "set": {
            "name": cepa_name("Ecuador"),
            "acronyms": acr("UAE-Ecuador CEPA"),
            "other_names": [{"lang": "es", "name": "Acuerdo de Asociación Económica Integral entre Ecuador y Emiratos Árabes Unidos"}],
            "status": "signed",
            "signed": "2026-03-01",
            "notes": "Joint declaration on negotiations signed on 2024-04-22. Signed in Quito on 1 March 2026 (WAM, "
                     "dated 2 March in UAE time, says the agreement was announced). Not in force on 2026-11-23.",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("parties", "Ecuadorian Ministry of Production, Foreign Trade, Investment and Fisheries",
             "https://www.produccion.gob.ec/acuerdo-de-asociacion-economica-integral-entre-ecuador-y-emiratos-arabes-unidos/"),
            ("signed", "Ecuadorian Ministry of Production, Foreign Trade, Investment and Fisheries",
             "https://www.produccion.gob.ec/acuerdo-de-asociacion-economica-integral-entre-ecuador-y-emiratos-arabes-unidos/"),
            ("status", "Ecuadorian Government Communication Secretariat, bulletin 265 of 1 March 2026",
             "https://www.comunicacion.gob.ec/el-gobierno-de-daniel-noboa-consolida-historico-vinculo-diplomatico-con-emiratos-arabes-unidos-2/"),
            ("signed", EDIT, edit("a6f1f8a9-ebbb-4904-9a86-32dd1e8d306c")),
            ("notes", WAM, wam("bz0244f-crown-prince-abu-dhabi-president-ecuador-discuss")),
            ("notes", SICE, "https://web.archive.org/web/20251005215220/http://www.sice.oas.org/TPD/ECU_UAE/ECU_UAE_e.ASP"),
        ],
    },
    "AEBJ": {
        "new": True,
        "set": {
            "name": cepa_name("Benin"),
            "acronyms": acr("UAE-Benin CEPA"),
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2026-10-25",
            "parties": country("AE", "BJ"),
            "notes": "Signed in Abu Dhabi (WAM reports the presidents witnessing its exchange). Not in force on "
                     "2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("c2x5viw-uae-and-benin-presidents-witness-exchange")),
            ("signed", WAM, wam("c2x5vlu-cepa-takes-relations-with-uae-new-horizons-benins")),
            ("status", WAM, wam("c2x5viw-uae-and-benin-presidents-witness-exchange")),
        ],
    },
    # --- negotiations ------------------------------------------------------------------------------------
    "AEJP": {
        "set": {
            "name": "Japan-United Arab Emirates Comprehensive Economic Partnership Agreement",
            "acronyms": acr("Japan-UAE CEPA"),
            "other_names": [{"lang": "en", "name": "Japan-United Arab Emirates Economic Partnership Agreement"}],
            "notes": "Negotiations concluded on 5 March 2026; not signed on 2026-11-23. Called an EPA until the "
                     "seventh round.",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("aric_id", ARIC, "https://aric.adb.org/fta.php?id=463&ssid=3"),
            ("status", "Ministry of Foreign Affairs of Japan", "https://www.mofa.go.jp/policy/economy/fta/uae.html"),
            ("notes", "Ministry of Foreign Affairs of Japan", "https://www.mofa.go.jp/policy/economy/fta/uae.html"),
        ],
    },
    "AETH": {
        "new": True,
        "set": {
            "name": "Thailand-UAE Comprehensive Economic Partnership Agreement",
            "acronyms": acr("Thai-UAE CEPA"),
            "agreement_type": "fta",
            "status": "negotiating",
            "parties": country("AE", "TH"),
            "notes": "Negotiations launched in May 2023 and concluded on 7 October 2026 (announced in Bangkok on "
                     "8 October 2026); signing is expected in the first quarter of 2027.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("c2n1hr9-uae-thailand-conclude-cepa-negotiations-opening")),
            ("status", "Government Public Relations Department of Thailand (Wayback Machine capture)",
             "https://web.archive.org/web/20261008151945/https://thailand.prd.go.th/en/content/category/detail/id/48/iid/549398"),
            ("notes", "Government Public Relations Department of Thailand (Wayback Machine capture)",
             "https://web.archive.org/web/20261008151945/https://thailand.prd.go.th/en/content/category/detail/id/48/iid/549398"),
        ],
    },
    "AEMZ": {
        "new": True,
        "set": {
            "name": cepa_name("Mozambique"),
            "acronyms": acr("UAE-Mozambique CEPA"),
            "agreement_type": "fta",
            "status": "negotiating",
            "parties": country("AE", "MZ"),
            "notes": "Negotiations concluded and the final terms were announced in Abu Dhabi on 14 November 2026; not "
                     "signed on 2026-11-23.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("c392jlz-uae-mozambique-conclude-cepa-negotiations-non-oil")),
            ("status", WAM, wam("c392jlz-uae-mozambique-conclude-cepa-negotiations-non-oil")),
            ("notes", WAM, wam("c392jlz-uae-mozambique-conclude-cepa-negotiations-non-oil")),
        ],
    },
    "AEMA-CEPA": {
        "new": True,
        "set": {
            "name": cepa_name("Morocco"),
            "acronyms": acr("UAE-Morocco CEPA"),
            "agreement_type": "fta",
            "status": "negotiating",
            "parties": country("AE", "MA"),
            "notes": "Ministers signed a joint declaration in Rabat on 27 July 2024 announcing the conclusion of "
                     "negotiations; no signature was found by 2026-11-23. Whether it would replace the 2001 UAE-Morocco "
                     "free trade agreement (AEMA) is not known, because its text is not public.",
            "verification": "official",
        },
        "prov": [
            ("parties", WAM, wam("b4dfd0u-uae-morocco-finalise-terms-comprehensive-economic")),
            ("status", WAM, wam("b4dfd0u-uae-morocco-finalise-terms-comprehensive-economic")),
            ("notes", WAM, wam("b4dfd0u-uae-morocco-finalise-terms-comprehensive-economic")),
        ],
    },
    "AEMA": {
        "set": {
            "notes": "The UAE and Morocco concluded negotiations on a Comprehensive Economic Partnership Agreement "
                     "(AEMA-CEPA) on 27 July 2024; it was not signed by 2026-11-23.",
        },
        "prov": [
            ("notes", WAM, wam("b4dfd0u-uae-morocco-finalise-terms-comprehensive-economic")),
        ],
    },
    "AEPE": {
        "set": {
            "notes": "Ministers agreed to start negotiations at WTO MC13 in Abu Dhabi in February 2024 and agreed the "
                     "terms of reference on 4 September 2025. Rounds: 25-28 November 2025 and 26-28 January 2026 "
                     "(virtual).",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("parties", "Peruvian Ministry of Foreign Trade and Tourism (MINCETUR), trade agreements portal",
             "https://www.acuerdoscomerciales.gob.pe/Negociacion/Emiratos_Arabes/inicio.html"),
            ("status", "Peruvian Ministry of Foreign Trade and Tourism (MINCETUR), trade agreements portal",
             "https://www.acuerdoscomerciales.gob.pe/Negociacion/Emiratos_Arabes/Sobre_Acuerdo.html"),
            ("notes", "Peruvian Ministry of Foreign Trade and Tourism (MINCETUR), trade agreements portal",
             "https://www.acuerdoscomerciales.gob.pe/Negociacion/Emiratos_Arabes/Sobre_Acuerdo.html"),
        ],
    },
    "MERCOSURAE": {
        "set": {
            "notes": "Negotiations announced in Asunción on 7 July 2024 (first round 2-4 July 2024); the fourth round "
                     "concluded on 2025-11-07 (SICE). On 30 June 2026 the MERCOSUR presidents reaffirmed their intention "
                     "to conclude them as soon as possible. Argentina and the UAE separately launched bilateral CEPA "
                     "negotiations on 24 September 2026.",
            "verification": "official",
        },
        "drop_prov": ["parties"],
        "prov": [
            ("parties", "Government of Brazil, Siscomex, MERCOSUR-UAE", "https://www.gov.br/siscomex/pt-br/acordos-comerciais/mercosul-eau"),
            ("status", "Paraguayan Ministry of Foreign Affairs, joint communiqué of the MERCOSUR presidents (30 June 2026)",
             "https://www.mre.gov.py/wp-content/uploads/2026/06/Comunicado-conjunto-de-los-presidentes-de-los-Estados-Partes-del-Mercosur.pdf"),
            ("notes", WAM, wam("c2epg0y-uae-argentina-launch-cepa-negotiations-issue-joint")),
            ("notes", SICE, "https://web.archive.org/web/20251117062701/http://www.sice.oas.org/TPD/MER_UAE/MER_UAE_e.asp"),
        ],
    },
}


def ordered(record: dict) -> dict:
    extra = [k for k in record if k not in FIELD_ORDER]
    if extra:
        raise SystemExit(f"{record.get('id')}: unknown fields {extra}")
    return {k: record[k] for k in FIELD_ORDER if k in record}


def apply(rid: str, change: dict) -> dict:
    path = DATA / f"{rid}.yaml"
    if change.get("new"):
        if path.exists():
            raise SystemExit(f"{rid}: exists, but marked new")
        record: dict = {"id": rid}
    else:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    for key, value in change.get("set", {}).items():
        if value is None:
            record.pop(key, None)
        else:
            record[key] = value
    links = list(record.get("links") or [])
    for url, kind in change.get("links", []):
        if not any(link["url"] == url for link in links):
            links.append({"url": url, "type": kind})
    if links:
        record["links"] = links
    prov = change.get("prov", [])
    if prov:
        fields = {f for f, _, _ in prov} | set(change.get("drop_prov", []))
        kept = [p for p in record.get("provenance", []) if p["field"] not in fields]
        for f, source, url in prov:
            kept.append({"field": f, "source": source, "url": url, "retrieved_at": TODAY})
        record["provenance"] = kept
    record["last_verified"] = TODAY
    return ordered(record)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for rid, change in CHANGES.items():
        record = apply(rid, change)
        text = yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)
        if args.dry_run:
            print(text)
        else:
            (DATA / f"{rid}.yaml").write_text(text, encoding="utf-8")
    print(f"{len(CHANGES)} records")


if __name__ == "__main__":
    main()
