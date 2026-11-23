#!/usr/bin/env python3
"""One-off: match the EDIT treaty list to data/trade_agreements/ and link the treaty texts.

EDIT (Electronic Database of Investment Treaties, World Trade Institute, https://edit.wti.org/)
lists 4,271 documents (2026-11-23): 3,462 BITs, 664 other investment agreements ("OIIA":
treaties with investment provisions such as FTAs, framework agreements and plurilateral
investment treaties) and 145 model treaties. Input is the directory written by
``fetch_edit.py``. Model treaties are not agreements and map to nothing.

A treaty matches a registry record with the same parties. Parties compare as ids (``EU``,
``BLEU``, countries), as the member countries of each bloc (EDIT writes ``EFTA`` where the
registry lists the EFTA states; a record linked to an intblock stands for the intblock's
members), and, on the same date of signature, as overlapping member sets. A BIT matches only
``investment`` records; an OIIA prefers other records. Levels, best first:

- the same date of signature (or the founding date of a linked record's intblock);
- the same year of signature (for an OIIA, at most 45 days apart or the same entry into force);
- the only record of the pair, for a BIT whose dates differ only by a typing slip (one part of
  the date of signature, or the same entry into force).

Ties go to the record with the same entry into force, then to the closer name ("interim",
"framework", "investment"...). A treaty dated like an ``instruments`` entry of a record is that
instrument. EDIT lists treaties of Czechoslovakia, the USSR and the former Yugoslavia with
successor states: such a BIT matches each successor's record with the same date of signature.
``MANUAL`` settles the rest by hand: plurilateral treaties, the agreements that one registry
record covers (``component``), and rejected candidates.

``--write`` adds a ``treaty_text`` link to the EDIT document page of each matched record when
EDIT has the text, and notes each date where EDIT differs from the record. It changes no date,
status or verification level. ``--report`` writes the match JSON for ``write_edit_report.py``.

Usage: python -I scripts/oneoff/import_edit.py RAW_DIR [--write] [--report JSON]
"""

import collections
import csv
import glob
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-11-23"
SOURCE = "EDIT - Electronic Database of Investment Treaties (World Trade Institute)"
DOCUMENT = "https://edit.wti.org/document/show/{uuid}"
KIND = {"WTI_TYPE_TREATY_BIT": "BIT", "WTI_TYPE_TREATY_OIIA": "OIIA", "WTI_TYPE_TREATY_MT": "Model"}
LABEL = {"signed": "date of signature", "in_force": "date of entry into force", "ended": "date of termination"}

# EDIT party codes that are not ISO alpha-3 codes of data/countries: blocs (intblock ids),
# EDIT's own codes for a few countries, and the former Yugoslavia, read as Serbia (the
# continuing state of the Federal Republic of Yugoslavia and of Serbia and Montenegro).
CODES = {
    "EU": "EU", "EC": "EU", "BLEU": "BLEU", "EFTA": "EFTA", "MERCOSUR": "MERCOSUR", "ASEAN": "ASEAN",
    "CACM": "CACM", "ECOWAS": "ECOWAS", "CARICOM": "CARICOM", "SADC": "SADC", "ANCOM": "CAN",
    "AU": "AFUNION", "COMESA": "COMESA", "SACU": "SACU", "WAEMU": "UEMOA", "CEMAC": "CEMAC",
    "PA": "PACIFICALLIANCE", "CEN-SAD": "CENSAD", "CEFTA": "CEFTA", "BIMSTEC": "BIMSTEC", "SAFTA": "SAFTA",
    "OPEC": "OPEC", "ECCAS": "ECCAS", "CEPGL": "ECGLC", "LAIA": "ALADI", "SPARTECA": "SPARTECA",
    "OECD": "OECD", "GCC": "CCASG", "EEU": "EAEU", "EAC": "EAC", "LAS": "LAS", "CIS": "CIS", "ECO": "ECO",
    "UMA": "UMA", "ECT": "ECT",
    "SCG": "RS", "RKS": "XK", "TWV": "TW", "TWA": "TW", "GBN": "GA", "HON": "HN",
}
# YUG: before 27 April 1992 the Socialist Federal Republic, whose treaties each successor
# state may apply; from then on the Federal Republic (Serbia, with Montenegro until 2006).
SFRY = ["RS", "ME", "BA", "HR", "MK", "SI", "XK"]
FRY_FROM = "1992-04-27"
# Codes split wrongly by EDIT's export, and party lists that contradict the treaty's name.
FIX = {"{CAN": ["CAN"], "KOR}_2014-09-22.xml": ["KOR"], "GEO.USA": ["GEO", "USA"], "SRB;YUG": ["SRB"]}
PARTIES = {
    "Chile - China Supplementary Agreement on Investment (2012)": ["CHL", "CHN"],
    "Belgium-Luxembourg Economic Union (BLEU) - Thailand BIT (1986)": ["BLEU", "THA"],
    "Uruguay - Saudi Arabia BIT (2025)": ["SAU", "URY"],
    "Saudi Arabia - United States TIFA (2004)": ["SAU", "USA"],
}
MEMBER = {"member", "founding_member", "former_member"}
KEYWORDS = {
    "interim": "interim", "association": "association", "stabilisation": "stabilisation",
    "stabilization": "stabilisation", "framework": "framework", "investment": "investment",
    "modernised": "modernised", "modernized": "modernised", "global": "global", "advanced": "advanced",
    "partnership": "partnership", "cooperation": "cooperation", "co": "cooperation", "upgrade": "upgrade",
    "upgraded": "upgrade", "upgrading": "upgrade", "protocol": "protocol", "services": "services",
}

