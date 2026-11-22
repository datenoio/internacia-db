# intblocks-data-quality Specification

## Purpose
TBD - created by archiving change add-scheduled-link-validation. Update Purpose after archive.
## Requirements
### Requirement: Scheduled external link validation

The repository SHALL run intblock URL and Wikidata validation on a scheduled cadence independent of pull request CI.

#### Scenario: Weekly scheduled run

- **WHEN** the scheduled workflow triggers on the default branch
- **THEN** `validate_links.py` executes and produces a report artifact

#### Scenario: Scheduled failure does not block merges

- **WHEN** the scheduled link validation finds broken URLs
- **THEN** the workflow completes with failure status but does not block unrelated pull request merges

### Requirement: Link validation report artifact

Scheduled and manual link validation runs SHALL produce a machine-readable or markdown report suitable for triage.

#### Scenario: Report uploaded on scheduled run

- **WHEN** scheduled validation completes
- **THEN** a report file is available as a workflow artifact

#### Scenario: Manual validation with report

- **WHEN** a maintainer runs `validate_links.py --report links-report.json`
- **THEN** a structured report is written to the specified path

### Requirement: Intblock YAML JSON Schema validation

Every file under `data/intblocks/**/*.yaml` SHALL validate against `data/schemas/intblocks.schema.json` before dataset export. The JSON Schema SHALL declare the canonical intblock field set, and its top-level `additionalProperties` SHALL be `false` (or a documented narrow allowlist) so that undeclared fields are rejected rather than silently accepted.

#### Scenario: Valid intblock file passes schema

- **WHEN** `validate_intblocks.py` runs on a well-formed intblock YAML file using only declared fields
- **THEN** validation reports no schema errors for that file

#### Scenario: Invalid intblock file fails schema

- **WHEN** an intblock YAML file has a required field with wrong type
- **THEN** validation reports a schema error and exits with non-zero status

#### Scenario: Undeclared field rejected

- **WHEN** an intblock YAML file contains a key that is not part of the canonical declared field set
- **THEN** validation reports an additional-property error rather than silently accepting the field

### Requirement: Intblock identifier uniqueness

Each intblock record SHALL have a unique `id` across all YAML files under `data/intblocks/`.

#### Scenario: Duplicate intblock id rejected

- **WHEN** two intblock YAML files share the same `id`
- **THEN** validation reports a duplicate identifier error

### Requirement: Blocktype taxonomy validation

Every entry in an intblock's `blocktype` list SHALL reference a defined blocktype in the blocktypes **source** taxonomy file under `data/blocktypes/` (not the generated datasets copy).

#### Scenario: Valid blocktype accepted

- **WHEN** an intblock has `blocktype: [intorg]` and `intorg` exists in `data/blocktypes/blocktypes.yaml`
- **THEN** blocktype validation passes

#### Scenario: Unknown blocktype rejected

- **WHEN** an intblock references a blocktype not in the source taxonomy
- **THEN** validation reports a blocktype reference error

### Requirement: Configurable intblocks completeness thresholds

Completeness rules for intblocks SHALL be defined in `data/schemas/intblocks_completeness.yaml` with per-field `max_null_rate` and `mode` (`warn` or `error`).

#### Scenario: Field exceeding warn threshold emits warning

- **WHEN** `wikidata_id` null rate exceeds configured `max_null_rate` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Field exceeding error threshold fails build

- **WHEN** a field has `mode: error` and null rate exceeds `max_null_rate`
- **THEN** validation fails with a completeness error

### Requirement: Intblock includes contract enforcement

For each entry in `includes`, `id` SHALL be the authoritative member identifier; `name` is a source label and MAY differ from canonical country names.

#### Scenario: Include with valid country id passes

- **WHEN** an include has `type: country` and `id: US` and `data/countries/US.yaml` exists
- **THEN** include validation passes for that entry

#### Scenario: Include with missing country id fails or warns per config

- **WHEN** an include has `type: country` and `id: ZZ` with no matching country file
- **THEN** validation reports an unresolved include per completeness config mode

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
After high-profile description replacement, the configured templated-description `max_null_rate` or
equivalent threshold SHALL be tightened incrementally (e.g. from current ~24% toward ≤15% warn target).

#### Scenario: Templated description counted

