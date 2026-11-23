"""Validation of the trade agreements registry (``data/trade_agreements/*.yaml``).

Cross-record rules: the JSON Schema, file names and ids, the shared id namespace with
intblocks, party and intblock resolution, status and date consistency, supersession links,
and record freshness. See ``openspec/changes/add-trade-agreements-registry``.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema

from internacia_builder.trade_agreements import PARTY_INCLUDE_STATUSES, linked_fields

Issue = dict[str, Any]

# Statuses that need a date on the agreement row (after a linked record reads its intblock).
NEEDS_SIGNED = frozenset({"signed"})
NEEDS_IN_FORCE = frozenset({"in_force", "terminated", "superseded"})
NEEDS_ENDED = frozenset({"terminated", "superseded"})
CANDIDATE_STATUSES = frozenset({"signed", "in_force"})
# Catalogue identifiers: each value names one instrument, so it appears on one record.
CATALOGUE_IDS = ("wto_rta_id", "aric_id", "gptad_id", "dta_id")
# Investment treaty ids end in -BIT, or -BIT-YYYY for a further treaty between the same parties.
INVESTMENT_ID_SUFFIX = re.compile(r"-BIT(-\d{4})?$")


def _issue(issue_type: str, path: str, record_id: str, field: str, value: Any, action: str) -> Issue:
    return {
        "issue_type": issue_type,
        "file_path": path,
        "record_id": record_id,
        "field": field,
        "current_value": "" if value is None else str(value),
        "suggested_action": action,
    }


def _dates(record: dict[str, Any], intblock: dict[str, Any] | None) -> dict[str, Any]:
    """The agreement's dates as exported: the record's own, else the linked intblock's.

    A record with ``provisional_application`` takes ``in_force`` only from itself, so an
    intblock's start date is not read as a definitive entry into force.
    """
    fields = linked_fields(intblock) if intblock is not None else {}
    if record.get("provisional_application"):
        fields = {k: v for k, v in fields.items() if k != "in_force"}
    dates = {k: record.get(k) or fields.get(k) for k in ("signed", "in_force", "ended")}
    dates["provisional_application"] = record.get("provisional_application")
    return dates


def check_trade_agreements(
    records: list[dict[str, Any]],
    paths: list[str],
    schema: dict[str, Any],
    intblocks: list[dict[str, Any]],
    country_codes: set[str],
    aliases: list[dict[str, Any]] | None = None,
) -> list[Issue]:
    """Schema, identifier, resolution, status and date rules for registry records."""
    issues: list[Issue] = []
    validator = jsonschema.validators.validator_for(schema)(schema) if schema else None
    intblocks_by_id = {str(r.get("id")): r for r in intblocks if r.get("id")}
    registry_ids = {str(r.get("id")) for r in records if r.get("id")}
    other_aliases = {
        str(a.get("alias")): a
        for a in aliases or []
        if isinstance(a, dict) and a.get("reason") != "moved"
    }
    seen: dict[str, str] = {}
    seen_catalogue: dict[tuple[str, Any], str] = {}
    for record, path in zip(records, paths, strict=True):
        rid = str(record.get("id") or "")
        if validator is not None:
            errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
            for error in errors:
                field = ".".join(str(p) for p in error.path) or "(root)"
                issues.append({
                    "issue_type": "SCHEMA_ERROR",
                    "file_path": path,
                    "record_id": rid or "unknown",
                    "field": field,
                    "current_value": "",
                    "suggested_action": error.message,
                })
            if errors:
                continue
        stem = Path(path).stem
        if stem != rid:
            issues.append(_issue("FILENAME_ID_MISMATCH", path, rid, "id", rid, f"Rename the file to {rid}.yaml or fix the id"))
        if rid in seen:
            issues.append({
                "issue_type": "DUPLICATE_IDENTIFIER",
                "file_path": path,
                "record_id": rid,
                "field": "id",
                "current_value": rid,
                "suggested_action": f"Trade agreement id {rid} is also used by {seen[rid]}",
            })
        seen.setdefault(rid, path)
        for key in CATALOGUE_IDS:
            value = record.get(key)
            if value is None:
                continue
            if (key, value) in seen_catalogue:
                issues.append({
                    "issue_type": "DUPLICATE_IDENTIFIER",
                    "file_path": path,
                    "record_id": rid,
                    "field": key,
                    "current_value": str(value),
                    "suggested_action": f"{key} {value} is also set on {seen_catalogue[(key, value)]}; one catalogue entry maps to one record",
                })
            seen_catalogue.setdefault((key, value), rid)

        linked = record.get("intblock")
        intblock = intblocks_by_id.get(str(linked)) if linked else None
        if rid in intblocks_by_id and str(linked or "") != rid:
            issues.append({
                "issue_type": "TRADE_AGREEMENT_ID_COLLISION",
                "file_path": path,
                "record_id": rid,
                "field": "id",
                "current_value": rid,
                "suggested_action": f"Id {rid} is an intblock id; use another id or link the record with intblock: {rid}",
            })
        if rid in other_aliases:
            issues.append({
                "issue_type": "TRADE_AGREEMENT_ID_COLLISION",
                "file_path": path,
                "record_id": rid,
                "field": "id",
                "current_value": rid,
                "suggested_action": f"Id {rid} is a registered intblock alias ({other_aliases[rid].get('reason')}); use another id",
            })

        investment = record.get("agreement_type") == "investment"
        if investment and not linked and not INVESTMENT_ID_SUFFIX.search(rid):
            issues.append(_issue(
                "TRADE_AGREEMENT_ID_SUFFIX", path, rid, "id", rid,
                "An investment treaty that is not linked to an intblock needs an id ending in -BIT or -BIT-YYYY",
            ))
        if INVESTMENT_ID_SUFFIX.search(rid) and not investment:
            issues.append(_issue(
                "TRADE_AGREEMENT_ID_SUFFIX", path, rid, "agreement_type", record.get("agreement_type"),
                "An id ending in -BIT or -BIT-YYYY is reserved for agreement_type: investment",
            ))
        if linked and intblock is None:
            issues.append({
                "issue_type": "UNRESOLVED_TRADE_AGREEMENT_REF",
                "file_path": path,
                "record_id": rid,
                "field": "intblock",
                "current_value": linked,
                "suggested_action": f"intblock {linked} does not match any intblock id",
            })
        if linked and record.get("verification") != "official":
            issues.append({
                "issue_type": "TRADE_AGREEMENT_VERIFICATION_CONFLICT",
                "file_path": path,
                "record_id": rid,
                "field": "verification",
                "current_value": record.get("verification"),
                "suggested_action": "A record linked to an intblock takes its roster from it; set verification: official",
            })
        if intblock is not None:
            ever = [
                inc for inc in intblock.get("includes") or []
                if isinstance(inc, dict) and inc.get("status") in PARTY_INCLUDE_STATUSES
            ]
            if len(ever) < 3:
                issues.append({
                    "issue_type": "TRADE_AGREEMENT_PARTY_COUNT",
                    "file_path": path,
                    "record_id": rid,
                    "field": "intblock",
                    "current_value": linked,
                    "suggested_action": (
                        f"intblock {linked} has {len(ever)} parties; an agreement with two parties lists "
                        "them in parties and has no intblock"
                    ),
                })

        party_ids: set[str] = set()
        for index, party in enumerate(record.get("parties") or []):
            pid = str(party.get("id"))
            field = f"parties[{index}].id"
            if pid in party_ids:
                issues.append({
                    "issue_type": "DUPLICATE_TRADE_AGREEMENT_PARTY",
                    "file_path": path,
                    "record_id": rid,
                    "field": field,
                    "current_value": pid,
                    "suggested_action": f"Party {pid} is listed twice",
                })
            party_ids.add(pid)
            known = country_codes if party.get("type") == "country" else set(intblocks_by_id)
            if pid not in known:
                issues.append({
                    "issue_type": "UNRESOLVED_TRADE_AGREEMENT_PARTY",
                    "file_path": path,
                    "record_id": rid,
                    "field": field,
                    "current_value": pid,
                    "suggested_action": f"Party {pid} does not match any {party.get('type')} id",
                })

        status = record.get("status")
        dates = _dates(record, intblock)
        for needed, key in ((NEEDS_SIGNED, "signed"), (NEEDS_IN_FORCE, "in_force"), (NEEDS_ENDED, "ended")):
            # An agreement applied provisionally counts as in force without a definitive date.
            if key == "in_force" and dates.get("provisional_application"):
                continue
            if status in needed and not dates.get(key):
                issues.append({
                    "issue_type": "TRADE_AGREEMENT_STATUS_DATE",
                    "file_path": path,
                    "record_id": rid,
                    "field": key,
                    "current_value": status,
                    "suggested_action": f"status {status} needs a {key} date"
                    + (" (read from the linked intblock)" if intblock is not None else ""),
                })
        for key in ("in_force", "provisional_application"):
            if status in {"signed", "proposed", "negotiating", "abandoned"} and dates.get(key):
                issues.append({
                    "issue_type": "TRADE_AGREEMENT_STATUS_DATE",
                    "file_path": path,
                    "record_id": rid,
                    "field": key,
                    "current_value": status,
                    "suggested_action": f"status {status} contradicts the {key} date {dates[key]}",
                })
        # An agreement may enter into force retroactively (ANZCERTA: signed 28 March 1983, in
        # force from 1 January 1983), so only ``ended`` is checked against the earlier dates.
        # Compare at the shared precision, so 2018 and 2018-07-17 do not conflict.
        ended = dates.get("ended")
        for key in ("signed", "in_force", "provisional_application"):
            value = dates.get(key)
            if ended and value:
                n = min(len(str(value)), len(str(ended)))
                if str(value)[:n] > str(ended)[:n]:
                    issues.append({
                        "issue_type": "TRADE_AGREEMENT_STATUS_DATE",
                        "file_path": path,
                        "record_id": rid,
                        "field": "ended",
                        "current_value": f"{key}={value}, ended={ended}",
                        "suggested_action": f"ended is earlier than {key}",
                    })

        for key in ("supersedes", "superseded_by"):
            ref = record.get(key)
            if ref and str(ref) not in registry_ids:
                issues.append({
                    "issue_type": "UNRESOLVED_TRADE_AGREEMENT_REF",
                    "file_path": path,
                    "record_id": rid,
                    "field": key,
                    "current_value": ref,
                    "suggested_action": f"{key} {ref} does not match any trade agreement id",
                })
        if status == "superseded" and not record.get("superseded_by"):
            issues.append({
                "issue_type": "TRADE_AGREEMENT_STATUS_DATE",
                "file_path": path,
                "record_id": rid,
                "field": "superseded_by",
                "current_value": status,
                "suggested_action": "status superseded needs superseded_by",
            })
    return issues


def check_trade_agreement_files(errors: list[tuple[str, str]]) -> list[Issue]:
    """Files under data/trade_agreements/ that are not valid YAML mappings."""
    return [
        {
            "issue_type": "SCHEMA_ERROR",
            "file_path": path,
            "record_id": Path(path).stem,
            "field": "(root)",
            "current_value": "",
            "suggested_action": message,
        }
        for path, message in errors
    ]


def check_intblock_candidates(records: list[dict[str, Any]], paths: list[str]) -> list[Issue]:
    """Report-only: signed or in-force agreements with three or more listed parties and no intblock."""
    issues: list[Issue] = []
    for record, path in zip(records, paths, strict=True):
        parties = [p for p in record.get("parties") or [] if isinstance(p, dict) and not p.get("left")]
        if record.get("intblock") or record.get("status") not in CANDIDATE_STATUSES or len(parties) < 3:
            continue
        issues.append({
            "issue_type": "TRADE_AGREEMENT_INTBLOCK_CANDIDATE",
            "file_path": path,
            "record_id": str(record.get("id")),
            "field": "parties",
            "current_value": str(len(parties)),
            "suggested_action": "Add an intblock with a roster from an official source and link it with intblock:",
        })
    return issues


def check_trade_agreement_freshness(
    records: list[dict[str, Any]], paths: list[str], max_age_months: int, today: date | None = None
) -> list[Issue]:
    """Warn when a record's ``last_verified`` is older than the configured threshold."""
    if max_age_months <= 0:
        return []
    today = today or date.today()
    issues: list[Issue] = []
    for record, path in zip(records, paths, strict=True):
        raw = record.get("last_verified")
        try:
            checked = date.fromisoformat(str(raw))
        except ValueError:
            continue
        months = (today.year - checked.year) * 12 + (today.month - checked.month)
        if months > max_age_months:
            issues.append({
                "issue_type": "STALE_TRADE_AGREEMENT",
                "file_path": path,
                "record_id": str(record.get("id")),
                "field": "last_verified",
                "current_value": str(raw),
                "suggested_action": f"last_verified is {months} months old; re-check the record",
            })
    return issues
