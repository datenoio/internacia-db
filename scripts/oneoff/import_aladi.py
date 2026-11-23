#!/usr/bin/env python3
"""One-off: add ALADI partial-scope agreements that are in force or signed and missing from the registry.

Input is the directory written by ``fetch_aladi.py`` (``index.json`` and ``docs/<code>.html``).
The pages are untrusted data: keep them outside the repository and run this script with
``python -I``.

A walk on 2026-11-23 compared ALADI's 90 current agreements with the registry by signatories
and date of signature. 15 carry no trade preferences (transport, tourism, waterway and
vehicle rules under Article 14, the agricultural health council), 25 already had a record
(the Mexico agreements from WTO RTA-IS, the GPTAD walk's ALADI records, and ACE 18, which is
MERCOSUR's Treaty of Asunción), and the 51 in ``SELECT`` had none. This script writes one
record for each of them.

ALADI is the depositary, so the records are ``verification: official``. Signatories come
from ``Países signatarios``, the date of signature from ``Fecha de suscripción`` (US order,
``MM/DD/YY`` or ``MM/DD/YYYY``), and entry into force from ``Entrada en vigor`` (``DD/MM/YYYY``
or Spanish words); when it differs by pair of parties, each party gets the date of its
first pair. An agreement for which ALADI has no notice of entry into force is ``signed``.
Historical (terminated) ALADI agreements are not imported here: their records give no end
date. See ``docs/intblock-sources.md``.

Usage: python -I scripts/oneoff/import_aladi.py ALADI_DIR [--write]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "trade_agreements"
RETRIEVED = "2026-11-23"
SOURCE = "ALADI, agreements database"
RECORD = "http://www2.aladi.org/nsfaladi/{}.nsf/0/{}?OpenDocument"

ES = {
    "argentina": "AR", "bolivia": "BO", "brasil": "BR", "chile": "CL", "colombia": "CO", "cuba": "CU",
    "ecuador": "EC", "méxico": "MX", "panamá": "PA", "paraguay": "PY", "perú": "PE", "uruguay": "UY",
    "venezuela": "VE", "costa rica": "CR", "el salvador": "SV", "guatemala": "GT", "honduras": "HN",
    "nicaragua": "NI", "trinidad y tobago": "TT", "guyana": "GY", "suriname": "SR",
    "san cristobal y nieves": "KN",
}
EN = {
    "AR": "Argentina", "BO": "Bolivia", "BR": "Brazil", "CL": "Chile", "CO": "Colombia", "CU": "Cuba",
    "EC": "Ecuador", "MX": "Mexico", "PA": "Panama", "PY": "Paraguay", "PE": "Peru", "UY": "Uruguay",
    "VE": "Venezuela", "CR": "Costa Rica", "SV": "El Salvador", "GT": "Guatemala", "HN": "Honduras",
    "NI": "Nicaragua", "TT": "Trinidad and Tobago", "GY": "Guyana", "SR": "Suriname", "KN": "Saint Kitts and Nevis",
}
MERCOSUR = {"AR", "BR", "PY", "UY"}
MONTHS = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
MONTHS["setiembre"] = 9
NO_DATE = "ALADI, the depositary, has no notice of its entry into force."

# ALADI code -> record id, agreement type and notes (checked by hand against the ALADI record).
# ``parties`` overrides the signatories ALADI lists; ``title`` overrides the generated name.
SELECT: dict[str, dict] = {
    "AAP.CE Nº 2": {"id": "BRUY", "type": "pta", "notes": "The Brazil - Uruguay Trade Expansion Protocol (PEC)."},
    "AAP.CE Nº 13": {"id": "ARPY", "type": "pta"},
    "AAP.CE Nº 14": {"id": "ARBR", "type": "fta",
                     "notes": "The Argentina - Brazil tariff elimination programme towards a common market, "
                              "taken up by MERCOSUR."},
    "AAP.CE Nº 16": {"id": "ARCL", "type": "pta"},
    "AAP.CE Nº 40": {"id": "CUVE", "type": "pta"},
    "AAP.CE Nº 42": {"id": "CLCU", "type": "pta"},
    "AAP.CE Nº 46": {"id": "CUEC", "type": "pta"},
    "AAP.CE Nº 47": {"id": "BOCU", "type": "pta"},
    "AAP.CE Nº 49": {"id": "COCU", "type": "pta"},
    "AAP.CE Nº 50": {"id": "CUPE", "type": "pta"},
    "AAP.CE Nº 54": {"id": "MERCOSURMX", "type": "framework",
                     "notes": "Framework agreement for a free trade area between MERCOSUR and Mexico."},
    "AAP.CE Nº 55": {"id": "MERCOSURMX-ACE55", "type": "pta",
                     "notes": "Free trade in the automotive sector between MERCOSUR states and Mexico."},
    "AAP.CE Nº 57": {"id": "ARUY", "type": "pta", "notes": "Trade in the automotive sector."},
    "AAP.CE Nº 62": {"id": "MERCOSURCU", "type": "pta"},
    "AAP.CE Nº 63": {"id": "UYVE", "type": "pta", "notes": "Venezuela grants duty-free access to listed goods."},
    "AAP.CE Nº 64": {"id": "PYVE", "type": "pta", "notes": "Venezuela grants duty-free access to listed goods."},
    "AAP.CE Nº 68": {"id": "ARVE", "type": "pta",
                     "notes": "Governs trade during Venezuela's accession to MERCOSUR."},
    "AAP.CE Nº 69": {"id": "BRVE", "type": "pta",
                     "notes": "Governs trade during Venezuela's accession to MERCOSUR."},
    "AAP.CE Nº 70": {"id": "ECOALBA", "type": "framework",
                     "title": "Economic Complementation Agreement No. 70: Framework Agreement for the Economic "
                              "Space of the Bolivarian Alliance for the Peoples of Our America - Peoples' Trade "
                              "Treaty (ECOALBA-TCP)"},
    "AAP.CE Nº 71": {"id": "CUPA", "type": "pta"},
    "AAP.CE Nº 72": {"id": "MERCOSURCO", "type": "fta",
                     "notes": "ALADI gives the dates of application between Colombia and each MERCOSUR state."},
    "AAP.CE Nº 73": {"id": "CLUY", "type": "fta"},
    "AAP.CE Nº 74": {"id": "BRPY", "type": "framework"},
    "AAP.CE Nº 75": {"id": "CLEC", "type": "fta"},
    "AAP.CE Nº 76": {"id": "MERCOSURPA", "type": "framework"},
    "AAP.A25TM Nº 6": {"id": "CONI", "type": "pta"},
    "AAP.A25TM Nº 7": {"id": "COCR-1984", "type": "pta",
                       "notes": "Not the 2013 Colombia - Costa Rica FTA (COCR)."},
    "AAP.A25TM Nº 16": {"id": "HNVE", "type": "pta"},
    "AAP.A25TM Nº 20": {"id": "TTVE", "type": "pta"},
    "AAP.A25TM Nº 22": {"id": "GYVE", "type": "pta"},
    "AAP.A25TM Nº 23": {"id": "GTVE", "type": "pta"},
    "AAP.A25TM Nº 25": {"id": "NIVE", "type": "pta"},
    "AAP.A25TM Nº 26": {"id": "CRVE", "type": "pta"},
    "AAP.A25TM Nº 27": {"id": "SVVE", "type": "pta"},
    "AAP.A25TM Nº 29": {"id": "COPA", "type": "pta"},
    "AAP.A25TM Nº 36": {"id": "CUGT", "type": "pta"},
    "AAP.A25TM Nº 37": {"id": "GTMXSV", "type": "other",
                        "parties": ["MX", "GT", {"id": "SV", "note": "Listed by ALADI as a party; the text is "
                                                                     "signed by Mexico and Guatemala."}],
                        "notes": "Trade in natural gas between Mexico and Guatemala: transport, distribution, "
                                 "storage, export and import."},
    "AAP.A25TM Nº 38": {"id": "BRGY", "type": "pta",
                        "parties": ["BR", "GY", {"id": "KN", "note": "Listed by ALADI as a party; the text is "
                                                                     "signed by Brazil and Guyana."}]},
    "AAP.A25TM Nº 41": {"id": "BRSR", "type": "pta", "notes": "Tariff preferences for rice."},
    "AAP.A25TM Nº 42": {"id": "ECGT", "type": "pta"},
    "AAP.A25TM Nº 44": {"id": "CUNI", "type": "pta"},
    "AAP.A25TM Nº 45": {"id": "ECNI", "type": "pta"},
    "AAP.A25TM Nº 47": {"id": "CUHN", "type": "pta"},
    "AAP.A25TM Nº 48": {"id": "BOSV", "type": "pta"},
    "AAP.A14TM Nº 12": {"id": "MERCOSURCACM", "type": "framework",
                        "parties": ["AR", "BR", "PY", "UY", "CR", "GT", "HN", "NI", "SV"],
                        "title": "Framework Agreement on Trade and Investment between MERCOSUR and the Central "
                                 "American Common Market"},
    "AAP.AG Nº 1": {"id": "ARUY-AG1", "type": "pta", "notes": "Preferential treatment for live cattle and meat."},
    "AAP.AG Nº 2": {"id": "ALADI-AG2", "type": "pta", "notes": "Liberalisation of trade in seeds."},
    "AR.AM Nº 1": {"id": "ALADI-AM1", "type": "preference_scheme", "beneficiary": "BO"},
    "AR.AM Nº 2": {"id": "ALADI-AM2", "type": "preference_scheme", "beneficiary": "EC"},
    "AR.AM Nº 3": {"id": "ALADI-AM3", "type": "preference_scheme", "beneficiary": "PY"},
    "AR.PAR Nº 4": {"id": "ALADI-PAR", "type": "pta",
                    "parties": ["AR", "BO", "BR", "CL", "CO", "EC", "MX", "PE", "PY", "UY", "VE",
                                {"id": "CU", "note": "Joined after acceding to ALADI in 1999."},
                                {"id": "PA", "note": "Joined after acceding to ALADI in 2012."}],
                    "title": "Regional Agreement No. 4 establishing the Regional Tariff Preference",
                    "notes": "A tariff preference that each member grants to the goods of the others, with "
                             "margins graded by level of development."},
}
FIELD_ORDER = ["id", "name", "other_names", "agreement_type", "status", "signed", "in_force", "parties", "notes",
               "verification", "last_verified", "provenance"]


def page_text(path: Path) -> str:
    t = path.read_text(encoding="latin-1")
    t = re.sub(r"<(script|style).*?</\1>", "", t, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " | ", t))
    t = re.sub(r"(\s*\|\s*)+", " | ", t)
    return re.sub(r"\s+", " ", t)


def field(text: str, label: str) -> str:
    """A record field: ``label | : | value | ____``."""
    m = re.search(re.escape(label) + r" \| : \| (.*?) \| _{5,}", text)
    return m.group(1).strip() if m else ""


def signature_date(value: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})", value.strip())
    if not m:
        return None
    year = int(m.group(3))
    if year < 100:
        year += 1900 if year >= 60 else 2000
    return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"


DATE = r"(\d{1,2}/\d{1,2}/\d{4}|\d{1,2} de [a-zé]+ de \d{4})"


def day_first(value: str) -> str | None:
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{1,2}) de ([a-zé]+) de (\d{4})", value)
    if m and m.group(2) in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None


def codes(names: str) -> list[str]:
    """Country codes in a Spanish list such as ``Argentina, Brasil, Uruguay (MERCOSUR)``."""
    names = re.sub(r"\((MERCOSUR|MCCA|CARICOM)\)", "", names.lower())
    out = []
    for key in sorted(ES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(key)}\b", names):
            out.append(ES[key])
            names = re.sub(rf"\b{re.escape(key)}\b", " ", names)
    return sorted(out)


def entry_into_force(value: str) -> tuple[str | None, dict[str, str]]:
    """The earliest date and, when dates differ by pair, each party's first date."""
    per_party: dict[str, str] = {}
    pairs = re.findall(rf"(?:Entre|entre|Para)\s+([^:|]+?)\s*:\s*{DATE}", value)
    pairs += [(who, d) for who, d in re.findall(rf"para ([^|]+?) el (?:día )?{DATE}", value)]
    for who, raw in pairs:
        date = day_first(raw)
        for code in codes(who.replace("-", " y ")):
            if date and (code not in per_party or date < per_party[code]):
                per_party[code] = date
    dates = sorted({d for d in (day_first(x) for x in re.findall(DATE, value)) if d})
    first = dates[0] if dates else None
    return first, per_party if len(set(per_party.values())) > 1 else {}


