"""Country data-quality rule checkers.

Single implementation shared by the ``analyze-quality`` report generator and the
``validate_countries`` CLI. Each checker returns structured issue dicts with
``issue_type``, ``field``, ``current_value``, and ``suggested_action`` keys
(cross-record checkers also set ``file_path``/``record_id``).
"""

from __future__ import annotations

import math
import re
from datetime import date
from functools import lru_cache
from typing import Any

import jsonschema

ALPHA3 = re.compile(r"^[A-Z]{3}$")
ISO4217 = re.compile(r"^[A-Z]{3}$")
ALPHA2 = re.compile(r"^[A-Z]{2}$")
TLD_RE = re.compile(r"^\.[a-z0-9-]{2,}$")
# Structural check only: '+' followed by country code and optional area prefix
# (e.g. '+358', '+35818'); ITU allocation is not verified.
CALLING_CODE_RE = re.compile(r"^\+\d{1,7}$")

# Control characters (except tab/newline), U+FFFD, and common double-encoded
# UTF-8 artifacts ('Ã©', 'â€™', 'Ð' + Cyrillic continuation, …).
MOJIBAKE_RE = re.compile(
    r"[\ufffd\u0000-\u0008\u000b\u000c\u000e-\u001f]"
    r"|Ã[\u0080-\u00bf©¨«»¤¶¼]"
    r"|â€"
    r"|Â[\u00a0-\u00bf]"
)

# Canonical continent → UN M49-style subregion table used by
# REGION_HIERARCHY_MISMATCH. Transcontinental exceptions are allowlisted in
# countries_completeness.yaml under region_hierarchy.allowlist.
CONTINENT_SUBREGIONS: dict[str, frozenset[str]] = {
    "Africa": frozenset(
        {"Northern Africa", "Eastern Africa", "Middle Africa", "Southern Africa", "Western Africa"}
    ),
    "Antarctica": frozenset(),
    "Asia": frozenset(
        {"Central Asia", "Eastern Asia", "South-Eastern Asia", "Southern Asia", "Western Asia"}
    ),
    "Europe": frozenset(
        {
            "Central Europe",
            "Eastern Europe",
            "Northern Europe",
            "Southeast Europe",
            "Southern Europe",
            "Western Europe",
        }
    ),
    "North America": frozenset({"Caribbean", "Central America", "North America"}),
    "Oceania": frozenset({"Australia and New Zealand", "Melanesia", "Micronesia", "Polynesia"}),
    "South America": frozenset({"South America"}),
}

REGIONAL_INDICATOR_BASE = 0x1F1E6

ENTITY_TYPES = frozenset(
    {
        "sovereign_state",
        "dependent_territory",
        "special_administrative_region",
        "disputed_territory",
        "historical_entity",
        "supranational_grouping",
        "statistical_area",
    }
)

CODE_STATUSES = frozenset(
    {
        "official_iso3166_1",
        "user_assigned",
        "obsolete",
        "exceptionally_reserved",
    }
)

NON_ISO_ALPHA2 = frozenset({"AN", "JG", "KV"})
USER_ASSIGNED_EXCEPTIONS = frozenset({"XA", "XS", "XT", "XN"})

# Entity types that cannot be UN members or independent states.
NON_SOVEREIGN_ENTITY_TYPES = frozenset(
    {"dependent_territory", "special_administrative_region", "statistical_area"}
)

EXPECTED_OFFICIAL_ISO_COUNT = 249


def is_null_field(record: dict[str, Any], field: str) -> bool:
    if field == "timezones" and record.get("timezone_status") == "not_applicable":
        return False
    if field not in record:
        return True
    val = record[field]
    if val is None:
        return True
    if val == "" or val == [] or val == {}:
        return True
    return False


