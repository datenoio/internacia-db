## ADDED Requirements

### Requirement: Committed dataset freshness gate

Pull request CI SHALL rebuild datasets into a temporary location and fail when the committed `data/datasets/` primary-key sets, row counts, or manifest build identity differ from the fresh build, except for changes explicitly allowed via an opt-in flag. The validate workflow path filters SHALL include `data/datasets/**` so dataset-only commits are validated.

#### Scenario: Stale committed artifact fails CI

- **WHEN** a pull request changes source YAML but does not rebuild `data/datasets/`
- **THEN** the freshness gate detects the id-set or row-count difference and the CI workflow fails

#### Scenario: Dataset-only commit is validated

- **WHEN** a commit modifies only files under `data/datasets/`
- **THEN** the validate workflow still runs because the path filter includes `data/datasets/**`

### Requirement: Blocktypes build manifest

Each successful build SHALL write `data/datasets/blocktypes.manifest.json` containing at minimum `version`, `build_date` (ISO 8601), `git_commit`, `row_count`, and `schema_hash`, matching the fields of the countries and intblocks manifests.

#### Scenario: Blocktypes manifest written after build

- **WHEN** `scripts/builder.py build` completes a blocktypes export
- **THEN** `blocktypes.manifest.json` exists with `row_count` equal to the number of defined blocktypes

#### Scenario: Documentation and release assets match emitted manifests

- **WHEN** documentation or the release workflow references `blocktypes.manifest.json`
- **THEN** the referenced file is actually produced by the build
