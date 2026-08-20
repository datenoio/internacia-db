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