- **WHEN** a record's description matches the boilerplate pattern (e.g. "International entity focused on …")
- **THEN** it is counted toward the templated-description rate in the validation report

#### Scenario: Rate over threshold warns

- **WHEN** the templated-description rate exceeds the configured `max` with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

#### Scenario: Threshold ratchets after backfill

- **WHEN** high-profile description replacement reduces the templated rate below the previous threshold
- **THEN** maintainers MAY lower the configured warn threshold in `intblocks_completeness.yaml` to prevent regression

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

### Requirement: Include date consistency

For each `includes[]` entry, `joined` and `left` dates SHALL parse as `YYYY`, `YYYYs`, `YYYY-MM`, or `YYYY-MM-DD`, SHALL NOT lie in the future, `left` SHALL NOT precede `joined`, and neither SHALL postdate the block's `dissolved` date. Comparisons SHALL be precision-aware (a bare year is not "before" a specific date in the same year). `joined` earlier than `founded` SHALL NOT be flagged, because signature and ratification dates commonly precede entry into force. Violations SHALL be reported as `INCLUDE_DATE_INCONSISTENCY`.

#### Scenario: Left before joined reported

- **WHEN** an include has `joined: 1995` and `left: 1990`
- **THEN** validation reports an `INCLUDE_DATE_INCONSISTENCY` issue

#### Scenario: Join after dissolution reported

- **WHEN** a block has `dissolved: 1991` and an include has `joined: 1994`
- **THEN** validation reports an `INCLUDE_DATE_INCONSISTENCY` issue

#### Scenario: Ratification before entry into force passes

- **WHEN** a block has `founded: 2008-07-03` and an include has `joined: 2008-05-09`
- **THEN** no `INCLUDE_DATE_INCONSISTENCY` issue is reported

### Requirement: Founding members appear in includes

Each `founding_members` entry SHALL resolve to an existing country code and, when the record has a populated `includes` list, SHALL appear in it. Violations SHALL be reported as `FOUNDING_MEMBER_NOT_INCLUDED` warnings (former founders may legitimately be absent and are resolved by adding a `former_member` include entry or removing the founder).

#### Scenario: Founder missing from includes warned

- **WHEN** `founding_members` contains `CU` but no include entry has `id: CU`
- **THEN** validation reports a `FOUNDING_MEMBER_NOT_INCLUDED` warning

### Requirement: Historical entity membership status

An include entry referencing a country with `entity_type: historical_entity` SHALL NOT carry an active-class status (`member`, `founding_member`, `associate`, `associate_member`, `associated`, `participant`) in a block whose `status` is not `historical`. Violations SHALL be reported as `HISTORICAL_ENTITY_ACTIVE_MEMBER`.

#### Scenario: Dissolved country as active member warned

- **WHEN** an active block includes `AN` (Netherlands Antilles, a historical entity) with status `member`
- **THEN** validation reports a `HISTORICAL_ENTITY_ACTIVE_MEMBER` warning

### Requirement: Verification freshness

When `last_verified` is populated and `quality.last_verified_max_age_months` is configured in `intblocks_completeness.yaml`, records whose `last_verified` date is older than the configured age SHALL be reported as `STALE_LAST_VERIFIED` (LOW advisory).

#### Scenario: Old verification date warned

- **WHEN** `last_verified` is more than the configured maximum months in the past
- **THEN** validation reports a `STALE_LAST_VERIFIED` advisory

### Requirement: Canonical topic catalog

Topic keys on intblock records SHALL exist in the canonical catalog `data/schemas/topics.yaml`. Keys absent from the catalog SHALL be reported as `UNKNOWN_TOPIC_KEY` warnings; deprecated keys remain governed by the existing alias rule.

#### Scenario: Unknown topic key warned

- **WHEN** a record uses topic key `undersea_basket_weaving` not present in `topics.yaml`
- **THEN** validation reports an `UNKNOWN_TOPIC_KEY` warning

#### Scenario: Catalogued key passes

- **WHEN** a record uses topic key `water` present in `topics.yaml`
- **THEN** no `UNKNOWN_TOPIC_KEY` issue is reported

### Requirement: Text encoding integrity for intblocks

`name` and `description` fields SHALL NOT contain control characters, U+FFFD replacement characters, or double-encoded UTF-8 artifacts. Violations SHALL be reported as `MOJIBAKE_TEXT`.