# Hand decisions, by the first 8 characters of the EDIT uuid: a list of record ids (matched),
# "component:<id>" (a separate instrument of an agreement that the record covers as a whole,
# such as an investment agreement under an ASEAN+1 framework; no link), "reject" (the
# automatic candidate is another agreement; the treaty is missing), or "hold:<reason>".
MANUAL: dict[str, object] = {
    # Same agreement; the registry record has no date of signature yet (status lags).
    "ae1d7b74": ["EFTAVN"], "d9902ed8": ["GCCGB"], "22b34640": ["EUAU"], "a6f1f8a9": ["AEEC"],
    "d9b52eb4": ["BDJP"], "05972a42": ["INOM"], "22793505": ["CRIL"], "fab3d113": ["AEMY"],
    "320d1ce6": ["AEGE"], "8ef05d92": ["AUSG-OTHER"], "f93a6047": ["PKUS"], "821f3336": ["EUID"],
    # Same agreement, other dates.
    "31643fa9": ["DOCENTRALAMERICA"], "decfea95": ["EUTR"], "041ce2c3": ["CAUA-BIT"],
    "54ffe77a": ["JOSG"],  # typed BIT by EDIT; the FTA signed with the BIT
    # The USSR treaty and EDIT's Tajik copy of it.
    "2dddc9eb": ["ATTJ-BIT"], "a3f4a27e": ["ATRU-BIT"],
    # One EDIT treaty, several bilateral records.
    "78ecc332": ["CLCR", "CLGT", "CLHN", "CLNI", "CLSV"], "a5f3a60a": ["PASV"],
    "66d8409c": ["GTMX", "HNMX", "MXSV"], "e84b9985": ["COGTHNSV"],
    # Records linked to an intblock, and other plurilateral agreements.
    "48a361e0": ["EUCENTRALAMERICA"], "3aabb19a": ["UKCENTRALAMERICA"], "25dd4d38": ["EUMERCOSUR"],
    "f9412a83": ["EUSADCEPA"], "90a55f5d": ["MERCOSURSG"],
    "221cf07c": ["CACM"], "cc6a9d7a": ["CAN"], "a0c0b8de": ["CARICOM"], "c3b73b1c": ["ECOWAS"],
    "dc5b9a61": ["YAOUNDE-1963"], "0a86f09a": ["YAOUNDE-1969"], "b5abf2cc": ["LOME-1975"],
    "8a201121": ["LOME-1979"], "8d06c317": ["LOME-1984"], "b9ec58d3": ["SPARTECA"], "ea727b54": ["ALADI"],
    "7b6dfde6": ["OICIA"], "d444ad42": ["CCASG"], "a4d166ab": ["ECCAS"], "556d6ba2": ["AEC"],
    "f683dff7": ["EEA"], "4f342018": ["COMESA"], "57ce5bd9": ["UEMOA"], "6152dafa": ["EAC"],
    "e8b581e9": ["SAFTA"], "86ca25d5": ["BIMSTECFTA-FA"], "bd9ba222": ["MERCOSURCOECVE"],
    "e09b728a": ["TPSEP"], "f892ab10": ["EUCARIFORUMEPA"], "82356d54": ["ACIA"], "ef44d1cd": ["EUESAEPA"],
    "0fc404e7": ["EUANDEAN"], "16b739e3": ["EFTACRPA"], "e3ceee59": ["PACIFICALLIANCE"],
    "c22dbcc3": ["TPP"], "cc9cb87f": ["PACERPLUS"], "a07c46c7": ["KRCENTRALAMERICA"], "2bcf1adc": ["CPTPP"],
    "71f64914": ["UKESA"], "ede1b1d5": ["UKCARIFORUM"], "ef7d5b15": ["UKANDEAN"], "518b0084": ["INTRAEUBIT"],
    "bc8f045d": ["RCEP"], "c95cc294": ["GBISLINO"], "b2351442": ["PACALLSG"], "0ae96bf4": ["CEZ"],
    # Records another walk is editing now (CIS/EAEU, AfCFTA): matched, linked later.
    "6ca248c8": ["AfCFTA"], "71b83283": ["CISFTASERVICES"], "b733d847": ["EAEU"], "2f0ac0e9": ["EAEUVN"],
    # Separate instruments of an agreement the record covers.
    "d649ceac": "component:AKFTA", "7f0d5a37": "component:ACFTA", "5d30ad06": "component:AIFTA",
    "a3f45739": "component:AHKFTA", "85f0e03b": "component:CNHK", "e22ed8eb": "component:CNMO",
    "7bf088ee": "component:CNTW", "6956dd57": "component:KRTR", "951fe918": "component:CLCN",
    "ab5c1d85": "component:ANZCERTA", "f5d4b683": "component:AANZFTA", "a25d92e0": "component:NZSG",
    "f2d883f9": "component:CACL", "d58ff7d1": "component:EFTAKR", "c15c0426": "component:APTA",
    "4da58773": "component:EUMERCOSUR", "7fdf653d": "component:CARICOM", "f6f1abf2": "component:ECOWAS",
    "8d62b212": "component:ECOWAS", "21826fb3": "component:ECOWAS", "962e84e3": "component:ECOWAS",
    "9030e714": "component:ECOWAS", "8f9d38e2": "component:ECOWAS", "146e64ab": "component:CCASG",
    "b34ba160": "component:EFTA", "9e298bed": "component:MERCOSUR", "3674b186": "component:MERCOSUR",
    "a295e4fe": "component:MERCOSUR", "b7f1b612": "component:MERCOSUR", "b219ea5b": "component:CACM",
    "2d45e123": "component:CACM", "ef27497c": "component:EUOCT", "8993cb69": "component:AfCFTA",
    # Automatic candidates that are other agreements.
    **{u: "reject" for u in (
        "8612dec2", "9857d219", "0f0a6c11", "0d8a5823", "ccd9e55c", "17866449", "a41762f9", "d9c22487",
        "55bca13c", "7f8f7107", "36d7399b", "e88cfde0", "cae939ea", "b16f57f0", "c25f25e7", "1d2b4748",
        "30e8cddd", "8a86b537", "327cf631", "723b6b6b", "e634190b", "3890c517", "3e33a282", "54943600",
        "155995cf", "8e2ac157", "dd637383")},
    # Held, with the reason.
    "73d2cfcf": "hold:EDIT dates the GCC-New Zealand FTA 31 October 2011; the registry has it under negotiation",
    "abe4f153": "hold:UAIA: task 3.2 of add-investment-agreements waits for a party government or the League of Arab States",
    "183fb021": "hold:the ECT is an intblock; a registry record is not planned",
    "78c3145a": "hold:predecessor of ACIA (1987-2012); no intblock",
    "ba140599": "hold:Lomé IV: needs the ACP roster from EUR-Lex", "c3339a39": "hold:Cotonou Agreement: needs the ACP roster",
    "f177edb8": "hold:Samoa Agreement: needs the OACPS roster",
    "eff5dbcb": "add", "66f74a5f": "add", "038454da": "add",
    # BITs that EDIT alone lists, held: probably the registry's treaty with other dates, or
    # replaced by a later treaty of the pair while EDIT gives no termination.
    **{u: "hold:the registry's record of the pair may be the same treaty with other dates" for u in (
        "6e02c033", "b10c5aad", "281107f4")},
    **{u: "hold:a later treaty of the pair is in the registry and EDIT gives no date of termination" for u in (
        "8f15dc41", "1d3514a7", "fd7f944c", "ef34fdb7")},
    "5f1d397b": "hold:an establishment convention, not an investment treaty",
}


