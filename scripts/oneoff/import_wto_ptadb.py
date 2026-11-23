#!/usr/bin/env python3
"""One-off: walk the WTO Preferential Trade Arrangements Database into data/trade_agreements/.

The PTA Database (https://ptadb.wto.org/ptaList.aspx) lists the non-reciprocal preference schemes
that WTO members notify: GSP schemes, LDC-only schemes and other preference programmes. It has
no API. ``fetch`` reads the list page, each scheme card (an ASP.NET postback on the list) and
the beneficiary page of each scheme and sub-scheme, then saves a JSON snapshot. The pages are
untrusted data: keep the snapshot outside the repository and run this script with ``python -I``.

Do not trust the "As of" version dropdown of a card. The server caches it across sessions, so it
often shows the versions of another scheme. Versions get their dates from a global map of
version id to label, built from every dropdown seen. The latest version id of a scheme comes
from a hidden column of the list.

``write`` maps the snapshot to registry records with the hand-checked tables below:

- ``SCHEMES``: one registry record per PTA id. The 4 EAEU rows (Armenia, Kazakhstan, the
  Kyrgyz Republic, Russia) are one legal instrument and become one record, ``EAEU-GSP``;
- ``SUBSCHEMES``: one record per sub-scheme beneficiary list, with ``parent`` set;
- ``EXISTING``: rows already in the registry, which only get ``wto_pta_ids``.

New records are ``verification: catalogue``. Their parties are the grantor and the beneficiaries
of the latest version, and their provenance names the date of that version. "Tariffs & Trade"
pages are never read. See ``openspec/changes/add-preference-scheme-rosters``.

``history`` reads every version of every scheme and adds a ``versions`` list to the snapshot.
``write`` then dates the beneficiaries from consecutive versions that list beneficiaries, adds
former beneficiaries, and, with ``--report``, writes a TSV review of the linked intblocks, whose
official rosters it does not edit. See ``openspec/changes/add-preference-scheme-beneficiary-history``.

Usage:
  python -I scripts/oneoff/import_wto_ptadb.py fetch SNAPSHOT_JSON
  python -I scripts/oneoff/import_wto_ptadb.py history SNAPSHOT_JSON HISTORY_JSON
  python -I scripts/oneoff/import_wto_ptadb.py write SNAPSHOT_OR_HISTORY_JSON [--write] [--report TSV]
"""

from __future__ import annotations

import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
BASE = "https://ptadb.wto.org/"
LIST_URL = BASE + "ptaList.aspx"
SOURCE = "WTO Preferential Trade Arrangements Database"
LIST_GRID = "ctl00$MainContent$ptaListControl1$GridView1${}$pta_hyperlink"
SUBSCHEME_COMBO = "ctl00$ctl00$MainContent$ptaInfo$ptaBenefList$combo_subschemes"
VERSION_COMBO = "ctl00$ctl00$MainContent$ptaInfo$ptaNotificationSummary1$ptaNotificationsListControl1$DropDownList1"
FIELD_ORDER = [
    "id",
    "name",
    "acronyms",
    "other_names",
    "agreement_type",
    "status",
    "signed",
    "in_force",
    "ended",
    "parties",
    "intblock",
    "supersedes",
    "superseded_by",
    "parent",
    "wto_rta_id",
    "aric_id",
    "wto_pta_ids",
    "wikidata_id",
    "links",
    "description",
    "notes",
    "verification",
    "last_verified",
    "provenance",
]

# WTO numeric codes that are not an ISO 3166-1 numeric code of a country in data/countries.
CODE_OVERRIDES = {
    "899": ("EU", "intblock"),
    "893": ("ME", "country"),
    "892": ("RS", "country"),
    "888": ("XK", "country"),
    "736": ("SD", "country"),
    "158": ("TW", "country"),
    "419": ("LA", "country"),  # "Laos" in older EU and Korean versions; 418 elsewhere
}
# Parts of a member state that a beneficiary list names on their own: no party row, a note instead.
CODE_SKIPPED = {"128": "Canary Islands", "146": "Ceuta and Melilla"}
# Statistical groupings in older Australian versions: not a country, no party row.
CODE_AGGREGATES = {"579": "Other Oceania, n.e.s.", "848": "U.S. Oceania, n.e.s."}