#### Scenario: Double-encoded UTF-8 reported

- **WHEN** a description contains the byte sequence rendered as `Ã©` (double-encoded é)
- **THEN** validation reports a `MOJIBAKE_TEXT` issue

### Requirement: Membership list internal consistency

Intblock membership data SHALL be internally consistent: an `includes` list SHALL NOT contain two entries with the same `id`, a populated `membership_count` SHALL match the number of `includes` entries within the tolerance configured in `data/schemas/intblocks_completeness.yaml` unless the record declares a non-country `membership_count_type`, and a record with `membership_applicability: not_applicable` SHALL NOT have a non-empty `includes` list. Violations SHALL be reported as `DUPLICATE_INCLUDE_ENTRY`, `MEMBERSHIP_COUNT_MISMATCH`, and `CONTRADICTORY_APPLICABILITY` respectively at MEDIUM priority.

#### Scenario: Duplicate include entry reported

- **WHEN** an intblock's `includes` list contains two entries with `id: FR`
- **THEN** validation reports a `DUPLICATE_INCLUDE_ENTRY` issue

#### Scenario: Membership count mismatch reported

- **WHEN** an intblock has `membership_count: 10` and 13 `includes` entries with mismatch beyond the configured tolerance and no non-country `membership_count_type`
- **THEN** validation reports a `MEMBERSHIP_COUNT_MISMATCH` issue

#### Scenario: Non-country count exempt from roster comparison

- **WHEN** an intblock declares `membership_count_type: companies` with `membership_count: 3000` and a short country `includes` list
- **THEN** validation does not report a `MEMBERSHIP_COUNT_MISMATCH` issue

#### Scenario: Contradictory applicability marker reported

- **WHEN** an intblock has `membership_applicability: not_applicable` and a non-empty `includes` list
- **THEN** validation reports a `CONTRADICTORY_APPLICABILITY` issue

### Requirement: Lifecycle chronology validation

Intblock lifecycle fields SHALL be chronologically coherent: `founded` and `dissolved` SHALL parse as dates or years, `dissolved` SHALL NOT precede `founded`, neither SHALL be in the future, and a record with `status: historical` SHALL declare a `dissolved` date. Violations SHALL be reported as `CHRONOLOGY_ERROR` (dates) or `LIFECYCLE_INCONSISTENCY` (status) at MEDIUM priority.

#### Scenario: Dissolved before founded reported

- **WHEN** an intblock has `founded: '1990'` and `dissolved: '1985'`
- **THEN** validation reports a `CHRONOLOGY_ERROR` issue

#### Scenario: Future founding date reported

- **WHEN** an intblock has a `founded` value later than the current date
- **THEN** validation reports a `CHRONOLOGY_ERROR` issue

#### Scenario: Historical status without dissolved date reported

- **WHEN** an intblock has `status: historical` and no `dissolved` value
- **THEN** validation reports a `LIFECYCLE_INCONSISTENCY` issue

#### Scenario: Dissolved record without historical status reported

- **WHEN** an intblock has a `dissolved` value and `status: formal`
- **THEN** validation reports a `LIFECYCLE_INCONSISTENCY` issue

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

### Requirement: Schema and export field parity

The intblock JSON Schema properties and the Arrow export schema field names SHALL be kept in parity, verified by an automated test with an explicit allowlist for documented source-only or export-normalized fields.

#### Scenario: Export field missing from JSON Schema fails parity

- **WHEN** the Arrow export schema exports a field that is neither declared in the JSON Schema nor on the parity allowlist
- **THEN** the schema-parity test fails

#### Scenario: Declared canonical field is exported

- **WHEN** a field is declared canonical in the JSON Schema and is not source-only
- **THEN** the Arrow export schema includes that field and the parity test passes

### Requirement: Intblocks gap backlog tracking

Deferred intblock candidates from gap analysis SHALL be tracked in `dev/research/backlog.md` with status, rationale, and sourcing requirements.

#### Scenario: Backlog lists deferred candidates

- **WHEN** a maintainer opens `dev/research/backlog.md`
- **THEN** each candidate from the gap analysis **Still Deferred** section appears with a documented status

#### Scenario: Shipped item updated

- **WHEN** a deferred candidate is added to the dataset
- **THEN** backlog status changes to `shipped` with reference to the YAML file path