def name_for(code: str, spec: dict, parties: list[str]) -> tuple[str, str]:
    if spec.get("title"):
        english = spec["title"]
    else:
        kind, number = code.split(" Nº ")
        countries = [p for p in parties if p not in MERCOSUR] if set(parties) > MERCOSUR else parties
        if set(parties) > MERCOSUR:
            between = "the MERCOSUR States Parties and " + " and ".join(EN[c] for c in countries)
        else:
            between = " and ".join(EN[c] for c in parties)
        if kind == "AAP.CE":
            english = f"Economic Complementation Agreement No. {number} between {between}"
        elif kind == "AAP.A25TM":
            english = f"Partial Scope Agreement No. {number} between {between} (Article 25 of the 1980 Montevideo Treaty)"
        elif kind == "AAP.AG":
            english = f"Agricultural Partial Scope Agreement No. {number} between {between}"
        elif kind == "AR.AM":
            english = f"Regional Market Opening Agreement No. {number} in favour of {EN[spec['beneficiary']]}"
        else:
            english = f"{kind} No. {number}"
    kind, number = code.split(" Nº ")
    spanish = {
        "AAP.CE": f"Acuerdo de Complementación Económica N° {number}",
        "AAP.A25TM": f"Acuerdo de Alcance Parcial N° {number} (Artículo 25 del Tratado de Montevideo 1980)",
        "AAP.A14TM": f"Acuerdo de Alcance Parcial N° {number} (Artículo 14 del Tratado de Montevideo 1980)",
        "AAP.AG": f"Acuerdo de Alcance Parcial Agropecuario N° {number}",
        "AR.AM": f"Acuerdo Regional de Apertura de Mercados N° {number}",
        "AR.PAR": f"Acuerdo Regional N° {number} - Preferencia Arancelaria Regional",
    }[kind]
    return english, spanish


