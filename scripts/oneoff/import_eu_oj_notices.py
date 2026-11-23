#!/usr/bin/env python3
"""One-off: date EU trade agreements from Official Journal notices and EUR-Lex metadata.

The Council's treaties database blocks automated access. The same facts are published in the
Official Journal as notices in EUR-Lex sector 2 (CELEX ``2YYYYX...``): "Notice concerning the
provisional application of ..." and "Information concerning the entry into force of ...". They
are read from the Publications Office Cellar: the SPARQL endpoint
(``https://publications.europa.eu/webapi/rdf/sparql``) finds each notice, and its work URI,
requested with ``Accept: text/html`` and ``Accept-Language: eng``, returns the text. Notices
from before about 2004 have no English HTML; for those agreements the dates come from the
agreement's own Cellar metadata (signature, entry into force, end of validity).

``PLAN`` lists every date this pass sets, with the notice or agreement CELEX it comes from.

``fetch CACHE_DIR``
    Download the notice texts and the agreement metadata into CACHE_DIR (outside the
    repository) and check that every planned date appears there: a notice must contain the date
    as written in the Official Journal ("1 September 2014"), and an agreement's Cellar metadata
    must list it. Writes ``CACHE_DIR/eu_oj.json``; exits non-zero if a date is not found.

``apply CACHE_DIR [--write]``
    Print, and with ``--write`` make, the changes: ``provisional_application`` and the
    definitive ``in_force`` (removed where the agreement is applied provisionally only), the
    records of the Interim Agreements that preceded the Stabilisation and Association
    Agreements and the EU-Lebanon Association Agreement, and the Europe Agreements with
    Estonia, Latvia and Lithuania. Every date is cited in ``provenance``.

Run with ``python -I``. See ``openspec/changes/add-trade-agreement-provisional-application``.
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
INTBLOCKS = ROOT / "data" / "intblocks"
RETRIEVED = "2026-11-23"
SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
USER_AGENT = "internacia-db one-off (trade agreements registry)"
NOTICE_SOURCE = "EUR-Lex (Official Journal notice)"
CELLAR_SOURCE = "EUR-Lex (Publications Office Cellar)"
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force",
    "provisional_application", "ended", "parties", "intblock", "supersedes", "superseded_by",
    "wto_rta_id", "aric_id", "wikidata_id", "links", "description", "notes", "verification",
    "last_verified", "provenance",
]
LINKED_FIELD_ORDER = ["id", "intblock"]


def eurlex(celex: str) -> str:
    return "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:" + urllib.parse.quote(celex, safe="")


# Dates of existing records. A value is (date, CELEX); a CELEX with an "X" is an Official
# Journal notice, any other CELEX is the agreement's Cellar metadata. ``in_force: None``
# removes the date: the agreement is applied provisionally only.
PLAN: dict[str, dict] = {
    "CETA": {"provisional_application": ("2017-09-21", "22017X0916(02)"), "in_force": None,
             "note": "Applied provisionally from 21 September 2017 (OJ L 238, 16.9.2017, CELEX 22017X0916(02)); it has not "
                     "entered into force."},
    "EUKR": {"provisional_application": ("2011-07-01", "22011X0628(01)"),
             "in_force": ("2015-12-13", "22015X1125(01)")},
    "EUUA": {"provisional_application": ("2016-01-01", "22015X1205(01)"),
             "in_force": ("2017-09-01", "22017X0725(01)"),
             "note": "Other parts of the Association Agreement applied provisionally from 1 November 2014 "
                     "(CELEX 22014X1031(01)); its trade title from 1 January 2016."},
    "EUGE": {"provisional_application": ("2014-09-01", "22014X0830(01)"),
             "in_force": ("2016-07-01", "22016X0618(02)")},
    "EUMD": {"provisional_application": ("2014-09-01", "22014X0830(02)"),
             "in_force": ("2016-07-01", "22016X0618(03)")},
    "EUAM": {"provisional_application": ("2018-06-01", "22018X0517(01)"),
             "in_force": ("2021-03-01", "22021X0216(01)")},
    "EUCL-2002": {"provisional_application": ("2003-02-01", "22002A1230(01)"),
                  "in_force": ("2005-03-01", "22005X0402(01)")},
    "EUCI": {"provisional_application": ("2016-09-03", "22016X1007(01)"), "in_force": None},
    "EUGH": {"provisional_application": ("2016-12-15", "22016X1215(01)"), "in_force": None},
    "EUCENTRALAFRICAEPA": {"provisional_application": ("2014-08-04", "22014X0828(01)"), "in_force": None},
    # Linked records: dates on the record, rosters and per-party dates on the intblock.
    "EUANDEAN": {"provisional_application": ("2013-03-01", "22013X0228(01)"),
                 "in_force": ("2024-11-01", "22024X02804"),
                 "note": "Applied provisionally with Peru from 1 March 2013 (CELEX 22013X0228(01)), with Colombia from "
                         "1 August 2013 (CELEX 22013X0726(01)) and with Ecuador from 1 January 2017 (CELEX "
                         "22016X1229(02)); the agreement and Ecuador's accession protocol entered into force on "
                         "1 November 2024."},
    "EUCENTRALAMERICA": {"provisional_application": ("2013-08-01", "22013X0731(01)"),
                         "in_force": ("2024-05-01", "22024X02157"),
                         "note": "Part IV (trade) applied provisionally with Honduras, Nicaragua and Panama from "
                                 "1 August 2013, with Costa Rica and El Salvador from 1 October 2013 and with Guatemala "
                                 "from 1 December 2013; the Association Agreement entered into force on 1 May 2024."},
    "EUMERCOSUR": {"provisional_application": ("2026-05-01", "22026X00868"),
                   "note": "The Interim Agreement on Trade applies provisionally from 1 May 2026 between the EU and "
                           "Argentina, Brazil, Paraguay and Uruguay (CELEX 22026X00868)."},
    "EUESAEPA": {"provisional_application": ("2012-05-14", "22012X0512(01)"),
                 "note": "Applied provisionally with Madagascar, Mauritius, Seychelles and Zimbabwe from 14 May 2012 "
                         "and with Comoros from 7 February 2019 (CELEX 22019X0722(01)); not in force."},
    "EUSADCEPA": {"provisional_application": ("2016-10-10", "22016X1011(01)"),
                  "note": "Applied provisionally with Botswana, Lesotho, Namibia, South Africa and Eswatini from "
                          "10 October 2016 and with Mozambique from 4 February 2018 (CELEX 22018X0210(01)); not in force."},
}
# Linked records with no Official Journal notice in Cellar: the date is the intblock's
# active_period start, cited to the source the intblock gives for it.
FROM_INTBLOCK: dict[str, str] = {
    "EUCARIFORUMEPA": "Applied provisionally since 29 December 2008; not in force.",
    "EUPACIFICEPA": "Applied provisionally with Papua New Guinea from 20 December 2009, Fiji from 28 July 2014 "
                    "(CELEX 22014X0731(04)), Samoa from 31 December 2018 (CELEX 22019X0116(01)) and Solomon Islands "
                    "from 17 May 2020 (CELEX 22020X0520(01)); not in force.",
}
# Party notes on intblocks: intblock id -> {party: (text, notice)}.
PARTY_NOTES: dict[str, dict[str, tuple[str, str]]] = {
    "EUCENTRALAMERICA": {
        "HN": ("Part IV (trade) applied provisionally from 1 August 2013.", "22013X0731(03)"),
        "NI": ("Part IV (trade) applied provisionally from 1 August 2013.", "22013X0731(01)"),
        "PA": ("Part IV (trade) applied provisionally from 1 August 2013.", "22013X0731(02)"),
        "CR": ("Part IV (trade) applied provisionally from 1 October 2013.", "22013X0928(01)"),
        "SV": ("Part IV (trade) applied provisionally from 1 October 2013.", "22013X0928(02)"),
        "GT": ("Part IV (trade) applied provisionally from 1 December 2013.", "22013X1126(01)"),
    },
    "EUANDEAN": {
        "PE": ("Applied provisionally from 1 March 2013.", "22013X0228(01)"),
        "CO": ("Applied provisionally from 1 August 2013.", "22013X0726(01)"),
    },
}

# Interim Agreements and Europe Agreements added as records of their own: new id ->
# (fields, the record it precedes or follows, CELEX of the agreement, notices).
NEW: dict[str, dict] = {
    "EUAL-2006": {"successor": "EUAL", "partner": "AL", "celex": "22006A0901(01)",
                  "name": "EC - Albania Interim Agreement of 2006", "signed": "2006-06-12",
                  "in_force": ("2006-12-01", "22006X1117(01)"), "ended": "2009-04-01"},
    "EUMK-2001": {"successor": "EUMK", "partner": "MK", "celex": "22001A0504(01)",
                  "name": "EC - North Macedonia Interim Agreement of 2001", "signed": "2001-04-09",
                  "in_force": ("2001-06-01", "22001X0519(01)"), "ended": "2004-04-01"},
    "EUME-2007": {"successor": "EUME", "partner": "ME", "celex": "22007A1228(01)",
                  "name": "EC - Montenegro Interim Agreement of 2007", "signed": "2007-10-15",
                  "in_force": ("2008-01-01", "22007A1228(01)"), "ended": "2010-05-01"},
    "EUBA-2008": {"successor": "EUBA", "partner": "BA", "celex": "22008A0630(01)",
                  "name": "EC - Bosnia and Herzegovina Interim Agreement of 2008", "signed": "2008-06-16",
                  "in_force": ("2008-07-01", "22008X0715(01)"), "ended": "2015-06-01"},
    "EURS-2008": {"successor": "EURS", "partner": "RS", "celex": "22010A0130(02)",
                  "name": "EC - Serbia Interim Agreement of 2008", "signed": "2008-04-29",
                  "in_force": ("2010-02-01", "22010A0130(02)"), "ended": "2013-09-01"},
    "EULB-2002": {"successor": "EULB", "partner": "LB", "celex": "22002A0930(01)",
                  "name": "EC - Lebanon Interim Agreement of 2002", "signed": "2002-06-17",
                  "in_force": ("2003-03-01", "22003X0122(01)"), "ended": "2006-04-01"},
    # The Europe Agreements replaced the 1994 free trade agreements (EUEE, EULV, EULT).
    "EUEE-1995": {"predecessor": "EUEE", "partner": "EE", "celex": "21998A0309(01)",
                  "name": "EC - Estonia Europe Agreement", "signed": "1995-06-12",
                  "in_force": ("1998-02-01", "21998A0309(01)"), "ended": "2004-05-01"},
    "EULV-1995": {"predecessor": "EULV", "partner": "LV", "celex": "21998A0202(01)",
                  "name": "EC - Latvia Europe Agreement", "signed": "1995-06-12",
                  "in_force": ("1998-02-01", "21998A0202(01)"), "ended": "2004-05-01"},
    "EULT-1995": {"predecessor": "EULT", "partner": "LT", "celex": "21998A0220(01)",
                  "name": "EC - Lithuania Europe Agreement", "signed": "1995-06-12",
                  "in_force": ("1998-02-01", "21998A0220(01)"), "ended": "2004-05-01"},
}
# The Stabilisation and Association Agreements and the Lebanon Association Agreement keep their
# record and WTO RTA-IS id, with their own entry into force.
SUCCESSOR_IN_FORCE: dict[str, tuple[str, str]] = {
    "EUAL": ("2009-04-01", "22009X0424(01)"),
    "EUMK": ("2004-04-01", "22004X0323(01)"),
    "EUME": ("2010-05-01", "22010A0429(01)"),
    "EUBA": ("2015-06-01", "22015X0630(01)"),
    "EURS": ("2013-09-01", "22013A1018(01)"),
    "EULB": ("2006-04-01", "22006X0704(01)"),
}

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def written(iso_date: str) -> str:
    """2014-09-01 -> '1 September 2014', as the Official Journal writes dates."""
    d = datetime.strptime(iso_date, "%Y-%m-%d")
    return f"{d.day} {d.strftime('%B')} {d.year}"


def sparql(query: str) -> list[dict]:
    url = SPARQL + "?" + urllib.parse.urlencode({"query": query})
    request = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json",
                                                   "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)["results"]["bindings"]


def work(celex: str) -> dict:
    """Cellar work URI, English title and legal dates of one CELEX number.

    ``work_date_document`` is the date of the instrument; for an agreement whose signature date
    is not recorded separately (the 2001 EC-North Macedonia Interim Agreement) it is the date of
    signature.
    """
    rows = sparql(f'''PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?w ?title ?p ?d WHERE {{
  ?w cdm:resource_legal_id_celex "{celex}"^^<http://www.w3.org/2001/XMLSchema#string> .
  OPTIONAL {{ ?e cdm:expression_belongs_to_work ?w ; cdm:expression_title ?title ;
     cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> }}
  OPTIONAL {{ ?w ?p ?d . FILTER(?p IN (cdm:resource_legal_date_signature, cdm:work_date_document,
     cdm:resource_legal_date_entry-into-force, cdm:resource_legal_date_end-of-validity)) }}
}}''')
    if not rows:
        raise SystemExit(f"{celex}: not found in Cellar")
    dates: dict[str, set[str]] = {}
    for row in rows:
        if "p" in row:
            dates.setdefault(row["p"]["value"].split("#")[-1], set()).add(row["d"]["value"])
    return {"uri": rows[0]["w"]["value"], "title": (rows[0].get("title") or {}).get("value"),
            "dates": {k: sorted(v) for k, v in dates.items()}}


def text(uri: str, cache: Path, celex: str) -> str:
    target = cache / "eu_notices" / (re.sub(r"[()]", "_", celex) + ".html")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(uri, headers={"Accept": "text/html, application/xhtml+xml",
                                                       "Accept-Language": "eng", "User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            target.write_bytes(response.read())
        time.sleep(0.4)
    raw = target.read_text(encoding="utf-8", errors="ignore")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def planned() -> list[tuple[str, str]]:
    """Every (date, CELEX) pair the plan relies on."""
    pairs = []
    for spec in PLAN.values():
        for key in ("provisional_application", "in_force"):
            if spec.get(key):
                pairs.append(spec[key])
    for notes in PARTY_NOTES.values():
        for note, celex in notes.values():
            day = re.search(rf"(\d{{1,2}}) ({MONTHS}) (\d{{4}})", note)
            pairs.append((datetime.strptime(day.group(0), "%d %B %Y").strftime("%Y-%m-%d"), celex))
    for spec in NEW.values():
        pairs.append(spec["in_force"])
        pairs.append((spec["signed"], spec["celex"]))
    pairs.extend(SUCCESSOR_IN_FORCE.values())
    return pairs


def fetch(cache: Path) -> int:
    cache.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict] = {}
    missing = []
    for iso_date, celex in planned():
        if celex not in report:
            report[celex] = work(celex)
            if "X" in celex:
                report[celex]["text"] = text(report[celex]["uri"], cache, celex)
        entry = report[celex]
        if "X" in celex:
            found = written(iso_date) in entry["text"]
        else:
            found = any(iso_date in values for values in entry["dates"].values())
        if not found:
            missing.append(f"{celex}: {iso_date}")
        print(f"{celex} {iso_date} {'ok' if found else 'NOT FOUND'}", file=sys.stderr)
    for spec in NEW.values():
        report.setdefault(spec["celex"], work(spec["celex"]))
    (cache / "eu_oj.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    if missing:
        print("dates not found:", *missing, sep="\n  ", file=sys.stderr)
        return 1
    return 0


def ordered(record: dict) -> dict:
    order = LINKED_FIELD_ORDER + [k for k in FIELD_ORDER if k not in LINKED_FIELD_ORDER] if record.get(
        "intblock") else FIELD_ORDER
    out = {k: record[k] for k in order if k in record}
    out.update({k: v for k, v in record.items() if k not in out})
    return out


def cite(record: dict, field: str, celex: str) -> None:
    source = NOTICE_SOURCE if "X" in celex else CELLAR_SOURCE
    url = eurlex(celex)
    for p in record.setdefault("provenance", []):
        if p.get("field") == field and p.get("url") == url:
            p["retrieved_at"] = RETRIEVED
            return
    record["provenance"].append({"field": field, "source": source, "url": url, "retrieved_at": RETRIEVED})


def add_note(record: dict, note: str) -> None:
    if note not in (record.get("notes") or ""):
        record["notes"] = ((record.get("notes") or "").rstrip() + " " + note).strip()


def load(rid: str) -> dict:
    return yaml.safe_load((REGISTRY / f"{rid}.yaml").read_text(encoding="utf-8"))


def save(record: dict, write: bool) -> None:
    if write:
        (REGISTRY / f"{record['id']}.yaml").write_text(
            yaml.safe_dump(ordered(record), sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")


def drop_applied_clause(record: dict) -> None:
    """Remove the earlier convention's explanation that in_force is the first application date."""
    notes = record.get("notes") or ""
    notes = re.sub(r";? ?in_force is the (?:earlier |start )?[^.;]*?(?:applied|application)[^.]*\.", ".", notes)
    record["notes"] = re.sub(r"\.\.+", ".", notes).strip() or None
    if record["notes"] is None:
        record.pop("notes")


