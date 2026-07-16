## ADDED Requirements

### Requirement: Build and quality logic in installable package

Dataset build/export logic and the quality analyzer SHALL live in the installable `internacia_builder` package (for example `internacia_builder.build` and `internacia_builder.quality`), and `scripts/builder.py` SHALL be a thin CLI shim over that package. The quality analyzer SHALL reuse the package validators rather than duplicating validation rules.

#### Scenario: Build importable from package

- **WHEN** a developer imports the build entry point from `internacia_builder`
- **THEN** datasets can be built without importing from `scripts/` via `sys.path` mutation

#### Scenario: Analyzer reuses validators

- **WHEN** the quality analyzer checks intblock references or country borders
- **THEN** it calls shared validation functions rather than a duplicated copy

### Requirement: Console entry points for build and quality

`pyproject.toml` SHALL expose `internacia-build` and `internacia-analyze-quality` console entry points, and the package SHALL carry a documented version aligned with dataset releases rather than a placeholder.

#### Scenario: Build entry point runs

- **WHEN** a user runs `internacia-build` after `pip install -e .`
- **THEN** the datasets build the same as `python scripts/builder.py build`

#### Scenario: Package reports a real version

- **WHEN** a consumer inspects `internacia_builder.__version__`
- **THEN** it reports the current release version, not `0.0.0`

### Requirement: Cross-format export equivalence tests

The test suite SHALL verify that all committed export formats agree on row count and primary-key set per dataset, and that build manifests match actual exported rows.

#### Scenario: Format parity asserted

- **WHEN** the export equivalence test runs against a build
- **THEN** JSONL, YAML, Parquet, and DuckDB report identical id sets and row counts for each dataset

#### Scenario: Manifest count matches rows

- **WHEN** the manifest consistency test runs
- **THEN** each manifest `row_count` equals the number of exported rows for that dataset
