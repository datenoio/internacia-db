"""Intblock data-quality rule checkers.

Single implementation shared by the ``analyze-quality`` report generator and the
``validate_intblocks`` CLI. Each checker returns structured issue dicts with
``issue_type``, ``field``, ``current_value``, and ``suggested_action`` keys
(cross-record checkers also set ``file_path``/``record_id``).
"""

from __future__ import annotations

import re
import time
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema

from internacia_builder.validate.completeness import (
    PRIORITY_TO_LEVEL,
    is_null_intblock_field,
)

WIKIDATA_RE = re.compile(r"^Q\d+$")
DATE_RE = re.compile(r"^(\d{4})(?:s)?(?:-(\d{2}))?(?:-(\d{2}))?$")

TEMPLATED_DESC_RE = re.compile(
    r"^\s*(international entity focused on|an? international (organization|entity)|"
    r"regional (organization|entity) focused on|international organization for)",
    re.IGNORECASE,
)

# Include statuses that count toward a member-style headcount when checking
# membership_count. Observers/partners/suspended members are often excluded
# from official membership figures.
MEMBER_CLASS_STATUSES = frozenset(
    {"member", "founding_member", "associate_member", "associate", "associated"}
)

# Statuses that assert current, active participation. Used to flag historical
# entity countries (e.g. dissolved states) still carried as active members.
ACTIVE_CLASS_STATUSES = MEMBER_CLASS_STATUSES | {"participant"}


SCOPE_CATEGORIES = frozenset(
    {
        "igo",
        "treaty_body",
        "policy_forum",
        "reference_enumeration",
        "intergovernmental_body",
        "non_state_organization",
    }
)

# Statuses that deny the formal, institutional standing an IGO requires.
NON_INSTITUTIONAL_STATUSES = frozenset({"informal", "de-facto"})

# legal_status wording that states a non-state legal form (NGO, non-profit, charity, private
# body, industry or trade association, union federation). Bare "association", "partnership" or
# "network" are not markers: associations of public authorities are a policy question.
NON_STATE_LEGAL_STATUS_RE = re.compile(
    r"\b(non-?governmental|ngo|non-?profit|not-for-profit|charity|private|"
    r"industry[ _]association|trade association|business association|civil association|"
    r"union federation)\b",
    re.IGNORECASE,
)

# scope_category values whose records may carry institutional_design: the object describes
# intergovernmental authority, so named country sets and non-state bodies cannot have it.
INSTITUTIONAL_DESIGN_SCOPES = frozenset({"igo", "treaty_body", "policy_forum", "intergovernmental_body"})

# institutional_design list subfields in which "none" must be the only value.
EXCLUSIVE_NONE_FIELDS = ("independent_organs", "enforcement")

# Include statuses of a current full member, for veto_holders resolution.
CURRENT_MEMBER_STATUSES = frozenset({"member", "founding_member"})

# Decision rules under which every member can block, so no member holds an extra veto.
BLOCKING_DECISION_RULES = frozenset({"consensus", "unanimity"})


def check_intblock_scope_category(
    record: dict[str, Any], igo_legal_status_allowlist: frozenset[str] | set[str] = frozenset()
) -> list[dict[str, Any]]:
    """Validate scope_category syntax, known semantics, and status consistency.

    ``igo_legal_status_allowlist`` lists reviewed IDs whose ``legal_status`` wording looks
    non-state but whose ``igo`` category is kept pending a policy decision.
    """
    category = record.get("scope_category")
    blocktypes = {str(value) for value in (record.get("blocktype") or [])}

    if category and str(category) not in SCOPE_CATEGORIES:
        return [{
            "issue_type": "UNKNOWN_SCOPE_CATEGORY",
            "field": "scope_category",
            "current_value": str(category),
            "suggested_action": (
                f"scope_category '{category}' is unknown; use one of "
                f"{sorted(SCOPE_CATEGORIES)}"
            ),
        }]

    if "wbgroup" in blocktypes and category != "reference_enumeration":
        return [{
            "issue_type": "SCOPE_CATEGORY_SEMANTIC_MISMATCH",
            "field": "scope_category",
            "current_value": str(category or ""),
            "suggested_action": (
                "World Bank classification groups must use "
                "scope_category 'reference_enumeration', not an organization category"
            ),
        }]

    legal_status = str(record.get("legal_status") or "")
    if (
        category == "igo"
        and NON_STATE_LEGAL_STATUS_RE.search(legal_status)
        and str(record.get("id") or "") not in igo_legal_status_allowlist
    ):
        return [{
            "issue_type": "SCOPE_CATEGORY_SEMANTIC_MISMATCH",
            "field": "scope_category",
            "current_value": str(category),
            "suggested_action": (
                f"legal_status '{legal_status}' states a non-state legal form, which contradicts "
                "scope_category 'igo'; use 'non_state_organization' (or another category) with a "
                "cited source, or add the id to scope_category.igo_legal_status_allowlist in "
                "intblocks_completeness.yaml after review (see docs/intblock-inclusion-policy.md)"
            ),
        }]

    status = record.get("status")
    if category == "igo" and status in NON_INSTITUTIONAL_STATUSES:
        return [{
            "issue_type": "SCOPE_CATEGORY_STATUS_CONFLICT",
            "field": "scope_category",
            "current_value": str(category),
            "suggested_action": (
                f"status '{status}' contradicts scope_category 'igo', which requires "
                "independent institutional identity; use 'policy_forum' or "
                "'reference_enumeration' (see docs/intblock-inclusion-policy.md)"
            ),
        }]

    if status == "formal" and not category:
        return [{
            "issue_type": "MISSING_SCOPE_CATEGORY",
            "field": "scope_category",
            "current_value": "",
            "suggested_action": (
                "formal record missing scope_category "
                "(see docs/intblock-inclusion-policy.md)"
            ),
        }]

    return []