def apply(cache: Path, write: bool) -> int:
    report = json.loads((cache / "eu_oj.json").read_text(encoding="utf-8"))

    for rid, spec in PLAN.items():
        record = load(rid)
        changes = []
        start, celex = spec["provisional_application"]
        if record.get("provisional_application") != start:
            changes.append(f"provisional_application -> {start}")
            record["provisional_application"] = start
        cite(record, "provisional_application", celex)
        if "in_force" in spec:
            if spec["in_force"] is None:
                if record.get("in_force"):
                    changes.append(f"in_force {record['in_force']} removed")
                    record.pop("in_force")
            else:
                value, source = spec["in_force"]
                if str(record.get("in_force") or "") != value:
                    changes.append(f"in_force {record.get('in_force')} -> {value}")
                    record["in_force"] = value
                cite(record, "in_force", source)
        drop_applied_clause(record)
        if spec.get("note"):
            add_note(record, spec["note"])
        record["verification"] = "official"
        record["last_verified"] = RETRIEVED
        print(f"{rid}: " + ("; ".join(changes) or "provenance only"))
        save(record, write)

    for rid, note in FROM_INTBLOCK.items():
        record = load(rid)
        block = yaml.safe_load(next(INTBLOCKS.glob(f"*/{rid}.yaml")).read_text(encoding="utf-8"))
        start = str(block["active_period"]["start"])
        source = next(p for p in block["provenance"] if p.get("field") == "active_period")
        print(f"{rid}: provisional_application -> {start} (intblock)")
        record["provisional_application"] = start
        record.setdefault("provenance", []).append({
            "field": "provisional_application", "source": source["source"], "url": source["url"],
            "retrieved_at": RETRIEVED})
        add_note(record, note)
        record["last_verified"] = RETRIEVED
        save(record, write)

    for block, notes in PARTY_NOTES.items():
        path = next(INTBLOCKS.glob(f"*/{block}.yaml"))
        text_ = path.read_text(encoding="utf-8")
        for party, (note, celex) in notes.items():
            pattern = re.compile(rf"(^- id: {party}\n(?:  .*\n)*?)(?=^- |^\S)", re.M)
            match = pattern.search(text_)
            if not match or "  note:" in match.group(1):
                print(f"{block}/{party}: note not added (missing or already noted)")
                continue
            line = f"  note: {note.rstrip('.')} (CELEX {celex}).\n"
            text_ = text_[:match.end(1)] + line + text_[match.end(1):]
            print(f"{block}/{party}: note")
        if not re.search(r"^- field: includes\n  source: EUR-Lex \(Official Journal notice\)", text_, re.M):
            text_ = text_.rstrip("\n") + (
                f"\n- field: includes\n  source: {NOTICE_SOURCE}\n  retrieved_at: '{RETRIEVED}'\n"
                f"  url: {eurlex(next(iter(notes.values()))[1])}\n")
        text_ = re.sub(r"^last_verified: '[\d-]+'$", f"last_verified: '{RETRIEVED}'", text_, flags=re.M)
        if write:
            path.write_text(text_, encoding="utf-8")

    for rid, spec in NEW.items():
        meta = report[spec["celex"]]
        successor = spec.get("successor")
        predecessor = spec.get("predecessor")
        value, source = spec["in_force"]
        record = {
            "id": rid,
            "name": spec["name"],
            # The Cellar title lists the protocols and final act after " - "; keep the agreement's title.
            "other_names": [{"lang": "en", "name": re.sub(r"\s+", " ", meta["title"]).split(" - ")[0].strip()}]
            if meta.get("title") else [],
            "agreement_type": "fta",
            "status": "superseded" if successor else "terminated",
            "signed": spec["signed"],
            "in_force": value,
            "ended": spec["ended"],
            "parties": [{"id": "EU", "type": "intblock"}, {"id": spec["partner"], "type": "country"}],
            "links": [{"url": eurlex(spec["celex"]), "type": "website"}],
            "verification": "official",
            "last_verified": RETRIEVED,
            "provenance": [],
        }
        if successor:
            record["superseded_by"] = successor
            add_note(record, f"Interim Agreement on trade and trade-related matters, applied until the agreement "
                             f"it anticipated (`{successor}`) entered into force.")
        if predecessor:
            record["supersedes"] = predecessor
            record["notes"] = (
                "Europe Agreement establishing an association, signed on 12 June 1995; it replaced "
                f"the 1994 free trade agreement (`{predecessor}`) on 1 February 1998 and ended on the partner's "
                "accession to the EU on 1 May 2004.")
        if not record["other_names"]:
            record.pop("other_names")
        for field in ("parties", "signed", "name"):
            cite(record, field, spec["celex"])
        cite(record, "in_force", source)
        cite(record, "ended", spec["celex"])
        print(f"{rid}: new ({record['status']}, {spec['signed']} - {value} - {spec['ended']})")
        save(record, write)

        if successor:
            target = load(successor)
            new_value, new_source = SUCCESSOR_IN_FORCE[successor]
            print(f"{successor}: in_force {target.get('in_force')} -> {new_value}; supersedes {rid}")
            target["in_force"] = new_value
            target["supersedes"] = rid
            drop_applied_clause(target)
            add_note(target, f"Its trade provisions applied earlier, from {written(value)}, under the Interim "
                             f"Agreement (`{rid}`), which WTO RTA-IS counts as the start of this RTA.")
            cite(target, "in_force", new_source)
            target["verification"] = "official"
            target["last_verified"] = RETRIEVED
            save(target, write)
        if predecessor:
            target = load(predecessor)
            fta = re.search(r"CELEX ([0-9A-Z]+\(\d+\))", target.get("notes") or "")
            print(f"{predecessor}: superseded by {rid}, ended {target.get('ended')} -> 1998-02-01")
            target["status"] = "superseded"
            target["superseded_by"] = rid
            target["ended"] = "1998-02-01"
            target["notes"] = (
                f"Replaced on 1 February 1998 by the Europe Agreement (`{rid}`); EUR-Lex gives end of validity on "
                "31 January 1998. WTO RTA-IS counts the two as one RTA ending on 1 May 2004.")
            cite(target, "ended", fta.group(1) if fta else spec["celex"])
            target["verification"] = "official"
            target["last_verified"] = RETRIEVED
            save(target, write)
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
