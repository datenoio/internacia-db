"""Roster watch: comparison, Wikidata parsing and issue sync (network mocked)."""
from unittest.mock import MagicMock

from internacia_builder.roster_watch import ISSUE_LABEL, Drift, IssueSync, compare, issue_body, wikidata_members

RECORD = {
    "id": "XO",
    "name": "Example Org",
    "wikidata_id": "Q1",
    "includes": [
        {"id": "FR", "type": "country", "status": "member"},
        {"id": "DE", "type": "country", "status": "founding_member"},
        {"id": "GB", "type": "country", "status": "member", "left": "2020-01-31"},
        {"id": "CA", "type": "country", "status": "observer"},
        {"id": "XO2", "type": "organization", "status": "member"},
    ],
}


def test_compare_uses_current_full_members():
    drift = compare(RECORD, {"FR", "IT"})
    assert drift.only_internacia == ["DE"] and drift.only_wikidata == ["IT"]
    assert drift.overlap == 0.5 and not drift.low_overlap
    assert not compare(RECORD, {"FR", "DE"}).has_drift


def test_wikidata_parsing_maps_constituent_countries():
    response = MagicMock(status_code=200)
    response.json.return_value = {"results": {"bindings": [
        {"country": {"value": "http://www.wikidata.org/entity/Q142"}, "iso": {"value": "fr"}},
        {"country": {"value": "http://www.wikidata.org/entity/Q55"}},
        {"country": {"value": "http://www.wikidata.org/entity/Q756617"}},
        {"country": {"value": "http://www.wikidata.org/entity/Q999"}},
    ]}}
    session = MagicMock()
    session.get.return_value = response
    assert wikidata_members("Q1", session) == {"FR", "NL", "DK"}
    assert "wd:Q1" in session.get.call_args.kwargs["params"]["query"]


def _sync(open_issues):
    session = MagicMock()
    session.get.return_value.json.return_value = open_issues
    return IssueSync("datenoio/internacia-db", "token", session), session


def test_opens_updates_skips_and_closes_issues():
    changed = Drift("A", "Org A", "Q1", only_internacia=["FR"])
    same = Drift("B", "Org B", "Q2", only_wikidata=["DE"])
    resolved = Drift("C", "Org C", "Q3")
    new = Drift("D", "Org D", "Q4", only_wikidata=["IT"])
    stale_a = Drift("A", "Org A", "Q1", only_internacia=["ES"])
    issues = [
        {"number": 1, "state": "open", "body": issue_body(stale_a, "2026-10-01")},
        {"number": 2, "state": "open", "body": issue_body(same, "2026-10-01")},
        {"number": 3, "state": "open", "body": issue_body(Drift("C", "Org C", "Q3", only_wikidata=["PT"]), "2026-10-01")},
        # Closed as completed by an earlier run: does not stop D from being reported.
        {"number": 4, "state": "closed", "state_reason": "completed", "body": issue_body(new, "2026-09-01")},
    ]
    sync, session = _sync(issues)
    actions = sync.sync([changed, same, resolved, new, Drift("E", "Org E", "", error="x")], "2026-10-22")
    assert actions == {"opened": ["D"], "updated": ["A"], "closed": ["C"], "dismissed": []}
    assert session.get.call_args.kwargs["params"]["state"] == "all"
    created = next(c.kwargs["json"] for c in session.post.call_args_list if "labels" in c.kwargs["json"])
    assert any(c.args[0].endswith("/labels") for c in session.post.call_args_list)
    assert created["labels"] == [ISSUE_LABEL] and created["title"] == "Roster drift: D (Org D)"
    assert "`IT`" in created["body"]


def test_drift_closed_as_not_planned_is_not_reopened_until_it_changes():
    reviewed = Drift("UN", "United Nations", "Q1065", only_internacia=["DK"])
    changed = Drift("AU", "African Union", "Q7159", only_internacia=["EH", "ML"])
    issues = [
        {"number": 83, "state": "closed", "state_reason": "not_planned", "body": issue_body(reviewed, "2026-10-26")},
        {"number": 85, "state": "closed", "state_reason": "not_planned",
         "body": issue_body(Drift("AU", "African Union", "Q7159", only_internacia=["EH"]), "2026-10-26")},
    ]
    sync, session = _sync(issues)
    actions = sync.sync([reviewed, changed], "2026-11-23")
    assert actions == {"opened": ["AU"], "updated": [], "closed": [], "dismissed": ["UN"]}
    assert not session.patch.called


def test_low_overlap_note():
    drift = compare(RECORD, set())
    assert drift.low_overlap
    assert "Low overlap (0%" in issue_body(drift, "2026-10-22")
