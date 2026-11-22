#!/usr/bin/env python3
"""One-off: parse cached ADB ARIC FTA detail pages into the DETAIL_JSON that import_aric_ftas.py reads.

Usage: python -I scripts/oneoff/parse_aric_pages.py LIST_JSON PAGES_DIR OUT_JSON

PAGES_DIR holds one fta.php?id=N&ssid=3 page per row, saved as N.html (untrusted data).
"""
import html
import json
import re
import sys
from pathlib import Path

STATUS_LABELS = ["Signed and In Effect", "Signed but not yet In Effect", "Negotiations launched",
                 "Proposed/Under consultation and study", "Framework Agreement signed", "(FA) signed",
                 "Discontinued", "Negotiations suspended", "Under negotiation", "Official negotiations launched",
                 "Under Negotiation"]

def lines_of(h):
    t = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    return [line.strip() for line in t.splitlines() if line.strip()]

def parse(path, title):
    L = lines_of(path.read_text(encoding="utf-8", errors="replace"))
    out = {"members": [], "dates": [], "wto": [], "short": None, "docs": []}
    try:
        i = next(k for k in range(len(L) - 1) if L[k] == "Trade and Investment" and L[k + 1] == title)
    except StopIteration:
        i = next((k for k, line in enumerate(L) if line == title), None)
        if i is None:
            # The page title can differ from the list title: take the heading after the
            # second "Trade and Investment" breadcrumb.
            hits = [k for k in range(len(L) - 1) if L[k] == "Trade and Investment" and L[k + 1] != "Trade and Investment"]
            if len(hits) < 2:
                out["error"] = "title not found"
                return out
            i = hits[1]
            out["page_title"] = L[i + 1]
            if L[i + 1] == "ASEAN Free Trade Area":
                # fta.php?id=N redirects to the AFTA page for some rows: no usable detail.
                out["error"] = "redirected to the AFTA page"
                return out
    j = i + 2
    if j + 2 < len(L) and L[j] == "(" and L[j + 2] == ")":
        out["short"] = L[j + 1]
    try:
        m = L.index("Members", i)
        r = L.index("Relevant Dates", m)
    except ValueError:
        out["error"] = "no members/dates"
        return out
    out["members"] = L[m + 1:r]
    end = next((k for k in range(r, min(len(L), r + 40)) if L[k] in ("Legal Documents", "Links", "Featured Publications")), r + 20)
    block = L[r + 1:end]
    k = 0
    section = "status"
    while k < len(block):
        item = block[k]
        if item == "Notified to the WTO":
            section = "wto"
            k += 1
            continue
        if k + 1 < len(block) and re.fullmatch(r"\d{4}(-\d{2}(-\d{1,2})?)?", block[k + 1]):
            (out["wto"] if section == "wto" else out["dates"]).append([item, block[k + 1]])
            k += 2
        else:
            k += 1
    if end < len(L) and L[end] == "Legal Documents":
        nxt = next((k for k in range(end + 1, min(len(L), end + 30)) if L[k] in ("Links", "Featured Publications")), end + 1)
        out["docs"] = L[end + 1:nxt]
    return out

rows = {r["id"]: r for r in json.load(open(sys.argv[1]))}
res = {}
for p in sorted(Path(sys.argv[2]).glob("*.html")):
    rid = p.stem
    if rid not in rows:
        continue
    res[rid] = parse(p, rows[rid]["title"])
json.dump(res, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
print(len(res), sum(1 for v in res.values() if v.get("error")))
