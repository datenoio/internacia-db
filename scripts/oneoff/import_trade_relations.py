#!/usr/bin/env python3
"""One-off: walk bilateral trade relations agreements into data/trade_agreements/.

Inputs: the UNTS rows written by ``parse_untc_details.py`` and one JSON file per national
treaty database (``AU.json``, ``CA.json``, ``CH.json``, ``NL.json``: ``{"source", "agreements":
[{"reporter", "partner_alpha2", "title", "signed", "in_force", "status", "ended", "url",
"unts_registration", "doubtful", ...}]}``). All of them are untrusted data: keep them outside
the repository and run this script with ``python -I``.

Each agreement gets one result, checked in this order:

- ``existing``: a registry record with the same two parties and a signing date in the same
  year (or the same UNTS registration) already exists; it gains ``unts_registration``;
- ``official``: a national database lists it (status from that database, matched to a UNTS
  row by registration number or by parties and signing year when there is one);
- ``catalogue``: UNTS only, concluded in 2000 or later, and neither party a current EU member
  state; ``in_force`` when the UNTS gives an entry-into-force date, else ``signed``;
- ``candidate``: any other UNTS-only row; reported, not written;
- ``skipped``: a party is not in data/countries (USSR, Czechoslovakia, Yugoslavia, GDR), the
  row is marked doubtful by the national database walk, or its status is unknown.

Ids: the earliest agreement of a pair takes ``<pair>-TRA`` and each further one
``<pair>-TRA-<year>`` (``<pair>-TRA-<year><month>`` on a clash), as for investment treaties; a
bloc party (``BENELUX``, ``BLEU``) comes first. See ``openspec/changes/add-trade-relations-walk``.

Usage: python -I scripts/oneoff/import_trade_relations.py UNTS_JSON NATDB_DIR [--write] [--report JSON]
"""

import collections
import glob
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-11-23"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "unctad_iia_id",
    "unts_registration", "wikidata_id", "links", "description", "notes", "verification", "last_verified",
    "provenance",
]
UNTS_SOURCE = "United Nations Treaty Collection, United Nations Treaty Series"
NATDB = {
    "AU": "Australian Government Department of Foreign Affairs and Trade, Australian Treaties Database",
    "CA": "Global Affairs Canada, Canada Treaty Information",
    "CH": "Swiss Federal Chancellery, Fedlex (classified compilation of federal law)",
    "NL": "Government of the Netherlands, Treaty Database (Verdragenbank)",
}
MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
     "november", "december"], 1)}
MANUAL = {
    "United Kingdom of Great Britain and Northern Ireland": "GB", "United States of America": "US",
    "Russian Federation": "RU", "Republic of Korea": "KR", "Korea (Republic of)": "KR",
    "Democratic People's Republic of Korea": "KP", "Iran (Islamic Republic of)": "IR",
    "Venezuela (Bolivarian Republic of)": "VE", "Bolivia (Plurinational State of)": "BO",
    "Republic of Moldova": "MD", "United Republic of Tanzania": "TZ", "Lao People's Democratic Republic": "LA",
    "Syrian Arab Republic": "SY", "Viet Nam": "VN", "Türkiye": "TR", "Turkey": "TR", "Czech Republic": "CZ",
    "Czechia": "CZ", "Slovakia": "SK", "North Macedonia": "MK", "The former Yugoslav Republic of Macedonia": "MK",
    "Côte d'Ivoire": "CI", "Congo": "CG", "Democratic Republic of the Congo": "CD", "Zaire": "CD",
    "Egypt": "EG", "United Arab Republic": "EG", "Ceylon": "LK", "Burma": "MM", "Myanmar": "MM",
    "Kampuchea": "KH", "Democratic Kampuchea": "KH", "Dahomey": "BJ", "Upper Volta": "BF",
    "Swaziland": "SZ", "Eswatini": "SZ", "Cabo Verde": "CV", "Cape Verde": "CV", "Holy See": "VA",
    "State of Palestine": "PS", "Micronesia (Federated States of)": "FM", "Netherlands (Kingdom of the)": "NL",
    "Netherlands": "NL", "Germany": "DE", "Germany, Federal Republic of": "DE", "Federal Republic of Germany": "DE",
}
HISTORICAL = re.compile(r"soviet|czechoslovak|yugoslavia|german democratic|serbia and montenegro|zanzibar|"
                        r"united arab republic.*syria|south vietnam|republic of viet-nam|tanganyika", re.I)
