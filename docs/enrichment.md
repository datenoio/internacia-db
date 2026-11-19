# Country data enrichment

Externally sourced country fields (`population`, `area`, `gini`, `timezones`, `native_names`, World Bank classifications) are populated by `scripts/enrich_countries.py` and validated on every PR.

## Refresh cadence

| Field group | Source | Suggested refresh |
|---|---|---|
| `population`, `area`, `gini` | World Bank API | Annually (after WB spring update) |
| `timezones` | IANA `zone1970.tab` | When tzdata bundle is updated in `scripts/data/` |
| `native_names`, `wikidata_id` | Wikidata | Annually or when labels change |
| `region`, `adminregion`, `incomeLevel`, `lendingType` | World Bank API (`/v2/country`); M49 inference for entities the Bank does not classify | Monthly `enrich`; at the latest after the Bank's 1 July reclassification |

**Provenance staleness threshold:** 12 months (`provenance.max_age_months` in `data/schemas/countries_completeness.yaml`). Validation warns when `retrieved_at` is older than this.

**Intblock `last_verified` SLA:** 12 months (`quality.last_verified_max_age_months` in `data/schemas/intblocks_completeness.yaml`). Validation warns (`STALE_LAST_VERIFIED`) when `last_verified` is older. Stamp `last_verified` whenever you check a roster against an official source. Missing `last_verified` is a completeness warning, not an error.

Catalogues already searched for missing intblocks, and the roster authorities used
to compile membership, are listed in [intblock-sources.md](intblock-sources.md).
How to search those catalogues and improve existing country / intblock records:
[discovery.md](discovery.md).

**Provenance depth threshold:** at least four field-level entries per record (`provenance.min_count` in `data/schemas/countries_completeness.yaml` and `data/schemas/intblocks_completeness.yaml`). Validation warns via `INSUFFICIENT_PROVENANCE` when below the minimum.

## Maintainer workflow

### 1. Check current state (no network)

```bash
python scripts/enrich_countries.py check
python scripts/validate_countries.py
```

`check` reports stale provenance entries and fields still missing enrichment targets.

### 2. Refresh from sources

```bash
# Full enrichment (World Bank + Wikidata + timezones)
python scripts/enrich_countries.py enrich

# World Bank classifications only, plus the wbgroup rosters derived from them
python scripts/enrich_countries.py refresh-classifications

# Targeted backfills (no Wikidata fetch)
python scripts/enrich_countries.py backfill-classifications
python scripts/enrich_countries.py backfill-gini

# Preserve existing provenance; unknown historical retrieval dates are not invented
python scripts/enrich_countries.py backfill-provenance
```

Use `--code XX` on `enrich` for a single country. Use `--dry-run` to preview YAML diffs.

`refresh-classifications` (and `enrich`) copy the Bank's ids and labels verbatim for every
economy it classifies, with provenance source `World Bank` and the economy's API URL. Entities
the Bank does not classify keep their inferred values, recoded to current ids (`OEC`/`NOC` →
`HIC`, `NC` → `LNX`); a high-income entity has no `adminregion`. The run then rebuilds the
`wbgroup` rosters (`EAS` … `SSF`, `ECA`/`LAC`/`MNA`/`SSA`, `HIC`/`UMC`/`LMC`/`LIC`, `MIC`,
`LMY`) from the refreshed fields; the `World Bank group rosters` validation rule warns when a
roster and the country fields disagree. A single-country `enrich --code` run does not touch
the rosters.
Usable World Bank responses refresh existing World Bank observations without
regressing their observation year. Other curated sources remain unchanged unless
`--force` is used. Failed, unused, and unchanged observations retain their retrieval
dates. New Wikidata fallback values omit unknown years; they never write zero.
Sources are schema/date-validated before atomic replacement. Metadata enrichment
on intblocks does not advance `last_verified`, which denotes roster verification.

### 3. Validate and build

```bash
python scripts/validate_countries.py --report completeness-report.json
pytest tests/
python scripts/builder.py build
```