# PTA id -> registry record. ``grantor`` overrides the provider of the row; ``status`` and
# ``ended`` override the dates of the list (a lapsed authority); ``also`` lists the other PTA ids
# of the same instrument.
SCHEMES: dict[int, dict] = {
    69: {"id": "AU-GSP", "parent": "GSP"},
    62: {"id": "CA-GSP", "parent": "GSP"},
    84: {"id": "CL-LDC"},
    36: {"id": "EU-GSP", "parent": "GSP", "acronyms": ["GSP"]},
    76: {
        "id": "EU-ATM-WB",
        "name": "Autonomous trade measures for the Western Balkans",
        "other": "Trade preferences for countries of the Western Balkans",
    },
    82: {
        "id": "EU-ATP-PK",
        "name": "Autonomous trade preferences for Pakistan",
        "other": "Trade preferences for Pakistan",
    },
    75: {
        "id": "EU-ATP-MD",
        "name": "Autonomous trade preferences for the Republic of Moldova",
        "other": "Trade preferences for the Republic of Moldova",
        "note": "The EU-Moldova Association Agreement (EUMD), with its free trade area, replaced the preferences.",
    },
    53: {"id": "IS-GSP", "parent": "GSP"},
    71: {
        "id": "IN-DFTP",
        "name": "Duty-Free Tariff Preference Scheme for Least Developed Countries (India)",
        "other": "Duty-Free Tariff Preference Scheme for LDCs",
        "acronyms": ["DFTP"],
    },
    63: {"id": "JP-GSP", "parent": "GSP"},
    52: {"id": "KR-LDC"},
    72: {"id": "KG-LDC", "status": "superseded", "superseded_by": "EAEU-GSP"},
    97: {"id": "ME-LDC"},
    46: {"id": "MA-LDC"},
    66: {"id": "NZ-GSP", "parent": "GSP"},
    43: {"id": "NO-GSP", "parent": "GSP"},
    83: {
        "id": "RU-GSP-2010",
        "parent": "GSP",
        "status": "superseded",
        "superseded_by": "EAEU-GSP",
        "note": "Russia's row for the unified system of tariff preferences of the Customs Union of Belarus, "
        "Kazakhstan and Russia, which the EAEU system replaced on 10 October 2016 in the PTA Database.",
    },
    98: {
        "id": "EAEU-GSP",
        "parent": "GSP",
        "grantor": ("EAEU", "intblock"),
        "also": [87, 96, 100],
        "name": "Unified System of Tariff Preferences of the Eurasian Economic Union",
        "note": "One instrument, notified separately by Armenia (PTA 96), Kazakhstan (87), the Kyrgyz Republic "
        "(100) and Russia (98), whose beneficiary lists are identical. Belarus applies the same system "
        "but is not a WTO member, so it has no PTA Database row.",
    },
    64: {"id": "CH-GSP", "parent": "GSP"},
    68: {"id": "TW-LDC"},
    86: {"id": "TJ-LDC"},
    85: {"id": "TH-LDC"},
    73: {"id": "TR-GSP", "parent": "GSP"},
    101: {
        "id": "GB-DCTS",
        "parent": "GSP",
        "name": "Developing Countries Trading Scheme (United Kingdom)",
        "other": "Developing Countries Trading Scheme – United Kingdom",
        "acronyms": ["DCTS"],
    },
    99: {
        "id": "GB-GSP",
        "parent": "GSP",
        "name": "Generalized System of Preferences – United Kingdom",
        "status": "superseded",
        "superseded_by": "GB-DCTS",
    },
    67: {
        "id": "US-ATPA",
        "acronyms": ["ATPA"],
        "note": "Extended and widened by the Andean Trade Promotion and Drug Eradication Act (ATPDEA) of 2002.",
    },
    77: {"id": "US-FTTPI"},
    49: {
        "id": "US-GSP",
        "parent": "GSP",
        "status": "terminated",
        "ended": "2020-12-31",
        "note": "The statutory authorization lapsed on 31 December 2020 and had not been renewed by 2026-11-23; "
        "earlier lapses were followed by retroactive renewals. The PTA Database gives no end date.",
    },
    88: {
        "id": "US-NTPP",
        "name": "Nepal Trade Preference Program",
        "other": "Trade preferences for Nepal",
        "acronyms": ["NTPP"],
    },
}
# Rows that get no record, with the reason.
SKIP = {
    79: "China's duty-free treatment for LDCs: the latest version (2024-12-01) lists no beneficiaries, "
    "though the 7 earlier versions do"
}
# Rows already in the registry: they only get wto_pta_ids.
EXISTING = {37: "AGOA", 70: "CARIBCAN", 78: "CBERA", 80: "SPARTECA"}
MERGED = {other: pta for pta, spec in SCHEMES.items() for other in spec.get("also", [])}

