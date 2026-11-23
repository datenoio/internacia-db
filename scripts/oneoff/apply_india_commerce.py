"""Apply the India Department of Commerce walk (2026-11-23) to data/trade_agreements/.

One-off script. The Department of Commerce lists India's trade agreements, with their texts, in
a JSON API (https://www.commerce.gov.in/ministryofcommerce/api/v1/international-trade/trade-agreements,
plus the sub-pages ``india-africa-trade-agreement`` and ``india-asean-agreements``). Dates come
from the texts; entry into force and current status come from the Press Information Bureau (PIB),
the partner governments, the depositaries and the treaty registers named in each record. Agreements
whose current status no official source states are held, not written; see docs/intblock-sources.md
(India Department of Commerce row) and the pull request body.

Usage: python scripts/oneoff/apply_india_commerce.py [--dry-run]
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
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by", "parent",
    "wto_rta_id", "aric_id", "unctad_iia_id", "unts_registration", "wto_pta_ids", "gptad_id", "dta_id",
    "wikidata_id", "links", "description", "notes", "instruments", "verification", "last_verified",
    "provenance",
]

DOC = "Department of Commerce, Government of India, trade agreements"
DOC_LIST = "https://www.commerce.gov.in/ministryofcommerce/api/v1/international-trade/trade-agreements"
DOC_AFRICA = DOC_LIST + "/india-africa-trade-agreement"
PIB = "Press Information Bureau, Government of India"
ASEAN = "ASEAN Secretariat, legal instruments with external parties"
ARIC = "Asia Regional Integration Center (ADB), FTA database"


def doc_file(path: str) -> str:
    return f"https://www.commerce.gov.in/files/{path}"


def pib(prid: str) -> str:
    return f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"


def country(*codes: str) -> list[dict]:
    return [{"id": c, "type": "country"} for c in codes]


# Record id -> changes. Keys:
#   set: fields to set (None removes the field)
#   prov: list of (field, source, url) provenance entries; they replace existing entries for the same fields
#   drop_prov: further provenance fields to drop
#   keep_prov: True to add the prov entries next to existing ones for the same fields
#   links: links to add (url, type)
#   instruments: instruments to append (dicts in schema order)
#   new: True for a new record (set must hold every required field)
CHANGES: dict[str, dict] = {
    # --- South Asia -------------------------------------------------------------------------------
    "SATIS": {
        # Added at catalogue level by the Pakistan TDAP walk; the SAARC Secretariat note confirms it.
        "set": {
            "notes": "Signed at Thimphu at the sixteenth SAARC Summit. Article 29: it enters into force once all "
                     "Contracting States have ratified it and the SAARC Secretariat has notified this, and it is an "
                     "adjunct to the SAFTA Agreement. A SAARC Secretariat note states that all member states ratified "
                     "it and that it entered into force on 29 November 2012, the date the Maldives trade ministry and "
                     "the Nepalese foreign ministry also give. The schedules of specific commitments were still under "
                     "negotiation.",
            "verification": "official",
        },
        "keep_prov": True,
        "prov": [
            ("in_force", "SAARC Secretariat, note on regional cooperation in trade facilitation (hosted by UN ESCAP)",
             "https://www.unescap.org/sites/default/files/SAARC%20ROC-TF.pdf"),
            ("status", "Ministry of Foreign Affairs of Nepal, Nepal and SAARC",
             "https://mofa.gov.np/pages/nepal-and-saarc-5/"),
        ],
    },
    "BTIN": {
        "set": {
            "status": "superseded",
            "ended": "2017-07-29",
            "superseded_by": "BTIN-2016",
            "notes": "The 2006 agreement ran for ten years from 29 July 2006. India and Bhutan extended it from 29 July "
                     "2016 for one year or until the new Agreement on Trade, Commerce and Transit (BTIN-2016) entered "
                     "into force, which it did on 29 July 2017.",
        },
        "prov": [
            ("ended", PIB, "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=169333"),
            ("superseded_by", PIB, "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=169333"),
        ],
    },
    "BTIN-2016": {
        "new": True,
        "set": {
            "name": "Agreement on Trade, Commerce and Transit between the Government of the Republic of India and the "
                    "Royal Government of Bhutan",
            "other_names": [{"lang": "en", "name": "India-Bhutan Agreement on Trade, Commerce and Transit"}],
            "agreement_type": "pta",
            "status": "in_force",
            "signed": "2016-11-12",
            "in_force": "2017-07-29",
            "parties": country("BT", "IN"),
            "supersedes": "BTIN",
            "notes": "Signed at Thimphu. It keeps the free trade regime between the two countries and runs for ten "
                     "years; it may be renewed by mutual consent. In September 2026 the two governments were "
                     "discussing its renewal.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/MOC_636404697883366996_Agreement_between_India_Bhutan_12th_Nov_2016.pdf"),
                   "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/MOC_636404697883366996_Agreement_between_India_Bhutan_12th_Nov_2016.pdf")),
            ("signed", DOC, doc_file("2025-01/MOC_636404697883366996_Agreement_between_India_Bhutan_12th_Nov_2016.pdf")),
            ("in_force", PIB, "https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=169333"),
            ("status", "Ministry of Foreign Affairs and External Trade of Bhutan, joint press release (September 2026)",
             "https://www.mfa.gov.bt/18141-2/"),
        ],
    },
    "INNP": {
        "set": {
            "status": "superseded",
            "ended": "2009-10-27",
            "superseded_by": "INNP-2009",
            "notes": "The Treaty of Trade of 6 December 1991, as amended. The revised treaty signed on 27 October 2009 "
                     "(INNP-2009) superseded it on signature.",
        },
        "prov": [
            ("ended", DOC, doc_file("2025-01/nepal.pdf")),
            ("superseded_by", DOC, doc_file("2025-01/nepal.pdf")),
        ],
    },
    "INNP-2009": {
        "new": True,
        "set": {
            "name": "Revised Treaty of Trade between the Government of India and the Government of Nepal",
            "other_names": [{"lang": "en", "name": "Revised Indo-Nepal Treaty of Trade"}],
            "agreement_type": "pta",
            "status": "in_force",
            "signed": "2009-10-27",
            "in_force": "2009-10-27",
            "parties": country("IN", "NP"),
            "supersedes": "INNP",
            "notes": "Signed at Kathmandu; in force on signature for seven years, renewed automatically for further "
                     "seven-year periods (renewed in October 2016 and October 2023). It gives Nepal duty-free access "
                     "to the Indian market for most goods.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/nepal.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/nepal.pdf")),
            ("signed", DOC, doc_file("2025-01/nepal.pdf")),
            ("in_force", DOC, doc_file("2025-01/nepal.pdf")),
            ("status", "Embassy of India, Kathmandu, commerce wing brief",
             "https://www.indembkathmandu.gov.in/commerce-wing-brief"),
        ],
    },
    "BDIN-TRA-2015": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of the Republic of India and the Government of the "
                    "People's Republic of Bangladesh",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "2015-06-06",
            "in_force": "2015-04-01",
            "parties": country("BD", "IN"),
            "notes": "Signed at Dhaka; valid for five years from 1 April 2015 and extended automatically for further "
                     "five-year terms. It renewed the bilateral trade agreement first signed on 28 March 1972 and "
                     "revised in 1980 and 2006, which the registry does not record separately.",
            "verification": "official",
        },
        "links": [(doc_file("2026-01/Trade%20Agreement%20%20Indo-Bangladesh%20%5B2015%5D.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2026-01/Trade%20Agreement%20%20Indo-Bangladesh%20%5B2015%5D.pdf")),
            ("signed", DOC, doc_file("2026-01/Trade%20Agreement%20%20Indo-Bangladesh%20%5B2015%5D.pdf")),
            ("in_force", DOC, doc_file("2026-01/Trade%20Agreement%20%20Indo-Bangladesh%20%5B2015%5D.pdf")),
            ("status", DOC, DOC_LIST),
        ],
    },
    "INMV-TRA": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of the Republic of India and the Government of the "
                    "Republic of Maldives",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1981-03-31",
            "in_force": "1981-03-31",
            "parties": country("IN", "MV"),
            "notes": "Signed at Malé. In force for one year and thereafter until modified or terminated on three "
                     "months' notice. The Department of Commerce still lists it among India's trade agreements.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/maldives.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/maldives.pdf")),
            ("signed", DOC, doc_file("2025-01/maldives.pdf")),
            ("in_force", DOC, doc_file("2025-01/maldives.pdf")),
            ("status", DOC, DOC_LIST),
        ],
    },
    "INMN-TRA-1996": {
        "new": True,
        "set": {
            "name": "Agreement between the Government of the Republic of India and the Government of Mongolia on "
                    "Trade and Economic Cooperation",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1996-09-16",
            "in_force": "1996-09-16",
            "parties": country("IN", "MN"),
            "notes": "Signed at Ulaanbaatar; in force on signature for an indefinite period, terminable on six months' "
                     "notice. It terminated the India-Mongolia Trade Agreement of 8 February 1978, which the "
                     "registry does not record separately.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/mongolio.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/mongolio.pdf")),
            ("signed", DOC, doc_file("2025-01/mongolio.pdf")),
            ("in_force", DOC, doc_file("2025-01/mongolio.pdf")),
            ("status", DOC, DOC_LIST),
        ],
    },
    "INPK-TRA": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of Pakistan and the Government of India",
            "agreement_type": "trade_relations",
            "status": "terminated",
            "signed": "1975-01-23",
            "in_force": "1975-01-23",
            "ended": "1978-01-22",
            "parties": country("IN", "PK"),
            "notes": "Signed at Islamabad; in force on signature for one year "
                     "and extended automatically once, for two years. It has no further renewal clause and lapsed "
                     "in January 1978.",
            "verification": "official",
        },
        "links": [(doc_file("2026-01/India%20Pakistan.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2026-01/India%20Pakistan.pdf")),
            ("signed", DOC, doc_file("2026-01/India%20Pakistan.pdf")),
            ("in_force", DOC, doc_file("2026-01/India%20Pakistan.pdf")),
            ("ended", DOC, doc_file("2026-01/India%20Pakistan.pdf")),
        ],
    },
    # --- Oman ---------------------------------------------------------------------------------------
    "INOM": {
        "set": {
            "name": "India-Oman Comprehensive Economic Partnership Agreement",
            "acronyms": [{"lang": "en", "value": "India-Oman CEPA"}],
            "other_names": [{"lang": "en", "name": "India-Oman Free Trade Agreement"}],
            "status": "in_force",
            "signed": "2025-12-18",
            "in_force": "2026-06-01",
            "notes": "Signed at Muscat.",
            "verification": "official",
        },
        "drop_prov": ["notes"],
        "prov": [
            ("signed", PIB, pib("2267513")),
            ("in_force", PIB, pib("2267513")),
            ("status", PIB, pib("2268595")),
        ],
    },
    # --- ASEAN --------------------------------------------------------------------------------------
    "AIFTA": {
        "instruments": [
            {
                "id": "services-2014",
                "kind": "supplementary_agreement",
                "name": "Agreement on Trade in Services under the Framework Agreement on Comprehensive Economic "
                        "Cooperation between the Association of Southeast Asian Nations and the Republic of India",
                "status": "in_force",
                "signed": "2014-11-13",
                "in_force": "2015-07-01",
                "coverage": ["services"],
                "notes": "Signed at Nay Pyi Taw. In force on 1 July 2015 for the first parties and sixty days after "
                         "notification for the others (Article 32); Indonesia notified last, on 21 December 2018.",
                "provenance": [
                    {"field": "instruments", "source": ASEAN, "url": "https://asean.org/?p=175386",
                     "retrieved_at": TODAY},
                    {"field": "instruments", "source": DOC, "url": DOC_LIST + "/india-asean-agreements",
                     "retrieved_at": TODAY},
                ],
            },
            {
                "id": "investment-2014",
                "kind": "supplementary_agreement",
                "name": "Agreement on Investment under the Framework Agreement on Comprehensive Economic Cooperation "
                        "between the Association of Southeast Asian Nations and the Republic of India",
                "status": "in_force",
                "signed": "2014-11-12",
                "in_force": "2015-07-01",
                "coverage": ["investment"],
                "notes": "Signed at Nay Pyi Taw. In force on 1 July 2015 for the first parties; Cambodia notified "
                         "last, on 21 January 2021.",
                "provenance": [
                    {"field": "instruments", "source": ASEAN,
                     "url": "https://asean.org/dialogue-partners/framework-agreement-on-comprehensive-economic-"
                            "cooperation-between-the-association-of-southeast-asian-nations-and-the-republic-of-lndia/"
                            "agreement-on-investment-under-the-framework-agreement-on-comprehensive-economic-"
                            "cooperation-between-the-association-of-southeast-asian-nations-and-the-republic-of-india/",
                     "retrieved_at": TODAY},
                    {"field": "instruments", "source": DOC, "url": DOC_LIST + "/india-asean-agreements",
                     "retrieved_at": TODAY},
                ],
            },
        ],
    },
    # --- Latin America ------------------------------------------------------------------------------
    "MERCOSURIN-FA": {
        "new": True,
        "set": {
            "name": "Framework Agreement between the MERCOSUR and the Republic of India",
            "agreement_type": "framework",
            "status": "signed",
            "signed": "2003-06-17",
            "parties": country("AR", "BR", "PY", "UY", "IN"),
            "notes": "Signed at Asunción. It foresaw a preferential trade agreement as a first step towards a free "
                     "trade area; that agreement (INDIAMERCOSURPTA) was signed in 2004 and entered into force in "
                     "2009. The depositary, Paraguay, lists the framework agreement as pending India's ratification "
                     "(Brazil notified on 2003-07-03, Paraguay on 2006-02-14, Uruguay on 2006-07-26, Argentina "
                     "ratified on 2009-10-27). Brazil's Concórdia database marks it in force for Brazil only.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/Framework_Agreeement_MERCOSUR.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/Framework_Agreeement_MERCOSUR.pdf")),
            ("signed", DOC, doc_file("2025-01/Framework_Agreeement_MERCOSUR.pdf")),
            ("status", "Ministry of Foreign Affairs of Paraguay (MERCOSUR depositary), treaty database",
             "https://www.mre.gov.py/tratados/public_web/ConsultaMercosur.aspx?id=483"),
            ("notes", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_multi_ficha.php?id=mqSl"),
        ],
    },
    "ARIN-TRA": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of the Republic of India and the Government of the "
                    "Argentine Republic",
            "agreement_type": "trade_relations",
            "status": "terminated",
            "signed": "1966-03-26",
            "in_force": "1967-05-26",
            "ended": "1970-05-26",
            "parties": country("AR", "IN"),
            "unts_registration": "I-8697",
            "notes": "Signed at New Delhi. In force for two years from the exchange of ratifications, extended once "
                     "for one year; it expired on 1970-05-26 (Argentina: \"vence el plazo del Convenio\").",
            "verification": "official",
        },
        "links": [
            (doc_file("2025-01/MOC_637117634515656361_Trade-Agreement-with-Argentina-1966.pdf"), "treaty_text"),
            ("https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKimA==", "website"),
            ("https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280129661", "website"),
        ],
        "prov": [
            ("parties", DOC, doc_file("2025-01/MOC_637117634515656361_Trade-Agreement-with-Argentina-1966.pdf")),
            ("signed", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKimA=="),
            ("in_force", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKimA=="),
            ("ended", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKimA=="),
            ("unts_registration", "United Nations Treaty Collection, United Nations Treaty Series",
             "https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280129661"),
        ],
    },
    "ARIN-TRA-1981": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of the Republic of India and the Government of the "
                    "Republic of Argentina",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1981-07-28",
            "in_force": "1982-08-13",
            "provisional_application": "1981-07-28",
            "parties": country("AR", "IN"),
            "notes": "Signed at Buenos Aires; applied provisionally from signature and in force definitively from the "
                     "exchange of ratifications (Argentine Law 22.623). Three years, then renewed automatically for "
                     "one-year periods.",
            "verification": "official",
        },
        "links": [
            (doc_file("2025-01/MOC_636752899695215740_Agreement_India_Argentina.pdf"), "treaty_text"),
            ("https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKinA==", "website"),
        ],
        "prov": [
            ("parties", DOC, doc_file("2025-01/MOC_636752899695215740_Agreement_India_Argentina.pdf")),
            ("signed", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKinA=="),
            ("in_force", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKinA=="),
            ("status", "Ministry of Foreign Affairs of Argentina, Biblioteca Digital de Tratados",
             "https://tratados.cancilleria.gob.ar/tratado_ficha.php?id=lKKinA=="),
        ],
    },
    "BRIN-TRA": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of India and the Government of the Republic of Brazil",
            "agreement_type": "trade_relations",
            "status": "in_force",
            "signed": "1968-02-03",
            "in_force": "1969-08-27",
            "parties": country("BR", "IN"),
            "unts_registration": "I-11961",
            "notes": "Signed at New Delhi; in force from the exchange of ratifications for three years, then renewed "
                     "automatically. Brazil's Concórdia database lists it as in force, with a 1997 complementary "
                     "adjustment.",
            "verification": "official",
        },
        "links": [
            (doc_file("2025-01/MOC_637117635139914314_Trade-Agreement-with-Brazil-1968.pdf"), "treaty_text"),
            ("https://concordia.itamaraty.gov.br/acordo/1668", "website"),
            ("https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280114d43", "website"),
        ],
        "prov": [
            ("parties", DOC, doc_file("2025-01/MOC_637117635139914314_Trade-Agreement-with-Brazil-1968.pdf")),
            ("signed", DOC, doc_file("2025-01/MOC_637117635139914314_Trade-Agreement-with-Brazil-1968.pdf")),
            ("in_force", "Ministry of Foreign Affairs of Brazil, Concórdia treaty database",
             "https://concordia.itamaraty.gov.br/acordo/1668"),
            ("status", "Ministry of Foreign Affairs of Brazil, Concórdia treaty database",
             "https://concordia.itamaraty.gov.br/acordo/1668"),
            ("unts_registration", "United Nations Treaty Collection, United Nations Treaty Series",
             "https://treaties.un.org/Pages/showDetails.aspx?objid=0800000280114d43"),
        ],
    },
    "CLIN-TRA": {
        "new": True,
        "set": {
            "name": "Trade Agreement between the Government of India and the Government of the Republic of Chile",
            "agreement_type": "trade_relations",
            "status": "terminated",
            "signed": "1956-10-16",
            "in_force": "1956-10-16",
            "ended": "1959-12-31",
            "parties": country("CL", "IN"),
            "notes": "Signed at New Delhi; in force on signature and valid up to 31 December 1959. A new trade "
                     "agreement, signed at Santiago on 10 March 1960, applied from 1 January 1960; it and the 1972 "
                     "trade agreement are not recorded, because no source states their current status.",
            "verification": "official",
        },
        "links": [(doc_file("2025-01/MOC_637117635783233640_Trade-Agreement-with-Chile-1956.pdf"), "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2025-01/MOC_637117635783233640_Trade-Agreement-with-Chile-1956.pdf")),
            ("signed", DOC, doc_file("2025-01/MOC_637117635783233640_Trade-Agreement-with-Chile-1956.pdf")),
            ("in_force", DOC, doc_file("2025-01/MOC_637117635783233640_Trade-Agreement-with-Chile-1956.pdf")),
            ("ended", DOC, doc_file("2025-01/MOC_637117635783233640_Trade-Agreement-with-Chile-1956.pdf")),
        ],
    },
    # --- Africa -------------------------------------------------------------------------------------
    "INRW-TCF": {
        "new": True,
        "set": {
            "name": "Trade Cooperation Framework between the Government of the Republic of India and the Government "
                    "of the Republic of Rwanda",
            "agreement_type": "framework",
            "status": "in_force",
            "signed": "2018-07-23",
            "in_force": "2018-07-23",
            "parties": country("IN", "RW"),
            "notes": "Signed at Kigali during the Indian Prime Minister's visit; in force on signature for five years, "
                     "renewed automatically for five-year periods. It terminated the India-Rwanda trade agreement "
                     "of 13 June 1990 (Article 11).",
            "verification": "official",
        },
        "links": [(doc_file("2026-01/Trade%20Cooperation%20Framework%20India-Rwanda%20signed%20in%202018%20%282%29.pdf"),
                   "treaty_text")],
        "prov": [
            ("parties", DOC, doc_file("2026-01/Trade%20Cooperation%20Framework%20India-Rwanda%20signed%20in%202018%20%282%29.pdf")),
            ("signed", PIB, "https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1539787"),
            ("in_force", DOC, doc_file("2026-01/Trade%20Cooperation%20Framework%20India-Rwanda%20signed%20in%202018%20%282%29.pdf")),
            ("status", DOC, DOC_LIST),
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
    if change.get("instruments"):
        existing = list(record.get("instruments") or [])
        ids = {i["id"] for i in existing}
        for inst in change["instruments"]:
            if inst["id"] in ids:
                raise SystemExit(f"{rid}: instrument {inst['id']} exists")
            existing.append(inst)
        record["instruments"] = existing
    prov = change.get("prov", [])
    if prov:
        fields = set() if change.get("keep_prov") else {f for f, _, _ in prov}
        fields |= set(change.get("drop_prov", []))
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
