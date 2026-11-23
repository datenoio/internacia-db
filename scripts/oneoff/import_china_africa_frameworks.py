#!/usr/bin/env python3
"""One-off: China–Africa framework agreements on economic partnership for shared development.

MOFCOM counted 40 framework agreements with African countries by September 2026.
``import_mofcom_fta.py`` added four of them (South Africa, Nigeria, Namibia, Cabo Verde) and
the early harvest records (Congo, Kenya, Seychelles, Gabon). This script adds the others that
official releases name, checked on 2026-11-23:

- the 22 agreed and signed during the FOCAC Beijing Summit in September 2024 (MOFCOM release,
  reprinted on the summit website);
- Kenya, signed in Beijing on 24 April 2025 (minister Wang Wentao's activity page);
- seven that MOFCOM reported on 1 July 2025 as recently signed; the release gives no dates,
  and the Chinese Embassy in Zambia dates the Zambian one to June 2025.

Countries that already have a record (an early harvest arrangement: CGCN, CNKE, CNSC, CNGA)
get the framework agreement in their notes. Six of the 40 are not named in any release found
(MOFCOM's site search needs a captcha); they are left for a later walk.

Not idempotent: notes are appended. Usage: python -I scripts/oneoff/import_china_africa_frameworks.py [--write]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
MOFCOM = "Ministry of Commerce of the People's Republic of China"
FOCAC_2024 = "https://2024focacsummit.mfa.gov.cn/pthd/202409/t20240914_11490655.htm"
BATCH_2025 = "https://sms.mofcom.gov.cn/gzdt/art/2025/art_0126506c021243b7b8384c7a83fee32c.html"
ZAMBIA = "https://zm.china-embassy.gov.cn/sbgx/jm/202507/t20250704_11665721.htm"
KENYA = "http://wangwentao.mofcom.gov.cn/zyhd/art/2025/art_fc16c5055c4e4ba881b350c613d65e8f.html"
AFRICA_PAGE = "https://fta.mofcom.gov.cn/channel/african_special.shtml"
TITLE = ("Framework Agreement on Economic Partnership for Shared Development between the Government of the "
         "People's Republic of China and the Government of {}")
SCOPE = ("It sets out objectives, principles, the scope of negotiations, institutional arrangements, entry into "
         "force, amendment and termination, and future negotiations on trade, investment and other specific areas.")
FOCAC_NOTE = ("One of the 22 framework agreements on economic partnership for shared development that China and "
              "African countries agreed and signed during the Beijing Summit of the Forum on China-Africa Cooperation "
              "in September 2024. " + SCOPE)
BATCH_NOTE = ("One of seven framework agreements on economic partnership for shared development, with Angola, Benin, "
              "the Gambia, Ghana, Senegal, Somalia and Zambia, that MOFCOM reported on 1 July 2025 as recently signed; "
              "the release gives no signing dates.")

# alpha-2 -> (short name, official name with article)
FOCAC = {
    "ET": ("Ethiopia", "the Federal Democratic Republic of Ethiopia"),
    "BI": ("Burundi", "the Republic of Burundi"),
    "GQ": ("Equatorial Guinea", "the Republic of Equatorial Guinea"),
    "CD": ("Democratic Republic of the Congo", "the Democratic Republic of the Congo"),
    "DJ": ("Djibouti", "the Republic of Djibouti"),
    "ZW": ("Zimbabwe", "the Republic of Zimbabwe"),
    "GW": ("Guinea-Bissau", "the Republic of Guinea-Bissau"),
    "KM": ("Comoros", "the Union of the Comoros"),
    "CI": ("Côte d'Ivoire", "the Republic of Côte d'Ivoire"),
    "LR": ("Liberia", "the Republic of Liberia"),
    "LY": ("Libya", "the State of Libya"),
    "MG": ("Madagascar", "the Republic of Madagascar"),
    "MR": ("Mauritania", "the Islamic Republic of Mauritania"),
    "SS": ("South Sudan", "the Republic of South Sudan"),
    "SL": ("Sierra Leone", "the Republic of Sierra Leone"),
    "ST": ("Sao Tome and Principe", "the Democratic Republic of São Tomé and Príncipe"),
    "UG": ("Uganda", "the Republic of Uganda"),
    "TD": ("Chad", "the Republic of Chad"),
    "CF": ("Central African Republic", "the Central African Republic"),
}
BATCH = {
    "AO": ("Angola", "the Republic of Angola"),
    "GM": ("Gambia", "the Republic of the Gambia"),
    "SO": ("Somalia", "the Federal Republic of Somalia"),
    "ZM": ("Zambia", "the Republic of Zambia"),
    "BJ": ("Benin", "the Republic of Benin"),
    "GH": ("Ghana", "the Republic of Ghana"),
    "SN": ("Senegal", "the Republic of Senegal"),
}

# Existing early harvest records: the framework agreement goes in their notes.
NOTES = {
    "CGCN": ("The framework agreement on economic partnership for shared development was one of the 22 signed "
             "during the FOCAC Beijing Summit in September 2024.", FOCAC_2024),
    "CNSC": ("The framework agreement on economic partnership for shared development was one of the 22 signed "
             "during the FOCAC Beijing Summit in September 2024.", FOCAC_2024),
    "CNKE": ("The framework agreement on economic partnership for shared development was signed in Beijing on "
             "24 April 2025, during President Ruto's state visit.", KENYA),
}
GABON_OLD = ("Gabon was among the first African countries to sign a framework agreement on economic partnership "
             "for shared development with China (MOFCOM gives no date).")
GABON_NEW = ("Gabon signed a framework agreement on economic partnership for shared development with China during "
             "the FOCAC Beijing Summit in September 2024, one of the first 22.")


def prov(field: str, url: str, source: str = MOFCOM) -> dict[str, str]:
    return {"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED}


def record_id(code: str) -> str:
    return "".join(sorted([code, "CN"]))


def framework(code: str, short: str, official: str, signed: str, notes: str, sources: list[dict]) -> dict:
    return {
        "id": record_id(code),
        "name": TITLE.format(official),
        "other_names": [{"lang": "en",
                         "name": f"China-{short} Framework Agreement on Economic Partnership for Shared Development"}],
        "agreement_type": "framework",
        "status": "signed",
        "signed": signed,
        "parties": [{"id": "CN", "type": "country"}, {"id": code, "type": "country"}],
        "links": [{"url": AFRICA_PAGE, "type": "website"}],
        "notes": notes,
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": sources,
    }


def new_records() -> list[dict]:
    records = []
    for code, (short, official) in FOCAC.items():
        records.append(framework(code, short, official, "2024-09", FOCAC_NOTE,
                                 [prov("parties", FOCAC_2024), prov("signed", FOCAC_2024)]))
    for code, (short, official) in BATCH.items():
        if code == "ZM":
            notes = (BATCH_NOTE + " The Chinese Embassy in Zambia reports that Minister Wang Wentao and Minister "
                     "Mulenga signed it during the June 2025 Ministerial Meeting of Coordinators on the "
                     "Implementation of FOCAC Follow-up Actions and the China-Africa Economic and Trade Expo.")
            sources = [prov("parties", BATCH_2025), prov("signed", ZAMBIA, "Embassy of the People's Republic of "
                                                         "China in the Republic of Zambia")]
            signed = "2025-06"
        else:
            notes, sources, signed = BATCH_NOTE, [prov("parties", BATCH_2025), prov("signed", BATCH_2025)], "2025"
        records.append(framework(code, short, official, signed, notes, sources))
    return records


def main(argv: list[str]) -> int:
    write = "--write" in argv
    problems = 0
    for record in new_records():
        path = REGISTRY / f"{record['id']}.yaml"
        if path.exists():
            print("exists:", path.name)
            problems += 1
        elif write:
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    for rid, (text, url) in {**NOTES, "CNGA": (None, FOCAC_2024)}.items():
        path = REGISTRY / f"{rid}.yaml"
        record: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
        if rid == "CNGA":
            if GABON_OLD not in record["notes"]:
                print("CNGA notes changed; skipped")
                problems += 1
                continue
            record["notes"] = record["notes"].replace(GABON_OLD, GABON_NEW)
        else:
            record["notes"] = f"{record.get('notes', '').strip()} {text}".strip()
        record["provenance"].append(prov("notes", url))
        if write:
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    print(f"new {len(new_records())}, updated {len(NOTES) + 1}, problems {problems}{'' if write else ' (dry run)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