# (PTA id, sub-scheme label without its count) -> record. ``in_force`` is set when the legal basis
# of the sub-scheme gives it; otherwise the record takes the date of the PTA Database version.
SUBSCHEMES: dict[tuple[int, str], dict] = {
    (98, "Least-developed countries (LDCs)"): {
        "id": "EAEU-GSP-LDC",
        "in_force": "2016-10-10",
        "name": "Least developed countries in the EAEU unified system of tariff preferences",
    },
    (69, "Least-developed countries (LDCs)"): {
        "id": "AU-GSP-LDC",
        "name": "Least developed countries in the Australian GSP",
    },
    (62, "Least-Developed Countries' Tariff"): {
        "id": "CA-GSP-LDCT",
        "name": "Least Developed Country Tariff (Canada)",
        "acronyms": ["LDCT"],
    },
    (36, "Everything but Arms (LDCs)"): {
        "id": "EU-GSP-EBA",
        "name": "Everything but Arms",
        "acronyms": ["EBA"],
        "in_force": "2001-03-05",
        "in_force_source": "Council Regulation (EC) No 416/2001",
    },
    (36, "GSP+"): {"existing": "GSPPLUS"},
    (66, "Least-developed countries (LDCs)"): {
        "id": "NZ-GSP-LDC",
        "name": "Least developed countries in the New Zealand GSP",
    },
    (43, "GSP PLUS"): {"id": "NO-GSP-PLUS", "name": "GSP Plus (Norway)"},
    (43, "GSP zero"): {"id": "NO-GSP-ZERO", "name": "GSP zero (Norway)"},
    (83, "Least-developed countries (LDCs)"): {
        "id": "RU-GSP-2010-LDC",
        "in_force": "2010-01-01",
        "name": "Least developed countries in the Customs Union unified system of tariff preferences",
    },
    (64, "Least-developed countries (LDCs) and countries undergoing debt relief"): {
        "id": "CH-GSP-LDC",
        "name": "Least developed countries and countries undergoing debt relief in the Swiss GSP",
    },
    (73, "Least-developed countries (LDCs)"): {
        "id": "TR-GSP-LDC",
        "name": "Least developed countries in the Turkish GSP",
    },
    (73, "Special incentive arrangement"): {
        "id": "TR-GSP-SIA",
        "name": "Special incentive arrangement of the Turkish GSP",
    },
    (99, "Enhanced Framework"): {
        "id": "GB-GSP-ENHANCED",
        "in_force": "2021-01-01",
        "name": "Enhanced Framework of the United Kingdom GSP",
    },
    (99, "General Framework"): {
        "id": "GB-GSP-GENERAL",
        "in_force": "2021-01-01",
        "name": "General Framework of the United Kingdom GSP",
    },
    (99, "Least developed countries framework"): {
        "id": "GB-GSP-LDC",
        "in_force": "2021-01-01",
        "name": "Least Developed Countries Framework of the United Kingdom GSP",
    },
    (37, "Textile and apparel benefits"): {
        "id": "AGOA-APPAREL",
        "in_force": "2000-05-18",
        "name": "AGOA textile and apparel benefits",
        "in_force_source": "Trade and Development Act of 2000",
    },
    (49, "Least-developed countries (LDCs)"): {
        "id": "US-GSP-LDC",
        "name": "Least-developed beneficiary developing countries in the US GSP",
    },
}


# ---------------------------------------------------------------------------- fetch


class Session:
    """One ASP.NET session: cookies plus the form state of the last page."""

    def __init__(self) -> None:
        jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        self.opener.addheaders = [("User-Agent", "Mozilla/5.0 (internacia-db one-off import)")]

    def get(self, url: str) -> str:
        with self.opener.open(url, timeout=60) as response:
            return response.read().decode("utf-8")

    def post(self, url: str, page: str, fields: dict[str, str]) -> str:
        data = {}
        for name in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "__VIEWSTATEENCRYPTED"):
            match = re.search(r'id="' + name + r'" value="([^"]*)"', page)
            if match:
                data[name] = html.unescape(match.group(1))
        data.update(fields)
        with self.opener.open(url, urllib.parse.urlencode(data).encode(), timeout=60) as response:
            return response.read().decode("utf-8")


def text_lines(page: str) -> list[str]:
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    return [line.strip() for line in html.unescape(re.sub(r"<[^>]+>", "\n", page)).split("\n") if line.strip()]


def options(page: str, name: str) -> list[tuple[str, str]]:
    match = re.search(r'<select name="[^"]*' + re.escape(name.split("$")[-1]) + r'".*?</select>', page, re.S)
    if not match:
        return []
    return [(v, html.unescape(label).strip()) for v, label in re.findall(r'value="([^"]*)">([^<]*)', match.group(0))]


def beneficiaries(page: str) -> list[list[str]]:
    match = re.search(r'id="MainContent_ptaInfo_ptaBenefList_GridViewData".*?</table>', page, re.S)
    if not match:
        return []
    return [
        [code, html.unescape(name)]
        for code, name in re.findall(r'Country\.aspx\?code=(\w+)">([^<]+)</a>', match.group(0))
    ]


def list_rows(page: str) -> list[dict]:
    table = re.search(r"<table[^>]*GridView1.*?</table>", page, re.S).group(0)
    rows = []
    for index, row in enumerate(re.findall(r"<tr.*?</tr>", table, re.S)[1:]):
        cells = [
            re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        ]
        rows.append(
            {
                "control": f"ctl{index + 2:02d}",
                "provider": cells[1],
                "name": cells[2],
                "type": cells[3],
                "entry_into_force": cells[5],
                "end_date": cells[6],
                "pta_id": int(cells[7]),
                "version_id": cells[8],
                "provider_code": cells[9],
            }
        )
    return rows


def card(row: dict, versions: dict[str, str]) -> tuple[str, Session]:
    session = Session()
    listing = session.get(LIST_URL)
    page = session.post(LIST_URL, listing, {"__EVENTTARGET": LIST_GRID.format(row["control"]), "__EVENTARGUMENT": ""})
    versions.update(options(page, VERSION_COMBO))
    return page, session