def load_edit(raw: Path) -> list[dict]:
    items = []
    for path in sorted(raw.glob("fs_p*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        items += json.loads(path.read_text(encoding="utf-8"))["_embedded"]["items"]
    rows = collections.defaultdict(list)
    with (raw / "export.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows[(row["Name"].strip(), row["Date of signature"])].append(row)
    treaties = []
    for item in items:
        day = (item.get("date_signed") or "")[:10]
        row = rows[(item["name"].strip(), day)]
        row = row.pop(0) if row else {}
        codes = []
        for code in PARTIES.get(item["name"].strip()) or item.get("party_iso_code") or []:
            codes += FIX.get(code, [code])
        treaties.append({
            "uuid": item["uuid"], "name": item["name"].strip(), "kind": KIND[item["treaty_type"]],
            "codes": codes, "signed": day or None, "in_force": (item.get("date_into_force") or "")[:10] or None,
            "terminated": (item.get("date_terminated") or "")[:10] or None,
            "published": (item.get("date_published") or "")[:10] or None,
            "languages": [x for x in (row.get("Origin language") or "").split(",") if x],
            "reference": row.get("Doc Reference"), "has_text": bool((item.get("preview_text") or "").strip()),
        })
    return treaties


def load_registry() -> dict[str, dict]:
    registry = {}
    for path in sorted(glob.glob(str(ROOT / "data/trade_agreements/*.yaml"))):
        text = Path(path).read_text(encoding="utf-8")
        record = yaml.safe_load(text)
        registry[record["id"]] = {"path": Path(path), "text": text, "record": record}
    return registry


def load_blocs() -> dict[str, dict]:
    blocs = {}
    for path in glob.glob(str(ROOT / "data/intblocks/*/*.yaml")):
        record = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=yaml.CSafeLoader)
        blocs[record["id"]] = {"includes": record.get("includes") or [], "founded": str(record.get("founded") or "")}
    return blocs


def iso3_map() -> dict[str, str]:
    out = {}
    for path in glob.glob(str(ROOT / "data/countries/*.yaml")):
        record = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=yaml.CSafeLoader)
        if record.get("iso3code"):
            out[record["iso3code"]] = record["code"]
    return out


def expand(ids, day: str | None, blocs: dict, depth: int = 0) -> frozenset:
    """The countries of a party set on a date: a bloc stands for its members then."""
    out = set()
    for pid in ids:
        if pid not in blocs or depth > 2:
            out.add(pid)
            continue
        for member in blocs[pid]["includes"]:
            if member.get("status") not in MEMBER:
                continue
            joined, left = str(member.get("joined") or ""), str(member.get("left") or "")
            if day and joined and joined[: len(day)] > day:
                continue
            if day and left and left[:10] <= day:
                continue
            out |= expand({member["id"]}, day, blocs, depth + 1) if member.get("type") == "intblock" else {member["id"]}
    return frozenset(out)


def undated(ids: frozenset, blocs: dict) -> frozenset:
    """Today's members of the blocs in a party set; empty when a party joined one of them later
    (the EU with Lithuania), since that set would also hold the bloc's other partners."""
    members = {m["id"] for b in ids & set(blocs) for m in blocs[b]["includes"] if m.get("status") in MEMBER}
    return frozenset() if (ids - set(blocs)) & members else expand(ids, None, blocs)


def record_sets(record: dict, blocs: dict) -> tuple[frozenset, set[frozenset]]:
    """The id set of a record and the country sets it may be written as."""
    day = str(record.get("signed") or "") or None
    if record.get("intblock"):
        ids = frozenset({record["intblock"]})
        return ids, {s for s in (ids, expand(ids, day, blocs), undated(ids, blocs)) if s}
    ids = frozenset(p["id"] for p in record["parties"])
    current = frozenset(p["id"] for p in record["parties"] if not p.get("left"))
    return ids, {s for s in (ids, current, expand(ids, day, blocs), undated(current, blocs)) if s}


def keywords(name: str) -> set[str]:
    return {KEYWORDS[w] for w in re.findall(r"[a-z]+", (name or "").lower()) if w in KEYWORDS}


def days_apart(a: str, b: str) -> int:
    try:
        return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)
    except ValueError:
        return 9999


