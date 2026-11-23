#!/usr/bin/env python3
"""One-off: check the UK's trade agreements against gov.uk and the UK treaty series.

Source: the collection "The UK's trade agreements"
(https://www.gov.uk/government/collections/the-uks-trade-agreements) and the collection of each
agreement it links. gov.uk pages are read through the Content API
(``https://www.gov.uk/api/content<path>``) and the Search API; no key is needed.

Each agreement collection holds the treaty as published when it was laid before Parliament
(Country Series ``CS <Country> No.N/YYYY`` or Miscellaneous Series ``MS No.N/YYYY``). Once a treaty
is in force the FCDO republishes it in the Treaty Series (``TS No.N/YYYY``). The cover page of
each PDF names the place and date of signature and, in square brackets, whether and when the
treaty entered into force. Only the first pages of each PDF are read.

Two steps:

``fetch CACHE_DIR``
    Download the collection pages, the treaty pages and the treaty PDFs into CACHE_DIR (keep it
    outside the repository: the files are untrusted data) and write ``CACHE_DIR/govuk.json``
    with the treaty publications of every record in ``AGREEMENTS``. Needs ``pypdf``
    (``pip install pypdf``), which is not a dependency of the builder.

``apply CACHE_DIR [--write]``
    Print the changes the report supports for each record and, with ``--write``, write them:
    gov.uk name (the earlier name stays in ``other_names``), the collection link, the date of
    signature and of entry into force from the treaty series, the series numbers in ``notes``,
    ``verification: official`` and UK Government provenance. A date that differs from the record
    is replaced only from a treaty-series cover page, and the earlier value is named in the
    report. Party rosters are not changed here; they are edited by hand.

Run with ``python -I``. See ``openspec/changes/archive/2026-11-23-add-trade-agreements-registry``.
"""

from __future__ import annotations

import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SOURCE = "UK Government"
TREATY_SOURCE = "UK Government, UK Treaty Series"
GOVUK = "https://www.gov.uk"
API = GOVUK + "/api/content"
SEARCH = GOVUK + "/api/search.json"
USER_AGENT = "internacia-db one-off (trade agreements registry)"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "wikidata_id", "links", "description", "notes", "verification",
    "last_verified", "provenance",
]

