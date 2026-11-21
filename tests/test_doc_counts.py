"""Guard that consumer-facing docs match manifest row counts."""

import check_doc_counts


def test_consumer_docs_match_manifest_counts():
    errors = check_doc_counts.check()
    assert errors == [], errors


def test_load_counts_positive():
    counts = check_doc_counts.load_counts()
    assert counts["countries"] == 256
    assert counts["intblocks"] > 0
    assert counts["blocktypes"] > 0


def test_intblock_count_is_rounded_down_to_the_hundred():
    assert check_doc_counts.advertised("intblocks", 1304) == "1300+"
    assert check_doc_counts.advertised("intblocks", 1399) == "1300+"
    assert check_doc_counts.advertised("intblocks", 1400) == "1400+"
    assert check_doc_counts.advertised("countries", 256) == "256"


def _docs(root, text):
    for rel in check_doc_counts.REQUIRE:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_adding_records_within_the_hundred_needs_no_doc_edit(tmp_path):
    _docs(tmp_path, "**256** countries, **1300+** intblocks, **83** blocktypes")
    for intblocks in (1304, 1310, 1399):
        counts = {"countries": 256, "intblocks": intblocks, "blocktypes": 83}
        assert check_doc_counts.check(tmp_path, counts) == []


def test_crossing_a_hundred_flags_the_older_rounded_count(tmp_path):
    _docs(tmp_path, "**256** countries, **1300+** intblocks, **83** blocktypes")
    errors = check_doc_counts.check(tmp_path, {"countries": 256, "intblocks": 1400, "blocktypes": 83})
    assert any("missing current intblocks count 1400+" in e for e in errors)
    assert any("older rounded intblock count 1300+" in e for e in errors)