### Requirement: Historical entity modeling consistency

Intblock records representing dissolved or historical organizations SHALL use consistent `status`, `dissolved`, and optional `predecessor`/`successor` fields per documented taxonomy.

#### Scenario: Historical alliance modeled consistently

- **WHEN** a historical military alliance record is added from the backlog
- **THEN** it includes `dissolved` date and `status` indicating historical status

### Requirement: Initiative scope exclusion criteria

Candidates classified as initiatives or programs without fixed membership SHALL be documented as `excluded` with rationale rather than added as intblocks.

#### Scenario: Initiative excluded with rationale

- **WHEN** a candidate is determined to be a program without stable membership
- **THEN** backlog marks it `excluded` with a documented reason

### Requirement: Blocktypes source and generated separation

Blocktypes taxonomy SHALL be maintained as source YAML under `data/blocktypes/` and exported to `data/datasets/` by the builder.

#### Scenario: Builder reads source taxonomy

- **WHEN** `scripts/builder.py build` exports blocktypes
- **THEN** it reads from `data/blocktypes/blocktypes.yaml` and writes generated artifacts to `data/datasets/`

#### Scenario: Contributors edit source not generated copy

- **WHEN** a contributor adds a new blocktype
- **THEN** they edit `data/blocktypes/blocktypes.yaml` and rebuild rather than editing generated files directly

### Requirement: High-profile intblock contextual metadata

High-profile intblock records (maintainer-defined cohort including UN principal organs, major regional blocs, and top multilateral institutions) SHALL have non-empty `legal_status`, `geographic_scope`, and `headquarters` after backfill.

#### Scenario: Major IGO has legal status

- **WHEN** backfill completes for a UN specialized agency in the high-profile cohort
- **THEN** the record includes `legal_status` describing its treaty or charter basis

#### Scenario: Major IGO has geographic scope

- **WHEN** backfill completes for NATO in the high-profile cohort
- **THEN** the record includes `geographic_scope` indicating regional or global reach

#### Scenario: Major IGO has headquarters

- **WHEN** backfill completes for the European Union in the high-profile cohort
- **THEN** the record includes `headquarters` with city and country

### Requirement: Context field provenance on enrichment

Automated or semi-automated backfill of `legal_status`, `geographic_scope`, or `headquarters` SHALL add corresponding `provenance` entries.

#### Scenario: Headquarters enrichment provenance

- **WHEN** `headquarters` is filled from an official organization website
- **THEN** a provenance entry documents `field`, `source`, and `retrieved_at`

### Requirement: Tier 2 high-priority intblock coverage

The intblocks dataset SHALL include records for the six Tier 2 gaps identified in `dev/research/report_manus_20260615.md`: `CHIP4`, `DEPA`, `PEPFAR`, `MSF`, `UNCITRAL`, and `UNCLOS`.

#### Scenario: Digital alliance record exists

- **WHEN** a consumer queries intblocks by `id: CHIP4`
- **THEN** a source record exists describing the semiconductor coordination alliance

#### Scenario: Digital trade agreement exists

- **WHEN** a consumer queries intblocks by `id: DEPA`
- **THEN** a source record exists for the Digital Economy Partnership Agreement

#### Scenario: Major health program exists

- **WHEN** a consumer queries intblocks by `id: PEPFAR`
- **THEN** a source record exists with documented membership or partner-country model

#### Scenario: Humanitarian NGO exists

- **WHEN** a consumer queries intblocks by `id: MSF`
- **THEN** a source record exists for Médecins Sans Frontières with appropriate non-IGO classification

#### Scenario: Trade law body exists

- **WHEN** a consumer queries intblocks by `id: UNCITRAL`
- **THEN** a source record exists for the UN Commission on International Trade Law

#### Scenario: Law of the Sea treaty exists

- **WHEN** a consumer queries intblocks by `id: UNCLOS`
- **THEN** a source record exists for the UN Convention on the Law of the Sea with party membership

### Requirement: UN principal organs coverage

The intblocks dataset SHALL include records for the three principal UN organs identified as Tier 1 gaps: UN Security Council (`UNSC`), UN General Assembly (`UNGA`), and UN Human Rights Council (`UNHRC`).

#### Scenario: UNSC record exists

