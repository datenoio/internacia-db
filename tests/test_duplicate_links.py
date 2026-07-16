"""Unit tests for builder.check_duplicate_links de-noising."""

import builder


def _issues(records):
    rel = [f"data/intblocks/x/{r.get('id', r.get('code'))}.yaml" for r in records]
    return builder.check_duplicate_links(rel, records)


def test_reports_unrelated_shared_website():
    records = [
        {"id": "A", "links": [{"url": "https://shared.org/", "type": "website"}]},
        {"id": "B", "links": [{"url": "http://www.shared.org", "type": "website"}]},
    ]
    issues = _issues(records)
    assert len(issues) == 2
    assert all(i["issue_type"] == "DUPLICATE_LINK" for i in issues)
    assert issues[0]["current_value"] == "shared.org"


def test_ignores_reference_catalog_hosts():
    records = [
        {"id": "A", "links": [{"url": "https://en.wikipedia.org/wiki/X", "type": "wikipedia"}]},
        {"id": "B", "links": [{"url": "https://en.wikipedia.org/wiki/X", "type": "wikipedia"}]},
    ]
    assert _issues(records) == []


def test_suppresses_related_records():
    records = [
        {"id": "PARENT", "links": [{"url": "https://org.int", "type": "website"}], "suborganizations": [{"id": "CHILD"}]},
        {"id": "CHILD", "links": [{"url": "https://org.int", "type": "website"}], "partof": "PARENT"},
    ]
    assert _issues(records) == []


def test_ignores_non_website_link_types():
    records = [
        {"id": "A", "links": [{"url": "https://data.org", "type": "wikidata"}]},
        {"id": "B", "links": [{"url": "https://data.org", "type": "wikidata"}]},
    ]
    assert _issues(records) == []
