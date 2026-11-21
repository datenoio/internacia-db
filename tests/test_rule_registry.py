"""The shared rule registry: one rule list for the validators and analyze-quality."""

import json
import re
import shutil
from pathlib import Path

import yaml

from internacia_builder import build
from internacia_builder.quality_report import ISSUE_PRIORITY_MAP, RULE_DESCRIPTIONS
from internacia_builder.validate import registry
from internacia_builder.yaml_io import safe_load

ROOT = Path(__file__).resolve().parents[1]
BLOCKING = {"CRITICAL", "IMPORTANT"}
KNOWN_TYPES = {t for types in ISSUE_PRIORITY_MAP.values() for t in types}


def test_every_emitted_issue_type_is_classified_and_described():
    emitted = set()
    for path in (ROOT / "internacia_builder" / "validate").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        emitted |= set(re.findall(r'"issue_type":\s*"([A-Z_]+)"', text))
        emitted |= set(re.findall(r'issue_type = "([A-Z_]+)"', text))
    assert emitted - KNOWN_TYPES == set()
    assert emitted - set(RULE_DESCRIPTIONS) == set()


def test_rules_are_unique_and_well_formed():
    for dataset, rules in registry.RULES.items():
        names = [rule.name for rule in rules]
        assert len(names) == len(set(names)), dataset
        for rule in rules:
            assert rule.dataset == dataset
            assert rule.severity in {"error", "warning", None}


def test_dated_rules_are_the_freshness_warnings():
    """Only rules that age a recorded date are dated: --fail-on-warning skips exactly these."""
    dated = {(rule.dataset, rule.name) for rules in registry.RULES.values() for rule in rules if rule.dated}
    assert dated == {
        (registry.COUNTRIES, "border status freshness"),
        (registry.COUNTRIES, "provenance freshness"),
        (registry.INTBLOCKS, "last verified"),
        (registry.INTBLOCKS, "provenance freshness"),
    }
    assert all(rule.severity == "warning" for rules in registry.RULES.values() for rule in rules if rule.dated)


def _project(tmp_path: Path) -> Path:
    """A small project: real schemas and config, four records with planted defects."""
    for rel in ("data/schemas", "data/blocktypes", "data/watch"):
        shutil.copytree(ROOT / rel, tmp_path / rel)
    for rel in ("data/intblocks_aliases.yaml", "data/attribute_intblock_migrations.yaml"):
        if (ROOT / rel).exists():
            shutil.copy(ROOT / rel, tmp_path / rel)

    def copy(rel: str, edit) -> None:
        record = safe_load((ROOT / rel).read_text(encoding="utf-8"))
        edit(record)
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")

    copy("data/countries/FR.yaml", lambda r: r.update(dvd_region=9, tld="FR"))
    copy("data/countries/DE.yaml", lambda r: r.update(currencies=[{"code": "eur", "name": "Euro"}]))
    nato = next(ROOT.glob("data/intblocks/*/NATO.yaml")).relative_to(ROOT)
    eu = next(ROOT.glob("data/intblocks/*/EU.yaml")).relative_to(ROOT)
    copy(str(nato), lambda r: r.update(blocktype=[*r["blocktype"], "spaceforce"], topics=[]))
    copy(str(eu), lambda r: r.pop("wikidata_id"))
    return tmp_path


def test_validators_and_analyze_quality_see_the_same_findings(tmp_path, monkeypatch):
    root = _project(tmp_path)
    ctx = registry.load_context(root)
    findings = list(registry.run_rules([*registry.COUNTRY_RULES, *registry.INTBLOCK_RULES], ctx))
    types = {issue["issue_type"] for _, issue in findings}
    assert {"INVALID_ATTRIBUTE_FIELD", "INVALID_TLD", "INVALID_CURRENCY_CODE", "UNKNOWN_BLOCKTYPE",
            "MISSING_TOPICS", "MISSING_WIKIDATA_ID"} <= types

    for rule, issue in findings:
        priority = build.get_priority_level(issue["issue_type"], issue)
        if rule.severity == "error":
            assert priority in BLOCKING, (rule.name, issue["issue_type"], priority)

    errors, warnings, _ = registry.validator_messages(registry.COUNTRIES, ctx)
    assert "data/countries/FR.yaml: dvd_region must be an integer in 1..6 when present" in errors
    assert any("tld 'FR'" in w for w in warnings)
    errors, warnings, _ = registry.validator_messages(registry.INTBLOCKS, ctx)
    assert any(e.endswith("unknown blocktype 'spaceforce'") for e in errors)
    assert any("wikidata_id" in e and "EU.yaml" in e for e in errors)
    assert any(w.endswith("NATO.yaml: missing topics") for w in warnings)

    monkeypatch.setattr(build, "get_project_root", lambda: root)
    build.analyze_quality(output=tmp_path / "quality", check_http=False, check_wikidata=False)
    reported = [json.loads(line) for line in (tmp_path / "quality" / "full_report.jsonl").open()]
    validator_rules = [(rule, issue) for rule, issue in findings if rule.severity is not None]
    for _, issue in validator_rules:
        assert any(
            r["issue_type"] == issue["issue_type"] and r["file_path"] == issue["file_path"]
            for r in reported
        ), issue
    by_type = {r["issue_type"]: r["priority"] for r in reported}
    assert by_type["INVALID_ATTRIBUTE_FIELD"] == "IMPORTANT"
    assert by_type["MISSING_WIKIDATA_ID"] == "IMPORTANT"


def test_parse_errors_are_reported_once(tmp_path):
    root = _project(tmp_path)
    (root / "data/countries/XX.yaml").write_text("code: [unterminated\n", encoding="utf-8")
    (root / "data/countries/YY.yaml").write_text("- a list\n", encoding="utf-8")
    ctx = registry.load_context(root)
    assert ctx.countries.file_count == 4
    assert [rel for rel, _ in ctx.countries.errors] == ["data/countries/XX.yaml", "data/countries/YY.yaml"]
    assert "YAML parse error" in ctx.countries.errors[0][1]
    assert ctx.countries.errors[1][1] == "expected a mapping at the document root"