### 4. Review diffs

- Confirm `year` values are positive integers (never `year: 0` for World Bank indicators).
- Confirm each updated field has a matching `provenance` entry with today's `retrieved_at`.
- Expect `gini` to remain null for 86 records in the current snapshot; missing
  observations are expected for many territories and other uncovered entities.

## Gini completeness ratcheting

Current coverage: ~170/256 records with `gini` (~33.6% null). `countries_completeness.yaml` sets `gini.max_null_rate: 0.33` in **warn** mode. When coverage improves materially, lower `max_null_rate` and optionally switch `mode` to `error` in a documented release.

## Out of scope

Socioeconomic profile fields (HDI, GDP per capita, government type, internet penetration) are **not** part of this dataset. See `openspec/AGENTS.md` — countries are reference data only.

## Automation

`.github/workflows/enrichment-check.yml` runs monthly (and on `workflow_dispatch`):

1. Freshness `check` and validation report.
2. `enrich_countries.py enrich` and `enrich_intblocks.py enrich`.
3. `scripts/enrichment_split.py snapshot` records the changed records and splits them by source,
   following [`data/schemas/enrichment_sources.yaml`](../data/schemas/enrichment_sources.yaml):

   | Source | Fields |
   |---|---|
   | `wb-indicators` | `population`, `area`, `gini` |
   | `wb-classifications` | `region`, `adminregion`, `incomeLevel`, `lendingType` (always reviewed) |
   | `wikidata-countries` | `wikidata_id`, `native_names`, `common_names` |
   | `iana-timezones` | `timezones`, `timezone_status` |
   | `intblock-metadata` | intblock `description`, `other_names`, `acronyms`, `founded`, `headquarters`, `wikidata_id` |
   | `other` | anything else (always reviewed) |

   Provenance entries go with their field. The report and the snapshot are uploaded as the
   `enrichment-check-report` artifact.
4. For each source with changes, a job applies only that source's changes to `main`, validates,
   rebuilds and runs the quality gate, then opens or refreshes a PR on `enrichment/<source>`.

**Auto-merge.** A PR merges by itself once CI passes when every change fills an empty value, only
adds list items or mapping keys, or stays within the field's threshold (population ±10%, area
±2%, Gini ±5 points), and the source is not always reviewed. Otherwise it is labelled
`needs-review` and assigned to the reviewer in the `ENRICHMENT_REVIEWER` repository variable.
Enrichment never changes ids, `includes` or enum values: those fields belong to no source, so
such a change would land in the reviewed `other` PR.

Metadata-only intblock changes (the `intblock-metadata` fields, `scope_category`, and their
provenance) do not need `last_verified`, which attests the roster; the validator's changed-record
rule skips them.

**Requirements:** the internacia-bot GitHub App secrets (`INTERNACIA_BOT_CLIENT_ID`,
`INTERNACIA_BOT_PRIVATE_KEY`), "Allow auto-merge", and branch protection on `main` requiring the
validation checks. The workflow never pushes to `main`.

Crosswalk seeding: `scripts/seed_country_crosswalks.py` (`--check` by default). The one-off
`scope_category` backfill is in `scripts/oneoff/label_scope_category.py`.

## Intblock Wikidata completeness

Every intblock must have `wikidata_id` **or** appear in
[`data/schemas/wikidata_exclusions.yaml`](../data/schemas/wikidata_exclusions.yaml).

Exclusion entries require: `id`, `reason`, `verified_at`, `source`.

**Criteria for exclusion:** no Wikidata item exists after search; regional
sub-bodies without distinct Q-ids; ephemeral enumerations; pending enrichment
backfill after a documented audit.

**Review cadence:** re-run `python scripts/enrich_intblocks.py enrich` (or the
monthly enrichment workflow) and remove ids from the exclusion list when a
Q-id is found. Validation fails (`MISSING_WIKIDATA_ID`) for records missing both.
