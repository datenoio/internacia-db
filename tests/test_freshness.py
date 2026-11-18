"""last_verified KPI and the rule for new or changed records."""
from datetime import date

from internacia_builder.freshness import check_changed_records, kpi_markdown, last_verified_kpi, load_tier1

TODAY = date(2026, 10, 22)


def test_kpi_counts_missing_and_overdue():
    records = [
        {"id": "A", "last_verified": "2026-10-01"},
        {"id": "B", "last_verified": "2026-01-01"},
        {"id": "C"},
        {"id": "D", "last_verified": "not-a-date"},
        {"id": "E", "last_verified": "2025-01-01"},
    ]
    kpi = last_verified_kpi(records, ["A", "B", "C"], max_age_months=12, tier1_max_age_months=6, today=TODAY)
    assert (kpi["all"]["total"], kpi["all"]["missing"], kpi["all"]["stale"]) == (5, 1, 2)
    assert kpi["all"]["missing_share"] == 0.2
    assert kpi["tier1"]["stale_ids"] == ["B"] and kpi["tier1"]["missing_ids"] == ["C"]
    assert "| Tier 1 | 3 | 1 (33.3%) | 1 (33.3%, >6 months) |" in kpi_markdown(kpi)


def test_new_and_changed_records_need_last_verified():
    before = {"id": "X", "name": "Old", "includes": [{"id": "FR"}]}
    records = [
        ("data/intblocks/a/NEW.yaml", {"id": "NEW"}),
        ("data/intblocks/a/X.yaml", {**before, "name": "New"}),
        ("data/intblocks/a/SAME.yaml", {"id": "SAME"}),
    ]
    changed = {"data/intblocks/a/NEW.yaml": None, "data/intblocks/a/X.yaml": before}
    errors = check_changed_records(records, changed, "origin/main")
    assert len(errors) == 2
    assert errors[0].startswith("data/intblocks/a/NEW.yaml: new since origin/main")
    assert errors[1].startswith("data/intblocks/a/X.yaml: changed since origin/main")


def test_roster_change_must_refresh_last_verified():
    before = {"id": "X", "last_verified": "2026-01-01", "includes": [{"id": "FR"}]}
    after_same_date = {**before, "includes": [{"id": "FR"}, {"id": "DE"}]}
    errors = check_changed_records([("x.yaml", after_same_date)], {"x.yaml": before}, "origin/main")
    assert errors and "includes changed" in errors[0]
    refreshed = {**after_same_date, "last_verified": "2026-10-22"}
    assert check_changed_records([("x.yaml", refreshed)], {"x.yaml": before}, "origin/main") == []
    description_only = {**before, "description": "edited"}
    assert check_changed_records([("x.yaml", description_only)], {"x.yaml": before}, "origin/main") == []


def test_reclassifying_a_record_does_not_need_last_verified():
    before = {"id": "QSD", "status": "informal", "scope_category": "igo", "includes": [{"id": "IN"}]}
    reclassified = {**before, "scope_category": "policy_forum", "provenance": [{"field": "scope_category"}]}
    assert check_changed_records([("q.yaml", reclassified)], {"q.yaml": before}, "origin/main") == []
    renamed = {**reclassified, "name": "Quad"}
    assert check_changed_records([("q.yaml", renamed)], {"q.yaml": before}, "origin/main")


def test_tier1_list_is_loaded():
    tier1 = load_tier1()
    assert {"UN", "EU", "NATO", "AFUNION", "G-20"} <= set(tier1)
    assert len(tier1) == len(set(tier1))
