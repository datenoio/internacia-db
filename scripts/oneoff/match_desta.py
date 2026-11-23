#!/usr/bin/env python3
"""One-off: match the DESTA v2.3 list of treaties to the trade agreements registry.

DESTA (Design of Trade Agreements, https://www.designoftradeagreements.org/downloads/) lists
903 base treaties (plus accessions, withdrawals, protocols, consolidated versions and
negotiations). Each base treaty is matched to registry records:

1. by name, when DESTA marks it WTO-listed: its ``wto_name`` is looked up in the RTA Name
   column of the WTO RTA-IS export (``--wto``) and the RTA ID in the records' ``wto_rta_id``
   and instrument ids;
2. by parties and year: a bilateral treaty (``typememb`` 1) needs a two-party record with the
   same two countries; a plurilateral treaty needs a record whose roster (parties, or the
   members of a linked or party intblock) matches the DESTA members (at least 80 percent, or
   at most one country in five different), and a bloc-and-country record must have the same
   third countries; the year of signature (or of entry into force) may differ by one;
3. by an acronym in the DESTA name that is a record id (``(SPARTECA)``).

A record matched by two treaties keeps the treaty with the closer year; the other becomes
ambiguous. The groups are ``matched`` (one record), ``ambiguous`` (records with the same
parties but another year, or several records) and ``missing`` (no record with those parties).
``OVERRIDES`` holds hand matches. Each row gets a ``confidence`` (high, medium, low for
ambiguous, none for missing). DESTA numeric country codes are ISO 3166 numeric; Kosovo is
900.

The downloads are untrusted data: keep them outside the repository and run this script with
``python -I``.

Usage: python -I scripts/oneoff/match_desta.py DESTA_DIR [--wto AllRTAs.xlsx]
       [--ref LABEL=CHECKOUT ...] [--csv OUT.csv] [--json OUT.json]

``--ref`` adds other checkouts (for example open pull requests) after this one; a record id
found in several is credited to the first.
"""
import argparse
import csv
import glob
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
_CACHE: dict = {}

# DESTA number -> (record id, reason), checked by hand.
OVERRIDES = {
    "140": ("BRGY", "AAP.A25TM 38; ALADI also lists Saint Kitts and Nevis, which DESTA leaves out"),
    "267": ("MERCOSURCU", "ACE 62; the record lists the MERCOSUR states one by one"),
    "24": ("ARCAN-ACE48", "ACE 48 between Argentina and the Andean Community countries"),
    "687": ("USVN-TRA", "the 2000 US - Viet Nam bilateral trade agreement, a trade relations record"),
    "976": ("LAUS-TRA", "the 2003 US - Laos bilateral trade agreement, a trade relations record"),
}


def load(f):
    b = open(f, "rb").read()
    h = hashlib.sha1(b).hexdigest()
    if h not in _CACHE:
        _CACHE[h] = yaml.load(b.decode("utf-8"), Loader=_LOADER)
    return _CACHE[h]


ap = argparse.ArgumentParser()
ap.add_argument("desta_dir")
ap.add_argument("--wto")
ap.add_argument("--ref", action="append", default=[])
ap.add_argument("--csv")
ap.add_argument("--json")
args = ap.parse_args()
DESTA_DIR = Path(args.desta_dir)
REFS = [("this", ROOT)] + [(x.split("=", 1)[0], Path(x.split("=", 1)[1])) for x in args.ref]
PARTY_STATUSES = {"member", "founding_member", "former_member", "participant", "associate_member",
                  "associate", "contributor", "recipient"}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def year(v):
    if v is None:
        return None
    m = re.match(r"(\d{4})", str(v))
    return int(m.group(1)) if m else None


# --- countries
num2code = {}
for f in glob.glob(f"{ROOT}/data/countries/*.yaml"):
    d = load(f)
    if d.get("numeric_code"):
        num2code[str(d["numeric_code"]).zfill(3)] = d["code"]
num2code["900"] = "XK"


def code(n):
    n = str(n).strip()
    if not n:
        return None
    return num2code.get(n.zfill(3), f"?{n}")


