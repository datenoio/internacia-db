"""validate_countries / validate_intblocks runs on small directories outside data/.

Outside data/ the repository-state gates (identifier stability, changed records, tier-1
roster) are skipped, so these exercise the registry rules and the CLI plumbing.
"""

import json
import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml

from internacia_builder.validate import border_rules, country_rules, intblock_rules, registry
from internacia_builder.validate import countries as vc
from internacia_builder.validate import intblocks as vi

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def no_include_resolution(monkeypatch):
    """Skip resolving every intblock include against a two-country directory
    (covered by test_cross_dataset.py)."""
    monkeypatch.setattr(vc, "validate_intblock_refs", lambda *args: ([], []))


def _copy(src: Path, dest: Path, **changes) -> Path:
    record = yaml.safe_load(src.read_text(encoding="utf-8"))
    record.update(changes)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return dest


def test_countries_cli(tmp_path, no_include_resolution):
    countries = tmp_path / "countries"
    fr = _copy(ROOT / "data/countries/FR.yaml", countries / "FR.yaml", dvd_region=9)
    _copy(ROOT / "data/countries/DE.yaml", countries / "DE.yaml")
    (countries / "ZZ.yaml").write_text("code: [unterminated\n", encoding="utf-8")
    report = tmp_path / "report.json"

    assert vc.run_validation(countries_dir=countries, report=report) == 1

    summary = json.loads(report.read_text(encoding="utf-8"))
    assert summary["countries_validated"] == 2
    assert summary["error_count"] == len(summary["errors"])
    assert f"{fr}: dvd_region must be an integer in 1..6 when present" in summary["errors"]
    assert any(e.startswith(f"{countries / 'ZZ.yaml'}: YAML parse error") for e in summary["errors"])
    assert any(e.startswith("entity policy:") for e in summary["errors"])  # 2 of 249 ISO records
    assert summary["completeness"]["row_count"] == 2


def test_countries_cli_json_output(tmp_path, capsys, no_include_resolution):
    countries = tmp_path / "countries"
    _copy(ROOT / "data/countries/FR.yaml", countries / "FR.yaml", tld="FR")
    vc.run_validation(countries_dir=countries, json_output=True)
    result = json.loads(capsys.readouterr().out)
    assert result["dataset"] == "countries" and result["validated"] == 1
    assert any("tld 'FR'" in w["message"] for w in result["warnings"])


def test_countries_cli_empty_directory(tmp_path):
    (tmp_path / "countries").mkdir()
    assert vc.run_validation(countries_dir=tmp_path / "countries") == 1


def test_intblocks_cli(tmp_path):
    intblocks = tmp_path / "intblocks"
    nato_src = next(ROOT.glob("data/intblocks/*/NATO.yaml"))
    nato_record = yaml.safe_load(nato_src.read_text(encoding="utf-8"))
    nato = _copy(nato_src, intblocks / nato_src.parent.name / "NATO.yaml",
                 blocktype=[*nato_record["blocktype"], "spaceforce"], topics=[])
    eu_src = next(ROOT.glob("data/intblocks/*/EU.yaml"))
    _copy(eu_src, intblocks / eu_src.parent.name / "EU.yaml")
    (intblocks / "misc").mkdir()
    (intblocks / "misc" / "LIST.yaml").write_text("- not a mapping\n", encoding="utf-8")
    report = tmp_path / "report.json"

    assert vi.run_validation(intblocks_dir=intblocks, report=report) == 1

    summary = json.loads(report.read_text(encoding="utf-8"))
    assert summary["intblocks_validated"] == 2
    assert f"{nato}: unknown blocktype 'spaceforce'" in summary["errors"]
    assert f"{intblocks / 'misc' / 'LIST.yaml'}: expected a mapping at the document root" in summary["errors"]
    assert f"{nato}: missing topics" in summary["warnings"]
    assert "description_quality" in summary and summary["completeness"]["row_count"] == 2


@pytest.mark.parametrize("module", [vc, vi])
def test_validators_pass_on_the_repository_data(module):
    if not shutil.which("git"):
        pytest.skip("git is needed for the repository-state gates")
    assert module.run_validation() == 0


class _FarFuture(date):
    """A today() years ahead, when every recorded last_verified and provenance date is stale."""

    @classmethod
    def today(cls):
        return cls(2035, 1, 1)


@pytest.mark.parametrize("module", [vc, vi])
def test_fail_on_warning_reports_but_ignores_dated_warnings(module, monkeypatch, capsys):
    """CI runs the validators with --fail-on-warning. Freshness warnings appear as the calendar
    advances, so they must not fail it; every other warning must."""
    if not shutil.which("git"):
        pytest.skip("git is needed for the repository-state gates")
    for rules in (border_rules, country_rules, intblock_rules):
        monkeypatch.setattr(rules, "date", _FarFuture)

    assert module.run_validation(fail_on_warning=True, json_output=True) == 0
    warnings = [w["message"] for w in json.loads(capsys.readouterr().out)["warnings"]]
    assert any("stale (" in w or "not verified since" in w for w in warnings)

    messages = registry.validator_messages

    def with_planted_warning(dataset, ctx):
        errors, plain, dated = messages(dataset, ctx)
        return errors, [*plain, "planted warning"], dated

    monkeypatch.setattr(registry, "validator_messages", with_planted_warning)
    assert module.run_validation(fail_on_warning=True) == 1
    assert module.run_validation() == 0
