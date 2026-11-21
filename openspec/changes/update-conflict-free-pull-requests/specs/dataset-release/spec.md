## MODIFIED Requirements

### Requirement: Committed dataset freshness gate

Pull request CI SHALL rebuild datasets into a temporary location and fail when a committed `data/datasets/` descriptor differs from the fresh build. The committed descriptors SHALL be only the files that change with the schema or with rare source edits: `contract.json`, `README.md`, `intblocks_aliases.json`, `countries_aliases.json`, `attribute_intblock_migrations.json` and `border_status.json`. Build manifests (`*.manifest.json`) and `datapackage.json` SHALL NOT be committed, because they carry per-build checksums, sizes, row counts and build identity that every data change rewrites; the build SHALL still write them and every GitHub Release SHALL still ship them. CI SHALL fail when a generated export or a build-only descriptor is tracked in git. The validate workflow path filters SHALL include `data/datasets/**` so dataset-only commits are validated.

#### Scenario: Stale committed artifact fails CI

- **WHEN** a pull request changes the source schema but does not rebuild `contract.json`
- **THEN** the freshness gate detects the difference and the CI workflow fails

#### Scenario: Data change touches no descriptor

- **WHEN** a pull request adds an intblock record and rebuilds
- **THEN** git shows no change under `data/datasets/` and the freshness gate passes

#### Scenario: Build manifest tracked by mistake

- **WHEN** a pull request adds `data/datasets/intblocks.manifest.json` to git
- **THEN** the freshness gate fails and names the file

#### Scenario: Dataset-only commit is validated

- **WHEN** a commit modifies only files under `data/datasets/`
- **THEN** the validate workflow still runs because the path filter includes `data/datasets/**`

## ADDED Requirements

### Requirement: Changelog fragments

A pull request SHALL record its consumer-visible changes as one fragment file `changelog.d/<slug>.md` instead of editing `CHANGELOG.md`. A fragment SHALL contain only Keep a Changelog subsections (`### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`), each with at least one entry. Entries SHALL NOT carry running dataset totals. When the release train writes a release, it SHALL merge the `[Unreleased]` body of `CHANGELOG.md` and every fragment into the dated release section, grouped by subsection in Keep a Changelog order, and SHALL delete the merged fragments in the same release pull request.

#### Scenario: Two pull requests add entries

- **WHEN** two open pull requests each add a changelog fragment with a different slug
- **THEN** neither pull request conflicts with the other in changelog files

#### Scenario: Release merges fragments

- **WHEN** the release train applies `v4.3.0` with fragments `ah.md` (`### Added`) and `fix-view.md` (`### Fixed`)
- **THEN** the `## [4.3.0]` section has one `### Added` and one `### Fixed` subsection holding those entries, and `changelog.d/` keeps only its README

#### Scenario: Unknown subsection

- **WHEN** a fragment uses `### Notes`
- **THEN** the test suite fails and names the fragment