def after(lines: list[str], key: str) -> str | None:
    return lines[lines.index(key) + 1] if key in lines else None


def fetch(out: Path) -> int:
    rows = list_rows(Session().get(LIST_URL))
    versions: dict[str, str] = {}
    for row in rows:
        page, session = card(row, versions)
        lines = text_lines(page)
        title = after(lines, "Processing...")
        if title != row["name"].replace("  ", " ") and title and title.split()[:4] != row["name"].split()[:4]:
            print(f"warning: card title {title!r} does not match row {row['name']!r}", file=sys.stderr)
        paragraph = after(lines, "Notification provision in the Transparency Mechanism for PTAs")
        row["notification"] = paragraph if paragraph and paragraph.startswith("Paragraph") else None
        benefit = session.get(BASE + "ptaBeneficiaries.aspx")
        versions.update(options(benefit, VERSION_COMBO))
        row["beneficiaries"] = beneficiaries(benefit)
        row["subschemes"] = {}
        rendered = [v for v, _ in options(benefit, VERSION_COMBO)]
        for value, label in options(benefit, SUBSCHEME_COMBO):
            if value == "0":
                continue
            fields = {"__EVENTTARGET": SUBSCHEME_COMBO, "__EVENTARGUMENT": "", SUBSCHEME_COMBO: value}
            # Post the row's own latest version. Event validation only accepts a version the page
            # rendered, so fall back to the rendered selection when the cached dropdown lacks it.
            fields[VERSION_COMBO] = row["version_id"] if row["version_id"] in rendered else (rendered[-1:] or [""])[0]
            sub = beneficiaries(session.post(BASE + "ptaBeneficiaries.aspx", benefit, fields))
            count = re.search(r"\((\d+)\)$", label)
            if count and int(count.group(1)) != len(sub):
                print(f"warning: {row['pta_id']} {label!r} lists {len(sub)} beneficiaries", file=sys.stderr)
            row["subschemes"][re.sub(r"\s*\(\d+\)$", "", label).strip()] = sub
        print(
            f"{row['control']} {row['pta_id']:>3} {row['name'][:60]}: {len(row['beneficiaries'])} beneficiaries, "
            f"{len(row['subschemes'])} sub-schemes",
            file=sys.stderr,
        )
        time.sleep(1)
    for _ in range(6):
        missing = [row for row in rows if row["version_id"] not in versions]
        if not missing:
            break
        for row in missing:
            card(row, versions)
            time.sleep(2)
    for row in rows:
        label = versions.get(row["version_id"])
        match = re.match(r"(\d\d)/(\d\d)/(\d{4})", label or "")
        row["version_date"] = f"{match.group(3)}-{match.group(2)}-{match.group(1)}" if match else None
    snapshot = {"retrieved_at": date.today().isoformat(), "source": LIST_URL, "rows": rows}
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        f"{len(rows)} rows; version date unknown for {[r['pta_id'] for r in rows if not r['version_date']]}",
        file=sys.stderr,
    )
    return 0


def iso(label: str) -> str | None:
    """``29/06/2017 (5)`` -> ``2017-06-29``."""
    match = re.match(r"(\d\d)/(\d\d)/(\d{4})", label or "")
    return f"{match.group(3)}-{match.group(2)}-{match.group(1)}" if match else None


def scheme_versions(row: dict, tries: int = 8) -> tuple[list[tuple[str, str]], str, Session]:
    """The scheme's own version list, its beneficiary page and session.

    The cached dropdown may hold another scheme's versions; it is the scheme's own list when it
    contains the scheme's latest version id (a hidden column of the list).
    """
    for attempt in range(tries):
        _, session = card(row, {})
        page = session.get(BASE + "ptaBeneficiaries.aspx")
        versions = options(page, VERSION_COMBO)
        if row["version_id"] in {v for v, _ in versions}:
            return versions, page, session
        time.sleep(2 + attempt)
    raise SystemExit(f"PTA {row['pta_id']}: no version list with version {row['version_id']} after {tries} tries")


def page_title(page: str) -> str | None:
    return after(text_lines(page), "Processing...")


