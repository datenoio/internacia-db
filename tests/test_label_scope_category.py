"""Regression tests for scope-category labeling heuristics."""

from pathlib import Path

import label_scope_category as labels


def test_wbgroup_directory_is_reference_enumeration():
    path = Path("data/intblocks/wbgroup/WLD.yaml")
    record = {"id": "WLD", "blocktype": ["wbgroup"], "status": "formal"}

    assert labels.heuristic(path, record) == "reference_enumeration"


def test_wbgroup_blocktype_is_reference_even_outside_directory():
    path = Path("data/intblocks/economic/WLD.yaml")
    record = {"id": "WLD", "blocktype": ["economic", "wbgroup"], "status": "formal"}

    assert labels.heuristic(path, record) == "reference_enumeration"


def test_regular_intorg_remains_igo():
    path = Path("data/intblocks/intorg/TEST.yaml")
    record = {"id": "TEST", "blocktype": ["intorg"], "status": "formal"}
    assert labels.heuristic(path, record) == "igo"


def test_legacy_labeler_never_modifies_yaml(tmp_path, monkeypatch, capsys):
    intorg = tmp_path / "intorg"
    intorg.mkdir()
    new = intorg / "TEST.yaml"
    new.write_text("id: TEST\nblocktype:\n- intorg\nstatus: formal\n", encoding="utf-8")
    explicit = intorg / "UN.yaml"
    explicit.write_text("id: UN\nblocktype:\n- intorg\nstatus: formal\nscope_category: policy_forum\n", encoding="utf-8")
    before = (new.read_bytes(), explicit.read_bytes())
    monkeypatch.setattr(labels, "INTBLOCKS", tmp_path)

    labels.main()

    assert (new.read_bytes(), explicit.read_bytes()) == before
    output = capsys.readouterr().out
    assert "Suggestion only: TEST -> igo" in output
    assert "UN ->" not in output