# Registry id -> (gov.uk name, agreement collections). The name is the one the "UK trade
# agreements in effect" page links, in title case.
AGREEMENTS: dict[str, tuple[str, list[str]]] = {
    "ALGB": ("UK-Albania Partnership, Trade and Cooperation Agreement",
             ["uk-albania-partnership-trade-and-cooperation-agreement"]),
    "CAGB": ("UK-Canada Trade Continuity Agreement", ["uk-canada-trade-continuity-agreement"]),
    "CHGBLI": ("UK-Switzerland-Liechtenstein Trade Agreement",
               ["uk-switzerland-trade-agreement", "uk-switzerland-liechtenstein-trade-agreement"]),
    "CIGB": ("UK-Côte d'Ivoire Stepping Stone Economic Partnership Agreement",
             ["uk-cote-divoire-stepping-stone-economic-partnership-agreement"]),
    "CLGB": ("UK-Chile Association Agreement", ["uk-chile-association-agreement"]),
    "CMGB": ("UK-Cameroon Economic Partnership Agreement", ["uk-cameroon-economic-partnership-agreement"]),
    "EGGB": ("UK-Egypt Association Agreement", ["uk-egypt-associationagreement"]),
    "FOGB": ("UK-Faroe Islands Free Trade Agreement", ["uk-faroe-islands-free-trade-agreement-fta"]),
    "GBGE": ("UK-Georgia Strategic Partnership and Cooperation Agreement",
             ["uk-georgia-strategic-partnership-and-cooperation-agreement--2"]),
    "GBGH": ("UK-Ghana Interim Trade Partnership Agreement", ["uk-ghana-interim-trade-partnership-agreement"]),
    "GBIL": ("UK-Israel Trade and Partnership Agreement", ["uk-israel-trade-and-partnership-agreement"]),
    "GBISLINO": ("UK-Norway, Iceland and Liechtenstein Free Trade Agreement",
                 ["uk-norway-iceland-and-liechtenstein-free-trade-agreement"]),
    "GBJO": ("UK-Jordan Association Agreement", ["uk-jordan-association-agreement"]),
    "GBKE": ("UK-Kenya Economic Partnership Agreement", ["uk-kenya-economic-partnership-agreement"]),
    "GBKR": ("UK-South Korea Trade Agreement", ["uk-south-korea-trade-agreement"]),
    "GBLB": ("UK-Lebanon Association Agreement", ["uk-lebanon-association-agreement"]),
    "GBMA": ("UK-Morocco Association Agreement", ["uk-morocco-association-agreement"]),
    "GBMD": ("UK-Moldova Strategic Partnership, Trade and Cooperation Agreement",
             ["uk-moldova-strategic-partnership-trade-and-cooperation-agreement"]),
    "GBMK": ("UK-North Macedonia Partnership, Trade and Cooperation Agreement",
             ["uk-north-macedonia-partnership-trade-andcooperationagreement"]),
    "GBMX": ("UK-Mexico Trade Continuity Agreement", ["uk-mexico-trade-continuity-agreement"]),
    "GBPS": ("UK-Palestinian Authority Political, Trade and Partnership Agreement",
             ["uk-palestinian-authority-political-trade-and-partnership-agreement"]),
    "GBRS": ("UK-Serbia Partnership, Trade and Cooperation Agreement",
             ["uk-serbia-partnership-trade-and-cooperation-agreement"]),
    "GBSG": ("UK-Singapore Free Trade Agreement", ["uk-singapore-trade-agreement"]),
    "GBSG-DEA": ("UK-Singapore Digital Economy Agreement", ["uk-singapore-digital-economy-agreement"]),
    "GBTN": ("UK-Tunisia Association Agreement", ["uk-tunisia-association-agreement"]),
    "GBTR": ("UK-Turkey Trade Agreement", ["uk-turkey-trade-agreement"]),
    "GBUA": ("UK-Ukraine Political, Free Trade and Strategic Partnership Agreement",
             ["uk-ukraine-political-free-trade-and-strategic-partnership-agreement"]),
    "GBUA-DTA": ("UK-Ukraine Digital Trade Agreement", ["uk-ukraine-digital-trade-agreement"]),
    "GBVN": ("UK-Vietnam Free Trade Agreement", ["uk-vietnam-free-trade-agreement"]),
    "GBXK": ("UK-Kosovo Partnership, Trade and Cooperation Agreement",
             ["uk-kosovopartnership-trade-and-cooperationagreement"]),
    "SACUGBMZ": ("SACUM-UK Economic Partnership Agreement", ["sacum-uk-economic-partnership-agreement-epa"]),
    "UKANDEAN": ("UK-Andean Countries Trade Agreement", ["uk-andean-countries-trade-agreement"]),
    "UKCARIFORUM": ("CARIFORUM-UK Economic Partnership Agreement",
                    ["cariforum-uk-economic-partnership-agreement"]),
    "UKCENTRALAMERICA": ("UK-Central America Association Agreement",
                         ["uk-central-america-association-agreement"]),
    "UKESA": ("ESA-UK Economic Partnership Agreement", ["esa-uk-economic-partnership-agreement-epa--2"]),
}

GUIDE = GOVUK + "/guidance/"
IN_EFFECT = GOVUK + "/guidance/uk-trade-agreements-in-effect"

