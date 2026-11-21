"""Changelog fragments under changelog.d/ and how the release merges them."""

from datetime import date
from pathlib import Path

import pytest

from internacia_builder import changelog, release

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("path", changelog.fragment_paths(ROOT), ids=lambda p: p.name)
def test_repository_fragments_are_valid(path):
    assert changelog.check_fragment(path) == []


def _fragment(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_fragment_problems(tmp_path):
    assert changelog.check_fragment(_fragment(tmp_path, "ok.md", "### Added\n\n- `AH` record.\n")) == []
    problems = changelog.check_fragment(
        _fragment(tmp_path, "bad.md", "Intro.\n\n## [Unreleased]\n\n### Notes\n\n- Twelve records (1297 intblocks).\n\n### Fixed\n")
    )
    assert any("text before the first" in p for p in problems)
    assert any("unknown subsection '### Notes'" in p for p in problems)
    assert any("empty subsection '### Fixed'" in p for p in problems)
    assert any("'#' or '##' headings" in p for p in problems)
    assert any("running dataset total (1297 intblocks)" in p for p in problems)
    assert changelog.check_fragment(_fragment(tmp_path, "empty.md", "\n")) == [
        "changelog.d/empty.md: no '### ' subsection (Added, Changed, Deprecated, Removed, Fixed, Security)"
    ]


def test_merge_groups_subsections_in_keep_a_changelog_order():
    unreleased = "### Fixed\n\n- NATO roster.\n\n### Added\n\n- `EU` alias.\n  Two lines."
    fragments = ["### Added\n\n- `AH` record.\n", "### Changed\n\n- Rounded counts.\n\n### Added\n\n- `TAR` link.\n"]
    assert changelog.merge(unreleased, fragments) == (
        "### Added\n\n- `EU` alias.\n  Two lines.\n- `AH` record.\n- `TAR` link.\n\n"
        "### Changed\n\n- Rounded counts.\n\n"
        "### Fixed\n\n- NATO roster."
    )


def test_merge_keeps_prose_and_unknown_unreleased_subsections():
    unreleased = "Migration notes first.\n\n### Migration\n\nRun the query below."
    assert changelog.merge(unreleased, ["### Removed\n\n- `intorg`.\n"]) == (
        "Migration notes first.\n\n### Removed\n\n- `intorg`.\n\n### Migration\n\nRun the query below."
    )


def _release_tree(tmp_path, unreleased):
    (tmp_path / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [Unreleased]\n\n{unreleased}## [3.0.0] - 2026-10-16\n\n- Old.\n", encoding="utf-8"
    )
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "internacia-builder"\nversion = "3.0.0"\n')
    directory = tmp_path / changelog.FRAGMENTS_DIR
    directory.mkdir()
    (directory / changelog.README).write_text("# Changelog fragments\n")
    return directory


def test_apply_version_merges_and_deletes_fragments(tmp_path):
    directory = _release_tree(tmp_path, "### Fixed\n\n- NATO roster.\n\n")
    (directory / "ah.md").write_text("### Added\n\n- `AH` record.\n")
    (directory / "fix-view.md").write_text("### Fixed\n\n- `country_borders` view.\n")

    written = release.apply_version(tmp_path, "3.1.0", date(2026, 11, 21), "- Intblocks: 1 → 2 records")

    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8").startswith(
        "# Changelog\n\n## [Unreleased]\n\n## [3.1.0] - 2026-11-21\n\n"
        "### Added\n\n- `AH` record.\n\n### Fixed\n\n- NATO roster.\n- `country_borders` view.\n\n"
        "### Data changes since the previous release\n\n- Intblocks: 1 → 2 records\n\n## [3.0.0] - 2026-10-16"
    )
    assert sorted(p.name for p in directory.iterdir()) == [changelog.README]
    assert directory / "ah.md" in written and directory / "fix-view.md" in written


def test_apply_version_refuses_an_invalid_fragment(tmp_path):
    directory = _release_tree(tmp_path, "")
    (directory / "bad.md").write_text("### Notes\n\n- Something.\n")
    with pytest.raises(ValueError, match="unknown subsection"):
        release.apply_version(tmp_path, "3.0.1", date(2026, 11, 21), "")
    assert (directory / "bad.md").exists()
