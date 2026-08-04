"""Tests for partof hierarchy validation."""

from __future__ import annotations

from internacia_builder.validate import cross_rules


def test_org_partof_treaty_like_fails():
    records = [
        {"id": "EU", "blocktype": ["economic", "political"], "partof": ["EEA"]},
        {"id": "EEA", "blocktype": ["economic", "agreement"], "legal_status": "treaty"},
    ]
    paths = ["economic/EU.yaml", "economic/EEA.yaml"]
    issues = cross_rules.check_partof_hierarchy(records, paths)
    assert len(issues) == 1
    assert issues[0]["issue_type"] == "INVALID_PARTOF_TARGET"
    assert issues[0]["current_value"] == "EEA"
    assert issues[0]["record_id"] == "EU"


def test_org_partof_org_passes():
    records = [
        {"id": "ILO", "blocktype": ["unagency"], "partof": ["UN"]},
        {"id": "UN", "blocktype": ["intorg", "political"]},
    ]
    assert cross_rules.check_partof_hierarchy(records, ["a.yaml", "b.yaml"]) == []


def test_treaty_nested_under_treaty_passes():
    records = [
        {
            "id": "PARISAGREEMENT",
            "blocktype": ["environment", "agreement"],
            "legal_status": "treaty",
            "partof": ["UNFCCC"],
        },
        {"id": "UNFCCC", "blocktype": ["environment", "agreement"], "legal_status": "treaty"},
    ]
    assert cross_rules.check_partof_hierarchy(records, ["a.yaml", "b.yaml"]) == []


def test_fund_partof_convention_passes():
    records = [
        {"id": "GCF", "blocktype": ["fund"], "partof": ["UNFCCC"]},
        {"id": "UNFCCC", "blocktype": ["environment", "agreement"]},
    ]
    assert cross_rules.check_partof_hierarchy(records, ["a.yaml", "b.yaml"]) == []
