#!/usr/bin/env python3
"""One-off: walk the UNCTAD IIA Navigator BITs into data/trade_agreements/ (catalogue level).

Input is the JSON written by ``parse_unctad_pages.py`` and the same captures TSV. Each treaty
id becomes one result:

- ``unresolved_party``: a party is neither a country in data/countries nor an intblock (the
  former Yugoslavia); skipped;
- ``mapped_existing``: an ``investment`` record with the same two parties and the same signing
  date or year, or the only record of the pair when UNCTAD also lists one treaty for it. The
  record gains ``unctad_iia_id``; it keeps its own dates and notes UNCTAD's when they differ;
- ``new``: a ``verification: catalogue`` record with ``agreement_type: investment``.

Ids: ``<pair>-BIT`` when the pair has one BIT in UNCTAD, otherwise ``<pair>-BIT-<year>``
(``<pair>-BIT-<year><month>`` on a clash); a bloc party (``BLEU``) comes first. The row comes
from the latest capture among the party pages that list the treaty. Status: ``In force`` ->
``in_force``; ``Signed (not in force)`` -> ``signed``; ``Terminated`` -> ``terminated`` with the
termination date as ``ended``, or ``abandoned`` with a note when no entry-into-force date is
given. UNCTAD lists a BLEU treaty under Belgium and Luxembourg; it gets the ``BLEU`` intblock as
one party. See ``openspec/changes/add-unctad-bit-walk``.

Usage: python -I scripts/oneoff/import_unctad_bits.py PARSED_JSON CAPTURES_TSV [--write] [--report JSON]
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
SOURCE = "UNCTAD Investment Policy Hub, International Investment Agreements Navigator (Wayback Machine capture of {d})"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "unctad_iia_id",
    "wikidata_id", "links", "description", "notes", "verification", "last_verified", "provenance",
]
STATUS = {"In force": "in_force", "Signed (not in force)": "signed", "Terminated": "terminated"}
LABEL = {"signed": "date of signature", "in_force": "date of entry into force", "status": "status"}

# UNCTAD economy names that the normalised country-name lookup does not resolve.
MANUAL = {
    "BLEU (Belgium-Luxembourg Economic Union)": ("intblock", "BLEU"),
    "Korea, Republic of": ("country", "KR"), "Korea, Dem. People's Rep. of": ("country", "KP"),
    "Congo": ("country", "CG"), "Congo, Democratic Republic of the": ("country", "CD"),
    "Hong Kong, China SAR": ("country", "HK"), "Macao, China SAR": ("country", "MO"),
    "Taiwan Province of China": ("country", "TW"), "State of Palestine": ("country", "PS"),
    "Lao People's Democratic Republic": ("country", "LA"), "Iran, Islamic Republic of": ("country", "IR"),
    "Moldova, Republic of": ("country", "MD"), "Tanzania, United Republic of": ("country", "TZ"),
    "United Republic of Tanzania": ("country", "TZ"), "Venezuela, Bolivarian Republic of": ("country", "VE"),
    "Bolivia, Plurinational State of": ("country", "BO"), "Micronesia, Federated States of": ("country", "FM"),
    "Côte d'Ivoire": ("country", "CI"), "Türkiye": ("country", "TR"), "Turkey": ("country", "TR"),
    "Czechia": ("country", "CZ"), "Eswatini": ("country", "SZ"), "Cabo Verde": ("country", "CV"),
    "North Macedonia": ("country", "MK"), "Syrian Arab Republic": ("country", "SY"), "Viet Nam": ("country", "VN"),
    "Russian Federation": ("country", "RU"), "United States of America": ("country", "US"),
    "United Kingdom": ("country", "GB"), "Kyrgyzstan": ("country", "KG"), "Gambia": ("country", "GM"),
    "Egypt": ("country", "EG"), "Yemen": ("country", "YE"), "Bahamas": ("country", "BS"),
    "Curaçao": ("country", "CW"), "Saint Kitts and Nevis": ("country", "KN"), "Saint Lucia": ("country", "LC"),
    "Saint Vincent and the Grenadines": ("country", "VC"), "Sao Tome and Principe": ("country", "ST"),
    "Brunei Darussalam": ("country", "BN"), "Timor-Leste": ("country", "TL"), "Slovakia": ("country", "SK"),
}
STOP = r"\b(the|of|and|republic|rep|state|states|federal|democratic|people s|peoples|islamic|kingdom|plurinational|bolivarian|united republic)\b"


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


def resolve(name: str | None, names: dict[str, str]) -> tuple[str, str] | None:
    if not name:
        return None
    if name in MANUAL:
        return MANUAL[name]
    code = names.get(norm(name))
    return ("country", code) if code else None


def iso(value: str) -> str | None:
    if not value:
        return None
    for fmt, out in (("%d/%m/%Y", "%Y-%m-%d"), ("%m/%Y", "%Y-%m"), ("%m-%Y", "%Y-%m"), ("%Y", "%Y")):
        try:
            return datetime.strptime(value, fmt).strftime(out)
        except ValueError:
            pass
    raise ValueError(value)


def capture_date(stamp: str) -> str:
    return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"


def pair_code(parties: list[tuple[str, str]]) -> str:
    blocs = sorted(p[1] for p in parties if p[0] == "intblock")
    return "".join(blocs + sorted(p[1] for p in parties if p[0] == "country"))


def dump(record: dict) -> str:
    ordered = {k: record[k] for k in FIELD_ORDER if k in record}
    return yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=120)


def main(argv: list[str]) -> int:
    parsed = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    urls = {}
    for line in Path(argv[1]).read_text(encoding="utf-8").splitlines():
        cid, stamp, url = line.split("\t")
        urls[cid] = (stamp, url)
    write = "--write" in argv
    report_path = argv[argv.index("--report") + 1] if "--report" in argv else None

    names = country_names()
    economies = dict(parsed["economies"])
    for views in parsed["rows"].values():
        for view in views:
            for cid, name in view["other_parties"]:
                economies.setdefault(str(cid), name)

    registry = {}
    for path in glob.glob(str(ROOT / "data/trade_agreements/*.yaml")):
        record = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        registry[record["id"]] = (Path(path), record)
    taken = set(registry)
    by_pair = collections.defaultdict(list)
    for rid, (_, record) in registry.items():
        if record.get("agreement_type") == "investment" and record.get("parties"):
            by_pair[frozenset(p["id"] for p in record["parties"])].append(rid)

    report = collections.defaultdict(list)
    treaties = []
    for tid, views in parsed["rows"].items():
        views = [v for v in views if v["type"] == "BITs"]
        if not views:
            continue
        best = max(views, key=lambda v: v["capture"])
        cids = {v["page_country"] for v in views} | {c for v in views for c, _ in v["other_parties"]}
        parties, unresolved = [], []
        for cid in sorted(cids):
            hit = resolve(economies.get(str(cid)), names)
            (parties if hit else unresolved).append(hit or (cid, economies.get(str(cid))))
        if unresolved:
            report["unresolved_party"].append((int(tid), best["short_title"], unresolved))
            continue
        if "BLEU" in best["short_title"]:
            # UNCTAD lists a BLEU treaty on the pages of Belgium and Luxembourg; the party is the union.
            parties = [("intblock", "BLEU")] + [p for p in parties if p[1] not in ("BE", "LU", "BLEU")]
        if len(parties) != 2:
            report["party_count"].append((int(tid), best["short_title"], parties))
            continue
        for key in ("status", "signed", "in_force", "terminated"):
            values = {v[key] for v in views}
            if len(values) > 1:
                report["view_conflict"].append((int(tid), best["short_title"], key, sorted(values)))
        treaties.append({"tid": int(tid), "view": best, "parties": parties})

    per_pair = collections.Counter(pair_code(t["parties"]) for t in treaties)
    used, written = set(), []
    for treaty in sorted(treaties, key=lambda t: (pair_code(t["parties"]), t["view"]["signed"][-4:], t["tid"])):
        view, tid, pc = treaty["view"], treaty["tid"], pair_code(treaty["parties"])
        signed, in_force, ended = iso(view["signed"]), iso(view["in_force"]), iso(view["terminated"])
        status = STATUS.get(view["status"])
        notes = []
        if status is None:
            report["unknown_status"].append((tid, view["short_title"], view["status"]))
            continue
        if status == "signed":
            in_force = ended = None
        if status == "in_force":
            if not in_force:
                report["in_force_without_date"].append((tid, view["short_title"]))
                continue
            ended = None
        if status == "terminated":
            if not ended:
                report["terminated_without_date"].append((tid, view["short_title"]))
                continue
            if not in_force:
                status = "abandoned"
                notes.append(f"The IIA Navigator lists the treaty as terminated on {ended} and gives no date of entry into force.")
                ended = None
        stamp, page_url = urls[str(view["page_country"])]
        wayback = f"https://web.archive.org/web/{stamp}/{page_url}"
        source = SOURCE.format(d=capture_date(stamp))

        party_set = frozenset(p[1] for p in treaty["parties"])
        match = None
        for rid in by_pair.get(party_set, []):
            existing = str(registry[rid][1].get("signed", ""))
            if signed and (existing == signed or existing[:4] == signed[:4]):
                match = rid
        if match is None and len(by_pair.get(party_set, [])) == 1 and per_pair[pc] == 1:
            match = by_pair[party_set][0]
        if match:
            used.add(match)
            path, record = registry[match]
            new = {"signed": signed, "in_force": in_force, "status": status}
            diffs = {k: v for k, v in new.items() if v and record.get(k) != v}
            if diffs:
                report["existing_differs"].append((match, tid, {k: (record.get(k), v) for k, v in diffs.items()}))
            if record.get("unctad_iia_id") != tid:
                record = dict(record, unctad_iia_id=tid)
                extra = [f"The UNCTAD IIA Navigator gives {v} as the {LABEL[k]}." for k, v in diffs.items()]
                if extra:
                    record["notes"] = " ".join(filter(None, [record.get("notes"), *extra]))
                provenance = list(record["provenance"])
                provenance.append({"field": "unctad_iia_id", "source": source, "retrieved_at": TODAY, "url": wayback})
                if extra:
                    provenance.append({"field": "notes", "source": source, "retrieved_at": TODAY, "url": wayback})
                record["provenance"] = provenance
                if write:
                    path.write_text(dump(record), encoding="utf-8")
            report["mapped_existing"].append((match, tid))
            continue

        rid = f"{pc}-BIT" if per_pair[pc] == 1 and f"{pc}-BIT" not in taken else f"{pc}-BIT-{(signed or '0000')[:4]}"
        if rid in taken:
            rid = f"{pc}-BIT-{(signed or '0000')[:7].replace('-', '')}"
        if rid in taken:
            report["id_collision"].append((tid, rid))
            continue
        taken.add(rid)
        record = {"id": rid, "name": view["short_title"], "agreement_type": "investment", "status": status}
        record.update({k: v for k, v in (("signed", signed), ("in_force", in_force), ("ended", ended)) if v})
        record["parties"] = [
            {"id": p[1], "type": p[0]} for p in sorted(treaty["parties"], key=lambda p: (p[0] != "intblock", p[1]))
        ]
        record["unctad_iia_id"] = tid
        treaty_url = (f"https://investmentpolicy.unctad.org/international-investment-agreements/treaties/"
                      f"{view['type_slug']}/{tid}/{view['slug']}")
        record["links"] = [{"url": treaty_url, "type": "website"}]
        if notes:
            record["notes"] = " ".join(notes)
        record["verification"] = "catalogue"
        record["last_verified"] = capture_date(stamp)
        fields = ["parties", "status"] + [k for k in ("signed", "in_force", "ended") if k in record]
        fields += ["notes"] if notes else []
        record["provenance"] = [{"field": f, "source": source, "retrieved_at": TODAY, "url": wayback} for f in fields]
        written.append(record)
        if write:
            (ROOT / "data/trade_agreements" / f"{rid}.yaml").write_text(dump(record), encoding="utf-8")

    summary = {
        "treaties": len(parsed["rows"]),
        "bit_treaties": len(treaties),
        "new_records": len(written),
        "new_by_status": dict(collections.Counter(r["status"] for r in written)),
        "existing_not_in_unctad": sorted(r for rids in by_pair.values() for r in rids if r not in used),
        **{k: len(v) for k, v in report.items()},
    }
    print(json.dumps(summary, indent=1))
    if report_path:
        Path(report_path).write_text(json.dumps({"summary": summary, "report": report}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
