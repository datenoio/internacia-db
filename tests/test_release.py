"""Release train: level, next version, data diff and the version bump."""

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest
import yaml

from internacia_builder import release
from internacia_builder.contract import build_contract
from internacia_builder.yaml_io import safe_load

ROOT = Path(__file__).resolve().parents[1]


def test_next_version():
    assert release.next_version("v3.0.0", "patch") == "3.0.1"
    assert release.next_version("3.0.4", "minor") == "3.1.0"
    assert release.next_version("v3.1.2", "major") == "4.0.0"


def _snapshot(countries, intblocks):
    return release.Snapshot(
        countries={c: {"code": c} for c in countries},
        intblocks={i: dict(record, id=i) for i, record in intblocks.items()},
    )


def test_data_diff_records_and_memberships():
    before = _snapshot(["FR", "DE", "XX"], {
        "EU": {"includes": [{"id": "FR", "type": "country", "status": "member"},
                            {"id": "DE", "type": "country", "status": "member"}]},
    })
    after = _snapshot(["FR", "DE", "YY"], {
        "EU": {"includes": [{"id": "FR", "type": "country", "status": "member"},
                            {"id": "DE", "type": "country", "status": "member", "left": "2030-01-01"},
                            {"id": "YY", "type": "country", "status": "candidate"}]},
        "NEW": {"includes": []},
    })
    diff = release.data_diff(before, after)
    assert diff["countries"] == {"count": [3, 3], "added": ["YY"], "removed": ["XX"], "changed": []}
    assert diff["intblocks"]["added"] == ["NEW"] and diff["intblocks"]["changed"] == ["EU"]
    memberships = diff["memberships"]
    assert memberships["count"] == [2, 3]
    assert memberships["added"] == [{"intblock": "EU", "country": "YY", "status": "candidate"}]
    assert memberships["changed"] == [{"intblock": "EU", "country": "DE", "fields": {"left": [None, "2030-01-01"]}}]


def test_apply_version(tmp_path):
    (tmp_path / "internacia_builder").mkdir()
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Fixed\n\n- NATO roster.\n\n## [3.0.0] - 2026-10-16\n\n- Old.\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "internacia-builder"\nversion = "3.0.0"\n')
    (tmp_path / "internacia_builder/__init__.py").write_text('__version__ = "3.0.0"\n')
    (tmp_path / "CITATION.cff").write_text("version: 3.0.0\ndate-released: 2026-10-16\n")
    (tmp_path / "uv.lock").write_text('[[package]]\nname = "internacia-builder"\nversion = "3.0.0"\n')

    release.apply_version(tmp_path, "3.0.1", date(2026, 11, 8), "- Countries: 256 → 256 records")

    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert changelog.startswith(
        "# Changelog\n\n## [Unreleased]\n\n## [3.0.1] - 2026-11-08\n\n### Fixed\n\n- NATO roster.\n\n"
        "### Data changes since the previous release\n\n- Countries: 256 → 256 records\n\n## [3.0.0] - 2026-10-16"
    )
    assert 'version = "3.0.1"' in (tmp_path / "pyproject.toml").read_text()
    assert (tmp_path / "internacia_builder/__init__.py").read_text() == '__version__ = "3.0.1"\n'
    assert (tmp_path / "CITATION.cff").read_text() == "version: 3.0.1\ndate-released: 2026-11-08\n"
    assert 'version = "3.0.1"' in (tmp_path / "uv.lock").read_text()


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    """A git repository with a v1.0.0 tag: real schemas, two countries, one intblock."""
    if not shutil.which("git"):
        pytest.skip("git is required")
    shutil.copytree(ROOT / "data/schemas", tmp_path / "data/schemas")
    shutil.copytree(ROOT / "data/blocktypes", tmp_path / "data/blocktypes")
    for code in ("FR", "DE"):
        (tmp_path / "data/countries").mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / f"data/countries/{code}.yaml", tmp_path / f"data/countries/{code}.yaml")
    nato = next(ROOT.glob("data/intblocks/*/NATO.yaml"))
    (tmp_path / "data/intblocks/military").mkdir(parents=True)
    shutil.copy(nato, tmp_path / "data/intblocks/military/NATO.yaml")
    (tmp_path / "data/datasets").mkdir()
    (tmp_path / "data/datasets/contract.json").write_text(json.dumps(build_contract("1.0.0", tmp_path)))
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.org", "add", ".")
    _git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@example.org", "commit", "-q", "-m", "data")
    _git(tmp_path, "tag", "v1.0.0")
    return tmp_path


def _commit(repo: Path) -> None:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.org", "commit", "-q", "-m", "change")


def test_plan_nothing_to_release(repo):
    plan = release.plan_release(repo)
    assert (plan.previous, plan.level, plan.version) == ("v1.0.0", "none", None)


def test_plan_patch_for_changed_values(repo):
    path = repo / "data/countries/FR.yaml"
    record = safe_load(path.read_text(encoding="utf-8"))
    record["capital_city"]["name"] = "Paris (updated)"
    path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    _commit(repo)
    plan = release.plan_release(repo)
    assert (plan.level, plan.version) == ("patch", "1.0.1")
    assert plan.diff["countries"]["changed"] == ["FR"]


def test_plan_minor_for_new_records(repo):
    shutil.copy(ROOT / "data/countries/IT.yaml", repo / "data/countries/IT.yaml")
    _commit(repo)
    plan = release.plan_release(repo)
    assert (plan.level, plan.version) == ("minor", "1.1.0")
    assert "countries added: IT" in plan.reasons["minor"]
    assert "Countries: 2 → 3 records; added `IT`" in release.render_summary(plan)


def test_plan_major_stops_the_train(repo):
    (repo / "data/countries/DE.yaml").unlink()
    _commit(repo)
    plan = release.plan_release(repo)
    assert (plan.level, plan.version) == ("major", None)
    assert plan.reasons["major"] == ["countries removed: DE"]


def test_plan_major_for_removed_enum_value(repo):
    path = repo / "data/schemas/intblocks.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    schema["properties"]["status"]["enum"].remove("historical")
    path.write_text(json.dumps(schema), encoding="utf-8")
    _commit(repo)
    assert any("values removed: historical" in r for r in release.plan_release(repo).reasons["major"])


def test_plan_counts_trade_agreements(repo):
    (repo / "data/trade_agreements").mkdir()
    for agreement in ("AANZFTA", "ACFTA"):
        shutil.copy(ROOT / f"data/trade_agreements/{agreement}.yaml", repo / f"data/trade_agreements/{agreement}.yaml")
    _commit(repo)
    _git(repo, "tag", "v1.0.1")
    shutil.copy(ROOT / "data/trade_agreements/ACIA.yaml", repo / "data/trade_agreements/ACIA.yaml")
    path = repo / "data/trade_agreements/ACFTA.yaml"
    record = safe_load(path.read_text(encoding="utf-8"))
    record["last_verified"] = "2099-01-01"
    path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding="utf-8")
    _commit(repo)
    plan = release.plan_release(repo)
    assert plan.previous == "v1.0.1"
    assert plan.diff["trade_agreements"] == {"count": [2, 3], "added": ["ACIA"], "removed": [], "changed": ["ACFTA"]}
    assert "- Trade agreements: 2 → 3 records; added `ACIA`; 1 changed" in release.render_summary(plan)


def test_summary_skips_empty_trade_agreements(repo):
    shutil.copy(ROOT / "data/countries/IT.yaml", repo / "data/countries/IT.yaml")
    _commit(repo)
    assert "Trade agreements" not in release.render_summary(release.plan_release(repo))