- **WHEN** a consumer queries intblocks by `id: UNSC`
- **THEN** a YAML source file exists with required fields and a description of the Security Council's peace-and-security mandate

#### Scenario: UNGA record exists

- **WHEN** a consumer queries intblocks by `id: UNGA`
- **THEN** a YAML source file exists representing the General Assembly as the UN's main deliberative organ

#### Scenario: UNHRC record exists

- **WHEN** a consumer queries intblocks by `id: UNHRC`
- **THEN** a YAML source file exists with membership and status reflecting the Human Rights Council

### Requirement: UN organ hierarchical linkage

UN principal organ records SHALL declare `partof: [UN]` unless a documented exception applies.

#### Scenario: Organ linked to UN

- **WHEN** `UNSC`, `UNGA`, or `UNHRC` records are added
- **THEN** each includes `partof` referencing the existing `UN` intblock id

### Requirement: Primary blocktype directory alignment

The first value in an intblock record's `blocktype` list SHALL match the parent directory name under `data/intblocks/` (e.g. a record in `data/intblocks/trade/` must have primary blocktype `trade`).

#### Scenario: Aligned record passes

- **WHEN** `data/intblocks/trade/WTO.yaml` has `blocktype: [trade, intorg]`
- **THEN** directory alignment validation passes

#### Scenario: Misaligned primary blocktype reported

- **WHEN** a record in `data/intblocks/political/` has `blocktype: [economic, political]`
- **THEN** validation reports a primary blocktype–directory mismatch

### Requirement: Directory name matches blocktype value

Category directories under `data/intblocks/` SHALL use blocktype values as directory names, not synonyms (e.g. `tax` not `taxation`, `transport` not `transportation`).

#### Scenario: Renamed directory validates

- **WHEN** records are stored under `data/intblocks/tax/`
- **THEN** no directory named `taxation` exists in the intblocks tree

### Requirement: Orphan blocktype cleanup

Blocktype taxonomy entries that are not referenced by any intblock record SHALL be removed from the blocktypes source file unless explicitly reserved for upcoming records.

#### Scenario: Unused plural blocktype removed

- **WHEN** no record uses blocktype `unregionalblocks`
- **THEN** that entry is absent from the blocktypes taxonomy

### Requirement: Canonical topic alias registry

Deprecated intblock topic keys SHALL be documented in `data/schemas/topic_aliases.yaml` with a `canonical` target and optional `reason` for each deprecated key.

#### Scenario: Deprecated key maps to canonical

- **WHEN** a maintainer looks up `climate` in the alias registry
- **THEN** the canonical target is `climate_change`

#### Scenario: Validator warns on deprecated key

- **WHEN** an intblock record uses a topic key listed as deprecated in the alias registry
- **THEN** `validate_intblocks.py` emits a warning naming the canonical replacement

### Requirement: Minimum topic assignment

Every intblock record SHALL have at least one entry in its `topics` list after consolidation.

#### Scenario: Record with topics passes

- **WHEN** an intblock YAML has `topics` with one or more keys
- **THEN** topic completeness validation passes for that record

#### Scenario: Empty topics fails or warns per config

- **WHEN** an intblock record has an empty or missing `topics` list
- **THEN** validation reports per configured mode in intblocks completeness config

### Requirement: Topic taxonomy governance

The repository SHALL document in `docs/topic-taxonomy.md` the process for proposing, approving, merging, and deprecating topic keys.

#### Scenario: Contributor finds governance doc

- **WHEN** a contributor needs to add a new topic key
- **THEN** `docs/topic-taxonomy.md` describes the approval and alias-update steps

### Requirement: High-value organization coverage from 2026-08 audit

The intblocks dataset SHALL include records for the following bodies identified as verified coverage gaps: Codex Alimentarius Commission, Basel Committee on Banking Supervision, Court of Justice of the European Union, Inter-American Court of Human Rights, African Court on Human and Peoples' Rights, World Anti-Doping Agency, and the UN Secretariat. Each record SHALL meet the existing completeness gates and carry provenance for enriched fields.

#### Scenario: Codex Alimentarius record exists

- **WHEN** a consumer searches intblocks for the global food-standards body
- **THEN** a `CODEX` record exists with its member roster and FAO/WHO parentage

#### Scenario: Regional human-rights courts present