# Provisional application that a UK Government source states: record id -> (date, source URL,
# note). The UK list of agreements in effect gives the mechanism ("Provisional application");
# the date is the one the agreement began to apply, as the cited page or the catalogue gives it.
PROVISIONAL: dict[str, tuple[str, str, str]] = {
    "CAGB": ("2021-01-01", GOVUK + "/government/publications/memorandum-of-understanding-between-the-uk-and-"
             "canada-on-the-trade-continuity-agreement",
             "A memorandum of understanding applied the agreement from 1 January 2021 until its entry into "
             "force on 1 April 2021."),
    "GBKE": ("2021-01-01", GOVUK + "/government/collections/uk-kenya-economic-partnership-agreement",
             "A memorandum of understanding between the UK and Kenya applied the agreement from 1 January 2021 "
             "until its entry into force on 22 March 2021."),
    "GBMK": ("2021-01-01", IN_EFFECT,
             "Applied provisionally from 1 January 2021; it entered into force on 29 December 2023."),
    "GBTR": ("2021-01-01", IN_EFFECT,
             "Applied provisionally from 1 January 2021; it entered into force on 20 April 2021."),
    "GBRS": ("2021-05-20", GUIDE + "trade-with-serbia",
             "In effect from 20 May 2021; it entered into force on 15 July 2021."),
    "GBISLINO": ("2021-12-01", GUIDE + "trade-with-norway",
                 "Applied with Norway from 1 December 2021 and with Liechtenstein from 1 January 2022; it entered "
                 "into force for the UK, Norway and Liechtenstein on 1 September 2022. It applied with Iceland from "
                 "1 September 2022 and entered into force for Iceland on 1 February 2023."),
    "GBMA": ("2021-01-01", IN_EFFECT,
             "The UK lists the agreement as applied provisionally; no Treaty Series publication records its entry "
             "into force."),
    "UKCARIFORUM": ("2021-01-01", IN_EFFECT,
                    "The UK lists the agreement as applied provisionally; it has not been published in the Treaty "
                    "Series."),
}
# Provisionally applied agreements with no definitive entry into force: in_force is removed.
PROVISIONAL_ONLY = {"GBMA", "UKCARIFORUM"}
# Cover pages the regular expression does not read: record id -> {field: (value, series)}.
OVERRIDES: dict[str, dict[str, tuple[str, str]]] = {
    # "London and Kyiv, 20 March, 5 and 11 May 2023": the first signature.
    "GBUA-DTA": {"signed": ("2023-03-20", "CS Ukraine No.2/2023")},
}

# Treaty publications that are not the agreement itself (memoranda, amendments, decisions).
NOT_THE_AGREEMENT = re.compile(
    r"memorandum|exchange of (letters|notes)|amending|decision|explanatory|protocol 4|spirits", re.I
)
SERIES = re.compile(r"\[((?:CS [^\]]+?|MS|TS) No\.? ?\d+/\d{4})\]")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
SIGNATURE = re.compile(rf"([A-Z][A-Za-z'’ .-]{{1,40}}?),? (\d{{1,2}}) ({MONTHS}) (\d{{4}})")
BRACKET = re.compile(r"\[(The [^\]]{5,500})\]")
IN_FORCE = re.compile(rf"entered into force(?: on)? (\d{{1,2}}) ({MONTHS}) (\d{{4}})")
COMMAND_PAPER = re.compile(r"\bCP ?(\d{2,4})\b")


def iso(day: str, month: str, year: str) -> str:
    return datetime.strptime(f"{day} {month} {year}", "%d %B %Y").strftime("%Y-%m-%d")


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def treaty_title(title: str) -> str:
    """``UK/Georgia: Strategic Partnership ... [CS Georgia No.1/2019]`` -> text before the series."""
    return re.sub(r"\s*\[[^\]]*\]\s*$", "", title).strip()


def plain_title(title: str) -> str:
    """Title without the series, a ``(with ...)`` annex note, case or spelling variants, for matching."""
    text = re.sub(r"\s*\(with [^)]*\)", "", treaty_title(title)).lower()
    return re.sub(r"\s+", " ", text.replace("türkiye", "turkey")).strip()


def cover(pdf: bytes) -> str:
    from pypdf import PdfReader  # noqa: PLC0415 - optional, only the fetch step needs it

    reader = PdfReader(io.BytesIO(pdf))
    text = " ".join((reader.pages[i].extract_text() or "") for i in range(min(2, len(reader.pages))))
    return re.sub(r"\s+", " ", text)


def parse_cover(text: str) -> dict:
    head, _, tail = text.partition("Presented to Parliament")
    signatures = [
        {"place": place.strip(), "date": iso(day, month, year)}
        for place, day, month, year in SIGNATURE.findall(head)
        if "into force" not in place
    ]
    bracket = BRACKET.search(head)
    status = bracket.group(1) if bracket else None
    in_force = IN_FORCE.search(status or "")
    return {
        "signatures": signatures,
        "status_text": status,
        "in_force": iso(*in_force.groups()) if in_force else None,
        "not_in_force": bool(status and "not in force" in status.lower()),
        # The publication's own command paper follows "Presented to Parliament"; a Treaty Series
        # cover names the earlier one before it ("previously published as ... CP 196").
        "command_papers": COMMAND_PAPER.findall(tail[:400])[:1],
    }


