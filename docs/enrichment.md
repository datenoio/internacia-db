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

# Sync provenance from existing indicator structs
python scripts/enrich_countries.py backfill-provenance
```

Use `--code XX` on `enrich` for a single country. Use `--dry-run` to preview YAML diffs.

### 3. Validate and build

```bash
python scripts/validate_countries.py --report completeness-report.json
pytest tests/
python scripts/builder.py build
```

### 4. Review diffs

- Confirm `year` values are positive integers (never `year: 0` for World Bank indicators).
- Confirm each updated field has a matching `provenance` entry with today's `retrieved_at`.
- Expect `gini` to remain null for ~82 territories where World Bank publishes no observation.

## Gini completeness ratcheting

Current coverage: ~170/252 records with `gini` (~32.5% null). `countries_completeness.yaml` sets `gini.max_null_rate: 0.33` in **warn** mode. When coverage improves materially, lower `max_null_rate` and optionally switch `mode` to `error` in a documented release.

## Out of scope

Socioeconomic profile fields (HDI, GDP per capita, government type, internet penetration) are **not** part of this dataset. See `openspec/AGENTS.md` — countries are reference data only.

## Automation

`.github/workflows/enrichment-check.yml` runs monthly (and on manual dispatch) to execute `enrich_countries.py check` and upload a report artifact. It does not modify data or open PRs automatically.
