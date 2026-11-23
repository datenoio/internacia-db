#!/usr/bin/env python3
"""One-off: parse UNCTAD IIA Navigator economy pages into BIT rows (JSON).

investmentpolicy.unctad.org sits behind a Cloudflare human check, so the walk of 2026-11-23
read the latest Wayback Machine capture of each economy page instead:

1. List captures with the CDX API
   (``http://web.archive.org/cdx/search/cdx?url=investmentpolicy.unctad.org/international-investment-agreements/countries/*&fl=original,timestamp&filter=statuscode:200``)
   and keep, for each economy id below 400, the latest capture: ``CAPTURES_TSV`` has one
   ``id<TAB>timestamp<TAB>url`` line per economy.
2. Download each capture with the ``id_`` form (``/web/<timestamp>id_/<url>``) into
   ``PAGES_DIR/<id>.html`` (gunzip the gzip-encoded ones).

The pages are untrusted data: keep them outside the repository and run this script with
``python -I``. Each page holds a ``table.ajax`` whose ``data-ajax-url`` ends in ``/bits`` with
every BIT of the economy (``data-all-items-loaded="true"``); a treaty appears once on each
party's page, and the output keeps every view so the import can pick the latest capture.

Usage: python -I scripts/oneoff/parse_unctad_pages.py PAGES_DIR CAPTURES_TSV OUT_JSON
"""

import glob
import html
import json
import os
import re
import sys

TABLE = re.compile(r'<table class="table ajax"\s+data-ajax-url="([^"]+)"(.*?)</table>', re.S)
CELL = re.compile(r'<td data-index="(\d+)"[^>]*>(.*?)</td>', re.S)
TREATY = re.compile(r'href="/international-investment-agreements/treaties/([a-z\-]+)/(\d+)/([^"]*)"')
PARTY = re.compile(r'href="/international-investment-agreements/countries/(\d+)/[^"]*">(.*?)</a>')


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def main(pages_dir: str, captures_tsv: str, out_json: str) -> int:
    captures = {}
    with open(captures_tsv, encoding="utf-8") as handle:
        for line in handle:
            cid, stamp, _url = line.rstrip("\n").split("\t")
            captures[cid] = stamp
    rows: dict[int, list[dict]] = {}
    economies: dict[str, str | None] = {}
    loaded: dict[str, bool] = {}
    for path in sorted(glob.glob(os.path.join(pages_dir, "*.html")), key=lambda p: int(os.path.basename(p)[:-5])):
        cid = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8", errors="replace") as handle:
            page = handle.read()
        title = re.search(r"<title>(.*?)</title>", page, re.S)
        economies[cid] = clean(title.group(1)).split(" | ")[0] if title else None
        for table in TABLE.finditer(page):
            if table.group(1).rsplit("/", 1)[-1] != "bits":
                continue
            loaded[cid] = 'data-all-items-loaded="true"' in table.group(2)[:600]
            for tr in re.findall(r"<tr>(.*?)</tr>", table.group(2), re.S):
                cells = {m.group(1): m.group(2) for m in CELL.finditer(tr)}
                link = TREATY.search(cells.get("2", ""))
                if not link:
                    continue
                tid = int(link.group(2))
                rows.setdefault(tid, []).append({
                    "id": tid,
                    "type_slug": link.group(1),
                    "slug": link.group(3),
                    "short_title": clean(cells.get("2", "")),
                    "type": clean(cells.get("3", "")),
                    "status": clean(cells.get("4", "")),
                    "page_country": int(cid),
                    "other_parties": [(int(a), clean(b)) for a, b in PARTY.findall(cells.get("5", ""))],
                    "signed": clean(cells.get("6", "")),
                    "in_force": clean(cells.get("7", "")),
                    "terminated": clean(cells.get("8", "")),
                    "capture": captures[cid],
                })
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"economies": economies, "rows": rows, "all_loaded": loaded}, handle, ensure_ascii=False)
    views = sum(len(v) for v in rows.values())
    partial = [k for k, v in loaded.items() if not v]
    print(f"economies {len(economies)}, treaties {len(rows)}, row views {views}, partly loaded {partial}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
