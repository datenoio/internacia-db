"""``last_verified``: the verification KPI and the rule for changed records.

``last_verified`` says when a person last checked a record's roster against the source in
its ``provenance``. The KPI tracks how many records were never verified or are overdue; the
rule makes every new or changed record carry a date, and every roster change refresh it.
"""

from __future__ import annotations

import os
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from internacia_builder.paths import project_root


def load_tier1(root: Path | None = None) -> list[str]:
    """Tier-1 intblock ids from ``data/watch/rosters.yaml``."""
    path = (root or project_root()) / "data" / "watch" / "rosters.yaml"
    if not path.exists():
        return []
    config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [str(entry["id"]) for entry in config.get("tier1") or []]


def _age_months(raw: Any, today: date) -> int | None:
    try:
        year, month, day = (int(part) for part in str(raw).split("-"))
        verified = date(year, month, day)
    except (TypeError, ValueError):
        return None
    return (today.year - verified.year) * 12 + (today.month - verified.month)


def _overdue(raw: Any, today: date, max_age_months: int) -> bool:
    """Older than the window, or not a valid date."""
    age = _age_months(raw, today)
    return age is None or age > max_age_months


def last_verified_kpi(
    records: list[dict[str, Any]],
    tier1: list[str],
    *,
    max_age_months: int,
    tier1_max_age_months: int,
    today: date | None = None,
) -> dict[str, Any]:
    """Counts and shares of never-verified and overdue records, overall and for tier 1."""
    today = today or date.today()
    tier1_set = set(tier1)

    def summary(rows: list[dict[str, Any]], max_age: int) -> dict[str, Any]:
        total = len(rows)
        missing = [r for r in rows if not r.get("last_verified")]
        stale = [r for r in rows if r.get("last_verified") and _overdue(r["last_verified"], today, max_age)]
        return {
            "total": total,
            "missing": len(missing),
            "missing_share": round(len(missing) / total, 4) if total else 0.0,
            "stale": len(stale),
            "stale_share": round(len(stale) / total, 4) if total else 0.0,
            "max_age_months": max_age,
        }

    tier1_rows = [r for r in records if str(r.get("id")) in tier1_set]
    result = {
        "as_of": today.isoformat(),
        "all": summary(records, max_age_months),
        "tier1": summary(tier1_rows, tier1_max_age_months),
    }
    result["tier1"]["missing_ids"] = sorted(str(r.get("id")) for r in tier1_rows if not r.get("last_verified"))
    result["tier1"]["stale_ids"] = sorted(
        str(r.get("id")) for r in tier1_rows if r.get("last_verified") and _overdue(r["last_verified"], today, tier1_max_age_months)
    )
    return result


def kpi_markdown(kpi: dict[str, Any]) -> str:
    """The KPI as a Markdown table (CI job summaries)."""
    lines = [
        f"### last_verified ({kpi['as_of']})",
        "",
        "| Scope | Records | Never verified | Overdue (window) |",
        "|---|---|---|---|",
    ]
    for label, key in (("All intblocks", "all"), ("Tier 1", "tier1")):
        s = kpi[key]
        lines.append(
            f"| {label} | {s['total']} | {s['missing']} ({s['missing_share']:.1%}) | "
            f"{s['stale']} ({s['stale_share']:.1%}, >{s['max_age_months']} months) |"
        )
    for label, key in (("Tier 1 never verified", "missing_ids"), ("Tier 1 overdue", "stale_ids")):
        if kpi["tier1"][key]:
            lines += ["", f"{label}: {', '.join(kpi['tier1'][key])}"]
    return "\n".join(lines) + "\n"


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None
    return result.stdout if result.returncode == 0 else None


def comparison_base(root: Path) -> str | None:
    """The ref changes are measured against: ``INTERNACIA_BASE_REF``, the pull request base
    (``GITHUB_BASE_REF``), else ``origin/main``; None if none exists."""
    candidates = [os.environ.get("INTERNACIA_BASE_REF")]
    if os.environ.get("GITHUB_BASE_REF"):
        candidates.append(f"origin/{os.environ['GITHUB_BASE_REF']}")
    candidates.append("origin/main")
    for ref in filter(None, candidates):
        if _git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") is not None:
            return ref
    return None


def changed_base_records(
    root: Path, base: str, source_dir: str = "data/intblocks"
) -> dict[str, dict[str, Any] | None]:
    """``{relative path: record at the merge base, or None if new}`` for YAML files under
    ``source_dir`` that differ from the merge base (committed, uncommitted or untracked).

    A file moved between category directories is compared with its record at the old path,
    so a move alone does not make a record look new.
    """
    merge_base = (_git(root, "merge-base", base, "HEAD") or "").strip() or base
    changed = (_git(root, "diff", "--name-only", merge_base, "--", source_dir) or "").splitlines()
    changed += (_git(root, "ls-files", "--others", "--exclude-standard", "--", source_dir) or "").splitlines()
    renamed_from: dict[str, str] = {}
    for line in (_git(root, "diff", "--name-status", "-M", merge_base, "--", source_dir) or "").splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].startswith("R"):
            renamed_from[parts[2]] = parts[1]
    records: dict[str, dict[str, Any] | None] = {}
    for path in sorted(set(changed) - set(renamed_from.values())):
        if path.endswith(".yaml"):
            text = _git(root, "show", f"{merge_base}:{renamed_from.get(path, path)}")
            records[path] = (yaml.safe_load(text) or {}) if text is not None else None
    return records