- **WHEN** a consumer lists records in the `court/` category
- **THEN** the Court of Justice of the EU, the Inter-American Court of Human Rights, and the African Court on Human and Peoples' Rights are present alongside ECHR

#### Scenario: UN Secretariat completes principal organs

- **WHEN** a consumer queries intblocks with `partof` containing `UN`
- **THEN** a UN Secretariat record appears alongside UNGA, UNSC, and UNHRC

### Requirement: Criminal court alias disambiguation

The intblock alias map SHALL document that the International Criminal Court is stored under id `ICW`, distinguishing it from the cricket body stored under `ICC`.

#### Scenario: Agent resolves ICC ambiguity

- **WHEN** an agent looks up "ICC" via the aliases artifact
- **THEN** it finds guidance that the criminal court is `ICW` and `ICC` is the International Cricket Council

### Requirement: Intblock scope category

Intblock records MAY include an optional `scope_category` field with values from a documented enum (`igo`, `treaty_body`, `policy_forum`, `reference_enumeration`) declared in `intblocks.schema.json`. The inclusion policy document SHALL define each category with examples.

#### Scenario: Core IGO labeled

- **WHEN** a consumer reads `data/intblocks/military/NATO.yaml` after labeling
- **THEN** `scope_category` is `igo`

#### Scenario: Reference enumeration labeled

- **WHEN** a consumer filters intblocks where `scope_category = 'reference_enumeration'`
- **THEN** DVD region records are included and NATO is excluded

### Requirement: Intblock inclusion policy document

The repository SHALL maintain `docs/intblock-inclusion-policy.md` stating what qualifies for an intblock record, how scope categories map to blocktypes, and how consumers should filter mixed corpora.

#### Scenario: Policy answers forum vs IGO question

- **WHEN** a reader asks whether Munich Security Conference belongs in the same filter as NATO
- **THEN** the policy doc explains the scope_category distinction and recommended filters

### Requirement: Membership count unit qualifier

The intblock schema SHALL provide an optional `membership_count_type` field (enum: `countries`, `organizations`, `companies`, `individuals`, `mixed`) declaring the unit of `membership_count`. When absent, the count SHALL be interpreted as country members. Records declaring a non-country type SHALL carry a provenance entry for `membership_count`.

#### Scenario: Consumer distinguishes count units

- **WHEN** a consumer reads a record with `membership_count: 3000` and `membership_count_type: companies`
- **THEN** the consumer can tell the count is not a country-member count

#### Scenario: Non-country count requires provenance

- **WHEN** a record declares a non-country `membership_count_type` without a `membership_count` provenance entry
- **THEN** validation reports an issue

### Requirement: Partof hierarchy semantic validation

Validation SHALL flag intblock records whose `partof.id` references a target classified as a treaty or agreement (`legal_status: treaty` or blocktype includes `agreement`) rather than a parent organization.

#### Scenario: EU partof EEA flagged

- **WHEN** validation runs on `economic/EU.yaml` with `partof: EEA` before correction
- **THEN** a hierarchy reversal finding is reported

#### Scenario: WHO partof UN passes

- **WHEN** validation runs on `unagency/WHO.yaml` with `partof: UN`
- **THEN** no hierarchy reversal finding is reported

### Requirement: UN specialized agency partof convention documented

`docs/intblock-inclusion-policy.md` SHALL document whether UN specialized agencies link `partof` directly to `UN` or through intermediate bodies such as `ECOSOC`.

#### Scenario: ILO convention documented

- **WHEN** a maintainer edits UN agency hierarchy
- **THEN** the policy doc states the chosen convention and lists affected agencies

### Requirement: Wikidata identifier completeness with exclusions

Every intblock record SHALL include a `wikidata_id` OR appear on a maintained exclusion list (`data/schemas/wikidata_exclusions.yaml`) documenting that no Wikidata item exists, with verification date and source. Validation SHALL fail on records missing both.

#### Scenario: Excluded org passes validation

- **WHEN** AFROSAIE lacks wikidata_id but is listed on the exclusion list with verified_at
- **THEN** validation passes

#### Scenario: Unlisted missing id fails

- **WHEN** an intblock with a findable Wikidata item lacks wikidata_id and is not excluded
- **THEN** validation reports a completeness error

#### Scenario: Fixable backfill reduces exclusions

