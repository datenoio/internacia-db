"""Reviewed six-record non-formal scope cohort: exact identity and evidence."""

from pathlib import Path

import pytest
import yaml

from internacia_builder.paths import project_root
from internacia_builder.validate.intblock_rules import check_intblock_scope_category

ROOT = Path(project_root())
MANIFEST = ROOT / "data/schemas/scope_category_nonformal_30.yaml"
EXPECTED = {
    "ARABW": ("reference_enumeration", "informal", 22),
    "BALTICSTATES": ("reference_enumeration", "informal", 3),
    "HISPAM": ("reference_enumeration", "informal", 18),
    "MIDAMERICA": ("reference_enumeration", "informal", 36),
    "SLAVISPHERE": ("reference_enumeration", "informal", 13),
    "CMA": ("policy_forum", "de-facto", 4),
}


@pytest.mark.parametrize("record_id", sorted(EXPECTED))
def test_approved_nonformal_category_and_source_provenance(record_id: str) -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    entry = manifest["records"][record_id]
    record = yaml.safe_load((ROOT / entry["path"]).read_text(encoding="utf-8"))
    category, status, roster_count = EXPECTED[record_id]

    assert entry["review_state"] == "source_reviewed"
    assert entry["category"] == record["scope_category"] == category
    assert record["status"] == status
    assert record["id"] == record_id
    assert len(record["includes"]) == record["membership_count"] == roster_count
    assert check_intblock_scope_category(record) == []
    provenance = [p for p in record["provenance"] if p.get("field") == "scope_category"]
    assert len(provenance) == 1
    assert {k: provenance[0][k] for k in ("source", "url", "retrieved_at")} == entry["evidence"]
    assert provenance[0]["url"].startswith("https://")