def typing_slip(edit_signed: str | None, signed: str) -> bool:
    """Dates of signature that differ in one part only (year, month or day)."""
    if not edit_signed or len(signed) != 10:
        return not edit_signed
    a, b = edit_signed.split("-"), signed.split("-")
    return sum(x != y for x, y in zip(a, b, strict=True)) == 1


def level(treaty: dict, entry: dict, blocs: dict) -> tuple[float, str]:
    """How well a record fits the treaty: 3 same date, 2 same year, 0.5 only record, 0 no."""
    record = entry["record"]
    signed = str(record.get("signed") or "")
    if record.get("intblock") and not signed:
        signed = blocs.get(record["intblock"], {}).get("founded", "")
    edit = treaty["signed"]
    for instrument in record.get("instruments") or []:
        day = str(instrument.get("signed") or "")
        if edit and day and edit.startswith(day) and edit != signed:
            return 1, f"instrument {instrument['id']}"
    if edit and edit == signed:
        return 3, "date of signature"
    eif_same = bool(treaty["in_force"]) and treaty["in_force"] == str(record.get("in_force") or "")
    if edit and signed[:4] == edit[:4]:
        if treaty["kind"] == "BIT" or eif_same or len(signed) < 10 or days_apart(edit, signed) <= 45:
            return 2, "year of signature"
        return 0.4, "same year, dates far apart"
    if treaty["kind"] == "BIT" and (eif_same or typing_slip(edit, signed)):
        return 0.5, "only record of the pair, date differs by a typing slip"
    if treaty["kind"] == "OIIA" and not signed:
        return 0.4, "only record of the pair, which has no date of signature"
    return 0, ""


