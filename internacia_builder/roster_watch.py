"""Roster watch: compare tier-1 memberships with Wikidata and report drift as issues.

Rosters are the core value of the dataset and need a human to verify them, so the watch
never edits data. For every tier-1 organization in ``data/watch/rosters.yaml`` it compares
the current country members in ``includes`` with the countries Wikidata lists as current
members (``member of`` P463 on the country, or ``has part(s)`` P527 on the organization,
without an end time P582 and not deprecated), and keeps one GitHub issue per organization
with the differences.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

from internacia_builder.freshness import load_tier1
from internacia_builder.paths import project_root
from internacia_builder.yaml_io import safe_load

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "internacia-db-roster-watch/1.0 (https://github.com/datenoio/internacia-db)"
CURRENT_STATUSES = {"member", "founding_member"}
ISSUE_LABEL = "roster-drift"
# Items that carry memberships in Wikidata without an ISO 3166-1 code of their own. For the
# Netherlands the code is on the kingdom (Q29999) while some memberships sit on the
# constituent country Q55. For Denmark it is the other way round: the code is on Q35 while
# UN and OECD membership sit on the Kingdom of Denmark (Q756617).
ISO_OVERRIDES = {"Q55": "NL", "Q756617": "DK"}
MARKER = re.compile(r"<!-- roster-watch:(\S+) (\w+) -->")
# Below this share of our members confirmed by Wikidata, the wikidata_id or Wikidata's
# modelling is the likelier cause than the roster.
LOW_OVERLAP = 0.5


@dataclass
class Drift:
    """Differences between internacia-db and Wikidata for one organization."""

    id: str
    name: str
    wikidata_id: str
    only_internacia: list[str] = field(default_factory=list)
    only_wikidata: list[str] = field(default_factory=list)
    overlap: float = 1.0
    error: str | None = None

    @property
    def low_overlap(self) -> bool:
        return self.overlap < LOW_OVERLAP

    @property
    def fingerprint(self) -> str:
        """Changes only when the differences change, so unchanged drift is not re-posted."""
        text = f"{self.wikidata_id}|{','.join(self.only_internacia)}|{','.join(self.only_wikidata)}"
        return hashlib.sha256(text.encode()).hexdigest()[:12]

    @property
    def has_drift(self) -> bool:
        return bool(self.only_internacia or self.only_wikidata)


def current_members(record: dict[str, Any]) -> set[str]:
    """Alpha-2 codes of current full members (member/founding_member, no ``left`` date)."""
    return {
        str(m["id"])
        for m in record.get("includes") or []
        if m.get("type") == "country" and m.get("status") in CURRENT_STATUSES and not m.get("left")
    }


def sparql_query(wikidata_id: str) -> str:
    return f"""