# Repository taxonomy fields: they classify the record under docs/intblock-inclusion-policy.md
# and data/blocktypes/blocktypes.yaml and say nothing about the roster, so reclassifying a
# record does not attest its members.
CLASSIFICATION_FIELDS = frozenset({"scope_category", "blocktype"})


def _enrichment_metadata_fields() -> frozenset[str]:
    """Intblock fields the metadata enricher fills from Wikidata, plus their provenance
    and the repository's classification fields.

    ``last_verified`` attests the roster, so changes limited to these fields do not need it.
    """
    from internacia_builder.enrichment_sources import load_policy  # noqa: PLC0415 (import cycle)

    return load_policy().fields("intblocks") | {"provenance"} | CLASSIFICATION_FIELDS


def _roster(includes: Any) -> Any:
    """``includes`` without the labels of ``type: country`` entries.

    The build copies those labels from the country records, so renaming one is not a
    roster change and does not need ``last_verified``.
    """
    if not isinstance(includes, list):
        return includes
    return [
        {k: v for k, v in inc.items() if k != "name"} if isinstance(inc, dict) and inc.get("type") == "country" else inc
        for inc in includes
    ]


def _deprecated_statuses() -> dict[str, set[str]]:
    """``{deprecated status: replacements}`` from data/schemas/includes_status.yaml."""
    from internacia_builder.paths import project_root  # noqa: PLC0415

    path = project_root() / "data" / "schemas" / "includes_status.yaml"
    statuses = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("statuses") or {}
    return {
        str(name): set((spec.get("deprecated") or {}).get("replacements") or [])
        for name, spec in statuses.items()
        if isinstance(spec, dict) and spec.get("deprecated")
    }


def _same_roster(before: Any, after: Any, deprecated: dict[str, set[str]]) -> bool:
    """Rosters are equal ignoring country labels and the recoding of a deprecated status to
    one of its listed replacements (a vocabulary migration, not a change of who is a member)."""
    before, after = _roster(before), _roster(after)
    if not (isinstance(before, list) and isinstance(after, list)) or len(before) != len(after):
        return before == after
    for old, new in zip(before, after, strict=True):
        if old == new:
            continue
        if not (isinstance(old, dict) and isinstance(new, dict)):
            return False
        if new.get("status") not in deprecated.get(str(old.get("status")), set()) or {**old, "status": new.get("status")} != new:
            return False
    return True


def _strip(record: dict[str, Any], names: frozenset[str]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in names and k != "includes"}


def check_changed_records(
    records: list[tuple[str, dict[str, Any]]],
    changed: dict[str, dict[str, Any] | None],
    base_ref: str,
    today: date | None = None,
) -> list[str]:
    """
    Errors for records that are new or changed since ``base_ref`` (``changed``, from
    ``changed_base_records``) and have no ``last_verified``, and for records whose
    ``includes`` changed while ``last_verified`` stayed the same. Changes limited to the
    enrichment metadata fields (data/schemas/enrichment_sources.yaml), to
    ``CLASSIFICATION_FIELDS``, to the labels of country includes, or to recoding a deprecated
    include status to one of its replacements are exempt.

    A roster change may keep the base's ``last_verified`` when that date is ``today``
    (default: the current date): the base was verified earlier the same day, so no later
    true date exists to set.
    """
    today_iso = (today or date.today()).isoformat()
    errors: list[str] = []
    metadata = _enrichment_metadata_fields()
    deprecated = _deprecated_statuses()
    for rel, record in records:
        if rel not in changed:
            continue
        before = changed[rel]
        if before == record or (
            before is not None
            and _strip(before, metadata) == _strip(record, metadata)
            and _same_roster(before.get("includes"), record.get("includes"), deprecated)
        ):
            continue
        if not record.get("last_verified"):
            state = "new" if before is None else "changed"
            errors.append(
                f"{rel}: {state} since {base_ref} but has no last_verified; set it to the date you "
                "checked the record against its provenance source"
            )
        elif (
            before is not None
            and not _same_roster(before.get("includes"), record.get("includes"), deprecated)
            and before.get("last_verified") == record.get("last_verified")
            and str(record.get("last_verified")) != today_iso
        ):
            errors.append(
                f"{rel}: includes changed since {base_ref} but last_verified is still "
                f"{record.get('last_verified')}; update it after verifying the roster"
            )
    return errors
