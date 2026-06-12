## MODIFIED Requirements

### Requirement: Intblocks validation before export

The dataset builder SHALL run intblock validation before writing intblocks derived artifacts by importing the validation module directly rather than subprocess invocation.

#### Scenario: Build fails on intblock schema error

- **WHEN** the builder runs and an intblock YAML file fails schema validation
- **THEN** the build exits with non-zero status and does not overwrite intblocks outputs

#### Scenario: Validator importable in tests

- **WHEN** pytest imports the intblocks validation module
- **THEN** validation functions are callable without spawning a subprocess

### Requirement: Countries validation before export

The dataset builder SHALL run country validation before export by importing the validation module directly rather than subprocess invocation.

#### Scenario: Country validation without subprocess

- **WHEN** the builder runs pre-export validation
- **THEN** it calls the countries validation module directly without `subprocess.run`

## ADDED Requirements

### Requirement: Shared HTTP client for enrichment and link validation

External HTTP calls in enrichment and link validation SHALL use a shared client module with configurable rate limiting and retry with backoff.

#### Scenario: Rate limit applied

- **WHEN** enrichment fetches multiple World Bank or Wikidata endpoints
- **THEN** requests respect the configured minimum delay between calls

#### Scenario: Retry on transient failure

- **WHEN** an HTTP request fails with a retryable status code
- **THEN** the client retries up to a configured limit before reporting failure

### Requirement: CLI backward compatibility shims

Existing `scripts/*.py` entry points SHALL remain functional for at least one release cycle after package extraction.

#### Scenario: Legacy script path works

- **WHEN** a user runs `python scripts/builder.py build`
- **THEN** the build completes successfully via shim delegation to the package CLI