# --- WTO export
def read_export(path):
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    with zipfile.ZipFile(path) as z:
        shared = ["".join(t.text or "" for t in si.iter(f"{ns}t"))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{ns}si")]
        targets = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheet = next(s for s in ET.fromstring(z.read("xl/workbook.xml")).find(f"{ns}sheets")
                     if s.get("name") == "AllRTAs")
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
    header = table[0]
    return [dict(zip(header, (r + [None] * len(header))[: len(header)], strict=True)) for r in table[1:] if r]


wto = read_export(args.wto) if args.wto else []
wto_by_name = {}
for r in wto:
    wto_by_name.setdefault(norm(r.get("RTA Name")), []).append(int(r["RTA ID"]))

# --- registry
registry = {}  # id -> record info (main preferred, else first PR)
for ref, checkout in REFS:
    base = f"{checkout}/data"
    blocs = {}
    for f in glob.glob(f"{base}/intblocks/*/*.yaml"):
        d = load(f)
        inc = [i["id"] for i in (d.get("includes") or []) if i.get("status") in PARTY_STATUSES]
        blocs[d["id"]] = {"includes": inc, "founded": d.get("founded"), "name": d.get("name")}
    for f in sorted(glob.glob(f"{base}/trade_agreements/*.yaml")):
        d = load(f)
        rid = d["id"]
        if rid in registry:
            if ref != "this" and registry[rid]["raw"] != d:
                registry[rid]["changed_in"].append(ref)
            continue
        countries, bloc_ids, direct = set(), [], []
        if d.get("intblock"):
            b = blocs.get(d["intblock"], {})
            countries |= set(b.get("includes", []))
            bloc_ids.append(d["intblock"])
            signed = d.get("signed") or b.get("founded")
        else:
            signed = d.get("signed")
            for p in d.get("parties") or []:
                direct.append(p["id"])
                if p["type"] == "intblock":
                    bloc_ids.append(p["id"])
                    countries |= set(blocs.get(p["id"], {}).get("includes", []))
                else:
                    countries.add(p["id"])
        registry[rid] = {
            "id": rid, "ref": ref, "changed_in": [], "raw": d,
            "name": d.get("name") or blocs.get(d.get("intblock"), {}).get("name"),
            "type": d.get("agreement_type"), "status": d.get("status"),
            "signed": signed, "in_force": d.get("in_force"),
            "sy": year(signed), "ey": year(d.get("in_force")),
            "wto": d.get("wto_rta_id"), "wto_ids": set(),
            "countries": countries, "blocs": bloc_ids, "direct": direct,
            "direct_countries": {p for p in direct if p not in bloc_ids},
        }
        # instruments may cite more WTO ids
        for ins in d.get("instruments") or []:
            if ins.get("wto_rta_id"):
                registry[rid]["wto_ids"].add(ins["wto_rta_id"])
        if d.get("wto_rta_id"):
            registry[rid]["wto_ids"].add(d["wto_rta_id"])

all_bloc_names = {}
for _f in glob.glob(f"{ROOT}/data/intblocks/*/*.yaml"):
    _d = load(_f)
    all_bloc_names[_d["id"]] = norm(_d.get("name"))
FORMER_MEMBERS = {"EU": {"GB"}, "EFTA": {"AT", "FI", "SE", "PT", "GB", "DK"}}
registry_blocs = {}
for _f in glob.glob(f"{ROOT}/data/intblocks/*/*.yaml"):
    _d = load(_f)
    registry_blocs[_d["id"]] = [i["id"] for i in (_d.get("includes") or []) if i.get("status") in PARTY_STATUSES]

by_wto = {}
for r in registry.values():
    for w in r["wto_ids"]:
        by_wto.setdefault(w, []).append(r["id"])

# --- DESTA
rows = list(csv.DictReader(open(DESTA_DIR / "desta_list_of_treaties_02_03.csv", encoding="cp1252")))
dyads = list(csv.DictReader(open(DESTA_DIR / "desta_list_of_treaties_02_03_dyads.csv", encoding="cp1252")))
members = {}
for r in rows:
    cs = [code(r[f"c{i}"]) for i in range(1, 92) if r.get(f"c{i}", "").strip()]
    members[r["number"]] = cs
pair_of = {}
for r in dyads:
    pair_of.setdefault(r["number"], set()).add(frozenset((code(r["iso1"]), code(r["iso2"]))))

TRADE_TYPES = {"fta", "customs_union", "pta", "services", "digital", "framework", "other", None}


def candidates(t):
    C = set(members[t["number"]])
    y = int(t["year"]) if t["year"].strip() else None
    e = int(t["entryforceyear"]) if t["entryforceyear"].strip() else None
    out = []
    for r in registry.values():
        if r["type"] in {"preference_scheme", "investment", "trade_relations"}:
            continue
        R = r["countries"]
        if not R:
            continue
        inter = len(C & R)
        if inter < 2:
            continue
        if t["typememb"] == "1":
            # bilateral: both countries must be parties, and the record must be bilateral-ish
            if not C <= R:
                continue
            if len(r["direct"]) != 2 and not (len(R) == 2):
                continue
            if len(r["direct"]) == 2 and r["blocs"]:
                continue  # bloc-country record cannot be a country-country treaty
            score_set = 1.0 if R == C else 0.8
        else:
            if r["blocs"] and r["direct_countries"]:
                # bloc + third country: the third countries must agree exactly
                bloc_members = set()
                for b in r["blocs"]:
                    bloc_members |= set(registry_blocs.get(b, [])) | FORMER_MEMBERS.get(b, set())
                c_res = C - (bloc_members - r["direct_countries"])
                if c_res != r["direct_countries"]:
                    continue
                if len(C & bloc_members) < 2 and bloc_members:
                    continue
                score_set = 0.9
            else:
                jac = inter / len(C | R)
                diff = len(C ^ R)
                if jac < 0.8 and diff > max(1, round(0.2 * len(C | R))):
                    continue
                score_set = round(jac, 2)
        dy = None
        if y and r["sy"]:
            dy = abs(y - r["sy"])
        elif e and r["ey"]:
            dy = abs(e - r["ey"])
        de = abs(e - r["ey"]) if e and r["ey"] else None
        out.append({"id": r["id"], "set": round(score_set, 2), "dy": dy, "de": de})
    return out


results = []
base = [r for r in rows if r["entry_type"] == "base_treaty"]
for t in base:
    C = members[t["number"]]
    wto_ids = wto_by_name.get(norm(t["wto_name"]), []) if t["wto_listed"] == "1" else []
    via_wto = sorted({rid for w in wto_ids for rid in by_wto.get(w, [])})
    cands = candidates(t)
    good = [c for c in cands if (c["dy"] is not None and c["dy"] <= 1) or (c["de"] is not None and c["de"] <= 1)]
    good.sort(key=lambda c: (-c["set"], c["dy"] if c["dy"] is not None else 99, c["de"] if c["de"] is not None else 99))
    res = {"number": t["number"], "name": t["name"], "year": t["year"], "eif": t["entryforceyear"],
           "typememb": t["typememb"], "regioncon": t["regioncon"], "wto_listed": t["wto_listed"],
           "wto_name": t["wto_name"], "wto_ids": wto_ids, "countries": C,
           "via_wto": via_wto, "cands": cands[:12], "good": good[:6]}
    if via_wto:
        if len(via_wto) == 1:
            res["group"], res["match"], res["how"] = "matched", via_wto[0], "wto_name"
        else:
            g = [c["id"] for c in good if c["id"] in via_wto]
            if len(g) >= 1:
                res["group"], res["match"], res["how"] = "matched", g[0], "wto_name+parties"
            else:
                res["group"], res["how"] = "ambiguous", "several records cite the WTO id"
    elif good:
        top = [c for c in good if c["set"] == good[0]["set"] and c["dy"] == good[0]["dy"] and c["de"] == good[0]["de"]]
        if len(top) == 1 and good[0]["set"] >= 0.8:
            res["group"], res["match"], res["how"] = "matched", top[0]["id"], "parties+year"
        elif len(top) == 1:
            res["group"], res["match"], res["how"] = "matched", top[0]["id"], "roster+year"
        else:
            res["group"], res["how"] = "ambiguous", "several records share parties and year"
    elif cands:
        res["group"], res["how"] = "ambiguous", "parties match, year differs"
    else:
        res["group"], res["how"] = "missing", ""
    if res["group"] == "missing" and t["typememb"] != "1":
        acr = re.findall(r"\(([A-Z][A-Za-z/-]+)\)", t["name"])
        acr = [a for x in acr for a in x.split("/")]
        hits = [a for a in acr if a in registry]
        if hits:
            res["group"], res["match"], res["how"] = "matched", hits[0], "acronym"
        else:
            ib = [a for a in acr if a in registry_blocs]
            if ib:
                res["intblock_only"] = ib
    if res["group"] == "missing" and t["typememb"] != "1" and "intblock_only" not in res:
        nm = norm(t["name"])
        ib = [k for k, v in all_bloc_names.items() if v == nm]
        if ib:
            res["intblock_only"] = ib
    if res.get("match"):
        m = registry[res["match"]]
        res["match_ref"] = m["ref"]
        res["match_name"] = m["name"]
        res["match_signed"] = str(m["signed"])
    results.append(res)

for r in results:
    if r["number"] in OVERRIDES and OVERRIDES[r["number"]][0] in registry:
        r["group"], r["match"], r["how"] = "matched", OVERRIDES[r["number"]][0], "hand: " + OVERRIDES[r["number"]][1]
        m = registry[r["match"]]
        r["match_ref"], r["match_name"], r["match_signed"] = m["ref"], m["name"], str(m["signed"])

# one registry record per DESTA treaty: keep the closest year, demote the others
claims = defaultdict(list)
for r in results:
    if r.get("match"):
        claims[r["match"]].append(r)
for rid, rs in claims.items():
    if len(rs) < 2:
        continue
    def key(x, sy=registry[rid]["sy"]):
        dy = abs(int(x["year"]) - sy) if x["year"].strip() and sy else 50
        return (0 if x["how"].startswith("hand") else 1, dy, 0 if x["how"].startswith("wto") else 1,
                0 if x["how"] == "parties+year" else 1)
    rs.sort(key=key)
    for loser in rs[1:]:
        loser["group"] = "ambiguous"
        loser["how"] = f"same record as DESTA {rs[0]['number']} ({rid}); other instrument or duplicate"
        loser["shadow"] = rid
        loser.pop("match")

# pair-level view for bilateral treaties
pairs = set()
for r in registry.values():
    if r["type"] in {"preference_scheme"}:
        continue
    if len(r["direct"]) == 2 and not r["blocs"]:
        pairs.add(frozenset(r["direct"]))
pair_ref = {}
for r in registry.values():
    if len(r["direct"]) == 2 and not r["blocs"]:
        k = frozenset(r["direct"])
        pair_ref.setdefault(k, []).append((r["id"], r["ref"], str(r["signed"]), r["type"]))
for r in results:
    if r["typememb"] == "1" and len(r["countries"]) == 2:
        k = frozenset(r["countries"])
        r["pair_records"] = pair_ref.get(k, [])

def confidence(r: dict) -> str:
    """high: hand match, a single WTO RTA ID, or the same parties and the same year. medium: the
    same parties one year apart, a roster or bloc match, or an acronym. low: ambiguous. none:
    missing. Only high and medium matches may set ``desta_id`` without review."""
    if r["group"] == "missing":
        return "none"
    if r["group"] == "ambiguous":
        return "low"
    how = r.get("how", "")
    if how.startswith("hand") or how == "wto_name":
        return "high"
    if how == "parties+year":
        c = next((c for c in r["good"] if c["id"] == r["match"]), None)
        if c and c["set"] == 1.0 and (c["dy"] == 0 or (c["dy"] is None and c["de"] == 0)):
            return "high"
    return "medium"


for r in results:
    r["countries"] = list(r["countries"])
    r["confidence"] = confidence(r)
if args.json:
    Path(args.json).write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
if args.csv:
    with open(args.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["desta_number", "name", "year", "entryforceyear", "typememb", "regioncon", "wto_listed",
                    "group", "record_id", "record_in", "method", "confidence", "same_parties"])
        for r in results:
            same = r.get("shadow") or ";".join(c["id"] for c in r["cands"][:4]) if r["group"] != "matched" else ""
            w.writerow([r["number"], r["name"], r["year"], r["eif"], r["typememb"], r["regioncon"], r["wto_listed"],
                        r["group"], r.get("match", ""), r.get("match_ref", ""), r.get("how", ""), confidence(r),
                        same])
print(Counter(r["group"] for r in results))
print(Counter((r["group"], r["typememb"]) for r in results))
print(Counter(r.get("match_ref") for r in results if r.get("match")))
