"""Apply the Turkish Ministry of Trade check (2026-11-23) to data/trade_agreements/.

One-off script. The facts come from the Turkish Ministry of Trade (ticaret.gov.tr, trade.gov.tr):
its pages on FTAs in force, in ratification and in negotiation, on preferential trade agreements
(TTA) and on trade in services agreements, its information note on Türkiye's FTAs, and its news.
The EU-Türkiye ECSC steel agreement comes from EUR-Lex (Publications Office Cellar). A few dates
come from Turkish press and chamber reports where the Ministry pages give only the year; their
provenance names them.

Usage: python scripts/oneoff/apply_turkey_ministry.py [--dry-run]
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote

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

MOT = "Turkish Ministry of Trade"
MOT_EN = "Turkish Ministry of Trade (English site)"
EURLEX = "EUR-Lex (Publications Office Cellar)"


def mot(path: str) -> str:
    return f"https://ticaret.gov.tr/{quote(path)}"


def fta(slug: str) -> str:
    return mot(f"dis-iliskiler/serbest-ticaret-anlasmalari/{slug}")


def eurlex(celex: str) -> str:
    return f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}"


IN_FORCE = "Turkish Ministry of Trade, FTAs in force"
IN_RATIFICATION = "Turkish Ministry of Trade, FTAs in ratification"
TTA = "Turkish Ministry of Trade, preferential trade agreements"
TTA_URL = mot("dis-iliskiler/tercihli-ticaret-anlasmalari")
SERVICES = "Turkish Ministry of Trade, trade in services agreements"
SERVICES_URL = mot("dis-iliskiler/hizmet-ticareti-anlasmalari")
NOTE = "Turkish Ministry of Trade, information note on Türkiye's free trade agreements"
NOTE_URL = mot("data/5b872ada13b8761450e18f4b/Türkiye'ninSTA'ları.docx")
NEGOTIATIONS = "Turkish Ministry of Trade, FTA negotiations in progress (page of 2 August 2024)"
NEGOTIATIONS_URL = fta("muzakere-sureci-devam-eden-stalar")
EN_FTA = "Turkish Ministry of Trade (English site), free trade agreements"
EN_FTA_URL = "https://www.trade.gov.tr/free-trade-agreements"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in codes]


def instrument(id_: str, kind: str, name: str, status: str, prov: list[tuple[str, str]], **extra) -> dict:
    item = {"id": id_, "kind": kind, "name": name, "status": status, **extra}
    item["provenance"] = [
        {"field": "instruments", "source": source, "url": url, "retrieved_at": TODAY} for source, url in prov
    ]
    return {k: item[k] for k in INSTRUMENT_ORDER if k in item}


def stalled_fta(partner: str, codes: tuple[str, ...]) -> dict:
    return {
        "new": True,
        "set": {
            "name": f"{partner}-Türkiye Free Trade Agreement",
            "agreement_type": "fta",
            "status": "negotiating",
            "parties": country(*codes),
            "notes": STALLED_NOTE,
            "verification": "official",
        },
        "prov": [
            ("parties", NOTE, NOTE_URL),
            ("status", NOTE, NOTE_URL),
            ("notes", NEGOTIATIONS, NEGOTIATIONS_URL),
        ],
    }


STALLED_NOTE = (
    "The Ministry of Trade's information note on Türkiye's FTAs lists it among the FTA negotiations formally "
    "launched with ten countries or groups, where the Ministry works to speed the process up. Its page on "
    "negotiations in progress (2 August 2024) names active negotiations only with Japan, Indonesia and the GCC."
)

# Record id -> changes. Keys:
#   set: fields to set (None removes the field)
#   prov: list of (field, source, url) provenance entries; they replace existing entries for the same fields
#   links: links to add (url, type)
#   instruments: instruments to add (replacing any with the same id)
#   new: True for a new record (set must hold every required field)
CHANGES: dict[str, dict] = {
    # --- new agreements in force or signed --------------------------------------------------------------
    "QATR": {
        "new": True,
        "set": {
            "name": "Trade and Economic Partnership Agreement between the Government of the Republic of Türkiye "
                    "and the Government of the State of Qatar",
            "acronyms": [{"lang": "en", "value": "TEPA"}],
            "other_names": [
                {"lang": "tr", "name": "Türkiye Cumhuriyeti Hükümeti ile Katar Devleti Hükümeti Arasında Ticaret ve "
                                       "Ekonomik Ortaklık Anlaşması"},
                {"lang": "en", "name": "Türkiye-Qatar Trade and Economic Partnership Agreement"},
            ],
            "agreement_type": "fta",
            "status": "in_force",
            "signed": "2018-11-26",
            "in_force": "2025-08-01",
            "parties": country("QA", "TR"),
            "notes": "Covers trade in goods, trade in services (with financial services and telecommunications "
                     "annexes) and e-commerce. Türkiye approved the agreement and the notes amending it by "
                     "Presidential Decision No. 8448, published in the Resmî Gazete No. 32545 of 13 May 2024.",
            "verification": "official",
        },
        "links": [(fta("yururlukte-bulunan-stalar/katar"), "website")],
        "prov": [
            ("parties", IN_FORCE, fta("yururlukte-bulunan-stalar/katar")),
            ("signed", MOT, mot("data/688a1b4313b876cb2c1efab6/Katar Bilgi Notu.pdf")),
            ("in_force", IN_FORCE, fta("yururlukte-bulunan-stalar/katar")),
            ("status", IN_FORCE, fta("yururlukte-bulunan-stalar/katar")),
            ("notes", IN_FORCE, fta("yururlukte-bulunan-stalar/katar")),
        ],
    },
    "SDTR": {
        "new": True,
        "set": {
            "name": "Türkiye-Sudan Trade and Economic Partnership Agreement",
            "other_names": [{"lang": "tr", "name": "Türkiye-Sudan Ticaret ve Ekonomik Ortaklık Anlaşması"}],
            "agreement_type": "fta",
            "status": "signed",
            "signed": "2017-12-24",
            "parties": country("SD", "TR"),
            "notes": "Signed in Khartoum by the Turkish Minister of Economy and the Sudanese Minister of Trade. It "
                     "enters into force once both parties complete ratification; the Ministry of Trade lists it "
                     "among FTAs in ratification.",
            "verification": "official",
        },
        "links": [(fta("onay-sureci-devam-eden-stalar/sudan"), "website")],
        "prov": [
            ("parties", IN_RATIFICATION, fta("onay-sureci-devam-eden-stalar/sudan")),
            ("signed", IN_RATIFICATION, fta("onay-sureci-devam-eden-stalar/sudan")),
            ("status", IN_RATIFICATION, fta("onay-sureci-devam-eden-stalar")),
            ("notes", MOT, mot("data/5c3c3a5013b87620f0628c6c/Sudan-Web Sitesi Notu.docx")),
        ],
    },
    "IRTR": {
        "new": True,
        "set": {
            "name": "Preferential Trade Agreement between the Government of the Republic of Turkey and the "
                    "Government of the Islamic Republic of Iran",
            "other_names": [{"lang": "en", "name": "Iran-Türkiye Preferential Trade Agreement"}],
            "agreement_type": "pta",
            "status": "in_force",
            "signed": "2014-01-29",
            "in_force": "2015-01-01",
            "parties": country("IR", "TR"),
            "notes": "Signed by the Turkish Minister of Economy and the Iranian Minister of Industry, Mines and "
                     "Trade. Türkiye's approval was published in the Resmî Gazete No. 29165 of 4 November 2014. "
                     "The Ministry of Trade lists it among Türkiye's preferential trade agreements in force since "
                     "2015.",
            "verification": "official",
        },
        "links": [(mot("data/62bda27513b8763814c5165a/İran TTA.zip.zip"), "treaty_text")],
        "prov": [
            ("parties", TTA, TTA_URL),
            ("status", TTA, TTA_URL),
            ("signed", "Bursa Chamber of Commerce and Industry (BTSO), Iran country report 2024",
             "https://butso.org.tr/belgeler/2024/ULKE_RAPORLARI/iran-ulke-raporu-2024.pdf"),
            ("in_force", "Dünya, report of 1 January 2015 on the agreement entering into force that day",
             "https://www.dunya.com/ekonomi/turkiye-ve-iran-gumruk-vergilerini-dusurdu-haberi-267318"),
            ("notes", "Bursa Chamber of Commerce and Industry (BTSO), Iran country report 2024",
             "https://butso.org.tr/belgeler/2024/ULKE_RAPORLARI/iran-ulke-raporu-2024.pdf"),
        ],
    },
    "EUTR-ECSC": {
        "new": True,
        "set": {
            "name": "Agreement between the European Coal and Steel Community and the Republic of Turkey on trade in "
                    "products covered by the Treaty establishing the European Coal and Steel Community",
            "other_names": [{"lang": "en", "name": "ECSC-Türkiye Agreement on trade in steel products"}],
            "agreement_type": "fta",
            "status": "in_force",
            "signed": "1996-07-25",
            "in_force": "1996-08-01",
            "parties": [{"id": "EU", "type": "intblock"}, {"id": "TR", "type": "country"}],
            "notes": "Free trade in the coal and steel products of the ECSC Treaty, which the customs union (EUTR) "
                     "does not cover. The EU took it over when the ECSC Treaty expired in 2002; EUR-Lex lists it as "
                     "still valid (CELEX 21996A0907(01)).",
            "verification": "official",
        },
        "instruments": [
            instrument(
                "decision-1999-2", "joint_committee_decision",
                "Decision No 2/99 of the Joint Committee of 8 July 1999 amending Protocol 1 of the Agreement",
                "terminated", [(EURLEX, eurlex("21999D0812(01)"))],
                signed="1999-07-08", in_force="1999-07-08", ended="2009-03-01", coverage=["goods"],
                notes="EUR-Lex also gives 1 January 1999 as a date of entry into force, and 1 March 2009 as the "
                      "end of validity, when Decision No 1/2009 applied.",
            ),
            instrument(
                "decision-2009-1", "joint_committee_decision",
                "Decision No 1/2009 of the Joint Committee of 24 February 2009 amending Protocol 1 to the Agreement",
                "in_force", [(EURLEX, eurlex("22009D0403"))],
                signed="2009-02-24", in_force="2009-03-01", coverage=["goods"],
            ),
            instrument(
                "decision-2025-1", "joint_committee_decision",
                "Decision No 1/2025 of the EU-Türkiye Joint Committee of 22 December 2025 replacing Protocol 1 "
                "concerning the definition of the concept of originating products and methods of administrative "
                "cooperation",
                "in_force", [(EURLEX, eurlex("22026D0359"))],
                signed="2025-12-22", in_force="2025-12-22", coverage=["goods"],
            ),
        ],
        "links": [(eurlex("21996A0907(01)"), "website")],
        "prov": [
            ("parties", EURLEX, eurlex("21996A0907(01)")),
            ("signed", EURLEX, eurlex("21996A0907(01)")),
            ("in_force", EURLEX, eurlex("21996X0907(01)")),
            ("status", EURLEX, eurlex("21996A0907(01)")),
            ("notes", EURLEX, eurlex("21996A0907(01)")),
        ],
    },
    # --- new negotiations ---------------------------------------------------------------------------------
    "DZTR": {
        "new": True,
        "set": {
            "name": "Algeria-Türkiye Preferential Trade Agreement",
            "agreement_type": "pta",
            "status": "negotiating",
            "parties": country("DZ", "TR"),
            "verification": "official",
        },
        "prov": [("parties", TTA, TTA_URL), ("status", TTA, TTA_URL)],
    },
    "MXTR": stalled_fta("Mexico", ("MX", "TR")),
    "PETR": stalled_fta("Peru", ("PE", "TR")),
    "COTR": stalled_fta("Colombia", ("CO", "TR")),
    "ECTR": stalled_fta("Ecuador", ("EC", "TR")),
    "CMTR": stalled_fta("Cameroon", ("CM", "TR")),
    "MERCOSURTR": {
        **stalled_fta("MERCOSUR", ("AR", "BR", "PY", "UY", "TR")),
    },
    "BYTR": {
        "new": True,
        "set": {
            "name": "Belarus-Türkiye Trade in Services Agreement",
            "agreement_type": "services",
            "status": "negotiating",
            "parties": country("BY", "TR"),
            "notes": "A services-only agreement: the customs union with the EU keeps Türkiye from negotiating an FTA "
                     "on trade in goods with Belarus.",
            "verification": "official",
        },
        "prov": [("parties", SERVICES, SERVICES_URL), ("status", SERVICES, SERVICES_URL),
                 ("notes", SERVICES, SERVICES_URL)],
    },
    "RUTR": {
        "new": True,
        "set": {
            "name": "Russia-Türkiye Trade in Services Agreement",
            "agreement_type": "services",
            "status": "proposed",
            "parties": country("RU", "TR"),
            "notes": "The Ministry of Trade reports talks with Russia on an agreement like the one it negotiates "
                     "with Belarus (BYTR).",
            "verification": "official",
        },
        "prov": [("parties", SERVICES, SERVICES_URL), ("status", SERVICES, SERVICES_URL),
                 ("notes", SERVICES, SERVICES_URL)],
    },
    "KZTR": {
        "new": True,
        "set": {
            "name": "Kazakhstan-Türkiye Trade in Services Agreement",
            "agreement_type": "services",
            "status": "proposed",
            "parties": country("KZ", "TR"),
            "notes": "The Ministry of Trade reports talks with Kazakhstan on an agreement like the one it negotiates "
                     "with Belarus (BYTR).",
            "verification": "official",
        },
        "prov": [("parties", SERVICES, SERVICES_URL), ("status", SERVICES, SERVICES_URL),
                 ("notes", SERVICES, SERVICES_URL)],
    },
    "TRUZ-DIGITAL": {
        "new": True,
        "set": {
            "name": "Türkiye-Uzbekistan Digital Trade Agreement",
            "agreement_type": "digital",
            "status": "negotiating",
            "parties": country("TR", "UZ"),
            "verification": "official",
        },
        "prov": [("parties", SERVICES, SERVICES_URL), ("status", SERVICES, SERVICES_URL)],
    },
    # --- status and date corrections ----------------------------------------------------------------------
    "TRUA": {
        "set": {
            "status": "in_force",
            "signed": "2022-02-03",
            "in_force": "2026-10-01",
            "notes": "Signed in Kyiv. Türkiye completed ratification by a Presidential Decision published on "
                     "4 October 2024, Ukraine when its President approved it on 31 July 2026. The tariff reductions "
                     "in the goods schedules apply from 1 January 2027.",
            "verification": "official",
        },
        "links": [
            (fta("yururlukte-bulunan-stalar/ukrayna"), "website"),
            (mot("data/6abe634f269de1cd603cdd65/Türkiye-Ukrayna STA.pdf"), "treaty_text"),
        ],
        "prov": [
            ("signed", IN_FORCE, fta("yururlukte-bulunan-stalar/ukrayna")),
            ("in_force", IN_FORCE, fta("yururlukte-bulunan-stalar/ukrayna")),
            ("status", IN_FORCE, fta("yururlukte-bulunan-stalar/ukrayna")),
            ("notes", IN_FORCE, fta("yururlukte-bulunan-stalar/ukrayna")),
        ],
    },
    "PKTR": {
        "set": {
            "name": "Trade in Goods Agreement between the Republic of Türkiye and the Islamic Republic of Pakistan",
            "other_names": [
                {"lang": "en", "name": "Pakistan-Türkiye Preferential Trade Agreement"},
                {"lang": "en", "name": "Pakistan-Türkiye PTA"},
                {"lang": "tr", "name": "Türkiye-Pakistan Mal Ticareti Anlaşması"},
            ],
            "status": "in_force",
            "signed": "2022-08-12",
            "in_force": "2023-05-01",
            "notes": "Signed in Islamabad. It builds on the Framework Agreement Establishing a Free Trade Area "
                     "between Türkiye and Pakistan, signed in Islamabad on 22 March 2016. The Ministry of Trade lists "
                     "it among Türkiye's preferential trade agreements. ADB ARIC gave July 2022 for signature.",
            "verification": "official",
        },
        "links": [(mot("data/62bda27513b8763814c5165a/Pakistan_MTA.zip"), "treaty_text")],
        "prov": [
            ("name", TTA, mot("data/62bda27513b8763814c5165a/Pakistan_MTA.zip")),
            ("signed", MOT, mot("haberler/turkiye-ile-pakistan-arasinda-mal-ticaret-anlasmasi-imzalandi")),
            ("in_force", TTA, TTA_URL),
            ("status", TTA, TTA_URL),
            ("notes", TTA, mot("data/62bda27513b8763814c5165a/Pakistan_MTA.zip")),
        ],
    },
    "TRUZ": {
        "set": {"in_force": "2023-07-01", "verification": "official"},
        "links": [(mot("data/62bda27513b8763814c5165a/Özbekistan TTA.zip"), "treaty_text")],
        "prov": [("in_force", TTA, TTA_URL), ("status", TTA, TTA_URL)],
    },
    "AZTR": {
        "set": {"signed": "2020-02-25", "verification": "official"},
        "instruments": [
            instrument(
                "protocol-2023", "amending_protocol",
                "Protocol Amending the Preferential Trade Agreement between the Government of the Republic of "
                "Türkiye and the Government of the Republic of Azerbaijan",
                "in_force",
                [(MOT, mot("haberler/turkiye-azerbaycan-tercihli-ticaret-antlasmasi-imzalandi")), (TTA, TTA_URL)],
                signed="2023-04-29", in_force="2024-07-01", coverage=["goods"],
                notes="Signed in Samsun. Adds agricultural and industrial products to the concessions of the "
                      "Agreement.",
            ),
        ],
        "links": [(mot("data/62bda27513b8763814c5165a/AZ TTA.zip"), "treaty_text")],
        "prov": [
            ("signed", "Turkish Ministry of Trade, text of the 2023 Protocol amending the Agreement",
             mot("data/62bda27513b8763814c5165a/Azerbaycan TTA Ek Protokoller.zip")),
            ("in_force", TTA, TTA_URL),
            ("status", TTA, TTA_URL),
        ],
    },
    "KRTR": {
        "set": {"verification": "official"},
        "instruments": [
            instrument(
                "services-2015", "supplementary_agreement",
                "Agreement on Trade in Services between the Republic of Turkey and the Republic of Korea",
                "in_force", [(EN_FTA, "https://www.trade.gov.tr/free-trade-agreements/republic-of-korea"),
                             (IN_FORCE, fta("yururlukte-bulunan-stalar/guney-kore"))],
                signed="2015-02-26", in_force="2018-08-01", coverage=["services"],
            ),
            instrument(
                "investment-2015", "supplementary_agreement",
                "Agreement on Investment between the Republic of Turkey and the Republic of Korea",
                "in_force", [(EN_FTA, "https://www.trade.gov.tr/free-trade-agreements/republic-of-korea"),
                             (IN_FORCE, fta("yururlukte-bulunan-stalar/guney-kore"))],
                signed="2015-02-26", in_force="2018-08-01", coverage=["investment"],
            ),
        ],
        "prov": [
            ("signed", EN_FTA, "https://www.trade.gov.tr/free-trade-agreements/republic-of-korea"),
            ("in_force", IN_FORCE, fta("yururlukte-bulunan-stalar/guney-kore")),
        ],
    },
    "MYTR": {
        "instruments": [
            instrument(
                "revised-protocol-1-2022", "amending_protocol",
                "Revised Protocol No. 1 expanding the scope of the Türkiye-Malaysia Free Trade Agreement to trade in "
                "services and investment",
                "in_force", [(IN_FORCE, fta("yururlukte-bulunan-stalar/malezya"))],
                signed="2022-09-29", in_force="2024-08-01", coverage=["services", "investment"],
            ),
        ],
    },
    "GETR": {
        "set": {
            "in_force": "2008-11-01",
            "notes": "Signed in Tbilisi and published in the Resmî Gazete No. 27007 of 24 September 2008. The "
                     "Ministry of Trade gives 1 November 2008 for entry into force; the record held 2008-01-11 from "
                     "ADB ARIC.",
            "verification": "official",
        },
        "instruments": [
            instrument(
                "expansion-protocols", "amending_protocol",
                "Protocols expanding the scope of the Türkiye-Georgia Free Trade Agreement",
                "signed",
                [(IN_FORCE, fta("yururlukte-bulunan-stalar")),
                 ("Caliber.az, report of 9 September 2022 quoting the Georgian Ministry of Economy and Sustainable "
                  "Development",
                  "https://caliber.az/en/post/georgia-to-export-some-agricultural-products-to-turkiye-at-zero-tariff")],
                signed="2022-09-09", coverage=["goods", "services"],
                notes="Signed in Tbilisi by the Georgian Minister of Economy and Sustainable Development and the "
                      "Turkish Minister of Trade. They add trade in services and further agricultural concessions. "
                      "The Ministry of Trade reports them signed and awaiting ratification.",
            ),
        ],
        "prov": [
            ("signed", IN_FORCE, fta("yururlukte-bulunan-stalar/gurcistan")),
            ("in_force", IN_FORCE, fta("yururlukte-bulunan-stalar/gurcistan")),
            ("notes", IN_FORCE, fta("yururlukte-bulunan-stalar/gurcistan")),
        ],
    },
    "BATR": {
        "set": {
            "in_force": "2021-08-01",
            "notes": "The revised FTA replaced the 2002 agreement (BATR-2002). The record held 2003 for entry into "
                     "force from ADB ARIC, the year the 2002 agreement entered into force.",
            "verification": "official",
        },
        "prov": [
            ("signed", IN_FORCE, fta("yururlukte-bulunan-stalar/bosna-hersek")),
            ("in_force", IN_FORCE, fta("yururlukte-bulunan-stalar/bosna-hersek")),
            ("status", IN_FORCE, fta("yururlukte-bulunan-stalar/bosna-hersek")),
            ("notes", IN_FORCE, fta("yururlukte-bulunan-stalar/bosna-hersek")),
        ],
    },
    "SYTR": {
        "set": {
            "notes": "EDIT gives 2004-12-22 as the date of signature. Türkiye suspended the agreement on "
                     "6 December 2011; the Ministry of Trade does not count it among the FTAs in force.",
        },
        "prov": [
            ("notes", "EDIT - Electronic Database of Investment Treaties (World Trade Institute)",
             "https://edit.wti.org/document/show/f5a5a32f-928e-4ccf-b822-5bd8f210cd6b"),
            ("notes", EN_FTA, EN_FTA_URL),
        ],
    },
    "MVTR": {
        "set": {
            "name": "Maldives-Türkiye Preferential Trade Agreement",
            "other_names": [
                {"lang": "en", "name": "Maldives-Türkiye Free Trade Agreement"},
                {"lang": "en", "name": "Maldives-Türkiye FTA"},
            ],
            "agreement_type": "pta",
            "notes": "The Ministry of Trade lists it as a preferential trade agreement (TTA) in internal ratification; "
                     "ADB ARIC calls it a free trade agreement.",
            "verification": "official",
        },
        "prov": [
            ("name", TTA, TTA_URL),
            ("status", TTA, TTA_URL),
            ("notes", TTA, TTA_URL),
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