def build(code: str, spec: dict, agreement: dict, text: str) -> dict:
    listed = codes(field(text, "Países signatarios"))
    signed = signature_date(field(text, "Fecha de suscripción"))
    first, per_party = entry_into_force(field(text, "Entrada en vigor"))
    raw_parties = spec.get("parties") or listed
    ids = [p if isinstance(p, str) else p["id"] for p in raw_parties]
    english, spanish = name_for(code, spec, ids)
    parties = []
    for p in raw_parties:
        party = {"id": p, "type": "country"} if isinstance(p, str) else {"id": p["id"], "type": "country",
                                                                         **{k: v for k, v in p.items() if k != "id"}}
        if party["id"] == spec.get("beneficiary"):
            party["note"] = "Beneficiary: the other members grant duty-free access to listed goods without reciprocity."
        if party["id"] in per_party:
            party = {"id": party["id"], "type": "country", "in_force": per_party[party["id"]],
                     **{k: v for k, v in party.items() if k not in ("id", "type")}}
        parties.append(party)
    notes = [f"Registered with ALADI as {code.replace('Nº', 'No.')}."]
    if spec.get("notes"):
        notes.append(spec["notes"])
    if not first:
        notes.append(NO_DATE)
    record = {
        "id": spec["id"], "name": english, "other_names": [{"lang": "es", "name": spanish}],
        "agreement_type": spec["type"], "status": "in_force" if first else "signed", "signed": signed,
    }
    if first:
        record["in_force"] = first
    record["parties"] = parties
    record["notes"] = " ".join(notes)
    record["verification"] = "official"
    record["last_verified"] = RETRIEVED
    url = RECORD.format("textacdos" if agreement["db"] == "cur" else "histtextacdos", agreement["main"])
    record["provenance"] = [{"field": f, "source": SOURCE, "url": url, "retrieved_at": RETRIEVED}
                            for f in ("parties", "signed", "in_force" if first else "status")]
    overridden = {p["id"] for p in raw_parties if isinstance(p, dict)}
    problems = sorted(set(ids) - set(listed) - overridden)
    if problems:
        print(f"! {code}: parties {problems} are not among the ALADI signatories {listed}")
    return {k: record[k] for k in FIELD_ORDER if k in record}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("aladi_dir", type=Path)
    parser.add_argument("--write", action="store_true", help="write the records to data/trade_agreements/")
    args = parser.parse_args(argv)
    index = json.loads((args.aladi_dir / "index.json").read_text(encoding="utf-8"))
    written = 0
    for code, spec in SELECT.items():
        agreement = index[code]
        if agreement["db"] != "cur":
            print(f"! {code} is not a current agreement")
            continue
        text = page_text(args.aladi_dir / "docs" / (code.replace(" ", "_").replace("º", "") + ".html"))
        record = build(code, spec, agreement, text)
        path = REGISTRY / f"{record['id']}.yaml"
        print(f"{code:18} {record['id']:18} {record['status']:9} {record['signed']} {record.get('in_force', '-'):10} "
              f"{','.join(p['id'] for p in record['parties'])}")
        if args.write and not path.exists():
            path.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
            written += 1
    print(f"{len(SELECT)} agreements, wrote {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
