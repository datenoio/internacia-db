## ADDED Requirements

### Requirement: Pinned runtime dependencies

All packages in the runtime dependency manifest SHALL specify version constraints that produce reproducible installs.

#### Scenario: Reproducible pip install

- **WHEN** two developers run `pip install -r requirements.txt` on the same commit
- **THEN** they receive the same package versions within declared constraints

#### Scenario: CI uses pinned dependencies

- **WHEN** CI installs dependencies from the manifest
- **THEN** no unpinned package resolves to an unexpected major version

### Requirement: Automated dependency update proposals

The repository SHALL configure Dependabot (or equivalent) to propose updates for pip packages and GitHub Actions.

#### Scenario: Dependabot configured

- **WHEN** a dependency has a security or version update available
- **THEN** Dependabot opens a pull request with updated constraints

### Requirement: CI dependency caching

CI workflows SHALL cache pip wheels between runs to reduce install time.

#### Scenario: Cache hit on repeated CI run

- **WHEN** CI runs on a pull request with unchanged `requirements.txt`
- **THEN** pip install reuses cached wheels when available
