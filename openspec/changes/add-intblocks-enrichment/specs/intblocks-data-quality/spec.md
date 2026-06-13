## ADDED Requirements

### Requirement: Intblock field-level provenance

Intblock YAML records MAY include a `provenance` list. When present, each entry SHALL include
`field`, `source`, and `retrieved_at` (ISO 8601 date); `url` and `license` are optional. Enrichment
that fills a field from an external source SHALL record a corresponding provenance entry. The
`provenance` field SHALL be exported in all dataset formats.

#### Scenario: Enrichment adds provenance

- **WHEN** `enrich_intblocks.py` fills `wikidata_id` from Wikidata
- **THEN** the record gains a `provenance` entry with `field: wikidata_id` and `source: Wikidata`

#### Scenario: Records without enrichment omit provenance

- **WHEN** an intblock file has only hand-curated data
- **THEN** validation passes whether or not `provenance` is present

### Requirement: High-confidence wikidata_id backfill

Automated `wikidata_id` backfill SHALL only assign an identifier when there is a high-confidence
match: an existing Wikidata link on the record, or a normalized exact match between the record name
(or acronym) and a Wikidata search candidate's label or alias. Ambiguous matches SHALL be left
unassigned.

#### Scenario: Exact name match assigns id

- **WHEN** a record named "African Union" has no `wikidata_id` and Wikidata returns a candidate whose label is "African Union"
- **THEN** the record's `wikidata_id` is set to that candidate's QID with provenance

#### Scenario: No confident match leaves record unchanged

- **WHEN** no Wikidata candidate label or alias matches the record name or acronym
- **THEN** the record's `wikidata_id` remains unset

### Requirement: Description quality gate

`validate_intblocks.py` SHALL measure the share of records using templated boilerplate descriptions
and report it against a configurable threshold in `intblocks_completeness.yaml` (warn or error mode).

#### Scenario: Templated description counted

- **WHEN** a record's description matches the boilerplate pattern (e.g. "International entity focused on …")
- **THEN** it is counted toward the templated-description rate in the validation report

#### Scenario: Rate over threshold warns

- **WHEN** the templated-description rate exceeds the configured `max` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

### Requirement: Multilingual alias enrichment

Enrichment SHALL backfill multilingual `other_names` (keyed by language code) and acronym aliases
from Wikidata labels and aliases for records with a resolved `wikidata_id`, without removing existing
entries.

#### Scenario: Other-name added for a UN language

- **WHEN** a record has a `wikidata_id` and Wikidata has a French label not already in `other_names`
- **THEN** enrichment adds an `other_names` entry with `id: fr` and the French label

#### Scenario: Existing names preserved

- **WHEN** a record already has an `other_names` entry for a language
- **THEN** enrichment does not overwrite that entry
