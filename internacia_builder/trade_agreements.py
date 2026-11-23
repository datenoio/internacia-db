"""Trade agreements registry: load ``data/trade_agreements/*.yaml`` and derive export rows.

A record either lists its ``parties`` or links to the intblock that holds its roster
(``intblock``). A linked record takes its name, links, acronyms, other names and Wikidata id
from that intblock, its dates too unless it sets them, and its parties from the intblock's
``includes``, so a roster is never kept in two places. See ``openspec/changes/add-trade-agreements-registry``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from internacia_builder.yaml_io import safe_load

TRADE_AGREEMENTS_DIR = ("data", "trade_agreements")

# includes[].status values that make a country a party to the agreement of a linked
# intblock. Observers, partners, funders and similar links are not parties. On a
# non-reciprocal preference scheme the grantor is a ``contributor`` and each beneficiary a
# ``recipient``; both are parties of the scheme.
PARTY_INCLUDE_STATUSES = frozenset(
    {
        "member",
        "founding_member",
        "former_member",
        "participant",
        "associate",
        "associate_member",
        "associated",
        "contributor",
        "recipient",
    }
)

# includes[].type -> trade_agreement_parties.party_type
INCLUDE_PARTY_TYPES = {
    "country": "country",
    "territory": "territory",
    "historical-country": "historical-country",
    "organization": "intblock",
}

PARTY_TYPES = ["country", "historical-country", "intblock", "territory"]
PARTY_STATUSES = ["former_party", "party"]


def trade_agreements_dir(root: Path) -> Path:
    return root.joinpath(*TRADE_AGREEMENTS_DIR)


def load_trade_agreement_records(root: Path) -> list[dict[str, Any]]:
    """Source records sorted by file name; malformed files are skipped (the validator reports them)."""
    directory = trade_agreements_dir(root)
    if not directory.exists():
        return []
    records = []
    for path in sorted(directory.glob("*.yaml")):
        record = safe_load(path.read_text(encoding="utf-8"))
        if isinstance(record, dict):
            records.append(record)
    return records


def _date(value: Any) -> str | None:
    return None if value is None or value == "" else str(value)


def _int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def linked_fields(intblock: dict[str, Any]) -> dict[str, Any]:
    """The agreement fields a linked record reads from its intblock."""
    period = intblock.get("active_period") or {}
    return {
        "name": intblock.get("name"),
        "signed": _date(intblock.get("founded")),
        "in_force": _date(period.get("start")),
        "ended": _date(intblock.get("dissolved")) or _date(period.get("end")),
        "wikidata_id": intblock.get("wikidata_id"),
        "links": [
            {"url": link.get("url"), "type": link.get("type")}
            for link in intblock.get("links") or []
            if isinstance(link, dict)
        ],
        "acronyms": [
            {"lang": a.get("lang"), "value": a.get("value")}
            for a in intblock.get("acronyms") or []
            if isinstance(a, dict)
        ],
        "other_names": [
            {"lang": n.get("id"), "name": n.get("name")}
            for n in intblock.get("other_names") or []
            if isinstance(n, dict)
        ],
        "description": intblock.get("description"),
    }


def intblock_party_rows(agreement_id: str, intblock: dict[str, Any]) -> list[dict[str, Any]]:
    """Party rows of a linked record, from the intblock's party-like ``includes`` entries."""
    rows = []
    for inc in intblock.get("includes") or []:
        if not isinstance(inc, dict) or inc.get("status") not in PARTY_INCLUDE_STATUSES:
            continue
        left = _date(inc.get("left"))
        former = left is not None or inc.get("status") == "former_member"
        rows.append(
            {
                "agreement_id": agreement_id,
                "party_id": str(inc.get("id")),
                "party_type": INCLUDE_PARTY_TYPES.get(str(inc.get("type")), str(inc.get("type"))),
                "status": "former_party" if former else "party",
                "signed": None,
                "in_force": None,
                "joined": _date(inc.get("joined")),
                "left": left,
                "note": inc.get("note"),
                "source": "intblock",
            }
        )
    return rows


def record_party_rows(agreement_id: str, record: dict[str, Any]) -> list[dict[str, Any]]:
    """Party rows of a record that lists its parties."""
    rows = []
    for party in record.get("parties") or []:
        if not isinstance(party, dict):
            continue
        left = _date(party.get("left"))
        signed = _date(party.get("signed"))
        in_force = _date(party.get("in_force"))
        rows.append(
            {
                "agreement_id": agreement_id,
                "party_id": str(party.get("id")),
                "party_type": str(party.get("type")),
                "status": "former_party" if left else "party",
                "signed": signed,
                "in_force": in_force,
                "joined": in_force or signed,
                "left": left,
                "note": party.get("note"),
                "source": "record",
            }
        )
    return rows