def main(argv: list[str]) -> int:
    raw = Path(argv[0])
    write = "--write" in argv
    report_path = argv[argv.index("--report") + 1] if "--report" in argv else None
    treaties = load_edit(raw)
    registry = load_registry()
    blocs = load_blocs()
    iso3 = iso3_map()

    index, by_signed, id_sets = collections.defaultdict(set), collections.defaultdict(set), {}
    for rid, entry in registry.items():
        record = entry["record"]
        if not record.get("parties") and not record.get("intblock"):
            continue
        ids, sets = record_sets(record, blocs)
        id_sets[rid] = (ids, sets)
        for s in sets:
            index[s].add(rid)
        day = str(record.get("signed") or "") or (blocs.get(record.get("intblock"), {}).get("founded") if record.get("intblock") else "")
        if day:
            by_signed[day].add(rid)

    report = collections.defaultdict(list)
    work = []
    for treaty in treaties:
        if treaty["kind"] == "Model":
            report["model"].append(treaty)
            continue
        ids, unresolved = set(), []
        for code in treaty["codes"]:
            if code == "YUG":
                ids |= set(SFRY) if (treaty["signed"] or "") < FRY_FROM else {"RS"}
                continue
            pid = CODES.get(code) or iso3.get(code)
            (ids.add(pid) if pid else unresolved.append(code))
        treaty["ids"] = frozenset(ids)
        treaty["unresolved"] = unresolved
        manual = MANUAL.get(treaty["uuid"][:8])
        treaty["manual"] = manual
        bit_split = treaty["kind"] == "BIT" and len(ids) > 3 and not unresolved
        if manual is None and not bit_split and (unresolved or len(ids) < 2 or len(ids) > 3):
            report["plurilateral"].append(treaty)
            continue
        work.append(treaty)

    pairs = []  # (score, treaty index, record id, method)
    assigned: dict[int, list] = collections.defaultdict(list)
    taken: dict[str, int] = {}
    for n, treaty in enumerate(work):
        manual = treaty["manual"]
        if isinstance(manual, list):
            for rid in manual:
                assert rid in registry, rid
                assigned[n].append((rid, "by hand", "by hand", (9, 1, 1)))
                taken[rid] = n
            continue
        if isinstance(manual, str):
            continue
        edit_sets = {s for s in (treaty["ids"], expand(treaty["ids"], treaty["signed"], blocs),
                                 undated(treaty["ids"], blocs)) if s}
        found = {}
        if treaty["kind"] == "BIT" and len(treaty["ids"]) >= 3 and treaty["signed"]:
            # A treaty of a former federation listed with its successor states.
            for rid in by_signed.get(treaty["signed"], ()):
                if id_sets[rid][0] < treaty["ids"] and len(id_sets[rid][0]) == 2:
                    found[rid] = "successor state"
        for s in edit_sets:
            for rid in index.get(s, ()):
                found.setdefault(rid, "parties" if treaty["ids"] in id_sets[rid][1] else "bloc members")
        if not found and treaty["signed"]:
            # Bloc rosters change: allow a difference made of bloc members only.
            wide = expand(treaty["ids"], treaty["signed"], blocs)
            for rid in by_signed.get(treaty["signed"], ()):
                involved = (treaty["ids"] | id_sets[rid][0]) & set(blocs)
                members = {m["id"] for b in involved for m in blocs[b]["includes"] if m.get("status") in MEMBER}
                for s in id_sets[rid][1]:
                    if len(wide & s) / len(wide | s) >= 0.6 and wide ^ s <= members:
                        found[rid] = "overlapping parties"
        scored = []
        for rid, how in found.items():
            entry = registry[rid]
            record = entry["record"]
            if treaty["kind"] == "BIT" and record.get("agreement_type") != "investment":
                continue
            lvl, why = level(treaty, entry, blocs)
            if lvl <= 0:
                continue
            eif = int(bool(treaty["in_force"]) and treaty["in_force"] == str(record.get("in_force") or ""))
            words = len(keywords(treaty["name"]) & keywords(record.get("name") or record.get("intblock")))
            scored.append(((lvl, eif, words), rid, f"{how}, {why}"))
        if treaty["kind"] == "OIIA" and any(registry[r]["record"].get("agreement_type") != "investment"
                                             and s[0] >= 2 for s, r, _ in scored):
            scored = [x for x in scored if registry[x[1]]["record"].get("agreement_type") != "investment"]
        pairs += [(s, n, rid, how) for s, rid, how in scored]
        treaty["candidates"] = [(rid, how, list(s)) for s, rid, how in sorted(scored, reverse=True)]

    # Assign the best pairs first. A tie between two records, or two treaties, is ambiguous.
    ambiguous: dict[int, str] = {}
    pairs.sort(key=lambda p: (p[0], -p[1]), reverse=True)
    for score, n, rid, how in pairs:
        treaty = work[n]
        if n in ambiguous:
            continue
        if score[0] == 1:  # an instrument: report it, never take the record
            if not assigned[n]:
                treaty.setdefault("instrument", (rid, how))
            continue
        if score[0] < 1 and score[0] != 0.5:
            if not assigned[n] and n not in ambiguous:
                ambiguous[n] = how
            continue
        if rid in taken and taken[rid] != n:
            rival = work[taken[rid]]
            rival_score = next(a[3] for a in assigned[taken[rid]] if a[0] == rid)
            same = (rival["ids"], rival["signed"], rival["in_force"]) == (treaty["ids"], treaty["signed"], treaty["in_force"])
            if same and not assigned[n]:
                treaty["duplicate_of"] = rival["uuid"]
            elif rival_score == score and not assigned[n]:
                ambiguous[n] = f"two EDIT documents for {rid}"
                ambiguous[taken[rid]] = f"two EDIT documents for {rid}"
            continue
        if assigned[n]:
            first = assigned[n][0]
            if "successor state" in how and "successor state" in first[2] and first[3][0] == score[0]:
                assigned[n].append((rid, how, how, score))
                taken[rid] = n
            elif first[3] == score:
                ambiguous[n] = "two records at the same level"
            continue
        assigned[n].append((rid, how, how, score))
        taken[rid] = n

    for n, treaty in enumerate(work):
        manual = treaty["manual"]
        if isinstance(manual, str):
            group, _, detail = manual.partition(":")
            treaty["record" if group == "component" else "reason"] = detail or None
            treaty["rejected"] = group == "reject"
            report[{"reject": "missing", "hold": "held", "add": "added"}[group] if group != "component" else "component"].append(treaty)
        elif n in ambiguous and not any(k in ambiguous[n] for k in ("only record", "same year")):
            treaty["reason"] = ambiguous[n]
            report["ambiguous"].append(treaty)
        elif n in ambiguous:
            treaty["reason"] = ambiguous[n]
            report["missing"].append(treaty)
        elif assigned[n]:
            treaty["matched"] = [(rid, how) for rid, how, _, _ in assigned[n]]
            report["matched"].append(treaty)
        elif treaty.get("duplicate_of"):
            report["duplicate"].append(treaty)
        elif treaty.get("instrument"):
            treaty["record"] = treaty["instrument"][0]
            report["instrument"].append(treaty)
        else:
            report["missing"].append(treaty)

    # Compare dates.
    for treaty in report["matched"]:
        treaty["conflicts"] = []
        for rid, _ in treaty["matched"]:
            record = registry[rid]["record"]
            edit = {"signed": treaty["signed"], "in_force": treaty["in_force"], "ended": treaty["terminated"]}
            for key, value in edit.items():
                mine = str(record.get(key) or "") or None
                if value and mine != value and not (mine and len(mine) < 10 and value.startswith(mine)):
                    treaty["conflicts"].append((rid, key, mine, value))
            if treaty["terminated"] and record.get("status") in ("in_force", "signed", "negotiating"):
                treaty["conflicts"].append((rid, "status", record.get("status"), "terminated"))
            elif treaty["in_force"] and record.get("status") in ("signed", "negotiating", "proposed"):
                treaty["conflicts"].append((rid, "status", record.get("status"), "in_force"))
            elif treaty["signed"] and record.get("status") in ("negotiating", "proposed"):
                treaty["conflicts"].append((rid, "status", record.get("status"), "signed"))

    # Missing BITs: a new catalogue record when EDIT gives the entry into force, else held.
    for treaty in list(report["missing"]):
        if treaty["kind"] != "BIT" or treaty.get("rejected"):
            continue
        if len(treaty["ids"]) != 2:
            treaty["reason"] = "a party has no country record (the former Yugoslavia)"
        elif not treaty["in_force"]:
            treaty["reason"] = "EDIT gives no date of entry into force, so not the status"
        elif treaty["signed"] and treaty["signed"] > treaty["in_force"]:
            treaty["reason"] = "EDIT's date of signature is after its entry into force"
        else:
            report["added"].append(treaty)
            report["missing"].remove(treaty)
            continue
        report["held"].append(treaty)
        report["missing"].remove(treaty)
    for treaty in report["missing"]:
        treaty["category"] = category(treaty["name"])

    summary = {
        "documents": len(treaties),
        "by_kind": dict(collections.Counter(t["kind"] for t in treaties)),
        **{k: len(v) for k, v in report.items()},
        "matched_records": len(taken),
        "matched_with_text": sum(1 for t in report["matched"] if t["has_text"]),
        "conflicts": sum(len(t["conflicts"]) for t in report["matched"]),
    }
    written = write_records(report, registry, write) if write or report_path else {}
    summary.update({k: len(v) for k, v in written.items()})
    print(json.dumps(summary, indent=1))
    if report_path:
        def plain(t: dict) -> dict:
            return {k: (sorted(v) if isinstance(v, frozenset) else v) for k, v in t.items() if k != "manual"}
        Path(report_path).write_text(json.dumps(
            {"summary": summary, "written": written,
             "report": {k: [plain(t) for t in v] for k, v in report.items()}},
            indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


CATEGORIES = [
    ("treaty of friendship, commerce and navigation or of establishment",
     r"FCN|Friendship|Amity|Navigation|Establishment"),
    ("trade and investment framework agreement or council", r"TIFA|TICFA|TICA|Council|MoUTI|Arrangement|Investment Development"),
    ("cooperation, partnership or framework agreement",
     r"Coop|Co-op|Partnership|PCA|Framework|Associative|Guarant|Initiative|Sustainab|Gibraltar|Free Movement"),
]


def category(name: str) -> str:
    for label, pattern in CATEGORIES:
        if re.search(pattern, name):
            return label
    return "other"


# Records that sessions running at the same time edit (CIS/EAEU, AfCFTA): matched, not written.
SKIP_PREFIX = ("EAEU", "CISFTA")
SKIP = {"AfCFTA"}
FIELD_ORDER = [
    "id", "name", "acronyms", "other_names", "agreement_type", "status", "signed", "in_force", "ended",
    "parties", "intblock", "supersedes", "superseded_by", "wto_rta_id", "aric_id", "unctad_iia_id",
    "wikidata_id", "links", "description", "notes", "verification", "last_verified", "provenance",
]
DG_TRADE = "European Commission, Directorate-General for Trade"
# EU investment agreements that EDIT lists and the registry lacked, with official dates.
OFFICIAL = {
    "eff5dbcb": {
        "id": "EUSG-BIT", "name": "EU-Singapore Investment Protection Agreement", "acronyms": ["EUSIPA"],
        "status": "signed", "signed": "2018-10-19", "parties": ["EU", "SG"],
        "notes": "Signed with the EU-Singapore Free Trade Agreement (EUSG); it enters into force when all EU "
                 "Member States have ratified it.",
        "source": DG_TRADE + ", EU-Singapore page",
        "url": "https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/singapore_en",
    },
    "66f74a5f": {
        "id": "EUVN-BIT", "name": "EU-Viet Nam Investment Protection Agreement", "acronyms": ["EVIPA"],
        "status": "signed", "signed": "2019-06-30", "parties": ["EU", "VN"],
        "notes": "Signed with the EU-Viet Nam Free Trade Agreement (EUVN); it enters into force when all EU "
                 "Member States have ratified it (18 had by June 2024, per the European Commission).",
        "source": DG_TRADE + ", EU-Viet Nam page",
        "url": "https://policy.trade.ec.europa.eu/eu-trade-relationships-country-and-region/countries-and-regions/viet-nam_en",
    },
    "038454da": {
        "id": "EUAO-BIT", "name": "EU-Angola Sustainable Investment Facilitation Agreement", "acronyms": ["SIFA"],
        "status": "in_force", "signed": "2023-11-17", "in_force": "2024-09-01", "parties": ["EU", "AO"],
        "notes": "An investment facilitation agreement: it has no investment protection or investor-state "
                 "dispute settlement.",
        "source": "EUR-Lex, CELEX 22024A00830 (Official Journal of the European Union)",
        "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:22024A00830",
    },
}


def dump(record: dict) -> str:
    ordered = {k: record[k] for k in FIELD_ORDER if k in record}
    ordered.update({k: v for k, v in record.items() if k not in ordered})
    return yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=120)


def plain_dump(record: dict) -> str:
    return yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120)


