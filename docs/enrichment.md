# Country data enrichment

Externally sourced country fields (`population`, `area`, `gini`, `timezones`, `native_names`, World Bank classifications) are populated by `scripts/enrich_countries.py` and validated on every PR.

## Refresh cadence

| Field group | Source | Suggested refresh |
|---|---|---|
| `population`, `area`, `gini` | World Bank API | Annually (after WB spring update) |
| `timezones` | IANA `zone1970.tab` | When tzdata bundle is updated in `scripts/data/` |
| `native_names`, `wikidata_id` | Wikidata | Annually or when labels change |
| `region`, `adminregion`, `incomeLevel`, `lendingType` | World Bank + M49 inference | When classification policy changes |

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

# Targeted backfills (no Wikidata fetch)
python scripts/enrich_countries.py backfill-classifications
python scripts/enrich_countries.py backfill-gini

# Preserve existing provenance; unknown historical retrieval dates are not invented
python scripts/enrich_countries.py backfill-provenance
```

Use `--code XX` on `enrich` for a single country. Use `--dry-run` to preview YAML diffs.
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

1. Freshness `check` + validation report
2. `enrich_countries.py enrich` and `enrich_intblocks.py enrich`
3. If YAML changes, validates and rebuilds exports and quality reports before opening a PR labeled
   `enrichment` on branch `chore/monthly-enrichment`

Reports are published as the `enrichment-check-report` workflow artifact (90-day retention) and
summarized on the run page; they are never committed:
`enrichment-check-report.txt`, `enrichment-validation.json`, and `dataquality/full_report.jsonl`
when exports were rebuilt.

The PR is opened with a token minted from the `internacia-bot` GitHub App
(`actions/create-github-app-token`), so `validate.yml` runs on it. PRs opened with the default
`GITHUB_TOKEN` never trigger CI. Required repository (or org) secrets:

| Secret | Value |
|--------|-------|
| `INTERNACIA_BOT_CLIENT_ID` | App **Client ID** (`Iv23…`) |
| `INTERNACIA_BOT_PRIVATE_KEY` | Full PEM private key generated for the app |

The app needs repository permissions **Contents: Read and write** and **Pull requests: Read and
write**, installed on `datenoio/internacia-db`. If the secrets are missing, the run still uploads
the report artifact and then fails at the PR step.

**Maintainer review expectations:** spot-check provenance dates and unexpected
roster/value swings before merge. The workflow never pushes directly to `main`.

Optional one-off seeds: `scripts/seed_country_crosswalks.py`,
`scripts/label_scope_category.py`.

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