def build_trade_agreement_rows(
    records: list[dict[str, Any]], intblocks: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Rows of the ``trade_agreements`` and ``trade_agreement_parties`` tables."""
    by_id = {str(r.get("id")): r for r in intblocks if r.get("id")}
    agreements: list[dict[str, Any]] = []
    parties: list[dict[str, Any]] = []
    for record in records:
        agreement_id = str(record.get("id"))
        linked = record.get("intblock")
        intblock = by_id.get(str(linked)) if linked else None
        fields = linked_fields(intblock) if intblock else {}
        rows = (
            intblock_party_rows(agreement_id, intblock)
            if intblock
            else record_party_rows(agreement_id, record)
        )
        parties.extend(rows)

        source = dict(fields) if intblock else record
        if intblock:
            # A linked record may set its own dates; they override the intblock's.
            source.update({k: record[k] for k in ("signed", "in_force", "ended") if record.get(k)})
        pick = source.get

        agreements.append(
            {
                "id": agreement_id,
                "name": pick("name"),
                "agreement_type": record.get("agreement_type"),
                "status": record.get("status"),
                "signed": _date(pick("signed")),
                "in_force": _date(pick("in_force")),
                "ended": _date(pick("ended")),
                "intblock_id": str(linked) if linked else None,
                "party_count": sum(1 for row in rows if row["status"] == "party"),
                "supersedes": record.get("supersedes"),
                "superseded_by": record.get("superseded_by"),
                "wto_rta_id": _int(record.get("wto_rta_id")),
                "aric_id": _int(record.get("aric_id")),
                "wikidata_id": pick("wikidata_id"),
                "acronyms": [
                    {"lang": a.get("lang"), "value": a.get("value")}
                    for a in (pick("acronyms") or [])
                    if isinstance(a, dict)
                ],
                "other_names": [
                    {"lang": n.get("lang"), "name": n.get("name")}
                    for n in (pick("other_names") or [])
                    if isinstance(n, dict)
                ],
                "links": [
                    {"url": link.get("url"), "type": link.get("type")}
                    for link in (pick("links") or [])
                    if isinstance(link, dict)
                ],
                "description": record.get("description") or fields.get("description"),
                "notes": record.get("notes"),
                "verification": record.get("verification"),
                "last_verified": _date(record.get("last_verified")),
                "provenance": [
                    {
                        "field": p.get("field"),
                        "source": p.get("source"),
                        "url": p.get("url"),
                        "retrieved_at": _date(p.get("retrieved_at")),
                        "license": p.get("license"),
                    }
                    for p in record.get("provenance") or []
                    if isinstance(p, dict)
                ],
            }
        )
    agreements.sort(key=lambda r: r["id"])
    parties.sort(key=lambda r: (r["agreement_id"], r["party_id"]))
    return agreements, parties


def _provenance_rows(rows: Any) -> list[dict[str, Any]]:
    return [
        {
            "field": p.get("field"),
            "source": p.get("source"),
            "url": p.get("url"),
            "retrieved_at": _date(p.get("retrieved_at")),
            "license": p.get("license"),
        }
        for p in rows or []
        if isinstance(p, dict)
    ]


def build_trade_agreement_instrument_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rows of the ``trade_agreement_instruments`` table, from each record's ``instruments``.

    A linked record's instruments are its own, never the intblock's. Rows are sorted by
    agreement, then by signature date (undated instruments last), then by id.
    """
    rows: list[dict[str, Any]] = []
    for record in records:
        agreement_id = str(record.get("id"))
        for item in record.get("instruments") or []:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "agreement_id": agreement_id,
                    "instrument_id": str(item.get("id")),
                    "kind": item.get("kind"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "signed": _date(item.get("signed")),
                    "in_force": _date(item.get("in_force")),
                    "ended": _date(item.get("ended")),
                    "coverage": [str(c) for c in item.get("coverage") or []],
                    "other_names": [
                        {"lang": n.get("lang"), "name": n.get("name")}
                        for n in item.get("other_names") or []
                        if isinstance(n, dict)
                    ],
                    "notes": item.get("notes"),
                    "provenance": _provenance_rows(item.get("provenance")),
                }
            )
    rows.sort(key=lambda r: (r["agreement_id"], r["signed"] is None, r["signed"] or "", r["instrument_id"]))
    return rows