def put(record: dict, key: str, value, before: tuple[str, ...]) -> dict:
    """The record with key set, in place when present, else before the first of ``before``."""
    if key in record:
        return {**record, key: value}
    anchor = next(k for k in before if k in record)
    out = {}
    for k, v in record.items():
        if k == anchor:
            out[key] = value
        out[k] = v
    return out


def insert_link(text: str, url: str) -> str:
    """Add a treaty_text link at the end of the links list, keeping the layout (as import_gptad.py)."""
    item = f"- url: {url}\n  type: treaty_text\n"
    if "\nlinks:\n" in text:
        head, tail = text.split("\nlinks:\n", 1)
        lines = tail.splitlines(keepends=True)
        n = 0
        while n < len(lines) and (lines[n].startswith("- ") or lines[n].startswith("  ")):
            n += 1
        return head + "\nlinks:\n" + "".join(lines[:n]) + item + "".join(lines[n:])
    for anchor in ("\ndescription:", "\nnotes:", "\nverification:"):
        if anchor in text:
            return text.replace(anchor, f"\nlinks:\n{item.rstrip()}{anchor}", 1)
    raise ValueError("no anchor for links")


def pair_code(parties: list[tuple[str, str]]) -> str:
    blocs = sorted(p[1] for p in parties if p[0] == "intblock")
    return "".join(blocs + sorted(p[1] for p in parties if p[0] == "country"))


