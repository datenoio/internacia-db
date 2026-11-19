"""World Bank country classifications and the ``wbgroup`` rosters derived from them.

The World Bank publishes a region, an administrative region, an income level, and a lending
type for each economy it classifies (``https://api.worldbank.org/v2/country``). Country records
take those four fields from that endpoint, trimmed but otherwise verbatim. Entities the Bank
does not classify keep their geographic inferences, recoded to the Bank's current ids and
labels. The ``wbgroup`` intblocks listed in :data:`WB_GROUP_BLOCKS` are the same
classifications seen as groups, so their rosters are rebuilt from, and checked against, the
country fields.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

WB_COUNTRY_API = "https://api.worldbank.org/v2/country"
WB_SOURCE = "World Bank"
# Provenance source for values the Bank once published for an entity it no longer classifies.
WB_HISTORICAL_SOURCE = "World Bank (historical classification)"
WB_GROUP_SOURCE = "World Bank (WDI income/region groupings)"

CLASSIFICATION_FIELDS = ("region", "adminregion", "incomeLevel", "lendingType")
HIGH_INCOME = "HIC"

# Current World Bank labels, as the API returns them (trimmed).
LABELS: dict[str, dict[str, str]] = {
    "region": {
        "EAS": "East Asia & Pacific",
        "ECS": "Europe & Central Asia",
        "LCN": "Latin America & Caribbean",
        "MEA": "Middle East, North Africa, Afghanistan & Pakistan",
        "NAC": "North America",
        "SAS": "South Asia",
        "SSF": "Sub-Saharan Africa",
    },
    "adminregion": {
        "EAP": "East Asia & Pacific (excluding high income)",
        "ECA": "Europe & Central Asia (excluding high income)",
        "LAC": "Latin America & Caribbean (excluding high income)",
        "MNA": "Middle East, North Africa, Afghanistan & Pakistan (excluding high income)",
        "SAS": "South Asia",
        "SSA": "Sub-Saharan Africa (excluding high income)",
    },
    "incomeLevel": {
        "HIC": "High income",
        "UMC": "Upper middle income",
        "LMC": "Lower middle income",
        "LIC": "Low income",
    },
    "lendingType": {
        "IBD": "IBRD",
        "IDB": "Blend",
        "IDX": "IDA",
        "LNX": "Not classified",
    },
}

# Ids the Bank no longer uses: the OECD / non-OECD split of high income (dropped in 2016),
# the old "not classified" lending code, and the region id once used for an administrative region.
LEGACY_IDS: dict[str, dict[str, str]] = {
    "incomeLevel": {"OEC": HIGH_INCOME, "NOC": HIGH_INCOME},
    "lendingType": {"NC": "LNX"},
    "adminregion": {"MEA": "MNA"},
}

# wbgroup intblock id -> (country field, the field ids whose economies the group lists).
WB_GROUP_BLOCKS: dict[str, tuple[str, frozenset[str]]] = {
    **{rid: ("region", frozenset({rid})) for rid in ("EAS", "ECS", "LCN", "MEA", "NAC", "SAS", "SSF")},
    **{aid: ("adminregion", frozenset({aid})) for aid in ("ECA", "LAC", "MNA", "SSA")},
    **{iid: ("incomeLevel", frozenset({iid})) for iid in ("HIC", "UMC", "LMC", "LIC")},
    "MIC": ("incomeLevel", frozenset({"LMC", "UMC"})),
    "LMY": ("incomeLevel", frozenset({"LIC", "LMC", "UMC"})),
}
_GROUP_QUERY = {"region": "region", "adminregion": "region", "incomeLevel": "incomelevel"}
ROSTER_STATUSES = frozenset({"member", "founding_member"})


def parse_country_classifications(payload: Any) -> dict[str, dict[str, Any]]:
    """ISO alpha-2 -> ``{"wb_id": ..., field: {"id", "value"} | None}`` for every economy.

    ``payload`` is the decoded ``/v2/country?format=json`` response. Aggregates are skipped;
    an empty classification (the Bank's ``{"id": ""}``) becomes ``None``.
    """
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("unexpected World Bank country response")
    meta, rows = payload[0] or {}, payload[1] or []
    if int(meta.get("pages") or 1) > 1:
        raise ValueError("World Bank country response is paginated; request a larger per_page")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        region = row.get("region") or {}
        iso2 = str(row.get("iso2Code") or "").strip().upper()
        if (
            not iso2
            or str(region.get("id") or "") in ("", "NA")
            or str(region.get("value") or "").strip() == "Aggregates"
        ):
            continue
        entry: dict[str, Any] = {"wb_id": str(row.get("id") or "")}
        for field in CLASSIFICATION_FIELDS:
            obj = row.get(field) or {}
            code = str(obj.get("id") or "").strip()
            entry[field] = {"id": code, "value": str(obj.get("value") or "").strip()} if code else None
        out[iso2] = entry
    return out


def _provenance(record: dict[str, Any], field: str) -> dict[str, Any] | None:
    return next((p for p in record.get("provenance") or [] if isinstance(p, dict) and p.get("field") == field), None)


def _set_provenance(record: dict[str, Any], field: str, source: str, url: str, retrieved_at: str) -> None:
    """Replace the field's provenance entry in place (keeps the list order stable)."""
    entry = {"field": field, "source": source, "retrieved_at": retrieved_at, "url": url}
    provenance = record.get("provenance") or []
    for idx, existing in enumerate(provenance):
        if isinstance(existing, dict) and existing.get("field") == field:
            provenance[idx] = entry
            break
    else:
        provenance.append(entry)
    record["provenance"] = provenance


def _drop_field(record: dict[str, Any], field: str) -> None:
    record.pop(field, None)
    if record.get("provenance"):
        record["provenance"] = [
            p for p in record["provenance"] if not (isinstance(p, dict) and p.get("field") == field)
        ]


def apply_world_bank_classification(
    record: dict[str, Any], entry: dict[str, Any], *, retrieved_at: str | None = None
) -> set[str]:
    """Set the four classification fields to the Bank's values; returns the fields that changed.

    A field the Bank leaves empty (``adminregion`` for high-income economies) is removed with its
    provenance. Provenance is restamped only for a changed value or a different source or URL.
    """
    retrieved_at = retrieved_at or date.today().isoformat()
    url = f"{WB_COUNTRY_API}/{entry['wb_id']}"
    changed: set[str] = set()
    for field in CLASSIFICATION_FIELDS:
        value = entry.get(field)
        prov = _provenance(record, field)
        if value is None:
            if field in record or prov:
                _drop_field(record, field)
                changed.add(field)
            continue
        if record.get(field) != value or not prov or prov.get("source") != WB_SOURCE or prov.get("url") != url:
            record[field] = dict(value)
            _set_provenance(record, field, WB_SOURCE, url, retrieved_at)
            changed.add(field)
    return changed


def modernize_classification(record: dict[str, Any]) -> set[str]:
    """Recode an entity the Bank does not classify to current ids and labels.

    Retired ids map to their successors (``OEC``/``NOC`` -> ``HIC``, ``NC`` -> ``LNX``); a
    high-income entity loses ``adminregion``, which the Bank publishes only for low- and
    middle-income economies. Provenance that claims a current Bank retrieval is relabelled
    :data:`WB_HISTORICAL_SOURCE`. Returns the fields that changed.
    """
    changed: set[str] = set()
    for field in ("region", "incomeLevel", "lendingType", "adminregion"):
        obj = record.get(field)
        if not isinstance(obj, dict) or not obj.get("id"):
            continue
        code = LEGACY_IDS.get(field, {}).get(str(obj["id"]), str(obj["id"]))
        value = {"id": code, "value": LABELS[field].get(code, str(obj.get("value") or ""))}
        if value != obj:
            record[field] = value
            changed.add(field)
    if (record.get("incomeLevel") or {}).get("id") == HIGH_INCOME and (
        "adminregion" in record or _provenance(record, "adminregion")
    ):
        _drop_field(record, "adminregion")
        changed.add("adminregion")
    for field in CLASSIFICATION_FIELDS:
        prov = _provenance(record, field)
        if prov and prov.get("source") == WB_SOURCE:
            prov["source"] = WB_HISTORICAL_SOURCE
            changed.add(field)
    return changed


def is_wb_classified(record: dict[str, Any], field: str) -> bool:
    """True when the record's ``field`` comes from the Bank's current classification."""
    prov = _provenance(record, field)
    return bool(record.get(field) and prov and prov.get("source") == WB_SOURCE)


def wb_group_members(countries: Iterable[dict[str, Any]], block_id: str) -> set[str]:
    """Country codes the wbgroup intblock ``block_id`` should list, from the country fields."""
    field, ids = WB_GROUP_BLOCKS[block_id]
    return {
        str(c["code"])
        for c in countries
        if c.get("code") and is_wb_classified(c, field) and (c.get(field) or {}).get("id") in ids
    }


def _is_roster_entry(inc: Any) -> bool:
    return isinstance(inc, dict) and inc.get("type") == "country" and inc.get("status") in ROSTER_STATUSES


def roster_members(block: dict[str, Any]) -> set[str]:
    return {str(inc["id"]) for inc in block.get("includes") or [] if _is_roster_entry(inc) and inc.get("id")}


def is_wb_group_block(block: dict[str, Any]) -> bool:
    blocktypes = block.get("blocktype") or []
    if isinstance(blocktypes, str):
        blocktypes = [blocktypes]
    return str(block.get("id") or "") in WB_GROUP_BLOCKS and "wbgroup" in blocktypes


def sync_wb_group_block(
    block: dict[str, Any], countries_by_code: dict[str, dict[str, Any]], *, retrieved_at: str | None = None
) -> bool:
    """Rebuild a wbgroup roster from the country classifications; returns True when it changed.

    Entries for members that stay keep their fields; every country entry carries the country's
    ``name``, which is what the build exports (``fill_country_include_names``).
    """
    expected = wb_group_members(countries_by_code.values(), str(block["id"]))
    if roster_members(block) == expected:
        return False
    retrieved_at = retrieved_at or date.today().isoformat()
    includes = list(block.get("includes") or [])
    was_sorted = [str(i.get("id")) for i in includes if isinstance(i, dict)] == sorted(
        str(i.get("id")) for i in includes if isinstance(i, dict)
    )
    kept = [inc for inc in includes if not _is_roster_entry(inc) or str(inc.get("id")) in expected]
    for inc in kept:
        country = countries_by_code.get(str(inc.get("id"))) if _is_roster_entry(inc) else None
        if country and country.get("name"):
            inc["name"] = country["name"]
    present = {str(inc["id"]) for inc in kept if _is_roster_entry(inc)}
    for code in sorted(expected - present):
        kept.append(
            {"id": code, "name": countries_by_code[code].get("name", code), "type": "country", "status": "member"}
        )
    if was_sorted:
        kept.sort(key=lambda inc: str(inc.get("id")) if isinstance(inc, dict) else "")
    block["includes"] = kept
    block["membership_count"] = len(expected)
    field, _ = WB_GROUP_BLOCKS[str(block["id"])]
    url = f"{WB_COUNTRY_API}?{_GROUP_QUERY[field]}={block['id']}"
    for prov_field in ("includes", "membership_count"):
        _set_provenance(block, prov_field, WB_GROUP_SOURCE, url, retrieved_at)
    block["last_verified"] = retrieved_at
    return True


def check_wb_group_rosters(
    intblock_records: list[dict[str, Any]],
    intblock_paths: list[str],
    countries_by_code: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """wbgroup rosters must list exactly the economies whose World Bank field puts them there."""
    issues: list[dict[str, Any]] = []
    fix = "run `python scripts/enrich_countries.py refresh-classifications`"
    for record, path in zip(intblock_records, intblock_paths, strict=False):
        if not is_wb_group_block(record):
            continue
        block_id = str(record["id"])
        field, _ = WB_GROUP_BLOCKS[block_id]
        expected = wb_group_members(countries_by_code.values(), block_id)
        actual = roster_members(record)
        for code, listed in [
            *((c, False) for c in sorted(expected - actual)),
            *((c, True) for c in sorted(actual - expected)),
        ]:
            country = countries_by_code.get(code) or {}
            current = (country.get(field) or {}).get("id") or "absent"
            if not listed:
                action = f"{code} has World Bank {field} '{current}' but is not listed in {block_id}; {fix}"
            elif not is_wb_classified(country, field):
                action = f"{block_id} lists {code}, which the World Bank does not classify by {field}; {fix}"
            else:
                action = f"{block_id} lists {code}, whose World Bank {field} is '{current}'; {fix}"
            issues.append(
                {
                    "issue_type": "WB_GROUP_ROSTER_MISMATCH",
                    "field": "includes",
                    "current_value": code,
                    "suggested_action": action,
                    "file_path": path,
                    "record_id": block_id,
                }
            )
    return issues
