"""Tests for scripts/generate_schema_migration.py"""

from __future__ import annotations

import json
from pathlib import Path

import generate_schema_migration as gsm


def test_diff_props_detects_added_removed_and_type_change(tmp_path: Path):
    prev = {
        "code": {"type": "string"},
        "name": {"type": "string"},
        "old_field": {"type": "integer"},
    }
    curr = {
        "code": {"type": "string"},
        "name": {"type": "integer"},
        "new_field": {"type": "string"},
    }
    d = gsm.diff_props(prev, curr)
    assert d["added"] == ["new_field"]
    assert d["removed"] == ["old_field"]
    assert d["type_changed"] == [{"field": "name", "from": "string", "to": "integer"}]


def test_build_migration_writes_versioned_file(tmp_path: Path):
    prev_dir = tmp_path / "prev"
    curr_dir = tmp_path / "curr"
    prev_dir.mkdir()
    curr_dir.mkdir()
    (prev_dir / "countries.schema.json").write_text(
        json.dumps({"properties": {"code": {"type": "string"}}}), encoding="utf-8"
    )
    (curr_dir / "countries.schema.json").write_text(
        json.dumps({"properties": {"code": {"type": "string"}, "ioc_code": {"type": "string"}}}),
        encoding="utf-8",
    )
    (curr_dir / "intblocks.schema.json").write_text(
        json.dumps({"properties": {"id": {"type": "string"}}}), encoding="utf-8"
    )
    migration = gsm.build_migration(prev_dir, curr_dir, "1.11.0")
    assert migration["version"] == "1.11.0"
    assert migration["schema_changed"] is True
    assert "ioc_code" in migration["datasets"]["countries"]["added"]
