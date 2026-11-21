# Changelog fragments

Do not edit `CHANGELOG.md` in a pull request. Add one file here instead:
`changelog.d/<slug>.md`, where `<slug>` is short, lowercase and unique, such as the
branch name without its `claude/` prefix (`asian-highway-network.md`).

Every pull request used to insert its entry at the top of `### Added` under
`[Unreleased]`, so any two open pull requests conflicted and had to merge `main`, rebuild
and wait for CI again. One file per pull request never conflicts.

## Format

A fragment holds only Keep a Changelog subsections, each with at least one entry:
`### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`.

```markdown
### Added

- `AH` (Asian Highway Network, Wikidata Q728802), a `project`/`transport` record for the
  ESCAP road network itself, checked on 2026-11-21.

### Fixed

- `country_borders` view reads on DuckDB before 2.0.
```

Do not write running dataset totals such as "(1304 intblocks)": they are stale as soon
as another pull request merges. The release adds a generated data-change summary.

`tests/test_changelog.py` checks every fragment. When the release train prepares a
release (`scripts/prepare_release.py --apply`), it merges the `[Unreleased]` body of
`CHANGELOG.md` and every fragment into the dated release section, grouped by subsection,
and deletes the fragments.
