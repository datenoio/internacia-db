"""Regression contract for reviewed model-gap scope taxonomy records."""

from pathlib import Path

import pytest
import yaml

from internacia_builder.paths import project_root
from internacia_builder.validate.intblock_rules import (
    check_intblock_membership_consistency,
    check_intblock_scope_category,
)

BODY_IDS = (
    "APFIC", "CECAF", "CIFAA", "CODEX", "COPESCAALC", "EIFAAC",
    "SWIOFC", "WECAFC", "ADF", "AF", "RDR", "GCCPO",
)
NGO_IDS = ("MSF", "CANTO", "ACIL")
NO_COUNTRY_ROSTER = ("ADF", "AF", "GCCPO", "MSF", "CANTO", "ACIL")


def _record(record_id: str) -> dict:
    paths = list((Path(project_root()) / "data/intblocks").glob(f"*/{record_id}.yaml"))
    assert len(paths) == 1
    return yaml.safe_load(paths[0].read_text(encoding="utf-8"))


@pytest.mark.parametrize("record_id", BODY_IDS + NGO_IDS)
def test_model_gap_category_and_provenance(record_id: str):
    record = _record(record_id)
    expected = "intergovernmental_body" if record_id in BODY_IDS else "non_state_organization"
    assert record["scope_category"] == expected
    assert check_intblock_scope_category(record) == []
    evidence = [p for p in record.get("provenance", []) if p.get("field") == "scope_category"]
    assert len(evidence) == 1
    assert evidence[0]["url"].startswith("https://")


@pytest.mark.parametrize("record_id", NO_COUNTRY_ROSTER)
def test_no_false_country_membership(record_id: str):
    record = _record(record_id)
    assert "includes" not in record
    assert "membership_count" not in record
    assert record["membership_applicability"] == "not_applicable"
    assert check_intblock_membership_consistency(record) == []
    assert any(p.get("field") == "membership_applicability" for p in record["provenance"])
    assert all(p.get("field") in record for p in record["provenance"])


def test_rdr_only_retains_actual_state_participants():
    record = _record("RDR")
    assert [item["id"] for item in record["includes"]] == ["DE", "AT", "CH", "LI"]
    assert {item["status"] for item in record["includes"]} == {"participant"}
    assert "membership_count" not in record
    assert check_intblock_membership_consistency(record) == []
