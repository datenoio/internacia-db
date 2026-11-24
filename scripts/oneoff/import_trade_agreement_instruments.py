#!/usr/bin/env python3
"""One-off: fill ``instruments`` on data/trade_agreements/ records (add-trade-agreement-instruments).

Two sources, merged per record:

1. **China FTA Network (MOFCOM).** The upgrade and early harvest facts that
   ``import_mofcom_fta.py`` wrote into ``notes`` move into ``instruments``; the sentences it
   appended (and their ``notes`` provenance rows) are removed from the records.
2. **WTO RTA-IS, sheet ``RTA Changes``** of the full export
   (https://rtais.wto.org/UI/ExportAllRTAList.aspx; untrusted input, run with ``python -I``).
   LAIA partial-scope agreements (RTA ID 135) are separate agreements and are skipped. Every
   other row maps to a record by ``wto_rta_id``. Joint Committee decisions and CEPA Supplements
   are named from the remarks; the other rows are named by hand in ``OVERRIDES``. Rows that
   change who applies the agreement (a withdrawal, entry into force between some parties) are
   party data and are skipped, as is the one row without dates.

When both sources describe one instrument (``MERGE``), the MOFCOM item keeps its dates (a party
government), takes a missing date from the WTO row, notes a conflicting one, and gets both
provenance rows.

Usage: python -I scripts/oneoff/import_trade_agreement_instruments.py EXPORT_XLSX [--write]
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
WTO_SOURCE = "WTO Regional Trade Agreements Information System"
WTO_CARD = "https://rtais.wto.org/UI/PublicShowRTAIDCard.aspx?rtaid={}"
MOFCOM = "Ministry of Commerce of the People's Republic of China, China FTA Network"
B = "https://fta.mofcom.gov.cn"
LAIA_RTA_ID = 135

# ``instruments`` goes after ``notes``, or else before the first of these keys.
INSTRUMENTS_BEFORE = ("wto_rta_id", "aric_id", "verification")
ITEM_ORDER = ["id", "kind", "name", "other_names", "status", "signed", "in_force", "ended", "coverage", "notes",
              "provenance"]
COVERAGE = {"Goods": ["goods"], "Services": ["services"], "Goods & Services": ["goods", "services"]}
ROMAN = {"": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}


def mofcom(path: str) -> dict[str, str]:
    return {"field": "instruments", "source": MOFCOM, "url": B + path, "retrieved_at": RETRIEVED}


def wto(rta_id: int) -> dict[str, str]:
    return {"field": "instruments", "source": WTO_SOURCE, "url": WTO_CARD.format(rta_id), "retrieved_at": RETRIEVED}


# --- MOFCOM instruments ------------------------------------------------------------------------

MOFCOM_ITEMS: dict[str, list[dict[str, Any]]] = {
    "ACFTA": [
        {"id": "upgrade-2015", "kind": "amending_protocol",
         "name": "Protocol to Amend the Framework Agreement on Comprehensive Economic Co-operation and Certain "
                 "Agreements thereunder between the Association of Southeast Asian Nations and the People's "
                 "Republic of China",
         "status": "in_force", "signed": "2015-11-22", "in_force": "2019-10-22",
         "notes": "The version 2.0 upgrade. Signed in Kuala Lumpur; in force for China and Viet Nam from 1 July "
                  "2016 and for all parties from 22 October 2019.",
         "provenance": [mofcom("/article/c/zhengwugk/201910/41659.html")]},
        {"id": "upgrade-2025", "kind": "amending_protocol",
         "name": "ASEAN-China Free Trade Area 3.0 Upgrade Protocol",
         "other_names": [{"lang": "zh", "name": "中国—东盟自贸区3.0版升级议定书"}],
         "status": "signed", "signed": "2025-10-28",
         "notes": "Signed in Kuala Lumpur. On 16 November 2026 the leaders announced its entry into force on "
                  "1 December 2026.",
         "provenance": [mofcom("/article/c/zhengwugk/202510/57382.html"),
                        mofcom("/article/c/zhengwugk/202611/100334.html")]},
    ],
    "CHCN": [
        {"id": "enhancement-2026", "kind": "amending_protocol",
         "name": "China-Switzerland Free Trade Agreement Enhancement Protocol",
         "status": "signed", "signed": "2026-10-30", "coverage": ["goods", "services", "investment"],
         "notes": "A joint study on upgrading the agreement was launched in January 2017. Negotiations launched "
                  "in September 2024 were concluded with a memorandum of understanding on 20 August 2026; the "
                  "protocol was signed in Beijing.",
         "provenance": [mofcom("/article/c/zhengwugk/202608/100187.html"),
                        mofcom("/article/e/enrelease/202611/100316.html")]},
    ],
    "CLCN": [
        {"id": "upgrade-2017", "kind": "amending_protocol",
         "name": "Protocol to Amend the Free Trade Agreement and the Supplementary Agreement on Trade in Services "
                 "of the Free Trade Agreement between the Government of the Republic of Chile and the Government "
                 "of the People's Republic of China",
         "status": "signed", "signed": "2017-11-11",
         "notes": "Upgrade negotiations were launched in November 2016; the protocol was signed in Da Nang.",
         "provenance": [mofcom("/article/c/zhengwugk/201711/36117.html")]},
    ],
    "CNGE": [
        {"id": "upgrade-2026", "kind": "amending_protocol",
         "name": "China-Georgia Free Trade Agreement Upgrade Protocol",
         "status": "signed", "signed": "2026-04-22",
         "notes": "Upgrade negotiations launched in July 2025 were substantially concluded in September 2025 and "
                  "closed by a memorandum of understanding signed in Shanghai on 4 November 2025; the protocol "
                  "was signed in Beijing.",
         "provenance": [mofcom("/article/c/zhengwugk/202511/57419.html"),
                        mofcom("/article/c/zhengwugk/202604/58237.html")]},
    ],
    "CNKR": [
        {"id": "second-phase", "kind": "amending_protocol",
         "name": "China-Korea Free Trade Agreement second phase",
         "status": "negotiating", "coverage": ["services", "investment"],
         "notes": "Negotiations on investment and trade in services on a negative-list basis were launched in "
                  "December 2017 and held 17 formal rounds from March 2018; MOFCOM announced their substantial "
                  "conclusion on 19 November 2026, with signature pending.",
         "provenance": [mofcom("/article/c/zhengwugk/202611/100346.html")]},
    ],
    "CNNI": [
        {"id": "early-harvest-2022", "kind": "early_harvest",
         "name": "Early Harvest Arrangement for the Free Trade Agreement between the Government of the People's "
                 "Republic of China and the Government of the Republic of Nicaragua",
         "other_names": [{"lang": "zh", "name": "中华人民共和国政府和尼加拉瓜共和国政府关于自由贸易协定早期收获的安排"}],
         "status": "in_force", "signed": "2022-07-12", "in_force": "2023-05-01",
         "notes": "Signed by video link together with the launch of negotiations on the full FTA.",
         "provenance": [mofcom("/article/c/zhengwugk/202207/49157.html"),
                        mofcom("/article/c/zhengwugk/202304/53863.html")]},
    ],
    "CNNZ": [
        {"id": "upgrade-2021", "kind": "amending_protocol",
         "name": "Protocol to Upgrade the Free Trade Agreement between the Government of the People's Republic of "
                 "China and the Government of New Zealand",
         "status": "in_force", "signed": "2021-01-26", "in_force": "2022-04-07",
         "notes": "Upgrade negotiations were launched in November 2016.",
         "provenance": [mofcom("/article/c/zhengwugk/202202/47457.html")]},
        {"id": "services-negative-list", "kind": "exchange_of_letters",
         "name": "Negotiations on trade in services on a negative-list basis",
         "status": "negotiating", "coverage": ["services"],
         "notes": "Launched by an exchange of letters signed on 13 June 2024.",
         "provenance": [mofcom("/article/e/enrelease/202406/55618.html")]},
    ],
    "CNPE": [
        {"id": "optimization-2024", "kind": "amending_protocol",
         "name": "Optimization Protocol of the Free Trade Agreement between the Government of the People's Republic "
                 "of China and the Government of the Republic of Peru",
         "status": "in_force", "signed": "2024-11-14", "in_force": "2026-11-01",
         "notes": "Upgrade negotiations were launched in November 2018.",
         "provenance": [mofcom("/article/e/enrelease/202611/100318.html")]},
    ],
    "CNPK": [
        {"id": "second-phase-2019", "kind": "amending_protocol",
         "name": "Protocol on Amending the Free Trade Agreement between the Government of the People's Republic of "
                 "China and the Government of the Islamic Republic of Pakistan",
         "status": "signed", "signed": "2019-04-28",
         "notes": "The second-phase protocol, signed in Beijing.",
         "provenance": [mofcom("/article/e/enrelease/201904/40777.html")]},
    ],
    "CNSG": [
        {"id": "upgrade-2018", "kind": "amending_protocol",
         "name": "Protocol to Upgrade the Free Trade Agreement between the Government of the People's Republic of "
                 "China and the Government of the Republic of Singapore",
         "status": "in_force", "signed": "2018-11-12", "in_force": "2019-10-16",
         "notes": "Its changes to the rules of origin apply from 1 January 2020.",
         "provenance": [mofcom("/article/c/zhengwugk/201910/41637.html")]},
        {"id": "further-upgrade-2023", "kind": "amending_protocol",
         "name": "Protocol on Further Upgrading the Free Trade Agreement between the Government of the People's "
                 "Republic of China and the Government of the Republic of Singapore",
         "status": "in_force", "signed": "2023-12", "in_force": "2024-12-31", "coverage": ["services", "investment"],
         "notes": "Negotiations launched on 8 December 2020; services and investment commitments on a "
                  "negative-list basis.",
         "provenance": [mofcom("/article/c/zhengwugk/202412/56246.html")]},
    ],
    "SACUCN": [
        {"id": "early-harvest", "kind": "early_harvest",
         "name": "Early Harvest Arrangement of the China-SACU Agreement on Economic Partnership for Shared "
                 "Development",
         "status": "negotiating",
         "notes": "The first round of negotiations was held in Beijing on 20-21 October 2026.",
         "provenance": [mofcom("/article/c/african/africannews/202610/100272.html")]},
    ],
}

# Notes that stay on the record after the MOFCOM sentences move: facts with no instrument date.
KEEP_NOTES = {
    "CNSG": ("A protocol amending the agreement's rules of origin and services commitments was signed on 27 July "
             "2011; MOFCOM gives no date for its entry into force.",
             {"field": "notes", "source": MOFCOM, "url": B + "/article/c/zhengwugk/201108/26826.html",
              "retrieved_at": RETRIEVED}),
}

# WTO rows (record id, signature date) that describe a MOFCOM item: merge into that item.
MERGE = {("ACFTA", "2015-11-21"): "upgrade-2015", ("CLCN", "2017-11-11"): "upgrade-2017",
         ("CNPK", "2019-04-28"): "second-phase-2019"}

# --- WTO rows named by hand: (record id, signature date, entry into force, n-th such row) --------

SKIP = "skip"
OVERRIDES: dict[tuple[str, str | None, str | None, int], Any] = {
    ("EFTATN", "2024-10-09", "2026-03-01", 0): ("protocol-b-2024", "other",
        "Amendment of Protocol B (rules of origin) to the EFTA-Tunisia Free Trade Agreement"),
    ("JPMX", "2006-09-20", "2007-04-01", 0): ("market-access-protocol-2006", "amending_protocol",
        "Protocol between Japan and the United Mexican States related to improvement of market access conditions "
        "based on Paragraphs 3 and 5 of Article 5 of the Agreement"),
    ("JPMX", "2008-01-31", "2008-03-01", 0): ("notes-annex-3-2008", "exchange_of_letters",
        "Exchange of Diplomatic Notes for the Modification to Annex 3 of the Agreement"),
    ("JPMX", "2012-03-02", "2012-04-01", 0): ("notes-annex-4-2012", "exchange_of_letters",
        "Exchange of Diplomatic Notes for the Modification to Annex 4 of the Agreement"),
    ("JPMX", "2011-09-22", "2012-04-01", 0): ("amending-protocol-2011", "amending_protocol",
        "Protocol Amending the Agreement between Japan and Mexico for the Strengthening of the Economic Partnership"),
    ("CNMO", "2018-12-12", "2018-12-12", 0): ("trade-in-goods-2018", "supplementary_agreement",
        "CEPA Agreement on Trade in Goods"),
    ("CNMO", "2024-10-10", "2024-10-10", 0): ("services-amendment-2024", "amending_protocol",
        "Second Agreement Concerning Amendment to the CEPA Agreement on Trade in Services"),
    ("CNMO", "2019-11-20", "2019-11-20", 0): ("services-amendment-2019", "amending_protocol",
        "Agreement Concerning Amendment to the CEPA Agreement on Trade in Services"),
    ("CNMO", "2014-12-18", "2014-12-18", 0): ("guangdong-services-2014", "supplementary_agreement",
        "Agreement between the Mainland and Macao on Achieving Basic Liberalization of Trade in Services in "
        "Guangdong"),
    ("CNMO", "2015-11-28", "2015-11-28", 0): ("trade-in-services-2015", "supplementary_agreement",
        "CEPA Agreement on Trade in Services"),
    ("CNMO", "2017-12-18", "2017-12-18", 0): [
        ("investment-2017", "supplementary_agreement", "CEPA Investment Agreement", ["investment"]),
        ("ecotech-2017", "supplementary_agreement", "CEPA Agreement on Economic and Technical Cooperation", None),
    ],
    ("CNHK", "2019-11-21", "2019-11-21", 0): ("services-amendment-2019", "amending_protocol",
        "Agreement concerning Amendment to the CEPA Agreement on Trade in Services"),
    ("CNHK", "2024-10-09", "2024-10-09", 0): ("services-amendment-2024", "amending_protocol",
        "Second Agreement Concerning Amendment to the CEPA Agreement on Trade in Services"),
    ("CNHK", "2018-12-14", "2018-12-14", 0): ("trade-in-goods-2018", "supplementary_agreement",
        "CEPA Agreement on Trade in Goods"),
    ("CNHK", "2014-12-18", "2014-12-18", 0): ("guangdong-services-2014", "supplementary_agreement",
        "Agreement between the Mainland and Hong Kong on Achieving Basic Liberalization of Trade in Services in "
        "Guangdong"),
    ("CNHK", "2015-11-27", "2015-11-27", 0): ("trade-in-services-2015", "supplementary_agreement",
        "CEPA Agreement on Trade in Services"),
    ("CNHK", "2017-06-28", "2017-06-28", 0): [
        ("investment-2017", "supplementary_agreement", "CEPA Investment Agreement", ["investment"]),
        ("ecotech-2017", "supplementary_agreement", "CEPA Agreement on Economic and Technical Cooperation", None),
    ],
    ("JPSG", "2007-11-27", "2008-01-01", 0): ("notes-annex-ii-2007", "exchange_of_letters",
        "Exchange of Diplomatic Notes amending Annexes IIA and IIB of the Agreement"),
    ("JPSG", "2007-03-19", "2007-09-02", 0): ("general-review-protocol-2007", "amending_protocol",
        "Protocol Amending the Agreement between Japan and the Republic of Singapore for a New-Age Economic "
        "Partnership"),
    ("CACL", "2012-04-16", "2013-09-30", 0): ("amending-agreement-2012", "amending_protocol",
        "Agreement to Amend the Free Trade Agreement between the Government of Canada and the Government of the "
        "Republic of Chile"),
    ("CACL", "2017-06-05", "2019-02-05", 0): ("amending-agreements-2017", "amending_protocol",
        "Agreements of 2017 to amend the Free Trade Agreement between the Government of Canada and the Government "
        "of the Republic of Chile"),
    ("CAIL", "2018-05-28", "2019-09-01", 0): ("modernization-2018", "amending_protocol",
        "Modernized Canada-Israel Free Trade Agreement"),
    ("EUCU", "2020-01-30", "2021-01-01", 0): SKIP,  # the United Kingdom's withdrawal: party data
    ("EUOCT", None, None, 0): SKIP,  # no dates; three changes to the legal basis, left for hand review
    ("USKR", "2018-09-24", "2019-01-01", 0): ("amending-protocol-2018", "amending_protocol",
        "Protocol Amending the Free Trade Agreement between the United States of America and the Republic of "
        "Korea"),
    ("AANZFTA", "2014-08-26", "2015-10-01", 0): ("first-protocol-2014", "amending_protocol",
        "First Protocol to Amend the Agreement Establishing the ASEAN-Australia-New Zealand Free Trade Area"),
    ("MKUA", "2022-10-06", "2023-07-06", 0): ("decisions-2022", "joint_committee_decision",
        "Decisions No. 1/2022 and No. 2/2022 of the Joint Committee of the Free Trade Agreement between North "
        "Macedonia and Ukraine"),
    ("EFTAAL", "2015-09-18", "2017-06-01", 0): ("amending-protocol-2015", "amending_protocol",
        "Protocol Amending the Free Trade Agreement between the EFTA States and Albania"),
    ("EFTARS", "2015-05-20", "2017-02-01", 0): ("amending-protocol-2015", "amending_protocol",
        "Protocol Amending the Free Trade Agreement between the EFTA States and Serbia"),
    ("EFTARS", "2018-06-19", "2020-01-01", 0): ("decision-2018-pem-origin", "joint_committee_decision",
        "Joint Committee decision aligning Protocol B with the Regional Convention on Pan-Euro-Mediterranean "
        "preferential rules of origin"),
    ("EFTARS", "2018-06-19", "2021-07-01", 0): ("decision-2018-trade-facilitation", "joint_committee_decision",
        "Joint Committee decision updating Annex IV on trade facilitation"),
    ("EFTARS", "2021-05-28", "2022-01-01", 0): ("decision-2021-transitional-origin", "joint_committee_decision",
        "Joint Committee decision on transitional rules of origin in Protocol B"),
    ("CETA", "2024-10-10", "2025-12-18", 0): ("mra-architects-2024", "other",
        "Mutual Recognition Agreement for architects"),
    ("RSTR", "2018-01-30", "2019-06-01", 0): ("protocol-i-2018", "amending_protocol",
        "Revised Protocol I on agricultural products"),
    # The signature column repeats the FTA's own date; the remarks date the Decision.
    ("GETR", "2007-11-21", "2021-04-29", 0): ("decision-2016-1", "joint_committee_decision",
        "Decision No. 1/2016 of the Joint Committee replacing Protocol II on rules of origin",
        ["goods"], {"signed": "2016-10-28"}),
    ("G-3", "2010-06-11", "2011-08-02", 0): ("amending-protocol-2010", "amending_protocol",
        "Amending Protocol to the Free Trade Agreement between Colombia and Mexico"),
    ("MXUY", "2012-10-01", "2013-03-01", 0): ("amending-protocol-2012", "amending_protocol",
        "Protocol Amending the Free Trade Agreement between the United Mexican States and the Eastern Republic "
        "of Uruguay"),
    ("METR", "2019-07-17", "2022-07-01", 0): ("protocol-i-2019", "amending_protocol",
        "Protocol I on additional concessions on agricultural products"),
    ("EFTABA", "2022-07-07", "2023-09-01", 0): ("annex-ix-protocol-2022", "amending_protocol",
        "Protocol amending the Free Trade Agreement between the EFTA States and Bosnia and Herzegovina (new "
        "Annex IX)"),
    ("EFTABA", "2022-07-07", "2023-09-01", 1): ("agriculture-protocols-2022", "amending_protocol",
        "Protocols amending the Agreements on Agriculture between the EFTA States and Bosnia and Herzegovina "
        "(new Annex IX)"),
    ("CLHK", "2022-01-18", "2023-04-06", 0): ("services-schedules-2022", "amending_protocol",
        "Amendment of the Schedules of Specific Commitments on Trade in Services"),
    ("EFTAME", "2021-07-14", "2022-04-01", 0): ("amending-protocol-2021", "amending_protocol",
        "Protocol Amending the Free Trade Agreement between the EFTA States and Montenegro"),
    ("AFTA", "2019-01-22", "2020-09-20", 0): ("proof-of-origin-protocol-2019", "amending_protocol",
        "Protocol to Amend the ASEAN Trade in Goods Agreement (proof of origin)"),
    ("GBISLINO", "2023-01-30", "2023-02-01", 0): SKIP,  # entry into force with Iceland: party data
    ("GBISLINO", "2022-08-31", "2022-09-01", 0): SKIP,  # entry into force with Liechtenstein, Norway
}

# --- input -------------------------------------------------------------------------------------

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_changes(path: Path) -> list[dict[str, str | None]]:
    """Rows of the ``RTA Changes`` sheet (the workbook's second sheet) as dicts by header."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si"):
                shared.append("".join(t.text or "" for t in si.iter(NS + "t")))
        root = ET.fromstring(z.read("xl/worksheets/sheet2.xml"))
    table = []
    for row in root.iter(NS + "row"):
        cells: dict[str, str | None] = {}
        for c in row.iter(NS + "c"):
            col = re.match(r"[A-Z]+", c.get("r", "")).group(0)
            v, inline = c.find(NS + "v"), c.find(NS + "is")
            if c.get("t") == "s" and v is not None:
                cells[col] = shared[int(v.text)]
            elif c.get("t") == "inlineStr" and inline is not None:
                cells[col] = "".join(t.text or "" for t in inline.iter(NS + "t"))
            else:
                cells[col] = v.text if v is not None else None
        table.append(cells)
    header = table[0]
    return [{header[k]: v for k, v in r.items() if k in header} for r in table[1:]]


def excel_date(value: str | None) -> str | None:
    if not value:
        return None
    return (dt.date(1899, 12, 30) + dt.timedelta(days=int(float(value)))).isoformat()


# --- mapping -----------------------------------------------------------------------------------

DECISION = re.compile(
    r"Decisions? No\.\s*(\d+(?:\s*[–-]\s*\d+)?) of (\d{4}) of the ((?:Joint )?[A-Za-z ,.-]+?Committee)")
SUPPLEMENT = re.compile(
    r"^(Supplement(?: ([IVX]+))? to the Mainland and (?:Macao|Hong Kong) Closer Economic Partnership Arrangement)")


def auto_item(remarks: str) -> tuple[str, str, str] | None:
    """(id, kind, name) for Joint Committee decisions and CEPA Supplements; None otherwise."""
    m = DECISION.search(remarks)
    if m:
        number = re.sub(r"\s*[–-]\s*", "-", m.group(1))
        plural = "Decisions" if "-" in number else "Decision"
        return (f"decision-{m.group(2)}-{number}", "joint_committee_decision",
                f"{plural} No. {number} of {m.group(2)} of the {m.group(3)}")
    m = SUPPLEMENT.match(remarks)
    if m:
        return f"supplement-{ROMAN[m.group(2) or '']}", "amending_protocol", m.group(1)
    return None


def wto_items(rows: list[dict], by_rta: dict[int, str]) -> tuple[dict[str, list[dict]], list[str]]:
    items: dict[str, list[dict]] = {}
    problems: list[str] = []
    seen: dict[tuple, int] = {}
    for row in rows:
        rta = int(row["RTA ID"])
        if rta == LAIA_RTA_ID:
            continue
        rid = by_rta[rta]
        signed, in_force = excel_date(row.get("Date of signature of changes")), excel_date(
            row.get("Date of entry into force of changes"))
        key3 = (rid, signed, in_force)
        n = seen.get(key3, 0)
        seen[key3] = n + 1
        remarks = " ".join((row.get("Remarks") or "").split())
        coverage = COVERAGE.get((row.get("Changes affect") or "").strip())
        if (rid, signed) in MERGE:
            items.setdefault(rid, []).append({"merge": MERGE[(rid, signed)], "signed": signed, "in_force": in_force,
                                              "coverage": coverage, "provenance": [wto(rta)]})
            continue
        spec = OVERRIDES.get((*key3, n))
        if spec == SKIP:
            continue
        specs = spec if isinstance(spec, list) else [spec] if spec else []
        if not specs:
            auto = auto_item(remarks)
            if not auto:
                problems.append(f"{rid} {signed} {in_force}: no name for: {remarks[:90]}")
                continue
            specs = [auto]
        for s in specs:
            iid, kind, name = s[0], s[1], s[2]
            cov = s[3] if len(s) > 3 else coverage
            dates = {"signed": signed, "in_force": in_force}
            if len(s) > 4 and s[4]:
                dates.update(s[4])
            item = {"id": iid, "kind": kind, "name": name, "status": "in_force" if dates["in_force"] else "signed",
                    **{k: v for k, v in dates.items() if v}}
            if cov:
                item["coverage"] = cov
            item["provenance"] = [wto(rta)]
            items.setdefault(rid, []).append(item)
    return items, problems


def merge_into(base: dict, extra: dict) -> None:
    """Merge a WTO row into a MOFCOM item: keep MOFCOM dates, fill gaps, note conflicts."""
    conflicts = []
    for key in ("signed", "in_force"):
        if extra.get(key) and not base.get(key):
            base[key] = extra[key]
            if key == "in_force":
                base["status"] = "in_force"
        elif extra.get(key) and extra[key] != base.get(key):
            conflicts.append(f"{'signature' if key == 'signed' else 'entry into force'} on {extra[key]}")
    if conflicts:
        base["notes"] = (base.get("notes", "") + f" WTO RTA-IS gives {' and '.join(conflicts)}.").strip()
    if extra.get("coverage") and not base.get("coverage"):
        base["coverage"] = extra["coverage"]
    base["provenance"] = base["provenance"] + extra["provenance"]


def ordered(item: dict, order: list[str]) -> dict:
    return {k: item[k] for k in order if k in item}


def with_instruments(record: dict, instruments: list[dict]) -> dict:
    """The record with ``instruments`` set, other keys left in their order."""
    record = {k: v for k, v in record.items() if k != "instruments"}
    anchor = "notes" if "notes" in record else None
    out: dict = {}
    for key, value in record.items():
        if anchor is None and key in INSTRUMENTS_BEFORE and "instruments" not in out:
            out["instruments"] = instruments
        out[key] = value
        if key == anchor:
            out["instruments"] = instruments
    out.setdefault("instruments", instruments)
    return out


def load_mofcom_updates() -> dict[str, dict]:
    path = Path(__file__).with_name("import_mofcom_fta.py")
    spec = importlib.util.spec_from_file_location("import_mofcom_fta", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UPDATES


def strip_mofcom_notes(record: dict, upd: dict) -> None:
    """Remove the sentences and ``notes`` provenance rows that import_mofcom_fta.py appended."""
    text = upd.get("append_notes")
    if text and record.get("notes"):
        notes = record["notes"].replace(text, "").strip()
        if notes:
            record["notes"] = notes
        else:
            del record["notes"]
    added = [row for row in upd.get("provenance") or [] if row.get("field") == "notes"]
    record["provenance"] = [row for row in record.get("provenance") or [] if row not in added]


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    write = "--write" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    paths = sorted(REGISTRY.glob("*.yaml"))
    records = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths}
    by_rta = {int(r["wto_rta_id"]): rid for rid, r in records.items() if r.get("wto_rta_id")}
    from_wto, problems = wto_items(read_changes(Path(args[0])), by_rta)
    updates = load_mofcom_updates()

    changed = 0
    for rid in sorted(set(MOFCOM_ITEMS) | set(from_wto)):
        record = records[rid]
        if record.get("instruments"):
            problems.append(f"{rid}: already has instruments; skipped")
            continue
        items = [dict(i, provenance=list(i["provenance"])) for i in MOFCOM_ITEMS.get(rid, [])]
        by_id = {i["id"]: i for i in items}
        for item in from_wto.get(rid, []):
            if "merge" in item:
                merge_into(by_id[item["merge"]], item)
            elif item["id"] in by_id:
                problems.append(f"{rid}: duplicate instrument id {item['id']}")
            else:
                items.append(item)
                by_id[item["id"]] = item
        if rid in MOFCOM_ITEMS:
            strip_mofcom_notes(record, updates.get(rid, {}))
        if rid in KEEP_NOTES:
            text, prov = KEEP_NOTES[rid]
            record["notes"] = f"{record.get('notes', '')} {text}".strip()
            record["provenance"].append(prov)
        items.sort(key=lambda i: (i.get("signed") is None, i.get("signed") or "", i["id"]))
        record = records[rid] = with_instruments(record, [ordered(i, ITEM_ORDER) for i in items])
        new = yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)
        changed += 1
        if write:
            (REGISTRY / f"{rid}.yaml").write_text(new, encoding="utf-8")
    total = sum(len(records[r].get("instruments") or []) for r in records)
    for p in problems:
        print("problem:", p)
    print(f"records {changed}, instruments {total}, problems {len(problems)}{'' if write else ' (dry run)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