def check_country_schema(record: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
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


def check_country_borders(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    borders = record.get("borders")
    if borders is None:
        return errors
    if not isinstance(borders, list):
        errors.append({
            "issue_type": "INVALID_BORDER_REFERENCE",
            "field": "borders",
            "current_value": str(borders),
            "suggested_action": "borders must be a list of alpha-3 country codes"
        })
        return errors
    for b in borders:
        if not isinstance(b, str) or not ALPHA3.match(b):
            errors.append({
                "issue_type": "INVALID_BORDER_REFERENCE",
                "field": "borders",
                "current_value": str(b),
                "suggested_action": f"border '{b}' must be ISO alpha-3 uppercase"
            })
    return errors


def check_country_indicator_years(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    for field in ("population", "area", "gini"):
        val = record.get(field)
        if not isinstance(val, dict):
            continue
        year = val.get("year")
        if year is None:
            continue
        if not isinstance(year, int) or isinstance(year, bool) or year <= 0:
            errors.append({
                "issue_type": "INVALID_INDICATOR_YEAR",
                "field": f"{field}.year",
                "current_value": str(year),
                "suggested_action": f"{field}.year must be a positive integer or omitted"
            })
    return errors


def check_country_indicator_values(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Plausibility bounds for indicator structs.

    Population may legitimately be zero (uninhabited territories); negative
    values, non-positive area, gini outside (0, 100), and future years are
    data errors.
    """
    issues: list[dict[str, Any]] = []
    current_year = date.today().year
    for field in ("population", "area", "gini"):
        val = record.get(field)
        if not isinstance(val, dict):
            continue
        raw = val.get("value")
        if raw is not None:
            try:
                num = float(raw)
            except (TypeError, ValueError):
                num = None
                issues.append({
                    "issue_type": "INVALID_INDICATOR_VALUE",
                    "field": f"{field}.value",
                    "current_value": str(raw),
                    "suggested_action": f"{field}.value must be numeric",
                })
            if num is not None:
                bad = (
                    (field == "population" and num < 0)
                    or (field == "area" and num <= 0)
                    or (field == "gini" and not (0 < num < 100))
                )
                if bad:
                    issues.append({
                        "issue_type": "INVALID_INDICATOR_VALUE",
                        "field": f"{field}.value",
                        "current_value": str(raw),
                        "suggested_action": f"{field}.value {raw} is outside the plausible range",
                    })
        year = val.get("year")
        if isinstance(year, int) and not isinstance(year, bool) and year > current_year:
            issues.append({
                "issue_type": "INVALID_INDICATOR_VALUE",
                "field": f"{field}.year",
                "current_value": str(year),
                "suggested_action": f"{field}.year {year} is in the future",
            })
    return issues


def check_country_whitespace(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    sub = record.get("subregion")
    if isinstance(sub, str) and sub != sub.strip():
        errors.append({
            "issue_type": "WHITESPACE_IN_CATEGORICAL_FIELD",
            "field": "subregion",
            "current_value": sub,
            "suggested_action": "Strip leading/trailing whitespace"
        })
    for key in ("region", "adminregion"):
        obj = record.get(key)
        if isinstance(obj, dict):
            val = obj.get("value")
            if isinstance(val, str) and val != val.strip():
                errors.append({
                    "issue_type": "WHITESPACE_IN_CATEGORICAL_FIELD",
                    "field": f"{key}.value",
                    "current_value": val,
                    "suggested_action": "Strip leading/trailing whitespace"
                })
    return errors


def check_country_entity_status(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    code = str(record.get("code", ""))
    entity_type = record.get("entity_type")
    code_status = record.get("code_status")

    if not entity_type:
        errors.append({
            "issue_type": "INVALID_ENTITY_TYPE",
            "field": "entity_type",
            "current_value": None,
            "suggested_action": "Specify entity_type"
        })
    elif entity_type not in ENTITY_TYPES:
        errors.append({
            "issue_type": "INVALID_ENTITY_TYPE",
            "field": "entity_type",
            "current_value": entity_type,
            "suggested_action": f"entity_type must be one of {sorted(ENTITY_TYPES)}"
        })

    if not code_status:
        errors.append({
            "issue_type": "INVALID_CODE_STATUS",
            "field": "code_status",
            "current_value": None,
            "suggested_action": "Specify code_status"
        })
    elif code_status not in CODE_STATUSES:
        errors.append({
            "issue_type": "INVALID_CODE_STATUS",
            "field": "code_status",
            "current_value": code_status,
            "suggested_action": f"code_status must be one of {sorted(CODE_STATUSES)}"
        })

    if code in NON_ISO_ALPHA2:
        if code_status == "official_iso3166_1":
            errors.append({
                "issue_type": "INVALID_CODE_STATUS",
                "field": "code_status",
                "current_value": code_status,
                "suggested_action": f"non-ISO code '{code}' must not have code_status official_iso3166_1"
            })
    elif code_status and code_status != "official_iso3166_1":
        if re.match(r"^[A-Z]{2}$", code) and code not in USER_ASSIGNED_EXCEPTIONS:
            errors.append({
                "issue_type": "INVALID_CODE_STATUS",
                "field": "code_status",
                "current_value": code_status,
                "suggested_action": f"ISO-style code '{code}' must have code_status official_iso3166_1"
            })

    return errors


def check_country_entity_flags(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Boolean status flags must be consistent with entity_type and un_status."""
    issues: list[dict[str, Any]] = []
    un_status = record.get("un_status")
    un_member = record.get("un_member")
    if un_status is not None:
        expected_member = un_status == "member"
        if un_member is not None and un_member is not expected_member:
            issues.append({
                "issue_type": "INCONSISTENT_ENTITY_FLAGS",
                "field": "un_status",
                "current_value": str(un_status),
                "suggested_action": (
                    f"un_status '{un_status}' contradicts un_member {un_member}; "
                    "member requires un_member true, observer/non_member require false"
                ),
            })
    entity_type = record.get("entity_type")
    if entity_type not in NON_SOVEREIGN_ENTITY_TYPES:
        return issues
    for flag in ("un_member", "independent"):
        if record.get(flag) is True:
            issues.append({
                "issue_type": "INCONSISTENT_ENTITY_FLAGS",
                "field": flag,
                "current_value": "True",
                "suggested_action": f"{flag} must not be true for entity_type '{entity_type}'",
            })
    return issues


def check_country_currency_codes(record: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for idx, cur in enumerate(record.get("currencies") or []):
        if not isinstance(cur, dict):
            continue
        code = cur.get("code")
        if code is None:
            continue
        if not isinstance(code, str) or not ISO4217.match(code):
            issues.append({
                "issue_type": "INVALID_CURRENCY_CODE",
                "field": f"currencies[{idx}].code",
                "current_value": str(code),
                "suggested_action": f"currencies[{idx}].code '{code}' is not ISO 4217 uppercase",
            })
    return issues


def _check_coord_pair(obj: dict[str, Any], prefix: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for key, lo, hi in (("lat", -90, 90), ("lng", -180, 180)):
        raw = obj.get(key)
        if raw is None:
            continue
        try:
            num = float(raw)
        except (TypeError, ValueError):
            num = None
        if num is None or not (lo <= num <= hi):
            issues.append({
                "issue_type": "INVALID_COORDINATES",
                "field": f"{prefix}.{key}",
                "current_value": str(raw),
                "suggested_action": f"{prefix}.{key} must be between {lo} and {hi}",
            })
    return issues


def check_country_coordinates(record: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for key in ("centroid", "capital_city"):
        obj = record.get(key)
        if isinstance(obj, dict):
            issues.extend(_check_coord_pair(obj, key))
    return issues


@lru_cache(maxsize=1)
def _iana_timezones() -> frozenset[str]:
    """Available IANA timezone names, or empty when the tz database is missing."""
    try:
        from zoneinfo import available_timezones

        return frozenset(available_timezones())
    except Exception:
        return frozenset()


def check_country_tld(record: dict[str, Any]) -> list[dict[str, Any]]:
    tld = record.get("tld")
    if tld is None or tld == "":
        return []
    if not isinstance(tld, str) or not TLD_RE.match(tld):
        return [{
            "issue_type": "INVALID_TLD",
            "field": "tld",
            "current_value": str(tld),
            "suggested_action": f"tld '{tld}' must be a lowercase top-level domain like '.fr'",
        }]
    return []


def check_country_calling_codes(record: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for idx, code in enumerate(record.get("calling_codes") or []):
        if not isinstance(code, str) or not CALLING_CODE_RE.match(code):
            issues.append({
                "issue_type": "INVALID_CALLING_CODE",
                "field": f"calling_codes[{idx}]",
                "current_value": str(code),
                "suggested_action": f"calling code '{code}' must be '+' followed by digits (e.g. '+33')",
            })
    return issues


def check_country_timezones(record: dict[str, Any]) -> list[dict[str, Any]]:
    known = _iana_timezones()
    if not known:
        return []  # tz database unavailable in this runtime; skip rather than guess
    issues: list[dict[str, Any]] = []
    for idx, tz in enumerate(record.get("timezones") or []):
        if str(tz) not in known:
            issues.append({
                "issue_type": "INVALID_TIMEZONE",
                "field": f"timezones[{idx}]",
                "current_value": str(tz),
                "suggested_action": f"timezone '{tz}' is not in the IANA tz database",
            })
    return issues


def flag_emoji_for_code(code: str) -> str:
    """Unicode regional-indicator flag derived from an alpha-2 code."""
    return "".join(chr(REGIONAL_INDICATOR_BASE + ord(ch) - ord("A")) for ch in code)


def check_country_flag_emoji(record: dict[str, Any]) -> list[dict[str, Any]]:
    """flag_emoji must be mechanically derivable from the ISO alpha-2 code.

    Only enforced for official ISO codes: user-assigned and historical entities
    may carry non-standard or historical flags.
    """
    flag = record.get("flag_emoji")
    code = str(record.get("code", ""))
    if not flag or not ALPHA2.match(code) or record.get("code_status") != "official_iso3166_1":
        return []
    expected = flag_emoji_for_code(code)
    if str(flag) != expected:
        return [{
            "issue_type": "FLAG_EMOJI_MISMATCH",
            "field": "flag_emoji",
            "current_value": str(flag),
            "suggested_action": f"flag_emoji does not match the regional-indicator pair for '{code}' ({expected})",
        }]
    return []


def check_country_landlocked(record: dict[str, Any]) -> list[dict[str, Any]]:
    # borders holds ISO 3166-1 alpha-3 codes only, so non-ISO records
    # (user-assigned, obsolete) legitimately have empty borders even when
    # the entity is landlocked (e.g. XS, XT, XN).
    if record.get("code_status") != "official_iso3166_1":
        return []
    if record.get("landlocked") is True and not record.get("borders"):
        return [{
            "issue_type": "LANDLOCKED_INCONSISTENCY",
            "field": "landlocked",
            "current_value": "True",
            "suggested_action": "landlocked is true but borders is empty; an entity without land neighbors cannot be landlocked",
        }]
    return []


def check_country_region_hierarchy(
    record: dict[str, Any],
    allowlist: set[str] | None = None,
) -> list[dict[str, Any]]:
    """subregion must belong to at least one of the record's continents.

    Transcontinental or administratively reassigned entities are suppressed via
    ``region_hierarchy.allowlist`` (country codes) in countries_completeness.yaml.
    """
    allowlist = allowlist or set()
    code = str(record.get("code", ""))
    sub = record.get("subregion")
    continents = record.get("continents") or []
    if not sub or not continents or code in allowlist:
        return []
    known = [str(c) for c in continents if str(c) in CONTINENT_SUBREGIONS]
    if not known:
        return []  # unknown continent labels are a schema concern, not hierarchy
    if any(str(sub) in CONTINENT_SUBREGIONS[c] for c in known):
        return []
    return [{
        "issue_type": "REGION_HIERARCHY_MISMATCH",
        "field": "subregion",
        "current_value": str(sub),
        "suggested_action": (
            f"subregion '{sub}' does not belong to continents {known}; "
            "fix the value or allowlist the code in region_hierarchy.allowlist"
        ),
    }]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in kilometres."""
    p = math.pi / 180
    a = (
        0.5
        - math.cos((lat2 - lat1) * p) / 2
        + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos((lng2 - lng1) * p)) / 2
    )
    return 12742 * math.asin(math.sqrt(a))


def _coord_pair(obj: Any) -> tuple[float, float] | None:
    if not isinstance(obj, dict):
        return None
    try:
        lat = float(obj.get("lat"))
        lng = float(obj.get("lng"))
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None  # out-of-range coordinates are reported by INVALID_COORDINATES
    return (lat, lng)


def allowed_distance_km(
    area_km2: Any,
    *,
    min_km: float,
    area_multiplier: float,
    default_km: float,
) -> float:
    """Area-scaled distance budget: large countries legitimately place capitals
    or headquarters far from their centroid."""
    try:
        area = float(area_km2)
    except (TypeError, ValueError):
        return default_km
    if area <= 0:
        return default_km
    return max(min_km, area_multiplier * math.sqrt(area))


def check_country_capital_distance(
    record: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Capital must lie within an area-scaled distance of the centroid; catches
    swapped or mis-signed coordinates that pass range checks."""
    rule = ((config or {}).get("geography") or {}).get("capital_distance") or {}
    allowlist = {str(x) for x in (rule.get("allowlist") or [])}
    code = str(record.get("code", ""))
    if code in allowlist:
        return []
    cap = _coord_pair(record.get("capital_city"))
    cen = _coord_pair(record.get("centroid"))
    if cap is None or cen is None:
        return []
    dist = haversine_km(cap[0], cap[1], cen[0], cen[1])
    allowed = allowed_distance_km(
        (record.get("area") or {}).get("value") if isinstance(record.get("area"), dict) else None,
        min_km=float(rule.get("min_km", 500)),
        area_multiplier=float(rule.get("area_multiplier", 2.0)),
        default_km=float(rule.get("default_km", 1500)),
    )
    if dist > allowed:
        return [{
            "issue_type": "CAPITAL_FAR_FROM_CENTROID",
            "field": "capital_city",
            "current_value": f"lat={cap[0]}, lng={cap[1]}",
            "suggested_action": (
                f"capital is {dist:.0f} km from the centroid (allowed {allowed:.0f} km); "
                "check for swapped lat/lng or wrong sign, or allowlist the code"
            ),
        }]
    return []


def check_text_encoding(
    record: dict[str, Any],
    fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    """Control characters, U+FFFD, and double-encoded UTF-8 markers in text fields."""
    issues: list[dict[str, Any]] = []

    def scan(value: Any, field: str) -> None:
        if isinstance(value, str) and MOJIBAKE_RE.search(value):
            issues.append({
                "issue_type": "MOJIBAKE_TEXT",
                "field": field,
                "current_value": value[:120],
                "suggested_action": f"{field} contains control characters or double-encoded UTF-8; re-enter the text",
            })
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                scan(item, f"{field}[{idx}]")

    for field in fields:
        scan(record.get(field), field)
    return issues


def check_country_text_encoding(record: dict[str, Any]) -> list[dict[str, Any]]:
    return check_text_encoding(record, ("name", "official_name", "common_names"))


def check_country_filename(record: dict[str, Any], rel_path: str) -> list[dict[str, Any]]:
    code = str(record.get("code", ""))
    if not code:
        return []
    stem = rel_path.rsplit("/", 1)[-1]
    stem = stem[:-5] if stem.endswith(".yaml") else stem
    if stem != code:
        return [{
            "issue_type": "FILENAME_ID_MISMATCH",
            "field": "code",
            "current_value": code,
            "suggested_action": f"filename stem '{stem}' does not match code '{code}'",
        }]
    return []


def _resolve_field_path(record: dict[str, Any], field: str) -> bool:
    """True when a (possibly dotted) provenance field path exists on the record."""
    node: Any = record
    for part in str(field).split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return False
    return True


def check_provenance_integrity(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Provenance entries must reference existing fields with valid, non-future dates."""
    issues: list[dict[str, Any]] = []
    today = date.today()
    for idx, entry in enumerate(record.get("provenance") or []):
        if not isinstance(entry, dict):
            issues.append({
                "issue_type": "PROVENANCE_INTEGRITY",
                "field": f"provenance[{idx}]",
                "current_value": str(entry),
                "suggested_action": "Provenance entry must be a mapping",
            })
            continue
        field = entry.get("field")
        if not field or not _resolve_field_path(record, str(field)):
            issues.append({
                "issue_type": "PROVENANCE_INTEGRITY",
                "field": f"provenance[{idx}].field",
                "current_value": str(field),
                "suggested_action": f"provenance field '{field}' does not exist on the record",
            })
        retrieved = entry.get("retrieved_at")
        if retrieved is None:
            continue
        try:
            year, month, day = (int(p) for p in str(retrieved).split("-"))
            retrieved_date = date(year, month, day)
        except (TypeError, ValueError):
            issues.append({
                "issue_type": "PROVENANCE_INTEGRITY",
                "field": f"provenance[{idx}].retrieved_at",
                "current_value": str(retrieved),
                "suggested_action": f"retrieved_at '{retrieved}' is not a valid ISO date",
            })
            continue
        if retrieved_date > today:
            issues.append({
                "issue_type": "PROVENANCE_INTEGRITY",
                "field": f"provenance[{idx}].retrieved_at",
                "current_value": str(retrieved),
                "suggested_action": f"retrieved_at '{retrieved}' is in the future",
            })
    return issues


def check_provenance_count(
    record: dict[str, Any],
    *,
    min_count: int,
) -> list[dict[str, Any]]:
    """Report records whose provenance list has fewer than min_count entries."""
    if min_count <= 0:
        return []
    provenance = record.get("provenance") or []
    count = len(provenance) if isinstance(provenance, list) else 0
    if count >= min_count:
        return []
    return [{
        "issue_type": "INSUFFICIENT_PROVENANCE",
        "field": "provenance",
        "current_value": str(count),
        "suggested_action": (
            f"provenance has {count} entr{'y' if count == 1 else 'ies'}; "
            f"expected at least {min_count}"
        ),
    }]


def check_provenance_freshness(record: dict[str, Any], *, max_age_months: int) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    today = date.today()
    for entry in record.get("provenance") or []:
        if not isinstance(entry, dict):
            continue
        field = entry.get("field")
        retrieved = entry.get("retrieved_at")
        if not field or not retrieved:
            continue
        try:
            year, month, day = (int(p) for p in str(retrieved).split("-"))
            retrieved_date = date(year, month, day)
        except (TypeError, ValueError):
            continue  # invalid dates are reported by check_provenance_integrity
        age_months = (today.year - retrieved_date.year) * 12 + (today.month - retrieved_date.month)
        if age_months > max_age_months:
            issues.append({
                "issue_type": "STALE_PROVENANCE",
                "field": str(field),
                "current_value": str(retrieved),
                "suggested_action": f"provenance for '{field}' stale ({retrieved}, >{max_age_months} months)",
            })
    return issues


def check_country_duplicates(records: list[dict[str, Any]], rel_paths: list[str]) -> list[dict[str, Any]]:
    errors = []
    by_code = {}
    by_iso3 = {}
    by_numeric = {}

    for path, rec in zip(rel_paths, records, strict=False):
        record_id = rec.get("code", "unknown")
        for field, mapping in (
            ("code", by_code),
            ("iso3code", by_iso3),
            ("numeric_code", by_numeric),
        ):
            val = str(rec.get(field, ""))
            if not val:
                continue
            if val in mapping and mapping[val][0] != path:
                errors.append({
                    "issue_type": "DUPLICATE_IDENTIFIER",
                    "field": field,
                    "current_value": val,
                    "suggested_action": f"Duplicate {field} '{val}' found in both {path} and {mapping[val][0]}",
                    "file_path": path,
                    "record_id": record_id,
                    "other_path": mapping[val][0],
                })
            else:
                mapping[val] = (path, record_id)
    return errors


def validate_official_iso_count(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    count = sum(1 for r in records if r.get("code_status") == "official_iso3166_1")
    if count != EXPECTED_OFFICIAL_ISO_COUNT:
        errors.append({
            "issue_type": "INVALID_ISO_COUNT",
            "field": "code_status",
            "current_value": str(count),
            "suggested_action": f"Expected exactly {EXPECTED_OFFICIAL_ISO_COUNT} official_iso3166_1 records, but found {count}"
        })
    return errors


def validate_completeness(
    records: list[dict[str, Any]],
    config: dict[str, Any],
    *,
    null_checker=None,
    attach_field_priority: bool = False,
) -> list[dict[str, Any]]:
    from internacia_builder.validate.completeness import priority_level

    errors = []
    n = len(records)
    if n == 0:
        return errors
    checker = null_checker or is_null_field
    fields_cfg = config.get("fields", {})
    for field, rules in fields_cfg.items():
        null_count = sum(1 for r in records if checker(r, field))
        null_rate = null_count / n
        max_rate = float(rules.get("max_null_rate", 1.0))
        mode = rules.get("mode", "warn")
        if null_rate > max_rate:
            issue_type = "COMPLETENESS_ERROR" if mode == "error" else "COMPLETENESS_WARN"
            issue = {
                "issue_type": issue_type,
                "field": field,
                "current_value": f"{null_rate:.2%} null rate ({null_count}/{n})",
                "suggested_action": f"Ensure {field} is populated (max null rate allowed: {max_rate:.2%})",
            }
            if attach_field_priority:
                issue["priority"] = priority_level(config, field)
            errors.append(issue)
    return errors