# Titles that the UNTS subject term "Trade" catches but that are not trade relations agreements.
OFF_TOPIC = re.compile(r"electricity|energy|digital|cooperation office|transfer of technology|technical|"
                       r"military|exhibition|training|statistic|textile|clothing|apparel|cereal|meat|beef|sugar|"
                       r"steel|coal|timber|fisher|tobacco|wine|spirits|cotton|rice|wheat|grain|coffee|cocoa|"
                       r"tariffs and trade|tokyo round|multilateral trade negotiations|trade (mission|representation|"
                       r"delegation|office)s?\b|commercial (mission|representation|office)s?\b|free trade|"
                       r"customs union|partnership|association|investment|payments?\b|clearing", re.I)
# A UNTS-only record must also look like a trade relations agreement itself, not an MoU, a side
# letter, a framework or a sector instrument.
UNTS_ONLY_TITLE = re.compile(r"^(agreement|treaty|trade agreement|economic and trade agreement|"
                             r"trade and economic (co-?operation )?agreement|long[- ]term trade agreement)\b", re.I)
UNTS_ONLY_TOPIC = re.compile(r"\btrade\b|\bcommerc|economic and trade|trade and economic", re.I)
UNTS_ONLY_NOT = re.compile(r"memorandum|protocol|exchange of|framework|working|promotion|technology|mechanism|"
                           r"defen[cs]e|preferential|liberali[sz]|ministerial|joint (committee|commission)|"
                           r"mutual|health|concerning the|remed|anti-?dumping|safeguard", re.I)
STOP = r"\b(the|of|and|republic|rep|state|states|federal|democratic|people s|peoples|islamic|kingdom|plurinational|bolivarian|united republic|government)\b"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(re.sub(STOP, " ", text).split())


def country_names() -> dict[str, str]:
    names: dict[str, str] = {}
    for path in glob.glob(str(ROOT / "data/countries/*.yaml")):
        record = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        candidates = [record.get("name"), record.get("official_name")]
        candidates += [n.get("name") for n in record.get("other_names") or [] if n.get("id") == "en"]
        candidates += [c.get("name") if isinstance(c, dict) else c for c in record.get("common_names") or []]
        for candidate in candidates:
            if candidate:
                names.setdefault(norm(candidate), record["code"])
    return names


def resolve(name: str, names: dict[str, str]) -> str | None:
    if name in MANUAL:
        return MANUAL[name]
    if HISTORICAL.search(name):
        return None
    if re.search(r"belg.*luxemb", name, re.I):
        return "BLEU"
    return names.get(norm(name))