def publication(path: str, cache: Path) -> dict:
    page = get_json(API + path)
    details = page.get("details") or {}
    attachments = [
        a for a in details.get("attachments") or []
        if str(a.get("url", "")).lower().endswith(".pdf")
        and not NOT_THE_AGREEMENT.search(plain_title(a.get("title") or ""))
    ]
    # The formal title is the paragraph "Published title: <title>."; other paragraphs follow.
    match = re.search(r"Published title:\s*(.*?)</p>", details.get("body") or "", re.S)
    published = (
        re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip(" .")
        if match else None
    )
    entry = {
        "title": page.get("title"),
        "path": path,
        "url": GOVUK + path,
        "series": (SERIES.search(page.get("title") or "") or [None, None])[1],
        "published_title": published,
        "first_published_at": (page.get("first_published_at") or "")[:10],
        "pdf": None,
        "cover": None,
    }
    if attachments:
        url = attachments[0]["url"]
        target = cache / "pdf" / Path(urllib.parse.urlparse(url).path).name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(get_bytes(url))
            time.sleep(0.3)
        entry["pdf"] = url
        entry["cover"] = parse_cover(cover(target.read_bytes()))
    return entry


def treaty_series(title: str) -> list[str]:
    """Paths of TS publications with the same title as a CS or MS publication."""
    query = {"q": title, "filter_content_store_document_type": "international_treaty", "count": "20",
             "fields": "title,link"}
    results = get_json(SEARCH + "?" + urllib.parse.urlencode(query)).get("results") or []
    return [
        r["link"] for r in results
        if "[TS No" in r.get("title", "") and plain_title(r["title"]) == plain_title(title)
    ]


