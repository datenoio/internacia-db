## MODIFIED Requirements

### Requirement: Source attribution documentation

The repository SHALL document upstream data sources and their license obligations in an
`ATTRIBUTION.md` file, including World Bank, Wikidata, IANA tzdata, and mledoze/countries
(ODbL-1.0), plus a recommended citation for reusing the datasets. Any upstream source cited in
per-record `provenance` entries SHALL appear in the attribution table, and share-alike-licensed
sources SHALL carry a documented compatibility rationale for redistribution under the dataset
license.

#### Scenario: Upstream sources attributed

- **WHEN** a consumer reads `ATTRIBUTION.md`
- **THEN** it lists World Bank (CC-BY-4.0), Wikidata (CC0), IANA tzdata, and mledoze/countries (ODbL-1.0) with links

#### Scenario: Citation guidance available

- **WHEN** a researcher wants to cite the datasets
- **THEN** `ATTRIBUTION.md` provides a recommended citation format

#### Scenario: Provenance-cited source appears in attribution table

- **WHEN** a source is named in any country or intblock `provenance` entry
- **THEN** `ATTRIBUTION.md` contains a row for that source with its license

#### Scenario: Share-alike source has compatibility rationale

- **WHEN** a consumer checks how ODbL-derived fields are redistributed under CC-BY-4.0
- **THEN** `ATTRIBUTION.md` (or a linked document) states the compatibility rationale

## ADDED Requirements

### Requirement: Machine-readable citation metadata

The repository SHALL provide a valid `CITATION.cff` file at the root referencing the dataset's Zenodo DOI, and `README.md` SHALL display a DOI badge.

#### Scenario: GitHub citation widget works

- **WHEN** a visitor opens the repository on GitHub
- **THEN** the "Cite this repository" widget renders from `CITATION.cff` including the DOI

#### Scenario: DOI badge present

- **WHEN** a reader views `README.md`
- **THEN** a Zenodo DOI badge links to the dataset's DOI record