- **WHEN** ACAO is backfilled with Q22686285
- **THEN** it is removed from the exclusion list if present and validation requires wikidata_id

### Requirement: Structural metadata enrichment from Wikidata

For intblock records with a resolved `wikidata_id`, enrichment SHALL backfill `headquarters` (from headquarters location and coordinate claims) and `founded` (from the inception claim) when those fields are empty, recording a `provenance` entry for each filled field and never overwriting existing hand-curated values.

#### Scenario: Headquarters filled from Wikidata

- **WHEN** a record has a `wikidata_id`, an empty `headquarters`, and Wikidata exposes a headquarters location claim
- **THEN** enrichment sets `headquarters` and adds a `provenance` entry with `field: headquarters` and `source: Wikidata`

#### Scenario: Existing founded date preserved

- **WHEN** a record already has a `founded` value
- **THEN** enrichment does not overwrite it even if Wikidata exposes an inception claim

### Requirement: Verification timestamp policy

Records touched by enrichment or manual verification SHALL carry a `last_verified` ISO 8601 date, and `validate_intblocks.py` SHALL report `last_verified` coverage against a configurable threshold in `intblocks_completeness.yaml` in warn mode.

#### Scenario: Enrichment stamps last_verified

- **WHEN** `enrich_intblocks.py` updates any field on a record
- **THEN** the record's `last_verified` is set to the run date

#### Scenario: Low coverage warns without failing build

- **WHEN** the share of records with a `last_verified` date is below the configured threshold with `mode: warn`
- **THEN** validation emits a warning but does not fail the build

### Requirement: Consistent scope reporting
Standalone validation and quality analysis SHALL emit the same missing formal
scope issue. Explicit historical identifiers SHALL be validated without treating
them as current-country rows.

#### Scenario: Missing formal scope
- **WHEN** a formal record omits scope_category
- **THEN** both validation and quality analysis report that omission

#### Scenario: Unknown historical reference
- **WHEN** a historical-country include references an unrecognized identifier
- **THEN** validation reports an unresolved historical reference

### Requirement: Honest enrichment dates
Enrichment SHALL preserve untouched retrieval dates, refresh provider-backed
values only from usable responses, and preserve declared observation precision.
Updating metadata alone SHALL NOT imply membership-roster verification.

#### Scenario: Provider failure
- **WHEN** a provider returns no usable observation for an existing field
- **THEN** its stored value and retrieval date remain unchanged

#### Scenario: Year-only inception
- **WHEN** Wikidata supplies a year-precision inception
- **THEN** the authored date contains only the year and no fabricated month or day

### Requirement: Duplicate-link classification

The quality analyzer's duplicate-link check SHALL classify findings by link type and SHALL NOT treat country `tld` values as URLs. Expected shared domains and parent/child entity relationships SHALL be allowed, and the report SHALL distinguish "possible duplicate entity" from "shared external citation".

#### Scenario: TLD not flagged as duplicate link

- **WHEN** two country records share a top-level domain such as `.fr`
- **THEN** the analyzer does not emit a `DUPLICATE_LINK` finding derived from a `tld` pseudo-URL

#### Scenario: Shared citation classified separately from duplicate entity

- **WHEN** two distinct organizations legitimately cite the same external source URL
- **THEN** the finding is classified as a shared external citation rather than a possible duplicate entity

### Requirement: Attribute partitions excluded from intblocks

The intblocks dataset SHALL NOT contain records whose primary purpose is to encode a country attribute partition for DVD region, government form, legal system, rail gauge, television/broadcast system, traffic hand, writing direction, or writing system. Those classifications SHALL live on country records and/or vocab catalogs. Named geographic or set groupings MAY remain as intblocks with `scope_category: reference_enumeration`.

#### Scenario: Traffichand directory removed

- **WHEN** a consumer lists `data/intblocks/` after this change ships
- **THEN** no `traffichand` category directory exists

#### Scenario: Geographic reference enumeration retained

- **WHEN** a consumer filters intblocks with `scope_category = 'reference_enumeration'`
- **THEN** geographic groupings such as SIDS remain available and attribute-partition blocktypes do not

#### Scenario: Blocktype taxonomy drops attribute types

- **WHEN** `data/blocktypes/blocktypes.yaml` is read after retirement
- **THEN** it does not define `dvdregion`, `govform`, `lawsystem`, `railgauge`, `teleregion`, `traffichand`, `writingdirection`, or `writingsystem`