def history(snapshot_path: Path, out: Path) -> int:
    """Read every version of every scheme (design decision 1 of add-preference-scheme-beneficiary-history)."""
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    done: dict[int, list[dict]] = {}
    for row in snapshot["rows"]:
        if row["pta_id"] in done:  # SPARTECA has one PTA id on two rows
            row["versions"] = done[row["pta_id"]]
            continue
        versions, page, session = scheme_versions(row)
        expected = page_title(page)
        found = []
        for value, label in versions:
            current = session.post(
                BASE + "ptaBeneficiaries.aspx",
                page,
                {"__EVENTTARGET": VERSION_COMBO, "__EVENTARGUMENT": "", VERSION_COMBO: value},
            )
            if page_title(current) != expected:
                raise SystemExit(f"PTA {row['pta_id']} version {value}: page title {page_title(current)!r}")
            entry = {"id": value, "label": label, "date": iso(label), "beneficiaries": beneficiaries(current)}
            entry["subschemes"], entry["unverified_subschemes"] = {}, []
            if value == row["version_id"]:
                # Posting the latest version id makes the server return a stale sub-scheme grid (the
                # one of the version viewed before, or none). The fetch read these lists from the
                # default page, which shows the latest version, and checked them against the counts
                # in the dropdown labels.
                entry["subschemes"] = row["subschemes"]
                found.append(entry)
                continue
            for sub_value, sub_label in options(current, SUBSCHEME_COMBO):
                if sub_value == "0":
                    continue
                name = re.sub(r"\s*\(\d+\)$", "", sub_label).strip()
                count = re.search(r"\((\d+)\)$", sub_label)
                fields = {
                    "__EVENTTARGET": SUBSCHEME_COMBO,
                    "__EVENTARGUMENT": "",
                    SUBSCHEME_COMBO: sub_value,
                    VERSION_COMBO: value,
                }
                sub = beneficiaries(session.post(BASE + "ptaBeneficiaries.aspx", current, fields))
                if count and len(sub) != int(count.group(1)):
                    # The label gives the list's size: a list of another size is a stale grid. Leave it
                    # out of the dates rather than guess.
                    print(
                        f"review: PTA {row['pta_id']} {label} {name!r}: {len(sub)} listed, label says "
                        f"{count.group(1)}; left out",
                        file=sys.stderr,
                    )
                    entry["unverified_subschemes"].append(name)
                    continue
                entry["subschemes"][name] = sub
                time.sleep(0.5)
            found.append(entry)
            time.sleep(0.5)
        latest = found[-1] if found else {}
        if latest.get("id") != row["version_id"]:
            print(
                f"warning: PTA {row['pta_id']}: last version {latest.get('id')} is not {row['version_id']}",
                file=sys.stderr,
            )
        if {c for c, _ in latest.get("beneficiaries", [])} != {c for c, _ in row["beneficiaries"]}:
            print(f"warning: PTA {row['pta_id']}: latest version list differs from the snapshot", file=sys.stderr)
        populated = [v for v in found if v["beneficiaries"]]
        for before, after_ in zip(populated, populated[1:], strict=False):
            if len(after_["beneficiaries"]) < len(before["beneficiaries"]) / 2:
                print(
                    f"review: PTA {row['pta_id']}: {len(before['beneficiaries'])} beneficiaries on {before['date']}, "
                    f"{len(after_['beneficiaries'])} on {after_['date']}",
                    file=sys.stderr,
                )
        labels = [set(v["subschemes"]) for v in populated]
        if labels and any(s != labels[-1] for s in labels if s):
            print(
                f"review: PTA {row['pta_id']}: sub-scheme labels change: {sorted(set().union(*labels))}",
                file=sys.stderr,
            )
        print(
            f"{row['pta_id']:>3} {row['name'][:50]}: {len(found)} versions, {len(populated)} with beneficiaries "
            f"(from {populated[0]['date'] if populated else '-'})",
            file=sys.stderr,
        )
        row["versions"] = done[row["pta_id"]] = found
    snapshot["history_retrieved_at"] = date.today().isoformat()
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


# ---------------------------------------------------------------------------- write


def wto_date(value: str | None) -> str | None:
    """``01-Jul-1971`` -> ``1971-07-01``."""
    if not value:
        return None
    day, month, year = value.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{year}-{months.index(month) + 1:02d}-{int(day):02d}"


def clean_name(name: str) -> str:
    """Drop the date range WTO appends to a row that a later scheme replaced."""
    return re.sub(r"\s*\((?:As of [\d.]+|[\d.]+ to [\d.]+)\)$", "", re.sub(r"\s+", " ", name)).strip()


