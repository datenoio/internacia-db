## ADDED Requirements

### Requirement: Hugging Face dataset mirror

Tagged releases SHALL publish countries and intblocks Parquet artifacts to a Hugging Face Datasets repository linked from README.

#### Scenario: HF dataset updated on release

- **WHEN** release workflow completes for tag `v*`
- **THEN** the Hugging Face dataset revision matches the release Parquet artifacts

### Requirement: Automated Zenodo deposit

The release workflow SHALL deposit release artifacts to Zenodo under the existing concept DOI, producing a version-specific DOI for each release.

#### Scenario: Zenodo version follows tag

- **WHEN** tag `v2.0.0` is released
- **THEN** Zenodo records a new version linked to concept DOI `10.5281/zenodo.21452328`
