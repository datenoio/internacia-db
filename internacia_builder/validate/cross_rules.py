"""Cross-record and cross-dataset data-quality rule checkers.

Single implementation shared by the ``analyze-quality`` report generator and the
CLI validators. Checkers here need visibility across multiple records (or both
datasets) and return structured issue dicts.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

ALPHA2_RE = re.compile(r"^[A-Z]{2}$")

# Reference catalogs where two entities legitimately share a host (the link points
# at the same underlying subject, not a data-entry error).
_DUPLICATE_LINK_IGNORED_HOSTS = (
    "wikipedia.org",
    "wikidata.org",
    "wikimedia.org",
    "dbpedia.org",
)


def _normalize_link(url: str) -> str:
    """Normalize a URL for duplicate comparison: drop scheme, leading www, and
    trailing slashes; lowercase the host."""
    u = url.strip().lower()
    for scheme in ("https://", "http://", "//"):
        if u.startswith(scheme):
            u = u[len(scheme) :]
            break
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


def _related_ids(rec: dict[str, Any]) -> set[str]:
    """Ids this record is hierarchically related to (parent/child orgs), which may
    legitimately share an official website."""
    related: set[str] = set()
    partof = rec.get("partof")
    if isinstance(partof, str):
        related.add(partof)
    elif isinstance(partof, dict):
        related.add(str(partof.get("id", "")))
    elif isinstance(partof, list):
        for p in partof:
            related.add(str(p.get("id", "")) if isinstance(p, dict) else str(p))
    for sub in rec.get("suborganizations") or []:
        if isinstance(sub, dict) and sub.get("id"):
            related.add(str(sub["id"]))
    for key in ("predecessor", "successor"):
        if rec.get(key):
            related.add(str(rec[key]))
    related.discard("")
    return related


def check_duplicate_links(rel_paths: list[str], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Report only *true* duplicate external links.

    A duplicate is flagged when the same normalized ``website`` URL is used by two
    or more records that are not hierarchically related. Synthetic TLD pseudo-links,
    reference-catalog hosts (Wikipedia/Wikidata), and shared links among related
    organizations are excluded to keep the report signal-heavy.
    """
    link_to_records: dict[str, list[tuple[str, str, set[str]]]] = {}
    for path, rec in zip(rel_paths, records, strict=False):
        rid = str(rec.get("code") or rec.get("id") or "unknown")
        related = _related_ids(rec)
        for link in rec.get("links") or []:
            if not isinstance(link, dict) or not link.get("url"):
                continue
            if link.get("type") not in (None, "website"):
                continue
            norm = _normalize_link(str(link["url"]))
            if not norm or any(host in norm for host in _DUPLICATE_LINK_IGNORED_HOSTS):
                continue
            link_to_records.setdefault(norm, []).append((path, rid, related))

    issues: list[dict[str, Any]] = []
    for norm, metas in link_to_records.items():
        ids = {rid for _, rid, _ in metas}
        if len(ids) < 2:
            continue
        # Suppress when every record in the group is related to every other.
        all_related = all(
            ids - {rid} <= related for _, rid, related in metas
        )
        if all_related:
            continue
        sharers = sorted(ids)
        for path, rid, _ in metas:
            issues.append({
                "issue_type": "DUPLICATE_LINK",
                "field": "links",
                "current_value": norm,
                "suggested_action": f"Website '{norm}' is shared by unrelated records: {sharers}",
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_duplicate_wikidata_ids(
    rel_paths: list[str],
    records: list[dict[str, Any]],
    allowlist: set[str] | None = None,
) -> list[dict[str, Any]]:
    """A wikidata_id must identify at most one record across both datasets.

    Q-ids in the allowlist (configured under ``references.wikidata_duplicate_allowlist``
    in ``intblocks_completeness.yaml``) are suppressed — e.g. concept-level items
    intentionally shared by several records.
    """
    allowlist = allowlist or set()
    by_qid: dict[str, list[tuple[str, str]]] = {}
    for path, rec in zip(rel_paths, records, strict=False):
        qid = rec.get("wikidata_id")
        if not qid or str(qid) in allowlist:
            continue
        rid = str(rec.get("code") or rec.get("id") or "unknown")
        by_qid.setdefault(str(qid), []).append((path, rid))

    issues: list[dict[str, Any]] = []
    for qid, metas in by_qid.items():
        if len({rid for _, rid in metas}) < 2:
            continue
        sharers = sorted({rid for _, rid in metas})
        for path, rid in metas:
            issues.append({
                "issue_type": "DUPLICATE_WIKIDATA_ID",
                "field": "wikidata_id",
                "current_value": qid,
                "suggested_action": f"wikidata_id '{qid}' is shared by records: {sharers}; each record needs its own Q-id",
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_border_resolution(
    records: list[dict[str, Any]], rel_paths: list[str]
) -> list[dict[str, Any]]:
    """Every border alpha-3 must resolve to an existing country's iso3code and
    must not reference the record itself."""
    known_iso3 = {str(r.get("iso3code", "")) for r in records if r.get("iso3code")}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        own = str(rec.get("iso3code", ""))
        record_id = rec.get("code", "unknown")
        for b in rec.get("borders") or []:
            border = str(b)
            if border == own:
                issues.append({
                    "issue_type": "UNRESOLVED_BORDER_REFERENCE",
                    "field": "borders",
                    "current_value": border,
                    "suggested_action": f"border '{border}' references the record itself",
                    "file_path": path,
                    "record_id": record_id,
                })
            elif border not in known_iso3:
                issues.append({
                    "issue_type": "UNRESOLVED_BORDER_REFERENCE",
                    "field": "borders",
                    "current_value": border,
                    "suggested_action": f"border '{border}' does not match any country iso3code",
                    "file_path": path,
                    "record_id": record_id,
                })
    return issues


def check_border_reciprocity(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    allowlist: set[tuple[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """If A lists B as a border, B should list A. Allowlisted (A, B) iso3 pairs
    are suppressed (each direction is listed explicitly)."""
    allowlist = allowlist or set()
    by_iso3 = {str(r.get("iso3code", "")): r for r in records if r.get("iso3code")}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        own = str(rec.get("iso3code", ""))
        if not own:
            continue
        record_id = rec.get("code", "unknown")
        for b in rec.get("borders") or []:
            border = str(b)
            other = by_iso3.get(border)
            if other is None or border == own:
                continue  # unresolved/self borders are reported by check_border_resolution
            if own in (other.get("borders") or []):
                continue
            if (own, border) in allowlist:
                continue
            issues.append({
                "issue_type": "NONRECIPROCAL_BORDER",
                "field": "borders",
                "current_value": border,
                "suggested_action": (
                    f"'{record_id}' lists '{border}' as a border but '{border}' does not list "
                    f"'{own}' back; fix the neighbor or allowlist the pair"
                ),
                "file_path": path,
                "record_id": record_id,
            })
    return issues


def load_border_reciprocity_allowlist(config: dict[str, Any]) -> set[tuple[str, str]]:
    """Parse `borders.reciprocity_allowlist` entries of the form 'ABC-XYZ'
    (meaning: ABC may list XYZ without XYZ listing ABC back)."""
    raw = (config.get("borders") or {}).get("reciprocity_allowlist") or []
    pairs: set[tuple[str, str]] = set()
    for entry in raw:
        parts = str(entry).split("-")
        if len(parts) == 2:
            pairs.add((parts[0].strip(), parts[1].strip()))
    return pairs


def check_wikidata_completeness(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    exclusions: set[str],
) -> list[dict[str, Any]]:
    """Every intblock needs wikidata_id unless listed on the exclusion registry."""
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        record_id = str(rec.get("id") or "unknown")
        if rec.get("wikidata_id"):
            continue
        if record_id in exclusions:
            continue
        issues.append(
            {
                "issue_type": "MISSING_WIKIDATA_ID",
                "field": "wikidata_id",
                "current_value": "",
                "suggested_action": (
                    "Add wikidata_id or document the record on data/schemas/wikidata_exclusions.yaml"
                ),
                "file_path": path,
                "record_id": record_id,
            }
        )
    return issues


ORG_PARENT_BLOCKTYPES = frozenset(
    {
        "political",
        "intorg",
        "unagency",
        "forum",
        "parliamentary",
        "court",
        "bank",
        "fund",
        "meteorology",
        "standards",
        "transport",
        "postal",
        "research",
    }
)


def _is_treaty_like(rec: dict[str, Any]) -> bool:
    blocktypes = {str(bt).lower() for bt in (rec.get("blocktype") or [])}
    legal = str(rec.get("legal_status") or "").lower()
    return legal == "treaty" or "agreement" in blocktypes


def check_partof_hierarchy(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    """partof must not reference pure treaty/agreement records (organizational hierarchy only)."""
    by_id = {str(rec.get("id", "")): rec for rec in records if rec.get("id")}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        record_id = rec.get("id", "unknown")
        partof = rec.get("partof")
        if not partof:
            continue
        refs: list[str]
        if isinstance(partof, str):
            refs = [partof]
        elif isinstance(partof, list):
            refs = [str(p.get("id", "")) if isinstance(p, dict) else str(p) for p in partof]
        else:
            continue
        source_blocktypes = {str(bt).lower() for bt in (rec.get("blocktype") or [])}
        source_is_treaty = _is_treaty_like(rec)
        for ref in refs:
            if not ref:
                continue
            target = by_id.get(ref)
            if not target:
                continue
            target_blocktypes = {str(bt).lower() for bt in (target.get("blocktype") or [])}
            if target_blocktypes & ORG_PARENT_BLOCKTYPES:
                continue
            if source_is_treaty and _is_treaty_like(target):
                continue
            if "fund" in source_blocktypes and _is_treaty_like(target):
                continue
            if _is_treaty_like(target):
                issues.append(
                    {
                        "issue_type": "INVALID_PARTOF_TARGET",
                        "field": "partof",
                        "current_value": ref,
                        "suggested_action": (
                            f"partof reference '{ref}' is a treaty/agreement, not an organizational parent; "
                            "document the relationship in description/notes instead"
                        ),
                        "file_path": path,
                        "record_id": record_id,
                    }
                )
    return issues


def validate_partof_refs(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    errors = []
    known_ids = {str(rec.get("id", "")) for rec in records if rec.get("id")}
    for path, rec in zip(rel_paths, records, strict=False):
        record_id = rec.get("id", "unknown")
        partof = rec.get("partof")
        if partof is None:
            continue
        if isinstance(partof, str):
            refs = [partof]
        elif isinstance(partof, dict):
            refs = [str(partof.get("id", ""))]
        elif isinstance(partof, list):
            refs = [str(p.get("id", "")) if isinstance(p, dict) else str(p) for p in partof]
        else:
            continue
        for ref in refs:
            if ref and ref not in known_ids:
                errors.append({
                    "issue_type": "UNRESOLVED_PARTOF_REF",
                    "field": "partof",
                    "current_value": ref,
                    "suggested_action": f"partof reference '{ref}' does not match any known intblock id",
                    "file_path": path,
                    "record_id": record_id
                })
    return errors


def check_org_refs(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    alias_names: set[str] | None = None,
    allowlist: set[str] | None = None,
) -> list[dict[str, Any]]:
    """predecessor/successor/suborganizations ids must resolve to known intblock
    ids, registered aliases, or allowlisted affiliated bodies (configured under
    ``references.org_ref_allowlist`` in ``intblocks_completeness.yaml``)."""
    alias_names = alias_names or set()
    known_ids = {str(rec.get("id", "")) for rec in records if rec.get("id")}
    resolvable = known_ids | alias_names | (allowlist or set())
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        record_id = rec.get("id", "unknown")
        for key in ("predecessor", "successor"):
            ref = rec.get(key)
            if ref and str(ref) not in resolvable:
                issues.append({
                    "issue_type": "UNRESOLVED_ORG_REF",
                    "field": key,
                    "current_value": str(ref),
                    "suggested_action": f"{key} '{ref}' does not match any intblock id or alias",
                    "file_path": path,
                    "record_id": record_id,
                })
        for idx, sub in enumerate(rec.get("suborganizations") or []):
            if not isinstance(sub, dict):
                continue
            sid = str(sub.get("id", ""))
            if sid and sid not in resolvable:
                issues.append({
                    "issue_type": "UNRESOLVED_ORG_REF",
                    "field": f"suborganizations[{idx}].id",
                    "current_value": sid,
                    "suggested_action": f"suborganization '{sid}' does not match any intblock id or alias",
                    "file_path": path,
                    "record_id": record_id,
                })
    return issues


def _partof_id_list(rec: dict[str, Any]) -> list[str]:
    """Normalized partof references (string, dict, or list forms)."""
    partof = rec.get("partof")
    if isinstance(partof, str):
        refs = [partof]
    elif isinstance(partof, dict):
        refs = [str(partof.get("id", ""))]
    elif isinstance(partof, list):
        refs = [str(p.get("id", "")) if isinstance(p, dict) else str(p) for p in partof]
    else:
        refs = []
    return [r for r in refs if r]


def check_successor_reciprocity(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    """When A.successor resolves to B, B.predecessor must reference A back
    (and vice versa). Unresolved references are reported by UNRESOLVED_ORG_REF.

    Only an *empty* inverse field is flagged: predecessor/successor are
    single-valued, so a record absorbed from several organizations can point
    back at just one of them.
    """
    by_id = {str(r.get("id", "")): r for r in records if r.get("id")}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        rid = str(rec.get("id", ""))
        for field, inverse in (("successor", "predecessor"), ("predecessor", "successor")):
            ref = rec.get(field)
            if not ref:
                continue
            other = by_id.get(str(ref))
            if other is None or other.get(inverse):
                continue
            issues.append({
                "issue_type": "SUCCESSOR_RECIPROCITY",
                "field": field,
                "current_value": str(ref),
                "suggested_action": (
                    f"'{rid}' lists {field} '{ref}' but '{ref}' does not list "
                    f"{inverse} '{rid}' back; add the reverse reference"
                ),
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_partof_suborg_reciprocity(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    """A child listed in a parent's suborganizations must declare that parent in
    partof. The inverse is not required: umbrella organizations do not enumerate
    every affiliated body."""
    path_by_id = {
        str(r.get("id", "")): p for p, r in zip(rel_paths, records, strict=False) if r.get("id")
    }
    by_id = {str(r.get("id", "")): r for r in records if r.get("id")}
    issues: list[dict[str, Any]] = []
    for _, rec in zip(rel_paths, records, strict=False):
        parent_id = str(rec.get("id", ""))
        for sub in rec.get("suborganizations") or []:
            if not isinstance(sub, dict):
                continue
            child_id = str(sub.get("id", ""))
            child = by_id.get(child_id)
            if child is None:  # unresolved ids are reported by UNRESOLVED_ORG_REF
                continue
            if parent_id in _partof_id_list(child):
                continue
            issues.append({
                "issue_type": "PARTOF_SUBORG_RECIPROCITY",
                "field": "partof",
                "current_value": str(child.get("partof")),
                "suggested_action": (
                    f"'{parent_id}' lists '{child_id}' in suborganizations but "
                    f"'{child_id}' does not declare partof '{parent_id}'"
                ),
                "file_path": path_by_id.get(child_id, "cross-record"),
                "record_id": child_id,
            })
    return issues


def check_parent_entity_refs(
    records: list[dict[str, Any]],
    rel_paths: list[str],
) -> list[dict[str, Any]]:
    """countries: parent_entity.code must resolve to an existing country record."""
    known = {str(r.get("code", "")) for r in records if r.get("code")}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        parent = rec.get("parent_entity")
        if not isinstance(parent, dict):
            continue
        code = str(parent.get("code") or "")
        if not code or code in known:
            continue
        issues.append({
            "issue_type": "UNRESOLVED_PARENT_ENTITY",
            "field": "parent_entity.code",
            "current_value": code,
            "suggested_action": f"parent_entity '{code}' does not match any country record",
            "file_path": path,
            "record_id": rec.get("code", "unknown"),
        })
    return issues


def check_hq_coordinates(
    intblocks_records: list[dict[str, Any]],
    intblocks_paths: list[str],
    countries_by_code: dict[str, dict[str, Any]],
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """headquarters.coordinates must lie within an area-scaled distance of the
    HQ country's centroid; catches swapped or mis-signed coordinates."""
    from internacia_builder.validate.country_rules import (
        _coord_pair,
        allowed_distance_km,
        haversine_km,
    )

    rule = ((config or {}).get("geography") or {}).get("hq_distance") or {}
    allowlist = {str(x) for x in (rule.get("allowlist") or [])}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(intblocks_paths, intblocks_records, strict=False):
        rid = str(rec.get("id", "unknown"))
        if rid in allowlist:
            continue
        hq = rec.get("headquarters")
        if not isinstance(hq, dict):
            continue
        coords = _coord_pair(hq.get("coordinates"))
        country = countries_by_code.get(str(hq.get("country") or "").strip())
        if coords is None or country is None:
            continue
        centroid = _coord_pair(country.get("centroid"))
        if centroid is None:
            continue
        dist = haversine_km(coords[0], coords[1], centroid[0], centroid[1])
        area = country.get("area") if isinstance(country.get("area"), dict) else {}
        allowed = allowed_distance_km(
            (area or {}).get("value"),
            min_km=float(rule.get("min_km", 500)),
            area_multiplier=float(rule.get("area_multiplier", 2.5)),
            default_km=float(rule.get("default_km", 1500)),
        )
        if dist > allowed:
            issues.append({
                "issue_type": "HQ_COORDINATES_OUTSIDE_COUNTRY",
                "field": "headquarters.coordinates",
                "current_value": f"lat={coords[0]}, lng={coords[1]}",
                "suggested_action": (
                    f"headquarters coordinates are {dist:.0f} km from the centroid of "
                    f"'{hq.get('country')}' (allowed {allowed:.0f} km); check for swapped lat/lng"
                ),
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_duplicate_acronyms(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    allowlist: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Advisory: unrelated records sharing an English acronym and a blocktype
    may be duplicate entities. Real-world collisions go in
    ``references.acronym_duplicate_allowlist`` of intblocks_completeness.yaml."""
    allowlist = allowlist or set()
    by_acronym: dict[str, list[tuple[str, str]]] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for path, rec in zip(rel_paths, records, strict=False):
        rid = str(rec.get("id", ""))
        if not rid:
            continue
        by_id[rid] = rec
        for entry in rec.get("acronyms") or []:
            if not isinstance(entry, dict) or entry.get("lang") != "en":
                continue
            value = str(entry.get("value") or "").strip()
            if value and value not in allowlist:
                by_acronym.setdefault(value, []).append((path, rid))

    issues: list[dict[str, Any]] = []
    for acronym, metas in by_acronym.items():
        ids = {rid for _, rid in metas}
        if len(ids) < 2:
            continue
        # Suppress when every sharer is related to every other (parent/child,
        # predecessor/successor pairs legitimately share acronyms).
        if all(ids - {rid} <= _related_ids(by_id[rid]) for rid in ids):
            continue
        # Only flag when the records overlap in blocktype: a bank and a sports
        # federation sharing three letters is coincidence, not duplication.
        blocktype_sets = [set(by_id[rid].get("blocktype") or []) for rid in ids]
        if not set.intersection(*blocktype_sets):
            continue
        sharers = sorted(ids)
        for path, rid in metas:
            issues.append({
                "issue_type": "DUPLICATE_ACRONYM",
                "field": "acronyms",
                "current_value": acronym,
                "suggested_action": (
                    f"English acronym '{acronym}' is shared by same-blocktype records {sharers}; "
                    "merge duplicates or allowlist the acronym"
                ),
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_historical_entity_members(
    intblocks_records: list[dict[str, Any]],
    intblocks_paths: list[str],
    countries_by_code: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """A non-historical block must not carry a historical entity country
    (e.g. a dissolved state) with an active-class include status."""
    from internacia_builder.validate.intblock_rules import ACTIVE_CLASS_STATUSES

    issues: list[dict[str, Any]] = []
    for path, rec in zip(intblocks_paths, intblocks_records, strict=False):
        if rec.get("status") == "historical":
            continue
        rid = str(rec.get("id", "unknown"))
        for idx, inc in enumerate(rec.get("includes") or []):
            if not isinstance(inc, dict) or inc.get("type") != "country":
                continue
            country = countries_by_code.get(str(inc.get("id") or ""))
            if not country or country.get("entity_type") != "historical_entity":
                continue
            if str(inc.get("status", "")) not in ACTIVE_CLASS_STATUSES:
                continue
            issues.append({
                "issue_type": "HISTORICAL_ENTITY_ACTIVE_MEMBER",
                "field": f"includes[{idx}].status",
                "current_value": str(inc.get("status")),
                "suggested_action": (
                    f"'{inc.get('id')}' is a historical entity but is listed with active "
                    f"status '{inc.get('status')}'; use former_member or remove the entry"
                ),
                "file_path": path,
                "record_id": rid,
            })
    return issues


def check_hq_country(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    country_codes: set[str],
    allowlist: set[str] | None = None,
) -> list[dict[str, Any]]:
    """headquarters.country must resolve to an existing country file or an
    allowlisted special entity."""
    allowlist = allowlist or set()
    issues: list[dict[str, Any]] = []
    for path, rec in zip(rel_paths, records, strict=False):
        hq = rec.get("headquarters")
        if not isinstance(hq, dict):
            continue
        raw = hq.get("country")
        if not raw:
            continue
        code = str(raw).strip()
        if code in country_codes or code in allowlist:
            continue
        issues.append({
            "issue_type": "UNRESOLVED_HQ_COUNTRY",
            "field": "headquarters.country",
            "current_value": code,
            "suggested_action": f"headquarters country '{code}' does not match any country file",
            "file_path": path,
            "record_id": rec.get("id", "unknown"),
        })
    return issues


def validate_aliases(
    aliases: list[dict[str, Any]],
    known_ids: set[str],
) -> list[dict[str, Any]]:
    errors = []
    seen_aliases = set()
    for entry in aliases:
        if not isinstance(entry, dict):
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": str(entry),
                "suggested_action": "Alias entry must be a dictionary"
            })
            continue
        alias = str(entry.get("alias") or "")
        target = str(entry.get("target") or "")
        reason = str(entry.get("reason") or "")
        if not alias or not target:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": f"alias={alias}, target={target}",
                "suggested_action": "Alias entry must contain non-empty alias and target fields"
            })
            continue
        if alias in seen_aliases:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": alias,
                "suggested_action": f"Duplicate alias entry for '{alias}'"
            })
        seen_aliases.add(alias)
        if reason not in {"renamed", "merged", "disambiguated"}:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": reason,
                "suggested_action": f"Alias '{alias}': invalid reason '{reason}' (must be renamed, merged, or disambiguated)"
            })
        if target not in known_ids:
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": target,
                "suggested_action": f"Alias '{alias}' target '{target}' does not match any existing intblock id"
            })
        if alias in known_ids and reason != "disambiguated":
            errors.append({
                "issue_type": "ALIAS_INTEGRITY_ERROR",
                "field": "aliases",
                "current_value": alias,
                "suggested_action": f"Alias '{alias}' collides with a current intblock id; mark reason 'disambiguated'"
            })
    return errors


ATTRIBUTE_MIGRATION_FIELDS = frozenset(
    {
        "car_side",
        "writing_directions",
        "writing_systems",
        "dvd_region",
        "broadcast_systems",
        "legal_systems",
        "rail_gauges",
    }
)


def validate_attribute_intblock_migrations(
    migrations: list[dict[str, Any]],
    known_intblock_ids: set[str],
) -> list[dict[str, Any]]:
    """Validate retirements of attribute-partition intblocks to country fields/vocabs."""
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in migrations:
        if not isinstance(entry, dict):
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "attribute_intblock_migrations",
                    "current_value": str(entry),
                    "suggested_action": "Migration entry must be a dictionary",
                }
            )
            continue
        rid = str(entry.get("retired_id") or "")
        if not rid:
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "retired_id",
                    "current_value": "",
                    "suggested_action": "Migration entry must include retired_id",
                }
            )
            continue
        if rid in seen:
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "retired_id",
                    "current_value": rid,
                    "suggested_action": f"Duplicate migration entry for '{rid}'",
                }
            )
        seen.add(rid)
        if rid in known_intblock_ids:
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "retired_id",
                    "current_value": rid,
                    "suggested_action": (
                        f"retired_id '{rid}' still exists as a current intblock; "
                        "delete the intblock or remove the migration entry"
                    ),
                }
            )
        disposition = entry.get("disposition")
        if disposition == "vocab_only":
            if not entry.get("vocab"):
                errors.append(
                    {
                        "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                        "field": "vocab",
                        "current_value": rid,
                        "suggested_action": f"vocab_only retirement '{rid}' must set vocab",
                    }
                )
            continue
        field = str(entry.get("country_field") or "")
        if field not in ATTRIBUTE_MIGRATION_FIELDS:
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "country_field",
                    "current_value": field or "(missing)",
                    "suggested_action": (
                        f"Migration '{rid}' country_field must be one of "
                        f"{sorted(ATTRIBUTE_MIGRATION_FIELDS)} or disposition vocab_only"
                    ),
                }
            )
            continue
        if field == "car_side" and entry.get("country_value") not in {"left", "right"}:
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "country_value",
                    "current_value": str(entry.get("country_value")),
                    "suggested_action": f"Migration '{rid}' car_side value must be left or right",
                }
            )
        if field == "dvd_region":
            val = entry.get("country_value")
            if not isinstance(val, int) or isinstance(val, bool) or val < 1 or val > 6:
                errors.append(
                    {
                        "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                        "field": "country_value",
                        "current_value": str(val),
                        "suggested_action": f"Migration '{rid}' dvd_region value must be 1..6",
                    }
                )
        if field in {
            "writing_directions",
            "writing_systems",
            "broadcast_systems",
            "legal_systems",
            "rail_gauges",
        } and not entry.get("country_value_id"):
            errors.append(
                {
                    "issue_type": "ATTRIBUTE_MIGRATION_ERROR",
                    "field": "country_value_id",
                    "current_value": rid,
                    "suggested_action": f"Migration '{rid}' must set country_value_id",
                }
            )
    return errors


def validate_intblock_refs(
    countries_dir: Path,
    intblocks_records: list[dict[str, Any]],
    intblocks_paths: list[str],
    completeness_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    errors = []
    allowlist = set(completeness_cfg.get("special_entity_allowlist") or [])
    issue_type = "UNRESOLVED_COUNTRY_INCLUDE"

    for path, data in zip(intblocks_paths, intblocks_records, strict=False):
        record_id = data.get("id", "unknown")
        for inc in data.get("includes") or []:
            if not isinstance(inc, dict) or inc.get("type") != "country":
                continue
            raw_id = inc.get("id", "")
            if isinstance(raw_id, bool):
                continue
            cid = str(raw_id).strip()
            if not ALPHA2_RE.match(cid):
                continue
            country_file = countries_dir / f"{cid}.yaml"
            if country_file.exists() or cid in allowlist:
                continue

            errors.append({
                "issue_type": issue_type,
                "field": "includes",
                "current_value": cid,
                "suggested_action": f"Country include '{cid}' does not match any valid country file",
                "file_path": path,
                "record_id": record_id
            })
    return errors


def _normalize_display_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return text


def _name_keys(name: str) -> set[str]:
    """Comparison keys for a country display name.

    Besides plain normalization, generate rotations for UN-style inverted forms so
    'Korea, Republic of' and 'Bolivia (Plurinational State of)' match
    'Republic of Korea' and 'Plurinational State of Bolivia'.
    """
    forms = {name}
    m = re.match(r"^([^,(]+),\s*(.+)$", name)
    if m:
        forms.add(f"{m.group(2).strip()} {m.group(1).strip()}")
    m = re.match(r"^([^(]+)\(([^)]+)\)\s*$", name)
    if m:
        forms.add(f"{m.group(2).strip()} {m.group(1).strip()}")
    return {_normalize_display_name(f) for f in forms if f}


def _country_name_variants(country: dict[str, Any]) -> set[str]:
    names = {str(country.get("name", "")), str(country.get("official_name", ""))}
    names |= {str(x) for x in (country.get("common_names") or [])}
    names |= {
        str(o.get("name", ""))
        for o in (country.get("other_names") or [])
        if isinstance(o, dict)
    }
    for nn in (country.get("native_names") or {}).values():
        if isinstance(nn, dict):
            names |= {str(nn.get("official", "")), str(nn.get("common", ""))}
    variants: set[str] = set()
    for n in names:
        if n:
            variants |= _name_keys(n)
    return variants


def check_include_name_mismatch(
    intblocks_records: list[dict[str, Any]],
    intblocks_paths: list[str],
    countries_by_code: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Advisory: includes[].name differs from every known name variant of the
    referenced country. `name` is display-only per the includes contract, so
    this never fails validation."""
    variants_cache: dict[str, set[str]] = {}
    issues: list[dict[str, Any]] = []
    for path, rec in zip(intblocks_paths, intblocks_records, strict=False):
        record_id = rec.get("id", "unknown")
        for idx, inc in enumerate(rec.get("includes") or []):
            if not isinstance(inc, dict) or inc.get("type") != "country":
                continue
            cid = str(inc.get("id", "")).strip().upper()
            display = str(inc.get("name", "")).strip()
            country = countries_by_code.get(cid)
            if not country or not display:
                continue
            if cid not in variants_cache:
                variants_cache[cid] = _country_name_variants(country)
            if _name_keys(display) & variants_cache[cid]:
                continue
            issues.append({
                "issue_type": "INCLUDE_NAME_MISMATCH",
                "field": f"includes[{idx}].name",
                "current_value": display,
                "suggested_action": (
                    f"include name '{display}' differs from canonical "
                    f"'{country.get('name')}' for {cid} (display-only; advisory)"
                ),
                "file_path": path,
                "record_id": record_id,
            })
    return issues
