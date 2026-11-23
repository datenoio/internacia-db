"""Apply the Pakistan check (2026-11-23) to data/trade_agreements/.

One-off script. The list of arrangements Pakistan holds, with their dates, comes from the
Preferential Trade Access Database of the Trade Development Authority of Pakistan (TDAP PTAD,
ptad.tdap.gov.pk, JSON API `/api/modules/<code>`). Dates are checked against the customs
notifications (S.R.O.) of the Federal Board of Revenue, the partner governments (president.az,
lex.uz, Indonesian Presidential Regulation 114/2018, Malaysian MITI), MOFCOM, the WTO RTA
database, EUR-Lex (Publications Office Cellar) and the Omani official gazette. Where only the
press gives a date, provenance names it.

Usage: python scripts/oneoff/apply_pakistan_ptad.py [--dry-run]
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
    "provisional_application", "ended", "parties", "instruments", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "gptad_id", "dta_id", "unctad_iia_id", "unts_registration", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]
INSTRUMENT_ORDER = [
    "id", "kind", "name", "other_names", "status", "signed", "in_force", "ended", "coverage", "notes", "provenance",
]

PTAD = "Trade Development Authority of Pakistan, Preferential Trade Access Database (PTAD)"


def ptad(code: str) -> str:
    return f"https://ptad.tdap.gov.pk/modules/{code}"


FBR = "Federal Board of Revenue (Pakistan), customs notification"
FBR_ACTIVE = "Federal Board of Revenue (Pakistan), active customs notifications on imports"
FBR_ACTIVE_URL = "https://www.fbr.gov.pk/Activesrosimport"
EURLEX = "EUR-Lex (Publications Office Cellar)"
WTO = "WTO Regional Trade Agreements Information System"
MOFCOM = "Ministry of Commerce of the People's Republic of China, China FTA Network"
MOFCOM_PK = "https://fta.mofcom.gov.cn/topic/china_pakistan_phase.shtml"


def eurlex(celex: str) -> str:
    return f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}"


def rta(rtaid: int) -> str:
    return f"https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid={rtaid}"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in codes]


def instrument(id_: str, kind: str, name: str, status: str, prov: list[tuple[str, str]], **extra) -> dict:
    item = {"id": id_, "kind": kind, "name": name, "status": status, **extra}
    item["provenance"] = [
        {"field": "instruments", "source": source, "url": url, "retrieved_at": TODAY} for source, url in prov
    ]
    return {k: item[k] for k in INSTRUMENT_ORDER if k in item}


AZ_SRO = "https://download1.fbr.gov.pk/SROs/202412161512240413SRO2053-2024.pdf"
AZ_SIGNING = "https://president.az/en/articles/view/66461/print"
AF_SRO = "https://download1.fbr.gov.pk/SROs/2025731227123130SRO1386.pdf"
AF_DAWN = "https://www.dawn.com/news/1926219"
SATIS_TEXT = "https://www.commerce.gov.in/files/2025-01/SAARC-Agreement-on-Trade-in-Services-SATS.pdf"
SATIS_MV = "https://trade.gov.mv/?p=9036"
SATIS_MV_SOURCE = "Ministry of Economic Development, Transport and Trade (Maldives), SAARC agreements page"
OMAN_RD = "https://qanoon.om/p/2004/rd2004116/"
UZ_LEX = "https://lex.uz/en/docs/6384452"
UZ_SRO = "https://download1.fbr.gov.pk/SROs/2023313153534123SRO329-2023.pdf"
ID_PERPRES = "https://jdih.kemenkeu.go.id/fullText/2018/114TAHUN2018PERPRES.pdf"
MY_TEXT = "https://fta.miti.gov.my/miti-fta/resources/auto%20download%20images/55892379ea5d1.pdf"
MY_EHP_DAWN = "https://www.dawn.com/news/159157"
CN_MOU = "https://fta.mofcom.gov.cn/upload/agreementFiles/pakistan/xieyi/mywtljbwl_en.pdf"
CN_EHP_ANNEX4 = "https://fta.mofcom.gov.cn/upload/agreementFiles/pakistan/xieyi/annex4.pdf"
CN_SERVICES = "https://fta.mofcom.gov.cn/upload/agreementFiles/pakistan/xieyi/xiedingwenben_en.pdf"

EU_1976 = "21976A0601(01)"
EU_1985 = "21986A0425(01)"
EU_2001 = "22004A1223(03)"

# Record id -> changes. Keys:
#   set: fields to set (None removes the field)
#   prov: list of (field, source, url) provenance entries; they replace existing entries for the same fields
#   links: links to add (url, type)
#   instruments: instruments to add (replacing any with the same id)
#   new: True for a new record (set must hold every required field)
CHANGES: dict[str, dict] = {
    # --- new agreements ---------------------------------------------------------------------------------
    "AZPK": {
        "new": True,
        "set": {
            "name": "Preferential Trade Agreement between the Government of the Republic of Azerbaijan and the "
                    "Government of the Islamic Republic of Pakistan",
            "other_names": [
                {"lang": "en", "name": "Azerbaijan-Pakistan Preferential Trade Agreement"},
                {"lang": "en", "name": "Pakistan-Azerbaijan PTA"},
            ],
            "agreement_type": "pta",
            "status": "in_force",
            "signed": "2024-07-11",
            "in_force": "2024-12-16",
            "parties": country("AZ", "PK"),
            "notes": "Exchanged at Islamabad during the visit of President Ilham Aliyev, together with an agreement "
                     "on transit trade. Pakistan grants its concessions from 16 December 2024 (S.R.O. 2053(I)/2024 "
                     "of 13 December 2024), the date TDAP gives for entry into force. TDAP lists 18 tariff lines "
                     "for Azerbaijan and 17 for Pakistan.",
            "verification": "official",
        },
        "links": [("https://www.commerce.gov.pk/wp-content/uploads/2024/07/Pak-Azerbaijan-PTA.pdf", "treaty_text")],
        "prov": [
            ("name", "Official website of the President of the Republic of Azerbaijan", AZ_SIGNING),
            ("parties", PTAD, ptad("AZE_PAK")),
            ("signed", "Official website of the President of the Republic of Azerbaijan", AZ_SIGNING),
            ("in_force", FBR + " S.R.O. 2053(I)/2024", AZ_SRO),
            ("in_force", PTAD, ptad("AZE_PAK")),
            ("status", PTAD, ptad("AZE_PAK")),
        ],
    },
    "AFPK-EHP": {
        "new": True,
        "set": {
            "name": "Pakistan-Afghanistan Early Harvest Program",
            "agreement_type": "pta",
            "status": "terminated",
            "signed": "2025-07-23",
            "in_force": "2025-08-01",
            "ended": "2026-07-31",
            "parties": country("AF", "PK"),
            "notes": "Signed at Islamabad. Concessions on eight farm products (Pakistan: grapes, "
                     "pomegranates, apples, tomatoes; Afghanistan: mangoes, kinnows, bananas, potatoes) for one "
                     "year, 1 August 2025 to 31 July 2026, extendable by mutual agreement; Pakistan applied them "
                     "by S.R.O. 1386(I)/2025 for the same period. No extension was found on 2026-11-23. It was to "
                     "prepare a preferential trade agreement; the free trade agreement studied since 2005 is AFPK.",
            "verification": "official",
        },
        "prov": [
            ("name", FBR + " S.R.O. 1386(I)/2025", AF_SRO),
            ("parties", FBR + " S.R.O. 1386(I)/2025", AF_SRO),
            ("signed", "Dawn", AF_DAWN),
            ("in_force", FBR + " S.R.O. 1386(I)/2025", AF_SRO),
            ("ended", FBR + " S.R.O. 1386(I)/2025", AF_SRO),
            ("status", FBR + " S.R.O. 1386(I)/2025", AF_SRO),
        ],
    },
    "SATIS": {
        "new": True,
        "set": {
            "name": "SAARC Agreement on Trade in Services",
            "acronyms": [{"lang": "en", "value": "SATIS"}],
            "agreement_type": "services",
            "status": "in_force",
            "signed": "2010-04-29",
            "in_force": "2012-11-29",
            "parties": country("AF", "BD", "BT", "IN", "MV", "NP", "PK", "LK"),
            "notes": "Signed at Thimphu at the sixteenth SAARC Summit. Article 29: it enters into force once all "
                     "Contracting States have ratified it and the SAARC Secretariat has notified this, and it is "
                     "an adjunct to the SAFTA Agreement. The entry-into-force date is the one the Maldives trade "
                     "ministry gave on its SAARC page, which a search index still held on 2026-11-23 after the "
                     "page was taken down; no SAARC Secretariat notice was found.",
            "verification": "catalogue",
        },
        "links": [(SATIS_TEXT, "treaty_text")],
        "prov": [
            ("name", "Department of Commerce (India), trade agreements: text of the agreement", SATIS_TEXT),
            ("parties", "Department of Commerce (India), trade agreements: text of the agreement", SATIS_TEXT),
            ("signed", "Department of Commerce (India), trade agreements: text of the agreement", SATIS_TEXT),
            ("in_force", SATIS_MV_SOURCE, SATIS_MV),
            ("status", SATIS_MV_SOURCE, SATIS_MV),
        ],
    },
    "EUPK-TRA-1976": {
        "new": True,
        "set": {
            "name": "Commercial Cooperation Agreement between the European Economic Community and the Islamic "
                    "Republic of Pakistan",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1976-06-01",
            "in_force": "1976-07-01",
            "parties": [{"id": "EU", "type": "intblock"}, {"id": "PK", "type": "country"}],
            "notes": "Article 2 grants most-favoured-nation treatment under the GATT; it set up a Joint Commission. "
                     "Concluded for five years and extended from year to year. The 1985 agreement (EUPK-TRA-1985) "
                     "does not say that it replaces this one, and EUR-Lex still records it as in force.",
            "verification": "official",
        },
        "links": [(eurlex(EU_1976), "treaty_text")],
        "prov": [
            (field, EURLEX, eurlex(EU_1976)) for field in ("name", "parties", "signed", "in_force", "status")
        ],
    },
    "EUPK-TRA-1985": {
        "new": True,
        "set": {
            "name": "Agreement for commercial, economic and development cooperation between the European Economic "
                    "Community and the Islamic Republic of Pakistan",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1985-07-23",
            "in_force": "1986-05-01",
            "parties": [{"id": "EU", "type": "intblock"}, {"id": "PK", "type": "country"}],
            "notes": "Signed at Brussels. Article 1 grants most-favoured-nation treatment under the GATT. Concluded "
                     "for five years and extended automatically from year to year. The 2001 cooperation agreement "
                     "(EUPK-2001) says relations have developed beyond it but does not end it, and EUR-Lex still "
                     "records it as in force.",
            "verification": "official",
        },
        "links": [(eurlex(EU_1985), "treaty_text")],
        "prov": [
            (field, EURLEX, eurlex(EU_1985)) for field in ("name", "parties", "signed", "in_force", "status")
        ],
    },
    "EUPK-2001": {
        "new": True,
        "set": {
            "name": "Cooperation Agreement between the European Community and the Islamic Republic of Pakistan on "
                    "partnership and development fields",
            "agreement_type": "framework",
            "status": "in_force",
            "signed": "2001-11-24",
            "in_force": "2004-09-01",
            "parties": [{"id": "EU", "type": "intblock"}, {"id": "PK", "type": "country"}],
            "notes": "Signed at Islamabad. Article 3 commits the parties to trade under the WTO Agreement and to "
                     "consult on anti-dumping procedures, without tariff commitments; the agreement also covers "
                     "development cooperation and a Joint Commission. Concluded for five years and renewed yearly.",
            "verification": "official",
        },
        "links": [(eurlex(EU_2001), "treaty_text")],
        "prov": [
            (field, EURLEX, eurlex(EU_2001)) for field in ("name", "parties", "signed", "in_force", "status")
        ],
    },
    "GCCPK-FA": {
        "new": True,
        "set": {
            "name": "Framework Agreement on Economic Cooperation between the States of the Cooperation Council for "
                    "the Arab States of the Gulf and the Islamic Republic of Pakistan",
            "other_names": [
                {"lang": "ar", "name": "الاتفاقية الإطارية للتعاون الاقتصادي بين دول مجلس التعاون لدول الخليج "
                                       "العربية وجمهورية باكستان الإسلامية"},
            ],
            "agreement_type": "framework",
            "status": "signed",
            "signed": "2004-08-26",
            "parties": country("PK", "BH", "KW", "OM", "QA", "SA", "AE"),
            "notes": "Signed at Islamabad. Oman ratified it by Royal Decree 116/2004 of 24 November 2004, together "
                     "with the GCC framework agreement with India. The date it entered into force was not found. "
                     "It led to the free trade agreement negotiations recorded as GCCPK.",
            "verification": "official",
        },
        "prov": [
            ("name", "Qanoon.om, Royal Decree 116/2004 (Official Gazette of the Sultanate of Oman 780)", OMAN_RD),
            ("parties", "Qanoon.om, Royal Decree 116/2004 (Official Gazette of the Sultanate of Oman 780)", OMAN_RD),
            ("signed", "Qanoon.om, Royal Decree 116/2004 (Official Gazette of the Sultanate of Oman 780)", OMAN_RD),
            ("status", "Qanoon.om, Royal Decree 116/2004 (Official Gazette of the Sultanate of Oman 780)", OMAN_RD),
        ],
    },
    # --- corrected records ------------------------------------------------------------------------------
    "PKUZ": {
        "set": {
            "name": "Preferential Trade Agreement between the Government of the Republic of Uzbekistan and the "
                    "Government of the Islamic Republic of Pakistan",
            "other_names": [
                {"lang": "en", "name": "Pakistan-Uzbekistan Preferential Trade Agreement"},
                {"lang": "en", "name": "Pakistan-Uzbekistan PTA"},
            ],
            "signed": "2022-03-03",
            "in_force": "2023-03-13",
            "notes": "Signed at Islamabad. Pakistan grants its concessions from 13 March 2023 (S.R.O. 329(I)/2023). "
                     "ADB ARIC gave only 2023.",
            "verification": "official",
        },
        "links": [(UZ_LEX, "treaty_text")],
        "instruments": [
            instrument(
                "protocol-2026", "amending_protocol",
                "Protocol expanding the product coverage of the Preferential Trade Agreement between the Government "
                "of the Republic of Uzbekistan and the Government of the Islamic Republic of Pakistan",
                "in_force", [(PTAD, ptad("UZB_PAK"))],
                signed="2026-02-05", in_force="2026-08-14", coverage=["goods"],
                notes="Signed at Islamabad under Article 17. Pakistan applies it from 14 August 2026 (S.R.O. "
                      "1349(I)/2026 of 13 August 2026, amending S.R.O. 329(I)/2023): 46 HS-6 items for imports into "
                      "Pakistan and 42 for imports into Uzbekistan.",
            ),
        ],
        "prov": [
            ("name", "National Database of Legislation of the Republic of Uzbekistan (lex.uz)", UZ_LEX),
            ("signed", "National Database of Legislation of the Republic of Uzbekistan (lex.uz)", UZ_LEX),
            ("in_force", "National Database of Legislation of the Republic of Uzbekistan (lex.uz)", UZ_LEX),
            ("in_force", FBR + " S.R.O. 329(I)/2023", UZ_SRO),
            ("status", PTAD, ptad("UZB_PAK")),
            ("notes", FBR + " S.R.O. 329(I)/2023", UZ_SRO),
        ],
    },
    "IDPK": {
        "set": {
            "name": "Preferential Trade Agreement between the Government of the Republic of Indonesia and the "
                    "Government of the Islamic Republic of Pakistan",
            "other_names": [
                {"lang": "en", "name": "Indonesia-Pakistan Preferential Trade Agreement"},
                {"lang": "en", "name": "Indonesia-Pakistan PTA"},
            ],
            "in_force": "2013-09-01",
            "notes": "Done at Jakarta. Pakistan grants its concessions from 1 September 2013 (S.R.O. 741(I)/2013, "
                     "as amended by S.R.O. 1252(I)/2022), the date the WTO RTA database and TDAP give; ADB "
                     "ARIC gave 2013-09-13.",
            "verification": "official",
        },
        "instruments": [
            instrument(
                "protocol-2018", "amending_protocol",
                "Protocol to Amend the Preferential Trade Agreement between the Government of the Republic of "
                "Indonesia and the Government of the Islamic Republic of Pakistan",
                "in_force",
                [("Indonesian Presidential Regulation 114/2018 (JDIH Ministry of Finance)", ID_PERPRES),
                 (WTO, rta(952))],
                signed="2018-01-27", in_force="2019-03-01", coverage=["goods"],
                notes="Signed at Islamabad; Indonesia ratified it by Presidential Regulation 114/2018. It adds tariff "
                      "concessions for 20 Pakistani products.",
            ),
        ],
        "prov": [
            ("name", "Indonesian Presidential Regulation 114/2018 (JDIH Ministry of Finance)", ID_PERPRES),
            ("signed", "Indonesian Presidential Regulation 114/2018 (JDIH Ministry of Finance)", ID_PERPRES),
            ("in_force", WTO, rta(952)),
            ("in_force", PTAD, ptad("IDN_PAK")),
            ("status", WTO, rta(952)),
            ("notes", FBR_ACTIVE, FBR_ACTIVE_URL),
        ],
    },
    "CNPK": {
        "instruments": [
            instrument(
                "early-harvest-2005", "early_harvest",
                "Agreement on the Early Harvest Program for the Free Trade Agreement between China and Pakistan",
                "in_force",
                [(MOFCOM, MOFCOM_PK), (MOFCOM, CN_MOU), (MOFCOM, CN_EHP_ANNEX4), (FBR_ACTIVE, FBR_ACTIVE_URL)],
                signed="2005-04-05", in_force="2006-01-01", coverage=["goods"],
                notes="Signed at Islamabad during the visit of Premier Wen Jiabao, together with the memorandum of "
                      "understanding that launched the FTA negotiations. Annex 4 has it implemented no later than "
                      "1 January 2006, with the last tariff cuts on 1 January 2008; Pakistan applied it by S.R.O. "
                      "1296(I)/2005 of 31 December 2005.",
            ),
            instrument(
                "services-2009", "supplementary_agreement",
                "Agreement on Trade in Services between the Government of the People's Republic of China and the "
                "Government of the Islamic Republic of Pakistan",
                "in_force", [(MOFCOM, CN_SERVICES), (WTO, rta(153))],
                signed="2009-02-21", in_force="2009-10-10", coverage=["services"],
                notes="Signed at Wuhan. A protocol on banking services was signed at Islamabad in April 2015.",
            ),
        ],
    },
    "MYPK": {
        "instruments": [
            instrument(
                "early-harvest-2005", "early_harvest",
                "Agreement on the Early Harvest Programme for the Free Trade Agreement between the Government of "
                "Malaysia and the Government of the Islamic Republic of Pakistan",
                "terminated", [("Ministry of Investment, Trade and Industry (Malaysia), text of the MPCEPA", MY_TEXT),
                               ("Dawn", MY_EHP_DAWN), (FBR_ACTIVE, FBR_ACTIVE_URL)],
                signed="2005-10-01", in_force="2006-01-01", ended="2008-01-01", coverage=["goods"],
                notes="Signed at Kuala Lumpur and applied from 1 January 2006 (Pakistan: S.R.O. 1298(I)/2005). "
                      "Article 134 of the CEPA ended it, with the 1987 trade agreement and the 1995 investment "
                      "agreement, on the day the CEPA entered into force.",
            ),
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
    if change.get("instruments"):
        new_ids = {i["id"] for i in change["instruments"]}
        kept = [i for i in record.get("instruments") or [] if i["id"] not in new_ids]
        record["instruments"] = kept + change["instruments"]
    links = list(record.get("links") or [])
    for url, kind in change.get("links", []):
        if not any(link["url"] == url for link in links):
            links.append({"url": url, "type": kind})
    if links:
        record["links"] = links
    prov = change.get("prov", [])
    if prov:
        fields = {f for f, _, _ in prov}
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
