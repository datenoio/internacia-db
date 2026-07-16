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
    return []


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
    if isinstance(mc, int) and not isinstance(mc, bool) and includes:
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