SELECT DISTINCT ?country ?iso WHERE {{
  {{ ?country p:P463 ?st . ?st ps:P463 wd:{wikidata_id} . }}
  UNION
  {{ wd:{wikidata_id} p:P527 ?st . ?st ps:P527 ?country . }}
  ?st wikibase:rank ?rank .
  FILTER(?rank != wikibase:DeprecatedRank)
  FILTER NOT EXISTS {{ ?st pq:P582 ?end }}
  OPTIONAL {{ ?country wdt:P297 ?iso . }}
}}"""


def wikidata_members(wikidata_id: str, session: requests.Session, retries: int = 3) -> set[str]:
    """Alpha-2 codes Wikidata lists as current members of ``wikidata_id``."""
    for attempt in range(retries):
        response = session.get(
            SPARQL_URL,
            params={"query": sparql_query(wikidata_id), "format": "json"},
            headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
            timeout=60,
        )
        if response.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
            time.sleep(5 * (attempt + 1))
            continue
        response.raise_for_status()
        members = set()
        for row in response.json()["results"]["bindings"]:
            qid = row["country"]["value"].rsplit("/", 1)[-1]
            iso = row["iso"]["value"].upper() if "iso" in row else ISO_OVERRIDES.get(qid)
            if iso:
                members.add(iso)
        return members
    raise RuntimeError("unreachable")


def compare(record: dict[str, Any], wikidata: set[str]) -> Drift:
    ours = current_members(record)
    return Drift(
        id=str(record["id"]),
        name=str(record.get("name") or record["id"]),
        wikidata_id=str(record.get("wikidata_id") or ""),
        only_internacia=sorted(ours - wikidata),
        only_wikidata=sorted(wikidata - ours),
        overlap=round(len(ours & wikidata) / len(ours), 3) if ours else 1.0,
    )


def load_records(root: Path, ids: list[str]) -> dict[str, dict[str, Any]]:
    files = {path.stem: path for path in (root / "data" / "intblocks").rglob("*.yaml")}
    return {i: safe_load(files[i].read_text(encoding="utf-8")) for i in ids if i in files}


def run(
    ids: list[str] | None = None,
    root: Path | None = None,
    session: requests.Session | None = None,
    pause: float = 1.0,
) -> list[Drift]:
    """Compare each tier-1 organization (or ``ids``) with Wikidata."""
    root = root or project_root()
    session = session or requests.Session()
    results = []
    for block_id, record in load_records(root, ids or load_tier1(root)).items():
        wikidata_id = record.get("wikidata_id")
        if not wikidata_id:
            results.append(Drift(block_id, str(record.get("name")), "", error="no wikidata_id"))
            continue
        try:
            results.append(compare(record, wikidata_members(str(wikidata_id), session)))
        except (requests.RequestException, KeyError, ValueError) as e:
            results.append(Drift(block_id, str(record.get("name")), str(wikidata_id), error=str(e)))
        time.sleep(pause)
    return results


def issue_title(drift: Drift) -> str:
    return f"Roster drift: {drift.id} ({drift.name})"


def issue_body(drift: Drift, as_of: str) -> str:
    def codes(values: list[str]) -> str:
        return ", ".join(f"`{v}`" for v in values) or "none"

    return (
        f"The weekly roster watch ({as_of}) found differences between the current members of "
        f"**{drift.name}** (`{drift.id}`) and Wikidata "
        f"[{drift.wikidata_id}](https://www.wikidata.org/wiki/{drift.wikidata_id}).\n\n"
        f"| | Countries |\n|---|---|\n"
        f"| In internacia-db only | {codes(drift.only_internacia)} |\n"
        f"| In Wikidata only | {codes(drift.only_wikidata)} |\n\n"
        + (
            f"**Low overlap ({drift.overlap:.0%} of our members are confirmed by Wikidata).** Check "
            f"that `wikidata_id` {drift.wikidata_id} is this organization and how Wikidata models "
            "its membership before changing the roster.\n\n"
            if drift.low_overlap
            else ""
        )
        + "Wikidata can be wrong or late. Check the organization's official member list (the "
        "source in the record's `provenance`), then either fix `includes` (and `last_verified`) "
        "or, if internacia-db is right, close this issue as *not planned* with a comment naming "
        "the source. The watch does not reopen it while the differences stay the same. This "
        "issue is updated by `.github/workflows/roster-watch.yml` and closed automatically when "
        "the rosters agree.\n\n"
        f"<!-- roster-watch:{drift.id} {drift.fingerprint} -->"
    )


class IssueSync:
    """Create, update and close one issue per organization through the GitHub REST API."""

    def __init__(self, repo: str, token: str, session: requests.Session | None = None):
        self.api = f"https://api.github.com/repos/{repo}"
        self.session = session or requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        )

    def _ensure_label(self) -> None:
        response = self.session.post(
            f"{self.api}/labels",
            json={"name": ISSUE_LABEL, "color": "d93f0b", "description": "Roster differs from external sources"},
        )
        if response.status_code not in (201, 422):  # 422: the label already exists
            response.raise_for_status()

    def _issues(self) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
        """Open issues by organization, and fingerprints of issues a person closed as not planned."""
        listed: list[dict[str, Any]] = []
        for page in range(1, 51):
            response = self.session.get(
                f"{self.api}/issues",
                params={"labels": ISSUE_LABEL, "state": "all", "per_page": 100, "page": page},
            )
            response.raise_for_status()
            batch = response.json()
            listed.extend(batch)
            if len(batch) < 100:
                break
        issues: dict[str, dict[str, Any]] = {}
        dismissed: dict[str, set[str]] = {}
        for issue in listed:
            match = MARKER.search(issue.get("body") or "")
            if not match:
                continue
            if issue.get("state") == "open":
                issues[match.group(1)] = {**issue, "fingerprint": match.group(2)}
            elif issue.get("state_reason") == "not_planned":
                dismissed.setdefault(match.group(1), set()).add(match.group(2))
        return issues, dismissed

    def sync(self, drifts: list[Drift], as_of: str) -> dict[str, list[str]]:
        """Open or update issues for drift, close issues whose rosters now agree.

        Drift that a person already reviewed and closed as not planned (internacia-db is right)
        is not reported again until the differences change.
        """
        existing, dismissed = self._issues()
        actions: dict[str, list[str]] = {"opened": [], "updated": [], "closed": [], "dismissed": []}
        for drift in drifts:
            if drift.error:
                continue
            issue = existing.get(drift.id)
            if drift.has_drift:
                payload = {"title": issue_title(drift), "body": issue_body(drift, as_of)}
                if issue is None and drift.fingerprint in dismissed.get(drift.id, set()):
                    actions["dismissed"].append(drift.id)
                    continue
                if issue is None:
                    if not actions["opened"]:
                        self._ensure_label()
                    response = self.session.post(f"{self.api}/issues", json={**payload, "labels": [ISSUE_LABEL]})
                    actions["opened"].append(drift.id)
                elif issue["fingerprint"] != drift.fingerprint:
                    response = self.session.patch(f"{self.api}/issues/{issue['number']}", json=payload)
                    actions["updated"].append(drift.id)
                else:
                    continue
                response.raise_for_status()
            elif issue is not None:
                comment = f"The rosters agree as of {as_of}; closing."
                self.session.post(f"{self.api}/issues/{issue['number']}/comments", json={"body": comment}).raise_for_status()
                self.session.patch(
                    f"{self.api}/issues/{issue['number']}", json={"state": "closed", "state_reason": "completed"}
                ).raise_for_status()
                actions["closed"].append(drift.id)
        return actions


def report_markdown(drifts: list[Drift], as_of: str) -> str:
    lines = [f"### Roster watch ({as_of})", "", "| Organization | Only internacia-db | Only Wikidata |", "|---|---|---|"]
    for d in drifts:
        if d.error:
            lines.append(f"| {d.id} | error: {d.error} | |")
        elif d.has_drift:
            note = f" (low overlap {d.overlap:.0%}: check wikidata_id {d.wikidata_id})" if d.low_overlap else ""
            ours = ", ".join(d.only_internacia) or "–"
            theirs = ", ".join(d.only_wikidata) or "–"
            lines.append(f"| {d.id}{note} | {ours} | {theirs} |")
    agree = [d.id for d in drifts if not d.error and not d.has_drift]
    lines += ["", f"Agree: {', '.join(agree) or 'none'}"]
    return "\n".join(lines) + "\n"