def fetch(cache: Path) -> int:
    cache.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict] = {}
    for rid, (name, collections) in AGREEMENTS.items():
        entry = {"name": name, "collections": [], "publications": []}
        for slug in collections:
            path = f"/government/collections/{slug}"
            page = get_json(API + path)
            entry["collections"].append({"url": GOVUK + path, "title": page.get("title")})
            for doc in (page.get("links") or {}).get("documents") or []:
                title = doc.get("title") or ""
                if doc.get("document_type") != "international_treaty" or NOT_THE_AGREEMENT.search(
                    plain_title(title)
                ):
                    continue
                if not re.search(r"\[(CS|MS) ", title):
                    continue
                entry["publications"].append(publication(doc["base_path"], cache))
                for ts_path in treaty_series(treaty_title(title)):
                    entry["publications"].append(publication(ts_path, cache))
            time.sleep(0.3)
        report[rid] = entry
        print(rid, [p["series"] for p in entry["publications"]], file=sys.stderr)
    (cache / "govuk.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


def ordered(record: dict) -> dict:
    out = {k: record[k] for k in FIELD_ORDER if k in record}
    out.update({k: v for k, v in record.items() if k not in out})
    return out


def series_note(publications: list[dict]) -> str | None:
    parts = []
    for pub in publications:
        if not pub.get("series"):
            continue
        papers = (pub.get("cover") or {}).get("command_papers") or []
        cp = f" (CP {papers[0]})" if papers else ""
        series = re.sub(r"No\. ?", "No.", pub["series"])
        parts.append(f"{series}{cp}")
    if not parts:
        return None
    return "Published by the UK as " + ", then ".join(parts) + "."


def apply(cache: Path, write: bool) -> int:
    report = json.loads((cache / "govuk.json").read_text(encoding="utf-8"))
    for rid, entry in report.items():
        path = REGISTRY / f"{rid}.yaml"
        if not path.exists():
            print(f"{rid}: no record (create it by hand first)")
            continue
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        changes: list[str] = []
        pubs = entry["publications"]
        laid = [p for p in pubs if p["series"] and not p["series"].startswith("TS")]
        ts = [p for p in pubs if p["series"] and p["series"].startswith("TS")]
        collection = entry["collections"][0]["url"]

        if record.get("name") != entry["name"]:
            others = record.setdefault("other_names", [])
            if record.get("name") and all(o.get("name") != record["name"] for o in others):
                others.insert(0, {"lang": "en", "name": record["name"]})
            changes.append(f"name {record.get('name')!r} -> {entry['name']!r}")
            record["name"] = entry["name"]
        for pub in laid[:1]:
            formal = pub.get("published_title")
            others = record.setdefault("other_names", [])
            if formal and formal != record["name"] and all(o.get("name") != formal for o in others):
                others.append({"lang": "en", "name": formal})

        links = record.setdefault("links", [])
        for col in entry["collections"]:
            if all(link.get("url") != col["url"] for link in links):
                links.insert(0, {"url": col["url"], "type": "website"})
                changes.append(f"link {col['url']}")

        provenance = record.setdefault("provenance", [])
        catalogue = sorted({p.get("source") for p in provenance if p.get("source") and "UK Government" not in p["source"]
                            and p.get("field") in {"parties", "status", "signed", "in_force"}})
        replaced: list[str] = []

        def cite(field: str, url: str, source: str = SOURCE, provenance: list = provenance) -> None:
            for p in provenance:
                if p.get("field") == field and p.get("url") == url:
                    p["retrieved_at"] = RETRIEVED
                    return
            provenance.append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})

        signatures = sorted(
            {s["date"] for p in laid + ts for s in (p.get("cover") or {}).get("signatures") or []}
        )
        if signatures:
            source_pub = next(p for p in laid + ts if (p.get("cover") or {}).get("signatures"))
            signed = signatures[0]
            override = OVERRIDES.get(rid, {}).get("signed")
            if override:
                signed = override[0]
            if str(record.get("signed") or "") != signed:
                changes.append(f"signed {record.get('signed')} -> {signed}")
                if record.get("signed"):
                    replaced.append(f"the signature date as {record['signed']}")
                record["signed"] = signed
            cite("signed", source_pub["url"], TREATY_SOURCE)

        if not signatures and rid in OVERRIDES and "signed" in OVERRIDES[rid]:
            value, series = OVERRIDES[rid]["signed"]
            pub = next(p for p in laid + ts if p.get("series") == series)
            if str(record.get("signed") or "") != value:
                changes.append(f"signed {record.get('signed')} -> {value}")
                record["signed"] = value
            cite("signed", pub["url"], TREATY_SOURCE)

        forced = [(p, p["cover"]["in_force"]) for p in ts if (p.get("cover") or {}).get("in_force")]
        if forced:
            pub, in_force = forced[0]
            if str(record.get("in_force") or "") != in_force:
                changes.append(f"in_force {record.get('in_force')} -> {in_force}")
                if record.get("in_force") and rid not in PROVISIONAL:
                    replaced.append(f"the entry into force date as {record['in_force']}")
                record["in_force"] = in_force
            cite("in_force", pub["url"], TREATY_SOURCE)

        note = series_note(laid + ts)
        if note and note not in (record.get("notes") or ""):
            record["notes"] = (record.get("notes", "").rstrip() + " " + note).strip()
            changes.append("notes: " + note)

        if rid in PROVISIONAL:
            start, url, text = PROVISIONAL[rid]
            if record.get("provisional_application") != start:
                changes.append(f"provisional_application -> {start}")
                record["provisional_application"] = start
            if rid in PROVISIONAL_ONLY and record.get("in_force"):
                changes.append(f"in_force {record['in_force']} removed (applied provisionally only)")
                replaced.append(f"the entry into force date as {record['in_force']}")
                record.pop("in_force")
            cite("provisional_application", url)
            if text not in (record.get("notes") or ""):
                record["notes"] = (record.get("notes", "").rstrip() + " " + text).strip()

        if replaced and catalogue:
            verb = "gives" if len(catalogue) == 1 else "give"
            text = f"{' and '.join(catalogue)} {verb} " + " and ".join(replaced) + "."
            if text not in (record.get("notes") or ""):
                record["notes"] = (record.get("notes", "").rstrip() + " " + text).strip()

        cite("parties", collection)
        cite("status", GOVUK + "/guidance/uk-trade-agreements-in-effect")
        cite("name", collection)
        record["verification"] = "official"
        record["last_verified"] = RETRIEVED
        print(f"{rid}: " + ("; ".join(changes) if changes else "provenance only"))
        if write:
            path.write_text(
                yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120),
                encoding="utf-8",
            )
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"fetch", "apply"}:
        print(__doc__)
        return 2
    cache = Path(argv[1])
    if argv[0] == "fetch":
        return fetch(cache)
    return apply(cache, "--write" in argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
