# contributor-docs Specification

## Purpose
TBD - created by archiving change add-contributor-docs. Update Purpose after archive.
## Requirements
### Requirement: Contributing guide

The repository SHALL include `CONTRIBUTING.md` describing development setup, validation commands, and pull request expectations.

#### Scenario: New contributor finds setup steps

- **WHEN** a contributor opens `CONTRIBUTING.md`
- **THEN** they find instructions to install dependencies, run validation, and build datasets

#### Scenario: PR checklist documented

- **WHEN** a contributor prepares a data change pull request
- **THEN** CONTRIBUTING lists required checks (validate countries, builder, pytest when available)

### Requirement: README accuracy

README SHALL list all maintained utility scripts and link to gap analysis files with correct paths. README SHALL state current dataset counts (countries, intblocks, categories, blocktypes) consistent with the build manifests, with the intblock count rounded down to the hundred and written as `N+`, and SHALL accurately describe which validators run before export. README SHALL describe driving side and other migrated attribute classifications as country properties, not intblock categories, after attribute intblock retirement.

#### Scenario: Scripts table complete

- **WHEN** a reader checks the README scripts table
- **THEN** all non-deprecated scripts under `scripts/` are listed with purpose

#### Scenario: Gap analysis link valid

- **WHEN** a reader follows the gap analysis link in README Notes
- **THEN** the linked file path exists and has no typographical errors

#### Scenario: Counts match manifests

- **WHEN** a reader compares README dataset counts to the built `*.manifest.json` files
- **THEN** the stated country and blocktype counts equal the manifests, and the stated intblock count is the manifest count rounded down to the hundred, followed by `+`

#### Scenario: Validation description accurate

- **WHEN** a reader reads the README validation section
- **THEN** it states that both country and intblock validation run before export

#### Scenario: Field table mentions car_side as country property

- **WHEN** a reader opens the README countries field summary after attribute migration
- **THEN** `car_side` and the newly added attribute fields are listed as country properties rather than intblock categories

### Requirement: CI status visibility

README SHALL display a CI workflow status badge for the validate workflow.

#### Scenario: Badge present

- **WHEN** a reader views README on the default branch
- **THEN** a badge reflects the status of `.github/workflows/validate.yml`

### Requirement: Documentation count accuracy

Dataset record and category counts stated across maintained documentation (`llms.txt`, `docs/ai-consumers.md`, `openspec/project.md`, and other docs) SHALL match the current build manifests, and referenced generated artifacts SHALL exist. The intblock count SHALL be stated rounded down to the hundred and written as `N+`, so that adding records does not change documentation until the count crosses a hundred.

#### Scenario: llms.txt counts current

- **WHEN** a consumer reads intblock and country counts in `llms.txt`
- **THEN** the country count equals the manifest `row_count`, and the intblock count is the manifest `row_count` rounded down to the hundred, followed by `+`

#### Scenario: Adding a record leaves docs unchanged

- **WHEN** a pull request raises the intblock count from 1304 to 1310
- **THEN** the documentation count check passes without documentation edits

#### Scenario: Dataset card states the rounded count

- **WHEN** the build writes the committed dataset card `data/datasets/README.md` with 1304 intblocks
- **THEN** the card states `1300+` intblocks, so a build with 1310 intblocks writes the same card

#### Scenario: Referenced artifact exists

- **WHEN** documentation references a generated file such as a manifest
- **THEN** that file is produced by the build

### Requirement: Internal documentation link checking

CI SHALL run an internal Markdown link checker over repository docs and fail on broken internal links.

#### Scenario: Broken internal link fails CI

- **WHEN** a Markdown file links to a repository path that does not exist
- **THEN** the link-check step fails

### Requirement: Generated data dictionary

The repository SHALL maintain `docs/data-dictionary.md` generated from `countries.schema.json` and `intblocks.schema.json`, with a script to regenerate it when schemas change.

#### Scenario: Field reference available

- **WHEN** a non-technical user opens the data dictionary
- **THEN** they find every country and intblock field with type and description

#### Scenario: Schema drift detected

- **WHEN** a pull request modifies a JSON Schema without regenerating the dictionary
- **THEN** CI or documented check fails or warns

### Requirement: GitHub issue templates

The repository SHALL provide structured GitHub issue templates for data errors, data/org requests, and code bugs under `.github/ISSUE_TEMPLATE/`.

