"""Regression tests for scope-category labeling heuristics."""

import importlib.util
from pathlib import Path

_PATH = Path(__file__).resolve().parents[1] / "scripts" / "oneoff" / "label_scope_category.py"
_spec = importlib.util.spec_from_file_location("label_scope_category", _PATH)
labels = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(labels)


def test_wbgroup_directory_is_reference_enumeration():
    path = Path("data/intblocks/wbgroup/WLD.yaml")
    record = {"id": "WLD", "blocktype": ["wbgroup"], "status": "formal"}

    assert labels.heuristic(path, record) == "reference_enumeration"


def test_wbgroup_blocktype_is_reference_even_outside_directory():
    path = Path("data/intblocks/economic/WLD.yaml")
    record = {"id": "WLD", "blocktype": ["economic", "wbgroup"], "status": "formal"}

    assert labels.heuristic(path, record) == "reference_enumeration"


def test_regular_political_record_is_igo():
    path = Path("data/intblocks/political/TEST.yaml")
    record = {"id": "TEST", "blocktype": ["political"], "status": "formal"}
    assert labels.heuristic(path, record) == "igo"


def test_deprecated_intorg_implies_no_category():
    path = Path("data/intblocks/fisheries/TEST.yaml")
    record = {"id": "TEST", "blocktype": ["fisheries", "intorg"], "status": "formal"}
    assert labels.heuristic(path, record) is None


def test_legacy_labeler_never_modifies_yaml(tmp_path, monkeypatch, capsys):
    political = tmp_path / "political"
    political.mkdir()
    new = political / "TEST.yaml"
    new.write_text("id: TEST\nblocktype:\n- political\nstatus: formal\n", encoding="utf-8")
    explicit = political / "UN.yaml"
    explicit.write_text("id: UN\nblocktype:\n- political\nstatus: formal\nscope_category: policy_forum\n", encoding="utf-8")
    before = (new.read_bytes(), explicit.read_bytes())
    monkeypatch.setattr(labels, "INTBLOCKS", tmp_path)

    labels.main()

    assert (new.read_bytes(), explicit.read_bytes()) == before
    output = capsys.readouterr().out
    assert "Suggestion only: TEST -> igo" in output
    assert "UN ->" not in output
