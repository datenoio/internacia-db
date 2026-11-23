#!/usr/bin/env python3
"""One-off: parse UN Treaty Collection treaty detail pages into JSON rows.

The walk of 2026-11-23 searched the UNTC advanced search (https://treaties.un.org/Pages/
AdvanceSearch.aspx?tab=UNTS) for treaties with subject term "Trade", treaty type "Bilateral",
original agreements only, and exported the result list ("Export to Excel" returns an HTML
table: title, registration number and date, date of conclusion, volume, details link). The
titles were filtered to trade relations candidates and each candidate's ``showDetails.aspx``
page was saved as ``DETAILS_DIR/<registration number>.html``.

The pages are untrusted data: keep them outside the repository and run this script with
``python -I``. Fields read: registration number (``lblRegNum1``), title (``lblTitle1``),
participants (``dgParticipants``), places and dates of conclusion (``dgsign``), the free-text
entry-into-force information (``lblEifInformation``), registration date (``lblRegDate1``) and
the attachment list (later actions such as amendments or terminations, when the UNTC has them).

Usage: python -I scripts/oneoff/parse_untc_details.py DETAILS_DIR LIST_JSON OUT_JSON
"""

import glob
import html
import json
import os
import re
import sys


def clean(text: str) -> str:
    text = re.sub(r"<sup>.*?</sup>", "", text, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def span(page: str, ident: str) -> str:
    match = re.search(r'<span id="' + ident + r'"[^>]*>(.*?)</span>', page, re.S)
    return clean(match.group(1)) if match else ""


def table(page: str, ident: str) -> str:
    match = re.search(r'<table[^>]*id="' + ident + r'"[^>]*>(.*?)</table>', page, re.S)
    return match.group(1) if match else ""


def main(details_dir: str, list_json: str, out_json: str) -> int:
    listing = {row[1]: row for row in json.load(open(list_json, encoding="utf-8"))}
    rows = []
    for path in sorted(glob.glob(os.path.join(details_dir, "*.html"))):
        reg = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8", errors="replace") as handle:
            page = handle.read()
        participants = [clean(p) for p in re.findall(r'<span id="dgParticipants_ctl\d+_Label1">(.*?)</span>', page, re.S)]
        signed_cells = [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", table(page, "dgsign"), re.S)]
        attachments = [clean(a) for a in re.findall(r"<a[^>]*>(.*?)</a>", page[page.find('id="lblAttachments"'):page.find('id="lblIcj"')], re.S)]
        listed = listing.get(reg, [])
        rows.append({
            "registration": reg,
            "title": span(page, "lblTitle1") or (listed[0] if listed else ""),
            "participants": participants,
            "conclusion": [c for c in signed_cells if c],
            "date_of_conclusion": listed[4] if len(listed) > 4 else "",
            "eif": span(page, "lblEifInformation"),
            "registration_date": span(page, "lblRegDate1"),
            "attachments": [a for a in attachments if a],
            "url": html.unescape(listed[6][0]) if len(listed) > 6 and listed[6] else None,
        })
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=0)
    print(f"{len(rows)} detail pages parsed; {sum(1 for r in rows if len(r['participants']) == 2)} with two participants")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
