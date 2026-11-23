#!/usr/bin/env python3
"""One-off: import Canada's investment treaties (FIPAs) into data/trade_agreements/.

Sources (Government of Canada, read on 2026-11-23):

- the Global Affairs Canada (GAC) agreements table, one row per agreement with a status from
  "1. Exploratory discussions" to "11. Superseded" (only the 59 FIPA rows are used);
- the Canada Treaty Series (CTS) result list for the subject "Investment protection" (49
  treaties) and the CTS details page of each treaty (signature, entry into force, suspension and
  the CTS citation).

``--fetch`` downloads the three kinds of page into CACHE_DIR; without it the cached copies are
read. The pages are untrusted data: keep CACHE_DIR outside the repository and run this script
with ``python -I``.

Each GAC row becomes one ``-BIT`` record (``agreement_type: investment``, ``verification:
official``), with its status mapped as in ``openspec/changes/add-investment-agreements/design.md``
(decision 3). CTS dates replace or complete the GAC entry into force date. CTS treaties that the
GAC table omits are added from ``EXTRA``; ``SKIP`` lists the two that are not imported.
Hand-checked facts (terminations, suspensions, negotiation history) are in ``OVERRIDES`` and
``NOTES``.

Usage: python -I scripts/oneoff/import_canada_fipas.py CACHE_DIR [--fetch] [--write]
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
GAC_TABLE = "https://international.canada.ca/en/services/business/trade/agreements-negotiations/investment-agreements"
GAC_SOURCE = "Global Affairs Canada, Canada's international trade and investment agreements"
CTS_LIST = (
    "https://www.treaty-accord.gc.ca/result-resultat.aspx?lang=eng&type=10"
    "&subject=fcc00d15-c737-eb11-96a3-005056834bd1&page=1&maxRecords=50"
)
CTS_DETAILS = "https://treaty-accord.gc.ca/details.aspx?id={}&lang=eng"
CTS_TEXT = "https://treaty-accord.gc.ca/text-texte.aspx?id={}&lang=eng"
IGC = "https://www.international.gc.ca/trade-commerce/trade-agreements-accords-commerciaux/agr-acc/"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "wikidata_id", "links",
    "description", "notes", "verification", "last_verified", "provenance",
]

# GAC "Country grouping" names of the FIPA rows.
COUNTRIES = {
    "Albania": "AL", "Argentina": "AR", "Armenia": "AM", "Bahrain": "BH", "Barbados": "BB", "Benin": "BJ",
    "Burkina Faso": "BF", "Cameroon": "CM", "China": "CN", "Costa Rica": "CR", "Côte d’Ivoire": "CI",
    "Croatia": "HR", "Czechia": "CZ", "Democratic Republic of the Congo": "CD", "Ecuador": "EC", "Egypt": "EG",
    "Gabon": "GA", "Georgia": "GE", "Ghana": "GH", "Guinea": "GN", "Hong Kong": "HK", "Hungary": "HU",
    "India": "IN", "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE", "Kosovo": "XK", "Kuwait": "KW",
    "Latvia": "LV", "Lebanon": "LB", "Macedonia": "MK", "Madagascar": "MG", "Mali": "ML", "Mauritania": "MR",
    "Moldova": "MD", "Mongolia": "MN", "Mozambique": "MZ", "Nigeria": "NG", "Pakistan": "PK", "Panama": "PA",
    "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Qatar": "QA", "Romania": "RO", "Russia": "RU",
    "Rwanda": "RW", "Senegal": "SN", "Serbia": "RS", "Slovakia": "SK", "Tanzania": "TZ", "Thailand": "TH",
    "Trinidad and Tobago": "TT", "Tunisia": "TN", "Ukraine": "UA", "United Arab Emirates": "AE",
    "Uruguay": "UY", "Venezuela": "VE", "Zambia": "ZM",
}

# CTS treaty for each GAC row that has one (checked by hand against the CTS list).
CTS_FOR_GAC = {
    "AE": 105574, "AM": 101530, "AR": 101514, "BB": 101526, "BF": 105442, "BJ": 105414, "CI": 105441,
    "CM": 105417, "CN": 105363, "CR": 101533, "CZ": 105128, "EC": 101522, "EG": 101524, "GN": 105444,
    "HK": 105446, "HR": 101527, "HU": 101513, "JO": 105176, "KW": 105333, "LB": 101529, "LV": 105169,
    "MD": 105445, "ML": 105440, "MN": 105484, "NG": 105404, "PA": 101523, "PE": 105078, "PH": 101525,
    "PL": 101511, "RO": 105170, "RS": 105426, "RU": 101516, "SK": 105168, "SN": 105438, "TH": 101528,
    "TT": 101520, "TZ": 105391, "UA": 101517, "UY": 101532, "VE": 101531, "XK": 105479,
}

# CTS treaties that the GAC table omits: CTS id -> (record id, parties).
EXTRA = {
    103269: ("CASV-BIT", ["CA", "SV"]),
    101519: ("CAZA-BIT", ["CA", "ZA"]),
    101521: ("CARO-BIT-1996", ["CA", "RO"]),
    101518: ("CALV-BIT-1995", ["CA", "LV"]),
    101512: ("CAUY-BIT-1991", ["CA", "UY"]),
    101515: ("CACZSK-BIT", ["CA", "CZ", "SK"]),
}
SKIP = {
    101508: "Canada-Yugoslavia agreement of 1979: CTS still lists it in force, with no source for which successor states apply it",
    105087: "ICSID Convention: a multilateral convention, not a bilateral investment treaty",
}

GAC_STATUS = {
    "1": "proposed", "2": "negotiating", "3": "negotiating", "4": "signed", "5": "signed", "6": "in_force",
    "7": "terminated", "8": "abandoned", "9": "superseded", "10": "in_force", "11": "superseded",
}

INACTIVE = "Global Affairs Canada lists the status as 8. Inactive."
COMMONS_CIIT_19 = "https://www.ourcommons.ca/documentviewer/en/44-1/CIIT/report-19/page-24"

# Hand-checked facts. Keys are record ids; values are merged into the record. "_notes_url" and
# "_notes_source" add a provenance entry for the notes; "_ended_url" one for ended.
OVERRIDES: dict[str, dict] = {
    "ARCA-BIT": {
        "status": "in_force",
        "notes": "Global Affairs Canada lists Canada-Argentina as 2. In negotiations, toward a new agreement; the "
                 "1991 agreement recorded here remains in force according to the Canada Treaty Series.",
        "_notes_url": GAC_TABLE, "_notes_source": GAC_SOURCE,
    },
    "CAUY-BIT": {
        "status": "in_force",
        "notes": "Global Affairs Canada lists Canada-Uruguay as 2. In negotiations, toward a new agreement; the 1997 "
                 "agreement recorded here remains in force according to the Canada Treaty Series. An earlier "
                 "agreement, signed in 1991, never entered into force (CAUY-BIT-1991).",
        "_notes_url": GAC_TABLE, "_notes_source": GAC_SOURCE,
    },
    "CATZ-BIT": {
        "status": "terminated", "ended": "2023-12-09",
        "notes": "Terminated at the end of 9 December 2023, after Tanzania notified Canada of its intention to "
                 "terminate it. For investments made before that date, Articles 1 to 40 and 42 remain in force "
                 "for fifteen years, until 9 December 2038. Global Affairs Canada lists Canada-Tanzania as 2. In "
                 "negotiations.",
        "_notes_url": IGC + "tanzania-tanzanie/fipa-apie/index.aspx?lang=eng",
        "_ended_url": IGC + "tanzania-tanzanie/fipa-apie/index.aspx?lang=eng",
    },
    "CAEC-BIT": {
        "ended": "2018",
        "notes": "Ecuador gave notice of termination in 2017, effective in 2018. Investments made before the "
                 "termination remain protected until 2033 (House of Commons Standing Committee on International "
                 "Trade, report 19, 44th Parliament).",
        "_notes_url": COMMONS_CIIT_19, "_notes_source": "House of Commons Standing Committee on International Trade",
        "_ended_url": COMMONS_CIIT_19, "_ended_source": "House of Commons Standing Committee on International Trade",
    },
    "CAPA-BIT": {
        "superseded_by": "CAPA",
        "notes": "Suspended, not terminated, on 1 April 2013, the date the Canada-Panama Free Trade Agreement "
                 "(CAPA) entered into force; Global Affairs Canada lists the status as 9. Suspended.",
    },
    "CAPE-BIT": {
        "superseded_by": "CAPE",
        "notes": "Suspended, not terminated, on 1 August 2009, the date the Canada-Peru Free Trade Agreement (CAPE) "
                 "entered into force; Global Affairs Canada lists the status as 9. Suspended.",
    },
    "CAUA-BIT": {
        "superseded_by": "CAUA",
        "notes": "Suspended on 1 July 2024, the date the modernized Canada-Ukraine Free Trade Agreement (CAUA), "
                 "which has an investment chapter, entered into force; Global Affairs Canada lists the status as "
                 "11. Superseded.",
    },
    "CARU-BIT": {
        "notes": "Signed in Moscow on 20 November 1989 with the Union of Soviet Socialist Republics; Global Affairs "
                 "Canada lists it under Russia.",
        "_notes_url": CTS_DETAILS.format(101516), "_notes_source": "Canada Treaty Series, E101516",
    },
    "CASV-BIT": {
        "status": "signed",
        "notes": "Signed in San Salvador on 31 May 1999; not in force. Not listed in the Global Affairs Canada "
                 "agreements table.",
    },
    "CAZA-BIT": {
        "status": "signed",
        "notes": "The Canada Treaty Series lists only Canada's signature, in Toronto on 27 November 1995; not in "
                 "force. Not listed in the Global Affairs Canada agreements table.",
    },
    "CARO-BIT-1996": {
        "status": "superseded", "superseded_by": "CARO-BIT", "ended": "2011-11-23",
        "notes": "Terminated when the 2009 Canada-Romania agreement (CARO-BIT) entered into force on 23 November "
                 "2011, except for disputes already submitted to arbitration under it.",
        "_ended_url": CTS_TEXT.format(105170), "_ended_source": "Canada Treaty Series, text of E105170 (final provisions)",
    },
    "CALV-BIT-1995": {
        "status": "superseded", "superseded_by": "CALV-BIT", "ended": "2011-11-24",
        "notes": "Terminated when the 2009 Canada-Latvia agreement (CALV-BIT) entered into force on 24 November "
                 "2011, except for disputes already submitted to arbitration under it.",
        "_ended_url": CTS_TEXT.format(105169), "_ended_source": "Canada Treaty Series, text of E105169 (final provisions)",
    },
    "CAUY-BIT-1991": {
        "status": "abandoned", "superseded_by": "CAUY-BIT",
        "notes": "Signed in Ottawa on 16 May 1991; never entered into force, and the Canada Treaty Series lists it "
                 "as terminated. The agreement signed on 29 October 1997 (CAUY-BIT) is in force.",
    },
    "CACZSK-BIT": {
        "status": "terminated", "ended": "2012-03-14",
        "notes": "Signed in Prague on 15 November 1990 with the Czech and Slovak Federal Republic and continued by "
                 "the Czech Republic and Slovakia. Terminated for the Czech Republic on 22 January 2012 and for "
                 "Slovakia on 14 March 2012, when their new agreements (CACZ-BIT, CASK-BIT) entered into force, "
                 "except for disputes already submitted to arbitration.",
        "_party_left": {"CZ": "2012-01-22", "SK": "2012-03-14"},
        "_ended_url": CTS_TEXT.format(105168), "_ended_source": "Canada Treaty Series, text of E105168 (final provisions)",
    },
}

# Negotiation history from the GAC background pages, for rows without a CTS treaty.
NOTES = {
    "AL": "Negotiations were held in 2013, with the second round in Tirana on 20-22 March 2013; their conclusion was "
          "announced in November 2013, but no agreement was signed. " + INACTIVE,
    "BH": "Exploratory discussions were held on 4 January 2009; negotiations began in February 2009 and were "
          "concluded in February 2010, but no agreement was signed. Global Affairs Canada lists the status as "
          "1. Exploratory discussions.",
    "CD": "Negotiations were launched in 2015, with one round in February 2015. Global Affairs Canada lists the status "
          "as 1. Exploratory discussions.",
    "GA": "Negotiations were launched in 2015; two rounds were held, the last in July 2015. " + INACTIVE,
    "GE": "Negotiations began in 2018, with the first round in August 2018.",
    "GH": "Negotiations began in 2011. " + INACTIVE,
    "IN": "Canada and India negotiated toward a FIPA without concluding one. " + INACTIVE,
    "KZ": "The first round of negotiations was held in Astana in June 2011. Global Affairs Canada lists the status "
          "as 1. Exploratory discussions.",
    "KE": "Canada and Kenya agreed in 2014 to begin negotiations. " + INACTIVE,
    "MK": "The second round of negotiations was held on 6-7 October 2014. " + INACTIVE,
    "MG": "Negotiations were concluded in August 2008, but no agreement was signed. " + INACTIVE,
    "MR": "Negotiations began in 2015, with one round in April 2015. " + INACTIVE,
    "MZ": "Negotiations were launched in 2014; two rounds were held, the last in May 2015. " + INACTIVE,
    "NG": "Negotiations were held and completed in Abuja in April 2013; signed in Abuja on 6 May 2014; not in force.",
    "PK": "Rounds of negotiations were held in Islamabad on 31 October-2 November 2011 and in Ottawa on 28-29 May "
          "2012.",
    "QA": "Negotiations began in 2018, with one round in March 2018.",
    "RW": "Negotiations were launched in 2014, with one round in November 2014. " + INACTIVE,
    "TN": "Canada and Tunisia agreed in 2009 to begin negotiations; two rounds were held in 2009 and a third in Tunis "
          "on 21-23 April 2015.",
    "ZM": "The first round of negotiations was held in May 2012 and their conclusion was announced in March 2013, "
          "but no agreement was signed. Global Affairs Canada lists the status as 2. In negotiations.",
}


UNAVAILABLE = "The data you are trying to access is not currently available"


def fetch(url: str, attempts: int = 4) -> str:
    """Fetch a page; CTS sometimes answers with a temporary "not available" page, so retry."""
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=90) as response:
            page = response.read().decode("utf-8", "replace")
        if UNAVAILABLE not in page:
            return page
        time.sleep(3 * (attempt + 1))
    raise SystemExit(f"{url}: still not available after {attempts} attempts")


def text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_gac(page: str) -> list[dict]:
    body = page[page.find("<tbody>"):page.find("</tbody>")]
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        group, kind, status, cell = re.findall(r"<td>(.*?)</td>", tr, re.S)
        if not text(kind).startswith("Foreign Investment"):
            continue
        link = re.search(r'<a href="([^"]+)">(.*?)</a>', cell, re.S)
        in_force = re.search(r"In force:</strong>\s*(.*?)</p>", cell, re.S)
        rows.append({
            "group": text(group), "status": text(status), "url": html.unescape(link.group(1)),
            "name": text(link.group(2)), "in_force": text(in_force.group(1)) if in_force else "",
        })
    return rows


def parse_cts_list(page: str) -> dict[int, dict]:
    treaties = {}
    for block in re.split(r"<h2 class='clsSubTitle'>", page)[1:]:
        head = re.search(r"details\.aspx\?lang=eng&id=(\d+)[^>]*>(.*?)</a>", block, re.S)
        fields = {
            text(k).rstrip(":"): text(v)
            for k, v in re.findall(r"<div class='LeftBold37'[^>]*>(.*?)</div><div[^>]*class='Left63'[^>]*>(.*?)</div>", block, re.S)
        }
        treaties[int(head.group(1))] = {"title": text(head.group(2)), **fields}
    return treaties


def iso(day: str) -> str:
    return datetime.strptime(day, "%d %B %Y").date().isoformat()


def parse_cts_details(page: str) -> dict:
    main = re.search(r"<main.*?</main>", page, re.S)
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", main.group(0) if main else page, flags=re.S)
    body = re.sub(r"<(br|/p|/li|/tr|/h\d|/div|/td|/th|/dt|/dd)[^>]*>", "\n", body)
    lines = [text(x) for x in body.split("\n")]
    lines = [x for x in lines if x]
    out: dict = {"signatures": []}
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if line == "Entry into Force":
            out["in_force"] = iso(nxt)
        elif line == "Suspended":
            out["suspended"] = iso(nxt)
        elif line == "Canada Treaty Series":
            out["cts"] = nxt
        elif re.search(r" - \d{2} [A-Z][a-z]+ \d{4}$", line):
            out["signatures"].append(iso(line.rsplit(" - ", 1)[1]))
    if out["signatures"]:
        out["signed"] = max(out["signatures"])
    return out


def record_id(parties: list[str]) -> str:
    return "".join(sorted(parties)) + "-BIT"


def ordered(record: dict) -> dict:
    return {k: record[k] for k in FIELD_ORDER if k in record}


def prov(field: str, url: str, source: str) -> dict:
    return {"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED}


def build(cache: Path) -> tuple[list[dict], list[str]]:
    gac = parse_gac((cache / "gac.html").read_text(encoding="utf-8"))
    cts = parse_cts_list((cache / "cts_list.html").read_text(encoding="utf-8"))
    details = {}
    for i in cts:
        page = (cache / f"cts_{i}.html").read_text(encoding="utf-8")
        if UNAVAILABLE in page:
            raise SystemExit(f"cts_{i}.html is a 'not available' page; run again with --fetch")
        details[i] = parse_cts_details(page)
    report: list[str] = []
    used = set()
    records = []

    def apply_cts(rec: dict, cts_id: int) -> None:
        d = details[cts_id]
        source = f"Canada Treaty Series, E{cts_id}" + (f" (CTS {d['cts']})" if d.get("cts") else "")
        url = CTS_DETAILS.format(cts_id)
        title = cts[cts_id]["title"]
        if title != rec["name"]:
            rec["other_names"] = [{"lang": "en", "name": title}]
        if d.get("signed"):
            rec["signed"] = d["signed"]
            rec["provenance"].append(prov("signed", url, source))
        if d.get("in_force"):
            rec["in_force"] = d["in_force"]
            rec["provenance"].append(prov("in_force", url, source))
        if d.get("suspended"):
            rec["ended"] = d["suspended"]
            rec["provenance"].append(prov("ended", url, source))

    for row in gac:
        code = COUNTRIES[row["group"]]
        parties = ["CA", code]
        rid = record_id(parties)
        number = row["status"].split(".")[0]
        rec = {
            "id": rid, "name": row["name"], "acronyms": [{"lang": "en", "value": "FIPA"}],
            "agreement_type": "investment", "status": GAC_STATUS[number],
            "parties": [{"id": p, "type": "country"} for p in parties],
            "verification": "official", "last_verified": RETRIEVED,
            "provenance": [prov("parties", GAC_TABLE, GAC_SOURCE), prov("status", GAC_TABLE, GAC_SOURCE)],
        }
        if "treaty-accord.gc.ca" not in row["url"]:
            rec["links"] = [{"url": row["url"], "type": "website"}]
        cts_id = CTS_FOR_GAC.get(code)
        if cts_id:
            used.add(cts_id)
            apply_cts(rec, cts_id)
            gac_date = re.search(r"\d{4}-\d{2}-\d{2}", row["in_force"])
            if gac_date and rec.get("in_force") != gac_date.group(0):
                report.append(f"{rid}: GAC in force {gac_date.group(0)}, CTS {rec.get('in_force')}")
        elif number == "6":
            report.append(f"{rid}: in force on GAC but no CTS treaty")
        if code in NOTES:
            rec["notes"] = NOTES[code]
            rec["provenance"].append(prov("notes", row["url"], "Global Affairs Canada"))
        records.append(rec)

    for cts_id, (rid, parties) in EXTRA.items():
        used.add(cts_id)
        rec = {
            "id": rid, "name": cts[cts_id]["title"], "acronyms": [{"lang": "en", "value": "FIPA"}],
            "agreement_type": "investment", "status": "in_force",
            "parties": [{"id": p, "type": "country"} for p in parties],
            "verification": "official", "last_verified": RETRIEVED,
            "provenance": [prov("parties", CTS_DETAILS.format(cts_id), f"Canada Treaty Series, E{cts_id}"),
                           prov("status", CTS_LIST, "Canada Treaty Series, subject Investment protection")],
        }
        apply_cts(rec, cts_id)
        records.append(rec)

    for rec in records:
        extra = OVERRIDES.get(rec["id"], {})
        for key, value in extra.items():
            if not key.startswith("_"):
                rec[key] = value
        for party in rec["parties"]:
            if party["id"] in extra.get("_party_left", {}):
                party["left"] = extra["_party_left"][party["id"]]
        if "_notes_url" in extra:
            rec["provenance"].append(prov("notes", extra["_notes_url"], extra.get("_notes_source", "Global Affairs Canada")))
        if "_ended_url" in extra:
            rec["provenance"].append(prov("ended", extra["_ended_url"], extra.get("_ended_source", "Global Affairs Canada")))

    for cts_id, treaty in cts.items():
        if cts_id not in used and cts_id not in SKIP:
            report.append(f"CTS E{cts_id} not imported: {treaty['title']}")
    for cts_id, reason in SKIP.items():
        report.append(f"skipped CTS E{cts_id}: {reason}")
    return [ordered(r) for r in records], report


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cache = Path(argv[0])
    if "--fetch" in argv:
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "gac.html").write_text(fetch(GAC_TABLE), encoding="utf-8")
        page = fetch(CTS_LIST)
        (cache / "cts_list.html").write_text(page, encoding="utf-8")
        for cts_id in parse_cts_list(page):
            (cache / f"cts_{cts_id}.html").write_text(fetch(CTS_DETAILS.format(cts_id)), encoding="utf-8")
            time.sleep(0.4)
    records, report = build(cache)
    print(json.dumps({"records": len(records), "by_status": _count(records)}, indent=1))
    for line in report:
        print(line)
    if "--write" in argv:
        for rec in records:
            path = REGISTRY / f"{rec['id']}.yaml"
            path.write_text(yaml.safe_dump(rec, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
        print(f"wrote {len(records)} files")
    return 0


def _count(records: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
