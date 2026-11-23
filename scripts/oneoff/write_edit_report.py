#!/usr/bin/env python3
"""One-off: write the EDIT match report from the JSON of ``import_edit.py --report``.

Writes ``docs/history/edit-match-2026-11-23.csv`` (one row per EDIT document and record,
with the EDIT uuid that a later ``edit_uuid`` backfill can apply) and
``docs/history/edit-date-conflicts-2026-11-23.csv`` (each date where EDIT differs from the
record). The Markdown page is written by hand from the counts this script prints.

Usage: python -I scripts/oneoff/write_edit_report.py MATCH_JSON
"""

import collections
import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/history"
HIGH = ("parties, date of signature", "successor state, date of signature", "by hand")


def confidence(method: str) -> str:
    if method.startswith(HIGH):
        return "high"
    if "typing slip" in method:
        return "low"
    return "medium"


def main(argv: list[str]) -> int:
    data = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    report, written = data["report"], data["written"]
    added = set(written.get("added", []))
    linked = set(written.get("links", []))
    rows = []
    for group, treaties in report.items():
        for t in treaties:
            base = {
                "edit_uuid": t["uuid"], "edit_name": t["name"], "edit_type": t["kind"],
                "edit_reference": t.get("reference") or "", "edit_parties": ",".join(t["codes"]),
                "edit_signed": t["signed"] or "", "edit_in_force": t["in_force"] or "",
                "edit_terminated": t["terminated"] or "", "edit_languages": ",".join(t["languages"]),
                "edit_has_text": "yes" if t["has_text"] else "no", "group": group,
            }
            if group == "matched":
                for rid, method in t["matched"]:
                    rows.append({**base, "record_id": rid, "method": method, "confidence": confidence(method),
                                 "treaty_text_link": "yes" if rid in linked and t["has_text"] else "no",
                                 "reason": ""})
                continue
            rid = t.get("record") or ""
            if group == "duplicate":
                reason = f"EDIT lists the same treaty as {t['duplicate_of']}"
            elif group == "instrument":
                reason = f"dated like an instrument of {rid} ({t['instrument'][1]})"
            elif group == "missing":
                reason = t.get("category", "") + ("; the automatic candidate is another agreement" if t.get("rejected") else "")
            else:
                reason = t.get("reason") or ""
            rows.append({**base, "record_id": rid, "method": "", "confidence": "",
                         "treaty_text_link": "yes" if group == "added" and rid in added and t["has_text"] else "no",
                         "reason": reason})
    order = {"matched": 0, "added": 1, "component": 2, "instrument": 3, "duplicate": 4, "held": 5,
             "missing": 6, "plurilateral": 7, "model": 8}
    rows.sort(key=lambda r: (order.get(r["group"], 9), r["edit_signed"], r["edit_name"], r["record_id"]))
    with (OUT / "edit-match-2026-11-23.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    records = {}
    conflicts = []
    noted = set(written.get("notes", [])) | {"CLID", "USBH"}
    for t in report["matched"]:
        for rid, key, mine, value in t["conflicts"]:
            if rid not in records:
                records[rid] = yaml.safe_load((ROOT / "data/trade_agreements" / f"{rid}.yaml").read_text(encoding="utf-8"))
            record = records[rid]
            if record.get("verification") == "official":
                held_by = "official"
            elif record.get("unctad_iia_id"):
                held_by = "UNCTAD IIA Navigator"
            else:
                held_by = "other catalogue"
            conflicts.append({
                "record_id": rid, "field": key, "registry": mine or "", "edit": value, "registry_source": held_by,
                "unctad_iia_id": record.get("unctad_iia_id") or "", "edit_uuid": t["uuid"],
                "noted": "yes" if rid in noted and key != "status" and f"EDIT gives {value}" in (record.get("notes") or "") else "no",
            })
    conflicts.sort(key=lambda r: (r["record_id"], r["field"]))
    with (OUT / "edit-date-conflicts-2026-11-23.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(conflicts[0]))
        writer.writeheader()
        writer.writerows(conflicts)

    print("groups", dict(collections.Counter(r["group"] for r in rows)))
    print("documents by group", {g: len(v) for g, v in report.items()})
    print("matched rows by confidence", dict(collections.Counter(r["confidence"] for r in rows if r["group"] == "matched")))
    print("matched by kind", dict(collections.Counter(t["kind"] for t in report["matched"])))
    print("methods", dict(collections.Counter(m.split(",")[0] for t in report["matched"] for _, m in t["matched"])))
    print("links", len(linked), "notes", len(noted & set(records)))
    print("conflicts", dict(collections.Counter((c["registry_source"], c["field"], "empty" if not c["registry"] else "differs")
                                                for c in conflicts)))
    print("missing by category", dict(collections.Counter((t["kind"], t.get("category")) for t in report["missing"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
