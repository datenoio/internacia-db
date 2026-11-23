#!/usr/bin/env python3
"""One-off: download the World Bank GPTAD library and agreement pages for import_gptad.py.

The Global Preferential Trade Agreements Database (https://wits.worldbank.org/gptad/) has
no export. This script saves, into OUT_DIR (keep it outside the repository):

- ``library.html``: the library table (one row per agreement: common name, membership,
  type, dates, WTO notification, in-force status, links to the full-text and annex PDFs);
- ``ids.json``: every agreement id (``dispIDS``) with its common name, collected from
  provision searches whose result lists together cover the database;
- ``detail/<id>.html``: the indexed provisions of one agreement (official name, languages,
  WTO document symbol, predecessor agreements and the full-text PDF link).

The detail view is an ASP.NET postback, so each detail request posts the view state of a
search whose result list contains that id. Requests are spaced by ``--delay`` seconds.
Standard library only; the saved pages are untrusted data.

Usage: python -I scripts/oneoff/fetch_gptad.py OUT_DIR [--delay 1.0] [--only ID,ID]
"""

from __future__ import annotations

import argparse
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://wits.worldbank.org/gptad/"
# Provision searches (field code, text) whose result lists together hold every agreement.
SEARCHES = [
    ("I_1_4", "agreement"),  # Type of Agreement
    ("I_1_3", "a"),  # Membership
    ("I_1_1", "a"),  # Common Name
    ("I_1_1", "e"),
    ("All Fields", "the"),
]


def opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "Mozilla/5.0 (internacia-db GPTAD walk)")]
    return op


def fetch(op: urllib.request.OpenerDirector, url: str, data: list[tuple[str, str]] | dict | None = None) -> str:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    with op.open(url, body, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def result_ids(page: str) -> dict[int, str]:
    """Agreement ids and common names in a search result page."""
    if 'id="dispIDS"' not in page:
        return {}
    block = page.split('id="dispIDS"', 1)[1].split("</select>", 1)[0]
    return {
        int(i): html.unescape(name).strip()
        for i, name in re.findall(r"<option[^>]*value=[\"']?(\d+)[^>]*>([^<]*)", block)
    }


def hidden_fields(page: str) -> list[tuple[str, str]]:
    """The hidden inputs (view state, event validation) of the result page's form."""
    form = page.split('id="provSelect"', 1)[1].split("</form>", 1)[0]
    fields = []
    for tag in re.findall(r"<input[^>]*type=\"hidden\"[^>]*>", form):
        name = re.search(r'name="([^"]+)"', tag)
        value = re.search(r'value="([^"]*)"', tag)
        if name:
            fields.append((name.group(1), html.unescape(value.group(1)) if value else ""))
    return fields


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--only", help="comma-separated ids to fetch (default: all)")
    args = parser.parse_args(argv)
    out: Path = args.out_dir
    (out / "detail").mkdir(parents=True, exist_ok=True)

    op = opener()
    (out / "library.html").write_text(fetch(op, BASE + "library.aspx"), encoding="utf-8")
    fetch(op, BASE + "database_landing.aspx")

    names: dict[int, str] = {}
    sessions: list[tuple[set[int], list[tuple[str, str]]]] = []
    for field, text in SEARCHES:
        page = fetch(op, BASE + "database_search_results.aspx",
                     {"provisionText": text, "provisionName": field, "-New": "Submit"})
        ids = result_ids(page)
        names.update(ids)
        sessions.append((set(ids), hidden_fields(page)))
        time.sleep(args.delay)
    (out / "ids.json").write_text(
        json.dumps({str(k): v for k, v in sorted(names.items())}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"{len(names)} agreement ids")

    wanted = sorted(int(i) for i in args.only.split(",")) if args.only else sorted(names)
    missing = 0
    for agreement in wanted:
        target = out / "detail" / f"{agreement}.html"
        if target.exists():
            continue
        session = next((fields for ids, fields in sessions if agreement in ids), None)
        if session is None:
            print(f"! {agreement}: in no search result list", file=sys.stderr)
            missing += 1
            continue
        data = [*session, ("dispIDS", str(agreement)), ("ChktoshowNullcolumns", "1")]
        page = fetch(op, BASE + "database_search_results.aspx?show=1", data)
        if "I.1.1" not in page:
            print(f"! {agreement}: no provisions in the response", file=sys.stderr)
            missing += 1
        else:
            target.write_text(page, encoding="utf-8")
        time.sleep(args.delay)
    print(f"saved {len(list((out / 'detail').glob('*.html')))} detail pages, {missing} failed")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
