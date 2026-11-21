## MODIFIED Requirements

### Requirement: Intblock quality report parity

Every intblock rule enforced by `validate_intblocks.py` SHALL also be executed by the quality analyzer and surfaced in `dataquality/` reports, including filename-to-`id` alignment, directory-to-blocktype alignment, deprecated topic key detection against `data/schemas/topic_aliases.yaml`, the `wikidata_id` requirement, `partof` targets, and provenance integrity (each `provenance[].field` naming an existing record field with a valid, non-future `retrieved_at` date). Parity SHALL follow from both consumers running the shared rule registry.

#### Scenario: Filename and id mismatch appears in quality report

- **WHEN** the file `data/intblocks/bank/ADB.yaml` contains `id: XYZ`
- **THEN** the analyzer reports a `FILENAME_ID_MISMATCH` issue

#### Scenario: Directory and blocktype mismatch appears in quality report

- **WHEN** an intblock file under `data/intblocks/bank/` has no `bank` entry in its `blocktype` list
- **THEN** the analyzer reports a `DIRECTORY_BLOCKTYPE_MISMATCH` issue

#### Scenario: Deprecated topic key appears in quality report

- **WHEN** an intblock uses topic key `climate`, which `topic_aliases.yaml` maps to canonical `climate_change`
- **THEN** the analyzer reports a `DEPRECATED_TOPIC_KEY` issue

#### Scenario: Missing wikidata_id appears in quality report

- **WHEN** an intblock has no `wikidata_id` and is not listed in `data/schemas/wikidata_exclusions.yaml`
- **THEN** `validate_intblocks.py` reports an error and the analyzer reports a `MISSING_WIKIDATA_ID` issue
