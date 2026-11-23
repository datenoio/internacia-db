#!/usr/bin/env python3
"""One-off: map World Bank Deep Trade Agreements (DTA) ids to trade agreement records.

Input is an XLSX file of the DTA database, version 2 of 23 January 2024: "DTA 1.0 -
Horizontal Content (v2).xlsx" or "DTA 2.0 - Vertical Content (v2).xlsx", linked from
https://datatopics.worldbank.org/dta/table.html. Both have the same ``Agreements`` sheet: one row
per agreement, with ``WB ID`` (the key of every DTA content file), ``RTA ID`` and columns copied
from the WTO RTA-IS export. The file is untrusted data: keep it outside the repository and run
this script with ``python -I``.

Each ``WB ID`` gets one result, checked in this order:

- ``mapped``: the record that already has the ``dta_id``; ``MAPPED`` (checked by hand: DTA
  gives a placeholder RTA ID, or an RTA ID that the current WTO export no longer lists);
- ``skipped``: an accession or EC/EU enlargement (``Accession?`` is ``Yes``). The registry
  records these as party dates of the agreement acceded to, not as records;
- ``mapped``: the one record whose ``wto_rta_id`` is the row's RTA ID;
- ``unmatched``: anything else, listed in the report.

Mapped records get ``dta_id``, written after their other catalogue ids. No record is added, and
no status, date, party or verification level changes: the DTA ``Agreements`` sheet is an older
copy of WTO RTA-IS, which the registry already walked. The DTA content data (policy-area
coverage, legal enforceability, provision coding) is not imported: it is a depth measure, out of
the registry scope. See ``openspec/changes/add-dta-catalogue-links``.

Usage: python -I scripts/oneoff/import_dta.py DTA_XLSX [--write] [--report TSV]
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
SHEET = "Agreements"

# WB ID -> registry id, checked by hand.
MAPPED = {
    # RTA ID 999A1: RCEP had not been notified to the WTO; the registry record has no wto_rta_id.
    395: "RCEP",
    # RTA ID 999A2: AfCFTA, notified since as RTA ID 1086 (the record's wto_rta_id).
    396: "AfCFTA",
    # RTA ID 999A3: the EU-MERCOSUR trade agreement, coded from the 2019 agreement in principle
    # (DTA status "Early Announcement"); the registry record is the agreement now in force.
    397: "EUMERCOSUR",
    # RTA ID 136: SPARTECA (1980), which the current WTO RTA-IS export no longer lists.
    14: "SPARTECA",
}
# Catalogue id fields, in record order; dta_id goes after the last one present.
CATALOGUE_KEYS = ("wto_rta_id", "aric_id", "gptad_id")
FALLBACK_ANCHORS = ("\nwikidata_id:", "\nlinks:", "\ndescription:", "\nnotes:", "\nverification:")


# --- input -----------------------------------------------------------------------------------

def read_sheet(path: Path, name: str) -> list[dict]:
    """Rows of one sheet as dicts, read with the standard library only."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    with zipfile.ZipFile(path) as z:
        shared = [
            "".join(t.text or "" for t in si.iter(f"{ns}t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{ns}si")
        ]
        targets = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheet = next(s for s in ET.fromstring(z.read("xl/workbook.xml")).find(f"{ns}sheets") if s.get("name") == name)
        target = targets[sheet.get(rel)].lstrip("/")
        root = ET.fromstring(z.read(target if target.startswith("xl/") else f"xl/{target}"))
    table = []
    for row in root.iter(f"{ns}row"):
        cells = {}
        for c in row.findall(f"{ns}c"):
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            v = c.find(f"{ns}v")
            if c.get("t") == "s" and v is not None:
                cells[col - 1] = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                cells[col - 1] = "".join(t.text or "" for t in c.iter(f"{ns}t"))
            else:
                cells[col - 1] = v.text if v is not None else None
        table.append([cells.get(i) for i in range(max(cells) + 1)] if cells else [])
    header = [str(h).strip() if h is not None else "" for h in table[0]]
    return [dict(zip(header, (r + [None] * len(header))[: len(header)], strict=True)) for r in table[1:] if any(r)]


def integer(value) -> int | None:
    """An Excel number as int (``437`` or ``437.0``); None for text such as ``999A1``."""
    text = str(value).strip() if value is not None else ""
    if re.fullmatch(r"\d+(\.0+)?", text):
        return int(float(text))
    return None


def excel_date(value) -> str:
    if integer(value) is None:
        return ""
    return (date(1899, 12, 30) + timedelta(days=integer(value))).isoformat()


def clean(text) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


# --- output ----------------------------------------------------------------------------------

def insert_dta_id(text: str, dta_id: int) -> str:
    """Add ``dta_id`` after the record's other catalogue ids, keeping its layout."""
    if re.search(r"(?m)^dta_id:", text):
        return text
    lines = text.splitlines(keepends=True)
    last = max((i for i, line in enumerate(lines) if line.split(":", 1)[0] in CATALOGUE_KEYS), default=None)
    if last is not None:
        return "".join(lines[: last + 1] + [f"dta_id: {dta_id}\n"] + lines[last + 1:])
    for anchor in FALLBACK_ANCHORS:
        if anchor in text:
            return text.replace(anchor, f"\ndta_id: {dta_id}{anchor}", 1)
    raise ValueError("no place for dta_id")


# --- main ------------------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dta_xlsx", type=Path)
    parser.add_argument("--write", action="store_true", help="write dta_id to data/trade_agreements/")
    parser.add_argument("--report", type=Path, help="TSV with one row per WB ID")
    args = parser.parse_args(argv)

    rows = read_sheet(args.dta_xlsx, SHEET)
    registry = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(REGISTRY.glob("*.yaml"))}
    by_dta = {int(r["dta_id"]): rid for rid, r in registry.items() if r.get("dta_id")}
    by_wto: dict[int, list[str]] = {}
    for rid, record in registry.items():
        if record.get("wto_rta_id"):
            by_wto.setdefault(int(record["wto_rta_id"]), []).append(rid)
    for wb_id, rid in MAPPED.items():
        if rid not in registry:
            print(f"! MAPPED {wb_id} names {rid}, which is not a registry record")
            return 1

    results: list[dict] = []
    for row in rows:
        wb_id = integer(row.get("WB ID"))
        if wb_id is None:
            print(f"! row without a WB ID: {clean(row.get('Agreement'))}")
            return 1
        rta_raw = clean(row.get("RTA ID"))
        rta = integer(row.get("RTA ID"))
        result = {
            "wb_id": wb_id, "rta_id": str(rta) if rta is not None else rta_raw,
            "agreement": clean(row.get("Agreement")), "status": clean(row.get("Status")),
            "signed": excel_date(row.get("Date of Signature (G)")) or excel_date(row.get("Date of Signature (S)")),
            "accession": clean(row.get("Accession?")),
        }
        if wb_id in by_dta:
            result.update(result="mapped", record=by_dta[wb_id], how="dta_id", detail="")
        elif wb_id in MAPPED:
            result.update(result="mapped", record=MAPPED[wb_id], how="MAPPED", detail="")
        elif result["accession"].lower() == "yes":
            result.update(result="skipped", record="", how="accession",
                          detail="accession or enlargement: party dates of the agreement acceded to")
        elif rta is not None and len(by_wto.get(rta, [])) == 1:
            result.update(result="mapped", record=by_wto[rta][0], how="wto_rta_id", detail="")
        else:
            result.update(result="unmatched", record="", how="",
                          detail=" ".join(by_wto.get(rta, [])) if rta is not None else "placeholder RTA ID")
        results.append(result)

    # A record takes one DTA id, and a DTA id one record.
    claims: dict[str, list[int]] = {}
    for r in results:
        if r["result"] == "mapped":
            claims.setdefault(r["record"], []).append(r["wb_id"])
    conflicts = {rid: ids for rid, ids in claims.items() if len(ids) > 1}
    seen_ids = [r["wb_id"] for r in results]
    if conflicts or len(seen_ids) != len(set(seen_ids)):
        print(f"! conflicts: {conflicts}; repeated WB IDs: {sorted({i for i in seen_ids if seen_ids.count(i) > 1})}")
        return 1

    counts: dict[str, int] = {}
    for r in results:
        key = f"{r['result']}:{r['how']}" if r["how"] else r["result"]
        counts[key] = counts.get(key, 0) + 1
    print(f"rows={len(results)}", " ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    if args.report:
        cols = ["wb_id", "result", "how", "record", "detail", "rta_id", "agreement", "status", "signed", "accession"]
        with args.report.open("w", encoding="utf-8") as out:
            out.write("\t".join(cols) + "\n")
            for r in results:
                out.write("\t".join(str(r.get(c, "")).replace("\t", " ") for c in cols) + "\n")

    if args.write:
        written = 0
        for r in results:
            if r["result"] != "mapped":
                continue
            path = REGISTRY / f"{r['record']}.yaml"
            text = path.read_text(encoding="utf-8")
            new = insert_dta_id(text, r["wb_id"])
            if new != text:
                path.write_text(new, encoding="utf-8")
                written += 1
        print(f"wrote {written} records")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
