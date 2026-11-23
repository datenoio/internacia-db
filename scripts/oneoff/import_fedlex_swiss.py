#!/usr/bin/env python3
"""One-off: check Switzerland's bilateral trade agreements against Fedlex.

Fedlex, the Swiss federal law publication platform, publishes its data as linked data with
a SPARQL endpoint (``https://fedlex.data.admin.ch/sparqlendpoint``; JOLux ontology). Each
treaty in the Classified Compilation has its SR number (``jolux:historicalLegalId``), the
date of the instrument (``jolux:dateDocument``, the signature date), the date it entered into
force for Switzerland (``jolux:dateEntryInForce``) and, once repealed, the date it ceased to
apply (``jolux:dateNoLongerInForce``, the last day of application).

``PLAN`` lists every record this pass touches and the Fedlex act each date comes from. A
treaty is found by SR number and signature date, or, for one not yet in the compilation, by
its German title and signature date.

``fetch CACHE_DIR``
    Query Fedlex for every planned act, check every planned date against it and write
    ``CACHE_DIR/fedlex.json``; exits non-zero if an act or a date is not found.

``apply CACHE_DIR [--write]``
    Print, and with ``--write`` make, the changes: Fedlex links, dates and provenance on the
    existing records, the Swiss party dates on the EFTA agreements with the Baltic states, and
    four new records (the 1923 customs treaty with Liechtenstein, the 1999 EU-Switzerland
    agriculture agreement, and the Berne Financial Services Agreement and the services mobility
    agreement with the United Kingdom).

Run with ``python -I``.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
SOURCE = "Fedlex (Swiss federal law platform)"
USER_AGENT = "internacia-db one-off (trade agreements registry)"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "wikidata_id", "links", "description", "notes", "instruments", "verification",
    "last_verified", "provenance",
]

# Fedlex acts: key -> (SR number or None, signature date, German title fragment when no SR).
ACTS: dict[str, tuple[str | None, str, str | None]] = {
    "CHCN": ("0.946.292.492", "2013-07-06", None),
    "CHJP": ("0.946.294.632", "2009-02-19", None),
    "CHFOLI": ("0.946.293.142", "1994-01-12", None),
    "CHEE": ("0.946.293.341", "1992-12-21", None),
    "CHLV": ("0.946.294.871", "1992-12-22", None),
    "CHLT": ("0.946.295.161", "1992-11-24", None),
    "EFTAEE": ("0.632.313.341", "1995-12-07", None),
    "EFTALV": ("0.632.314.871.2", "1995-12-07", None),
    "EFTALT": ("0.632.315.162", "1995-12-07", None),
    "CHLI": ("0.631.112.514", "1923-03-29", None),
    "EUCH-AGRI": ("0.916.026.81", "1999-06-21", None),
    "EUCH-AGRI-LI": ("0.916.026.812", "2007-09-27", None),
    "CHGB-MOBILITY": ("0.946.293.671.2", "2020-12-14", None),
    "CHGB-FSA": (None, "2023-12-21", "gegenseitige Anerkennung im Bereich der Finanzdienstleistungen"),
}

# Existing records: dates Fedlex gives (signed, in_force, ended). ``ended`` is the day after
# Fedlex's last day of application, the registry's convention.
EXISTING: dict[str, dict] = {
    "CHCN": {"signed": "2013-07-06", "in_force": "2014-07-01"},
    "CHJP": {"signed": "2009-02-19", "in_force": "2009-09-01"},
    "CHFOLI": {"signed": "1994-01-12", "in_force": "1995-03-01"},
    "CHEE": {"signed": "1992-12-21", "in_force": "1994-03-02", "ended": "1997-10-01", "superseded_by": "EFTAEE"},
    "CHLV": {"signed": "1992-12-22", "in_force": "1994-03-01", "ended": "1997-08-01", "superseded_by": "EFTALV"},
    "CHLT": {"signed": "1992-11-24", "in_force": "1994-03-01", "ended": "1997-08-01", "superseded_by": "EFTALT"},
}
# EFTA agreements with the Baltic states: Switzerland's own entry into force.
SWISS_PARTY: dict[str, str] = {"EFTAEE": "1997-10-01", "EFTALV": "1997-08-01", "EFTALT": "1997-08-01"}

GOVUK_FSA = "https://www.gov.uk/government/publications/the-berne-financial-services-agreement"
NEW: dict[str, dict] = {
    "CHLI": {
        "name": "Switzerland-Liechtenstein Customs Treaty",
        "agreement_type": "customs_union", "status": "in_force",
        "signed": "1923-03-29", "in_force": "1924-01-01",
        "parties": [{"id": "CH", "type": "country"}, {"id": "LI", "type": "country"}],
        "description": "Treaty joining the Principality of Liechtenstein to the Swiss customs territory, signed on "
                       "29 March 1923 and in force since 1 January 1924; the two countries form one customs territory.",
        "notes": "Supplemented by an agreement and an additional protocol of 2 November 1994 (SR 0.631.112.514.6 "
                 "and 0.631.112.514.2), in force in 1995.",
    },
    "EUCH-AGRI": {
        "name": "EU-Switzerland Agreement on Trade in Agricultural Products",
        "agreement_type": "pta", "status": "in_force",
        "signed": "1999-06-21", "in_force": "2002-06-01",
        "parties": [{"id": "EU", "type": "intblock"}, {"id": "CH", "type": "country"},
                    {"id": "LI", "type": "country", "in_force": "2007-09-27",
                     "note": "Included by the Additional Agreement of 27 September 2007 (SR 0.916.026.812)."}],
        "description": "Agreement of the first package of bilateral agreements between Switzerland and the EU "
                       "(Bilaterals I), signed on 21 June 1999 and in force since 1 June 2002, with tariff concessions "
                       "on agricultural products and the mutual recognition of rules on veterinary, plant health, "
                       "organic farming and wine and spirit products.",
        "notes": "One of the seven Bilaterals I agreements, which entered into force together on 1 June 2002. Liechtenstein "
                 "was included by an Additional Agreement between Switzerland, Liechtenstein and the European Community, "
                 "in force on signature on 27 September 2007.",
    },
    "CHGB-MOBILITY": {
        "name": "UK-Switzerland Services Mobility Agreement",
        "agreement_type": "services", "status": "in_force",
        "signed": "2020-12-14", "in_force": "2021-01-01",
        "parties": [{"id": "CH", "type": "country"}, {"id": "GB", "type": "country"}],
        "description": "Temporary agreement between Switzerland and the United Kingdom on the mobility of service "
                       "suppliers, signed on 14 December 2020 and in force since 1 January 2021.",
        "notes": "Concluded for a limited period; Fedlex lists an earlier and a current version under SR 0.946.293.671.2, "
                 "the current one in force.",
    },
    "CHGB-FSA": {
        "name": "Berne Financial Services Agreement",
        "agreement_type": "services", "status": "in_force",
        "signed": "2023-12-21", "in_force": "2026-01-01",
        "parties": [{"id": "CH", "type": "country"}, {"id": "GB", "type": "country"}],
        "description": "Agreement between the United Kingdom and Switzerland on mutual recognition in financial "
                       "services, signed on 21 December 2023 and in force since 1 January 2026. It uses outcomes-based "
                       "mutual recognition of domestic regulation to open cross-border trade in financial services to "
                       "wholesale and sophisticated clients.",
        "notes": "The UK and Switzerland concluded an enhanced free trade agreement (`CHGB-2026`) in July 2026; "
                 "wholesale financial services remain covered by this agreement.",
        "links": [GOVUK_FSA],
    },
}


def sparql(query: str) -> list[dict]:
    url = SPARQL + "?" + urllib.parse.urlencode({"query": query})
    request = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json",
                                                   "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)["results"]["bindings"]


def find(sr: str | None, signed: str, title: str | None) -> dict:
    """The consolidated act with this SR number (or title fragment) and signature date."""
    match = f'jolux:historicalLegalId "{sr}"' if sr else ""
    title_filter = f'FILTER(CONTAINS(?t, "{title}"))' if title else ""
    rows = sparql(f'''PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
SELECT DISTINCT ?a ?lang ?t ?eif ?end ?status WHERE {{
  ?a a jolux:ConsolidationAbstract ; jolux:dateDocument "{signed}"^^<http://www.w3.org/2001/XMLSchema#date> ;
     jolux:isRealizedBy ?e . {"?a " + match + " ." if sr else ""}
  ?e jolux:language ?lang ; jolux:title ?t . {title_filter}
  OPTIONAL {{ ?a jolux:dateEntryInForce ?eif }} OPTIONAL {{ ?a jolux:dateNoLongerInForce ?end }}
  OPTIONAL {{ ?a jolux:inForceStatus ?status }}
}}''')
    if not rows:
        raise SystemExit(f"Fedlex act not found: SR {sr} signed {signed} {title or ''}")
    # Several versions can share an SR number; prefer the one in force.
    rows.sort(key=lambda r: (not r.get("status", {}).get("value", "").endswith("/0"), r["a"]["value"]))
    uri = rows[0]["a"]["value"]
    titles = {r["lang"]["value"].rsplit("/", 1)[-1]: " ".join(r["t"]["value"].split())
              for r in rows if r["a"]["value"] == uri}
    first = rows[0]
    return {
        "uri": uri,
        "url": uri.replace("https://fedlex.data.admin.ch/", "https://www.fedlex.admin.ch/") + "/de",
        "sr": sr,
        "signed": signed,
        "in_force": (first.get("eif") or {}).get("value"),
        "last_day": (first.get("end") or {}).get("value"),
        # inForceStatus .../0 is in force, .../3 no longer in force; acts not yet consolidated have none.
        "no_longer_in_force": first.get("status", {}).get("value", "").endswith("/3"),
        "titles": titles,
    }


def day_after(iso_date: str) -> str:
    return (date.fromisoformat(iso_date) + timedelta(days=1)).isoformat()


def fetch(cache: Path) -> int:
    cache.mkdir(parents=True, exist_ok=True)
    report = {key: find(*spec) for key, spec in ACTS.items()}
    problems = []
    for rid, spec in EXISTING.items():
        act = report[rid]
        if act["in_force"] != spec["in_force"]:
            problems.append(f"{rid}: in_force {spec['in_force']} != Fedlex {act['in_force']}")
        # Fedlex gives either the first day without application (the bilateral Baltic agreements)
        # or the last day of application (the EFTA ones); the registry's ``ended`` is the former.
        if "ended" in spec and spec["ended"] not in {act["last_day"], act["last_day"] and day_after(act["last_day"])}:
            problems.append(f"{rid}: ended {spec['ended']} != Fedlex last day {act['last_day']}")
    for rid, value in SWISS_PARTY.items():
        if report[rid]["in_force"] != value:
            problems.append(f"{rid}: CH in_force {value} != Fedlex {report[rid]['in_force']}")
    for rid, spec in NEW.items():
        act = report[rid]
        if act["in_force"] != spec["in_force"] or act["no_longer_in_force"]:
            problems.append(f"{rid}: in_force {spec['in_force']} != Fedlex {act['in_force']} (no longer in force: "
                            f"{act['no_longer_in_force']})")
    li = report["EUCH-AGRI-LI"]["in_force"]
    if li != NEW["EUCH-AGRI"]["parties"][2]["in_force"]:
        problems.append(f"EUCH-AGRI: Liechtenstein in_force != Fedlex {li}")
    (cache / "fedlex.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    for line in problems:
        print(line, file=sys.stderr)
    print(f"{len(report)} acts, {len(problems)} problem(s)", file=sys.stderr)
    return 1 if problems else 0


def ordered(record: dict) -> dict:
    out = {k: record[k] for k in FIELD_ORDER if k in record}
    out.update({k: v for k, v in record.items() if k not in out})
    return out


def cite(record: dict, field: str, url: str, source: str = SOURCE) -> None:
    for p in record.setdefault("provenance", []):
        if p.get("field") == field and p.get("url") == url:
            p["retrieved_at"] = RETRIEVED
            return
    record["provenance"].append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})


def link(record: dict, url: str) -> None:
    links = record.setdefault("links", [])
    if all(entry.get("url") != url for entry in links):
        links.insert(0, {"url": url, "type": "website"})


def add_note(record: dict, note: str) -> None:
    if note not in (record.get("notes") or ""):
        record["notes"] = ((record.get("notes") or "").rstrip() + " " + note).strip()


def apply(cache: Path, write: bool) -> int:
    report = json.loads((cache / "fedlex.json").read_text(encoding="utf-8"))

    def save(record: dict) -> None:
        if write:
            (REGISTRY / f"{record['id']}.yaml").write_text(
                yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")

    for rid, spec in EXISTING.items():
        record = yaml.safe_load((REGISTRY / f"{rid}.yaml").read_text(encoding="utf-8"))
        act = report[rid]
        changes = []
        for field in ("signed", "in_force", "ended"):
            if field in spec and str(record.get(field) or "") != spec[field]:
                changes.append(f"{field} {record.get(field)} -> {spec[field]}")
                if field == "in_force" and record.get(field):
                    add_note(record, f"WTO RTA-IS gives entry into force on {record[field]}; Fedlex gives "
                                     f"{spec[field]} for Switzerland.")
                if field == "ended" and record.get(field):
                    add_note(record, f"WTO RTA-IS gives {record[field]} as the end date, the date the EFTA "
                                     f"agreement entered into force for the partner.")
                record[field] = spec[field]
            if field in spec:
                cite(record, field, act["url"])
        if spec.get("superseded_by"):
            record["status"] = "superseded"
            record["superseded_by"] = spec["superseded_by"]
            add_note(record, f"Replaced for Switzerland by the EFTA agreement (`{spec['superseded_by']}`), in force "
                             f"for Switzerland from {spec['ended']} (Fedlex SR {report[spec['superseded_by']]['sr']}).")
        if act["titles"].get("DEU"):
            others = record.setdefault("other_names", [])
            title = act["titles"]["DEU"]
            if all(o.get("name") != title for o in others):
                others.append({"lang": "de", "name": title})
        link(record, act["url"])
        cite(record, "parties", act["url"])
        record["verification"] = "official"
        record["last_verified"] = RETRIEVED
        print(f"{rid}: " + ("; ".join(changes) or "Fedlex link and provenance"))
        save(record)

    for rid, value in SWISS_PARTY.items():
        record = yaml.safe_load((REGISTRY / f"{rid}.yaml").read_text(encoding="utf-8"))
        act = report[rid]
        parties = record["parties"]
        swiss = next((p for p in parties if p["id"] == "CH"), None)
        if swiss is None:
            swiss = {"id": "CH", "type": "country"}
            parties.append(swiss)
            print(f"{rid}: Switzerland added as a party")
        swiss["in_force"] = value
        add_note(record, f"Fedlex (SR {act['sr']}) gives Switzerland's entry into force on {value}.")
        if all(p["id"] != "NO" for p in parties):
            add_note(record, "The Fedlex title names the EFTA States as parties; Norway, an EFTA State at signature, "
                             "is not listed here and was not checked.")
        link(record, act["url"])
        cite(record, "parties", act["url"])
        record["last_verified"] = RETRIEVED
        print(f"{rid}: CH in_force {value}")
        save(record)

    for rid, spec in NEW.items():
        act = report[rid]
        record = {"id": rid, "name": spec["name"]}
        record["other_names"] = [{"lang": lang.lower()[:2], "name": act["titles"][lang]}
                                 for lang in ("DEU", "FRA") if act["titles"].get(lang)]
        for key in ("agreement_type", "status", "signed", "in_force", "parties", "description", "notes"):
            record[key] = spec[key]
        record["links"] = [{"url": act["url"], "type": "website"}]
        for extra in spec.get("links", []):
            record["links"].append({"url": extra, "type": "website"})
        record["verification"] = "official"
        record["last_verified"] = RETRIEVED
        record["provenance"] = []
        for field in ("parties", "signed", "in_force", "name"):
            cite(record, field, act["url"])
        if rid == "EUCH-AGRI":
            cite(record, "parties", report["EUCH-AGRI-LI"]["url"])
        for extra in spec.get("links", []):
            cite(record, "description", extra, "UK Government")
        print(f"{rid}: new {spec['agreement_type']} {spec['signed']} / {spec['in_force']}")
        save(record)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"fetch", "apply"}:
        print(__doc__)
        return 2
    cache = Path(argv[1])
    if argv[0] == "fetch":
        return fetch(cache)
    return apply(cache, "--write" in argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