def load_codes() -> dict[str, str]:
    codes = {}
    for path in sorted((ROOT / "data" / "countries").glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        for key in ("m49_code", "numeric_code"):
            if record.get(key):
                codes[str(record[key]).zfill(3)] = path.stem
    return codes


def party(code: str, codes: dict[str, str]) -> tuple[str, str] | None:
    if code in CODE_OVERRIDES:
        return CODE_OVERRIDES[code]
    return (codes[code], "country") if code in codes else None


def ordered(record: dict) -> dict:
    return {k: record[k] for k in FIELD_ORDER if record.get(k) not in (None, [], "")}


def provenance(
    version_date: str | None, retrieved: str, fields: tuple[str, ...], stats: dict | None = None
) -> list[dict]:
    """Beneficiary lists come from dated versions; status and dates come from the list."""
    versioned = f"{SOURCE}, version as of {version_date}" if version_date else f"{SOURCE}, latest version"
    if stats and stats["lists"] > 1:
        versioned = f"{SOURCE}, versions as of {stats['first']} to {stats['last']}"
    return [
        {"field": f, "source": versioned if f == "parties" else SOURCE, "url": LIST_URL, "retrieved_at": retrieved}
        for f in fields
    ]


def countries(n: int) -> str:
    return "1 country or territory" if n == 1 else f"{n} countries and territories"


def beneficiary_parties(entries: list[list[str]], codes: dict[str, str], grantor: str) -> tuple[list[dict], list[str]]:
    parties, skipped, seen = [], [], set()
    for code, name in entries:
        if code in CODE_SKIPPED:
            skipped.append(CODE_SKIPPED[code])
            continue
        if code in CODE_AGGREGATES:
            continue
        resolved = party(code, codes)
        if resolved is None:
            raise SystemExit(f"unmapped WTO code {code} ({name})")
        pid, ptype = resolved
        if pid in seen or pid == grantor:
            continue
        seen.add(pid)
        parties.append({"id": pid, "type": ptype, "role": "beneficiary"})
    return sorted(parties, key=lambda p: p["id"]), skipped


def populated(row: dict, label: str | None = None) -> list[tuple[str, list[list[str]]]]:
    """``(date, entries)`` of each version that lists beneficiaries (of the scheme, or of sub-scheme ``label``)."""
    found = []
    for version in row.get("versions") or []:
        entries = version["beneficiaries"] if label is None else version["subschemes"].get(label) or []
        if entries and version.get("date"):
            found.append((version["date"], entries))
    return found


def dated_parties(
    lists: list[tuple[str, list[list[str]]]],
    codes: dict[str, str],
    grantor: str,
    starts_scheme: bool,
    ended: str | None = None,
) -> tuple[list[dict], dict]:
    """Beneficiaries with dates from consecutive populated versions (beneficiary-history decisions 1-3).

    A beneficiary listed in the first list has no ``in_force`` unless that list is the scheme's first
    version. Each party keeps its latest spell; earlier spells go in its note.
    """
    present = []
    types: dict[str, str] = {}
    for _, entries in lists:
        parties, _ = beneficiary_parties(entries, codes, grantor)
        present.append({p["id"] for p in parties})
        types.update({p["id"]: p["type"] for p in parties})

    def known_start(index: int) -> bool:
        return index > 0 or starts_scheme

    result, former = [], 0
    for pid in sorted(types):
        spells, start = [], None
        for index, ids in enumerate(present):
            if pid in ids and start is None:
                start = index
            elif pid not in ids and start is not None:
                spells.append((start, index))
                start = None
        if start is not None:
            spells.append((start, None))
        first, end = spells[-1]
        party = {"id": pid, "type": types[pid], "role": "beneficiary"}
        if known_start(first):
            party["in_force"] = lists[first][0]
        if end is not None:
            # A version notified after the scheme ended may drop a beneficiary: it left by the end.
            party["left"] = min(lists[end][0], ended) if ended else lists[end][0]
            former += 1
        earlier = []
        for s, e in spells[:-1]:
            if known_start(s):
                earlier.append(f"Also a beneficiary from {lists[s][0]} to {lists[e][0]}.")
            else:
                earlier.append(f"Also a beneficiary until {lists[e][0]} (listed from {lists[0][0]}).")
        if earlier:
            party["note"] = " ".join(earlier)
        result.append(party)
    return result, {"first": lists[0][0], "last": lists[-1][0], "lists": len(lists), "former": former}


def history_note(stats: dict, starts_scheme: bool) -> str:
    if stats["lists"] < 2:
        return ""
    baseline = (
        f"those listed on {stats['first']}, the scheme's first version, have that date"
        if starts_scheme
        else f"none for those already listed on {stats['first']}, the earliest list"
    )
    text = (
        f"Beneficiary dates come from the {stats['lists']} PTA Database versions with a beneficiary list, as of "
        f"{stats['first']} to {stats['last']}: in_force is the date of the version that first lists a beneficiary "
        f"({baseline}) and left the date of the first version that no longer lists it. They are no-later-than "
        "dates, not designation dates."
    )
    if stats["former"]:
        text += (
            f" {stats['former']} former {'beneficiary is' if stats['former'] == 1 else 'beneficiaries are'} included."
        )
    return text


def roster(
    row: dict,
    codes: dict[str, str],
    grantor: str,
    label: str | None = None,
    ended: str | None = None,
) -> tuple[list[dict], list[str], dict | None, bool]:
    """Beneficiary parties (dated when the snapshot has versions), skipped names, stats, starts_scheme."""
    latest = row["beneficiaries"] if label is None else row["subschemes"][label]
    current, skipped = beneficiary_parties(latest, codes, grantor)
    lists = populated(row, label)
    if len(lists) < 2:
        return current, skipped, None, False
    versions = [v for v in row["versions"] if v.get("date")]
    starts_scheme = lists[0][0] == versions[0]["date"]
    parties, stats = dated_parties(lists, codes, grantor, starts_scheme, ended)
    now = {p["id"] for p in parties if not p.get("left")}
    if now != {p["id"] for p in current}:
        raise SystemExit(f"PTA {row['pta_id']} {label or ''}: the latest version list differs from the snapshot")
    return parties, skipped, stats, starts_scheme


def build(snapshot: dict) -> tuple[list[dict], dict[str, dict]]:
    """New records, and the changes to existing ones (id -> fields to set)."""
    codes = load_codes()
    retrieved = snapshot["retrieved_at"]
    rows = {}
    for row in snapshot["rows"]:
        rows.setdefault(row["pta_id"], row)  # SPARTECA has one PTA id on two rows
    records, existing = [], {}
    for pta, rid in EXISTING.items():
        existing[rid] = {"wto_pta_ids": [pta]}
    existing["GSPPLUS"] = {"parent": "EU-GSP"}
    done = set(EXISTING) | set(MERGED) | set(SKIP)
    for pta, reason in SKIP.items():
        print(f"skipped\t{pta}\t{reason}")
    if set(rows) - done - set(SCHEMES):
        raise SystemExit(f"PTA ids without a mapping: {sorted(set(rows) - done - set(SCHEMES))}")
    by_pta = {}
    for pta, spec in SCHEMES.items():
        row = rows[pta]
        grantor = spec.get("grantor") or party(row["provider_code"], codes)
        status = spec.get("status") or ("terminated" if row["end_date"] else "in_force")
        ended = spec.get("ended") or wto_date(row["end_date"])
        record_ended = ended if status in ("terminated", "superseded") else None
        parties, skipped, stats, starts = roster(row, codes, grantor[0], ended=record_ended)
        current = sum(1 for p in parties if not p.get("left"))
        ids = sorted([pta, *spec.get("also", [])])
        notes = [spec["note"]] if spec.get("note") else []
        version = row["version_date"]
        notes.append(
            f"Current beneficiaries are those of the PTA Database version as of {version or 'an unknown date'} "
            f"({countries(current)}), not checked against the grantor's own list."
        )
        if stats:
            notes.append(history_note(stats, starts))
        if skipped:
            notes.append(
                f"The list also names {' and '.join(sorted(set(skipped)))}, part of a member state; no party row."
            )
        if row.get("notification"):
            paragraph = row["notification"].replace("Paragraph", "paragraph")
            notes.append(f"Notified under {paragraph} of the Transparency Mechanism for PTAs (WT/L/806).")
        record = {
            "id": spec["id"],
            "name": spec.get("name") or clean_name(row["name"]),
            "acronyms": [{"lang": "en", "value": a} for a in spec.get("acronyms", [])],
            "other_names": [{"lang": "en", "name": spec["other"]}] if spec.get("other") else [],
            "agreement_type": "preference_scheme",
            "status": status,
            "in_force": wto_date(row["entry_into_force"]),
            "ended": record_ended,
            "parties": [{"id": grantor[0], "type": grantor[1], "role": "grantor"}, *parties],
            "superseded_by": spec.get("superseded_by"),
            "parent": spec.get("parent"),
            "wto_pta_ids": ids,
            "notes": " ".join(notes),
            "verification": "catalogue",
            "last_verified": retrieved,
            "provenance": provenance(version, retrieved, ("parties", "status", "in_force"), stats),
        }
        records.append(record)
        by_pta[pta] = record
    for (pta, label), spec in SUBSCHEMES.items():
        row = rows[pta]
        if label not in row["subschemes"]:
            raise SystemExit(f"sub-scheme {label!r} not in PTA {pta}")
        if spec.get("existing"):
            continue
        parent = by_pta.get(pta)
        parent_id = parent["id"] if parent else EXISTING[pta]
        grantor = dict(parent["parties"][0]) if parent else {"id": "US", "type": "country", "role": "grantor"}
        status = parent["status"] if parent else "in_force"
        ended_by = (parent or {}).get("ended") if status in ("terminated", "superseded") else None
        parties, _, stats, starts = roster(row, codes, grantor["id"], label, ended=ended_by)
        current = [p for p in parties if not p.get("left")]
        notes = []
        if pta == 98:
            kz = {p["id"] for p in beneficiary_parties(rows[87]["subschemes"][label], codes, "EAEU")[0]}
            extra = sorted(kz - {p["id"] for p in current})
            if extra:
                notes.append(
                    f"Kazakhstan's notification (PTA 87) also lists {', '.join(extra)}; the list here is "
                    "the one Armenia, the Kyrgyz Republic and Russia notify."
                )
        version = row["version_date"]
        earliest = stats["first"] if stats else version
        in_force = spec.get("in_force") or earliest
        if not spec.get("in_force"):
            # A version notified after the scheme lapsed (US GSP) still lists a sub-scheme that was in
            # force before: it was in force by the parent's end date at the latest.
            if ended_by and earliest and ended_by < earliest:
                in_force = ended_by
            notes.append(
                "The PTA Database gives no start date for the sub-scheme. in_force is the latest date by "
                f"which it was in force: {in_force}, from the earliest version that lists it ({earliest})"
                + (" and the end of the parent scheme." if in_force != earliest else ".")
            )
        notes.append(
            f"Current beneficiaries are those of the PTA Database version as of {version or 'an unknown date'} "
            f"({countries(len(current))}), not checked against the grantor's own list."
        )
        if stats:
            notes.append(history_note(stats, starts))
        prov = provenance(version, retrieved, ("parties", "status"), stats)
        if spec.get("in_force_source"):
            prov.append({"field": "in_force", "source": spec["in_force_source"], "retrieved_at": retrieved})
        else:
            prov.append(
                {
                    "field": "in_force",
                    "source": f"{SOURCE}, version as of {earliest}",
                    "url": LIST_URL,
                    "retrieved_at": retrieved,
                }
            )
        records.append(
            {
                "id": spec["id"],
                "name": spec["name"],
                "acronyms": [{"lang": "en", "value": a} for a in spec.get("acronyms", [])],
                "agreement_type": "preference_scheme",
                "status": "terminated" if status == "superseded" else status,
                "in_force": in_force,
                "ended": ended_by,
                "parties": [grantor, *parties],
                "parent": parent_id,
                "notes": " ".join(notes),
                "verification": "catalogue",
                "last_verified": retrieved,
                "provenance": prov,
            }
        )
    return records, existing


# PTA id -> (linked intblock, sub-scheme label): official rosters that are reviewed, not rewritten.
LINKED = {
    37: ("AGOA", None),
    70: ("CARIBCAN", None),
    78: ("CBERA", None),
    80: ("SPARTECA", None),
    36: ("GSPPLUS", "GSP+"),
}


def review(snapshot: dict, out: Path) -> None:
    """TSV of the dates the versions suggest for linked intblocks, and their membership differences."""
    codes = load_codes()
    rows = {}
    for row in snapshot["rows"]:
        rows.setdefault(row["pta_id"], row)
    header = (
        "intblock\tcountry\tpta_in_force\tpta_left\tpta_note\tincludes_status\tincludes_joined\tincludes_left\tfinding"
    )
    lines = [header]
    for pta, (intblock_id, label) in LINKED.items():
        intblock = yaml.safe_load(
            (ROOT / "data" / "intblocks" / "pta" / f"{intblock_id}.yaml").read_text(encoding="utf-8")
        )
        includes = {str(i["id"]): i for i in intblock.get("includes") or [] if i.get("status") in INCLUDE_STATUSES}
        grantor = next(k for k, v in includes.items() if v["status"] == "contributor")
        parties, _, _, _ = roster(rows[pta], codes, grantor, label)
        dated = {p["id"]: p for p in parties}
        recipients = {k for k, v in includes.items() if v["status"] == "recipient"}
        for cid in sorted(set(dated) | recipients):
            p, inc = dated.get(cid, {}), includes.get(cid, {})
            if not inc:
                finding = "listed in PTA Database versions, not in includes"
            elif not p:
                finding = "in includes, in no PTA Database version"
            elif bool(p.get("left")) != bool(inc.get("left")):
                finding = "current in one source only"
            elif (p.get("in_force") and not inc.get("joined")) or (p.get("left") and not inc.get("left")):
                finding = "date suggested"
            else:
                finding = ""
            lines.append(
                "\t".join(
                    str(x or "")
                    for x in (
                        intblock_id,
                        cid,
                        p.get("in_force"),
                        p.get("left"),
                        p.get("note"),
                        inc.get("status"),
                        inc.get("joined"),
                        inc.get("left"),
                        finding,
                    )
                )
            )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    flagged = sum(1 for line in lines[1:] if not line.endswith("\t"))
    print(f"review: {len(lines) - 1} rows, {flagged} with a finding, in {out}")


INCLUDE_STATUSES = {"contributor", "recipient"}


def write(snapshot_path: Path, apply: bool, report: Path | None = None) -> int:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    records, existing = build(snapshot)
    if report:
        review(snapshot, report)
    taken = {p.stem for p in REGISTRY.glob("*.yaml")}
    for record in records:
        state = "update" if record["id"] in taken else "new"
        beneficiaries = sum(1 for p in record["parties"] if p["role"] == "beneficiary")
        print(f"{state}\t{record['id']}\t{record['status']}\t{beneficiaries}\t{record.get('parent') or ''}")
        if apply:
            (REGISTRY / f"{record['id']}.yaml").write_text(
                yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120), encoding="utf-8"
            )
    for rid, fields in existing.items():
        path = REGISTRY / f"{rid}.yaml"
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        # Keep the record's own key order; new keys go just before verification.
        updated = {}
        for key, value in record.items():
            if key == "verification":
                updated.update({k: v for k, v in fields.items() if k not in record})
            updated[key] = fields.get(key, value)
        print(f"existing\t{rid}\t{fields}")
        if apply:
            path.write_text(yaml.safe_dump(updated, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    print(f"{len(records)} records, {len(existing)} existing updated" + ("" if apply else " (dry run; pass --write)"))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "fetch":
        return fetch(Path(argv[1]))
    if len(argv) >= 3 and argv[0] == "history":
        return history(Path(argv[1]), Path(argv[2]))
    if len(argv) >= 2 and argv[0] == "write":
        report = Path(argv[argv.index("--report") + 1]) if "--report" in argv[2:] else None
        return write(Path(argv[1]), "--write" in argv[2:], report)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