def write_records(report: dict, registry: dict, write: bool) -> dict:
    """Links and notes on matched records, and the new records. Returns what was (or would be) written."""
    out = collections.defaultdict(list)
    changes = collections.defaultdict(lambda: {"links": [], "notes": [], "uuids": []})
    for treaty in report["matched"]:
        url = DOCUMENT.format(uuid=treaty["uuid"])
        for rid, _ in treaty["matched"]:
            if rid.startswith(SKIP_PREFIX) or rid in SKIP:
                out["skipped_parallel_walk"].append(rid)
                continue
            change = changes[rid]
            if treaty["has_text"] and url not in registry[rid]["text"]:
                change["links"].append(url)
            record = registry[rid]["record"]
            for crid, key, mine, value in treaty["conflicts"]:
                # A date the record lacks is a gap, not a conflict, except on a catalogue record
                # (where it means another status); a linked record keeps its dates on the intblock.
                if crid != rid or key not in LABEL or record.get("intblock"):
                    continue
                if mine is None and record.get("verification") != "catalogue":
                    continue
                change["notes"].append((f"EDIT gives {value} as the {LABEL[key]}.", url))
    for rid, change in sorted(changes.items()):
        entry = registry[rid]
        text, record = entry["text"], entry["record"]
        sentences = [(s, u) for s, u in dict.fromkeys(change["notes"]) if s not in (record.get("notes") or "")]
        if sentences and plain_dump(record) == text:
            notes = " ".join(filter(None, [record.get("notes"), *[s for s, _ in sentences]]))
            record = put(record, "notes", notes, ("verification",))
            if change["links"]:
                links = list(record.get("links") or []) + [{"url": u, "type": "treaty_text"} for u in change["links"]]
                record = put(record, "links", links, ("description", "notes", "verification"))
            record["provenance"] = list(record["provenance"]) + [
                {"field": "notes", "source": SOURCE, "retrieved_at": TODAY, "url": u}
                for u in dict.fromkeys(u for _, u in sentences)]
            new_text = plain_dump(record)
            out["notes"].append(rid)
        else:
            if sentences:
                out["notes_not_written"].append(rid)
            new_text = text
            for u in change["links"]:
                new_text = insert_link(new_text, u)
        if change["links"]:
            out["links"].append(rid)
        if new_text != text and write:
            entry["path"].write_text(new_text, encoding="utf-8")

    taken = set(registry)
    for treaty in report["added"]:
        spec = OFFICIAL.get(treaty["uuid"][:8])
        url = DOCUMENT.format(uuid=treaty["uuid"])
        if spec:
            parties = [("intblock" if p in ("EU", "BLEU") else "country", p) for p in spec["parties"]]
            record = {"id": spec["id"], "name": spec["name"], "acronyms": [{"lang": "en", "value": a} for a in spec["acronyms"]],
                      "agreement_type": "investment", "status": spec["status"]}
            record.update({k: spec[k] for k in ("signed", "in_force") if spec.get(k)})
            verification, source, src_url, fields = "official", spec["source"], spec["url"], ["status", "signed", "in_force"]
        else:
            parties = [("intblock" if p == "BLEU" else "country", p) for p in sorted(treaty["ids"])]
            pc = pair_code(parties)
            rid = f"{pc}-BIT" if f"{pc}-BIT" not in taken else f"{pc}-BIT-{treaty['signed'][:4]}"
            status = "terminated" if treaty["terminated"] else "in_force"
            record = {"id": rid, "name": re.sub(r"\s+", " ", treaty["name"]), "agreement_type": "investment",
                      "status": status, "signed": treaty["signed"], "in_force": treaty["in_force"]}
            if treaty["terminated"]:
                record["ended"] = treaty["terminated"]
            verification, source, src_url, fields = "catalogue", SOURCE, url, ["status", "signed", "in_force", "ended"]
        if record["id"] in taken:
            out["id_collision"].append(record["id"])
            continue
        taken.add(record["id"])
        record["parties"] = [{"id": p, "type": kind} for kind, p in sorted(parties, key=lambda x: (x[0] != "intblock", x[1]))]
        if treaty["has_text"]:
            record["links"] = [{"url": url, "type": "treaty_text"}]
        if spec:
            record["notes"] = spec["notes"]
        record["verification"] = verification
        record["last_verified"] = TODAY
        record["provenance"] = [{"field": "parties", "source": source, "retrieved_at": TODAY, "url": src_url}]
        record["provenance"] += [{"field": f, "source": source, "retrieved_at": TODAY, "url": src_url}
                                 for f in fields if f == "status" or f in record]
        if spec:
            record["provenance"].append({"field": "links", "source": SOURCE, "retrieved_at": TODAY, "url": url})
        treaty["record"] = record["id"]
        out["added"].append(record["id"])
        if write:
            (ROOT / "data/trade_agreements" / f"{record['id']}.yaml").write_text(dump(record), encoding="utf-8")
    return dict(out)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