### Requirement: Government form not modeled as country org membership

`govform` intblock records SHALL be retired from the intblocks corpus. Government-form typology SHALL NOT be reintroduced as intblock membership rosters. Optional vocab-only preservation of form definitions is permitted without country `includes` and without adding government-type fields to countries.

#### Scenario: No govform includes after retirement

- **WHEN** intblocks validation runs after this change
- **THEN** no intblock file under a `govform` blocktype exists

#### Scenario: Countries remain without government type field

- **WHEN** `countries.schema.json` is inspected after this change
- **THEN** it does not define government form / govform properties

### Requirement: Audited roster accuracy

Rosters of intblock records flagged by the 2026-08 external audit (`AFUNION`, `INTERPOL`, `CIS`, `UN`, `AIIB`, cricket `ICC`) SHALL match the membership published by the organization's official source at verification time, with `membership_count` equal to the current-member roster, correct `geographic_scope`, and membership status transitions (`former_member`, `associate_member`, `observer`, `left` dates) recorded instead of stale plain `member` entries. Each corrected field SHALL carry a provenance entry naming the official source.

#### Scenario: African Union includes SADR

- **WHEN** a consumer counts current members of `AFUNION`
- **THEN** the result is 55 and includes `EH`

#### Scenario: Interpol roster matches official count

- **WHEN** a consumer counts current members of `INTERPOL`
- **THEN** the result is 196 (matching the official member list, in which `FM` and `PW` are members and Aruba, Curaçao, and Sint Maarten appear as territory members), and `geographic_scope` is `global`

#### Scenario: CIS withdrawals recorded

- **WHEN** a consumer queries `CIS` includes for Georgia and Ukraine
- **THEN** both carry `status: former_member` with a `left` date, and Turkmenistan carries an associate status

#### Scenario: UN record is globally scoped with observers

- **WHEN** a consumer reads `political/UN.yaml`
- **THEN** `geographic_scope` is `global`, `PS` and `VA` appear with `status: observer`, and the member count remains 193

#### Scenario: Membership count matches roster for audited records

- **WHEN** validation compares `membership_count` to the includes roster for `AIIB` and cricket `ICC`
- **THEN** the values agree within the configured tolerance

### Requirement: No composite blocktypes

A blocktype SHALL NOT be defined as the combination of two or more other blocktypes. A record that belongs to several domains SHALL list each domain blocktype. The composite keys `eccurr` (economic and currency union) and `cuscurr` (customs and currency union) SHALL be deprecated, with replacements `[economic, currency]` and `[customs, currency]`, and SHALL stay only on their reviewed baseline records (`eccurr`: `OECS`; `cuscurr`: `CEMAC`, `UEMOA`) until the next MAJOR release.

#### Scenario: Customs union that shares a currency

- **WHEN** a contributor adds a customs union whose treaty also creates a shared currency
- **THEN** the record has `blocktype` with `customs` first and `currency` as a secondary value, and no `cuscurr`

#### Scenario: New record with a composite blocktype rejected

- **WHEN** a record outside the baseline adds `eccurr` or `cuscurr` to its `blocktype` list
- **THEN** validation reports a deprecated-blocktype ratchet error that names the record

#### Scenario: Composite blocktype as primary rejected

- **WHEN** a record has `blocktype: [eccurr, economic]`
- **THEN** validation reports that a deprecated blocktype is the primary blocktype

### Requirement: Currency union records

Every current currency union or shared-currency area SHALL have its own record with primary blocktype `currency`, whose `includes` list is the roster of countries that use the currency under that arrangement. A record with another primary blocktype SHALL carry `currency` as a secondary blocktype only when its own founding instruments establish or administer the shared currency and every full member uses it.

#### Scenario: Euro area roster

- **WHEN** a consumer needs the countries that use the euro as EU member states
- **THEN** the `EUROAREA` record lists the 21 euro area member states, and `EU` does not carry `currency`, because 6 of its 27 members do not use the euro

#### Scenario: Organization that administers its members' currency

- **WHEN** every full member of an organization uses a currency that the organization's treaties establish
- **THEN** the organization carries `currency` as a secondary blocktype, and the currency union is still a separate `currency` record