#### Scenario: Data error report guided

- **WHEN** a user opens a new GitHub issue
- **THEN** they can choose a data error template with fields for record id, expected vs actual, and source URL

### Requirement: Non-programmer getting started guide

The repository SHALL include `docs/getting-started.md` explaining what the datasets contain, how to open CSV or lite exports, and how to cite via DOI.

#### Scenario: Educator finds entry path

- **WHEN** a reader follows README link to getting started
- **THEN** they can open country data in a spreadsheet without installing DuckDB

### Requirement: Pipeline architecture diagram

README or `docs/architecture.md` SHALL include a diagram of the YAML → validate → enrich → build → release pipeline with key paths.

#### Scenario: New contributor understands flow

- **WHEN** a contributor views the architecture diagram
- **THEN** they can identify where validation, enrichment, and export occur

### Requirement: Dev artifact indexes

`dev/research/README.md` and `dev/scripts/README.md` SHALL index research reports and script support status; `data/_legacy/` SHALL carry a warning that contents are obsolete.

#### Scenario: Research reports discoverable

- **WHEN** a reader opens dev/research README
- **THEN** they find links to gap analysis reports and methodology notes

### Requirement: Intblock taxonomy documentation

`docs/ai-consumers.md` SHALL document the `scope_category` field and link to `docs/intblock-inclusion-policy.md`.

#### Scenario: Agent discovers scope filter

- **WHEN** an LLM agent reads `llms.txt` or `docs/ai-consumers.md`
- **THEN** it finds a DuckDB filter example excluding reference enumerations from IGO membership queries

### Requirement: LLM tool-call schema artifacts

The repository SHALL publish compact JSON Schema subsets at `data/schemas/country_lookup.openai.json` and `data/schemas/intblock_lookup.openai.json` suitable for OpenAI function-calling and similar tool-use APIs, documented in `docs/ai-consumers.md`.

#### Scenario: Agent loads country lookup schema

- **WHEN** an integrator reads `country_lookup.openai.json`
- **THEN** it defines query parameters for lookup by ISO code or name without nested struct definitions

### Requirement: Token budget guidance

`llms.txt` SHALL include approximate token counts or relative size guidance for major consumption paths (full Parquet/JSON vs lite exports vs DuckDB projection queries).

#### Scenario: Agent chooses lite path

- **WHEN** an LLM agent reads llms.txt before loading data
- **THEN** it finds token budget hints recommending lite exports for entity-linking-only tasks

### Requirement: Policy-researcher query recipes

`docs/query-examples.md` SHALL include tested membership-analysis queries for policy researchers (organization overlap, former members, regional community density, succession chains) validated by `tests/test_documented_queries.py`.

#### Scenario: NATO and EU overlap query tested

- **WHEN** CI runs documented query tests
- **THEN** the NATO∩EU membership query returns the expected country count

### Requirement: Documented includes status enum

`docs/ai-consumers.md` SHALL list canonical `includes[].status` values from `data/schemas/includes_status.yaml` with semantics for LLM-generated filters.

#### Scenario: Status filter documented

- **WHEN** a consumer reads ai-consumers membership section
- **THEN** they find definitions for `member`, `former_member`, `observer`, and `founding_member`

### Requirement: Tabular export documentation

README and `docs/ai-consumers.md` SHALL document CSV, lite, JSON array, and datapackage export paths with guidance on which format to choose by user type (spreadsheet, LLM lite, programmatic full).

#### Scenario: Non-programmer finds CSV path

- **WHEN** a reader opens `docs/getting-started.md` or README format table
- **THEN** they find instructions to download and open `countries.csv` without DuckDB or Parquet tooling

### Requirement: Policy document index

README or `docs/ai-consumers.md` SHALL link to `docs/entity-classification-policy.md` and the CIS2 build-inclusion section of `docs/country-code-policy.md`.

#### Scenario: Contributor finds classification policy

- **WHEN** a contributor opens CONTRIBUTING or country-code-policy
- **THEN** they find a link to the entity classification policy for disputed-territory edits

### Requirement: Attribute vs geographic enumeration guidance

Contributor and AI-consumer documentation SHALL explain that country attribute partitions (traffic hand, scripts, DVD region, broadcast systems, legal traditions, rail gauges) are country fields, while named geographic reference sets may remain intblocks. Documentation SHALL link to `docs/intblock-inclusion-policy.md` and the attribute migration artifact for retired ids.

