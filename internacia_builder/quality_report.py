"""Data-quality report generators used by the ``analyze-quality`` command.

NOTE: several rules configured here intentionally mirror
``internacia_builder.validate.*`` (known duplication tracked in the
``refactor-builder-into-package`` OpenSpec change). Keep the two consistent
when editing either side.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

# ==============================================================================
# Data Quality Analysis and Reporting
# ==============================================================================

# Priority mapping for issue types
ISSUE_PRIORITY_MAP = {
    "CRITICAL": [
        "SCHEMA_ERROR",
        "DUPLICATE_IDENTIFIER",
        "DUPLICATE_INTBLOCK_ID",
    ],
    "IMPORTANT": [
        "INVALID_BORDER_REFERENCE",
        "UNRESOLVED_BORDER_REFERENCE",
        "UNRESOLVED_ORG_REF",
        "UNRESOLVED_HQ_COUNTRY",
        "DUPLICATE_WIKIDATA_ID",
        "FILENAME_ID_MISMATCH",
        "DIRECTORY_BLOCKTYPE_MISMATCH",
        "INVALID_INDICATOR_YEAR",
        "INVALID_ENTITY_TYPE",
        "INVALID_CODE_STATUS",
        "INVALID_ISO_COUNT",
        "UNKNOWN_BLOCKTYPE",
        "ALIAS_INTEGRITY_ERROR",
        "UNRESOLVED_COUNTRY_INCLUDE",
        "COMPLETENESS_ERROR",
        "MISSING_MANDATORY_FIELD",
        "MISSING_INCLUDES_APPLICABILITY",
        "INVALID_INCLUDE_STATUS",
        "UNRESOLVED_PARENT_ENTITY",
        "INVALID_PARTOF_TARGET",
        "MISSING_WIKIDATA_ID",
    ],
    "MEDIUM": [
        "UNRESOLVED_PARTOF_REF",
        "NONRECIPROCAL_BORDER",
        "LIFECYCLE_INCONSISTENCY",
        "CHRONOLOGY_ERROR",
        "DUPLICATE_INCLUDE_ENTRY",
        "MEMBERSHIP_COUNT_MISMATCH",
        "CONTRADICTORY_APPLICABILITY",
        "INVALID_INDICATOR_VALUE",
        "INCONSISTENT_ENTITY_FLAGS",
        "INVALID_CURRENCY_CODE",
        "INVALID_COORDINATES",
        "PROVENANCE_INTEGRITY",
        "INSUFFICIENT_PROVENANCE",
        "TEMPLATED_DESCRIPTION",
        "COMPLETENESS_WARN",
        "MISSING_PREFERRED_FIELD",
        "INVALID_URL",
        "INVALID_ID",
        "INVALID_TLD",
        "INVALID_CALLING_CODE",
        "INVALID_TIMEZONE",
        "FLAG_EMOJI_MISMATCH",
        "LANDLOCKED_INCONSISTENCY",
        "REGION_HIERARCHY_MISMATCH",
        "CAPITAL_FAR_FROM_CENTROID",
        "HQ_COORDINATES_OUTSIDE_COUNTRY",
        "INCLUDE_DATE_INCONSISTENCY",
        "FOUNDING_MEMBER_NOT_INCLUDED",
        "HISTORICAL_ENTITY_ACTIVE_MEMBER",
        "UNKNOWN_TOPIC_KEY",
        "MOJIBAKE_TEXT",
    ],
    "LOW": [
        "WHITESPACE_IN_CATEGORICAL_FIELD",
        "DUPLICATE_LINK",
        "DEPRECATED_TOPIC_KEY",
        "STALE_PROVENANCE",
        "INCLUDE_NAME_MISMATCH",
        "STALE_LAST_VERIFIED",
        "SUCCESSOR_RECIPROCITY",
        "PARTOF_SUBORG_RECIPROCITY",
        "DUPLICATE_ACRONYM",
    ],
}

RULE_DESCRIPTIONS = {
    "SCHEMA_ERROR": "YAML source does not validate against its JSON Schema definition.",
    "DUPLICATE_IDENTIFIER": "Multiple countries share the same code, ISO3 code, or numeric code.",
    "DUPLICATE_INTBLOCK_ID": "Multiple intblocks share the same ID.",
    "INVALID_BORDER_REFERENCE": "Country borders list references a non-existent or invalid alpha-3 code.",
    "INVALID_INDICATOR_YEAR": "Population, area, or Gini index contains a zero or negative year.",
    "INVALID_ENTITY_TYPE": "Country record has an invalid or missing entity type classification.",
    "INVALID_CODE_STATUS": "Country record has an invalid or missing ISO code status classification.",
    "INVALID_ISO_COUNT": "Total count of official ISO 3166-1 country records does not match the expected count (249).",
    "UNKNOWN_BLOCKTYPE": "An intblock references a blocktype not defined in the taxonomy.",
    "UNRESOLVED_PARTOF_REF": "An intblock's partof references a non-existent intblock ID.",
    "LIFECYCLE_INCONSISTENCY": "Historical intblock uses non-standard ended key or has status mismatch.",
    "ALIAS_INTEGRITY_ERROR": "Acronym alias targets an unresolved ID or is misconfigured.",
    "TEMPLATED_DESCRIPTION": "An intblock uses templated boilerplate description.",
    "UNRESOLVED_COUNTRY_INCLUDE": "An intblock's includes references a non-existent country code.",
    "COMPLETENESS_ERROR": "Completeness validation failed (error mode) due to too many missing values.",
    "COMPLETENESS_WARN": "Completeness validation warned (warn mode) due to missing values.",
    "MISSING_MANDATORY_FIELD": "A mandatory intblock field is missing or empty.",
    "MISSING_PREFERRED_FIELD": "A preferred intblock field is missing or empty.",
    "MISSING_INCLUDES_APPLICABILITY": "Record lacks includes and has no membership_applicability marker.",
    "INVALID_INCLUDE_STATUS": "An includes entry uses a status not defined in includes_status.yaml.",
    "WHITESPACE_IN_CATEGORICAL_FIELD": "Leading/trailing whitespace found in categorical text fields.",
    "DUPLICATE_LINK": "Multiple records share the same external URL.",
    "INVALID_URL": "A URL in the intblock is invalid or inaccessible.",
    "INVALID_ID": "A Wikidata Q-ID is invalid or doesn't match the record's name.",
    "UNRESOLVED_BORDER_REFERENCE": "A border alpha-3 code does not resolve to any country's iso3code, or references the record itself.",
    "NONRECIPROCAL_BORDER": "Country A lists B as a border but B does not list A back (allowlisted pairs suppressed).",
    "UNRESOLVED_ORG_REF": "predecessor/successor/suborganizations references a non-existent intblock id or alias.",
    "UNRESOLVED_HQ_COUNTRY": "headquarters.country does not resolve to any country file or allowlisted entity.",
    "DUPLICATE_WIKIDATA_ID": "Two or more records share the same wikidata_id (allowlisted Q-ids suppressed).",
    "FILENAME_ID_MISMATCH": "YAML filename stem does not match the record's code/id.",
    "DIRECTORY_BLOCKTYPE_MISMATCH": "Intblock category directory is not present in the record's blocktype list.",
    "CHRONOLOGY_ERROR": "founded/dissolved dates are unparseable, out of order, or in the future.",
    "DUPLICATE_INCLUDE_ENTRY": "The same country id appears more than once in an intblock's includes list.",
    "MEMBERSHIP_COUNT_MISMATCH": "membership_count matches neither the total nor the member-class includes count.",
    "CONTRADICTORY_APPLICABILITY": "membership_applicability is not_applicable but the includes list is populated.",
    "INVALID_INDICATOR_VALUE": "Population, area, or Gini value is outside the plausible range, or the year is in the future.",
    "INCONSISTENT_ENTITY_FLAGS": "un_member/independent flags contradict the record's entity_type.",
    "INVALID_CURRENCY_CODE": "A currency code is not a valid ISO 4217 uppercase code.",
    "INVALID_COORDINATES": "Latitude/longitude outside valid ranges in centroid, capital_city, or headquarters coordinates.",
    "PROVENANCE_INTEGRITY": "A provenance entry references a non-existent field or has an invalid/future retrieved_at date.",
    "INSUFFICIENT_PROVENANCE": "The provenance list has fewer entries than the configured minimum.",
    "DEPRECATED_TOPIC_KEY": "A topic key is deprecated in topic_aliases.yaml and should use its canonical replacement.",
    "STALE_PROVENANCE": "A provenance entry is older than the configured maximum age.",
    "INCLUDE_NAME_MISMATCH": "Advisory: includes[].name differs from every known name variant of the referenced country (display-only).",
    "INVALID_TLD": "tld is not a lowercase '.xx'-style top-level domain.",
    "INVALID_CALLING_CODE": "A calling_codes entry is not '+' followed by digits.",
    "INVALID_TIMEZONE": "A timezones entry is not in the IANA tz database.",
    "FLAG_EMOJI_MISMATCH": "flag_emoji does not match the regional-indicator pair derived from the ISO code.",
    "LANDLOCKED_INCONSISTENCY": "landlocked is true but the borders list is empty.",
    "REGION_HIERARCHY_MISMATCH": "subregion does not belong to any of the record's continents (allowlisted exceptions suppressed).",
    "CAPITAL_FAR_FROM_CENTROID": "Capital coordinates exceed the area-scaled distance budget from the centroid (likely swapped/mis-signed).",
    "UNRESOLVED_PARENT_ENTITY": "parent_entity.code does not resolve to any country record.",
    "HQ_COORDINATES_OUTSIDE_COUNTRY": "Headquarters coordinates exceed the area-scaled distance budget from the HQ country's centroid.",
    "INCLUDE_DATE_INCONSISTENCY": "includes[].joined/left dates are unparseable, future, misordered, or postdate dissolution.",
    "FOUNDING_MEMBER_NOT_INCLUDED": "A founding_members entry does not resolve to a country or is absent from includes.",
    "HISTORICAL_ENTITY_ACTIVE_MEMBER": "An active block lists a historical entity country with an active-class include status.",
    "STALE_LAST_VERIFIED": "last_verified is older than the configured maximum age (advisory).",
    "UNKNOWN_TOPIC_KEY": "A topic key is absent from the canonical catalog data/schemas/topics.yaml.",
    "MOJIBAKE_TEXT": "Text contains control characters, U+FFFD, or double-encoded UTF-8 artifacts.",
    "SUCCESSOR_RECIPROCITY": "Advisory: a resolved predecessor/successor reference lacks its reverse link.",
    "PARTOF_SUBORG_RECIPROCITY": "Advisory: a record listed in a parent's suborganizations does not declare that parent in partof.",
    "DUPLICATE_ACRONYM": "Advisory: unrelated same-blocktype records share an English acronym (possible duplicate entity).",
}

def get_priority_level(issue_type: str, issue: dict[str, Any] | None = None) -> str:
    if issue and issue.get("priority"):
        return str(issue["priority"])
    for priority, issue_types in ISSUE_PRIORITY_MAP.items():
        if issue_type in issue_types:
            return priority
    return "MEDIUM"

def extract_country_codes(record: dict[str, Any], dataset_type: str) -> list[str]:
    codes = []
    if dataset_type == "countries":
        code = record.get("code")
        if code:
            codes.append(str(code).upper())
    elif dataset_type == "intblocks":
        # Headquarters country
        hq = record.get("headquarters") or {}
        hq_country = hq.get("country")
        if hq_country and len(str(hq_country)) == 2:
            codes.append(str(hq_country).upper())

        # Includes countries
        for inc in record.get("includes") or []:
            if isinstance(inc, dict) and inc.get("type") == "country":
                cid = inc.get("id")
                if cid and len(str(cid)) == 2:
                    c_upper = str(cid).upper()
                    if c_upper not in codes:
                        codes.append(c_upper)
    return codes if codes else ["UNKNOWN"]


# Rule checker implementations live in internacia_builder.validate.country_rules,
# intblock_rules, and cross_rules (shared with the CLI validators).




# Report Writers

def generate_full_report(issues: list[dict[str, Any]], records_with_issues: dict[str, Any], total_records: int, output_path: Path) -> None:
    report_lines = []
    report_lines.append("DATA QUALITY ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Records Analyzed: {total_records}")
    report_lines.append(f"Total Issues Found: {len(issues)}")
    report_lines.append(f"Records with Issues: {len(records_with_issues)}")
    report_lines.append("")

    issues_by_type = {}
    for issue in issues:
        issue_type = issue["issue_type"]
        issues_by_type.setdefault(issue_type, []).append(issue)

    report_lines.append("=== ISSUES BY TYPE ===")
    report_lines.append("")

    for issue_type in sorted(issues_by_type.keys()):
        issues_list = issues_by_type[issue_type]
        report_lines.append(f"[{issue_type}]")
        report_lines.append(f"Count: {len(issues_list)}")
        report_lines.append(f"Priority: {issues_list[0].get('priority', 'MEDIUM')}")
        report_lines.append("")

        for issue in issues_list[:50]:
            report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
            report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
            report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Issue: {issue_type}")
            report_lines.append(f"Field: {issue.get('field', 'unknown')}")
            report_lines.append(f"Current Value: {issue.get('current_value')}")
            report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
            report_lines.append("")

        if len(issues_list) > 50:
            n = len(issues_list) - 50
            report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
            report_lines.append("")

    report_lines.append("")
    report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
    report_lines.append("")
    for issue_type in sorted(issues_by_type.keys()):
        count = len(issues_by_type[issue_type])
        priority = issues_by_type[issue_type][0].get("priority", "MEDIUM") if issues_by_type[issue_type] else "MEDIUM"
        report_lines.append(f"{issue_type} ({priority}): {count} issue" + ("s" if count != 1 else ""))

    report_lines.append("")
    report_lines.append("=== SUMMARY BY PRIORITY ===")
    report_lines.append("")
    issues_by_priority = {}
    for issue in issues:
        priority = issue.get("priority", "MEDIUM")
        issues_by_priority.setdefault(priority, []).append(issue)

    for priority in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        if priority in issues_by_priority:
            count = len(issues_by_priority[priority])
            report_lines.append(f"{priority}: {count} issue" + ("s" if count != 1 else ""))

    report_lines.append("")
    report_lines.append("=== RECORDS WITH MULTIPLE ISSUES (3+) ===")
    report_lines.append("")

    multi_issue_records = {
        rid: data for rid, data in records_with_issues.items() if len(data["issues"]) >= 3
    }

    if multi_issue_records:
        for record_id, data in sorted(multi_issue_records.items(), key=lambda x: len(x[1]["issues"]), reverse=True)[:100]:
            report_lines.append(f"Record ID: {record_id}")
            report_lines.append(f"File: {data.get('file_path', 'unknown')}")
            report_lines.append(f"Country: {data.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Issue Count: {len(data['issues'])}")
            report_lines.append("Issues:")
            for issue in data["issues"]:
                report_lines.append(f"  - {issue['issue_type']} ({issue.get('priority', 'MEDIUM')}): {issue['field']}")
            report_lines.append("")
    else:
        report_lines.append("No records found with 3+ issues")

    output_path.write_text("\n".join(report_lines), encoding="utf-8")

def generate_country_reports(issues_by_country: dict[str, list[dict[str, Any]]], records_by_country: dict[str, dict[str, Any]], output_dir: Path) -> None:
    countries_dir = output_dir / "countries"
    countries_dir.mkdir(parents=True, exist_ok=True)

    countries_with_issues = {c for c, issues in issues_by_country.items() if issues}
    if countries_dir.exists():
        for f in countries_dir.iterdir():
            if f.is_file() and f.name.endswith(".txt"):
                country_code = f.name[:-4]
                if country_code not in countries_with_issues:
                    f.unlink()

    for country_code, country_issues in issues_by_country.items():
        if not country_issues:
            continue

        country_records = records_by_country.get(country_code, {})
        report_lines = []
        report_lines.append(f"DATA QUALITY REPORT - COUNTRY: {country_code}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Country Code: {country_code}")
        report_lines.append(f"Total Records with Issues: {len(country_records)}")
        report_lines.append(f"Total Issues Found: {len(country_issues)}")
        report_lines.append("")

        issues_by_type = {}
        for issue in country_issues:
            issue_type = issue["issue_type"]
            issues_by_type.setdefault(issue_type, []).append(issue)

        report_lines.append("=== ISSUES BY TYPE ===")
        report_lines.append("")

        for issue_type in sorted(issues_by_type.keys()):
            issues_list = issues_by_type[issue_type]
            report_lines.append(f"[{issue_type}]")
            report_lines.append(f"Count: {len(issues_list)}")
            report_lines.append(f"Priority: {issues_list[0].get('priority', 'MEDIUM')}")
            report_lines.append("")

            for issue in issues_list[:100]:
                report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
                report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
                report_lines.append(f"Issue: {issue_type}")
                report_lines.append(f"Field: {issue.get('field', 'unknown')}")
                report_lines.append(f"Current Value: {issue.get('current_value')}")
                report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
                report_lines.append("")

            if len(issues_list) > 100:
                n = len(issues_list) - 100
                report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
                report_lines.append("")

        report_lines.append("")
        report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
        report_lines.append("")
        for issue_type in sorted(issues_by_type.keys()):
            count = len(issues_by_type[issue_type])
            report_lines.append(f"{issue_type}: {count} issue" + ("s" if count != 1 else ""))

        multi_issue_records = {
            rid: data for rid, data in country_records.items() if len(data["issues"]) >= 3
        }

        if multi_issue_records:
            report_lines.append("")
            report_lines.append("=== RECORDS WITH MULTIPLE ISSUES (3+) ===")
            report_lines.append("")
            for record_id, data in sorted(multi_issue_records.items(), key=lambda x: len(x[1]["issues"]), reverse=True)[:50]:
                report_lines.append(f"Record ID: {record_id}")
                report_lines.append(f"File: {data.get('file_path', 'unknown')}")
                report_lines.append(f"Issue Count: {len(data['issues'])}")
                report_lines.append("Issues:")
                for issue in data["issues"]:
                    report_lines.append(f"  - {issue['issue_type']}: {issue['field']}")
                report_lines.append("")

        country_file = countries_dir / f"{country_code}.txt"
        country_file.write_text("\n".join(report_lines), encoding="utf-8")

def generate_priority_reports(issues_by_priority: dict[str, list[dict[str, Any]]], output_dir: Path) -> None:
    priorities_dir = output_dir / "priorities"
    priorities_dir.mkdir(parents=True, exist_ok=True)

    for priority in ["CRITICAL", "IMPORTANT", "MEDIUM", "LOW"]:
        priority_issues = issues_by_priority.get(priority, [])
        report_lines = []
        if not priority_issues:
            report_lines.append(f"DATA QUALITY REPORT - PRIORITY: {priority}")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Priority Level: {priority}")
            report_lines.append("Total Issues Found: 0")
            report_lines.append("")
            report_lines.append("No issues at this priority level.")
            priority_file = priorities_dir / f"{priority}.txt"
            priority_file.write_text("\n".join(report_lines), encoding="utf-8")
            continue

        report_lines.append(f"DATA QUALITY REPORT - PRIORITY: {priority}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Priority Level: {priority}")
        report_lines.append(f"Total Issues Found: {len(priority_issues)}")
        report_lines.append("")

        issues_by_type = {}
        for issue in priority_issues:
            issue_type = issue["issue_type"]
            issues_by_type.setdefault(issue_type, []).append(issue)

        report_lines.append("=== ISSUES BY TYPE ===")
        report_lines.append("")

        for issue_type in sorted(issues_by_type.keys()):
            issues_list = issues_by_type[issue_type]
            report_lines.append(f"[{issue_type}]")
            report_lines.append(f"Count: {len(issues_list)}")
            report_lines.append("")

            for issue in issues_list[:100]:
                report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
                report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
                report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
                report_lines.append(f"Issue: {issue_type}")
                report_lines.append(f"Field: {issue.get('field', 'unknown')}")
                report_lines.append(f"Current Value: {issue.get('current_value')}")
                report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
                report_lines.append("")

            if len(issues_list) > 100:
                n = len(issues_list) - 100
                report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
                report_lines.append("")

        report_lines.append("")
        report_lines.append("=== SUMMARY BY ISSUE TYPE ===")
        report_lines.append("")
        for issue_type in sorted(issues_by_type.keys()):
            count = len(issues_by_type[issue_type])
            report_lines.append(f"{issue_type}: {count} issue" + ("s" if count != 1 else ""))

        report_lines.append("")
        report_lines.append("=== SUMMARY BY COUNTRY ===")
        report_lines.append("")
        issues_by_country = {}
        for issue in priority_issues:
            country_code = issue.get("country_code", "UNKNOWN")
            issues_by_country.setdefault(country_code, []).append(issue)

        for country_code in sorted(issues_by_country.keys()):
            count = len(issues_by_country[country_code])
            report_lines.append(f"{country_code}: {count} issue" + ("s" if count != 1 else ""))

        priority_file = priorities_dir / f"{priority}.txt"
        priority_file.write_text("\n".join(report_lines), encoding="utf-8")

def generate_rule_reports(issues_by_type: dict[str, list[dict[str, Any]]], output_dir: Path) -> None:
    rules_dir = output_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    known_issue_types = []
    for issue_types in ISSUE_PRIORITY_MAP.values():
        known_issue_types.extend(issue_types)

    for issue_type in known_issue_types:
        if not issues_by_type.get(issue_type):
            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", issue_type)
            rule_file = rules_dir / f"{safe_name}.txt"
            if rule_file.exists():
                rule_file.unlink()

    for issue_type, issues_list in issues_by_type.items():
        if not issues_list:
            continue

        priority = issues_list[0].get("priority", "MEDIUM")
        report_lines = []
        report_lines.append(f"DATA QUALITY REPORT - RULE: {issue_type}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Issue Type: {issue_type}")
        report_lines.append(f"Priority: {priority}")
        report_lines.append(f"Total Issues Found: {len(issues_list)}")

        rule_desc = RULE_DESCRIPTIONS.get(issue_type)
        if rule_desc:
            report_lines.append("")
            report_lines.append(f"Description: {rule_desc}")

        report_lines.append("")
        report_lines.append("=== AFFECTED RECORDS ===")
        report_lines.append("")

        for issue in issues_list[:100]:
            report_lines.append(f"File: {issue.get('file_path', 'unknown')}")
            report_lines.append(f"Record ID: {issue.get('record_id', 'unknown')}")
            report_lines.append(f"Country: {issue.get('country_code', 'UNKNOWN')}")
            report_lines.append(f"Field: {issue.get('field', 'unknown')}")
            report_lines.append(f"Current Value: {issue.get('current_value')}")
            report_lines.append(f"Suggested Action: {issue.get('suggested_action')}")
            report_lines.append("")

        if len(issues_list) > 100:
            n = len(issues_list) - 100
            report_lines.append(f"... and {n} more record" + ("s" if n != 1 else "") + " with this issue")
            report_lines.append("")

        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", issue_type)
        rule_file = rules_dir / f"{safe_name}.txt"
        rule_file.write_text("\n".join(report_lines), encoding="utf-8")
