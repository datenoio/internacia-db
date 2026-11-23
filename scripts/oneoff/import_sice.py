#!/usr/bin/env python3
"""One-off: add agreements from the OAS Foreign Trade Information System (SICE) to data/trade_agreements/.

SICE (http://www.sice.oas.org) lists the trade agreements of the Americas: the agreements table
(``agreements_e.asp``: free trade, framework and preferential agreements with signature and entry
into force dates), one page per agreement ending with an "About the Agreement" / "Información
complementaria" block (signature, entry into force, often per pair of parties) and the Trade Policy
Developments index (``tpd_e.asp``: agreements under negotiation and signed but not in force, each with
a page of dated documents). sice.oas.org answers scripts with a Cloudflare challenge, so the pages
were read from Internet Archive snapshots; every provenance URL below is the snapshot that was read.

The registry already held 91 of the 148 rows of the agreements table (most through the WTO RTA-IS
and ADB ARIC walks). This script writes the rest, checked by hand against the snapshots:

- in force: ALADI partial scope agreements (ACE, AAP.A25TM, AAP.C) and free trade agreements that
  were never notified to the WTO, with the per-pair entry into force dates SICE gives as party
  ``in_force`` dates;
- signed or recently in force: rows of the Trade Policy Developments index whose status a party
  government confirms (UAE Ministry of Economy and Tourism, Peru's official gazette El Peruano);
- under negotiation: Trade Policy Developments rows with a dated document since 2022.

New records are ``verification: catalogue`` unless a party government gave the dates. Not written
(listed in the pull request): agreements SICE gives no entry into force date for, rows whose SICE
dates contradict each other, rows already in the registry under another shape (Central America
agreements kept as bilateral records, EU agreements with the Andean countries), dormant negotiations,
and rows other open pull requests cover. ALADI codes go in ``acronyms`` (``lang: es``).

Usage: python -I scripts/oneoff/import_sice.py [--write]
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SOURCE = "OAS Foreign Trade Information System (SICE)"
SNAPSHOT = "https://web.archive.org/web/{ts}/http://www.sice.oas.org{path}"
TABLE = ("/agreements_e.asp", "20261011022627")
TPD = ("/tpd_e.asp", "20260519023454")
UAE_MOET = "UAE Ministry of Economy and Tourism"
EL_PERUANO = "Diario Oficial El Peruano"
ALADI = "Latin American Integration Association (ALADI)"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]
MERCOSUR = ["AR", "BR", "PY", "UY"]


def P(code: str, **extra) -> dict:
    """A party: a country code, or ``CARICOM`` and other blocs with ``type="intblock"``."""
    party = {"id": code, "type": extra.pop("type", "country")}
    party.update(extra)
    return party


# Each entry: record fields, plus ``page`` (SICE path, snapshot) for the agreement page that was
# read, ``status_from`` ("table", "tpd" or "page") and optional ``extra`` provenance rows.
RECORDS: list[dict] = [
    # --- free trade agreements in the SICE table -----------------------------------------------
    dict(id="ARCL", name="Chile - Argentina Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2017-11-02", in_force="2019-05-02", parties=[P("AR"), P("CL")], status_from="table"),
    dict(id="BRCL", name="Brazil - Chile Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2018-11-21", in_force="2022-01-25", parties=[P("BR"), P("CL")], status_from="table"),
    dict(id="CLUY", name="Chile - Uruguay Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2016-10-04", in_force="2018-12-13", parties=[P("CL"), P("UY")], status_from="table"),
    dict(id="CLPY", name="Chile - Paraguay Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2021-12-01", in_force="2024-02-15", parties=[P("CL"), P("PY")],
         page=("/Trade/CHL_PRY/CHL_PRY_Index_e.asp", "20251116011654")),
    dict(id="CLEC", name="Chile - Ecuador Economic Complementation Agreement No. 75",
         acronyms=["AAP.CE 75"], agreement_type="fta", status="in_force",
         signed="2020-08-13", in_force="2022-05-16", parties=[P("CL"), P("EC")],
         page=("/Trade/CHL_ECU/CHL_ECU_index_PDF_s.asp", "20251114060311")),
    dict(id="CREC", name="Costa Rica - Ecuador Trade Partnership Agreement",
         other_names=[("es", "Acuerdo de Asociación Comercial Costa Rica - Ecuador")],
         agreement_type="fta", status="in_force", signed="2023-03-01", in_force="2024-10-01",
         parties=[P("CR"), P("EC")], page=("/Trade/CRI_ECU/CRI_ECU_Index_s.asp", "20251217163750")),
    dict(id="AECR", name="Costa Rica - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="in_force", signed="2024-04-17", in_force="2025-04-01",
         parties=[P("AE"), P("CR")], page=("/Trade/CRI_UAE/CRI_UAE_index_e.asp", "20251218013624"),
         notes="The SICE agreements table gives 2025-01-04 for entry into force; the SICE agreement page and the "
               "UAE Ministry of Economy and Tourism give 2025-04-01.",
         verification="official",
         extra=[("in_force", UAE_MOET, "https://www.moet.gov.ae/en/uae-costa-rica-cepa")]),
    dict(id="GTIL", name="Guatemala - Israel Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2022-09-22", in_force="2024-03-07", parties=[P("GT"), P("IL")],
         page=("/Trade/GTM_ISR/GTM_ISR_Index_e.asp", "20250910165614")),
    dict(id="PYTW", name="Paraguay - Republic of China (Taiwan) Economic Cooperation Agreement",
         agreement_type="fta", status="in_force", signed="2017-07-12", in_force="2018-02-28",
         parties=[P("PY"), P("TW")], page=("/Trade/PAR_TWN/PAR_TWN_index_e.asp", "20251117025531")),
    dict(id="MERCOSURPE", name="MERCOSUR - Peru Economic Complementation Agreement No. 58",
         acronyms=["AAP.CE 58"], agreement_type="fta", status="in_force", signed="2005-11-30", in_force="2006-01-02",
         parties=[P("PE"), P("AR"), P("BR"), P("PY", in_force="2006-02-06"), P("UY")],
         notes="SICE gives no single entry into force date, only the parties' internal approvals (December 2005 to "
               "February 2006). The ALADI fact sheet gives 2006-01-02 for Argentina, Brazil and Uruguay with Peru and "
               "2006-02-06 for Paraguay with Peru.",
         page=("/Trade/MRCSRPerACE58/ACE.asp", "20261016213122"),
         extra=[("in_force", ALADI, "https://www2.aladi.org/SitioALADI/documentos/FichasDescriptivasAcuerdos/"
                 "FD_AAP.CE_58_Argentina_Brasil_Paraguay_Perú_Uruguay.pdf")]),
    dict(id="MERCOSURCO", name="MERCOSUR - Colombia Economic Complementation Agreement No. 72",
         acronyms=["AAP.CE 72"], agreement_type="fta", status="in_force", signed="2017-07-21", in_force="2017-12-20",
         parties=[P("CO"), P("AR", in_force="2017-12-20"), P("BR", in_force="2017-12-20"),
                  P("PY", in_force="2019-01-29"), P("UY", in_force="2018-06-11")],
         notes="Replaces ACE 59 between Colombia and MERCOSUR; SICE notes that some sections of ACE 59 stay in force.",
         page=("/Trade/COL_MER/COL_MER_index_s.asp", "20260808111913")),
    # --- framework agreements --------------------------------------------------------------------
    dict(id="MERCOSURMX", name="MERCOSUR - Mexico Economic Complementation Agreement No. 54 (framework agreement)",
         acronyms=["AAP.CE 54"], agreement_type="framework", status="in_force", signed="2002-07-05",
         in_force="2006-01-05", parties=[P("MX"), *[P(c) for c in MERCOSUR]],
         page=("/Trade/MERCOSURMexACE54/MERMex_s.asp", "20261016232359")),
    dict(id="MERCOSURMX-AUTO",
         name="MERCOSUR - Mexico Economic Complementation Agreement No. 55 (automotive sector)",
         acronyms=["AAP.CE 55"], agreement_type="pta", status="in_force", signed="2002-09-27", in_force="2003-01-01",
         parties=[P("MX"), P("AR"), P("BR", in_force="2003-01-15"), P("PY"), P("UY")],
         notes="In force until replaced by a MERCOSUR - Mexico free trade agreement. Argentina suspended its "
               "application for three years in June 2012 (SICE).",
         page=("/Trade/MERCOSURMexACE55/MERMexAuto_s.asp", "20251016214137")),
    dict(id="MERCOSURMA", name="MERCOSUR - Morocco Framework Agreement", agreement_type="framework",
         status="in_force", signed="2004-11-26", in_force="2010-04-29", parties=[P("MA"), *[P(c) for c in MERCOSUR]],
         status_from="table"),
    # --- preferential agreements (ALADI partial scope and others) --------------------------------
    dict(id="MERCOSURCOECVE",
         name="MERCOSUR - Colombia, Ecuador and Venezuela Economic Complementation Agreement No. 59",
         acronyms=["AAP.CE 59"], agreement_type="fta", status="in_force", signed="2004-10-18", in_force="2005-01-05",
         parties=[P("CO", in_force="2005-02-01"), P("EC", in_force="2005-04-01"), P("VE", in_force="2005-01-05"),
                  P("AR", in_force="2005-01-05"), P("BR", in_force="2005-02-01"), P("PY", in_force="2005-04-19"),
                  P("UY", in_force="2005-01-05")],
         notes="Agreement between MERCOSUR and Andean Community members. SICE gives entry into force per pair of "
               "parties between 2005-01-05 and 2005-04-19; a party's date here is its first pair. Colombia and "
               "MERCOSUR later signed ACE 72 (MERCOSURCO), and some sections of ACE 59 stay in force.",
         page=("/Trade/mrcsrac/eca_s.asp", "20261019155120")),
    dict(id="ARBR", name="Argentina - Brazil Economic Complementation Agreement No. 14", acronyms=["AAP.CE 14"],
         agreement_type="pta", status="in_force", signed="1990-12-20", in_force="1990-12-20",
         parties=[P("AR"), P("BR")], page=("/Trade/ARG_BRA/ARGBRA_ind_s.asp", "20261017211646")),
    dict(id="ARCL-1991", name="Argentina - Chile Economic Complementation Agreement No. 16", acronyms=["AAP.CE 16"],
         agreement_type="pta", status="in_force", signed="1991-08-02", in_force="1991-08-02",
         parties=[P("AR"), P("CL")],
         notes="ALADI notes on SICE: under Article 48 of ACE 35 (MERCOSURCL) the tariff preferences of ACE 16 no "
               "longer apply, while its provisions compatible with ACE 35 stay in force.",
         page=("/Trade/argchi/indice_s.asp", "20261016225920")),
    dict(id="ARUY-AUTO", name="Argentina - Uruguay Economic Complementation Agreement No. 57 (automotive sector)",
         acronyms=["AAP.CE 57"], agreement_type="pta", status="in_force", signed="2003-03-31", in_force="2003-05-01",
         parties=[P("AR"), P("UY")], page=("/Trade/arguru/ACE57_s.asp", "20261016214546")),
    dict(id="BRUY", name="Brazil - Uruguay Economic Complementation Agreement No. 2", acronyms=["AAP.CE 2"],
         agreement_type="pta", status="in_force", signed="1986-09-30", in_force="1986-10-01",
         parties=[P("BR"), P("UY")], page=("/Trade/BRA_UR/BRA_UR_ind_s.asp", "20250910175303")),
    dict(id="BRGYKN", name="Brazil - Guyana - Saint Kitts and Nevis Partial Scope Agreement No. 38",
         acronyms=["AAP.A25TM 38"], agreement_type="pta", status="in_force", signed="2001-06-27", in_force="2004-05-31",
         parties=[P("BR"), P("GY"), P("KN", in_force="2012-07-05", note="Acceded by the Sixth Additional Protocol")],
         page=("/Trade/BRA_GUY/BRA_GUY_Index_s.asp", "20261017023718")),
    dict(id="BRSR", name="Brazil - Suriname Partial Scope Agreement No. 41", acronyms=["AAP.A25TM 41"],
         agreement_type="pta", status="in_force", signed="2005-04-21", in_force="2006-07-26",
         parties=[P("BR"), P("SR")], page=("/Trade/BRA_SUR/index_s.asp", "20251018101550")),
    dict(id="COVE", name="Colombia - Venezuela Partial Scope Agreement No. 28", acronyms=["AAP.C 28"],
         agreement_type="pta", status="in_force", signed="2011-11-28", in_force="2012-10-19",
         parties=[P("CO"), P("VE")], page=("/Trade/COL_VEN/index_s.asp", "20261017055944")),
    dict(id="PEVE", name="Peru - Venezuela Partial Scope Agreement", agreement_type="pta", status="in_force",
         signed="2012-01-07", in_force="2013-08-01", parties=[P("PE"), P("VE")], status_from="table"),
    dict(id="COPA", name="Colombia - Panama Partial Scope Agreement No. 29", acronyms=["AAP.A25TM 29"],
         agreement_type="pta", status="in_force", signed="1993-07-09", in_force="1995-01-18",
         parties=[P("CO"), P("PA")], page=("/Trade/colpan/colpan_s.asp", "20261014192157")),
    dict(id="ECGT", name="Ecuador - Guatemala Partial Scope Agreement No. 42", acronyms=["AAP.A25TM 42"],
         agreement_type="pta", status="in_force", signed="2011-04-15", in_force="2013-02-19",
         parties=[P("EC"), P("GT")], page=("/Trade/ECU_GTM/Index_s.asp", "20261017000510")),
    dict(id="BZGT", name="Belize - Guatemala Partial Scope Agreement", agreement_type="pta", status="in_force",
         signed="2006-06-26", in_force="2010-04-04", parties=[P("BZ"), P("GT")],
         page=("/Trade/BLZ_GTM/Index_e.asp", "20251218071121")),
    dict(id="BZTW", name="Belize - Republic of China (Taiwan) Partial Scope Economic Cooperation Agreement",
         agreement_type="pta", status="in_force", signed="2020-09-30", in_force="2020-09-30",
         parties=[P("BZ"), P("TW")], status_from="table"),
    dict(id="GTVE", name="Guatemala - Venezuela Partial Scope Agreement No. 23", acronyms=["AAP.A25TM 23"],
         agreement_type="pta", status="in_force", signed="1985-10-30", in_force="1986-04-10",
         parties=[P("GT"), P("VE")], page=("/Trade/vengua/Indice.asp", "20261017173243")),
    dict(id="GYVE", name="Guyana - Venezuela Partial Scope Agreement No. 22", acronyms=["AAP.A25TM 22"],
         agreement_type="pta", status="in_force", signed="1990-10-27", in_force="1991-06-28",
         parties=[P("GY"), P("VE")], page=("/Trade/vengu/indice.asp", "20261016204218")),
    # --- Trade Policy Developments: signed, or in force since the snapshot ------------------------
    dict(id="AECL", name="Chile - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="in_force", signed="2024-07-29", in_force="2025-11-24",
         parties=[P("AE"), P("CL")], page=("/TPD/CHL_GCC/CHL_GCC_e.ASP", "20251218091928"), status_from="official",
         notes="The SICE Trade Policy Developments index (May 2026 snapshot) still lists it as signed but not in "
               "force; the UAE Ministry of Economy and Tourism gives entry into force on 2025-11-24.",
         verification="official", extra=[("status", UAE_MOET, "https://www.moet.gov.ae/en/uae-chile-cepa")]),
    dict(id="AECO", name="Colombia - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="signed", signed="2024-04-18", parties=[P("AE"), P("CO")],
         page=("/TPD/COL_UAE/COL_UAE_e.asp", "20251217163344"), status_from="tpd"),
    dict(id="GTPE", name="Guatemala - Peru Free Trade Agreement", agreement_type="fta", status="in_force",
         signed="2011", in_force="2026-07-01", parties=[P("GT"), P("PE")],
         page=("/TPD/CACM_PER/GTM_PER_e.asp", "20251118011944"), status_from="official",
         notes="Signed in 2011 and ratified by Guatemala in 2013; a protocol signed on 2025-04-23 allowed entry into "
               "force, which El Peruano reports for 2026-07-01 together with the protocol.",
         verification="official",
         extra=[("status", EL_PERUANO,
                 "https://www.elperuano.pe/noticia/298631-tlc-peru-guatemala-en-vigencia-el-1-de-julio")]),
    dict(id="COPA-2013", name="Colombia - Panama Free Trade Agreement", agreement_type="fta", status="signed",
         signed="2013-09-20", parties=[P("CO"), P("PA")], page=("/TPD/COL_PAN/COL_PAN_e.ASP", "20251114051645"),
         status_from="tpd"),
    dict(id="ILPA", name="Israel - Panama Free Trade Agreement", agreement_type="fta", status="signed",
         signed="2018-05-18", parties=[P("IL"), P("PA")], page=("/TPD/PAN_ISR/PAN_ISR_e.asp", "20251114051021"),
         status_from="tpd", notes="Approved by Panama's National Assembly on 2019-10-10 (SICE)."),
    dict(id="PATT", name="Panama - Trinidad and Tobago Partial Scope Trade Agreement", agreement_type="pta",
         status="signed", signed="2013-10-03", parties=[P("PA"), P("TT")],
         page=("/TPD/PAN_TTO/PAN_TTO_e.asp", "20251217163230"), status_from="tpd"),
    dict(id="MERCOSURPA", name="MERCOSUR - Panama Economic Complementation Agreement", agreement_type="fta",
         status="signed", signed="2024-12-06", parties=[P("PA"), *[P(c) for c in MERCOSUR]],
         page=("/TPD/MER_PAN/MER_PAN_e.asp", "20251217163347"), status_from="tpd",
         notes="The SICE Trade Policy Developments index lists it under negotiation; its page gives the signature."),
    # --- Trade Policy Developments: under negotiation, with a dated document since 2022 -----------
    dict(id="BZSV", name="Belize - El Salvador Partial Scope Agreement", agreement_type="pta", status="negotiating",
         parties=[P("BZ"), P("SV")], page=("/TPD/SLV_BLZ/SLV_BLZ_e.ASP", "20251118004344"), status_from="tpd",
         notes="Negotiations launched on 2024-12-11; third round concluded on 2025-08-19 (SICE)."),    dict(id="CLTT", name="Chile - Trinidad and Tobago Partial Scope Agreement", agreement_type="pta",
         status="negotiating", parties=[P("CL"), P("TT")], page=("/TPD/CHL_TTO/CHL_TTO_e.ASP", "20251217163232"),
         status_from="tpd", notes="First round in August 2021; fourth round concluded on 2023-06-01 (SICE)."),
    dict(id="CRIL", name="Costa Rica - Israel Free Trade Agreement", agreement_type="fta", status="negotiating",
         parties=[P("CR"), P("IL")], page=("/TPD/CRI_ISR/CRI_ISR_e.ASP", "20251217163225"), status_from="tpd",
         notes="Negotiations announced on 2023-03-29; technical closure announced on 2025-11-13 (SICE)."),
    dict(id="DOEC", name="Dominican Republic - Ecuador Trade Agreement", agreement_type="fta", status="negotiating",
         parties=[P("DO"), P("EC")], page=("/TPD/ECU_DOM/ECU_DOM_e.ASP", "20251218035253"), status_from="tpd",
         notes="Joint declaration to begin negotiations signed on 2024-02-26 (SICE)."),
    dict(id="AEEC", name="Ecuador - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="negotiating", parties=[P("AE"), P("EC")],
         page=("/TPD/ECU_UAE/ECU_UAE_e.ASP", "20251005215220"), status_from="tpd",
         notes="Joint declaration on negotiations signed on 2024-04-22; technical meetings on 2025-05-03 (SICE)."),
    dict(id="MERCOSURAE", name="MERCOSUR - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="negotiating", parties=[P("AE"), *[P(c) for c in MERCOSUR]],
         page=("/TPD/MER_UAE/MER_UAE_e.asp", "20251117062701"), status_from="tpd",
         notes="First round concluded on 2024-07-05; fourth round concluded on 2025-11-07 (SICE)."),
    dict(id="AEPE", name="Peru - United Arab Emirates Comprehensive Economic Partnership Agreement",
         agreement_type="fta", status="negotiating", parties=[P("AE"), P("PE")],
         page=("/TPD/PER_UAE/PER_UAE_e.ASP", "20260130200123"), status_from="tpd",
         notes="Negotiations launched on 2025-11-25 with a first round on 2025-11-25/28 (SICE)."),
    dict(id="PESV", name="El Salvador - Peru Free Trade Agreement", agreement_type="fta", status="negotiating",
         parties=[P("PE"), P("SV")], page=("/TPD/CACM_PER/SLV_PER_e.asp", "20250813040627"), status_from="tpd",
         notes="Part of the 2010 Central America - Peru talks; restarted on 2025-02-04, with rounds in March and May "
               "2025 (SICE)."),
    dict(id="INUS", name="India - United States Bilateral Trade Agreement", agreement_type="fta",
         status="negotiating", parties=[P("IN"), P("US")], page=("/TPD/USA_IND/USA_IND_e.asp", "20260329084436"),
         status_from="tpd",
         notes="A framework for an interim agreement on reciprocal trade was announced on 2026-02-06 (SICE)."),
    dict(id="GCCCL", name="Chile - Gulf Cooperation Council Free Trade Agreement", agreement_type="fta",
         status="proposed", parties=[P("CL"), *[P(c) for c in ("AE", "BH", "KW", "OM", "QA", "SA")]],
         page=("/TPD/CHL_GCC/CHL_GCC_e.ASP", "20251218091928"), status_from="tpd",
         notes="Chile and the GCC signed a memorandum of understanding on 2021-02-24 to develop feasibility studies "
               "(SICE); Chile then negotiated a bilateral agreement with the UAE (AECL)."),
]


def snapshot(where: tuple[str, str]) -> str:
    return SNAPSHOT.format(ts=where[1], path=where[0])


def build(entry: dict) -> dict:
    entry = dict(entry)
    page = entry.pop("page", None)
    status_from = entry.pop("status_from", "page" if page else "table")
    extra = entry.pop("extra", [])
    record = {k: v for k, v in entry.items() if k not in ("acronyms", "other_names")}
    if entry.get("acronyms"):
        record["acronyms"] = [{"lang": "es", "value": a} for a in entry["acronyms"]]
    if entry.get("other_names"):
        record["other_names"] = [{"lang": lang, "name": name} for lang, name in entry["other_names"]]
    record.setdefault("verification", "catalogue")
    record["last_verified"] = RETRIEVED
    party_source = snapshot(page) if page else snapshot(TABLE)
    status_source = {"table": snapshot(TABLE), "tpd": snapshot(page or TPD)}.get(status_from, party_source)
    provenance = [
        {"field": "parties", "source": SOURCE, "url": party_source, "retrieved_at": RETRIEVED},
        {"field": "status", "source": SOURCE, "url": status_source, "retrieved_at": RETRIEVED},
    ]
    for field, source, url in extra:
        provenance.append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})
    if status_from == "official":
        provenance = [p for p in provenance if not (p["field"] == "status" and p["source"] == SOURCE)]
    record["provenance"] = provenance
    keys = [k for k in FIELD_ORDER if k in record]
    return {k: record[k] for k in keys}


def main(argv: list[str]) -> int:
    write = "--write" in argv
    countries = {p.stem for p in (ROOT / "data" / "countries").glob("*.yaml")}
    intblocks = {p.stem for p in (ROOT / "data" / "intblocks").rglob("*.yaml")}
    texts = {p.stem: p.read_text(encoding="utf-8") for p in REGISTRY.glob("*.yaml")}
    existing = {k: yaml.safe_load(v) for k, v in texts.items()}
    problems = unchanged = 0
    seen: set[str] = set()
    for entry in RECORDS:
        record = build(entry)
        rid = record["id"]
        text = yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)
        if texts.get(rid) == text:
            unchanged += 1
            seen.add(rid)
            continue
        if rid in texts or rid in intblocks or rid in seen:
            print(f"! {rid}: id already used")
            problems += 1
        seen.add(rid)
        ids = []
        for party in record["parties"]:
            known = countries if party["type"] == "country" else intblocks
            if party["id"] not in known:
                print(f"! {rid}: unknown {party['type']} {party['id']}")
                problems += 1
            ids.append(party["id"])
        same = [
            k for k, r in existing.items()
            if sorted(p["id"] for p in r.get("parties") or []) == sorted(ids)
            and r.get("agreement_type") == record["agreement_type"]
        ]
        if same:
            print(f"  {rid}: same parties and type as {', '.join(sorted(same))} (checked: different instrument)")
        if write:
            (REGISTRY / f"{rid}.yaml").write_text(text, encoding="utf-8")
    print(f"{len(RECORDS)} records ({unchanged} unchanged){' written' if write else ''}, problems {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