def _current_country_members(record: dict[str, Any]) -> set[str]:
    """Alpha-2 codes of current full country members (no ``left`` date)."""
    members: set[str] = set()
    for include in record.get("includes") or []:
        if not isinstance(include, dict) or include.get("left"):
            continue
        if (include.get("type") or "country") != "country":
            continue
        if include.get("status") in CURRENT_MEMBER_STATUSES and include.get("id"):
            members.add(str(include["id"]))
    return members


def check_intblock_institutional_design(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Structural rules for ``institutional_design`` that JSON Schema cannot express.

    Enum values, list uniqueness and unknown keys are JSON Schema errors. This rule checks
    the entity kind, exclusive ``none`` values, veto holders against the current roster,
    and the required provenance entry (see data/schemas/institutional_design.yaml).
    """
    design = record.get("institutional_design")
    if not isinstance(design, dict):
        return []
    issues: list[dict[str, Any]] = []

    category = record.get("scope_category")
    if category not in INSTITUTIONAL_DESIGN_SCOPES:
        issues.append({
            "issue_type": "INSTITUTIONAL_DESIGN_SCOPE_CONFLICT",
            "field": "institutional_design",
            "current_value": str(category or ""),
            "suggested_action": (
                f"scope_category '{category or ''}' cannot carry institutional_design; it is allowed "
                f"only on {sorted(INSTITUTIONAL_DESIGN_SCOPES)}"
            ),
        })

    for name in EXCLUSIVE_NONE_FIELDS:
        values = design.get(name)
        if isinstance(values, list) and "none" in values and len(values) > 1:
            issues.append({
                "issue_type": "INSTITUTIONAL_DESIGN_NONE_CONFLICT",
                "field": f"institutional_design.{name}",
                "current_value": ",".join(str(v) for v in values),
                "suggested_action": f"'none' must be the only value of institutional_design.{name}",
            })

    veto_holders = design.get("veto_holders")
    if isinstance(veto_holders, list) and veto_holders:
        members = _current_country_members(record)
        for code in veto_holders:
            if str(code) not in members:
                issues.append({
                    "issue_type": "INVALID_VETO_HOLDER",
                    "field": "institutional_design.veto_holders",
                    "current_value": str(code),
                    "suggested_action": (
                        f"veto holder '{code}' is not a current country member of the record "
                        "(includes entry with status member or founding_member and no left date)"
                    ),
                })

    has_provenance = any(
        isinstance(entry, dict)
        and (str(entry.get("field") or "") == "institutional_design"
             or str(entry.get("field") or "").startswith("institutional_design."))
        for entry in record.get("provenance") or []
    )
    if not has_provenance:
        issues.append({
            "issue_type": "MISSING_INSTITUTIONAL_DESIGN_PROVENANCE",
            "field": "institutional_design",
            "current_value": "",
            "suggested_action": (
                "add a provenance entry with field 'institutional_design' (or "
                "'institutional_design.<subfield>') citing the founding instrument or rules of procedure"
            ),
        })
    return issues


def check_intblock_veto_under_consensus(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Warn when veto holders are listed for a body where every member can already block."""
    design = record.get("institutional_design")
    if not isinstance(design, dict):
        return []
    rule = design.get("decision_rule")
    if design.get("veto_holders") and rule in BLOCKING_DECISION_RULES:
        return [{
            "issue_type": "VETO_HOLDERS_UNDER_CONSENSUS",
            "field": "institutional_design.veto_holders",
            "current_value": ",".join(str(v) for v in design["veto_holders"]),
            "suggested_action": (
                f"decision_rule '{rule}' lets every member block; record veto_holders only for "
                "treaty-granted vetoes that other members lack"
            ),
        }]
    return []


def check_scope_coverage(records: list[dict], config: dict) -> list[dict]:
    scope = config.get("scope_category") or {}
    limit = scope.get("max_missing_formal")
    missing_records = [r for r in records if r.get("status") == "formal" and not r.get("scope_category")]
    missing = len(missing_records)
    unexpected = {r.get("id", "unknown") for r in missing_records} - set(scope.get("pending_taxonomy") or {})
    if limit is None or (missing <= limit and ("pending_taxonomy" not in scope or not unexpected)):
        return []
    return [{"issue_type": "COMPLETENESS_ERROR", "field": "scope_category", "current_value": str(missing),
             "suggested_action": f"Missing formal scope_category count {missing}; ratchet {limit}; unexpected IDs: {sorted(unexpected)}"}]


def check_intblock_schema(record: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(record), key=lambda e: e.path):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append({
            "issue_type": "SCHEMA_ERROR",
            "field": path,
            "current_value": str(err.instance),
            "suggested_action": f"Fix schema error: {err.message}",
            "message": err.message,
        })
    return errors


def check_intblock_duplicates(records: list[dict[str, Any]], rel_paths: list[str]) -> list[dict[str, Any]]:
    errors = []
    seen = {}
    for path, rec in zip(rel_paths, records, strict=False):
        rid = str(rec.get("id", ""))
        if not rid:
            continue
        if rid in seen and seen[rid][0] != path:
            errors.append({
                "issue_type": "DUPLICATE_INTBLOCK_ID",
                "field": "id",
                "current_value": rid,
                "suggested_action": f"Duplicate intblock ID '{rid}' found in both {path} and {seen[rid][0]}",
                "file_path": path,
                "record_id": rid,
                "other_path": seen[rid][0],
            })
        else:
            seen[rid] = (path, rid)
    return errors


def check_intblock_blocktypes(record: dict[str, Any], taxonomy: set[str]) -> list[dict[str, Any]]:
    errors = []
    for bt in record.get("blocktype") or []:
        if str(bt) not in taxonomy:
            errors.append({
                "issue_type": "UNKNOWN_BLOCKTYPE",
                "field": "blocktype",
                "current_value": str(bt),
                "suggested_action": f"blocktype '{bt}' must exist in the blocktypes taxonomy"
            })
    return errors


def check_intblock_filename(record: dict[str, Any], rel_path: str) -> list[dict[str, Any]]:
    rid = str(record.get("id", ""))
    if not rid:
        return []
    stem = Path(rel_path).stem
    if stem != rid:
        return [{
            "issue_type": "FILENAME_ID_MISMATCH",
            "field": "id",
            "current_value": rid,
            "suggested_action": f"filename stem '{stem}' does not match id '{rid}'",
        }]
    return []


def check_intblock_directory_alignment(record: dict[str, Any], rel_path: str) -> list[dict[str, Any]]:
    bts = [str(b) for b in (record.get("blocktype") or [])]
    if not bts:
        return []
    parts = rel_path.split("/")
    if len(parts) < 3 or parts[0] != "data" or parts[1] != "intblocks":
        return []
    dir_name = parts[2]
    if dir_name not in bts:
        return [{
            "issue_type": "DIRECTORY_BLOCKTYPE_MISMATCH",
            "field": "blocktype",
            "current_value": str(bts),
            "suggested_action": f"directory '{dir_name}' is not in blocktype list {bts}",
        }]
    if bts[0] != dir_name:
        return [{
            "issue_type": "PRIMARY_BLOCKTYPE_MISMATCH",
            "field": "blocktype",
            "current_value": str(bts),
            "suggested_action": (
                f"primary blocktype '{bts[0]}' does not match directory '{dir_name}'; "
                f"put '{dir_name}' first in the blocktype list"
            ),
        }]
    return []


BLOCKTYPES_SOURCE = "data/blocktypes/blocktypes.yaml"


def check_blocktype_descriptions(catalog: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Every blocktype taxonomy entry needs a non-empty English ``description`` (scope note)."""
    return [
        {
            "issue_type": "MISSING_BLOCKTYPE_DESCRIPTION",
            "field": "description",
            "current_value": bt_id,
            "suggested_action": f"blocktype '{bt_id}' has no description in {BLOCKTYPES_SOURCE}",
            "file_path": BLOCKTYPES_SOURCE,
            "record_id": bt_id,
        }
        for bt_id, spec in sorted(catalog.items())
        if not str(spec.get("description") or "").strip()
    ]


def check_deprecated_primary_blocktype(
    record: dict[str, Any], catalog: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """A deprecated blocktype must not be a record's primary (first) blocktype."""
    bts = [str(b) for b in (record.get("blocktype") or [])]
    if not bts or not (catalog.get(bts[0]) or {}).get("deprecated"):
        return []
    return [{
        "issue_type": "DEPRECATED_PRIMARY_BLOCKTYPE",
        "field": "blocktype",
        "current_value": bts[0],
        "suggested_action": (
            f"blocktype '{bts[0]}' is deprecated and cannot be the primary blocktype; move the record "
            f"to a domain directory (see {BLOCKTYPES_SOURCE})"
        ),
    }]


def check_deprecated_blocktype_ratchet(
    records: list[dict[str, Any]],
    rel_paths: list[str],
    catalog: dict[str, dict[str, Any]],
    baseline: dict[str, set[str]],
    gone_ids: set[str],
) -> list[dict[str, Any]]:
    """Records carrying a deprecated blocktype must equal its reviewed baseline until removal.

    ``gone_ids`` are alias names (merged, renamed, retired): a baseline id that left that way is
    no longer expected. The set may neither grow nor shrink before the MAJOR release.
    """
    issues: list[dict[str, Any]] = []
    for bt_id in sorted(b for b, spec in catalog.items() if spec.get("deprecated")):
        if bt_id not in baseline:
            issues.append({
                "issue_type": "DEPRECATED_BLOCKTYPE_RATCHET",
                "field": "blocktype",
                "current_value": bt_id,
                "suggested_action": (
                    f"deprecated blocktype '{bt_id}' has no baseline in "
                    "data/schemas/deprecated_blocktypes_baseline.yaml"
                ),
                "file_path": BLOCKTYPES_SOURCE,
                "record_id": bt_id,
            })
            continue
        expected = baseline[bt_id] - gone_ids
        carrying: dict[str, str] = {}
        for rec, rel in zip(records, rel_paths, strict=False):
            if bt_id in {str(b) for b in (rec.get("blocktype") or [])}:
                carrying[str(rec.get("id") or "")] = rel
        present = {str(r.get("id") or ""): rel for r, rel in zip(records, rel_paths, strict=False)}
        for rid in sorted(set(carrying) - expected):
            issues.append({
                "issue_type": "DEPRECATED_BLOCKTYPE_RATCHET",
                "field": "blocktype",
                "current_value": bt_id,
                "suggested_action": f"'{rid}' adds deprecated blocktype '{bt_id}', which is outside its baseline",
                "file_path": carrying[rid],
                "record_id": rid,
            })
        for rid in sorted((expected & set(present)) - set(carrying)):
            issues.append({
                "issue_type": "DEPRECATED_BLOCKTYPE_RATCHET",
                "field": "blocktype",
                "current_value": bt_id,
                "suggested_action": (
                    f"'{rid}' dropped deprecated blocktype '{bt_id}' before its removal release; "
                    "keep it as the last blocktype until the next MAJOR release"
                ),
                "file_path": present[rid],
                "record_id": rid,
            })
    return issues


def check_intblock_topics_present(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Flag records without topics."""
    if record.get("topics"):
        return []
    return [{
        "issue_type": "MISSING_TOPICS",
        "field": "topics",
        "current_value": None,
        "suggested_action": "add at least one topic from data/schemas/topics.yaml",
    }]


def check_intblock_topics(
    record: dict[str, Any],
    topic_aliases: dict[str, str],
    topic_catalog: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Flag deprecated topic keys and, when a canonical catalog is supplied,
    keys absent from data/schemas/topics.yaml."""
    issues: list[dict[str, Any]] = []
    for idx, topic in enumerate(record.get("topics") or []):
        if not isinstance(topic, dict):
            continue
        key = str(topic.get("key") or "")
        if topic_aliases and key in topic_aliases:
            issues.append({
                "issue_type": "DEPRECATED_TOPIC_KEY",
                "field": f"topics[{idx}].key",
                "current_value": key,
                "suggested_action": f"deprecated topic '{key}' (use '{topic_aliases[key]}')",
            })
        elif topic_catalog and key and key not in topic_catalog:
            issues.append({
                "issue_type": "UNKNOWN_TOPIC_KEY",
                "field": f"topics[{idx}].key",
                "current_value": key,
                "suggested_action": (
                    f"topic '{key}' is not in data/schemas/topics.yaml; "
                    "reuse a canonical key or add the new key to the catalog"
                ),
            })
    return issues


def _parse_lifecycle_date(raw: str) -> tuple[int, int, int] | None:
    """Parse YYYY / YYYYs / YYYY-MM / YYYY-MM-DD into a comparable tuple."""
    m = DATE_RE.match(raw)
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2) or 1)
    day = int(m.group(3) or 1)
    try:
        date(year, month, day)
    except ValueError:
        return None
    return (year, month, day)


def check_intblock_lifecycle(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    if "ended" in record:
        errors.append({
            "issue_type": "LIFECYCLE_INCONSISTENCY",
            "field": "ended",
            "current_value": str(record.get("ended")),
            "suggested_action": "Use the standard 'dissolved' field instead of 'ended'"
        })
    if record.get("dissolved") and record.get("status") not in ("historical", None):
        errors.append({
            "issue_type": "LIFECYCLE_INCONSISTENCY",
            "field": "status",
            "current_value": str(record.get("status")),
            "suggested_action": f"Record has a dissolved date but status is '{record.get('status')}', expected 'historical'"
        })
    if record.get("status") == "historical" and not record.get("dissolved"):
        errors.append({
            "issue_type": "LIFECYCLE_INCONSISTENCY",
            "field": "dissolved",
            "current_value": None,
            "suggested_action": "Record has status 'historical' but no dissolved date; add 'dissolved'"
        })
    return errors


def check_intblock_chronology(record: dict[str, Any]) -> list[dict[str, Any]]:
    """founded/dissolved must parse, be ordered, and not lie in the future."""
    issues: list[dict[str, Any]] = []
    today = (date.today().year, date.today().month, date.today().day)
    parsed: dict[str, tuple[int, int, int]] = {}
    for field in ("founded", "dissolved"):
        raw = record.get(field)
        if raw is None or raw == "":
            continue
        value = _parse_lifecycle_date(str(raw))
        if value is None:
            issues.append({
                "issue_type": "CHRONOLOGY_ERROR",
                "field": field,
                "current_value": str(raw),
                "suggested_action": f"{field} '{raw}' is not a valid date (YYYY, YYYY-MM, YYYY-MM-DD, or YYYYs)",
            })
            continue
        if value > today:
            issues.append({
                "issue_type": "CHRONOLOGY_ERROR",
                "field": field,
                "current_value": str(raw),
                "suggested_action": f"{field} '{raw}' is in the future",
            })
        parsed[field] = value
    if "founded" in parsed and "dissolved" in parsed and parsed["dissolved"] < parsed["founded"]:
        issues.append({
            "issue_type": "CHRONOLOGY_ERROR",
            "field": "dissolved",
            "current_value": str(record.get("dissolved")),
            "suggested_action": (
                f"dissolved '{record.get('dissolved')}' precedes founded '{record.get('founded')}'"
            ),
        })
    return issues


def _parse_precise_date(raw: str) -> tuple[int, int | None, int | None] | None:
    """Parse YYYY / YYYYs / YYYY-MM / YYYY-MM-DD keeping the stated precision."""
    m = DATE_RE.match(raw)
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) else None
    day = int(m.group(3)) if m.group(3) else None
    try:
        # month/day 0 (e.g. '1991-00-00') must fail, so don't coalesce with `or`.
        date(year, 1 if month is None else month, 1 if day is None else day)
    except ValueError:
        return None
    return (year, month, day)


def _compare_precise(
    a: tuple[int, int | None, int | None],
    b: tuple[int, int | None, int | None],
) -> int:
    """Compare two dates at their coarsest common precision (-1, 0, or 1).

    '2015' vs '2015-11-01' compares equal: a bare year neither precedes nor
    follows a specific date within that year.
    """
    for x, y in zip(a, b, strict=True):
        if x is None or y is None:
            return 0
        if x != y:
            return -1 if x < y else 1
    return 0


def check_intblock_include_dates(record: dict[str, Any]) -> list[dict[str, Any]]:
    """includes[].joined/left must parse, not lie in the future, stay ordered,
    and not postdate the block's dissolution.

    joined earlier than founded is deliberately not flagged: signature and
    ratification dates commonly precede an organization's entry into force.
    """
    issues: list[dict[str, Any]] = []
    today = (date.today().year, date.today().month, date.today().day)
    dissolved = None
    if record.get("dissolved"):
        dissolved = _parse_precise_date(str(record["dissolved"]))

    for idx, inc in enumerate(record.get("includes") or []):
        if not isinstance(inc, dict):
            continue
        parsed: dict[str, tuple[int, int | None, int | None]] = {}
        for field in ("joined", "left"):
            raw = inc.get(field)
            if raw is None or raw == "":
                continue
            value = _parse_precise_date(str(raw))
            if value is None:
                issues.append({
                    "issue_type": "INCLUDE_DATE_INCONSISTENCY",
                    "field": f"includes[{idx}].{field}",
                    "current_value": str(raw),
                    "suggested_action": (
                        f"{field} '{raw}' is not a valid date (YYYY, YYYY-MM, YYYY-MM-DD, or YYYYs)"
                    ),
                })
                continue
            if _compare_precise(value, today) > 0:
                issues.append({
                    "issue_type": "INCLUDE_DATE_INCONSISTENCY",
                    "field": f"includes[{idx}].{field}",
                    "current_value": str(raw),
                    "suggested_action": f"{field} '{raw}' is in the future",
                })
            parsed[field] = value

        if "joined" in parsed and "left" in parsed and _compare_precise(parsed["left"], parsed["joined"]) < 0:
            issues.append({
                "issue_type": "INCLUDE_DATE_INCONSISTENCY",
                "field": f"includes[{idx}].left",
                "current_value": str(inc.get("left")),
                "suggested_action": f"left '{inc.get('left')}' precedes joined '{inc.get('joined')}'",
            })
        if dissolved:
            for field in ("joined", "left"):
                if field in parsed and _compare_precise(parsed[field], dissolved) > 0:
                    issues.append({
                        "issue_type": "INCLUDE_DATE_INCONSISTENCY",
                        "field": f"includes[{idx}].{field}",
                        "current_value": str(inc.get(field)),
                        "suggested_action": (
                            f"{field} '{inc.get(field)}' postdates the block's dissolved date "
                            f"'{record.get('dissolved')}'"
                        ),
                    })
    return issues


def check_intblock_founding_members(
    record: dict[str, Any],
    country_codes: set[str],
) -> list[dict[str, Any]]:
    """founding_members entries must resolve to country codes and, when the
    record has includes, appear in that list."""
    issues: list[dict[str, Any]] = []
    founding = record.get("founding_members") or []
    if not founding:
        return issues
    include_ids = {
        str(inc.get("id"))
        for inc in (record.get("includes") or [])
        if isinstance(inc, dict) and inc.get("id")
    }
    for idx, member in enumerate(founding):
        mid = str(member)
        if country_codes and mid not in country_codes:
            issues.append({
                "issue_type": "FOUNDING_MEMBER_NOT_INCLUDED",
                "field": f"founding_members[{idx}]",
                "current_value": mid,
                "suggested_action": f"founding member '{mid}' does not resolve to any country code",
            })
        elif include_ids and mid not in include_ids:
            issues.append({
                "issue_type": "FOUNDING_MEMBER_NOT_INCLUDED",
                "field": f"founding_members[{idx}]",
                "current_value": mid,
                "suggested_action": (
                    f"founding member '{mid}' is absent from includes; add it "
                    "(e.g. with status former_member) or remove the founder entry"
                ),
            })
    return issues


def check_intblock_last_verified(
    record: dict[str, Any],
    *,
    max_age_months: int,
) -> list[dict[str, Any]]:
    """Advisory when last_verified is older than the configured maximum age."""
    raw = record.get("last_verified")
    if not raw or max_age_months <= 0:
        return []
    try:
        year, month, day = (int(p) for p in str(raw).split("-"))
        verified = date(year, month, day)
    except (TypeError, ValueError):
        return [{
            "issue_type": "STALE_LAST_VERIFIED",
            "field": "last_verified",
            "current_value": str(raw),
            "suggested_action": f"last_verified '{raw}' is not a valid ISO date",
        }]
    today = date.today()
    age_months = (today.year - verified.year) * 12 + (today.month - verified.month)
    if age_months > max_age_months:
        return [{
            "issue_type": "STALE_LAST_VERIFIED",
            "field": "last_verified",
            "current_value": str(raw),
            "suggested_action": (
                f"record not verified since {raw} (>{max_age_months} months); re-verify membership and links"
            ),
        }]
    return []


def check_intblock_text_encoding(record: dict[str, Any]) -> list[dict[str, Any]]:
    from internacia_builder.validate.country_rules import check_text_encoding

    return check_text_encoding(record, ("name", "description"))


def check_intblock_membership_consistency(
    record: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Duplicate includes entries, membership_count mismatch, and contradictory
    membership_applicability markers."""
    issues: list[dict[str, Any]] = []
    includes = [inc for inc in (record.get("includes") or []) if isinstance(inc, dict)]

    seen: set[tuple[str, str]] = set()
    for idx, inc in enumerate(includes):
        key = (str(inc.get("type", "")), str(inc.get("id", "")))
        if not key[1]:
            continue
        if key in seen:
            issues.append({
                "issue_type": "DUPLICATE_INCLUDE_ENTRY",
                "field": f"includes[{idx}]",
                "current_value": str(inc.get("id")),
                "suggested_action": f"'{inc.get('id')}' appears more than once in includes; remove the duplicate entry",
            })
        seen.add(key)

    if record.get("membership_applicability") == "not_applicable" and includes:
        issues.append({
            "issue_type": "CONTRADICTORY_APPLICABILITY",
            "field": "membership_applicability",
            "current_value": "not_applicable",
            "suggested_action": "membership_applicability is not_applicable but includes is populated; remove the marker or the includes",
        })

    mc_rule = ((config or {}).get("includes") or {}).get("membership_count") or {}
    tolerance = int(mc_rule.get("tolerance", 0))
    mc = record.get("membership_count")
    mc_type = record.get("membership_count_type")
    non_country_count = mc_type is not None and mc_type != "countries"
    if isinstance(mc, int) and not isinstance(mc, bool) and includes and not non_country_count:
        total = len(includes)
        member_class = sum(
            1 for inc in includes if str(inc.get("status", "")) in MEMBER_CLASS_STATUSES
        )
        # membership_count may legitimately count either all participants or
        # only member-class entries; flag only when it matches neither.
        if all(abs(mc - candidate) > tolerance for candidate in (total, member_class)):
            issues.append({
                "issue_type": "MEMBERSHIP_COUNT_MISMATCH",
                "field": "membership_count",
                "current_value": str(mc),
                "suggested_action": (
                    f"membership_count {mc} matches neither total includes ({total}) "
                    f"nor member-class includes ({member_class})"
                ),
            })
    if non_country_count:
        provenance_fields = {
            str(p.get("field")) for p in (record.get("provenance") or []) if isinstance(p, dict)
        }
        if "membership_count" not in provenance_fields:
            issues.append({
                "issue_type": "MEMBERSHIP_COUNT_MISMATCH",
                "field": "membership_count",
                "current_value": str(mc),
                "suggested_action": (
                    f"membership_count_type is '{mc_type}' (non-country count); "
                    "a provenance entry for membership_count is required"
                ),
            })
    return issues


def check_intblock_description_quality(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    desc = str(record.get("description") or "")
    if TEMPLATED_DESC_RE.match(desc):
        errors.append({
            "issue_type": "TEMPLATED_DESCRIPTION",
            "field": "description",
            "current_value": desc,
            "suggested_action": "Rewrite description to avoid templated boilerplate",
            "priority": "MEDIUM",
        })
    return errors


def check_intblock_includes_contract(
    record: dict[str, Any],
    config: dict[str, Any],
    status_catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    includes_rule = (config.get("includes") or {}).get("membership_applicability") or {}
    if includes_rule.get("require_marker_when_empty") and is_null_intblock_field(record, "includes"):
        if record.get("membership_applicability") != "not_applicable":
            priority_key = str(includes_rule.get("priority") or "high")
            issue_priority = PRIORITY_TO_LEVEL.get(priority_key, "IMPORTANT")
            if includes_rule.get("mode", "warn") == "warn" and issue_priority == "IMPORTANT":
                issue_priority = "MEDIUM"
            issues.append({
                "issue_type": "MISSING_INCLUDES_APPLICABILITY",
                "field": "includes",
                "current_value": None,
                "suggested_action": (
                    "Populate includes or set membership_applicability: not_applicable "
                    "when membership is intentionally absent"
                ),
                "priority": issue_priority,
            })

    status_rule = (config.get("includes") or {}).get("status") or {}
    allowed = set(status_catalog)
    if allowed:
        for idx, inc in enumerate(record.get("includes") or []):
            if not isinstance(inc, dict):
                continue
            status = inc.get("status")
            if status is None or status == "":
                issues.append({
                    "issue_type": "INVALID_INCLUDE_STATUS",
                    "field": f"includes[{idx}].status",
                    "current_value": None,
                    "suggested_action": "Set status from data/schemas/includes_status.yaml",
                    "priority": PRIORITY_TO_LEVEL.get(str(status_rule.get("priority") or "high"), "IMPORTANT"),
                })
            elif str(status) not in allowed:
                issues.append({
                    "issue_type": "INVALID_INCLUDE_STATUS",
                    "field": f"includes[{idx}].status",
                    "current_value": str(status),
                    "suggested_action": f"Use a defined status from includes_status.yaml (not '{status}')",
                    "priority": PRIORITY_TO_LEVEL.get(str(status_rule.get("priority") or "high"), "IMPORTANT"),
                })
    return issues


def check_deprecated_include_statuses(
    record: dict[str, Any], status_catalog: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Warn on includes[].status values marked ``deprecated`` in includes_status.yaml."""
    issues: list[dict[str, Any]] = []
    for idx, inc in enumerate(record.get("includes") or []):
        if not isinstance(inc, dict):
            continue
        status = str(inc.get("status") or "")
        marker = (status_catalog.get(status) or {}).get("deprecated")
        if not marker:
            continue
        replacements = " or ".join(f"'{r}'" for r in marker.get("replacements") or [])
        issues.append({
            "issue_type": "DEPRECATED_INCLUDE_STATUS",
            "field": f"includes[{idx}].status",
            "current_value": status,
            "suggested_action": (
                f"status '{status}' is deprecated and will be removed in the {marker.get('removal') or 'next MAJOR'} "
                f"release; use {replacements} (see data/schemas/includes_status.yaml)"
            ),
        })
    return issues


def check_intblock_links(
    record: dict[str, Any],
    check_http: bool = False,
    check_wikidata: bool = False,
) -> list[dict[str, Any]]:
    errors = []
    entity_name = record.get("name", "")
    links = record.get("links", [])
    wikidata_ids_in_links = []

    try:
        import sys
        scripts_dir = str(Path(__file__).resolve().parents[2] / "scripts")
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
        from validate_links import REQUEST_DELAY, extract_wikidata_id, validate_url, validate_wikidata_entity
    except ImportError:
        def extract_wikidata_id(url: str) -> str | None:
            match = re.search(r"Q\d+", url)
            return match.group(0) if match else None

        def validate_url(url: str, timeout: int = 10) -> tuple[bool, str, int]:
            return True, "", 200

        def validate_wikidata_entity(qid: str, entity_name: str) -> tuple[bool, str]:
            return True, ""

        REQUEST_DELAY = 0.0

    for i, link in enumerate(links):
        if not isinstance(link, dict):
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}]",
                "current_value": str(link),
                "suggested_action": "Link must be a dictionary"
            })
            continue

        url = link.get("url", "")
        link_type = link.get("type", "")

        if not url:
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}].url",
                "current_value": None,
                "suggested_action": "Missing URL"
            })
            continue

        if not link_type:
            errors.append({
                "issue_type": "SCHEMA_ERROR",
                "field": f"links[{i}].type",
                "current_value": None,
                "suggested_action": "Missing type"
            })
            continue

        if link_type == "wikidata":
            qid = extract_wikidata_id(url)
            if qid:
                wikidata_ids_in_links.append(qid)
            else:
                errors.append({
                    "issue_type": "INVALID_URL",
                    "field": f"links[{i}].url",
                    "current_value": url,
                    "suggested_action": "Could not extract Q-number from Wikidata URL"
                })

        if check_http:
            is_valid, error_msg, _ = validate_url(url)
            if not is_valid:
                errors.append({
                    "issue_type": "INVALID_URL",
                    "field": f"links[{i}].url",
                    "current_value": url,
                    "suggested_action": f"URL check failed: {error_msg}"
                })
            time.sleep(REQUEST_DELAY)

    wikidata_id = record.get("wikidata_id")
    if wikidata_id:
        if not WIKIDATA_RE.match(str(wikidata_id)):
            errors.append({
                "issue_type": "INVALID_ID",
                "field": "wikidata_id",
                "current_value": str(wikidata_id),
                "suggested_action": "wikidata_id has invalid format (must be Q followed by digits)"
            })
        else:
            if wikidata_ids_in_links and wikidata_id not in wikidata_ids_in_links:
                errors.append({
                    "issue_type": "INVALID_ID",
                    "field": "wikidata_id",
                    "current_value": str(wikidata_id),
                    "suggested_action": f"wikidata_id does not match any wikidata link Q-numbers: {wikidata_ids_in_links}"
                })

            if check_wikidata and entity_name:
                is_valid, error_msg = validate_wikidata_entity(wikidata_id, entity_name)
                if not is_valid:
                    errors.append({
                        "issue_type": "INVALID_ID",
                        "field": "wikidata_id",
                        "current_value": str(wikidata_id),
                        "suggested_action": f"Wikidata validation failed: {error_msg}"
                    })
                time.sleep(REQUEST_DELAY)

    if wikidata_ids_in_links and not wikidata_id:
        errors.append({
            "issue_type": "INVALID_ID",
            "field": "wikidata_id",
            "current_value": None,
            "suggested_action": f"Record has wikidata link(s) but missing wikidata_id field. Found: {wikidata_ids_in_links}"
        })

    return errors
