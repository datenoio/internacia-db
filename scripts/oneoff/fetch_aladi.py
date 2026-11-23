#!/usr/bin/env python3
"""One-off: download ALADI's agreement records for import_aladi.py.

ALADI (the Latin American Integration Association) is the depositary of the partial-scope
agreements its members conclude under the 1980 Montevideo Treaty. Its agreement database is an
HCL Domino application that answers over plain HTTP only: current agreements are in
``textacdos.nsf``, terminated ones in ``histtextacdos.nsf``. This script saves, into OUT_DIR
(keep it outside the repository):

- ``views/<db>_<view>.xml``: each view as ``ReadViewEntries`` XML. Domino returns at most
  1000 entries per request, and ``Start`` must be the position string of the last entry
  seen (such as ``3.10.15``), so the views are paged by position;
- ``index.json``: one entry per agreement (code such as ``AAP.CE Nº 59``, the view label
  with the signatories, the database, and the documents filed under it);
- ``docs/<code>.html``: the main record of each agreement (signatories, date of signature,
  entry into force, related agreements, synthesis).

Views read: economic complementation (``aceweb``), Article 25 agreements with non-members
(``art25web``), Article 14 agreements (``Art14web``), agricultural (``agropecuariosweb``),
regional market opening (``aperturaweb``), regional tariff preference (``parweb``),
renegotiation (``renegoweb``), and the historical database by country. Trade promotion
agreements (AAP.PC) carry no tariff preferences and are not fetched. Standard library
only; the saved pages are untrusted data.

Usage: python -I scripts/oneoff/fetch_aladi.py OUT_DIR [--delay 0.4]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "http://www2.aladi.org/nsfaladi/"
CURRENT = ["aceweb", "art25web", "Art14web", "agropecuariosweb", "aperturaweb", "parweb", "renegoweb"]
HISTORICAL = "f88cf0ec27a4b651032576790064fc05"  # historical agreements, by country


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (internacia-db ALADI walk)"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def read_view(db: str, view: str, delay: float) -> list[ET.Element]:
    """Every entry of a view, paged by position."""
    entries: list[ET.Element] = []
    seen: set[str] = set()
    start = "1"
    while True:
        root = ET.fromstring(get(f"{BASE}{db}.nsf/{view}?ReadViewEntries&Start={start}&Count=1000&ExpandView"))
        batch = [ve for ve in root.findall("viewentry") if ve.get("position") not in seen]
        if not batch:
            return entries
        for ve in batch:
            seen.add(ve.get("position", ""))
            entries.append(ve)
        start = batch[-1].get("position", "")
        time.sleep(delay)


def index_view(entries: list[ET.Element], db: str, depth: int, out: dict) -> None:
    """Agreements (category rows at ``depth``) and the documents filed under each."""
    current = None
    for ve in entries:
        level = ve.get("position", "").count(".")
        cells = {
            e.get("name"): re.sub(r"\s+", " ", " ".join(x.text or "" for x in e.iter("text"))).strip()
            for e in ve.findall("entrydata")
        }
        category = any(e.get("category") == "true" for e in ve.findall("entrydata"))
        if category and level == depth:
            label = next((v for v in cells.values() if v), "")
            m = re.match(r"((?:AAP|AR)\.[A-Z0-9]+ Nº \d+)", label)
            current = m.group(1) if m else label
            out.setdefault(current, {"code": current, "label": label, "db": db, "docs": []})
        elif not category and current and ve.get("unid") and level == depth + 1:
            docs = out[current]["docs"]
            if ve.get("unid") not in [d[0] for d in docs]:
                docs.append((ve.get("unid"), cells.get("Subject", "")))


def doc_name(code: str) -> str:
    return code.replace(" ", "_").replace("º", "") + ".html"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--delay", type=float, default=0.4)
    args = parser.parse_args(argv)
    out: Path = args.out_dir
    (out / "views").mkdir(parents=True, exist_ok=True)
    (out / "docs").mkdir(exist_ok=True)

    index: dict[str, dict] = {}
    for db, view, depth in [("textacdos", v, 0) for v in CURRENT] + [("histtextacdos", HISTORICAL, 1)]:
        entries = read_view(db, view, args.delay)
        root = ET.Element("viewentries")
        root.extend(entries)
        ET.ElementTree(root).write(out / "views" / f"{db}_{view}.xml", encoding="utf-8")
        index_view(entries, "cur" if db == "textacdos" else "hist", depth, index)
        print(f"{db}/{view}: {len(entries)} entries")

    fetched = 0
    for code, agreement in index.items():
        docs = agreement["docs"]
        main_doc = next((u for u, s in docs if s.strip().lower().startswith("acuerdo")), docs[0][0] if docs else None)
        agreement["main"] = main_doc
        target = out / "docs" / doc_name(code)
        if not main_doc or target.exists():
            continue
        db = "textacdos" if agreement["db"] == "cur" else "histtextacdos"
        target.write_bytes(get(f"{BASE}{db}.nsf/0/{main_doc}?OpenDocument"))
        fetched += 1
        time.sleep(args.delay)
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(index)} agreements, {fetched} records fetched")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
