## MODIFIED Requirements

### Requirement: Native names map

Every country record SHALL have `native_names` as a map from language key to `{official, common}` for the entity's own languages. The keys SHALL be the record's `languages[]` entries, mapped through `data/vocabs/language_codes.yaml` to ISO 639-1 (or ISO 639-3 when no ISO 639-1 code exists). `official` SHALL come from the Wikidata official name (P1448) in that language. `common` SHALL come from the Wikidata label in that language, or from the native label (P1705) when the label repeats `official`. Aliases SHALL NOT be used. Either value MAY be null, and an entry with neither SHALL be omitted. Names in languages that are not in `languages[]` belong in `other_names`, not in `native_names`. The map SHALL be empty only when `languages[]` is empty.

#### Scenario: Native names populated

- **WHEN** enrichment completes for all country sources
- **THEN** no country record has a null or missing `native_names` key at export time

#### Scenario: Official and common are not swapped

- **WHEN** enrichment builds `native_names` for Germany
- **THEN** the `de` entry has `official` "Bundesrepublik Deutschland" and `common` "Deutschland", and there is no `en` entry

#### Scenario: Aliases are excluded

- **WHEN** a Wikidata alias such as "Red China" exists for an entity
- **THEN** it does not appear in any `native_names` value

#### Scenario: Chinese uses the entity's script

- **WHEN** enrichment builds the `zh` entry for CN and for TW
- **THEN** CN uses Simplified characters (`common` 中国) and TW uses Traditional characters

#### Scenario: Key outside the entity's languages

- **WHEN** a record has a `native_names` key that is not one of its mapped `languages[]`
- **THEN** validation reports a `NATIVE_NAME_LANGUAGE` warning for that key

#### Scenario: Entity without languages

- **WHEN** a record has an empty `languages[]` (for example AQ)
- **THEN** an empty `native_names` map passes completeness, while an empty map on a record with languages fails it