def unts_date(value: str) -> str | None:
    try:
        return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def eif_date(text: str) -> str | None:
    """First full date in the UNTS entry-into-force text ('1 July 1964 by signature')."""
    match = re.search(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", text or "")
    if match and match.group(2).lower() in MONTHS:
        return f"{match.group(3)}-{MONTHS[match.group(2).lower()]:02d}-{int(match.group(1)):02d}"
    return None


def short_title(title: str) -> str:
    title = re.sub(r"\s*\((with|together with)[^)]*\)", "", title)
    title = re.sub(r"[.,]?\s*(Signed|Done|Concluded) at .*$", "", title, flags=re.I)
    return title.strip().rstrip(".").strip()


BLOCS = {"BLEU", "BENELUX"}


def pair_code(parties: list[str]) -> str:
    blocs = sorted(p for p in parties if p in BLOCS)
    return "".join(blocs + sorted(p for p in parties if p not in BLOCS))


def dump(record: dict) -> str:
    return yaml.safe_dump({k: record[k] for k in FIELD_ORDER if k in record}, sort_keys=False,
                          allow_unicode=True, width=120)


def main(argv: list[str]) -> int:
    unts_rows = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    natdb_rows = []
    for path in sorted(Path(argv[1]).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data.get("agreements", []):
            natdb_rows.append(dict(row, _source=data.get("source"), _db=path.stem))
    write = "--write" in argv
    report_path = argv[argv.index("--report") + 1] if "--report" in argv else None
    names = country_names()
    eu = {i["id"] for i in yaml.safe_load((ROOT / "data/intblocks/economic/EU.yaml").read_text())["includes"]
          if i.get("status") in ("member", "founding_member") and not i.get("left")}

    registry = {}
    for path in glob.glob(str(ROOT / "data/trade_agreements/*.yaml")):
        record = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        registry[record["id"]] = (Path(path), record)
    taken = set(registry)
    by_pair = collections.defaultdict(list)
    for rid, (_, record) in registry.items():
        if record.get("parties"):
            by_pair[frozenset(p["id"] for p in record["parties"])].append(rid)
    by_unts = {r.get("unts_registration"): rid for rid, (_, r) in registry.items() if r.get("unts_registration")}
    report = collections.defaultdict(list)

    # UNTS rows: resolve parties.
    unts = []
    for row in unts_rows:
        if OFF_TOPIC.search(row["title"]):
            report["unts_off_topic"].append((row["registration"], row["title"][:100]))
            continue
        parties = [resolve(p, names) for p in row["participants"]]
        if len(row["participants"]) != 2 or None in parties or len(set(parties)) != 2:
            report["unts_unresolved"].append((row["registration"], row["participants"], row["title"][:100]))
            continue
        unts.append(dict(row, parties=parties, signed=unts_date(row["date_of_conclusion"]),
                         in_force=eif_date(row["eif"])))
    unts_by_reg = {r["registration"]: r for r in unts}
    unts_by_pair = collections.defaultdict(list)
    for row in unts:
        unts_by_pair[frozenset(row["parties"])].append(row)

    # Agreements to consider: national rows first, then UNTS rows nobody claimed.
    items, claimed = [], set()
    for row in natdb_rows:
        if re.search(r"belg.*luxemb|bleu\b|uebl\b", row.get("partner_name") or "", re.I):
            row["partner_alpha2"] = "BLEU"
        partner = row.get("partner_alpha2")
        if not partner or row.get("doubtful") or row.get("status") not in ("in_force", "terminated", "not_yet_in_force"):
            report["natdb_skipped"].append((row["_db"], row.get("partner_name"), row.get("title", "")[:90],
                                            row.get("status"), bool(row.get("doubtful"))))
            continue
        partner = row.get("partner_alpha2")
        reporter = row["reporter"]
        if set(row.get("reporter_parties") or []) >= {"NL", "BE", "LU"}:
            # The Dutch database records Benelux, or the Netherlands with the BLEU, as the party.
            reporter = "BENELUX"
        parties = [reporter, partner]
        match = unts_by_reg.get(row.get("unts_registration") or "")
        if match is None:
            same = [u for u in unts_by_pair.get(frozenset(parties), [])
                    if row.get("signed") and u["signed"] and u["signed"][:4] == str(row["signed"])[:4]
                    and u["registration"] not in claimed]
            match = same[0] if len(same) == 1 else None
        if match:
            claimed.add(match["registration"])
        items.append({"kind": "official", "parties": parties, "nat": row, "unts": match})
    for row in unts:
        if row["registration"] in claimed:
            continue
        year = int((row["signed"] or "0000")[:4])
        title = short_title(row["title"])
        looks_right = UNTS_ONLY_TITLE.search(title) and UNTS_ONLY_TOPIC.search(title) and not UNTS_ONLY_NOT.search(title)
        if year >= 2000 and not (set(row["parties"]) & eu) and looks_right:
            items.append({"kind": "catalogue", "parties": row["parties"], "nat": None, "unts": row})
        else:
            report["candidate"].append((row["registration"], row["parties"], row["signed"], short_title(row["title"])))

    # Existing records.
    fresh = []
    for item in items:
        nat, un = item["nat"], item["unts"]
        signed = (nat or {}).get("signed") or (un or {}).get("signed")
        existing = by_unts.get((un or {}).get("registration"))
        if existing is None:
            for rid in by_pair.get(frozenset(item["parties"]), []):
                r = registry[rid][1]
                kind = r.get("agreement_type")
                if not signed or kind == "investment":
                    continue  # a BIT signed in the same year is a different instrument
                same_year = str(r.get("signed", ""))[:4] == str(signed)[:4]
                if (kind == "trade_relations" and same_year) or str(r.get("signed", "")) == str(signed):
                    existing = rid
        if existing:
            path, record = registry[existing]
            report["existing"].append((existing, (un or {}).get("registration"), (nat or {}).get("title")))
            if un and not record.get("unts_registration") and record.get("agreement_type") == "trade_relations":
                record = dict(record, unts_registration=un["registration"])
                record["provenance"] = list(record["provenance"]) + [{
                    "field": "unts_registration", "source": UNTS_SOURCE, "retrieved_at": TODAY, "url": un["url"]}]
                if write:
                    path.write_text(dump(record), encoding="utf-8")
            continue
        item["signed"] = signed
        fresh.append(item)

    per_pair = collections.Counter(pair_code(i["parties"]) for i in fresh)
    for item in fresh:
        pc = pair_code(item["parties"])
        if any(rid.startswith(pc + "-TRA") for rid in taken):
            per_pair[pc] += 1
    written = []
    for item in sorted(fresh, key=lambda i: (pair_code(i["parties"]), str(i["signed"]))):
        nat, un, pc = item["nat"], item["unts"], pair_code(item["parties"])
        year = str(item["signed"] or "0000")[:4]
        # As for investment treaties: the earliest agreement of a pair takes -TRA, a further one -TRA-<year>.
        rid = f"{pc}-TRA" if f"{pc}-TRA" not in taken else f"{pc}-TRA-{year}"
        if rid in taken:
            rid = f"{pc}-TRA-{str(item['signed'] or '000000')[:7].replace('-', '')}"
        if rid in taken:
            report["id_collision"].append((rid, (un or {}).get("registration"), (nat or {}).get("title")))
            continue
        taken.add(rid)
        title = (nat or {}).get("title") or short_title(un["title"])
        record = {"id": rid, "name": title, "agreement_type": "trade_relations"}
        provenance, notes, links = [], [], []
        if nat:
            status = {"in_force": "in_force", "terminated": "terminated", "not_yet_in_force": "signed"}[nat["status"]]
            record["status"] = status
            for key in ("signed", "in_force", "ended"):
                value = nat.get(key) or (un or {}).get(key) if key != "ended" else nat.get("ended")
                if status == "signed" and key in ("in_force", "ended"):
                    continue
                if status == "in_force" and key == "ended":
                    continue
                if value:
                    record[key] = str(value)
            if status == "terminated" and not record.get("ended"):
                report["terminated_without_end"].append((rid, title))
                taken.discard(rid)
                continue
            if status in ("in_force", "terminated") and not record.get("in_force"):
                report["no_in_force_date"].append((rid, title))
                taken.discard(rid)
                continue
            source = nat.get("_source") or NATDB[nat["_db"]]
            for field in ["parties", "status"] + [k for k in ("signed", "in_force", "ended") if k in record]:
                provenance.append({"field": field, "source": source, "retrieved_at": TODAY, "url": nat.get("url")})
            if nat.get("url"):
                links.append({"url": nat["url"], "type": "website"})
            if nat.get("note"):
                notes.append(str(nat["note"]).rstrip(".") + ".")
            record["verification"] = "official"
        else:
            record["status"] = "in_force" if un["in_force"] else "signed"
            if un["signed"]:
                record["signed"] = un["signed"]
            if un["in_force"]:
                record["in_force"] = un["in_force"]
            notes.append("Status from the UN Treaty Series registration only: the UNTS records no termination, "
                         "and no party treaty database was checked.")
            record["verification"] = "catalogue"
            for field in ["parties", "status"] + [k for k in ("signed", "in_force") if k in record] + ["notes"]:
                provenance.append({"field": field, "source": UNTS_SOURCE, "retrieved_at": TODAY, "url": un["url"]})
        record["parties"] = [{"id": p, "type": "intblock" if p in BLOCS else "country"}
                             for p in sorted(item["parties"], key=lambda p: (p not in BLOCS, p))]
        if un:
            record["unts_registration"] = un["registration"]
            links.append({"url": un["url"], "type": "website"})
            if nat:
                provenance.append({"field": "unts_registration", "source": UNTS_SOURCE, "retrieved_at": TODAY,
                                   "url": un["url"]})
        if links:
            record["links"] = links
        if notes:
            record["notes"] = " ".join(notes)
        record["last_verified"] = TODAY
        record["provenance"] = provenance
        written.append(record)
        if write:
            (ROOT / "data/trade_agreements" / f"{rid}.yaml").write_text(dump(record), encoding="utf-8")

    summary = {
        "unts_rows": len(unts_rows), "unts_resolved": len(unts), "natdb_rows": len(natdb_rows),
        "written": len(written),
        "written_by": dict(collections.Counter((r["verification"], r["status"]) for r in written).most_common()),
        **{k: len(v) for k, v in report.items()},
    }
    summary["written_by"] = {f"{k[0]}/{k[1]}": v for k, v in summary["written_by"].items()}
    print(json.dumps(summary, indent=1))
    if report_path:
        report["written_records"] = [(r["id"], r["verification"], r["status"], r.get("signed"), r["name"][:110])
                                     for r in written]
        Path(report_path).write_text(json.dumps({"summary": summary, "report": report}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
