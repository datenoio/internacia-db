## ADDED Requirements

### Requirement: Explicit dataset license

The repository SHALL declare an explicit license for the compiled datasets in `data/datasets/`,
separate from the source-code license (`LICENSE`). The data license SHALL be recorded in a
`DATA_LICENSE` file at the repository root using a recognized open-data license (e.g. CC-BY-4.0 or
CC0-1.0).

#### Scenario: Data license file present

- **WHEN** a consumer inspects the repository root
- **THEN** a `DATA_LICENSE` file exists stating the license that applies to dataset artifacts

#### Scenario: Code and data licenses distinguished

- **WHEN** a consumer reads the README license section
- **THEN** it states that source code is MIT-licensed and dataset artifacts are covered by `DATA_LICENSE`

### Requirement: Source attribution documentation

The repository SHALL document upstream data sources and their license obligations in an
`ATTRIBUTION.md` file, including World Bank, Wikidata, and IANA tzdata, plus a recommended citation
for reusing the datasets.

#### Scenario: Upstream sources attributed

- **WHEN** a consumer reads `ATTRIBUTION.md`
- **THEN** it lists World Bank (CC-BY-4.0), Wikidata (CC0), and IANA tzdata with links

#### Scenario: Citation guidance available

- **WHEN** a researcher wants to cite the datasets
- **THEN** `ATTRIBUTION.md` provides a recommended citation format

### Requirement: License metadata in build manifest

Each dataset build manifest (`countries.manifest.json`, `intblocks.manifest.json`) SHALL include a
machine-readable `data_license` field containing the SPDX identifier of the dataset license.

#### Scenario: Manifest declares data license

- **WHEN** `scripts/builder.py` writes a dataset manifest
- **THEN** the manifest contains a non-empty `data_license` field with an SPDX identifier (e.g. `CC-BY-4.0`)
