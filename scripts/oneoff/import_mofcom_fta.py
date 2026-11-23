#!/usr/bin/env python3
"""One-off: add China FTA Network (MOFCOM) facts to data/trade_agreements/.

Source: the China FTA Network of the Ministry of Commerce of the People's Republic of China,
https://fta.mofcom.gov.cn/ (English and Chinese pages, checked on 2026-11-23). Its news lists
are served by ``POST /edi_ecms_web_front/front/fta/list`` (form fields ``cid`` and
``pageNumber``); every fact below was read from the release cited in its provenance.

The data is curated by hand in this file, not parsed:

- ``NEW``: agreements and framework agreements the registry did not hold. MOFCOM is a party
  government, so these records are ``verification: official``.
- ``UPDATES``: names, links, notes and provenance for existing records (upgrade protocols,
  early harvest arrangements, joint feasibility studies, dead MOFCOM links).

Upgrade protocols are recorded in ``notes`` until the schema has a field for them.

Usage: python -I scripts/oneoff/import_mofcom_fta.py [--write]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SOURCE = "Ministry of Commerce of the People's Republic of China, China FTA Network"
B = "https://fta.mofcom.gov.cn"

# Canonical key order; keys a record lacks are inserted after their nearest present predecessor.
ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wikidata_id", "links", "description", "notes",
    "wto_rta_id", "aric_id", "verification", "last_verified", "provenance",
]


def prov(field: str, path: str) -> dict[str, str]:
    return {"field": field, "source": SOURCE, "url": B + path, "retrieved_at": RETRIEVED}


def site(path: str) -> dict[str, str]:
    return {"url": B + path, "type": "website"}


def pair(other: str) -> list[dict[str, str]]:
    return [{"id": "CN", "type": "country"}, {"id": other, "type": "country"}]


# --- new records ------------------------------------------------------------------------------

PACIFIC = "/topic/enpacificislands.shtml"
PACIFIC_FIVE = "/article/c/zhengwugk/202511/57422.html"
EEPA_SCOPE = (
    "It covers objectives, principles, the scope of negotiations on specific areas, contact points and "
    "institutional arrangements; market access is left to those negotiations."
)
AFRICA = "/channel/african_special.shtml"
EPSD = "Framework Agreement on Economic Partnership for Shared Development between the Government of the People's Republic of China and the Government of"  # noqa: E501
EHA = "Early Harvest Arrangement of the Agreement on Economic Partnership for Shared Development between the Government of the People's Republic of China and the Government of"  # noqa: E501
def zero_tariff(partner: str) -> str:
    return (
        f"Under the arrangement China moves to zero tariffs on 100% of tariff lines for {partner}, which further "
        "opens its market to Chinese goods."
    )

NOT_IN_FORCE = "MOFCOM had announced no entry into force by 23 November 2026."


def eepa(cid: str, country: str, signed: str, article: str, extra: str = "") -> dict[str, Any]:
    """A China-Pacific Island country framework agreement on enhanced economic partnership."""
    party = cid[2:4]
    return {
        "id": cid,
        "name": f"China-{country} Framework Agreement on Enhanced Economic Partnership",
        "agreement_type": "framework",
        "status": "signed",
        "signed": signed,
        "parties": pair(party),
        "links": [site(PACIFIC)],
        "notes": (f"Framework agreement on enhanced economic partnership (EEPA) signed on {extra}").strip(),
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [prov("parties", article), prov("signed", article), prov("notes", article)],
    }


def framework(cid: str, country: str, official: str, zh: str, signed: str, article: str, notes: str) -> dict:
    """A China-African country framework agreement on economic partnership for shared development."""
    return {
        "id": cid,
        "name": f"{EPSD} {official}",
        "other_names": [
            {"lang": "en", "name": f"China-{country} Framework Agreement on Economic Partnership for Shared Development"},
            {"lang": "zh", "name": zh},
        ],
        "agreement_type": "framework",
        "status": "signed",
        "signed": signed,
        "parties": pair(cid[2:4]),
        "links": [site(AFRICA)],
        "notes": notes,
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [prov("parties", article), prov("signed", article), prov("notes", article)],
    }


NEW: list[dict[str, Any]] = [
    {
        "id": "CNHN",
        "name": "Early Harvest Arrangement for the Free Trade Agreement between the Government of the People's "
        "Republic of China and the Government of the Republic of Honduras",
        "other_names": [
            {"lang": "en", "name": "China-Honduras FTA Early Harvest Arrangement"},
            {"lang": "zh", "name": "中华人民共和国政府和洪都拉斯共和国政府关于自由贸易协定早期收获的安排"},
        ],
        "agreement_type": "pta",
        "status": "in_force",
        "signed": "2024-02-07",
        "in_force": "2024-09-01",
        "parties": pair("HN"),
        "links": [site("/topic/enhonduras.shtml"), site("/channel/honduras_special.shtml")],
        "notes": "Early harvest arrangement of the China-Honduras FTA, signed by video link on 7 February 2024 and "
        "in force from 1 September 2024. Negotiations on the full FTA were launched on 4 July 2023 and had held "
        "six rounds by September 2024; MOFCOM still listed them as under negotiation on 23 November 2026.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("name", "/article/e/enhonduras/enhondurasnews/202402/55869.html"),
            prov("parties", "/article/c/zhengwugk/202409/55879.html"),
            prov("signed", "/article/c/zhengwugk/202409/55879.html"),
            prov("in_force", "/article/c/zhengwugk/202409/55879.html"),
            prov("notes", "/article/c/zhengwugk/202307/54167.html"),
            prov("notes", "/fta_tanpan.shtml"),
        ],
    },
    {
        "id": "CNSV",
        "name": "China-El Salvador Free Trade Agreement",
        "other_names": [{"lang": "zh", "name": "中国—萨尔瓦多自由贸易协定"}],
        "agreement_type": "fta",
        "status": "negotiating",
        "parties": pair("SV"),
        "links": [site("/channel/elsalvador_special.shtml")],
        "notes": "Negotiations were launched by video link on 17 April 2024; the first round was held in Beijing "
        "in August 2024 and the second in San Salvador in November 2024.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("status", "/article/c/zhengwugk/202404/55403.html"),
            prov("parties", "/article/c/zhengwugk/202404/55403.html"),
            prov("notes", "/article/c/elsalvador/elsalvadornews/202411/56058.html"),
        ],
    },
    {
        "id": "CNPS",
        "name": "China-Palestine Free Trade Agreement",
        "other_names": [{"lang": "zh", "name": "中国—巴勒斯坦自由贸易协定"}],
        "agreement_type": "fta",
        "status": "negotiating",
        "parties": pair("PS"),
        "links": [site("/channel/palestine_special.shtml")],
        "notes": "A joint feasibility study was launched in November 2017 and completed in July 2018. Negotiations "
        "were launched by a memorandum of understanding signed on 23 October 2018.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("status", "/article/c/zhengwugk/201810/39219.html"),
            prov("parties", "/article/c/zhengwugk/201810/39219.html"),
            prov("notes", "/article/c/zhengwugk/201807/38397.html"),
        ],
    },
    {
        "id": "CNUY",
        "name": "China-Uruguay Free Trade Agreement",
        "other_names": [{"lang": "zh", "name": "中国—乌拉圭自由贸易协定"}],
        "agreement_type": "fta",
        "status": "proposed",
        "parties": pair("UY"),
        "notes": "A joint feasibility study launched in September 2021 was completed by July 2022 (MOFCOM "
        "spokesperson, 14 July 2022); no negotiations have been launched, and MOFCOM's list of agreements under "
        "study did not include it on 23 November 2026. Uruguay is a MERCOSUR member; see MERCOSURCN.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("status", "/article/c/zhengwugk/202207/49182.html"),
            prov("parties", "/article/c/zhengwugk/202207/49182.html"),
            prov("notes", "/fta_yanjiu.shtml"),
        ],
    },
    eepa("CNFM", "Federated States of Micronesia", "2025-11-04", PACIFIC_FIVE,
         f"4 November 2025, the same day as those with Fiji, Kiribati, Nauru and Vanuatu. {EEPA_SCOPE}"),
    eepa("CNKI", "Kiribati", "2025-11-04", PACIFIC_FIVE,
         f"4 November 2025, the same day as those with Fiji, Micronesia, Nauru and Vanuatu. {EEPA_SCOPE}"),
    eepa("CNNR", "Nauru", "2025-11-04", PACIFIC_FIVE,
         f"4 November 2025, the same day as those with Fiji, Kiribati, Micronesia and Vanuatu. {EEPA_SCOPE}"),
    eepa("CNVU", "Vanuatu", "2025-11-04", PACIFIC_FIVE,
         f"4 November 2025, the same day as those with Fiji, Kiribati, Micronesia and Nauru. {EEPA_SCOPE} The "
         "first round of negotiations on the China-Vanuatu Enhanced Economic Partnership Agreement was held by "
         "video on 6-10 July 2026 and the second in Beijing on 12-16 October 2026."),
    eepa("CNFJ-EEPA", "Fiji", "2025-11-04", PACIFIC_FIVE,
         f"4 November 2025, the same day as those with Kiribati, Micronesia, Nauru and Vanuatu. {EEPA_SCOPE} The "
         "earlier FTA joint feasibility study is recorded as CNFJ."),
    eepa("CNTO", "Tonga", "2025-11-25", "/article/c/zhengwugk/202511/57514.html",
         f"25 November 2025 in Beijing. {EEPA_SCOPE}"),
    eepa("CNPG-EEPA", "Papua New Guinea", "2026-05-21", "/article/c/zhengwugk/202605/58437.html",
         f"21 May 2026, during the APEC trade ministers' meeting, with a joint statement. {EEPA_SCOPE} The FTA "
         "joint feasibility study is recorded as CNPG."),
    eepa("CNSB", "Solomon Islands", "2026-07-14", "/article/c/zhengwugk/202607/100169.html",
         f"14 July 2026. {EEPA_SCOPE}"),
    {
        "id": "CNKE",
        "name": f"{EHA} the Republic of Kenya",
        "other_names": [
            {"lang": "en", "name": "China-Kenya Early Harvest Arrangement"},
            {"lang": "zh", "name": "中华人民共和国政府和肯尼亚共和国政府关于共同发展经济伙伴关系协定早期收获的安排"},
        ],
        "agreement_type": "fta",
        "status": "signed",
        "signed": "2026-03-24",
        "parties": pair("KE"),
        "links": [site(AFRICA)],
        "notes": "Signed on 24 March 2026; the second early harvest arrangement between China and an African "
        f"country, after the Republic of the Congo (CGCN). {zero_tariff('Kenya')} {NOT_IN_FORCE}",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("name", "/article/e/enrelease/202603/58178.html"),
            prov("parties", "/article/c/zhengwugk/202603/58059.html"),
            prov("signed", "/article/c/zhengwugk/202603/58059.html"),
            prov("notes", "/article/e/enrelease/202603/58178.html"),
        ],
    },
    {
        "id": "CNSC",
        "name": f"{EHA} the Republic of Seychelles",
        "other_names": [
            {"lang": "en", "name": "China-Seychelles Early Harvest Arrangement"},
            {"lang": "zh", "name": "中华人民共和国政府与塞舌尔共和国政府关于共同发展经济伙伴关系协定早期收获的安排"},
        ],
        "agreement_type": "fta",
        "status": "signed",
        "signed": "2026-09-10",
        "parties": pair("SC"),
        "links": [site(AFRICA)],
        "notes": f"Signed on 10 September 2026. {zero_tariff('Seychelles')} {NOT_IN_FORCE}",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("parties", "/article/c/zhengwugk/202609/100215.html"),
            prov("signed", "/article/c/zhengwugk/202609/100215.html"),
            prov("notes", "/article/c/zhengwugk/202609/100215.html"),
        ],
    },
    {
        "id": "CNGA",
        "name": "Early Harvest Arrangement of the China-Gabon Agreement on Economic Partnership for Shared "
        "Development",
        "other_names": [{"lang": "zh", "name": "中国和加蓬共同发展经济伙伴关系协定早期收获安排"}],
        "agreement_type": "fta",
        "status": "negotiating",
        "parties": pair("GA"),
        "links": [site(AFRICA)],
        "notes": "Gabon was among the first African countries to sign a framework agreement on economic partnership "
        "for shared development with China (MOFCOM gives no date). After a round of negotiations in October 2026, "
        "a memorandum of understanding concluding the early harvest negotiations was signed on 6 November 2026; "
        "the arrangement itself had not been signed by 23 November 2026.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("parties", "/article/c/zhengwugk/202611/100311.html"),
            prov("status", "/article/c/zhengwugk/202611/100311.html"),
            prov("notes", "/article/c/zhengwugk/202611/100311.html"),
        ],
    },
    framework(
        "CNZA", "South Africa", "the Republic of South Africa", "中华人民共和国政府和南非共和国政府共同发展经济伙伴关系框架协定",
        "2026-02-06", "/article/c/zhengwugk/202602/57880.html",
        "Signed in Beijing on 6 February 2026 after the ninth meeting of the China-South Africa Joint Economic "
        "and Trade Committee; the 33rd framework agreement of this kind between China and an African country. "
        "Negotiations on an early harvest arrangement with the Southern African Customs Union, of which South "
        "Africa is a member, opened in October 2026 (SACUCN).",
    ),
    framework(
        "CNNG", "Nigeria", "the Federal Republic of Nigeria", "中华人民共和国政府和尼日利亚联邦共和国政府共同发展经济伙伴关系框架协定",
        "2026-03-26", "/article/c/zhengwugk/202603/58060.html",
        "Signed on 26 March 2026, during the 14th WTO Ministerial Conference; the 34th framework agreement of this "
        "kind between China and an African country.",
    ),
    framework(
        "CNNA", "Namibia", "the Republic of Namibia", "中华人民共和国政府和纳米比亚共和国政府共同发展经济伙伴关系框架协定",
        "2026-07", "/article/c/zhengwugk/202607/100168.html",
        "Signed in Beijing in July 2026 (MOFCOM release of 16 July 2026); the 38th framework agreement of this "
        "kind between China and an African country. Namibia is a member of the Southern African Customs Union "
        "(SACUCN).",
    ),
    framework(
        "CNCV", "Cabo Verde", "the Republic of Cabo Verde", "中华人民共和国政府和佛得角共和国政府共同发展经济伙伴关系框架协定",
        "2026-09-09", "/article/e/enrelease/202609/100219.html",
        "Signed in Beijing on 9 September 2026; the 40th framework agreement of this kind between China and an "
        "African country. The two sides confirmed the same day that negotiations on the early harvest "
        "arrangement had been substantially concluded.",
    ),
]

# --- updates to existing records ---------------------------------------------------------------

UPDATES: dict[str, dict[str, Any]] = {
    "CGCN": {
        "name": f"{EHA} the Republic of the Congo",
        "other_names": [
            {"lang": "en", "name": "China - Congo"},
            {"lang": "zh", "name": "中华人民共和国政府与刚果共和国政府关于共同发展经济伙伴关系协定早期收获的安排"},
        ],
        "links": [site("/topic/encongo.shtml")],
        "notes": "A joint statement launching negotiations on the China-Republic of the Congo Agreement on Economic "
        "Partnership for Shared Development was signed in Changsha on 11 June 2025. The early harvest arrangement, "
        "signed in Shanghai on 4 November 2025 and in force from 1 April 2026, covers tariff reductions on goods, "
        "rules of origin and institutional provisions; it is the first such arrangement between China and an "
        f"African country. {zero_tariff('the Republic of the Congo')} WTO RTA-IS lists it as China - Congo.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("name", "/article/e/enrelease/202511/57755.html"),
            prov("signed", "/article/c/zhengwugk/202604/58083.html"),
            prov("in_force", "/article/c/zhengwugk/202604/58083.html"),
            prov("notes", "/article/c/zhengwugk/202506/57744.html"),
        ],
    },
    "BYCN": {
        "name": "Agreement on Trade in Services and Investment between the Government of the People's Republic of "
        "China and the Government of the Republic of Belarus",
        "other_names": [
            {"lang": "en", "name": "China - Belarus"},
            {"lang": "en", "name": "China-Belarus Service and Investment Agreement"},
            {"lang": "zh", "name": "中华人民共和国政府和白俄罗斯共和国政府服务贸易和投资协定"},
        ],
        "links": [site("/topic/enbelarus.shtml")],
        "notes": "Negotiations were launched in December 2020. Signed on 22 August 2024 and in force from 1 January "
        "2026, it covers trade in services (positive list), investment (pre-establishment national treatment with a "
        "negative list for non-services sectors) and the temporary entry of business persons. MOFCOM describes it as "
        "China's first free trade agreement with a member state of the Eurasian Economic Union. WTO RTA-IS lists it "
        "as China - Belarus.",
        "verification": "official",
        "last_verified": RETRIEVED,
        "provenance": [
            prov("name", "/article/c/zhengwugk/202408/56111.html"),
            prov("signed", "/article/c/zhengwugk/202408/56111.html"),
            prov("in_force", "/article/c/zhengwugk/202512/57637.html"),
            prov("notes", "/article/c/zhengwugk/202512/57637.html"),
        ],
    },
    "CNKR": {
        "replace_links": {B + "/korea/korea_special.shtml": B + "/topic/enkorea.shtml"},
        "append_notes": "Second-phase negotiations on investment and trade in services on a negative-list basis were "
        "launched in December 2017 and held 17 formal rounds from March 2018; MOFCOM announced their substantial "
        "conclusion on 19 November 2026, with signature pending.",
        "provenance": [prov("notes", "/article/c/zhengwugk/202611/100346.html")],
    },
    "CNRS": {"replace_provenance_urls": {B + "/english/fta_qianshu.shtml": B + "/fta_qianshu.shtml"}},
    "CHCN": {
        "links": [site("/topic/enswiss.shtml")],
        "append_notes": "A joint study on upgrading the agreement was launched in January 2017. Upgrade negotiations "
        "launched in September 2024 were concluded with a memorandum of understanding on 20 August 2026; the "
        "Enhancement Protocol was signed in Beijing on 30 October 2026 and is not yet in force.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/202608/100187.html"),
            prov("notes", "/article/e/enrelease/202611/100316.html"),
        ],
    },
    "CNPE": {
        "links": [site("/topic/enperu.shtml")],
        "append_notes": "Upgrade negotiations were launched in November 2018; the Optimization Protocol, signed on "
        "14 November 2024, entered into force on 1 November 2026.",
        "provenance": [prov("notes", "/article/e/enrelease/202611/100318.html")],
    },
    "CNSG": {
        "links": [site("/topic/china_singapore_upgrade.shtml")],
        "append_notes": "Protocols amending the agreement were signed in July 2011 and November 2018; the Upgrade "
        "Protocol signed on 12 November 2018 entered into force on 16 October 2019. Further upgrade negotiations "
        "launched on 8 December 2020 led to a protocol on further upgrading the agreement, signed in December 2023 "
        "with services and investment commitments on a negative-list basis and in force from 31 December 2024.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/201910/41637.html"),
            prov("notes", "/article/c/zhengwugk/202412/56246.html"),
        ],
    },
    "CNNZ": {
        "links": [site("/topic/ennewzealand.shtml")],
        "append_notes": "Upgrade negotiations were launched in November 2016; the Upgrade Protocol, signed on "
        "26 January 2021, entered into force on 7 April 2022. Negotiations on trade in services on a negative-list "
        "basis were launched by an exchange of letters on 13 June 2024.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/202202/47457.html"),
            prov("notes", "/article/e/enrelease/202406/55618.html"),
        ],
    },
    "CLCN": {
        "links": [site("/topic/china_chile_upgrade.shtml")],
        "append_notes": "Upgrade negotiations were launched in November 2016; the Protocol amending the FTA and its "
        "Supplementary Agreement on Trade in Services was signed in Da Nang on 11 November 2017.",
        "provenance": [prov("notes", "/article/c/zhengwugk/201711/36117.html")],
    },
    "CNGE": {
        "links": [site("/topic/engeorgia.shtml")],
        "append_notes": "Upgrade negotiations launched in July 2025 were substantially concluded in September 2025 "
        "and closed by a memorandum of understanding signed in Shanghai on 4 November 2025; the upgrade protocol was "
        "signed in Beijing on 22 April 2026.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/202511/57419.html"),
            prov("notes", "/article/c/zhengwugk/202604/58237.html"),
        ],
    },
    "CNPK": {
        "links": [site("/topic/china_pakistan_phase.shtml")],
        "append_notes": "The second-phase protocol amending the FTA was signed in Beijing on 28 April 2019.",
        "provenance": [prov("notes", "/article/e/enrelease/201904/40777.html")],
    },
    "CNNI": {
        "append_notes": "An early harvest arrangement, signed by video link on 12 July 2022 together with the launch "
        "of negotiations on the full FTA, was in force from 1 May 2023.",
        "provenance": [prov("notes", "/article/c/zhengwugk/202304/53863.html")],
    },
    "ACFTA": {
        "append_notes": "The protocol amending the Framework Agreement and certain agreements under it (the version "
        "2.0 upgrade) was signed in Kuala Lumpur on 22 November 2015; it entered into force for China and Viet Nam "
        "on 1 July 2016 and for all parties on 22 October 2019. The version 3.0 upgrade protocol was signed in "
        "Kuala Lumpur on 28 October 2025; on 16 November 2026 the leaders announced its entry into force on "
        "1 December 2026.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/201910/41659.html"),
            prov("notes", "/article/c/zhengwugk/202510/57382.html"),
            prov("notes", "/article/c/zhengwugk/202611/100334.html"),
        ],
    },
    "SACUCN": {
        "append_notes": "The first round of negotiations on an early harvest arrangement of the China-SACU Agreement "
        "on Economic Partnership for Shared Development was held in Beijing on 20-21 October 2026.",
        "provenance": [prov("notes", "/article/c/african/africannews/202610/100272.html")],
    },
    "CNCO": {
        "links": [site("/list/e/encolombia/encolombianews/1/cateinfo.html")],
        "append_notes": "A memorandum of understanding launching a joint feasibility study was signed on 9 May 2012.",
        "provenance": [prov("notes", "/article/c/zhengwugk/201205/26836.html")],
    },
    "CNNP": {
        "links": [site("/list/e/ennepal/ennepalnews/1/cateinfo.html")],
        "append_notes": "A memorandum of understanding launching a joint feasibility study was signed in Beijing on "
        "21 March 2016.",
        "provenance": [prov("notes", "/article/c/zhengwugk/201603/31017.html")],
    },
    "CNMN": {
        "links": [site("/list/e/enmongol/enmongolnews/1/cateinfo.html")],
        "append_notes": "A memorandum of understanding launching a joint feasibility study was signed on "
        "12 May 2017.",
        "provenance": [prov("notes", "/article/c/zhengwugk/201705/34937.html")],
    },
    "CACN": {
        "links": [site("/list/e/encanada/encanadanews/1/cateinfo.html")],
        "append_notes": "The first meeting of the joint feasibility study and exploratory discussions was held in "
        "Beijing on 20-24 February 2017; the fourth was held in Ottawa in September 2017.",
        "provenance": [
            prov("notes", "/article/c/zhengwugk/201702/34257.html"),
            prov("notes", "/article/c/zhengwugk/201709/35899.html"),
        ],
    },
    "CNFJ": {
        "links": [site("/list/e/enfiji/enfijinews/1/cateinfo.html")],
        "append_notes": "Fiji was the first Pacific Island country to conduct an FTA joint feasibility study with "
        "China; the study's working group held its second meeting in Beijing on 14-15 November 2016. The 2025 "
        "framework agreement on enhanced economic partnership is recorded as CNFJ-EEPA.",
        "provenance": [prov("notes", "/article/c/zhengwugk/201611/33623.html")],
    },
    "CNPG": {
        "links": [site("/list/e/enbaxin/enbaxinnews/1/cateinfo.html")],
        "append_notes": "The 2026 framework agreement on enhanced economic partnership is recorded as CNPG-EEPA.",
        "provenance": [prov("notes", "/article/c/zhengwugk/202605/58437.html")],
    },
    "BDCN": {"links": [site("/list/e/enbengal/enbengalnews/1/cateinfo.html")]},
    "CNIL": {"links": [site("/list/e/enisrael/enisraelnews/1/cateinfo.html")]},
    "CNLK": {"links": [site("/list/e/ensrilanka/ensrilankanews/1/cateinfo.html")]},
    "CNMD": {"links": [site("/list/e/enmoldova/enmoldovanews/1/cateinfo.html")]},
    "CNPA": {"links": [site("/list/e/enpanama/enpanamanews/1/cateinfo.html")]},
    "CNNO": {"links": [site("/topic/ennorway.shtml")]},
    "GCCCN": {"links": [site("/topic/engcc.shtml")]},
    "CNJPKR": {"links": [site("/topic/chinarh.shtml")]},
    "CNCR": {"links": [site("/topic/encosta.shtml")]},
    "CNIS": {"links": [site("/topic/eniceland.shtml")]},
    "CNKH": {"links": [site("/topic/encambodia.shtml")]},
    "CNMU": {"links": [site("/topic/enmauritius.shtml")]},
    "CNMV": {"links": [site("/topic/enmaldives.shtml")]},
    "CNHK": {"links": [site("/topic/enhongkong.shtml")]},
    "CNMO": {"links": [site("/topic/enmacau.shtml")]},
    "CHAFTA": {"links": [site("/topic/enaustralia.shtml")]},
    # A reprint of a press conference of China's Ministry of Foreign Affairs (10 November 2022); the
    # page's posting date (2026-11) is not the date of the event.
    "HNSVTW": {
        "party_left": {
            "SV": (
                "2022-11-07",
                "On 7 November 2022 the Constitutional Chamber of El Salvador's Supreme Court lifted the "
                "protective measures that had kept the agreement in force for El Salvador.",
            )
        },
        "provenance": [prov("parties", "/article/c/elsalvador/elsalvadorguandian/202611/100321.html")],
    },
}

# Pages that only add a link get a provenance row for it.
for _rid, _upd in UPDATES.items():
    if _upd.get("links") and not _upd.get("provenance") and "name" not in _upd:
        _upd["provenance"] = [prov("links", _upd["links"][0]["url"][len(B):])]


# --- apply -------------------------------------------------------------------------------------

def insert(record: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    """Set ``key``; a key the record lacks goes after the closest preceding key in ``ORDER``."""
    if key in record:
        record[key] = value
        return record
    before = ORDER[: ORDER.index(key)]
    anchor = next((k for k in reversed(before) if k in record), None)
    out: dict[str, Any] = {}
    if anchor is None:
        out[key] = value
    for k, v in record.items():
        out[k] = v
        if k == anchor:
            out[key] = value
    return out


def apply_update(record: dict[str, Any], upd: dict[str, Any]) -> dict[str, Any]:
    for key in ("name", "other_names", "verification", "last_verified"):
        if key in upd:
            record = insert(record, key, upd[key])
    for old, new in (upd.get("replace_links") or {}).items():
        for link in record.get("links") or []:
            if link.get("url") == old:
                link["url"] = new
    for old, new in (upd.get("replace_provenance_urls") or {}).items():
        for row in record.get("provenance") or []:
            if row.get("url") == old:
                row["url"] = new
    for pid, (left, note) in (upd.get("party_left") or {}).items():
        for party in record.get("parties") or []:
            if party.get("id") == pid:
                party["left"] = left
                party["note"] = note
    if upd.get("links"):
        links = list(record.get("links") or [])
        have = {link.get("url") for link in links}
        links = [link for link in upd["links"] if link["url"] not in have] + links
        record = insert(record, "links", links)
    if "notes" in upd:
        record = insert(record, "notes", upd["notes"])
    if upd.get("append_notes"):
        current = (record.get("notes") or "").strip()
        record = insert(record, "notes", f"{current} {upd['append_notes']}".strip())
    if upd.get("provenance"):
        rows = list(record.get("provenance") or [])
        rows += [row for row in upd["provenance"] if row not in rows]
        record["provenance"] = rows
    return record


def dump(record: dict[str, Any]) -> str:
    return yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)


def main(argv: list[str]) -> int:
    write = "--write" in argv
    problems = 0
    for record in NEW:
        path = REGISTRY / f"{record['id']}.yaml"
        if path.exists():
            print(f"exists, skipped: {path.name}")
            problems += 1
            continue
        if write:
            path.write_text(dump({k: record[k] for k in ORDER if k in record}), encoding="utf-8")
    changed = 0
    for rid, upd in UPDATES.items():
        path = REGISTRY / f"{rid}.yaml"
        text = path.read_text(encoding="utf-8")
        record = yaml.safe_load(text)
        new = dump(apply_update(record, upd))
        if new != text:
            changed += 1
            if write:
                path.write_text(new, encoding="utf-8")
    print(f"new {len(NEW)}, updated {changed}, problems {problems}{'' if write else ' (dry run)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
