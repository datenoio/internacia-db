# Change: Add a transit dependence layer

## Why

Trade influence is not only how much two countries trade. A country can depend on a neighbour that it barely trades with, because its goods cross that neighbour's territory. Armenia is landlocked, and its land borders with Türkiye and Azerbaijan are closed. Almost all of its foreign trade therefore passes through Georgia's ports and over Georgia's border with Russia. The small volume of Armenian–Georgian trade understates Georgia's leverage.

Internacia already holds the structural inputs for this kind of dependence. It has land `borders`, the `landlocked` flag, 25 gas pipeline records and transport-corridor treaties. Three things are missing:

- **The function of each country on an infrastructure route.** All 68 country entries on the 25 gas pipelines are `status: member`. Nothing says which country supplies gas, which carries it, and which receives it.
- **Whether a land border can be crossed.** A closed border looks the same as an open one. On the current border graph, Armenia appears to have three direct coastal neighbours (Georgia, Iran, Türkiye); with its closed borders removed, it has two.
- **A documented way to compute sea-access dependence**, and a way to join bilateral trade data, which stays outside the repository.

A prototype on the current data shows what the graph alone gives. 44 official countries are landlocked. Six have exactly one coastal neighbour: KG and TJ (China), LS (South Africa), SM and VA (Italy), and TM (Iran). Two are doubly landlocked: LI and UZ. The prototype also shows the graph's limits. It routes Kyrgyzstan to the sea through China, while its freight mostly goes by rail through Kazakhstan to Russia. The structural measure is therefore a lower bound on dependence, not a route model.

## What Changes

This change adds structural transit facts, keeps every time series downstream, and documents how to combine the two.

- **Infrastructure roles.** Declare the optional `includes[].role` field, which is already exported but unused and undeclared. Roles are `origin`, `transit` and `destination`, defined in `data/schemas/include_roles.yaml`. They are allowed only on infrastructure records (blocktype `gaspipeline` in this change). Backfill all 25 gas pipelines from a reviewed manifest, with provenance.
- **Border crossing status.** Add an edge dataset of land-border crossing status: `data/borders/border_status.yaml`. Each entry has an unordered `iso3code` pair, a status (`closed` or `restricted`), `since`, an optional `until`, and provenance. Export it as a `border_status` table, plus a `country_borders` view that flattens `countries.borders` with that status. Absence of an entry means that no closure is recorded, not that the border is verified open. Backfill a reviewed pilot of well-documented closures.
- **Sea-access recipe.** Add a tested DuckDB recipe that lists, for each landlocked country, its gateways to the sea over crossable borders. For each first-hop neighbour it gives the distance in borders to the nearest coastal country, and it flags countries with a single gateway.
- **Trade dependence documentation.** Document the bilateral dependence measures (partner share, asymmetry, exposure, partner concentration, in-bloc leverage) and how to join an external trade table on `iso3code`. No trade data ships.

The change adds nothing to the country schema. It does not store trade values, trade shares, transit volumes, route capacity or any composite score.

## Impact

Every addition is optional or a new table, and every new enum is open. Under the versioning policy this ships as a MINOR release.

- Affected specs: new `transit-routes` (infrastructure roles, the sea-access recipe, trade dependence documentation) and new `border-crossing-status`.
- Affected source:
  - `data/schemas/intblocks.schema.json` (`includes[].role`)
  - new `data/schemas/include_roles.yaml`
  - new `data/schemas/border_status.schema.json`
  - new `data/borders/border_status.yaml`
  - reviewed manifests for the two pilots
  - 25 records under `data/intblocks/gaspipeline/`
- Affected code:
  - `internacia_builder/schemas.py` (Arrow schema for `border_status`)
  - `internacia_builder/export.py` and `internacia_builder/contract.py` (new table and view)
  - validators and the shared rule registry
  - a dry-run-first backfill script for roles
  - tests
- Affected documentation:
  - `docs/query-examples.md` (with `tests/test_documented_queries.py`)
  - `docs/ai-consumers.md`
  - `docs/data-contract.md`
  - `docs/intblock-inclusion-policy.md`
  - `docs/when-to-use-internacia.md`
  - `docs/data-dictionary.md` (generated)
  - `llms.txt`
  - `CHANGELOG.md`
- Affected exports:
  - intblocks: `includes[].role` gains values; the column already exists.
  - New `border_status` table in Parquet, JSONL and DuckDB, with a manifest.
  - New DuckDB view `country_borders`.
- Not breaking: no column is removed or retyped, and no identifier changes.
