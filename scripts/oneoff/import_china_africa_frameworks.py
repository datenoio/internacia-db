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
  and the Chinese Embassy in Zambia dates the Zambian one to June 2025;
- three for which MOFCOM published no release: Cameroon (10 December 2025, reported by the
  state daily Cameroon Tribune), Botswana (April 2026) and Togo (23 April 2026), both dated on
  the bilateral relations pages of the Chinese Ministry of Foreign Affairs.

Countries that already have a record (an early harvest arrangement: CGCN, CNKE, CNSC, CNGA)
get the framework agreement in their notes. Three of the 40 are not named in any source found
(MOFCOM's site search needs a captcha); they are left for a later walk.

Idempotent: existing records and notes already added are skipped.
Usage: python -I scripts/oneoff/import_china_africa_frameworks.py [--write]
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
MFA = "Ministry of Foreign Affairs of the People's Republic of China"
MFA_AFRICA = "https://www.mfa.gov.cn/web/gjhdq_676201/gj_676203/fz_677316/"
BOTSWANA = MFA_AFRICA + "1206_677438/sbgx_677442/"
BOTSWANA_2026 = MFA_AFRICA + "1206_677438/1207_677450/202610/t20261013_12039645.shtml"
TOGO = MFA_AFRICA + "1206_677534/sbgx_677538/"
TOGO_2026 = MFA_AFRICA + "1206_677534/1207_677546/202610/t20261015_12041062.shtml"
CAMEROON = ("https://cameroon-tribune.cm/article.html/74474/fr.html/"
            "cooperation-commerciale-cameroun-chine-coup-daccelerateur")
CAMEROON_BIC = ("https://www.businessincameroon.com/public-management/"
                "1212-15487-cameroon-china-trade-pact-opens-door-to-tariff-free-push-for-cameroon-exports")
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

UNANNOUNCED_NOTE = " MOFCOM published no release on it, so its place in MOFCOM's count of 40 is not known."
# alpha-2 -> (short name, official name, signed, notes, [(field, url, source)])
UNANNOUNCED = {
    "CM": ("Cameroon", "the Republic of Cameroon", "2025-12-10",
           "Signed in Yaoundé on 10 December 2025, at the Ministry of External Relations, by the Minister of Trade "
           "Luc Magloire Mbarga Atangana and the Chinese Ambassador Xu Yong. The minister called it the first stage "
           "of negotiations on market access, manufacturing and agriculture." + UNANNOUNCED_NOTE,
           [("parties", CAMEROON, "Cameroon Tribune (SOPECAM, the state daily)"),
            ("signed", CAMEROON, "Cameroon Tribune (SOPECAM, the state daily)"),
            ("notes", CAMEROON_BIC, "Business in Cameroon")]),
    "BW": ("Botswana", "the Republic of Botswana", "2026-04",
           "Signed in April 2026 (Chinese Ministry of Foreign Affairs, bilateral relations page). In their joint "
           "statement of October 2026 the two sides agreed to work for an early harvest arrangement, signed in line "
           "with the procedures of the Southern African Customs Union and its members (SACUCN)." + UNANNOUNCED_NOTE,
           [("parties", BOTSWANA, MFA), ("signed", BOTSWANA, MFA), ("notes", BOTSWANA_2026, MFA)]),
    "TG": ("Togo", "the Togolese Republic", "2026-04-23",
           "Signed on 23 April 2026 (Chinese Ministry of Foreign Affairs, bilateral relations page). In their joint "
           "statement of October 2026 the two sides agreed to build on the framework agreement and advance the "
           "follow-up module negotiations." + UNANNOUNCED_NOTE,
           [("parties", TOGO, MFA), ("signed", TOGO, MFA), ("notes", TOGO_2026, MFA)]),
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
    for code, (short, official, signed, notes, sources) in UNANNOUNCED.items():
        records.append(framework(code, short, official, signed, notes,
                                 [prov(field, url, source) for field, url, source in sources]))
    return records


def main(argv: list[str]) -> int:
    write = "--write" in argv
    problems = written = updated = 0
    for record in new_records():
        path = REGISTRY / f"{record['id']}.yaml"
        if path.exists():
            continue
        written += 1
        if write:
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    for rid, (text, url) in {**NOTES, "CNGA": (None, FOCAC_2024)}.items():
        path = REGISTRY / f"{rid}.yaml"
        record: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
        if (text or GABON_NEW) in record.get("notes", ""):
            continue
        if rid == "CNGA":
            if GABON_OLD not in record["notes"]:
                print("CNGA notes changed; skipped")
                problems += 1
                continue
            record["notes"] = record["notes"].replace(GABON_OLD, GABON_NEW)
        else:
            record["notes"] = f"{record.get('notes', '').strip()} {text}".strip()
        record["provenance"].append(prov("notes", url))
        updated += 1
        if write:
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    print(f"new {written}, updated {updated}, problems {problems}{'' if write else ' (dry run)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