#### Scenario: Agent discovers car_side instead of traffichand

- **WHEN** an agent reads `docs/ai-consumers.md` or `llms.txt` for driving-side queries
- **THEN** the docs prescribe filtering `countries.car_side` and mention that `traffichand` intblocks are retired

#### Scenario: Inclusion policy distinguishes attribute partitions

- **WHEN** a contributor reads `docs/intblock-inclusion-policy.md`
- **THEN** the policy states attribute partitions are out of intblock scope and points to country fields / vocabs

### Requirement: Documented example execution accuracy

Every executable example in maintained consumer documentation (`README.md`, `llms.txt`, `docs/query-examples.md`, `docs/query-examples.zh.md`, `docs/ai-consumers.md`, `docs/agents/query.md`) SHALL execute successfully against the current committed artifacts and return the documented result. Examples that filter on stored field values SHALL use the exact stored strings, and examples with deterministic results SHALL state an expected count that is asserted by a test.

#### Scenario: World Bank region example returns rows

- **WHEN** a consumer runs the documented World Bank region filter from `docs/query-examples.md` against `internacia.duckdb`
- **THEN** the query returns the documented non-zero row count

#### Scenario: Pandas example runs on a default install

- **WHEN** a consumer runs the documented pandas parquet snippet with a default `pip install pandas pyarrow` environment
- **THEN** the snippet executes without raising and yields the documented values

#### Scenario: Documented classification-gap figures match data

- **WHEN** documentation states how many entities lack World Bank `region`/`incomeLevel` or `adminregion` values
- **THEN** the stated figures equal the counts computed from the current countries artifact

### Requirement: Memory-bounded query recipes

Documented DuckDB query recipes SHALL execute within a bounded memory budget enforced by the documented-queries test suite, and SHALL NOT use unconstrained cross joins (`JOIN ... ON TRUE`) where an UNNEST-first rewrite produces the same result.

#### Scenario: Recipe completes under memory limit

- **WHEN** the documented-queries test suite runs every cookbook recipe with an explicit DuckDB `memory_limit`
- **THEN** every recipe completes without an out-of-memory error

#### Scenario: Cross-join recipe rewritten

- **WHEN** a membership-coverage recipe needs to combine `countries` with `intblocks.includes`
- **THEN** the documented form unnests `includes` before joining to `countries` instead of cross-joining whole tables

### Requirement: Canonical organization link integrity

All self-referential repository links in maintained documentation (README badge, API/SDK sister-repo links, agent indexes) SHALL point to the canonical GitHub organization of the repository's `origin` remote, and sister-repository links SHALL use absolute URLs that resolve when viewed on GitHub.

#### Scenario: README badge resolves

- **WHEN** a reader clicks the CI badge at the top of `README.md`
- **THEN** it opens the validate workflow of the canonical repository without a 404

#### Scenario: Sister repository links resolve

- **WHEN** a reader follows an API or SDK link from any maintained doc
- **THEN** the absolute URL resolves to the canonical `datenoio` repository

### Requirement: Agent index superset consistency

If an extended agent index (`llms-full.txt`) is published alongside `llms.txt`, it SHALL contain all information present in `llms.txt` plus additional detail; otherwise it SHALL NOT be published.

#### Scenario: Extended index is a superset

- **WHEN** a crawler prefers `llms-full.txt` over `llms.txt`
- **THEN** it receives at least all facts, counts, and gotchas present in `llms.txt`

### Requirement: Planning document freshness

Planning documents under `docs/` that describe roadmap state (`improvement-plan.md`, `strategy-and-user-needs.md`) SHALL carry a dated status header identifying the release they were written against, and items shipped in later releases SHALL be marked as shipped rather than presented as open gaps.

#### Scenario: Shipped item marked

- **WHEN** a reader consults a planning doc for an item that has since shipped (e.g. the alias map)
- **THEN** the item is marked shipped with a reference to the release or change that delivered it

### Requirement: Legacy data quarantine notice

Agent-facing indexes (`AGENTS.md`, `llms.txt`) SHALL warn that `data/_legacy/` contains obsolete pre-pipeline dumps that MUST NOT be consumed.

#### Scenario: Agent warned away from legacy dumps

- **WHEN** an agent reads `AGENTS.md` or `llms.txt` to locate data
- **THEN** it finds an explicit instruction not to read `data/_legacy/`

